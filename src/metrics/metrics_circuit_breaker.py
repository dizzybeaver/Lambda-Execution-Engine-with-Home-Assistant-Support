"""
metrics_circuit_breaker.py - Circuit Breaker Statistics
Version: 2025.9.18-CONSOLIDATED
Description: Failure patterns and state changes metrics category

CONSOLIDATES metrics from:
- interfaces.py circuit breaker patterns
- Various circuit breaker implementations
- Scattered failure tracking patterns

ELIMINATES:
- Duplicate circuit breaker metrics collection
- Scattered failure rate tracking patterns
- Redundant state change statistics
"""

import logging
import time
import threading
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)

# ===== SECTION 1: CIRCUIT BREAKER METRICS TYPES =====

class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class CircuitEvent(Enum):
    """Circuit breaker events."""
    SUCCESS = "success"
    FAILURE = "failure"
    TIMEOUT = "timeout"
    STATE_CHANGE = "state_change"
    THRESHOLD_EXCEEDED = "threshold_exceeded"
    RECOVERY_ATTEMPT = "recovery_attempt"

@dataclass
class CircuitBreakerMetrics:
    """CONSOLIDATED: Circuit breaker monitoring metrics."""
    # State tracking
    current_state: CircuitState = CircuitState.CLOSED
    state_changes: int = 0
    time_in_open_ms: float = 0.0
    time_in_half_open_ms: float = 0.0
    time_in_closed_ms: float = 0.0
    
    # Request tracking
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    timeout_requests: int = 0
    
    # Circuit actions
    circuit_opens: int = 0
    circuit_closes: int = 0
    half_open_attempts: int = 0
    recovery_successes: int = 0
    recovery_failures: int = 0
    
    # Performance metrics
    avg_response_time_ms: float = 0.0
    avg_failure_time_ms: float = 0.0
    
    # Thresholds and configuration
    failure_threshold: int = 5
    recovery_timeout_ms: float = 60000.0  # 1 minute
    request_timeout_ms: float = 30000.0   # 30 seconds
    
    # Tracking
    first_request_time: Optional[float] = None
    last_request_time: Optional[float] = None
    last_state_change_time: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'state': {
                'current': self.current_state.value,
                'changes': self.state_changes,
                'time_distribution_ms': {
                    'closed': self.time_in_closed_ms,
                    'open': self.time_in_open_ms,
                    'half_open': self.time_in_half_open_ms
                },
                'last_change': self.last_state_change_time
            },
            'requests': {
                'total': self.total_requests,
                'successful': self.successful_requests,
                'failed': self.failed_requests,
                'timeouts': self.timeout_requests,
                'success_rate': self.success_rate(),
                'failure_rate': self.failure_rate()
            },
            'circuit_actions': {
                'opens': self.circuit_opens,
                'closes': self.circuit_closes,
                'half_open_attempts': self.half_open_attempts,
                'recovery_successes': self.recovery_successes,
                'recovery_failures': self.recovery_failures,
                'recovery_success_rate': self.recovery_success_rate()
            },
            'performance': {
                'avg_response_time_ms': self.avg_response_time_ms,
                'avg_failure_time_ms': self.avg_failure_time_ms
            },
            'configuration': {
                'failure_threshold': self.failure_threshold,
                'recovery_timeout_ms': self.recovery_timeout_ms,
                'request_timeout_ms': self.request_timeout_ms
            },
            'timeline': {
                'first_request': self.first_request_time,
                'last_request': self.last_request_time,
                'duration_seconds': self.duration_seconds()
            }
        }
    
    def success_rate(self) -> float:
        """Calculate success rate."""
        return (self.successful_requests / self.total_requests * 100) if self.total_requests > 0 else 0.0
    
    def failure_rate(self) -> float:
        """Calculate failure rate."""
        return (self.failed_requests / self.total_requests * 100) if self.total_requests > 0 else 0.0
    
    def recovery_success_rate(self) -> float:
        """Calculate recovery success rate."""
        total_recoveries = self.recovery_successes + self.recovery_failures
        return (self.recovery_successes / total_recoveries * 100) if total_recoveries > 0 else 0.0
    
    def duration_seconds(self) -> float:
        """Calculate total duration."""
        if self.first_request_time and self.last_request_time:
            return self.last_request_time - self.first_request_time
        return 0.0

