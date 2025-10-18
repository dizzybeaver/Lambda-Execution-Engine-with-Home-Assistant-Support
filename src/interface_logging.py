"""
interface_logging.py - Logging Interface Router (SUGA-ISP Architecture)
Version: 2025.10.17.15
Description: Firewall router for Logging interface with import protection

CHANGELOG:
- 2025.10.17.15: FIXED Issue #20 - Added import error protection
  - Added try/except wrapper for logging_core imports
  - Sets _LOGGING_AVAILABLE flag on success/failure
  - Stores import error message for debugging
  - Provides clear error when Logging unavailable
- 2025.10.16.04: Bug fixes - Added error handling, parameter validation
- 2025.10.15.01: Initial SUGA-ISP router implementation

Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any

# Import protection
try:
    from logging_core import (
        _execute_log_info_implementation,
        _execute_log_error_implementation,
        _execute_log_warning_implementation,
        _execute_log_debug_implementation,
        _execute_log_operation_start_implementation,
        _execute_log_operation_success_implementation,
        _execute_log_operation_failure_implementation
    )
    _LOGGING_AVAILABLE = True
    _LOGGING_IMPORT_ERROR = None
except ImportError as e:
    _LOGGING_AVAILABLE = False
    _LOGGING_IMPORT_ERROR = str(e)
    _execute_log_info_implementation = None
    _execute_log_error_implementation = None
    _execute_log_warning_implementation = None
    _execute_log_debug_implementation = None
    _execute_log_operation_start_implementation = None
    _execute_log_operation_success_implementation = None
    _execute_log_operation_failure_implementation = None


_VALID_LOGGING_OPERATIONS = [
    'log_info', 'log_error', 'log_warning', 'log_debug',
    'log_operation_start', 'log_operation_success', 'log_operation_failure'
]


def execute_logging_operation(operation: str, **kwargs) -> Any:
    """
    Route logging operation requests to internal implementations.
    
    Args:
        operation: The logging operation to execute
        **kwargs: Operation-specific parameters
        
    Returns:
        Operation result from internal implementation
        
    Raises:
        RuntimeError: If Logging interface unavailable
        ValueError: If operation is unknown or parameters invalid
    """
    # Check Logging availability
    if not _LOGGING_AVAILABLE:
        raise RuntimeError(
            f"Logging interface unavailable: {_LOGGING_IMPORT_ERROR}. "
            "This may indicate missing logging_core module or circular import."
        )
    
    if operation not in _VALID_LOGGING_OPERATIONS:
        raise ValueError(
            f"Unknown logging operation: '{operation}'. "
            f"Valid operations: {', '.join(_VALID_LOGGING_OPERATIONS)}"
        )
    
    if operation == 'log_info':
        if 'message' not in kwargs:
            raise ValueError("logging.log_info requires 'message' parameter")
        return _execute_log_info_implementation(**kwargs)
    
    elif operation == 'log_error':
        if 'message' not in kwargs:
            raise ValueError("logging.log_error requires 'message' parameter")
        return _execute_log_error_implementation(**kwargs)
    
    elif operation == 'log_warning':
        if 'message' not in kwargs:
            raise ValueError("logging.log_warning requires 'message' parameter")
        return _execute_log_warning_implementation(**kwargs)
    
    elif operation == 'log_debug':
        if 'message' not in kwargs:
            raise ValueError("logging.log_debug requires 'message' parameter")
        return _execute_log_debug_implementation(**kwargs)
    
    elif operation == 'log_operation_start':
        if 'operation' not in kwargs:
            raise ValueError("logging.log_operation_start requires 'operation' parameter")
        return _execute_log_operation_start_implementation(**kwargs)
    
    elif operation == 'log_operation_success':
        if 'operation' not in kwargs:
            raise ValueError("logging.log_operation_success requires 'operation' parameter")
        if 'duration_ms' not in kwargs:
            raise ValueError("logging.log_operation_success requires 'duration_ms' parameter")
        return _execute_log_operation_success_implementation(**kwargs)
    
    elif operation == 'log_operation_failure':
        if 'operation' not in kwargs:
            raise ValueError("logging.log_operation_failure requires 'operation' parameter")
        if 'error' not in kwargs:
            raise ValueError("logging.log_operation_failure requires 'error' parameter")
        return _execute_log_operation_failure_implementation(**kwargs)
    
    else:
        raise ValueError(f"Unhandled logging operation: '{operation}'")


__all__ = ['execute_logging_operation']

# EOF
