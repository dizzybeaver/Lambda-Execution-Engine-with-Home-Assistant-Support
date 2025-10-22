"""
gateway_wrappers_logging.py - LOGGING Interface Wrappers
Version: 2025.10.22.02
Description: Convenience wrappers for LOGGING interface operations

Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Optional
from gateway_core import GatewayInterface, execute_operation


def log_info(message: str, **kwargs) -> None:
    """Log info message."""
    execute_operation(GatewayInterface.LOGGING, 'log_info', message=message, **kwargs)


def log_error(message: str, error: Optional[Exception] = None, **kwargs) -> None:
    """Log error message."""
    execute_operation(GatewayInterface.LOGGING, 'log_error', message=message, error=error, **kwargs)


def log_warning(message: str, **kwargs) -> None:
    """Log warning message."""
    execute_operation(GatewayInterface.LOGGING, 'log_warning', message=message, **kwargs)


def log_debug(message: str, **kwargs) -> None:
    """Log debug message."""
    execute_operation(GatewayInterface.LOGGING, 'log_debug', message=message, **kwargs)


def log_operation_start(operation_name: str, **kwargs) -> None:
    """
    Log operation start.
    
    FIXED 2025.10.20.02: Renamed 'operation' to 'operation_name' to avoid conflict
    with execute_operation() positional parameter.
    
    Args:
        operation_name: Name of operation being started
        **kwargs: Additional logging context
    """
    execute_operation(GatewayInterface.LOGGING, 'log_operation_start', operation_name=operation_name, **kwargs)


def log_operation_success(operation_name: str, duration_ms: float, **kwargs) -> None:
    """
    Log operation success.
    
    FIXED 2025.10.20.02: Renamed 'operation' to 'operation_name' to avoid conflict
    with execute_operation() positional parameter.
    
    Args:
        operation_name: Name of operation that succeeded
        duration_ms: Operation duration in milliseconds
        **kwargs: Additional logging context
    """
    execute_operation(GatewayInterface.LOGGING, 'log_operation_success', operation_name=operation_name, duration_ms=duration_ms, **kwargs)


def log_operation_failure(operation_name: str, error: str, **kwargs) -> None:
    """
    Log operation failure.
    
    FIXED 2025.10.20.02: Renamed 'operation' to 'operation_name' to avoid conflict
    with execute_operation() positional parameter.
    
    Args:
        operation_name: Name of operation that failed
        error: Error description
        **kwargs: Additional logging context
    """
    execute_operation(GatewayInterface.LOGGING, 'log_operation_failure', operation_name=operation_name, error=error, **kwargs)


__all__ = [
    'log_info',
    'log_error',
    'log_warning',
    'log_debug',
    'log_operation_start',
    'log_operation_success',
    'log_operation_failure',
]
