"""
metrics_core.py - Core metrics collection manager
Version: 2025.10.15.01
Description: MetricsCore class with unified operations and gateway implementation functions

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

import os
import time
import threading
from typing import Dict, Any, Optional, List
from collections import defaultdict

from metrics_types import (
    MetricOperation,
    ResponseType,
    ResponseMetrics,
    HTTPClientMetrics,
    CircuitBreakerMetrics
)
from metrics_helper import calculate_percentile, build_metric_key


# ===== CONFIGURATION =====

_USE_GENERIC_OPERATIONS = os.getenv('USE_GENERIC_OPERATIONS', 'true').lower() == 'true'


# ===== METRICS CORE IMPLEMENTATION =====

class MetricsCore:
    """Singleton metrics manager with unified operations."""
    
    def __init__(self):
        self._lock = threading.Lock()
        self._metrics: Dict[str, List[float]] = defaultdict(list)
        self._counters: Dict[str, int] = defaultdict(int)
        self._gauges: Dict[str, float] = {}
        self._histograms: Dict[str, List[float]] = defaultdict(list)
        self._stats = {
            'total_metrics': 0,
            'unique_metrics': 0,
            'counters': 0,
            'gauges': 0,
            'histograms': 0
        }
        self._response_metrics = ResponseMetrics()
        self._http_metrics = HTTPClientMetrics()
        self._circuit_breaker_metrics: Dict[str, CircuitBreakerMetrics] = {}
        # Phase 4 Task #7: Dispatcher timing storage
        self._dispatcher_timings: Dict[str, List[float]] = defaultdict(list)
        self._dispatcher_call_counts: Dict[str, int] = defaultdict(int)
    
    def execute_metric_operation(self, operation: MetricOperation, *args, **kwargs) -> Any:
        """Universal metric operation executor."""
        start_time = time.time()
        
        if _USE_GENERIC_OPERATIONS:
            result = self._execute_generic_operation(operation, *args, **kwargs)
        else:
            result = self._execute_direct_operation(operation, *args, **kwargs)
        
        duration_ms = (time.time() - start_time) * 1000
        self._record_dispatcher_metric(operation, duration_ms)
        
        return result
    
    def _execute_generic_operation(self, operation: MetricOperation, *args, **kwargs) -> Any:
        """Execute operation using generic dispatcher."""
        operation_map = {
            MetricOperation.RECORD: lambda: self.record_metric(*args, **kwargs),
            MetricOperation.INCREMENT: lambda: self.increment_counter(*args, **kwargs),
            MetricOperation.GAUGE: lambda: self.set_gauge(*args, **kwargs),
            MetricOperation.HISTOGRAM: lambda: self.record_histogram(*args, **kwargs),
            MetricOperation.GET_METRIC: lambda: self.get_metric(*args, **kwargs),
            MetricOperation.GET_STATS: lambda: self.get_stats(),
            MetricOperation.CLEAR: lambda: self.clear_metrics(),
            MetricOperation.RECORD_DISPATCHER_TIMING: lambda: self.record_dispatcher_timing(*args, **kwargs),
            MetricOperation.GET_DISPATCHER_STATS: lambda: self.get_dispatcher_stats(),
            MetricOperation.GET_OPERATION_METRICS: lambda: self.get_operation_metrics(),
        }
        
        handler = operation_map.get(operation)
        if handler:
            return handler()
        return None
    
    def _execute_direct_operation(self, operation: MetricOperation, *args, **kwargs) -> Any:
        """Execute operation directly."""
        return self._execute_generic_operation(operation, *args, **kwargs)
    
    def record_metric(self, name: str, value: float, dimensions: Optional[Dict[str, str]] = None) -> bool:
        """Record a metric value."""
        with self._lock:
            key = build_metric_key(name, dimensions)
            self._metrics[key].append(value)
            self._stats['total_metrics'] += 1
            self._stats['unique_metrics'] = len(self._metrics)
        return True
    
    def increment_counter(self, name: str, value: int = 1) -> int:
        """Increment a counter metric."""
        with self._lock:
            self._counters[name] += value
            self._stats['counters'] = len(self._counters)
            return self._counters[name]
    
    def set_gauge(self, name: str, value: float) -> float:
        """Set a gauge metric."""
        with self._lock:
            self._gauges[name] = value
            self._stats['gauges'] = len(self._gauges)
            return value
    
    def record_histogram(self, name: str, value: float) -> None:
        """Record a histogram value."""
        with self._lock:
            self._histograms[name].append(value)
            self._stats['histograms'] = len(self._histograms)
    
    def get_metric(self, name: str) -> Optional[Dict[str, Any]]:
        """Get metric by name."""
        with self._lock:
            result = {}
            
            if name in self._counters:
                result['counter'] = self._counters[name]
            
            if name in self._gauges:
                result['gauge'] = self._gauges[name]
            
            if name in self._histograms:
                values = self._histograms[name]
                if values:
                    result['histogram'] = {
                        'count': len(values),
                        'sum': sum(values),
                        'avg': sum(values) / len(values),
                        'min': min(values),
                        'max': max(values)
                    }
            
            # Check metrics with any dimensions
            for key in self._metrics:
                if key.startswith(name):
                    values = self._metrics[key]
                    if values:
                        result[key] = {
                            'count': len(values),
                            'sum': sum(values),
                            'avg': sum(values) / len(values),
                            'min': min(values),
                            'max': max(values)
                        }
            
            return result if result else None
    
    def get_stats(self) -> Dict[str, Any]:
        """Get overall metrics statistics."""
        with self._lock:
            return {
                'total_metrics': self._stats['total_metrics'],
                'unique_metrics': self._stats['unique_metrics'],
                'counters': self._stats['counters'],
                'gauges': self._stats['gauges'],
                'histograms': self._stats['histograms'],
                'response_metrics': {
                    'total_responses': self._response_metrics.total_responses,
                    'success_rate': self._response_metrics.success_rate()
                },
                'http_metrics': {
                    'total_requests': self._http_metrics.total_requests,
                    'successful_requests': self._http_metrics.successful_requests
                },
                'circuit_breakers': len(self._circuit_breaker_metrics)
            }
    
    def clear_metrics(self) -> Dict[str, int]:
        """Clear all metrics."""
        with self._lock:
            counts = {
                'metrics_cleared': len(self._metrics),
                'counters_cleared': len(self._counters),
                'gauges_cleared': len(self._gauges),
                'histograms_cleared': len(self._histograms)
            }
            
            self._metrics.clear()
            self._counters.clear()
            self._gauges.clear()
            self._histograms.clear()
            self._stats = {
                'total_metrics': 0,
                'unique_metrics': 0,
                'counters': 0,
                'gauges': 0,
                'histograms': 0
            }
            
            return counts
    
    def _record_dispatcher_metric(self, operation: MetricOperation, duration_ms: float):
        """Record dispatcher performance metric (self-recording)."""
        # Avoid infinite recursion
        if operation != MetricOperation.RECORD_DISPATCHER_TIMING:
            self.record_dispatcher_timing('MetricsCore', operation.value, duration_ms)
    
    # ===== SPECIALIZED METRIC RECORDING =====
    
    def record_response_metric(self, response_type: ResponseType, response_time_ms: float = 0.0) -> None:
        """Record response metrics."""
        with self._lock:
            self._response_metrics.total_responses += 1
            
            if response_type == ResponseType.SUCCESS:
                self._response_metrics.successful_responses += 1
            elif response_type == ResponseType.ERROR:
                self._response_metrics.error_responses += 1
            elif response_type == ResponseType.TIMEOUT:
                self._response_metrics.timeout_responses += 1
            elif response_type == ResponseType.CACHED:
                self._response_metrics.cached_responses += 1
            elif response_type == ResponseType.FALLBACK:
                self._response_metrics.fallback_responses += 1
            
            if response_time_ms > 0:
                if response_time_ms < self._response_metrics.fastest_response_ms:
                    self._response_metrics.fastest_response_ms = response_time_ms
                if response_time_ms > self._response_metrics.slowest_response_ms:
                    self._response_metrics.slowest_response_ms = response_time_ms
                
                total_time = self._response_metrics.avg_response_time_ms * (self._response_metrics.total_responses - 1)
                self._response_metrics.avg_response_time_ms = (total_time + response_time_ms) / self._response_metrics.total_responses
            
            if self._response_metrics.total_responses > 0:
                self._response_metrics.cache_hit_rate = (
                    self._response_metrics.cached_responses / self._response_metrics.total_responses * 100
                )
    
    def record_http_request(self, success: bool, response_time_ms: float = 0.0, 
                          method: Optional[str] = None, status_code: Optional[int] = None) -> None:
        """Record HTTP client metrics."""
        with self._lock:
            self._http_metrics.total_requests += 1
            
            if success:
                self._http_metrics.successful_requests += 1
            else:
                self._http_metrics.failed_requests += 1
            
            if response_time_ms > 0:
                self._http_metrics.total_response_time_ms += response_time_ms
                self._http_metrics.avg_response_time_ms = (
                    self._http_metrics.total_response_time_ms / self._http_metrics.total_requests
                )
            
            if method:
                self._http_metrics.requests_by_method[method] += 1
            
            if status_code:
                self._http_metrics.requests_by_status[status_code] += 1
    
    def record_circuit_breaker_event(self, circuit_name: str, event_type: str, 
                                    success: Optional[bool] = None) -> None:
        """Record circuit breaker event."""
        with self._lock:
            if circuit_name not in self._circuit_breaker_metrics:
                self._circuit_breaker_metrics[circuit_name] = CircuitBreakerMetrics()
            
            cb = self._circuit_breaker_metrics[circuit_name]
            cb.total_requests += 1
            
            if event_type == 'state_change':
                cb.state = str(success) if success is not None else 'unknown'
            elif event_type == 'failure':
                cb.failure_count += 1
                cb.last_failure_time = time.time()
            elif event_type == 'success':
                cb.success_count += 1
    
    def get_response_metrics(self) -> Dict[str, Any]:
        """Get response metrics."""
        with self._lock:
            return {
                'total_responses': self._response_metrics.total_responses,
                'successful_responses': self._response_metrics.successful_responses,
                'error_responses': self._response_metrics.error_responses,
                'timeout_responses': self._response_metrics.timeout_responses,
                'cached_responses': self._response_metrics.cached_responses,
                'fallback_responses': self._response_metrics.fallback_responses,
                'avg_response_time_ms': round(self._response_metrics.avg_response_time_ms, 2),
                'fastest_response_ms': self._response_metrics.fastest_response_ms if self._response_metrics.fastest_response_ms != float('inf') else 0,
                'slowest_response_ms': round(self._response_metrics.slowest_response_ms, 2),
                'cache_hit_rate': round(self._response_metrics.cache_hit_rate, 2),
                'success_rate': round(self._response_metrics.success_rate(), 2)
            }
    
    def get_http_metrics(self) -> Dict[str, Any]:
        """Get HTTP client metrics."""
        with self._lock:
            return {
                'total_requests': self._http_metrics.total_requests,
                'successful_requests': self._http_metrics.successful_requests,
                'failed_requests': self._http_metrics.failed_requests,
                'avg_response_time_ms': round(self._http_metrics.avg_response_time_ms, 2),
                'requests_by_method': dict(self._http_metrics.requests_by_method),
                'requests_by_status': dict(self._http_metrics.requests_by_status)
            }
    
    def get_circuit_breaker_metrics(self, circuit_name: Optional[str] = None) -> Dict[str, Any]:
        """Get circuit breaker metrics."""
        with self._lock:
            if circuit_name:
                if circuit_name in self._circuit_breaker_metrics:
                    cb = self._circuit_breaker_metrics[circuit_name]
                    return {
                        'state': cb.state,
                        'failure_count': cb.failure_count,
                        'success_count': cb.success_count,
                        'last_failure_time': cb.last_failure_time,
                        'total_requests': cb.total_requests
                    }
                return {}
            
            result = {}
            for name, cb in self._circuit_breaker_metrics.items():
                result[name] = {
                    'state': cb.state,
                    'failure_count': cb.failure_count,
                    'success_count': cb.success_count,
                    'last_failure_time': cb.last_failure_time,
                    'total_requests': cb.total_requests
                }
            return result
    
    # ===== DISPATCHER TIMING (PHASE 4 TASK #7) =====
    
    def record_dispatcher_timing(self, interface_name: str, operation_name: str, duration_ms: float) -> bool:
        """Record dispatcher timing metric."""
        with self._lock:
            key = f"{interface_name}.{operation_name}"
            self._dispatcher_timings[key].append(duration_ms)
            self._dispatcher_call_counts[key] += 1
            
            self.record_metric(
                f"dispatcher.{interface_name}.{operation_name}.duration_ms",
                duration_ms,
                {'interface': interface_name, 'operation': operation_name}
            )
        return True
    
    def get_dispatcher_stats(self) -> Dict[str, Any]:
        """Get dispatcher performance statistics."""
        with self._lock:
            stats = {}
            for key, timings in self._dispatcher_timings.items():
                if timings:
                    stats[key] = {
                        'call_count': self._dispatcher_call_counts[key],
                        'total_ms': sum(timings),
                        'avg_ms': sum(timings) / len(timings),
                        'min_ms': min(timings),
                        'max_ms': max(timings),
                        'p95_ms': calculate_percentile(timings, 95),
                        'p99_ms': calculate_percentile(timings, 99)
                    }
            return {'stats': stats, 'total_operations': sum(self._dispatcher_call_counts.values())}
    
    def get_operation_metrics(self) -> Dict[str, Any]:
        """Get operation-level metrics."""
        with self._lock:
            interfaces = defaultdict(lambda: {'operations': {}, 'total_calls': 0})
            for key, count in self._dispatcher_call_counts.items():
                if '.' in key:
                    interface, operation = key.split('.', 1)
                    interfaces[interface]['operations'][operation] = count
                    interfaces[interface]['total_calls'] += count
            
            for interface, data in interfaces.items():
                if interface in ['CacheCore', 'LoggingCore', 'SecurityCore', 'MetricsCore']:
                    all_timings = []
                    for op_key, timing_list in self._dispatcher_timings.items():
                        if op_key.startswith(interface):
                            all_timings.extend(timing_list)
                    
                    if all_timings:
                        data['avg_duration_ms'] = sum(all_timings) / len(all_timings)
                        data['total_duration_ms'] = sum(all_timings)
            
            return dict(interfaces)


# ===== SINGLETON INSTANCE =====

_MANAGER = MetricsCore()


# ===== GATEWAY IMPLEMENTATION FUNCTIONS =====
# Import from metrics_operations.py to make available via metrics_core

from metrics_operations import (
    _execute_record_metric_implementation,
    _execute_increment_counter_implementation,
    _execute_get_stats_implementation,
    _execute_record_operation_metric_implementation,
    _execute_record_error_response_metric_implementation,
    _execute_record_cache_metric_implementation,
    _execute_record_api_metric_implementation,
    _execute_record_response_metric_implementation,
    _execute_record_http_metric_implementation,
    _execute_record_circuit_breaker_metric_implementation,
    _execute_get_response_metrics_implementation,
    _execute_get_http_metrics_implementation,
    _execute_get_circuit_breaker_metrics_implementation,
    _execute_record_dispatcher_timing_implementation,
    _execute_get_dispatcher_stats_implementation,
    _execute_get_operation_metrics_implementation,
    execute_metrics_operation,
    get_metrics_summary,
)


__all__ = [
    'MetricsCore',
    '_MANAGER',
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
    'execute_metrics_operation',
    'get_metrics_summary',
]

# EOF
