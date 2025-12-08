"""
circuit_breaker_core.py - Circuit Breaker Pattern Implementation
Version: 2025.10.22.01
Description: Circuit breaker 

DESIGN DECISIONS:

1. NO Threading Locks (AP-08, DEC-04):
   Lambda is single-threaded per container
   Threading locks add overhead without benefit
   Rate limiting provides DoS protection
   This is the correct Lambda pattern

2. Direct Gateway Access (Performance Optimization):
   Gateway registry points directly to this file
   Bypasses interface router for performance-critical path
   Circuit breaker called frequently, optimization justified
   SIMA-compliant exception for infrastructure components

3. Rate Limiting Instead of Locks:
   1000 ops/sec limit (higher than WebSocket's 300)
   Circuit breaker is infrastructure, needs higher throughput
   Provides DoS protection without lock overhead

REF-IDs:
- AP-08: No threading locks (CRITICAL)
- DEC-04: Lambda single-threaded model
- LESS-17: Threading locks unnecessary in Lambda
- LESS-18: SINGLETON pattern for lifecycle management
- LESS-21: Rate limiting essential for DoS protection

Copyright 2025 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

import time
import uuid
from typing import Callable, Dict, Any, Optional
from collections import deque
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
    Single circuit breaker instance.
    
    COMPLIANCE:
    - AP-08: No threading locks (Lambda single-threaded)
    - DEC-04: Lambda single-threaded model
    - LESS-21: Rate limiting for DoS protection
    """
    
    def __init__(self, name: str, failure_threshold: int = 5, timeout: int = 60):
        self.name = name
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.state = CircuitState.CLOSED
        self.failures = 0
        self.last_failure_time = None
        
        # Statistics
        self._total_calls = 0
        self._successful_calls = 0
        self._failed_calls = 0
        self._rejected_calls = 0
    
    def call(self, func: Callable, rate_limit_check: Callable, *args, **kwargs) -> Any:
        """
        Execute function with circuit breaker protection.
        
        Args:
            func: Function to execute
            rate_limit_check: Callable that returns True if within rate limit
            *args, **kwargs: Arguments for func
        
        Returns:
            Function result
            
        Raises:
            Exception: If circuit is open or function fails
        """
        # Check rate limit first
        if not rate_limit_check():
            raise Exception(f"Circuit breaker '{self.name}': Rate limit exceeded")
        
        self._total_calls += 1
        
        # Check if circuit is open
        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time > self.timeout:
                self.state = CircuitState.HALF_OPEN
            else:
                self._rejected_calls += 1
                raise Exception(f"Circuit breaker '{self.name}' is OPEN")
        
        # Create operation context
        correlation_id = str(uuid.uuid4())
        start_time = time.time()
        
        try:
            # Import from gateway for cross-interface utilities
            from gateway import execute_operation, GatewayInterface
            
            # Execute the function
            result = func(*args, **kwargs)
            
            # Record success metrics via gateway
            duration_ms = (time.time() - start_time) * 1000
            try:
                execute_operation(
                    GatewayInterface.METRICS,
                    'record_metric',
                    name='circuit_breaker_call_duration',
                    value=duration_ms,
                    tags={
                        'operation': 'call',
                        'success': 'true',
                        'correlation_id': correlation_id
                    }
                )
            except Exception:
                pass  # Metrics failure should not crash circuit breaker
            
            self._on_success()
            return result
            
        except ImportError:
            # Fallback: execute without gateway
            try:
                result = func(*args, **kwargs)
                self._on_success()
                return result
            except Exception as e:
                self._on_failure()
                raise
        
        except Exception as e:
            # Record failure metrics via gateway
            duration_ms = (time.time() - start_time) * 1000
            try:
                from gateway import execute_operation, GatewayInterface
                execute_operation(
                    GatewayInterface.METRICS,
                    'record_metric',
                    name='circuit_breaker_call_duration',
                    value=duration_ms,
                    tags={
                        'operation': 'call',
                        'success': 'false',
                        'correlation_id': correlation_id
                    }
                )
                
                execute_operation(
                    GatewayInterface.LOGGING,
                    'log_error',
                    message=f"Circuit breaker call failed: {str(e)}",
                    extra={'correlation_id': correlation_id}
                )
            except Exception:
                pass  # Metrics/logging failure should not crash circuit breaker
            
            self._on_failure()
            raise
    
    def _on_success(self):
        """Handle successful call (no locks needed in single-threaded Lambda)."""
        self._successful_calls += 1
        self.failures = 0
        if self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.CLOSED
    
    def _on_failure(self):
        """Handle failed call (no locks needed in single-threaded Lambda)."""
        self._failed_calls += 1
        self.failures += 1
        self.last_failure_time = time.time()
        if self.failures >= self.failure_threshold:
            self.state = CircuitState.OPEN
    
    def reset(self):
        """Reset circuit breaker state."""
        self.state = CircuitState.CLOSED
        self.failures = 0
        self.last_failure_time = None
        # Don't reset statistics - preserve for diagnostics
    
    def get_state(self) -> Dict[str, Any]:
        """Get current circuit breaker state."""
        return {
            'name': self.name,
            'state': self.state.value,
            'failures': self.failures,
            'threshold': self.failure_threshold,
            'timeout': self.timeout,
            'last_failure': self.last_failure_time,
            'statistics': {
                'total_calls': self._total_calls,
                'successful_calls': self._successful_calls,
                'failed_calls': self._failed_calls,
                'rejected_calls': self._rejected_calls
            }
        }


