"""
interface_circuit_breaker.py - Circuit Breaker Interface Router
Version: 2025.10.17.02
Description: Router/Firewall for circuit breaker interface - ONLY file gateway.py accesses

SUGA-ISP ARCHITECTURE:
- This file is the INTERFACE ROUTER (firewall)
- Gateway.py imports ONLY from this file
- This file routes operations to circuit_breaker_core.py
- Internal circuit_breaker_core is isolated from external access

DESIGN DECISIONS:
1. Unified Architecture:
   - Previously circuit breaker bypassed router for performance
   - Now unified with all other interfaces for consistency
   - Function names match circuit_breaker_core exactly (no overhead)
   - Simple pass-through routing maintains performance

2. Operation Routing:
   - All 4 operations route through execute_circuit_breaker_operation()
   - Direct delegation to circuit_breaker_core implementation functions
   - No validation overhead (validation done in core if needed)

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


# ===== MAIN ROUTER FUNCTION =====

def execute_circuit_breaker_operation(operation: str, **kwargs) -> Any:
    """
    Route circuit breaker operations to internal implementations.
    
    SUGA-ISP Pattern: Single entry point for all circuit breaker operations.
    Gateway calls this function, which routes to appropriate implementation.
    
    Supported operations:
    - 'get': Get or create circuit breaker
    - 'call': Execute function with circuit breaker protection
    - 'get_all_states': Get states of all circuit breakers
    - 'reset_all': Reset all circuit breakers
    
    Args:
        operation: Operation name
        **kwargs: Operation-specific parameters
        
    Returns:
        Operation result
        
    Raises:
        ValueError: If operation is unknown
    """
    if operation == 'get':
        return get_breaker_implementation(**kwargs)
    
    elif operation == 'call':
        return execute_with_breaker_implementation(**kwargs)
    
    elif operation == 'get_all_states':
        return get_all_states_implementation(**kwargs)
    
    elif operation == 'reset_all':
        return reset_all_implementation(**kwargs)
    
    else:
        raise ValueError(f"Unknown circuit breaker operation: {operation}")


# ===== MODULE EXPORTS =====

__all__ = [
    'execute_circuit_breaker_operation',
]

# EOF
