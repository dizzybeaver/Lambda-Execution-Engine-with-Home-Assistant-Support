"""
debug_health.py - Debug Health Check Operations
Version: 2025.10.22.02
Description: Health check operations for debug subsystem

CHANGES (2025.10.22.02):
- Added _check_security_health() for SECURITY interface

CHANGES (2025.10.22.01):
- Added _check_logging_health() for LOGGING interface

Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
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
    """Check LOGGING interface health."""
    try:
        import gateway
        
        rate_stats = gateway.logging_get_rate_limit_stats()
        error_stats = gateway.logging_get_error_stats()
        template_stats = gateway.logging_get_template_stats()
        
        healthy = True
        issues = []
        warnings = []
        
        if rate_stats.get('limit_exceeded', False):
            healthy = False
            issues.append(f"Rate limit exceeded: {rate_stats['log_count']}/{rate_stats['limit']}")
        elif rate_stats.get('log_count', 0) > rate_stats.get('limit', 500) * 0.8:
            warnings.append(f"Approaching rate limit: {rate_stats['log_count']}/{rate_stats['limit']}")
        
        error_count = error_stats.get('total_errors', 0)
        if error_count > 90:
            warnings.append(f"Error log near capacity: {error_count}/100")
        
        errors_by_type = error_stats.get('errors_by_type', {})
        for error_type, count in errors_by_type.items():
            if count > 10:
                warnings.append(f"High error count for {error_type}: {count}")
        
        if template_stats.get('templates_cached', 0) > 0:
            hit_rate = template_stats.get('hit_rate', 0)
            if hit_rate < 50:
                warnings.append(f"Low template cache hit rate: {hit_rate:.1f}%")
        
        return {
            'component': 'LOGGING',
            'healthy': healthy,
            'issues': issues,
            'warnings': warnings,
            'stats': {
                'rate_limit': rate_stats,
                'errors': error_stats,
                'templates': template_stats
            }
        }
        
    except Exception as e:
        return {
            'component': 'LOGGING',
            'healthy': False,
            'error': str(e)
        }


def _check_security_health(**kwargs) -> Dict[str, Any]:
    """
    Check SECURITY interface health.
    
    Verifies:
    - Rate limiter state (not exceeded)
    - Validator statistics
    - Crypto statistics
    - No excessive rate limiting
    
    Returns:
        Dict with health status and issues
    """
    try:
        import gateway
        
        stats = gateway.security_get_stats()
        
        healthy = True
        issues = []
        warnings = []
        
        # Check rate limiting
        rate_limit_stats = stats.get('rate_limit', {})
        current_ops = rate_limit_stats.get('current_operations', 0)
        rate_limit = rate_limit_stats.get('rate_limit', 1000)
        rate_limited_count = rate_limit_stats.get('rate_limited_count', 0)
        
        if current_ops >= rate_limit:
            healthy = False
            issues.append(f"Rate limit exceeded: {current_ops}/{rate_limit}")
        elif current_ops > rate_limit * 0.8:
            warnings.append(f"Approaching rate limit: {current_ops}/{rate_limit}")
        
        if rate_limited_count > 0:
            if rate_limited_count > 100:
                issues.append(f"High rate limit rejections: {rate_limited_count}")
            else:
                warnings.append(f"Some operations rate limited: {rate_limited_count}")
        
        # Check validator stats
        validator_operations = stats.get('validator_operations_count', 0)
        validator_failures = stats.get('validator_failures_count', 0)
        
        if validator_operations > 0:
            failure_rate = (validator_failures / validator_operations) * 100
            if failure_rate > 50:
                issues.append(f"High validation failure rate: {failure_rate:.1f}%")
            elif failure_rate > 20:
                warnings.append(f"Elevated validation failures: {failure_rate:.1f}%")
        
        # Check crypto stats
        crypto_operations = stats.get('crypto_operations_count', 0)
        crypto_failures = stats.get('crypto_failures_count', 0)
        
        if crypto_operations > 0 and crypto_failures > 0:
            crypto_failure_rate = (crypto_failures / crypto_operations) * 100
            if crypto_failure_rate > 10:
                issues.append(f"Crypto operations failing: {crypto_failure_rate:.1f}%")
        
        return {
            'component': 'SECURITY',
            'healthy': healthy,
            'issues': issues,
            'warnings': warnings,
            'stats': stats
        }
        
    except Exception as e:
        return {
            'component': 'SECURITY',
            'healthy': False,
            'error': str(e)
        }


def _generate_health_report(**kwargs) -> Dict[str, Any]:
    """Generate comprehensive health report with dispatcher metrics."""
    from debug_diagnostics import _diagnose_system_health
    from debug_validation import _validate_system_architecture, _validate_imports, _validate_gateway_routing
    from debug_verification import _verify_registry_operations
    from debug_stats import _get_system_stats, _get_optimization_stats, _get_dispatcher_stats
    
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
    '_generate_health_report'
]

# EOF
