"""
gateway_wrappers_metrics.py - METRICS Interface Wrappers
Version: 2025.10.26.01
Description: Convenience wrappers for METRICS interface operations

CHANGELOG:
- 2025.10.26.01: PHASE 5 EXTRACTION - Added performance reporting wrapper
  - ADDED: get_performance_report() - System-wide performance analysis
  - Makes performance reporting available across entire Lambda via INT-04
  - Extracted from ha_core.py to eliminate duplication

Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any, Dict
from gateway_core import GatewayInterface, execute_operation


def record_metric(name: str, value: float, **kwargs) -> None:
    """Record metric."""
    execute_operation(GatewayInterface.METRICS, 'record', name=name, value=value, **kwargs)


def increment_counter(name: str, value: int = 1, **kwargs) -> None:
    """Increment counter."""
    execute_operation(GatewayInterface.METRICS, 'increment', name=name, value=value, **kwargs)


def get_metrics_stats() -> Dict[str, Any]:
    """Get metrics statistics."""
    return execute_operation(GatewayInterface.METRICS, 'get_stats')


def record_operation_metric(operation_name: str, duration_ms: float, success: bool = True, **kwargs) -> None:
    """
    Record operation metric.
    
    FIXED 2025.10.20.02: Renamed 'operation' to 'operation_name' to avoid conflict
    with execute_operation() positional parameter.
    
    Args:
        operation_name: Name of operation being recorded
        duration_ms: Operation duration in milliseconds
        success: Whether operation succeeded (default: True)
        **kwargs: Additional metric dimensions
    """
    execute_operation(GatewayInterface.METRICS, 'record_operation', operation_name=operation_name, duration_ms=duration_ms, success=success, **kwargs)


def record_error_metric(error_type: str, **kwargs) -> None:
    """Record error metric."""
    execute_operation(GatewayInterface.METRICS, 'record_error', error_type=error_type, **kwargs)


def record_cache_metric(operation_name: str, hit: bool, **kwargs) -> None:
    """
    Record cache metric.
    
    FIXED 2025.10.20.02: Renamed 'operation' to 'operation_name' to avoid conflict
    with execute_operation() positional parameter.
    
    Args:
        operation_name: Name of cache operation (e.g. 'get', 'set')
        hit: Whether cache operation was a hit (True) or miss (False)
        **kwargs: Additional metric dimensions
    """
    execute_operation(GatewayInterface.METRICS, 'record_cache', operation_name=operation_name, hit=hit, **kwargs)


def record_api_metric(endpoint: str, method: str, status_code: int, duration_ms: float, **kwargs) -> None:
    """Record API metric."""
    execute_operation(GatewayInterface.METRICS, 'record_api', endpoint=endpoint, method=method, status_code=status_code, duration_ms=duration_ms, **kwargs)


# ADDED Phase 5: Performance reporting wrapper
def get_performance_report(slow_threshold_ms: float = 1000, **kwargs) -> Dict[str, Any]:
    """
    Get comprehensive performance report with analysis and recommendations.
    
    ADDED Phase 5: Extracted from ha_core.py - now available system-wide via INT-04 (METRICS).
    
    Analyzes metrics data to provide:
    - Operation timing with percentiles (p50, p95, p99)
    - Cache efficiency analysis
    - Slow operation detection
    - Intelligent performance recommendations
    
    Args:
        slow_threshold_ms: Threshold for slow operation detection (default: 1000ms)
        **kwargs: Additional parameters for future extensibility
        
    Returns:
        Dict with comprehensive performance report:
        {
            'timestamp': float,
            'metrics_version': str,
            'slow_threshold_ms': float,
            'operations': {op_name: {avg_ms, min_ms, max_ms, p50_ms, p95_ms, p99_ms}},
            'cache_efficiency': {hit_rate_percent, efficiency_score, ...},
            'slow_operations': [{operation, p95_ms, max_ms}, ...],
            'recommendations': [str, ...]
        }
        
    Example:
        >>> report = get_performance_report()
        >>> print(report['cache_efficiency']['hit_rate_percent'])
        82.5
        >>> for rec in report['recommendations']:
        ...     print(f"âš¡ {rec}")
    """
    return execute_operation(GatewayInterface.METRICS, 'get_performance_report', 
                           slow_threshold_ms=slow_threshold_ms, **kwargs)


__all__ = [
    'record_metric',
    'increment_counter',
    'get_metrics_stats',
    'record_operation_metric',
    'record_error_metric',
    'record_cache_metric',
    'record_api_metric',
    'get_performance_report',  # ADDED Phase 5
]
