"""
metrics_core.py - Core metrics implementation with public API

Version: 2025.11.29.REFACTOR_01
Description: PHASE 1 - Add public API functions for SUGA compliance

CHANGELOG:
- 2025.11.29.REFACTOR_01: Add public API layer
  - ADDED: 18 public wrapper functions (no underscores)
  - PATTERN: Public functions delegate to _MANAGER
  - PURPOSE: Enable interface layer to call public API instead of private _MANAGER
  - NEXT: Phase 2 will rewrite interface_metrics.py to use these

Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from collections import defaultdict

from metrics_types import MetricOperation, ResponseType, ResponseMetrics, HTTPClientMetrics, CircuitBreakerMetrics


# ===== METRICS CORE CLASS (PRIVATE) =====

class MetricsCore:
    """Core metrics manager - singleton implementation."""
    
    def __init__(self):
        self._metrics = defaultdict(float)
        self._counters = defaultdict(int)
        self._gauges = defaultdict(float)
        self._histograms = defaultdict(list)
        self._response_metrics = ResponseMetrics()
        self._http_metrics = HTTPClientMetrics()
        self._circuit_breaker_metrics = {}
        self._dispatcher_timings = defaultdict(list)
        self._dispatcher_call_counts = defaultdict(int)
        self._operation_metrics = defaultdict(lambda: {'count': 0, 'total_ms': 0, 'durations': []})
    
    def record_metric(self, name: str, value: float, dimensions: Optional[Dict[str, str]] = None) -> bool:
        """Record a metric value."""
        key = self._build_metric_key(name, dimensions)
        self._metrics[key] = value
        return True
    
    def increment_counter(self, name: str, value: int = 1) -> int:
        """Increment a counter."""
        self._counters[name] += value
        return self._counters[name]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get all statistics."""
        return {
            'metrics': dict(self._metrics),
            'counters': dict(self._counters),
            'gauges': dict(self._gauges),
            'histograms': {k: list(v) for k, v in self._histograms.items()}
        }
    
    def record_operation_metric(self, operation_name: str, success: bool, duration_ms: float, error_type: Optional[str]) -> bool:
        """Record operation metric."""
        dimensions = {'operation': operation_name, 'success': str(success)}
        if error_type:
            dimensions['error_type'] = error_type
        self.record_metric(f'operation.{operation_name}.count', 1.0, dimensions)
        if duration_ms > 0:
            self.record_metric(f'operation.{operation_name}.duration_ms', duration_ms, dimensions)
            op_key = operation_name
            self._operation_metrics[op_key]['count'] += 1
            self._operation_metrics[op_key]['total_ms'] += duration_ms
            self._operation_metrics[op_key]['durations'].append(duration_ms)
        return True
    
    def record_error_response(self, error_type: str, severity: str, category: str) -> bool:
        """Record error response."""
        dimensions = {'error_type': error_type, 'severity': severity, 'category': category}
        self.record_metric('error.response.count', 1.0, dimensions)
        return True
    
    def record_cache_metric(self, operation_name: str, hit: bool, miss: bool, duration_ms: float) -> bool:
        """Record cache metric."""
        dimensions = {'operation': operation_name, 'hit': str(hit), 'miss': str(miss)}
        self.record_metric(f'cache.{operation_name}.count', 1.0, dimensions)
        if duration_ms > 0:
            self.record_metric(f'cache.{operation_name}.duration_ms', duration_ms, dimensions)
        return True
    
    def record_api_metric(self, api_name: str, endpoint: str, success: bool, duration_ms: float, status_code: Optional[int]) -> bool:
        """Record API metric."""
        dimensions = {'api': api_name, 'endpoint': endpoint, 'success': str(success)}
        if status_code:
            dimensions['status_code'] = str(status_code)
        self.record_metric(f'api.{api_name}.count', 1.0, dimensions)
        if duration_ms > 0:
            self.record_metric(f'api.{api_name}.duration_ms', duration_ms, dimensions)
        return True
    
    def record_response_metric(self, response_type: str, success: bool, error_type: Optional[str]) -> bool:
        """Record response metric."""
        dimensions = {'response_type': response_type, 'success': str(success)}
        if error_type:
            dimensions['error_type'] = error_type
        self.record_metric('response.count', 1.0, dimensions)
        return True
    
    def record_http_metric(self, method: str, url: str, status_code: int, duration_ms: float, response_size: int) -> bool:
        """Record HTTP metric."""
        self._http_metrics.total_requests += 1
        if 200 <= status_code < 300:
            self._http_metrics.successful_requests += 1
        else:
            self._http_metrics.failed_requests += 1
        self._http_metrics.total_response_time_ms += duration_ms
        self._http_metrics.avg_response_time_ms = self._http_metrics.total_response_time_ms / self._http_metrics.total_requests
        self._http_metrics.requests_by_method[method] += 1
        self._http_metrics.requests_by_status[status_code] += 1
        return True
    
    def record_circuit_breaker_event(self, circuit_name: str, event_type: str, success: bool) -> bool:
        """Record circuit breaker event."""
        if circuit_name not in self._circuit_breaker_metrics:
            self._circuit_breaker_metrics[circuit_name] = CircuitBreakerMetrics(name=circuit_name)
        cb = self._circuit_breaker_metrics[circuit_name]
        cb.total_requests += 1
        if success:
            cb.successful_requests += 1
        else:
            cb.failed_requests += 1
        return True
    
    def get_response_metrics(self) -> Dict[str, Any]:
        """Get response metrics."""
        return {
            'total': self._response_metrics.total_responses,
            'successful': self._response_metrics.successful_responses,
            'errors': self._response_metrics.error_responses
        }
    
    def get_http_metrics(self) -> Dict[str, Any]:
        """Get HTTP metrics."""
        return {
            'total_requests': self._http_metrics.total_requests,
            'successful': self._http_metrics.successful_requests,
            'failed': self._http_metrics.failed_requests,
            'avg_response_time_ms': self._http_metrics.avg_response_time_ms
        }
    
    def get_circuit_breaker_metrics(self, circuit_name: Optional[str] = None) -> Dict[str, Any]:
        """Get circuit breaker metrics."""
        if circuit_name:
            return self._circuit_breaker_metrics.get(circuit_name, {})
        return {name: cb for name, cb in self._circuit_breaker_metrics.items()}
    
    def record_dispatcher_timing(self, interface_name: str, operation_name: str, duration_ms: float) -> bool:
        """Record dispatcher timing."""
        key = f"{interface_name}.{operation_name}"
        self._dispatcher_timings[key].append(duration_ms)
        self._dispatcher_call_counts[key] += 1
        return True
    
    def get_dispatcher_stats(self) -> Dict[str, Any]:
        """Get dispatcher statistics."""
        stats = {}
        for key, timings in self._dispatcher_timings.items():
            stats[key] = {
                'count': self._dispatcher_call_counts[key],
                'avg_ms': sum(timings) / len(timings) if timings else 0,
                'min_ms': min(timings) if timings else 0,
                'max_ms': max(timings) if timings else 0
            }
        return stats
    
    def get_operation_metrics(self) -> Dict[str, Any]:
        """Get operation metrics."""
        return dict(self._operation_metrics)
    
    def reset_metrics(self) -> bool:
        """Reset all metrics."""
        self._metrics.clear()
        self._counters.clear()
        self._gauges.clear()
        self._histograms.clear()
        self._response_metrics = ResponseMetrics()
        self._http_metrics = HTTPClientMetrics()
        self._circuit_breaker_metrics.clear()
        self._dispatcher_timings.clear()
        self._dispatcher_call_counts.clear()
        self._operation_metrics.clear()
        return True
    
    def get_performance_report(self, slow_threshold_ms: float = 100.0) -> Dict[str, Any]:
        """Generate performance report."""
        operations = {}
        for op_name, metrics in self._operation_metrics.items():
            if metrics['count'] > 0:
                durations = metrics['durations']
                sorted_durations = sorted(durations)
                operations[op_name] = {
                    'count': metrics['count'],
                    'avg_ms': metrics['total_ms'] / metrics['count'],
                    'p50_ms': sorted_durations[len(sorted_durations) // 2] if sorted_durations else 0,
                    'p95_ms': sorted_durations[int(len(sorted_durations) * 0.95)] if sorted_durations else 0,
                    'p99_ms': sorted_durations[int(len(sorted_durations) * 0.99)] if sorted_durations else 0,
                }
        
        slow_ops = [
            {'operation': op, 'avg_ms': stats['avg_ms'], 'p95_ms': stats['p95_ms']}
            for op, stats in operations.items()
            if stats['avg_ms'] > slow_threshold_ms
        ]
        slow_ops.sort(key=lambda x: x['p95_ms'], reverse=True)
        
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'slow_threshold_ms': slow_threshold_ms,
            'operations': operations,
            'slow_operations': slow_ops[:5],
            'slow_operation_count': len(slow_ops)
        }
    
    def _build_metric_key(self, name: str, dimensions: Optional[Dict[str, str]]) -> str:
        """Build metric key from name and dimensions."""
        if not dimensions:
            return name
        dim_str = ','.join(f"{k}={v}" for k, v in sorted(dimensions.items()))
        return f"{name}[{dim_str}]"


