"""
metrics/metrics_core.py

Version: 2025-12-11_1
Purpose: Core metrics implementation with debug integration
Project: LEE
License: Apache 2.0

MODIFIED: Added debug calls throughout
MODIFIED: Refactored to metrics/ subdirectory
"""

from typing import Dict, Any, Optional
from datetime import datetime
from collections import defaultdict

from metrics.metrics_types import ResponseMetrics, HTTPClientMetrics, CircuitBreakerMetrics


class MetricsCore:
    """Core metrics manager - singleton."""
    
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
        """Record metric value."""
        key = self._build_metric_key(name, dimensions)
        self._metrics[key] = value
        return True
    
    def increment_counter(self, name: str, value: int = 1) -> int:
        """Increment counter."""
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
        self._http_metrics.requests_by_method[method] += 1
        self._http_metrics.requests_by_status[status_code] += 1
        self._http_metrics.total_response_time_ms += duration_ms
        self._http_metrics.avg_response_time_ms = self._http_metrics.total_response_time_ms / self._http_metrics.total_requests
        return True
    
    def record_circuit_breaker_event(self, circuit_name: str, event_type: str, success: bool) -> bool:
        """Record circuit breaker event."""
        if circuit_name not in self._circuit_breaker_metrics:
            self._circuit_breaker_metrics[circuit_name] = CircuitBreakerMetrics(circuit_name=circuit_name)
        metrics = self._circuit_breaker_metrics[circuit_name]
        metrics.total_calls += 1
        if success:
            metrics.successful_calls += 1
        else:
            metrics.failed_calls += 1
        if event_type == 'open':
            metrics.circuit_opens += 1
        elif event_type == 'half_open':
            metrics.half_open_attempts += 1
        return True
    
    def get_response_metrics(self) -> Dict[str, Any]:
        """Get response metrics."""
        return {
            'total_responses': self._response_metrics.total_responses,
            'successful_responses': self._response_metrics.successful_responses,
            'error_responses': self._response_metrics.error_responses,
            'success_rate': self._response_metrics.success_rate()
        }
    
    def get_http_metrics(self) -> Dict[str, Any]:
        """Get HTTP metrics."""
        return {
            'total_requests': self._http_metrics.total_requests,
            'successful_requests': self._http_metrics.successful_requests,
            'failed_requests': self._http_metrics.failed_requests,
            'avg_response_time_ms': self._http_metrics.avg_response_time_ms,
            'requests_by_method': dict(self._http_metrics.requests_by_method),
            'requests_by_status': dict(self._http_metrics.requests_by_status)
        }
    
    def get_circuit_breaker_metrics(self, circuit_name: Optional[str] = None) -> Dict[str, Any]:
        """Get circuit breaker metrics."""
        if circuit_name:
            if circuit_name in self._circuit_breaker_metrics:
                metrics = self._circuit_breaker_metrics[circuit_name]
                return {
                    'circuit_name': metrics.circuit_name,
                    'total_calls': metrics.total_calls,
                    'successful_calls': metrics.successful_calls,
                    'failed_calls': metrics.failed_calls,
                    'circuit_opens': metrics.circuit_opens,
                    'half_open_attempts': metrics.half_open_attempts
                }
            return {}
        return {name: self.get_circuit_breaker_metrics(name) for name in self._circuit_breaker_metrics.keys()}
    
    def record_dispatcher_timing(self, interface_name: str, operation_name: str, duration_ms: float) -> bool:
        """Record dispatcher timing."""
        key = f"{interface_name}.{operation_name}"
        self._dispatcher_timings[key].append(duration_ms)
        self._dispatcher_call_counts[key] += 1
        return True
    
    def get_dispatcher_stats(self) -> Dict[str, Any]:
        """Get dispatcher stats."""
        stats = {}
        for key, timings in self._dispatcher_timings.items():
            if timings:
                stats[key] = {
                    'count': self._dispatcher_call_counts[key],
                    'avg_ms': sum(timings) / len(timings),
                    'min_ms': min(timings),
                    'max_ms': max(timings)
                }
        return stats
    
    def get_operation_metrics(self) -> Dict[str, Any]:
        """Get operation metrics."""
        return {op: {
            'count': data['count'],
            'avg_ms': data['total_ms'] / data['count'] if data['count'] > 0 else 0,
            'total_ms': data['total_ms']
        } for op, data in self._operation_metrics.items()}
    
    def get_performance_report(self, slow_threshold_ms: float = 100.0) -> Dict[str, Any]:
        """Get performance report."""
        from metrics.metrics_helper import calculate_percentiles
        operations = {}
        for op, data in self._operation_metrics.items():
            if data['durations']:
                percentiles = calculate_percentiles(data['durations'])
                operations[op] = {
                    'count': data['count'],
                    'avg_ms': data['total_ms'] / data['count'],
                    'min_ms': min(data['durations']),
                    'max_ms': max(data['durations']),
                    'p50_ms': percentiles['p50'],
                    'p95_ms': percentiles['p95'],
                    'p99_ms': percentiles['p99']
                }
        slow_operations = [
            {'operation': op, 'p95_ms': metrics['p95_ms'], 'max_ms': metrics['max_ms']}
            for op, metrics in operations.items()
            if metrics['p95_ms'] > slow_threshold_ms
        ]
        return {
            'timestamp': datetime.now().isoformat(),
            'metrics_version': '2025-12-11_1',
            'slow_threshold_ms': slow_threshold_ms,
            'operations': operations,
            'slow_operations': slow_operations,
            'slow_operation_count': len(slow_operations)
        }
    
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
    
    def _build_metric_key(self, name: str, dimensions: Optional[Dict[str, str]]) -> str:
        """Build metric key from name and dimensions."""
        if not dimensions:
            return name
        dim_str = ','.join(f"{k}={v}" for k, v in sorted(dimensions.items()))
        return f"{name}[{dim_str}]"


