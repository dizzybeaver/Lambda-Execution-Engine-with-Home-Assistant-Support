"""
metrics_core.py - Unified metrics collection with dispatcher timing operations
Version: 2025.10.15.02
Description: Complete metrics with dispatcher timing operations (Phase 4 Task #7)

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
from enum import Enum
from collections import defaultdict, deque
from dataclasses import dataclass, field


# ===== CONFIGURATION =====

_USE_GENERIC_OPERATIONS = os.getenv('USE_GENERIC_OPERATIONS', 'true').lower() == 'true'


# ===== ENUMERATIONS =====

class MetricOperation(Enum):
    """Generic metric operations."""
    RECORD = "record"
    INCREMENT = "increment"
    DECREMENT = "decrement"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    GET_METRIC = "get_metric"
    GET_STATS = "get_stats"
    CLEAR = "clear"
    # Phase 4 Task #7: Dispatcher timing operations
    RECORD_DISPATCHER_TIMING = "record_dispatcher_timing"
    GET_DISPATCHER_STATS = "get_dispatcher_stats"
    GET_OPERATION_METRICS = "get_operation_metrics"


class MetricType(Enum):
    """Metric types."""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"


class ResponseType(Enum):
    """Response types for tracking."""
    SUCCESS = "success"
    ERROR = "error"
    TIMEOUT = "timeout"
    CACHED = "cached"
    FALLBACK = "fallback"


# ===== SPECIALIZED DATA STRUCTURES =====

@dataclass
class ResponseMetrics:
    """Response metrics data structure."""
    total_responses: int = 0
    successful_responses: int = 0
    error_responses: int = 0
    timeout_responses: int = 0
    cached_responses: int = 0
    fallback_responses: int = 0
    avg_response_time_ms: float = 0.0
    fastest_response_ms: float = float('inf')
    slowest_response_ms: float = 0.0
    cache_hit_rate: float = 0.0
    
    def success_rate(self) -> float:
        """Calculate success rate percentage."""
        return (self.successful_responses / self.total_responses * 100) if self.total_responses > 0 else 0.0


@dataclass
class HTTPClientMetrics:
    """HTTP client metrics data structure."""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    avg_response_time_ms: float = 0.0
    total_response_time_ms: float = 0.0
    requests_by_method: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    requests_by_status: Dict[int, int] = field(default_factory=lambda: defaultdict(int))


@dataclass
class CircuitBreakerMetrics:
    """Circuit breaker metrics data structure."""
    state: str = "closed"
    failure_count: int = 0
    success_count: int = 0
    last_failure_time: Optional[float] = None
    total_requests: int = 0


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
        if operation == MetricOperation.RECORD:
            name = args[0] if args else kwargs.get('name')
            value = args[1] if len(args) > 1 else kwargs.get('value')
            dimensions = args[2] if len(args) > 2 else kwargs.get('dimensions')
            return self.record_metric(name, value, dimensions)
        elif operation == MetricOperation.INCREMENT:
            name = args[0] if args else kwargs.get('name')
            value = args[1] if len(args) > 1 else kwargs.get('value', 1)
            return self.increment_counter(name, value)
        elif operation == MetricOperation.DECREMENT:
            name = args[0] if args else kwargs.get('name')
            value = args[1] if len(args) > 1 else kwargs.get('value', 1)
            return self.increment_counter(name, -value)
        elif operation == MetricOperation.GAUGE:
            name = args[0] if args else kwargs.get('name')
            value = args[1] if len(args) > 1 else kwargs.get('value')
            return self.set_gauge(name, value)
        elif operation == MetricOperation.HISTOGRAM:
            name = args[0] if args else kwargs.get('name')
            value = args[1] if len(args) > 1 else kwargs.get('value')
            return self.record_histogram(name, value)
        elif operation == MetricOperation.GET_METRIC:
            name = args[0] if args else kwargs.get('name')
            return self.get_metric(name)
        elif operation == MetricOperation.GET_STATS:
            return self.get_stats()
        elif operation == MetricOperation.CLEAR:
            return self.clear_metrics()
        # Phase 4 Task #7: New dispatcher operations
        elif operation == MetricOperation.RECORD_DISPATCHER_TIMING:
            interface_name = args[0] if args else kwargs.get('interface_name')
            operation_name = args[1] if len(args) > 1 else kwargs.get('operation_name')
            duration_ms = args[2] if len(args) > 2 else kwargs.get('duration_ms')
            return self.record_dispatcher_timing(interface_name, operation_name, duration_ms)
        elif operation == MetricOperation.GET_DISPATCHER_STATS:
            return self.get_dispatcher_stats()
        elif operation == MetricOperation.GET_OPERATION_METRICS:
            return self.get_operation_metrics()
        
        return None
    
    def _execute_direct_operation(self, operation: MetricOperation, *args, **kwargs) -> Any:
        """Execute operation using direct method calls."""
        return self._execute_generic_operation(operation, *args, **kwargs)
    
    def record_metric(self, name: str, value: float, dimensions: Optional[Dict[str, str]] = None) -> bool:
        """Record a metric value."""
        with self._lock:
            key = self._build_metric_key(name, dimensions)
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
    
    # Phase 4 Task #7: New dispatcher methods
    def record_dispatcher_timing(self, interface_name: str, operation_name: str, duration_ms: float) -> bool:
        """Record dispatcher timing metric (Phase 4 Task #7)."""
        with self._lock:
            key = f"{interface_name}.{operation_name}"
            self._dispatcher_timings[key].append(duration_ms)
            self._dispatcher_call_counts[key] += 1
            
            # Also record as regular metric for backwards compatibility
            self.record_metric(
                f"dispatcher.{interface_name}.{operation_name}.duration_ms",
                duration_ms,
                {'interface': interface_name, 'operation': operation_name}
            )
        return True
    
    def get_dispatcher_stats(self) -> Dict[str, Any]:
        """Get dispatcher performance statistics (Phase 4 Task #7)."""
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
                        'p95_ms': self._calculate_percentile(timings, 95),
                        'p99_ms': self._calculate_percentile(timings, 99)
                    }
            return {'stats': stats, 'total_operations': sum(self._dispatcher_call_counts.values())}
    
    def get_operation_metrics(self) -> Dict[str, Any]:
        """Get operation-level metrics (Phase 4 Task #7)."""
        with self._lock:
            metrics = {}
            
            # Group by interface
            interfaces = defaultdict(lambda: {'operations': {}, 'total_calls': 0})
            for key, count in self._dispatcher_call_counts.items():
                if '.' in key:
                    interface, operation = key.split('.', 1)
                    interfaces[interface]['operations'][operation] = count
                    interfaces[interface]['total_calls'] += count
            
            # Calculate interface-level stats
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
    
    def _calculate_percentile(self, values: List[float], percentile: float) -> float:
        """Calculate percentile value."""
        if not values:
            return 0.0
        sorted_values = sorted(values)
        index = int((percentile / 100) * len(sorted_values))
        return sorted_values[min(index, len(sorted_values) - 1)]
    
    def _build_metric_key(self, name: str, dimensions: Optional[Dict[str, str]] = None) -> str:
        """Build metric key with dimensions."""
        if not dimensions:
            return name
        
        sorted_dims = sorted(dimensions.items())
        dim_str = ','.join(f"{k}={v}" for k, v in sorted_dims)
        return f"{name}[{dim_str}]"
    
    def _record_dispatcher_metric(self, operation: MetricOperation, duration_ms: float):
        """Record dispatcher performance metric (self-recording)."""
        # MetricsCore records its own dispatcher timing directly
        if operation != MetricOperation.RECORD_DISPATCHER_TIMING:  # Avoid infinite recursion
            self.record_dispatcher_timing('MetricsCore', operation.value, duration_ms)
    
    # Specialized metric recording methods
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
                # Update timing stats
                if response_time_ms < self._response_metrics.fastest_response_ms:
                    self._response_metrics.fastest_response_ms = response_time_ms
                if response_time_ms > self._response_metrics.slowest_response_ms:
                    self._response_metrics.slowest_response_ms = response_time_ms
                
                # Update average
                total_time = self._response_metrics.avg_response_time_ms * (self._response_metrics.total_responses - 1)
                self._response_metrics.avg_response_time_ms = (total_time + response_time_ms) / self._response_metrics.total_responses
            
            # Update cache hit rate
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
    
    def record_circuit_breaker_event(self, circuit_name: str, event_type: str, success: Optional[bool] = None) -> None:
        """Record circuit breaker metrics."""
        with self._lock:
            if circuit_name not in self._circuit_breaker_metrics:
                self._circuit_breaker_metrics[circuit_name] = CircuitBreakerMetrics()
            
            cb = self._circuit_breaker_metrics[circuit_name]
            cb.total_requests += 1
            
            if event_type == 'open':
                cb.state = 'open'
                cb.failure_count += 1
                cb.last_failure_time = time.time()
            elif event_type == 'close':
                cb.state = 'closed'
                cb.failure_count = 0
            elif event_type == 'half_open':
                cb.state = 'half_open'
            elif event_type == 'success':
                cb.success_count += 1
            elif event_type == 'failure':
                cb.failure_count += 1
                cb.last_failure_time = time.time()
    
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
                'fastest_response_ms': round(self._response_metrics.fastest_response_ms, 2),
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
            
            # Return all circuit breakers
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


