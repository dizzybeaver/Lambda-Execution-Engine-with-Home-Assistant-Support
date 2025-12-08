"""
diagnosis_health.py
Version: 2025-12-08_1
Purpose: Component health checks and system health reporting
License: Apache 2.0
"""

import time
from typing import Dict, Any


def check_component_health(**kwargs) -> Dict[str, Any]:
    """Check component health."""
    try:
        from gateway import check_all_components
        return check_all_components()
    except ImportError:
        return {'success': False, 'error': 'Gateway not available'}


def check_gateway_health(**kwargs) -> Dict[str, Any]:
    """
    Check gateway health.
    
    PRESERVED FROM: debug_health.py::_check_gateway_health()
    """
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


def generate_health_report(**kwargs) -> Dict[str, Any]:
    """
    Generate comprehensive health report with dispatcher metrics.
    
    PRESERVED FROM: debug_health.py::_generate_health_report()
    """
    # Lazy imports to avoid circular dependencies
    from diagnosis_performance import diagnose_system_health
    from diagnosis_core import (
        validate_system_architecture,
        validate_imports,
        validate_gateway_routing
    )
    from debug_verification import verify_registry_operations
    from debug_stats import get_system_stats, get_optimization_stats, get_dispatcher_stats
    
    try:
        dispatcher_stats = get_dispatcher_stats()
    except:
        dispatcher_stats = {'error': 'dispatcher stats not available'}
    
    return {
        'timestamp': '2025-12-08',
        'system_health': diagnose_system_health(),
        'validation': {
            'architecture': validate_system_architecture(),
            'imports': validate_imports(),
            'gateway_routing': validate_gateway_routing(),
            'registry_operations': verify_registry_operations()
        },
        'stats': get_system_stats(),
        'optimization': get_optimization_stats(),
        'dispatcher_performance': dispatcher_stats
    }


def check_initialization_health(**kwargs) -> Dict[str, Any]:
    """Check INITIALIZATION interface health (AP-08, DEC-04, LESS-17, LESS-18, LESS-21)."""
    try:
        import initialization_core
        from gateway import singleton_get
        
        health = {
            'interface': 'INITIALIZATION',
            'timestamp': time.time(),
            'checks': {},
            'compliance': {},
            'status': 'healthy'
        }
        
        # Check 1: SINGLETON manager registered
        manager = singleton_get('initialization_manager')
        health['checks']['singleton_registered'] = {
            'status': 'pass' if manager is not None else 'fail',
            'value': manager is not None,
            'requirement': 'INITIALIZATION manager must be registered (LESS-18)'
        }
        
        # Check 2: Rate limiting enabled
        if hasattr(initialization_core, 'InitializationCore'):
            core_instance = initialization_core.InitializationCore()
            has_rate_limiter = hasattr(core_instance, '_rate_limiter')
            health['checks']['rate_limiting'] = {
                'status': 'pass' if has_rate_limiter else 'fail',
                'value': has_rate_limiter,
                'rate': '1000 ops/sec' if has_rate_limiter else 'N/A',
                'requirement': 'Rate limiting required for DoS protection (LESS-21)'
            }
        else:
            health['checks']['rate_limiting'] = {
                'status': 'fail',
                'value': False,
                'requirement': 'InitializationCore class not found'
            }
        
        # Check 3: NO threading locks (CRITICAL - AP-08, DEC-04)
        source_file = initialization_core.__file__
        with open(source_file, 'r') as f:
            source_code = f.read()
        
        has_lock_import = 'from threading import Lock' in source_code or 'import threading' in source_code
        has_lock_usage = 'Lock()' in source_code or 'self._lock' in source_code
        has_locks = has_lock_import or has_lock_usage
        
        health['checks']['no_threading_locks'] = {
            'status': 'fail' if has_locks else 'pass',
            'value': not has_locks,
            'lock_import': has_lock_import,
            'lock_usage': has_lock_usage,
            'requirement': 'NO threading locks allowed (AP-08, DEC-04)'
        }
        
        if has_locks:
            health['status'] = 'critical'
        
        # Check 4: Reset operation available
        has_reset = hasattr(initialization_core.InitializationCore, 'reset')
        health['checks']['reset_available'] = {
            'status': 'pass' if has_reset else 'fail',
            'value': has_reset,
            'requirement': 'Reset operation required for lifecycle management'
        }
        
        # Compliance summary
        health['compliance']['ap_08'] = not has_locks
        health['compliance']['dec_04'] = not has_locks
        health['compliance']['less_17'] = not has_locks
        health['compliance']['less_18'] = manager is not None
        health['compliance']['less_21'] = has_rate_limiter if hasattr(initialization_core, 'InitializationCore') else False
        
        # Overall status
        all_checks_pass = all(
            check['status'] == 'pass' 
            for check in health['checks'].values()
        )
        if not all_checks_pass and health['status'] != 'critical':
            health['status'] = 'degraded'
        
        return health
        
    except Exception as e:
        return {
            'interface': 'INITIALIZATION',
            'status': 'error',
            'error': str(e),
            'timestamp': time.time()
        }


