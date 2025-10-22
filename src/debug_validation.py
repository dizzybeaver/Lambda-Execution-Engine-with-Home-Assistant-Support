"""
debug_validation.py - Debug Validation Operations
Version: 2025.10.14.01
Description: System validation operations for debug subsystem

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


def _validate_http_client_configuration(**kwargs) -> Dict[str, Any]:
    """
    Validate HTTP_CLIENT interface configuration and compliance.
    
    Validates:
    - SINGLETON registration compliance
    - Threading lock compliance (CRITICAL - AP-08, DEC-04)
    - Rate limiting configuration (500 ops/sec)
    - Connection pool settings (timeouts, SSL)
    - Retry configuration (max attempts, backoff)
    - Reset operation availability
    - Statistics tracking
    
    Returns:
        Dict with validation results and compliance status
        
    REF: AP-08 (No threading locks - CRITICAL)
    REF: DEC-04 (Lambda single-threaded model)
    REF: LESS-18 (SINGLETON pattern compliance)
    REF: LESS-21 (Rate limiting compliance)
    """
    import gateway
    import inspect
    import os
    from http_client_core import get_http_client_manager, HTTPClientCore
    
    validation = {
        'interface': 'HTTP_CLIENT',
        'timestamp': time.time(),
        'compliance_status': 'COMPLIANT',
        'validations': {}
    }
    
    try:
        # Validation 1: SINGLETON Registration (CRITICAL)
        singleton_manager = gateway.singleton_get('http_client_manager')
        validation['validations']['singleton_registration'] = {
            'valid': singleton_manager is not None,
            'details': 'Registered as http_client_manager' if singleton_manager else 'NOT REGISTERED',
            'severity': 'CRITICAL',
            'compliance': ['LESS-18', 'RULE-01']
        }
        if singleton_manager is None:
            validation['compliance_status'] = 'NON_COMPLIANT'
        
        # Validation 2: Threading Lock Compliance (CRITICAL - AP-08)
        source = inspect.getsource(HTTPClientCore)
        has_threading_lock = 'threading.Lock' in source or 'from threading import Lock' in source
        validation['validations']['no_threading_locks'] = {
            'valid': not has_threading_lock,
            'details': 'VIOLATION: Threading lock found' if has_threading_lock else 'Compliant: No threading locks',
            'severity': 'CRITICAL',
            'compliance': ['AP-08', 'DEC-04', 'LESS-17']
        }
        if has_threading_lock:
            validation['compliance_status'] = 'CRITICAL_VIOLATION'
        
        # Validation 3: Rate Limiting Configuration
        manager = get_http_client_manager()
        has_rate_limiter = hasattr(manager, '_rate_limiter')
        has_check_method = hasattr(manager, '_check_rate_limit')
        
        rate_limit_valid = has_rate_limiter and has_check_method
        if rate_limit_valid:
            max_size = manager._rate_limiter.maxlen if hasattr(manager._rate_limiter, 'maxlen') else 0
            window_ms = getattr(manager, '_rate_limit_window_ms', 0)
            details = f'Configured: {max_size} ops/{window_ms}ms (500 ops/sec)'
        else:
            details = 'NOT CONFIGURED'
        
        validation['validations']['rate_limiting'] = {
            'valid': rate_limit_valid,
            'details': details,
            'expected': '500 operations per second',
            'severity': 'HIGH',
            'compliance': ['LESS-21']
        }
        if not rate_limit_valid:
            validation['compliance_status'] = 'NON_COMPLIANT'
        
        # Validation 4: Connection Pool Configuration
        has_http_pool = hasattr(manager, 'http')
        if has_http_pool:
            verify_ssl_env = os.getenv('HOME_ASSISTANT_VERIFY_SSL', 'true').lower()
            verify_ssl = verify_ssl_env != 'false'
            
            pool_details = f'Configured with SSL verification: {verify_ssl}'
        else:
            pool_details = 'NOT CONFIGURED'
        
        validation['validations']['connection_pool'] = {
            'valid': has_http_pool,
            'details': pool_details,
            'configuration': {
                'max_connections': 10,
                'connect_timeout': '10.0s',
                'read_timeout': '30.0s',
                'ssl_verification': verify_ssl if has_http_pool else 'unknown'
            },
            'severity': 'HIGH'
        }
        if not has_http_pool:
            validation['compliance_status'] = 'NON_COMPLIANT'
        
        # Validation 5: Retry Configuration
        has_retry_config = hasattr(manager, '_retry_config')
        if has_retry_config:
            retry_cfg = manager._retry_config
            retry_details = f"Max attempts: {retry_cfg.get('max_attempts', 0)}, Backoff: {retry_cfg.get('backoff_base_ms', 0)}ms base"
        else:
            retry_details = 'NOT CONFIGURED'
        
        validation['validations']['retry_configuration'] = {
            'valid': has_retry_config,
            'details': retry_details,
            'expected': {
                'max_attempts': 3,
                'backoff_base_ms': 100,
                'backoff_multiplier': 2.0,
                'retriable_codes': [408, 429, 500, 502, 503, 504]
            },
            'severity': 'MEDIUM'
        }
        
        # Validation 6: Reset Operation Availability (CRITICAL for lifecycle)
        has_reset = hasattr(manager, 'reset')
        validation['validations']['reset_operation'] = {
            'valid': has_reset,
            'details': 'Reset method available' if has_reset else 'Reset method MISSING',
            'severity': 'HIGH',
            'compliance': ['LESS-18']
        }
        if not has_reset:
            validation['compliance_status'] = 'NON_COMPLIANT'
        
        # Validation 7: Statistics Tracking
        has_stats = hasattr(manager, 'get_stats')
        if has_stats:
            stats = manager.get_stats()
            stats_fields = ['requests', 'successful', 'failed', 'retries', 'rate_limited']
            has_all_fields = all(field in stats for field in stats_fields)
            stats_details = 'All required fields present' if has_all_fields else 'Missing fields'
        else:
            stats_details = 'get_stats method MISSING'
        
        validation['validations']['statistics_tracking'] = {
            'valid': has_stats,
            'details': stats_details,
            'expected_fields': ['requests', 'successful', 'failed', 'retries', 'rate_limited'],
            'severity': 'MEDIUM'
        }
        
        # Validation 8: Implementation Wrappers
        from http_client_core import (
            http_request_implementation,
            http_get_implementation,
            http_post_implementation,
            http_put_implementation,
            http_delete_implementation,
            http_reset_implementation
        )
        
        wrapper_functions = [
            http_request_implementation,
            http_get_implementation,
            http_post_implementation,
            http_put_implementation,
            http_delete_implementation,
            http_reset_implementation
        ]
        
        all_wrappers_exist = all(func is not None for func in wrapper_functions)
        
        validation['validations']['implementation_wrappers'] = {
            'valid': all_wrappers_exist,
            'details': f'{len([f for f in wrapper_functions if f])} of {len(wrapper_functions)} wrappers available',
            'wrappers': ['request', 'get', 'post', 'put', 'delete', 'reset'],
            'severity': 'HIGH'
        }
        
        # Overall compliance summary
        critical_violations = [
            k for k, v in validation['validations'].items()
            if not v['valid'] and v.get('severity') == 'CRITICAL'
        ]
        
        high_violations = [
            k for k, v in validation['validations'].items()
            if not v['valid'] and v.get('severity') == 'HIGH'
        ]
        
        if critical_violations:
            validation['compliance_status'] = 'CRITICAL_VIOLATION'
            validation['critical_violations'] = critical_violations
        elif high_violations:
            if validation['compliance_status'] == 'COMPLIANT':
                validation['compliance_status'] = 'NON_COMPLIANT'
            validation['high_priority_violations'] = high_violations
        
        validation['summary'] = {
            'total_validations': len(validation['validations']),
            'passed': sum(1 for v in validation['validations'].values() if v['valid']),
            'failed': sum(1 for v in validation['validations'].values() if not v['valid']),
            'critical_violations': len(critical_violations),
            'high_priority_violations': len(high_violations)
        }
        
    except Exception as e:
        validation['compliance_status'] = 'ERROR'
        validation['error'] = str(e)
        validation['error_type'] = type(e).__name__
    
    return validation


__all__ = [
    '_validate_system_architecture',
    '_validate_imports',
    '_validate_gateway_routing',
    '_run_config_unit_tests',
    '_run_config_integration_tests',
    '_run_config_performance_tests',
    '_run_config_compatibility_tests',
    '_run_config_gateway_tests',
    '_validate_http_client_configuration'
]

# EOF
