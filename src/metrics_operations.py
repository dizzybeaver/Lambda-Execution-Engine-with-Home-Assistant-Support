"""
metrics_operations.py - Gateway implementation functions for metrics
Version: 2025.11.29.01
Description: FIXED missing function export causing circular import failure

CHANGELOG:
- 2025.11.29.01: BUG FIX - Missing export in __all__
  - FIXED: Added _execute_get_performance_report_implementation to __all__
  - CAUSE: Function existed but wasn't exported, causing ImportError
  - ERROR: "cannot import name '_execute_get_performance_report_implementation'"
  - IMPACT: Metrics interface failed to initialize, breaking all metrics calls
  
- 2025.10.26.01: PHASE 5 EXTRACTION - Performance reporting moved from ha_core.py
  - ADDED: _execute_get_performance_report_implementation()
  - ADDED: _calculate_percentiles() - Statistical helper for performance analysis
  - ADDED: _generate_performance_recommendations() - Intelligent recommendation engine

Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Dict, Any, Optional, List

from metrics_types import MetricOperation, ResponseType

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
    from metrics_helper import build_dimensions, record_metric_with_duration
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
    from metrics_helper import build_dimensions
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
    
    UPDATED 2025.10.21.01: Use build_dimensions() helper
    """
    from metrics_core import _MANAGER
    from metrics_helper import build_dimensions
    dimensions = build_dimensions(
        {'operation': operation_name, 'hit': str(hit), 'miss': str(miss)}
    )
    _MANAGER.record_metric(f'cache.{operation_name}.count', 1.0, dimensions)
    if duration_ms > 0:
        _MANAGER.record_metric(f'cache.{operation_name}.duration_ms', duration_ms, dimensions)
    return True


def _execute_record_api_metric_implementation(api_name: str, endpoint: str, success: bool = True, duration_ms: float = 0, status_code: Optional[int] = None, **kwargs) -> bool:
    """
    Execute record API metric.
    
    UPDATED 2025.10.21.01: Use build_dimensions() helper
    UPDATED 2025.10.21.02: Use record_metric_with_duration() helper
    """
    from metrics_helper import build_dimensions, record_metric_with_duration
    dimensions = build_dimensions(
        {'api': api_name, 'endpoint': endpoint, 'success': str(success)},
        status_code=status_code
    )
    return record_metric_with_duration(
        f'api.{api_name}.count',
        dimensions,
        duration_ms=duration_ms if duration_ms > 0 else None
    )


def _execute_record_response_metric_implementation(response_type: str, success: bool = True, error_type: Optional[str] = None, **kwargs) -> bool:
    """Execute record response metric."""
    from metrics_core import _MANAGER
    dimensions = {'response_type': response_type, 'success': str(success)}
    if error_type:
        dimensions['error_type'] = error_type
    _MANAGER.record_metric('response.count', 1.0, dimensions)
    return True


def _execute_record_http_metric_implementation(method: str, url: str, status_code: int, duration_ms: float, response_size: int = 0, **kwargs) -> bool:
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