def check_utility_health(**kwargs) -> Dict[str, Any]:
    """Check UTILITY interface health (AP-08, DEC-04, LESS-17, LESS-18, LESS-21)."""
    try:
        import utility_core
        from gateway import singleton_get
        
        health = {
            'interface': 'UTILITY',
            'timestamp': time.time(),
            'checks': {},
            'compliance': {},
            'status': 'healthy'
        }
        
        # Check 1: SINGLETON manager registered
        manager = singleton_get('utility_manager')
        health['checks']['singleton_registered'] = {
            'status': 'pass' if manager is not None else 'fail',
            'value': manager is not None,
            'requirement': 'UTILITY manager must be registered (LESS-18)'
        }
        
        # Check 2: Rate limiting enabled
        if hasattr(utility_core, 'SharedUtilityCore'):
            core_instance = utility_core.SharedUtilityCore()
            has_rate_limiter = hasattr(core_instance, '_rate_limiter')
            health['checks']['rate_limiting'] = {
                'status': 'pass' if has_rate_limiter else 'fail',
                'value': has_rate_limiter,
                'rate': '1000 ops/sec' if has_rate_limiter else 'N/A',
                'requirement': 'Rate limiting required for DoS protection (LESS-21)'
            }
        else:
            health['checks']['rate_limiting'] = {
                'status': 'fail',
                'value': False,
                'requirement': 'SharedUtilityCore class not found'
            }
        
        # Check 3: NO threading locks (CRITICAL - AP-08, DEC-04)
        source_file = utility_core.__file__
        with open(source_file, 'r') as f:
            source_code = f.read()
        
        has_lock_import = 'import threading' in source_code
        has_lock_usage = 'Lock()' in source_code or 'self._lock' in source_code
        has_locks = has_lock_import or has_lock_usage
        
        health['checks']['no_threading_locks'] = {
            'status': 'fail' if has_locks else 'pass',
            'value': not has_locks,
            'lock_import': has_lock_import,
            'lock_usage': has_lock_usage,
            'requirement': 'NO threading locks allowed (AP-08, DEC-04)'
        }
        
        if has_locks:
            health['status'] = 'critical'
        
        # Check 4: Reset operation available
        has_reset = hasattr(utility_core.SharedUtilityCore, 'reset')
        health['checks']['reset_available'] = {
            'status': 'pass' if has_reset else 'fail',
            'value': has_reset,
            'requirement': 'Reset operation required for lifecycle management'
        }
        
        # Compliance summary
        health['compliance']['ap_08'] = not has_locks
        health['compliance']['dec_04'] = not has_locks
        health['compliance']['less_17'] = not has_locks
        health['compliance']['less_18'] = manager is not None
        health['compliance']['less_21'] = has_rate_limiter if hasattr(utility_core, 'SharedUtilityCore') else False
        
        # Overall status
        all_checks_pass = all(
            check['status'] == 'pass' 
            for check in health['checks'].values()
        )
        if not all_checks_pass and health['status'] != 'critical':
            health['status'] = 'degraded'
        
        return health
        
    except Exception as e:
        return {
            'interface': 'UTILITY',
            'status': 'error',
            'error': str(e),
            'timestamp': time.time()
        }


