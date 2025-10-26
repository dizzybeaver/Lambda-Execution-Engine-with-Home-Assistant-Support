"""
ha_alexa.py - Alexa Smart Home Integration (Native HA Endpoint)
Version: 2025.10.26.PHASE2
Description: COLD START OPTIMIZATION + Performance optimization

CHANGELOG:
- 2025.10.26.PHASE2: Performance optimization - replaced custom timing with gateway metrics
  * REMOVED: _is_debug_mode() and _print_timing() functions (7 lines)
  * REMOVED: All manual timing code from all handlers (49 lines)
  * REMOVED: time module import (no longer needed)
  * ADDED: Proper gateway metrics for operation tracking
  * TOTAL REDUCTION: 56 lines of custom timing code removed
- 2025.10.19.COLD_START_OPT: CRITICAL FIX - Lazy imports
  - Removed module-level import of ha_core (was 293ms!)
  - Added lazy imports inside functions (only when needed)
  - Reduces ha_alexa import time: 293ms → ~40ms (saves 250ms per cold start)
  - First API call pays the 250ms once, subsequent calls cached
  
Design Decision: Lazy imports inside functions
Reason: Module-level ha_core import triggers entire dependency chain (ha_config, 
        config_param_store, preloaded boto3). By loading only when needed, we defer
        this cost until actual use, dramatically improving cold start time.

Copyright 2025 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

import os
from typing import Dict, Any
from gateway import (
    log_info, log_error, log_debug, log_warning,
    increment_counter,
    generate_correlation_id
)


def process_alexa_directive(event: Dict[str, Any]) -> Dict[str, Any]:
    """Process Alexa Smart Home directive by forwarding to HA's native endpoint."""
    # MODIFIED: Removed all custom timing code, using gateway metrics
    
    correlation_id = generate_correlation_id()
    
    try:
        # LAZY IMPORT: Only load ha_core when actually needed
        try:
            from ha_core import call_ha_api, get_ha_config
        except ImportError as e:
            log_error(f"[{correlation_id}] ha_core not available: {e}")
            increment_counter('ha_alexa_import_error')
            return _create_error_response({}, 'INTERNAL_ERROR', 'HA core unavailable')
        
        directive = event.get('directive', {})
        header = directive.get('header', {})
        namespace = header.get('namespace', '')
        name = header.get('name', '')
        
        log_info(f"[{correlation_id}] Alexa directive: {namespace}.{name}")
        
        # ADDED: Metric tracking for directive types
        increment_counter('alexa_directive_received')
        increment_counter(f'alexa_directive_{namespace}')
        
        if namespace == 'Alexa.Discovery' and name == 'Discover':
            return handle_discovery(event)
        elif namespace == 'Alexa.Authorization' and name == 'AcceptGrant':
            return handle_accept_grant(event)
        else:
            return _forward_to_ha_alexa(event, correlation_id)
        
    except Exception as e:
        log_error(f"[{correlation_id}] Directive processing failed: {str(e)}")
        increment_counter('alexa_directive_error')
        return _create_error_response({}, 'INTERNAL_ERROR', str(e))


def handle_discovery(event: Dict[str, Any]) -> Dict[str, Any]:
    """Handle Alexa discovery - returns all devices."""
    # MODIFIED: Removed all custom timing code, using gateway metrics
    
    correlation_id = generate_correlation_id()
    
    try:
        # LAZY IMPORT: Only load ha_core when actually needed
        from ha_core import call_ha_api
        
        result = call_ha_api('/api/alexa/smart_home', method='POST', data=event)
        
        if not result.get('success'):
            error_msg = result.get('error', 'Unknown error')
            log_error(f"[{correlation_id}] Discovery failed: {error_msg}")
            increment_counter('alexa_discovery_failed')
            return _create_error_response({}, 'BRIDGE_UNREACHABLE', f'Discovery failed: {error_msg}')
        
        response_data = result.get('data')
        
        if not response_data:
            log_error(f"[{correlation_id}] No discovery data returned")
            increment_counter('alexa_discovery_no_data')
            return _create_error_response({}, 'INTERNAL_ERROR', 'No discovery data')
        
        # ADDED: Success metric
        increment_counter('alexa_discovery_success')
        return response_data
        
    except Exception as e:
        log_error(f"[{correlation_id}] Discovery error: {str(e)}")
        increment_counter('alexa_discovery_error')
        return _create_error_response({}, 'BRIDGE_UNREACHABLE', f'Discovery error: {str(e)}')


