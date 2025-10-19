"""
config_param_store.py - AWS Systems Manager Parameter Store Client
Version: 2025.10.19.07
Description: NUCLEAR FIX - Impossible to return object() instances

CHANGELOG:
- 2025.10.19.07: CRITICAL FIX - NUCLEAR option to prevent object() returns
  - Added _sanitize_default() to NEVER allow object() as default
  - Added _sanitize_return() to validate EVERY return value
  - These safety checks make it IMPOSSIBLE to return object()
  - If SSM is disabled or fails, returns empty string or actual default
  - Maximum paranoia mode activated

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
else:
    log_debug("Parameter Store disabled")


# ===== NUCLEAR SAFETY FUNCTIONS =====

def _sanitize_default(default: Any, key: str) -> Any:
    """
    NUCLEAR SAFETY: Ensure default is NEVER an object() instance.
    
    This is the safety net that prevents the bug.
    """
    if default is None:
        return None
    
    # Check if it's an object() instance
    if type(default).__name__ == 'object':
        log_error(f"[SANITIZE] {key}: CRITICAL - default is object() instance, converting to empty string!")
        return ''
    
    # Check if string representation contains object reference  
    default_str = str(default)
    if '<object object' in default_str:
        log_error(f"[SANITIZE] {key}: CRITICAL - default contains object reference: {default_str}")
        return ''
    
    # Validate it's a primitive type
    if not isinstance(default, (str, int, float, bool, list, dict, tuple, set, type(None))):
        log_error(f"[SANITIZE] {key}: CRITICAL - default is non-primitive type {type(default).__name__}, converting to empty string!")
        return ''
    
    return default


def _sanitize_return(value: Any, key: str) -> Any:
    """
    NUCLEAR SAFETY: Validate return value is NEVER an object() instance.
    
    This is the final safety check before returning to caller.
    """
    if value is None:
        return None
    
    # Check if it's an object() instance
    if type(value).__name__ == 'object':
        log_error(f"[SANITIZE RETURN] {key}: CRITICAL - Detected object() instance being returned!")
        return None
    
    # Check if string representation contains object reference
    value_str = str(value)
    if '<object object' in value_str:
        log_error(f"[SANITIZE RETURN] {key}: CRITICAL - Return value contains object reference: {value_str}")
        return None
    
    # Validate it's a valid type
    if not isinstance(value, (str, int, float, bool, list, dict, tuple, set, type(None))):
        log_error(f"[SANITIZE RETURN] {key}: CRITICAL - Return value is invalid type {type(value).__name__}!")
        return None
    
    return value


def _extract_string_from_value(value: Any, key: str) -> Optional[str]:
    """BULLETPROOF string extraction from any value type."""
    if value is None:
        return None
    
    # Check for object reference
    value_str = str(value)
    if '<object object' in value_str:
        log_error(f"[EXTRACT] {key}: DETECTED OBJECT REFERENCE! type={type(value)}")
        return None
    
    # Handle string
    if isinstance(value, str):
        if not value or value.isspace():
            return None
        log_debug(f"[EXTRACT] {key}: Valid string (length={len(value)})")
        return value
    
    # Handle boolean
    if isinstance(value, bool):
        return str(value).lower()
    
    # Handle numbers
    if isinstance(value, (int, float)):
        return str(value)
    
    # Unexpected type
    log_warning(f"[EXTRACT] {key}: Unexpected type {type(value).__name__}")
    try:
        result = str(value)
        if '<object object' in result or not result or result.isspace():
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
        log_debug(f"ParameterStoreClient initialized with prefix: {self._prefix}")
    
    def _get_ssm_client(self):
        """Get SSM client with safety checks."""
        if not _USE_PARAMETER_STORE:
            log_warning("SSM client requested but USE_PARAMETER_STORE=false")
            return None
        
        if self._ssm_client is None:
            if _BOTO3_SSM_CLIENT is not None:
                self._ssm_client = _BOTO3_SSM_CLIENT
                log_debug("Using pre-initialized SSM client")
            else:
                try:
                    import boto3
                    self._ssm_client = boto3.client('ssm')
                    log_debug("SSM client created via lazy loading")
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
        Get parameter from SSM with NUCLEAR SAFETY against object() returns.
        
        This version is IMPOSSIBLE to return object() instances.
        """
        log_info(f"[SSM GET] {key}: Starting (USE_PARAMETER_STORE={_USE_PARAMETER_STORE})")
        
        # NUCLEAR SAFETY: Sanitize default immediately
        safe_default = _sanitize_default(default, key)
        log_debug(f"[SSM GET] {key}: Sanitized default type={type(safe_default).__name__}")
        
        # Check if SSM is even enabled
        if not _USE_PARAMETER_STORE:
            log_debug(f"[SSM GET] {key}: SSM disabled, returning sanitized default")
            return _sanitize_return(safe_default, key)
        
        # Check cache
        cache_key = f"{self._cache_prefix}{key}"
        if use_cache:
            cached = cache_get(cache_key)
            if cached is not None:
                sanitized_cached = _sanitize_return(cached, key)
                if sanitized_cached is not None:
                    log_debug(f"[SSM GET] {key}: Cache hit")
                    return sanitized_cached
                else:
                    log_warning(f"[SSM GET] {key}: Cached value failed sanitization, clearing cache")
                    cache_delete(cache_key)
        
        # Build path
        param_path = self._build_param_path(key)
        
        try:
            # Get SSM client
            ssm = self._get_ssm_client()
            if ssm is None:
                log_error(f"[SSM GET] {key}: SSM client is None, returning safe default")
                return _sanitize_return(safe_default, key)
            
            log_debug(f"[SSM GET] {key}: Calling ssm.get_parameter('{param_path}')")
            
            # Call SSM API
            response = ssm.get_parameter(
                Name=param_path,
                WithDecryption=with_decryption
            )
            
            log_debug(f"[SSM GET] {key}: Response received")
            
            # Validate response structure
            if not isinstance(response, dict):
                log_error(f"[SSM GET] {key}: Response not dict")
                return _sanitize_return(safe_default, key)
            
            if 'Parameter' not in response:
                log_error(f"[SSM GET] {key}: Response missing 'Parameter' key")
                return _sanitize_return(safe_default, key)
            
            parameter = response['Parameter']
            
            if not isinstance(parameter, dict):
                log_error(f"[SSM GET] {key}: Parameter not dict")
                return _sanitize_return(safe_default, key)
            
            if 'Value' not in parameter:
                log_error(f"[SSM GET] {key}: Parameter missing 'Value' key")
                return _sanitize_return(safe_default, key)
            
            # Extract raw value
            raw_value = parameter['Value']
            log_info(f"[SSM GET] {key}: Raw value type={type(raw_value).__name__}")
            
            # Extract string
            value = _extract_string_from_value(raw_value, key)
            
            if value is None:
                log_error(f"[SSM GET] {key}: String extraction failed, returning safe default")
                return _sanitize_return(safe_default, key)
            
            # Final validation
            if not isinstance(value, str):
                log_error(f"[SSM GET] {key}: Final value not string!")
                return _sanitize_return(safe_default, key)
            
            if '<object object' in value:
                log_error(f"[SSM GET] {key}: String contains object reference!")
                return _sanitize_return(safe_default, key)
            
            log_info(f"[SSM GET] {key}: SUCCESS - Valid string (length={len(value)})")
            
            # Cache result
            if use_cache:
                cache_set(cache_key, value, ttl=self._cache_ttl)
            
            # NUCLEAR SAFETY: Sanitize before return
            return _sanitize_return(value, key)
            
        except Exception as e:
            log_error(f"[SSM GET] {key}: EXCEPTION - {type(e).__name__}: {e}")
            
            import traceback
            log_error(f"[SSM GET] {key}: Traceback:\n{traceback.format_exc()}")
            
            # Clear cache on error
            if use_cache:
                cache_delete(cache_key)
            
            # NUCLEAR SAFETY: Return sanitized default
            return _sanitize_return(safe_default, key)
    
    def get_parameters(self, keys: List[str], default: Any = None,
                       with_decryption: bool = True) -> Dict[str, Any]:
        """Batch get multiple parameters."""
        results = {}
        for key in keys:
            results[key] = self.get_parameter(key, default, with_decryption)
        return results
    
    def invalidate_cache(self, key: Optional[str] = None):
        """Invalidate cached parameter(s)."""
        if key:
            cache_key = f"{self._cache_prefix}{key}"
            cache_delete(cache_key)


# ===== MODULE-LEVEL SINGLETON =====

_param_store_client = ParameterStoreClient()


# ===== CONVENIENCE FUNCTIONS =====

def get_parameter(key: str, default: Any = None, with_decryption: bool = True, 
                  use_cache: bool = True) -> Any:
    """
    Get parameter from SSM (convenience wrapper with NUCLEAR SAFETY).
    
    This function is IMPOSSIBLE to return object() instances.
    """
    return _param_store_client.get_parameter(key, default, with_decryption, use_cache)


def get_parameters(keys: List[str], default: Any = None, 
                   with_decryption: bool = True) -> Dict[str, Any]:
    """Batch get parameters from SSM."""
    return _param_store_client.get_parameters(keys, default, with_decryption)


def invalidate_cache(key: Optional[str] = None):
    """Invalidate SSM parameter cache."""
    _param_store_client.invalidate_cache(key)


log_debug("config_param_store.py module loaded with NUCLEAR SAFETY")
log_debug(f"Parameter Store enabled: {_USE_PARAMETER_STORE}")


__all__ = [
    'ParameterStoreClient',
    'get_parameter',
    'get_parameters', 
    'invalidate_cache'
]

# EOF
