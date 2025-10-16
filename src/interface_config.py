"""
interface_config.py - Config Interface Router (SUGA-ISP Architecture)
Version: 2025.10.16.01
Description: Firewall router for Config interface

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

# âœ… ALLOWED: Import internal files within same Config interface
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


def execute_config_operation(operation: str, **kwargs) -> Any:
    """
    Route config operation requests to internal implementations.
    This is called by the SUGA-ISP (gateway.py).
    
    Args:
        operation: The config operation to execute ('initialize', 'get', 'set', 'reload', etc.)
        **kwargs: Operation-specific parameters
        
    Returns:
        Operation result from internal implementation
        
    Raises:
        ValueError: If operation is unknown
    """
    
    if operation == 'initialize':
        return _initialize_implementation(**kwargs)
    
    elif operation == 'get' or operation == 'get_parameter':
        return _get_parameter_implementation(**kwargs)
    
    elif operation == 'set' or operation == 'set_parameter':
        return _set_parameter_implementation(**kwargs)
    
    elif operation == 'get_category':
        return _get_category_implementation(**kwargs)
    
    elif operation == 'reload':
        return _reload_implementation(**kwargs)
    
    elif operation == 'switch_preset':
        return _switch_preset_implementation(**kwargs)
    
    elif operation == 'get_state':
        return _get_state_implementation(**kwargs)
    
    elif operation == 'load_environment' or operation == 'load_from_environment':
        return _load_environment_implementation(**kwargs)
    
    elif operation == 'load_file' or operation == 'load_from_file':
        return _load_file_implementation(**kwargs)
    
    elif operation == 'validate' or operation == 'validate_all':
        return _validate_all_implementation(**kwargs)
    
    else:
        raise ValueError(f"Unknown config operation: {operation}")


__all__ = [
    'execute_config_operation'
]

# EOF