def check_singleton_health(**kwargs) -> Dict[str, Any]:
    """Check SINGLETON interface health (AP-08, DEC-04, LESS-17, LESS-18, LESS-21)."""
    try:
        import singleton_core
        from gateway import singleton_get
        
        health = {
            'interface': 'SINGLETON',
            'timestamp': time.time(),
            'checks': {},
            'compliance': {},
            'status': 'healthy'
        }
        
        # Check 1: SINGLETON manager registered
        manager = singleton_get('singleton_manager')
        health['checks']['singleton_registered'] = {
            'status': 'pass' if manager is not None else 'fail',
            'value': manager is not None,
            'requirement': 'SINGLETON manager must be registered (LESS-18)'
        }
        
        # Check 2: Rate limiting enabled
        if hasattr(singleton_core, 'SingletonCore'):
            core_instance = singleton_core.SingletonCore()
            has_rate_limiter = hasattr(core_instance, '_rate_limiter')
            health['checks']['rate_limiting'] = {
                'status': 'pass' if has_rate_limiter else 'fail',
                'value': has_rate_limiter,
                'rate': '1000 ops/sec' if has_rate_limiter else 'N/A',
                'requirement': 'Rate limiting required for DoS protection (LESS-21)'
            }
        else:
            health['checks']['rate_limiting'] = {
                'status': 'fail',
                'value': False,
                'requirement': 'SingletonCore class not found'
            }
        
        # Check 3: NO threading locks (CRITICAL - AP-08, DEC-04)
        source_file = singleton_core.__file__
        with open(source_file, 'r') as f:
            source_code = f.read()
        
        has_lock_import = 'from threading import Lock' in source_code or 'import threading' in source_code
        has_lock_usage = 'Lock()' in source_code or 'self._lock' in source_code
        has_locks = has_lock_import or has_lock_usage
        
        health['checks']['no_threading_locks'] = {
            'status': 'fail' if has_locks else 'pass',
            'value': not has_locks,
            'lock_import': has_lock_import,
            'lock_usage': has_lock_usage,
            'requirement': 'NO threading locks allowed (AP-08, DEC-04)'
        }
        
        if has_locks:
            health['status'] = 'critical'
        
        # Check 4: Reset operation available
        has_reset = hasattr(singleton_core.SingletonCore, 'reset')
        health['checks']['reset_available'] = {
            'status': 'pass' if has_reset else 'fail',
            'value': has_reset,
            'requirement': 'Reset operation required for lifecycle management'
        }
        
        # Compliance summary
        health['compliance']['ap_08'] = not has_locks
        health['compliance']['dec_04'] = not has_locks
        health['compliance']['less_17'] = not has_locks
        health['compliance']['less_18'] = manager is not None
        health['compliance']['less_21'] = has_rate_limiter if hasattr(singleton_core, 'SingletonCore') else False
        
        # Overall status
        all_checks_pass = all(
            check['status'] == 'pass' 
            for check in health['checks'].values()
        )
        if not all_checks_pass and health['status'] != 'critical':
            health['status'] = 'degraded'
        
        return health
        
    except Exception as e:
        return {
            'interface': 'SINGLETON',
            'status': 'error',
            'error': str(e),
            'timestamp': time.time()
        }


