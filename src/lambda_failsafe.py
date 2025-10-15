"""
lambda_failsafe.py - Emergency Failsafe Handler (Optimized)
Version: 2025.10.15.01
Description: Standalone emergency backup handler for direct Home Assistant passthrough.
             Zero LEE dependencies - completely independent backup system.

Copyright 2025 Joseph Hersey

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

import os
import json
import logging
import urllib3
from typing import Dict, Any, Optional, Tuple


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
    
    Lazy loads boto3 only when needed to minimize cold start impact.
    
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
        # Lazy load boto3 only when SSM is needed
        import boto3
        
        ssm = boto3.client('ssm')
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
    3. Legacy environment variable names
    
    Supports SSM Parameter Store:
    - USE_PARAMETER_STORE=true enables SSM
    - PARAMETER_PREFIX sets base path (default: /lambda-execution-engine)
    - Reads: {prefix}/home_assistant/url, {prefix}/home_assistant/token
    
    Supports environment variables (new names):
    - HOME_ASSISTANT_URL
    - HOME_ASSISTANT_TOKEN
    - HOME_ASSISTANT_VERIFY_SSL
    
    Supports legacy environment variables:
    - BASE_URL
    - LONG_LIVED_ACCESS_TOKEN
    - NOT_VERIFY_SSL
    
    Returns:
        Dict containing validated configuration
        
    Raises:
        AssertionError: If required configuration is missing
    """
    # Check if SSM Parameter Store is enabled
    use_parameter_store = os.environ.get('USE_PARAMETER_STORE', 'false').lower() == 'true'
    parameter_prefix = os.environ.get('PARAMETER_PREFIX', '/lambda-execution-engine')
    
    _logger.debug('Configuration mode: use_parameter_store=%s, prefix=%s', use_parameter_store, parameter_prefix)
    
    # Load base URL
    base_url = None
    if use_parameter_store:
        base_url = _load_from_ssm(parameter_prefix, 'home_assistant/url')
    
    if base_url is None:
        # Fallback to environment variables (new name first, then legacy)
        base_url = os.environ.get('HOME_ASSISTANT_URL') or os.environ.get('BASE_URL')
    
    assert base_url is not None, 'Missing required configuration: HOME_ASSISTANT_URL (environment) or home_assistant/url (SSM)'
    
    # Normalize URL (strip trailing slash)
    base_url = base_url.strip('/')
    
    # Load SSL verification setting
    verify_ssl = True  # default
    
    if use_parameter_store:
        verify_ssl_ssm = _load_from_ssm(parameter_prefix, 'home_assistant/verify_ssl')
        if verify_ssl_ssm is not None:
            verify_ssl = verify_ssl_ssm.lower() != 'false'
    
    # Environment variables override SSM (if present)
    verify_ssl_env = os.environ.get('HOME_ASSISTANT_VERIFY_SSL')
    not_verify_ssl_env = os.environ.get('NOT_VERIFY_SSL')
    
    if verify_ssl_env is not None:
        verify_ssl = verify_ssl_env.lower() != 'false'
    elif not_verify_ssl_env is not None:
        verify_ssl = not_verify_ssl_env.lower() != 'true'
    
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

