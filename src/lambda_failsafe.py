"""
lambda_failsafe.py - Emergency Failsafe Handler (INDEPENDENT)
Version: 2025.10.21.INDEPENDENT
Description: Direct passthrough to Home Assistant, NO SUGA dependencies

CRITICAL: This file must work independently of SUGA infrastructure
- Simple in-memory cache (no gateway)
- Direct boto3 SSM (no config_param_store)
- Minimal dependencies (stdlib + boto3)

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


# ===== SIMPLE IN-MEMORY CACHE (NO GATEWAY DEPENDENCY) =====

_TOKEN_CACHE = {'value': None, 'timestamp': 0}
_CACHE_TTL = 300  # 5 minutes


def _simple_cache_get(key: str) -> Optional[str]:
    """Simple cache get - no gateway dependency."""
    if key == 'ssm_token':
        if _TOKEN_CACHE['value'] and (time.time() - _TOKEN_CACHE['timestamp'] < _CACHE_TTL):
            return _TOKEN_CACHE['value']
    return None


def _simple_cache_set(key: str, value: str):
    """Simple cache set - no gateway dependency."""
    if key == 'ssm_token':
        _TOKEN_CACHE['value'] = value
        _TOKEN_CACHE['timestamp'] = time.time()


# ===== TOKEN LOADING =====

def _load_token_from_ssm() -> Optional[str]:
    """
    Load Home Assistant token from SSM Parameter Store.
    
    INDEPENDENCE: Uses simple in-memory cache, NO gateway dependencies.
    Only used if USE_PARAMETER_STORE=true in failsafe mode.
    
    Returns:
        Token string or None
    """
    _start = time.perf_counter()
    _print_timing("Loading token from SSM...")
    _print_debug("Attempting SSM token retrieval in failsafe mode")
    
    try:
        # Check simple cache first
        cached = _simple_cache_get('ssm_token')
        if cached:
            _elapsed = (time.perf_counter() - _start) * 1000
            _print_timing(f"SSM token (CACHED): {_elapsed:.2f}ms")
            _logger.info("Token loaded from failsafe cache")
            return cached
        
        # Direct SSM retrieval - bypass config_param_store to avoid gateway dependency
        _print_debug("Cache miss, fetching from SSM")
        import boto3
        
        param_prefix = os.environ.get('PARAMETER_PREFIX', '/lambda-execution-engine')
        param_path = f"{param_prefix}/home_assistant/token"
        
        _print_debug(f"SSM parameter path: {param_path}")
        
        ssm = boto3.client('ssm')
        response = ssm.get_parameter(Name=param_path, WithDecryption=True)
        token = response['Parameter']['Value']
        
        # Cache it
        _simple_cache_set('ssm_token', token)
        
        _elapsed = (time.perf_counter() - _start) * 1000
        _print_timing(f"SSM token retrieval: {_elapsed:.2f}ms, success=True")
        _logger.info("Token loaded from SSM Parameter Store")
        
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
    """
    _start = time.perf_counter()
    _print_timing("===== LOAD_FAILSAFE_CONFIG START =====")
    _print_debug("Loading failsafe configuration")
    
    # Get token
    use_param_store = os.environ.get('USE_PARAMETER_STORE', 'false').lower() == 'true'
    
    if use_param_store:
        _print_debug("USE_PARAMETER_STORE=true, attempting SSM")
        token = _load_token_from_ssm()
    else:
        _print_debug("USE_PARAMETER_STORE=false, using environment")
        token = None
    
    # Fallback to environment variables
    if not token:
        _print_debug("Falling back to environment variables for token")
        token = os.environ.get('HOME_ASSISTANT_TOKEN') or os.environ.get('LONG_LIVED_ACCESS_TOKEN')
    
    # Build config
    config = {
        'api_endpoint': f"{os.environ.get('HOME_ASSISTANT_URL', 'http://homeassistant.local:8123')}/api/alexa/smart_home",
        'fallback_token': token,
        'verify_ssl': os.environ.get('HOME_ASSISTANT_VERIFY_SSL', 'true').lower() == 'true'
    }
    
    _elapsed = (time.perf_counter() - _start) * 1000
    _print_timing(f"===== LOAD_FAILSAFE_CONFIG COMPLETE: {_elapsed:.2f}ms =====")
    _print_debug(f"Config loaded: url={config['api_endpoint']}, has_token={bool(token)}")
    
    return config


# ===== TOKEN EXTRACTION =====

def _extract_bearer_token(event: Dict[str, Any], fallback_token: Optional[str]) -> str:
    """
    Extract Bearer token from Alexa event or use fallback.
    
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
    
    _logger.info('⚠️ FAILSAFE MODE ACTIVATED - Bypassing Lambda Execution Engine')
    _print_debug("Failsafe mode handler invoked")
    
    try:
        # Load configuration
        config = _load_failsafe_config()
        
        # Forward to Home Assistant
        response = _forward_to_home_assistant(event, config)
        
        _total_time = (time.perf_counter() - _start) * 1000
        _print_timing(f"===== FAILSAFE HANDLER COMPLETE: {_total_time:.2f}ms =====")
        
        _logger.info(f'✔️ Failsafe request successful ({_total_time:.0f}ms)')
        
        return response
        
    except Exception as e:
        _error_time = (time.perf_counter() - _start) * 1000
        _print_timing(f"===== FAILSAFE HANDLER FAILED: {_error_time:.2f}ms =====")
        _print_debug(f"Failsafe handler exception: {e}")
        
        _logger.error(f'❌ Failsafe request failed: {e}')
        
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


# Alias for backwards compatibility
handler = lambda_handler

# EOF
