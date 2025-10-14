"""
aws/logging_core.py - Unified logging interface (gateway-facing)
Version: 2025.10.14.01
Description: Gateway compatibility layer for logging subsystem

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

# Import from split modules
from logging_types import (
    LogOperation,
    LogTemplate,
    ErrorLogLevel,
    ErrorEntry,
    ErrorLogEntry,
)

from logging_manager import _MANAGER

from logging_operations import execute_logging_operation


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
    return execute_logging_operation(LogOperation.LOG_OPERATION_SUCCESS, operation, duration_ms, result, correlation_id)


def _execute_log_operation_failure_implementation(operation: str, error: Exception, duration_ms: float = 0, correlation_id: Optional[str] = None, context: Optional[Dict[str, Any]] = None, **kwargs) -> None:
    """Execute log operation failure."""
    return execute_logging_operation(LogOperation.LOG_OPERATION_FAILURE, operation, error, duration_ms, correlation_id, context)


# ===== PUBLIC INTERFACE =====

def log_template_fast(template: LogTemplate, *args, level: int = logging.INFO) -> None:
    """Public interface for fast template logging."""
    _MANAGER.log_template_fast(template, *args, level=level)


def get_logging_stats() -> Dict[str, Any]:
    """Public interface for logging statistics."""
    return _MANAGER.get_stats()


# ===== ERROR RESPONSE TRACKING INTERNAL FUNCTIONS =====

def _log_error_response_internal(error_response: Dict[str, Any], 
                                correlation_id: Optional[str] = None,
                                source_module: Optional[str] = None,
                                lambda_context = None,
                                additional_context: Optional[Dict[str, Any]] = None) -> str:
    """Internal implementation for logging error responses."""
    return _MANAGER.log_error_response(
        error_response=error_response,
        correlation_id=correlation_id,
        source_module=source_module,
        lambda_context=lambda_context,
        additional_context=additional_context
    )


def _get_error_response_analytics_internal(time_range_minutes: int = 60,
                                          include_details: bool = False) -> Dict[str, Any]:
    """Internal implementation for getting error response analytics."""
    return _MANAGER.get_error_analytics(time_range_minutes, include_details)


def _clear_error_response_logs_internal(older_than_minutes: Optional[int] = None) -> Dict[str, Any]:
    """Internal implementation for clearing error response logs."""
    return _MANAGER.clear_error_logs(older_than_minutes)


# ===== EXPORTS =====

__all__ = [
    # Types
    'LogOperation',
    'LogTemplate',
    'ErrorLogLevel',
    'ErrorEntry',
    'ErrorLogEntry',
    
    # Core
    'execute_logging_operation',
    
    # Public interface
    'log_template_fast',
    'get_logging_stats',
    
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
]

# EOF
