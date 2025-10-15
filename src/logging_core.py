"""
aws/logging_core.py - Unified logging interface (gateway-facing)
Version: 2025.10.15.07
Description: Gateway compatibility layer for logging subsystem
            FIXED: All sibling imports now use relative imports with dots

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

import logging
from typing import Dict, Any, Optional

# FIXED: Import from split modules using relative imports
from .logging_types import (
    LogOperation,
    LogTemplate,
    ErrorLogLevel,
    ErrorEntry,
    ErrorLogEntry,
)

from .logging_manager import _MANAGER

from .logging_operations import execute_logging_operation


# ===== COMPATIBILITY LAYER FOR GATEWAY =====

def _execute_log_info_implementation(message: str, extra: Optional[Dict[str, Any]] = None, **kwargs) -> None:
    """Execute log info operation."""
    return execute_logging_operation(LogOperation.LOG_INFO, message, extra=extra)


def _execute_log_error_implementation(message: str, error: Optional[Exception] = None, extra: Optional[Dict[str, Any]] = None, **kwargs) -> None:
    """Execute log error operation."""
    return execute_logging_operation(LogOperation.LOG_ERROR, message, error=error, extra=extra)


def _execute_log_warning_implementation(message: str, extra: Optional[Dict[str, Any]] = None, **kwargs) -> None:
    """Execute log warning operation."""
    return execute_logging_operation(LogOperation.LOG_WARNING, message, extra=extra)


def _execute_log_debug_implementation(message: str, extra: Optional[Dict[str, Any]] = None, **kwargs) -> None:
    """Execute log debug operation."""
    return execute_logging_operation(LogOperation.LOG_DEBUG, message, extra=extra)


def _execute_log_operation_start_implementation(operation: str, correlation_id: Optional[str] = None, context: Optional[Dict[str, Any]] = None, **kwargs) -> str:
    """Execute log operation start."""
    if not correlation_id:
        from gateway import execute_operation, GatewayInterface
        correlation_id = execute_operation(GatewayInterface.SECURITY, 'generate_correlation_id')
    
    execute_logging_operation(LogOperation.LOG_OPERATION_START, operation, correlation_id)
    return correlation_id


def _execute_log_operation_success_implementation(operation: str, duration_ms: float = 0, correlation_id: Optional[str] = None, result: Any = None, **kwargs) -> None:
    """Execute log operation success."""
    execute_logging_operation(LogOperation.LOG_OPERATION_SUCCESS, operation, duration_ms, correlation_id, result)


def _execute_log_operation_failure_implementation(operation: str, error: str, correlation_id: Optional[str] = None, **kwargs) -> None:
    """Execute log operation failure."""
    execute_logging_operation(LogOperation.LOG_OPERATION_FAILURE, operation, error, correlation_id)


# ===== ERROR RESPONSE TRACKING =====

def _log_error_response_internal(status_code: int, error_message: str, correlation_id: Optional[str] = None, **kwargs) -> None:
    """Internal function to log error responses for analytics."""
    _MANAGER.log_error_response(status_code, error_message, correlation_id)


def _get_error_response_analytics_internal(**kwargs) -> Dict[str, Any]:
    """Internal function to get error response analytics."""
    return _MANAGER.get_error_response_analytics()


def _clear_error_response_logs_internal(**kwargs) -> None:
    """Internal function to clear error response logs."""
    _MANAGER.clear_error_response_logs()


# ===== EXPORTS =====

__all__ = [
    # Gateway compatibility layer
    '_execute_log_info_implementation',
    '_execute_log_error_implementation',
    '_execute_log_warning_implementation',
    '_execute_log_debug_implementation',
    '_execute_log_operation_start_implementation',
    '_execute_log_operation_success_implementation',
    '_execute_log_operation_failure_implementation',
    
    # Error response tracking
    '_log_error_response_internal',
    '_get_error_response_analytics_internal',
    '_clear_error_response_logs_internal',
    
    # Re-export from other modules for convenience
    'LogOperation',
    'LogTemplate',
    'ErrorLogLevel',
    'ErrorEntry',
    'ErrorLogEntry',
    'execute_logging_operation',
]

# EOF
