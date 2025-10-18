"""
interface_cache.py - Cache Interface Router (SUGA-ISP Architecture)
Version: 2025.10.17.13
Description: Firewall router for Cache interface with parameter validation and import protection

CHANGELOG:
- 2025.10.17.13: FIXED Issue #20 - Added import error protection
  - Added try/except wrapper for cache_core imports
  - Sets _CACHE_AVAILABLE flag on success/failure
  - Stores import error message for debugging
  - Provides clear error when cache unavailable
  - Follows pattern from interface_utility.py and logging_core.py
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

IMPORT PROTECTION:
Router checks cache_core availability at module load time.
If import fails (missing module, circular dependency, etc):
- Sets _CACHE_AVAILABLE = False
- Stores error message in _CACHE_IMPORT_ERROR
- All operations fail fast with clear error message
- Prevents cascade failures from import issues

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

# Import protection - try to load cache_core implementations
try:
    from cache_core import (
        _execute_get_implementation,
        _execute_set_implementation,
        _execute_exists_implementation,
        _execute_delete_implementation,
        _execute_clear_implementation,
        _execute_cleanup_expired_implementation,
        _execute_get_stats_implementation
    )
    _CACHE_AVAILABLE = True
    _CACHE_IMPORT_ERROR = None
except ImportError as e:
    _CACHE_AVAILABLE = False
    _CACHE_IMPORT_ERROR = str(e)
    # Define stub implementations to prevent NameError
    _execute_get_implementation = None
    _execute_set_implementation = None
    _execute_exists_implementation = None
    _execute_delete_implementation = None
    _execute_clear_implementation = None
    _execute_cleanup_expired_implementation = None
    _execute_get_stats_implementation = None


_VALID_CACHE_OPERATIONS = [
    'get', 'set', 'exists', 'delete', 'clear', 
    'cleanup_expired', 'get_stats'
]


def execute_cache_operation(operation: str, **kwargs) -> Any:
    """
    Route cache operation requests to internal implementations with parameter validation.
    This is called by the SUGA-ISP (gateway.py).
    
    Args:
        operation: Operation name to execute
        **kwargs: Operation-specific parameters
        
    Returns:
        Operation result (type varies by operation)
        
    Raises:
        RuntimeError: If cache interface unavailable
        ValueError: If operation unknown or parameters invalid
    """
    # Check cache availability first
    if not _CACHE_AVAILABLE:
        raise RuntimeError(
            f"Cache interface unavailable: {_CACHE_IMPORT_ERROR}. "
            "This may indicate missing cache_core module or circular import."
        )
    
    # Validate operation
    if operation not in _VALID_CACHE_OPERATIONS:
        raise ValueError(
            f"Unknown cache operation: '{operation}'. "
            f"Valid operations: {', '.join(_VALID_CACHE_OPERATIONS)}"
        )
    
    # Route to appropriate implementation with parameter validation
    if operation == 'get':
        # Validate required parameters
        if 'key' not in kwargs:
            raise ValueError("cache.get requires 'key' parameter")
        if not isinstance(kwargs['key'], str):
            raise TypeError(
                f"cache.get 'key' must be str, got {type(kwargs['key']).__name__}"
            )
        return _execute_get_implementation(**kwargs)
    
    elif operation == 'set':
        # Validate required parameters
        if 'key' not in kwargs:
            raise ValueError("cache.set requires 'key' parameter")
        if 'value' not in kwargs:
            raise ValueError("cache.set requires 'value' parameter")
        if not isinstance(kwargs['key'], str):
            raise TypeError(
                f"cache.set 'key' must be str, got {type(kwargs['key']).__name__}"
            )
        return _execute_set_implementation(**kwargs)
    
    elif operation == 'exists':
        # Validate required parameters
        if 'key' not in kwargs:
            raise ValueError("cache.exists requires 'key' parameter")
        if not isinstance(kwargs['key'], str):
            raise TypeError(
                f"cache.exists 'key' must be str, got {type(kwargs['key']).__name__}"
            )
        return _execute_exists_implementation(**kwargs)
    
    elif operation == 'delete':
        # Validate required parameters
        if 'key' not in kwargs:
            raise ValueError("cache.delete requires 'key' parameter")
        if not isinstance(kwargs['key'], str):
            raise TypeError(
                f"cache.delete 'key' must be str, got {type(kwargs['key']).__name__}"
            )
        return _execute_delete_implementation(**kwargs)
    
    elif operation == 'clear':
        # No parameters required
        return _execute_clear_implementation(**kwargs)
    
    elif operation == 'cleanup_expired':
        # No parameters required
        return _execute_cleanup_expired_implementation(**kwargs)
    
    elif operation == 'get_stats':
        # No parameters required
        return _execute_get_stats_implementation(**kwargs)
    
    else:
        # Should never reach here due to validation above, but defensive
        raise ValueError(f"Unhandled cache operation: '{operation}'")


__all__ = ['execute_cache_operation']

# EOF