class CircuitBreakerCore:
    """
    Manages circuit breakers with SINGLETON pattern and rate limiting.
    
    COMPLIANCE:
    - AP-08: No threading locks (Lambda single-threaded)
    - DEC-04: Lambda single-threaded model
    - LESS-18: SINGLETON pattern via get_circuit_breaker_manager()
    - LESS-21: Rate limiting (1000 ops/sec)
    """
    
    def __init__(self):
        self._breakers: Dict[str, CircuitBreaker] = {}
        
        # Rate limiting (1000 ops/sec - higher for infrastructure)
        # LESS-21: Rate limiting essential for DoS protection
        self._rate_limiter = deque(maxlen=1000)  # 1000 ops/sec window
        self._rate_limit_window_ms = 1000  # 1 second window
        self._rate_limited_count = 0
        
        # Statistics
        self._total_operations = 0
    
    def _check_rate_limit(self) -> bool:
        """
        Check if operation is within rate limit.
        
        LESS-21: Uses deque for efficient rate limiting.
        No threading locks needed (AP-08, DEC-04).
        
        Returns:
            bool: True if operation allowed, False if rate limited
        """
        now = time.time() * 1000  # milliseconds
        
        # Remove expired timestamps
        while self._rate_limiter and (now - self._rate_limiter[0]) > self._rate_limit_window_ms:
            self._rate_limiter.popleft()
        
        # Check if over limit
        if len(self._rate_limiter) >= 1000:  # 1000 ops/sec
            self._rate_limited_count += 1
            return False
        
        # Add current timestamp
        self._rate_limiter.append(now)
        return True
    
    def get(self, name: str, failure_threshold: int = 5, timeout: int = 60) -> CircuitBreaker:
        """Get or create circuit breaker (no locks needed in single-threaded Lambda)."""
        if not self._check_rate_limit():
            raise Exception("Rate limit exceeded")
        
        self._total_operations += 1
        
        if name not in self._breakers:
            self._breakers[name] = CircuitBreaker(name, failure_threshold, timeout)
        return self._breakers[name]
    
    def call(self, name: str, func: Callable, *args, **kwargs) -> Any:
        """Call function with circuit breaker protection."""
        if not self._check_rate_limit():
            raise Exception("Rate limit exceeded")
        
        self._total_operations += 1
        breaker = self.get(name)
        return breaker.call(func, self._check_rate_limit, *args, **kwargs)
    
    def get_all_states(self) -> Dict[str, Dict[str, Any]]:
        """Get states of all circuit breakers."""
        if not self._check_rate_limit():
            raise Exception("Rate limit exceeded")
        
        self._total_operations += 1
        return {
            name: breaker.get_state()
            for name, breaker in self._breakers.items()
        }
    
    def reset_all(self):
        """Reset all circuit breakers."""
        if not self._check_rate_limit():
            raise Exception("Rate limit exceeded")
        
        self._total_operations += 1
        for breaker in self._breakers.values():
            breaker.reset()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get circuit breaker manager statistics."""
        if not self._check_rate_limit():
            from gateway import create_error_response
            return create_error_response('Rate limit exceeded', 'RATE_LIMIT_EXCEEDED')
        
        from gateway import create_success_response
        
        return create_success_response("Circuit breaker statistics", {
            'total_operations': self._total_operations,
            'breakers_count': len(self._breakers),
            'rate_limited_count': self._rate_limited_count,
            'rate_limit_window_ms': self._rate_limit_window_ms,
            'current_rate_limit_size': len(self._rate_limiter),
            'max_rate_limit': self._rate_limiter.maxlen,
            'breakers': {
                name: breaker.get_state()
                for name, breaker in self._breakers.items()
            }
        })
    
    def reset(self) -> bool:
        """
        Reset circuit breaker manager state.
        
        LESS-18: Provides lifecycle management capability.
        Clears all breakers and statistics.
        
        Returns:
            bool: True if reset successful, False if rate limited
        """
        if not self._check_rate_limit():
            return False
        
        try:
            # Reset all breakers
            self._breakers.clear()
            
            # Reset statistics
            self._total_operations = 0
            
            # Reset rate limiting
            self._rate_limiter.clear()
            self._rate_limited_count = 0
            
            return True
        except Exception:
            return False


# SINGLETON pattern for lifecycle management (LESS-18)
_circuit_breaker_core = None


def get_circuit_breaker_manager() -> CircuitBreakerCore:
    """
    Get SINGLETON circuit breaker manager instance.
    
    LESS-18: SINGLETON pattern provides lifecycle management.
    Uses gateway SINGLETON registry with fallback to module-level instance.
    
    Returns:
        CircuitBreakerCore: The singleton manager instance
        
    REF-IDs:
    - LESS-18: SINGLETON pattern for lifecycle management
    - DEC-04: No threading locks needed (Lambda single-threaded)
    """
    global _circuit_breaker_core
    
    try:
        # Try to use gateway SINGLETON registry
        from gateway import singleton_get, singleton_register
        
        manager = singleton_get('circuit_breaker_manager')
        if manager is None:
            # Create new instance and register
            if _circuit_breaker_core is None:
                _circuit_breaker_core = CircuitBreakerCore()
            singleton_register('circuit_breaker_manager', _circuit_breaker_core)
            manager = _circuit_breaker_core
        
        return manager
        
    except (ImportError, Exception):
        # Fallback to module-level singleton
        if _circuit_breaker_core is None:
            _circuit_breaker_core = CircuitBreakerCore()
        return _circuit_breaker_core


# ===== GATEWAY IMPLEMENTATION FUNCTIONS =====
# Updated to use SINGLETON manager pattern

def get_breaker_implementation(name: str, failure_threshold: int = 5, 
                               timeout: int = 60, **kwargs) -> Dict[str, Any]:
    """Get circuit breaker state using SINGLETON manager."""
    manager = get_circuit_breaker_manager()
    breaker = manager.get(name, failure_threshold, timeout)
    return breaker.get_state()


def execute_with_breaker_implementation(name: str, func: Callable, 
                                       args: tuple = (), **kwargs) -> Any:
    """Execute call with circuit breaker protection using SINGLETON manager."""
    manager = get_circuit_breaker_manager()
    return manager.call(name, func, *args, **kwargs)


def get_all_states_implementation(**kwargs) -> Dict[str, Dict[str, Any]]:
    """Get all circuit breaker states using SINGLETON manager."""
    manager = get_circuit_breaker_manager()
    return manager.get_all_states()


def reset_all_implementation(**kwargs):
    """Reset all circuit breakers using SINGLETON manager."""
    manager = get_circuit_breaker_manager()
    manager.reset_all()


def get_stats_implementation(**kwargs) -> Dict[str, Any]:
    """Get circuit breaker statistics using SINGLETON manager."""
    manager = get_circuit_breaker_manager()
    return manager.get_stats()


def reset_implementation(**kwargs) -> Dict[str, Any]:
    """Reset circuit breaker manager state using SINGLETON manager."""
    manager = get_circuit_breaker_manager()
    success = manager.reset()
    
    from gateway import create_success_response, create_error_response
    
    if success:
        return create_success_response("Circuit breaker manager reset", {
            'reset': True
        })
    else:
        return create_error_response('Reset rate limited', 'RATE_LIMIT_EXCEEDED')


# ===== EXPORTS =====

__all__ = [
    'CircuitState',
    'CircuitBreaker',
    'CircuitBreakerCore',
    'get_circuit_breaker_manager',
    'get_breaker_implementation',
    'execute_with_breaker_implementation',
    'get_all_states_implementation',
    'reset_all_implementation',
    'get_stats_implementation',
    'reset_implementation',
]

# EOF
