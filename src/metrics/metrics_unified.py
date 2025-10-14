"""
metrics_unified.py
Version: 2025.10.13.01
Description: Unified metrics extensions with AWS Lambda compatible imports

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

from typing import Dict, Any, Optional, List
from gateway import execute_operation, GatewayInterface
import time


# ===== UNIFIED METRICS RECORDING =====

def record_metric(metric_name: str, value: float = 1.0, dimensions: Optional[Dict[str, str]] = None) -> bool:
    """
    Record any metric through unified gateway pattern.
    Replaces multiple duplicate implementations.
    """
    return execute_operation(
        GatewayInterface.METRICS,
        'record',
        metric_name=metric_name,
        value=value,
        dimensions=dimensions
    )


def increment_counter(counter_name: str, value: int = 1) -> int:
    """
    Increment counter through unified gateway pattern.
    Replaces duplicate counter implementations.
    """
    return execute_operation(
        GatewayInterface.METRICS,
        'increment',
        counter_name=counter_name,
        value=value
    )


def record_operation_metric(operation: str, success: bool = True, duration_ms: float = 0, 
                           error_type: Optional[str] = None) -> bool:
    """
    Record operation metrics with standard dimensions.
    Unified pattern for operation tracking.
    """
    dimensions = {
        'operation': operation,
        'success': str(success)
    }
    
    if error_type:
        dimensions['error_type'] = error_type
    
    # Record operation count
    record_metric(f'operation.{operation}.count', 1.0, dimensions)
    
    # Record duration if provided
    if duration_ms > 0:
        record_metric(f'operation.{operation}.duration_ms', duration_ms, dimensions)
    
    return True


def record_error_response_metric(error_type: str, severity: str = 'medium', 
                                 category: str = 'general', context: Optional[Dict] = None) -> bool:
    """
    Record error response metrics with categorization.
    Unified error tracking pattern.
    """
    dimensions = {
        'error_type': error_type,
        'severity': severity,
        'category': category
    }
    
    # Record error count
    record_metric('error.response.count', 1.0, dimensions)
    
    # Record additional context metrics if provided
    if context:
        for key, value in context.items():
            if isinstance(value, (int, float)):
                record_metric(f'error.{error_type}.{key}', float(value), dimensions)
    
    return True


def record_cache_metric(operation: str, hit: bool = False, miss: bool = False, 
                       eviction: bool = False, duration_ms: float = 0) -> bool:
    """
    Record cache operation metrics.
    Unified cache tracking pattern.
    """
    dimensions = {'operation': operation}
    
    if hit:
        record_metric('cache.hit', 1.0, dimensions)
    if miss:
        record_metric('cache.miss', 1.0, dimensions)
    if eviction:
        record_metric('cache.eviction', 1.0, dimensions)
    if duration_ms > 0:
        record_metric('cache.operation.duration_ms', duration_ms, dimensions)
    
    return True


def record_api_metric(endpoint: str, method: str, status_code: int, 
                     duration_ms: float, success: bool = True) -> bool:
    """
    Record API request metrics.
    Unified API tracking pattern.
    """
    dimensions = {
        'endpoint': endpoint,
        'method': method,
        'status_code': str(status_code),
        'success': str(success)
    }
    
    # Record request count
    record_metric('api.request.count', 1.0, dimensions)
    
    # Record duration
    record_metric('api.request.duration_ms', duration_ms, dimensions)
    
    # Record status code distribution
    record_metric(f'api.status.{status_code}', 1.0, dimensions)
    
    return True


# ===== UNIFIED METRICS RETRIEVAL =====

def get_all_metrics() -> Dict[str, Any]:
    """
    Get all metrics through unified gateway pattern.
    Replaces duplicate stats implementations.
    """
    return execute_operation(
        GatewayInterface.METRICS,
        'get_metrics'
    )


def get_metric_stats(metric_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Get statistics for specific metric or all metrics.
    Unified stats retrieval pattern.
    """
    if metric_name:
        from metrics_core import get_metric_value
        return get_metric_value(metric_name) or {}
    
    return get_all_metrics()


def get_operation_metrics(operation: str, time_window_minutes: int = 60) -> Dict[str, Any]:
    """
    Get metrics for specific operation within time window.
    Unified operation metrics pattern.
    """
    all_metrics = get_all_metrics()
    
    # Filter metrics for this operation
    operation_metrics = {
        k: v for k, v in all_metrics.items()
        if operation in k
    }
    
    return {
        'operation': operation,
        'time_window_minutes': time_window_minutes,
        'metrics': operation_metrics,
        'timestamp': time.time()
    }


def get_error_metrics(error_type: Optional[str] = None) -> Dict[str, Any]:
    """
    Get error metrics, optionally filtered by error type.
    Unified error metrics pattern.
    """
    all_metrics = get_all_metrics()
    
    # Filter error metrics
    error_metrics = {
        k: v for k, v in all_metrics.items()
        if k.startswith('error.')
    }
    
    if error_type:
        error_metrics = {
            k: v for k, v in error_metrics.items()
            if error_type in k
        }
    
    return {
        'error_type': error_type,
        'metrics': error_metrics,
        'timestamp': time.time()
    }


# ===== UNIFIED PERFORMANCE TRACKING =====

class PerformanceTracker:
    """
    Unified performance tracking with automatic metric recording.
    Context manager for operation timing.
    """
    
    def __init__(self, operation: str, auto_record: bool = True):
        self.operation = operation
        self.auto_record = auto_record
        self.start_time = None
        self.end_time = None
        self.duration_ms = 0
        self.success = True
        self.error_type = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
        self.duration_ms = (self.end_time - self.start_time) * 1000
        
        if exc_type is not None:
            self.success = False
            self.error_type = exc_type.__name__
        
        if self.auto_record:
            record_operation_metric(
                self.operation,
                success=self.success,
                duration_ms=self.duration_ms,
                error_type=self.error_type
            )
        
        return False  # Don't suppress exceptions


def track_performance(operation: str):
    """
    Decorator for automatic performance tracking.
    Records operation metrics automatically.
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            with PerformanceTracker(operation):
                return func(*args, **kwargs)
        return wrapper
    return decorator


# ===== UNIFIED BATCH OPERATIONS =====

def record_batch_metrics(metrics: List[Dict[str, Any]]) -> bool:
    """
    Record multiple metrics in batch.
    Optimized for bulk metric recording.
    """
    success_count = 0
    
    for metric in metrics:
        try:
            metric_name = metric.get('name')
            value = metric.get('value', 1.0)
            dimensions = metric.get('dimensions')
            
            if record_metric(metric_name, value, dimensions):
                success_count += 1
        except Exception:
            continue
    
    return success_count == len(metrics)


# ===== EXPORTED FUNCTIONS =====

__all__ = [
    'record_metric',
    'increment_counter',
    'record_operation_metric',
    'record_error_response_metric',
    'record_cache_metric',
    'record_api_metric',
    'get_all_metrics',
    'get_metric_stats',
    'get_operation_metrics',
    'get_error_metrics',
    'PerformanceTracker',
    'track_performance',
    'record_batch_metrics'
]

# EOF