class CircuitBreakerMetricsManager:
    """CONSOLIDATED: Circuit breaker metrics collection and management."""
    
    def __init__(self, circuit_name: str = "default"):
        self.circuit_name = circuit_name
        self._metrics = CircuitBreakerMetrics()
        self._lock = threading.Lock()
        self._event_history: List[Dict[str, Any]] = []
        
        # State timing
        self._current_state_start_time = time.time()
        
        # Configuration
        self._max_history = 50
        self._cost_protection_active = False
        
        logger.debug(f"Circuit breaker metrics manager initialized for '{circuit_name}'")
    
    def record_request(self, success: bool, response_time_ms: float = 0.0, 
                      event_type: CircuitEvent = None) -> None:
        """Record a circuit breaker request."""
        current_time = time.time()
        
        with self._lock:
            if self._cost_protection_active:
                return
            
            # Update request counts
            self._metrics.total_requests += 1
            if success:
                self._metrics.successful_requests += 1
                if event_type is None:
                    event_type = CircuitEvent.SUCCESS
            else:
                self._metrics.failed_requests += 1
                if event_type is None:
                    event_type = CircuitEvent.FAILURE
            
            # Update response time
            if response_time_ms > 0:
                if success:
                    total_time = self._metrics.avg_response_time_ms * (self._metrics.successful_requests - 1)
                    self._metrics.avg_response_time_ms = (total_time + response_time_ms) / self._metrics.successful_requests
                else:
                    total_time = self._metrics.avg_failure_time_ms * (self._metrics.failed_requests - 1)
                    self._metrics.avg_failure_time_ms = (total_time + response_time_ms) / self._metrics.failed_requests
            
            # Update timeline
            if not self._metrics.first_request_time:
                self._metrics.first_request_time = current_time
            self._metrics.last_request_time = current_time
            
            # Store event
            self._store_event({
                'type': event_type.value,
                'success': success,
                'response_time_ms': response_time_ms,
                'timestamp': current_time,
                'state': self._metrics.current_state.value
            })
    
    def record_state_change(self, new_state: CircuitState, reason: str = None) -> None:
        """Record circuit breaker state change."""
        current_time = time.time()
        
        with self._lock:
            if self._cost_protection_active:
                return
            
            old_state = self._metrics.current_state
            
            # Update state timing
            state_duration_ms = (current_time - self._current_state_start_time) * 1000
            if old_state == CircuitState.CLOSED:
                self._metrics.time_in_closed_ms += state_duration_ms
            elif old_state == CircuitState.OPEN:
                self._metrics.time_in_open_ms += state_duration_ms
            elif old_state == CircuitState.HALF_OPEN:
                self._metrics.time_in_half_open_ms += state_duration_ms
            
            # Update state
            self._metrics.current_state = new_state
            self._metrics.state_changes += 1
            self._metrics.last_state_change_time = current_time
            self._current_state_start_time = current_time
            
            # Update specific counters
            if new_state == CircuitState.OPEN:
                self._metrics.circuit_opens += 1
            elif new_state == CircuitState.CLOSED and old_state != CircuitState.CLOSED:
                self._metrics.circuit_closes += 1
            elif new_state == CircuitState.HALF_OPEN:
                self._metrics.half_open_attempts += 1
            
            # Store event
            self._store_event({
                'type': CircuitEvent.STATE_CHANGE.value,
                'old_state': old_state.value,
                'new_state': new_state.value,
                'reason': reason,
                'timestamp': current_time,
                'state_duration_ms': state_duration_ms
            })
    
    def record_timeout(self, timeout_ms: float = 0.0) -> None:
        """Record request timeout."""
        current_time = time.time()
        
        with self._lock:
            if self._cost_protection_active:
                return
            
            self._metrics.timeout_requests += 1
            self._metrics.failed_requests += 1
            self._metrics.total_requests += 1
            
            # Update timeline
            if not self._metrics.first_request_time:
                self._metrics.first_request_time = current_time
            self._metrics.last_request_time = current_time
            
            # Store event
            self._store_event({
                'type': CircuitEvent.TIMEOUT.value,
                'timeout_ms': timeout_ms,
                'timestamp': current_time,
                'state': self._metrics.current_state.value
            })
    
    def record_recovery_attempt(self, success: bool) -> None:
        """Record recovery attempt."""
        current_time = time.time()
        
        with self._lock:
            if self._cost_protection_active:
                return
            
            if success:
                self._metrics.recovery_successes += 1
            else:
                self._metrics.recovery_failures += 1
            
            # Store event
            self._store_event({
                'type': CircuitEvent.RECOVERY_ATTEMPT.value,
                'success': success,
                'timestamp': current_time,
                'state': self._metrics.current_state.value
            })
    
    def _store_event(self, event: Dict[str, Any]) -> None:
        """Store circuit breaker event in history."""
        self._event_history.append(event)
        
        # Maintain history size
        if len(self._event_history) > self._max_history:
            self._event_history = self._event_history[-self._max_history:]
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get comprehensive circuit breaker metrics."""
        with self._lock:
            metrics_data = self._metrics.to_dict()
            metrics_data['circuit_name'] = self.circuit_name
            metrics_data['recent_events'] = self._event_history[-10:]  # Last 10 events
            metrics_data['cost_protection_active'] = self._cost_protection_active
            return metrics_data
    
    def reset_metrics(self) -> None:
        """Reset circuit breaker metrics."""
        with self._lock:
            old_state = self._metrics.current_state
            self._metrics = CircuitBreakerMetrics()
            self._metrics.current_state = old_state  # Preserve current state
            self._event_history.clear()
            self._current_state_start_time = time.time()
    
    def set_cost_protection(self, active: bool) -> None:
        """Set cost protection state."""
        with self._lock:
            self._cost_protection_active = active

# ===== SECTION 2: GLOBAL MANAGERS =====

_circuit_breaker_managers: Dict[str, CircuitBreakerMetricsManager] = {}
_managers_lock = threading.Lock()

def get_circuit_breaker_metrics_manager(circuit_name: str = "default") -> CircuitBreakerMetricsManager:
    """Get or create circuit breaker metrics manager for specific circuit."""
    global _circuit_breaker_managers
    
    if circuit_name not in _circuit_breaker_managers:
        with _managers_lock:
            if circuit_name not in _circuit_breaker_managers:
                _circuit_breaker_managers[circuit_name] = CircuitBreakerMetricsManager(circuit_name)
    
    return _circuit_breaker_managers[circuit_name]

# ===== SECTION 3: MODULE FUNCTIONS =====

def record_circuit_success(circuit_name: str = "default", response_time_ms: float = 0.0) -> None:
    """Record successful circuit breaker request."""
    get_circuit_breaker_metrics_manager(circuit_name).record_request(True, response_time_ms, CircuitEvent.SUCCESS)

def record_circuit_failure(circuit_name: str = "default", response_time_ms: float = 0.0) -> None:
    """Record failed circuit breaker request."""
    get_circuit_breaker_metrics_manager(circuit_name).record_request(False, response_time_ms, CircuitEvent.FAILURE)

def record_circuit_timeout(circuit_name: str = "default", timeout_ms: float = 0.0) -> None:
    """Record circuit breaker timeout."""
    get_circuit_breaker_metrics_manager(circuit_name).record_timeout(timeout_ms)

def record_circuit_state_change(new_state: CircuitState, circuit_name: str = "default", reason: str = None) -> None:
    """Record circuit breaker state change."""
    get_circuit_breaker_metrics_manager(circuit_name).record_state_change(new_state, reason)

def record_circuit_recovery(success: bool, circuit_name: str = "default") -> None:
    """Record circuit breaker recovery attempt."""
    get_circuit_breaker_metrics_manager(circuit_name).record_recovery_attempt(success)

def get_circuit_breaker_metrics(circuit_name: str = "default") -> Dict[str, Any]:
    """Get circuit breaker metrics for specific circuit."""
    return get_circuit_breaker_metrics_manager(circuit_name).get_metrics()

def get_all_circuit_metrics() -> Dict[str, Dict[str, Any]]:
    """Get metrics for all circuit breakers."""
    with _managers_lock:
        return {name: manager.get_metrics() for name, manager in _circuit_breaker_managers.items()}

def reset_circuit_breaker_metrics(circuit_name: str = "default") -> None:
    """Reset circuit breaker metrics."""
    get_circuit_breaker_metrics_manager(circuit_name).reset_metrics()

# ===== SECTION 4: MODULE EXPORTS =====

__all__ = [
    # Classes and enums
    'CircuitBreakerMetrics',
    'CircuitBreakerMetricsManager',
    'CircuitState',
    'CircuitEvent',
    
    # Manager access
    'get_circuit_breaker_metrics_manager',
    
    # Convenience functions
    'record_circuit_success',
    'record_circuit_failure',
    'record_circuit_timeout',
    'record_circuit_state_change',
    'record_circuit_recovery',
    'get_circuit_breaker_metrics',
    'get_all_circuit_metrics',
    'reset_circuit_breaker_metrics'
]

# EOF
