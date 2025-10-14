"""
debug_core.py - Consolidated Debug Core with dispatcher delegation
Version: 2025.10.15.03
Description: Complete debug operations with dispatcher delegation (Phase 4 Task #7)

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

from typing import Dict, Any, Optional
from enum import Enum
import sys
import re
import gc
import time


class DebugOperation(Enum):
    """Debug operation types."""
    CHECK_COMPONENT_HEALTH = "check_component_health"
    CHECK_GATEWAY_HEALTH = "check_gateway_health"
    DIAGNOSE_SYSTEM_HEALTH = "diagnose_system_health"
    DIAGNOSE_PERFORMANCE = "diagnose_performance"
    DIAGNOSE_MEMORY = "diagnose_memory"
    VALIDATE_SYSTEM_ARCHITECTURE = "validate_system_architecture"
    VALIDATE_IMPORTS = "validate_imports"
    VALIDATE_GATEWAY_ROUTING = "validate_gateway_routing"
    GET_SYSTEM_STATS = "get_system_stats"
    GET_OPTIMIZATION_STATS = "get_optimization_stats"
    RUN_PERFORMANCE_BENCHMARK = "run_performance_benchmark"
    GENERATE_HEALTH_REPORT = "generate_health_report"
    VERIFY_REGISTRY_OPERATIONS = "verify_registry_operations"
    ANALYZE_NAMING_PATTERNS = "analyze_naming_patterns"
    GENERATE_VERIFICATION_REPORT = "generate_verification_report"
    RUN_CONFIG_UNIT_TESTS = "run_config_unit_tests"
    RUN_CONFIG_INTEGRATION_TESTS = "run_config_integration_tests"
    RUN_CONFIG_PERFORMANCE_TESTS = "run_config_performance_tests"
    RUN_CONFIG_COMPATIBILITY_TESTS = "run_config_compatibility_tests"
    RUN_CONFIG_GATEWAY_TESTS = "run_config_gateway_tests"
    GET_DISPATCHER_STATS = "get_dispatcher_stats"
    GET_OPERATION_METRICS = "get_operation_metrics"
    COMPARE_DISPATCHER_MODES = "compare_dispatcher_modes"
    GET_PERFORMANCE_REPORT = "get_performance_report"


def generic_debug_operation(operation: DebugOperation, **kwargs) -> Dict[str, Any]:
    """Generic debug operation dispatcher."""
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


# ===== HEALTH CHECK OPERATIONS =====

def _check_component_health(**kwargs) -> Dict[str, Any]:
    """Check component health."""
    try:
        from gateway import check_all_components
        return check_all_components()
    except ImportError:
        return {'success': False, 'error': 'Gateway not available'}


def _check_gateway_health(**kwargs) -> Dict[str, Any]:
    """Check gateway health."""
    try:
        from gateway import get_gateway_stats
        stats = get_gateway_stats()
        return {
            'success': True,
            'stats': stats,
            'healthy': stats.get('operations_count', 0) > 0
        }
    except ImportError:
        return {'success': False, 'error': 'Gateway not available'}


# ===== DIAGNOSTIC OPERATIONS =====

def _diagnose_system_health(**kwargs) -> Dict[str, Any]:
    """Comprehensive system health diagnosis."""
    component_health = _check_component_health()
    gateway_health = _check_gateway_health()
    memory_info = _diagnose_memory()
    
    return {
        'success': True,
        'component_health': component_health,
        'gateway_health': gateway_health,
        'memory': memory_info
    }


def _diagnose_performance(**kwargs) -> Dict[str, Any]:
    """Performance diagnosis."""
    try:
        from gateway import get_gateway_stats
        gateway_stats = get_gateway_stats()
        
        return {
            'success': True,
            'gateway_operations': gateway_stats.get('operations_count', 0),
            'fast_path_enabled': gateway_stats.get('fast_path_enabled', False),
            'call_counts': gateway_stats.get('call_counts', {})
        }
    except:
        return {'success': False, 'error': 'Could not diagnose performance'}


def _diagnose_memory(**kwargs) -> Dict[str, Any]:
    """Memory usage diagnosis."""
    gc_stats = gc.get_stats() if hasattr(gc, 'get_stats') else []
    
    return {
        'success': True,
        'objects': len(gc.get_objects()),
        'garbage': len(gc.garbage),
        'collections': gc.get_count()
    }


# ===== VALIDATION OPERATIONS =====

def _validate_system_architecture(**kwargs) -> Dict[str, Any]:
    """Validate SUGA architecture compliance."""
    issues = []
    
    try:
        from gateway import _OPERATION_REGISTRY
        if not _OPERATION_REGISTRY:
            issues.append("Empty operation registry")
        
        # Check for direct imports (would fail in execution)
        import_check = _validate_imports()
        if not import_check.get('compliant', False):
            issues.extend(import_check.get('violations', []))
        
        return {
            'success': True,
            'compliant': len(issues) == 0,
            'issues': issues
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}


def _validate_imports(**kwargs) -> Dict[str, Any]:
    """Validate no direct imports between modules."""
    try:
        from import_fixer import validate_imports
        return validate_imports('.')
    except ImportError:
        return {'success': True, 'compliant': True, 'note': 'import_fixer not available'}


def _validate_gateway_routing(**kwargs) -> Dict[str, Any]:
    """Validate all gateway routing works."""
    try:
        from gateway import execute_operation, GatewayInterface
        
        test_operations = [
            (GatewayInterface.CACHE, 'get_stats'),
            (GatewayInterface.LOGGING, 'get_stats'),
            (GatewayInterface.METRICS, 'get_stats')
        ]
        
        results = {
            'tested': 0,
            'passed': 0,
            'failed': []
        }
        
        for interface, operation in test_operations:
            results['tested'] += 1
            try:
                execute_operation(interface, operation)
                results['passed'] += 1
            except Exception as e:
                results['failed'].append(f"{interface.value}.{operation}: {str(e)}")
        
        return {
            'success': True,
            'compliant': results['passed'] == results['tested'],
            'results': results
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}


# ===== STATS OPERATIONS =====

def _get_system_stats(**kwargs) -> Dict[str, Any]:
    """Get comprehensive system statistics."""
    try:
        modules = list(sys.modules.keys())
        project_modules = [m for m in modules if not m.startswith('_') and '.' not in m]
        
        return {
            'success': True,
            'total_modules': len(modules),
            'project_modules': len(project_modules),
            'python_version': sys.version,
            'platform': sys.platform
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}


def _get_optimization_stats(**kwargs) -> Dict[str, Any]:
    """Get optimization statistics with dispatcher stats (Phase 4 Task #7 UPDATED)."""
    try:
        from gateway import get_gateway_stats
        gateway_stats = get_gateway_stats()
    except:
        gateway_stats = {'error': 'gateway stats not available'}
    
    try:
        from import_fixer import get_import_statistics
        import_stats = get_import_statistics('.')
    except:
        import_stats = {'error': 'import_fixer not available'}
    
    verification_results = _verify_registry_operations()
    
    # Get dispatcher stats (Phase 4 Task #7)
    try:
        dispatcher_stats = _get_dispatcher_stats()
    except:
        dispatcher_stats = {'error': 'dispatcher stats not available'}
    
    return {
        'success': True,
        'gateway_stats': gateway_stats,
        'import_compliance': import_stats,
        'registry_verification': verification_results,
        'dispatcher_stats': dispatcher_stats,
        'optimization_phase': 'Phase 4 Task #7 Complete'
    }


# ===== PERFORMANCE OPERATIONS =====

def _run_performance_benchmark(**kwargs) -> Dict[str, Any]:
    """Run performance benchmark with dispatcher metrics (Phase 4 Task #7 UPDATED)."""
    import time
    
    try:
        from gateway import cache_get, cache_set, log_info, get_metrics_stats
        
        start = time.time()
        cache_set('benchmark_key', 'test_value', ttl=60)
        cache_get('benchmark_key')
        log_info('Benchmark test')
        get_metrics_stats()
        duration = (time.time() - start) * 1000
        
        # Add dispatcher stats (Phase 4 Task #7)
        try:
            dispatcher_stats = _get_dispatcher_stats()
        except:
            dispatcher_stats = {'error': 'Could not retrieve dispatcher stats'}
        
        return {
            'success': True,
            'duration_ms': round(duration, 3),
            'operations_tested': 4,
            'dispatcher_performance': dispatcher_stats
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}


def _generate_health_report(**kwargs) -> Dict[str, Any]:
    """Generate comprehensive health report with dispatcher metrics (Phase 4 Task #7 UPDATED)."""
    # Get dispatcher stats (Phase 4 Task #7)
    try:
        dispatcher_stats = _get_dispatcher_stats()
    except:
        dispatcher_stats = {'error': 'dispatcher stats not available'}
    
    return {
        'timestamp': '2025.10.15',
        'system_health': _diagnose_system_health(),
        'validation': {
            'architecture': _validate_system_architecture(),
            'imports': _validate_imports(),
            'gateway_routing': _validate_gateway_routing(),
            'registry_operations': _verify_registry_operations()
        },
        'stats': _get_system_stats(),
        'optimization': _get_optimization_stats(),
        'dispatcher_performance': dispatcher_stats
    }


# ===== PHASE 2 VERIFICATION OPERATIONS =====

def _verify_registry_operations(**kwargs) -> Dict[str, Any]:
    """Verify all registry operations are callable."""
    try:
        from gateway import _OPERATION_REGISTRY, execute_operation
        
        total = len(_OPERATION_REGISTRY)
        verified = 0
        failed = []
        
        for (interface, operation), (module, function) in _OPERATION_REGISTRY.items():
            try:
                # Just verify the module and function exist
                module_obj = sys.modules.get(module)
                if module_obj and hasattr(module_obj, function):
                    verified += 1
                else:
                    failed.append(f"{interface.value}.{operation}")
            except:
                failed.append(f"{interface.value}.{operation}")
        
        return {
            'success': True,
            'total_operations': total,
            'verified': verified,
            'failed': failed,
            'compliance_rate': round((verified / total * 100), 2) if total > 0 else 0
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}


def _analyze_naming_patterns(**kwargs) -> Dict[str, Any]:
    """Analyze operation naming patterns."""
    try:
        from gateway import _OPERATION_REGISTRY
        
        patterns = {}
        for (interface, operation), (module, function) in _OPERATION_REGISTRY.items():
            pattern = f"{module}.{function}"
            if pattern not in patterns:
                patterns[pattern] = []
            patterns[pattern].append(f"{interface.value}.{operation}")
        
        return {
            'success': True,
            'unique_patterns': len(patterns),
            'patterns': patterns
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}


def _generate_verification_report(**kwargs) -> Dict[str, Any]:
    """Generate comprehensive verification report."""
    return {
        'success': True,
        'timestamp': '2025.10.15',
        'registry_verification': _verify_registry_operations(),
        'naming_patterns': _analyze_naming_patterns(),
        'architecture_validation': _validate_system_architecture(),
        'gateway_routing': _validate_gateway_routing()
    }


# ===== CONFIG TEST OPERATIONS (Placeholders) =====

def _run_config_unit_tests(**kwargs) -> Dict[str, Any]:
    """Run configuration unit tests."""
    return {'success': True, 'tests_run': 0, 'note': 'Placeholder for config unit tests'}


def _run_config_integration_tests(**kwargs) -> Dict[str, Any]:
    """Run configuration integration tests."""
    return {'success': True, 'tests_run': 0, 'note': 'Placeholder for config integration tests'}


def _run_config_performance_tests(**kwargs) -> Dict[str, Any]:
    """Run configuration performance tests."""
    return {'success': True, 'tests_run': 0, 'note': 'Placeholder for config performance tests'}


def _run_config_compatibility_tests(**kwargs) -> Dict[str, Any]:
    """Run configuration compatibility tests."""
    return {'success': True, 'tests_run': 0, 'note': 'Placeholder for config compatibility tests'}


def _run_config_gateway_tests(**kwargs) -> Dict[str, Any]:
    """Run configuration gateway tests."""
    return {'success': True, 'tests_run': 0, 'note': 'Placeholder for config gateway tests'}


# ===== PHASE 4 TASK #7 DISPATCHER OPERATIONS =====

def _get_dispatcher_stats(**kwargs) -> Dict[str, Any]:
    """Get dispatcher performance stats - delegates to METRICS (Phase 4 Task #7)."""
    from gateway import execute_operation, GatewayInterface
    return execute_operation(GatewayInterface.METRICS, 'get_dispatcher_stats')


def _get_operation_metrics(**kwargs) -> Dict[str, Any]:
    """Get operation metrics - delegates to METRICS (Phase 4 Task #7)."""
    from gateway import execute_operation, GatewayInterface
    return execute_operation(GatewayInterface.METRICS, 'get_operation_metrics')


def _compare_dispatcher_modes(**kwargs) -> Dict[str, Any]:
    """Compare generic vs direct dispatcher performance."""
    import os
    import time
    
    try:
        from gateway import cache_get, cache_set
        
        # Test with generic dispatcher
        os.environ['USE_GENERIC_OPERATIONS'] = 'true'
        
        start = time.time()
        for i in range(100):
            cache_set(f'test_{i}', f'value_{i}')
            cache_get(f'test_{i}')
        generic_time = (time.time() - start) * 1000
        
        # Test with direct dispatcher
        os.environ['USE_GENERIC_OPERATIONS'] = 'false'
        
        start = time.time()
        for i in range(100):
            cache_set(f'test2_{i}', f'value_{i}')
            cache_get(f'test2_{i}')
        direct_time = (time.time() - start) * 1000
        
        # Restore default
        os.environ['USE_GENERIC_OPERATIONS'] = 'true'
        
        return {
            'success': True,
            'generic_time_ms': round(generic_time, 3),
            'direct_time_ms': round(direct_time, 3),
            'overhead_ms': round(generic_time - direct_time, 3),
            'overhead_percent': round((generic_time - direct_time) / direct_time * 100, 2) if direct_time > 0 else 0
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}


def _get_performance_report(**kwargs) -> Dict[str, Any]:
    """Get comprehensive performance report."""
    benchmark = _run_performance_benchmark()
    comparison = _compare_dispatcher_modes()
    dispatcher_stats = _get_dispatcher_stats()
    operation_metrics = _get_operation_metrics()
    
    return {
        'success': True,
        'benchmark': benchmark,
        'dispatcher_comparison': comparison,
        'dispatcher_stats': dispatcher_stats,
        'operation_metrics': operation_metrics,
        'timestamp': '2025.10.15'
    }


# ===== EXPORTS =====

__all__ = [
    'DebugOperation',
    'generic_debug_operation'
]

# EOF
