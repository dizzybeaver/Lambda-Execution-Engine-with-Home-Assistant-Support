# Filename: logging_core.py
"""
logging_core.py - Unified logging interface (SECURITY HARDENED)
Version: 2025.10.21.02
Description: Gateway compatibility layer with exception sanitization

SECURITY ENHANCEMENTS (2025.10.21.02):
- CVE-LOG-004 FIX: Exception details sanitization
- Sanitize stack traces to prevent information disclosure
- Remove internal file paths from error messages
- Limit exception detail exposure in production

CHANGELOG:
- 2025.10.21.02: SECURITY HARDENING - Exception sanitization (CVE-LOG-004)
- 2025.10.21.01: Added DEBUG_MODE support (DEC-22 compliance)
- 2025.10.20.02: CRITICAL FIX - Renamed 'operation' to 'operation_name'
- 2025.10.16.05: Bug fixes applied (error parameter standardization)

Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

import os
import traceback
from typing import Union, Optional, Dict, Any
from logging_manager import get_logging_core
from logging_types import ErrorLogLevel
import logging

# ===== CONFIGURATION =====

# SECURITY: Exception sanitization mode
SANITIZE_EXCEPTIONS = os.getenv('SANITIZE_EXCEPTIONS', 'true').lower() == 'true'
LAMBDA_MODE = os.getenv('LAMBDA_MODE', 'normal').lower()

# ===== DEBUG_MODE SUPPORT (DEC-22) =====

def _is_debug_mode() -> bool:
    """Check if DEBUG_MODE is enabled."""
    return os.getenv('DEBUG_MODE', 'false').lower() == 'true'

def _print_debug(msg: str, component: str = 'LOGGING_CORE'):
    """Print debug message if DEBUG_MODE=true (DEC-22)."""
    if _is_debug_mode():
        print(f"[{component}_DEBUG] {msg}")

_print_debug("Loading logging_core.py module (SECURITY HARDENED)")

# ===== EXCEPTION SANITIZATION (CVE-LOG-004 FIX) =====

def _sanitize_exception_details(error: Union[str, Exception], 
                                include_traceback: bool = False) -> str:
    """
    Sanitize exception details to prevent information disclosure.
    
    SECURITY CRITICAL: Prevents CVE-LOG-004.
    - Removes internal file paths
    - Removes AWS Lambda environment details
    - Limits traceback exposure in production
    - Preserves exception type and message
    
    Args:
        error: Exception or error string
        include_traceback: Whether to include sanitized traceback
        
    Returns:
        str: Sanitized error description
    """
    if error is None:
        return "No error details"
    
    # Convert to string if needed
    if isinstance(error, Exception):
        error_type = type(error).__name__
        error_msg = str(error)
    else:
        error_type = "Error"
        error_msg = str(error)
    
    # Basic sanitization: limit message length
    error_msg = error_msg[:500]
    
    if not SANITIZE_EXCEPTIONS:
        # In development/debug mode, return full details
        if include_traceback and isinstance(error, Exception):
            tb = traceback.format_exception(type(error), error, error.__traceback__)
            return f"{error_type}: {error_msg}\n{''.join(tb)}"
        return f"{error_type}: {error_msg}"
    
    # PRODUCTION MODE: Aggressive sanitization
    
    # Remove file paths that expose internal structure
    sanitized_msg = error_msg
    
    # Remove common AWS Lambda paths
    sanitized_msg = sanitized_msg.replace('/var/task/', '[APP]/')
    sanitized_msg = sanitized_msg.replace('/opt/python/', '[LIB]/')
    sanitized_msg = sanitized_msg.replace('/usr/local/', '[SYS]/')
    
    # Remove SSM parameter paths (security sensitive)
    if '/lambda-execution-engine/' in sanitized_msg:
        sanitized_msg = sanitized_msg.replace('/lambda-execution-engine/', '[PARAM]/')
    
    # Remove potential credentials in connection strings
    if 'password=' in sanitized_msg.lower():
        import re
        sanitized_msg = re.sub(r'password=[^;\s]+', 'password=***', sanitized_msg, flags=re.IGNORECASE)
    if 'token=' in sanitized_msg.lower():
        sanitized_msg = re.sub(r'token=[^;\s]+', 'token=***', sanitized_msg, flags=re.IGNORECASE)
    
    # Build sanitized output
    result = f"{error_type}: {sanitized_msg}"
    
    # Add minimal traceback info if requested (file:line only, no paths)
    if include_traceback and isinstance(error, Exception):
        try:
            tb_lines = traceback.format_tb(error.__traceback__)
            if tb_lines:
                # Extract only the last frame (where error occurred)
                last_frame = tb_lines[-1]
                # Remove file path, keep only filename and line number
                import re
                match = re.search(r'File "([^"]+)", line (\d+)', last_frame)
                if match:
                    filepath, lineno = match.groups()
                    filename = filepath.split('/')[-1]  # Just filename
                    result += f"\n  at {filename}:{lineno}"
        except Exception:
            # If traceback extraction fails, skip it
            pass
    
    return result

# ===== IMPLEMENTATION FUNCTIONS =====

def _execute_log_info_implementation(message: str, **kwargs) -> None:
    """Log info message (message already sanitized by interface_logging)."""
    _print_debug(f"_execute_log_info_implementation: message={message[:50]}...")
    core = get_logging_core()
    core.log(message, level=logging.INFO, **kwargs)

def _execute_log_warning_implementation(message: str, **kwargs) -> None:
    """Log warning message (message already sanitized)."""
    _print_debug(f"_execute_log_warning_implementation: message={message[:50]}...")
    core = get_logging_core()
    core.log(message, level=logging.WARNING, **kwargs)

def _execute_log_error_implementation(message: str, error: Union[str, Exception] = None, **kwargs) -> None:
    """
    Log error message with sanitized exception details.
    
    SECURITY: Exception details are sanitized (CVE-LOG-004).
    """
    _print_debug(f"_execute_log_error_implementation: message={message[:50]}...")
    
    core = get_logging_core()
    
    # Sanitize exception details (SECURITY CRITICAL)
    if error:
        sanitized_error = _sanitize_exception_details(error, include_traceback=_is_debug_mode())
        kwargs['error'] = sanitized_error
        
        # Add error type for tracking
        if isinstance(error, Exception):
            kwargs['error_type'] = type(error).__name__
    
    # Determine severity level
    level = ErrorLogLevel.MEDIUM
    if 'level' in kwargs:
        level = kwargs.pop('level')
    
    core.log_error_with_tracking(message, error=kwargs.get('error'), level=level, **kwargs)

def _execute_log_debug_implementation(message: str, **kwargs) -> None:
    """Log debug message (only if DEBUG_MODE enabled)."""
    if _is_debug_mode():
        _print_debug(f"_execute_log_debug_implementation: message={message[:50]}...")
        core = get_logging_core()
        core.log(message, level=logging.DEBUG, **kwargs)

def _execute_log_critical_implementation(message: str, **kwargs) -> None:
    """Log critical message."""
    _print_debug(f"_execute_log_critical_implementation: message={message[:50]}...")
    core = get_logging_core()
    core.log(message, level=logging.CRITICAL, **kwargs)

def _execute_log_operation_start_implementation(operation_name: str, **kwargs) -> None:
    """
    Log operation start (operation_name already sanitized).
    
    Args:
        operation_name: Name of operation starting
        **kwargs: Additional context (already sanitized)
    """
    _print_debug(f"_execute_log_operation_start_implementation: operation={operation_name}")
    core = get_logging_core()
    core.log(f"Operation started: {operation_name}", level=logging.INFO, **kwargs)

def _execute_log_operation_success_implementation(operation_name: str, duration_ms: float, **kwargs) -> None:
    """
    Log operation success with duration.
    
    Args:
        operation_name: Name of operation (already sanitized)
        duration_ms: Operation duration in milliseconds
        **kwargs: Additional context (already sanitized)
    """
    _print_debug(f"_execute_log_operation_success_implementation: operation={operation_name}, duration={duration_ms}ms")
    core = get_logging_core()
    core.log(f"Operation completed: {operation_name} ({duration_ms:.2f}ms)", 
             level=logging.INFO, **kwargs)

def _execute_log_operation_failure_implementation(operation_name: str, error: Union[str, Exception], **kwargs) -> None:
    """
    Log operation failure with sanitized error.
    
    SECURITY: Exception details are sanitized (CVE-LOG-004).
    
    Args:
        operation_name: Name of operation (already sanitized)
        error: Exception or error message
        **kwargs: Additional context (already sanitized)
    """
    _print_debug(f"_execute_log_operation_failure_implementation: operation={operation_name}")
    
    # Sanitize error details (SECURITY CRITICAL)
    sanitized_error = _sanitize_exception_details(error, include_traceback=_is_debug_mode())
    
    core = get_logging_core()
    core.log_error_with_tracking(
        f"Operation failed: {operation_name}",
        error=sanitized_error,
        level=ErrorLogLevel.HIGH,
        **kwargs
    )

# ===== EXPORTS =====

__all__ = [
    '_execute_log_info_implementation',
    '_execute_log_warning_implementation',
    '_execute_log_error_implementation',
    '_execute_log_debug_implementation',
    '_execute_log_critical_implementation',
    '_execute_log_operation_start_implementation',
    '_execute_log_operation_success_implementation',
    '_execute_log_operation_failure_implementation',
]

# EOF
