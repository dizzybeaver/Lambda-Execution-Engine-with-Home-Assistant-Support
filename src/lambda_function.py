"""
lambda_function.py - AWS Lambda Entry Point
Version: 2025.10.19.03
Description: Main Lambda handler with SUGA-ISP gateway integration

CHANGELOG:
- 2025.10.19.03: Removed debug logging statements
- 2025.10.19.02: Added extensive DEBUG logging throughout
- 2025.10.19.01: Added ha_discovery mode for Alexa discovery debug tracing
- 2025.10.18.10: Added Alexa.Authorization namespace routing to fix AcceptGrant

Copyright 2025 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

import json
import os
import time
import urllib3
from typing import Dict, Any


# ===== LAMBDA MODE SELECTION =====

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """AWS Lambda entry point with mode selection."""
    
    lambda_mode = os.getenv('LAMBDA_MODE', 'normal').lower()
    
    if lambda_mode == 'failsafe':
        try:
            import lambda_failsafe
            return lambda_failsafe.lambda_handler(event, context)
        except ImportError:
            lambda_mode = 'normal'
    
    elif lambda_mode == 'diagnostic':
        try:
            import lambda_diagnostic
            return lambda_diagnostic.lambda_handler(event, context)
        except ImportError:
            lambda_mode = 'normal'
    
    elif lambda_mode == 'emergency':
        try:
            import lambda_emergency
            return lambda_emergency.lambda_handler(event, context)
        except ImportError:
            lambda_mode = 'normal'
    
    elif lambda_mode == 'ha_connection_test':
        try:
            import lambda_ha_connection
            return lambda_ha_connection.lambda_handler(event, context)
        except ImportError:
            lambda_mode = 'normal'
    
    elif lambda_mode == 'ha_discovery':
        try:
            import debug_discovery
            return debug_discovery.lambda_handler(event, context)
        except ImportError:
            lambda_mode = 'normal'
    
    return lambda_handler_normal(event, context)


def lambda_handler_normal(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Normal Lambda handler with full LEE."""
    
    try:
        from gateway import (
            log_info, log_error, log_debug,
            execute_operation, GatewayInterface,
            increment_counter, format_response,
            validate_request, validate_token
        )
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": f"Gateway import failed: {str(e)}"})
        }
    
    try:
        log_info("Lambda invocation started", 
                request_id=context.aws_request_id,
                function_name=context.function_name,
                memory_limit=context.memory_limit_in_mb,
                remaining_time=context.get_remaining_time_in_millis())
        
        increment_counter("lambda_invocations")
        
        request_type = determine_request_type(event)
        log_debug(f"Request type: {request_type}")
        
        if request_type == "alexa":
            return handle_alexa_request(event, context)
        elif request_type == "diagnostic":
            return handle_diagnostic_request(event, context)
        else:
            return format_response(400, {
                "error": "Unknown request type",
                "event": event
            })
            
    except Exception as e:
        log_error("Lambda execution failed", error=e)
        return format_response(500, {
            "error": str(e),
            "error_type": type(e).__name__
        })


def determine_request_type(event: Dict[str, Any]) -> str:
    """Determine the type of request from the event structure."""
    
    if "directive" in event:
        return "alexa"
    
    if "test_type" in event:
        return "diagnostic"
    
    return "unknown"


