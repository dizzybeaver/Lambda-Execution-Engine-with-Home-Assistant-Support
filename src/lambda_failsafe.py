"""
lambda_failsafe.py

Version: 2025.1205.01
Date: 2025-12-05
Purpose: Failsafe Alexa handler with LWA OAuth support

CHANGES (2025.1205.01 - LWA MIGRATION):
- REMOVED: fallback_token parameter from _extract_bearer_token()
- REMOVED: SSM token fallback logic
- MODIFIED: Token extraction to LWA-only (directive-based)
- ADDED: Enhanced error handling for missing tokens
- ADDED: Debug logging for token location tracking
- UPDATED: lambda_failsafe_handler() for LWA OAuth flow

LWA Migration: Token MUST come from Alexa directive (OAuth flow).
No SSM fallback token support. Account linking required.

Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

import json
import os
import uuid
from typing import Any, Dict, Optional
import time
import requests

# Gateway imports
from gateway import (
    log_info,
    log_error,
    log_warning,
    log_debug,
    increment_counter,
    record_metric,
    generate_correlation_id
)


# ===== CONFIGURATION =====

def _load_failsafe_config() -> Dict[str, Any]:
    """
    Load failsafe configuration from environment.
    
    LWA Migration: No token in config.
    Token comes from Alexa directive only.
    """
    return {
        'ha_url': os.environ.get('HOME_ASSISTANT_URL', 'https://homeassistant.local:8123'),
        'timeout': int(os.environ.get('HOME_ASSISTANT_TIMEOUT', '30')),
        'verify_ssl': os.environ.get('VERIFY_SSL', 'true').lower() == 'true'
    }


# ===== TOKEN EXTRACTION (LWA) =====

def _extract_bearer_token(event: Dict[str, Any]) -> str:
    """
    Extract bearer token from Alexa directive.
    
    LWA Migration: Removed fallback token support.
    Token MUST come from Alexa directive (OAuth flow).
    
    Priority:
        1. directive.endpoint.scope.token (standard location)
        2. directive.payload.scope.token (discovery/grant)
    
    Args:
        event: Alexa Smart Home event
        
    Returns:
        Bearer token string
        
    Raises:
        ValueError: If no token found in directive
    """
    directive = event.get('directive', {})
    
    # Try endpoint scope (most common for control directives)
    endpoint = directive.get('endpoint', {})
    scope = endpoint.get('scope', {})
    token = scope.get('token')
    
    if token:
        log_debug('Token found in directive.endpoint.scope')
        increment_counter('alexa_token_extracted_endpoint')
        return token
    
    # Try payload scope (discovery/grant directives)
    payload = directive.get('payload', {})
    scope = payload.get('scope', {})
    token = scope.get('token')
    
    if token:
        log_debug('Token found in directive.payload.scope')
        increment_counter('alexa_token_extracted_payload')
        return token
    
    # LWA Migration: No fallback token
    log_error('No token in Alexa directive - account linking may not be configured')
    increment_counter('alexa_token_missing')
    
    raise ValueError('No Bearer token in Alexa directive (LWA account linking required)')


# ===== ERROR RESPONSE =====

def _create_error_response(error_type: str, message: str, correlation_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Create Alexa error response.
    
    Args:
        error_type: Alexa error type
        message: Error message
        correlation_id: Optional correlation ID
        
    Returns:
        Alexa ErrorResponse
    """
    response = {
        'event': {
            'header': {
                'namespace': 'Alexa',
                'name': 'ErrorResponse',
                'messageId': str(uuid.uuid4()),
                'payloadVersion': '3'
            },
            'payload': {
                'type': error_type,
                'message': message
            }
        }
    }
    
    if correlation_id:
        response['event']['header']['correlationToken'] = correlation_id
    
    return response


# ===== HA FORWARDING =====

