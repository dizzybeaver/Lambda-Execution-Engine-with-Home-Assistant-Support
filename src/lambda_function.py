"""
lambda_function.py - AWS Lambda Entry Point (DIAGNOSTIC WITH TIMING)
Version: 2025.10.19.DIAG_PRINT
Description: Production code with print() timing to find the 10.5 second delay

CHANGELOG:
- 2025.10.19.DIAG_PRINT: Added print() timing throughout production code
  - Uses print() instead of log_info() (logging system appears broken)
  - Times every major operation
  - Shows exactly where the 10.5 seconds is spent
  - TEMPORARY - Remove timing after diagnosis

Copyright 2025 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

import json
import os
import time

# PERFORMANCE OPTIMIZATION: Module-level imports
import urllib3
from typing import Dict, Any

# Track timing from module load
_MODULE_LOAD_TIME = time.time()

# PERFORMANCE OPTIMIZATION: Pre-import gateway functions
print(f"[TIMING] Starting gateway imports at module level...")
_start = time.time()
from gateway import (
    log_info, log_error, log_debug,
    execute_operation, GatewayInterface,
    increment_counter, format_response,
    validate_request, validate_token
)
_gateway_import_ms = (time.time() - _start) * 1000
print(f"[TIMING] Gateway imports complete: {_gateway_import_ms:.2f}ms")


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """AWS Lambda entry point with mode selection."""
    
    handler_start = time.time()
    print(f"[TIMING] ===== LAMBDA HANDLER START =====")
    print(f"[TIMING] Request ID: {context.aws_request_id}")
    print(f"[TIMING] Memory: {context.memory_limit_in_mb}MB")
    
    lambda_mode = os.getenv('LAMBDA_MODE', 'normal').lower()
    mode_time = (time.time() - handler_start) * 1000
    print(f"[TIMING] Mode selection ({lambda_mode}): +{mode_time:.2f}ms")
    
    if lambda_mode == 'failsafe':
        print(f"[TIMING] Importing lambda_failsafe...")
        import_start = time.time()
        try:
            import lambda_failsafe
            import_ms = (time.time() - import_start) * 1000
            print(f"[TIMING] lambda_failsafe imported: {import_ms:.2f}ms")
            return lambda_failsafe.lambda_handler(event, context)
        except ImportError:
            lambda_mode = 'normal'
            print(f"[TIMING] lambda_failsafe not found, using normal")
    
    elif lambda_mode == 'diagnostic':
        print(f"[TIMING] Importing lambda_diagnostic...")
        import_start = time.time()
        try:
            import lambda_diagnostic
            import_ms = (time.time() - import_start) * 1000
            print(f"[TIMING] lambda_diagnostic imported: {import_ms:.2f}ms")
            return lambda_diagnostic.lambda_handler(event, context)
        except ImportError:
            lambda_mode = 'normal'
            print(f"[TIMING] lambda_diagnostic not found, using normal")
    
    elif lambda_mode == 'emergency':
        print(f"[TIMING] Importing lambda_emergency...")
        import_start = time.time()
        try:
            import lambda_emergency
            import_ms = (time.time() - import_start) * 1000
            print(f"[TIMING] lambda_emergency imported: {import_ms:.2f}ms")
            return lambda_emergency.lambda_handler(event, context)
        except ImportError:
            lambda_mode = 'normal'
            print(f"[TIMING] lambda_emergency not found, using normal")
    
    elif lambda_mode == 'ha_connection_test':
        print(f"[TIMING] Importing lambda_ha_connection...")
        import_start = time.time()
        try:
            import lambda_ha_connection
            import_ms = (time.time() - import_start) * 1000
            print(f"[TIMING] lambda_ha_connection imported: {import_ms:.2f}ms")
            return lambda_ha_connection.lambda_handler(event, context)
        except ImportError:
            lambda_mode = 'normal'
            print(f"[TIMING] lambda_ha_connection not found, using normal")
    
    elif lambda_mode == 'ha_discovery':
        print(f"[TIMING] Importing debug_discovery...")
        import_start = time.time()
        try:
            import debug_discovery
            import_ms = (time.time() - import_start) * 1000
            print(f"[TIMING] debug_discovery imported: {import_ms:.2f}ms")
            return debug_discovery.lambda_handler(event, context)
        except ImportError:
            lambda_mode = 'normal'
            print(f"[TIMING] debug_discovery not found, using normal")
    
    print(f"[TIMING] Using normal handler")
    return lambda_handler_normal(event, context)


def lambda_handler_normal(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Normal Lambda handler with full LEE."""
    
    handler_start = time.time()
    print(f"[TIMING] ===== NORMAL HANDLER START =====")
    
    try:
        # First log_info call
        print(f"[TIMING] Calling log_info() for first time...")
        log_start = time.time()
        log_info("Lambda invocation started", 
                request_id=context.aws_request_id,
                function_name=context.function_name,
                memory_limit=context.memory_limit_in_mb,
                remaining_time=context.get_remaining_time_in_millis())
        log_ms = (time.time() - log_start) * 1000
        print(f"[TIMING] log_info() completed: {log_ms:.2f}ms")
        
        # Increment counter
        print(f"[TIMING] Calling increment_counter()...")
        counter_start = time.time()
        increment_counter("lambda.invocations")
        counter_ms = (time.time() - counter_start) * 1000
        print(f"[TIMING] increment_counter() completed: {counter_ms:.2f}ms")
        
        # Determine request type
        print(f"[TIMING] Determining request type...")
        type_start = time.time()
        request_type = determine_request_type(event)
        type_ms = (time.time() - type_start) * 1000
        print(f"[TIMING] Request type determined ({request_type}): {type_ms:.2f}ms")
        
        # Route to appropriate handler
        total_before_routing = (time.time() - handler_start) * 1000
        print(f"[TIMING] *** TOTAL BEFORE ROUTING: {total_before_routing:.2f}ms ***")
        
        if request_type == 'alexa':
            print(f"[TIMING] Routing to Alexa handler...")
            routing_start = time.time()
            result = handle_alexa_request(event, context)
            routing_ms = (time.time() - routing_start) * 1000
            print(f"[TIMING] Alexa handler completed: {routing_ms:.2f}ms")
            
        elif request_type == 'diagnostic':
            print(f"[TIMING] Routing to diagnostic handler...")
            routing_start = time.time()
            result = handle_diagnostic_request(event, context)
            routing_ms = (time.time() - routing_start) * 1000
            print(f"[TIMING] Diagnostic handler completed: {routing_ms:.2f}ms")
            
        else:
            print(f"[TIMING] Unknown request type: {request_type}")
            result = format_response(400, {"error": f"Unknown request type: {request_type}"})
        
        total_ms = (time.time() - handler_start) * 1000
        print(f"[TIMING] *** TOTAL HANDLER TIME: {total_ms:.2f}ms ***")
        
        return result
        
    except Exception as e:
        error_time = (time.time() - handler_start) * 1000
        print(f"[TIMING] !!! ERROR after {error_time:.2f}ms: {str(e)}")
        log_error(f"Lambda handler error: {str(e)}", 
                 request_id=context.aws_request_id,
                 error_type=type(e).__name__)
        return format_response(500, {"error": str(e)})


