"""
debug_performance.py - Debug Performance Operations
Version: 2025.10.22.02
Description: Performance benchmarking operations for debug subsystem

CHANGES (2025.10.22.02):
- Added _benchmark_security_operations() for SECURITY interface

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
        from debug_stats import _get_dispatcher_stats
        
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
    """Benchmark LOGGING interface operations."""
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
        
        recommendations = []
        if results['log_info']['ops_per_sec'] < 10000:
            recommendations.append("Consider reducing log verbosity for performance")
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


def _benchmark_security_operations(**kwargs) -> Dict[str, Any]:
    """
    Benchmark SECURITY interface operations.
    
    Tests:
    - validate_string() throughput
    - sanitize() throughput
    - hash() performance
    - encrypt/decrypt roundtrip
    - reset operation performance
    
    Returns:
        Dict with benchmark results and recommendations
    """
    try:
        import gateway
        import time
        
        results = {}
        
        # Reset for clean benchmark
        gateway.security_reset()
        
        # Benchmark: validate_string
        start = time.perf_counter()
        for i in range(1000):
            gateway.security_validate_string(f"test_string_{i}", min_length=5, max_length=100)
        duration_ms = (time.perf_counter() - start) * 1000
        results['validate_string'] = {
            'ops': 1000,
            'duration_ms': round(duration_ms, 2),
            'ops_per_sec': round(1000 / (duration_ms / 1000), 0),
            'avg_latency_us': round((duration_ms * 1000) / 1000, 2)
        }
        
        # Benchmark: sanitize
        gateway.security_reset()
        test_data = "<script>alert('xss')</script>Test data"
        start = time.perf_counter()
        for i in range(1000):
            gateway.security_sanitize(data=test_data)
        duration_ms = (time.perf_counter() - start) * 1000
        results['sanitize'] = {
            'ops': 1000,
            'duration_ms': round(duration_ms, 2),
            'ops_per_sec': round(1000 / (duration_ms / 1000), 0),
            'avg_latency_us': round((duration_ms * 1000) / 1000, 2)
        }
        
        # Benchmark: hash
        gateway.security_reset()
        start = time.perf_counter()
        for i in range(500):
            gateway.security_hash(data=f"test_data_{i}")
        duration_ms = (time.perf_counter() - start) * 1000
        results['hash'] = {
            'ops': 500,
            'duration_ms': round(duration_ms, 2),
            'ops_per_sec': round(500 / (duration_ms / 1000), 0),
            'avg_latency_us': round((duration_ms * 1000) / 500, 2)
        }
        
        # Benchmark: encrypt/decrypt roundtrip
        gateway.security_reset()
        test_message = "Sensitive data to encrypt"
        start = time.perf_counter()
        for i in range(100):
            encrypted = gateway.security_encrypt(data=test_message)
            decrypted = gateway.security_decrypt(data=encrypted)
        duration_ms = (time.perf_counter() - start) * 1000
        results['encrypt_decrypt_roundtrip'] = {
            'ops': 100,
            'duration_ms': round(duration_ms, 2),
            'ops_per_sec': round(100 / (duration_ms / 1000), 0),
            'avg_latency_ms': round(duration_ms / 100, 2)
        }
        
        # Benchmark: reset operation
        start = time.perf_counter()
        for i in range(100):
            gateway.security_reset()
        duration_ms = (time.perf_counter() - start) * 1000
        results['reset'] = {
            'ops': 100,
            'duration_ms': round(duration_ms, 2),
            'ops_per_sec': round(100 / (duration_ms / 1000), 0),
            'avg_latency_us': round((duration_ms * 1000) / 100, 2)
        }
        
        # Benchmark: rate limiting overhead
        gateway.security_reset()
        # Fill near rate limit
        for i in range(900):
            gateway.security_validate_string(f"fill_{i}", min_length=1, max_length=50)
        
        # Measure rate limit check overhead
        start = time.perf_counter()
        for i in range(100):
            try:
                gateway.security_validate_string(f"rate_test_{i}", min_length=1, max_length=50)
            except RuntimeError:
                pass  # Rate limited
        duration_ms = (time.perf_counter() - start) * 1000
        results['rate_limit_overhead'] = {
            'ops': 100,
            'duration_ms': round(duration_ms, 2),
            'note': 'Measures cost of rate limit checks'
        }
        
        # Generate recommendations
        recommendations = []
        
        if results['validate_string']['ops_per_sec'] < 10000:
            recommendations.append("Validation operations slower than expected")
        
        if results['encrypt_decrypt_roundtrip']['avg_latency_ms'] > 5:
            recommendations.append("Crypto operations have high latency, consider optimization")
        
        if results['sanitize']['ops_per_sec'] > 50000:
            recommendations.append("Sanitization performing excellently")
        
        if not recommendations:
            recommendations.append("SECURITY performance is optimal")
        
        return {
            'success': True,
            'component': 'SECURITY',
            'results': results,
            'recommendations': recommendations
        }
        
    except Exception as e:
        return {
            'success': False,
            'component': 'SECURITY',
            'error': str(e)
        }


def _get_performance_report(**kwargs) -> Dict[str, Any]:
    """Get comprehensive performance report."""
    from debug_stats import _get_dispatcher_stats, _get_operation_metrics
    
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
    '_benchmark_security_operations',
    '_get_performance_report'
]

# EOF
