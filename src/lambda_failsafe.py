"""
lambda_failsafe.py - Emergency Failsafe Handler (SIMPLIFIED)
Version: 2025.10.20.TOKEN_ONLY
Description: Direct passthrough to Home Assistant with ONLY token from SSM

BREAKING CHANGE:
- SSM retrieves ONLY the Home Assistant token
- ALL other configuration from environment variables
- Faster failsafe activation, simpler implementation

CHANGELOG:
- 2025.10.20.TOKEN_ONLY: SIMPLIFIED - Only token from SSM
  - Uses simplified config_param_store.get_ha_token()
  - All other config from environment
  - Improved debug output
  - Faster failsafe mode

Copyright 2025 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

import os
import json
import time
from typing import Dict, Any, Optional
from urllib import request
from urllib.error import URLError, HTTPError


def _is_debug_mode() -> bool:
    """Check if DEBUG_MODE is enabled."""
    return os.getenv('DEBUG_MODE', 'false').lower() == 'true'


def _is_debug_timings() -> bool:
    """Check if DEBUG_TIMINGS is enabled."""
    return os.getenv('DEBUG_TIMINGS', 'false').lower() == 'true'


def _print_debug(msg: str):
    """Print debug message only if DEBUG_MODE=true."""
    if _is_debug_mode():
        print(f"[FAILSAFE_DEBUG] {msg}")


def _print_timing(msg: str):
    """Print timing message only if DEBUG_TIMINGS=true."""
    if _is_debug_timings():
        print(f"[FAILSAFE_TIMING] {msg}")


# ===== LOGGING =====

class _Logger:
    """Minimal logger for failsafe mode."""
    
    @staticmethod
    def debug(msg: str):
        if _is_debug_mode():
            print(f"[FAILSAFE] DEBUG: {msg}")
    
    @staticmethod
    def info(msg: str):
        print(f"[FAILSAFE] INFO: {msg}")
    
    @staticmethod
    def warning(msg: str):
        print(f"[FAILSAFE] WARNING: {msg}")
    
    @staticmethod
    def error(msg: str):
        print(f"[FAILSAFE] ERROR: {msg}")


_logger = _Logger()


# ===== TOKEN LOADING =====

def _load_token_from_ssm() -> Optional[str]:
    """
    Load Home Assistant token from SSM Parameter Store.
    
    Only used if USE_PARAMETER_STORE=true in failsafe mode.
    
    Returns:
        Token string or None
    """
    _start = time.perf_counter()
    _print_timing("Loading token from SSM...")
    _print_debug("Attempting SSM token retrieval in failsafe mode")
    
    try:
        # Lazy import config_param_store
        from config_param_store import get_ha_token
        
        token = get_ha_token(use_cache=True)
        
        _elapsed = (time.perf_counter() - _start) * 1000
        _print_timing(f"SSM token retrieval: {_elapsed:.2f}ms, success={token is not None}")
        
        if token:
            _print_debug("Token retrieved from SSM")
            _logger.info("Token loaded from SSM Parameter Store")
        else:
            _print_debug("SSM returned None")
            _logger.warning("SSM token retrieval returned None")
        
        return token
        
    except Exception as e:
        _elapsed = (time.perf_counter() - _start) * 1000
        _print_timing(f"SSM token retrieval failed: {_elapsed:.2f}ms")
        _print_debug(f"SSM exception: {e}")
        _logger.error(f"Failed to load token from SSM: {e}")
        return None


# ===== CONFIGURATION =====

def _load_failsafe_config() -> Dict[str, Any]:
    """
    Load failsafe configuration.
    
    Configuration priority for token:
    1. SSM Parameter Store (if USE_PARAMETER_STORE=true)
    2. HOME_ASSISTANT_TOKEN environment variable
    3. LONG_LIVED_ACCESS_TOKEN environment variable (legacy)
    
    All other configuration from environment only.
    
    Returns:
        Configuration dictionary
        
    Raises:
        ValueError: If HOME_ASSISTANT_URL not configured
    """
    _start = time.perf_counter()
    _print_timing("===== LOAD_FAILSAFE_CONFIG START =====")
    _print_debug("Loading failsafe configuration")
    
    use_parameter_store = os.getenv('USE_PARAMETER_STORE', 'false').lower() == 'true'
    
    # Load base URL from environment (ALWAYS from environment in failsafe)
    base_url = os.getenv('HOME_ASSISTANT_URL')
    if not base_url:
        _print_debug("HOME_ASSISTANT_URL not set")
        raise ValueError('HOME_ASSISTANT_URL not configured')
    
    _print_debug(f"Base URL: {base_url}")
    
    # Load SSL verification setting
    verify_ssl_str = os.getenv('HOME_ASSISTANT_VERIFY_SSL', 'true').lower()
    verify_ssl = verify_ssl_str != 'false'
    _print_debug(f"SSL verification: {verify_ssl}")
    
    # Load token
    fallback_token = None
    
    if use_parameter_store:
        _print_debug("USE_PARAMETER_STORE=true, attempting SSM")
        fallback_token = _load_token_from_ssm()
    
    # Fallback to environment if SSM failed or disabled
    if fallback_token is None:
        _print_debug("Loading token from environment")
        fallback_token = os.getenv('HOME_ASSISTANT_TOKEN') or os.getenv('LONG_LIVED_ACCESS_TOKEN')
        
        if fallback_token:
            _print_debug("Token found in environment")
        else:
            _print_debug("No token in environment")
    
    config = {
        'base_url': base_url,
        'verify_ssl': verify_ssl,
        'debug_mode': _is_debug_mode(),
        'fallback_token': fallback_token,
        'api_endpoint': f'{base_url}/api/alexa/smart_home',
        'use_parameter_store': use_parameter_store
    }
    
    _elapsed = (time.perf_counter() - _start) * 1000
    _print_timing(f"===== LOAD_FAILSAFE_CONFIG COMPLETE: {_elapsed:.2f}ms =====")
    
    _logger.debug(f'Failsafe configuration loaded: base_url={base_url}, verify_ssl={verify_ssl}, ssm={use_parameter_store}, has_token={fallback_token is not None}')
    
    return config


# ===== TOKEN EXTRACTION =====

def _extract_bearer_token(event: Dict[str, Any], fallback_token: Optional[str] = None) -> str:
    """
    Extract Bearer token from Alexa directive event.
    
    Priority:
    1. directive.endpoint.scope.token (user-linked account)
    2. directive.payload.scope.token (discovery phase)
    3. fallback_token (from SSM or environment)
    
    Args:
        event: Alexa Smart Home event
        fallback_token: Fallback token if not in event
        
    Returns:
        Bearer token
        
    Raises:
        ValueError: If no token found
    """
    _print_debug("Extracting bearer token from event")
    
    directive = event.get('directive', {})
    
    # Try endpoint scope
    endpoint = directive.get('endpoint', {})
    scope = endpoint.get('scope', {})
    token = scope.get('token')
    
    if token:
        _print_debug("Token found in directive.endpoint.scope")
        return token
    
    # Try payload scope
    payload = directive.get('payload', {})
    scope = payload.get('scope', {})
    token = scope.get('token')
    
    if token:
        _print_debug("Token found in directive.payload.scope")
        return token
    
    # Use fallback token (from SSM or environment)
    if fallback_token:
        _print_debug("Using fallback token from configuration")
        _logger.warning('Using fallback token (no token in Alexa event)')
        return fallback_token
    
    _print_debug("No token found anywhere")
    raise ValueError('No Bearer token found in event or configuration')


# ===== HTTP REQUEST =====

def _forward_to_home_assistant(event: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Forward Alexa directive directly to Home Assistant.
    
    Args:
        event: Alexa Smart Home event
        config: Failsafe configuration
        
    Returns:
        Home Assistant response
    """
    _start = time.perf_counter()
    _print_timing("===== FORWARD_TO_HOME_ASSISTANT START =====")
    _print_debug("Forwarding request to Home Assistant")
    
    try:
        # Extract token
        token = _extract_bearer_token(event, config.get('fallback_token'))
        _print_debug(f"Token extracted (length={len(token)})")
        
        # Prepare request
        url = config['api_endpoint']
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        body = json.dumps(event).encode('utf-8')
        
        _print_debug(f"Request URL: {url}")
        _print_timing("Sending HTTP request...")
        
        # Create request
        req = request.Request(url, data=body, headers=headers, method='POST')
        
        # Make HTTP call
        _http_start = time.perf_counter()
        with request.urlopen(req, timeout=30) as response:
            response_body = response.read().decode('utf-8')
            response_data = json.loads(response_body)
        
        _http_time = (time.perf_counter() - _http_start) * 1000
        _print_timing(f"HTTP request: {_http_time:.2f}ms")
        _print_debug(f"Response received: status=200")
        
        _total_time = (time.perf_counter() - _start) * 1000
        _print_timing(f"===== FORWARD_TO_HOME_ASSISTANT COMPLETE: {_total_time:.2f}ms =====")
        
        return response_data
        
    except HTTPError as e:
        _error_time = (time.perf_counter() - _start) * 1000
        _print_timing(f"HTTP error after {_error_time:.2f}ms: status={e.code}")
        _print_debug(f"HTTP error: {e.code} {e.reason}")
        _logger.error(f'HTTP error forwarding to HA: {e.code} {e.reason}')
        raise
        
    except URLError as e:
        _error_time = (time.perf_counter() - _start) * 1000
        _print_timing(f"URL error after {_error_time:.2f}ms")
        _print_debug(f"URL error: {e.reason}")
        _logger.error(f'URL error forwarding to HA: {e.reason}')
        raise
        
    except Exception as e:
        _error_time = (time.perf_counter() - _start) * 1000
        _print_timing(f"Exception after {_error_time:.2f}ms: {e}")
        _print_debug(f"Exception: {e}")
        _logger.error(f'Error forwarding to HA: {e}')
        raise