def _create_http_client(verify_ssl: bool, connect_timeout: float = 2.0, read_timeout: float = 10.0) -> urllib3.PoolManager:
    """
    Create configured urllib3 HTTP client.
    
    Args:
        verify_ssl: Whether to verify SSL certificates
        connect_timeout: Connection timeout in seconds
        read_timeout: Read timeout in seconds
        
    Returns:
        Configured urllib3.PoolManager instance
    """
    cert_reqs = 'CERT_REQUIRED' if verify_ssl else 'CERT_NONE'
    
    http = urllib3.PoolManager(
        cert_reqs=cert_reqs,
        timeout=urllib3.Timeout(connect=connect_timeout, read=read_timeout),
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

def _make_ha_request(http: urllib3.PoolManager, api_endpoint: str, token: str, event: Dict[str, Any]) -> urllib3.response.HTTPResponse:
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

def _parse_ha_response(response: urllib3.response.HTTPResponse, message_id: str = 'error') -> Dict[str, Any]:
    """
    Parse Home Assistant response and handle errors.
    
    Args:
        response: HTTP response from Home Assistant
        message_id: Message ID for error tracking
        
    Returns:
        Parsed JSON response or error response
    """
    if response.status >= 400:
        error_message = response.data.decode('utf-8', errors='replace')
        
        # Determine error type based on status code
        if response.status in (401, 403):
            error_type = 'INVALID_AUTHORIZATION_CREDENTIAL'
        else:
            error_type = 'INTERNAL_ERROR'
        
        _logger.error('Home Assistant error: status=%d, message=%s', response.status, error_message)
        return _build_alexa_error_response(error_type, error_message, message_id)
    
    # Parse successful response
    try:
        response_data = response.data.decode('utf-8')
        _logger.debug('Home Assistant response data: %s', response_data)
        return json.loads(response_data)
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        _logger.error('Failed to parse Home Assistant response: %s', str(e))
        return _build_alexa_error_response('INTERNAL_ERROR', f'Response parsing failed: {str(e)}', message_id)


# ===== MAIN HANDLER =====

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Emergency failsafe handler for Alexa directives.
    
    This is a completely standalone handler with zero LEE dependencies.
    It provides direct passthrough to Home Assistant's native Alexa API.
    
    Configuration Sources (in priority order):
        1. AWS Systems Manager Parameter Store (if enabled)
        2. Lambda Environment Variables
        3. Legacy environment variable names
    
    Environment Variables:
        USE_PARAMETER_STORE: Enable SSM Parameter Store (true/false)
        PARAMETER_PREFIX: SSM parameter path prefix (default: /lambda-execution-engine)
        
        HOME_ASSISTANT_URL or BASE_URL: Base URL of Home Assistant instance
        HOME_ASSISTANT_TOKEN or LONG_LIVED_ACCESS_TOKEN: Authentication token (debug only)
        HOME_ASSISTANT_VERIFY_SSL or NOT_VERIFY_SSL: SSL verification setting
        DEBUG_MODE or DEBUG: Enable debug logging
    
    SSM Parameter Store Paths (if USE_PARAMETER_STORE=true):
        {PARAMETER_PREFIX}/home_assistant/url: Base URL
        {PARAMETER_PREFIX}/home_assistant/token: Access token (SecureString recommended)
        {PARAMETER_PREFIX}/home_assistant/verify_ssl: SSL verification (optional)
    
    IAM Permissions Required (if using SSM):
        - ssm:GetParameter on arn:aws:ssm:REGION:ACCOUNT:parameter{PARAMETER_PREFIX}/*
    
    Args:
        event: Alexa directive event
        context: Lambda context
        
    Returns:
        Alexa response or error response
    """
    try:
        _logger.debug('Failsafe handler invoked: %s', event)
        
        # Load configuration
        config = _load_failsafe_config()
        
        # Validate payload version
        directive = event.get('directive', {})
        payload_version = directive.get('header', {}).get('payloadVersion')
        assert payload_version == '3', f'Unsupported payload version: {payload_version} (only v3 supported)'
        
        # Extract authentication token
        token = _extract_bearer_token(event, config['fallback_token'])
        
        # Create HTTP client
        http = _create_http_client(config['verify_ssl'])
        
        # Make request to Home Assistant
        response = _make_ha_request(http, config['api_endpoint'], token, event)
        
        # Parse and return response
        message_id = directive.get('header', {}).get('messageId', 'error')
        return _parse_ha_response(response, message_id)
        
    except AssertionError as e:
        _logger.error('Validation error: %s', str(e))
        return _build_alexa_error_response('INVALID_DIRECTIVE', str(e))
    
    except Exception as e:
        _logger.error('Unexpected error in failsafe handler: %s', str(e), exc_info=True)
        return _build_alexa_error_response('INTERNAL_ERROR', f'Failsafe handler error: {str(e)}')


# EOF
