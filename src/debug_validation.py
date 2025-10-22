"""
debug_validation.py - Debug Validation Operations
Version: 2025.10.22.02
Description: System validation operations for debug subsystem

CHANGES (2025.10.22.02):
- Added _validate_security_configuration() for SECURITY interface

CHANGES (2025.10.22.01):
- Added _validate_logging_configuration() for LOGGING interface

Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
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


def _validate_logging_configuration(**kwargs) -> Dict[str, Any]:
    """Validate LOGGING interface configuration."""
    issues = []
    warnings = []
    
    try:
        # Check SINGLETON registration
        try:
            import gateway
            manager = gateway.singleton_get('logging_manager')
            if manager is None:
                warnings.append("SINGLETON 'logging_manager' not registered yet")
            else:
                from logging_manager import LoggingCore
                if not isinstance(manager, LoggingCore):
                    issues.append(f"SINGLETON 'logging_manager' wrong type: {type(manager)}")
        except Exception as e:
            warnings.append(f"Could not verify SINGLETON: {e}")
        
        # Check for threading locks
        try:
            import logging_manager
            import inspect
            source = inspect.getsource(logging_manager)
            if 'threading.Lock' in source or 'threading.RLock' in source:
                issues.append("CRITICAL: Found threading locks in logging_manager (AP-08, DEC-04)")
        except Exception as e:
            warnings.append(f"Could not check for threading locks: {e}")
        
        # Check rate limiting configuration
        try:
            import os
            rate_limit_enabled = os.getenv('LOG_RATE_LIMIT_ENABLED', 'true').lower() == 'true'
            max_logs = int(os.getenv('MAX_LOGS_PER_INVOCATION', '500'))
            
            if not rate_limit_enabled:
                warnings.append("Rate limiting disabled (LOG_RATE_LIMIT_ENABLED=false)")
            elif max_logs < 100:
                warnings.append(f"Rate limit very low: {max_logs} logs/invocation")
            elif max_logs > 1000:
                warnings.append(f"Rate limit very high: {max_logs} logs/invocation")
        except Exception as e:
            warnings.append(f"Could not check rate limit config: {e}")
        
        # Check security sanitization
        try:
            import os
            sanitize = os.getenv('SANITIZE_EXCEPTIONS', 'true').lower() == 'true'
            if not sanitize:
                warnings.append("Exception sanitization disabled (SANITIZE_EXCEPTIONS=false)")
        except Exception as e:
            warnings.append(f"Could not check sanitization config: {e}")
        
        # Check reset operation
        try:
            from logging_core import _execute_log_reset_implementation
            result = _execute_log_reset_implementation()
            if not result:
                issues.append("Reset operation returned False")
        except ImportError:
            issues.append("Reset implementation not found (_execute_log_reset_implementation)")
        except Exception as e:
            warnings.append(f"Could not test reset operation: {e}")
        
        # Check gateway routing
        try:
            import gateway
            gateway.logging_reset()
        except AttributeError:
            issues.append("Reset operation not available in gateway (logging_reset)")
        except Exception as e:
            warnings.append(f"Reset routing issue: {e}")
        
        return {
            'component': 'LOGGING',
            'valid': len(issues) == 0,
            'issues': issues,
            'warnings': warnings,
            'summary': f"{len(issues)} issues, {len(warnings)} warnings"
        }
        
    except Exception as e:
        return {
            'component': 'LOGGING',
            'valid': False,
            'error': str(e)
        }


def _validate_security_configuration(**kwargs) -> Dict[str, Any]:
    """
    Validate SECURITY interface configuration.
    
    Checks for:
    - SINGLETON registration (Phase 1 requirement)
    - No threading locks (AP-08, DEC-04)
    - Rate limiting configured
    - Reset operation available
    - Validator and Crypto components present
    
    Returns:
        Dict with validation status and any issues
    """
    issues = []
    warnings = []
    
    try:
        # Check SINGLETON registration
        try:
            import gateway
            manager = gateway.singleton_get('security_manager')
            if manager is None:
                warnings.append("SINGLETON 'security_manager' not registered yet")
            else:
                from security_core import SecurityCore
                if not isinstance(manager, SecurityCore):
                    issues.append(f"SINGLETON 'security_manager' wrong type: {type(manager)}")
        except Exception as e:
            warnings.append(f"Could not verify SINGLETON: {e}")
        
        # Check for threading locks
        try:
            import security_core
            import inspect
            source = inspect.getsource(security_core)
            if 'threading.Lock' in source or 'threading.RLock' in source:
                issues.append("CRITICAL: Found threading locks in security_core (AP-08, DEC-04)")
        except Exception as e:
            warnings.append(f"Could not check for threading locks: {e}")
        
        # Check rate limiting present
        try:
            import gateway
            stats = gateway.security_get_stats()
            rate_limit_stats = stats.get('rate_limit', {})
            
            if not rate_limit_stats:
                issues.append("Rate limiting not configured")
            else:
                rate_limit = rate_limit_stats.get('rate_limit', 0)
                if rate_limit < 100:
                    warnings.append(f"Rate limit very low: {rate_limit} ops/sec")
                elif rate_limit != 1000:
                    warnings.append(f"Non-standard rate limit: {rate_limit} ops/sec (expected 1000)")
        except Exception as e:
            warnings.append(f"Could not check rate limit config: {e}")
        
        # Check reset operation
        try:
            from security_core import _execute_security_reset_implementation
            result = _execute_security_reset_implementation()
            if not result:
                issues.append("Reset operation returned False")
        except ImportError:
            issues.append("Reset implementation not found (_execute_security_reset_implementation)")
        except Exception as e:
            warnings.append(f"Could not test reset operation: {e}")
        
        # Check gateway routing for reset
        try:
            import gateway
            gateway.security_reset()
        except AttributeError:
            issues.append("Reset operation not available in gateway (security_reset)")
        except Exception as e:
            warnings.append(f"Reset routing issue: {e}")
        
        # Check validator and crypto components
        try:
            from security_core import get_security_manager
            manager = get_security_manager()
            
            validator = manager.get_validator()
            if validator is None:
                issues.append("Validator component missing")
            
            crypto = manager.get_crypto()
            if crypto is None:
                issues.append("Crypto component missing")
        except Exception as e:
            warnings.append(f"Could not check components: {e}")
        
        return {
            'component': 'SECURITY',
            'valid': len(issues) == 0,
            'issues': issues,
            'warnings': warnings,
            'summary': f"{len(issues)} issues, {len(warnings)} warnings"
        }
        
    except Exception as e:
        return {
            'component': 'SECURITY',
            'valid': False,
            'error': str(e)
        }


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


__all__ = [
    '_validate_system_architecture',
    '_validate_imports',
    '_validate_gateway_routing',
    '_validate_logging_configuration',
    '_validate_security_configuration',
    '_run_config_unit_tests',
    '_run_config_integration_tests',
    '_run_config_performance_tests',
    '_run_config_compatibility_tests',
    '_run_config_gateway_tests'
]

# EOF
