"""
ha_interface_alexa.py - Alexa Interface Layer (INT-HA-01)
Version: 1.0.0 - PHASE 1
Date: 2025-11-03
Description: Interface layer for Alexa Smart Home integration

PHASE 1: Setup & Structure
- Created Alexa interface routing layer
- 7 routing functions to ha_alexa_core
- Lazy imports to core layer
- ISP compliant

Architecture:
ha_interconnect.py → ha_interface_alexa.py → ha_alexa_core.py

Copyright 2025 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

from typing import Dict, Any, Optional


def process_directive(event: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """
    Process Alexa Smart Home directive.
    
    Interface layer routing.
    Routes to: ha_alexa_core.process_directive_impl
    
    Args:
        event: Alexa directive event
        **kwargs: Additional options
        
    Returns:
        Alexa response dictionary
    """

    import home_assistant.ha_alexa_core as ha_alexa_core
    return ha_alexa_core.process_directive_impl(event, **kwargs)


def handle_discovery(event: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """
    Handle Alexa device discovery.
    
    Interface layer routing.
    Routes to: ha_alexa_core.handle_discovery_impl
    
    Args:
        event: Alexa discovery event
        **kwargs: Additional options
        
    Returns:
        Discovery response
    """
    import home_assistant.ha_alexa_core as ha_alexa_core
    return ha_alexa_core.handle_discovery_impl(event, **kwargs)


def handle_control(event: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """
    Handle Alexa device control.
    
    Interface layer routing.
    Routes to: ha_alexa_core.handle_control_impl
    
    Args:
        event: Alexa control event
        **kwargs: Additional options
        
    Returns:
        Control response
    """
    import home_assistant.ha_alexa_core as ha_alexa_core
    return ha_alexa_core.handle_control_impl(event, **kwargs)


def handle_power_control(event: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """
    Handle Alexa power control.
    
    Interface layer routing.
    Routes to: ha_alexa_core.handle_power_control_impl
    
    Args:
        event: Alexa power event
        **kwargs: Additional options
        
    Returns:
        Power control response
    """
    import home_assistant.ha_alexa_core as ha_alexa_core
    return ha_alexa_core.handle_power_control_impl(event, **kwargs)


def handle_brightness_control(event: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """
    Handle Alexa brightness control.
    
    Interface layer routing.
    Routes to: ha_alexa_core.handle_brightness_control_impl
    
    Args:
        event: Alexa brightness event
        **kwargs: Additional options
        
    Returns:
        Brightness control response
    """
    import home_assistant.ha_alexa_core as ha_alexa_core
    return ha_alexa_core.handle_brightness_control_impl(event, **kwargs)


def handle_thermostat_control(event: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """
    Handle Alexa thermostat control.
    
    Interface layer routing.
    Routes to: ha_alexa_core.handle_thermostat_control_impl
    
    Args:
        event: Alexa thermostat event
        **kwargs: Additional options
        
    Returns:
        Thermostat control response
    """
    import home_assistant.ha_alexa_core as ha_alexa_core
    return ha_alexa_core.handle_thermostat_control_impl(event, **kwargs)


def handle_accept_grant(event: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """
    Handle Alexa AcceptGrant directive.
    
    Interface layer routing.
    Routes to: ha_alexa_core.handle_accept_grant_impl
    
    Args:
        event: AcceptGrant event
        **kwargs: Additional options
        
    Returns:
        AcceptGrant response
    """
    import home_assistant.ha_alexa_core as ha_alexa_core
    return ha_alexa_core.handle_accept_grant_impl(event, **kwargs)


__all__ = [
    'process_directive',
    'handle_discovery',
    'handle_control',
    'handle_power_control',
    'handle_brightness_control',
    'handle_thermostat_control',
    'handle_accept_grant',
]

# EOF
