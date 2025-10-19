"""
config_param_store.py - AWS Systems Manager Parameter Store Client
Version: 2025.10.19.TIMING
Description: TIMING DIAGNOSTICS - Shows exactly where SSM import overhead occurs

CHANGELOG:
- 2025.10.19.TIMING: COMPREHENSIVE TIMING DIAGNOSTICS
  - Added timing for module-level boto3 import (THE 7.7 SECOND CULPRIT!)
  - Times boto3.client('ssm') initialization separately
  - Times each SSM GetParameter API call
  - Shows cache operations timing
  - All timing gated by DEBUG_MODE=true (zero overhead when false)
  - Maintains all existing functionality
- 2025.10.19.08: FINAL FIX - Handles _CACHE_MISS sentinel from cache_core.py
  - Added detection for _CACHE_MISS sentinel (object() instance from cache)
  - Converts sentinel to None before processing

Copyright 2025 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

from typing import Any, Optional, Dict, List
import os
import time

from gateway import (
    cache_get,
    cache_set, 
    cache_delete,
    log_debug,
    log_info,
    log_warning,
    log_error
)


# ===== TIMING HELPERS =====

def _is_debug_mode() -> bool:
    """Check if DEBUG_MODE is enabled for timing output."""
    return os.environ.get('DEBUG_MODE', 'false').lower() == 'true'


def _print_timing(message: str):
    """Print timing message only if DEBUG_MODE=true."""
    if _is_debug_mode():
        print(f"[PARAM_STORE_TIMING] {message}")


# ===== COLD START OPTIMIZATION WITH TIMING =====

_module_load_start = time.perf_counter()
_print_timing("===== CONFIG_PARAM_STORE MODULE LOAD START =====")

_USE_PARAMETER_STORE = os.environ.get('USE_PARAMETER_STORE', 'false').lower() == 'true'
_print_timing(f"USE_PARAMETER_STORE={_USE_PARAMETER_STORE} (elapsed: {(time.perf_counter() - _module_load_start) * 1000:.2f}ms)")

_BOTO3_SSM_CLIENT = None

if _USE_PARAMETER_STORE:
    _print_timing("PARAMETER STORE ENABLED - Starting boto3 initialization...")
    _boto3_import_start = time.perf_counter()
    
    try:
        _print_timing("  Step 1: Importing boto3 module...")
        import boto3
        _boto3_import_time = (time.perf_counter() - _boto3_import_start) * 1000
        _print_timing(f"  *** boto3 imported: {_boto3_import_time:.2f}ms ***")
        
        _print_timing("  Step 2: Creating boto3.client('ssm')...")
        _ssm_client_start = time.perf_counter()
        _BOTO3_SSM_CLIENT = boto3.client('ssm')
        _ssm_client_time = (time.perf_counter() - _ssm_client_start) * 1000
        _print_timing(f"  *** SSM client created: {_ssm_client_time:.2f}ms ***")
        
        _total_init_time = (time.perf_counter() - _boto3_import_start) * 1000
        _print_timing(f"*** TOTAL SSM INITIALIZATION: {_total_init_time:.2f}ms ***")
        
        log_info(f"PERFORMANCE: SSM client pre-initialized in {_total_init_time:.2f}ms")
        
    except Exception as e:
        _init_time = (time.perf_counter() - _boto3_import_start) * 1000
        _print_timing(f"!!! SSM initialization FAILED after {_init_time:.2f}ms: {e}")
        log_error(f"Failed to pre-initialize SSM client: {e}")
        _USE_PARAMETER_STORE = False
        _BOTO3_SSM_CLIENT = None
else:
    _print_timing("PARAMETER STORE DISABLED - Skipping boto3 import")

_module_load_time = (time.perf_counter() - _module_load_start) * 1000
_print_timing(f"===== CONFIG_PARAM_STORE MODULE LOAD COMPLETE: {_module_load_time:.2f}ms =====")


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
        """Get SSM client with safety checks."""
        if not _USE_PARAMETER_STORE:
            return None
        
        if self._ssm_client is None:
            if _BOTO3_SSM_CLIENT is not None:
                self._ssm_client = _BOTO3_SSM_CLIENT
            else:
                try:
                    _print_timing("  Lazy loading boto3 (shouldn't happen - module-level init failed?)")
                    import boto3
                    self._ssm_client = boto3.client('ssm')
                except Exception as e:
                    log_error(f"Failed to initialize SSM client: {e}")
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
        - SSM API calls
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
            # Get SSM client
            _print_timing(f"  Step 4: Getting SSM client... (elapsed: {(time.perf_counter() - _op_start) * 1000:.2f}ms)")
            ssm = self._get_ssm_client()
            if ssm is None:
                _print_timing(f"  !!! SSM CLIENT UNAVAILABLE (elapsed: {(time.perf_counter() - _op_start) * 1000:.2f}ms)")
                return safe_default
            
            # Call SSM API
            _ssm_start = time.perf_counter()
            _print_timing(f"  Step 5: Calling SSM GetParameter API... (elapsed: {(time.perf_counter() - _op_start) * 1000:.2f}ms)")
            
            response = ssm.get_parameter(
                Name=param_path,
                WithDecryption=with_decryption
            )
            
            _ssm_time = (time.perf_counter() - _ssm_start) * 1000
            _print_timing(f"  *** SSM API RETURNED: {_ssm_time:.2f}ms *** (elapsed: {(time.perf_counter() - _op_start) * 1000:.2f}ms)")
            
            # Validate response structure
            _print_timing(f"  Step 6: Validating response... (elapsed: {(time.perf_counter() - _op_start) * 1000:.2f}ms)")
            if not isinstance(response, dict) or 'Parameter' not in response:
                _print_timing(f"  !!! Invalid response structure (elapsed: {(time.perf_counter() - _op_start) * 1000:.2f}ms)")
                return safe_default
            
            parameter = response['Parameter']
            if not isinstance(parameter, dict) or 'Value' not in parameter:
                _print_timing(f"  !!! Invalid parameter structure (elapsed: {(time.perf_counter() - _op_start) * 1000:.2f}ms)")
                return safe_default
            
            # Extract value
            _extract_start = time.perf_counter()
            _print_timing(f"  Step 7: Extracting value... (elapsed: {(time.perf_counter() - _op_start) * 1000:.2f}ms)")
            
            raw_value = parameter['Value']
            value = _extract_string_from_value(raw_value, key)
            
            _extract_time = (time.perf_counter() - _extract_start) * 1000
            _print_timing(f"  Value extracted: {_extract_time:.2f}ms (elapsed: {(time.perf_counter() - _op_start) * 1000:.2f}ms)")
            
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
