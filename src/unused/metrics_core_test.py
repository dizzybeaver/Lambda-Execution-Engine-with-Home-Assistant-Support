"""
metrics_core.py
Version: 2025.10.15.02
Description: Unified metrics collection with dispatcher timing operations (Phase 4 Task #7)

PHASE 4 TASK #7 - Ultra-Integration:
- Added RECORD_DISPATCHER_TIMING operation for centralized dispatcher metrics
- Added GET_DISPATCHER_STATS operation for querying dispatcher performance
- Added GET_OPERATION_METRICS operation for operation-level metrics
- Eliminates duplicate _record_dispatcher_metric implementations across cores

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
            value = args[1] if len(args) > 1 else kwargs.get('value', 1.0)
            dimensions = args[2] if len(args) > 2 else kwargs.get('dimensions')
            return self.record_metric(name, value, dimensions)
        
        elif operation == MetricOperation.INCREMENT:
            name = args[0] if args else kwargs.get('name')
            value = args[1] if len(args) > 1 else kwargs.get('value', 1)
            return self.increment_counter(name, value)
        
        elif operation == MetricOperation.DECREMENT:
            name = args[0] if args else kwargs.get('name')
            value = args[1] if len(args) > 1 else kwargs.get('value', 1)
            return self.decrement_counter(name, value)
        
        elif operation == MetricOperation.GAUGE:
            name = args[0] if args else kwargs.get('name')
            value = args[1] if len(args) > 1 else kwargs.get('value')
            return self.set_gauge(name, value)
        
        elif operation == MetricOperation.HISTOGRAM:
            name = args[0] if args else kwargs.get('name')
            value = args[1] if len(args) > 1 else kwargs.get('value')
            return self.add_histogram_value(name, value)
        
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
        """Execute operation directly (for comparison/fallback)."""
        return self._execute_generic_operation(operation, *args, **kwargs)
    
    def _record_dispatcher_metric(self, operation: MetricOperation, duration_ms: float):
        """Record dispatcher performance metric (self-recording for MetricsCore)."""
        try:
            self.record_dispatcher_timing('MetricsCore', operation.value, duration_ms)
        except Exception:
            pass
    
    # ===== PHASE 4 TASK #7: NEW DISPATCHER OPERATIONS =====
    
    def record_dispatcher_timing(self, interface_name: str, operation_name: str, duration_ms: float) -> bool:
        """Record dispatcher timing metric (centralized for all cores)."""
        try:
            with self._lock:
                key = f"{interface_name}.{operation_name}"
                self._dispatcher_timings[key].append(duration_ms)
                self._dispatcher_call_counts[key] += 1
                
                # Keep only last 1000 timings per operation
                if len(self._dispatcher_timings[key]) > 1000:
                    self._dispatcher_timings[key] = self._dispatcher_timings[key][-1000:]
                
                return True
        except Exception:
            return False
    
    def get_dispatcher_stats(self) -> Dict[str, Any]:
        """Get dispatcher performance statistics (aggregated by interface)."""
        with self._lock:
            stats_by_interface = {}
            
            for key, timings in self._dispatcher_timings.items():
                if not timings:
                    continue
                
                interface_name = key.split('.')[0]
                
                if interface_name not in stats_by_interface:
                    stats_by_interface[interface_name] = {
                        'total_calls': 0,
                        'operations': {},
                        'avg_duration_ms': 0.0,
                        'min_duration_ms': float('inf'),
                        'max_duration_ms': 0.0
                    }
                
                avg_duration = sum(timings) / len(timings)
                min_duration = min(timings)
                max_duration = max(timings)
                
                stats_by_interface[interface_name]['operations'][key] = {
                    'call_count': self._dispatcher_call_counts[key],
                    'avg_duration_ms': round(avg_duration, 3),
                    'min_duration_ms': round(min_duration, 3),
                    'max_duration_ms': round(max_duration, 3)
                }
                
                stats_by_interface[interface_name]['total_calls'] += self._dispatcher_call_counts[key]
            
            # Calculate interface-level averages
            for interface_name, stats in stats_by_interface.items():
                all_timings = []
                for key in self._dispatcher_timings:
                    if key.startswith(f"{interface_name}."):
                        all_timings.extend(self._dispatcher_timings[key])
                
                if all_timings:
                    stats['avg_duration_ms'] = round(sum(all_timings) / len(all_timings), 3)
                    stats['min_duration_ms'] = round(min(all_timings), 3)
                    stats['max_duration_ms'] = round(max(all_timings), 3)
            
            return {
                'success': True,
                'stats': stats_by_interface,
                'total_operations_tracked': len(self._dispatcher_timings)
            }
    
    def get_operation_metrics(self) -> Dict[str, Any]:
        """Get operation-level metrics (call frequency and timing)."""
        with self._lock:
            operations = []
            
            for key, call_count in self._dispatcher_call_counts.items():
                timings = self._dispatcher_timings.get(key, [])
                if timings:
                    avg_duration = sum(timings) / len(timings)
                    operations.append({
                        'operation': key,
                        'call_count': call_count,
                        'avg_duration_ms': round(avg_duration, 3)
                    })
            
            # Sort by call count descending
            operations.sort(key=lambda x: x['call_count'], reverse=True)
            
            return {
                'success': True,
                'metrics': {
                    'total_operations': len(operations),
                    'total_calls': sum(self._dispatcher_call_counts.values()),
                    'operations': operations[:50]  # Top 50 operations
                }
            }
    
    # ===== CORE METRIC OPERATIONS =====
    
    def record_metric(self, name: str, value: float = 1.0, dimensions: Optional[Dict[str, str]] = None) -> bool:
        """Record a metric value."""
        try:
            with self._lock:
                key = self._build_metric_key(name, dimensions)
                self._metrics[key].append(value)
                self._stats['total_metrics'] += 1
                if key not in self._counters:
                    self._stats['unique_metrics'] += 1
                return True
        except Exception:
            return False
    
    def increment_counter(self, name: str, value: int = 1) -> int:
        """Increment a counter."""
        with self._lock:
            self._counters[name] += value
            self._stats['counters'] = len(self._counters)
            return self._counters[name]
    
    def decrement_counter(self, name: str, value: int = 1) -> int:
        """Decrement a counter."""
        with self._lock:
            self._counters[name] -= value
            self._stats['counters'] = len(self._counters)
            return self._counters[name]
    
    def set_gauge(self, name: str, value: float) -> bool:
        """Set a gauge value."""
        try:
            with self._lock:
                self._gauges[name] = value
                self._stats['gauges'] = len(self._gauges)
                return True
        except Exception:
            return False
    
    def add_histogram_value(self, name: str, value: float) -> bool:
        """Add value to histogram."""
        try:
            with self._lock:
                self._histograms[name].append(value)
                self._stats['histograms'] = len(self._histograms)
                return True
        except Exception:
            return False
    
    def get_metric(self, name: str) -> Optional[Dict[str, Any]]:
        """Get metric value and statistics."""
        with self._lock:
            values = self._metrics.get(name, [])
            if not values:
                return None
            
            return {
                'name': name,
                'count': len(values),
                'sum': sum(values),
                'avg': sum(values) / len(values),
                'min': min(values),
                'max': max(values)
            }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get all metrics statistics."""
        with self._lock:
            return {
                'total_metrics': self._stats['total_metrics'],
                'unique_metrics': self._stats['unique_metrics'],
                'counters': self._stats['counters'],
                'gauges': self._stats['gauges'],
                'histograms': self._stats['histograms'],
                'dispatcher_operations': len(self._dispatcher_timings),
                'dispatcher_total_calls': sum(self._dispatcher_call_counts.values())
            }
    
    def clear_metrics(self) -> int:
        """Clear all metrics."""
        with self._lock:
            count = len(self._metrics)
            self._metrics.clear()
            self._counters.clear()
            self._gauges.clear()
            self._histograms.clear()
            self._dispatcher_timings.clear()
            self._dispatcher_call_counts.clear()
            self._stats = {
                'total_metrics': 0,
                'unique_metrics': 0,
                'counters': 0,
                'gauges': 0,
                'histograms': 0
            }
            return count
    
    def _build_metric_key(self, name: str, dimensions: Optional[Dict[str, str]] = None) -> str:
        """Build metric key with dimensions."""
        if not dimensions:
            return name
        dim_str = ','.join(f"{k}={v}" for k, v in sorted(dimensions.items()))
        return f"{name}[{dim_str}]"
    
    # ===== SPECIALIZED METRICS =====
    
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
                total_time = self._response_metrics.avg_response_time_ms * (self._response_metrics.total_responses - 1)
                self._response_metrics.avg_response_time_ms = (total_time + response_time_ms) / self._response_metrics.total_responses
                self._response_metrics.fastest_response_ms = min(self._response_metrics.fastest_response_ms, response_time_ms)
                self._response_metrics.slowest_response_ms = max(self._response_metrics.slowest_response_ms, response_time_ms)
    
    def record_http_request(self, success: bool, response_time_ms: float = 0.0, 
                           method: Optional[str] = None, status_code: Optional[int] = None) -> None:
        """Record HTTP request metrics."""
        with self._lock:
            self._http_metrics.total_requests += 1
            
            if success:
                self._http_metrics.successful_requests += 1
            else:
                self._http_metrics.failed_requests += 1
            
            if response_time_ms > 0:
                self._http_metrics.total_response_time_ms += response_time_ms
                self._http_metrics.avg_response_time_ms = self._http_metrics.total_response_time_ms / self._http_metrics.total_requests
            
            if method:
                self._http_metrics.requests_by_method[method] += 1
            
            if status_code:
                self._http_metrics.requests_by_status[status_code] += 1
    
    def record_circuit_breaker_event(self, circuit_name: str, event_type: str, success: Optional[bool] = None) -> None:
        """Record circuit breaker event."""
        with self._lock:
            if circuit_name not in self._circuit_breaker_metrics:
                self._circuit_breaker_metrics[circuit_name] = CircuitBreakerMetrics()
            
            cb_metrics = self._circuit_breaker_metrics[circuit_name]
            cb_metrics.total_requests += 1
            
            if event_type == 'state_change':
                cb_metrics.state = 'open' if not success else 'closed'
            elif success is not None:
                if success:
                    cb_metrics.success_count += 1
                else:
                    cb_metrics.failure_count += 1
                    cb_metrics.last_failure_time = time.time()
    
    def get_response_metrics(self) -> Dict[str, Any]:
        """Get response metrics."""
        with self._lock:
            return {
                'total_responses': self._response_metrics.total_responses,
                'successful_responses': self._response_metrics.successful_responses,
                'error_responses': self._response_metrics.error_responses,
                'success_rate': self._response_metrics.success_rate(),
                'avg_response_time_ms': round(self._response_metrics.avg_response_time_ms, 2)
            }
    
    def get_http_metrics(self) -> Dict[str, Any]:
        """Get HTTP metrics."""
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
                        'total_requests': cb.total_requests
                    }
                return {}
            
            return {name: {
                'state': cb.state,
                'failure_count': cb.failure_count,
                'success_count': cb.success_count,
                'total_requests': cb.total_requests
            } for name, cb in self._circuit_breaker_metrics.items()}


