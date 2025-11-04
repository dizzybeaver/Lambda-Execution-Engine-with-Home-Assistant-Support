# lambda_function.py
"""
lambda_function.py - AWS Lambda Entry Point (SELECTIVE IMPORTS + LUGS + HA-SUGA)
Version: 2025.1104.1
Description: Production code with lambda_preload + HA-SUGA subdirectory

CHANGELOG:
- 2025.1104.1: PHASE 6 - Complete HA-SUGA Migration
  * REMOVED: Fallback to old homeassistant_extension
  * MODIFIED: Alexa routing - HA-SUGA only (no fallback)
  * ADDED: Proper error handling when HA disabled
  * PHASE 6 CLEANUP: All old HA code paths removed
- 2025.11.03.HA_SUGA: PHASE 2 - HA-SUGA Integration
  * ADDED: sys.path fix for subdirectory imports
  * ADDED: HOME_ASSISTANT_ENABLE environment variable check
  * ADDED: Conditional import of home_assistant.ha_interconnect
- 2025.10.19.TIMING_FIX: Added DEBUG_MODE check for all timing logs
- 2025.10.19.SELECTIVE: Import lambda_preload FIRST for LUGS preloading

CRITICAL CHANGES (Phase 6):
1. HA-SUGA ONLY: No fallback to old homeassistant_extension
2. Clean separation: LEE works without HA when disabled
3. Proper error responses when HA needed but not enabled

Performance Impact:
- BEFORE: 239ms INIT + 10,615ms first request = 10,854ms total
- AFTER (LUGS): 400ms INIT + 150ms first request = 550ms total
- HA-SUGA: No impact when disabled, minimal when enabled (lazy imports)

Copyright 2025 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

# ===== CRITICAL: sys.path fix for subdirectory imports =====
# This MUST be first, before any imports
import sys
import os

# Ensure lambda_function.py's directory is in sys.path
# This allows subdirectory imports like: from home_assistant import ha_interconnect
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# ===== STANDARD IMPORTS =====
import json
import time
from typing import Dict, Any

# ===== CRITICAL: Import lambda_preload FIRST! =====
# This triggers all preloading during Lambda INIT (happens in background)
# Module-level imports load BEFORE first request, user doesn't wait!
import lambda_preload  # Preloads: typing, enum, urllib3 (selective), boto3 SSM (selective)

# ===== TIMING HELPER =====

def _is_debug_mode() -> bool:
    """Check if DEBUG_MODE is enabled."""
    return os.environ.get('DEBUG_MODE', 'false').lower() == 'true'


def _print_timing(msg: str):
    """Print timing message only if DEBUG_MODE=true."""
    if _is_debug_mode():
        print(f"[TIMING] {msg}")


# ===== PERFORMANCE OPTIMIZATION: Pre-import gateway functions =====
_timing_start = time.perf_counter()
_print_timing("Starting gateway imports at module level...")

from gateway import (
    log_info, log_error, log_debug,
    execute_operation, GatewayInterface,
    increment_counter, format_response,
    validate_request, validate_token
)

_gateway_time = (time.perf_counter() - _timing_start) * 1000
_print_timing(f"Gateway imports complete: {_gateway_time:.2f}ms")

# ===== PHASE 2/6: HA-SUGA INTEGRATION =====
# Check if Home Assistant extension is enabled
HA_ENABLED = os.getenv('HOME_ASSISTANT_ENABLE', 'false').lower() == 'true'
HA_AVAILABLE = False

# PHASE 6: Conditionally import HA-SUGA interconnect (NO FALLBACK)
if HA_ENABLED:
    _ha_start = time.perf_counter()
    _print_timing("HOME_ASSISTANT_ENABLE=true, loading HA-SUGA...")
    try:
        from home_assistant import ha_interconnect
        HA_AVAILABLE = True
        _ha_time = (time.perf_counter() - _ha_start) * 1000
        _print_timing(f"HA-SUGA loaded: {_ha_time:.2f}ms")
        log_info("HA-SUGA extension loaded successfully")
    except ImportError as e:
        _ha_time = (time.perf_counter() - _ha_start) * 1000
        _print_timing(f"HA-SUGA import failed after {_ha_time:.2f}ms: {e}")
        log_error(f"Failed to import HA-SUGA: {e}")
        HA_AVAILABLE = False
else:
    _print_timing("HOME_ASSISTANT_ENABLE=false, HA-SUGA not loaded")


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """AWS Lambda entry point with mode selection."""
    
    handler_start = time.perf_counter()
    _print_timing("===== LAMBDA HANDLER START =====")
    _print_timing(f"Request ID: {context.aws_request_id}")
    _print_timing(f"Memory: {context.memory_limit_in_mb}MB")
    
    lambda_mode = os.getenv('LAMBDA_MODE', 'normal').lower()
    mode_time = (time.perf_counter() - handler_start) * 1000
    _print_timing(f"Mode selection ({lambda_mode}): +{mode_time:.2f}ms")
    
    # Mode routing (for debug/diagnostic handlers)
    if lambda_mode == 'failsafe':
        _print_timing("Importing lambda_failsafe...")
        import_start = time.perf_counter()
        try:
            import lambda_failsafe
            import_ms = (time.perf_counter() - import_start) * 1000
            _print_timing(f"lambda_failsafe imported: {import_ms:.2f}ms")
            return lambda_failsafe.lambda_handler(event, context)
        except ImportError:
            lambda_mode = 'normal'
            _print_timing("lambda_failsafe not found, using normal")
    
    elif lambda_mode == 'diagnostic':
        _print_timing("Importing lambda_diagnostic...")
        import_start = time.perf_counter()
        try:
            import lambda_diagnostic
            import_ms = (time.perf_counter() - import_start) * 1000
            _print_timing(f"lambda_diagnostic imported: {import_ms:.2f}ms")
            return lambda_diagnostic.lambda_handler(event, context)
        except ImportError:
            lambda_mode = 'normal'
            _print_timing("lambda_diagnostic not found, using normal")
    
    elif lambda_mode == 'emergency':
        _print_timing("Importing lambda_emergency...")
        import_start = time.perf_counter()
        try:
            import lambda_emergency
            import_ms = (time.perf_counter() - import_start) * 1000
            _print_timing(f"lambda_emergency imported: {import_ms:.2f}ms")
            return lambda_emergency.lambda_handler(event, context)
        except ImportError:
            lambda_mode = 'normal'
            _print_timing("lambda_emergency not found, using normal")
    
    elif lambda_mode == 'ha_connection_test':
        _print_timing("Importing lambda_ha_connection...")
        import_start = time.perf_counter()
        try:
            import lambda_ha_connection
            import_ms = (time.perf_counter() - import_start) * 1000
            _print_timing(f"lambda_ha_connection imported: {import_ms:.2f}ms")
            return lambda_ha_connection.lambda_handler(event, context)
        except ImportError:
            lambda_mode = 'normal'
            _print_timing("lambda_ha_connection not found, using normal")
    
    elif lambda_mode == 'ha_discovery':
        _print_timing("Importing debug_discovery...")
        import_start = time.perf_counter()
        try:
            import debug_discovery
            import_ms = (time.perf_counter() - import_start) * 1000
            _print_timing(f"debug_discovery imported: {import_ms:.2f}ms")
            return debug_discovery.lambda_handler(event, context)
        except ImportError:
            lambda_mode = 'normal'
            _print_timing("debug_discovery not found, using normal")
    
    _print_timing("Using normal handler")
    return lambda_handler_normal(event, context)


def lambda_handler_normal(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Normal Lambda handler with full LEE."""
    
    normal_start = time.perf_counter()
    _print_timing("===== NORMAL HANDLER START =====")
    
    try:
        # Determine request type
        request_type = determine_request_type(event)
        type_time = (time.perf_counter() - normal_start) * 1000
        _print_timing(f"Request type determined ({request_type}): +{type_time:.2f}ms")
        
        # Route based on request type
        if request_type == 'alexa':
            result = handle_alexa_request(event, context)
        elif request_type == 'diagnostic':
            result = handle_diagnostic_request(event, context)
        else:
            result = handle_unknown_request(event, context)
        
        total_time = (time.perf_counter() - normal_start) * 1000
        _print_timing(f"*** TOTAL HANDLER TIME: {total_time:.2f}ms ***")
        
        return result
        
    except Exception as e:
        error_time = (time.perf_counter() - normal_start) * 1000
        _print_timing(f"!!! ERROR after {error_time:.2f}ms: {str(e)}")
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


