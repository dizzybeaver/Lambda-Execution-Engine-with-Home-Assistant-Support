"""
config_param_store.py - AWS Systems Manager Parameter Store Client
Version: 2025.10.19.08
Description: FINAL FIX - Handles cache sentinel values correctly

CHANGELOG:
- 2025.10.19.08: FINAL FIX - Handles _CACHE_MISS sentinel from cache_core.py
  - Added detection for _CACHE_MISS sentinel (object() instance from cache)
  - Converts sentinel to None before processing
  - Root cause: cache_core.py returns object() sentinel for cache misses
  - This sentinel was being passed as default parameter
  - Nuclear safety now specifically handles this case

Copyright 2025 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

from typing import Any, Optional, Dict, List
import os

from gateway import (
    cache_get,
    cache_set, 
    cache_delete,
    log_debug,
    log_info,
    log_warning,
    log_error
)


# ===== COLD START OPTIMIZATION =====

_USE_PARAMETER_STORE = os.environ.get('USE_PARAMETER_STORE', 'false').lower() == 'true'
_BOTO3_SSM_CLIENT = None

if _USE_PARAMETER_STORE:
    try:
        import boto3
        _BOTO3_SSM_CLIENT = boto3.client('ssm')
        log_info("PERFORMANCE: SSM client pre-initialized")
    except Exception as e:
        log_error(f"Failed to pre-initialize SSM client: {e}")
        _USE_PARAMETER_STORE = False
        _BOTO3_SSM_CLIENT = None


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
        Get parameter from SSM with proper sentinel handling.
        
        This version correctly handles _CACHE_MISS sentinel from cache_core.py.
        """
        # CRITICAL: Sanitize default immediately (handles cache sentinels)
        safe_default = _sanitize_default(default, key)
        
        # Check if SSM is enabled
        if not _USE_PARAMETER_STORE:
            return safe_default
        
        # Check cache
        cache_key = f"{self._cache_prefix}{key}"
        if use_cache:
            cached = cache_get(cache_key)
            if cached is not None and not _is_cache_sentinel(cached):
                return cached
        
        # Build path
        param_path = self._build_param_path(key)
        
        try:
            # Get SSM client
            ssm = self._get_ssm_client()
            if ssm is None:
                return safe_default
            
            # Call SSM API
            response = ssm.get_parameter(
                Name=param_path,
                WithDecryption=with_decryption
            )
            
            # Validate response structure
            if not isinstance(response, dict) or 'Parameter' not in response:
                return safe_default
            
            parameter = response['Parameter']
            if not isinstance(parameter, dict) or 'Value' not in parameter:
                return safe_default
            
            # Extract value
            raw_value = parameter['Value']
            value = _extract_string_from_value(raw_value, key)
            
            if value is None:
                return safe_default
            
            # Final validation
            if not isinstance(value, str) or not value:
                return safe_default
            
            log_info(f"[SSM GET] {key}: SUCCESS (length={len(value)})")
            
            # Cache result
            if use_cache:
                cache_set(cache_key, value, ttl=self._cache_ttl)
            
            return value
            
        except Exception as e:
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
