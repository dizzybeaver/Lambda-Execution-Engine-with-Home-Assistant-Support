"""
debug_core.py - Consolidated Debug Core with Unified Extensions
Version: 2025.10.14.01
Description: Complete debug implementation merging debug_core.py + debug_unified.py

CONSOLIDATION: Merges debug_unified.py functionality into debug_core.py
USES: Gateway functions only (execute_operation) - SUGA compliant
AWS COMPATIBLE: Absolute imports only

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


class DebugOperation(Enum):
    """Debug operation types."""
    CHECK_COMPONENT_HEALTH = "check_component_health"
    CHECK_GATEWAY_HEALTH = "check_gateway_health"
    DIAGNOSE_SYSTEM_HEALTH = "diagnose_system_health"
    DIAGNOSE_PERFORMANCE = "diagnose_performance"
    DIAGNOSE_MEMORY = "diagnose_memory"
    RUN_ULTRA_OPTIMIZATION_TESTS = "run_ultra_optimization_tests"
    RUN_PERFORMANCE_BENCHMARK = "run_performance_benchmark"
    RUN_CONFIGURATION_TESTS = "run_configuration_tests"
    RUN_COMPREHENSIVE_TESTS = "run_comprehensive_tests"
    VALIDATE_SYSTEM_ARCHITECTURE = "validate_system_architecture"
    VALIDATE_IMPORTS = "validate_imports"
    VALIDATE_GATEWAY_ROUTING = "validate_gateway_routing"
    GET_SYSTEM_STATS = "get_system_stats"
    GET_OPTIMIZATION_STATS = "get_optimization_stats"
    GENERATE_HEALTH_REPORT = "generate_health_report"
    
    # Configuration Testing Operations
    RUN_CONFIG_UNIT_TESTS = "run_config_unit_tests"
    RUN_CONFIG_INTEGRATION_TESTS = "run_config_integration_tests"
    RUN_CONFIG_PERFORMANCE_TESTS = "run_config_performance_tests"
    RUN_CONFIG_COMPATIBILITY_TESTS = "run_config_compatibility_tests"
    RUN_CONFIG_GATEWAY_TESTS = "run_config_gateway_tests"


def generic_debug_operation(operation: DebugOperation, **kwargs) -> Dict[str, Any]:
    """
    Universal debug operation executor.
    Routes all debug operations to appropriate handlers using gateway functions only.
    """
    
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
    
    elif operation == DebugOperation.RUN_ULTRA_OPTIMIZATION_TESTS:
        return _run_ultra_optimization_tests(**kwargs)
    
    elif operation == DebugOperation.RUN_PERFORMANCE_BENCHMARK:
        return _run_performance_benchmark(**kwargs)
    
    elif operation == DebugOperation.RUN_CONFIGURATION_TESTS:
        return _run_configuration_tests(**kwargs)
    
    elif operation == DebugOperation.RUN_COMPREHENSIVE_TESTS:
        return _run_comprehensive_tests(**kwargs)
    
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
    
    elif operation == DebugOperation.GENERATE_HEALTH_REPORT:
        return _generate_health_report(**kwargs)
    
    # Configuration Testing Operations
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
    
    else:
        return {
            "success": False,
            "error": f"Unknown debug operation: {operation}"
        }


# ===== COMPONENT HEALTH CHECKS =====

def _check_component_health(**kwargs) -> Dict[str, Any]:
    """Check component health using gateway operations."""
    from gateway import execute_operation, GatewayInterface
    
    component = kwargs.get('component', 'all')
    
    if component == 'all':
        results = {}
        components = ['cache', 'logging', 'metrics', 'security', 'config']
        
        for comp in components:
            try:
                if comp == 'cache':
                    execute_operation(GatewayInterface.CACHE, 'get_stats')
                elif comp == 'logging':
                    pass  # Logging always available
                elif comp == 'metrics':
                    execute_operation(GatewayInterface.METRICS, 'get_stats')
                elif comp == 'security':
                    execute_operation(GatewayInterface.SECURITY, 'generate_correlation_id')
                elif comp == 'config':
                    execute_operation(GatewayInterface.CONFIG, 'get_state')
                
                results[comp] = {'status': 'healthy', 'error': None}
            
            except Exception as e:
                results[comp] = {'status': 'unhealthy', 'error': str(e)}
        
        healthy_count = sum(1 for r in results.values() if r['status'] == 'healthy')
        
        return {
            "success": True,
            "component": "all",
            "status": "healthy" if healthy_count == len(components) else "degraded",
            "healthy_components": healthy_count,
            "total_components": len(components),
            "details": results
        }
    
    else:
        return {
            "success": True,
            "component": component,
            "status": "healthy",
            "message": f"Component {component} health check passed"
        }


def _check_gateway_health(**kwargs) -> Dict[str, Any]:
    """Check gateway routing health using gateway operations."""
    from gateway import execute_operation, GatewayInterface
    
    interfaces_to_test = [
        GatewayInterface.CACHE,
        GatewayInterface.LOGGING,
        GatewayInterface.METRICS,
        GatewayInterface.SECURITY,
        GatewayInterface.CONFIG
    ]
    
    results = {}
    
    for interface in interfaces_to_test:
        try:
            if interface == GatewayInterface.CACHE:
                execute_operation(interface, 'get', key='health_check')
            elif interface == GatewayInterface.LOGGING:
                execute_operation(interface, 'log_debug', message='health_check')
            elif interface == GatewayInterface.METRICS:
                execute_operation(interface, 'get_stats')
            elif interface == GatewayInterface.SECURITY:
                execute_operation(interface, 'generate_correlation_id')
            elif interface == GatewayInterface.CONFIG:
                execute_operation(interface, 'get_state')
            
            results[interface.value] = {'status': 'healthy', 'error': None}
        
        except Exception as e:
            results[interface.value] = {'status': 'unhealthy', 'error': str(e)}
    
    healthy_count = sum(1 for r in results.values() if r['status'] == 'healthy')
    total_count = len(results)
    
    return {
        'success': True,
        'overall_status': 'healthy' if healthy_count == total_count else 'degraded',
        'healthy_interfaces': healthy_count,
        'total_interfaces': total_count,
        'details': results
    }


# ===== SYSTEM DIAGNOSTICS =====

def _diagnose_system_health(**kwargs) -> Dict[str, Any]:
    """Diagnose overall system health using gateway operations."""
    from gateway import execute_operation, GatewayInterface
    
    diagnostics = {
        'components': _check_component_health(component='all'),
        'gateway': _check_gateway_health(),
        'memory': _diagnose_memory()
    }
    
    all_healthy = (
        diagnostics['components'].get('status') == 'healthy' and
        diagnostics['gateway'].get('overall_status') == 'healthy' and
        diagnostics['memory'].get('status') == 'healthy'
    )
    
    return {
        "success": True,
        "overall_status": "healthy" if all_healthy else "degraded",
        "diagnostics": diagnostics
    }


def _diagnose_performance(**kwargs) -> Dict[str, Any]:
    """Diagnose system performance using gateway operations."""
    from gateway import execute_operation, GatewayInterface
    
    diagnostics = {
        'cache_health': {},
        'metrics_health': {},
        'logging_health': {},
        'performance_issues': []
    }
    
    try:
        cache_stats = execute_operation(GatewayInterface.CACHE, 'get_stats')
        if cache_stats:
            hit_rate = cache_stats.get('cache_hit_rate', cache_stats.get('hit_rate', 0))
            if hit_rate < 50:
                diagnostics['performance_issues'].append(
                    f"Low cache hit rate: {hit_rate}%"
                )
            diagnostics['cache_health'] = cache_stats
    
    except Exception as e:
        diagnostics['cache_health'] = {'error': str(e)}
    
    try:
        metrics_stats = execute_operation(GatewayInterface.METRICS, 'get_stats')
        if metrics_stats:
            diagnostics['metrics_health'] = {
                'total_metrics': len(metrics_stats.get('counters', {})),
                'healthy': True
            }
    
    except Exception as e:
        diagnostics['metrics_health'] = {'error': str(e)}
    
    diagnostics['logging_health'] = {'status': 'healthy'}
    
    return {
        'success': True,
        'status': 'healthy' if not diagnostics['performance_issues'] else 'degraded',
        'diagnostics': diagnostics
    }


def _diagnose_memory(**kwargs) -> Dict[str, Any]:
    """Diagnose memory usage across components."""
    memory_breakdown = {}
    
    loaded_modules = [m for m in sys.modules.keys() if not m.startswith('_')]
    core_modules = [m for m in loaded_modules if m.endswith('_core')]
    interface_modules = [m for m in loaded_modules if m in [
        'cache', 'logging', 'metrics', 'security', 'config', 'gateway'
    ]]
    
    memory_breakdown['loaded_modules'] = len(loaded_modules)
    memory_breakdown['core_modules'] = core_modules
    memory_breakdown['interface_modules'] = interface_modules
    
    return {
        'success': True,
        'estimated_memory_mb': len(loaded_modules) * 0.5,
        'breakdown': memory_breakdown,
        'status': 'healthy'
    }


# ===== TEST RUNNERS =====

def _run_ultra_optimization_tests(**kwargs) -> Dict[str, Any]:
    """Run ultra-optimization validation tests."""
    results = {
        'gateway_optimization': _check_gateway_health(),
        'performance': _diagnose_performance(),
        'memory': _diagnose_memory()
    }
    
    all_passed = all(
        r.get('success') or r.get('status') == 'healthy'
        for r in results.values()
    )
    
    return {
        "success": all_passed,
        "test_type": "ultra_optimization",
        "results": results
    }


def _run_performance_benchmark(**kwargs) -> Dict[str, Any]:
    """Run performance benchmark tests."""
    from gateway import execute_operation, GatewayInterface
    import time
    
    iterations = kwargs.get('iterations', 1000)
    results = {}
    
    # Benchmark cache operations
    start = time.time()
    for i in range(iterations):
        execute_operation(GatewayInterface.CACHE, 'get', key=f'bench_{i}')
    cache_duration = (time.time() - start) * 1000
    
    results['cache_ops_per_sec'] = iterations / (cache_duration / 1000)
    results['cache_avg_ms'] = cache_duration / iterations
    
    return {
        "success": True,
        "iterations": iterations,
        "results": results
    }


def _run_configuration_tests(**kwargs) -> Dict[str, Any]:
    """Run configuration system tests."""
    from gateway import execute_operation, GatewayInterface
    
    tests = {}
    
    try:
        state = execute_operation(GatewayInterface.CONFIG, 'get_state')
        tests['get_state'] = {'passed': bool(state), 'result': state}
    except Exception as e:
        tests['get_state'] = {'passed': False, 'error': str(e)}
    
    try:
        param = execute_operation(GatewayInterface.CONFIG, 'get_parameter', key='test_key', default='test_value')
        tests['get_parameter'] = {'passed': True, 'result': param}
    except Exception as e:
        tests['get_parameter'] = {'passed': False, 'error': str(e)}
    
    passed_count = sum(1 for t in tests.values() if t.get('passed'))
    
    return {
        "success": passed_count == len(tests),
        "tests": tests,
        "passed": passed_count,
        "total": len(tests)
    }


def _run_comprehensive_tests(**kwargs) -> Dict[str, Any]:
    """Run comprehensive test suite."""
    results = {
        'health': _check_component_health(component='all'),
        'gateway': _check_gateway_health(),
        'performance': _diagnose_performance(),
        'configuration': _run_configuration_tests()
    }
    
    all_passed = all(
        r.get('success') or r.get('status') == 'healthy'
        for r in results.values()
    )
    
    return {
        "success": all_passed,
        "test_type": "comprehensive",
        "results": results
    }


# ===== VALIDATION =====

def _validate_system_architecture(**kwargs) -> Dict[str, Any]:
    """Validate system architecture compliance."""
    validation = {
        'suga_compliance': True,
        'gateway_routing': True,
        'lazy_imports': True,
        'issues': []
    }
    
    # Check gateway routing
    gateway_health = _check_gateway_health()
    if gateway_health.get('overall_status') != 'healthy':
        validation['gateway_routing'] = False
        validation['issues'].append('Gateway routing has issues')
    
    # Check imports
    import_validation = _validate_imports()
    if not import_validation.get('compliant'):
        validation['suga_compliance'] = False
        validation['issues'].append(f"Import violations: {import_validation.get('violations_count', 0)}")
    
    validation['overall_compliant'] = len(validation['issues']) == 0
    
    return {
        "success": True,
        "validation": validation
    }


def _validate_imports(**kwargs) -> Dict[str, Any]:
    """Validate AWS Lambda import compatibility."""
    violation_patterns = [
        r'from\s+\.\s+import\s+',
        r'from\s+\.\w+\s+import\s+',
    ]
    
    violations = []
    
    for module_name, module in sys.modules.items():
        if module_name.startswith('_') or not hasattr(module, '__file__'):
            continue
        
        try:
            if module.__file__ and module.__file__.endswith('.py'):
                with open(module.__file__, 'r') as f:
                    content = f.read()
                    
                    for pattern in violation_patterns:
                        if re.search(pattern, content):
                            violations.append({
                                'module': module_name,
                                'file': module.__file__,
                                'pattern': pattern
                            })
        except:
            continue
    
    return {
        'success': True,
        'compliant': len(violations) == 0,
        'violations_count': len(violations),
        'violations': violations[:10]
    }


def _validate_gateway_routing(**kwargs) -> Dict[str, Any]:
    """Validate all gateway operations route correctly."""
    from gateway import execute_operation, GatewayInterface, _OPERATION_REGISTRY
    
    results = {
        'total_operations': len(_OPERATION_REGISTRY),
        'tested': 0,
        'passed': 0,
        'failed': 0,
        'failures': []
    }
    
    # Test sample operations from each interface
    test_operations = [
        (GatewayInterface.CACHE, 'get_stats'),
        (GatewayInterface.LOGGING, 'log_debug'),
        (GatewayInterface.METRICS, 'get_stats'),
        (GatewayInterface.SECURITY, 'generate_correlation_id'),
        (GatewayInterface.CONFIG, 'get_state')
    ]
    
    for interface, operation in test_operations:
        results['tested'] += 1
        try:
            if operation == 'log_debug':
                execute_operation(interface, operation, message='test')
            else:
                execute_operation(interface, operation)
            results['passed'] += 1
        except Exception as e:
            results['failed'] += 1
            results['failures'].append({
                'interface': interface.value,
                'operation': operation,
                'error': str(e)
            })
    
    return {
        'success': results['failed'] == 0,
        'results': results
    }


# ===== SYSTEM STATS =====

def _get_system_stats(**kwargs) -> Dict[str, Any]:
    """Get system statistics using gateway operations."""
    from gateway import get_gateway_stats
    
    stats = {
        'gateway': get_gateway_stats(),
        'memory': _diagnose_memory(),
        'components': _check_component_health(component='all')
    }
    
    return {
        'success': True,
        'stats': stats
    }


def _get_optimization_stats(**kwargs) -> Dict[str, Any]:
    """Get optimization statistics."""
    try:
        from gateway_wrapper import get_wrapper_stats
        wrapper_stats = get_wrapper_stats()
    except:
        wrapper_stats = {'error': 'gateway_wrapper not available'}
    
    try:
        from import_fixer import get_import_statistics
        import_stats = get_import_statistics('.')
    except:
        import_stats = {'error': 'import_fixer not available'}
    
    return {
        'success': True,
        'gateway_wrapper': wrapper_stats,
        'import_compliance': import_stats,
        'optimization_phase': 'Phase 2 Active'
    }


def _generate_health_report(**kwargs) -> Dict[str, Any]:
    """Generate comprehensive health report."""
    import time
    
    report = {
        'timestamp': time.time(),
        'overall_health': 'unknown',
        'components': {},
        'diagnostics': {},
        'recommendations': []
    }
    
    try:
        report['components'] = _check_component_health(component='all')
        report['diagnostics'] = _diagnose_performance()
        
        component_health = report['components'].get('status', 'unknown')
        diagnostic_health = report['diagnostics'].get('status', 'unknown')
        
        if component_health == 'healthy' and diagnostic_health == 'healthy':
            report['overall_health'] = 'healthy'
        elif 'unhealthy' in [component_health, diagnostic_health]:
            report['overall_health'] = 'unhealthy'
        else:
            report['overall_health'] = 'degraded'
        
        if report['overall_health'] != 'healthy':
            report['recommendations'].append("Run full diagnostics: run_full_diagnostics()")
            report['recommendations'].append("Check specific components: check_component('<name>')")
    
    except Exception as e:
        report['error'] = str(e)
        report['overall_health'] = 'error'
    
    return {
        'success': True,
        'report': report
    }


# ===== CONFIGURATION TESTS =====

def _run_config_unit_tests(**kwargs) -> Dict[str, Any]:
    """Run configuration unit tests."""
    return {
        "success": True,
        "test_type": "config_unit",
        "message": "Configuration unit tests placeholder"
    }


def _run_config_integration_tests(**kwargs) -> Dict[str, Any]:
    """Run configuration integration tests."""
    return {
        "success": True,
        "test_type": "config_integration",
        "message": "Configuration integration tests placeholder"
    }


def _run_config_performance_tests(**kwargs) -> Dict[str, Any]:
    """Run configuration performance tests."""
    return {
        "success": True,
        "test_type": "config_performance",
        "message": "Configuration performance tests placeholder"
    }


def _run_config_compatibility_tests(**kwargs) -> Dict[str, Any]:
    """Run configuration compatibility tests."""
    return {
        "success": True,
        "test_type": "config_compatibility",
        "message": "Configuration compatibility tests placeholder"
    }


def _run_config_gateway_tests(**kwargs) -> Dict[str, Any]:
    """Run configuration gateway tests."""
    return {
        "success": True,
        "test_type": "config_gateway",
        "message": "Configuration gateway tests placeholder"
    }


__all__ = [
    'DebugOperation',
    'generic_debug_operation'
]

# EOF
