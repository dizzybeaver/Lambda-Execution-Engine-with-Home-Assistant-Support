"""
circuit_breaker_core.py - Circuit Breaker Pattern Implementation
Version: 2025.10.14.01

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
from typing import Any, Callable, Dict
from threading import Lock
from enum import Enum


class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreaker:
    """Circuit breaker with error handling and state management."""
    
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
        from shared_utilities import (
            create_operation_context, close_operation_context, 
            handle_operation_error, record_operation_metrics
        )
        
        context = create_operation_context('circuit_breaker', 'call', circuit_name=self.name)
        start_time = time.time()
        
        with self._lock:
            if self.state == CircuitState.OPEN:
                if self.last_failure_time and (time.time() - self.last_failure_time) > self.timeout:
                    self.state = CircuitState.HALF_OPEN
                else:
                    execution_time = (time.time() - start_time) * 1000
                    record_operation_metrics(
                        interface='circuit_breaker',
                        operation='call_blocked',
                        execution_time=execution_time,
                        success=False,
                        circuit_name=self.name,
                        circuit_state=self.state.value
                    )
                    close_operation_context(context, success=False)
                    return handle_operation_error(
                        'circuit_breaker', 'call',
                        Exception(f"Circuit breaker {self.name} is OPEN"),
                        context['correlation_id']
                    )
        
        try:
            result = func(*args, **kwargs)
            execution_time = (time.time() - start_time) * 1000
            self._on_success()
            
            record_operation_metrics(
                interface='circuit_breaker',
                operation='call',
                execution_time=execution_time,
                success=True,
                circuit_name=self.name,
                circuit_state=self.state.value
            )
            
            close_operation_context(context, success=True, result=result)
            return result
            
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            self._on_failure()
            
            record_operation_metrics(
                interface='circuit_breaker',
                operation='call',
                execution_time=execution_time,
                success=False,
                circuit_name=self.name,
                circuit_state=self.state.value
            )
            
            close_operation_context(context, success=False)
            return handle_operation_error('circuit_breaker', 'call', e, context['correlation_id'])
    
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
    
    def reset(self):
        """Reset circuit breaker state."""
        from shared_utilities import record_operation_metrics
        
        start_time = time.time()
        
        with self._lock:
            self.state = CircuitState.CLOSED
            self.failures = 0
            self.last_failure_time = None
        
        execution_time = (time.time() - start_time) * 1000
        record_operation_metrics(
            interface='circuit_breaker',
            operation='reset',
            execution_time=execution_time,
            success=True,
            circuit_name=self.name,
            circuit_state=self.state.value
        )
    
    def get_state(self) -> Dict[str, Any]:
        """Get current circuit breaker state."""
        with self._lock:
            return {
                'name': self.name,
                'state': self.state.value,
                'failures': self.failures,
                'threshold': self.failure_threshold,
                'timeout': self.timeout,
                'last_failure': self.last_failure_time
            }


class CircuitBreakerCore:
    """Manages circuit breakers with shared_utilities integration."""
    
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
        """Call function with circuit breaker protection."""
        breaker = self.get(name)
        return breaker.call(func, *args, **kwargs)
    
    def get_all_states(self) -> Dict[str, Dict[str, Any]]:
        """Get states of all circuit breakers."""
        with self._lock:
            return {
                name: breaker.get_state()
                for name, breaker in self._breakers.items()
            }
    
    def reset_all(self):
        """Reset all circuit breakers."""
        with self._lock:
            for breaker in self._breakers.values():
                breaker.reset()


# ===== SINGLETON INSTANCE =====

_CIRCUIT_BREAKER_MANAGER = CircuitBreakerCore()


# ===== GATEWAY IMPLEMENTATION FUNCTIONS =====
# Function names MUST match gateway.py _OPERATION_REGISTRY exactly

def get_breaker_implementation(name: str, failure_threshold: int = 5, 
                               timeout: int = 60, **kwargs) -> Dict[str, Any]:
    """Execute get circuit breaker operation.
    
    Returns circuit breaker state dict instead of CircuitBreaker object
    to maintain gateway interface consistency.
    """
    breaker = _CIRCUIT_BREAKER_MANAGER.get(name, failure_threshold, timeout)
    return breaker.get_state()


def execute_with_breaker_implementation(name: str, func: Callable, 
                                       args: tuple = (), **kwargs) -> Any:
    """Execute call with circuit breaker protection."""
    return _CIRCUIT_BREAKER_MANAGER.call(name, func, *args, **kwargs)


def get_all_states_implementation(**kwargs) -> Dict[str, Dict[str, Any]]:
    """Execute get all circuit breaker states."""
    return _CIRCUIT_BREAKER_MANAGER.get_all_states()


def reset_all_implementation(**kwargs):
    """Execute reset all circuit breakers."""
    _CIRCUIT_BREAKER_MANAGER.reset_all()


# ===== EXPORTS =====

__all__ = [
    'CircuitState',
    'CircuitBreaker',
    'CircuitBreakerCore',
    'get_breaker_implementation',
    'execute_with_breaker_implementation',
    'get_all_states_implementation',
    'reset_all_implementation',
]

# EOF