def check_system_health(**kwargs) -> Dict[str, Any]:
    """Comprehensive system-wide health check for all 12 interfaces."""
    try:
        system_health = {
            'timestamp': time.time(),
            'interfaces': {},
            'overall_compliance': {},
            'critical_issues': [],
            'warnings': [],
            'recommendations': [],
            'status': 'healthy'
        }
        
        # Check all 12 interfaces (using placeholders for now)
        interfaces_to_check = [
            ('METRICS', _check_metrics_health),
            ('CACHE', _check_cache_health),
            ('LOGGING', _check_logging_health),
            ('SECURITY', _check_security_health),
            ('CONFIG', _check_config_health),
            ('HTTP_CLIENT', _check_http_client_health),
            ('WEBSOCKET', _check_websocket_health),
            ('CIRCUIT_BREAKER', _check_circuit_breaker_health),
            ('SINGLETON', check_singleton_health),
            ('INITIALIZATION', check_initialization_health),
            ('UTILITY', check_utility_health),
        ]
        
        for interface_name, check_func in interfaces_to_check:
            try:
                result = check_func()
                system_health['interfaces'][interface_name] = result
                
                # Check for critical issues
                if result.get('status') == 'critical':
                    system_health['critical_issues'].append(
                        f"{interface_name}: {result.get('checks', {})}"
                    )
                    system_health['status'] = 'critical'
                elif result.get('status') == 'degraded':
                    system_health['warnings'].append(
                        f"{interface_name}: Degraded performance"
                    )
                    if system_health['status'] == 'healthy':
                        system_health['status'] = 'degraded'
                
            except Exception as e:
                system_health['interfaces'][interface_name] = {
                    'status': 'error',
                    'error': str(e)
                }
                system_health['warnings'].append(f"{interface_name}: Health check failed")
        
        # Overall compliance summary (preserved logic)
        all_interfaces = system_health['interfaces']
        total_interfaces = len(all_interfaces)
        
        ap_08_compliant = sum(
            1 for i in all_interfaces.values() 
            if i.get('compliance', {}).get('ap_08', False)
        )
        dec_04_compliant = sum(
            1 for i in all_interfaces.values() 
            if i.get('compliance', {}).get('dec_04', False)
        )
        less_17_compliant = sum(
            1 for i in all_interfaces.values() 
            if i.get('compliance', {}).get('less_17', False)
        )
        less_18_compliant = sum(
            1 for i in all_interfaces.values() 
            if i.get('compliance', {}).get('less_18', False)
        )
        less_21_compliant = sum(
            1 for i in all_interfaces.values() 
            if i.get('compliance', {}).get('less_21', False)
        )
        
        system_health['overall_compliance'] = {
            'ap_08_no_threading_locks': {
                'compliant': ap_08_compliant,
                'total': total_interfaces,
                'percentage': (ap_08_compliant / total_interfaces * 100) if total_interfaces > 0 else 0
            },
            'dec_04_lambda_single_threaded': {
                'compliant': dec_04_compliant,
                'total': total_interfaces,
                'percentage': (dec_04_compliant / total_interfaces * 100) if total_interfaces > 0 else 0
            },
            'less_17_threading_unnecessary': {
                'compliant': less_17_compliant,
                'total': total_interfaces,
                'percentage': (less_17_compliant / total_interfaces * 100) if total_interfaces > 0 else 0
            },
            'less_18_singleton_pattern': {
                'compliant': less_18_compliant,
                'total': total_interfaces,
                'percentage': (less_18_compliant / total_interfaces * 100) if total_interfaces > 0 else 0
            },
            'less_21_rate_limiting': {
                'compliant': less_21_compliant,
                'total': total_interfaces,
                'percentage': (less_21_compliant / total_interfaces * 100) if total_interfaces > 0 else 0
            }
        }
        
        # Recommendations (preserved logic)
        if ap_08_compliant < total_interfaces:
            system_health['recommendations'].append(
                f"Remove threading locks from {total_interfaces - ap_08_compliant} interfaces"
            )
        
        if less_18_compliant < total_interfaces:
            system_health['recommendations'].append(
                f"Add SINGLETON pattern to {total_interfaces - less_18_compliant} interfaces"
            )
        
        if less_21_compliant < total_interfaces:
            system_health['recommendations'].append(
                f"Add rate limiting to {total_interfaces - less_21_compliant} interfaces"
            )
        
        # Overall status determination (preserved logic)
        if not system_health['critical_issues']:
            if ap_08_compliant == total_interfaces and dec_04_compliant == total_interfaces:
                if less_18_compliant == total_interfaces and less_21_compliant == total_interfaces:
                    system_health['status'] = 'healthy'
                    system_health['recommendations'].append(
                        "✅ All interfaces fully optimized and compliant!"
                    )
                else:
                    system_health['status'] = 'degraded'
            else:
                system_health['status'] = 'critical'
        
        return system_health
        
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'timestamp': time.time()
        }


# Placeholder functions (preserved from debug_health.py)
def _check_metrics_health(**kwargs):
    return {'status': 'healthy', 'compliance': {'ap_08': True, 'dec_04': True, 'less_17': True, 'less_18': True, 'less_21': True}}

def _check_cache_health(**kwargs):
    return {'status': 'healthy', 'compliance': {'ap_08': True, 'dec_04': True, 'less_17': True, 'less_18': True, 'less_21': True}}

def _check_logging_health(**kwargs):
    return {'status': 'healthy', 'compliance': {'ap_08': True, 'dec_04': True, 'less_17': True, 'less_18': True, 'less_21': True}}

def _check_security_health(**kwargs):
    return {'status': 'healthy', 'compliance': {'ap_08': True, 'dec_04': True, 'less_17': True, 'less_18': True, 'less_21': True}}

def _check_config_health(**kwargs):
    return {'status': 'healthy', 'compliance': {'ap_08': True, 'dec_04': True, 'less_17': True, 'less_18': True, 'less_21': True}}

def _check_http_client_health(**kwargs):
    return {'status': 'healthy', 'compliance': {'ap_08': True, 'dec_04': True, 'less_17': True, 'less_18': True, 'less_21': True}}

def _check_websocket_health(**kwargs):
    return {'status': 'healthy', 'compliance': {'ap_08': True, 'dec_04': True, 'less_17': True, 'less_18': True, 'less_21': True}}

def _check_circuit_breaker_health(**kwargs):
    return {'status': 'healthy', 'compliance': {'ap_08': True, 'dec_04': True, 'less_17': True, 'less_18': True, 'less_21': True}}


__all__ = [
    'check_component_health',
    'check_gateway_health',
    'generate_health_report',
    'check_initialization_health',
    'check_utility_health',
    'check_singleton_health',
    'check_system_health'
]
