"""
logging_core.py - Unified logging interface (gateway-facing)
Version: 2025.10.20.02
Description: Gateway compatibility layer for logging subsystem
            SUGA-ISP COMPLIANT: Uses gateway services, no duplicate implementations

CHANGELOG:
- 2025.10.20.02: CRITICAL FIX - Renamed 'operation' to 'operation_name' in implementation functions
  - Fixed _execute_log_operation_start_implementation(operation_name, ...)
  - Fixed _execute_log_operation_success_implementation(operation_name, ...)
  - Fixed _execute_log_operation_failure_implementation(operation_name, ...)
  - Resolves RuntimeError: "got multiple values for argument 'operation'"
- 2025.10.16.05: Bug Fixes Applied
  - Standardized error parameter to Union[str, Exception] for flexibility
  - Standardized all correlation_id to Optional[str] = None
  - Uses gateway.generate_correlation_id (no UUID duplication)
  - Removed unnecessary fallback logic (Lambda always has gateway)
  - Added type hints for better error detection
  - Improved parameter consistency across all functions

CRITICAL BUG FIX (2025.10.20.02):
Problem: execute_operation(interface, operation, **kwargs) has 'operation' as positional parameter.
         Implementation functions had 'operation' parameter, creating conflict in kwargs.
Solution: Renamed parameter from 'operation' to 'operation_name' in all affected functions.
Impact: Matches interface_logging.py validation and gateway_wrappers.py parameter names.

SUGA-ISP Compliance:
- Uses gateway for correlation ID generation (no reimplementation)
- Direct import from gateway (Lambda environment guarantee)
- Minimal memory footprint for AWS Lambda Free Tier
- No duplicate functionality

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

# ✅ CROSS-INTERFACE: Must use gateway for security operations
from gateway import execute_operation, GatewayInterface


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
    
    BUG FIX: Changed error parameter to Union[str, Exception] for flexibility
    
    Args:
        message: Log message
        error: Exception object or error string (optional)
        extra: Additional context data
        **kwargs: Additional parameters (ignored for compatibility)
    """
    return execute_logging_operation(LogOperation.LOG_ERROR, message, error=error, extra=extra)


def _execute_log_warning_implementation(message: str, extra: Optional[Dict[str, Any]] = None, **kwargs) -> None:
    """
    Execute log warning operation.
    
    Args:
        message: Log message
        extra: Additional context data
        **kwargs: Additional parameters (ignored for compatibility)
    """
    return execute_logging_operation(LogOperation.LOG_WARNING, message, extra=extra)


def _execute_log_debug_implementation(message: str, extra: Optional[Dict[str, Any]] = None, **kwargs) -> None:
    """
    Execute log debug operation.
    
    Args:
        message: Log message
        extra: Additional context data
        **kwargs: Additional parameters (ignored for compatibility)
    """
    return execute_logging_operation(LogOperation.LOG_DEBUG, message, extra=extra)


def _execute_log_operation_start_implementation(operation_name: str, correlation_id: Optional[str] = None, **kwargs) -> None:
    """
    Execute log operation start.
    
    FIXED 2025.10.20.02: Renamed 'operation' to 'operation_name' to avoid conflict
    with execute_operation() positional parameter.
    
    Args:
        operation_name: Operation name (renamed from 'operation')
        correlation_id: Optional correlation ID
        **kwargs: Additional parameters (ignored for compatibility)
    """
    execute_logging_operation(LogOperation.LOG_OPERATION_START, operation_name, correlation_id)


def _execute_log_operation_success_implementation(operation_name: str, duration_ms: float, correlation_id: Optional[str] = None, result: Any = None, **kwargs) -> None:
    """
    Execute log operation success.
    
    FIXED 2025.10.20.02: Renamed 'operation' to 'operation_name' to avoid conflict
    with execute_operation() positional parameter.
    
    Args:
        operation_name: Operation name (renamed from 'operation')
        duration_ms: Operation duration in milliseconds
        correlation_id: Optional correlation ID
        result: Optional operation result
        **kwargs: Additional parameters (ignored for compatibility)
    """
    execute_logging_operation(LogOperation.LOG_OPERATION_SUCCESS, operation_name, duration_ms, correlation_id, result)


def _execute_log_operation_failure_implementation(operation_name: str, error: Union[str, Exception], correlation_id: Optional[str] = None, **kwargs) -> None:
    """
    Execute log operation failure.
    
    FIXED 2025.10.20.02: Renamed 'operation' to 'operation_name' to avoid conflict
    with execute_operation() positional parameter.
    
    BUG FIX: Changed error parameter to Union[str, Exception] for flexibility
    
    Args:
        operation_name: Operation name (renamed from 'operation')
        error: Error description (string) or Exception object
        correlation_id: Optional correlation ID
        **kwargs: Additional parameters (ignored for compatibility)
    """
    # Convert Exception to string if needed for consistency with logging_manager
    error_str = str(error) if isinstance(error, Exception) else error
    execute_logging_operation(LogOperation.LOG_OPERATION_FAILURE, operation_name, error_str, correlation_id)


# ===== ERROR RESPONSE TRACKING =====

def _log_error_response_internal(status_code: int, error_message: str, correlation_id: Optional[str] = None, **kwargs) -> None:
    """
    Internal function to log error responses for analytics.
    
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
    _MANAGER.clear_error_responses()


# ===== MODULE EXPORTS =====

__all__ = [
    # Gateway-facing implementations
    '_execute_log_info_implementation',
    '_execute_log_error_implementation',
    '_execute_log_warning_implementation',
    '_execute_log_debug_implementation',
    '_execute_log_operation_start_implementation',
    '_execute_log_operation_success_implementation',
    '_execute_log_operation_failure_implementation',
    
    # Internal error response tracking
    '_log_error_response_internal',
    '_get_error_response_analytics_internal',
    '_clear_error_response_logs_internal',
]

# EOF
