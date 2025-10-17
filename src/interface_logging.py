"""
interface_logging.py - Logging Interface Router (SUGA-ISP Architecture)
Version: 2025.10.16.03
Description: Firewall router for Logging interface
             BUG FIXES: Added error handling, parameter validation, improved robustness
             VERIFIED: Architecture-compliant, all imports from same interface

This file acts as the interface router (firewall) between the SUGA-ISP
and internal implementation files. Only this file may be accessed by
gateway.py. Internal files are isolated.

Error Handling Philosophy:
- Router validates parameters and wraps calls with error handling
- Implementation errors are caught, logged, and re-raised with context
- Centralized error handling exists in shared_utilities.handle_operation_error()
- This follows SUGA-ISP principle: routers route safely, implementations implement

Bug Fixes Applied:
- Added try/except wrapper for all implementation calls
- Added parameter validation for required fields
- Improved error context and logging
- Standardized operation name handling
- Added defensive programming practices

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

from typing import Any, Optional
import logging

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

# Initialize logger for router errors (defensive programming)
_router_logger = logging.getLogger(__name__)


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
        ValueError: If operation is unknown or parameters invalid
        Exception: If implementation raises an error (with added context)
    """
    
    # Validate operation parameter
    if not operation or not isinstance(operation, str):
        raise ValueError("Operation must be a non-empty string")
    
    # Normalize operation name (remove 'log_' prefix if present for consistency)
    normalized_op = operation.replace('log_', '') if operation.startswith('log_') else operation
    
    try:
        # Route to appropriate implementation with error handling
        if normalized_op == 'info' or operation == 'log_info':
            _validate_message_param(kwargs)
            return _execute_log_info_implementation(**kwargs)
        
        elif normalized_op == 'error' or operation == 'log_error':
            _validate_message_param(kwargs)
            return _execute_log_error_implementation(**kwargs)
        
        elif normalized_op == 'warning' or operation == 'log_warning':
            _validate_message_param(kwargs)
            return _execute_log_warning_implementation(**kwargs)
        
        elif normalized_op == 'debug' or operation == 'log_debug':
            _validate_message_param(kwargs)
            return _execute_log_debug_implementation(**kwargs)
        
        elif normalized_op == 'operation_start' or operation == 'log_operation_start':
            _validate_operation_param(kwargs)
            return _execute_log_operation_start_implementation(**kwargs)
        
        elif normalized_op == 'operation_success' or operation == 'log_operation_success':
            _validate_operation_param(kwargs)
            return _execute_log_operation_success_implementation(**kwargs)
        
        elif normalized_op in ['operation_failure', 'operation_error'] or operation in ['log_operation_failure', 'log_operation_error']:
            _validate_operation_param(kwargs)
            return _execute_log_operation_failure_implementation(**kwargs)
        
        elif normalized_op == 'operation_end' or operation == 'log_operation_end':
            # operation_end is an alias for operation_success with no result requirement
            _validate_operation_param(kwargs)
            return _execute_log_operation_success_implementation(**kwargs)
        
        else:
            raise ValueError(f"Unknown logging operation: {operation}")
    
    except ValueError:
        # Re-raise ValueError as-is (parameter validation errors)
        raise
    
    except Exception as e:
        # Wrap other exceptions with router context for better debugging
        error_msg = f"Logging router failed for operation '{operation}': {str(e)}"
        _router_logger.error(error_msg, exc_info=True)
        raise RuntimeError(error_msg) from e


def _validate_message_param(kwargs: dict) -> None:
    """
    Validate that message parameter exists and is valid.
    
    Args:
        kwargs: Parameter dictionary
        
    Raises:
        ValueError: If message is missing or invalid
    """
    if 'message' not in kwargs:
        raise ValueError("Missing required parameter: 'message'")
    
    message = kwargs.get('message')
    if not isinstance(message, str):
        raise ValueError(f"Parameter 'message' must be a string, got {type(message).__name__}")


def _validate_operation_param(kwargs: dict) -> None:
    """
    Validate that operation parameter exists and is valid.
    
    Args:
        kwargs: Parameter dictionary
        
    Raises:
        ValueError: If operation is missing or invalid
    """
    if 'operation' not in kwargs:
        raise ValueError("Missing required parameter: 'operation'")
    
    operation = kwargs.get('operation')
    if not isinstance(operation, str) or not operation.strip():
        raise ValueError(f"Parameter 'operation' must be a non-empty string, got {type(operation).__name__}")


__all__ = [
    'execute_logging_operation'
]

# EOF
