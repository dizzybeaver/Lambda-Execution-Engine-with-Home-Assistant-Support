"""
circuit_breaker.py - Circuit Breaker Operations Primary Gateway Interface
Version: 2025.09.27.01
Description: Ultra-pure gateway for circuit breaker operations - pure delegation only

ARCHITECTURE: PRIMARY GATEWAY INTERFACE
- Function declarations ONLY - no implementation code
- Pure delegation to circuit_breaker_core.py
- External access point for circuit breaker operations
- Ultra-optimized for 128MB Lambda constraint

PRIMARY GATEWAY FUNCTIONS:
- get_circuit_breaker() - Circuit breaker instance management
- circuit_breaker_call() - Protected function execution
- get_circuit_breaker_status() - Status monitoring and health checks
- reset_circuit_breaker() - Circuit breaker reset operations

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

from typing import Dict, Any, Callable
from .circuit_breaker_core import generic_circuit_breaker_operation, CircuitBreakerOperation

# ===== SECTION 1: PRIMARY GATEWAY INTERFACE FUNCTIONS =====

def get_circuit_breaker(name: str):
    """
    Primary gateway function for circuit breaker instance management.
    Pure delegation to circuit_breaker_core implementation.
    """
    result = generic_circuit_breaker_operation(
        CircuitBreakerOperation.GET_BREAKER,
        name=name
    )
    return result.get("circuit_breaker")

def circuit_breaker_call(name: str, func: Callable, **kwargs) -> Any:
    """
    Primary gateway function for protected function execution.
    Pure delegation to circuit_breaker_core implementation.
    """
    result = generic_circuit_breaker_operation(
        CircuitBreakerOperation.CALL,
        name=name,
        func=func,
        **kwargs
    )
    return result.get("result")

def get_circuit_breaker_status(name: str = None) -> Dict[str, Any]:
    """
    Primary gateway function for circuit breaker status monitoring.
    Pure delegation to circuit_breaker_core implementation.
    """
    return generic_circuit_breaker_operation(
        CircuitBreakerOperation.GET_STATUS,
        name=name
    )

def reset_circuit_breaker(name: str) -> bool:
    """
    Primary gateway function for circuit breaker reset operations.
    Pure delegation to circuit_breaker_core implementation.
    """
    result = generic_circuit_breaker_operation(
        CircuitBreakerOperation.RESET,
        name=name
    )
    return result.get("success", False)

# ===== SECTION 2: MODULE EXPORTS =====

__all__ = [
    'get_circuit_breaker',
    'circuit_breaker_call',
    'get_circuit_breaker_status',
    'reset_circuit_breaker'
]

# EOF