# ===== MAIN HANDLER =====

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Failsafe Lambda handler.
    
    Emergency mode: bypass all LEE/SUGA infrastructure, forward directly to HA.
    
    Args:
        event: Alexa Smart Home event
        context: Lambda context
        
    Returns:
        Alexa Smart Home response
    """
    _start = time.perf_counter()
    _print_timing("===== FAILSAFE HANDLER START =====")
    
    _logger.info('âš ï¸ FAILSAFE MODE ACTIVATED - Bypassing Lambda Execution Engine')
    _print_debug("Failsafe mode handler invoked")
    
    try:
        # Load configuration
        config = _load_failsafe_config()
        
        # Forward to Home Assistant
        response = _forward_to_home_assistant(event, config)
        
        _total_time = (time.perf_counter() - _start) * 1000
        _print_timing(f"===== FAILSAFE HANDLER COMPLETE: {_total_time:.2f}ms =====")
        
        _logger.info(f'âœ"ï¸ Failsafe request successful ({_total_time:.0f}ms)')
        
        return response
        
    except Exception as e:
        _error_time = (time.perf_counter() - _start) * 1000
        _print_timing(f"===== FAILSAFE HANDLER FAILED: {_error_time:.2f}ms =====")
        _print_debug(f"Failsafe handler exception: {e}")
        
        _logger.error(f'â›"ï¸ Failsafe request failed: {e}')
        
        # Return error response in Alexa format
        return {
            'event': {
                'header': {
                    'namespace': 'Alexa',
                    'name': 'ErrorResponse',
                    'messageId': event.get('directive', {}).get('header', {}).get('messageId', 'unknown'),
                    'payloadVersion': '3'
                },
                'payload': {
                    'type': 'INTERNAL_ERROR',
                    'message': f'Failsafe mode error: {str(e)}'
                }
            }
        }


# EOF
