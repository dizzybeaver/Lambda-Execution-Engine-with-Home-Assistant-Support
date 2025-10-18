"""
interface_config.py - Config Interface Router (SUGA-ISP Architecture)
Version: 2025.10.17.14
Description: Firewall router for Config interface with parameter validation and import protection

CHANGELOG:
- 2025.10.17.14: FIXED Issue #20 - Added import error protection
  - Added try/except wrapper for config_core imports
  - Sets _CONFIG_AVAILABLE flag on success/failure
  - Stores import error message for debugging
  - Provides clear error when Config unavailable
- 2025.10.17.05: Added parameter validation for all operations (Issue #18 fix)
  - Validates 'key' parameter for get/set operations
  - Validates 'category' parameter for get_category
  - Validates 'filepath' parameter for load_file
  - Type checking for all string parameters
  - Clear error messages for missing/invalid parameters
- 2025.10.16.01: Initial SUGA-ISP router implementation

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
    from config_core import (
        _initialize_implementation,
        _get_parameter_implementation,
        _set_parameter_implementation,
        _get_category_implementation,
        _reload_implementation,
        _switch_preset_implementation,
        _get_state_implementation,
        _load_environment_implementation,
        _load_file_implementation,
        _validate_all_implementation
    )
    _CONFIG_AVAILABLE = True
    _CONFIG_IMPORT_ERROR = None
except ImportError as e:
    _CONFIG_AVAILABLE = False
    _CONFIG_IMPORT_ERROR = str(e)
    _initialize_implementation = None
    _get_parameter_implementation = None
    _set_parameter_implementation = None
    _get_category_implementation = None
    _reload_implementation = None
    _switch_preset_implementation = None
    _get_state_implementation = None
    _load_environment_implementation = None
    _load_file_implementation = None
    _validate_all_implementation = None


_VALID_CONFIG_OPERATIONS = [
    'initialize', 'get', 'set', 'get_category', 'reload',
    'switch_preset', 'get_state', 'load_environment', 'load_file', 'validate_all'
]


def execute_config_operation(operation: str, **kwargs) -> Any:
    """
    Route config operation requests to internal implementations with parameter validation.
    This is called by the SUGA-ISP (gateway.py).
    
    Args:
        operation: Config operation to execute
        **kwargs: Operation-specific parameters
        
    Returns:
        Operation result
        
    Raises:
        RuntimeError: If Config interface unavailable
        ValueError: If operation is unknown or required parameters missing
    """
    # Check Config availability
    if not _CONFIG_AVAILABLE:
        raise RuntimeError(
            f"Config interface unavailable: {_CONFIG_IMPORT_ERROR}. "
            "This may indicate missing config_core module or circular import."
        )
    
    if operation not in _VALID_CONFIG_OPERATIONS:
        raise ValueError(
            f"Unknown config operation: '{operation}'. "
            f"Valid operations: {', '.join(_VALID_CONFIG_OPERATIONS)}"
        )
    
    if operation == 'initialize':
        return _initialize_implementation(**kwargs)
    
    elif operation == 'get':
        if 'key' not in kwargs:
            raise ValueError("config.get requires 'key' parameter")
        if not isinstance(kwargs['key'], str):
            raise TypeError(f"config.get 'key' must be str, got {type(kwargs['key']).__name__}")
        return _get_parameter_implementation(**kwargs)
    
    elif operation == 'set':
        if 'key' not in kwargs:
            raise ValueError("config.set requires 'key' parameter")
        if 'value' not in kwargs:
            raise ValueError("config.set requires 'value' parameter")
        if not isinstance(kwargs['key'], str):
            raise TypeError(f"config.set 'key' must be str, got {type(kwargs['key']).__name__}")
        return _set_parameter_implementation(**kwargs)
    
    elif operation == 'get_category':
        if 'category' not in kwargs:
            raise ValueError("config.get_category requires 'category' parameter")
        if not isinstance(kwargs['category'], str):
            raise TypeError(f"config.get_category 'category' must be str, got {type(kwargs['category']).__name__}")
        return _get_category_implementation(**kwargs)
    
    elif operation == 'reload':
        return _reload_implementation(**kwargs)
    
    elif operation == 'switch_preset':
        if 'preset_name' not in kwargs:
            raise ValueError("config.switch_preset requires 'preset_name' parameter")
        if not isinstance(kwargs['preset_name'], str):
            raise TypeError(f"config.switch_preset 'preset_name' must be str, got {type(kwargs['preset_name']).__name__}")
        return _switch_preset_implementation(**kwargs)
    
    elif operation == 'get_state':
        return _get_state_implementation(**kwargs)
    
    elif operation == 'load_environment':
        return _load_environment_implementation(**kwargs)
    
    elif operation == 'load_file':
        if 'filepath' not in kwargs:
            raise ValueError("config.load_file requires 'filepath' parameter")
        if not isinstance(kwargs['filepath'], str):
            raise TypeError(f"config.load_file 'filepath' must be str, got {type(kwargs['filepath']).__name__}")
        return _load_file_implementation(**kwargs)
    
    elif operation == 'validate_all':
        return _validate_all_implementation(**kwargs)
    
    else:
        raise ValueError(f"Unhandled config operation: '{operation}'")


__all__ = ['execute_config_operation']

# EOF
