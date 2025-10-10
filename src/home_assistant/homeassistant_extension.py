"""
homeassistant_extension.py - Simplified Forwarding Pattern
Version: 2025.10.10.02
Description: Forwards Alexa Smart Home events directly to HA's endpoint

Copyright 2025 Joseph Hersey
Licensed under Apache 2.0
"""

import time
import os
import json
from typing import Dict, Any, Optional

from gateway import (
    cache_get, cache_set, cache_delete,
    log_info, log_error, log_debug,
    make_post_request,
    create_success_response, create_error_response,
    GatewayInterface, execute_operation,
    get_parameter
)

HA_ASSISTANT_NAME_CACHE_KEY = "ha_assistant_name"


def process_alexa_ha_request(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Forward Alexa Smart Home directive to Home Assistant endpoint.
    Matches HA's reference lambda implementation.
    """
    try:
        log_debug(f"Processing Alexa directive: {event.get('directive', {}).get('header', {})}")
        
        # Get base URL from Parameter Store or environment
        base_url = get_parameter('home_assistant_url', '')
        if not base_url:
            return _create_error_response('BASE_URL not configured')
        
        base_url = base_url.rstrip('/')
        
        # Validate directive
        directive = event.get('directive')
        if not directive:
            return _create_error_response('Missing directive')
        
        # Extract token from directive (multiple possible locations)
        token = _extract_token_from_directive(directive)
        if not token:
            # Fallback to Parameter Store/env token for testing
            token = get_parameter('home_assistant_token', '')
        
        if not token:
            return _create_error_response('Missing authorization token', 'INVALID_AUTHORIZATION_CREDENTIAL')
        
        # Forward to HA's smart home endpoint
        url = f'{base_url}/api/alexa/smart_home'
        
        response = make_post_request(
            url,
            event,
            headers={
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            },
            timeout=10
        )
        
        # Handle response
        if not response.get('success'):
            log_error(f"HA request failed: {response.get('error')}")
            return _create_error_response('Home Assistant request failed', 'INTERNAL_ERROR')
        
        status_code = response.get('status_code', 200)
        
        if status_code >= 400:
            error_type = 'INVALID_AUTHORIZATION_CREDENTIAL' if status_code in (401, 403) else 'INTERNAL_ERROR'
            return _create_error_response(f'HA returned {status_code}', error_type)
        
        # Return HA's response
        return response.get('data', {})
        
    except Exception as e:
        log_error(f"Alexa request processing failed: {str(e)}")
        return _create_error_response(str(e), 'INTERNAL_ERROR')


def _extract_token_from_directive(directive: Dict[str, Any]) -> Optional[str]:
    """Extract bearer token from directive (handles multiple locations)."""
    # Try endpoint scope
    scope = directive.get('endpoint', {}).get('scope')
    
    # Try grantee (for Linking directive)
    if not scope:
        scope = directive.get('payload', {}).get('grantee')
    
    # Try payload scope (for Discovery directive)
    if not scope:
        scope = directive.get('payload', {}).get('scope')
    
    if scope and scope.get('type') == 'BearerToken':
        return scope.get('token')
    
    return None


def _create_error_response(message: str, error_type: str = 'INTERNAL_ERROR') -> Dict[str, Any]:
    """Create Alexa error response."""
    return {
        'event': {
            'header': {
                'namespace': 'Alexa',
                'name': 'ErrorResponse',
                'messageId': str(time.time()),
                'payloadVersion': '3'
            },
            'payload': {
                'type': error_type,
                'message': message
            }
        }
    }


def is_ha_extension_enabled() -> bool:
    """Check if HA extension is enabled."""
    return os.environ.get("HOME_ASSISTANT_ENABLED", "false").lower() == "true"


def get_ha_assistant_name() -> str:
    """Get configured assistant name."""
    try:
        cached = cache_get(HA_ASSISTANT_NAME_CACHE_KEY)
        if cached:
            return cached
        
        name = os.environ.get('HA_ASSISTANT_NAME', 'Jeeves')
        cache_set(HA_ASSISTANT_NAME_CACHE_KEY, name, ttl=3600)
        return name
    except:
        return 'Jeeves'


def get_ha_status() -> Dict[str, Any]:
    """Get HA connection status."""
    try:
        base_url = get_parameter('home_assistant_url', '')
        token = get_parameter('home_assistant_token', '')
        
        if not base_url or not token:
            return create_error_response("HA not configured")
        
        url = f'{base_url.rstrip("/")}/api/'
        response = execute_operation(
            GatewayInterface.HTTP_CLIENT,
            'get',
            url=url,
            headers={'Authorization': f'Bearer {token}'}
        )
        
        success = response.get('success') and response.get('status_code') == 200
        
        return create_success_response(
            "HA status checked",
            {'connected': success}
        ) if success else create_error_response("HA connection failed")
        
    except Exception as e:
        return create_error_response(f"Status check failed: {str(e)}")


def get_ha_diagnostic_info() -> Dict[str, Any]:
    """Get diagnostic information."""
    return create_success_response("Diagnostics", {
        'timestamp': time.time(),
        'ha_enabled': is_ha_extension_enabled(),
        'connection_status': 'forwarding',
        'assistant_name': get_ha_assistant_name(),
        'assistant_name_source': 'environment_variable',
        'configuration': {
            'base_url_configured': bool(get_parameter('home_assistant_url', '')),
            'token_configured': bool(get_parameter('home_assistant_token', '')),
            'timeout': 30,
            'ssl_verify': True
        },
        'connection_test': _test_ha_connection()
    })


def _test_ha_connection() -> Dict[str, Any]:
    """Test HA connection."""
    try:
        status = get_ha_status()
        return {
            'success': status.get('success', False),
            'error': status.get('error') if not status.get('success') else None
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}


def get_assistant_name_status() -> Dict[str, Any]:
    """Get assistant name status for diagnostics."""
    try:
        name = get_ha_assistant_name()
        return create_success_response("Assistant name retrieved", {
            'current_name': name,
            'source': 'environment_variable',
            'cached': bool(cache_get(HA_ASSISTANT_NAME_CACHE_KEY))
        })
    except Exception as e:
        return create_error_response(f"Failed to get assistant name: {str(e)}")


# EOF
