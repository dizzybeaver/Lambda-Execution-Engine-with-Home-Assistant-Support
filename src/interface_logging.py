"""
interface_logging.py - Logging Interface Router (SUGA-ISP Architecture)
Version: 2025.10.17.17
Description: Router for Logging interface with dispatch dictionary pattern

CHANGELOG:
- 2025.10.17.17: MODERNIZED with dispatch dictionary pattern
  - Converted from elif chain (7 operations) to dispatch dictionary
  - O(1) operation lookup vs O(n) elif chain
  - Reduced code from ~160 lines to ~145 lines
  - Easier to maintain and extend (add operation = 1 line)
  - Follows pattern from interface_utility.py v2025.10.17.16
  - All validation logic preserved in helper functions
- 2025.10.17.15: FIXED Issue #20 - Added import error protection
- 2025.10.16.04: Bug fixes - Added error handling, parameter validation

Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any, Callable, Dict

# ===== IMPORT PROTECTION =====

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


# ===== VALIDATION HELPERS =====

def _validate_message_param(kwargs: Dict[str, Any], operation: str) -> None:
    """Validate message parameter exists."""
    if 'message' not in kwargs:
        raise ValueError(f"logging.{operation} requires 'message' parameter")


def _validate_operation_start_params(kwargs: Dict[str, Any]) -> None:
    """Validate log_operation_start parameters."""
    if 'operation' not in kwargs:
        raise ValueError("logging.log_operation_start requires 'operation' parameter")


def _validate_operation_success_params(kwargs: Dict[str, Any]) -> None:
    """Validate log_operation_success parameters."""
    if 'operation' not in kwargs:
        raise ValueError("logging.log_operation_success requires 'operation' parameter")
    if 'duration_ms' not in kwargs:
        raise ValueError("logging.log_operation_success requires 'duration_ms' parameter")


def _validate_operation_failure_params(kwargs: Dict[str, Any]) -> None:
    """Validate log_operation_failure parameters."""
    if 'operation' not in kwargs:
        raise ValueError("logging.log_operation_failure requires 'operation' parameter")
    if 'error' not in kwargs:
        raise ValueError("logging.log_operation_failure requires 'error' parameter")


# ===== OPERATION DISPATCH =====

def _build_dispatch_dict() -> Dict[str, Callable]:
    """Build dispatch dictionary for logging operations. Only called if logging available."""
    return {
        'log_info': lambda **kwargs: (
            _validate_message_param(kwargs, 'log_info'),
            _execute_log_info_implementation(**kwargs)
        )[1],
        
        'log_error': lambda **kwargs: (
            _validate_message_param(kwargs, 'log_error'),
            _execute_log_error_implementation(**kwargs)
        )[1],
        
        'log_warning': lambda **kwargs: (
            _validate_message_param(kwargs, 'log_warning'),
            _execute_log_warning_implementation(**kwargs)
        )[1],
        
        'log_debug': lambda **kwargs: (
            _validate_message_param(kwargs, 'log_debug'),
            _execute_log_debug_implementation(**kwargs)
        )[1],
        
        'log_operation_start': lambda **kwargs: (
            _validate_operation_start_params(kwargs),
            _execute_log_operation_start_implementation(**kwargs)
        )[1],
        
        'log_operation_success': lambda **kwargs: (
            _validate_operation_success_params(kwargs),
            _execute_log_operation_success_implementation(**kwargs)
        )[1],
        
        'log_operation_failure': lambda **kwargs: (
            _validate_operation_failure_params(kwargs),
            _execute_log_operation_failure_implementation(**kwargs)
        )[1],
    }

_OPERATION_DISPATCH = _build_dispatch_dict() if _LOGGING_AVAILABLE else {}


# ===== MAIN ROUTER FUNCTION =====

def execute_logging_operation(operation: str, **kwargs) -> Any:
    """
    Route logging operation requests using dispatch dictionary pattern.
    
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
    
    # Validate operation exists
    if operation not in _OPERATION_DISPATCH:
        raise ValueError(
            f"Unknown logging operation: '{operation}'. "
            f"Valid operations: {', '.join(_OPERATION_DISPATCH.keys())}"
        )
    
    # Dispatch using dictionary lookup (O(1))
    return _OPERATION_DISPATCH[operation](**kwargs)


__all__ = ['execute_logging_operation']

# EOF
