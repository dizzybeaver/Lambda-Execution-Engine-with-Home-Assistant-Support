"""
metrics_operations.py - Gateway implementation functions for metrics
Version: 2025.10.21.02
Description: PHASE 2 TASK 2.3 - Use record_metric_with_duration() helper to eliminate duplication

CHANGELOG:
- 2025.10.21.02: PHASE 2 TASK 2.3 - Genericize metric recording pattern
  - Updated 2 functions to use record_metric_with_duration() helper
  - Eliminated ~20 LOC of duplicated recording logic
  - Functions updated:
    * _execute_record_operation_metric_implementation
    * _execute_record_api_metric_implementation

- 2025.10.21.01: PHASE 2 TASK 2.1 - Genericize dimension building
  - Updated 6 functions to use build_dimensions() helper
  - Eliminated ~40 LOC of duplicated dimension building logic
  - Functions updated:
    * _execute_record_operation_metric_implementation
    * _execute_record_error_response_metric_implementation
    * _execute_record_cache_metric_implementation
    * _execute_record_api_metric_implementation
    
- 2025.10.20.03: BUG FIX - Parameter name mismatch
  - FIXED: _execute_record_cache_metric_implementation() signature
  - Changed: operation: str → operation_name: str
  - Reason: Gateway wrapper sends operation_name, not operation
  - This fixes CloudWatch error: "missing 1 required positional argument: 'operation'"

Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Dict, Any, Optional

from metrics_types import MetricOperation, ResponseType
from metrics_helper import build_dimensions, record_metric_with_duration

# CIRCULAR IMPORT FIX: Do NOT import _MANAGER at module level
# Import it inside each function instead to avoid:
# interface_metrics → metrics_operations → metrics_core → metrics_operations


# ===== GATEWAY IMPLEMENTATION FUNCTIONS =====

def _execute_record_metric_implementation(name: str, value: float, dimensions: Optional[Dict[str, str]] = None, **kwargs) -> bool:
    """Execute record metric operation."""
    from metrics_core import _MANAGER
    return _MANAGER.execute_metric_operation(MetricOperation.RECORD, name, value, dimensions)


def _execute_increment_counter_implementation(name: str, value: int = 1, **kwargs) -> int:
    """Execute increment counter operation."""
    from metrics_core import _MANAGER
    return _MANAGER.execute_metric_operation(MetricOperation.INCREMENT, name, value)


def _execute_get_stats_implementation(**kwargs) -> Dict[str, Any]:
    """Execute get stats operation."""
    from metrics_core import _MANAGER
    return _MANAGER.execute_metric_operation(MetricOperation.GET_STATS)


def _execute_record_operation_metric_implementation(operation_name: str, success: bool = True, duration_ms: float = 0, error_type: Optional[str] = None, **kwargs) -> bool:
    """
    Execute record operation metric.
    
    FIXED 2025.10.20.03: Changed parameter from 'operation' to 'operation_name'
    to match gateway wrapper signature and avoid parameter conflicts.
    
    UPDATED 2025.10.21.01: Use build_dimensions() helper
    UPDATED 2025.10.21.02: Use record_metric_with_duration() helper
    """
    dimensions = build_dimensions(
        {'operation': operation_name, 'success': str(success)},
        error_type=error_type
    )
    return record_metric_with_duration(
        f'operation.{operation_name}.count',
        dimensions,
        duration_ms=duration_ms if duration_ms > 0 else None
    )


def _execute_record_error_response_metric_implementation(error_type: str, severity: str = 'medium', category: str = 'internal', context: Optional[Dict] = None, **kwargs) -> bool:
    """
    Execute record error response metric.
    
    UPDATED 2025.10.21.01: Use build_dimensions() helper
    """
    from metrics_core import _MANAGER
    dimensions = build_dimensions(
        {'error_type': error_type, 'severity': severity, 'category': category}
    )
    _MANAGER.record_metric('error.response.count', 1.0, dimensions)
    return True


def _execute_record_cache_metric_implementation(operation_name: str, hit: bool = False, miss: bool = False, eviction: bool = False, duration_ms: float = 0, **kwargs) -> bool:
    """
    Execute record cache metric.
    
    FIXED 2025.10.20.03: Changed parameter from 'operation' to 'operation_name'
    to match gateway wrapper signature and avoid parameter conflicts.
    
    UPDATED 2025.10.21.01: Use build_dimensions() helper for conditional dimensions
    
    Args:
        operation_name: Name of cache operation (e.g., 'get', 'set')
        hit: Whether operation resulted in cache hit
        miss: Whether operation resulted in cache miss
        eviction: Whether operation caused eviction
        duration_ms: Operation duration in milliseconds
        **kwargs: Additional parameters (ignored)
        
    Returns:
        True if metric recorded successfully
    """
    from metrics_core import _MANAGER
    base_dimensions = {'operation': operation_name}
    
    if hit:
        dimensions = build_dimensions(base_dimensions, result='hit')
        _MANAGER.record_metric('cache.hit', 1.0, dimensions)
    if miss:
        dimensions = build_dimensions(base_dimensions, result='miss')
        _MANAGER.record_metric('cache.miss', 1.0, dimensions)
    if eviction:
        _MANAGER.record_metric('cache.eviction', 1.0, base_dimensions)
    if duration_ms > 0:
        _MANAGER.record_metric('cache.duration_ms', duration_ms, base_dimensions)
    return True


def _execute_record_api_metric_implementation(api: str, method: str = 'GET', status_code: int = 200, duration_ms: float = 0, **kwargs) -> bool:
    """
    Execute record API metric.
    
    UPDATED 2025.10.21.01: Use build_dimensions() helper
    UPDATED 2025.10.21.02: Use record_metric_with_duration() helper
    """
    dimensions = build_dimensions(
        {'api': api, 'method': method, 'status': str(status_code)}
    )
    return record_metric_with_duration(
        'api.request',
        dimensions,
        duration_ms=duration_ms if duration_ms > 0 else None
    )


def _execute_record_response_metric_implementation(response_type: ResponseType, status_code: int, duration_ms: float = 0, **kwargs) -> bool:
    """Execute record response metric."""
    from metrics_core import _MANAGER
    _MANAGER.record_response_metric(response_type, status_code, duration_ms)
    return True


def _execute_record_http_metric_implementation(method: str, url: str, status_code: int, duration_ms: float, response_size: Optional[int] = None, **kwargs) -> bool:
    """Execute record HTTP metric."""
    from metrics_core import _MANAGER
    _MANAGER.record_http_metric(method, url, status_code, duration_ms, response_size)
    return True


def _execute_record_circuit_breaker_metric_implementation(circuit_name: str, event_type: str, success: bool = True, **kwargs) -> bool:
    """Execute record circuit breaker metric."""
    from metrics_core import _MANAGER
    _MANAGER.record_circuit_breaker_event(circuit_name, event_type, success)
    return True


def _execute_get_response_metrics_implementation(**kwargs) -> Dict[str, Any]:
    """Execute get response metrics operation."""
    from metrics_core import _MANAGER
    return _MANAGER.get_response_metrics()


def _execute_get_http_metrics_implementation(**kwargs) -> Dict[str, Any]:
    """Execute get HTTP metrics operation."""
    from metrics_core import _MANAGER
    return _MANAGER.get_http_metrics()


def _execute_get_circuit_breaker_metrics_implementation(circuit_name: Optional[str] = None, **kwargs) -> Dict[str, Any]:
    """Execute get circuit breaker metrics operation."""
    from metrics_core import _MANAGER
    return _MANAGER.get_circuit_breaker_metrics(circuit_name)


def _execute_record_dispatcher_timing_implementation(interface_name: str, operation_name: str, duration_ms: float, **kwargs) -> bool:
    """Execute record dispatcher timing operation."""
    from metrics_core import _MANAGER
    return _MANAGER.record_dispatcher_timing(interface_name, operation_name, duration_ms)


def _execute_get_dispatcher_stats_implementation(**kwargs) -> Dict[str, Any]:
    """Execute get dispatcher stats operation."""
    from metrics_core import _MANAGER
    return _MANAGER.get_dispatcher_stats()


def _execute_get_operation_metrics_implementation(**kwargs) -> Dict[str, Any]:
    """Execute get operation metrics operation."""
    from metrics_core import _MANAGER
    return _MANAGER.get_operation_metrics()

def _execute_reset_metrics_implementation(**kwargs) -> bool:
    """
    Execute reset metrics operation.
    
    Resets all metrics to initial state. Useful for testing and debugging.
    
    Returns:
        bool: True if reset successful
        
    Example:
        result = _execute_reset_metrics_implementation()
        # All metrics cleared
    """
    from metrics_core import _MANAGER
    return _MANAGER.reset_metrics()

# ===== HELPER FUNCTIONS =====

def execute_metrics_operation(operation: MetricOperation, **kwargs) -> Any:
    """Execute metrics operation via MetricsCore."""
    from metrics_core import _MANAGER
    return _MANAGER.execute_metric_operation(operation, **kwargs)


def get_metrics_summary() -> Dict[str, Any]:
    """Get comprehensive metrics summary."""
    from metrics_core import _MANAGER
    return {
        'stats': _MANAGER.get_stats(),
        'response_metrics': _MANAGER.get_response_metrics(),
        'http_metrics': _MANAGER.get_http_metrics(),
        'circuit_breaker_metrics': _MANAGER.get_circuit_breaker_metrics(),
        'dispatcher_stats': _MANAGER.get_dispatcher_stats()
    }


__all__ = [
    '_execute_record_metric_implementation',
    '_execute_increment_counter_implementation',
    '_execute_get_stats_implementation',
    '_execute_record_operation_metric_implementation',
    '_execute_record_error_response_metric_implementation',
    '_execute_record_cache_metric_implementation',
    '_execute_record_api_metric_implementation',
    '_execute_record_response_metric_implementation',
    '_execute_record_http_metric_implementation',
    '_execute_record_circuit_breaker_metric_implementation',
    '_execute_get_response_metrics_implementation',
    '_execute_get_http_metrics_implementation',
    '_execute_get_circuit_breaker_metrics_implementation',
    '_execute_record_dispatcher_timing_implementation',
    '_execute_get_dispatcher_stats_implementation',
    '_execute_get_operation_metrics_implementation',
    '_execute_reset_metrics_implementation',
    'execute_metrics_operation',
    'get_metrics_summary',
]

# EOF
