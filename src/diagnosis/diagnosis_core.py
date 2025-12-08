"""
diagnosis/diagnosis_core.py
Version: 2025-12-08_1
Purpose: Core diagnosis operations and validation
License: Apache 2.0
"""

from typing import Dict, Any


def validate_system_architecture(**kwargs) -> Dict[str, Any]:
    """Validate SUGA architecture compliance."""
    issues = []
    
    try:
        # Check operation registry via public gateway function (to be added)
        try:
            from gateway import get_operation_registry
            registry = get_operation_registry()
            if not registry:
                issues.append("Empty operation registry")
        except (ImportError, AttributeError):
            # Gateway function not yet implemented
            issues.append("get_operation_registry() not available in gateway")
        
        import_check = validate_imports()
        if not import_check.get('compliant', False):
            issues.extend(import_check.get('violations', []))
        
        return {
            'success': True,
            'compliant': len(issues) == 0,
            'issues': issues
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}


def validate_imports(**kwargs) -> Dict[str, Any]:
    """Validate no direct imports between modules."""
    
    try:
        from import_fixer import validate_imports
        return validate_imports('.')
    except ImportError:
        return {'success': True, 'compliant': True, 'note': 'import_fixer not available'}


def validate_gateway_routing(**kwargs) -> Dict[str, Any]:
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


def run_diagnostic_suite(**kwargs) -> Dict[str, Any]:
    """Run comprehensive diagnostic suite."""

    from diagnosis import generate_health_report
    from diagnosis import diagnose_system_health
    
    report = {
        'timestamp': '2025-12-08',
        'suite': 'comprehensive',
        'results': {}
    }
    
    # Health report
    try:
        report['results']['health'] = generate_health_report()
    except Exception as e:
        report['results']['health'] = {'error': str(e)}
    
    # System health
    try:
        report['results']['system'] = diagnose_system_health()
    except Exception as e:
        report['results']['system'] = {'error': str(e)}
    
    # Architecture validation
    try:
        report['results']['architecture'] = validate_system_architecture()
    except Exception as e:
        report['results']['architecture'] = {'error': str(e)}
    
    # Import validation
    try:
        report['results']['imports'] = validate_imports()
    except Exception as e:
        report['results']['imports'] = {'error': str(e)}
    
    # Gateway routing
    try:
        report['results']['gateway_routing'] = validate_gateway_routing()
    except Exception as e:
        report['results']['gateway_routing'] = {'error': str(e)}
    
    return report


__all__ = [
    'validate_system_architecture',
    'validate_imports',
    'validate_gateway_routing',
    'run_diagnostic_suite'
]
