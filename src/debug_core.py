"""
debug_core.py - Debug Operation Dispatcher
Version: 2025.10.22.02
Description: Dispatch dictionary pattern for debug operations

CHANGES (2025.10.22.02):
- Added 4 CONFIG operations (12 dispatch entries with aliases)
  - CHECK_CONFIG_HEALTH / CONFIG_HEALTH / HEALTH_CONFIG
  - DIAGNOSE_CONFIG_PERFORMANCE / CONFIG_PERFORMANCE / PERFORMANCE_CONFIG
  - VALIDATE_CONFIG_CONFIGURATION / CONFIG_CONFIGURATION / CONFIGURATION_CONFIG
  - BENCHMARK_CONFIG_OPERATIONS / CONFIG_BENCHMARK / BENCHMARK_CONFIG

CHANGES (2025.10.22.01):
- Added 4 LOGGING operations (12 dispatch entries with aliases)

CHANGELOG:
- 2025.10.17.18: MODERNIZED with dispatch dictionary pattern (Issue #47)
  - Converted from ~30+ elif chain to dispatch dictionary
  - O(1) operation lookup vs O(n) elif chain
  - Reduced code complexity significantly
  - Easier to add new debug operations (1 line vs 5+ lines)
  - Supports operation aliases (uppercase conversion preserved)
  - All lazy imports preserved (modules loaded only when needed)
- 2025.10.16.01: Fixed ALL import paths - removed 'debug.' prefix

Copyright 2025 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

from typing import Dict, Any, Callable


# ===== OPERATION DISPATCH =====

def _build_dispatch_dict() -> Dict[str, Callable]:
    """
    Build dispatch dictionary for debug operations.
    
    Uses lazy imports - modules loaded only when operation is called.
    Supports aliases - multiple names map to same implementation.
    """
    return {
        # Health operations
        'CHECK_COMPONENT_HEALTH': lambda **kwargs: __import__('debug_health', fromlist=['_check_component_health'])._check_component_health(**kwargs),
        'COMPONENT_HEALTH': lambda **kwargs: __import__('debug_health', fromlist=['_check_component_health'])._check_component_health(**kwargs),
        
        'CHECK_GATEWAY_HEALTH': lambda **kwargs: __import__('debug_health', fromlist=['_check_gateway_health'])._check_gateway_health(**kwargs),
        'GATEWAY_HEALTH': lambda **kwargs: __import__('debug_health', fromlist=['_check_gateway_health'])._check_gateway_health(**kwargs),
        
        'GENERATE_HEALTH_REPORT': lambda **kwargs: __import__('debug_health', fromlist=['_generate_health_report'])._generate_health_report(**kwargs),
        'HEALTH_REPORT': lambda **kwargs: __import__('debug_health', fromlist=['_generate_health_report'])._generate_health_report(**kwargs),
        
        # LOGGING operations (12 entries: 4 operations × 3 aliases each)
        'CHECK_LOGGING_HEALTH': lambda **kwargs: __import__('debug_health', fromlist=['_check_logging_health'])._check_logging_health(**kwargs),
        'LOGGING_HEALTH': lambda **kwargs: __import__('debug_health', fromlist=['_check_logging_health'])._check_logging_health(**kwargs),
        'HEALTH_LOGGING': lambda **kwargs: __import__('debug_health', fromlist=['_check_logging_health'])._check_logging_health(**kwargs),
        
        'DIAGNOSE_LOGGING_PERFORMANCE': lambda **kwargs: __import__('debug_diagnostics', fromlist=['_diagnose_logging_performance'])._diagnose_logging_performance(**kwargs),
        'LOGGING_PERFORMANCE': lambda **kwargs: __import__('debug_diagnostics', fromlist=['_diagnose_logging_performance'])._diagnose_logging_performance(**kwargs),
        'PERFORMANCE_LOGGING': lambda **kwargs: __import__('debug_diagnostics', fromlist=['_diagnose_logging_performance'])._diagnose_logging_performance(**kwargs),
        
        'VALIDATE_LOGGING_CONFIGURATION': lambda **kwargs: __import__('debug_validation', fromlist=['_validate_logging_configuration'])._validate_logging_configuration(**kwargs),
        'LOGGING_CONFIGURATION': lambda **kwargs: __import__('debug_validation', fromlist=['_validate_logging_configuration'])._validate_logging_configuration(**kwargs),
        'CONFIGURATION_LOGGING': lambda **kwargs: __import__('debug_validation', fromlist=['_validate_logging_configuration'])._validate_logging_configuration(**kwargs),
        
        'BENCHMARK_LOGGING_OPERATIONS': lambda **kwargs: __import__('debug_performance', fromlist=['_benchmark_logging_operations'])._benchmark_logging_operations(**kwargs),
        'LOGGING_BENCHMARK': lambda **kwargs: __import__('debug_performance', fromlist=['_benchmark_logging_operations'])._benchmark_logging_operations(**kwargs),
        'BENCHMARK_LOGGING': lambda **kwargs: __import__('debug_performance', fromlist=['_benchmark_logging_operations'])._benchmark_logging_operations(**kwargs),
        
        # SECURITY operations (12 entries: 4 operations × 3 aliases each)
        'CHECK_SECURITY_HEALTH': lambda **kwargs: __import__('debug_health', fromlist=['_check_security_health'])._check_security_health(**kwargs),
        'SECURITY_HEALTH': lambda **kwargs: __import__('debug_health', fromlist=['_check_security_health'])._check_security_health(**kwargs),
        'HEALTH_SECURITY': lambda **kwargs: __import__('debug_health', fromlist=['_check_security_health'])._check_security_health(**kwargs),
        
        'DIAGNOSE_SECURITY_PERFORMANCE': lambda **kwargs: __import__('debug_diagnostics', fromlist=['_diagnose_security_performance'])._diagnose_security_performance(**kwargs),
        'SECURITY_PERFORMANCE': lambda **kwargs: __import__('debug_diagnostics', fromlist=['_diagnose_security_performance'])._diagnose_security_performance(**kwargs),
        'PERFORMANCE_SECURITY': lambda **kwargs: __import__('debug_diagnostics', fromlist=['_diagnose_security_performance'])._diagnose_security_performance(**kwargs),
        
        'VALIDATE_SECURITY_CONFIGURATION': lambda **kwargs: __import__('debug_validation', fromlist=['_validate_security_configuration'])._validate_security_configuration(**kwargs),
        'SECURITY_CONFIGURATION': lambda **kwargs: __import__('debug_validation', fromlist=['_validate_security_configuration'])._validate_security_configuration(**kwargs),
        'CONFIGURATION_SECURITY': lambda **kwargs: __import__('debug_validation', fromlist=['_validate_security_configuration'])._validate_security_configuration(**kwargs),
        
        'BENCHMARK_SECURITY_OPERATIONS': lambda **kwargs: __import__('debug_performance', fromlist=['_benchmark_security_operations'])._benchmark_security_operations(**kwargs),
        'SECURITY_BENCHMARK': lambda **kwargs: __import__('debug_performance', fromlist=['_benchmark_security_operations'])._benchmark_security_operations(**kwargs),
        'BENCHMARK_SECURITY': lambda **kwargs: __import__('debug_performance', fromlist=['_benchmark_security_operations'])._benchmark_security_operations(**kwargs),
        
        # CONFIG operations (12 entries: 4 operations × 3 aliases each)
        'CHECK_CONFIG_HEALTH': lambda **kwargs: __import__('debug_health', fromlist=['_check_config_health'])._check_config_health(**kwargs),
        'CONFIG_HEALTH': lambda **kwargs: __import__('debug_health', fromlist=['_check_config_health'])._check_config_health(**kwargs),
        'HEALTH_CONFIG': lambda **kwargs: __import__('debug_health', fromlist=['_check_config_health'])._check_config_health(**kwargs),
        
        'DIAGNOSE_CONFIG_PERFORMANCE': lambda **kwargs: __import__('debug_diagnostics', fromlist=['_diagnose_config_performance'])._diagnose_config_performance(**kwargs),
        'CONFIG_PERFORMANCE': lambda **kwargs: __import__('debug_diagnostics', fromlist=['_diagnose_config_performance'])._diagnose_config_performance(**kwargs),
        'PERFORMANCE_CONFIG': lambda **kwargs: __import__('debug_diagnostics', fromlist=['_diagnose_config_performance'])._diagnose_config_performance(**kwargs),
        
        'VALIDATE_CONFIG_CONFIGURATION': lambda **kwargs: __import__('debug_validation', fromlist=['_validate_config_configuration'])._validate_config_configuration(**kwargs),
        'CONFIG_CONFIGURATION': lambda **kwargs: __import__('debug_validation', fromlist=['_validate_config_configuration'])._validate_config_configuration(**kwargs),
        'CONFIGURATION_CONFIG': lambda **kwargs: __import__('debug_validation', fromlist=['_validate_config_configuration'])._validate_config_configuration(**kwargs),
        
        'BENCHMARK_CONFIG_OPERATIONS': lambda **kwargs: __import__('debug_performance', fromlist=['_benchmark_config_operations'])._benchmark_config_operations(**kwargs),
        'CONFIG_BENCHMARK': lambda **kwargs: __import__('debug_performance', fromlist=['_benchmark_config_operations'])._benchmark_config_operations(**kwargs),
        'BENCHMARK_CONFIG': lambda **kwargs: __import__('debug_performance', fromlist=['_benchmark_config_operations'])._benchmark_config_operations(**kwargs),
        
        # Diagnostic operations
        'DIAGNOSE_SYSTEM_HEALTH': lambda **kwargs: __import__('debug_diagnostics', fromlist=['_diagnose_system_health'])._diagnose_system_health(**kwargs),
        'SYSTEM_HEALTH': lambda **kwargs: __import__('debug_diagnostics', fromlist=['_diagnose_system_health'])._diagnose_system_health(**kwargs),
        
        'DIAGNOSE_PERFORMANCE': lambda **kwargs: __import__('debug_diagnostics', fromlist=['_diagnose_performance'])._diagnose_performance(**kwargs),
        'PERFORMANCE': lambda **kwargs: __import__('debug_diagnostics', fromlist=['_diagnose_performance'])._diagnose_performance(**kwargs),
        
        'DIAGNOSE_MEMORY': lambda **kwargs: __import__('debug_diagnostics', fromlist=['_diagnose_memory'])._diagnose_memory(**kwargs),
        'MEMORY': lambda **kwargs: __import__('debug_diagnostics', fromlist=['_diagnose_memory'])._diagnose_memory(**kwargs),
        
        # Validation operations
        'VALIDATE_SYSTEM_ARCHITECTURE': lambda **kwargs: __import__('debug_validation', fromlist=['_validate_system_architecture'])._validate_system_architecture(**kwargs),
        'SYSTEM_ARCHITECTURE': lambda **kwargs: __import__('debug_validation', fromlist=['_validate_system_architecture'])._validate_system_architecture(**kwargs),
        
        'VALIDATE_IMPORTS': lambda **kwargs: __import__('debug_validation', fromlist=['_validate_imports'])._validate_imports(**kwargs),
        'IMPORTS': lambda **kwargs: __import__('debug_validation', fromlist=['_validate_imports'])._validate_imports(**kwargs),
        
        'VALIDATE_GATEWAY_ROUTING': lambda **kwargs: __import__('debug_validation', fromlist=['_validate_gateway_routing'])._validate_gateway_routing(**kwargs),
        'GATEWAY_ROUTING': lambda **kwargs: __import__('debug_validation', fromlist=['_validate_gateway_routing'])._validate_gateway_routing(**kwargs),
        
        'RUN_CONFIG_UNIT_TESTS': lambda **kwargs: __import__('debug_validation', fromlist=['_run_config_unit_tests'])._run_config_unit_tests(**kwargs),
        'CONFIG_UNIT_TESTS': lambda **kwargs: __import__('debug_validation', fromlist=['_run_config_unit_tests'])._run_config_unit_tests(**kwargs),
        
        'RUN_CONFIG_INTEGRATION_TESTS': lambda **kwargs: __import__('debug_validation', fromlist=['_run_config_integration_tests'])._run_config_integration_tests(**kwargs),
        'CONFIG_INTEGRATION_TESTS': lambda **kwargs: __import__('debug_validation', fromlist=['_run_config_integration_tests'])._run_config_integration_tests(**kwargs),
        
        'RUN_CONFIG_PERFORMANCE_TESTS': lambda **kwargs: __import__('debug_validation', fromlist=['_run_config_performance_tests'])._run_config_performance_tests(**kwargs),
        'CONFIG_PERFORMANCE_TESTS': lambda **kwargs: __import__('debug_validation', fromlist=['_run_config_performance_tests'])._run_config_performance_tests(**kwargs),
        
        'RUN_CONFIG_COMPATIBILITY_TESTS': lambda **kwargs: __import__('debug_validation', fromlist=['_run_config_compatibility_tests'])._run_config_compatibility_tests(**kwargs),
        'CONFIG_COMPATIBILITY_TESTS': lambda **kwargs: __import__('debug_validation', fromlist=['_run_config_compatibility_tests'])._run_config_compatibility_tests(**kwargs),
        
        'RUN_CONFIG_GATEWAY_TESTS': lambda **kwargs: __import__('debug_validation', fromlist=['_run_config_gateway_tests'])._run_config_gateway_tests(**kwargs),
        'CONFIG_GATEWAY_TESTS': lambda **kwargs: __import__('debug_validation', fromlist=['_run_config_gateway_tests'])._run_config_gateway_tests(**kwargs),
        
        # Statistics operations
        'GET_SYSTEM_STATS': lambda **kwargs: __import__('debug_stats', fromlist=['_get_system_stats'])._get_system_stats(**kwargs),
        'SYSTEM_STATS': lambda **kwargs: __import__('debug_stats', fromlist=['_get_system_stats'])._get_system_stats(**kwargs),
        
        'GET_OPTIMIZATION_STATS': lambda **kwargs: __import__('debug_stats', fromlist=['_get_optimization_stats'])._get_optimization_stats(**kwargs),
        'OPTIMIZATION_STATS': lambda **kwargs: __import__('debug_stats', fromlist=['_get_optimization_stats'])._get_optimization_stats(**kwargs),
        
        'GET_DISPATCHER_STATS': lambda **kwargs: __import__('debug_stats', fromlist=['_get_dispatcher_stats'])._get_dispatcher_stats(**kwargs),
        'DISPATCHER_STATS': lambda **kwargs: __import__('debug_stats', fromlist=['_get_dispatcher_stats'])._get_dispatcher_stats(**kwargs),
        
        'GET_OPERATION_METRICS': lambda **kwargs: __import__('debug_stats', fromlist=['_get_operation_metrics'])._get_operation_metrics(**kwargs),
        'OPERATION_METRICS': lambda **kwargs: __import__('debug_stats', fromlist=['_get_operation_metrics'])._get_operation_metrics(**kwargs),
        
        'GET_GATEWAY_STATS': lambda **kwargs: __import__('gateway_core', fromlist=['get_gateway_stats']).get_gateway_stats(),
        'GATEWAY_STATS': lambda **kwargs: __import__('gateway_core', fromlist=['get_gateway_stats']).get_gateway_stats(),
        
        # Performance operations
        'RUN_PERFORMANCE_BENCHMARK': lambda **kwargs: __import__('debug_performance', fromlist=['_run_performance_benchmark'])._run_performance_benchmark(**kwargs),
        'PERFORMANCE_BENCHMARK': lambda **kwargs: __import__('debug_performance', fromlist=['_run_performance_benchmark'])._run_performance_benchmark(**kwargs),
        
        'COMPARE_DISPATCHER_MODES': lambda **kwargs: __import__('debug_performance', fromlist=['_compare_dispatcher_modes'])._compare_dispatcher_modes(**kwargs),
        'DISPATCHER_MODES': lambda **kwargs: __import__('debug_performance', fromlist=['_compare_dispatcher_modes'])._compare_dispatcher_modes(**kwargs),
        
        'GET_PERFORMANCE_REPORT': lambda **kwargs: __import__('debug_performance', fromlist=['_get_performance_report'])._get_performance_report(**kwargs),
        'PERFORMANCE_REPORT': lambda **kwargs: __import__('debug_performance', fromlist=['_get_performance_report'])._get_performance_report(**kwargs),
        
        # Verification operations
        'VERIFY_REGISTRY_OPERATIONS': lambda **kwargs: __import__('debug_verification', fromlist=['_verify_registry_operations'])._verify_registry_operations(**kwargs),
        'REGISTRY_OPERATIONS': lambda **kwargs: __import__('debug_verification', fromlist=['_verify_registry_operations'])._verify_registry_operations(**kwargs),
        
        'ANALYZE_NAMING_PATTERNS': lambda **kwargs: __import__('debug_verification', fromlist=['_analyze_naming_patterns'])._analyze_naming_patterns(**kwargs),
        'NAMING_PATTERNS': lambda **kwargs: __import__('debug_verification', fromlist=['_analyze_naming_patterns'])._analyze_naming_patterns(**kwargs),
        
        'GENERATE_VERIFICATION_REPORT': lambda **kwargs: __import__('debug_verification', fromlist=['_generate_verification_report'])._generate_verification_report(**kwargs),
        'VERIFICATION_REPORT': lambda **kwargs: __import__('debug_verification', fromlist=['_generate_verification_report'])._generate_verification_report(**kwargs),
        
        # Placeholder operations (not yet implemented)
        'RUN_DEBUG_TESTS': lambda **kwargs: {'success': True, 'message': 'Debug tests placeholder', 'tests_run': 0},
        'DEBUG_TESTS': lambda **kwargs: {'success': True, 'message': 'Debug tests placeholder', 'tests_run': 0},
        
        'VALIDATE_OPERATION_SIGNATURES': lambda **kwargs: {'success': True, 'message': 'Operation signatures validation placeholder'},
        'OPERATION_SIGNATURES': lambda **kwargs: {'success': True, 'message': 'Operation signatures validation placeholder'},
        
        'VALIDATE_INTERFACE_COMPLIANCE': lambda **kwargs: {'success': True, 'message': 'Interface compliance validation placeholder'},
        'INTERFACE_COMPLIANCE': lambda **kwargs: {'success': True, 'message': 'Interface compliance validation placeholder'},
        
        'CHECK_CIRCULAR_DEPENDENCIES': lambda **kwargs: {'success': True, 'message': 'Circular dependency check placeholder'},
        'CIRCULAR_DEPENDENCIES': lambda **kwargs: {'success': True, 'message': 'Circular dependency check placeholder'},
        
        'MEASURE_EXECUTION_TIMES': lambda **kwargs: {'success': True, 'message': 'Execution times measurement placeholder'},
        'EXECUTION_TIMES': lambda **kwargs: {'success': True, 'message': 'Execution times measurement placeholder'},
        
        'RUN_PERFORMANCE_PROFILE': lambda **kwargs: {'success': True, 'message': 'Performance profiling placeholder'},
        'PERFORMANCE_PROFILE': lambda **kwargs: {'success': True, 'message': 'Performance profiling placeholder'},
        
        'RUN_MEMORY_PROFILE': lambda **kwargs: {'success': True, 'message': 'Memory profiling placeholder'},
        'MEMORY_PROFILE': lambda **kwargs: {'success': True, 'message': 'Memory profiling placeholder'},
        
        'CHECK_MEMORY_USAGE': lambda **kwargs: {'success': True, 'message': 'Memory usage check placeholder'},
        'MEMORY_USAGE': lambda **kwargs: {'success': True, 'message': 'Memory usage check placeholder'},
    }

_OPERATION_DISPATCH = _build_dispatch_dict()


# ===== MAIN DISPATCHER FUNCTION =====

def generic_debug_operation(operation: str, **kwargs) -> Dict[str, Any]:
    """
    Generic debug operation dispatcher using dispatch dictionary pattern.
    
    Routes operations to appropriate internal debug modules.
    Uses lazy imports - modules loaded only when operation is called.
    Supports operation aliases via dictionary mapping.
    
    Args:
        operation: Debug operation name (case-insensitive)
        **kwargs: Operation-specific parameters
        
    Returns:
        Operation result dictionary
    """
    # Convert operation to uppercase for lookup
    op = operation.upper() if isinstance(operation, str) else str(operation).upper()
    
    try:
        # Lookup in dispatch dictionary (O(1))
        if op in _OPERATION_DISPATCH:
            return _OPERATION_DISPATCH[op](**kwargs)
        else:
            return {
                'success': False,
                'error': f'Unknown debug operation: {operation}',
                'operation_received': operation,
                'operation_normalized': op,
                'valid_operations': sorted(set(_OPERATION_DISPATCH.keys()))
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
