"""
utility_error_handling.py
Version: 2025.10.13.03
Description: Unified error handling with salvaged validation and batch helpers

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

from typing import Dict, Any, Optional, Callable, List
import functools
import time
from gateway import execute_operation, GatewayInterface, create_error_response, create_success_response


class ErrorSeverity:
    """Error severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory:
    """Error category types."""
    VALIDATION = "validation"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    NOT_FOUND = "not_found"
    INTERNAL = "internal"
    EXTERNAL = "external"
    TIMEOUT = "timeout"


def handle_error(error: Exception, operation: str, context: Optional[Dict[str, Any]] = None,
                severity: str = ErrorSeverity.MEDIUM, category: str = ErrorCategory.INTERNAL,
                correlation_id: Optional[str] = None) -> Dict[str, Any]:
    """Unified error handling with logging and metrics."""
    error_type = type(error).__name__
    error_message = str(error)
    
    error_context = {
        'operation': operation,
        'error_type': error_type,
        'severity': severity,
        'category': category
    }
    
    if context:
        error_context.update(context)
    
    if correlation_id:
        error_context['correlation_id'] = correlation_id
    
    execute_operation(
        GatewayInterface.LOGGING,
        'log_error',
        message=f"Error in {operation}: {error_message}",
        error=error,
        extra=error_context
    )
    
    execute_operation(
        GatewayInterface.METRICS,
        'record_error',
        error_type=error_type,
        severity=severity,
        category=category,
        context=error_context
    )
    
    execute_operation(
        GatewayInterface.METRICS,
        'record_operation',
        operation=operation,
        success=False,
        error_type=error_type
    )
    
    return create_error_response(
        message=f"{operation} failed: {error_message}",
        error_code=f"{category.upper()}_{error_type.upper()}"
    )