# ===== SINGLETON INSTANCE (PRIVATE) =====

_MANAGER = MetricsCore()


# ===== PUBLIC API FUNCTIONS =====

def record_metric(name: str, value: float, dimensions: Optional[Dict[str, str]] = None) -> bool:
    """Record a metric value."""
    return _MANAGER.record_metric(name, value, dimensions)

def increment_counter(name: str, value: int = 1) -> int:
    """Increment a counter metric."""
    return _MANAGER.increment_counter(name, value)

def get_stats() -> Dict[str, Any]:
    """Get all metrics statistics."""
    return _MANAGER.get_stats()

def record_operation_metric(operation_name: str, success: bool = True, duration_ms: float = 0, error_type: Optional[str] = None) -> bool:
    """Record operation metric with timing."""
    return _MANAGER.record_operation_metric(operation_name, success, duration_ms, error_type)

def record_error_response(error_type: str, severity: str = 'medium', category: str = 'internal') -> bool:
    """Record error response metric."""
    return _MANAGER.record_error_response(error_type, severity, category)

def record_cache_metric(operation_name: str, hit: bool = False, miss: bool = False, duration_ms: float = 0) -> bool:
    """Record cache operation metric."""
    return _MANAGER.record_cache_metric(operation_name, hit, miss, duration_ms)