def _is_ha_event(event: Dict[str, Any]) -> bool:
    """
    Determine if event is HA-related.
    
    PHASE 6: Helper function for HA event detection.
    """
    # Check for Alexa Smart Home directive
    if 'directive' in event:
        directive = event.get('directive', {})
        header = directive.get('header', {})
        namespace = header.get('namespace', '')
        if namespace.startswith('Alexa'):
            return True
    
    # Check for HA-specific event types
    event_type = event.get('type', '')
    if event_type in ['ha_devices', 'ha_assist', 'ha_alexa']:
        return True
    
    return False


def handle_alexa_request(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Handle Alexa Smart Home requests.
    
    PHASE 6: MODIFIED - HA-SUGA only, no fallback
    - Routes to ha_interconnect when HA_AVAILABLE=true
    - Returns error response if HA needed but not enabled
    """
    
    alexa_start = time.perf_counter()
    _print_timing("===== ALEXA REQUEST HANDLER =====")
    
    try:
        # Extract namespace
        directive = event.get('directive', {})
        header = directive.get('header', {})
        namespace = header.get('namespace', '')
        name = header.get('name', '')
        
        _print_timing(f"Processing: {namespace}.{name}")
        
        # PHASE 6: Check if HA is available
        if not HA_AVAILABLE:
            _print_timing("ERROR: Alexa request but HA not available")
            log_error("Alexa request received but HOME_ASSISTANT_ENABLE=false or HA import failed")
            increment_counter('alexa_ha_not_available')
            
            return {
                'event': {
                    'header': {
                        'namespace': 'Alexa',
                        'name': 'ErrorResponse',
                        'messageId': 'error',
                        'correlationToken': header.get('correlationToken'),
                        'payloadVersion': '3'
                    },
                    'payload': {
                        'type': 'BRIDGE_UNREACHABLE',
                        'message': 'Home Assistant extension not enabled. Set HOME_ASSISTANT_ENABLE=true'
                    }
                }
            }
        
        # PHASE 6: Route to HA-SUGA (only path)
        _print_timing("Routing to HA-SUGA (ha_interconnect)...")
        route_start = time.perf_counter()
        
        result = ha_interconnect.alexa_process_directive(event)
        
        route_ms = (time.perf_counter() - route_start) * 1000
        _print_timing(f"HA-SUGA handler: {route_ms:.2f}ms")
        
        total_ms = (time.perf_counter() - alexa_start) * 1000
        _print_timing(f"*** TOTAL ALEXA REQUEST: {total_ms:.2f}ms ***")
        
        return result
        
    except Exception as e:
        error_time = (time.perf_counter() - alexa_start) * 1000
        _print_timing(f"!!! ALEXA ERROR after {error_time:.2f}ms: {str(e)}")
        log_error(f"Alexa request error: {str(e)}")
        increment_counter('alexa_request_error')
        return {
            'event': {
                'header': {
                    'namespace': 'Alexa',
                    'name': 'ErrorResponse',
                    'messageId': 'error',
                    'payloadVersion': '3'
                },
                'payload': {
                    'type': 'INTERNAL_ERROR',
                    'message': str(e)
                }
            }
        }


def handle_diagnostic_request(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Handle diagnostic/health check requests."""
    log_info(f"Diagnostic request: {event.get('test_type', 'health_check')}")
    return format_response(200, {
        "status": "ok",
        "request_id": context.aws_request_id,
        "memory_limit_mb": context.memory_limit_in_mb,
        "remaining_time_ms": context.get_remaining_time_in_millis(),
        "ha_suga_enabled": HA_ENABLED,
        "ha_suga_available": HA_AVAILABLE
    })


def handle_unknown_request(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Handle unknown request types."""
    log_info(f"Unknown request type: {event}")
    return format_response(400, {
        "error": "Unknown request type",
        "event_keys": list(event.keys())
    })


# EOF
