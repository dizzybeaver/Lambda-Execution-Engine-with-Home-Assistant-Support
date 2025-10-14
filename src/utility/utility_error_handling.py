"""
utility_error_handling.py
Version: 2025.10.13.02
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

from gateway import (
    execute_operation, GatewayInterface,
    create_error_response, create_success_response
)
from logging_unified import log_error, log_info, log_warning
from metrics_unified import record_error_response_metric, record_operation_metric


# ===== ERROR SEVERITY AND CATEGORIES =====

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


# ===== UNIFIED ERROR HANDLER =====

def handle_error(error: Exception, operation: str, context: Optional[Dict[str, Any]] = None,
                severity: str = ErrorSeverity.MEDIUM, category: str = ErrorCategory.INTERNAL,
                correlation_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Unified error handling with logging and metrics.
    Uses unified logging and metrics gateways.
    """
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
    
    log_error(
        f"Error in {operation}: {error_message}",
        error=error,
        extra=error_context,
        correlation_id=correlation_id
    )
    
    record_error_response_metric(
        error_type=error_type,
        severity=severity,
        category=category,
        context=error_context
    )
    
    record_operation_metric(
        operation=operation,
        success=False,
        error_type=error_type
    )
    
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
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                log_info(f"Starting {operation}", extra={'function': func.__name__})
                
                result = func(*args, **kwargs)
                
                log_info(f"Completed {operation}", extra={'function': func.__name__})
                
                record_operation_metric(operation=operation, success=True)
                
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


# ===== VALIDATION ERROR HELPERS =====

def handle_validation_error(field: str, message: str, operation: str,
                           correlation_id: Optional[str] = None) -> Dict[str, Any]:
    """Handle validation errors with standard formatting."""
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
    """Validate required fields are present."""
    for field in required_fields:
        if field not in data or data[field] is None:
            return handle_validation_error(
                field=field,
                message="Required field is missing or null",
                operation=operation
            )
    
    return None


# ===== RETRY HELPERS =====

def with_retry(operation: str, max_attempts: int = 3, delay_seconds: float = 1.0,
              backoff_multiplier: float = 2.0):
    """Decorator for automatic retry with exponential backoff."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            attempt = 0
            current_delay = delay_seconds
            
            while attempt < max_attempts:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    attempt += 1
                    
                    if attempt >= max_attempts:
                        log_error(
                            f"Retry failed after {max_attempts} attempts: {operation}",
                            error=e
                        )
                        raise
                    
                    log_warning(
                        f"Retry attempt {attempt}/{max_attempts} for {operation}",
                        extra={'delay_seconds': current_delay}
                    )
                    
                    time.sleep(current_delay)
                    current_delay *= backoff_multiplier
        
        return wrapper
    return decorator


# ===== SALVAGED VALIDATION HELPERS FROM PHASE 2 =====

def validate_required(value: Any, field_name: str) -> None:
    """
    Validate field is present and not None.
    Salvaged from validation_wrapper.py
    """
    if value is None:
        raise ValueError(f"{field_name} is required")


def validate_type(value: Any, expected_type: type, field_name: str) -> None:
    """
    Validate value is of expected type.
    Salvaged from validation_wrapper.py
    """
    if not isinstance(value, expected_type):
        raise TypeError(f"{field_name} must be {expected_type.__name__}, got {type(value).__name__}")


def validate_range(value: float, min_val: Optional[float], max_val: Optional[float], field_name: str) -> None:
    """
    Validate value is within range.
    Salvaged from validation_wrapper.py
    """
    if min_val is not None and value < min_val:
        raise ValueError(f"{field_name} value {value} below minimum {min_val}")
    
    if max_val is not None and value > max_val:
        raise ValueError(f"{field_name} value {value} above maximum {max_val}")


def safe_validate(validator_func: Callable, *args, **kwargs) -> Dict[str, Any]:
    """
    Run validator and return structured result instead of raising.
    Salvaged from validation_wrapper.py
    """
    try:
        validator_func(*args, **kwargs)
        return {'valid': True, 'error': None}
    except Exception as e:
        return {
            'valid': False,
            'error': str(e),
            'error_type': type(e).__name__
        }


# ===== SALVAGED BATCH OPERATIONS FROM PHASE 2 =====

def execute_operations_batch(operations: List[Dict[str, Any]], fail_fast: bool = False) -> List[Dict[str, Any]]:
    """
    Execute multiple operations sequentially with unified error handling.
    Salvaged from batch_operations.py - simplified for single-threaded Lambda.
    
    Args:
        operations: List of dicts with 'interface', 'operation', 'params'
        fail_fast: If True, stop on first error
    
    Returns:
        List of result dicts with 'success', 'result', 'error'
    """
    results = []
    
    for op in operations:
        try:
            interface = op.get('interface')
            operation = op.get('operation')
            params = op.get('params', {})
            
            result = execute_operation(interface, operation, **params)
            
            results.append({
                'success': True,
                'result': result,
                'error': None,
                'operation': operation
            })
        
        except Exception as e:
            results.append({
                'success': False,
                'result': None,
                'error': str(e),
                'operation': op.get('operation', 'unknown')
            })
            
            if fail_fast:
                break
    
    return results


def analyze_batch_results(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Analyze batch execution results.
    Salvaged from batch_operations.py
    """
    total = len(results)
    success = sum(1 for r in results if r.get('success'))
    failed = total - success
    
    success_rate = (success / total * 100) if total > 0 else 0
    
    return {
        'total_operations': total,
        'successful': success,
        'failed': failed,
        'success_rate_percent': round(success_rate, 2)
    }


__all__ = [
    'ErrorSeverity',
    'ErrorCategory',
    'handle_error',
    'with_error_handling',
    'handle_validation_error',
    'validate_required_fields',
    'with_retry',
    'validate_required',
    'validate_type',
    'validate_range',
    'safe_validate',
    'execute_operations_batch',
    'analyze_batch_results'
]

# EOF
