"""
metrics_core.py
Version: 2025.10.14.01
Description: Unified metrics collection with generic operations and specialized tracking

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

import time
import threading
from typing import Dict, Any, Optional, List
from enum import Enum
from collections import defaultdict, deque
from dataclasses import dataclass, field


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
    requests_by_method: Dict[str, int] = field(default_factory=dict)
    requests_by_status: Dict[int, int] = field(default_factory=dict)
    
    def success_rate(self) -> float:
        """Calculate success rate percentage."""
        return (self.successful_requests / self.total_requests * 100) if self.total_requests > 0 else 0.0


@dataclass
class CircuitBreakerMetrics:
    """Circuit breaker metrics data structure."""
    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    circuit_opens: int = 0
    circuit_closes: int = 0
    half_open_attempts: int = 0
    current_state: str = "closed"
    failure_rate: float = 0.0
    
    def calculate_failure_rate(self) -> float:
        """Calculate current failure rate."""
        return (self.failed_calls / self.total_calls * 100) if self.total_calls > 0 else 0.0


# ===== UNIFIED METRICS CORE =====

class MetricsCore:
    """Unified metrics manager with generic operations and specialized tracking."""
    
    def __init__(self):
        # Core metrics storage
        self._metrics: Dict[str, List[float]] = defaultdict(list)
        self._counters: Dict[str, int] = defaultdict(int)
        self._gauges: Dict[str, float] = {}
        self._histograms: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        
        # Specialized metrics
        self._response_metrics = ResponseMetrics()
        self._http_metrics = HTTPClientMetrics()
        self._circuit_breaker_metrics: Dict[str, CircuitBreakerMetrics] = {}
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Statistics
        self._stats = {
            'total_metrics': 0,
            'unique_metrics': 0,
            'counters': 0,
            'gauges': 0,
            'histograms': 0
        }
        
        # Response time tracking
        self._response_times = deque(maxlen=1000)
    
    # ===== GENERIC OPERATIONS =====
    
    def execute_metric_operation(self, operation: MetricOperation, *args, **kwargs) -> Any:
        """Generic metric operation executor."""
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
            value = args[1] if len(args) > 1 else kwargs.get('value', 0.0)
            return self.set_gauge(name, value)
        elif operation == MetricOperation.HISTOGRAM:
            name = args[0] if args else kwargs.get('name')
            value = args[1] if len(args) > 1 else kwargs.get('value', 0.0)
            return self.record_histogram(name, value)
        elif operation == MetricOperation.GET_METRIC:
            name = args[0] if args else kwargs.get('name')
            return self.get_metric(name)
        elif operation == MetricOperation.GET_STATS:
            return self.get_stats()
        elif operation == MetricOperation.CLEAR:
            return self.clear_metrics()
        return None
    
    def record_metric(self, name: str, value: float = 1.0, dimensions: Optional[Dict[str, str]] = None) -> bool:
        """Record metric value."""
        try:
            with self._lock:
                metric_key = self._build_metric_key(name, dimensions)
                self._metrics[metric_key].append(value)
                self._stats['total_metrics'] += 1
                self._stats['unique_metrics'] = len(self._metrics)
                return True
        except Exception:
            return False
    
    def increment_counter(self, name: str, value: int = 1) -> int:
        """Increment counter metric."""
        with self._lock:
            self._counters[name] += value
            self._stats['counters'] = len(self._counters)
            return self._counters[name]
    
    def decrement_counter(self, name: str, value: int = 1) -> int:
        """Decrement counter metric."""
        with self._lock:
            self._counters[name] -= value
            self._stats['counters'] = len(self._counters)
            return self._counters[name]
    
    def set_gauge(self, name: str, value: float) -> bool:
        """Set gauge metric value."""
        try:
            with self._lock:
                self._gauges[name] = value
                self._stats['gauges'] = len(self._gauges)
                return True
        except Exception:
            return False
    
    def record_histogram(self, name: str, value: float) -> bool:
        """Record histogram value."""
        try:
            with self._lock:
                self._histograms[name].append(value)
                self._stats['histograms'] = len(self._histograms)
                return True
        except Exception:
            return False
    
    def get_metric(self, name: str) -> Optional[Dict[str, Any]]:
        """Get metric value."""
        with self._lock:
            if name in self._counters:
                return {'type': MetricType.COUNTER.value, 'value': self._counters[name]}
            elif name in self._gauges:
                return {'type': MetricType.GAUGE.value, 'value': self._gauges[name]}
            elif name in self._histograms:
                values = list(self._histograms[name])
                return {
                    'type': MetricType.HISTOGRAM.value,
                    'count': len(values),
                    'values': values
                }
            elif name in self._metrics:
                values = self._metrics[name]
                return {
                    'type': 'metric',
                    'count': len(values),
                    'values': values
                }
            return None
    
    # ===== RESPONSE METRICS =====
    
    def record_response_metric(self, response_type: ResponseType, response_time_ms: float = 0.0) -> None:
        """Record response metric."""
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
                self._response_times.append(response_time_ms)
                
                # Update min/max
                if response_time_ms < self._response_metrics.fastest_response_ms:
                    self._response_metrics.fastest_response_ms = response_time_ms
                if response_time_ms > self._response_metrics.slowest_response_ms:
                    self._response_metrics.slowest_response_ms = response_time_ms
                
                # Update average
                if self._response_times:
                    self._response_metrics.avg_response_time_ms = sum(self._response_times) / len(self._response_times)
            
            # Update cache hit rate
            total_cacheable = self._response_metrics.cached_responses + self._response_metrics.successful_responses
            if total_cacheable > 0:
                self._response_metrics.cache_hit_rate = (self._response_metrics.cached_responses / total_cacheable) * 100
    
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
                'avg_response_time_ms': self._response_metrics.avg_response_time_ms,
                'fastest_response_ms': self._response_metrics.fastest_response_ms,
                'slowest_response_ms': self._response_metrics.slowest_response_ms,
                'cache_hit_rate': self._response_metrics.cache_hit_rate,
                'success_rate': self._response_metrics.success_rate()
            }
    
    # ===== HTTP CLIENT METRICS =====
    
    def record_http_request(self, success: bool, response_time_ms: float = 0.0, 
                           method: Optional[str] = None, status_code: Optional[int] = None) -> None:
        """Record HTTP request metric."""
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
                if method not in self._http_metrics.requests_by_method:
                    self._http_metrics.requests_by_method[method] = 0
                self._http_metrics.requests_by_method[method] += 1
            
            if status_code:
                if status_code not in self._http_metrics.requests_by_status:
                    self._http_metrics.requests_by_status[status_code] = 0
                self._http_metrics.requests_by_status[status_code] += 1
    
    def get_http_metrics(self) -> Dict[str, Any]:
        """Get HTTP client metrics."""
        with self._lock:
            return {
                'total_requests': self._http_metrics.total_requests,
                'successful_requests': self._http_metrics.successful_requests,
                'failed_requests': self._http_metrics.failed_requests,
                'avg_response_time_ms': self._http_metrics.avg_response_time_ms,
                'total_response_time_ms': self._http_metrics.total_response_time_ms,
                'requests_by_method': dict(self._http_metrics.requests_by_method),
                'requests_by_status': dict(self._http_metrics.requests_by_status),
                'success_rate': self._http_metrics.success_rate()
            }
    
    # ===== CIRCUIT BREAKER METRICS =====
    
    def record_circuit_breaker_event(self, circuit_name: str, event_type: str, 
                                     success: Optional[bool] = None) -> None:
        """Record circuit breaker event."""
        with self._lock:
            if circuit_name not in self._circuit_breaker_metrics:
                self._circuit_breaker_metrics[circuit_name] = CircuitBreakerMetrics()
            
            cb_metrics = self._circuit_breaker_metrics[circuit_name]
            
            if event_type == 'call':
                cb_metrics.total_calls += 1
                if success:
                    cb_metrics.successful_calls += 1
                else:
                    cb_metrics.failed_calls += 1
                cb_metrics.failure_rate = cb_metrics.calculate_failure_rate()
            
            elif event_type == 'open':
                cb_metrics.circuit_opens += 1
                cb_metrics.current_state = 'open'
            
            elif event_type == 'close':
                cb_metrics.circuit_closes += 1
                cb_metrics.current_state = 'closed'
            
            elif event_type == 'half_open':
                cb_metrics.half_open_attempts += 1
                cb_metrics.current_state = 'half_open'
    
    def get_circuit_breaker_metrics(self, circuit_name: Optional[str] = None) -> Dict[str, Any]:
        """Get circuit breaker metrics."""
        with self._lock:
            if circuit_name:
                if circuit_name in self._circuit_breaker_metrics:
                    cb = self._circuit_breaker_metrics[circuit_name]
                    return {
                        'total_calls': cb.total_calls,
                        'successful_calls': cb.successful_calls,
                        'failed_calls': cb.failed_calls,
                        'circuit_opens': cb.circuit_opens,
                        'circuit_closes': cb.circuit_closes,
                        'half_open_attempts': cb.half_open_attempts,
                        'current_state': cb.current_state,
                        'failure_rate': cb.failure_rate
                    }
                return {}
            
            # Return all circuit breaker metrics
            return {
                name: {
                    'total_calls': cb.total_calls,
                    'successful_calls': cb.successful_calls,
                    'failed_calls': cb.failed_calls,
                    'circuit_opens': cb.circuit_opens,
                    'circuit_closes': cb.circuit_closes,
                    'half_open_attempts': cb.half_open_attempts,
                    'current_state': cb.current_state,
                    'failure_rate': cb.failure_rate
                }
                for name, cb in self._circuit_breaker_metrics.items()
            }
    
    # ===== STATS AND MANAGEMENT =====
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive metrics statistics."""
        with self._lock:
            return {
                'total_metrics_recorded': self._stats['total_metrics'],
                'unique_metric_keys': self._stats['unique_metrics'],
                'active_counters': self._stats['counters'],
                'active_gauges': self._stats['gauges'],
                'active_histograms': self._stats['histograms'],
                'response_metrics': self.get_response_metrics(),
                'http_metrics': self.get_http_metrics(),
                'circuit_breaker_count': len(self._circuit_breaker_metrics)
            }
    
    def clear_metrics(self) -> bool:
        """Clear all metrics."""
        try:
            with self._lock:
                self._metrics.clear()
                self._counters.clear()
                self._gauges.clear()
                self._histograms.clear()
                self._response_metrics = ResponseMetrics()
                self._http_metrics = HTTPClientMetrics()
                self._circuit_breaker_metrics.clear()
                self._response_times.clear()
                self._stats = {
                    'total_metrics': 0,
                    'unique_metrics': 0,
                    'counters': 0,
                    'gauges': 0,
                    'histograms': 0
                }
                return True
        except Exception:
            return False
    
    def _build_metric_key(self, name: str, dimensions: Optional[Dict[str, str]]) -> str:
        """Build metric key with dimensions."""
        if not dimensions:
            return name
        
        dimension_str = ",".join(f"{k}={v}" for k, v in sorted(dimensions.items()))
        return f"{name}[{dimension_str}]"


# ===== SINGLETON INSTANCE =====

_MANAGER = MetricsCore()


# ===== IMPLEMENTATION FUNCTIONS FOR GATEWAY =====

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
]

# EOF
