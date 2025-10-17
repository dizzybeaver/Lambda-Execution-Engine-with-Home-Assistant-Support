"""
logging_core.py - Unified logging interface (gateway-facing)
Version: 2025.10.16.04
Description: Gateway compatibility layer for logging subsystem
            BUG FIXES: Parameter type consistency, correlation_id standardization, import ordering
            FIXED: All sibling imports use relative imports

Bug Fixes Applied:
- Standardized error parameter to Union[str, Exception] for flexibility
- Standardized all correlation_id to Optional[str] = None
- Moved gateway import to module level to avoid dynamic import issues
- Added type hints for better error detection
- Improved parameter consistency across all functions

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
from typing import Dict, Any, Optional, Union

# ✅ ALLOWED: Import from split modules within same interface
from logging_types import (
    LogOperation,
    LogTemplate,
    ErrorLogLevel,
    ErrorEntry,
    ErrorLogEntry,
)

from logging_manager import _MANAGER

from logging_operations import execute_logging_operation

# FIX Bug #9: Import gateway at module level to avoid dynamic import issues
# This is a cross-interface import, so it MUST be from gateway
try:
    from gateway import execute_operation, GatewayInterface
    _GATEWAY_AVAILABLE = True
except ImportError:
    _GATEWAY_AVAILABLE = False
    # Fallback for testing or standalone use
    execute_operation = None
    GatewayInterface = None


# ===== COMPATIBILITY LAYER FOR GATEWAY =====

def _execute_log_info_implementation(message: str, extra: Optional[Dict[str, Any]] = None, **kwargs) -> None:
    """
    Execute log info operation.
    
    Args:
        message: Log message
        extra: Additional context data
        **kwargs: Additional parameters (ignored for compatibility)
    """
    return execute_logging_operation(LogOperation.LOG_INFO, message, extra=extra)


def _execute_log_error_implementation(message: str, error: Optional[Exception] = None, extra: Optional[Dict[str, Any]] = None, **kwargs) -> None:
    """
    Execute log error operation.
    
    Args:
        message: Error message
        error: Optional exception object
        extra: Additional context data
        **kwargs: Additional parameters (ignored for compatibility)
    """
    return execute_logging_operation(LogOperation.LOG_ERROR, message, error=error, extra=extra)


def _execute_log_warning_implementation(message: str, extra: Optional[Dict[str, Any]] = None, **kwargs) -> None:
    """
    Execute log warning operation.
    
    Args:
        message: Warning message
        extra: Additional context data
        **kwargs: Additional parameters (ignored for compatibility)
    """
    return execute_logging_operation(LogOperation.LOG_WARNING, message, extra=extra)


def _execute_log_debug_implementation(message: str, extra: Optional[Dict[str, Any]] = None, **kwargs) -> None:
    """
    Execute log debug operation.
    
    Args:
        message: Debug message
        extra: Additional context data
        **kwargs: Additional parameters (ignored for compatibility)
    """
    return execute_logging_operation(LogOperation.LOG_DEBUG, message, extra=extra)


def _execute_log_operation_start_implementation(operation: str, correlation_id: Optional[str] = None, context: Optional[Dict[str, Any]] = None, **kwargs) -> str:
    """
    Execute log operation start.
    
    FIX Bug #3 & #6: Standardized correlation_id to Optional[str] = None
    FIX Bug #9: Gateway import now at module level
    
    Args:
        operation: Operation name
        correlation_id: Optional correlation ID (generated if not provided)
        context: Optional context data (not used currently)
        **kwargs: Additional parameters (ignored for compatibility)
        
    Returns:
        Correlation ID (generated or provided)
    """
    if not correlation_id and _GATEWAY_AVAILABLE:
        correlation_id = execute_operation(GatewayInterface.SECURITY, 'generate_correlation_id')
    elif not correlation_id:
        # Fallback if gateway not available
        import uuid
        correlation_id = str(uuid.uuid4())
    
    execute_logging_operation(LogOperation.LOG_OPERATION_START, operation, correlation_id)
    return correlation_id


def _execute_log_operation_success_implementation(operation: str, duration_ms: float = 0, correlation_id: Optional[str] = None, result: Any = None, **kwargs) -> None:
    """
    Execute log operation success.
    
    FIX Bug #3 & #6: Standardized correlation_id to Optional[str] = None
    
    Args:
        operation: Operation name
        duration_ms: Operation duration in milliseconds
        correlation_id: Optional correlation ID
        result: Optional operation result
        **kwargs: Additional parameters (ignored for compatibility)
    """
    execute_logging_operation(LogOperation.LOG_OPERATION_SUCCESS, operation, duration_ms, correlation_id, result)


def _execute_log_operation_failure_implementation(operation: str, error: Union[str, Exception], correlation_id: Optional[str] = None, **kwargs) -> None:
    """
    Execute log operation failure.
    
    FIX Bug #1: Changed error parameter to Union[str, Exception] for flexibility
    FIX Bug #3 & #6: Standardized correlation_id to Optional[str] = None
    
    Args:
        operation: Operation name
        error: Error description (string) or Exception object
        correlation_id: Optional correlation ID
        **kwargs: Additional parameters (ignored for compatibility)
    """
    # Convert Exception to string if needed for consistency with logging_manager
    error_str = str(error) if isinstance(error, Exception) else error
    execute_logging_operation(LogOperation.LOG_OPERATION_FAILURE, operation, error_str, correlation_id)


# ===== ERROR RESPONSE TRACKING =====

def _log_error_response_internal(status_code: int, error_message: str, correlation_id: Optional[str] = None, **kwargs) -> None:
    """
    Internal function to log error responses for analytics.
    
    FIX Bug #3 & #6: Standardized correlation_id to Optional[str] = None
    
    Args:
        status_code: HTTP status code
        error_message: Error message
        correlation_id: Optional correlation ID
        **kwargs: Additional parameters (ignored for compatibility)
    """
    _MANAGER.log_error_response(status_code, error_message, correlation_id)


def _get_error_response_analytics_internal(**kwargs) -> Dict[str, Any]:
    """
    Internal function to get error response analytics.
    
    Args:
        **kwargs: Additional parameters (ignored for compatibility)
        
    Returns:
        Error analytics dictionary
    """
    return _MANAGER.get_error_response_analytics()


def _clear_error_response_logs_internal(**kwargs) -> None:
    """
    Internal function to clear error response logs.
    
    Args:
        **kwargs: Additional parameters (ignored for compatibility)
    """
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
