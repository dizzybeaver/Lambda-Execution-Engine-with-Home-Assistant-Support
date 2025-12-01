# ha_interconnect_alexa.py
"""
ha_interconnect_alexa.py - Alexa Interface Gateway
Version: 1.0.0
Date: 2025-11-05
Purpose: Gateway wrapper for Alexa Smart Home operations

SECURITY:
- Input validation on all functions
- Error handling for invalid events
- Type checking before routing

Architecture:
ha_interconnect_alexa.py → ha_interface_alexa.py → ha_alexa_core.py

Functions: 7 Alexa gateway operations
- Process directive
- Handle discovery
- Handle control (power, brightness, thermostat)
- Handle authorization

Pattern:
Validates input → Routes to interface → Returns response

Copyright 2025 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

from typing import Dict, Any
from ha_interconnect_validation import _validate_event
from gateway import create_error_response


def alexa_process_directive(event: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """
    Process Alexa Smart Home directive.
    
    Gateway function for Alexa directive processing.
    Routes to: ha_interface_alexa.process_directive
    
    Args:
        event: Alexa directive event dictionary
        **kwargs: Additional options
        
    Returns:
        Alexa response dictionary
        
    Security:
        - Validates event structure
        - Returns error for invalid format
        
    REF: INT-HA-01
    """
    # ADDED: Input validation (CRIT-03)
    if not _validate_event(event):
        return create_error_response('Invalid event format', 'INVALID_INPUT')
    
    import home_assistant.ha_interface_alexa as ha_interface_alexa
    return ha_interface_alexa.process_directive(event, **kwargs)


def alexa_handle_discovery(event: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """
    Handle Alexa device discovery.
    
    Gateway function for Alexa discovery.
    Routes to: ha_interface_alexa.handle_discovery
    
    Args:
        event: Alexa discovery event
        **kwargs: Additional options
        
    Returns:
        Discovery response with device list
        
    Security:
        - Validates event structure
        - Returns error for invalid format
        
    REF: INT-HA-01
    """
    # ADDED: Input validation (CRIT-03)
    if not _validate_event(event):
        return create_error_response('Invalid event format', 'INVALID_INPUT')
    
    import home_assistant.ha_interface_alexa as ha_interface_alexa
    return ha_interface_alexa.handle_discovery(event, **kwargs)


def alexa_handle_control(event: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """
    Handle Alexa device control.
    
    Gateway function for Alexa control operations.
    Routes to: ha_interface_alexa.handle_control
    
    Args:
        event: Alexa control event
        **kwargs: Additional options
        
    Returns:
        Control response
        
    Security:
        - Validates event structure
        - Returns error for invalid format
        
    REF: INT-HA-01
    """
    # ADDED: Input validation (CRIT-03)
    if not _validate_event(event):
        return create_error_response('Invalid event format', 'INVALID_INPUT')
    
    import home_assistant.ha_interface_alexa as ha_interface_alexa
    return ha_interface_alexa.handle_control(event, **kwargs)


def alexa_handle_power_control(event: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """
    Handle Alexa power control (on/off).
    
    Gateway function for power control.
    Routes to: ha_interface_alexa.handle_power_control
    
    Args:
        event: Alexa power control event
        **kwargs: Additional options
        
    Returns:
        Power control response
        
    Security:
        - Validates event structure
        - Returns error for invalid format
        
    REF: INT-HA-01
    """
    # ADDED: Input validation (CRIT-03)
    if not _validate_event(event):
        return create_error_response('Invalid event format', 'INVALID_INPUT')
    
    import home_assistant.ha_interface_alexa as ha_interface_alexa
    return ha_interface_alexa.handle_power_control(event, **kwargs)


def alexa_handle_brightness_control(event: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """
    Handle Alexa brightness control.
    
    Gateway function for brightness adjustment.
    Routes to: ha_interface_alexa.handle_brightness_control
    
    Args:
        event: Alexa brightness event
        **kwargs: Additional options
        
    Returns:
        Brightness control response
        
    Security:
        - Validates event structure
        - Returns error for invalid format
        
    REF: INT-HA-01
    """
    # ADDED: Input validation (CRIT-03)
    if not _validate_event(event):
        return create_error_response('Invalid event format', 'INVALID_INPUT')
    
    import home_assistant.ha_interface_alexa as ha_interface_alexa
    return ha_interface_alexa.handle_brightness_control(event, **kwargs)


def alexa_handle_thermostat_control(event: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """
    Handle Alexa thermostat control.
    
    Gateway function for thermostat operations.
    Routes to: ha_interface_alexa.handle_thermostat_control
    
    Args:
        event: Alexa thermostat event
        **kwargs: Additional options
        
    Returns:
        Thermostat control response
        
    Security:
        - Validates event structure
        - Returns error for invalid format
        
    REF: INT-HA-01
    """
    # ADDED: Input validation (CRIT-03)
    if not _validate_event(event):
        return create_error_response('Invalid event format', 'INVALID_INPUT')
    
    import home_assistant.ha_interface_alexa as ha_interface_alexa
    return ha_interface_alexa.handle_thermostat_control(event, **kwargs)


def alexa_handle_accept_grant(event: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """
    Handle Alexa AcceptGrant directive.
    
    Gateway function for authorization grant.
    Routes to: ha_interface_alexa.handle_accept_grant
    
    Args:
        event: Alexa AcceptGrant event
        **kwargs: Additional options
        
    Returns:
        AcceptGrant response
        
    Security:
        - Validates event structure
        - Returns error for invalid format
        
    REF: INT-HA-01
    """
    # ADDED: Input validation (CRIT-03)
    if not _validate_event(event):
        return create_error_response('Invalid event format', 'INVALID_INPUT')
    
    import home_assistant.ha_interface_alexa as ha_interface_alexa
    return ha_interface_alexa.handle_accept_grant(event, **kwargs)


# ====================
# EXPORTS
# ====================

__all__ = [
    'alexa_process_directive',
    'alexa_handle_discovery',
    'alexa_handle_control',
    'alexa_handle_power_control',
    'alexa_handle_brightness_control',
    'alexa_handle_thermostat_control',
    'alexa_handle_accept_grant',
]

# EOF
