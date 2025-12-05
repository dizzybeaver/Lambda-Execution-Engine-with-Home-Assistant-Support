# lambda_function.py
"""
lambda_function.py - AWS Lambda Entry Point (SELECTIVE IMPORTS + LUGS + HA-SUGA)
Version: 2025.12.05.1
Description: Production code with lambda_preload + HA-SUGA subdirectory + LWA OAuth

CHANGES (2025.12.05.1 - LWA MIGRATION):
- ADDED: OAuth token extraction from Alexa directives
- ADDED: Token passing to HA handlers
- KEPT: All mode routing, timing, sys.path fix, lambda_preload

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

# Check if Home Assistant extension is enabled
HA_ENABLED = os.getenv('HOME_ASSISTANT_ENABLE', 'false').lower() == 'true'
HA_AVAILABLE = False

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


# ===== LWA OAUTH TOKEN EXTRACTION =====

def _extract_oauth_token(event: Dict[str, Any]) -> str:
    """
    Extract OAuth token from Alexa directive.
    
    LWA Migration: Token from directive, not config.
    
    Args:
        event: Alexa Smart Home event
        
    Returns:
        OAuth token string
        
    Raises:
        ValueError: If no token found
    """
    directive = event.get('directive', {})
    
    # Try endpoint.scope.token (control directives)
    endpoint = directive.get('endpoint', {})
    scope = endpoint.get('scope', {})
    token = scope.get('token')
    
    if token:
        log_debug('OAuth token extracted from directive.endpoint.scope')
        return token
    
    # Try payload.scope.token (discovery/grant)
    payload = directive.get('payload', {})
    scope = payload.get('scope', {})
    token = scope.get('token')
    
    if token:
        log_debug('OAuth token extracted from directive.payload.scope')
        return token
    
    log_error('No OAuth token in Alexa directive')
    raise ValueError('No OAuth token in directive')


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
            return lambda_failsafe.lambda_failsafe_handler(event, context)
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


def handle_alexa_request(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Handle Alexa Smart Home requests.
    
    LWA Migration: Extracts OAuth token and passes to HA.
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
        
        # LWA Migration: Extract OAuth token
        try:
            oauth_token = _extract_oauth_token(event)
            log_debug(f'OAuth token extracted (length={len(oauth_token)})')
            # Add token to event for HA processing
            event['oauth_token'] = oauth_token
        except ValueError as e:
            log_error(f'OAuth token extraction failed: {str(e)}')
            increment_counter('oauth_token_missing')
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
                        'type': 'INVALID_AUTHORIZATION_CREDENTIAL',
                        'message': 'Account linking required. Please link your account in the Alexa app.'
                    }
                }
            }
        
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
