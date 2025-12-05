"""
ha_interface_alexa.py - Alexa Interface Layer (INT-HA-01)
Version: 2.0.0
Date: 2025-12-02
Description: Interface layer for Alexa Smart Home integration

MODIFIED: Replace custom response builders with template rendering
MODIFIED: Use gateway.log_*() instead of custom debug code
ADDED: DISPATCH dictionary for CR-1 pattern
ADDED: execute_alexa_operation() router function

Architecture:
ha_interconnect.py → ha_interface_alexa.py → ha_alexa_core.py

Copyright 2025 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

from typing import Dict, Any, Optional


def _process_directive_impl(event: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """Process Alexa Smart Home directive."""
    import home_assistant.ha_alexa_core as ha_alexa_core
    return ha_alexa_core.process_directive_impl(event, **kwargs)


def _handle_discovery_impl(event: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """Handle Alexa device discovery."""
    import home_assistant.ha_alexa_core as ha_alexa_core
    return ha_alexa_core.handle_discovery_impl(event, **kwargs)


def _handle_control_impl(event: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """Handle Alexa device control."""
    import home_assistant.ha_alexa_core as ha_alexa_core
    return ha_alexa_core.handle_control_impl(event, **kwargs)


def _handle_power_control_impl(event: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """Handle Alexa power control."""
    import home_assistant.ha_alexa_core as ha_alexa_core
    return ha_alexa_core.handle_power_control_impl(event, **kwargs)


def _handle_brightness_control_impl(event: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """Handle Alexa brightness control."""
    import home_assistant.ha_alexa_core as ha_alexa_core
    return ha_alexa_core.handle_brightness_control_impl(event, **kwargs)


def _handle_thermostat_control_impl(event: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """Handle Alexa thermostat control."""
    import home_assistant.ha_alexa_core as ha_alexa_core
    return ha_alexa_core.handle_thermostat_control_impl(event, **kwargs)


def _handle_accept_grant_impl(event: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """Handle Alexa AcceptGrant directive."""
    import home_assistant.ha_alexa_core as ha_alexa_core
    return ha_alexa_core.handle_accept_grant_impl(event, **kwargs)


# ADDED: DISPATCH dictionary (CR-1 pattern)
DISPATCH = {
    'process_directive': _process_directive_impl,
    'handle_discovery': _handle_discovery_impl,
    'handle_control': _handle_control_impl,
    'handle_power_control': _handle_power_control_impl,
    'handle_brightness_control': _handle_brightness_control_impl,
    'handle_thermostat_control': _handle_thermostat_control_impl,
    'handle_accept_grant': _handle_accept_grant_impl,
}


# ADDED: Execute operation router (CR-1 pattern)
def execute_alexa_operation(operation: str, **kwargs) -> dict:
    """Execute Alexa operation via dispatch."""
    if operation not in DISPATCH:
        raise ValueError(f"Unknown Alexa operation: {operation}")
    
    handler = DISPATCH[operation]
    return handler(**kwargs)


# Maintain backward compatibility with original functions
def process_directive(event: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """Process Alexa directive."""
    return _process_directive_impl(event, **kwargs)


def handle_discovery(event: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """Handle discovery."""
    return _handle_discovery_impl(event, **kwargs)


def handle_control(event: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """Handle control."""
    return _handle_control_impl(event, **kwargs)


def handle_power_control(event: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """Handle power control."""
    return _handle_power_control_impl(event, **kwargs)


def handle_brightness_control(event: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """Handle brightness control."""
    return _handle_brightness_control_impl(event, **kwargs)


def handle_thermostat_control(event: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """Handle thermostat control."""
    return _handle_thermostat_control_impl(event, **kwargs)


def handle_accept_grant(event: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """Handle AcceptGrant."""
    return _handle_accept_grant_impl(event, **kwargs)


__all__ = [
    'execute_alexa_operation',
    'process_directive',
    'handle_discovery',
    'handle_control',
    'handle_power_control',
    'handle_brightness_control',
    'handle_thermostat_control',
    'handle_accept_grant',
]