# ===== SINGLETON INSTANCE =====

_MANAGER = MetricsCore()

# ===== IMPLEMENTATION WRAPPERS =====

def _execute_record_metric_implementation(name: str, value: float, dimensions: Optional[Dict[str, str]] = None, **kwargs) -> bool:
    """Execute record metric operation."""
    return _MANAGER.execute_metric_operation(MetricOperation.RECORD, name, value, dimensions)


def _execute_increment_counter_implementation(name: str, value: int = 1, **kwargs) -> int:
    """Execute increment counter operation."""
    return _MANAGER.execute_metric_operation(MetricOperation.INCREMENT, name, value)


def _execute_get_stats_implementation(**kwargs) -> Dict[str, Any]:
    """Execute get stats operation."""
    return _MANAGER.execute_metric_operation(MetricOperation.GET_STATS)


# Specialized operations - use direct _MANAGER calls to preserve exact original behavior
def _execute_record_operation_metric_implementation(operation: str, success: bool = True, duration_ms: float = 0, error_type: Optional[str] = None, **kwargs) -> bool:
    """Execute record operation metric."""
    dimensions = {'operation': operation, 'success': str(success)}
    if error_type:
        dimensions['error_type'] = error_type
    _MANAGER.record_metric(f'operation.{operation}.count', 1.0, dimensions)
    if duration_ms > 0:
        _MANAGER.record_metric(f'operation.{operation}.duration_ms', duration_ms, dimensions)
    return True


