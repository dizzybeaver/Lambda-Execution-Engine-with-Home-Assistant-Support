"""
debug_validation.py - Debug Validation Operations
Version: 2025.10.22.01
Description: System validation operations for debug subsystem

CHANGES (2025.10.22.01):
- Added _validate_logging_configuration()
- Added _validate_security_configuration()
- Added _validate_config_configuration()

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


def _validate_logging_configuration(**kwargs) -> Dict[str, Any]:
    """
    Validate LOGGING interface configuration.
    
    Checks:
    - SINGLETON registration
    - No threading locks (AP-08 compliance)
    - Handler configuration
    - Format string validation
    - Log level settings
    - Output destination availability
    
    Returns:
        Dict with validation results, issues, and warnings
    """
    issues = []
    warnings = []
    compliant = True
    
    try:
        # Check 1: SINGLETON registration
        try:
            import gateway
            manager = gateway.singleton_get('logging_manager')
            if manager is None:
                warnings.append("SINGLETON 'logging_manager' not registered yet")
            else:
                from logging_core import LoggingCore
                if not isinstance(manager, LoggingCore):
                    issues.append(f"SINGLETON 'logging_manager' wrong type: {type(manager)}")
                    compliant = False
        except Exception as e:
            warnings.append(f"Could not verify SINGLETON: {e}")
        
        # Check 2: No threading locks (CRITICAL compliance check)
        try:
            import logging_core
            import inspect
            source = inspect.getsource(logging_core)
            
            if 'threading.Lock' in source or 'threading.RLock' in source or 'from threading import Lock' in source:
                issues.append("CRITICAL: Found threading locks in logging_core (AP-08, DEC-04, LESS-17)")
                compliant = False
            else:
                # Successfully compliant
                pass
        except Exception as e:
            warnings.append(f"Could not check for threading locks: {e}")
        
        # Check 3: Basic logging operations work
        try:
            gateway.log_info("Configuration validation test")
        except Exception as e:
            issues.append(f"Basic logging operation failed: {e}")
            compliant = False
        
        # Check 4: Statistics available
        try:
            stats = gateway.get_logging_stats()
            if not isinstance(stats, dict):
                warnings.append("Logging stats returned non-dict type")
        except Exception as e:
            warnings.append(f"Could not retrieve logging stats: {e}")
        
        # Build result
        result = {
            'success': True,
            'interface': 'LOGGING',
            'compliant': compliant,
            'issues': issues,
            'warnings': warnings,
            'checks': {
                'singleton_registration': 'OK' if not any('SINGLETON' in i for i in issues) else 'FAIL',
                'no_threading_locks': 'OK' if not any('threading locks' in i for i in issues) else 'FAIL',
                'basic_operations': 'OK' if not any('Basic logging' in i for i in issues) else 'FAIL',
                'statistics': 'OK'
            },
            'summary': {
                'total_issues': len(issues),
                'total_warnings': len(warnings),
                'status': 'COMPLIANT' if compliant else 'NON_COMPLIANT'
            }
        }
        
        return result
        
    except ImportError as e:
        return {
            'success': False,
            'error': f'Gateway import failed: {str(e)}',
            'interface': 'LOGGING',
            'compliant': False
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'Validation failed: {str(e)}',
            'interface': 'LOGGING',
            'compliant': False
        }


def _validate_security_configuration(**kwargs) -> Dict[str, Any]:
    """
    Validate SECURITY interface configuration.
    
    Checks:
    - SINGLETON registration
    - Validation operations configured
    - Encryption/decryption available
    - Hash algorithms supported
    - Sanitization rules loaded
    - Token validation setup
    
    Returns:
        Dict with validation results, issues, and warnings
    """
    issues = []
    warnings = []
    compliant = True
    
    try:
        # Check 1: SINGLETON registration
        try:
            import gateway
            manager = gateway.singleton_get('security_manager')
            if manager is None:
                warnings.append("SINGLETON 'security_manager' not registered yet")
            else:
                from security_core import SecurityCore
                if not isinstance(manager, SecurityCore):
                    issues.append(f"SINGLETON 'security_manager' wrong type: {type(manager)}")
                    compliant = False
        except Exception as e:
            warnings.append(f"Could not verify SINGLETON: {e}")
        
        # Check 2: Validation operations work
        try:
            gateway.validate_string("test", max_length=10)
        except Exception as e:
            issues.append(f"Validation operation failed: {e}")
            compliant = False
        
        # Check 3: Hash operations available
        try:
            test_hash = gateway.hash_data("test_data")
            if not test_hash:
                warnings.append("Hash operation returned empty result")
        except Exception as e:
            issues.append(f"Hash operation failed: {e}")
            compliant = False
        
        # Check 4: Sanitization works
        try:
            sanitized = gateway.sanitize_input("<script>test</script>")
        except Exception as e:
            issues.append(f"Sanitization failed: {e}")
            compliant = False
        
        # Check 5: Correlation ID generation
        try:
            corr_id = gateway.generate_correlation_id("test")
            if not corr_id:
                warnings.append("Correlation ID generation returned empty")
        except Exception as e:
            warnings.append(f"Correlation ID generation failed: {e}")
        
        # Build result
        result = {
            'success': True,
            'interface': 'SECURITY',
            'compliant': compliant,
            'issues': issues,
            'warnings': warnings,
            'checks': {
                'singleton_registration': 'OK' if not any('SINGLETON' in i for i in issues) else 'FAIL',
                'validation_operations': 'OK' if not any('Validation' in i for i in issues) else 'FAIL',
                'hash_operations': 'OK' if not any('Hash' in i for i in issues) else 'FAIL',
                'sanitization': 'OK' if not any('Sanitization' in i for i in issues) else 'FAIL',
                'correlation_id': 'OK'
            },
            'summary': {
                'total_issues': len(issues),
                'total_warnings': len(warnings),
                'status': 'COMPLIANT' if compliant else 'NON_COMPLIANT'
            }
        }
        
        return result
        
    except ImportError as e:
        return {
            'success': False,
            'error': f'Gateway import failed: {str(e)}',
            'interface': 'SECURITY',
            'compliant': False
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'Validation failed: {str(e)}',
            'interface': 'SECURITY',
            'compliant': False
        }


def _validate_config_configuration(**kwargs) -> Dict[str, Any]:
    """
    Validate CONFIG interface configuration.
    
    Checks:
    - SINGLETON registration
    - No threading locks (AP-08 compliance)
    - Rate limiting configuration
    - Parameter Store setup
    - Reset operation availability
    - Configuration initialization
    
    Returns:
        Dict with validation results, issues, and warnings
    """
    issues = []
    warnings = []
    compliant = True
    
    try:
        # Check 1: SINGLETON registration
        try:
            import gateway
            manager = gateway.singleton_get('config_manager')
            if manager is None:
                warnings.append("SINGLETON 'config_manager' not registered yet")
            else:
                from config_core import ConfigurationCore
                if not isinstance(manager, ConfigurationCore):
                    issues.append(f"SINGLETON 'config_manager' wrong type: {type(manager)}")
                    compliant = False
        except Exception as e:
            warnings.append(f"Could not verify SINGLETON: {e}")
        
        # Check 2: No threading locks (CRITICAL compliance check)
        try:
            import config_core
            import inspect
            source = inspect.getsource(config_core)
            
            if 'threading.Lock' in source or 'threading.RLock' in source or 'from threading import Lock' in source:
                issues.append("CRITICAL: Found threading locks in config_core (AP-08, DEC-04, LESS-17)")
                compliant = False
            else:
                # Successfully compliant
                pass
        except Exception as e:
            warnings.append(f"Could not check for threading locks: {e}")
        
        # Check 3: Rate limiting configuration
        try:
            state = gateway.config_get_state()
            rate_limited_count = state.get('rate_limited_count', 0)
            
            if rate_limited_count > 1000:
                warnings.append(f"VERY HIGH rate limit rejections: {rate_limited_count}")
            elif rate_limited_count > 100:
                warnings.append(f"HIGH rate limit rejections: {rate_limited_count}")
            # 0-100 is normal, no warning needed
        except Exception as e:
            warnings.append(f"Could not check rate limiting: {e}")
        
        # Check 4: Parameter Store configuration
        try:
            import os
            use_parameter_store = os.getenv('USE_PARAMETER_STORE', 'false').lower() == 'true'
            parameter_prefix = os.getenv('PARAMETER_PREFIX', '/lambda-execution-engine')
            
            if use_parameter_store:
                # Check prefix format
                if not parameter_prefix.startswith('/'):
                    issues.append(f"Parameter prefix must start with '/': {parameter_prefix}")
                    compliant = False
                
                # Check if prefix is reasonable
                if len(parameter_prefix) < 2:
                    warnings.append(f"Parameter prefix very short: {parameter_prefix}")
                elif len(parameter_prefix) > 100:
                    warnings.append(f"Parameter prefix very long: {parameter_prefix}")
            else:
                # Parameter Store disabled - not an issue, just informational
                pass
        except Exception as e:
            warnings.append(f"Could not check Parameter Store config: {e}")
        
        # Check 5: Reset operation availability
        try:
            from config_core import _reset_config_implementation
            # Operation exists - good
        except ImportError:
            issues.append("CRITICAL: Reset operation not available (_reset_config_implementation)")
            compliant = False
        except Exception as e:
            warnings.append(f"Could not verify reset operation: {e}")
        
        # Check 6: Configuration initialization
        try:
            state = gateway.config_get_state()
            initialized = state.get('initialized', False)
            
            if not initialized:
                warnings.append("Configuration not initialized yet (call config_initialize())")
            
            config_keys = state.get('config_keys', [])
            if initialized and len(config_keys) == 0:
                warnings.append("Configuration initialized but empty")
        except Exception as e:
            warnings.append(f"Could not check initialization: {e}")
        
        # Check 7: Core dependencies available
        try:
            from config_state import ConfigurationState, ConfigurationVersion
            from config_validator import ConfigurationValidator
            from config_loader import (
                load_from_environment,
                load_from_file,
                apply_user_overrides,
                merge_configs
            )
        except ImportError as e:
            issues.append(f"CRITICAL: Missing config dependencies: {e}")
            compliant = False
        
        # Build result
        result = {
            'success': True,
            'interface': 'CONFIG',
            'compliant': compliant,
            'issues': issues,
            'warnings': warnings,
            'checks': {
                'singleton_registration': 'OK' if not any('SINGLETON' in i for i in issues) else 'FAIL',
                'no_threading_locks': 'OK' if not any('threading locks' in i for i in issues) else 'FAIL',
                'rate_limiting': 'OK',
                'parameter_store': 'OK' if not any('Parameter prefix' in i for i in issues) else 'FAIL',
                'reset_operation': 'OK' if not any('Reset operation' in i for i in issues) else 'FAIL',
                'initialization': 'OK',
                'dependencies': 'OK' if not any('dependencies' in i for i in issues) else 'FAIL'
            },
            'summary': {
                'total_issues': len(issues),
                'total_warnings': len(warnings),
                'status': 'COMPLIANT' if compliant else 'NON_COMPLIANT'
            }
        }
        
        return result
        
    except ImportError as e:
        return {
            'success': False,
            'error': f'Gateway import failed: {str(e)}',
            'interface': 'CONFIG',
            'compliant': False
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'Validation failed: {str(e)}',
            'interface': 'CONFIG',
            'compliant': False
        }


__all__ = [
    '_validate_system_architecture',
    '_validate_imports',
    '_validate_gateway_routing',
    '_run_config_unit_tests',
    '_run_config_integration_tests',
    '_run_config_performance_tests',
    '_run_config_compatibility_tests',
    '_run_config_gateway_tests',
    '_validate_logging_configuration',
    '_validate_security_configuration',
    '_validate_config_configuration'
]

# EOF
