"""
logging_unified.py
Version: 2025.10.13.01
Description: Unified logging extensions with AWS Lambda compatible imports

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

from typing import Dict, Any, Optional
from gateway import execute_operation, GatewayInterface, generate_correlation_id
import time


# ===== UNIFIED LOGGING OPERATIONS =====

def log_info(message: str, extra: Optional[Dict[str, Any]] = None, correlation_id: Optional[str] = None) -> None:
    """
    Log info message through unified gateway pattern.
    Replaces duplicate logging implementations.
    """
    extra_data = extra or {}
    if correlation_id:
        extra_data['correlation_id'] = correlation_id
    
    execute_operation(
        GatewayInterface.LOGGING,
        'log_info',
        message=message,
        extra=extra_data
    )


def log_error(message: str, error: Optional[Exception] = None, extra: Optional[Dict[str, Any]] = None,
              correlation_id: Optional[str] = None) -> None:
    """
    Log error message through unified gateway pattern.
    Replaces duplicate error logging implementations.
    """
    extra_data = extra or {}
    if correlation_id:
        extra_data['correlation_id'] = correlation_id
    
    execute_operation(
        GatewayInterface.LOGGING,
        'log_error',
        message=message,
        error=error,
        extra=extra_data
    )


def log_warning(message: str, extra: Optional[Dict[str, Any]] = None, correlation_id: Optional[str] = None) -> None:
    """
    Log warning message through unified gateway pattern.
    Replaces duplicate warning logging implementations.
    """
    extra_data = extra or {}
    if correlation_id:
        extra_data['correlation_id'] = correlation_id
    
    execute_operation(
        GatewayInterface.LOGGING,
        'log_warning',
        message=message,
        extra=extra_data
    )


def log_debug(message: str, extra: Optional[Dict[str, Any]] = None, correlation_id: Optional[str] = None) -> None:
    """
    Log debug message through unified gateway pattern.
    Replaces duplicate debug logging implementations.
    """
    extra_data = extra or {}
    if correlation_id:
        extra_data['correlation_id'] = correlation_id
    
    execute_operation(
        GatewayInterface.LOGGING,
        'log_debug',
        message=message,
        extra=extra_data
    )


# ===== UNIFIED OPERATION LOGGING =====

def log_operation_start(operation: str, correlation_id: Optional[str] = None, 
                       context: Optional[Dict[str, Any]] = None) -> str:
    """
    Log operation start with auto-generated correlation ID if not provided.
    Unified operation tracking pattern.
    """
    if not correlation_id:
        correlation_id = generate_correlation_id()
    
    extra = {'correlation_id': correlation_id}
    if context:
        extra.update(context)
    
    log_info(f"Operation started: {operation}", extra=extra, correlation_id=correlation_id)
    
    return correlation_id


def log_operation_success(operation: str, duration_ms: float = 0, correlation_id: Optional[str] = None,
                         result: Optional[Dict[str, Any]] = None) -> None:
    """
    Log successful operation completion.
    Unified success logging pattern.
    """
    extra = {
        'operation': operation,
        'duration_ms': duration_ms,
        'status': 'success'
    }
    
    if correlation_id:
        extra['correlation_id'] = correlation_id
    
    if result:
        extra['result_summary'] = str(result)[:100]  # Truncate for logging
    
    log_info(f"Operation completed: {operation} ({duration_ms:.2f}ms)", extra=extra, correlation_id=correlation_id)


def log_operation_failure(operation: str, error: Exception, duration_ms: float = 0,
                         correlation_id: Optional[str] = None, context: Optional[Dict[str, Any]] = None) -> None:
    """
    Log failed operation with error details.
    Unified failure logging pattern.
    """
    extra = {
        'operation': operation,
        'duration_ms': duration_ms,
        'status': 'failure',
        'error_type': type(error).__name__
    }
    
    if correlation_id:
        extra['correlation_id'] = correlation_id
    
    if context:
        extra.update(context)
    
    log_error(f"Operation failed: {operation} ({duration_ms:.2f}ms)", error=error, extra=extra, 
             correlation_id=correlation_id)


# ===== UNIFIED REQUEST/RESPONSE LOGGING =====

def log_request(endpoint: str, method: str, params: Optional[Dict[str, Any]] = None,
               correlation_id: Optional[str] = None) -> str:
    """
    Log incoming request with details.
    Unified request logging pattern.
    """
    if not correlation_id:
        correlation_id = generate_correlation_id()
    
    extra = {
        'correlation_id': correlation_id,
        'endpoint': endpoint,
        'method': method,
        'request_type': 'incoming'
    }
    
    if params:
        extra['params_count'] = len(params)
    
    log_info(f"Request received: {method} {endpoint}", extra=extra, correlation_id=correlation_id)
    
    return correlation_id


def log_response(endpoint: str, status_code: int, duration_ms: float,
                correlation_id: Optional[str] = None, response_size: int = 0) -> None:
    """
    Log outgoing response with metrics.
    Unified response logging pattern.
    """
    extra = {
        'endpoint': endpoint,
        'status_code': status_code,
        'duration_ms': duration_ms,
        'response_size': response_size,
        'response_type': 'outgoing'
    }
    
    if correlation_id:
        extra['correlation_id'] = correlation_id
    
    level = 'info' if status_code < 400 else 'warning' if status_code < 500 else 'error'
    
    message = f"Response sent: {status_code} for {endpoint} ({duration_ms:.2f}ms)"
    
    if level == 'error':
        log_error(message, extra=extra, correlation_id=correlation_id)
    elif level == 'warning':
        log_warning(message, extra=extra, correlation_id=correlation_id)
    else:
        log_info(message, extra=extra, correlation_id=correlation_id)


# ===== UNIFIED CONTEXT MANAGER =====

class OperationLogger:
    """
    Unified operation logging with automatic start/end tracking.
    Context manager for operation lifecycle logging.
    """
    
    def __init__(self, operation: str, correlation_id: Optional[str] = None,
                 context: Optional[Dict[str, Any]] = None, auto_log: bool = True):
        self.operation = operation
        self.correlation_id = correlation_id
        self.context = context or {}
        self.auto_log = auto_log
        self.start_time = None
        self.end_time = None
        self.duration_ms = 0
        self.success = True
        self.error = None
    
    def __enter__(self):
        self.start_time = time.time()
        
        if self.auto_log:
            self.correlation_id = log_operation_start(
                self.operation,
                correlation_id=self.correlation_id,
                context=self.context
            )
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
        self.duration_ms = (self.end_time - self.start_time) * 1000
        
        if exc_type is not None:
            self.success = False
            self.error = exc_val
        
        if self.auto_log:
            if self.success:
                log_operation_success(
                    self.operation,
                    duration_ms=self.duration_ms,
                    correlation_id=self.correlation_id
                )
            else:
                log_operation_failure(
                    self.operation,
                    error=self.error,
                    duration_ms=self.duration_ms,
                    correlation_id=self.correlation_id,
                    context=self.context
                )
        
        return False  # Don't suppress exceptions


def track_operation(operation: str):
    """
    Decorator for automatic operation logging.
    Logs operation start and completion automatically.
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            with OperationLogger(operation):
                return func(*args, **kwargs)
        return wrapper
    return decorator


# ===== UNIFIED BATCH LOGGING =====

def log_batch(messages: list, level: str = 'info', correlation_id: Optional[str] = None) -> None:
    """
    Log multiple messages in batch with same level.
    Optimized for bulk logging operations.
    """
    for msg in messages:
        message = msg if isinstance(msg, str) else str(msg)
        
        if level == 'error':
            log_error(message, correlation_id=correlation_id)
        elif level == 'warning':
            log_warning(message, correlation_id=correlation_id)
        elif level == 'debug':
            log_debug(message, correlation_id=correlation_id)
        else:
            log_info(message, correlation_id=correlation_id)


# ===== UNIFIED STATISTICS =====

def get_logging_stats() -> Dict[str, Any]:
    """
    Get logging statistics through unified gateway pattern.
    Replaces duplicate stats implementations.
    """
    from logging_core import get_logging_stats as core_get_stats
    return core_get_stats()


# ===== EXPORTED FUNCTIONS =====

__all__ = [
    'log_info',
    'log_error',
    'log_warning',
    'log_debug',
    'log_operation_start',
    'log_operation_success',
    'log_operation_failure',
    'log_request',
    'log_response',
    'OperationLogger',
    'track_operation',
    'log_batch',
    'get_logging_stats'
]

# EOF
