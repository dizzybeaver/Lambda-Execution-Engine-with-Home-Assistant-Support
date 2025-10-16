"""
interface_logging.py - Logging Interface Router (SUGA-ISP Architecture)
Version: 2025.10.15.01
Description: Firewall router for Logging interface

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

# ✅ ALLOWED: Import internal files within same Logging interface
from logging_core import (
    _execute_log_info_implementation,
    _execute_log_error_implementation,
    _execute_log_warning_implementation,
    _execute_log_debug_implementation,
    _execute_log_operation_start_implementation,
    _execute_log_operation_success_implementation,
    _execute_log_operation_failure_implementation
)


def execute_logging_operation(operation: str, **kwargs) -> Any:
    """
    Route logging operation requests to internal implementations.
    This is called by the SUGA-ISP (gateway.py).
    
    Args:
        operation: The logging operation to execute ('info', 'error', 'warning', etc.)
        **kwargs: Operation-specific parameters
        
    Returns:
        Operation result from internal implementation
        
    Raises:
        ValueError: If operation is unknown
    """
    
    if operation == 'info' or operation == 'log_info':
        return _execute_log_info_implementation(**kwargs)
    
    elif operation == 'error' or operation == 'log_error':
        return _execute_log_error_implementation(**kwargs)
    
    elif operation == 'warning' or operation == 'log_warning':
        return _execute_log_warning_implementation(**kwargs)
    
    elif operation == 'debug' or operation == 'log_debug':
        return _execute_log_debug_implementation(**kwargs)
    
    elif operation == 'operation_start' or operation == 'log_operation_start':
        return _execute_log_operation_start_implementation(**kwargs)
    
    elif operation == 'operation_success' or operation == 'log_operation_success':
        return _execute_log_operation_success_implementation(**kwargs)
    
    elif operation == 'operation_failure' or operation == 'log_operation_failure':
        return _execute_log_operation_failure_implementation(**kwargs)
    
    else:
        raise ValueError(f"Unknown logging operation: {operation}")


__all__ = [
    'execute_logging_operation'
]

# EOF
