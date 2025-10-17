"""
interface_cache.py - Cache Interface Router (SUGA-ISP Architecture)
Version: 2025.10.17.05
Description: Firewall router for Cache interface with parameter validation

CHANGELOG:
- 2025.10.17.05: Added parameter validation for all operations (Issue #18 fix)
  - Validates required parameters before routing
  - Clear error messages with parameter names
  - Type checking for key (must be string)
  - Follows interface_logging.py pattern for validation
- 2025.10.16.03: Bug fixes - added cleanup_expired routing, standardized operation names
- 2025.10.15.01: Initial SUGA-ISP router implementation

PARAMETER VALIDATION:
This router validates required parameters before routing to internal implementations.
Validation happens at the router level to:
- Provide clear error messages early
- Prevent invalid calls from reaching internal implementations
- Follow SUGA-ISP principle: routers validate, implementations execute

Error messages include:
- Operation name for context
- Missing parameter names
- Expected parameter types
- Actual received types when applicable

Copyright 2025 Joseph Hersey

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

from typing import Any

from cache_core import (
    _execute_get_implementation,
    _execute_set_implementation,
    _execute_exists_implementation,
    _execute_delete_implementation,
    _execute_clear_implementation,
    _execute_cleanup_expired_implementation,
    _execute_get_stats_implementation
)


_VALID_CACHE_OPERATIONS = [
    'get', 'set', 'exists', 'delete', 'clear', 
    'cleanup_expired', 'get_stats'
]


def execute_cache_operation(operation: str, **kwargs) -> Any:
    """
    Route cache operation requests to internal implementations with parameter validation.
    This is called by the SUGA-ISP (gateway.py).
    
    Args:
        operation: The cache operation to execute
                  Valid: 'get', 'set', 'exists', 'delete', 'clear', 
                         'cleanup_expired', 'get_stats'
        **kwargs: Operation-specific parameters
        
    Returns:
        Operation result from internal implementation
        
    Raises:
        ValueError: If operation is unknown or required parameters are missing/invalid
        
    Notes:
        - Parameter validation happens here before routing
        - Type validation ensures correct parameter types
        - Clear error messages identify missing/invalid parameters
    """
    
    if operation == 'get':
        _validate_key_param(kwargs, operation)
        return _execute_get_implementation(**kwargs)
    
    elif operation == 'set':
        _validate_set_params(kwargs, operation)
        return _execute_set_implementation(**kwargs)
    
    elif operation == 'exists':
        _validate_key_param(kwargs, operation)
        return _execute_exists_implementation(**kwargs)
    
    elif operation == 'delete':
        _validate_key_param(kwargs, operation)
        return _execute_delete_implementation(**kwargs)
    
    elif operation == 'clear':
        # No parameters required for clear
        return _execute_clear_implementation(**kwargs)
    
    elif operation == 'cleanup_expired':
        # No parameters required for cleanup_expired
        return _execute_cleanup_expired_implementation(**kwargs)
    
    elif operation == 'get_stats':
        # No parameters required for get_stats
        return _execute_get_stats_implementation(**kwargs)
    
    else:
        raise ValueError(
            f"Unknown cache operation: '{operation}'. "
            f"Valid operations: {', '.join(_VALID_CACHE_OPERATIONS)}"
        )


def _validate_key_param(kwargs: dict, operation: str) -> None:
    """
    Validate that key parameter exists and is a valid string.
    
    Args:
        kwargs: Parameter dictionary
        operation: Operation name (for error context)
        
    Raises:
        ValueError: If key is missing, not a string, or empty
    """
    if 'key' not in kwargs:
        raise ValueError(f"Cache operation '{operation}' requires parameter 'key'")
    
    key = kwargs.get('key')
    if not isinstance(key, str):
        raise ValueError(
            f"Cache operation '{operation}' parameter 'key' must be string, "
            f"got {type(key).__name__}"
        )
    
    if not key:
        raise ValueError(
            f"Cache operation '{operation}' parameter 'key' cannot be empty string"
        )


def _validate_set_params(kwargs: dict, operation: str) -> None:
    """
    Validate parameters for cache set operation.
    
    Args:
        kwargs: Parameter dictionary
        operation: Operation name (for error context)
        
    Raises:
        ValueError: If required parameters are missing or invalid
    """
    # Validate key parameter
    _validate_key_param(kwargs, operation)
    
    # Validate value parameter exists
    if 'value' not in kwargs:
        raise ValueError(f"Cache operation '{operation}' requires parameter 'value'")
    
    # Note: value can be any type including None, so no type validation
    
    # Validate ttl if provided (optional parameter)
    if 'ttl' in kwargs:
        ttl = kwargs.get('ttl')
        if not isinstance(ttl, (int, float)):
            raise ValueError(
                f"Cache operation '{operation}' parameter 'ttl' must be numeric, "
                f"got {type(ttl).__name__}"
            )
        if ttl <= 0:
            raise ValueError(
                f"Cache operation '{operation}' parameter 'ttl' must be positive, "
                f"got {ttl}"
            )


__all__ = [
    'execute_cache_operation'
]

# EOF
