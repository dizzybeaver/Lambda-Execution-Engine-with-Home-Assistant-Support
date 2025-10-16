"""
interface_singleton.py - Singleton Interface Router (SUGA-ISP Architecture)
Version: 2025.10.15.01
Description: Firewall router for Singleton interface

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

# ✅ ALLOWED: Import internal files within same Singleton interface
from singleton_core import (
    singleton_get_implementation,
    singleton_has_implementation,
    singleton_delete_implementation,
    singleton_clear_implementation,
    singleton_stats_implementation
)


def execute_singleton_operation(operation: str, **kwargs) -> Any:
    """
    Route singleton operation requests to internal implementations.
    This is called by the SUGA-ISP (gateway.py).
    
    Args:
        operation: The singleton operation to execute ('get', 'has', 'delete', etc.)
        **kwargs: Operation-specific parameters
        
    Returns:
        Operation result from internal implementation
        
    Raises:
        ValueError: If operation is unknown
    """
    
    if operation == 'get':
        return singleton_get_implementation(**kwargs)
    
    elif operation == 'has':
        return singleton_has_implementation(**kwargs)
    
    elif operation == 'delete':
        return singleton_delete_implementation(**kwargs)
    
    elif operation == 'clear':
        return singleton_clear_implementation(**kwargs)
    
    elif operation == 'stats':
        return singleton_stats_implementation(**kwargs)
    
    else:
        raise ValueError(f"Unknown singleton operation: {operation}")


__all__ = [
    'execute_singleton_operation'
]

# EOF
