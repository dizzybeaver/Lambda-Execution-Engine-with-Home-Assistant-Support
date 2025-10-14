"""
debug_core.py - Debug Operation Dispatcher
Version: 2025.10.14.01
Description: Dispatcher for debug operations - delegates to internal debug modules

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

from typing import Dict, Any
from debug import DebugOperation

# Import health operations
from debug.debug_health import (
    _check_component_health,
    _check_gateway_health,
    _generate_health_report
)

# Import diagnostic operations
from debug.debug_diagnostics import (
    _diagnose_system_health,
    _diagnose_performance,
    _diagnose_memory
)

# Import validation operations
from debug.debug_validation import (
    _validate_system_architecture,
    _validate_imports,
    _validate_gateway_routing,
    _run_config_unit_tests,
    _run_config_integration_tests,
    _run_config_performance_tests,
    _run_config_compatibility_tests,
    _run_config_gateway_tests
)

# Import statistics operations
from debug.debug_stats import (
    _get_system_stats,
    _get_optimization_stats,
    _get_dispatcher_stats,
    _get_operation_metrics
)

# Import performance operations
from debug.debug_performance import (
    _run_performance_benchmark,
    _compare_dispatcher_modes,
    _get_performance_report
)

# Import verification operations
from debug.debug_verification import (
    _verify_registry_operations,
    _analyze_naming_patterns,
    _generate_verification_report
)


def generic_debug_operation(operation: DebugOperation, **kwargs) -> Dict[str, Any]:
    """
    Generic debug operation dispatcher.
    Routes operations to appropriate internal debug modules.
    """
    try:
        if operation == DebugOperation.CHECK_COMPONENT_HEALTH:
            return _check_component_health(**kwargs)
        elif operation == DebugOperation.CHECK_GATEWAY_HEALTH:
            return _check_gateway_health(**kwargs)
        elif operation == DebugOperation.DIAGNOSE_SYSTEM_HEALTH:
            return _diagnose_system_health(**kwargs)
        elif operation == DebugOperation.DIAGNOSE_PERFORMANCE:
            return _diagnose_performance(**kwargs)
        elif operation == DebugOperation.DIAGNOSE_MEMORY:
            return _diagnose_memory(**kwargs)
        elif operation == DebugOperation.VALIDATE_SYSTEM_ARCHITECTURE:
            return _validate_system_architecture(**kwargs)
        elif operation == DebugOperation.VALIDATE_IMPORTS:
            return _validate_imports(**kwargs)
        elif operation == DebugOperation.VALIDATE_GATEWAY_ROUTING:
            return _validate_gateway_routing(**kwargs)
        elif operation == DebugOperation.GET_SYSTEM_STATS:
            return _get_system_stats(**kwargs)
        elif operation == DebugOperation.GET_OPTIMIZATION_STATS:
            return _get_optimization_stats(**kwargs)
        elif operation == DebugOperation.RUN_PERFORMANCE_BENCHMARK:
            return _run_performance_benchmark(**kwargs)
        elif operation == DebugOperation.GENERATE_HEALTH_REPORT:
            return _generate_health_report(**kwargs)
        elif operation == DebugOperation.VERIFY_REGISTRY_OPERATIONS:
            return _verify_registry_operations(**kwargs)
        elif operation == DebugOperation.ANALYZE_NAMING_PATTERNS:
            return _analyze_naming_patterns(**kwargs)
        elif operation == DebugOperation.GENERATE_VERIFICATION_REPORT:
            return _generate_verification_report(**kwargs)
        elif operation == DebugOperation.RUN_CONFIG_UNIT_TESTS:
            return _run_config_unit_tests(**kwargs)
        elif operation == DebugOperation.RUN_CONFIG_INTEGRATION_TESTS:
            return _run_config_integration_tests(**kwargs)
        elif operation == DebugOperation.RUN_CONFIG_PERFORMANCE_TESTS:
            return _run_config_performance_tests(**kwargs)
        elif operation == DebugOperation.RUN_CONFIG_COMPATIBILITY_TESTS:
            return _run_config_compatibility_tests(**kwargs)
        elif operation == DebugOperation.RUN_CONFIG_GATEWAY_TESTS:
            return _run_config_gateway_tests(**kwargs)
        elif operation == DebugOperation.GET_DISPATCHER_STATS:
            return _get_dispatcher_stats(**kwargs)
        elif operation == DebugOperation.GET_OPERATION_METRICS:
            return _get_operation_metrics(**kwargs)
        elif operation == DebugOperation.COMPARE_DISPATCHER_MODES:
            return _compare_dispatcher_modes(**kwargs)
        elif operation == DebugOperation.GET_PERFORMANCE_REPORT:
            return _get_performance_report(**kwargs)
        else:
            return {'success': False, 'error': f'Unknown operation: {operation}'}
    except Exception as e:
        return {'success': False, 'error': str(e)}


__all__ = [
    'DebugOperation',
    'generic_debug_operation'
]

# EOF
