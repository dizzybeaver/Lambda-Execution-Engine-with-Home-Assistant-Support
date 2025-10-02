"""
Circuit Breaker Core - Circuit Breaker Pattern Implementation
Version: 2025.09.30.02
Description: Circuit breaker implementation with shared utilities integration

ARCHITECTURE: CORE IMPLEMENTATION - INTERNAL ONLY
- Lazy-loaded by gateway.py
- Uses shared_utilities for operation metrics

OPTIMIZATION: Phase 1 Complete
- Integrated record_operation_metrics() from shared_utilities
- Consistent metric recording patterns
- Enhanced observability

Revolutionary Gateway Optimization: SUGA + LIGS + ZAFP Compatible

Copyright 2024 Anthropic PBC
Licensed under the Apache License, Version 2.0
"""

import time
from typing import Any, Callable, Dict
from threading import Lock
from enum import Enum


class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreaker:
    """Circuit breaker with configurable thresholds and metrics tracking."""
    
    def __init__(self, name: str, failure_threshold: int = 5, timeout: int = 60):
        self.name = name
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.state = CircuitState.CLOSED
        self.failures = 0
        self.last_failure_time = None
        self._lock = Lock()
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection and metrics."""
        start_time = time.time()
        success = True
        
        with self._lock:
            if self.state == CircuitState.OPEN:
                if self.last_failure_time and (time.time() - self.last_failure_time) > self.timeout:
                    self.state = CircuitState.HALF_OPEN
                else:
                    execution_time = (time.time() - start_time) * 1000
                    self._record_metrics("call_blocked", execution_time, False)
                    raise Exception(f"Circuit breaker {self.name} is OPEN")
        
        try:
            result = func(*args, **kwargs)
            execution_time = (time.time() - start_time) * 1000
            self._on_success()
            self._record_metrics("call", execution_time, True)
            return result
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            success = False
            self._on_failure()
            self._record_metrics("call", execution_time, False)
            raise e
    
    def _on_success(self):
        """Handle successful call with metrics."""
        with self._lock:
            self.failures = 0
            if self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.CLOSED
    
    def _on_failure(self):
        """Handle failed call with metrics."""
        with self._lock:
            self.failures += 1
            self.last_failure_time = time.time()
            if self.failures >= self.failure_threshold:
                self.state = CircuitState.OPEN
    
    def reset(self):
        """Reset circuit breaker state with metrics."""
        start_time = time.time()
        
        with self._lock:
            self.state = CircuitState.CLOSED
            self.failures = 0
            self.last_failure_time = None
        
        execution_time = (time.time() - start_time) * 1000
        self._record_metrics("reset", execution_time, True)
    
    def _record_metrics(self, operation: str, execution_time: float, success: bool):
        """Record operation metrics using shared utilities."""
        try:
            from .shared_utilities import record_operation_metrics
            record_operation_metrics(
                interface="circuit_breaker",
                operation=operation,
                execution_time=execution_time,
                success=success,
                circuit_name=self.name,
                circuit_state=self.state.value
            )
        except Exception:
            pass


class CircuitBreakerCore:
    """Manages circuit breakers with metrics integration."""
    
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


def _execute_get_implementation(name: str, failure_threshold: int = 5, 
                                timeout: int = 60, **kwargs) -> CircuitBreaker:
    """Execute get circuit breaker."""
    return _CIRCUIT_BREAKER_MANAGER.get(name, failure_threshold, timeout)


def _execute_call_implementation(name: str, func: Callable, args: tuple = (), **kwargs) -> Any:
    """Execute call with circuit breaker."""
    return _CIRCUIT_BREAKER_MANAGER.call(name, func, *args, **kwargs)


__all__ = [
    'CircuitState',
    'CircuitBreaker',
    '_execute_get_implementation',
    '_execute_call_implementation',
]

# EOF
