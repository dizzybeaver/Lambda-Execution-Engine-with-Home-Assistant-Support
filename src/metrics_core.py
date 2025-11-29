"""
metrics_operations.py - Gateway implementation functions for metrics
Version: 2025.10.26.01
Description: ADDED performance reporting and analysis functions (Phase 5 extraction from ha_core.py)

CHANGELOG:
- 2025.10.26.01: PHASE 5 EXTRACTION - Performance reporting moved from ha_core.py
  - ADDED: _execute_get_performance_report_implementation()
  - ADDED: _calculate_percentiles() - Statistical helper for performance analysis
  - ADDED: _generate_performance_recommendations() - Intelligent recommendation engine
  - BENEFIT: Makes performance reporting available system-wide (not just HA)
  - SUGA-COMPLIANT: Proper 3-layer pattern (gateway → interface → core)
- 2025.10.20.03: BUG FIX - Parameter name mismatch
  - FIXED: _execute_record_cache_metric_implementation() signature
  - Changed: operation: str → operation_name: str
  - Reason: Gateway wrapper sends operation_name, not operation
  - This fixes CloudWatch error: "missing 1 required positional argument: 'operation'"

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
    """
    from metrics_core import _MANAGER
    dimensions = {'operation': operation_name, 'success': str(success)}
    if error_type:
        dimensions['error_type'] = error_type
    _MANAGER.record_metric(f'operation.{operation_name}.count', 1.0, dimensions)
    if duration_ms > 0:
        _MANAGER.record_metric(f'operation.{operation_name}.duration_ms', duration_ms, dimensions)
    return True


def _execute_record_error_response_metric_implementation(error_type: str, severity: str = 'medium', category: str = 'internal', context: Optional[Dict] = None, **kwargs) -> bool:
    """Execute record error response metric."""
    from metrics_core import _MANAGER
    dimensions = {'error_type': error_type, 'severity': severity, 'category': category}
    _MANAGER.record_metric('error.response.count', 1.0, dimensions)
    return True