def _forward_to_home_assistant(event: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Forward Alexa directive to Home Assistant.
    
    Args:
        event: Alexa directive
        config: Configuration including token
        
    Returns:
        HA response or error response
    """

    correlation_id = generate_correlation_id()
    start_time = time.perf_counter()
    
    try:
        # Extract directive info
        directive = event.get('directive', {})
        header = directive.get('header', {})
        namespace = header.get('namespace', 'Unknown')
        name = header.get('name', 'Unknown')
        
        log_info(
            f'Forwarding to HA: {namespace}.{name}',
            correlation_id=correlation_id
        )
        
        # Build HA API endpoint
        ha_url = config['ha_url'].rstrip('/')
        endpoint = f'{ha_url}/api/alexa/smart_home'
        
        # Headers with OAuth token
        headers = {
            'Authorization': f"Bearer {config['token']}",
            'Content-Type': 'application/json'
        }
        
        # Forward directive
        response = requests.post(
            endpoint,
            json=event,
            headers=headers,
            timeout=config.get('timeout', 30),
            verify=config.get('verify_ssl', True)
        )
        
        duration_ms = (time.perf_counter() - start_time) * 1000
        
        # Check response
        if response.status_code == 200:
            log_info(
                f'HA response success: {namespace}.{name}',
                correlation_id=correlation_id,
                duration_ms=duration_ms
            )
            increment_counter('ha_forward_success')
            record_metric('ha_forward_duration_ms', duration_ms)
            
            return response.json()
        else:
            log_error(
                f'HA response error: {response.status_code}',
                correlation_id=correlation_id,
                status_code=response.status_code,
                response_text=response.text[:200]
            )
            increment_counter('ha_forward_error')
            
            return _create_error_response(
                'ENDPOINT_UNREACHABLE',
                f'Home Assistant returned {response.status_code}',
                correlation_id
            )
            
    except requests.exceptions.Timeout:
        duration_ms = (time.perf_counter() - start_time) * 1000
        log_error(
            'HA request timeout',
            correlation_id=correlation_id,
            duration_ms=duration_ms
        )
        increment_counter('ha_forward_timeout')
        
        return _create_error_response(
            'ENDPOINT_UNREACHABLE',
            'Home Assistant request timeout',
            correlation_id
        )
        
    except requests.exceptions.RequestException as e:
        duration_ms = (time.perf_counter() - start_time) * 1000
        log_error(
            f'HA request failed: {str(e)}',
            correlation_id=correlation_id,
            duration_ms=duration_ms
        )
        increment_counter('ha_forward_network_error')
        
        return _create_error_response(
            'ENDPOINT_UNREACHABLE',
            f'Home Assistant connection failed: {str(e)}',
            correlation_id
        )
        
    except Exception as e:
        duration_ms = (time.perf_counter() - start_time) * 1000
        log_error(
            f'HA forward unexpected error: {str(e)}',
            correlation_id=correlation_id,
            duration_ms=duration_ms
        )
        increment_counter('ha_forward_unexpected_error')
        
        return _create_error_response(
            'INTERNAL_ERROR',
            'Failed to process request',
            correlation_id
        )


# ===== HANDLER =====

def lambda_failsafe_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Failsafe Alexa handler (LWA-enabled).
    
    LWA Migration: Token MUST come from Alexa directive.
    No fallback token support. Account linking required.
    
    Args:
        event: Alexa Smart Home event
        context: Lambda context
        
    Returns:
        Alexa response or error response
    """
    correlation_id = generate_correlation_id()
    start_time = time.perf_counter()
    
    try:
        log_info('Failsafe handler invoked', correlation_id=correlation_id)
        increment_counter('failsafe_handler_invoked')
        
        # Load configuration (no token in config)
        config = _load_failsafe_config()
        
        # Extract token from directive (NO FALLBACK)
        try:
            token = _extract_bearer_token(event)
        except ValueError as e:
            # Token missing - account linking not configured
            log_error(
                f'Token extraction failed: {str(e)}',
                correlation_id=correlation_id
            )
            increment_counter('failsafe_token_missing')
            
            return {
                'event': {
                    'header': {
                        'namespace': 'Alexa',
                        'name': 'ErrorResponse',
                        'messageId': str(uuid.uuid4()),
                        'payloadVersion': '3'
                    },
                    'payload': {
                        'type': 'INVALID_AUTHORIZATION_CREDENTIAL',
                        'message': 'Account linking required. Please link your account in the Alexa app.'
                    }
                }
            }
        
        # Add token to config for forwarding
        config['token'] = token
        
        # Forward to HA with directive token
        response = _forward_to_home_assistant(event, config)
        
        duration_ms = (time.perf_counter() - start_time) * 1000
        log_info(
            'Failsafe handler complete',
            correlation_id=correlation_id,
            duration_ms=duration_ms
        )
        record_metric('failsafe_handler_duration_ms', duration_ms)
        increment_counter('failsafe_handler_success')
        
        return response
        
    except Exception as e:
        duration_ms = (time.perf_counter() - start_time) * 1000
        log_error(
            f'Failsafe handler error: {str(e)}',
            correlation_id=correlation_id,
            duration_ms=duration_ms
        )
        increment_counter('failsafe_handler_error')
        
        return _create_error_response(
            'INTERNAL_ERROR',
            'An unexpected error occurred',
            correlation_id
        )


# EOF