def _execute_record_error_response_metric_implementation(error_type: str, severity: str = 'medium', category: str = 'internal', context: Optional[Dict] = None, **kwargs) -> bool:
    """Execute record error response metric."""
    dimensions = {'error_type': error_type, 'severity': severity, 'category': category}
    _MANAGER.record_metric('error.response.count', 1.0, dimensions)
    return True


def _execute_record_cache_metric_implementation(operation: str, hit: bool = False, miss: bool = False, eviction: bool = False, duration_ms: float = 0, **kwargs) -> bool:
    """Execute record cache metric."""
    dimensions = {'operation': operation}
    if hit:
        _MANAGER.record_metric('cache.hit', 1.0, dimensions)
    if miss:
        _MANAGER.record_metric('cache.miss', 1.0, dimensions)
    if eviction:
        _MANAGER.record_metric('cache.eviction', 1.0, dimensions)
    if duration_ms > 0:
        _MANAGER.record_metric('cache.operation.duration_ms', duration_ms, dimensions)
    return True


def _execute_record_api_metric_implementation(endpoint: str, method: str, status_code: int, duration_ms: float, success: bool = True, **kwargs) -> bool:
    """Execute record API metric."""
    dimensions = {'endpoint': endpoint, 'method': method, 'status_code': str(status_code), 'success': str(success)}
    _MANAGER.record_metric('api.request.count', 1.0, dimensions)
    _MANAGER.record_metric('api.request.duration_ms', duration_ms, dimensions)
    _MANAGER.record_metric(f'api.status.{status_code}', 1.0, dimensions)
    return True


