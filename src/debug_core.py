"""
debug_core.py - Debug Operation Dispatcher
Version: 2025.10.16.01
Description: Dispatcher for debug operations - delegates to internal debug modules

CHANGELOG:
- 2025.10.16.01: Fixed ALL import paths - removed 'debug.' prefix (no subdirectory exists)
                 Changed 'from debug import' to 'from debug_types import'

Copyright 2025 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

from typing import Dict, Any


def generic_debug_operation(operation: str, **kwargs) -> Dict[str, Any]:
    """
    Generic debug operation dispatcher.
    Routes operations to appropriate internal debug modules.
    
    NOTE: operation parameter is a string, not enum (simpler for Lambda)
    All imports are from root level (no debug/ subdirectory)
    """
    
    # Convert operation string to uppercase for comparison
    op = operation.upper() if isinstance(operation, str) else str(operation).upper()
    
    try:
        # Health operations
        if op in ['CHECK_COMPONENT_HEALTH', 'COMPONENT_HEALTH']:
            from debug_health import _check_component_health
            return _check_component_health(**kwargs)
        elif op in ['CHECK_GATEWAY_HEALTH', 'GATEWAY_HEALTH']:
            from debug_health import _check_gateway_health
            return _check_gateway_health(**kwargs)
        elif op in ['GENERATE_HEALTH_REPORT', 'HEALTH_REPORT']:
            from debug_health import _generate_health_report
            return _generate_health_report(**kwargs)
        
        # Diagnostic operations
        elif op in ['DIAGNOSE_SYSTEM_HEALTH', 'SYSTEM_HEALTH']:
            from debug_diagnostics import _diagnose_system_health
            return _diagnose_system_health(**kwargs)
        elif op in ['DIAGNOSE_PERFORMANCE', 'PERFORMANCE']:
            from debug_diagnostics import _diagnose_performance
            return _diagnose_performance(**kwargs)
        elif op in ['DIAGNOSE_MEMORY', 'MEMORY']:
            from debug_diagnostics import _diagnose_memory
            return _diagnose_memory(**kwargs)
        
        # Validation operations
        elif op in ['VALIDATE_SYSTEM_ARCHITECTURE', 'SYSTEM_ARCHITECTURE']:
            from debug_validation import _validate_system_architecture
            return _validate_system_architecture(**kwargs)
        elif op in ['VALIDATE_IMPORTS', 'IMPORTS']:
            from debug_validation import _validate_imports
            return _validate_imports(**kwargs)
        elif op in ['VALIDATE_GATEWAY_ROUTING', 'GATEWAY_ROUTING']:
            from debug_validation import _validate_gateway_routing
            return _validate_gateway_routing(**kwargs)
        elif op in ['RUN_CONFIG_UNIT_TESTS', 'CONFIG_UNIT_TESTS']:
            from debug_validation import _run_config_unit_tests
            return _run_config_unit_tests(**kwargs)
        elif op in ['RUN_CONFIG_INTEGRATION_TESTS', 'CONFIG_INTEGRATION_TESTS']:
            from debug_validation import _run_config_integration_tests
            return _run_config_integration_tests(**kwargs)
        elif op in ['RUN_CONFIG_PERFORMANCE_TESTS', 'CONFIG_PERFORMANCE_TESTS']:
            from debug_validation import _run_config_performance_tests
            return _run_config_performance_tests(**kwargs)
        elif op in ['RUN_CONFIG_COMPATIBILITY_TESTS', 'CONFIG_COMPATIBILITY_TESTS']:
            from debug_validation import _run_config_compatibility_tests
            return _run_config_compatibility_tests(**kwargs)
        elif op in ['RUN_CONFIG_GATEWAY_TESTS', 'CONFIG_GATEWAY_TESTS']:
            from debug_validation import _run_config_gateway_tests
            return _run_config_gateway_tests(**kwargs)
        
        # Statistics operations  
        elif op in ['GET_SYSTEM_STATS', 'SYSTEM_STATS']:
            from debug_stats import _get_system_stats
            return _get_system_stats(**kwargs)
        elif op in ['GET_OPTIMIZATION_STATS', 'OPTIMIZATION_STATS']:
            from debug_stats import _get_optimization_stats
            return _get_optimization_stats(**kwargs)
        elif op in ['GET_DISPATCHER_STATS', 'DISPATCHER_STATS']:
            from debug_stats import _get_dispatcher_stats
            return _get_dispatcher_stats(**kwargs)
        elif op in ['GET_OPERATION_METRICS', 'OPERATION_METRICS']:
            from debug_stats import _get_operation_metrics
            return _get_operation_metrics(**kwargs)
        elif op in ['GET_GATEWAY_STATS', 'GATEWAY_STATS']:
            # Direct gateway stats call
            from gateway_core import get_gateway_stats
            return get_gateway_stats()
        
        # Performance operations
        elif op in ['RUN_PERFORMANCE_BENCHMARK', 'PERFORMANCE_BENCHMARK']:
            from debug_performance import _run_performance_benchmark
            return _run_performance_benchmark(**kwargs)
        elif op in ['COMPARE_DISPATCHER_MODES', 'DISPATCHER_MODES']:
            from debug_performance import _compare_dispatcher_modes
            return _compare_dispatcher_modes(**kwargs)
        elif op in ['GET_PERFORMANCE_REPORT', 'PERFORMANCE_REPORT']:
            from debug_performance import _get_performance_report
            return _get_performance_report(**kwargs)
        
        # Verification operations
        elif op in ['VERIFY_REGISTRY_OPERATIONS', 'REGISTRY_OPERATIONS']:
            from debug_verification import _verify_registry_operations
            return _verify_registry_operations(**kwargs)
        elif op in ['ANALYZE_NAMING_PATTERNS', 'NAMING_PATTERNS']:
            from debug_verification import _analyze_naming_patterns
            return _analyze_naming_patterns(**kwargs)
        elif op in ['GENERATE_VERIFICATION_REPORT', 'VERIFICATION_REPORT']:
            from debug_verification import _generate_verification_report
            return _generate_verification_report(**kwargs)
        
        # Test operations
        elif op in ['RUN_DEBUG_TESTS', 'DEBUG_TESTS']:
            return {
                'success': True,
                'message': 'Debug tests placeholder',
                'tests_run': 0
            }
        elif op in ['VALIDATE_OPERATION_SIGNATURES', 'OPERATION_SIGNATURES']:
            return {
                'success': True,
                'message': 'Operation signatures validation placeholder'
            }
        elif op in ['VALIDATE_INTERFACE_COMPLIANCE', 'INTERFACE_COMPLIANCE']:
            return {
                'success': True,
                'message': 'Interface compliance validation placeholder'
            }
        elif op in ['CHECK_CIRCULAR_DEPENDENCIES', 'CIRCULAR_DEPENDENCIES']:
            return {
                'success': True,
                'message': 'Circular dependency check placeholder'
            }
        elif op in ['MEASURE_EXECUTION_TIMES', 'EXECUTION_TIMES']:
            return {
                'success': True,
                'message': 'Execution times measurement placeholder'
            }
        elif op in ['RUN_PERFORMANCE_PROFILE', 'PERFORMANCE_PROFILE']:
            return {
                'success': True,
                'message': 'Performance profiling placeholder'
            }
        elif op in ['RUN_MEMORY_PROFILE', 'MEMORY_PROFILE']:
            return {
                'success': True,
                'message': 'Memory profiling placeholder'
            }
        elif op in ['CHECK_MEMORY_USAGE', 'MEMORY_USAGE']:
            return {
                'success': True,
                'message': 'Memory usage check placeholder'
            }
        
        else:
            return {
                'success': False,
                'error': f'Unknown debug operation: {operation}',
                'operation_received': operation,
                'operation_normalized': op
            }
            
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'error_type': type(e).__name__,
            'operation': operation
        }


__all__ = ['generic_debug_operation']

# EOF
