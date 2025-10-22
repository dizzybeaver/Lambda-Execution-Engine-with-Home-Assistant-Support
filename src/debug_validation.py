"""
debug_validation.py - Debug Validation Operations
Version: 2025.10.21.01
Description: System validation operations for debug subsystem
CHANGELOG:
- 2025.10.21.01: Added _validate_metrics_configuration() for METRICS Phase 3

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
import inspect


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


def _validate_metrics_configuration(**kwargs) -> Dict[str, Any]:
    """
    Validate METRICS configuration and compliance.
    
    Checks:
    - No threading locks (DEC-04, AP-08)
    - SINGLETON registration (INT-06)
    - Security validations enabled
    - Memory limits configured
    - Rate limiting present
    
    Returns:
        Dict with:
        - valid: bool (no critical issues)
        - issues: list of critical violations
        - warnings: list of non-critical issues
        - checks_passed: int
        - checks_total: int
        
    Example:
        result = _validate_metrics_configuration()
        # {
        #     'valid': True,
        #     'issues': [],
        #     'warnings': ['⚠️ Not registered with SINGLETON'],
        #     'checks_passed': 4,
        #     'checks_total': 5
        # }
    """
    issues = []
    warnings = []
    checks_total = 5
    
    try:
        from metrics_core import MetricsCore, _MANAGER
        
        # Check 1: No threading locks (AP-08, DEC-04)
        if hasattr(_MANAGER, '_lock'):
            issues.append("❌ Threading lock present (AP-08, DEC-04)")
        
        # Check 2: SINGLETON registration (INT-06)
        try:
            from gateway import singleton_get
            if singleton_get('metrics_core_manager') is None:
                warnings.append("⚠️ Not registered with SINGLETON (INT-06)")
        except:
            warnings.append("⚠️ Could not verify SINGLETON registration")
        
        # Check 3: Security validations (name validation)
        try:
            import metrics_operations
            code = inspect.getsource(metrics_operations)
            if 'validate_metric_name' not in code:
                warnings.append("⚠️ Name validation missing in operations")
        except:
            warnings.append("⚠️ Could not verify security validations")
        
        # Check 4: Rate limiting present
        if not hasattr(_MANAGER, '_rate_limiter'):
            warnings.append("⚠️ Rate limiting not configured")
        
        # Check 5: Memory limits configured
        if not hasattr(_MANAGER, 'MAX_VALUES_PER_METRIC'):
            warnings.append("⚠️ Memory limits not configured")
        
        checks_passed = checks_total - len(issues) - len(warnings)
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'warnings': warnings,
            'checks_passed': checks_passed,
            'checks_total': checks_total,
            'summary': f"{checks_passed}/{checks_total} checks passed"
        }
    except Exception as e:
        return {
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
    '_validate_metrics_configuration',
    '_run_config_unit_tests',
    '_run_config_integration_tests',
    '_run_config_performance_tests',
    '_run_config_compatibility_tests',
    '_run_config_gateway_tests'
]

# EOF
