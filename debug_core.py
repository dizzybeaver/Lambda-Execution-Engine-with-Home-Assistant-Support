"""
debug/debug_core.py - Debug Operation Dispatcher
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


def generic_debug_operation(operation, **kwargs) -> Dict[str, Any]:
    """
    Generic debug operation dispatcher.
    Routes operations to appropriate internal debug modules.
    Lazy imports to avoid circular dependencies.
    """
    # Import DebugOperation enum
    from debug import DebugOperation
    
    try:
        # Health operations
        if operation == DebugOperation.CHECK_COMPONENT_HEALTH:
            from debug.debug_health import _check_component_health
            return _check_component_health(**kwargs)
        elif operation == DebugOperation.CHECK_GATEWAY_HEALTH:
            from debug.debug_health import _check_gateway_health
            return _check_gateway_health(**kwargs)
        elif operation == DebugOperation.GENERATE_HEALTH_REPORT:
            from debug.debug_health import _generate_health_report
            return _generate_health_report(**kwargs)
        
        # Diagnostic operations
        elif operation == DebugOperation.DIAGNOSE_SYSTEM_HEALTH:
            from debug.debug_diagnostics import _diagnose_system_health
            return _diagnose_system_health(**kwargs)
        elif operation == DebugOperation.DIAGNOSE_PERFORMANCE:
            from debug.debug_diagnostics import _diagnose_performance
            return _diagnose_performance(**kwargs)
        elif operation == DebugOperation.DIAGNOSE_MEMORY:
            from debug.debug_diagnostics import _diagnose_memory
            return _diagnose_memory(**kwargs)
        
        # Validation operations
        elif operation == DebugOperation.VALIDATE_SYSTEM_ARCHITECTURE:
            from debug.debug_validation import _validate_system_architecture
            return _validate_system_architecture(**kwargs)
        elif operation == DebugOperation.VALIDATE_IMPORTS:
            from debug.debug_validation import _validate_imports
            return _validate_imports(**kwargs)
        elif operation == DebugOperation.VALIDATE_GATEWAY_ROUTING:
            from debug.debug_validation import _validate_gateway_routing
            return _validate_gateway_routing(**kwargs)
        elif operation == DebugOperation.RUN_CONFIG_UNIT_TESTS:
            from debug.debug_validation import _run_config_unit_tests
            return _run_config_unit_tests(**kwargs)
        elif operation == DebugOperation.RUN_CONFIG_INTEGRATION_TESTS:
            from debug.debug_validation import _run_config_integration_tests
            return _run_config_integration_tests(**kwargs)
        elif operation == DebugOperation.RUN_CONFIG_PERFORMANCE_TESTS:
            from debug.debug_validation import _run_config_performance_tests
            return _run_config_performance_tests(**kwargs)
        elif operation == DebugOperation.RUN_CONFIG_COMPATIBILITY_TESTS:
            from debug.debug_validation import _run_config_compatibility_tests
            return _run_config_compatibility_tests(**kwargs)
        elif operation == DebugOperation.RUN_CONFIG_GATEWAY_TESTS:
            from debug.debug_validation import _run_config_gateway_tests
            return _run_config_gateway_tests(**kwargs)
        
        # Statistics operations
        elif operation == DebugOperation.GET_SYSTEM_STATS:
            from debug.debug_stats import _get_system_stats
            return _get_system_stats(**kwargs)
        elif operation == DebugOperation.GET_OPTIMIZATION_STATS:
            from debug.debug_stats import _get_optimization_stats
            return _get_optimization_stats(**kwargs)
        elif operation == DebugOperation.GET_DISPATCHER_STATS:
            from debug.debug_stats import _get_dispatcher_stats
            return _get_dispatcher_stats(**kwargs)
        elif operation == DebugOperation.GET_OPERATION_METRICS:
            from debug.debug_stats import _get_operation_metrics
            return _get_operation_metrics(**kwargs)
        
        # Performance operations
        elif operation == DebugOperation.RUN_PERFORMANCE_BENCHMARK:
            from debug.debug_performance import _run_performance_benchmark
            return _run_performance_benchmark(**kwargs)
        elif operation == DebugOperation.COMPARE_DISPATCHER_MODES:
            from debug.debug_performance import _compare_dispatcher_modes
            return _compare_dispatcher_modes(**kwargs)
        elif operation == DebugOperation.GET_PERFORMANCE_REPORT:
            from debug.debug_performance import _get_performance_report
            return _get_performance_report(**kwargs)
        
        # Verification operations
        elif operation == DebugOperation.VERIFY_REGISTRY_OPERATIONS:
            from debug.debug_verification import _verify_registry_operations
            return _verify_registry_operations(**kwargs)
        elif operation == DebugOperation.ANALYZE_NAMING_PATTERNS:
            from debug.debug_verification import _analyze_naming_patterns
            return _analyze_naming_patterns(**kwargs)
        elif operation == DebugOperation.GENERATE_VERIFICATION_REPORT:
            from debug.debug_verification import _generate_verification_report
            return _generate_verification_report(**kwargs)
        
        else:
            return {'success': False, 'error': f'Unknown operation: {operation}'}
    except Exception as e:
        return {'success': False, 'error': str(e)}


__all__ = ['generic_debug_operation']

# EOF
