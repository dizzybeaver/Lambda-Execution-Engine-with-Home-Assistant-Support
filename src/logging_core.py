# Filename: interface_logging.py
"""
interface_logging.py - Logging Interface Router
Version: 2025.10.21.01
Description: Firewall router for Logging interface (SUGA-ISP COMPLIANT)
             This file acts as the interface router (firewall) between the SUGA-ISP
             and internal implementation files. Only this file may be accessed by
             gateway.py. Internal files are isolated.

CHANGELOG:
- 2025.10.21.01: Added DEBUG_MODE support (DEC-22 compliance)
  - Added _is_debug_mode() function to check DEBUG_MODE environment variable
  - Added _print_debug() function for consistent debug output
  - Added DEBUG_MODE checks at module initialization
  - Added debug logging for operation dispatch
  - Consistent with logging_manager.py and logging_core.py DEBUG_MODE pattern
- 2025.10.20.03: Parameter Validation Updates
  - Updated validation functions to expect 'operation_name' parameter
  - Matches gateway_wrappers.py parameter names
  - Aligned with logging_core.py implementation function parameters
- 2025.10.16.06: Architecture Compliance
  - Implements SUGA-ISP interface router pattern
  - Routes operations to logging_core.py implementations
  - Validates parameters before routing
  - Uses dispatch dictionary for O(1) routing

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

import os
from typing import Any, Dict, Callable

# ===== DEBUG_MODE SUPPORT (DEC-22) =====

def _is_debug_mode() -> bool:
    """Check if DEBUG_MODE environment variable is set to 'true'."""
    return os.getenv('DEBUG_MODE', 'false').lower() == 'true'

def _print_debug(msg: str, component: str = 'INTERFACE_LOGGING'):
    """Print debug message if DEBUG_MODE=true (DEC-22)."""
    if _is_debug_mode():
        print(f"[{component}_DEBUG] {msg}")

# Module initialization debug
_print_debug("Loading interface_logging.py module")


# ===== IMPORTS =====

try:
    from logging_core import (
        _execute_log_info_implementation,
        _execute_log_error_implementation,
        _execute_log_warning_implementation,
        _execute_log_debug_implementation,
        _execute_log_operation_start_implementation,
        _execute_log_operation_success_implementation,
        _execute_log_operation_failure_implementation,
    )
    _LOGGING_AVAILABLE = True
    _LOGGING_IMPORT_ERROR = None
    _print_debug("logging_core imported successfully")
except ImportError as e:
    _LOGGING_AVAILABLE = False
    _LOGGING_IMPORT_ERROR = str(e)
    _print_debug(f"logging_core import failed: {e}")


# ===== PARAMETER VALIDATION =====

def _validate_message_param(kwargs: Dict[str, Any], operation: str) -> None:
    """Validate message parameter exists."""
    if 'message' not in kwargs:
        raise ValueError(f"logging.{operation} requires 'message' parameter")


def _validate_operation_start_params(kwargs: Dict[str, Any]) -> None:
    """
    Validate log_operation_start parameters.
    
    FIXED 2025.10.20.02: Changed to expect 'operation_name' instead of 'operation'
    to match gateway_wrappers.py parameter rename.
    """
    if 'operation_name' not in kwargs:
        raise ValueError("logging.log_operation_start requires 'operation_name' parameter")


def _validate_operation_success_params(kwargs: Dict[str, Any]) -> None:
    """
    Validate log_operation_success parameters.
    
    FIXED 2025.10.20.02: Changed to expect 'operation_name' instead of 'operation'
    to match gateway_wrappers.py parameter rename.
    """
    if 'operation_name' not in kwargs:
        raise ValueError("logging.log_operation_success requires 'operation_name' parameter")
    if 'duration_ms' not in kwargs:
        raise ValueError("logging.log_operation_success requires 'duration_ms' parameter")


def _validate_operation_failure_params(kwargs: Dict[str, Any]) -> None:
    """
    Validate log_operation_failure parameters.
    
    FIXED 2025.10.20.02: Changed to expect 'operation_name' instead of 'operation'
    to match gateway_wrappers.py parameter rename.
    """
    if 'operation_name' not in kwargs:
        raise ValueError("logging.log_operation_failure requires 'operation_name' parameter")
    if 'error' not in kwargs:
        raise ValueError("logging.log_operation_failure requires 'error' parameter")


# ===== OPERATION DISPATCH =====

def _build_dispatch_dict() -> Dict[str, Callable]:
    """Build dispatch dictionary for logging operations. Only called if logging available."""
    _print_debug("Building operation dispatch dictionary")
    dispatch = {
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
    _print_debug(f"Dispatch dictionary built with {len(dispatch)} operations")
    return dispatch

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
    _print_debug(f"execute_logging_operation() called: operation='{operation}'")
    
    # Check Logging availability
    if not _LOGGING_AVAILABLE:
        error_msg = (
            f"Logging interface unavailable: {_LOGGING_IMPORT_ERROR}. "
            "This may indicate missing logging_core module or circular import."
        )
        _print_debug(f"ERROR: {error_msg}")
        raise RuntimeError(error_msg)
    
    # Validate operation exists
    if operation not in _OPERATION_DISPATCH:
        error_msg = (
            f"Unknown logging operation: '{operation}'. "
            f"Valid operations: {', '.join(_OPERATION_DISPATCH.keys())}"
        )
        _print_debug(f"ERROR: {error_msg}")
        raise ValueError(error_msg)
    
    # Dispatch using dictionary lookup (O(1))
    _print_debug(f"Dispatching operation '{operation}' to implementation")
    result = _OPERATION_DISPATCH[operation](**kwargs)
    _print_debug(f"Operation '{operation}' completed successfully")
    return result


__all__ = ['execute_logging_operation']

_print_debug("interface_logging.py module loaded successfully")

# EOF
