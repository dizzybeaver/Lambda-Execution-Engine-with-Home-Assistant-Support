"""
interface_config.py - Config Interface Router (SUGA-ISP Architecture)
Version: 2025.10.15.01
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

# ✅ ALLOWED: Import internal files within same Config interface
from config_core import (
    get_config_implementation,
    set_config_implementation,
    get_config_category_implementation,
    reload_config_implementation,
    switch_config_preset_implementation,
    get_config_state_implementation,
    load_config_from_environment_implementation,
    load_config_from_file_implementation,
    validate_all_config_implementation
)


def execute_config_operation(operation: str, **kwargs) -> Any:
    """
    Route config operation requests to internal implementations.
    This is called by the SUGA-ISP (gateway.py).
    
    Args:
        operation: The config operation to execute ('get', 'set', 'reload', etc.)
        **kwargs: Operation-specific parameters
        
    Returns:
        Operation result from internal implementation
        
    Raises:
        ValueError: If operation is unknown
    """
    
    if operation == 'get':
        return get_config_implementation(**kwargs)
    
    elif operation == 'set':
        return set_config_implementation(**kwargs)
    
    elif operation == 'get_category':
        return get_config_category_implementation(**kwargs)
    
    elif operation == 'reload':
        return reload_config_implementation(**kwargs)
    
    elif operation == 'switch_preset':
        return switch_config_preset_implementation(**kwargs)
    
    elif operation == 'get_state':
        return get_config_state_implementation(**kwargs)
    
    elif operation == 'load_from_environment':
        return load_config_from_environment_implementation(**kwargs)
    
    elif operation == 'load_from_file':
        return load_config_from_file_implementation(**kwargs)
    
    elif operation == 'validate_all':
        return validate_all_config_implementation(**kwargs)
    
    else:
        raise ValueError(f"Unknown config operation: {operation}")


__all__ = [
    'execute_config_operation'
]

# EOF
