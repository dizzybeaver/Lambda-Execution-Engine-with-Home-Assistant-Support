"""
interface_cache.py - Cache Interface Router (SUGA-ISP Architecture)
Version: 2025.10.15.01
Description: Firewall router for Cache interface

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

# ✅ ALLOWED: Import internal files within same Cache interface
from cache_core import (
    _execute_get_implementation,
    _execute_set_implementation,
    _execute_exists_implementation,
    _execute_delete_implementation,
    _execute_clear_implementation,
    _execute_get_stats_implementation
)


def execute_cache_operation(operation: str, **kwargs) -> Any:
    """
    Route cache operation requests to internal implementations.
    This is called by the SUGA-ISP (gateway.py).
    
    Args:
        operation: The cache operation to execute ('get', 'set', 'exists', etc.)
        **kwargs: Operation-specific parameters
        
    Returns:
        Operation result from internal implementation
        
    Raises:
        ValueError: If operation is unknown
    """
    
    if operation == 'get':
        return _execute_get_implementation(**kwargs)
    
    elif operation == 'set':
        return _execute_set_implementation(**kwargs)
    
    elif operation == 'exists':
        return _execute_exists_implementation(**kwargs)
    
    elif operation == 'delete':
        return _execute_delete_implementation(**kwargs)
    
    elif operation == 'clear':
        return _execute_clear_implementation(**kwargs)
    
    elif operation == 'stats' or operation == 'get_stats':
        return _execute_get_stats_implementation(**kwargs)
    
    else:
        raise ValueError(f"Unknown cache operation: {operation}")


__all__ = [
    'execute_cache_operation'
]

# EOF
