"""
interface_config.py - Config Interface Router (SUGA-ISP Architecture)
Version: 2025.10.17.05
Description: Firewall router for Config interface with parameter validation

CHANGELOG:
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


_VALID_CONFIG_OPERATIONS = [
    'initialize', 'get', 'set', 'get_category', 'reload',
    'switch_preset', 'get_state', 'load_environment', 'load_file', 'validate_all'
]


def execute_config_operation(operation: str, **kwargs) -> Any:
    """
    Route config operation requests to internal implementations with parameter validation.
    This is called by the SUGA-ISP (gateway.py).
    
    Args:
        operation: The config operation to execute
        **kwargs: Operation-specific parameters
        
    Returns:
        Operation result from internal implementation
        
    Raises:
        ValueError: If operation is unknown or required parameters are missing/invalid
    """
    
    if operation == 'initialize':
        return _initialize_implementation(**kwargs)
    
    elif operation == 'get':
        _validate_key_param(kwargs, operation)
        return _get_parameter_implementation(**kwargs)
    
    elif operation == 'set':
        _validate_set_params(kwargs, operation)
        return _set_parameter_implementation(**kwargs)
    
    elif operation == 'get_category':
        _validate_category_param(kwargs, operation)
        return _get_category_implementation(**kwargs)
    
    elif operation == 'reload':
        return _reload_implementation(**kwargs)
    
    elif operation == 'switch_preset':
        _validate_preset_param(kwargs, operation)
        return _switch_preset_implementation(**kwargs)
    
    elif operation == 'get_state':
        return _get_state_implementation(**kwargs)
    
    elif operation == 'load_environment':
        return _load_environment_implementation(**kwargs)
    
    elif operation == 'load_file':
        _validate_filepath_param(kwargs, operation)
        return _load_file_implementation(**kwargs)
    
    elif operation == 'validate_all':
        return _validate_all_implementation(**kwargs)
    
    else:
        raise ValueError(
            f"Unknown config operation: '{operation}'. "
            f"Valid operations: {', '.join(_VALID_CONFIG_OPERATIONS)}"
        )


def _validate_key_param(kwargs: dict, operation: str) -> None:
    """Validate key parameter for config operations."""
    if 'key' not in kwargs:
        raise ValueError(f"Config operation '{operation}' requires parameter 'key'")
    
    key = kwargs.get('key')
    if not isinstance(key, str):
        raise ValueError(
            f"Config operation '{operation}' parameter 'key' must be string, "
            f"got {type(key).__name__}"
        )
    
    if not key.strip():
        raise ValueError(f"Config operation '{operation}' parameter 'key' cannot be empty")


def _validate_set_params(kwargs: dict, operation: str) -> None:
    """Validate parameters for config set operation."""
    _validate_key_param(kwargs, operation)
    
    if 'value' not in kwargs:
        raise ValueError(f"Config operation '{operation}' requires parameter 'value'")


def _validate_category_param(kwargs: dict, operation: str) -> None:
    """Validate category parameter."""
    if 'category' not in kwargs:
        raise ValueError(f"Config operation '{operation}' requires parameter 'category'")
    
    category = kwargs.get('category')
    if not isinstance(category, str):
        raise ValueError(
            f"Config operation '{operation}' parameter 'category' must be string, "
            f"got {type(category).__name__}"
        )
    
    if not category.strip():
        raise ValueError(f"Config operation '{operation}' parameter 'category' cannot be empty")


def _validate_preset_param(kwargs: dict, operation: str) -> None:
    """Validate preset_name parameter."""
    if 'preset_name' not in kwargs:
        raise ValueError(f"Config operation '{operation}' requires parameter 'preset_name'")
    
    preset_name = kwargs.get('preset_name')
    if not isinstance(preset_name, str):
        raise ValueError(
            f"Config operation '{operation}' parameter 'preset_name' must be string, "
            f"got {type(preset_name).__name__}"
        )
    
    if not preset_name.strip():
        raise ValueError(f"Config operation '{operation}' parameter 'preset_name' cannot be empty")


def _validate_filepath_param(kwargs: dict, operation: str) -> None:
    """Validate filepath parameter."""
    if 'filepath' not in kwargs:
        raise ValueError(f"Config operation '{operation}' requires parameter 'filepath'")
    
    filepath = kwargs.get('filepath')
    if not isinstance(filepath, str):
        raise ValueError(
            f"Config operation '{operation}' parameter 'filepath' must be string, "
            f"got {type(filepath).__name__}"
        )
    
    if not filepath.strip():
        raise ValueError(f"Config operation '{operation}' parameter 'filepath' cannot be empty")


__all__ = [
    'execute_config_operation'
]

# EOF