def handle_accept_grant(event: Dict[str, Any]) -> Dict[str, Any]:
    """Handle Alexa AcceptGrant directive."""
    # MODIFIED: Removed all custom timing code
    
    correlation_id = generate_correlation_id()
    directive = event.get('directive', {})
    header = directive.get('header', {})
    
    log_info(f"[{correlation_id}] AcceptGrant received")
    
    # ADDED: Metric tracking
    increment_counter('alexa_accept_grant')
    
    # AcceptGrant just needs to acknowledge
    return {
        'event': {
            'header': {
                'namespace': 'Alexa.Authorization',
                'name': 'AcceptGrant.Response',
                'messageId': generate_correlation_id(),
                'correlationToken': header.get('correlationToken'),
                'payloadVersion': '3'
            },
            'payload': {}
        }
    }


def _forward_to_ha_alexa(event: Dict[str, Any], correlation_id: str) -> Dict[str, Any]:
    """Forward directive to Home Assistant's native Alexa endpoint."""
    # MODIFIED: Removed all custom timing code, using gateway metrics
    
    try:
        # LAZY IMPORT: Only load ha_core when actually needed
        from ha_core import call_ha_api
        
        result = call_ha_api(
            '/api/alexa/smart_home',
            method='POST',
            data=event
        )
        
        if not result.get('success'):
            error_msg = result.get('error', 'Unknown error')
            error_code = result.get('error_code', 'UNKNOWN')
            log_error(f"[{correlation_id}] HA API call failed: {error_code} - {error_msg}")
            increment_counter('alexa_forward_ha_failed')
            return _create_error_response({}, 'BRIDGE_UNREACHABLE', f'HA error: {error_msg}')
        
        response_data = result.get('data')
        
        if not response_data:
            log_error(f"[{correlation_id}] HA returned success but no data")
            increment_counter('alexa_forward_no_data')
            return _create_error_response({}, 'INTERNAL_ERROR', 'No response data from HA')
        
        # ADDED: Success metric
        increment_counter('alexa_forward_success')
        return response_data
        
    except Exception as e:
        log_error(f"[{correlation_id}] Failed to forward to HA: {str(e)}")
        increment_counter('alexa_forward_error')
        return _create_error_response({}, 'BRIDGE_UNREACHABLE', f'Connection error: {str(e)}')


def handle_control(event: Dict[str, Any]) -> Dict[str, Any]:
    """Handle control directive - forwards full event to HA."""
    # MODIFIED: Removed all custom timing code
    
    correlation_id = generate_correlation_id()
    
    # ADDED: Metric tracking
    increment_counter('alexa_control_request')
    
    result = _forward_to_ha_alexa(event, correlation_id)
    return result


def handle_power_control(event: Dict[str, Any]) -> Dict[str, Any]:
    """Handle power control - forwards to HA."""
    increment_counter('alexa_power_control')
    return handle_control(event)


def handle_brightness_control(event: Dict[str, Any]) -> Dict[str, Any]:
    """Handle brightness control - forwards to HA."""
    increment_counter('alexa_brightness_control')
    return handle_control(event)


def handle_thermostat_control(event: Dict[str, Any]) -> Dict[str, Any]:
    """Handle thermostat control - forwards to HA."""
    increment_counter('alexa_thermostat_control')
    return handle_control(event)


def _create_error_response(header: Dict[str, Any], error_type: str,
                          error_message: str) -> Dict[str, Any]:
    """
    Create Alexa error response.
    
    Note: This maintains Alexa Smart Home API format requirements.
    Not replaced with gateway create_error_response() as Alexa
    requires specific response structure per Alexa Smart Home API.
    """
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
