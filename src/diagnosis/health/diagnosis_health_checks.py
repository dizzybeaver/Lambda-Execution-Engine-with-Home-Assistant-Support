"""
diagnosis/health/diagnosis_health_checks.py
Version: 2025-12-08_1
Purpose: Basic component and gateway health checks
License: Apache 2.0
"""

from typing import Dict, Any


def check_component_health(**kwargs) -> Dict[str, Any]:
    """Check component health."""
    try:
        from gateway import check_all_components
        return check_all_components()
    except ImportError:
        return {'success': False, 'error': 'Gateway not available'}


def check_gateway_health(**kwargs) -> Dict[str, Any]:
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


def generate_health_report(**kwargs) -> Dict[str, Any]:
    """Generate comprehensive health report with dispatcher metrics."""
    from diagnosis import diagnose_system_health
    from diagnosis import (
        validate_system_architecture,
        validate_imports,
        validate_gateway_routing
    )
    from debug_verification import verify_registry_operations
    from debug_stats import get_system_stats, get_optimization_stats, get_dispatcher_stats
    
    try:
        dispatcher_stats = get_dispatcher_stats()
    except:
        dispatcher_stats = {'error': 'dispatcher stats not available'}
    
    return {
        'timestamp': '2025-12-08',
        'system_health': diagnose_system_health(),
        'validation': {
            'architecture': validate_system_architecture(),
            'imports': validate_imports(),
            'gateway_routing': validate_gateway_routing(),
            'registry_operations': verify_registry_operations()
        },
        'stats': get_system_stats(),
        'optimization': get_optimization_stats(),
        'dispatcher_performance': dispatcher_stats
    }


__all__ = [
    'check_component_health',
    'check_gateway_health',
    'generate_health_report'
]
