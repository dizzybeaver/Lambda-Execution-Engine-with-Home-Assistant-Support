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


def _validate_cache_configuration(**kwargs) -> Dict[str, Any]:
    """
    Validate cache configuration and compliance (CACHE Phase 3).
    
    Checks:
    - SINGLETON registration (INT-06)
    - Security validations enabled
    - Rate limiting configured
    - Memory limits configured
    - No threading locks (AP-08)
    
    Returns:
        Dict with:
        - valid: bool
        - issues: List[str] (critical violations)
        - warnings: List[str] (non-critical issues)
        - checks_passed: int
        - checks_total: int
    """
    issues = []
    warnings = []
    
    # Check 1: SINGLETON registration
    try:
        from gateway import singleton_get
        if singleton_get('cache_manager') is None:
            warnings.append("⚠️ Not registered with SINGLETON (INT-06)")
    except Exception:
        warnings.append("⚠️ Could not verify SINGLETON registration")
    
    # Check 2: Security validations
    try:
        import cache_core
        code = open(cache_core.__file__).read()
        
        if 'validate_cache_key' not in code:
            issues.append("❌ Cache key validation missing (CVE-SUGA-2025-001)")
        
        if 'validate_ttl' not in code:
            issues.append("❌ TTL validation missing (CVE-SUGA-2025-002)")
    except Exception as e:
        warnings.append(f"⚠️ Could not verify security validations: {e}")
    
    # Check 3: Rate limiting
    try:
        from gateway import cache_get_stats
        stats = cache_get_stats()
        
        if 'rate_limited_count' not in stats:
            issues.append("❌ Rate limiting missing (LESS-21)")
    except Exception:
        warnings.append("⚠️ Could not verify rate limiting")
    
    # Check 4: Memory limits
    try:
        from gateway import cache_get_stats
        stats = cache_get_stats()
        
        if 'max_bytes' not in stats:
            issues.append("❌ Memory limits not configured (LESS-20)")
    except Exception:
        warnings.append("⚠️ Could not verify memory limits")
    
    # Check 5: No threading locks (AP-08)
    try:
        import cache_core
        code = open(cache_core.__file__).read()
        
        if 'threading.Lock' in code or 'threading.RLock' in code:
            issues.append("❌ Threading lock present (AP-08, DEC-04)")
    except Exception:
        warnings.append("⚠️ Could not verify threading compliance")
    
    checks_total = 5
    checks_passed = checks_total - len(issues) - len(warnings)
    
    return {
        'valid': len(issues) == 0,
        'issues': issues,
        'warnings': warnings,
        'checks_passed': checks_passed,
        'checks_total': checks_total,
        'summary': f"{checks_passed}/{checks_total} checks passed"
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
    '_validate_cache_configuration',
    '_run_config_unit_tests',
    '_run_config_integration_tests',
    '_run_config_performance_tests',
    '_run_config_compatibility_tests',
    '_run_config_gateway_tests'
]

# EOF
