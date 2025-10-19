"""
lambda_failsafe.py - Emergency Failsafe Handler (SELECTIVE IMPORTS)
Version: 2025.10.19.SELECTIVE
Description: Standalone emergency backup handler using preloaded modules

CRITICAL CHANGE: Uses preloaded urllib3 and boto3 from lambda_preload
- NO module-level boto3 import (was causing 8,500ms delay!)
- Uses _BOTO3_SSM_CLIENT from lambda_preload (already initialized)
- Uses PoolManager and Timeout from lambda_preload (already loaded)

Performance: Imports in ~0ms (everything preloaded!)

Copyright 2025 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

import os
import json
import logging
from typing import Dict, Any, Optional, Tuple

# Import preloaded modules (already initialized during Lambda INIT!)
from lambda_preload import PoolManager, Timeout, _BOTO3_SSM_CLIENT, _USE_PARAMETER_STORE


# ===== LOGGING SETUP =====

def _setup_logging() -> logging.Logger:
    """Configure logging based on environment."""
    debug_mode = bool(os.environ.get('DEBUG_MODE', os.environ.get('DEBUG')))
    logger = logging.getLogger('HomeAssistant-Failsafe')
    logger.setLevel(logging.DEBUG if debug_mode else logging.INFO)
    return logger


_logger = _setup_logging()


# ===== SSM PARAMETER STORE SUPPORT =====

def _load_from_ssm(parameter_prefix: str, key: str) -> Optional[str]:
    """
    Load parameter from AWS Systems Manager Parameter Store.
    
    Uses PRELOADED SSM client from lambda_preload (no import overhead!)
    
    IAM Permissions Required:
        Your Lambda execution role must have:
        {
          "Effect": "Allow",
          "Action": ["ssm:GetParameter"],
          "Resource": "arn:aws:ssm:REGION:ACCOUNT:parameter{parameter_prefix}/*"
        }
    
    Args:
        parameter_prefix: SSM parameter path prefix (e.g., /lambda-execution-engine)
        key: Parameter key relative to prefix (e.g., home_assistant/url)
        
    Returns:
        Parameter value or None if not found/access denied
    """
    try:
        # Use preloaded SSM client (NO IMPORT OVERHEAD!)
        if not _USE_PARAMETER_STORE or _BOTO3_SSM_CLIENT is None:
            _logger.debug('SSM not available - preload disabled or failed')
            return None
        
        ssm = _BOTO3_SSM_CLIENT
        param_path = f"{parameter_prefix}/{key}"
        
        _logger.debug('Reading SSM parameter: %s', param_path)
        
        response = ssm.get_parameter(Name=param_path, WithDecryption=True)
        value = response['Parameter']['Value']
        
        _logger.debug('Successfully loaded parameter from SSM: %s', param_path)
        return value
        
    except Exception as e:
        _logger.debug('Failed to load SSM parameter %s: %s', key, str(e))
        return None


# ===== CONFIGURATION MANAGEMENT =====

def _load_failsafe_config() -> Dict[str, Any]:
    """
    Load and validate failsafe configuration from SSM or environment variables.
    
    Configuration priority:
    1. SSM Parameter Store (if USE_PARAMETER_STORE=true)
    2. Environment variables
    3. Defaults
    """
    use_parameter_store = os.environ.get('USE_PARAMETER_STORE', 'false').lower() == 'true'
    parameter_prefix = os.environ.get('PARAMETER_PREFIX', '/lambda-execution-engine')
    
    # Load base URL
    base_url = None
    if use_parameter_store:
        base_url = _load_from_ssm(parameter_prefix, 'home_assistant/url')
    
    if base_url is None:
        base_url = os.environ.get('HOME_ASSISTANT_URL')
    
    if not base_url:
        raise ValueError('HOME_ASSISTANT_URL not configured')
    
    # Load SSL verification setting
    verify_ssl_str = os.environ.get('HOME_ASSISTANT_VERIFY_SSL', 'true').lower()
    verify_ssl = verify_ssl_str != 'false'
    
    # Debug mode
    debug_mode = bool(os.environ.get('DEBUG_MODE', os.environ.get('DEBUG')))
    
    # Fallback token for debug mode only
    # Try SSM first, then environment variables
    fallback_token = None
    if debug_mode:
        if use_parameter_store:
            fallback_token = _load_from_ssm(parameter_prefix, 'home_assistant/token')
        
        if fallback_token is None:
            fallback_token = os.environ.get('HOME_ASSISTANT_TOKEN') or os.environ.get('LONG_LIVED_ACCESS_TOKEN')
    
    config = {
        'base_url': base_url,
        'verify_ssl': verify_ssl,
        'debug_mode': debug_mode,
        'fallback_token': fallback_token,
        'api_endpoint': f'{base_url}/api/alexa/smart_home',
        'use_parameter_store': use_parameter_store
    }
    
    _logger.debug('Failsafe configuration loaded: base_url=%s, verify_ssl=%s, ssm=%s', 
                  base_url, verify_ssl, use_parameter_store)
    return config


# ===== TOKEN EXTRACTION =====

def _extract_bearer_token(event: Dict[str, Any], fallback_token: Optional[str] = None) -> str:
    """
    Extract Bearer token from Alexa directive event.
    
    Token can be located in multiple places depending on directive type:
    - directive.endpoint.scope (most directives)
    - directive.payload.grantee (AcceptGrant/Linking directive)
    - directive.payload.scope (Discovery directive)
    
    Args:
        event: Alexa directive event
        fallback_token: Optional fallback token for debug mode
        
    Returns:
        Bearer token string
        
    Raises:
        AssertionError: If token cannot be found or is invalid
    """
    directive = event.get('directive')
    assert directive is not None, 'Malformatted request - missing directive'
    
    # Try multiple locations for scope
    scope = directive.get('endpoint', {}).get('scope')
    
    if scope is None:
        # Try grantee for Linking directive
        scope = directive.get('payload', {}).get('grantee')
    
    if scope is None:
        # Try payload scope for Discovery directive
        scope = directive.get('payload', {}).get('scope')
    
    assert scope is not None, 'Malformatted request - missing endpoint.scope'
    assert scope.get('type') == 'BearerToken', 'Only BearerToken authentication is supported'
    
    token = scope.get('token')
    
    # Use fallback token only in debug mode if no token found
    if token is None and fallback_token:
        _logger.warning('Using fallback token for debug purposes')
        token = fallback_token
    
    assert token is not None, 'Missing bearer token'
    
    return token


# ===== HTTP CLIENT =====

def _create_http_client(verify_ssl: bool, connect_timeout: float = 2.0, read_timeout: float = 10.0):
    """
    Create configured HTTP client using PRELOADED urllib3 classes.
    
    Uses PoolManager and Timeout from lambda_preload (NO IMPORT OVERHEAD!)
    
    Args:
        verify_ssl: Whether to verify SSL certificates
        connect_timeout: Connection timeout in seconds
        read_timeout: Read timeout in seconds
        
    Returns:
        Configured urllib3.PoolManager instance
    """
    cert_reqs = 'CERT_REQUIRED' if verify_ssl else 'CERT_NONE'
    
    # Use preloaded classes (NO IMPORT OVERHEAD!)
    http = PoolManager(
        cert_reqs=cert_reqs,
        timeout=Timeout(connect=connect_timeout, read=read_timeout),
        maxsize=5,
        retries=False
    )
    
    _logger.debug('HTTP client created: verify_ssl=%s, timeouts=(%s, %s)', verify_ssl, connect_timeout, read_timeout)
    return http


# ===== ERROR RESPONSE BUILDER =====

def _build_alexa_error_response(error_type: str, message: str, message_id: str = 'error') -> Dict[str, Any]:
    """
    Build standardized Alexa error response.
    
    Args:
        error_type: Alexa error type (INVALID_AUTHORIZATION_CREDENTIAL, INTERNAL_ERROR, etc.)
        message: Human-readable error message
        message_id: Message ID for tracking
        
    Returns:
        Alexa-formatted error response
    """
    return {
        'event': {
            'header': {
                'namespace': 'Alexa',
                'name': 'ErrorResponse',
                'messageId': message_id,
                'payloadVersion': '3'
            },
            'payload': {
                'type': error_type,
                'message': message
            }
        }
    }


# ===== HOME ASSISTANT REQUEST =====

def _make_ha_request(http, api_endpoint: str, token: str, event: Dict[str, Any]):
    """
    Make HTTP request to Home Assistant Alexa API.
    
    Args:
        http: Configured urllib3 HTTP client
        api_endpoint: Full API endpoint URL
        token: Bearer token for authentication
        event: Full Alexa event to forward
        
    Returns:
        HTTP response from Home Assistant
        
    Raises:
        Exception: If request fails
    """
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
    }
    
    body = json.dumps(event).encode('utf-8')
    
    _logger.debug('Making request to Home Assistant: %s', api_endpoint)
    
    response = http.request(
        'POST',
        api_endpoint,
        headers=headers,
        body=body
    )
    
    _logger.debug('Home Assistant response: status=%d', response.status)
    return response


# ===== RESPONSE PARSER =====

def _parse_ha_response(response, message_id: str = 'error') -> Dict[str, Any]:
    """
    Parse Home Assistant response and handle errors.
    
    Args:
        response: urllib3 HTTPResponse object
        message_id: Message ID for error responses
        
    Returns:
        Parsed response dict or error response
    """
    if response.status != 200:
        _logger.error('Home Assistant error: HTTP %d', response.status)
        return _build_alexa_error_response(
            'INTERNAL_ERROR',
            f'Home Assistant returned HTTP {response.status}',
            message_id
        )
    
    try:
        response_data = json.loads(response.data.decode('utf-8'))
        _logger.debug('Successfully parsed Home Assistant response')
        return response_data
    except Exception as e:
        _logger.error('Failed to parse Home Assistant response: %s', str(e))
        return _build_alexa_error_response(
            'INTERNAL_ERROR',
            f'Failed to parse response: {str(e)}',
            message_id
        )


# ===== MAIN HANDLER =====

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Emergency failsafe Lambda handler - direct Home Assistant passthrough.
    
    This handler bypasses all LEE infrastructure and forwards requests
    directly to Home Assistant. Use only in emergency situations.
    """
    _logger.info('FAILSAFE MODE: Direct Home Assistant passthrough')
    _logger.debug('Event: %s', json.dumps(event))
    
    try:
        # Load configuration
        config = _load_failsafe_config()
        
        # Extract bearer token
        token = _extract_bearer_token(event, config['fallback_token'])
        
        # Create HTTP client (uses preloaded urllib3!)
        http = _create_http_client(config['verify_ssl'])
        
        # Forward request to Home Assistant
        response = _make_ha_request(http, config['api_endpoint'], token, event)
        
        # Parse and return response
        message_id = event.get('directive', {}).get('header', {}).get('messageId', 'unknown')
        result = _parse_ha_response(response, message_id)
        
        _logger.info('FAILSAFE: Request completed successfully')
        return result
        
    except AssertionError as e:
        _logger.error('FAILSAFE: Validation error - %s', str(e))
        return _build_alexa_error_response('INVALID_DIRECTIVE', str(e))
        
    except Exception as e:
        _logger.error('FAILSAFE: Unexpected error - %s', str(e), exc_info=True)
        return _build_alexa_error_response('INTERNAL_ERROR', f'Failsafe error: {str(e)}')


# EOF
