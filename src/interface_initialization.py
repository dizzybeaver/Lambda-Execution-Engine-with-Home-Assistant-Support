"""
interface_initialization.py - Initialization Interface Router (SUGA-ISP Architecture)
Version: 2025.10.17.14
Description: Firewall router for Initialization interface with import protection

CHANGELOG:
- 2025.10.17.14: FIXED Issue #20 - Added import error protection
  - Added try/except wrapper for initialization_core imports
  - Sets _INITIALIZATION_AVAILABLE flag on success/failure
  - Stores import error message for debugging
  - Provides clear error when Initialization unavailable
- 2025.10.16.01: Bugs fixed - Added missing operations and imports
  - Added missing 'get_config' operation route
  - Added missing 'is_initialized' operation route
  - Added missing 'reset' operation route
  - Added 3 missing implementation function imports
  - Improved error handling with complete operation list

This file acts as the interface router (firewall) between the SUGA-ISP
and internal implementation files. Only this file may be accessed by
gateway.py. Internal files are isolated.

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
    from initialization_core import (
        _execute_initialize_implementation,
        _execute_get_config_implementation,
        _execute_is_initialized_implementation,
        _execute_reset_implementation,
        _execute_get_status_implementation,
        _execute_set_flag_implementation,
        _execute_get_flag_implementation
    )
    _INITIALIZATION_AVAILABLE = True
    _INITIALIZATION_IMPORT_ERROR = None
except ImportError as e:
    _INITIALIZATION_AVAILABLE = False
    _INITIALIZATION_IMPORT_ERROR = str(e)
    _execute_initialize_implementation = None
    _execute_get_config_implementation = None
    _execute_is_initialized_implementation = None
    _execute_reset_implementation = None
    _execute_get_status_implementation = None
    _execute_set_flag_implementation = None
    _execute_get_flag_implementation = None


_VALID_INITIALIZATION_OPERATIONS = [
    'initialize', 'get_config', 'is_initialized', 'reset',
    'get_status', 'set_flag', 'get_flag'
]


def execute_initialization_operation(operation: str, **kwargs) -> Any:
    """
    Route initialization operation requests to internal implementations.
    This is called by the SUGA-ISP (gateway.py).
    
    Args:
        operation: Initialization operation to execute
        **kwargs: Operation-specific parameters
        
    Returns:
        Operation result
        
    Raises:
        RuntimeError: If Initialization interface unavailable
        ValueError: If operation is unknown
    """
    # Check Initialization availability
    if not _INITIALIZATION_AVAILABLE:
        raise RuntimeError(
            f"Initialization interface unavailable: {_INITIALIZATION_IMPORT_ERROR}. "
            "This may indicate missing initialization_core module or circular import."
        )
    
    if operation not in _VALID_INITIALIZATION_OPERATIONS:
        raise ValueError(
            f"Unknown initialization operation: '{operation}'. "
            f"Valid operations: {', '.join(_VALID_INITIALIZATION_OPERATIONS)}"
        )
    
    if operation == 'initialize':
        return _execute_initialize_implementation(**kwargs)
    
    elif operation == 'get_config':
        return _execute_get_config_implementation(**kwargs)
    
    elif operation == 'is_initialized':
        return _execute_is_initialized_implementation(**kwargs)
    
    elif operation == 'reset':
        return _execute_reset_implementation(**kwargs)
    
    elif operation == 'get_status':
        return _execute_get_status_implementation(**kwargs)
    
    elif operation == 'set_flag':
        if 'flag_name' not in kwargs:
            raise ValueError("initialization.set_flag requires 'flag_name' parameter")
        if 'value' not in kwargs:
            raise ValueError("initialization.set_flag requires 'value' parameter")
        if not isinstance(kwargs['flag_name'], str):
            raise TypeError(f"initialization.set_flag 'flag_name' must be str, got {type(kwargs['flag_name']).__name__}")
        return _execute_set_flag_implementation(**kwargs)
    
    elif operation == 'get_flag':
        if 'flag_name' not in kwargs:
            raise ValueError("initialization.get_flag requires 'flag_name' parameter")
        if not isinstance(kwargs['flag_name'], str):
            raise TypeError(f"initialization.get_flag 'flag_name' must be str, got {type(kwargs['flag_name']).__name__}")
        return _execute_get_flag_implementation(**kwargs)
    
    else:
        raise ValueError(f"Unhandled initialization operation: '{operation}'")


__all__ = ['execute_initialization_operation']

# EOF
