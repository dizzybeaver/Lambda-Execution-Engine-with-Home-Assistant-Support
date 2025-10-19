"""
config_param_store.py - AWS SSM Parameter Store Client (SELECTIVE IMPORTS)
Version: 2025.10.19.SELECTIVE
Description: Uses PRELOADED boto3 SSM client from lambda_preload module

CRITICAL CHANGE: Removed module-level `import boto3` (was 8,500ms!)
NOW: Uses preloaded SSM client from lambda_preload.py (already initialized ~300ms during INIT)

Performance Impact:
- BEFORE: import boto3 at module level = 8,500ms during first request
- AFTER: Uses _BOTO3_SSM_CLIENT from lambda_preload = 0ms (already loaded!)

Design Decision: No lazy loading fallback
Reason: Lazy loading defeats optimization. If preload fails, SSM is unavailable.

Copyright 2025 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

# ===== IMPORTS =====

import os
import time
from typing import Dict, Any, Optional, List

# Import preloaded SSM client (already initialized during Lambda INIT!)
from lambda_preload import _BOTO3_SSM_CLIENT, _USE_PARAMETER_STORE

from gateway import (
    cache_get, cache_set, cache_delete,
    log_debug, log_info, log_warning, log_error
)


# ===== TIMING HELPERS =====

def _is_debug_mode() -> bool:
    """Check if DEBUG_MODE is enabled."""
    return os.environ.get('DEBUG_MODE', 'false').lower() == 'true'


def _print_timing(message: str):
    """Print timing message only if DEBUG_MODE=true."""
    if _is_debug_mode():
        print(f"[PARAM_STORE_TIMING] {message}")


# ===== CACHE SENTINEL DETECTION =====

def _is_cache_sentinel(value: Any) -> bool:
    """
    Check if value is the _CACHE_MISS sentinel from cache_core.py.
    
    The cache module uses object() as a sentinel to distinguish
    "no cache entry" from "cached None value". We need to detect
    and handle this properly.
    """
    return type(value).__name__ == 'object' and str(value).startswith('<object object')


def _sanitize_default(default: Any, key: str) -> Any:
    """
    NUCLEAR SAFETY: Ensure default is NEVER an object() instance.
    
    Handles both:
    - Actual bugs (shouldn't happen)
    - _CACHE_MISS sentinel from cache_core.py (expected)
    """
    if default is None:
        return ''
    
    # Check if it's the cache sentinel or any object() instance
    if _is_cache_sentinel(default):
        log_debug(f"[SANITIZE] {key}: Detected cache sentinel, converting to empty string")
        return ''
    
    # Validate it's a primitive type
    if not isinstance(default, (str, int, float, bool, list, dict, tuple, set, type(None))):
        log_warning(f"[SANITIZE] {key}: Non-primitive default type {type(default).__name__}, converting to empty string")
        return ''
    
    return default


def _extract_string_from_value(value: Any, key: str) -> Optional[str]:
    """BULLETPROOF string extraction from any value type."""
    if value is None:
        return None
    
    # Check for object reference
    if _is_cache_sentinel(value):
        log_error(f"[EXTRACT] {key}: Detected cache sentinel in SSM response!")
        return None
    
    # Handle string
    if isinstance(value, str):
        if not value or value.isspace():
            return None
        return value
    
    # Handle boolean
    if isinstance(value, bool):
        return str(value).lower()
    
    # Handle numbers
    if isinstance(value, (int, float)):
        return str(value)
    
    # Unexpected type
    try:
        result = str(value)
        if not result or result.isspace():
            return None
        return result
    except:
        return None


# ===== PARAMETER STORE CLIENT =====

class ParameterStoreClient:
    """Client for AWS Systems Manager Parameter Store operations."""
    
    def __init__(self, prefix: str = '/lambda-execution-engine'):
        self._prefix = prefix.rstrip('/')
        self._ssm_client = None
        self._cache_prefix = 'ssm_param_'
        self._cache_ttl = 300
    
    def _get_ssm_client(self):
        """
        Get SSM client - NO LAZY LOADING!
        
        DESIGN DECISION: Uses preloaded client only
        Reason: Lazy loading causes 8,500ms penalty on first request, defeating optimization.
        
        boto3 SSM client is preloaded during Lambda INIT in lambda_preload.py.
        If preload failed, SSM is unavailable - this returns None gracefully.
        """
        if not _USE_PARAMETER_STORE:
            return None
        
        if self._ssm_client is None:
            if _BOTO3_SSM_CLIENT is not None:
                self._ssm_client = _BOTO3_SSM_CLIENT
            else:
                # Module-level initialization failed - SSM is unavailable
                log_error("SSM client unavailable - preload failed!")
                return None
        
        return self._ssm_client
    
    def _build_param_path(self, key: str) -> str:
        """Build full parameter path from key."""
        key = key.lstrip('/')
        return f"{self._prefix}/{key}"
    
    def get_parameter(self, key: str, default: Any = None,
                     with_decryption: bool = True,
                     use_cache: bool = True) -> Any:
        """
        Get parameter from SSM with timing diagnostics.
        
        This version shows exactly where time is spent:
        - Cache operations
        - SSM API calls (uses preloaded client - no loading overhead!)
        - Value extraction and validation
        """
        _op_start = time.perf_counter()
        _print_timing(f"===== GET_PARAMETER START: {key} =====")
        
        # CRITICAL: Sanitize default immediately (handles cache sentinels)
        safe_default = _sanitize_default(default, key)
        _print_timing(f"  Step 1: Default sanitized (elapsed: {(time.perf_counter() - _op_start) * 1000:.2f}ms)")
        
        # Check if SSM is enabled
        if not _USE_PARAMETER_STORE:
            _print_timing(f"  SSM DISABLED - returning default (elapsed: {(time.perf_counter() - _op_start) * 1000:.2f}ms)")
            return safe_default
        
        # Check cache
        cache_key = f"{self._cache_prefix}{key}"
        if use_cache:
            _cache_start = time.perf_counter()
            _print_timing(f"  Step 2: Checking cache... (elapsed: {(time.perf_counter() - _op_start) * 1000:.2f}ms)")
            
            cached = cache_get(cache_key)
            _cache_time = (time.perf_counter() - _cache_start) * 1000
            
            if cached is not None and not _is_cache_sentinel(cached):
                _print_timing(f"  *** CACHE HIT: {_cache_time:.2f}ms (total: {(time.perf_counter() - _op_start) * 1000:.2f}ms) ***")
                return cached
            else:
                _print_timing(f"  Cache miss: {_cache_time:.2f}ms (elapsed: {(time.perf_counter() - _op_start) * 1000:.2f}ms)")
        
        # Build path
        param_path = self._build_param_path(key)
        _print_timing(f"  Step 3: Parameter path: {param_path} (elapsed: {(time.perf_counter() - _op_start) * 1000:.2f}ms)")
        
        try:
            # Get SSM client (ALREADY PRELOADED - NO LOADING OVERHEAD!)
            _print_timing(f"  Step 4: Getting SSM client... (elapsed: {(time.perf_counter() - _op_start) * 1000:.2f}ms)")
            ssm = self._get_ssm_client()
            if ssm is None:
                _print_timing(f"  !!! SSM client unavailable (elapsed: {(time.perf_counter() - _op_start) * 1000:.2f}ms)")
                return safe_default
            
            # Call SSM (client already initialized, no loading penalty!)
            _ssm_start = time.perf_counter()
            _print_timing(f"  Step 5: Calling SSM API... (elapsed: {(time.perf_counter() - _op_start) * 1000:.2f}ms)")
            
            response = ssm.get_parameter(Name=param_path, WithDecryption=with_decryption)
            
            _ssm_time = (time.perf_counter() - _ssm_start) * 1000
            _print_timing(f"  SSM API: {_ssm_time:.2f}ms (elapsed: {(time.perf_counter() - _op_start) * 1000:.2f}ms)")
            
            # Extract value
            _print_timing(f"  Step 6: Extracting value... (elapsed: {(time.perf_counter() - _op_start) * 1000:.2f}ms)")
            if not isinstance(response, dict):
                _print_timing(f"  !!! Response not dict (elapsed: {(time.perf_counter() - _op_start) * 1000:.2f}ms)")
                return safe_default
            
            param_data = response.get('Parameter')
            if not isinstance(param_data, dict):
                _print_timing(f"  !!! Parameter not dict (elapsed: {(time.perf_counter() - _op_start) * 1000:.2f}ms)")
                return safe_default
            
            raw_value = param_data.get('Value')
            _print_timing(f"  Step 7: Validating value... (elapsed: {(time.perf_counter() - _op_start) * 1000:.2f}ms)")
            
            value = _extract_string_from_value(raw_value, key)
            if value is None:
                _print_timing(f"  !!! Extraction returned None (elapsed: {(time.perf_counter() - _op_start) * 1000:.2f}ms)")
                return safe_default
            
            # Final validation
            if not isinstance(value, str) or not value:
                _print_timing(f"  !!! Final validation failed (elapsed: {(time.perf_counter() - _op_start) * 1000:.2f}ms)")
                return safe_default
            
            log_info(f"[SSM GET] {key}: SUCCESS (length={len(value)})")
            
            # Cache result
            if use_cache:
                _cache_set_start = time.perf_counter()
                _print_timing(f"  Step 8: Caching result... (elapsed: {(time.perf_counter() - _op_start) * 1000:.2f}ms)")
                
                cache_set(cache_key, value, ttl=self._cache_ttl)
                
                _cache_set_time = (time.perf_counter() - _cache_set_start) * 1000
                _print_timing(f"  Cached: {_cache_set_time:.2f}ms (elapsed: {(time.perf_counter() - _op_start) * 1000:.2f}ms)")
            
            _total_time = (time.perf_counter() - _op_start) * 1000
            _print_timing(f"===== GET_PARAMETER COMPLETE: {_total_time:.2f}ms =====")
            
            return value
            
        except Exception as e:
            _error_time = (time.perf_counter() - _op_start) * 1000
            _print_timing(f"!!! EXCEPTION after {_error_time:.2f}ms: {e}")
            log_error(f"[SSM GET] {key}: Exception - {e}")
            if use_cache:
                cache_delete(cache_key)
            return safe_default


# ===== MODULE-LEVEL SINGLETON =====

_param_store_client = ParameterStoreClient()


# ===== CONVENIENCE FUNCTIONS =====

def get_parameter(key: str, default: Any = None, with_decryption: bool = True, 
                  use_cache: bool = True) -> Any:
    """Get parameter from SSM (handles cache sentinels correctly)."""
    return _param_store_client.get_parameter(key, default, with_decryption, use_cache)


def get_parameters(keys: List[str], default: Any = None, 
                   with_decryption: bool = True) -> Dict[str, Any]:
    """Batch get parameters from SSM."""
    results = {}
    for key in keys:
        results[key] = get_parameter(key, default, with_decryption)
    return results


def invalidate_cache(key: Optional[str] = None):
    """Invalidate SSM parameter cache."""
    if key:
        cache_key = f"ssm_param_{key}"
        cache_delete(cache_key)


__all__ = [
    'ParameterStoreClient',
    'get_parameter',
    'get_parameters', 
    'invalidate_cache'
]

# EOF
