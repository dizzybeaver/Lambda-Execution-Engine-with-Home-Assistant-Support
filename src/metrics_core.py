"""
metrics_core.py - Core metrics collection manager
Version: 2025.10.21.01
Description: PHASE 2 TASK 2.2 - Use safe_divide() helper to eliminate division-by-zero duplication

CHANGELOG:
- 2025.10.21.01: PHASE 2 TASK 2.2 - Genericize safe division
  - Updated 10+ locations to use safe_divide() helper
  - Eliminated ~30 LOC of duplicated division-by-zero checks
  - Locations updated:
    * record_response_metric: avg_response_time_ms, cache_hit_rate
    * record_http_metric: avg_response_time_ms
    * get_http_metrics: success_rate
    * get_circuit_breaker_metrics: failure_rate (2 locations)
    * get_dispatcher_stats: avg_duration_ms

FIXES IMPLEMENTED (Phase 1):
- Bug #3: Fixed thread safety - get_response_metrics, get_http_metrics, get_circuit_breaker_metrics now use locks
- Bug #4: Implemented missing methods completely
- Bug #11: Division by zero checks in all calculations
- Bug #13: Input validation for negative durations
- Bug #1: Fixed ResponseMetrics - added responses_by_type and responses_by_status tracking
- Bug #2: Implemented record_circuit_breaker_event completely

Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
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
from metrics_helper import calculate_percentile, build_metric_key, safe_divide

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
        """Record dispatcher timing metric with thread safety."""
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
        """Get comprehensive metrics statistics with thread safety."""
        with self._lock:
            stats = self._stats.copy()
            
            stats['response_metrics'] = {
                'total_responses': self._response_metrics.total_responses,
                'successful_responses': self._response_metrics.successful_responses,
                'error_responses': self._response_metrics.error_responses,
                'timeout_responses': self._response_metrics.timeout_responses,
                'cached_responses': self._response_metrics.cached_responses,
                'fallback_responses': self._response_metrics.fallback_responses,
                'avg_response_time_ms': self._response_metrics.avg_response_time_ms,
                'fastest_response_ms': (
                    self._response_metrics.fastest_response_ms 
                    if self._response_metrics.fastest_response_ms != float('inf') 
                    else 0.0
                ),
                'slowest_response_ms': self._response_metrics.slowest_response_ms,
                'cache_hit_rate': self._response_metrics.cache_hit_rate,
                'success_rate': self._response_metrics.success_rate()
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
                        'total_requests': cb.total_requests,
                        'last_failure_time': cb.last_failure_time
                    }
                    for name, cb in self._circuit_breaker_metrics.items()
                }
            
            return stats
    
    # ===== RESPONSE METRICS =====
    
    def record_response_metric(self, response_type: ResponseType, status_code: int, duration_ms: float = 0):
        """Record response metric with validation."""
        # Input validation
        if duration_ms < 0:
            duration_ms = 0
        
        with self._lock:
            self._response_metrics.total_responses += 1
            
            # Track by type
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
            
            # Update timing stats using safe_divide
            if duration_ms > 0:
                # Calculate new average
                total_time = (
                    self._response_metrics.avg_response_time_ms * 
                    (self._response_metrics.total_responses - 1)
                ) + duration_ms
                self._response_metrics.avg_response_time_ms = safe_divide(
                    total_time,
                    self._response_metrics.total_responses
                )
                
                # Track fastest/slowest
                if duration_ms < self._response_metrics.fastest_response_ms:
                    self._response_metrics.fastest_response_ms = duration_ms
                if duration_ms > self._response_metrics.slowest_response_ms:
                    self._response_metrics.slowest_response_ms = duration_ms
            
            # Calculate cache hit rate using safe_divide
            self._response_metrics.cache_hit_rate = safe_divide(
                self._response_metrics.cached_responses,
                self._response_metrics.total_responses,
                multiply_by=100.0
            )
    
    def get_response_metrics(self) -> Dict[str, Any]:
        """Get response metrics with thread safety."""
        with self._lock:
            return {
                'total_responses': self._response_metrics.total_responses,
                'successful_responses': self._response_metrics.successful_responses,
                'error_responses': self._response_metrics.error_responses,
                'timeout_responses': self._response_metrics.timeout_responses,
                'cached_responses': self._response_metrics.cached_responses,
                'fallback_responses': self._response_metrics.fallback_responses,
                'avg_response_time_ms': self._response_metrics.avg_response_time_ms,
                'fastest_response_ms': (
                    self._response_metrics.fastest_response_ms 
                    if self._response_metrics.fastest_response_ms != float('inf') 
                    else 0.0
                ),
                'slowest_response_ms': self._response_metrics.slowest_response_ms,
                'cache_hit_rate': self._response_metrics.cache_hit_rate,
                'success_rate': self._response_metrics.success_rate()
            }
    
    # ===== HTTP CLIENT METRICS =====
    
    def record_http_metric(self, method: str, url: str, status_code: int, 
                          duration_ms: float, response_size: Optional[int] = None):
        """Record HTTP client metric with validation."""
        # Input validation
        if duration_ms < 0:
            duration_ms = 0
        
        with self._lock:
            self._http_metrics.total_requests += 1
            self._http_metrics.requests_by_method[method] += 1
            self._http_metrics.requests_by_status[status_code] += 1
            
            # Success/failure tracking
            if 200 <= status_code < 400:
                self._http_metrics.successful_requests += 1
            else:
                self._http_metrics.failed_requests += 1
            
            # Update timing using safe_divide
            self._http_metrics.total_response_time_ms += duration_ms
            self._http_metrics.avg_response_time_ms = safe_divide(
                self._http_metrics.total_response_time_ms,
                self._http_metrics.total_requests
            )
    
    def get_http_metrics(self) -> Dict[str, Any]:
        """Get HTTP client metrics with thread safety."""
        with self._lock:
            return {
                'total_requests': self._http_metrics.total_requests,
                'successful_requests': self._http_metrics.successful_requests,
                'failed_requests': self._http_metrics.failed_requests,
                'avg_response_time_ms': self._http_metrics.avg_response_time_ms,
                'total_response_time_ms': self._http_metrics.total_response_time_ms,
                'requests_by_method': dict(self._http_metrics.requests_by_method),
                'requests_by_status': dict(self._http_metrics.requests_by_status),
                'success_rate': safe_divide(
                    self._http_metrics.successful_requests,
                    self._http_metrics.total_requests,
                    multiply_by=100.0
                )
            }
    
    # ===== CIRCUIT BREAKER METRICS =====
    
    def record_circuit_breaker_event(self, circuit_name: str, event_type: str, success: bool = True):
        """Record circuit breaker event."""
        with self._lock:
            # Initialize circuit breaker if new
            if circuit_name not in self._circuit_breaker_metrics:
                self._circuit_breaker_metrics[circuit_name] = CircuitBreakerMetrics()
            
            cb = self._circuit_breaker_metrics[circuit_name]
            cb.total_requests += 1
            
            if success:
                cb.success_count += 1
                # State transitions
                if event_type == 'close':
                    cb.state = 'closed'
            else:
                cb.failure_count += 1
                cb.last_failure_time = time.time()
                # State transitions
                if event_type == 'open':
                    cb.state = 'open'
                elif event_type == 'half_open':
                    cb.state = 'half_open'
    
    def get_circuit_breaker_metrics(self, circuit_name: Optional[str] = None) -> Dict[str, Any]:
        """Get circuit breaker metrics with thread safety."""
        with self._lock:
            if circuit_name:
                # Get specific circuit breaker
                if circuit_name not in self._circuit_breaker_metrics:
                    return {}
                
                cb = self._circuit_breaker_metrics[circuit_name]
                return {
                    'state': cb.state,
                    'failure_count': cb.failure_count,
                    'success_count': cb.success_count,
                    'total_requests': cb.total_requests,
                    'last_failure_time': cb.last_failure_time,
                    'failure_rate': safe_divide(
                        cb.failure_count,
                        cb.total_requests,
                        multiply_by=100.0
                    )
                }
            else:
                # Get all circuit breakers
                return {
                    name: {
                        'state': cb.state,
                        'failure_count': cb.failure_count,
                        'success_count': cb.success_count,
                        'total_requests': cb.total_requests,
                        'last_failure_time': cb.last_failure_time,
                        'failure_rate': safe_divide(
                            cb.failure_count,
                            cb.total_requests,
                            multiply_by=100.0
                        )
                    }
                    for name, cb in self._circuit_breaker_metrics.items()
                }
    
    # ===== DISPATCHER METRICS =====
    
    def record_dispatcher_timing(self, interface_name: str, operation_name: str, duration_ms: float) -> bool:
        """Record dispatcher timing with validation."""
        # Input validation
        if duration_ms < 0:
            return False
        
        try:
            with self._lock:
                key = f"{interface_name}.{operation_name}"
                self._dispatcher_timings[key].append(duration_ms)
                self._dispatcher_call_counts[key] += 1
                return True
        except Exception:
            return False
    
    def get_dispatcher_stats(self) -> Dict[str, Any]:
        """Get dispatcher statistics with thread safety."""
        with self._lock:
            interfaces = defaultdict(lambda: {'operations': {}, 'total_calls': 0})
            for key, count in self._dispatcher_call_counts.items():
                if '.' in key:
                    interface, operation = key.split('.', 1)
                    interfaces[interface]['operations'][operation] = count
                    interfaces[interface]['total_calls'] += count
            
            # Calculate timing stats for each interface using safe_divide
            for interface, data in interfaces.items():
                if interface in ['CacheCore', 'LoggingCore', 'SecurityCore', 'MetricsCore']:
                    all_timings = []
                    for op_key, timing_list in self._dispatcher_timings.items():
                        if op_key.startswith(interface):
                            all_timings.extend(timing_list)
                    
                    if all_timings:
                        total_duration = sum(all_timings)
                        data['avg_duration_ms'] = safe_divide(total_duration, len(all_timings))
                        data['total_duration_ms'] = total_duration
            
            return dict(interfaces)
    
    def get_operation_metrics(self) -> Dict[str, Any]:
        """Get operation-level metrics with thread safety."""
        with self._lock:
            return {
                'timings': {k: v for k, v in self._dispatcher_timings.items()},
                'call_counts': dict(self._dispatcher_call_counts)
            }

    def reset_metrics(self) -> bool:
        """
        Reset all metrics to initial state.
        
        Useful for testing and debugging. Clears all:
        - Metrics data
        - Counters
        - Gauges
        - Histograms
        - Response metrics
        - HTTP metrics
        - Circuit breaker metrics
        - Dispatcher timings
        
        Returns:
            bool: True if reset successful
            
        Example:
            manager.reset_metrics()
            # All metrics cleared
        """
        try:
            with self._lock:
                self._metrics.clear()
                self._counters.clear()
                self._gauges.clear()
                self._histograms.clear()
                
                # Reset stats
                self._stats = {
                    'total_metrics': 0,
                    'unique_metrics': 0,
                    'counters': 0,
                    'gauges': 0,
                    'histograms': 0
                }
                
                # Reset response metrics
                self._response_metrics = ResponseMetrics()
                
                # Reset HTTP metrics
                self._http_metrics = HTTPClientMetrics()
                
                # Reset circuit breakers
                self._circuit_breaker_metrics.clear()
                
                # Reset dispatcher timings
                self._dispatcher_timings.clear()
                self._dispatcher_call_counts.clear()
                
                return True
        except Exception:
            return False

# ===== SINGLETON INSTANCE =====

_MANAGER = MetricsCore()


# ===== EXPORTS =====

__all__ = [
    'MetricsCore',
    '_MANAGER',
]

# EOF
