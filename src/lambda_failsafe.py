"""
lambda_failsafe.py - Emergency Failsafe Handler
Version: 2025.10.15.01
Description: Standalone failsafe for Home Assistant Alexa integration.
             COMPLETELY INDEPENDENT - No SUGA imports, no extensions.

Copyright 2025 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).

USAGE:
  Set these Lambda environment variables to activate:
    LEE_FAILSAFE_ENABLED=true
    HOME_ASSISTANT_URL=http://192.168.1.100:8123
    HOME_ASSISTANT_TOKEN=your_long_lived_token
    HOME_ASSISTANT_VERIFY_SSL=false  (optional, default: true)
    DEBUG_MODE=false  (optional, default: false)
"""

import os
import json
import logging
import urllib3

# Initialize logger
_debug = os.getenv('DEBUG_MODE', 'false').lower() == 'true'
_logger = logging.getLogger('LEE-Failsafe')
_logger.setLevel(logging.DEBUG if _debug else logging.INFO)


def lambda_handler(event, context):
    """
    Emergency failsafe handler for Home Assistant Alexa integration.
    Routes all requests directly to Home Assistant's /api/alexa/smart_home endpoint.
    """
    _logger.info("FAILSAFE MODE ACTIVE - Routing to Home Assistant directly")
    _logger.debug(f"Event: {json.dumps(event, default=str)}")

    # Load configuration from environment
    base_url = os.getenv('HOME_ASSISTANT_URL')
    if not base_url:
        _logger.error("HOME_ASSISTANT_URL not configured")
        return _create_error_response(
            'INVALID_CONFIGURATION',
            'HOME_ASSISTANT_URL environment variable not set'
        )
    
    base_url = base_url.strip("/")
    _logger.info(f"Using Home Assistant URL: {base_url}")

    # Validate Alexa directive structure
    directive = event.get('directive')
    if not directive:
        _logger.error("Missing directive in request")
        return _create_error_response(
            'INVALID_DIRECTIVE',
            'Malformatted request - missing directive'
        )
    
    # Validate payload version
    payload_version = directive.get('header', {}).get('payloadVersion')
    if payload_version != '3':
        _logger.error(f"Unsupported payload version: {payload_version}")
        return _create_error_response(
            'INVALID_DIRECTIVE',
            'Only payloadVersion 3 is supported'
        )
    
    # Extract access token from multiple possible locations
    token = _extract_token(directive)
    if not token:
        _logger.error("No access token found in request")
        return _create_error_response(
            'INVALID_AUTHORIZATION_CREDENTIAL',
            'Missing access token in request'
        )
    
    # Setup SSL verification
    verify_ssl = os.getenv('HOME_ASSISTANT_VERIFY_SSL', 'true').lower() == 'true'
    _logger.debug(f"SSL verification: {verify_ssl}")
    
    # Create HTTP pool manager
    http = urllib3.PoolManager(
        cert_reqs='CERT_REQUIRED' if verify_ssl else 'CERT_NONE',
        timeout=urllib3.Timeout(connect=2.0, read=10.0)
    )
    
    # Forward request to Home Assistant
    try:
        _logger.info("Forwarding request to Home Assistant")
        response = http.request(
            'POST',
            f'{base_url}/api/alexa/smart_home',
            headers={
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json',
            },
            body=json.dumps(event).encode('utf-8'),
        )
        
        _logger.info(f"Home Assistant response status: {response.status}")
        
        # Handle error responses
        if response.status >= 400:
            error_message = response.data.decode('utf-8')
            _logger.error(f"Home Assistant error: {error_message}")
            
            error_type = 'INVALID_AUTHORIZATION_CREDENTIAL' if response.status in (401, 403) else 'INTERNAL_ERROR'
            return _create_error_response(error_type, error_message)
        
        # Parse and return successful response
        response_data = json.loads(response.data.decode('utf-8'))
        _logger.debug(f"Response: {json.dumps(response_data, default=str)}")
        return response_data
        
    except urllib3.exceptions.TimeoutError as e:
        _logger.error(f"Request timeout: {str(e)}")
        return _create_error_response(
            'INTERNAL_ERROR',
            'Request to Home Assistant timed out'
        )
    except urllib3.exceptions.HTTPError as e:
        _logger.error(f"HTTP error: {str(e)}")
        return _create_error_response(
            'INTERNAL_ERROR',
            f'HTTP error communicating with Home Assistant: {str(e)}'
        )
    except Exception as e:
        _logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return _create_error_response(
            'INTERNAL_ERROR',
            f'Unexpected error: {str(e)}'
        )


def _extract_token(directive: dict) -> str:
    """
    Extract access token from directive.
    Tries multiple locations in order:
      1. endpoint.scope.token
      2. payload.grantee.token (for Linking directives)
      3. payload.scope.token (for Discovery directives)
      4. HOME_ASSISTANT_TOKEN env var (debug mode only)
    """
    # Try endpoint.scope
    scope = directive.get('endpoint', {}).get('scope')
    if scope and scope.get('type') == 'BearerToken':
        token = scope.get('token')
        if token:
            return token
    
    # Try payload.grantee (Linking directive)
    grantee = directive.get('payload', {}).get('grantee')
    if grantee and grantee.get('type') == 'BearerToken':
        token = grantee.get('token')
        if token:
            return token
    
    # Try payload.scope (Discovery directive)
    payload_scope = directive.get('payload', {}).get('scope')
    if payload_scope and payload_scope.get('type') == 'BearerToken':
        token = payload_scope.get('token')
        if token:
            return token
    
    # Fall back to environment variable in debug mode
    if _debug:
        env_token = os.getenv('HOME_ASSISTANT_TOKEN')
        if env_token:
            _logger.warning("Using token from HOME_ASSISTANT_TOKEN environment variable (debug mode)")
            return env_token
    
    return None


def _create_error_response(error_type: str, message: str) -> dict:
    """Create Alexa error response."""
    return {
        'event': {
            'header': {
                'namespace': 'Alexa',
                'name': 'ErrorResponse',
                'messageId': 'failsafe-error',
                'payloadVersion': '3'
            },
            'payload': {
                'type': error_type,
                'message': message
            }
        }
    }


# EOF
