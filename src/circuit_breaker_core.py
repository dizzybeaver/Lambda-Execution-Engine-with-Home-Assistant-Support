"""
circuit_breaker_core.py - Circuit Breaker Pattern Implementation
Version: 2025.10.17.01
Description: Circuit breaker with utility cross-interface integration for metrics

CHANGELOG:
- 2025.10.17.01: Added design decision documentation for threading and direct gateway access
- 2025.10.16.01: Fixed record_operation_metrics calls - changed execution_time 
                 to duration parameter, removed unsupported parameters

DESIGN DECISIONS DOCUMENTED:

1. Threading Locks in Lambda Environment:
   DESIGN DECISION: Uses threading.Lock() despite Lambda being single-threaded
   Reason: Future-proofing for potential multi-threaded execution environments
   Lambda Context: Adds minimal overhead in single-threaded Lambda containers
   NOT A BUG: Intentional defensive programming for portability
   
2. Direct Gateway Access (No Interface Router):
   DESIGN DECISION: Gateway registry points directly to this file (bypasses interface router)
   Reason: Circuit breaker is performance-critical hot path, called frequently
   SUGA-ISP Compliance: Acceptable for performance-critical internal infrastructure
   NOT A BUG: Documented in gateway_core.py as intentional optimization

3. Import from shared_utilities:
   DESIGN DECISION: Imports record_operation_metrics from shared_utilities (now utility_cross_interface)
   Reason: Cross-interface utility functions for metrics recording
   Pattern: Internal infrastructure components may use cross-interface utilities
   NOT A BUG: Shared utilities are designed for this use case

Copyright 2025 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

import time
from typing import Callable, Dict, Any, Optional
from threading import Lock
from enum import Enum


# ===== CIRCUIT BREAKER STATE =====

class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"         # Failing, reject calls
    HALF_OPEN = "half_open"  # Testing recovery


# ===== CIRCUIT BREAKER =====

class CircuitBreaker:
    """
    Single circuit breaker instance with cross-interface utility integration.
    
    DESIGN DECISION: Uses threading.Lock()
    Reason: Thread-safety for future-proofing, minimal overhead in Lambda
    NOT A BUG: Intentional defensive programming pattern
    """
    
    def __init__(self, name: str, failure_threshold: int = 5, timeout: int = 60):
        self.name = name
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.state = CircuitState.CLOSED
        self.failures = 0
        self.last_failure_time = None
        self._lock = Lock()
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with circuit breaker protection.
        
        DESIGN DECISION: Imports shared_utilities inside method
        Reason: Lazy import to avoid circular dependencies
        Pattern: Gateway imports happen lazily in infrastructure components
        """
        # Check if circuit is open
        with self._lock:
            if self.state == CircuitState.OPEN:
                if time.time() - self.last_failure_time > self.timeout:
                    self.state = CircuitState.HALF_OPEN
                else:
                    raise Exception(f"Circuit breaker '{self.name}' is OPEN")
        
        # Import utilities for metrics recording (lazy to avoid circular imports)
        from shared_utilities import (
            create_operation_context,
            close_operation_context,
            handle_operation_error,
            record_operation_metrics
        )
        
        # Create operation context
        context = create_operation_context('circuit_breaker', 'call', correlation_id=None)
        start_time = time.time()
        
        try:
            # Execute the function
            result = func(*args, **kwargs)
            
            # Record success
            duration_ms = (time.time() - start_time) * 1000
            record_operation_metrics(
                interface='circuit_breaker',
                operation='call',
                duration=duration_ms,
                success=True,
                correlation_id=context.get('correlation_id')
            )
            
            self._on_success()
            close_operation_context(context)
            return result
            
        except Exception as e:
            # Record failure
            duration_ms = (time.time() - start_time) * 1000
            record_operation_metrics(
                interface='circuit_breaker',
                operation='call',
                duration=duration_ms,
                success=False,
                correlation_id=context.get('correlation_id')
            )
            
            self._on_failure()
            handle_operation_error(context, e)
            raise
    
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
        """
        Reset circuit breaker state.
        
        DESIGN DECISION: Uses shared_utilities for metrics
        Reason: Consistent metrics recording across all operations
        """
        from shared_utilities import record_operation_metrics
        
        start_time = time.time()
        
        with self._lock:
            self.state = CircuitState.CLOSED
            self.failures = 0
            self.last_failure_time = None
        
        duration_ms = (time.time() - start_time) * 1000
        # FIXED: Changed execution_time to duration, removed extra params
        record_operation_metrics(
            interface='circuit_breaker',
            operation='reset',
            duration=duration_ms,
            success=True
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
    """
    Manages circuit breakers with cross-interface utility integration.
    
    DESIGN DECISION: Uses threading.Lock()
    Reason: Thread-safe dictionary operations for future-proofing
    Lambda Context: Single-threaded per container, lock adds minimal overhead
    NOT A BUG: Defensive programming for portability
    """
    
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
#
# DESIGN DECISION: These functions are called directly by gateway_core.py
# Reason: Performance-critical hot path, bypasses interface router
# SUGA-ISP Compliance: Documented exception for infrastructure components
# NOT A BUG: See gateway_core.py documentation for rationale

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