def _execute_record_cache_metric_implementation(operation_name: str, hit: bool = False, miss: bool = False, eviction: bool = False, duration_ms: float = 0, **kwargs) -> bool:
    """
    Execute record cache metric.
    
    FIXED 2025.10.20.03: Changed parameter from 'operation' to 'operation_name'
    to match gateway wrapper signature and avoid parameter conflicts.
    
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
    dimensions = {'operation': operation_name}
    if hit:
        dimensions['result'] = 'hit'
        _MANAGER.record_metric('cache.hit', 1.0, dimensions)
    if miss:
        dimensions['result'] = 'miss'
        _MANAGER.record_metric('cache.miss', 1.0, dimensions)
    if eviction:
        _MANAGER.record_metric('cache.eviction', 1.0, dimensions)
    if duration_ms > 0:
        _MANAGER.record_metric('cache.duration_ms', duration_ms, dimensions)
    return True


def _execute_record_api_metric_implementation(api: str, method: str = 'GET', status_code: int = 200, duration_ms: float = 0, **kwargs) -> bool:
    """Execute record API metric."""
    from metrics_core import _MANAGER
    dimensions = {'api': api, 'method': method, 'status': str(status_code)}
    _MANAGER.record_metric('api.request', 1.0, dimensions)
    if duration_ms > 0:
        _MANAGER.record_metric('api.duration_ms', duration_ms, dimensions)
    return True


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


# ===== PHASE 5: PERFORMANCE REPORTING (Extracted from ha_core.py) =====

def _calculate_percentiles(values: List[float], percentiles: List[int]) -> Dict[str, float]:
    """
    ADDED Phase 5: Calculate percentiles from list of values.
    
    EXTRACTED FROM: ha_core.py - Made available system-wide
    
    Args:
        values: List of numeric values
        percentiles: List of percentile values to calculate (e.g., [50, 95, 99])
        
    Returns:
        Dict mapping percentile to value (e.g., {'p50': 123.4, 'p95': 456.7})
        
    Example:
        >>> values = [10, 20, 30, 40, 50]
        >>> _calculate_percentiles(values, [50, 95])
        {'p50': 30, 'p95': 50}
    """
    if not values:
        return {f'p{p}': 0.0 for p in percentiles}
    
    sorted_values = sorted(values)
    result = {}
    
    for p in percentiles:
        index = int(len(sorted_values) * (p / 100.0))
        index = min(index, len(sorted_values) - 1)
        result[f'p{p}'] = sorted_values[index]
    
    return result


def _generate_performance_recommendations(
    operations: Dict[str, Any],
    cache_efficiency: Dict[str, Any],
    slow_ops: List[Dict[str, Any]],
    slow_threshold_ms: float = 1000
) -> List[str]:
    """
    ADDED Phase 5: Generate performance improvement recommendations.
    
    EXTRACTED FROM: ha_core.py - Made available system-wide
    
    Analyzes performance data and generates actionable recommendations
    for optimization based on operation timing, cache efficiency, and
    slow operation detection.
    
    Args:
        operations: Operation timing data from metrics
        cache_efficiency: Cache hit rate data
        slow_ops: List of slow operations
        slow_threshold_ms: Threshold for slow operation detection (default: 1000ms)
        
    Returns:
        List of actionable recommendations for performance improvement
        
    Example:
        >>> ops = {'api_call': {'avg_ms': 500, 'p95_ms': 800}}
        >>> cache = {'hit_rate_percent': 45.2}
        >>> slow = [{'operation': 'db_query', 'p95_ms': 1500}]
        >>> _generate_performance_recommendations(ops, cache, slow)
        ['Low cache hit rate (45.2%). Consider increasing cache TTL...',
         'Operation db_query is slow (p95: 1500ms). Consider optimization...']
    """
    recommendations = []
    
    # Cache efficiency recommendations
    if cache_efficiency:
        hit_rate = cache_efficiency.get('hit_rate_percent', 0)
        if hit_rate < 60:
            recommendations.append(
                f"Low cache hit rate ({hit_rate:.1f}%). Consider increasing cache TTL or "
                "enabling cache warming."
            )
        elif hit_rate > 90:
            recommendations.append(
                f"Excellent cache hit rate ({hit_rate:.1f}%). Current caching strategy is optimal."
            )
    
    # Slow operation recommendations
    if slow_ops:
        for op in slow_ops[:3]:  # Top 3 slowest
            recommendations.append(
                f"Operation '{op['operation']}' is slow (p95: {op['p95_ms']:.0f}ms). "
                f"Consider optimization or caching."
            )
    
    # General recommendations
    if not recommendations:
        recommendations.append("Performance metrics look good. No immediate optimizations needed.")
    
    return recommendations


def _execute_get_performance_report_implementation(
    slow_threshold_ms: float = 1000,
    **kwargs
) -> Dict[str, Any]:
    """
    ADDED Phase 5: Get comprehensive performance report.
    
    EXTRACTED FROM: ha_core.py - Made available system-wide via INT-04 (METRICS)
    
    Builds on existing get_metrics_stats() to provide performance analysis
    including operation timing, cache efficiency, percentile calculation,
    bottleneck identification, and intelligent recommendations.
    
    This is the CRITICAL enhancement that makes performance reporting available
    across the entire Lambda, not just Home Assistant operations.
    
    Args:
        slow_threshold_ms: Threshold for slow operation detection (default: 1000ms)
        **kwargs: Additional parameters (unused, for interface compatibility)
        
    Returns:
        Comprehensive performance report with:
        - timestamp: Report generation time
        - metrics_version: Metrics system version
        - operations: Per-operation timing analysis with percentiles
        - cache_efficiency: Cache hit rates and efficiency scoring
        - slow_operations: Top 5 slowest operations by p95
        - recommendations: Actionable performance improvement suggestions
        
    Example:
        >>> report = _execute_get_performance_report_implementation()
        >>> print(report['cache_efficiency']['hit_rate_percent'])
        82.5
        >>> print(report['recommendations'][0])
        'Excellent cache hit rate (82.5%). Current caching strategy is optimal.'
    """
    try:
        from metrics_core import _MANAGER
        from gateway import cache_stats, get_timestamp, create_success_response, create_error_response, log_error
        
        # Get raw metrics from existing INT-04 interface
        raw_metrics = _MANAGER.get_stats()
        
        # Get cache statistics from existing INT-01 interface
        cache_info = cache_stats()
        
        # Analyze operation metrics (those with '_duration_ms' suffix)
        operations = {}
        slow_operations_list = []
        
        for metric_name, values in raw_metrics.get('metrics', {}).items():
            if '_duration_ms' in metric_name:
                operation = metric_name.replace('_duration_ms', '')
                
                if values:
                    avg_ms = sum(values) / len(values)
                    percentiles = _calculate_percentiles(values, [50, 95, 99])
                    
                    operations[operation] = {
                        'avg_ms': avg_ms,
                        'min_ms': min(values),
                        'max_ms': max(values),
                        'p50_ms': percentiles['p50'],
                        'p95_ms': percentiles['p95'],
                        'p99_ms': percentiles['p99'],
                        'sample_count': len(values)
                    }
                    
                    # Identify slow operations
                    if percentiles['p95'] > slow_threshold_ms:
                        slow_operations_list.append({
                            'operation': operation,
                            'p95_ms': percentiles['p95'],
                            'max_ms': max(values)
                        })
        
        # Calculate cache efficiency
        cache_efficiency = {}
        if cache_info.get('hits', 0) + cache_info.get('misses', 0) > 0:
            total_requests = cache_info['hits'] + cache_info['misses']
            hit_rate = (cache_info['hits'] / total_requests) * 100
            cache_efficiency = {
                'hit_rate_percent': hit_rate,
                'total_hits': cache_info['hits'],
                'total_misses': cache_info['misses'],
                'efficiency_score': 'excellent' if hit_rate > 80 else
                                  'good' if hit_rate > 60 else
                                  'needs_improvement'
            }
        
        # Sort slow operations by p95 (descending) and take top 5
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
            'timestamp': get_timestamp(),
            'metrics_version': '2025.10.26.PHASE5',
            'slow_threshold_ms': slow_threshold_ms,
            'operations': operations,
            'cache_efficiency': cache_efficiency,
            'slow_operations': slow_operations_sorted,
            'slow_operation_count': len(slow_operations_list),
            'cache_stats': cache_info,
            'recommendations': recommendations
        }
        
        return create_success_response('Performance report generated', report)
        
    except Exception as e:
        log_error(f"Performance report generation failed: {str(e)}")
        return create_error_response(str(e), 'REPORT_GENERATION_FAILED')


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
    '_execute_get_performance_report_implementation',  # ADDED Phase 5
    'execute_metrics_operation',
    'get_metrics_summary',
    '_MANAGER',  # FIXED 2025.11.29.02: Export _MANAGER so metrics_operations can import it
]

# EOF
