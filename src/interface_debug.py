"""
interface_debug.py - Debug Interface Router
Version: 2025.10.17.06
Description: Router/Firewall for debug interface - ONLY file gateway.py accesses

CHANGELOG:
- 2025.10.17.06: Added parameter validation for operations (Issue #18 fix)
  - Validates operation is in supported list
  - Clear error messages for unknown operations
  - Lists all valid operations in error message
- 2025.10.17.02: Initial creation with SUGA-ISP router pattern

SUGA-ISP ARCHITECTURE:
- This file is the INTERFACE ROUTER (firewall)
- Gateway.py imports ONLY from this file
- This file routes operations to debug_core.py
- Internal debug_core is isolated from external access

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

from typing import Any, Dict
import logging

# Import from debug_core
from debug_core import generic_debug_operation

logger = logging.getLogger(__name__)


# ===== VALID OPERATIONS =====

_VALID_DEBUG_OPERATIONS = [
    'check_component_health',
    'check_gateway_health',
    'diagnose_system_health',
    'run_debug_tests',
    'validate_system_architecture',
    'get_system_stats',
    'get_optimization_stats',
    'get_dispatcher_stats',
    'get_operation_metrics',
    'get_gateway_stats',
    'verify_registry_operations',
    'validate_operation_signatures',
    'validate_interface_compliance',
    'check_circular_dependencies',
    'measure_execution_times',
    'run_performance_profile',
    'run_memory_profile',
    'check_memory_usage'
]


# ===== MAIN ROUTER FUNCTION =====

def execute_debug_operation(operation: str, **kwargs) -> Any:
    """
    Route debug operations to internal implementation with operation validation.
    
    SUGA-ISP Pattern: Single entry point for all debug operations.
    Gateway calls this function, which delegates to debug_core.generic_debug_operation().
    
    The debug_core.generic_debug_operation() function handles all 18 operations:
    - Health checks (component, gateway, system)
    - Testing (run_debug_tests, validate_architecture)
    - Statistics (system, optimization, dispatcher, operation, gateway)
    - Validation (registry, signatures, interface compliance, circular dependencies)
    - Performance (execution times, performance profile, memory profile, memory usage)
    
    Args:
        operation: Operation name (e.g., 'check_component_health')
        **kwargs: Operation-specific parameters
        
    Returns:
        Operation result (typically Dict[str, Any])
        
    Raises:
        ValueError: If operation is unknown
        
    Note:
        debug_core.generic_debug_operation() normalizes operation names
        (converts to uppercase, handles aliases) and handles all internal routing.
        Most debug operations have optional parameters only, as they are diagnostic tools.
    """
    # Validate operation is supported (case-insensitive check)
    if operation.lower() not in [op.lower() for op in _VALID_DEBUG_OPERATIONS]:
        raise ValueError(
            f"Unknown debug operation: '{operation}'. "
            f"Valid operations: {', '.join(_VALID_DEBUG_OPERATIONS)}"
        )
    
    # Route to debug_core which handles internal dispatching
    return generic_debug_operation(operation, **kwargs)


# ===== MODULE EXPORTS =====

__all__ = [
    'execute_debug_operation',
]

# EOF
