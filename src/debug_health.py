"""
debug_health.py - Debug Health Check Operations
Version: 2025.10.22.02
Description: Health check operations for debug subsystem

CHANGELOG:
- 2025.10.22.02: Added WEBSOCKET and CIRCUIT_BREAKER interface health checks
  - Added _check_websocket_health (SINGLETON, rate limiting, no locks)
  - Added _check_circuit_breaker_health (SINGLETON, rate limiting, no locks)
  - Both validate AP-08 compliance (CRITICAL: no threading locks)
  - Both verify LESS-21 compliance (rate limiting essential)

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


def _check_websocket_health(**kwargs) -> Dict[str, Any]:
    """
    Check WEBSOCKET interface health.
    
    Verifies:
    - SINGLETON registration (LESS-18)
    - Rate limiting configuration (LESS-21)
    - NO threading locks compliance (AP-08, DEC-04)
    - Reset operation availability
    - Statistics tracking
    
    REF-IDs:
    - AP-08: No threading locks
    - DEC-04: Lambda single-threaded
    - LESS-18: SINGLETON pattern
    - LESS-21: Rate limiting essential
    
    Returns:
        Health status with detailed diagnostics
    """
    from gateway import create_success_response, create_error_response
    
    health = {
        'interface': 'WEBSOCKET',
        'healthy': True,
        'checks': {},
        'warnings': [],
        'errors': []
    }
    
    try:
        # Check 1: SINGLETON registration
        try:
            from gateway import singleton_get
            manager = singleton_get('websocket_manager')
            if manager is not None:
                health['checks']['singleton_registered'] = True
            else:
                health['checks']['singleton_registered'] = False
                health['warnings'].append('SINGLETON not registered yet (will register on first use)')
        except Exception as e:
            health['checks']['singleton_registered'] = False
            health['warnings'].append(f'SINGLETON check failed: {str(e)}')
        
        # Check 2: Get manager and verify no threading locks
        try:
            from websocket_core import get_websocket_manager
            manager = get_websocket_manager()
            
            # Verify no threading locks (AP-08, DEC-04)
            has_lock = hasattr(manager, '_lock')
            health['checks']['no_threading_locks'] = not has_lock
            
            if has_lock:
                health['healthy'] = False
                health['errors'].append('CRITICAL: Threading locks found (violates AP-08, DEC-04)')
            
        except Exception as e:
            health['checks']['manager_accessible'] = False
            health['healthy'] = False
            health['errors'].append(f'Failed to get manager: {str(e)}')
        
        # Check 3: Rate limiting configuration
        try:
            if hasattr(manager, '_rate_limiter'):
                health['checks']['rate_limiting_enabled'] = True
                health['checks']['rate_limit_max'] = manager._rate_limiter.maxlen
                health['checks']['rate_limit_window_ms'] = manager._rate_limit_window_ms
                
                # Verify 300 ops/sec (WebSocket specific)
                if manager._rate_limiter.maxlen != 300:
                    health['warnings'].append(f'Rate limit is {manager._rate_limiter.maxlen} ops/sec, expected 300')
            else:
                health['checks']['rate_limiting_enabled'] = False
                health['healthy'] = False
                health['errors'].append('CRITICAL: Rate limiting not configured (violates LESS-21)')
        except Exception as e:
            health['checks']['rate_limiting_enabled'] = False
            health['warnings'].append(f'Rate limiting check failed: {str(e)}')
        
        # Check 4: Reset operation
        try:
            from websocket_core import websocket_reset_implementation
            health['checks']['reset_available'] = True
        except ImportError:
            health['checks']['reset_available'] = False
            health['warnings'].append('Reset operation not available')
        
        # Check 5: Statistics
        try:
            stats_result = manager.get_stats()
            if stats_result.get('success'):
                stats = stats_result.get('data', {})
                health['checks']['statistics_tracking'] = True
                health['statistics'] = {
                    'total_operations': stats.get('total_operations', 0),
                    'connections_count': stats.get('connections_count', 0),
                    'messages_sent': stats.get('messages_sent_count', 0),
                    'messages_received': stats.get('messages_received_count', 0),
                    'errors_count': stats.get('errors_count', 0),
                    'rate_limited_count': stats.get('rate_limited_count', 0)
                }
            else:
                health['checks']['statistics_tracking'] = False
                health['warnings'].append('Statistics not available')
        except Exception as e:
            health['checks']['statistics_tracking'] = False
            health['warnings'].append(f'Statistics check failed: {str(e)}')
        
        # Check 6: Core operations availability
        try:
            from websocket_core import (
                websocket_connect_implementation,
                websocket_send_implementation,
                websocket_receive_implementation,
                websocket_close_implementation,
                websocket_request_implementation
            )
            health['checks']['core_operations'] = True
        except ImportError as e:
            health['checks']['core_operations'] = False
            health['healthy'] = False
            health['errors'].append(f'Core operations unavailable: {str(e)}')
        
        # Final health determination
        if health['errors']:
            health['healthy'] = False
        
        return create_success_response('WEBSOCKET health check complete', health)
        
    except Exception as e:
        return create_error_response(f'Health check failed: {str(e)}', 'HEALTH_CHECK_FAILED')


def _check_circuit_breaker_health(**kwargs) -> Dict[str, Any]:
    """
    Check CIRCUIT_BREAKER interface health.
    
    Verifies:
    - SINGLETON registration (LESS-18)
    - Rate limiting configuration (LESS-21)
    - NO threading locks compliance (AP-08, DEC-04) - CRITICAL
    - Reset operation availability
    - Statistics tracking
    - Circuit breakers operational
    
    REF-IDs:
    - AP-08: No threading locks (CRITICAL)
    - DEC-04: Lambda single-threaded
    - LESS-18: SINGLETON pattern
    - LESS-21: Rate limiting essential
    
    Returns:
        Health status with detailed diagnostics
    """
    from gateway import create_success_response, create_error_response
    
    health = {
        'interface': 'CIRCUIT_BREAKER',
        'healthy': True,
        'checks': {},
        'warnings': [],
        'errors': [],
        'critical_issues': []
    }
    
    try:
        # Check 1: SINGLETON registration
        try:
            from gateway import singleton_get
            manager = singleton_get('circuit_breaker_manager')
            if manager is not None:
                health['checks']['singleton_registered'] = True
            else:
                health['checks']['singleton_registered'] = False
                health['warnings'].append('SINGLETON not registered yet (will register on first use)')
        except Exception as e:
            health['checks']['singleton_registered'] = False
            health['warnings'].append(f'SINGLETON check failed: {str(e)}')
        
        # Check 2: Get manager and verify no threading locks (CRITICAL)
        try:
            from circuit_breaker_core import get_circuit_breaker_manager
            manager = get_circuit_breaker_manager()
            
            # CRITICAL: Verify no threading locks (AP-08, DEC-04)
            has_lock = hasattr(manager, '_lock')
            health['checks']['no_threading_locks'] = not has_lock
            
            if has_lock:
                health['healthy'] = False
                health['critical_issues'].append(
                    'CRITICAL: Threading locks found (violates AP-08, DEC-04) - '
                    'Lambda is single-threaded, locks are unnecessary and harmful'
                )
        except Exception as e:
            health['checks']['manager_accessible'] = False
            health['healthy'] = False
            health['errors'].append(f'Failed to get manager: {str(e)}')
        
        # Check 3: Rate limiting configuration
        try:
            if hasattr(manager, '_rate_limiter'):
                health['checks']['rate_limiting_enabled'] = True
                health['checks']['rate_limit_max'] = manager._rate_limiter.maxlen
                health['checks']['rate_limit_window_ms'] = manager._rate_limit_window_ms
                
                # Verify 1000 ops/sec (Circuit Breaker specific)
                if manager._rate_limiter.maxlen != 1000:
                    health['warnings'].append(f'Rate limit is {manager._rate_limiter.maxlen} ops/sec, expected 1000')
            else:
                health['checks']['rate_limiting_enabled'] = False
                health['healthy'] = False
                health['errors'].append('CRITICAL: Rate limiting not configured (violates LESS-21)')
        except Exception as e:
            health['checks']['rate_limiting_enabled'] = False
            health['warnings'].append(f'Rate limiting check failed: {str(e)}')
        
        # Check 4: Reset operation
        try:
            from circuit_breaker_core import reset_implementation
            health['checks']['reset_available'] = True
        except ImportError:
            health['checks']['reset_available'] = False
            health['warnings'].append('Reset operation not available')
        
        # Check 5: Statistics
        try:
            stats_result = manager.get_stats()
            if stats_result.get('success'):
                stats = stats_result.get('data', {})
                health['checks']['statistics_tracking'] = True
                health['statistics'] = {
                    'total_operations': stats.get('total_operations', 0),
                    'breakers_count': stats.get('breakers_count', 0),
                    'rate_limited_count': stats.get('rate_limited_count', 0)
                }
            else:
                health['checks']['statistics_tracking'] = False
                health['warnings'].append('Statistics not available')
        except Exception as e:
            health['checks']['statistics_tracking'] = False
            health['warnings'].append(f'Statistics check failed: {str(e)}')
        
        # Check 6: Core operations availability
        try:
            from circuit_breaker_core import (
                get_breaker_implementation,
                execute_with_breaker_implementation,
                get_all_states_implementation,
                reset_all_implementation
            )
            health['checks']['core_operations'] = True
        except ImportError as e:
            health['checks']['core_operations'] = False
            health['healthy'] = False
            health['errors'].append(f'Core operations unavailable: {str(e)}')
        
        # Check 7: Circuit breaker functionality (test with dummy breaker)
        try:
            test_breaker = manager.get('health_check_test', failure_threshold=5, timeout=60)
            if test_breaker:
                health['checks']['circuit_breaker_creation'] = True
                # Clean up test breaker
                if 'health_check_test' in manager._breakers:
                    del manager._breakers['health_check_test']
            else:
                health['checks']['circuit_breaker_creation'] = False
                health['warnings'].append('Circuit breaker creation returned None')
        except Exception as e:
            health['checks']['circuit_breaker_creation'] = False
            health['warnings'].append(f'Circuit breaker creation test failed: {str(e)}')
        
        # Final health determination
        if health['critical_issues'] or health['errors']:
            health['healthy'] = False
        
        return create_success_response('CIRCUIT_BREAKER health check complete', health)
        
    except Exception as e:
        return create_error_response(f'Health check failed: {str(e)}', 'HEALTH_CHECK_FAILED')


__all__ = [
    '_check_component_health',
    '_check_gateway_health',
    '_generate_health_report',
    '_check_websocket_health',
    '_check_circuit_breaker_health'
]

# EOF
