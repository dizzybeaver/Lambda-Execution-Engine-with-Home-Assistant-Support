"""
ha_interconnect_alexa.py

Version: 2025.1205.02
Date: 2025-12-05
Purpose: Alexa gateway functions with LWA OAuth support

CHANGES (2025.1205.02 - LWA MIGRATION):
- MODIFIED: Extract OAuth token from event
- MODIFIED: Pass OAuth token to core implementations
- Token flows: event['oauth_token'] -> core functions

Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any, Dict

from gateway import create_error_response


# ===== VALIDATION =====

def _validate_event(event: Dict[str, Any]) -> bool:
    """Validate event has directive structure."""
    return isinstance(event, dict) and 'directive' in event


def _extract_token_from_event(event: Dict[str, Any]) -> str:
    """
    Extract OAuth token from event.
    
    LWA Migration: Token added to event by lambda_handler.
    
    Args:
        event: Event with oauth_token key
        
    Returns:
        OAuth token
        
    Raises:
        ValueError: If no token in event
    """
    token = event.get('oauth_token')
    if not token:
        raise ValueError('No oauth_token in event')
    return token


# ===== ALEXA HANDLERS =====

def alexa_process_directive(event: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """
    Process Alexa directive with OAuth token.
    
    LWA Migration: Extracts token from event, passes to core.
    """
    if not _validate_event(event):
        return create_error_response('Invalid event format', 'INVALID_INPUT')
    
    # Extract OAuth token from event
    try:
        oauth_token = _extract_token_from_event(event)
    except ValueError:
        return create_error_response(
            'No OAuth token in event',
            'INVALID_AUTHORIZATION_CREDENTIAL'
        )
    
    from home_assistant.ha_interconnect_core import execute_ha_operation, HAInterface
    return execute_ha_operation(
        HAInterface.ALEXA,
        'process_directive',
        event=event,
        oauth_token=oauth_token,  # Pass token to core
        **kwargs
    )


def alexa_handle_discovery(event: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """Handle Alexa discovery with OAuth token."""
    if not _validate_event(event):
        return create_error_response('Invalid event format', 'INVALID_INPUT')
    
    try:
        oauth_token = _extract_token_from_event(event)
    except ValueError:
        return create_error_response(
            'No OAuth token in event',
            'INVALID_AUTHORIZATION_CREDENTIAL'
        )
    
    from home_assistant.ha_interconnect_core import execute_ha_operation, HAInterface
    return execute_ha_operation(
        HAInterface.ALEXA,
        'handle_discovery',
        event=event,
        oauth_token=oauth_token,
        **kwargs
    )


def alexa_handle_control(event: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """Handle Alexa control with OAuth token."""
    if not _validate_event(event):
        return create_error_response('Invalid event format', 'INVALID_INPUT')
    
    try:
        oauth_token = _extract_token_from_event(event)
    except ValueError:
        return create_error_response(
            'No OAuth token in event',
            'INVALID_AUTHORIZATION_CREDENTIAL'
        )
    
    from home_assistant.ha_interconnect_core import execute_ha_operation, HAInterface
    return execute_ha_operation(
        HAInterface.ALEXA,
        'handle_control',
        event=event,
        oauth_token=oauth_token,
        **kwargs
    )


def alexa_handle_power_control(event: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """Handle Alexa power control with OAuth token."""
    if not _validate_event(event):
        return create_error_response('Invalid event format', 'INVALID_INPUT')
    
    try:
        oauth_token = _extract_token_from_event(event)
    except ValueError:
        return create_error_response(
            'No OAuth token in event',
            'INVALID_AUTHORIZATION_CREDENTIAL'
        )
    
    from home_assistant.ha_interconnect_core import execute_ha_operation, HAInterface
    return execute_ha_operation(
        HAInterface.ALEXA,
        'handle_power_control',
        event=event,
        oauth_token=oauth_token,
        **kwargs
    )


def alexa_handle_brightness_control(event: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """Handle Alexa brightness control with OAuth token."""
    if not _validate_event(event):
        return create_error_response('Invalid event format', 'INVALID_INPUT')
    
    try:
        oauth_token = _extract_token_from_event(event)
    except ValueError:
        return create_error_response(
            'No OAuth token in event',
            'INVALID_AUTHORIZATION_CREDENTIAL'
        )
    
    from home_assistant.ha_interconnect_core import execute_ha_operation, HAInterface
    return execute_ha_operation(
        HAInterface.ALEXA,
        'handle_brightness_control',
        event=event,
        oauth_token=oauth_token,
        **kwargs
    )


def alexa_handle_thermostat_control(event: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """Handle Alexa thermostat control with OAuth token."""
    if not _validate_event(event):
        return create_error_response('Invalid event format', 'INVALID_INPUT')
    
    try:
        oauth_token = _extract_token_from_event(event)
    except ValueError:
        return create_error_response(
            'No OAuth token in event',
            'INVALID_AUTHORIZATION_CREDENTIAL'
        )
    
    from home_assistant.ha_interconnect_core import execute_ha_operation, HAInterface
    return execute_ha_operation(
        HAInterface.ALEXA,
        'handle_thermostat_control',
        event=event,
        oauth_token=oauth_token,
        **kwargs
    )


def alexa_handle_accept_grant(event: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """Handle Alexa AcceptGrant directive with OAuth token."""
    if not _validate_event(event):
        return create_error_response('Invalid event format', 'INVALID_INPUT')
    
    try:
        oauth_token = _extract_token_from_event(event)
    except ValueError:
        return create_error_response(
            'No OAuth token in event',
            'INVALID_AUTHORIZATION_CREDENTIAL'
        )
    
    from home_assistant.ha_interconnect_core import execute_ha_operation, HAInterface
    return execute_ha_operation(
        HAInterface.ALEXA,
        'handle_accept_grant',
        event=event,
        oauth_token=oauth_token,
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
