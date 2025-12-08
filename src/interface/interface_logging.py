# Filename: interface_logging.py
"""
interface_logging.py - Logging Router (SECURITY HARDENED)
Version: 2025.10.22.01
Description: Firewall router for LOGGING interface with security sanitization

Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

import os
from typing import Any, Dict, Callable, Union

from logging_core import (
    _execute_log_info_implementation,
    _execute_log_warning_implementation,
    _execute_log_error_implementation,
    _execute_log_debug_implementation,
    _execute_log_operation_start_implementation,
    _execute_log_operation_success_implementation,
    _execute_log_operation_failure_implementation,
    _execute_log_reset_implementation,
)

# ===== DEBUG_MODE SUPPORT =====

def _is_debug_mode() -> bool:
    """Check if DEBUG_MODE is enabled."""
    return os.getenv('DEBUG_MODE', 'false').lower() == 'true'

def _print_debug(msg: str):
    """Print debug message if DEBUG_MODE=true."""
    if _is_debug_mode():
        print(f"[INTERFACE_LOGGING_DEBUG] {msg}")

_print_debug("Loading interface_logging.py module")

# ===== AVAILABILITY CHECK =====

try:
    from logging_manager import get_logging_core
    _LOGGING_AVAILABLE = True
    _LOGGING_IMPORT_ERROR = None
    _print_debug("Logging core available")
except ImportError as e:
    _LOGGING_AVAILABLE = False
    _LOGGING_IMPORT_ERROR = str(e)
    _print_debug(f"Logging core unavailable: {e}")

# ===== SECURITY SANITIZATION =====

_SENSITIVE_KEYS = {'password', 'token', 'secret', 'api_key', 'auth', 'credential'}

def _sanitize_log_data(message: str, extra: Dict[str, Any]) -> tuple[str, Dict[str, Any]]:
    """Sanitize log message and extra data (CVE-LOG-001, CVE-LOG-002, CVE-LOG-003)."""
    safe_message = message.replace('\n', ' ').replace('\r', ' ')[:500]
    
    safe_extra = {}
    for key, value in extra.items():
        if any(sens in key.lower() for sens in _SENSITIVE_KEYS):
            safe_extra[key] = '***REDACTED***'
        else:
            if isinstance(value, str):
                safe_extra[key] = value[:200]
            else:
                safe_extra[key] = value
    
    return safe_message, safe_extra

# ===== VALIDATION FUNCTIONS =====

def _validate_message_param(kwargs: Dict[str, Any], operation: str) -> None:
    """Validate message parameter (removed LogTemplate validation)."""
    if 'message' not in kwargs:
        raise ValueError(f"logging.{operation} requires 'message' parameter")
    
    message = str(kwargs['message'])
    message = message.replace('\n', ' ').replace('\r', ' ')
    kwargs['message'] = message[:500]
    
    extra = {k: v for k, v in kwargs.items() if k != 'message'}
    if extra:
        _, safe_extra = _sanitize_log_data("", extra)
        kwargs.update(safe_extra)

def _validate_operation_start_params(kwargs: Dict[str, Any]) -> None:
    """Validate operation_start parameters."""
    if 'operation_name' not in kwargs:
        raise ValueError("logging.log_operation_start requires 'operation_name' parameter")
    
    operation_name = str(kwargs['operation_name'])
    operation_name = operation_name.replace('\n', ' ').replace('\r', ' ')
    kwargs['operation_name'] = operation_name[:200]
    
    extra = {k: v for k, v in kwargs.items() if k != 'operation_name'}
    if extra:
        _, safe_extra = _sanitize_log_data("", extra)
        kwargs.update(safe_extra)

def _validate_operation_success_params(kwargs: Dict[str, Any]) -> None:
    """Validate operation_success parameters."""
    if 'operation_name' not in kwargs:
        raise ValueError("logging.log_operation_success requires 'operation_name' parameter")
    if 'duration_ms' not in kwargs:
        raise ValueError("logging.log_operation_success requires 'duration_ms' parameter")
    
    operation_name = str(kwargs['operation_name'])
    operation_name = operation_name.replace('\n', ' ').replace('\r', ' ')
    kwargs['operation_name'] = operation_name[:200]
    
    try:
        kwargs['duration_ms'] = float(kwargs['duration_ms'])
    except (ValueError, TypeError):
        raise ValueError("duration_ms must be numeric")
    
    extra = {k: v for k, v in kwargs.items() 
             if k not in ('operation_name', 'duration_ms')}
    if extra:
        _, safe_extra = _sanitize_log_data("", extra)
        kwargs.update(safe_extra)

def _validate_operation_failure_params(kwargs: Dict[str, Any]) -> None:
    """Validate operation_failure parameters."""
    if 'operation_name' not in kwargs:
        raise ValueError("logging.log_operation_failure requires 'operation_name' parameter")
    if 'error' not in kwargs:
        raise ValueError("logging.log_operation_failure requires 'error' parameter")
    
    operation_name = str(kwargs['operation_name'])
    operation_name = operation_name.replace('\n', ' ').replace('\r', ' ')
    kwargs['operation_name'] = operation_name[:200]
    
    if 'error' in kwargs and kwargs['error'] is not None:
        kwargs['error'] = str(kwargs['error'])[:500]
    
    extra = {k: v for k, v in kwargs.items() 
             if k not in ('operation_name', 'error')}
    if extra:
        _, safe_extra = _sanitize_log_data("", extra)
        kwargs.update(safe_extra)

# ===== OPERATION DISPATCH =====

_OPERATION_DISPATCH: Dict[str, Callable] = {
    'log_info': _execute_log_info_implementation,
    'log_error': _execute_log_error_implementation,
    'log_warning': _execute_log_warning_implementation,
    'log_debug': _execute_log_debug_implementation,
    'log_operation_start': _execute_log_operation_start_implementation,
    'log_operation_success': _execute_log_operation_success_implementation,
    'log_operation_failure': _execute_log_operation_failure_implementation,
    'reset': _execute_log_reset_implementation,
    'reset_logging': _execute_log_reset_implementation,
}

# ===== PUBLIC INTERFACE =====

def execute_logging_operation(operation: str, **kwargs) -> Any:
    """Execute logging operation with security hardening."""
    _print_debug(f"execute_logging_operation: operation={operation}")
    
    if not _LOGGING_AVAILABLE:
        raise RuntimeError(
            f"Logging system not available: {_LOGGING_IMPORT_ERROR}"
        )
    
    if operation not in _OPERATION_DISPATCH:
        valid_ops = ', '.join(sorted(_OPERATION_DISPATCH.keys()))
        raise ValueError(
            f"Unknown logging operation: '{operation}'. "
            f"Valid operations: {valid_ops}"
        )
    
    try:
        if operation in ('log_info', 'log_error', 'log_warning', 'log_debug'):
            _validate_message_param(kwargs, operation)
        elif operation == 'log_operation_start':
            _validate_operation_start_params(kwargs)
        elif operation == 'log_operation_success':
            _validate_operation_success_params(kwargs)
        elif operation == 'log_operation_failure':
            _validate_operation_failure_params(kwargs)
        # Reset operation needs no validation
    except ValueError as e:
        _print_debug(f"Validation failed: {e}")
        raise
    
    try:
        handler = _OPERATION_DISPATCH[operation]
        result = handler(**kwargs)
        _print_debug(f"Operation {operation} completed successfully")
        return result
        
    except Exception as e:
        _print_debug(f"Operation {operation} failed: {e}")
        print(f"[INTERFACE_LOGGING_ERROR] {operation} failed: {e}")
        raise

# ===== EXPORTS =====

__all__ = ['execute_logging_operation']

# EOF
