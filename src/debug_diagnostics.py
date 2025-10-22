"""
debug_diagnostics.py - Debug Diagnostic Operations
Version: 2025.10.22.02
Description: System diagnostic operations for debug subsystem

CHANGES (2025.10.22.02):
- Added _diagnose_security_performance() for SECURITY interface

CHANGES (2025.10.22.01):
- Added _diagnose_logging_performance() for LOGGING interface

Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Dict, Any
import gc


def _diagnose_system_health(**kwargs) -> Dict[str, Any]:
    """Comprehensive system health diagnosis."""
    from debug_health import _check_component_health, _check_gateway_health
    
    component_health = _check_component_health()
    gateway_health = _check_gateway_health()
    memory_info = _diagnose_memory()
    
    return {
        'success': True,
        'component_health': component_health,
        'gateway_health': gateway_health,
        'memory': memory_info
    }


def _diagnose_performance(**kwargs) -> Dict[str, Any]:
    """Performance diagnosis."""
    try:
        from gateway import get_gateway_stats
        gateway_stats = get_gateway_stats()
        
        return {
            'success': True,
            'gateway_operations': gateway_stats.get('operations_count', 0),
            'fast_path_enabled': gateway_stats.get('fast_path_enabled', False),
            'call_counts': gateway_stats.get('call_counts', {})
        }
    except:
        return {'success': False, 'error': 'Could not diagnose performance'}


def _diagnose_memory(**kwargs) -> Dict[str, Any]:
    """Memory usage diagnosis."""
    gc_stats = gc.get_stats() if hasattr(gc, 'get_stats') else []
    
    return {
        'success': True,
        'objects': len(gc.get_objects()),
        'garbage': len(gc.garbage),
        'collections': gc.get_count()
    }


def _diagnose_logging_performance(**kwargs) -> Dict[str, Any]:
    """Diagnose LOGGING interface performance."""
    try:
        import gateway
        
        rate_stats = gateway.logging_get_rate_limit_stats()
        error_stats = gateway.logging_get_error_stats()
        template_stats = gateway.logging_get_template_stats()
        
        insights = []
        recommendations = []
        
        log_count = rate_stats.get('log_count', 0)
        limit = rate_stats.get('limit', 500)
        limit_pct = (log_count / limit * 100) if limit > 0 else 0
        
        if rate_stats.get('limit_exceeded', False):
            insights.append(f"Rate limit EXCEEDED: {log_count}/{limit} logs")
            recommendations.append("Increase MAX_LOGS_PER_INVOCATION or reduce log verbosity")
        elif limit_pct > 80:
            insights.append(f"Approaching rate limit: {limit_pct:.1f}% used")
            recommendations.append("Monitor log volume, consider increasing limit")
        else:
            insights.append(f"Rate limiting healthy: {limit_pct:.1f}% used")
        
        if template_stats.get('templates_cached', 0) > 0:
            hit_rate = template_stats.get('hit_rate', 0)
            hits = template_stats.get('template_hits', 0)
            misses = template_stats.get('template_misses', 0)
            
            if hit_rate > 70:
                insights.append(f"Template cache EXCELLENT: {hit_rate:.1f}% hit rate")
            elif hit_rate > 50:
                insights.append(f"Template cache GOOD: {hit_rate:.1f}% hit rate")
            else:
                insights.append(f"Template cache POOR: {hit_rate:.1f}% hit rate")
                recommendations.append("Review template usage patterns")
            
            insights.append(f"Template stats: {hits} hits, {misses} misses, {template_stats['templates_cached']} cached")
        else:
            insights.append("Template caching disabled (USE_LOG_TEMPLATES=false)")
        
        error_count = error_stats.get('total_errors', 0)
        errors_by_type = error_stats.get('errors_by_type', {})
        
        if error_count > 0:
            insights.append(f"Error tracking: {error_count} total errors logged")
            sorted_errors = sorted(errors_by_type.items(), key=lambda x: x[1], reverse=True)
            if sorted_errors:
                top_3 = sorted_errors[:3]
                insights.append(f"Top error types: {', '.join(f'{t}({c})' for t, c in top_3)}")
                if sorted_errors[0][1] > 20:
                    recommendations.append(f"Investigate high error count for {sorted_errors[0][0]}")
        else:
            insights.append("No errors logged this invocation")
        
        if not recommendations:
            recommendations.append("LOGGING performance is optimal")
        
        return {
            'success': True,
            'component': 'LOGGING',
            'stats': {
                'rate_limit': rate_stats,
                'templates': template_stats,
                'errors': error_stats
            },
            'insights': insights,
            'recommendations': recommendations
        }
        
    except Exception as e:
        return {
            'success': False,
            'component': 'LOGGING',
            'error': str(e)
        }


def _diagnose_security_performance(**kwargs) -> Dict[str, Any]:
    """
    Diagnose SECURITY interface performance.
    
    Analyzes:
    - Rate limiting effectiveness
    - Validator operation distribution
    - Crypto operation patterns
    - Failure rate analysis
    
    Returns:
        Dict with performance insights and recommendations
    """
    try:
        import gateway
        
        stats = gateway.security_get_stats()
        
        insights = []
        recommendations = []
        
        # Analyze rate limiting
        rate_limit_stats = stats.get('rate_limit', {})
        current_ops = rate_limit_stats.get('current_operations', 0)
        rate_limit = rate_limit_stats.get('rate_limit', 1000)
        rate_limited_count = rate_limit_stats.get('rate_limited_count', 0)
        
        usage_pct = (current_ops / rate_limit * 100) if rate_limit > 0 else 0
        
        if rate_limited_count > 0:
            insights.append(f"Rate limiting active: {rate_limited_count} operations rejected")
            insights.append(f"Current usage: {usage_pct:.1f}% ({current_ops}/{rate_limit})")
            if rate_limited_count > 50:
                recommendations.append("High rate limiting suggests need to increase limit or optimize upstream")
        else:
            insights.append(f"Rate limiting healthy: {usage_pct:.1f}% used, no rejections")
        
        # Analyze validator performance
        validator_ops = stats.get('validator_operations_count', 0)
        validator_failures = stats.get('validator_failures_count', 0)
        
        if validator_ops > 0:
            failure_rate = (validator_failures / validator_ops) * 100
            insights.append(f"Validator operations: {validator_ops} total, {validator_failures} failures ({failure_rate:.1f}%)")
            
            if failure_rate > 30:
                recommendations.append("High validation failure rate suggests input quality issues")
            elif failure_rate > 10:
                recommendations.append("Monitor validation failures for patterns")
            else:
                insights.append("Validation failure rate acceptable")
        else:
            insights.append("No validator operations recorded")
        
        # Analyze crypto performance
        crypto_ops = stats.get('crypto_operations_count', 0)
        crypto_failures = stats.get('crypto_failures_count', 0)
        
        if crypto_ops > 0:
            crypto_failure_rate = (crypto_failures / crypto_ops) * 100
            insights.append(f"Crypto operations: {crypto_ops} total, {crypto_failures} failures ({crypto_failure_rate:.1f}%)")
            
            if crypto_failure_rate > 5:
                recommendations.append("Elevated crypto failures may indicate key management issues")
            else:
                insights.append("Crypto operations performing well")
        else:
            insights.append("No crypto operations recorded")
        
        # Operation distribution
        total_ops = validator_ops + crypto_ops
        if total_ops > 0:
            validator_pct = (validator_ops / total_ops) * 100
            crypto_pct = (crypto_ops / total_ops) * 100
            insights.append(f"Operation distribution: {validator_pct:.0f}% validation, {crypto_pct:.0f}% crypto")
        
        # Overall assessment
        if not recommendations:
            recommendations.append("SECURITY performance is optimal")
        
        return {
            'success': True,
            'component': 'SECURITY',
            'stats': stats,
            'insights': insights,
            'recommendations': recommendations
        }
        
    except Exception as e:
        return {
            'success': False,
            'component': 'SECURITY',
            'error': str(e)
        }


__all__ = [
    '_diagnose_system_health',
    '_diagnose_performance',
    '_diagnose_memory',
    '_diagnose_logging_performance',
    '_diagnose_security_performance'
]

# EOF