_MANAGER = MetricsCore()


# ===== IMPLEMENTATION WRAPPERS =====

def _execute_record_metric_implementation(name: str, value: float = 1.0, dimensions: Optional[Dict[str, str]] = None, **kwargs) -> bool:
    """Execute record metric operation."""
    return _MANAGER.execute_metric_operation(MetricOperation.RECORD, name, value, dimensions)


def _execute_increment_counter_implementation(name: str, value: int = 1, **kwargs) -> int:
    """Execute increment counter operation."""
    return _MANAGER.execute_metric_operation(MetricOperation.INCREMENT, name, value)


def _execute_get_stats_implementation(**kwargs) -> Dict[str, Any]:
    """Execute get stats operation."""
    return _MANAGER.execute_metric_operation(MetricOperation.GET_STATS)


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
        resp_type = ResponseType(response_type)
        _MANAGER.record_response_metric(resp_type, response_time_ms)
    except ValueError:
        pass


def _execute_record_http_metric_implementation(success: bool, response_time_ms: float = 0.0, method: Optional[str] = None, status_code: Optional[int] = None, **kwargs) -> None:
    """Execute record HTTP request metric."""
    _MANAGER.record_http_request(success, response_time_ms, method, status_code)


def _execute_record_circuit_breaker_metric_implementation(circuit_name: str, event_type: str, success: Optional[bool] = None, **kwargs) -> None:
    """Execute record circuit breaker event."""
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
    'get_metric_value',
    'record_response_metric',
    'record_http_request',
    'record_circuit_breaker_event',
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
]

# EOF
