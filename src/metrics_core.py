"""
metrics_core.py - Core metrics collection manager
Version: 2025.10.21.02 - PHASE 1 COMPLETE
Description: MetricsCore with security validations, memory limits, and rate limiting

PHASE 1 CHANGES COMPLETED:
✅ Removed threading locks (AP-08 compliance, DEC-04)
✅ Added security validations (Finding 5.1, 5.3, 5.5)
✅ Added memory limits with FIFO eviction (Finding 5.2)
✅ Added rate limiting (Finding 5.4)
✅ Prepared for SINGLETON registration (INT-06)
✅ Added reset_metrics() for testing

FIXES IMPLEMENTED:
- Bug #3: Removed threading locks (Lambda is single-threaded)
- Bug #11: Division by zero checks in all calculations
- Bug #13: Input validation for negative durations
- Bug #1: Fixed ResponseMetrics tracking
- Bug #2: Implemented record_circuit_breaker_event

SECURITY IMPROVEMENTS:
- Metric name validation (prevents injection attacks)
- Dimension value validation (prevents path traversal)
- Metric value validation (prevents NaN/Infinity)
- Rate limiting (prevents DoS attacks)
- Memory limits (prevents OOM attacks)

Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

import os
import time
import math
from typing import Dict, Any, Optional, List
from collections import defaultdict, deque

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
MAX_VALUES_PER_METRIC = int(os.getenv('MAX_VALUES_PER_METRIC', '1000'))
RATE_LIMIT_CALLS_PER_SECOND = int(os.getenv('RATE_LIMIT_CALLS_PER_SECOND', '1000'))


# ===== METRICS CORE IMPLEMENTATION =====

class MetricsCore:
    """
    Singleton metrics manager with unified operations.
    
    DESIGN DECISIONS:
    - No threading locks (DEC-04): Lambda is single-threaded
    - Security validations: Prevent injection attacks (Finding 5.1, 5.3, 5.5)
    - Memory limits: FIFO eviction at MAX_VALUES_PER_METRIC (Finding 5.2)
    - Rate limiting: Limit to RATE_LIMIT_CALLS_PER_SECOND (Finding 5.4)
    - Silent failures: Metrics never crash the app
    """
    
    def __init__(self):
        # Core metric storage
        self._metrics: Dict[str, List[float]] = defaultdict(list)
        self._counters: Dict[str, int] = defaultdict(int)
        self._gauges: Dict[str, float] = {}
        self._histograms: Dict[str, List[float]] = defaultdict(list)
        
        # Statistics tracking
        self._stats = {
            'total_metrics': 0,
            'unique_metrics': 0,
            'counters': 0,
            'gauges': 0,
            'histograms': 0,
            'rate_limited_count': 0  # Track rate limiting
        }
        
        # Specialized metrics
        self._response_metrics = ResponseMetrics()
        self._http_metrics = HTTPClientMetrics()
        self._circuit_breaker_metrics: Dict[str, CircuitBreakerMetrics] = {}
        
        # Dispatcher metrics
        self._dispatcher_timings: Dict[str, List[float]] = defaultdict(list)
        self._dispatcher_call_counts: Dict[str, int] = defaultdict(int)
        
        # Rate limiting (Finding 5.4)
        self._rate_limiter = deque(maxlen=RATE_LIMIT_CALLS_PER_SECOND)
        self._rate_limit_window_ms = 1000  # 1 second window
    
    def _check_rate_limit(self) -> bool:
        """
        Check if rate limit exceeded.
        
        Implementation:
        - Sliding window rate limiter
        - Limit: RATE_LIMIT_CALLS_PER_SECOND per second (default: 1000)
        - Uses deque for O(1) operations
        
        REF: Finding 5.4 (Add rate limiting to prevent DoS)
        
        Returns:
            True if call allowed, False if rate limited
        """
        now = time.time() * 1000  # milliseconds
        
        # Clean old timestamps outside window
        while self._rate_limiter and (now - self._rate_limiter[0]) > self._rate_limit_window_ms:
            self._rate_limiter.popleft()
        
        # Check if limit exceeded
        if len(self._rate_limiter) >= RATE_LIMIT_CALLS_PER_SECOND:
            self._stats['rate_limited_count'] += 1
            return False  # Rate limited
        
        # Record this call
        self._rate_limiter.append(now)
        return True
    
    def _apply_memory_limit(self, values: List[float]) -> None:
        """
        Apply FIFO eviction to keep list bounded.
        
        Implementation:
        - FIFO (First In, First Out) eviction
        - Simpler and faster than LRU
        - Prevents unbounded memory growth
        
        REF: Finding 5.2 (Add memory limits with FIFO eviction)
        
        Args:
            values: List to bound (modified in place)
        """
        while len(values) > MAX_VALUES_PER_METRIC:
            values.pop(0)  # Remove oldest value
    
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
        elif operation == MetricOperation.RESET:
            return self.reset_metrics()
        else:
            raise ValueError(f"Unknown metric operation: {operation}")
    
    def _execute_direct_operation(self, operation: MetricOperation, *args, **kwargs) -> Any:
        """Execute operation directly (legacy path)."""
        operation_map = {
            MetricOperation.RECORD: self.record_metric,
            MetricOperation.INCREMENT: self.increment_counter,
            MetricOperation.GET_STATS: self.get_stats,
            MetricOperation.RESET: self.reset_metrics,
        }
        
        handler = operation_map.get(operation)
        if not handler:
            raise ValueError(f"Unknown metric operation: {operation}")
        
        return handler(*args, **kwargs)
    
    def _record_dispatcher_metric(self, operation: MetricOperation, duration_ms: float):
        """Record dispatcher timing metric."""
        key = f"MetricsCore.{operation.value}"
        self._dispatcher_timings[key].append(duration_ms)
        self._dispatcher_call_counts[key] += 1
        
        # Apply memory limits to dispatcher timings too
        self._apply_memory_limit(self._dispatcher_timings[key])
    
    # ===== CORE METRIC OPERATIONS =====
    
    def record_metric(self, name: str, value: float, dimensions: Optional[Dict[str, str]] = None) -> bool:
        """
        Record a metric value with security validations.
        
        Security:
        - Validates metric name (Finding 5.1)
        - Validates metric value (Finding 5.5)
        - Rate limiting (Finding 5.4)
        - Memory limits (Finding 5.2)
        
        Args:
            name: Metric name (validated)
            value: Metric value (validated)
            dimensions: Optional dimensions (validated in helper)
            
        Returns:
            True if recorded, False if validation failed or rate limited
        """
        # Rate limiting check (Finding 5.4)
        if not self._check_rate_limit():
            return False  # Silently drop - metrics don't crash app
        
        try:
            # Security validations (imported via gateway per SIMA pattern)
            from gateway import validate_metric_name, validate_metric_value
            validate_metric_name(name)
            validate_metric_value(value)
            
            # Build key (this will validate dimensions)
            key = build_metric_key(name, dimensions)
            
            # Record metric
            self._metrics[key].append(value)
            
            # Apply memory limits (Finding 5.2)
            self._apply_memory_limit(self._metrics[key])
            
            # Update stats
            self._stats['total_metrics'] += 1
            self._stats['unique_metrics'] = len(self._metrics)
            return True
            
        except ValueError:
            # Security validation failed - log and reject
            # Note: Don't raise exception, metrics should never crash app
            return False
        except Exception:
            return False
    
    def increment_counter(self, name: str, value: int = 1) -> int:
        """
        Increment a counter metric.
        
        Args:
            name: Counter name
            value: Amount to increment (default: 1)
            
        Returns:
            New counter value
        """
        # Rate limiting
        if not self._check_rate_limit():
            return self._counters.get(name, 0)  # Return current value
        
        try:
            # Validate name
            from gateway import validate_metric_name
            validate_metric_name(name)
            
            self._counters[name] += value
            self._stats['counters'] = len(self._counters)
            return self._counters[name]
            
        except ValueError:
            return self._counters.get(name, 0)
        except Exception:
            return self._counters.get(name, 0)
    
    def set_gauge(self, name: str, value: float) -> bool:
        """
        Set a gauge metric.
        
        Args:
            name: Gauge name
            value: Gauge value
            
        Returns:
            True if set, False if validation failed
        """
        # Rate limiting
        if not self._check_rate_limit():
            return False
        
        try:
            # Validate
            from gateway import validate_metric_name, validate_metric_value
            validate_metric_name(name)
            validate_metric_value(value)
            
            self._gauges[name] = value
            self._stats['gauges'] = len(self._gauges)
            return True
            
        except ValueError:
            return False
        except Exception:
            return False
    
    def record_histogram(self, name: str, value: float) -> bool:
        """
        Record a histogram value.
        
        Args:
            name: Histogram name
            value: Value to record
            
        Returns:
            True if recorded, False if validation failed
        """
        # Rate limiting
        if not self._check_rate_limit():
            return False
        
        try:
            # Validate
            from gateway import validate_metric_name, validate_metric_value
            validate_metric_name(name)
            validate_metric_value(value)
            
            self._histograms[name].append(value)
            
            # Apply memory limits
            self._apply_memory_limit(self._histograms[name])
            
            self._stats['histograms'] = len(self._histograms)
            return True
            
        except ValueError:
            return False
        except Exception:
            return False
    
    def reset_metrics(self) -> bool:
        """
        Reset all metrics to initial state.
        
        Useful for:
        - Testing/debugging
        - Memory cleanup
        - Fresh start after errors
        
        Returns:
            True always
        """
        self._metrics.clear()
        self._counters.clear()
        self._gauges.clear()
        self._histograms.clear()
        self._dispatcher_timings.clear()
        self._dispatcher_call_counts.clear()
        self._rate_limiter.clear()
        
        self._stats = {
            'total_metrics': 0,
            'unique_metrics': 0,
            'counters': 0,
            'gauges': 0,
            'histograms': 0,
            'rate_limited_count': 0
        }
        
        self._response_metrics = ResponseMetrics()
        self._http_metrics = HTTPClientMetrics()
        self._circuit_breaker_metrics.clear()
        
        return True
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive metrics statistics.
        
        Returns:
            Dictionary with all statistics
        """
        stats = self._stats.copy()
        
        # Response metrics
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
        
        # HTTP metrics
        stats['http_metrics'] = {
            'total_requests': self._http_metrics.total_requests,
            'successful_requests': self._http_metrics.successful_requests,
            'failed_requests': self._http_metrics.failed_requests,
            'avg_response_time_ms': self._http_metrics.avg_response_time_ms,
            'requests_by_method': dict(self._http_metrics.requests_by_method),
            'requests_by_status': dict(self._http_metrics.requests_by_status)
        }
        
        # Circuit breaker metrics
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
        """
        Record response metric with validation.
        
        Args:
            response_type: Type of response
            status_code: HTTP status code
            duration_ms: Duration in milliseconds (validated)
        """
        # Rate limiting
        if not self._check_rate_limit():
            return
        
        # Input validation (Bug #13 fix)
        if duration_ms < 0:
            duration_ms = 0
        
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
        
        # Update timing stats (Bug #11 fix - division by zero check)
        if duration_ms > 0 and self._response_metrics.total_responses > 0:
            total_time = (
                self._response_metrics.avg_response_time_ms * 
                (self._response_metrics.total_responses - 1)
            ) + duration_ms
            self._response_metrics.avg_response_time_ms = (
                total_time / self._response_metrics.total_responses
            )
            
            if duration_ms < self._response_metrics.fastest_response_ms:
                self._response_metrics.fastest_response_ms = duration_ms
            if duration_ms > self._response_metrics.slowest_response_ms:
                self._response_metrics.slowest_response_ms = duration_ms
        
        # Calculate cache hit rate
        if self._response_metrics.total_responses > 0:
            self._response_metrics.cache_hit_rate = (
                self._response_metrics.cached_responses / 
                self._response_metrics.total_responses * 100
            )
    
    def get_response_metrics(self) -> Dict[str, Any]:
        """Get response metrics."""
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
        """
        Record HTTP client metric with validation.
        
        Args:
            method: HTTP method
            url: Request URL
            status_code: HTTP status code
            duration_ms: Duration in milliseconds
            response_size: Optional response size in bytes
        """
        # Rate limiting
        if not self._check_rate_limit():
            return
        
        # Input validation
        if duration_ms < 0:
            duration_ms = 0
        
        self._http_metrics.total_requests += 1
        self._http_metrics.requests_by_method[method] += 1
        self._http_metrics.requests_by_status[status_code] += 1
        
        # Success/failure tracking
        if 200 <= status_code < 400:
            self._http_metrics.successful_requests += 1
        else:
            self._http_metrics.failed_requests += 1
        
        # Update timing
        self._http_metrics.total_response_time_ms += duration_ms
        if self._http_metrics.total_requests > 0:
            self._http_metrics.avg_response_time_ms = (
                self._http_metrics.total_response_time_ms / 
                self._http_metrics.total_requests
            )
    
    def get_http_metrics(self) -> Dict[str, Any]:
        """Get HTTP client metrics."""
        return {
            'total_requests': self._http_metrics.total_requests,
            'successful_requests': self._http_metrics.successful_requests,
            'failed_requests': self._http_metrics.failed_requests,
            'avg_response_time_ms': self._http_metrics.avg_response_time_ms,
            'total_response_time_ms': self._http_metrics.total_response_time_ms,
            'requests_by_method': dict(self._http_metrics.requests_by_method),
            'requests_by_status': dict(self._http_metrics.requests_by_status),
            'success_rate': (
                (self._http_metrics.successful_requests / self._http_metrics.total_requests * 100)
                if self._http_metrics.total_requests > 0 else 0.0
            )
        }
    
    # ===== CIRCUIT BREAKER METRICS =====
    
    def record_circuit_breaker_event(self, circuit_name: str, event_type: str, success: bool = True):
        """
        Record circuit breaker event.
        
        Args:
            circuit_name: Name of circuit breaker
            event_type: Event type ('open', 'close', 'half_open')
            success: Whether operation succeeded
        """
        # Rate limiting
        if not self._check_rate_limit():
            return
        
        # Initialize circuit breaker if new
        if circuit_name not in self._circuit_breaker_metrics:
            self._circuit_breaker_metrics[circuit_name] = CircuitBreakerMetrics()
        
        cb = self._circuit_breaker_metrics[circuit_name]
        cb.total_requests += 1
        
        if success:
            cb.success_count += 1
            if event_type == 'close':
                cb.state = 'closed'
        else:
            cb.failure_count += 1
            cb.last_failure_time = time.time()
            if event_type == 'open':
                cb.state = 'open'
            elif event_type == 'half_open':
                cb.state = 'half_open'
    
    def get_circuit_breaker_metrics(self, circuit_name: Optional[str] = None) -> Dict[str, Any]:
        """Get circuit breaker metrics."""
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
                'failure_rate': (
                    (cb.failure_count / cb.total_requests * 100)
                    if cb.total_requests > 0 else 0.0
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
                    'failure_rate': (
                        (cb.failure_count / cb.total_requests * 100)
                        if cb.total_requests > 0 else 0.0
                    )
                }
                for name, cb in self._circuit_breaker_metrics.items()
            }
    
    # ===== DISPATCHER METRICS =====
    
    def record_dispatcher_timing(self, interface_name: str, operation_name: str, duration_ms: float) -> bool:
        """
        Record dispatcher timing with validation.
        
        Args:
            interface_name: Name of interface
            operation_name: Name of operation
            duration_ms: Duration in milliseconds
            
        Returns:
            True if recorded, False if validation failed
        """
        # Rate limiting
        if not self._check_rate_limit():
            return False
        
        # Input validation
        if duration_ms < 0:
            return False
        
        try:
            key = f"{interface_name}.{operation_name}"
            self._dispatcher_timings[key].append(duration_ms)
            self._dispatcher_call_counts[key] += 1
            
            # Apply memory limits
            self._apply_memory_limit(self._dispatcher_timings[key])
            
            return True
        except Exception:
            return False
    
    def get_dispatcher_stats(self) -> Dict[str, Any]:
        """Get dispatcher statistics."""
        interfaces = defaultdict(lambda: {'operations': {}, 'total_calls': 0})
        
        for key, count in self._dispatcher_call_counts.items():
            if '.' in key:
                interface, operation = key.split('.', 1)
                interfaces[interface]['operations'][operation] = count
                interfaces[interface]['total_calls'] += count
        
        # Calculate timing stats for each interface
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
        return {
            'timings': {k: v for k, v in self._dispatcher_timings.items()},
            'call_counts': dict(self._dispatcher_call_counts)
        }


# ===== SINGLETON INSTANCE =====

_MANAGER = MetricsCore()


# ===== EXPORTS =====

__all__ = [
    'MetricsCore',
    '_MANAGER',
]

# EOF
