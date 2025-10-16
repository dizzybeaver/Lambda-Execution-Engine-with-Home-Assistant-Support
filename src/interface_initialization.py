"""
interface_initialization.py - Initialization Interface Router (SUGA-ISP Architecture)
Version: 2025.10.15.01
Description: Firewall router for Initialization interface

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

# ✅ ALLOWED: Import internal files within same Initialization interface
from initialization_core import (
    initialize_system_implementation,
    get_initialization_state_implementation,
    is_initialized_implementation
)


def execute_initialization_operation(operation: str, **kwargs) -> Any:
    """
    Route initialization operation requests to internal implementations.
    This is called by the SUGA-ISP (gateway.py).
    
    Args:
        operation: The initialization operation to execute ('initialize_system', 'get_state', etc.)
        **kwargs: Operation-specific parameters
        
    Returns:
        Operation result from internal implementation
        
    Raises:
        ValueError: If operation is unknown
    """
    
    if operation == 'initialize_system':
        return initialize_system_implementation(**kwargs)
    
    elif operation == 'get_state':
        return get_initialization_state_implementation(**kwargs)
    
    elif operation == 'is_initialized':
        return is_initialized_implementation(**kwargs)
    
    else:
        raise ValueError(f"Unknown initialization operation: {operation}")


__all__ = [
    'execute_initialization_operation'
]

# EOF