def handle_alexa_request(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Handle Alexa Smart Home requests."""
    
    from gateway import (
        log_info, log_error, log_debug,
        increment_counter, format_response,
        GatewayInterface, execute_operation
    )
    
    try:
        directive = event.get("directive", {})
        header = directive.get("header", {})
        namespace = header.get("namespace", "")
        name = header.get("name", "")
        
        log_info(f"Alexa request: {namespace}.{name}")
        increment_counter(f"alexa_{namespace.lower()}_{name.lower()}")
        
        if namespace == "Alexa.Discovery":
            from homeassistant_extension import handle_alexa_discovery
            return handle_alexa_discovery(event)
        
        elif namespace == "Alexa.Authorization":
            from homeassistant_extension import handle_alexa_authorization
            return handle_alexa_authorization(event)
        
        elif namespace in ["Alexa.PowerController", "Alexa.BrightnessController",
                          "Alexa.ColorController", "Alexa.ThermostatController",
                          "Alexa.LockController", "Alexa"]:
            from homeassistant_extension import handle_alexa_control
            return handle_alexa_control(event)
        
        else:
            log_error(f"Unsupported Alexa namespace: {namespace}")
            return {
                "event": {
                    "header": {
                        "namespace": "Alexa",
                        "name": "ErrorResponse",
                        "messageId": header.get("messageId", "error"),
                        "payloadVersion": "3"
                    },
                    "payload": {
                        "type": "INVALID_DIRECTIVE",
                        "message": f"Unsupported namespace: {namespace}"
                    }
                }
            }
    
    except Exception as e:
        log_error(f"Alexa request failed: {str(e)}", error=e)
        return {
            "event": {
                "header": {
                    "namespace": "Alexa",
                    "name": "ErrorResponse",
                    "messageId": "error",
                    "payloadVersion": "3"
                },
                "payload": {
                    "type": "INTERNAL_ERROR",
                    "message": str(e)
                }
            }
        }


def handle_diagnostic_request(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Handle diagnostic/test requests."""
    
    test_type = event.get("test_type", "unknown")
    
    if test_type in ['network_test', 'ha_ping']:
        return handle_network_test(event, context)
    
    from gateway import (
        log_info, log_debug, log_error, increment_counter,
        format_response, execute_operation, GatewayInterface
    )
    
    try:
        log_info(f"Diagnostic request: {test_type}")
        increment_counter(f"diagnostic_{test_type}")
        
        response_data = {
            "timestamp": execute_operation(GatewayInterface.UTILITY, 'generate_uuid'),
            "test_type": test_type,
            "lambda_info": {
                "function_name": context.function_name,
                "function_version": context.function_version,
                "memory_limit": str(context.memory_limit_in_mb),
                "remaining_time": context.get_remaining_time_in_millis()
            }
        }
        
        if test_type in ["full", "configuration"]:
            response_data["gateway_stats"] = execute_operation(
                GatewayInterface.DEBUG, 
                'get_gateway_stats'
            )
        
        if test_type == "full":
            try:
                from homeassistant_extension import get_ha_diagnostic_info
                response_data["home_assistant"] = get_ha_diagnostic_info()
            except Exception as e:
                log_error(f"Diagnostic info failed: {str(e)}")
                response_data["home_assistant"] = {}
        
        if test_type in ["full", "configuration"]:
            response_data["environment"] = {
                "HOME_ASSISTANT_URL": os.getenv("HOME_ASSISTANT_URL"),
                "HOME_ASSISTANT_TOKEN": "..." if os.getenv("HOME_ASSISTANT_TOKEN") else None,
                "HOME_ASSISTANT_ENABLED": os.getenv("HOME_ASSISTANT_ENABLED", "false"),
                "USE_PARAMETER_STORE": os.getenv("USE_PARAMETER_STORE", "false"),
                "DEBUG_MODE": os.getenv("DEBUG_MODE", "false"),
                "LAMBDA_MODE": os.getenv("LAMBDA_MODE", "normal")
            }
        
        return format_response(200, response_data)
        
    except Exception as e:
        log_error(f"Diagnostic failed: {str(e)}", error=e)
        return format_response(500, {
            "error": str(e),
            "error_type": type(e).__name__
        })


def handle_network_test(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Network connectivity test - bypasses all LEE systems."""
    
    ha_url = os.getenv("HOME_ASSISTANT_URL")
    ha_token = os.getenv("HOME_ASSISTANT_TOKEN")
    
    if not ha_url or not ha_token:
        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": "Missing HA configuration",
                "ha_url": bool(ha_url),
                "ha_token": bool(ha_token)
            })
        }
    
    try:
        http = urllib3.PoolManager(timeout=urllib3.Timeout(connect=2.0, read=5.0))
        
        test_url = f"{ha_url.rstrip('/')}/api/"
        headers = {
            "Authorization": f"Bearer {ha_token}",
            "Content-Type": "application/json"
        }
        
        start_time = time.time()
        response = http.request('GET', test_url, headers=headers)
        duration = (time.time() - start_time) * 1000
        
        return {
            "statusCode": 200,
            "body": json.dumps({
                "success": True,
                "test_type": "network_test",
                "ha_url": ha_url,
                "http_status": response.status,
                "duration_ms": round(duration, 2),
                "headers": dict(response.headers)
            })
        }
        
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": str(e),
                "error_type": type(e).__name__,
                "test_type": "network_test",
                "ha_url": ha_url
            })
        }

# EOF
