"""
ha_alexa_core.py - Alexa Core Implementation (INT-HA-01)
Version: 3.0.0
Date: 2025-12-01
Description: Core implementation for Alexa Smart Home integration

Architecture:
ha_interconnect.py → ha_interface_alexa.py → ha_alexa_core.py (THIS FILE)

Copyright 2025 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

from typing import Dict, Any

# Import LEE services via gateway (ONLY way to access LEE)
from gateway import (
    log_info, log_error, log_debug, log_warning,
    increment_counter, generate_correlation_id
)


def process_directive_impl(event: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """
    Process Alexa Smart Home directive implementation.
    
    Core implementation for Alexa directive processing.
    Routes to appropriate handlers based on directive namespace and name.
    
    Args:
        event: Alexa directive event dictionary
        **kwargs: Additional options
        
    Returns:
        Alexa response dictionary
        
    Example:
        response = process_directive_impl(alexa_event)
        
    REF: INT-HA-01
    """
    correlation_id = generate_correlation_id()
    
    try:
        # LAZY IMPORT: Only load ha_interconnect when actually needed
        try:
            import home_assistant.ha_interconnect as ha_interconnect
        except ImportError as e:
            log_error(f"[{correlation_id}] ha_interconnect not available: {e}")
            increment_counter('ha_alexa_import_error')
            return _create_error_response({}, 'INTERNAL_ERROR', 'HA interconnect unavailable')
        
        directive = event.get('directive', {})
        header = directive.get('header', {})
        namespace = header.get('namespace', '')
        name = header.get('name', '')
        
        log_info(f"[{correlation_id}] Alexa directive: {namespace}.{name}")
        
        # Metric tracking for directive types
        increment_counter('alexa_directive_received')
        increment_counter(f'alexa_directive_{namespace}')
        
        # Route to appropriate handler
        if namespace == 'Alexa.Discovery' and name == 'Discover':
            return handle_discovery_impl(event, **kwargs)
        elif namespace == 'Alexa.Authorization' and name == 'AcceptGrant':
            return handle_accept_grant_impl(event, **kwargs)
        else:
            return _forward_to_ha_alexa(event, correlation_id)
        
    except Exception as e:
        log_error(f"[{correlation_id}] Directive processing failed: {str(e)}")
        increment_counter('alexa_directive_error')
        return _create_error_response({}, 'INTERNAL_ERROR', str(e))


def handle_discovery_impl(event: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """
    Handle Alexa device discovery implementation.
    
    Core implementation for device discovery.
    Queries Home Assistant for all available devices.
    
    Args:
        event: Alexa discovery event
        **kwargs: Additional options
        
    Returns:
        Discovery response with device list
        
    REF: INT-HA-01
    """
    correlation_id = generate_correlation_id()
    
    try:
        # LAZY IMPORT: Only load ha_interconnect when actually needed
        import home_assistant.ha_interconnect as ha_interconnect
        
        result = ha_interconnect.devices_call_ha_api('/api/alexa/smart_home', method='POST', data=event)
        
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
        
        increment_counter('alexa_discovery_success')
        return response_data
        
    except Exception as e:
        log_error(f"[{correlation_id}] Discovery error: {str(e)}")
        increment_counter('alexa_discovery_error')
        return _create_error_response({}, 'BRIDGE_UNREACHABLE', f'Discovery error: {str(e)}')


def handle_control_impl(event: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """
    Handle Alexa device control implementation.
    
    Core implementation for device control.
    Forwards control directives to Home Assistant.
    
    Args:
        event: Alexa control event
        **kwargs: Additional options
        
    Returns:
        Control response
        
    REF: INT-HA-01
    """
    correlation_id = generate_correlation_id()
    
    increment_counter('alexa_control_request')
    
    result = _forward_to_ha_alexa(event, correlation_id)
    return result


def handle_power_control_impl(event: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """
    Handle Alexa power control implementation.
    
    Core implementation for power control (on/off).
    
    Args:
        event: Alexa power control event
        **kwargs: Additional options
        
    Returns:
        Power control response
        
    REF: INT-HA-01
    """
    increment_counter('alexa_power_control')
    return handle_control_impl(event, **kwargs)


def handle_brightness_control_impl(event: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """
    Handle Alexa brightness control implementation.
    
    Core implementation for brightness adjustment.
    
    Args:
        event: Alexa brightness event
        **kwargs: Additional options
        
    Returns:
        Brightness control response
        
    REF: INT-HA-01
    """
    increment_counter('alexa_brightness_control')
    return handle_control_impl(event, **kwargs)


def handle_thermostat_control_impl(event: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """
    Handle Alexa thermostat control implementation.
    
    Core implementation for thermostat operations.
    
    Args:
        event: Alexa thermostat event
        **kwargs: Additional options
        
    Returns:
        Thermostat control response
        
    REF: INT-HA-01
    """
    increment_counter('alexa_thermostat_control')
    return handle_control_impl(event, **kwargs)


def handle_accept_grant_impl(event: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """
    Handle Alexa AcceptGrant directive implementation.
    
    Core implementation for authorization grant.
    Simple acknowledgment response per Alexa Smart Home API.
    
    Args:
        event: Alexa AcceptGrant event
        **kwargs: Additional options
        
    Returns:
        AcceptGrant response
        
    REF: INT-HA-01
    """
    correlation_id = generate_correlation_id()
    directive = event.get('directive', {})
    header = directive.get('header', {})
    
    log_info(f"[{correlation_id}] AcceptGrant received")
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


# ===== HELPER FUNCTIONS =====

def _forward_to_ha_alexa(event: Dict[str, Any], correlation_id: str) -> Dict[str, Any]:
    """
    Forward directive to Home Assistant's native Alexa endpoint.
    
    Helper function to forward directives to HA.
    
    Args:
        event: Alexa directive event
        correlation_id: Correlation ID for logging
        
    Returns:
        HA response or error response
    """
    try:
        # LAZY IMPORT: Only load ha_interconnect when actually needed
        import home_assistant.ha_interconnect as ha_interconnect
        
        result = ha_interconnect.devices_call_ha_api(
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
        
        increment_counter('alexa_forward_success')
        return response_data
        
    except Exception as e:
        log_error(f"[{correlation_id}] Failed to forward to HA: {str(e)}")
        increment_counter('alexa_forward_error')
        return _create_error_response({}, 'BRIDGE_UNREACHABLE', f'Connection error: {str(e)}')


def _create_error_response(header: Dict[str, Any], error_type: str,
                          error_message: str) -> Dict[str, Any]:
    """
    Create Alexa error response.
    
    Note: This maintains Alexa Smart Home API format requirements.
    Not replaced with gateway create_error_response() as Alexa
    requires specific response structure per Alexa Smart Home API.
    
    Args:
        header: Alexa directive header
        error_type: Error type code
        error_message: Error message
        
    Returns:
        Alexa-formatted error response
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
    'process_directive_impl',
    'handle_discovery_impl',
    'handle_control_impl',
    'handle_power_control_impl',
    'handle_brightness_control_impl',
    'handle_thermostat_control_impl',
    'handle_accept_grant_impl',
]

# EOF