def determine_request_type(event: Dict[str, Any]) -> str:
    """Determine the type of request."""
    if 'directive' in event:
        return 'alexa'
    elif 'test_type' in event or 'health_check' in event:
        return 'diagnostic'
    else:
        return 'unknown'


def handle_alexa_request(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Handle Alexa Smart Home requests with full namespace routing."""
    
    alexa_start = time.time()
    print(f"[TIMING] ===== ALEXA REQUEST HANDLER =====")
    
    try:
        # Extract namespace
        directive = event.get('directive', {})
        header = directive.get('header', {})
        namespace = header.get('namespace', '')
        name = header.get('name', '')
        
        print(f"[TIMING] Processing: {namespace}.{name}")
        
        # Import homeassistant_extension
        print(f"[TIMING] Importing homeassistant_extension module...")
        import_start = time.time()
        from homeassistant_extension import (
            handle_alexa_discovery,
            handle_alexa_authorization,
            handle_alexa_control
        )
        import_ms = (time.time() - import_start) * 1000
        print(f"[TIMING] *** homeassistant_extension imported: {import_ms:.2f}ms ***")
        
        # Route based on namespace
        if namespace == 'Alexa.Discovery':
            print(f"[TIMING] Routing to Discovery handler...")
            route_start = time.time()
            result = handle_alexa_discovery(event)
            route_ms = (time.time() - route_start) * 1000
            print(f"[TIMING] Discovery handler: {route_ms:.2f}ms")
            
        elif namespace == 'Alexa.Authorization':
            print(f"[TIMING] Routing to Authorization handler...")
            route_start = time.time()
            result = handle_alexa_authorization(event)
            route_ms = (time.time() - route_start) * 1000
            print(f"[TIMING] Authorization handler: {route_ms:.2f}ms")
            
        else:
            # All other controllers (Power, Brightness, Color, etc.)
            print(f"[TIMING] Routing to Control handler for {namespace}...")
            route_start = time.time()
            result = handle_alexa_control(event)
            route_ms = (time.time() - route_start) * 1000
            print(f"[TIMING] *** Control handler: {route_ms:.2f}ms ***")
        
        total_ms = (time.time() - alexa_start) * 1000
        print(f"[TIMING] *** TOTAL ALEXA REQUEST: {total_ms:.2f}ms ***")
        
        return result
        
    except Exception as e:
        error_time = (time.time() - alexa_start) * 1000
        print(f"[TIMING] !!! ALEXA ERROR after {error_time:.2f}ms: {str(e)}")
        log_error(f"Alexa request failed: {namespace}.{name}", 
                 error=str(e),
                 error_type=type(e).__name__,
                 namespace=namespace,
                 name=name)
        
        return {
            "event": {
                "header": {
                    "namespace": "Alexa",
                    "name": "ErrorResponse",
                    "messageId": header.get('messageId', 'unknown'),
                    "payloadVersion": "3"
                },
                "payload": {
                    "type": "INTERNAL_ERROR",
                    "message": str(e)
                }
            }
        }


def handle_diagnostic_request(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Handle diagnostic test requests."""
    
    diag_start = time.time()
    print(f"[TIMING] ===== DIAGNOSTIC REQUEST HANDLER =====")
    
    test_type = event.get('test_type', 'health_check')
    print(f"[TIMING] Test type: {test_type}")
    
    response = {
        "statusCode": 200,
        "body": json.dumps({
            "status": "ok",
            "test_type": test_type,
            "request_id": context.aws_request_id,
            "function_name": context.function_name,
            "memory_limit_mb": context.memory_limit_in_mb,
            "remaining_time_ms": context.get_remaining_time_in_millis()
        })
    }
    
    diag_ms = (time.time() - diag_start) * 1000
    print(f"[TIMING] Diagnostic completed: {diag_ms:.2f}ms")
    
    return response


# EOF