def record_api_metric(api_name: str, endpoint: str, success: bool = True, duration_ms: float = 0, status_code: Optional[int] = None) -> bool:
    """Record API call metric."""
    return _MANAGER.record_api_metric(api_name, endpoint, success, duration_ms, status_code)

def record_response_metric(response_type: str, success: bool = True, error_type: Optional[str] = None) -> bool:
    """Record response metric."""
    return _MANAGER.record_response_metric(response_type, success, error_type)

def record_http_metric(method: str, url: str, status_code: int, duration_ms: float, response_size: int = 0) -> bool:
    """Record HTTP request metric."""
    return _MANAGER.record_http_metric(method, url, status_code, duration_ms, response_size)

def record_circuit_breaker_event(circuit_name: str, event_type: str, success: bool = True) -> bool:
    """Record circuit breaker event."""
    return _MANAGER.record_circuit_breaker_event(circuit_name, event_type, success)

def get_response_metrics() -> Dict[str, Any]:
    """Get response metrics."""
    return _MANAGER.get_response_metrics()

def get_http_metrics() -> Dict[str, Any]:
    """Get HTTP metrics."""
    return _MANAGER.get_http_metrics()

def get_circuit_breaker_metrics(circuit_name: Optional[str] = None) -> Dict[str, Any]:
    """Get circuit breaker metrics."""
    return _MANAGER.get_circuit_breaker_metrics(circuit_name)

def record_dispatcher_timing(interface_name: str, operation_name: str, duration_ms: float) -> bool:
    """Record dispatcher timing."""
    return _MANAGER.record_dispatcher_timing(interface_name, operation_name, duration_ms)

def get_dispatcher_stats() -> Dict[str, Any]:
    """Get dispatcher statistics."""
    return _MANAGER.get_dispatcher_stats()

def get_operation_metrics() -> Dict[str, Any]:
    """Get operation metrics."""
    return _MANAGER.get_operation_metrics()

def reset_metrics() -> bool:
    """Reset all metrics."""
    return _MANAGER.reset_metrics()

def get_performance_report(slow_threshold_ms: float = 100.0) -> Dict[str, Any]:
    """Generate performance report."""
    return _MANAGER.get_performance_report(slow_threshold_ms)


# ===== EXPORTS =====

__all__ = [
    'MetricsCore',
    '_MANAGER',
    'record_metric',
    'increment_counter',
    'get_stats',
    'record_operation_metric',
    'record_error_response',
    'record_cache_metric',
    'record_api_metric',
    'record_response_metric',
    'record_http_metric',
    'record_circuit_breaker_event',
    'get_response_metrics',
    'get_http_metrics',
    'get_circuit_breaker_metrics',
    'record_dispatcher_timing',
    'get_dispatcher_stats',
    'get_operation_metrics',
    'reset_metrics',
    'get_performance_report',
]

# EOF
