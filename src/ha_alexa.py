"""
ha_alexa.py - Alexa Smart Home Integration (Native HA Endpoint)
Version: 2025.10.18.09
Description: Alexa integration using HA's native /api/alexa/smart_home endpoint.

CHANGELOG:
- 2025.10.18.09: REWRITTEN - Use HA's native Alexa endpoint instead of manual building
  - Now forwards entire directive to /api/alexa/smart_home (like working Lambda)
  - HA handles all discovery and control logic natively
  - Simplified from 500+ lines to <200 lines
  - Matches proven working architecture

Copyright 2025 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

import os
import json
from typing import Dict, Any
from gateway import (
    log_info, log_error, log_debug, log_warning,
    increment_counter,
    generate_correlation_id
)

# Try to import ha_core functions
try:
    from ha_core import call_ha_api, get_ha_config
    HA_CORE_AVAILABLE = True
except Exception as e:
    HA_CORE_AVAILABLE = False
    log_error(f"[HA_ALEXA] Failed to import ha_core: {type(e).__name__}: {str(e)}")


def _is_debug_mode() -> bool:
    """Check if DEBUG_MODE is enabled."""
    return os.getenv('DEBUG_MODE', 'false').lower() == 'true'


# ===== ALEXA DIRECTIVE PROCESSING =====

def process_alexa_directive(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process Alexa Smart Home directive by forwarding to HA's native endpoint.
    
    This matches the proven architecture from other_working_lambda.py.
    """
    correlation_id = generate_correlation_id()
    
    try:
        if _is_debug_mode():
            log_info(f"[{correlation_id}] [DEBUG] HA_ALEXA: process_alexa_directive called")
        
        if not HA_CORE_AVAILABLE:
            log_error(f"[{correlation_id}] ha_core not available")
            return _create_error_response({}, 'INTERNAL_ERROR', 'HA core unavailable')
        
        directive = event.get('directive', {})
        header = directive.get('header', {})
        namespace = header.get('namespace', '')
        name = header.get('name', '')
        
        log_info(f"[{correlation_id}] Alexa directive: {namespace}.{name}")
        
        # Route to specific handlers
        if namespace == 'Alexa.Discovery' and name == 'Discover':
            return handle_discovery(event)
        elif namespace == 'Alexa.Authorization' and name == 'AcceptGrant':
            return handle_accept_grant(event)
        else:
            # Forward all other directives to HA's native Alexa endpoint
            return _forward_to_ha_alexa(event, correlation_id)
        
    except Exception as e:
        if _is_debug_mode():
            log_error(f"[{correlation_id}] [DEBUG EXCEPTION] {type(e).__name__}: {str(e)}")
            import traceback
            log_error(f"[{correlation_id}] [DEBUG TRACEBACK]:\n{traceback.format_exc()}")
        log_error(f"[{correlation_id}] Directive processing failed: {str(e)}")
        return _create_error_response({}, 'INTERNAL_ERROR', str(e))