# SINGLETON instance
_MANAGER = MetricsCore()


# PUBLIC API - Interface layer uses these
def record_metric(name: str, value: float, dimensions: Optional[Dict[str, str]] = None, **kwargs) -> bool:
    return _MANAGER.record_metric(name, value, dimensions)

def increment_counter(name: str, value: int = 1, **kwargs) -> int:
    return _MANAGER.increment_counter(name, value)

def get_stats(**kwargs) -> Dict[str, Any]:
    return _MANAGER.get_stats()

def record_operation_metric(operation_name: str, success: bool = True, duration_ms: float = 0, error_type: Optional[str] = None, **kwargs) -> bool:
    return _MANAGER.record_operation_metric(operation_name, success, duration_ms, error_type)

def record_error_response(error_type: str, severity: str = 'medium', category: str = 'internal', **kwargs) -> bool:
    return _MANAGER.record_error_response(error_type, severity, category)

def record_cache_metric(operation_name: str, hit: bool = False, miss: bool = False, duration_ms: float = 0, **kwargs) -> bool:
    return _MANAGER.record_cache_metric(operation_name, hit, miss, duration_ms)

def record_api_metric(api_name: str, endpoint: str, success: bool = True, duration_ms: float = 0, status_code: Optional[int] = None, **kwargs) -> bool:
    return _MANAGER.record_api_metric(api_name, endpoint, success, duration_ms, status_code)

def record_response_metric(response_type: str, success: bool = True, error_type: Optional[str] = None, **kwargs) -> bool:
    return _MANAGER.record_response_metric(response_type, success, error_type)

def record_http_metric(method: str, url: str, status_code: int, duration_ms: float, response_size: int = 0, **kwargs) -> bool:
    return _MANAGER.record_http_metric(method, url, status_code, duration_ms, response_size)

def record_circuit_breaker_event(circuit_name: str, event_type: str, success: bool = True, **kwargs) -> bool:
    return _MANAGER.record_circuit_breaker_event(circuit_name, event_type, success)

def get_response_metrics(**kwargs) -> Dict[str, Any]:
    return _MANAGER.get_response_metrics()

def get_http_metrics(**kwargs) -> Dict[str, Any]:
    return _MANAGER.get_http_metrics()

def get_circuit_breaker_metrics(circuit_name: Optional[str] = None, **kwargs) -> Dict[str, Any]:
    return _MANAGER.get_circuit_breaker_metrics(circuit_name)

def record_dispatcher_timing(interface_name: str, operation_name: str, duration_ms: float, **kwargs) -> bool:
    return _MANAGER.record_dispatcher_timing(interface_name, operation_name, duration_ms)

def get_dispatcher_stats(**kwargs) -> Dict[str, Any]:
    return _MANAGER.get_dispatcher_stats()

def get_operation_metrics(**kwargs) -> Dict[str, Any]:
    return _MANAGER.get_operation_metrics()

def get_performance_report(slow_threshold_ms: float = 100.0, **kwargs) -> Dict[str, Any]:
    return _MANAGER.get_performance_report(slow_threshold_ms)

def reset_metrics(**kwargs) -> bool:
    return _MANAGER.reset_metrics()
