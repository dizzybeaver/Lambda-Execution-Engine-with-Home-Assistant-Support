"""
ha_interconnect_alexa.py - Alexa Interface Gateway
Version: 2.0.0
Date: 2025-12-02
Description: Gateway wrapper for Alexa Smart Home operations

MODIFIED: Use execute_ha_operation() for CR-1 pattern routing
KEPT: Input validation and error handling

Architecture:
ha_interconnect_alexa.py → ha_interconnect_core → ha_interface_alexa.py

Copyright 2025 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

from typing import Dict, Any
from gateway import create_error_response


def _validate_event(event: Any) -> bool:
    """Validate event is dict and not empty."""
    return isinstance(event, dict) and bool(event)


def alexa_process_directive(event: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """Process Alexa Smart Home directive."""
    if not _validate_event(event):
        return create_error_response('Invalid event format', 'INVALID_INPUT')
    
    from home_assistant.ha_interconnect_core import execute_ha_operation, HAInterface
    return execute_ha_operation(
        HAInterface.ALEXA,
        'process_directive',
        event=event,
        **kwargs
    )


def alexa_handle_discovery(event: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """Handle Alexa device discovery."""
    if not _validate_event(event):
        return create_error_response('Invalid event format', 'INVALID_INPUT')
    
    from home_assistant.ha_interconnect_core import execute_ha_operation, HAInterface
    return execute_ha_operation(
        HAInterface.ALEXA,
        'handle_discovery',
        event=event,
        **kwargs
    )


def alexa_handle_control(event: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """Handle Alexa device control."""
    if not _validate_event(event):
        return create_error_response('Invalid event format', 'INVALID_INPUT')
    
    from home_assistant.ha_interconnect_core import execute_ha_operation, HAInterface
    return execute_ha_operation(
        HAInterface.ALEXA,
        'handle_control',
        event=event,
        **kwargs
    )


def alexa_handle_power_control(event: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """Handle Alexa power control."""
    if not _validate_event(event):
        return create_error_response('Invalid event format', 'INVALID_INPUT')
    
    from home_assistant.ha_interconnect_core import execute_ha_operation, HAInterface
    return execute_ha_operation(
        HAInterface.ALEXA,
        'handle_power_control',
        event=event,
        **kwargs
    )


def alexa_handle_brightness_control(event: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """Handle Alexa brightness control."""
    if not _validate_event(event):
        return create_error_response('Invalid event format', 'INVALID_INPUT')
    
    from home_assistant.ha_interconnect_core import execute_ha_operation, HAInterface
    return execute_ha_operation(
        HAInterface.ALEXA,
        'handle_brightness_control',
        event=event,
        **kwargs
    )


def alexa_handle_thermostat_control(event: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """Handle Alexa thermostat control."""
    if not _validate_event(event):
        return create_error_response('Invalid event format', 'INVALID_INPUT')
    
    from home_assistant.ha_interconnect_core import execute_ha_operation, HAInterface
    return execute_ha_operation(
        HAInterface.ALEXA,
        'handle_thermostat_control',
        event=event,
        **kwargs
    )


def alexa_handle_accept_grant(event: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """Handle Alexa AcceptGrant directive."""
    if not _validate_event(event):
        return create_error_response('Invalid event format', 'INVALID_INPUT')
    
    from home_assistant.ha_interconnect_core import execute_ha_operation, HAInterface
    return execute_ha_operation(
        HAInterface.ALEXA,
        'handle_accept_grant',
        event=event,
        **kwargs
    )


__all__ = [
    'alexa_process_directive',
    'alexa_handle_discovery',
    'alexa_handle_control',
    'alexa_handle_power_control',
    'alexa_handle_brightness_control',
    'alexa_handle_thermostat_control',
    'alexa_handle_accept_grant',
]
