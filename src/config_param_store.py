"""
config_param_store.py - AWS Systems Manager Parameter Store Client (SIMPLIFIED)
Version: 2025.10.20.TOKEN_ONLY
Description: Retrieve ONLY the Home Assistant long-lived token from SSM

BREAKING CHANGE:
- SSM now retrieves ONLY /home_assistant/token
- ALL other configuration must be in Lambda environment variables
- Simplifies architecture, reduces SSM calls, improves performance

CHANGELOG:
- 2025.10.20.TOKEN_ONLY: SIMPLIFIED - Only token from SSM
  - Removed support for all other parameters
  - Single-purpose: retrieve HA token securely
  - Everything else must be environment variables
  - Reduces cold start overhead
  - Eliminates unnecessary SSM API calls

Copyright 2025 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

import os
import time
from typing import Any, Optional

# Lazy-loaded boto3 (only when SSM needed)
_SSM_CLIENT = None

# Gateway imports
from gateway import cache_get, cache_set, cache_delete, log_info, log_error


def _is_debug_mode() -> bool:
    """Check if DEBUG_MODE is enabled."""
    return os.getenv('DEBUG_MODE', 'false').lower() == 'true'


def _is_debug_timings() -> bool:
    """Check if DEBUG_TIMINGS is enabled."""
    return os.getenv('DEBUG_TIMINGS', 'false').lower() == 'true'


def _print_debug(msg: str):
    """Print debug message only if DEBUG_MODE=true."""
    if _is_debug_mode():
        print(f"[SSM_DEBUG] {msg}")


def _print_timing(msg: str):
    """Print timing message only if DEBUG_TIMINGS=true."""
    if _is_debug_timings():
        print(f"[SSM_TIMING] {msg}")


# ===== CONFIGURATION =====

_USE_PARAMETER_STORE = os.getenv('USE_PARAMETER_STORE', 'false').lower() == 'true'
_PARAMETER_PREFIX = os.getenv('PARAMETER_PREFIX', '/lambda-execution-engine')
_CACHE_TTL = int(os.getenv('SSM_CACHE_TTL', '300'))  # 5 minutes default


# ===== SSM CLIENT SINGLETON =====

def _get_ssm_client():
    """Get or create SSM client (lazy loaded)."""
    global _SSM_CLIENT
    
    if _SSM_CLIENT is not None:
        return _SSM_CLIENT
    
    _print_debug("Initializing SSM client...")
    _init_start = time.perf_counter()
    
    try:
        import boto3
        _SSM_CLIENT = boto3.client('ssm')
        
        _init_time = (time.perf_counter() - _init_start) * 1000
        _print_timing(f"SSM client initialized: {_init_time:.2f}ms")
        _print_debug("SSM client ready")
        
        return _SSM_CLIENT
        
    except Exception as e:
        _print_debug(f"SSM client initialization failed: {e}")
        log_error(f"Failed to initialize SSM client: {e}")
        return None


# ===== TOKEN RETRIEVAL =====

def get_ha_token(use_cache: bool = True) -> Optional[str]:
    """
    Get Home Assistant long-lived access token from SSM.
    
    This is the ONLY parameter retrieved from SSM.
    All other configuration must be in environment variables.
    
    Args:
        use_cache: Whether to use cached value (default: True)
        
    Returns:
        Token string if found, None otherwise
    """
    _op_start = time.perf_counter()
    _print_timing("===== GET_HA_TOKEN START =====")
    _print_debug("Retrieving Home Assistant token from SSM")
    
    # Check if SSM is enabled
    if not _USE_PARAMETER_STORE:
        _print_debug("SSM disabled (USE_PARAMETER_STORE=false)")
        _print_timing(f"SSM disabled - no token retrieval (elapsed: {(time.perf_counter() - _op_start) * 1000:.2f}ms)")
        return None
    
    # Check cache first
    cache_key = "ssm_ha_token"
    if use_cache:
        _cache_start = time.perf_counter()
        _print_timing(f"Checking cache... (elapsed: {(time.perf_counter() - _op_start) * 1000:.2f}ms)")
        _print_debug("Attempting cache retrieval")
        
        cached = cache_get(cache_key)
        _cache_time = (time.perf_counter() - _cache_start) * 1000
        
        # Check if cached value is valid (not a sentinel)
        if cached is not None:
            # Check for _CacheMiss sentinel
            cached_type = type(cached).__name__
            if cached_type == '_CacheMiss':
                _print_timing(f"Cache returned _CacheMiss sentinel: {_cache_time:.2f}ms")
                _print_debug("Cache miss - will fetch from SSM")
            elif isinstance(cached, str) and cached:
                _print_timing(f"*** CACHE HIT: {_cache_time:.2f}ms (total: {(time.perf_counter() - _op_start) * 1000:.2f}ms) ***")
                _print_debug("Token retrieved from cache")
                return cached
            else:
                _print_timing(f"Cache returned invalid value (type={cached_type}): {_cache_time:.2f}ms")
                _print_debug(f"Invalid cached value: {cached_type}")
        else:
            _print_timing(f"Cache miss (None): {_cache_time:.2f}ms (elapsed: {(time.perf_counter() - _op_start) * 1000:.2f}ms)")
            _print_debug("Cache returned None")
    
    # Build parameter path
    param_path = f"{_PARAMETER_PREFIX}/home_assistant/token"
    _print_debug(f"Parameter path: {param_path}")
    _print_timing(f"Parameter path: {param_path} (elapsed: {(time.perf_counter() - _op_start) * 1000:.2f}ms)")
    
    try:
        # Get SSM client
        _print_timing(f"Getting SSM client... (elapsed: {(time.perf_counter() - _op_start) * 1000:.2f}ms)")
        ssm = _get_ssm_client()
        if ssm is None:
            _print_timing(f"!!! SSM client unavailable (elapsed: {(time.perf_counter() - _op_start) * 1000:.2f}ms)")
            _print_debug("SSM client unavailable")
            return None
        
        # Call SSM API
        _ssm_start = time.perf_counter()
        _print_timing(f"Calling SSM API... (elapsed: {(time.perf_counter() - _op_start) * 1000:.2f}ms)")
        _print_debug("Calling SSM GetParameter API...")
        
        response = ssm.get_parameter(Name=param_path, WithDecryption=True)
        
        _ssm_time = (time.perf_counter() - _ssm_start) * 1000
        _print_timing(f"SSM API call: {_ssm_time:.2f}ms (elapsed: {(time.perf_counter() - _op_start) * 1000:.2f}ms)")
        _print_debug("SSM API call successful")
        
        # Extract value
        _print_timing(f"Extracting token... (elapsed: {(time.perf_counter() - _op_start) * 1000:.2f}ms)")
        
        if not isinstance(response, dict):
            _print_debug("Invalid response type from SSM")
            return None
        
        param_data = response.get('Parameter')
        if not isinstance(param_data, dict):
            _print_debug("Invalid parameter data from SSM")
            return None
        
        token = param_data.get('Value')
        
        # Validate token
        _print_timing(f"Validating token... (elapsed: {(time.perf_counter() - _op_start) * 1000:.2f}ms)")
        
        if not isinstance(token, str) or not token:
            _print_debug("Invalid or empty token")
            _print_timing(f"!!! Invalid token (elapsed: {(time.perf_counter() - _op_start) * 1000:.2f}ms)")
            return None
        
        log_info(f"[SSM GET] Token retrieved successfully (length={len(token)})")
        _print_debug(f"Token retrieved (length={len(token)})")
        
        # Cache the token
        if use_cache:
            _cache_set_start = time.perf_counter()
            _print_timing(f"Caching token... (elapsed: {(time.perf_counter() - _op_start) * 1000:.2f}ms)")
            
            cache_set(cache_key, token, ttl=_CACHE_TTL)
            
            _cache_set_time = (time.perf_counter() - _cache_set_start) * 1000
            _print_timing(f"Cached: {_cache_set_time:.2f}ms (elapsed: {(time.perf_counter() - _op_start) * 1000:.2f}ms)")
            _print_debug(f"Token cached (TTL={_CACHE_TTL}s)")
        
        _total_time = (time.perf_counter() - _op_start) * 1000
        _print_timing(f"===== GET_HA_TOKEN COMPLETE: {_total_time:.2f}ms =====")
        
        return token
        
    except Exception as e:
        _error_time = (time.perf_counter() - _op_start) * 1000
        _print_timing(f"!!! EXCEPTION after {_error_time:.2f}ms: {e}")
        _print_debug(f"Exception retrieving token: {e}")
        log_error(f"[SSM GET] Token retrieval failed: {e}")
        
        # Clear cache on error
        if use_cache:
            cache_delete(cache_key)
        
        return None


def invalidate_token_cache():
    """Invalidate cached Home Assistant token."""
    _print_debug("Invalidating token cache")
    cache_delete("ssm_ha_token")
    log_info("[SSM CACHE] Token cache invalidated")


# ===== PUBLIC API =====

__all__ = [
    'get_ha_token',
    'invalidate_token_cache'
]

# EOF
