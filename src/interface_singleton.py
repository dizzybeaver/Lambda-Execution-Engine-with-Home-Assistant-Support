"""
interface_singleton.py - Singleton Interface Router (SUGA-ISP Architecture)
Version: 2025.10.22.03
Description: Firewall router for Singleton interface with parameter validation and import protection

CHANGELOG:
- 2025.10.22.03: Added reset operation dispatch
- 2025.10.18.01: FIXED Issue #26 - Parameter name standardization (CRITICAL FIX)
  - Changed 'key' parameter to 'name' throughout validation functions
  - Renamed _validate_key_param() to _validate_name_param()
  - Updated all validation calls to use 'name' instead of 'key'
  - Aligns with singleton_core.py which expects 'name' parameter
  - Fixes http_client singleton access through circuit breaker
  - Resolves "singleton.get requires 'key' parameter" error
- 2025.10.17.14: FIXED Issue #20 - Added import error protection
  - Added try/except wrapper for singleton_core imports
  - Sets _SINGLETON_AVAILABLE flag on success/failure
  - Stores import error message for debugging
  - Provides clear error when Singleton unavailable
- 2025.10.17.05: Added parameter validation for all operations (Issue #18 fix)
  - Validates 'name' parameter for get/set/has/delete operations
  - Validates 'value' parameter for set operation
  - Type checking for name (must be string)
  - Clear error messages for missing/invalid parameters
- 2025.10.16.01: Added missing 'set' operation route, improved error handling
- 2025.10.15.01: Initial SUGA-ISP router implementation

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

# Import protection
try:
    from singleton_core import (
        _execute_get_implementation,
        _execute_set_implementation,
        _execute_has_implementation,
        _execute_delete_implementation,
        _execute_clear_implementation,
        _execute_get_stats_implementation,
        _execute_reset_implementation
    )
    _SINGLETON_AVAILABLE = True
    _SINGLETON_IMPORT_ERROR = None
except ImportError as e:
    _SINGLETON_AVAILABLE = False
    _SINGLETON_IMPORT_ERROR = str(e)
    _execute_get_implementation = None
    _execute_set_implementation = None
    _execute_has_implementation = None
    _execute_delete_implementation = None
    _execute_clear_implementation = None
    _execute_get_stats_implementation = None
    _execute_reset_implementation = None


_VALID_SINGLETON_OPERATIONS = [
    'get', 'set', 'has', 'delete', 'clear', 'stats', 'get_stats', 'reset'
]


def _validate_name_param(kwargs: dict, operation: str) -> None:
    """Validate name parameter presence and type."""
    if 'name' not in kwargs:
        raise ValueError(f"singleton.{operation} requires 'name' parameter")
    if not isinstance(kwargs['name'], str):
        raise TypeError(
            f"singleton.{operation} 'name' must be str, got {type(kwargs['name']).__name__}"
        )


def _validate_set_params(kwargs: dict, operation: str) -> None:
    """Validate set operation parameters."""
    _validate_name_param(kwargs, operation)
    if 'value' not in kwargs:
        raise ValueError(f"singleton.{operation} requires 'value' parameter")


def execute_singleton_operation(operation: str, **kwargs) -> Any:
    """
    Route singleton operation requests to internal implementations with parameter validation.
    This is called by the SUGA-ISP (gateway.py).
    
    Args:
        operation: The singleton operation to execute
        **kwargs: Operation-specific parameters
        
    Returns:
        Operation result from internal implementation
        
    Raises:
        RuntimeError: If Singleton interface unavailable
        ValueError: If operation is unknown or required parameters are missing/invalid
    """
    # Check Singleton availability
    if not _SINGLETON_AVAILABLE:
        raise RuntimeError(
            f"Singleton interface unavailable: {_SINGLETON_IMPORT_ERROR}. "
            "This may indicate missing singleton_core module or circular import."
        )
    
    if operation == 'get':
        _validate_name_param(kwargs, operation)
        return _execute_get_implementation(**kwargs)
    
    elif operation == 'set':
        _validate_set_params(kwargs, operation)
        return _execute_set_implementation(**kwargs)
    
    elif operation == 'has':
        _validate_name_param(kwargs, operation)
        return _execute_has_implementation(**kwargs)
    
    elif operation == 'delete':
        _validate_name_param(kwargs, operation)
        return _execute_delete_implementation(**kwargs)
    
    elif operation == 'clear':
        return _execute_clear_implementation(**kwargs)
    
    elif operation == 'stats' or operation == 'get_stats':
        return _execute_get_stats_implementation(**kwargs)
    
    elif operation == 'reset':
        return _execute_reset_implementation(**kwargs)
    
    else:
        raise ValueError(
            f"Unknown singleton operation: '{operation}'. "
            f"Valid operations: {', '.join(_VALID_SINGLETON_OPERATIONS)}"
        )


__all__ = ['execute_singleton_operation']

# EOF