def with_error_handling(operation: str, severity: str = ErrorSeverity.MEDIUM,
                       category: str = ErrorCategory.INTERNAL,
                       reraise: bool = False):
    """Decorator for automatic error handling with unified logging and metrics."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                execute_operation(
                    GatewayInterface.LOGGING,
                    'log_info',
                    message=f"Starting {operation}",
                    extra={'function': func.__name__}
                )
                
                result = func(*args, **kwargs)
                
                execute_operation(
                    GatewayInterface.LOGGING,
                    'log_info',
                    message=f"Completed {operation}",
                    extra={'function': func.__name__}
                )
                
                execute_operation(
                    GatewayInterface.METRICS,
                    'record_operation',
                    operation=operation,
                    success=True
                )
                
                return result
            
            except Exception as e:
                error_response = handle_error(
                    error=e,
                    operation=operation,
                    context={'function': func.__name__},
                    severity=severity,
                    category=category
                )
                
                if reraise:
                    raise
                
                return error_response
        
        return wrapper
    return decorator


def handle_validation_error(field: str, message: str, operation: str,
                           correlation_id: Optional[str] = None) -> Dict[str, Any]:
    """Handle validation errors with standard formatting."""
    error_context = {
        'field': field,
        'validation_message': message,
        'operation': operation
    }
    
    if correlation_id:
        error_context['correlation_id'] = correlation_id
    
    execute_operation(
        GatewayInterface.LOGGING,
        'log_warning',
        message=f"Validation error in {operation}: {field} - {message}",
        extra=error_context
    )
    
    execute_operation(
        GatewayInterface.METRICS,
        'record_error',
        error_type='ValidationError',
        severity=ErrorSeverity.LOW,
        category=ErrorCategory.VALIDATION,
        context=error_context
    )
    
    return create_error_response(
        message=f"Validation failed: {message}",
        error_code="VALIDATION_ERROR",
        details={'field': field}
    )


def handle_not_found_error(resource_type: str, resource_id: str, operation: str,
                          correlation_id: Optional[str] = None) -> Dict[str, Any]:
    """Handle resource not found errors."""
    error_context = {
        'resource_type': resource_type,
        'resource_id': resource_id,
        'operation': operation
    }
    
    if correlation_id:
        error_context['correlation_id'] = correlation_id
    
    execute_operation(
        GatewayInterface.LOGGING,
        'log_warning',
        message=f"Resource not found in {operation}: {resource_type} {resource_id}",
        extra=error_context
    )
    
    execute_operation(
        GatewayInterface.METRICS,
        'record_error',
        error_type='NotFoundError',
        severity=ErrorSeverity.LOW,
        category=ErrorCategory.NOT_FOUND,
        context=error_context
    )
    
    return create_error_response(
        message=f"{resource_type} not found: {resource_id}",
        error_code="NOT_FOUND",
        details={'resource_type': resource_type, 'resource_id': resource_id}
    )


def handle_timeout_error(operation: str, timeout_seconds: float,
                        correlation_id: Optional[str] = None) -> Dict[str, Any]:
    """Handle timeout errors."""
    error_context = {
        'operation': operation,
        'timeout_seconds': timeout_seconds
    }
    
    if correlation_id:
        error_context['correlation_id'] = correlation_id
    
    execute_operation(
        GatewayInterface.LOGGING,
        'log_error',
        message=f"Timeout in {operation}: {timeout_seconds}s",
        extra=error_context
    )
    
    execute_operation(
        GatewayInterface.METRICS,
        'record_error',
        error_type='TimeoutError',
        severity=ErrorSeverity.HIGH,
        category=ErrorCategory.TIMEOUT,
        context=error_context
    )
    
    return create_error_response(
        message=f"Operation timed out after {timeout_seconds}s",
        error_code="TIMEOUT",
        details={'timeout_seconds': timeout_seconds}
    )


def with_retry(max_attempts: int = 3, delay_seconds: float = 1.0,
              exponential_backoff: bool = False, operation_name: str = "operation"):
    """Decorator for automatic retry with exponential backoff."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                
                except Exception as e:
                    last_exception = e
                    
                    if attempt < max_attempts:
                        wait_time = delay_seconds * (2 ** (attempt - 1) if exponential_backoff else 1)
                        
                        execute_operation(
                            GatewayInterface.LOGGING,
                            'log_warning',
                            message=f"Retry attempt {attempt}/{max_attempts} for {operation_name}",
                            extra={
                                'attempt': attempt,
                                'max_attempts': max_attempts,
                                'wait_time': wait_time,
                                'error': str(e)
                            }
                        )
                        
                        time.sleep(wait_time)
                    else:
                        execute_operation(
                            GatewayInterface.LOGGING,
                            'log_error',
                            message=f"All retry attempts failed for {operation_name}",
                            error=e,
                            extra={
                                'attempts': max_attempts,
                                'final_error': str(e)
                            }
                        )
            
            if last_exception:
                raise last_exception
        
        return wrapper
    return decorator


def handle_batch_errors(results: List[Dict[str, Any]], operation: str) -> Dict[str, Any]:
    """Process and report on batch operation results."""
    total = len(results)
    successes = sum(1 for r in results if r.get('success', False))
    failures = total - successes
    
    execute_operation(
        GatewayInterface.LOGGING,
        'log_info',
        message=f"Batch {operation} completed: {successes}/{total} successful",
        extra={
            'total': total,
            'successes': successes,
            'failures': failures,
            'success_rate': round((successes / total) * 100, 2) if total > 0 else 0
        }
    )
    
    execute_operation(
        GatewayInterface.METRICS,
        'record_operation',
        operation=f"batch_{operation}",
        success=failures == 0,
        duration_ms=0
    )
    
    return {
        'success': failures == 0,
        'total': total,
        'successes': successes,
        'failures': failures,
        'results': results
    }


__all__ = [
    'ErrorSeverity',
    'ErrorCategory',
    'handle_error',
    'with_error_handling',
    'handle_validation_error',
    'handle_not_found_error',
    'handle_timeout_error',
    'with_retry',
    'handle_batch_errors',
]

# EOF
