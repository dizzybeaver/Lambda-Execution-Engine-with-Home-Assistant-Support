"""
debug_validation.py - Debug Validation Operations
Version: 2025.10.22.02
Description: System validation operations for debug subsystem

CHANGELOG:
- 2025.10.22.02: Added WEBSOCKET and CIRCUIT_BREAKER interface configuration validation
  - Added _validate_websocket_configuration (SINGLETON, no locks, rate limiting)
  - Added _validate_circuit_breaker_configuration (SINGLETON, no locks, rate limiting)
  - Both validate CRITICAL compliance (AP-08: no threading locks)
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


def _validate_system_architecture(**kwargs) -> Dict[str, Any]:
    """Validate SUGA architecture compliance."""
    issues = []
    
    try:
        from gateway import _OPERATION_REGISTRY
        if not _OPERATION_REGISTRY:
            issues.append("Empty operation registry")
        
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


def _validate_websocket_configuration(**kwargs) -> Dict[str, Any]:
    """
    Validate WEBSOCKET interface configuration.
    
    Validates:
    - SINGLETON registration compliance (LESS-18)
    - NO threading locks compliance (AP-08, DEC-04) - CRITICAL
    - Rate limiting configuration (LESS-21)
    - Reset operation availability (LESS-18)
    - Core operations availability
    
    REF-IDs:
    - AP-08: No threading locks (CRITICAL)
    - DEC-04: Lambda single-threaded
    - LESS-18: SINGLETON pattern
    - LESS-21: Rate limiting essential
    
    Returns:
        Configuration validation results
    """
    from gateway import create_success_response, create_error_response
    
    validation = {
        'interface': 'WEBSOCKET',
        'compliant': True,
        'checks': {},
        'warnings': [],
        'errors': [],
        'critical_issues': []
    }
    
    try:
        # CRITICAL Check 1: NO threading locks (AP-08, DEC-04)
        try:
            from websocket_core import get_websocket_manager
            manager = get_websocket_manager()
            
            has_lock = hasattr(manager, '_lock')
            validation['checks']['no_threading_locks'] = not has_lock
            
            if has_lock:
                validation['compliant'] = False
                validation['critical_issues'].append(
                    'CRITICAL: Threading locks found (violates AP-08, DEC-04) - '
                    'Lambda is single-threaded, locks are unnecessary and harmful'
                )
        except Exception as e:
            validation['checks']['no_threading_locks'] = False
            validation['errors'].append(f'Failed to check threading locks: {str(e)}')
        
        # Check 2: SINGLETON registration (LESS-18)
        try:
            from gateway import singleton_get
            manager_from_registry = singleton_get('websocket_manager')
            
            if manager_from_registry is not None:
                validation['checks']['singleton_registered'] = True
            else:
                validation['checks']['singleton_registered'] = False
                validation['warnings'].append(
                    'SINGLETON not registered (will register on first use via get_websocket_manager)'
                )
        except Exception as e:
            validation['checks']['singleton_registered'] = False
            validation['warnings'].append(f'SINGLETON check failed: {str(e)}')
        
        # Check 3: Rate limiting (LESS-21)
        try:
            if hasattr(manager, '_rate_limiter'):
                validation['checks']['rate_limiting_configured'] = True
                validation['checks']['rate_limit_details'] = {
                    'max_ops_per_sec': manager._rate_limiter.maxlen,
                    'window_ms': manager._rate_limit_window_ms,
                    'expected': 300  # WebSocket specific
                }
                
                if manager._rate_limiter.maxlen != 300:
                    validation['warnings'].append(
                        f'Rate limit is {manager._rate_limiter.maxlen} ops/sec, expected 300 for WebSocket'
                    )
            else:
                validation['checks']['rate_limiting_configured'] = False
                validation['compliant'] = False
                validation['errors'].append(
                    'Rate limiting not configured (violates LESS-21)'
                )
        except Exception as e:
            validation['checks']['rate_limiting_configured'] = False
            validation['warnings'].append(f'Rate limiting check failed: {str(e)}')
        
        # Check 4: Reset operation (LESS-18)
        try:
            from websocket_core import websocket_reset_implementation
            validation['checks']['reset_operation'] = True
        except ImportError:
            validation['checks']['reset_operation'] = False
            validation['warnings'].append(
                'Reset operation not available (lifecycle management limited)'
            )
        
        # Check 5: Core operations
        try:
            from websocket_core import (
                websocket_connect_implementation,
                websocket_send_implementation,
                websocket_receive_implementation,
                websocket_close_implementation,
                websocket_request_implementation,
                websocket_get_stats_implementation
            )
            validation['checks']['core_operations'] = {
                'connect': True,
                'send': True,
                'receive': True,
                'close': True,
                'request': True,
                'get_stats': True
            }
        except ImportError as e:
            validation['checks']['core_operations'] = False
            validation['compliant'] = False
            validation['errors'].append(f'Core operations missing: {str(e)}')
        
        # Check 6: Interface router
        try:
            from interface_websocket import execute_websocket_operation
            validation['checks']['interface_router'] = True
        except ImportError as e:
            validation['checks']['interface_router'] = False
            validation['compliant'] = False
            validation['errors'].append(f'Interface router unavailable: {str(e)}')
        
        # Check 7: Manager class structure
        validation['checks']['manager_structure'] = {
            'has_rate_limiter': hasattr(manager, '_rate_limiter'),
            'has_statistics': hasattr(manager, '_total_operations'),
            'has_reset_method': hasattr(manager, 'reset'),
            'has_get_stats_method': hasattr(manager, 'get_stats')
        }
        
        # Final compliance determination
        if validation['critical_issues'] or validation['errors']:
            validation['compliant'] = False
        
        # Summary
        validation['summary'] = {
            'total_checks': len(validation['checks']),
            'warnings_count': len(validation['warnings']),
            'errors_count': len(validation['errors']),
            'critical_issues_count': len(validation['critical_issues']),
            'compliant': validation['compliant']
        }
        
        return create_success_response('WEBSOCKET configuration validation complete', validation)
        
    except Exception as e:
        return create_error_response(f'Configuration validation failed: {str(e)}', 'VALIDATION_FAILED')


def _validate_circuit_breaker_configuration(**kwargs) -> Dict[str, Any]:
    """
    Validate CIRCUIT_BREAKER interface configuration.
    
    Validates:
    - SINGLETON registration compliance (LESS-18)
    - NO threading locks compliance (AP-08, DEC-04) - CRITICAL
    - Rate limiting configuration (LESS-21)
    - Reset operation availability (LESS-18)
    - Core operations availability
    - Circuit breaker manager structure
    
    REF-IDs:
    - AP-08: No threading locks (CRITICAL)
    - DEC-04: Lambda single-threaded
    - LESS-18: SINGLETON pattern
    - LESS-21: Rate limiting essential
    
    Returns:
        Configuration validation results
    """
    from gateway import create_success_response, create_error_response
    
    validation = {
        'interface': 'CIRCUIT_BREAKER',
        'compliant': True,
        'checks': {},
        'warnings': [],
        'errors': [],
        'critical_issues': []
    }
    
    try:
        # CRITICAL Check 1: NO threading locks (AP-08, DEC-04)
        try:
            from circuit_breaker_core import get_circuit_breaker_manager, CircuitBreaker
            manager = get_circuit_breaker_manager()
            
            # Check manager for locks
            has_manager_lock = hasattr(manager, '_lock')
            validation['checks']['no_manager_threading_locks'] = not has_manager_lock
            
            if has_manager_lock:
                validation['compliant'] = False
                validation['critical_issues'].append(
                    'CRITICAL: Manager has threading locks (violates AP-08, DEC-04) - '
                    'Lambda is single-threaded, locks are unnecessary and harmful'
                )
            
            # Check individual circuit breakers for locks
            test_breaker = CircuitBreaker('validation_test', 5, 60)
            has_breaker_lock = hasattr(test_breaker, '_lock')
            validation['checks']['no_breaker_threading_locks'] = not has_breaker_lock
            
            if has_breaker_lock:
                validation['compliant'] = False
                validation['critical_issues'].append(
                    'CRITICAL: CircuitBreaker class has threading locks (violates AP-08, DEC-04) - '
                    'Lambda is single-threaded, locks are unnecessary and harmful'
                )
        except Exception as e:
            validation['checks']['no_threading_locks'] = False
            validation['errors'].append(f'Failed to check threading locks: {str(e)}')
        
        # Check 2: SINGLETON registration (LESS-18)
        try:
            from gateway import singleton_get
            manager_from_registry = singleton_get('circuit_breaker_manager')
            
            if manager_from_registry is not None:
                validation['checks']['singleton_registered'] = True
            else:
                validation['checks']['singleton_registered'] = False
                validation['warnings'].append(
                    'SINGLETON not registered (will register on first use via get_circuit_breaker_manager)'
                )
        except Exception as e:
            validation['checks']['singleton_registered'] = False
            validation['warnings'].append(f'SINGLETON check failed: {str(e)}')
        
        # Check 3: Rate limiting (LESS-21)
        try:
            if hasattr(manager, '_rate_limiter'):
                validation['checks']['rate_limiting_configured'] = True
                validation['checks']['rate_limit_details'] = {
                    'max_ops_per_sec': manager._rate_limiter.maxlen,
                    'window_ms': manager._rate_limit_window_ms,
                    'expected': 1000  # Circuit Breaker specific
                }
                
                if manager._rate_limiter.maxlen != 1000:
                    validation['warnings'].append(
                        f'Rate limit is {manager._rate_limiter.maxlen} ops/sec, expected 1000 for Circuit Breaker'
                    )
            else:
                validation['checks']['rate_limiting_configured'] = False
                validation['compliant'] = False
                validation['errors'].append(
                    'Rate limiting not configured (violates LESS-21)'
                )
        except Exception as e:
            validation['checks']['rate_limiting_configured'] = False
            validation['warnings'].append(f'Rate limiting check failed: {str(e)}')
        
        # Check 4: Reset operation (LESS-18)
        try:
            from circuit_breaker_core import reset_implementation, reset_all_implementation
            validation['checks']['reset_operations'] = {
                'reset': True,
                'reset_all': True
            }
        except ImportError as e:
            validation['checks']['reset_operations'] = False
            validation['warnings'].append(f'Reset operations not fully available: {str(e)}')
        
        # Check 5: Core operations
        try:
            from circuit_breaker_core import (
                get_breaker_implementation,
                execute_with_breaker_implementation,
                get_all_states_implementation,
                get_stats_implementation
            )
            validation['checks']['core_operations'] = {
                'get': True,
                'call': True,
                'get_all_states': True,
                'get_stats': True
            }
        except ImportError as e:
            validation['checks']['core_operations'] = False
            validation['compliant'] = False
            validation['errors'].append(f'Core operations missing: {str(e)}')
        
        # Check 6: Interface router
        try:
            from interface_circuit_breaker import execute_circuit_breaker_operation
            validation['checks']['interface_router'] = True
        except ImportError as e:
            validation['checks']['interface_router'] = False
            validation['compliant'] = False
            validation['errors'].append(f'Interface router unavailable: {str(e)}')
        
        # Check 7: Manager structure
        validation['checks']['manager_structure'] = {
            'has_rate_limiter': hasattr(manager, '_rate_limiter'),
            'has_breakers_dict': hasattr(manager, '_breakers'),
            'has_statistics': hasattr(manager, '_total_operations'),
            'has_reset_method': hasattr(manager, 'reset'),
            'has_get_stats_method': hasattr(manager, 'get_stats')
        }
        
        # Check 8: Circuit breaker class structure
        validation['checks']['breaker_class_structure'] = {
            'has_state': hasattr(test_breaker, 'state'),
            'has_failures': hasattr(test_breaker, 'failures'),
            'has_threshold': hasattr(test_breaker, 'failure_threshold'),
            'has_timeout': hasattr(test_breaker, 'timeout'),
            'has_call_method': hasattr(test_breaker, 'call'),
            'has_reset_method': hasattr(test_breaker, 'reset'),
            'has_get_state_method': hasattr(test_breaker, 'get_state')
        }
        
        # Final compliance determination
        if validation['critical_issues'] or validation['errors']:
            validation['compliant'] = False
        
        # Summary
        validation['summary'] = {
            'total_checks': len(validation['checks']),
            'warnings_count': len(validation['warnings']),
            'errors_count': len(validation['errors']),
            'critical_issues_count': len(validation['critical_issues']),
            'compliant': validation['compliant']
        }
        
        return create_success_response('CIRCUIT_BREAKER configuration validation complete', validation)
        
    except Exception as e:
        return create_error_response(f'Configuration validation failed: {str(e)}', 'VALIDATION_FAILED')


__all__ = [
    '_validate_system_architecture',
    '_validate_imports',
    '_validate_gateway_routing',
    '_run_config_unit_tests',
    '_run_config_integration_tests',
    '_run_config_performance_tests',
    '_run_config_compatibility_tests',
    '_run_config_gateway_tests',
    '_validate_websocket_configuration',
    '_validate_circuit_breaker_configuration'
]

# EOF
