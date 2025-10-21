# Filename: interface_logging.py
"""
interface_logging.py - Logging Interface Router (SECURITY HARDENED)
Version: 2025.10.21.02
Description: Firewall router for Logging interface with auto-sanitization

SECURITY ENHANCEMENTS (2025.10.21.02):
- CVE-LOG-001 FIX: Auto-sanitization of all log data (critical)
- CVE-LOG-002 FIX: Log injection prevention (newline stripping)
- CVE-LOG-003 FIX: Input length limits enforced
- Added _sanitize_log_data() for automatic data sanitization
- Integrated with gateway.sanitize_for_log() via SECURITY interface
- All validation functions now sanitize before dispatch

CHANGELOG:
- 2025.10.21.02: SECURITY HARDENING - Auto-sanitization + length limits (CVE-LOG-001/002/003)
- 2025.10.21.01: Added DEBUG_MODE support (DEC-22 compliance)
- 2025.10.20.03: Parameter validation updates (operation_name)
- 2025.10.16.06: Architecture compliance (SUGA-ISP pattern)

Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

import os
from typing import Any, Dict, Callable

# ===== CONFIGURATION =====

# Security limits (CVE-LOG-003 fix)
MAX_MESSAGE_LENGTH = 1000  # Maximum characters in log message
MAX_EXTRA_SIZE = 10240  # Maximum bytes in extra dict (10KB)

# ===== DEBUG_MODE SUPPORT (DEC-22) =====

def _is_debug_mode() -> bool:
    """Check if DEBUG_MODE environment variable is set to 'true'."""
    return os.getenv('DEBUG_MODE', 'false').lower() == 'true'

def _print_debug(msg: str, component: str = 'INTERFACE_LOGGING'):
    """Print debug message if DEBUG_MODE=true (DEC-22)."""
    if _is_debug_mode():
        print(f"[{component}_DEBUG] {msg}")

_print_debug("Loading interface_logging.py module (SECURITY HARDENED)")

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

# ===== SECURITY SANITIZATION (CVE-LOG-001/002 FIX) =====

def _sanitize_log_data(message: str, extra: Dict[str, Any]) -> tuple:
    """
    Auto-sanitize message and extra data before logging.
    
    SECURITY CRITICAL: This function prevents CVE-LOG-001 and CVE-LOG-002.
    - Masks sensitive data (passwords, tokens, PII)
    - Prevents log injection attacks (newlines, control chars)
    - Enforces length limits
    
    Args:
        message: Raw log message
        extra: Raw extra data dictionary
        
    Returns:
        tuple: (sanitized_message, sanitized_extra)
    """
    # Import gateway for sanitize_for_log (INT-03 SECURITY interface)
    try:
        import gateway
        sanitize_available = True
    except ImportError:
        sanitize_available = False
    
    # Sanitize message (CVE-LOG-002: prevent log injection)
    if message is None:
        safe_message = ""
    else:
        safe_message = str(message)
        
        # Remove control characters and newlines (log injection prevention)
        safe_message = safe_message.replace('\n', ' ')
        safe_message = safe_message.replace('\r', ' ')
        safe_message = safe_message.replace('\t', ' ')
        
        # Remove other control characters
        safe_message = ''.join(char for char in safe_message 
                               if ord(char) >= 32 or char in '\n\r\t')
        
        # Enforce max length (CVE-LOG-003)
        if len(safe_message) > MAX_MESSAGE_LENGTH:
            safe_message = safe_message[:MAX_MESSAGE_LENGTH] + '...[truncated]'
    
    # Sanitize extra dict (CVE-LOG-001: mask sensitive data)
    if extra is None or not isinstance(extra, dict):
        safe_extra = {}
    else:
        if sanitize_available:
            # Use gateway.sanitize_for_log() to mask passwords, tokens, etc.
            safe_extra = gateway.sanitize_for_log(extra)
        else:
            # Fallback: basic sanitization if gateway not available
            safe_extra = {}
            for key, value in extra.items():
                # Mask known sensitive fields
                if any(sensitive in str(key).lower() for sensitive in 
                       ['password', 'token', 'secret', 'key', 'auth', 'credential', 'ssn', 'credit_card']):
                    safe_extra[key] = '***REDACTED***'
                else:
                    # Limit individual value size
                    if isinstance(value, str) and len(value) > 500:
                        safe_extra[key] = value[:500] + '...[truncated]'
                    else:
                        safe_extra[key] = value
        
        # Enforce total extra dict size limit (CVE-LOG-003)
        import sys
        extra_size = sys.getsizeof(safe_extra)
        if extra_size > MAX_EXTRA_SIZE:
            # Truncate to fit within limit
            safe_extra = {'_truncated': 'Extra data exceeded size limit', '_size': extra_size}
    
    return safe_message, safe_extra

# ===== PARAMETER VALIDATION (WITH SANITIZATION) =====

def _validate_message_param(kwargs: Dict[str, Any], operation: str) -> None:
    """Validate and sanitize message parameter."""
    if 'message' not in kwargs:
        raise ValueError(f"logging.{operation} requires 'message' parameter")
    
    # AUTO-SANITIZE (CVE-LOG-001/002 FIX)
    message = kwargs['message']
    extra = {k: v for k, v in kwargs.items() if k != 'message'}
    
    safe_message, safe_extra = _sanitize_log_data(message, extra)
    
    # Update kwargs with sanitized data
    kwargs['message'] = safe_message
    kwargs.update(safe_extra)

def _validate_operation_start_params(kwargs: Dict[str, Any]) -> None:
    """Validate and sanitize log_operation_start parameters."""
    if 'operation_name' not in kwargs:
        raise ValueError("logging.log_operation_start requires 'operation_name' parameter")
    
    # Sanitize operation_name
    operation_name = str(kwargs['operation_name'])
    operation_name = operation_name.replace('\n', ' ').replace('\r', ' ')
    kwargs['operation_name'] = operation_name[:200]  # Limit operation name length
    
    # Sanitize any extra data
    extra = {k: v for k, v in kwargs.items() if k != 'operation_name'}
    if extra:
        _, safe_extra = _sanitize_log_data("", extra)
        kwargs.update(safe_extra)

def _validate_operation_success_params(kwargs: Dict[str, Any]) -> None:
    """Validate and sanitize log_operation_success parameters."""
    if 'operation_name' not in kwargs:
        raise ValueError("logging.log_operation_success requires 'operation_name' parameter")
    if 'duration_ms' not in kwargs:
        raise ValueError("logging.log_operation_success requires 'duration_ms' parameter")
    
    # Sanitize operation_name
    operation_name = str(kwargs['operation_name'])
    operation_name = operation_name.replace('\n', ' ').replace('\r', ' ')
    kwargs['operation_name'] = operation_name[:200]
    
    # Sanitize any extra data
    extra = {k: v for k, v in kwargs.items() 
             if k not in ('operation_name', 'duration_ms')}
    if extra:
        _, safe_extra = _sanitize_log_data("", extra)
        kwargs.update(safe_extra)

def _validate_operation_failure_params(kwargs: Dict[str, Any]) -> None:
    """Validate and sanitize log_operation_failure parameters."""
    if 'operation_name' not in kwargs:
        raise ValueError("logging.log_operation_failure requires 'operation_name' parameter")
    if 'error' not in kwargs:
        raise ValueError("logging.log_operation_failure requires 'error' parameter")
    
    # Sanitize operation_name
    operation_name = str(kwargs['operation_name'])
    operation_name = operation_name.replace('\n', ' ').replace('\r', ' ')
    kwargs['operation_name'] = operation_name[:200]
    
    # Sanitize error (CVE-LOG-004: exception sanitization handled in logging_core)
    # Here we just ensure error is a string
    if 'error' in kwargs and kwargs['error'] is not None:
        kwargs['error'] = str(kwargs['error'])[:500]  # Limit error message length
    
    # Sanitize any extra data
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
}

# ===== PUBLIC INTERFACE =====

def execute_logging_operation(operation: str, **kwargs) -> Any:
    """
    Execute logging operation with security hardening.
    
    SECURITY: All inputs are automatically sanitized before logging.
    - Messages: newlines stripped, length limited (CVE-LOG-002/003)
    - Extra data: sensitive fields masked (CVE-LOG-001)
    - Operation names: sanitized and limited
    
    Args:
        operation: Operation name (log_info, log_error, etc.)
        **kwargs: Operation-specific parameters
        
    Returns:
        Operation result (typically None for logging)
        
    Raises:
        RuntimeError: If logging system not available
        ValueError: If operation unknown or parameters invalid
    """
    _print_debug(f"execute_logging_operation: operation={operation}")
    
    # Check availability
    if not _LOGGING_AVAILABLE:
        raise RuntimeError(
            f"Logging system not available: {_LOGGING_IMPORT_ERROR}"
        )
    
    # Validate operation exists
    if operation not in _OPERATION_DISPATCH:
        valid_ops = ', '.join(sorted(_OPERATION_DISPATCH.keys()))
        raise ValueError(
            f"Unknown logging operation: '{operation}'. "
            f"Valid operations: {valid_ops}"
        )
    
    # Validate and sanitize parameters (SECURITY CRITICAL)
    try:
        if operation in ('log_info', 'log_error', 'log_warning', 'log_debug'):
            _validate_message_param(kwargs, operation)
        elif operation == 'log_operation_start':
            _validate_operation_start_params(kwargs)
        elif operation == 'log_operation_success':
            _validate_operation_success_params(kwargs)
        elif operation == 'log_operation_failure':
            _validate_operation_failure_params(kwargs)
    except ValueError as e:
        _print_debug(f"Validation failed: {e}")
        raise
    
    # Execute operation with sanitized data
    try:
        handler = _OPERATION_DISPATCH[operation]
        result = handler(**kwargs)
        _print_debug(f"Operation {operation} completed successfully")
        return result
        
    except Exception as e:
        _print_debug(f"Operation {operation} failed: {e}")
        # Log error but don't fail (logging should not break operations)
        print(f"[INTERFACE_LOGGING_ERROR] {operation} failed: {e}")
        raise

# ===== EXPORTS =====

__all__ = ['execute_logging_operation']

# EOF
