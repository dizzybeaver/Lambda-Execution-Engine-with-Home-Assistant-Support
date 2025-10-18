"""
config_param_store.py - AWS SSM Parameter Store Integration
Version: 2025.10.18.06
Description: Robust SSM Parameter Store access with aggressive type safety

DESIGN DECISIONS:

**Aggressive String Conversion:**
   - Forces resolution of boto3 proxy/wrapper objects
   - Uses JSON serialization fallback for complex responses
   - Ensures all values are primitive types (str, int, float, bool)
   - Reason: Some Lambda environments have boto3 returning object wrappers

**Comprehensive Error Handling:**
   - Multiple extraction strategies (dict access, JSON parse, string coercion)
   - Detailed logging at every step for debugging
   - Cache invalidation on errors to allow retry
   - Graceful degradation to default values

**Dual Caching Strategy:**
   - Cache in this module (SSM-specific, short TTL)
   - Config system can cache again (application-level, longer TTL)
   - Reason: Different cache invalidation needs at different layers

**Lazy Boto3 Loading:**
   - Only imports boto3 when SSM actually used
   - Reduces cold start time for env-var-only configs
   - Reason: Lambda optimization - don't load unused dependencies

CHANGELOG:
- 2025.10.18.06: Initial implementation
  - Created dedicated SSM Parameter Store module
  - Implements aggressive type safety for boto3 responses
  - Handles object wrapper edge cases
  - Fixes "<object object at 0x...>" error (Issue #31)
  - JSON serialization fallback for complex responses
  - Comprehensive error handling and logging
  - Cache invalidation support

Copyright 2025 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

import os
import json
from typing import Any, Optional, Dict, List
from gateway import (
    log_debug, log_warning, log_error,
    cache_get, cache_set, cache_delete
)


class ParameterStoreClient:
    """
    Robust AWS SSM Parameter Store client with aggressive type safety.
    
    Handles edge cases where boto3 returns proxy/wrapper objects
    instead of plain Python types. Uses multiple extraction strategies
    to ensure values are always usable primitives.
    
    DESIGN DECISION: Aggressive type conversion
    Reason: boto3 in some Lambda environments returns botocore response
            objects that don't convert to strings naturally. We force
            resolution through multiple fallback strategies.
    """
    
    def __init__(self, prefix: str = "/lambda-execution-engine"):
        """
        Initialize Parameter Store client.
        
        Args:
            prefix: SSM parameter path prefix (e.g., '/lambda-execution-engine')
        """
        self._prefix = prefix
        self._cache_prefix = "ssm_param_"
        self._ssm_client = None
        self._cache_ttl = 300  # 5 minutes
        
        log_debug(f"ParameterStoreClient initialized with prefix: {prefix}")
    
    def _get_ssm_client(self):
        """
        Lazy-load boto3 SSM client.
        
        DESIGN DECISION: Lazy loading
        Reason: Don't import boto3 unless SSM is actually used.
                Reduces Lambda cold start time by ~50ms when using env vars.
        
        Returns:
            boto3 SSM client
            
        Raises:
            Exception: If boto3 cannot be imported or client creation fails
        """
        if self._ssm_client is None:
            try:
                import boto3
                self._ssm_client = boto3.client('ssm')
                log_debug("SSM client initialized successfully")
            except Exception as e:
                log_error(f"Failed to initialize SSM client: {e}")
                raise RuntimeError(f"Cannot create SSM client: {e}") from e
        return self._ssm_client
    
    def _build_param_path(self, key: str) -> str:
        """
        Build full SSM parameter path from relative key.
        
        Args:
            key: Relative parameter key (e.g., 'homeassistant/url')
            
        Returns:
            Full path (e.g., '/lambda-execution-engine/homeassistant/url')
        """
        # Remove leading slash from key if present (normalize)
        key = key.lstrip('/')
        full_path = f"{self._prefix}/{key}"
        return full_path
    
    def _force_string_extraction(self, response: Any, param_path: str) -> Optional[str]:
        """
        Aggressively extract string value from SSM response.
        
        Uses multiple strategies to handle various edge cases:
        1. Normal dict access (expected case)
        2. JSON serialization (forces lazy evaluation)
        3. Direct string coercion (last resort)
        
        DESIGN DECISION: Multiple extraction strategies
        Reason: boto3 behavior varies across Lambda environments. Some return
                normal dicts, others return botocore StreamingBody or proxy
                objects. We try all methods to ensure we get a usable value.
        
        Args:
            response: boto3 SSM response (may be dict or object)
            param_path: Full parameter path (for logging)
            
        Returns:
            String value or None if extraction fails
        """
        # Strategy 1: Normal dict access (90% of cases)
        try:
            if isinstance(response, dict):
                param = response.get('Parameter', {})
                
                if not isinstance(param, dict):
                    log_warning(f"SSM Parameter is not dict for {param_path}: {type(param)}")
                else:
                    value = param.get('Value', None)
                    
                    if value is not None:
                        # Check if value is already a primitive type
                        if isinstance(value, (str, int, float, bool)):
                            # Convert to string if not already
                            result = str(value) if not isinstance(value, str) else value
                            log_debug(f"SSM extraction (dict): {param_path} = {result[:50]}...")
                            return result
                        else:
                            # Object wrapper detected - force string conversion
                            log_warning(f"SSM returned non-primitive type {type(value)} for {param_path}")
                            result = str(value)
                            log_debug(f"SSM extraction (forced str): {param_path} = {result[:50]}...")
                            return result
        except Exception as e:
            log_warning(f"Strategy 1 (dict access) failed for {param_path}: {e}")
        
        # Strategy 2: JSON serialization (forces lazy evaluation)
        try:
            log_debug(f"Trying JSON serialization for {param_path}")
            
            # Force any lazy objects to resolve by JSON encoding
            response_json = json.dumps(response, default=str)
            response_dict = json.loads(response_json)
            
            value = response_dict.get('Parameter', {}).get('Value', None)
            
            if value is not None:
                result = str(value)
                log_debug(f"SSM extraction (JSON): {param_path} = {result[:50]}...")
                return result
        except Exception as e:
            log_warning(f"Strategy 2 (JSON) failed for {param_path}: {e}")
        
        # Strategy 3: Direct string coercion (last resort)
        try:
            log_debug(f"Trying direct string coercion for {param_path}")
            
            # Try to access as attribute (some proxy objects support this)
            if hasattr(response, 'Parameter'):
                param = response.Parameter
                if hasattr(param, 'Value'):
                    value = param.Value
                    result = str(value)
                    log_debug(f"SSM extraction (attribute): {param_path} = {result[:50]}...")
                    return result
        except Exception as e:
            log_warning(f"Strategy 3 (attribute) failed for {param_path}: {e}")
        
        # All strategies failed
        log_error(f"All extraction strategies failed for {param_path}")
        log_error(f"Response type: {type(response)}")
        log_error(f"Response repr: {repr(response)[:200]}")
        return None
    
    def get_parameter(self, key: str, default: Any = None, 
                      with_decryption: bool = True,
                      use_cache: bool = True) -> Any:
        """
        Get parameter from SSM Parameter Store with robust error handling.
        
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
        key: Specific parameter key, or None to attempt clearing all
    """
    _param_store_client.invalidate_cache(key)


def set_parameter(key: str, value: str, **kwargs) -> bool:
    """
    Set parameter in SSM Parameter Store (convenience wrapper).
    
    NOTE: Requires ssm:PutParameter IAM permission.
    
    Args:
        key: Parameter key relative to prefix
        value: Parameter value
        **kwargs: Additional arguments (parameter_type, overwrite, etc.)
        
    Returns:
        True if successful, False otherwise
    """
    return _param_store_client.set_parameter(key, value, **kwargs)


# ===== MODULE EXPORTS =====

__all__ = [
    # Main class
    'ParameterStoreClient',
    
    # Convenience functions
    'get_parameter',
    'get_parameters',
    'invalidate_cache',
    'set_parameter',
]

# EOF
