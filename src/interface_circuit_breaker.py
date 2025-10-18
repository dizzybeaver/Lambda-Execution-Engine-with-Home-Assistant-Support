"""
interface_circuit_breaker.py - Circuit Breaker Interface Router
Version: 2025.10.17.06
Description: Router/Firewall for circuit breaker interface - ONLY file gateway.py accesses

CHANGELOG:
- 2025.10.17.06: Added parameter validation for all operations (Issue #18 fix)
  - Validates 'name' parameter for get/call operations
  - Validates 'func' parameter for call operation
  - Type checking for name (must be string)
  - Clear error messages for missing/invalid parameters
- 2025.10.17.02: Initial creation with SUGA-ISP router pattern

SUGA-ISP ARCHITECTURE:
- This file is the INTERFACE ROUTER (firewall)
- Gateway.py imports ONLY from this file
- This file routes operations to circuit_breaker_core.py
- Internal circuit_breaker_core is isolated from external access

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

from typing import Any, Callable, Dict
import logging

# Import from circuit_breaker_core
from circuit_breaker_core import (
    get_breaker_implementation,
    execute_with_breaker_implementation,
    get_all_states_implementation,
    reset_all_implementation
)

logger = logging.getLogger(__name__)


# ===== VALID OPERATIONS =====

_VALID_CIRCUIT_BREAKER_OPERATIONS = ['get', 'call', 'get_all_states', 'reset_all']


# ===== MAIN ROUTER FUNCTION =====

def execute_circuit_breaker_operation(operation: str, **kwargs) -> Any:
    """
    Route circuit breaker operations to internal implementations with parameter validation.
    
    SUGA-ISP Pattern: Single entry point for all circuit breaker operations.
    Gateway calls this function, which routes to appropriate implementation.
    
    Supported operations:
    - 'get': Get or create circuit breaker (requires 'name')
    - 'call': Execute function with circuit breaker protection (requires 'name', 'func')
    - 'get_all_states': Get states of all circuit breakers (no parameters)
    - 'reset_all': Reset all circuit breakers (no parameters)
    
    Args:
        operation: Operation name
        **kwargs: Operation-specific parameters
        
    Returns:
        Operation result
        
    Raises:
        ValueError: If operation is unknown or required parameters are missing/invalid
    """
    if operation not in _VALID_CIRCUIT_BREAKER_OPERATIONS:
        raise ValueError(
            f"Unknown circuit breaker operation: '{operation}'. "
            f"Valid operations: {', '.join(_VALID_CIRCUIT_BREAKER_OPERATIONS)}"
        )
    
    if operation == 'get':
        _validate_name_param(kwargs, operation)
        return get_breaker_implementation(**kwargs)
    
    elif operation == 'call':
        _validate_name_param(kwargs, operation)
        _validate_func_param(kwargs, operation)
        return execute_with_breaker_implementation(**kwargs)
    
    elif operation == 'get_all_states':
        # No parameters required
        return get_all_states_implementation(**kwargs)
    
    elif operation == 'reset_all':
        # No parameters required
        return reset_all_implementation(**kwargs)
    
    else:
        # Should never reach here due to validation above, but defensive
        raise ValueError(f"Unknown circuit breaker operation: {operation}")


# ===== PARAMETER VALIDATION HELPERS =====

def _validate_name_param(kwargs: dict, operation: str) -> None:
    """
    Validate that name parameter exists and is a valid string.
    
    Args:
        kwargs: Parameter dictionary
        operation: Operation name (for error context)
        
    Raises:
        ValueError: If name is missing, not a string, or empty
    """
    if 'name' not in kwargs:
        raise ValueError(f"Circuit breaker operation '{operation}' requires parameter 'name'")
    
    name = kwargs.get('name')
    if not isinstance(name, str):
        raise ValueError(
            f"Circuit breaker operation '{operation}' parameter 'name' must be string, "
            f"got {type(name).__name__}"
        )
    
    if not name.strip():
        raise ValueError(
            f"Circuit breaker operation '{operation}' parameter 'name' cannot be empty string"
        )


def _validate_func_param(kwargs: dict, operation: str) -> None:
    """
    Validate that func parameter exists and is callable.
    
    Args:
        kwargs: Parameter dictionary
        operation: Operation name (for error context)
        
    Raises:
        ValueError: If func is missing or not callable
    """
    if 'func' not in kwargs:
        raise ValueError(f"Circuit breaker operation '{operation}' requires parameter 'func'")
    
    func = kwargs.get('func')
    if not callable(func):
        raise ValueError(
            f"Circuit breaker operation '{operation}' parameter 'func' must be callable, "
            f"got {type(func).__name__}"
        )


# ===== MODULE EXPORTS =====

__all__ = [
    'execute_circuit_breaker_operation',
]

# EOF
