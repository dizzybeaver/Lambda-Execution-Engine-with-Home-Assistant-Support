"""
lambda_function.py - AWS Lambda Entry Point
Version: 2025.10.19.02
Description: Main Lambda handler with SUGA-ISP gateway integration

CHANGELOG:
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


def _debug(msg: str):
    """Print debug unconditionally."""
    print(f"[DEBUG] {msg}")


# ===== LAMBDA MODE SELECTION =====

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """AWS Lambda entry point with mode selection."""
    
    _debug("═══════════════════════════════════════════════════")
    _debug("LAMBDA_HANDLER: Entry point started")
    _debug("═══════════════════════════════════════════════════")
    _debug(f"Request ID: {context.aws_request_id}")
    _debug(f"Function: {context.function_name}")
    _debug(f"Memory: {context.memory_limit_in_mb}MB")
    _debug(f"Event keys: {list(event.keys())}")
    
    lambda_mode = os.getenv('LAMBDA_MODE', 'normal').lower()
    _debug(f"LAMBDA_MODE: {lambda_mode}")
    
    if lambda_mode == 'failsafe':
        _debug("MODE: Attempting failsafe import")
        try:
            import lambda_failsafe
            _debug("MODE: Failsafe imported, calling handler")
            return lambda_failsafe.lambda_handler(event, context)
        except ImportError as e:
            _debug(f"MODE: Failsafe import failed: {e}")
            lambda_mode = 'normal'
    
    elif lambda_mode == 'diagnostic':
        _debug("MODE: Attempting diagnostic import")
        try:
            import lambda_diagnostic
            _debug("MODE: Diagnostic imported, calling handler")
            return lambda_diagnostic.lambda_handler(event, context)
        except ImportError as e:
            _debug(f"MODE: Diagnostic import failed: {e}")
            lambda_mode = 'normal'
    
    elif lambda_mode == 'emergency':
        _debug("MODE: Attempting emergency import")
        try:
            import lambda_emergency
            _debug("MODE: Emergency imported, calling handler")
            return lambda_emergency.lambda_handler(event, context)
        except ImportError as e:
            _debug(f"MODE: Emergency import failed: {e}")
            lambda_mode = 'normal'
    
    elif lambda_mode == 'ha_connection_test':
        _debug("MODE: Attempting ha_connection_test import")
        try:
            import lambda_ha_connection
            _debug("MODE: HA connection test imported, calling handler")
            return lambda_ha_connection.lambda_handler(event, context)
        except ImportError as e:
            _debug(f"MODE: HA connection test import failed: {e}")
            lambda_mode = 'normal'
    
    elif lambda_mode == 'ha_discovery':
        _debug("MODE: Attempting ha_discovery import")
        try:
            import debug_discovery
            _debug("MODE: Debug discovery imported, calling handler")
            return debug_discovery.lambda_handler(event, context)
        except ImportError as e:
            _debug(f"MODE: Debug discovery import failed: {e}")
            lambda_mode = 'normal'
    
    _debug("MODE: Using normal mode - calling lambda_handler_normal")
    return lambda_handler_normal(event, context)


def lambda_handler_normal(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Normal Lambda handler with full LEE."""
    
    _debug("───────────────────────────────────────────────────")
    _debug("LAMBDA_HANDLER_NORMAL: Started")
    _debug("───────────────────────────────────────────────────")
    
    _debug("NORMAL: Importing gateway functions...")
    try:
        from gateway import (
            log_info, log_error, log_debug,
            execute_operation, GatewayInterface,
            increment_counter, format_response,
            validate_request, validate_token
        )
        _debug("NORMAL: Gateway imports successful")
    except Exception as e:
        _debug(f"NORMAL: Gateway import FAILED: {type(e).__name__}: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": f"Gateway import failed: {str(e)}"})
        }
    
    try:
        _debug(f"NORMAL: Logging start with request_id={context.aws_request_id}")
        log_info("Lambda invocation started", 
                request_id=context.aws_request_id,
                function_name=context.function_name,
                memory_limit=context.memory_limit_in_mb,
                remaining_time=context.get_remaining_time_in_millis())
        _debug("NORMAL: log_info successful")
        
        _debug("NORMAL: Incrementing counter")
        increment_counter("lambda_invocations")
        _debug("NORMAL: Counter incremented")
        
        _debug("NORMAL: Determining request type")
        request_type = determine_request_type(event)
        _debug(f"NORMAL: Request type determined: {request_type}")
        
        log_debug(f"Request type: {request_type}")
        
        if request_type == "alexa":
            _debug("NORMAL: Routing to handle_alexa_request")
            return handle_alexa_request(event, context)
        elif request_type == "diagnostic":
            _debug("NORMAL: Routing to handle_diagnostic_request")
            return handle_diagnostic_request(event, context)
        else:
            _debug(f"NORMAL: Unknown request type: {request_type}")
            return format_response(400, {
                "error": "Unknown request type",
                "event": event
            })
            
    except Exception as e:
        _debug(f"NORMAL: Exception caught: {type(e).__name__}: {e}")
        import traceback
        _debug(f"NORMAL: Traceback:\n{traceback.format_exc()}")
        log_error("Lambda execution failed", error=e)
        return format_response(500, {
            "error": str(e),
            "error_type": type(e).__name__
        })


