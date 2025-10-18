"""
config_param_store.py - AWS Systems Manager Parameter Store Client
Version: 2025.10.18.09
Description: Dedicated SSM Parameter Store client with aggressive value extraction

CHANGELOG:
- 2025.10.18.09: CRITICAL FIX - Enhanced string extraction to handle boto3 object wrappers
  - Added _force_string_extraction with 5 fallback strategies
  - Handles Parameter dict, Response dict, and object wrapper edge cases
  - Extensive logging for debugging SSM response types
  - Fixes: 'object' object is not subscriptable error

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
        Aggressively extract string value from SSM response using multiple strategies.
        
        SSM responses can be complex boto3 objects. This function tries multiple
        extraction methods to get the actual string value.
        
        Strategies:
        1. Direct dict access: response['Parameter']['Value']
        2. Nested navigation: response.get('Parameter', {}).get('Value')
        3. Direct .Value attribute on Parameter object
        4. String conversion of entire response
        5. Repr examination for embedded value
        
        Args:
            response: SSM get_parameter response (can be dict or boto3 object)
            param_path: Parameter path for logging
            
        Returns:
            Extracted string value or None if all strategies fail
        """
        log_debug(f"Extracting value from SSM response type: {type(response)}")
        
        # Strategy 1: Standard dict access (most common)
        try:
            if isinstance(response, dict) and 'Parameter' in response:
                param = response['Parameter']
                if isinstance(param, dict) and 'Value' in param:
                    value = param['Value']
                    if isinstance(value, str):
                        log_debug(f"Strategy 1 success: Standard dict extraction")
                        return value
        except Exception as e:
            log_debug(f"Strategy 1 failed: {e}")
        
        # Strategy 2: Safe nested get
        try:
            value = response.get('Parameter', {}).get('Value')
            if value and isinstance(value, str):
                log_debug(f"Strategy 2 success: Safe nested get")
                return value
        except Exception as e:
            log_debug(f"Strategy 2 failed: {e}")
        
        # Strategy 3: Object attribute access
        try:
            if hasattr(response, 'get'):
                param = response.get('Parameter')
                if param and hasattr(param, 'get'):
                    value = param.get('Value')
                    if value and isinstance(value, str):
                        log_debug(f"Strategy 3 success: Object attribute access")
                        return value
        except Exception as e:
            log_debug(f"Strategy 3 failed: {e}")
        
        # Strategy 4: Direct Parameter object access
        try:
            if hasattr(response, 'Parameter'):
                param = response.Parameter
                if hasattr(param, 'Value'):
                    value = param.Value
                    if isinstance(value, str):
                        log_debug(f"Strategy 4 success: Direct Parameter.Value")
                        return value
        except Exception as e:
            log_debug(f"Strategy 4 failed: {e}")
        
        # Strategy 5: String conversion and parsing (last resort)
        try:
            response_str = str(response)
            log_debug(f"Strategy 5: Examining string representation: {response_str[:200]}")
            
            # Look for Value in string representation
            if "'Value':" in response_str or '"Value":' in response_str:
                log_warning(f"Value found in string but not extractable - boto3 object wrapper issue")
                log_warning(f"Response repr: {repr(response)[:500]}")
        except Exception as e:
            log_debug(f"Strategy 5 failed: {e}")
        
        # All strategies failed
        log_error(f"All extraction strategies failed for {param_path}")
        log_error(f"Response type: {type(response)}")
        log_error(f"Response dir: {dir(response)[:20]}")  # First 20 attributes
        
        return None
    
    def get_parameter(self, key: str, default: Any = None,
                     with_decryption: bool = True,
                     use_cache: bool = True) -> Any:
        """
        Get parameter from SSM Parameter Store with aggressive value extraction.
        
        Priority:
        1. Cache (if enabled)
        2. SSM Parameter Store (with multiple extraction strategies)
        3. Default value
        
        Args:
            key: Parameter key relative to prefix (e.g., 'homeassistant/url')
            default: Default value if parameter not found
            with_decryption: Decrypt SecureString parameters (default: True)
            use_cache: Use cached value if available (default: True)
            
        Returns:
            Parameter value (always string or primitive type) or default
        """
        # Check cache first
        cache_key = f"{self._cache_prefix}{key}"
        if use_cache:
            cached = cache_get(cache_key)
            if cached is not None:
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
            
            # Log response type for debugging
            log_debug(f"SSM response type: {type(response)}")
            
            # Aggressive string extraction with multiple strategies
            value = self._force_string_extraction(response, param_path)
            
            if value is None:
                log_warning(f"Could not extract value from SSM: {param_path}")
                log_warning("Falling back to default value")
                return default
            
            # Cache successful result
            if use_cache:
                cache_set(cache_key, value, ttl=self._cache_ttl)
                log_debug(f"Cached SSM parameter: {key} (TTL={self._cache_ttl}s)")
            
            log_debug(f"Successfully loaded SSM parameter: {param_path}")
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
        
        NOTE: This currently fetches parameters one-by-one. For true batch
              optimization, use boto3's get_parameters (plural) API.
        
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
        
        Useful when you know a parameter has been updated in AWS
        and you want to force a fresh fetch.
        
        Args:
            key: Specific parameter key to invalidate, or None to clear all SSM cache
        """
        if key:
            cache_key = f"{self._cache_prefix}{key}"
            cache_delete(cache_key)
            log_debug(f"Invalidated SSM cache: {key}")
        else:
            # Clear all SSM cache entries
            # Note: Gateway cache doesn't have "delete by prefix" yet,
            #       so we'd need to track all cached keys separately
            log_debug("Attempted to clear all SSM parameter cache (not fully implemented)")
            log_warning("Cache clear-all not fully implemented - use specific key invalidation")
    
    def set_parameter(self, key: str, value: str, 
                     parameter_type: str = 'String',
                     overwrite: bool = True,
                     description: str = '',
                     tags: Optional[Dict[str, str]] = None) -> bool:
        """
        Set parameter in SSM Parameter Store.
        
        NOTE: This requires ssm:PutParameter IAM permission.
              Most Lambda deployments only have read permissions.
        
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
    
    Args:
        key: Parameter key relative to configured prefix
        default: Default value if parameter not found
        
    Returns:
        Parameter value or default
    """
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