def _execute_record_response_metric_implementation(response_type: str, response_time_ms: float = 0.0, **kwargs) -> None:
    """Execute record response metric."""
    try:
        response_type_enum = ResponseType(response_type)
        _MANAGER.record_response_metric(response_type_enum, response_time_ms)
    except ValueError:
        pass


def _execute_record_http_metric_implementation(success: bool, response_time_ms: float = 0.0, method: Optional[str] = None, status_code: Optional[int] = None, **kwargs) -> None:
    """Execute record HTTP metric."""
    _MANAGER.record_http_request(success, response_time_ms, method, status_code)


def _execute_record_circuit_breaker_metric_implementation(circuit_name: str, event_type: str, success: Optional[bool] = None, **kwargs) -> None:
    """Execute record circuit breaker metric."""
    _MANAGER.record_circuit_breaker_event(circuit_name, event_type, success)


def _execute_get_response_metrics_implementation(**kwargs) -> Dict[str, Any]:
    """Execute get response metrics."""
    return _MANAGER.get_response_metrics()


def _execute_get_http_metrics_implementation(**kwargs) -> Dict[str, Any]:
    """Execute get HTTP metrics."""
    return _MANAGER.get_http_metrics()


def _execute_get_circuit_breaker_metrics_implementation(circuit_name: Optional[str] = None, **kwargs) -> Dict[str, Any]:
    """Execute get circuit breaker metrics."""
    return _MANAGER.get_circuit_breaker_metrics(circuit_name)


# Phase 4 Task #7: New dispatcher operation wrappers
def _execute_record_dispatcher_timing_implementation(interface_name: str, operation_name: str, duration_ms: float, **kwargs) -> bool:
    """Execute record dispatcher timing operation."""
    return _MANAGER.execute_metric_operation(MetricOperation.RECORD_DISPATCHER_TIMING, interface_name, operation_name, duration_ms)


def _execute_get_dispatcher_stats_implementation(**kwargs) -> Dict[str, Any]:
    """Execute get dispatcher stats operation."""
    return _MANAGER.execute_metric_operation(MetricOperation.GET_DISPATCHER_STATS)


def _execute_get_operation_metrics_implementation(**kwargs) -> Dict[str, Any]:
    """Execute get operation metrics operation."""
    return _MANAGER.execute_metric_operation(MetricOperation.GET_OPERATION_METRICS)


# ===== PUBLIC INTERFACE =====

def get_metric_value(name: str) -> Optional[Dict[str, Any]]:
    """Public interface for getting metric value."""
    return _MANAGER.get_metric(name)


def record_response_metric(response_type: ResponseType, response_time_ms: float = 0.0) -> None:
    """Public interface for recording response metrics."""
    _MANAGER.record_response_metric(response_type, response_time_ms)


def record_http_request(success: bool, response_time_ms: float = 0.0, 
                       method: Optional[str] = None, status_code: Optional[int] = None) -> None:
    """Public interface for recording HTTP metrics."""
    _MANAGER.record_http_request(success, response_time_ms, method, status_code)


def record_circuit_breaker_event(circuit_name: str, event_type: str, success: Optional[bool] = None) -> None:
    """Public interface for recording circuit breaker events."""
    _MANAGER.record_circuit_breaker_event(circuit_name, event_type, success)


# ===== EXPORTS =====

__all__ = [
    'MetricOperation',
    'MetricType',
    'ResponseType',
    'ResponseMetrics',
    'HTTPClientMetrics',
    'CircuitBreakerMetrics',
    'MetricsCore',
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
    'get_metric_value',
    'record_response_metric',
    'record_http_request',
    'record_circuit_breaker_event'
]

# EOF
