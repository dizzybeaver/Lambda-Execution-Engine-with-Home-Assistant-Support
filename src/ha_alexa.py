"""
ha_alexa.py - Alexa Smart Home Integration (Native HA Endpoint)
Version: 2025.10.19.TIMING
Description: Alexa integration with comprehensive DEBUG_MODE timing diagnostics

CHANGELOG:
- 2025.10.19.TIMING: Added comprehensive timing traces gated by DEBUG_MODE
- 2025.10.19.03: FIXED handle_control signature - accepts event not directive
- 2025.10.18.09: REWRITTEN - Use HA's native Alexa endpoint instead of manual building

Copyright 2025 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

import os
import time
from typing import Dict, Any
from gateway import (
    log_info, log_error, log_debug, log_warning,
    increment_counter,
    generate_correlation_id
)


def _is_debug_mode() -> bool:
    """Check if DEBUG_MODE is enabled."""
    return os.getenv('DEBUG_MODE', 'false').lower() == 'true'


def _print_timing(msg: str):
    """Print timing message only if DEBUG_MODE=true."""
    if _is_debug_mode():
        print(f"[HA_ALEXA_TIMING] {msg}")


# Try to import ha_core
try:
    from ha_core import call_ha_api, get_ha_config
    HA_CORE_AVAILABLE = True
except Exception as e:
    HA_CORE_AVAILABLE = False
    print(f"[HA_ALEXA] Failed to import ha_core: {type(e).__name__}: {str(e)}")


def process_alexa_directive(event: Dict[str, Any]) -> Dict[str, Any]:
    """Process Alexa Smart Home directive by forwarding to HA's native endpoint."""
    start_time = time.time()
    _print_timing("===== PROCESS_ALEXA_DIRECTIVE START =====")
    
    correlation_id = generate_correlation_id()
    
    try:
        if not HA_CORE_AVAILABLE:
            _print_timing(f"ha_core not available (elapsed: {(time.time() - start_time) * 1000:.2f}ms)")
            log_error(f"[{correlation_id}] ha_core not available")
            return _create_error_response({}, 'INTERNAL_ERROR', 'HA core unavailable')
        
        directive = event.get('directive', {})
        header = directive.get('header', {})
        namespace = header.get('namespace', '')
        name = header.get('name', '')
        
        _print_timing(f"Directive: {namespace}.{name} (elapsed: {(time.time() - start_time) * 1000:.2f}ms)")
        log_info(f"[{correlation_id}] Alexa directive: {namespace}.{name}")
        
        if namespace == 'Alexa.Discovery' and name == 'Discover':
            _print_timing(f"Routing to handle_discovery (elapsed: {(time.time() - start_time) * 1000:.2f}ms)")
            return handle_discovery(event)
        elif namespace == 'Alexa.Authorization' and name == 'AcceptGrant':
            _print_timing(f"Routing to handle_accept_grant (elapsed: {(time.time() - start_time) * 1000:.2f}ms)")
            return handle_accept_grant(event)
        else:
            _print_timing(f"Routing to _forward_to_ha_alexa (elapsed: {(time.time() - start_time) * 1000:.2f}ms)")
            return _forward_to_ha_alexa(event, correlation_id)
        
    except Exception as e:
        error_ms = (time.time() - start_time) * 1000
        _print_timing(f"!!! EXCEPTION after {error_ms:.2f}ms: {type(e).__name__}: {str(e)}")
        if _is_debug_mode():
            import traceback
            _print_timing(f"Traceback:\n{traceback.format_exc()}")
        log_error(f"[{correlation_id}] Directive processing failed: {str(e)}")
        return _create_error_response({}, 'INTERNAL_ERROR', str(e))


def handle_discovery(event: Dict[str, Any]) -> Dict[str, Any]:
    """Handle Alexa discovery by forwarding to HA's native /api/alexa/smart_home endpoint."""
    start_time = time.time()
    _print_timing("===== HANDLE_DISCOVERY START =====")
    
    correlation_id = generate_correlation_id()
    _print_timing(f"Forwarding discovery to HA (elapsed: {(time.time() - start_time) * 1000:.2f}ms)")
    
    result = _forward_to_ha_alexa(event, correlation_id)
    
    total_ms = (time.time() - start_time) * 1000
    _print_timing(f"===== HANDLE_DISCOVERY COMPLETE: {total_ms:.2f}ms =====")
    return result