def handle_discovery(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle Alexa discovery by forwarding to HA's native /api/alexa/smart_home endpoint.
    
    This is the proven approach - let Home Assistant do all the work.
    """
    correlation_id = generate_correlation_id()
    
    try:
        if _is_debug_mode():
            log_info(f"[{correlation_id}] [DEBUG] HA_ALEXA: handle_discovery called")
        
        log_info(f"[{correlation_id}] Processing Alexa discovery via HA native endpoint")
        
        # Forward entire event to HA's Alexa endpoint
        response = _forward_to_ha_alexa(event, correlation_id)
        
        if _is_debug_mode():
            if isinstance(response, dict) and 'event' in response:
                payload = response.get('event', {}).get('payload', {})
                endpoints = payload.get('endpoints', [])
                log_info(f"[{correlation_id}] [DEBUG] Discovery returned {len(endpoints)} endpoints")
        
        increment_counter('alexa_discovery')
        return response
        
    except Exception as e:
        if _is_debug_mode():
            log_error(f"[{correlation_id}] [DEBUG EXCEPTION] {type(e).__name__}: {str(e)}")
            import traceback
            log_error(f"[{correlation_id}] [DEBUG TRACEBACK]:\n{traceback.format_exc()}")
        log_error(f"[{correlation_id}] Discovery failed: {str(e)}")
        return _create_error_response({}, 'BRIDGE_UNREACHABLE', 'Cannot reach Home Assistant')


def handle_accept_grant(event: Dict[str, Any]) -> Dict[str, Any]:
    """Handle AcceptGrant directive."""
    correlation_id = generate_correlation_id()
    
    try:
        log_info(f"[{correlation_id}] Processing AcceptGrant")
        
        # Forward to HA
        response = _forward_to_ha_alexa(event, correlation_id)
        
        increment_counter('alexa_accept_grant')
        return response
        
    except Exception as e:
        log_error(f"[{correlation_id}] AcceptGrant failed: {str(e)}")
        return _create_error_response({}, 'INTERNAL_ERROR', str(e))


# ===== HA NATIVE ENDPOINT FORWARDING =====

def _forward_to_ha_alexa(event: Dict[str, Any], correlation_id: str) -> Dict[str, Any]:
    """
    Forward Alexa directive to HA's native /api/alexa/smart_home endpoint.
    
    This is the core of the integration - HA handles everything natively.
    """
    try:
        if _is_debug_mode():
            log_debug(f"[{correlation_id}] Forwarding to /api/alexa/smart_home")
        
        # Call HA's native Alexa endpoint with the full event
        result = call_ha_api(
            '/api/alexa/smart_home',
            method='POST',
            data=event
        )
        
        if _is_debug_mode():
            log_debug(f"[{correlation_id}] HA response received")
            log_debug(f"[{correlation_id}] Response success: {result.get('success')}")
        
        # Check if call succeeded
        if not result.get('success'):
            error_msg = result.get('error', 'Unknown error')
            error_code = result.get('error_code', 'UNKNOWN')
            log_error(f"[{correlation_id}] HA API call failed: {error_code} - {error_msg}")
            return _create_error_response({}, 'BRIDGE_UNREACHABLE', f'HA error: {error_msg}')
        
        # Extract response data
        response_data = result.get('data')
        
        if not response_data:
            log_error(f"[{correlation_id}] HA returned success but no data")
            return _create_error_response({}, 'INTERNAL_ERROR', 'No response data from HA')
        
        # HA returns the complete Alexa response format
        return response_data
        
    except Exception as e:
        if _is_debug_mode():
            log_error(f"[{correlation_id}] [DEBUG EXCEPTION] Forwarding failed: {type(e).__name__}: {str(e)}")
            import traceback
            log_error(f"[{correlation_id}] [DEBUG TRACEBACK]:\n{traceback.format_exc()}")
        log_error(f"[{correlation_id}] Failed to forward to HA: {str(e)}")
        return _create_error_response({}, 'BRIDGE_UNREACHABLE', f'Connection error: {str(e)}')


# ===== LEGACY HANDLERS (kept for compatibility) =====

def handle_control(directive: Dict[str, Any]) -> Dict[str, Any]:
    """Handle control directive - forwards to HA."""
    correlation_id = generate_correlation_id()
    event = {'directive': directive}
    return _forward_to_ha_alexa(event, correlation_id)


def handle_power_control(directive: Dict[str, Any]) -> Dict[str, Any]:
    """Handle power control - forwards to HA."""
    return handle_control(directive)


def handle_brightness_control(directive: Dict[str, Any]) -> Dict[str, Any]:
    """Handle brightness control - forwards to HA."""
    return handle_control(directive)


def handle_thermostat_control(directive: Dict[str, Any]) -> Dict[str, Any]:
    """Handle thermostat control - forwards to HA."""
    return handle_control(directive)


# ===== ERROR RESPONSES =====

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
