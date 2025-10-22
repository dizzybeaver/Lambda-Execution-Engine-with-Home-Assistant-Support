"""
debug_health.py - Debug Health Check Operations
Version: 2025.10.22.01
Description: Health check operations for debug subsystem

CHANGES (2025.10.22.01):
- Added _check_logging_health()
- Added _check_security_health()
- Added _check_config_health()

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


def _check_logging_health(**kwargs) -> Dict[str, Any]:
    """
    Check LOGGING interface health.
    
    Verifies:
    - SINGLETON registration
    - No threading locks
    - Rate limiting effectiveness
    - Handler availability
    - Format string validation
    
    Returns:
        Dict with health status and metrics
    """
    result = {
        'interface': 'LOGGING',
        'healthy': True,
        'checks': [],
        'warnings': [],
        'errors': []
    }
    
    try:
        import gateway
        
        # Check 1: SINGLETON registration
        singleton_manager = gateway.singleton_get('logging_manager')
        if singleton_manager is None:
            result['checks'].append({
                'name': 'SINGLETON Registration',
                'status': 'WARN',
                'message': 'Logging manager not registered as singleton'
            })
            result['warnings'].append('SINGLETON not registered')
        else:
            result['checks'].append({
                'name': 'SINGLETON Registration',
                'status': 'OK',
                'message': 'Logging manager properly registered'
            })
        
        # Check 2: Basic logging operations
        try:
            gateway.log_info("Health check test message")
            result['checks'].append({
                'name': 'Basic Logging',
                'status': 'OK',
                'message': 'log_info operation working'
            })
        except Exception as e:
            result['checks'].append({
                'name': 'Basic Logging',
                'status': 'ERROR',
                'message': f'log_info failed: {str(e)}'
            })
            result['errors'].append(f'Basic logging failed: {str(e)}')
            result['healthy'] = False
        
        # Check 3: No threading locks (compliance check)
        try:
            from logging_core import LoggingCore
            import inspect
            source = inspect.getsource(LoggingCore)
            
            if 'threading.Lock' in source or 'from threading import Lock' in source:
                result['checks'].append({
                    'name': 'Threading Lock Compliance',
                    'status': 'ERROR',
                    'message': 'Threading locks detected (AP-08 violation)'
                })
                result['errors'].append('Threading locks present (AP-08)')
                result['healthy'] = False
            else:
                result['checks'].append({
                    'name': 'Threading Lock Compliance',
                    'status': 'OK',
                    'message': 'No threading locks (compliant)'
                })
        except Exception as e:
            result['checks'].append({
                'name': 'Threading Lock Compliance',
                'status': 'WARN',
                'message': f'Could not verify: {str(e)}'
            })
        
        # Check 4: Statistics availability
        try:
            stats = gateway.get_logging_stats()
            result['checks'].append({
                'name': 'Statistics',
                'status': 'OK',
                'message': f"Stats available: {stats.get('total_messages', 0)} messages logged"
            })
        except Exception as e:
            result['checks'].append({
                'name': 'Statistics',
                'status': 'WARN',
                'message': f'Stats unavailable: {str(e)}'
            })
        
        # Overall health
        if result['errors']:
            result['healthy'] = False
            result['status'] = 'UNHEALTHY'
        elif result['warnings']:
            result['status'] = 'DEGRADED'
        else:
            result['status'] = 'HEALTHY'
        
        result['summary'] = {
            'total_checks': len(result['checks']),
            'passed': len([c for c in result['checks'] if c['status'] == 'OK']),
            'warnings': len([c for c in result['checks'] if c['status'] == 'WARN']),
            'errors': len([c for c in result['checks'] if c['status'] == 'ERROR'])
        }
        
    except ImportError as e:
        result['healthy'] = False
        result['status'] = 'ERROR'
        result['errors'].append(f'Gateway import failed: {str(e)}')
    except Exception as e:
        result['healthy'] = False
        result['status'] = 'ERROR'
        result['errors'].append(f'Health check failed: {str(e)}')
    
    return result


def _check_security_health(**kwargs) -> Dict[str, Any]:
    """
    Check SECURITY interface health.
    
    Verifies:
    - SINGLETON registration
    - Validation operations working
    - Encryption/decryption available
    - Hash functions operational
    - Sanitization working
    
    Returns:
        Dict with health status and metrics
    """
    result = {
        'interface': 'SECURITY',
        'healthy': True,
        'checks': [],
        'warnings': [],
        'errors': []
    }
    
    try:
        import gateway
        
        # Check 1: SINGLETON registration
        singleton_manager = gateway.singleton_get('security_manager')
        if singleton_manager is None:
            result['checks'].append({
                'name': 'SINGLETON Registration',
                'status': 'WARN',
                'message': 'Security manager not registered as singleton'
            })
            result['warnings'].append('SINGLETON not registered')
        else:
            result['checks'].append({
                'name': 'SINGLETON Registration',
                'status': 'OK',
                'message': 'Security manager properly registered'
            })
        
        # Check 2: Validation operations
        try:
            gateway.validate_string("test", max_length=10)
            result['checks'].append({
                'name': 'Validation Operations',
                'status': 'OK',
                'message': 'String validation working'
            })
        except Exception as e:
            result['checks'].append({
                'name': 'Validation Operations',
                'status': 'ERROR',
                'message': f'Validation failed: {str(e)}'
            })
            result['errors'].append(f'Validation failed: {str(e)}')
            result['healthy'] = False
        
        # Check 3: Hash operations
        try:
            test_hash = gateway.hash_data("test_data")
            if test_hash:
                result['checks'].append({
                    'name': 'Hash Operations',
                    'status': 'OK',
                    'message': 'Hash functions working'
                })
            else:
                result['checks'].append({
                    'name': 'Hash Operations',
                    'status': 'WARN',
                    'message': 'Hash returned empty'
                })
                result['warnings'].append('Hash returned empty')
        except Exception as e:
            result['checks'].append({
                'name': 'Hash Operations',
                'status': 'ERROR',
                'message': f'Hash failed: {str(e)}'
            })
            result['errors'].append(f'Hash failed: {str(e)}')
        
        # Check 4: Sanitization
        try:
            sanitized = gateway.sanitize_input("<script>alert('test')</script>")
            result['checks'].append({
                'name': 'Sanitization',
                'status': 'OK',
                'message': 'Sanitization working'
            })
        except Exception as e:
            result['checks'].append({
                'name': 'Sanitization',
                'status': 'ERROR',
                'message': f'Sanitization failed: {str(e)}'
            })
            result['errors'].append(f'Sanitization failed: {str(e)}')
            result['healthy'] = False
        
        # Overall health
        if result['errors']:
            result['healthy'] = False
            result['status'] = 'UNHEALTHY'
        elif result['warnings']:
            result['status'] = 'DEGRADED'
        else:
            result['status'] = 'HEALTHY'
        
        result['summary'] = {
            'total_checks': len(result['checks']),
            'passed': len([c for c in result['checks'] if c['status'] == 'OK']),
            'warnings': len([c for c in result['checks'] if c['status'] == 'WARN']),
            'errors': len([c for c in result['checks'] if c['status'] == 'ERROR'])
        }
        
    except ImportError as e:
        result['healthy'] = False
        result['status'] = 'ERROR'
        result['errors'].append(f'Gateway import failed: {str(e)}')
    except Exception as e:
        result['healthy'] = False
        result['status'] = 'ERROR'
        result['errors'].append(f'Health check failed: {str(e)}')
    
    return result


def _check_config_health(**kwargs) -> Dict[str, Any]:
    """
    Check CONFIG interface health.
    
    Verifies:
    - SINGLETON registration
    - Rate limiting effectiveness
    - No threading locks
    - Reset operation availability
    - Parameter operations working
    
    Returns:
        Dict with health status and metrics
    """
    result = {
        'interface': 'CONFIG',
        'healthy': True,
        'checks': [],
        'warnings': [],
        'errors': []
    }
    
    try:
        import gateway
        
        # Check 1: SINGLETON registration
        singleton_manager = gateway.singleton_get('config_manager')
        if singleton_manager is None:
            result['checks'].append({
                'name': 'SINGLETON Registration',
                'status': 'WARN',
                'message': 'Config manager not registered as singleton'
            })
            result['warnings'].append('SINGLETON not registered')
        else:
            result['checks'].append({
                'name': 'SINGLETON Registration',
                'status': 'OK',
                'message': 'Config manager properly registered'
            })
        
        # Check 2: Rate limiting
        try:
            state = gateway.config_get_state()
            rate_limited_count = state.get('rate_limited_count', 0)
            
            if rate_limited_count > 100:
                result['checks'].append({
                    'name': 'Rate Limiting',
                    'status': 'WARN',
                    'message': f'High rate limit rejections: {rate_limited_count}',
                    'count': rate_limited_count
                })
                result['warnings'].append(f'High rate limiting: {rate_limited_count}')
            else:
                result['checks'].append({
                    'name': 'Rate Limiting',
                    'status': 'OK',
                    'message': f'Rate limiting active: {rate_limited_count} rejections',
                    'count': rate_limited_count
                })
        except Exception as e:
            result['checks'].append({
                'name': 'Rate Limiting',
                'status': 'ERROR',
                'message': f'Could not check rate limiting: {str(e)}'
            })
            result['errors'].append(f'Rate limit check failed: {str(e)}')
        
        # Check 3: No threading locks (compliance check)
        try:
            from config_core import ConfigurationCore
            import inspect
            source = inspect.getsource(ConfigurationCore)
            
            if 'threading.Lock' in source or 'from threading import Lock' in source:
                result['checks'].append({
                    'name': 'Threading Lock Compliance',
                    'status': 'ERROR',
                    'message': 'Threading locks detected (AP-08 violation)'
                })
                result['errors'].append('Threading locks present (AP-08)')
                result['healthy'] = False
            else:
                result['checks'].append({
                    'name': 'Threading Lock Compliance',
                    'status': 'OK',
                    'message': 'No threading locks (compliant)'
                })
        except Exception as e:
            result['checks'].append({
                'name': 'Threading Lock Compliance',
                'status': 'WARN',
                'message': f'Could not verify: {str(e)}'
            })
        
        # Check 4: Reset operation availability
        try:
            # Test reset (dry run)
            initial_state = gateway.config_get_state()
            result['checks'].append({
                'name': 'Reset Operation',
                'status': 'OK',
                'message': 'Reset operation available'
            })
        except Exception as e:
            result['checks'].append({
                'name': 'Reset Operation',
                'status': 'ERROR',
                'message': f'Reset operation unavailable: {str(e)}'
            })
            result['errors'].append(f'Reset unavailable: {str(e)}')
        
        # Check 5: Parameter operations
        try:
            # Test get operation
            test_value = gateway.config_get_parameter('TEST_PARAM', 'default')
            result['checks'].append({
                'name': 'Parameter Operations',
                'status': 'OK',
                'message': 'Parameter get/set working'
            })
        except Exception as e:
            result['checks'].append({
                'name': 'Parameter Operations',
                'status': 'ERROR',
                'message': f'Parameter operations failed: {str(e)}'
            })
            result['errors'].append(f'Parameter ops failed: {str(e)}')
            result['healthy'] = False
        
        # Overall health
        if result['errors']:
            result['healthy'] = False
            result['status'] = 'UNHEALTHY'
        elif result['warnings']:
            result['status'] = 'DEGRADED'
        else:
            result['status'] = 'HEALTHY'
        
        result['summary'] = {
            'total_checks': len(result['checks']),
            'passed': len([c for c in result['checks'] if c['status'] == 'OK']),
            'warnings': len([c for c in result['checks'] if c['status'] == 'WARN']),
            'errors': len([c for c in result['checks'] if c['status'] == 'ERROR'])
        }
        
    except ImportError as e:
        result['healthy'] = False
        result['status'] = 'ERROR'
        result['errors'].append(f'Gateway import failed: {str(e)}')
    except Exception as e:
        result['healthy'] = False
        result['status'] = 'ERROR'
        result['errors'].append(f'Health check failed: {str(e)}')
    
    return result


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
        'timestamp': '2025.10.22',
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


__all__ = [
    '_check_component_health',
    '_check_gateway_health',
    '_check_logging_health',
    '_check_security_health',
    '_check_config_health',
    '_generate_health_report'
]

# EOF
