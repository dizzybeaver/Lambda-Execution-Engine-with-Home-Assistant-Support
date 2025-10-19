"""
lambda_function.py - AWS Lambda Entry Point
Version: 2025.10.19.01
Description: Main Lambda handler with SUGA-ISP gateway integration

CHANGELOG:
- 2025.10.19.01: Added ha_discovery mode for Alexa discovery debug tracing
- 2025.10.18.10: Added Alexa.Authorization namespace routing to fix AcceptGrant
- 2025.10.18.01: Added ha_connection_test mode for HA connection diagnostics
- 2025.10.16.10: Added network connectivity test (ha_ping/network_test)
- 2025.10.16.09: Added SKIP_HA_HEALTH_CHECK environment variable option

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
    """
    AWS Lambda entry point with mode selection.
    
    Modes:
    - normal: Full LEE operation (default)
    - failsafe: Direct HA passthrough via lambda_failsafe.py
    - diagnostic: Import testing via lambda_diagnostic.py
    - emergency: Emergency bypass via lambda_emergency.py
    - ha_connection_test: HA connection diagnostic via lambda_ha_connection.py
    - ha_discovery: Alexa discovery debug tracer via debug_discovery.py
    """
    
    # Check Lambda mode
    lambda_mode = os.getenv('LAMBDA_MODE', 'normal').lower()
    
    # Bypass modes - skip LEE entirely
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
    
    # Normal mode - full LEE operation
    return lambda_handler_normal(event, context)


def lambda_handler_normal(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Normal Lambda handler with full LEE."""
    
    # Lazy import gateway functions
    from gateway import (
        log_info, log_error, log_debug,
        execute_operation, GatewayInterface,
        increment_counter, format_response,
        validate_request, validate_token
    )
    
    try:
        log_info("Lambda invocation started", 
                request_id=context.aws_request_id,
                function_name=context.function_name,
                memory_limit=context.memory_limit_in_mb,
                remaining_time=context.get_remaining_time_in_millis())
        
        increment_counter("lambda_invocations")
        
        # Determine request type
        request_type = determine_request_type(event)
        log_debug(f"Request type: {request_type}")
        
        # Route to appropriate handler
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
    
    # Alexa Smart Home directive
    if "directive" in event:
        return "alexa"
    
    # Diagnostic/test request
    if "test_type" in event:
        return "diagnostic"
    
    # Default
    return "unknown"


def handle_alexa_request(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Handle Alexa Smart Home requests."""
    
    # Lazy import gateway and HA extension
    from gateway import (
        log_info, log_error, log_warning, increment_counter,
        validate_request, validate_token
    )
    from homeassistant_extension import (
        handle_alexa_discovery,
        handle_alexa_control,
        handle_alexa_authorization,
        is_ha_extension_enabled,
        get_ha_status
    )
    
    try:
        directive = event.get("directive", {})
        header = directive.get("header", {})
        namespace = header.get("namespace", "")
        name = header.get("name", "")
        
        log_info(f"Alexa request: {namespace}.{name}")
        increment_counter(f"alexa_{namespace.lower()}")
        
        # Check if HA extension is enabled
        if not is_ha_extension_enabled():
            log_error("Home Assistant extension is disabled")
            return {
                "event": {
                    "header": {
                        "namespace": "Alexa",
                        "name": "ErrorResponse",
                        "messageId": header.get("messageId", "error"),
                        "payloadVersion": "3"
                    },
                    "payload": {
                        "type": "BRIDGE_UNREACHABLE",
                        "message": "Home Assistant extension is disabled"
                    }
                }
            }
        
        # Route by namespace
        if namespace == "Alexa.Discovery":
            return handle_alexa_discovery(event, context)
        
        elif namespace == "Alexa.Authorization":
            return handle_alexa_authorization(event, context)
        
        elif namespace in ["Alexa.PowerController", "Alexa.BrightnessController",
                          "Alexa.ColorController", "Alexa.ColorTemperatureController",
                          "Alexa.ThermostatController", "Alexa.LockController",
                          "Alexa"]:
            return handle_alexa_control(event, context)
        
        else:
            log_warning(f"Unsupported namespace: {namespace}")
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
    
    # Special network connectivity test - bypass all LEE systems
    if test_type in ['network_test', 'ha_ping']:
        return handle_network_test(event, context)
    
    # Standard diagnostic with gateway
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
        
        # Add gateway stats
        if test_type in ["full", "configuration"]:
            response_data["gateway_stats"] = execute_operation(
                GatewayInterface.DEBUG, 
                'get_gateway_stats'
            )
        
        # Add Home Assistant diagnostic info
        if test_type == "full":
            try:
                from homeassistant_extension import get_ha_diagnostic_info
                response_data["home_assistant"] = get_ha_diagnostic_info()
            except Exception as e:
                log_error(f"Diagnostic info failed: {str(e)}")
                response_data["home_assistant"] = {}
        
        # Add environment info (sanitized)
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
    """
    Network connectivity test - bypasses all LEE systems.
    Direct urllib3 testing to HA.
    """
    
    print(f"[NETWORK_TEST] Starting network connectivity test")
    print(f"[NETWORK_TEST] Request ID: {context.aws_request_id}")
    
    # Load configuration
    ha_url = os.getenv('HOME_ASSISTANT_URL')
    ha_token = os.getenv('HOME_ASSISTANT_TOKEN')
    verify_ssl = os.getenv('HOME_ASSISTANT_VERIFY_SSL', 'true').lower() != 'false'
    
    print(f"[NETWORK_TEST] HA URL: {ha_url}")
    print(f"[NETWORK_TEST] Token present: {bool(ha_token)}")
    print(f"[NETWORK_TEST] Verify SSL: {verify_ssl}")
    
    if not ha_url:
        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": "HOME_ASSISTANT_URL not configured",
                "test_type": "network_test"
            })
        }
    
    # Test basic connectivity
    try:
        http = urllib3.PoolManager(
            cert_reqs='CERT_REQUIRED' if verify_ssl else 'CERT_NONE',
            timeout=urllib3.Timeout(connect=5.0, read=10.0)
        )
        
        # Try to reach HA API endpoint
        api_url = f"{ha_url}/api/"
        print(f"[NETWORK_TEST] Testing connection to: {api_url}")
        
        headers = {}
        if ha_token:
            headers['Authorization'] = f'Bearer {ha_token}'
        
        response = http.request('GET', api_url, headers=headers)
        
        print(f"[NETWORK_TEST] Response status: {response.status}")
        print(f"[NETWORK_TEST] Response headers: {dict(response.headers)}")
        
        return {
            "statusCode": 200,
            "body": json.dumps({
                "test_type": "network_test",
                "success": True,
                "ha_url": ha_url,
                "response_status": response.status,
                "response_headers": dict(response.headers),
                "ssl_verified": verify_ssl
            })
        }
        
    except Exception as e:
        print(f"[NETWORK_TEST] Error: {type(e).__name__}: {str(e)}")
        
        return {
            "statusCode": 500,
            "body": json.dumps({
                "test_type": "network_test",
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__,
                "ha_url": ha_url
            })
        }

# EOF
