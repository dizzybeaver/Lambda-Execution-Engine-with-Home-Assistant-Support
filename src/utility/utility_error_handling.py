"""
utility_error_handling.py
Version: 2025.10.13.01
Description: Unified error handling utilities with FIXED AWS Lambda imports

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

from typing import Dict, Any, Optional, Callable
import traceback
import functools

# FIXED: AWS Lambda compatible imports - NO relative imports
from gateway import execute_operation, GatewayInterface, create_error_response, create_success_response
from logging_unified import log_error, log_warning, log_info
from metrics_unified import record_error_response_metric, record_operation_metric


# ===== ERROR CATEGORIZATION =====

class ErrorCategory:
    """Standard error categories for unified handling."""
    VALIDATION = "validation"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    NOT_FOUND = "not_found"
    RATE_LIMIT = "rate_limit"
    TIMEOUT = "timeout"
    EXTERNAL_SERVICE = "external_service"
    DATABASE = "database"
    INTERNAL = "internal"
    CONFIGURATION = "configuration"


class ErrorSeverity:
    """Standard error severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# ===== UNIFIED ERROR HANDLER =====

def handle_error(error: Exception, operation: str, context: Optional[Dict[str, Any]] = None,
                severity: str = ErrorSeverity.MEDIUM, category: str = ErrorCategory.INTERNAL,
                correlation_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Unified error handling with logging and metrics.
    FIXED: Uses unified logging and metrics gateways.
    """
    error_type = type(error).__name__
    error_message = str(error)
    
    # Prepare context
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
    
    # FIXED: Log error through unified logging
    log_error(
        f"Error in {operation}: {error_message}",
        error=error,
        extra=error_context,
        correlation_id=correlation_id
    )
    
    # FIXED: Record error metrics through unified metrics
    record_error_response_metric(
        error_type=error_type,
        severity=severity,
        category=category,
        context=error_context
    )
    
    # FIXED: Record operation failure through unified metrics
    record_operation_metric(
        operation=operation,
        success=False,
        error_type=error_type
    )
    
    # Return error response
    return create_error_response(
        message=f"{operation} failed: {error_message}",
        error_code=f"{category.upper()}_{error_type.upper()}"
    )


# ===== ERROR DECORATOR =====

def with_error_handling(operation: str, severity: str = ErrorSeverity.MEDIUM,
                       category: str = ErrorCategory.INTERNAL,
                       reraise: bool = False):
    """
    Decorator for automatic error handling with unified logging and metrics.
    FIXED: Uses unified gateways for all operations.
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                # Log operation start
                log_info(f"Starting {operation}", extra={'function': func.__name__})
                
                # Execute function
                result = func(*args, **kwargs)
                
                # Log success
                log_info(f"Completed {operation}", extra={'function': func.__name__})
                
                # Record success metric
                record_operation_metric(operation=operation, success=True)
                
                return result
            
            except Exception as e:
                # Handle error
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


# ===== VALIDATION ERROR HELPERS =====

def handle_validation_error(field: str, message: str, operation: str,
                           correlation_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Handle validation errors with standard formatting.
    FIXED: Uses unified error handling.
    """
    validation_error = ValueError(f"Validation failed for {field}: {message}")
    
    return handle_error(
        error=validation_error,
        operation=operation,
        context={'field': field, 'validation_message': message},
        severity=ErrorSeverity.LOW,
        category=ErrorCategory.VALIDATION,
        correlation_id=correlation_id
    )


def validate_required_fields(data: Dict[str, Any], required_fields: list, operation: str) -> Optional[Dict[str, Any]]:
    """
    Validate required fields are present.
    FIXED: Uses unified validation error handling.
    """
    for field in required_fields:
        if field not in data or data[field] is None:
            return handle_validation_error(
                field=field,
                message="Required field is missing or null",
                operation=operation
            )
    
    return None  # No errors


# ===== RETRY HELPERS =====

def with_retry(operation: str, max_attempts: int = 3, delay_seconds: float = 1.0,
              backoff_multiplier: float = 2.0):
    """
    Decorator for automatic retry with exponential backoff.
    FIXED: Uses unified logging and metrics.
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            import time
            
            last_exception = None
            current_delay = delay_seconds
            
            for attempt in range(1, max_attempts + 1):
                try:
                    result = func(*args, **kwargs)
                    
                    # Log successful retry if not first attempt
                    if attempt > 1:
                        log_info(
                            f"Operation {operation} succeeded on attempt {attempt}/{max_attempts}",
                            extra={'attempts': attempt}
                        )
                    
                    return result
                
                except Exception as e:
                    last_exception = e
                    
                    if attempt < max_attempts:
                        # Log retry attempt
                        log_warning(
                            f"Operation {operation} failed on attempt {attempt}/{max_attempts}, retrying in {current_delay}s",
                            extra={
                                'attempt': attempt,
                                'max_attempts': max_attempts,
                                'delay_seconds': current_delay,
                                'error': str(e)
                            }
                        )
                        
                        # Wait before retry
                        time.sleep(current_delay)
                        current_delay *= backoff_multiplier
                    else:
                        # Final attempt failed
                        log_error(
                            f"Operation {operation} failed after {max_attempts} attempts",
                            error=e,
                            extra={'attempts': max_attempts}
                        )
            
            # All attempts failed
            if last_exception:
                return handle_error(
                    error=last_exception,
                    operation=operation,
                    context={'attempts': max_attempts, 'retry_exhausted': True},
                    severity=ErrorSeverity.HIGH
                )
            
            return create_error_response(
                message=f"{operation} failed after {max_attempts} attempts",
                error_code="RETRY_EXHAUSTED"
            )
        
        return wrapper
    return decorator


# ===== SAFE EXECUTION =====

def safe_execute(func: Callable, operation: str, default_return: Any = None,
                suppress_errors: bool = True, **kwargs) -> Any:
    """
    Safely execute function with unified error handling.
    FIXED: Uses unified logging and metrics.
    """
    try:
        return func(**kwargs)
    
    except Exception as e:
        # Handle error
        handle_error(
            error=e,
            operation=operation,
            context={'function': func.__name__},
            severity=ErrorSeverity.MEDIUM
        )
        
        if not suppress_errors:
            raise
        
        return default_return


# ===== CONTEXT MANAGER =====

class ErrorContext:
    """
    Context manager for unified error handling.
    FIXED: Uses unified logging and metrics.
    """
    
    def __init__(self, operation: str, severity: str = ErrorSeverity.MEDIUM,
                category: str = ErrorCategory.INTERNAL, reraise: bool = True,
                correlation_id: Optional[str] = None):
        self.operation = operation
        self.severity = severity
        self.category = category
        self.reraise = reraise
        self.correlation_id = correlation_id
        self.error = None
    
    def __enter__(self):
        log_info(f"Entering {self.operation}", correlation_id=self.correlation_id)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.error = exc_val
            
            # Handle error
            handle_error(
                error=exc_val,
                operation=self.operation,
                severity=self.severity,
                category=self.category,
                correlation_id=self.correlation_id
            )
            
            if self.reraise:
                return False  # Re-raise exception
            else:
                return True  # Suppress exception
        
        # No error
        log_info(f"Completed {self.operation}", correlation_id=self.correlation_id)
        return False


# ===== EXPORTED FUNCTIONS =====

__all__ = [
    'ErrorCategory',
    'ErrorSeverity',
    'handle_error',
    'with_error_handling',
    'handle_validation_error',
    'validate_required_fields',
    'with_retry',
    'safe_execute',
    'ErrorContext'
]

# EOF
