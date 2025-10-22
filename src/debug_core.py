"""
debug_core.py - Debug Operation Dispatcher
Version: 2025.10.17.18
Description: Dispatch dictionary pattern for debug operations

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
        'CHECK_COMPONENT_HEALTH': lambda **kw: __import__('debug_health', fromlist=['_check_component_health'])._check_component_health(**kw),
        'COMPONENT_HEALTH': lambda **kw: __import__('debug_health', fromlist=['_check_component_health'])._check_component_health(**kw),
        
        'CHECK_GATEWAY_HEALTH': lambda **kw: __import__('debug_health', fromlist=['_check_gateway_health'])._check_gateway_health(**kw),
        'GATEWAY_HEALTH': lambda **kw: __import__('debug_health', fromlist=['_check_gateway_health'])._check_gateway_health(**kw),
        
        'GENERATE_HEALTH_REPORT': lambda **kw: __import__('debug_health', fromlist=['_generate_health_report'])._generate_health_report(**kw),
        'HEALTH_REPORT': lambda **kw: __import__('debug_health', fromlist=['_generate_health_report'])._generate_health_report(**kw),
        
        # Diagnostic operations
        'DIAGNOSE_SYSTEM_HEALTH': lambda **kw: __import__('debug_diagnostics', fromlist=['_diagnose_system_health'])._diagnose_system_health(**kw),
        'SYSTEM_HEALTH': lambda **kw: __import__('debug_diagnostics', fromlist=['_diagnose_system_health'])._diagnose_system_health(**kw),
        
        'DIAGNOSE_PERFORMANCE': lambda **kw: __import__('debug_diagnostics', fromlist=['_diagnose_performance'])._diagnose_performance(**kw),
        'PERFORMANCE': lambda **kw: __import__('debug_diagnostics', fromlist=['_diagnose_performance'])._diagnose_performance(**kw),
        
        'DIAGNOSE_MEMORY': lambda **kw: __import__('debug_diagnostics', fromlist=['_diagnose_memory'])._diagnose_memory(**kw),
        'MEMORY': lambda **kw: __import__('debug_diagnostics', fromlist=['_diagnose_memory'])._diagnose_memory(**kw),
        
        # HTTP_CLIENT Interface Operations (12 dispatches = 4 ops × 3 aliases)
        'CHECK_HTTP_CLIENT_HEALTH': lambda **kw: __import__('debug_health', fromlist=['_check_http_client_health'])._check_http_client_health(**kw),
        'HTTP_CLIENT_HEALTH': lambda **kw: __import__('debug_health', fromlist=['_check_http_client_health'])._check_http_client_health(**kw),
        'HEALTH_HTTP_CLIENT': lambda **kw: __import__('debug_health', fromlist=['_check_http_client_health'])._check_http_client_health(**kw),
        
        'DIAGNOSE_HTTP_CLIENT_PERFORMANCE': lambda **kw: __import__('debug_diagnostics', fromlist=['_diagnose_http_client_performance'])._diagnose_http_client_performance(**kw),
        'HTTP_CLIENT_PERFORMANCE': lambda **kw: __import__('debug_diagnostics', fromlist=['_diagnose_http_client_performance'])._diagnose_http_client_performance(**kw),
        'PERFORMANCE_HTTP_CLIENT': lambda **kw: __import__('debug_diagnostics', fromlist=['_diagnose_http_client_performance'])._diagnose_http_client_performance(**kw),
        
        'VALIDATE_HTTP_CLIENT_CONFIGURATION': lambda **kw: __import__('debug_validation', fromlist=['_validate_http_client_configuration'])._validate_http_client_configuration(**kw),
        'HTTP_CLIENT_CONFIGURATION': lambda **kw: __import__('debug_validation', fromlist=['_validate_http_client_configuration'])._validate_http_client_configuration(**kw),
        'CONFIGURATION_HTTP_CLIENT': lambda **kw: __import__('debug_validation', fromlist=['_validate_http_client_configuration'])._validate_http_client_configuration(**kw),
        
        'BENCHMARK_HTTP_CLIENT_OPERATIONS': lambda **kw: __import__('debug_performance', fromlist=['_benchmark_http_client_operations'])._benchmark_http_client_operations(**kw),
        'HTTP_CLIENT_BENCHMARK': lambda **kw: __import__('debug_performance', fromlist=['_benchmark_http_client_operations'])._benchmark_http_client_operations(**kw),
        'BENCHMARK_HTTP_CLIENT': lambda **kw: __import__('debug_performance', fromlist=['_benchmark_http_client_operations'])._benchmark_http_client_operations(**kw),
        
        # Validation operations
        'VALIDATE_SYSTEM_ARCHITECTURE': lambda **kw: __import__('debug_validation', fromlist=['_validate_system_architecture'])._validate_system_architecture(**kw),
        'SYSTEM_ARCHITECTURE': lambda **kw: __import__('debug_validation', fromlist=['_validate_system_architecture'])._validate_system_architecture(**kw),
        
        'VALIDATE_IMPORTS': lambda **kw: __import__('debug_validation', fromlist=['_validate_imports'])._validate_imports(**kw),
        'IMPORTS': lambda **kw: __import__('debug_validation', fromlist=['_validate_imports'])._validate_imports(**kw),
        
        'VALIDATE_GATEWAY_ROUTING': lambda **kw: __import__('debug_validation', fromlist=['_validate_gateway_routing'])._validate_gateway_routing(**kw),
        'GATEWAY_ROUTING': lambda **kw: __import__('debug_validation', fromlist=['_validate_gateway_routing'])._validate_gateway_routing(**kw),
        
        'RUN_CONFIG_UNIT_TESTS': lambda **kw: __import__('debug_validation', fromlist=['_run_config_unit_tests'])._run_config_unit_tests(**kw),
        'CONFIG_UNIT_TESTS': lambda **kw: __import__('debug_validation', fromlist=['_run_config_unit_tests'])._run_config_unit_tests(**kw),
        
        'RUN_CONFIG_INTEGRATION_TESTS': lambda **kw: __import__('debug_validation', fromlist=['_run_config_integration_tests'])._run_config_integration_tests(**kw),
        'CONFIG_INTEGRATION_TESTS': lambda **kw: __import__('debug_validation', fromlist=['_run_config_integration_tests'])._run_config_integration_tests(**kw),
        
        'RUN_CONFIG_PERFORMANCE_TESTS': lambda **kw: __import__('debug_validation', fromlist=['_run_config_performance_tests'])._run_config_performance_tests(**kw),
        'CONFIG_PERFORMANCE_TESTS': lambda **kw: __import__('debug_validation', fromlist=['_run_config_performance_tests'])._run_config_performance_tests(**kw),
        
        'RUN_CONFIG_COMPATIBILITY_TESTS': lambda **kw: __import__('debug_validation', fromlist=['_run_config_compatibility_tests'])._run_config_compatibility_tests(**kw),
        'CONFIG_COMPATIBILITY_TESTS': lambda **kw: __import__('debug_validation', fromlist=['_run_config_compatibility_tests'])._run_config_compatibility_tests(**kw),
        
        'RUN_CONFIG_GATEWAY_TESTS': lambda **kw: __import__('debug_validation', fromlist=['_run_config_gateway_tests'])._run_config_gateway_tests(**kw),
        'CONFIG_GATEWAY_TESTS': lambda **kw: __import__('debug_validation', fromlist=['_run_config_gateway_tests'])._run_config_gateway_tests(**kw),
        
        # Statistics operations
        'GET_SYSTEM_STATS': lambda **kw: __import__('debug_stats', fromlist=['_get_system_stats'])._get_system_stats(**kw),
        'SYSTEM_STATS': lambda **kw: __import__('debug_stats', fromlist=['_get_system_stats'])._get_system_stats(**kw),
        
        'GET_OPTIMIZATION_STATS': lambda **kw: __import__('debug_stats', fromlist=['_get_optimization_stats'])._get_optimization_stats(**kw),
        'OPTIMIZATION_STATS': lambda **kw: __import__('debug_stats', fromlist=['_get_optimization_stats'])._get_optimization_stats(**kw),
        
        'GET_DISPATCHER_STATS': lambda **kw: __import__('debug_stats', fromlist=['_get_dispatcher_stats'])._get_dispatcher_stats(**kw),
        'DISPATCHER_STATS': lambda **kw: __import__('debug_stats', fromlist=['_get_dispatcher_stats'])._get_dispatcher_stats(**kw),
        
        'GET_OPERATION_METRICS': lambda **kw: __import__('debug_stats', fromlist=['_get_operation_metrics'])._get_operation_metrics(**kw),
        'OPERATION_METRICS': lambda **kw: __import__('debug_stats', fromlist=['_get_operation_metrics'])._get_operation_metrics(**kw),
        
        'GET_GATEWAY_STATS': lambda **kw: __import__('gateway_core', fromlist=['get_gateway_stats']).get_gateway_stats(),
        'GATEWAY_STATS': lambda **kw: __import__('gateway_core', fromlist=['get_gateway_stats']).get_gateway_stats(),
        
        # Performance operations
        'RUN_PERFORMANCE_BENCHMARK': lambda **kw: __import__('debug_performance', fromlist=['_run_performance_benchmark'])._run_performance_benchmark(**kw),
        'PERFORMANCE_BENCHMARK': lambda **kw: __import__('debug_performance', fromlist=['_run_performance_benchmark'])._run_performance_benchmark(**kw),
        
        'COMPARE_DISPATCHER_MODES': lambda **kw: __import__('debug_performance', fromlist=['_compare_dispatcher_modes'])._compare_dispatcher_modes(**kw),
        'DISPATCHER_MODES': lambda **kw: __import__('debug_performance', fromlist=['_compare_dispatcher_modes'])._compare_dispatcher_modes(**kw),
        
        'GET_PERFORMANCE_REPORT': lambda **kw: __import__('debug_performance', fromlist=['_get_performance_report'])._get_performance_report(**kw),
        'PERFORMANCE_REPORT': lambda **kw: __import__('debug_performance', fromlist=['_get_performance_report'])._get_performance_report(**kw),
        
        # Verification operations
        'VERIFY_REGISTRY_OPERATIONS': lambda **kw: __import__('debug_verification', fromlist=['_verify_registry_operations'])._verify_registry_operations(**kw),
        'REGISTRY_OPERATIONS': lambda **kw: __import__('debug_verification', fromlist=['_verify_registry_operations'])._verify_registry_operations(**kw),
        
        'ANALYZE_NAMING_PATTERNS': lambda **kw: __import__('debug_verification', fromlist=['_analyze_naming_patterns'])._analyze_naming_patterns(**kw),
        'NAMING_PATTERNS': lambda **kw: __import__('debug_verification', fromlist=['_analyze_naming_patterns'])._analyze_naming_patterns(**kw),
        
        'GENERATE_VERIFICATION_REPORT': lambda **kw: __import__('debug_verification', fromlist=['_generate_verification_report'])._generate_verification_report(**kw),
        'VERIFICATION_REPORT': lambda **kw: __import__('debug_verification', fromlist=['_generate_verification_report'])._generate_verification_report(**kw),
        
        # Placeholder operations (not yet implemented)
        'RUN_DEBUG_TESTS': lambda **kw: {'success': True, 'message': 'Debug tests placeholder', 'tests_run': 0},
        'DEBUG_TESTS': lambda **kw: {'success': True, 'message': 'Debug tests placeholder', 'tests_run': 0},
        
        'VALIDATE_OPERATION_SIGNATURES': lambda **kw: {'success': True, 'message': 'Operation signatures validation placeholder'},
        'OPERATION_SIGNATURES': lambda **kw: {'success': True, 'message': 'Operation signatures validation placeholder'},
        
        'VALIDATE_INTERFACE_COMPLIANCE': lambda **kw: {'success': True, 'message': 'Interface compliance validation placeholder'},
        'INTERFACE_COMPLIANCE': lambda **kw: {'success': True, 'message': 'Interface compliance validation placeholder'},
        
        'CHECK_CIRCULAR_DEPENDENCIES': lambda **kw: {'success': True, 'message': 'Circular dependency check placeholder'},
        'CIRCULAR_DEPENDENCIES': lambda **kw: {'success': True, 'message': 'Circular dependency check placeholder'},
        
        'MEASURE_EXECUTION_TIMES': lambda **kw: {'success': True, 'message': 'Execution times measurement placeholder'},
        'EXECUTION_TIMES': lambda **kw: {'success': True, 'message': 'Execution times measurement placeholder'},
        
        'RUN_PERFORMANCE_PROFILE': lambda **kw: {'success': True, 'message': 'Performance profiling placeholder'},
        'PERFORMANCE_PROFILE': lambda **kw: {'success': True, 'message': 'Performance profiling placeholder'},
        
        'RUN_MEMORY_PROFILE': lambda **kw: {'success': True, 'message': 'Memory profiling placeholder'},
        'MEMORY_PROFILE': lambda **kw: {'success': True, 'message': 'Memory profiling placeholder'},
        
        'CHECK_MEMORY_USAGE': lambda **kw: {'success': True, 'message': 'Memory usage check placeholder'},
        'MEMORY_USAGE': lambda **kw: {'success': True, 'message': 'Memory usage check placeholder'},
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