def _execute_get_performance_report_implementation(slow_threshold_ms: float = 100.0, **kwargs) -> Dict[str, Any]:
    """
    Execute get performance report operation.
    
    ADDED 2025.10.26.01: Extracted from ha_core.py to make available system-wide
    
    Generates comprehensive performance analysis including:
    - Operation timing statistics (count, avg, p50, p95, p99)
    - Cache efficiency metrics
    - Slow operation identification
    - Intelligent performance recommendations
    
    Args:
        slow_threshold_ms: Threshold in milliseconds to identify slow operations (default: 100.0)
        **kwargs: Additional parameters (reserved for future use)
        
    Returns:
        Dict containing:
        - timestamp: Report generation time
        - metrics_version: Metrics system version
        - slow_threshold_ms: Threshold used
        - operations: Dict of operation statistics
        - cache_efficiency: Cache hit/miss/eviction stats
        - slow_operations: List of operations exceeding threshold
        - slow_operation_count: Count of slow operations
        - cache_stats: Cache configuration and state
        - recommendations: List of actionable performance improvements
        
    Example:
        report = _execute_get_performance_report_implementation(slow_threshold_ms=150.0)
        print(f"Found {report['slow_operation_count']} slow operations")
        for rec in report['recommendations']:
            print(f"- {rec}")
    """
    from metrics_core import _MANAGER
    from datetime import datetime
    
    try:
        # Get all operation metrics
        operation_metrics = _MANAGER.get_operation_metrics()
        
        # Calculate percentiles for each operation
        operations = {}
        for op_name, metrics in operation_metrics.items():
            if metrics['count'] > 0:
                operations[op_name] = {
                    'count': metrics['count'],
                    'avg_ms': metrics['total_ms'] / metrics['count'],
                    'p50_ms': _calculate_percentiles(metrics.get('durations', []), [50])[50],
                    'p95_ms': _calculate_percentiles(metrics.get('durations', []), [95])[95],
                    'p99_ms': _calculate_percentiles(metrics.get('durations', []), [99])[99],
                }
        
        # Get cache efficiency
        cache_stats = _MANAGER.get_stats()
        cache_info = cache_stats.get('cache_info', {})
        cache_efficiency = {
            'hits': cache_info.get('hits', 0),
            'misses': cache_info.get('misses', 0),
            'evictions': cache_info.get('evictions', 0),
            'hit_rate': cache_info.get('hit_rate', 0.0)
        }
        
        # Identify slow operations
        slow_operations_list = [
            {'operation': op, 'avg_ms': stats['avg_ms'], 'p95_ms': stats['p95_ms']}
            for op, stats in operations.items()
            if stats['avg_ms'] > slow_threshold_ms
        ]
        
        slow_operations_sorted = sorted(
            slow_operations_list,
            key=lambda x: x['p95_ms'], 
            reverse=True
        )[:5]
        
        # Generate intelligent recommendations
        recommendations = _generate_performance_recommendations(
            operations, 
            cache_efficiency, 
            slow_operations_sorted,
            slow_threshold_ms
        )
        
        # Build comprehensive report
        report = {
            'timestamp': datetime.utcnow().isoformat(),
            'metrics_version': '2025.10.26.PHASE5',
            'slow_threshold_ms': slow_threshold_ms,
            'operations': operations,
            'cache_efficiency': cache_efficiency,
            'slow_operations': slow_operations_sorted,
            'slow_operation_count': len(slow_operations_list),
            'cache_stats': cache_info,
            'recommendations': recommendations
        }
        
        return report
        
    except Exception as e:
        from logging_manager import log_error
        log_error(f"Performance report generation failed: {str(e)}")
        return {
            'error': str(e),
            'error_type': 'REPORT_GENERATION_FAILED'
        }


# ===== HELPER FUNCTIONS =====

def _calculate_percentiles(durations: List[float], percentiles: List[int]) -> Dict[int, float]:
    """
    Calculate percentiles from duration list.
    
    Args:
        durations: List of duration values in milliseconds
        percentiles: List of percentile values to calculate (e.g., [50, 95, 99])
        
    Returns:
        Dict mapping percentile to calculated value
        
    Example:
        durations = [10, 20, 30, 40, 50]
        result = _calculate_percentiles(durations, [50, 95])
        # Returns: {50: 30.0, 95: 49.0}
    """
    if not durations:
        return {p: 0.0 for p in percentiles}
    
    sorted_durations = sorted(durations)
    result = {}
    
    for p in percentiles:
        index = int(len(sorted_durations) * p / 100)
        index = min(index, len(sorted_durations) - 1)
        result[p] = sorted_durations[index]
    
    return result


def _generate_performance_recommendations(
    operations: Dict[str, Dict],
    cache_efficiency: Dict[str, Any],
    slow_operations: List[Dict],
    slow_threshold_ms: float
) -> List[str]:
    """
    Generate intelligent performance recommendations.
    
    Args:
        operations: Dict of operation statistics
        cache_efficiency: Cache hit/miss statistics
        slow_operations: List of slow operations
        slow_threshold_ms: Threshold for slow operations
        
    Returns:
        List of actionable recommendation strings
        
    Example:
        recommendations = _generate_performance_recommendations(ops, cache, slow, 100)
        # Returns: ["Consider caching results for operation X", ...]
    """
    recommendations = []
    
    # Cache recommendations
    hit_rate = cache_efficiency.get('hit_rate', 0.0)
    if hit_rate < 0.5:
        recommendations.append(
            f"Cache hit rate is {hit_rate:.1%}. Consider reviewing cache TTL settings."
        )
    
    # Slow operation recommendations
    for slow_op in slow_operations[:3]:  # Top 3 slowest
        op_name = slow_op['operation']
        avg_ms = slow_op['avg_ms']
        recommendations.append(
            f"Operation '{op_name}' averages {avg_ms:.1f}ms. "
            f"Consider optimization or caching."
        )
    
    # Operation count recommendations
    total_ops = sum(op['count'] for op in operations.values())
    if total_ops > 10000:
        recommendations.append(
            f"High operation count ({total_ops}). Consider connection pooling."
        )
    
    return recommendations


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


# FIXED 2025.11.29.01: Added missing function to __all__
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
    '_execute_get_performance_report_implementation',  # FIXED: Added missing export
    'execute_metrics_operation',
    'get_metrics_summary',
]

# EOF
