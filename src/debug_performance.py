"""
debug_performance.py - Debug Performance Operations
Version: 2025.10.22.01
Description: Performance benchmarking operations for debug subsystem

CHANGES (2025.10.22.01):
- Added _benchmark_logging_operations() for LOGGING interface

Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Dict, Any
import time


def _run_performance_benchmark(**kwargs) -> Dict[str, Any]:
    """Run performance benchmark with dispatcher metrics."""
    try:
        from gateway import cache_get, cache_set, log_info, get_metrics_stats
        from debug.debug_stats import _get_dispatcher_stats
        
        start = time.time()
        cache_set('benchmark_key', 'test_value', ttl=60)
        cache_get('benchmark_key')
        log_info('Benchmark test')
        get_metrics_stats()
        duration = (time.time() - start) * 1000
        
        try:
            dispatcher_stats = _get_dispatcher_stats()
        except:
            dispatcher_stats = {'error': 'Could not retrieve dispatcher stats'}
        
        return {
            'success': True,
            'duration_ms': round(duration, 3),
            'operations_tested': 4,
            'dispatcher_performance': dispatcher_stats
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}


def _compare_dispatcher_modes(**kwargs) -> Dict[str, Any]:
    """Compare dispatcher performance modes."""
    try:
        from gateway import execute_operation, GatewayInterface
        return execute_operation(GatewayInterface.METRICS, 'compare_dispatcher_modes')
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'note': 'Dispatcher comparison requires METRICS interface support'
        }


def _benchmark_logging_operations(**kwargs) -> Dict[str, Any]:
    """
    Benchmark LOGGING interface operations.
    
    Tests:
    - log_info() throughput
    - log_error() throughput
    - Rate limiting overhead
    - Template caching efficiency
    - Reset operation performance
    
    Returns:
        Dict with benchmark results and recommendations
    """
    try:
        import gateway
        import time
        
        results = {}
        
        # Reset for clean benchmark
        gateway.logging_reset()
        
        # Benchmark: log_info
        start = time.perf_counter()
        for i in range(1000):
            gateway.log_info(f"Benchmark message {i}", test_run=True)
        duration_ms = (time.perf_counter() - start) * 1000
        results['log_info'] = {
            'ops': 1000,
            'duration_ms': round(duration_ms, 2),
            'ops_per_sec': round(1000 / (duration_ms / 1000), 0),
            'avg_latency_us': round((duration_ms * 1000) / 1000, 2)
        }
        
        # Benchmark: log_error
        gateway.logging_reset()
        start = time.perf_counter()
        for i in range(500):
            gateway.log_error(f"Error message {i}", error=f"Test error {i}")
        duration_ms = (time.perf_counter() - start) * 1000
        results['log_error'] = {
            'ops': 500,
            'duration_ms': round(duration_ms, 2),
            'ops_per_sec': round(500 / (duration_ms / 1000), 0),
            'avg_latency_us': round((duration_ms * 1000) / 500, 2)
        }
        
        # Benchmark: Rate limiting overhead
        gateway.logging_reset()
        # Fill rate limiter
        for i in range(500):
            gateway.log_info(f"Rate test {i}")
        
        # Measure rejected logs
        start = time.perf_counter()
        for i in range(100):
            gateway.log_info(f"Rejected {i}")
        duration_ms = (time.perf_counter() - start) * 1000
        results['rate_limit_overhead'] = {
            'ops': 100,
            'duration_ms': round(duration_ms, 2),
            'note': 'Measures cost of rate limit checks'
        }
        
        # Benchmark: Template caching (if enabled)
        import os
        if os.getenv('USE_LOG_TEMPLATES', 'false').lower() == 'true':
            gateway.logging_reset()
            template_msg = "Template test message"
            
            # First pass (misses)
            start = time.perf_counter()
            for i in range(100):
                gateway.log_info(template_msg)
            miss_duration_ms = (time.perf_counter() - start) * 1000
            
            # Second pass (hits)
            start = time.perf_counter()
            for i in range(100):
                gateway.log_info(template_msg)
            hit_duration_ms = (time.perf_counter() - start) * 1000
            
            improvement_pct = ((miss_duration_ms - hit_duration_ms) / miss_duration_ms) * 100
            
            results['template_cache'] = {
                'miss_duration_ms': round(miss_duration_ms, 2),
                'hit_duration_ms': round(hit_duration_ms, 2),
                'improvement_pct': round(improvement_pct, 1),
                'note': 'Template cache reduces latency'
            }
        else:
            results['template_cache'] = {
                'note': 'Template caching disabled (USE_LOG_TEMPLATES=false)'
            }
        
        # Benchmark: Reset operation
        start = time.perf_counter()
        for i in range(100):
            gateway.logging_reset()
        duration_ms = (time.perf_counter() - start) * 1000
        results['reset'] = {
            'ops': 100,
            'duration_ms': round(duration_ms, 2),
            'ops_per_sec': round(100 / (duration_ms / 1000), 0),
            'avg_latency_us': round((duration_ms * 1000) / 100, 2)
        }
        
        # Generate recommendations
        recommendations = []
        
        if results['log_info']['ops_per_sec'] < 10000:
            recommendations.append("Consider reducing log verbosity for performance")
        
        if 'template_cache' in results and 'improvement_pct' in results['template_cache']:
            if results['template_cache']['improvement_pct'] > 20:
                recommendations.append("Template caching providing significant benefit")
            elif results['template_cache']['improvement_pct'] < 5:
                recommendations.append("Template caching has minimal impact, consider disabling")
        
        if not recommendations:
            recommendations.append("LOGGING performance is optimal")
        
        return {
            'success': True,
            'component': 'LOGGING',
            'results': results,
            'recommendations': recommendations
        }
        
    except Exception as e:
        return {
            'success': False,
            'component': 'LOGGING',
            'error': str(e)
        }


def _get_performance_report(**kwargs) -> Dict[str, Any]:
    """Get comprehensive performance report."""
    from debug.debug_stats import _get_dispatcher_stats, _get_operation_metrics
    
    benchmark_results = _run_performance_benchmark()
    
    try:
        dispatcher_stats = _get_dispatcher_stats()
    except:
        dispatcher_stats = {'error': 'dispatcher stats not available'}
    
    try:
        operation_metrics = _get_operation_metrics()
    except:
        operation_metrics = {'error': 'operation metrics not available'}
    
    return {
        'success': True,
        'timestamp': '2025.10.22',
        'benchmark': benchmark_results,
        'dispatcher_stats': dispatcher_stats,
        'operation_metrics': operation_metrics
    }


__all__ = [
    '_run_performance_benchmark',
    '_compare_dispatcher_modes',
    '_benchmark_logging_operations',
    '_get_performance_report'
]

# EOF
