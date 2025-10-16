"""
metrics_core.py - Core metrics collection manager
Version: 2025.10.16.01
Description: MetricsCore class with unified operations - CIRCULAR IMPORT FIXED

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

# ===== CIRCULAR IMPORT FIX =====
# REMOVED: imports from metrics_operations (lines 23-39 in original)
# Those functions are never called in this file - only used by interface_metrics.py
# Importing them here creates circular dependency:
#   metrics_core → metrics_operations → metrics_core (_MANAGER)

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
            return self.record_metric(*args, **kwargs)
        elif operation == MetricOperation.INCREMENT:
            return self.increment_counter(*args, **kwargs)
        elif operation == MetricOperation.GET_STATS:
            return self.get_stats()
        else:
            raise ValueError(f"Unknown metric operation: {operation}")
    
    def _execute_direct_operation(self, operation: MetricOperation, *args, **kwargs) -> Any:
        """Execute operation directly (legacy path)."""
        operation_map = {
            MetricOperation.RECORD: self.record_metric,
            MetricOperation.INCREMENT: self.increment_counter,
            MetricOperation.GET_STATS: self.get_stats
        }
        
        handler = operation_map.get(operation)
        if not handler:
            raise ValueError(f"Unknown metric operation: {operation}")
        
        return handler(*args, **kwargs)
    
    def _record_dispatcher_metric(self, operation: MetricOperation, duration_ms: float):
        """Record dispatcher timing metric."""
        with self._lock:
            key = f"MetricsCore.{operation.value}"
            self._dispatcher_timings[key].append(duration_ms)
            self._dispatcher_call_counts[key] += 1
    
    # ===== CORE METRIC OPERATIONS =====
    
    def record_metric(self, name: str, value: float, dimensions: Optional[Dict[str, str]] = None) -> bool:
        """Record a metric value."""
        try:
            with self._lock:
                key = build_metric_key(name, dimensions)
                self._metrics[key].append(value)
                self._stats['total_metrics'] += 1
                self._stats['unique_metrics'] = len(self._metrics)
                return True
        except Exception:
            return False
    
    def increment_counter(self, name: str, value: int = 1) -> int:
        """Increment a counter metric."""
        with self._lock:
            self._counters[name] += value
            self._stats['counters'] = len(self._counters)
            return self._counters[name]
    
    def set_gauge(self, name: str, value: float) -> bool:
        """Set a gauge metric."""
        try:
            with self._lock:
                self._gauges[name] = value
                self._stats['gauges'] = len(self._gauges)
                return True
        except Exception:
            return False
    
    def record_histogram(self, name: str, value: float) -> bool:
        """Record a histogram value."""
        try:
            with self._lock:
                self._histograms[name].append(value)
                self._stats['histograms'] = len(self._histograms)
                return True
        except Exception:
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive metrics statistics."""
        with self._lock:
            stats = self._stats.copy()
            
            stats['response_metrics'] = {
                'total_responses': self._response_metrics.total_responses,
                'total_errors': self._response_metrics.total_errors,
                'avg_response_time_ms': self._response_metrics.avg_response_time_ms,
                'responses_by_type': dict(self._response_metrics.responses_by_type),
                'responses_by_status': dict(self._response_metrics.responses_by_status)
            }
            
            stats['http_metrics'] = {
                'total_requests': self._http_metrics.total_requests,
                'successful_requests': self._http_metrics.successful_requests,
                'failed_requests': self._http_metrics.failed_requests,
                'avg_response_time_ms': self._http_metrics.avg_response_time_ms,
                'requests_by_method': dict(self._http_metrics.requests_by_method),
                'requests_by_status': dict(self._http_metrics.requests_by_status)
            }
            
            if self._circuit_breaker_metrics:
                stats['circuit_breakers'] = {
                    name: {
                        'state': cb.state,
                        'failure_count': cb.failure_count,
                        'success_count': cb.success_count,
                        'total_requests': cb.total_requests
                    }
                    for name, cb in self._circuit_breaker_metrics.items()
                }
            
            return stats
    
    # ===== RESPONSE METRICS =====
    
    def record_response_metric(self, response_type: ResponseType, status_code: int, duration_ms: float = 0):
        """Record response metric."""
        with self._lock:
            self._response_metrics.total_responses += 1
            self._response_metrics.responses_by_type[response_type.value] += 1
            self._response_metrics.responses_by_status[status_code] += 1
            
            if status_code >= 400:
                self._response_metrics.total_errors += 1
            
            if duration_ms > 0:
                total_time = self._response_metrics.total_response_time_ms + duration_ms
                total_responses = self._response_metrics.total_responses
                self._response_metrics.avg_response_time_ms = total_time / total_responses
                self._response_metrics.total_response_time_ms = total_time
    
    def get_response_metrics(self) -> Dict[str, Any]:
        """Get response metrics."""
        with self._lock:
            return {
                'total_responses': self._response_metrics.total_responses,
                'total_errors': self._response_metrics.total_errors,
                'error_rate': self._response_metrics.total_errors / max(1, self._response_metrics.total_responses),
                'avg_response_time_ms': self._response_metrics.avg_response_time_ms,
                'total_response_time_ms': self._response_metrics.total_response_time_ms,
                'responses_by_type': dict(self._response_metrics.responses_by_type),
                'responses_by_status': dict(self._response_metrics.responses_by_status)
            }
    
    # ===== HTTP CLIENT METRICS =====
    
    def record_http_metric(self, method: str, url: str, status_code: int, duration_ms: float, response_size: Optional[int] = None):
        """Record HTTP client metric."""
        with self._lock:
            self._http_metrics.total_requests += 1
            self._http_metrics.requests_by_method[method] += 1
            self._http_metrics.requests_by_status[status_code] += 1
            
            if 200 <= status_code < 300:
                self._http_metrics.successful_requests += 1
            else:
                self._http_metrics.failed_requests += 1
            
            total_time = self._http_metrics.total_response_time_ms + duration_ms
            total_requests = self._http_metrics.total_requests
            self._http_metrics.avg_response_time_ms = total_time / total_requests
            self._http_metrics.total_response_time_ms = total_time
    
    def get_http_metrics(self) -> Dict[str, Any]:
        """Get HTTP client metrics."""
        with self._lock:
            return {
                'total_requests': self._http_metrics.total_requests,
                'successful_requests': self._http_metrics.successful_requests,
                'failed_requests': self._http_metrics.failed_requests,
                'success_rate': self._http_metrics.successful_requests / max(1, self._http_metrics.total_requests),
                'avg_response_time_ms': self._http_metrics.avg_response_time_ms,
                'total_response_time_ms': self._http_metrics.total_response_time_ms,
                'requests_by_method': dict(self._http_metrics.requests_by_method),
                'requests_by_status': dict(self._http_metrics.requests_by_status)
            }
    
    # ===== CIRCUIT BREAKER METRICS =====
    
    def record_circuit_breaker_event(self, circuit_name: str, event_type: str, success: bool = True):
        """Record circuit breaker event."""
        with self._lock:
            if circuit_name not in self._circuit_breaker_metrics:
                self._circuit_breaker_metrics[circuit_name] = CircuitBreakerMetrics()
            
            cb = self._circuit_breaker_metrics[circuit_name]
            cb.total_requests += 1
            
            if success:
                cb.success_count += 1
            else:
                cb.failure_count += 1
                cb.last_failure_time = time.time()
            
            if event_type == 'opened':
                cb.state = 'open'
            elif event_type == 'closed':
                cb.state = 'closed'
            elif event_type == 'half_open':
                cb.state = 'half_open'
    
    def get_circuit_breaker_metrics(self, circuit_name: Optional[str] = None) -> Dict[str, Any]:
        """Get circuit breaker metrics."""
        with self._lock:
            if circuit_name:
                cb = self._circuit_breaker_metrics.get(circuit_name)
                if cb:
                    return {
                        'state': cb.state,
                        'failure_count': cb.failure_count,
                        'success_count': cb.success_count,
                        'total_requests': cb.total_requests,
                        'last_failure_time': cb.last_failure_time
                    }
                return {}
            else:
                return {
                    name: {
                        'state': cb.state,
                        'failure_count': cb.failure_count,
                        'success_count': cb.success_count,
                        'total_requests': cb.total_requests
                    }
                    for name, cb in self._circuit_breaker_metrics.items()
                }
    
    # ===== DISPATCHER METRICS =====
    
    def record_dispatcher_timing(self, interface_name: str, operation_name: str, duration_ms: float) -> bool:
        """Record dispatcher timing."""
        try:
            with self._lock:
                key = f"{interface_name}.{operation_name}"
                self._dispatcher_timings[key].append(duration_ms)
                self._dispatcher_call_counts[key] += 1
                return True
        except Exception:
            return False
    
    def get_dispatcher_stats(self) -> Dict[str, Any]:
        """Get dispatcher statistics."""
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
    
    def get_operation_metrics(self) -> Dict[str, Any]:
        """Get operation-level metrics."""
        with self._lock:
            return {
                'timings': {k: v for k, v in self._dispatcher_timings.items()},
                'call_counts': dict(self._dispatcher_call_counts)
            }


# ===== SINGLETON INSTANCE =====

_MANAGER = MetricsCore()


# ===== EXPORTS =====
# CIRCULAR IMPORT FIX: Do NOT import from metrics_operations here!
# Those functions should be imported directly by interface_metrics.py
# 
# OLD CODE (CAUSED 30-SECOND TIMEOUT):
# from metrics_operations import (
#     _execute_record_metric_implementation,
#     _execute_increment_counter_implementation,
#     ... all other implementations
# )
#
# WHY THIS CAUSED TIMEOUT:
# 1. metrics_core.py imports from metrics_operations.py (these deleted lines)
# 2. metrics_operations.py imports _MANAGER from metrics_core.py (inside functions)
# 3. When loading metrics_core, Python hits these imports
# 4. Tries to load metrics_operations.py
# 5. Which tries to access _MANAGER from metrics_core.py
# 6. But _MANAGER isn't defined yet (circular dependency)
# 7. Result: 30-second timeout
#
# FIX: interface_metrics.py imports directly from metrics_operations.py
# No need to re-export through metrics_core.py

__all__ = [
    'MetricsCore',
    '_MANAGER',
]
# EOF
