"""
config_param_store.py - AWS Systems Manager Parameter Store Client
Version: 2025.10.18.11
Description: Dedicated SSM Parameter Store client with bulletproof value extraction

CHANGELOG:
- 2025.10.18.11: CRITICAL FIX - Prevent object() returns entirely
  - Changed default parameter from None to explicit check
  - Never return object() type under any circumstances
  - Added explicit boto3 response validation BEFORE extraction
  - Fixed Strategy 1 to handle ResponseMetadata properly
  - Return None (not object) on all failure paths
  - Fixes: Gateway returning <object object> instead of strings
- 2025.10.18.09: Enhanced string extraction with 5 strategies

Copyright 2025 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

from typing import Any, Optional, Dict, List
import os

# Import Gateway services
from gateway import (
    cache_get, cache_set, cache_delete,
    log_debug, log_warning, log_error
)


class ParameterStoreClient:
    """Client for AWS Systems Manager Parameter Store operations."""
    
    def __init__(self, prefix: str = '/lambda-execution-engine'):
        """
        Initialize Parameter Store client.
        
        Args:
            prefix: Base path prefix for all parameters
        """
        self._prefix = prefix.rstrip('/')
        self._ssm_client = None
        self._cache_prefix = 'ssm_param_'
        self._cache_ttl = 300  # 5 minutes default
    
    def _get_ssm_client(self):
        """Lazy load boto3 SSM client."""
        if self._ssm_client is None:
            try:
                import boto3
                self._ssm_client = boto3.client('ssm')
                log_debug("SSM client initialized")
            except Exception as e:
                log_error(f"Failed to initialize SSM client: {e}")
                raise
        return self._ssm_client
    
    def _build_param_path(self, key: str) -> str:
        """Build full parameter path from key."""
        # Remove leading slash from key if present
        key = key.lstrip('/')
        return f"{self._prefix}/{key}"
    
    def _force_string_extraction(self, response: Any, param_path: str) -> Optional[str]:
        """
        Aggressively extract string value from SSM response.
        
        CRITICAL: This function MUST return either a string or None.
        NEVER return object() or any other type.
        
        Args:
            response: SSM get_parameter response
            param_path: Parameter path for logging
            
        Returns:
            String value or None (NEVER object or other types)
        """
        # Validate response is not None
        if response is None:
            log_error(f"_force_string_extraction received None response for {param_path}")
            return None
        
        # Check if response is already object() type (shouldn't happen but be safe)
        if type(response).__name__ == 'object':
            log_error(f"_force_string_extraction received base object() for {param_path}")
            return None
        
        log_debug(f"Extracting value from SSM response type: {type(response)}")
        log_debug(f"Response repr: {repr(response)[:200]}")
        
        # Strategy 1: Standard dict access (most common for boto3)
        try:
            if isinstance(response, dict):
                # Check for ResponseMetadata (typical boto3 response)
                if 'ResponseMetadata' in response and 'Parameter' in response:
                    param = response['Parameter']
                    if isinstance(param, dict) and 'Value' in param:
                        value = param['Value']
                        if isinstance(value, str):
                            log_debug(f"Strategy 1 success: Standard boto3 dict extraction")
                            return value
                        else:
                            log_warning(f"Strategy 1: Value exists but not string: {type(value)}")
                elif 'Parameter' in response:
                    # Response without ResponseMetadata
                    param = response['Parameter']
                    if isinstance(param, dict) and 'Value' in param:
                        value = param['Value']
                        if isinstance(value, str):
                            log_debug(f"Strategy 1b success: Dict without ResponseMetadata")
                            return value
        except Exception as e:
            log_debug(f"Strategy 1 failed: {e}")
        
        # Strategy 2: Safe nested get
        try:
            if hasattr(response, 'get') and callable(response.get):
                param = response.get('Parameter')
                if param and isinstance(param, dict):
                    value = param.get('Value')
                    if value and isinstance(value, str):
                        log_debug(f"Strategy 2 success: Safe nested get")
                        return value
        except Exception as e:
            log_debug(f"Strategy 2 failed: {e}")
        
        # Strategy 3: Direct attribute access (boto3 object wrappers)
        try:
            if hasattr(response, 'Parameter'):
                param = response.Parameter
                if hasattr(param, 'Value'):
                    value = param.Value
                    if isinstance(value, str):
                        log_debug(f"Strategy 3 success: Direct attribute access")
                        return value
        except Exception as e:
            log_debug(f"Strategy 3 failed: {e}")
        
        # Strategy 4: dict() conversion of response
        try:
            response_dict = dict(response)
            if 'Parameter' in response_dict:
                param = response_dict['Parameter']
                if isinstance(param, dict) and 'Value' in param:
                    value = param['Value']
                    if isinstance(value, str):
                        log_debug(f"Strategy 4 success: dict() conversion")
                        return value
        except Exception as e:
            log_debug(f"Strategy 4 failed: {e}")
        
        # Strategy 5: String representation parsing (last resort, diagnostic only)
        try:
            response_str = str(response)
            if "'Value':" in response_str or '"Value":' in response_str:
                log_warning(f"Value detected in string representation but not extractable")
                log_warning(f"Response type: {type(response)}, Response: {response_str[:500]}")
        except Exception as e:
            log_debug(f"Strategy 5 failed: {e}")
        
        # ALL strategies failed - return None (not object!)
        log_error(f"All extraction strategies failed for {param_path}")
        log_error(f"Response type: {type(response)}")
        log_error(f"Response has __dict__: {hasattr(response, '__dict__')}")
        if hasattr(response, '__dict__'):
            log_error(f"Response __dict__ keys: {list(response.__dict__.keys())[:10]}")
        
        return None  # NEVER return object() or default parameter
    
    def get_parameter(self, key: str, default: Any = None,
                     with_decryption: bool = True,
                     use_cache: bool = True) -> Any:
        """
        Get parameter from SSM Parameter Store with bulletproof value extraction.
        
        CRITICAL: This function MUST return either a valid value or the default.
        It must NEVER return object() type.
        
        Args:
            key: Parameter key relative to prefix (e.g., 'homeassistant/url')
            default: Default value if parameter not found (default: None)
            with_decryption: Decrypt SecureString parameters (default: True)
            use_cache: Use cached value if available (default: True)
            
        Returns:
            Parameter value (string/primitive) or default value (NEVER object)
        """
        # Validate default is not object()
        if type(default).__name__ == 'object':
            log_error(f"get_parameter called with object() as default for {key}")
            default = None  # Override to None
        
        # Check cache first
        cache_key = f"{self._cache_prefix}{key}"
        if use_cache:
            cached = cache_get(cache_key)
            if cached is not None:
                # Validate cached value is not object()
                if type(cached).__name__ == 'object':
                    log_error(f"Cache contained object() for {key}, clearing")
                    cache_delete(cache_key)
                else:
                    log_debug(f"SSM cache hit: {key}")
                    return cached
        
        # Build parameter path
        param_path = self._build_param_path(key)
        
        try:
            # Get SSM client (lazy load)
            ssm = self._get_ssm_client()
            
            log_debug(f"Fetching SSM parameter: {param_path} (decrypt={with_decryption})")
            
            # Call SSM API
            response = ssm.get_parameter(
                Name=param_path,
                WithDecryption=with_decryption
            )
            
            # Validate we got a response
            if response is None:
                log_error(f"SSM get_parameter returned None for {param_path}")
                return default
            
            # Log response details
            log_debug(f"SSM response type: {type(response)}")
            log_debug(f"SSM response keys: {response.keys() if isinstance(response, dict) else 'N/A'}")
            
            # Extract string value using multiple strategies
            value = self._force_string_extraction(response, param_path)
            
            # Validate extraction result
            if value is None:
                log_warning(f"Could not extract value from SSM: {param_path}")
                log_warning("Returning default value")
                return default
            
            # Double-check value is not object()
            if type(value).__name__ == 'object':
                log_error(f"Extraction returned object() for {param_path} - BUG!")
                return default
            
            # Validate value is a usable primitive type
            if not isinstance(value, (str, int, float, bool)):
                log_warning(f"SSM value has unexpected type {type(value)} for {param_path}")
                # Try to convert to string
                try:
                    value = str(value)
                    log_debug(f"Converted value to string: {value[:50]}")
                except Exception as conv_err:
                    log_error(f"Failed to convert value to string: {conv_err}")
                    return default
            
            # Cache successful result (only if not object)
            if use_cache and type(value).__name__ != 'object':
                cache_set(cache_key, value, ttl=self._cache_ttl)
                log_debug(f"Cached SSM parameter: {key} (TTL={self._cache_ttl}s)")
            
            log_debug(f"Successfully loaded SSM parameter: {param_path}, type: {type(value)}")
            return value
        
        except Exception as e:
            log_warning(f"Failed to load SSM parameter {param_path}: {e}")
            log_warning(f"Error type: {type(e).__name__}")
            
            # Clear cache on error to allow retry next time
            if use_cache:
                cache_delete(cache_key)
                log_debug(f"Cleared cache for failed SSM parameter: {key}")
            
            return default
    
    def get_parameters(self, keys: List[str], default: Any = None,
                       with_decryption: bool = True) -> Dict[str, Any]:
        """
        Batch get multiple parameters.
        
        Args:
            keys: List of parameter keys relative to prefix
            default: Default value for missing parameters
            with_decryption: Decrypt SecureString parameters
            
        Returns:
            Dictionary mapping keys to values
        """
        results = {}
        for key in keys:
            results[key] = self.get_parameter(key, default, with_decryption)
        return results
    
    def invalidate_cache(self, key: Optional[str] = None):
        """
        Invalidate cached parameter(s).
        
        Args:
            key: Specific parameter key to invalidate, or None to clear all SSM cache
        """
        if key:
            cache_key = f"{self._cache_prefix}{key}"
            cache_delete(cache_key)
            log_debug(f"Invalidated SSM cache: {key}")
        else:
            log_debug("Attempted to clear all SSM parameter cache")
            log_warning("Cache clear-all not fully implemented - use specific key invalidation")
    
    def set_parameter(self, key: str, value: str, 
                     parameter_type: str = 'String',
                     overwrite: bool = True,
                     description: str = '',
                     tags: Optional[Dict[str, str]] = None) -> bool:
        """
        Set parameter in SSM Parameter Store.
        
        NOTE: This requires ssm:PutParameter IAM permission.
        
        Args:
            key: Parameter key relative to prefix
            value: Parameter value (will be converted to string)
            parameter_type: 'String', 'StringList', or 'SecureString'
            overwrite: Overwrite existing parameter if it exists
            description: Parameter description (optional)
            tags: Parameter tags (optional)
            
        Returns:
            True if successful, False otherwise
        """
        param_path = self._build_param_path(key)
        
        try:
            ssm = self._get_ssm_client()
            
            kwargs = {
                'Name': param_path,
                'Value': str(value),
                'Type': parameter_type,
                'Overwrite': overwrite
            }
            
            if description:
                kwargs['Description'] = description
            
            if tags:
                kwargs['Tags'] = [{'Key': k, 'Value': v} for k, v in tags.items()]
            
            log_debug(f"Setting SSM parameter: {param_path} (type={parameter_type})")
            
            response = ssm.put_parameter(**kwargs)
            
            # Invalidate cache since we just updated the parameter
            cache_key = f"{self._cache_prefix}{key}"
            cache_delete(cache_key)
            
            log_debug(f"Successfully set SSM parameter: {param_path} (version={response.get('Version')})")
            return True
        
        except Exception as e:
            log_error(f"Failed to set SSM parameter {param_path}: {e}")
            return False


# ===== SINGLETON INSTANCE =====

# Default instance with standard prefix
_param_store_client = ParameterStoreClient(
    prefix=os.environ.get('PARAMETER_PREFIX', '/lambda-execution-engine')
)


# ===== PUBLIC INTERFACE FUNCTIONS =====

def get_parameter(key: str, default: Any = None) -> Any:
    """
    Get parameter from SSM Parameter Store (convenience wrapper).
    
    CRITICAL: Returns actual value or default. NEVER returns object().
    
    Args:
        key: Parameter key relative to configured prefix
        default: Default value if parameter not found (default: None)
        
    Returns:
        Parameter value or default (NEVER object type)
    """
    # Validate default is not object()
    if type(default).__name__ == 'object':
        log_error(f"get_parameter called with object() default for {key}")
        default = None
    
    return _param_store_client.get_parameter(key, default)


def get_parameters(keys: List[str], default: Any = None) -> Dict[str, Any]:
    """
    Batch get parameters from SSM Parameter Store (convenience wrapper).
    
    Args:
        keys: List of parameter keys
        default: Default value for missing parameters
        
    Returns:
        Dictionary mapping keys to values
    """
    return _param_store_client.get_parameters(keys, default)


def invalidate_cache(key: Optional[str] = None):
    """
    Invalidate SSM parameter cache (convenience wrapper).
    
    Args:
        key: Specific key to invalidate, or None for all
    """
    _param_store_client.invalidate_cache(key)


def set_parameter(key: str, value: str, **kwargs) -> bool:
    """
    Set parameter in SSM Parameter Store (convenience wrapper).
    
    Args:
        key: Parameter key
        value: Parameter value
        **kwargs: Additional arguments for put_parameter
        
    Returns:
        True if successful
    """
    return _param_store_client.set_parameter(key, value, **kwargs)


__all__ = [
    'ParameterStoreClient',
    'get_parameter',
    'get_parameters', 
    'invalidate_cache',
    'set_parameter'
]

# EOF
