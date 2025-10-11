"""
metrics_specialized.py
Version: 2025.09.30.01
Description: Consolidated response, HTTP client, and circuit breaker metrics

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
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum
from collections import deque, defaultdict


# ===== RESPONSE METRICS =====

class ResponseType(Enum):
    SUCCESS = "success"
    ERROR = "error"
    TIMEOUT = "timeout"
    CACHED = "cached"
    FALLBACK = "fallback"


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
        return (self.successful_responses / self.total_responses * 100) if self.total_responses > 0 else 0.0


def record_response_metric(response_type: ResponseType, response_time_ms: float = 0.0, **kwargs):
    """Record response metric with shared pattern."""
    try:
        from shared_utilities import record_operation_metrics
        record_operation_metrics(
            interface="response",
            operation=response_type.value,
            execution_time=response_time_ms,
            success=(response_type == ResponseType.SUCCESS),
            **kwargs
        )
    except Exception:
        pass


# ===== HTTP CLIENT METRICS =====

class HTTPClientMetrics:
    """HTTP client metrics tracking."""
    
    def __init__(self):
        self._counters = defaultdict(int)
        self._totals = defaultdict(float)
        self._lock = threading.Lock()
    
    def record_request(self, success: bool, response_time_ms: float = 0.0, **dimensions):
        """Record HTTP request metric."""
        with self._lock:
            self._counters['total_requests'] += 1
            if success:
                self._counters['successful_requests'] += 1
            else:
                self._counters['failed_requests'] += 1
            
            if response_time_ms > 0:
                self._totals['response_time_ms'] += response_time_ms
                self._counters['response_time_recordings'] += 1
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get HTTP client metrics."""
        with self._lock:
            recordings = self._counters['response_time_recordings']
            avg_response_time = (self._totals['response_time_ms'] / recordings) if recordings > 0 else 0.0
            
            return {
                'counters': dict(self._counters),
                'averages': {
                    'response_time_ms': avg_response_time
                },
                'timestamp': time.time()
            }


_http_client_metrics = HTTPClientMetrics()


def record_http_request(success: bool, response_time_ms: float = 0.0, **dimensions):
    """Record HTTP request with shared pattern."""
    _http_client_metrics.record_request(success, response_time_ms, **dimensions)
    try:
        from shared_utilities import record_operation_metrics
        record_operation_metrics(
            interface="http_client",
            operation="request",
            execution_time=response_time_ms,
            success=success,
            **dimensions
        )
    except Exception:
        pass


def get_http_metrics() -> Dict[str, Any]:
    """Get HTTP client metrics."""
    return _http_client_metrics.get_metrics()


# ===== CIRCUIT BREAKER METRICS =====

class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitEvent(Enum):
    SUCCESS = "success"
    FAILURE = "failure"
    TIMEOUT = "timeout"
    STATE_CHANGE = "state_change"
    RECOVERY_ATTEMPT = "recovery_attempt"


@dataclass
class CircuitBreakerMetrics:
    """Circuit breaker metrics data structure."""
    current_state: CircuitState = CircuitState.CLOSED
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    timeout_requests: int = 0
    circuit_opens: int = 0
    circuit_closes: int = 0
    state_changes: int = 0
    avg_response_time_ms: float = 0.0
    
    def success_rate(self) -> float:
        return (self.successful_requests / self.total_requests * 100) if self.total_requests > 0 else 0.0


class CircuitBreakerMetricsManager:
    """Circuit breaker metrics management."""
    
    def __init__(self, circuit_name: str = "default"):
        self.circuit_name = circuit_name
        self._metrics = CircuitBreakerMetrics()
        self._lock = threading.Lock()
        self._event_history: deque = deque(maxlen=50)
    
    def record_request(self, success: bool, response_time_ms: float = 0.0, 
                      event_type: CircuitEvent = None):
        """Record circuit breaker request."""
        with self._lock:
            self._metrics.total_requests += 1
            
            if success:
                self._metrics.successful_requests += 1
            else:
                self._metrics.failed_requests += 1
            
            if response_time_ms > 0:
                total = self._metrics.avg_response_time_ms * (self._metrics.total_requests - 1)
                self._metrics.avg_response_time_ms = (total + response_time_ms) / self._metrics.total_requests
            
            self._event_history.append({
                'type': event_type.value if event_type else 'request',
                'success': success,
                'response_time_ms': response_time_ms,
                'timestamp': time.time()
            })
        
        try:
            from shared_utilities import record_operation_metrics
            record_operation_metrics(
                interface="circuit_breaker",
                operation="request",
                execution_time=response_time_ms,
                success=success,
                circuit_name=self.circuit_name
            )
        except Exception:
            pass
    
    def record_state_change(self, new_state: CircuitState):
        """Record state change."""
        with self._lock:
            self._metrics.current_state = new_state
            self._metrics.state_changes += 1
            
            if new_state == CircuitState.OPEN:
                self._metrics.circuit_opens += 1
            elif new_state == CircuitState.CLOSED:
                self._metrics.circuit_closes += 1
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get circuit breaker metrics."""
        with self._lock:
            return {
                'circuit_name': self.circuit_name,
                'state': self._metrics.current_state.value,
                'requests': {
                    'total': self._metrics.total_requests,
                    'successful': self._metrics.successful_requests,
                    'failed': self._metrics.failed_requests,
                    'success_rate': self._metrics.success_rate()
                },
                'circuit_actions': {
                    'opens': self._metrics.circuit_opens,
                    'closes': self._metrics.circuit_closes,
                    'state_changes': self._metrics.state_changes
                },
                'performance': {
                    'avg_response_time_ms': self._metrics.avg_response_time_ms
                },
                'recent_events': list(self._event_history)[-10:]
            }


_circuit_breaker_managers: Dict[str, CircuitBreakerMetricsManager] = {}
_cb_lock = threading.Lock()


def get_circuit_breaker_manager(circuit_name: str = "default") -> CircuitBreakerMetricsManager:
    """Get or create circuit breaker metrics manager."""
    if circuit_name not in _circuit_breaker_managers:
        with _cb_lock:
            if circuit_name not in _circuit_breaker_managers:
                _circuit_breaker_managers[circuit_name] = CircuitBreakerMetricsManager(circuit_name)
    return _circuit_breaker_managers[circuit_name]


def record_circuit_request(circuit_name: str, success: bool, response_time_ms: float = 0.0):
    """Record circuit breaker request."""
    manager = get_circuit_breaker_manager(circuit_name)
    manager.record_request(success, response_time_ms)


def get_circuit_metrics(circuit_name: str = "default") -> Dict[str, Any]:
    """Get circuit breaker metrics."""
    manager = get_circuit_breaker_manager(circuit_name)
    return manager.get_metrics()


__all__ = [
    'ResponseType',
    'ResponseMetrics',
    'record_response_metric',
    'HTTPClientMetrics',
    'record_http_request',
    'get_http_metrics',
    'CircuitState',
    'CircuitEvent',
    'CircuitBreakerMetrics',
    'CircuitBreakerMetricsManager',
    'get_circuit_breaker_manager',
    'record_circuit_request',
    'get_circuit_metrics',
]

# EOF
