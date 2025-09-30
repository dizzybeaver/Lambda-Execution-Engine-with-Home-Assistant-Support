"""
Circuit Breaker Core - Circuit Breaker Pattern Implementation
Version: 2025.09.29.01
Daily Revision: 001
"""

import time
from typing import Callable, Any, Dict, Optional
from enum import Enum
from threading import Lock

class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class CircuitBreaker:
    """Circuit breaker for fault tolerance."""
    
    def __init__(self, name: str, failure_threshold: int = 5, timeout: int = 60):
        self.name = name
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.state = CircuitState.CLOSED
        self.failures = 0
        self.last_failure_time = None
        self._lock = Lock()
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection."""
        with self._lock:
            if self.state == CircuitState.OPEN:
                if self._should_attempt_reset():
                    self.state = CircuitState.HALF_OPEN
                else:
                    raise Exception(f"Circuit breaker {self.name} is OPEN")
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e
    
    def _on_success(self):
        """Handle successful call."""
        with self._lock:
            self.failures = 0
            if self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.CLOSED
    
    def _on_failure(self):
        """Handle failed call."""
        with self._lock:
            self.failures += 1
            self.last_failure_time = time.time()
            
            if self.failures >= self.failure_threshold:
                self.state = CircuitState.OPEN
    
    def _should_attempt_reset(self) -> bool:
        """Check if should attempt reset."""
        if self.last_failure_time is None:
            return False
        return (time.time() - self.last_failure_time) >= self.timeout
    
    def get_state(self) -> Dict[str, Any]:
        """Get circuit breaker state."""
        return {
            'name': self.name,
            'state': self.state.value,
            'failures': self.failures,
            'threshold': self.failure_threshold
        }
    
    def reset(self):
        """Manually reset circuit breaker."""
        with self._lock:
            self.state = CircuitState.CLOSED
            self.failures = 0
            self.last_failure_time = None

class CircuitBreakerCore:
    """Manages circuit breakers."""
    
    def __init__(self):
        self._breakers: Dict[str, CircuitBreaker] = {}
        self._lock = Lock()
    
    def get(self, name: str, failure_threshold: int = 5, timeout: int = 60) -> CircuitBreaker:
        """Get or create circuit breaker."""
        if name not in self._breakers:
            with self._lock:
                if name not in self._breakers:
                    self._breakers[name] = CircuitBreaker(name, failure_threshold, timeout)
        return self._breakers[name]
    
    def call(self, name: str, func: Callable, *args, **kwargs) -> Any:
        """Call function with circuit breaker."""
        breaker = self.get(name)
        return breaker.call(func, *args, **kwargs)

_CIRCUIT_BREAKER_MANAGER = CircuitBreakerCore()

def _execute_get_implementation(name: str, failure_threshold: int = 5, timeout: int = 60, **kwargs) -> CircuitBreaker:
    """Execute get circuit breaker."""
    return _CIRCUIT_BREAKER_MANAGER.get(name, failure_threshold, timeout)

def _execute_call_implementation(name: str, func: Callable, args: tuple = (), **kwargs) -> Any:
    """Execute call with circuit breaker."""
    return _CIRCUIT_BREAKER_MANAGER.call(name, func, *args, **kwargs)

#EOF
