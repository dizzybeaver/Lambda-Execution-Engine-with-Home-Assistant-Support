"""
lambda_function.py
Version: 2025-12-08_1
Purpose: AWS Lambda entry point with mode routing via TEST interface
License: Apache 2.0
"""

# CRITICAL: sys.path fix for subdirectory imports
import sys
import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
 
import json
import time
from typing import Dict, Any

# CRITICAL: Import lambda_preload FIRST
import lambda_preload

# Timing helper
def _is_debug_mode() -> bool:
    """Check if DEBUG_MODE is enabled."""
    return os.environ.get('DEBUG_MODE', 'false').lower() == 'true'


def _print_timing(msg: str):
    """Print timing message only if DEBUG_MODE=true."""
    if _is_debug_mode():
        print(f"[TIMING] {msg}")


# Performance optimization: Pre-import gateway functions
_timing_start = time.perf_counter()
_print_timing("Starting gateway imports at module level...")

from gateway import (
    log_info, log_error, log_debug,
    execute_operation, GatewayInterface,
    increment_counter, format_response,
    test_lambda_mode
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


def _extract_oauth_token(event: Dict[str, Any]) -> str:
    """Extract OAuth token from Alexa directive."""
    directive = event.get('directive', {})
    header = directive.get('header', {})
    
    log_info(f"[TOKEN_DEBUG] Checking event for OAuth token")
    log_info(f"[TOKEN_DEBUG] Namespace: {header.get('namespace')}, Name: {header.get('name')}")
    log_info(f"[TOKEN_DEBUG] Directive keys: {list(directive.keys())}")
    
    # Check 1: directive.endpoint.scope.token (control directives)
    endpoint = directive.get('endpoint', {})
    if endpoint:
        log_info(f"[TOKEN_DEBUG] Endpoint keys: {list(endpoint.keys())}")
        scope = endpoint.get('scope', {})
        if scope:
            log_info(f"[TOKEN_DEBUG] Endpoint.scope keys: {list(scope.keys())}")
            token = scope.get('token')
            if token:
                log_info(f'[TOKEN_DEBUG] ✓ Token found in directive.endpoint.scope (length={len(token)})')
                return token
    
    # Check 2: directive.payload.scope.token (discovery/grant)
    payload = directive.get('payload', {})
    if payload:
        log_info(f"[TOKEN_DEBUG] Payload keys: {list(payload.keys())}")
        scope = payload.get('scope', {})
        if scope:
            log_info(f"[TOKEN_DEBUG] Payload.scope keys: {list(scope.keys())}")
            token = scope.get('token')
            if token:
                log_info(f'[TOKEN_DEBUG] ✓ Token found in directive.payload.scope (length={len(token)})')
                return token
    
    # Check 3: directive.payload.grantee.token (AcceptGrant)
    if payload:
        grantee = payload.get('grantee', {})
        if grantee:
            log_info(f"[TOKEN_DEBUG] Payload.grantee keys: {list(grantee.keys())}")
            token = grantee.get('token')
            if token:
                log_info(f'[TOKEN_DEBUG] ✓ Token found in directive.payload.grantee (length={len(token)})')
                return token
    
    # Check 4: directive.payload.grant.code (authorization code grant)
    if payload:
        grant = payload.get('grant', {})
        if grant:
            log_info(f"[TOKEN_DEBUG] Payload.grant keys: {list(grant.keys())}")
            code = grant.get('code')
            if code:
                log_info(f'[TOKEN_DEBUG] Found authorization code in directive.payload.grant (not a token)')
    
    log_error('[TOKEN_DEBUG] ✗ No token found in any location')
    log_error(f'[TOKEN_DEBUG] Full event structure: {json.dumps(event, indent=2, default=str)}')
    
    raise ValueError('No OAuth token in directive')


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """AWS Lambda entry point with mode routing."""
    handler_start = time.perf_counter()
    _print_timing("===== LAMBDA HANDLER START =====")
    _print_timing(f"Request ID: {context.aws_request_id}")
    _print_timing(f"Memory: {context.memory_limit_in_mb}MB")
    
    lambda_mode = os.getenv('LAMBDA_MODE', 'normal').lower()
    mode_time = (time.perf_counter() - handler_start) * 1000
    _print_timing(f"Mode selection ({lambda_mode}): +{mode_time:.2f}ms")
    
    # MODIFIED: Route non-normal modes to TEST interface via gateway
    if lambda_mode != 'normal':
        _print_timing(f"Routing mode '{lambda_mode}' to TEST interface...")
        return test_lambda_mode(lambda_mode, event, context)
    
    _print_timing("Using normal handler")
    return lambda_handler_normal(event, context)


def lambda_handler_normal(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Normal Lambda handler with full LEE."""
    normal_start = time.perf_counter()
    _print_timing("===== NORMAL HANDLER START =====")
    
    try:
        # Determine request type
        if 'directive' in event:
            result = handle_alexa_request(event, context)
        else:
            # Unknown request - return info
            log_info(f"Unknown request: {list(event.keys())}")
            result = format_response(400, {
                "error": "Unknown request type",
                "event_keys": list(event.keys())
            })
        
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


def handle_alexa_request(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Handle Alexa Smart Home requests with LWA OAuth."""
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
        
        # Extract OAuth token
        try:
            oauth_token = _extract_oauth_token(event)
            log_info(f'OAuth token extracted successfully (length={len(oauth_token)})')
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

# EOF
