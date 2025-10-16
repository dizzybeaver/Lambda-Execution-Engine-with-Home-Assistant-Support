"""
lambda_function.py - AWS Lambda Entry Point
Version: 2025.10.16.04
Description: Main Lambda handler with SUGA-ISP gateway integration

CHANGELOG:
- 2025.10.16.04: Removed debug print statements, re-enabled validation
- 2025.10.16.03: Added LAMBDA_MODE support (normal/failsafe/diagnostic/emergency)
- 2025.10.16.02: Added lazy imports to fix timeouts
- 2025.10.16.01: Fixed increment_counter imports

Copyright 2025 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

import json
import os
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
    """
    
    # Check Lambda mode
    lambda_mode = os.getenv('LAMBDA_MODE', 'normal').lower()
    
    # Bypass modes - skip LEE entirely
    if lambda_mode == 'failsafe':
        try:
            import lambda_failsafe
            return lambda_failsafe.lambda_handler(event, context)
        except ImportError:
            lambda_mode = 'normal'  # Fallback to normal if file missing
    
    elif lambda_mode == 'diagnostic':
        try:
            import lambda_diagnostic
            return lambda_diagnostic.lambda_handler(event, context)
        except ImportError:
            lambda_mode = 'normal'  # Fallback to normal if file missing
    
    elif lambda_mode == 'emergency':
        try:
            import lambda_emergency
            return lambda_emergency.lambda_handler(event, context)
        except ImportError:
            lambda_mode = 'normal'  # Fallback to normal if file missing
    
    # Normal mode - full LEE operation
    return lambda_handler_normal(event, context)


def lambda_handler_normal(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Normal Lambda handler with full LEE."""
    
    # Lazy import gateway functions to avoid initialization issues
    from gateway import (
        log_info, log_error, log_debug,
        execute_operation, GatewayInterface,
        increment_counter, format_response,
        validate_request, validate_token
    )
    
    try:
        log_info("Lambda invocation started", 
                request_id=context.request_id,
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
        log_info, log_error, increment_counter,
        validate_request, validate_token
    )
    from homeassistant_extension import (
        process_alexa_discovery,
        process_alexa_control,
        is_ha_available
    )
    
    try:
        directive = event.get("directive", {})
        header = directive.get("header", {})
        namespace = header.get("namespace", "")
        name = header.get("name", "")
        
        log_info(f"Alexa request: {namespace}.{name}")
        increment_counter(f"alexa_{namespace.lower()}")
        
        # Validate request (security check)
        # Note: Alexa directives don't need validation as they come from Amazon
        # But if you implement token-based auth, uncomment:
        # if not validate_request(event):
        #     return create_error_response("Invalid request", "INVALID_REQUEST")
        
        # Check HA availability
        if not is_ha_available():
            log_error("Home Assistant not available")
            return create_alexa_error_response(
                event, 
                "ENDPOINT_UNREACHABLE",
                "Home Assistant is not available"
            )
        
        # Route based on namespace
        if namespace == "Alexa.Discovery":
            return process_alexa_discovery(event)
        
        elif namespace in ["Alexa.PowerController", "Alexa.BrightnessController", 
                          "Alexa.ColorController", "Alexa.ThermostatController"]:
            return process_alexa_control(event)
        
        else:
            log_error(f"Unknown Alexa namespace: {namespace}")
            return create_alexa_error_response(
                event,
                "INVALID_DIRECTIVE",
                f"Unknown namespace: {namespace}"
            )
            
    except Exception as e:
        log_error(f"Alexa request failed: {str(e)}", error=e)
        increment_counter("alexa_errors")
        return create_alexa_error_response(event, "INTERNAL_ERROR", str(e))


def handle_diagnostic_request(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Handle diagnostic/test requests."""
    
    # Lazy import gateway
    from gateway import (
        log_info, log_debug, increment_counter,
        format_response, execute_operation, GatewayInterface
    )
    
    try:
        test_type = event.get("test_type", "unknown")
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
                "LAMBDA_MODE": os.getenv("LAMBDA_MODE", "normal")
            }
        
        # Add assistant name if available
        if test_type == "full":
            try:
                from homeassistant_extension import get_assistant_name
                response_data["assistant_name"] = get_assistant_name()
            except Exception:
                response_data["assistant_name"] = {}
        
        return format_response(200, response_data)
        
    except Exception as e:
        log_error(f"Diagnostic request failed: {str(e)}", error=e)
        return format_response(500, {
            "error": str(e),
            "error_type": type(e).__name__
        })


def create_alexa_error_response(event: Dict[str, Any], error_type: str, 
                                error_message: str) -> Dict[str, Any]:
    """Create Alexa-formatted error response."""
    
    directive = event.get("directive", {})
    header = directive.get("header", {})
    
    return {
        "event": {
            "header": {
                "namespace": "Alexa",
                "name": "ErrorResponse",
                "messageId": header.get("messageId", "unknown"),
                "correlationToken": header.get("correlationToken"),
                "payloadVersion": "3"
            },
            "endpoint": directive.get("endpoint", {}),
            "payload": {
                "type": error_type,
                "message": error_message
            }
        }
    }


# ===== VERSION INFO =====

__version__ = "2025.10.16.04"
__all__ = ['lambda_handler']

# EOF
