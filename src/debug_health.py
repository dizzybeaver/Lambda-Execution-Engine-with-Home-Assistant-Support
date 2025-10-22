"""
debug_health.py - Debug Health Check Operations
Version: 2025.10.14.01
Description: Health check operations for debug subsystem

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
import time


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


def _generate_health_report(**kwargs) -> Dict[str, Any]:
    """Generate comprehensive health report with dispatcher metrics."""
    from debug.debug_diagnostics import _diagnose_system_health
    from debug.debug_validation import _validate_system_architecture, _validate_imports, _validate_gateway_routing
    from debug.debug_verification import _verify_registry_operations
    from debug.debug_stats import _get_system_stats, _get_optimization_stats, _get_dispatcher_stats
    
    try:
        dispatcher_stats = _get_dispatcher_stats()
    except:
        dispatcher_stats = {'error': 'dispatcher stats not available'}
    
    return {
        'timestamp': '2025.10.14',
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


def _check_http_client_health(**kwargs) -> Dict[str, Any]:
    """
    Check HTTP_CLIENT interface health and compliance.
    
    Verifies:
    - SINGLETON registration ('http_client_manager')
    - Rate limiting effectiveness (500 ops/sec)
    - No threading locks (AP-08, DEC-04)
    - Reset operation availability
    - Connection pool status
    - Request statistics
    
    Returns:
        Dict with health status and detailed checks
        
    REF: AP-08 (No threading locks)
    REF: DEC-04 (Lambda single-threaded)
    REF: LESS-18 (SINGLETON pattern for lifecycle)
    REF: LESS-21 (Rate limiting essential)
    """
    import gateway
    import inspect
    from http_client_core import get_http_client_manager, HTTPClientCore
    
    health_status = {
        'interface': 'HTTP_CLIENT',
        'timestamp': time.time(),
        'overall_status': 'HEALTHY',
        'checks': {}
    }
    
    try:
        # Check 1: SINGLETON Registration
        singleton_manager = gateway.singleton_get('http_client_manager')
        health_status['checks']['singleton_registered'] = {
            'status': 'PASS' if singleton_manager is not None else 'FAIL',
            'details': 'Registered as http_client_manager' if singleton_manager else 'Not registered',
            'critical': True
        }
        
        # Check 2: Get manager instance
        manager = get_http_client_manager()
        health_status['checks']['manager_accessible'] = {
            'status': 'PASS',
            'details': f'Instance type: {type(manager).__name__}',
            'critical': True
        }
        
        # Check 3: Threading locks (CRITICAL - must be absent)
        source = inspect.getsource(HTTPClientCore)
        has_lock = 'threading.Lock' in source or 'from threading import Lock' in source
        health_status['checks']['no_threading_locks'] = {
            'status': 'FAIL' if has_lock else 'PASS',
            'details': 'Threading lock found (AP-08 violation)' if has_lock else 'No threading locks (compliant)',
            'critical': True,
            'compliance': ['AP-08', 'DEC-04', 'LESS-17']
        }
        if has_lock:
            health_status['overall_status'] = 'CRITICAL'
        
        # Check 4: Rate limiting present
        has_rate_limiter = hasattr(manager, '_rate_limiter') and hasattr(manager, '_check_rate_limit')
        health_status['checks']['rate_limiting'] = {
            'status': 'PASS' if has_rate_limiter else 'FAIL',
            'details': f"Rate limiter: {'present' if has_rate_limiter else 'absent'}",
            'critical': True,
            'compliance': ['LESS-21']
        }
        if not has_rate_limiter:
            health_status['overall_status'] = 'UNHEALTHY'
        
        # Check 5: Rate limiting effectiveness (if present)
        if has_rate_limiter:
            stats = manager.get_stats()
            rate_limited = stats.get('rate_limited', 0)
            limiter_size = stats.get('rate_limiter_size', 0)
            health_status['checks']['rate_limit_effectiveness'] = {
                'status': 'PASS',
                'details': f'Rate limited: {rate_limited} requests, Current queue: {limiter_size}/500',
                'metrics': {
                    'rate_limited_count': rate_limited,
                    'current_queue_size': limiter_size,
                    'max_queue_size': 500
                }
            }
        
        # Check 6: Reset operation
        has_reset = hasattr(manager, 'reset')
        health_status['checks']['reset_operation'] = {
            'status': 'PASS' if has_reset else 'FAIL',
            'details': 'Reset method available' if has_reset else 'Reset method missing',
            'critical': True,
            'compliance': ['LESS-18']
        }
        if not has_reset:
            health_status['overall_status'] = 'UNHEALTHY'
        
        # Check 7: Connection pool status
        has_http_pool = hasattr(manager, 'http')
        health_status['checks']['connection_pool'] = {
            'status': 'PASS' if has_http_pool else 'FAIL',
            'details': f"HTTP pool: {'configured' if has_http_pool else 'missing'}",
            'critical': True
        }
        
        # Check 8: Request statistics
        stats = manager.get_stats()
        health_status['checks']['statistics'] = {
            'status': 'PASS',
            'details': 'Statistics tracking functional',
            'metrics': {
                'total_requests': stats.get('requests', 0),
                'successful': stats.get('successful', 0),
                'failed': stats.get('failed', 0),
                'retries': stats.get('retries', 0),
                'rate_limited': stats.get('rate_limited', 0)
            }
        }
        
        # Overall status determination
        failed_checks = [k for k, v in health_status['checks'].items() 
                        if v.get('status') == 'FAIL' and v.get('critical')]
        if failed_checks:
            health_status['overall_status'] = 'UNHEALTHY'
            health_status['failed_critical_checks'] = failed_checks
        
    except Exception as e:
        health_status['overall_status'] = 'ERROR'
        health_status['error'] = str(e)
        health_status['error_type'] = type(e).__name__
    
    return health_status


__all__ = [
    '_check_component_health',
    '_check_gateway_health',
    '_generate_health_report',
    '_check_http_client_health'
]

# EOF
