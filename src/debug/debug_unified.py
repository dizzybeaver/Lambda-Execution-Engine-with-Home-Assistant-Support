"""
debug_unified.py
Version: 2025.10.13.01
Description: Unified debug extensions with comprehensive system diagnostics

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

from typing import Dict, Any, Optional, List
from gateway import execute_operation, GatewayInterface
from debug_core import DebugOperation


# ===== COMPONENT HEALTH CHECKS =====

def check_all_components() -> Dict[str, Any]:
    """
    Check health of all system components.
    Unified component checking pattern.
    """
    from debug_core import generic_debug_operation
    
    return generic_debug_operation(
        DebugOperation.CHECK_COMPONENT_HEALTH,
        component='all'
    )


def check_component(component_name: str) -> Dict[str, Any]:
    """
    Check specific component health.
    Unified component checking pattern.
    """
    from debug_core import generic_debug_operation
    
    return generic_debug_operation(
        DebugOperation.CHECK_COMPONENT_HEALTH,
        component=component_name
    )


def check_gateway_health() -> Dict[str, Any]:
    """
    Check gateway routing health.
    Tests all gateway interfaces.
    """
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
            # Test basic operation on each interface
            if interface == GatewayInterface.CACHE:
                execute_operation(interface, 'get', key='health_check')
            elif interface == GatewayInterface.LOGGING:
                execute_operation(interface, 'log_debug', message='health_check')
            elif interface == GatewayInterface.METRICS:
                execute_operation(interface, 'get_metrics')
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
        'overall_status': 'healthy' if healthy_count == total_count else 'degraded',
        'healthy_interfaces': healthy_count,
        'total_interfaces': total_count,
        'details': results
    }


# ===== SYSTEM DIAGNOSTICS =====

def run_full_diagnostics() -> Dict[str, Any]:
    """
    Run comprehensive system diagnostics.
    Unified diagnostics pattern.
    """
    from debug_core import generic_debug_operation
    
    return generic_debug_operation(DebugOperation.DIAGNOSE_SYSTEM_HEALTH)


def diagnose_performance() -> Dict[str, Any]:
    """
    Diagnose system performance issues.
    Checks metrics, cache, and operation latency.
    """
    diagnostics = {
        'cache_health': {},
        'metrics_health': {},
        'logging_health': {},
        'performance_issues': []
    }
    
    try:
        # Check cache performance
        cache_stats = execute_operation(GatewayInterface.CACHE, 'get_stats')
        if cache_stats:
            hit_rate = cache_stats.get('hit_rate', 0)
            if hit_rate < 50:
                diagnostics['performance_issues'].append(
                    f"Low cache hit rate: {hit_rate}%"
                )
            diagnostics['cache_health'] = cache_stats
    
    except Exception as e:
        diagnostics['cache_health'] = {'error': str(e)}
    
    try:
        # Check metrics performance
        metrics_stats = execute_operation(GatewayInterface.METRICS, 'get_metrics')
        if metrics_stats:
            diagnostics['metrics_health'] = {
                'total_metrics': len(metrics_stats),
                'healthy': True
            }
    
    except Exception as e:
        diagnostics['metrics_health'] = {'error': str(e)}
    
    return {
        'status': 'healthy' if not diagnostics['performance_issues'] else 'degraded',
        'diagnostics': diagnostics
    }


def diagnose_memory_usage() -> Dict[str, Any]:
    """
    Diagnose memory usage across components.
    Estimates memory footprint.
    """
    import sys
    
    memory_breakdown = {}
    
    # Check loaded modules
    loaded_modules = [m for m in sys.modules.keys() if not m.startswith('_')]
    core_modules = [m for m in loaded_modules if m.endswith('_core')]
    interface_modules = [m for m in loaded_modules if m in [
        'cache', 'logging', 'metrics', 'security', 'config', 'gateway'
    ]]
    
    memory_breakdown['loaded_modules'] = len(loaded_modules)
    memory_breakdown['core_modules'] = core_modules
    memory_breakdown['interface_modules'] = interface_modules
    
    return {
        'estimated_memory_mb': len(loaded_modules) * 0.5,  # Rough estimate
        'breakdown': memory_breakdown,
        'status': 'healthy'
    }


# ===== TEST RUNNERS =====

def run_comprehensive_tests() -> Dict[str, Any]:
    """
    Run comprehensive test suite.
    Unified test execution pattern.
    """
    from debug_core import generic_debug_operation
    
    return generic_debug_operation(DebugOperation.RUN_COMPREHENSIVE_TESTS)


def run_performance_tests() -> Dict[str, Any]:
    """
    Run performance benchmark tests.
    Unified performance testing pattern.
    """
    from debug_core import generic_debug_operation
    
    return generic_debug_operation(DebugOperation.RUN_PERFORMANCE_BENCHMARK)


def run_configuration_tests() -> Dict[str, Any]:
    """
    Run configuration system tests.
    Unified configuration testing pattern.
    """
    from debug_core import generic_debug_operation
    
    return generic_debug_operation(DebugOperation.RUN_CONFIGURATION_TESTS)


def run_ultra_optimization_tests() -> Dict[str, Any]:
    """
    Run ultra-optimization validation tests.
    Tests Phase 1 and Phase 2 optimizations.
    """
    from debug_core import generic_debug_operation
    
    return generic_debug_operation(DebugOperation.RUN_ULTRA_OPTIMIZATION_TESTS)


# ===== VALIDATION =====

def validate_architecture() -> Dict[str, Any]:
    """
    Validate system architecture compliance.
    Checks SUGA/LIGS/LUGS patterns.
    """
    from debug_core import generic_debug_operation
    
    return generic_debug_operation(DebugOperation.VALIDATE_SYSTEM_ARCHITECTURE)


def validate_imports() -> Dict[str, Any]:
    """
    Validate AWS Lambda import compatibility.
    Uses import_fixer to scan for violations.
    """
    try:
        from import_fixer import check_imports
        
        results = check_imports('.', report=False)
        
        return {
            'compliant': results['compliant'],
            'violations': len(results['violations']),
            'statistics': results['statistics']
        }
    
    except Exception as e:
        return {
            'error': str(e),
            'compliant': False
        }


def validate_gateway_routing() -> Dict[str, Any]:
    """
    Validate all gateway operations route correctly.
    Tests each interface operation.
    """
    test_results = {
        'cache': False,
        'logging': False,
        'metrics': False,
        'security': False,
        'config': False
    }
    
    try:
        # Test CACHE
        execute_operation(GatewayInterface.CACHE, 'get', key='test')
        test_results['cache'] = True
    except:
        pass
    
    try:
        # Test LOGGING
        execute_operation(GatewayInterface.LOGGING, 'log_debug', message='test')
        test_results['logging'] = True
    except:
        pass
    
    try:
        # Test METRICS
        execute_operation(GatewayInterface.METRICS, 'get_metrics')
        test_results['metrics'] = True
    except:
        pass
    
    try:
        # Test SECURITY
        execute_operation(GatewayInterface.SECURITY, 'generate_correlation_id')
        test_results['security'] = True
    except:
        pass
    
    try:
        # Test CONFIG
        execute_operation(GatewayInterface.CONFIG, 'get_state')
        test_results['config'] = True
    except:
        pass
    
    passed = sum(test_results.values())
    total = len(test_results)
    
    return {
        'passed': passed,
        'total': total,
        'success_rate': round((passed / total) * 100, 2),
        'details': test_results
    }


# ===== MONITORING AND STATS =====

def get_system_stats() -> Dict[str, Any]:
    """
    Get comprehensive system statistics.
    Aggregates stats from all components.
    """
    stats = {
        'cache': {},
        'metrics': {},
        'logging': {},
        'gateway': {}
    }
    
    try:
        stats['cache'] = execute_operation(GatewayInterface.CACHE, 'get_stats')
    except:
        stats['cache'] = {'error': 'unavailable'}
    
    try:
        stats['metrics'] = execute_operation(GatewayInterface.METRICS, 'get_metrics')
    except:
        stats['metrics'] = {'error': 'unavailable'}
    
    try:
        from gateway import _FAST_PATH_STATS
        stats['gateway'] = _FAST_PATH_STATS.copy()
    except:
        stats['gateway'] = {'error': 'unavailable'}
    
    return stats


def get_optimization_stats() -> Dict[str, Any]:
    """
    Get ultra-optimization statistics.
    Shows Phase 1 and Phase 2 improvements.
    """
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
        'gateway_wrapper': wrapper_stats,
        'import_compliance': import_stats,
        'optimization_phase': 'Phase 2 Active'
    }


# ===== REPORTING =====

def generate_health_report() -> Dict[str, Any]:
    """
    Generate comprehensive health report.
    Includes all diagnostics and tests.
    """
    report = {
        'timestamp': None,
        'overall_health': 'unknown',
        'components': {},
        'diagnostics': {},
        'recommendations': []
    }
    
    try:
        import time
        report['timestamp'] = time.time()
        
        # Component health
        report['components'] = check_all_components()
        
        # Performance diagnostics
        report['diagnostics'] = diagnose_performance()
        
        # Determine overall health
        component_health = report['components'].get('status', 'unknown')
        diagnostic_health = report['diagnostics'].get('status', 'unknown')
        
        if component_health == 'healthy' and diagnostic_health == 'healthy':
            report['overall_health'] = 'healthy'
        elif 'unhealthy' in [component_health, diagnostic_health]:
            report['overall_health'] = 'unhealthy'
        else:
            report['overall_health'] = 'degraded'
        
        # Add recommendations
        if report['overall_health'] != 'healthy':
            report['recommendations'].append("Run full diagnostics: run_full_diagnostics()")
            report['recommendations'].append("Check specific components: check_component('<name>')")
    
    except Exception as e:
        report['error'] = str(e)
        report['overall_health'] = 'error'
    
    return report


# ===== EXPORTED FUNCTIONS =====

__all__ = [
    'check_all_components',
    'check_component',
    'check_gateway_health',
    'run_full_diagnostics',
    'diagnose_performance',
    'diagnose_memory_usage',
    'run_comprehensive_tests',
    'run_performance_tests',
    'run_configuration_tests',
    'run_ultra_optimization_tests',
    'validate_architecture',
    'validate_imports',
    'validate_gateway_routing',
    'get_system_stats',
    'get_optimization_stats',
    'generate_health_report'
]

# EOF