def determine_request_type(event: Dict[str, Any]) -> str:
    """Determine the type of request from the event structure."""
    
    _debug("───────────────────────────────────────────────────")
    _debug("DETERMINE_REQUEST_TYPE: Started")
    _debug(f"DETERMINE: Event keys: {list(event.keys())}")
    
    if "directive" in event:
        _debug("DETERMINE: Found 'directive' - returning 'alexa'")
        return "alexa"
    
    if "test_type" in event:
        _debug("DETERMINE: Found 'test_type' - returning 'diagnostic'")
        return "diagnostic"
    
    _debug("DETERMINE: No known markers - returning 'unknown'")
    return "unknown"


def handle_alexa_request(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Handle Alexa Smart Home requests."""
    
    _debug("───────────────────────────────────────────────────")
    _debug("HANDLE_ALEXA_REQUEST: Started")
    _debug("───────────────────────────────────────────────────")
    
    _debug("ALEXA: Importing gateway functions...")
    try:
        from gateway import (
            log_info, log_error, log_warning, increment_counter,
            validate_request, validate_token
        )
        _debug("ALEXA: Gateway imports successful")
    except Exception as e:
        _debug(f"ALEXA: Gateway import FAILED: {e}")
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
                    "message": f"Gateway import failed: {str(e)}"
                }
            }
        }
    
    _debug("ALEXA: Importing homeassistant_extension...")
    try:
        from homeassistant_extension import (
            handle_alexa_discovery,
            handle_alexa_control,
            handle_alexa_authorization,
            is_ha_extension_enabled,
            get_ha_status
        )
        _debug("ALEXA: HA extension imports successful")
    except Exception as e:
        _debug(f"ALEXA: HA extension import FAILED: {e}")
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
                    "message": f"HA extension import failed: {str(e)}"
                }
            }
        }
    
    try:
        directive = event.get("directive", {})
        _debug(f"ALEXA: Directive keys: {list(directive.keys())}")
        
        header = directive.get("header", {})
        _debug(f"ALEXA: Header keys: {list(header.keys())}")
        
        namespace = header.get("namespace", "")
        name = header.get("name", "")
        _debug(f"ALEXA: namespace={namespace}, name={name}")
        
        log_info(f"Alexa request: {namespace}.{name}")
        increment_counter(f"alexa_{namespace.lower()}")
        
        _debug("ALEXA: Checking if HA extension enabled...")
        if not is_ha_extension_enabled():
            _debug("ALEXA: HA extension is DISABLED")
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
        
        _debug("ALEXA: HA extension is ENABLED")
        _debug(f"ALEXA: Routing by namespace: {namespace}")
        
        if namespace == "Alexa.Discovery":
            _debug("ALEXA: Calling handle_alexa_discovery")
            result = handle_alexa_discovery(event)
            _debug(f"ALEXA: handle_alexa_discovery returned, type={type(result)}")
            return result
        
        elif namespace == "Alexa.Authorization":
            _debug("ALEXA: Calling handle_alexa_authorization")
            result = handle_alexa_authorization(event)
            _debug(f"ALEXA: handle_alexa_authorization returned, type={type(result)}")
            return result
        
        elif namespace in ["Alexa.PowerController", "Alexa.BrightnessController",
                          "Alexa.ColorController", "Alexa.ColorTemperatureController",
                          "Alexa.ThermostatController", "Alexa.LockController",
                          "Alexa"]:
            _debug(f"ALEXA: Calling handle_alexa_control for {namespace}")
            result = handle_alexa_control(event)
            _debug(f"ALEXA: handle_alexa_control returned, type={type(result)}")
            return result
        
        else:
            _debug(f"ALEXA: Unsupported namespace: {namespace}")
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
        _debug(f"ALEXA: Exception caught: {type(e).__name__}: {e}")
        import traceback
        _debug(f"ALEXA: Traceback:\n{traceback.format_exc()}")
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
    
    _debug("───────────────────────────────────────────────────")
    _debug("HANDLE_DIAGNOSTIC_REQUEST: Started")
    _debug("───────────────────────────────────────────────────")
    
    test_type = event.get("test_type", "unknown")
    _debug(f"DIAGNOSTIC: test_type={test_type}")
    
    if test_type in ['network_test', 'ha_ping']:
        _debug("DIAGNOSTIC: Routing to handle_network_test")
        return handle_network_test(event, context)
    
    _debug("DIAGNOSTIC: Importing gateway functions...")
    from gateway import (
        log_info, log_debug, log_error, increment_counter,
        format_response, execute_operation, GatewayInterface
    )
    _debug("DIAGNOSTIC: Gateway imports successful")
    
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
        _debug(f"DIAGNOSTIC: Exception: {type(e).__name__}: {e}")
        log_error(f"Diagnostic failed: {str(e)}", error=e)
        return format_response(500, {
            "error": str(e),
            "error_type": type(e).__name__
        })


def handle_network_test(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Network connectivity test - bypasses all LEE systems."""
    
    _debug("───────────────────────────────────────────────────")
    _debug("HANDLE_NETWORK_TEST: Started")
    _debug("───────────────────────────────────────────────────")
    
    ha_url = os.getenv('HOME_ASSISTANT_URL')
    ha_token = os.getenv('HOME_ASSISTANT_TOKEN')
    verify_ssl = os.getenv('HOME_ASSISTANT_VERIFY_SSL', 'true').lower() != 'false'
    
    _debug(f"NETWORK_TEST: HA URL: {ha_url}")
    _debug(f"NETWORK_TEST: Token present: {bool(ha_token)}")
    _debug(f"NETWORK_TEST: Verify SSL: {verify_ssl}")
    
    if not ha_url:
        _debug("NETWORK_TEST: No HA URL configured")
        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": "HOME_ASSISTANT_URL not configured",
                "test_type": "network_test"
            })
        }
    
    try:
        _debug("NETWORK_TEST: Creating HTTP client")
        http = urllib3.PoolManager(
            cert_reqs='CERT_REQUIRED' if verify_ssl else 'CERT_NONE',
            timeout=urllib3.Timeout(connect=5.0, read=10.0)
        )
        
        api_url = f"{ha_url}/api/"
        _debug(f"NETWORK_TEST: Testing connection to: {api_url}")
        
        headers = {}
        if ha_token:
            headers['Authorization'] = f'Bearer {ha_token}'
        
        _debug("NETWORK_TEST: Making HTTP request...")
        response = http.request('GET', api_url, headers=headers)
        
        _debug(f"NETWORK_TEST: Response status: {response.status}")
        _debug(f"NETWORK_TEST: Success!")
        
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
        _debug(f"NETWORK_TEST: Error: {type(e).__name__}: {str(e)}")
        
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
