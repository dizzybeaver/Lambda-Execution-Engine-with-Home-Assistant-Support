"""
metrics_core.py
Version: 2025.10.13.03
Description: Metrics collection with generic operation pattern

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


class MetricsCore:
    """Core metrics manager with generic operations."""
    
    def __init__(self):
        self._metrics: Dict[str, List[float]] = defaultdict(list)
        self._counters: Dict[str, int] = defaultdict(int)
        self._gauges: Dict[str, float] = {}
        self._histograms: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self._lock = threading.RLock()
        self._stats = {
            'total_metrics': 0,
            'unique_metrics': 0,
            'counters': 0,
            'gauges': 0,
            'histograms': 0
        }
    
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
    
    def get_stats(self) -> Dict[str, Any]:
        """Get metrics statistics."""
        with self._lock:
            return {
                'total_metrics_recorded': self._stats['total_metrics'],
                'unique_metric_keys': self._stats['unique_metrics'],
                'active_counters': self._stats['counters'],
                'active_gauges': self._stats['gauges'],
                'active_histograms': self._stats['histograms']
            }
    
    def clear_metrics(self) -> bool:
        """Clear all metrics."""
        try:
            with self._lock:
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
                return True
        except Exception:
            return False
    
    def _build_metric_key(self, name: str, dimensions: Optional[Dict[str, str]]) -> str:
        """Build metric key with dimensions."""
        if not dimensions:
            return name
        
        dimension_str = ",".join(f"{k}={v}" for k, v in sorted(dimensions.items()))
        return f"{name}[{dimension_str}]"


_MANAGER = MetricsCore()


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


def get_metric_value(name: str) -> Optional[Dict[str, Any]]:
    """Public interface for getting metric value."""
    return _MANAGER.get_metric(name)


__all__ = [
    'MetricOperation',
    'MetricType',
    'get_metric_value',
    '_execute_record_metric_implementation',
    '_execute_increment_counter_implementation',
    '_execute_get_stats_implementation',
    '_execute_record_operation_metric_implementation',
    '_execute_record_error_response_metric_implementation',
    '_execute_record_cache_metric_implementation',
    '_execute_record_api_metric_implementation',
]

# EOF