def handle_accept_grant(event: Dict[str, Any]) -> Dict[str, Any]:
    """Handle AcceptGrant by forwarding to HA's native endpoint."""
    start_time = time.time()
    _print_timing("===== HANDLE_ACCEPT_GRANT START =====")
    
    correlation_id = generate_correlation_id()
    _print_timing(f"Forwarding AcceptGrant to HA (elapsed: {(time.time() - start_time) * 1000:.2f}ms)")
    
    result = _forward_to_ha_alexa(event, correlation_id)
    
    total_ms = (time.time() - start_time) * 1000
    _print_timing(f"===== HANDLE_ACCEPT_GRANT COMPLETE: {total_ms:.2f}ms =====")
    return result


def _forward_to_ha_alexa(event: Dict[str, Any], correlation_id: str) -> Dict[str, Any]:
    """Forward full Alexa event to HA's native /api/alexa/smart_home endpoint."""
    start_time = time.time()
    _print_timing("===== _FORWARD_TO_HA_ALEXA START =====")
    
    try:
        _print_timing(f"Calling call_ha_api()... (elapsed: {(time.time() - start_time) * 1000:.2f}ms)")
        api_start = time.time()
        
        result = call_ha_api(
            '/api/alexa/smart_home',
            method='POST',
            data=event
        )
        
        api_ms = (time.time() - api_start) * 1000
        _print_timing(f"*** call_ha_api() returned: {api_ms:.2f}ms ***")
        
        _print_timing(f"Checking result... (elapsed: {(time.time() - start_time) * 1000:.2f}ms)")
        
        if not result.get('success'):
            error_msg = result.get('error', 'Unknown error')
            error_code = result.get('error_code', 'UNKNOWN')
            _print_timing(f"HA API failed: {error_code} - {error_msg}")
            log_error(f"[{correlation_id}] HA API call failed: {error_code} - {error_msg}")
            return _create_error_response({}, 'BRIDGE_UNREACHABLE', f'HA error: {error_msg}')
        
        response_data = result.get('data')
        
        if not response_data:
            _print_timing(f"HA returned success but no data")
            log_error(f"[{correlation_id}] HA returned success but no data")
            return _create_error_response({}, 'INTERNAL_ERROR', 'No response data from HA')
        
        total_ms = (time.time() - start_time) * 1000
        _print_timing(f"===== _FORWARD_TO_HA_ALEXA COMPLETE: {total_ms:.2f}ms =====")
        return response_data
        
    except Exception as e:
        error_ms = (time.time() - start_time) * 1000
        _print_timing(f"!!! FORWARD ERROR after {error_ms:.2f}ms: {type(e).__name__}: {str(e)}")
        if _is_debug_mode():
            import traceback
            _print_timing(f"Traceback:\n{traceback.format_exc()}")
        log_error(f"[{correlation_id}] Failed to forward to HA: {str(e)}")
        return _create_error_response({}, 'BRIDGE_UNREACHABLE', f'Connection error: {str(e)}')


def handle_control(event: Dict[str, Any]) -> Dict[str, Any]:
    """Handle control directive - forwards full event to HA."""
    start_time = time.time()
    _print_timing("===== HANDLE_CONTROL START =====")
    
    correlation_id = generate_correlation_id()
    
    result = _forward_to_ha_alexa(event, correlation_id)
    
    total_ms = (time.time() - start_time) * 1000
    _print_timing(f"===== HANDLE_CONTROL COMPLETE: {total_ms:.2f}ms =====")
    return result


def handle_power_control(event: Dict[str, Any]) -> Dict[str, Any]:
    """Handle power control - forwards to HA."""
    return handle_control(event)


def handle_brightness_control(event: Dict[str, Any]) -> Dict[str, Any]:
    """Handle brightness control - forwards to HA."""
    return handle_control(event)


def handle_thermostat_control(event: Dict[str, Any]) -> Dict[str, Any]:
    """Handle thermostat control - forwards to HA."""
    return handle_control(event)


def _create_error_response(header: Dict[str, Any], error_type: str,
                          error_message: str) -> Dict[str, Any]:
    """Create Alexa error response."""
    correlation_id = generate_correlation_id()
    
    return {
        'event': {
            'header': {
                'namespace': 'Alexa',
                'name': 'ErrorResponse',
                'messageId': correlation_id,
                'correlationToken': header.get('correlationToken'),
                'payloadVersion': '3'
            },
            'payload': {
                'type': error_type,
                'message': error_message
            }
        }
    }


__all__ = [
    'process_alexa_directive',
    'handle_discovery',
    'handle_control',
    'handle_power_control',
    'handle_brightness_control',
    'handle_thermostat_control',
    'handle_accept_grant',
]

# EOF
