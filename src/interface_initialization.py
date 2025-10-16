"""
interface_initialization.py - Initialization Interface Router (SUGA-ISP Architecture)
Version: 2025.10.16.01
Description: Firewall router for Initialization interface - BUGS FIXED

This file acts as the interface router (firewall) between the SUGA-ISP
and internal implementation files. Only this file may be accessed by
gateway.py. Internal files are isolated.

FIXES APPLIED:
- Added missing 'get_config' operation route
- Added missing 'is_initialized' operation route
- Added missing 'reset' operation route
- Added 3 missing implementation function imports
- Improved error handling with complete operation list

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

# ✅ ALLOWED: Import internal files within same Initialization interface
from initialization_core import (
    _execute_initialize_implementation,
    _execute_get_config_implementation,
    _execute_is_initialized_implementation,
    _execute_reset_implementation,
    _execute_get_status_implementation,
    _execute_set_flag_implementation,
    _execute_get_flag_implementation
)


def execute_initialization_operation(operation: str, **kwargs) -> Any:
    """
    Route initialization operation requests to internal implementations.
    This is called by the SUGA-ISP (gateway.py).
    
    Args:
        operation: The initialization operation to execute
        **kwargs: Operation-specific parameters
        
    Returns:
        Operation result from internal implementation
        
    Raises:
        ValueError: If operation is unknown
        
    Valid operations:
        - initialize, initialize_system
        - get_status, get_state
        - get_config
        - is_initialized
        - reset
        - set_flag
        - get_flag
    """
    
    if operation == 'initialize' or operation == 'initialize_system':
        return _execute_initialize_implementation(**kwargs)
    
    elif operation == 'get_status' or operation == 'get_state':
        return _execute_get_status_implementation(**kwargs)
    
    elif operation == 'get_config':
        return _execute_get_config_implementation(**kwargs)
    
    elif operation == 'is_initialized':
        return _execute_is_initialized_implementation(**kwargs)
    
    elif operation == 'reset':
        return _execute_reset_implementation(**kwargs)
    
    elif operation == 'set_flag':
        return _execute_set_flag_implementation(**kwargs)
    
    elif operation == 'get_flag':
        return _execute_get_flag_implementation(**kwargs)
    
    else:
        raise ValueError(
            f"Unknown initialization operation: '{operation}'. "
            f"Valid operations: initialize, get_status, get_config, "
            f"is_initialized, reset, set_flag, get_flag"
        )


__all__ = [
    'execute_initialization_operation'
]

# EOF
