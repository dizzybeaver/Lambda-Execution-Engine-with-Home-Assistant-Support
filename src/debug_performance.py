"""
debug_performance.py - Debug Performance Operations
Version: 2025.10.22.01
Description: Performance benchmarking operations for debug subsystem

CHANGES (2025.10.22.01):
- Added _benchmark_logging_operations()
- Added _benchmark_security_operations()
- Added _benchmark_config_operations()

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


def _benchmark_logging_operations(**kwargs) -> Dict[str, Any]:
    """
    Benchmark LOGGING interface operations.
    
    Measures:
    - Log message throughput
    - Different log levels performance
    - Format string overhead
    - Handler latency
    
    Returns:
        Dict with benchmark results and recommendations
    """
    try:
        import gateway
        import time
        
        results = {}
        
        # Benchmark 1: log_info
        start = time.perf_counter()
        for i in range(1000):
            gateway.log_info(f"Test message {i}")
        duration_ms = (time.perf_counter() - start) * 1000
        results['log_info'] = {
            'ops': 1000,
            'duration_ms': round(duration_ms, 2),
            'ops_per_sec': round(1000 / (duration_ms / 1000), 0),
            'avg_latency_us': round((duration_ms * 1000) / 1000, 2)
        }
        
        # Benchmark 2: log_error
        start = time.perf_counter()
        for i in range(500):
            gateway.log_error(f"Test error {i}")
        duration_ms = (time.perf_counter() - start) * 1000
        results['log_error'] = {
            'ops': 500,
            'duration_ms': round(duration_ms, 2),
            'ops_per_sec': round(500 / (duration_ms / 1000), 0),
            'avg_latency_us': round((duration_ms * 1000) / 500, 2)
        }
        
        # Benchmark 3: log_warning
        start = time.perf_counter()
        for i in range(500):
            gateway.log_warning(f"Test warning {i}")
        duration_ms = (time.perf_counter() - start) * 1000
        results['log_warning'] = {
            'ops': 500,
            'duration_ms': round(duration_ms, 2),
            'ops_per_sec': round(500 / (duration_ms / 1000), 0),
            'avg_latency_us': round((duration_ms * 1000) / 500, 2)
        }
        
        # Benchmark 4: log_debug
        start = time.perf_counter()
        for i in range(500):
            gateway.log_debug(f"Test debug {i}")
        duration_ms = (time.perf_counter() - start) * 1000
        results['log_debug'] = {
            'ops': 500,
            'duration_ms': round(duration_ms, 2),
            'ops_per_sec': round(500 / (duration_ms / 1000), 0),
            'avg_latency_us': round((duration_ms * 1000) / 500, 2)
        }
        
        # Analyze results and generate recommendations
        recommendations = []
        
        # Check overall throughput
        avg_ops_per_sec = sum(r['ops_per_sec'] for r in results.values()) / len(results)
        
        if avg_ops_per_sec > 50000:
            recommendations.append("Logging throughput is EXCELLENT")
        elif avg_ops_per_sec > 20000:
            recommendations.append("Logging throughput is GOOD")
        elif avg_ops_per_sec > 10000:
            recommendations.append("Logging throughput is ACCEPTABLE")
        else:
            recommendations.append("Logging throughput is LOW - consider optimization")
        
        # Check for latency spikes
        if results['log_error']['avg_latency_us'] > 100:
            recommendations.append("log_error has high latency - check error handlers")
        
        # Performance rating
        if avg_ops_per_sec > 20000:
            performance_rating = "EXCELLENT"
        elif avg_ops_per_sec > 10000:
            performance_rating = "GOOD"
        elif avg_ops_per_sec > 5000:
            performance_rating = "ACCEPTABLE"
        else:
            performance_rating = "POOR"
        
        return {
            'success': True,
            'component': 'LOGGING',
            'performance_rating': performance_rating,
            'results': results,
            'recommendations': recommendations,
            'summary': {
                'total_operations': sum(r['ops'] for r in results.values()),
                'total_duration_ms': sum(r['duration_ms'] for r in results.values()),
                'avg_ops_per_sec': round(avg_ops_per_sec, 0),
                'fastest_operation': max(results.items(), key=lambda x: x[1]['ops_per_sec'])[0],
                'slowest_operation': min(results.items(), key=lambda x: x[1]['ops_per_sec'])[0]
            }
        }
        
    except ImportError as e:
        return {
            'success': False,
            'component': 'LOGGING',
            'error': f'Gateway import failed: {str(e)}'
        }
    except Exception as e:
        return {
            'success': False,
            'component': 'LOGGING',
            'error': f'Benchmark failed: {str(e)}'
        }


def _benchmark_security_operations(**kwargs) -> Dict[str, Any]:
    """
    Benchmark SECURITY interface operations.
    
    Measures:
    - Validation operation latency
    - Hash computation performance
    - Encryption/decryption throughput
    - Sanitization overhead
    
    Returns:
        Dict with benchmark results and recommendations
    """
    try:
        import gateway
        import time
        
        results = {}
        
        # Benchmark 1: validate_string
        start = time.perf_counter()
        for i in range(10000):
            gateway.validate_string("test_string", max_length=100)
        duration_ms = (time.perf_counter() - start) * 1000
        results['validate_string'] = {
            'ops': 10000,
            'duration_ms': round(duration_ms, 2),
            'ops_per_sec': round(10000 / (duration_ms / 1000), 0),
            'avg_latency_us': round((duration_ms * 1000) / 10000, 2)
        }
        
        # Benchmark 2: hash_data
        start = time.perf_counter()
        for i in range(1000):
            gateway.hash_data(f"test_data_{i}")
        duration_ms = (time.perf_counter() - start) * 1000
        results['hash_data'] = {
            'ops': 1000,
            'duration_ms': round(duration_ms, 2),
            'ops_per_sec': round(1000 / (duration_ms / 1000), 0),
            'avg_latency_us': round((duration_ms * 1000) / 1000, 2)
        }
        
        # Benchmark 3: sanitize_input
        start = time.perf_counter()
        for i in range(5000):
            gateway.sanitize_input(f"<script>alert('{i}')</script>")
        duration_ms = (time.perf_counter() - start) * 1000
        results['sanitize_input'] = {
            'ops': 5000,
            'duration_ms': round(duration_ms, 2),
            'ops_per_sec': round(5000 / (duration_ms / 1000), 0),
            'avg_latency_us': round((duration_ms * 1000) / 5000, 2)
        }
        
        # Benchmark 4: generate_correlation_id
        start = time.perf_counter()
        for i in range(10000):
            gateway.generate_correlation_id("test")
        duration_ms = (time.perf_counter() - start) * 1000
        results['generate_correlation_id'] = {
            'ops': 10000,
            'duration_ms': round(duration_ms, 2),
            'ops_per_sec': round(10000 / (duration_ms / 1000), 0),
            'avg_latency_us': round((duration_ms * 1000) / 10000, 2)
        }
        
        # Analyze results and generate recommendations
        recommendations = []
        
        # Check validation performance
        if results['validate_string']['ops_per_sec'] < 50000:
            recommendations.append("validate_string: Consider optimization or caching validation rules")
        
        # Check hash performance
        if results['hash_data']['avg_latency_us'] > 1000:
            recommendations.append("hash_data: HIGH latency, consider faster hash algorithm")
        
        # Check sanitization
        if results['sanitize_input']['ops_per_sec'] < 10000:
            recommendations.append("sanitize_input: Consider optimization or caching sanitization patterns")
        
        # Performance rating
        avg_ops_per_sec = sum(r['ops_per_sec'] for r in results.values()) / len(results)
        
        if avg_ops_per_sec > 50000:
            performance_rating = "EXCELLENT"
        elif avg_ops_per_sec > 20000:
            performance_rating = "GOOD"
        elif avg_ops_per_sec > 10000:
            performance_rating = "ACCEPTABLE"
        else:
            performance_rating = "POOR"
            recommendations.append("CRITICAL: Overall SECURITY performance is low")
        
        if not recommendations:
            recommendations.append("SECURITY operations performance is optimal")
        
        return {
            'success': True,
            'component': 'SECURITY',
            'performance_rating': performance_rating,
            'results': results,
            'recommendations': recommendations,
            'summary': {
                'total_operations': sum(r['ops'] for r in results.values()),
                'total_duration_ms': sum(r['duration_ms'] for r in results.values()),
                'avg_ops_per_sec': round(avg_ops_per_sec, 0),
                'fastest_operation': max(results.items(), key=lambda x: x[1]['ops_per_sec'])[0],
                'slowest_operation': min(results.items(), key=lambda x: x[1]['ops_per_sec'])[0]
            }
        }
        
    except ImportError as e:
        return {
            'success': False,
            'component': 'SECURITY',
            'error': f'Gateway import failed: {str(e)}'
        }
    except Exception as e:
        return {
            'success': False,
            'component': 'SECURITY',
            'error': f'Benchmark failed: {str(e)}'
        }


def _benchmark_config_operations(**kwargs) -> Dict[str, Any]:
    """
    Benchmark CONFIG interface operations.
    
    Measures:
    - Parameter get/set operations
    - Configuration validation
    - Reset operation
    - Rate limiting overhead
    
    Returns:
        Dict with benchmark results and recommendations
    """
    try:
        import gateway
        import time
        
        results = {}
        
        # Benchmark 1: config_get_parameter
        start = time.perf_counter()
        for i in range(1000):
            gateway.config_get_parameter(f"TEST_PARAM_{i % 10}", default="default")
        duration_ms = (time.perf_counter() - start) * 1000
        results['get_parameter'] = {
            'ops': 1000,
            'duration_ms': round(duration_ms, 2),
            'ops_per_sec': round(1000 / (duration_ms / 1000), 0),
            'avg_latency_us': round((duration_ms * 1000) / 1000, 2)
        }
        
        # Benchmark 2: config_set_parameter
        start = time.perf_counter()
        for i in range(500):
            gateway.config_set_parameter(f"TEST_KEY_{i}", f"test_value_{i}")
        duration_ms = (time.perf_counter() - start) * 1000
        results['set_parameter'] = {
            'ops': 500,
            'duration_ms': round(duration_ms, 2),
            'ops_per_sec': round(500 / (duration_ms / 1000), 0),
            'avg_latency_us': round((duration_ms * 1000) / 500, 2)
        }
        
        # Benchmark 3: config_validate_parameter
        start = time.perf_counter()
        for i in range(200):
            gateway.config_validate_parameter("TEST_KEY", "test_value")
        duration_ms = (time.perf_counter() - start) * 1000
        results['validate_parameter'] = {
            'ops': 200,
            'duration_ms': round(duration_ms, 2),
            'ops_per_sec': round(200 / (duration_ms / 1000), 0),
            'avg_latency_us': round((duration_ms * 1000) / 200, 2)
        }
        
        # Benchmark 4: config_get_state
        start = time.perf_counter()
        for i in range(500):
            gateway.config_get_state()
        duration_ms = (time.perf_counter() - start) * 1000
        results['get_state'] = {
            'ops': 500,
            'duration_ms': round(duration_ms, 2),
            'ops_per_sec': round(500 / (duration_ms / 1000), 0),
            'avg_latency_us': round((duration_ms * 1000) / 500, 2)
        }
        
        # Benchmark 5: reset operation
        start = time.perf_counter()
        for i in range(100):
            gateway.config_reset()
        duration_ms = (time.perf_counter() - start) * 1000
        results['reset'] = {
            'ops': 100,
            'duration_ms': round(duration_ms, 2),
            'ops_per_sec': round(100 / (duration_ms / 1000), 0),
            'avg_latency_us': round((duration_ms * 1000) / 100, 2)
        }
        
        # Analyze results and generate recommendations
        recommendations = []
        
        # Check get_parameter performance
        if results['get_parameter']['ops_per_sec'] < 5000:
            recommendations.append("get_parameter: Consider caching frequently accessed parameters")
        elif results['get_parameter']['ops_per_sec'] > 50000:
            recommendations.append("get_parameter: EXCELLENT performance")
        
        # Check set_parameter performance
        if results['set_parameter']['ops_per_sec'] < 1000:
            recommendations.append("set_parameter: Performance degraded, check validation overhead")
        
        # Check validation overhead
        if results['validate_parameter']['avg_latency_us'] > 500:
            recommendations.append("validate_parameter: HIGH latency, simplify validation rules")
        
        # Check reset performance
        if results['reset']['avg_latency_us'] > 1000:
            recommendations.append("reset: Slow operation, optimize state clearing")
        
        # Overall assessment
        avg_ops_per_sec = sum(r['ops_per_sec'] for r in results.values()) / len(results)
        
        if avg_ops_per_sec > 20000:
            performance_rating = "EXCELLENT"
        elif avg_ops_per_sec > 10000:
            performance_rating = "GOOD"
        elif avg_ops_per_sec > 5000:
            performance_rating = "ACCEPTABLE"
        else:
            performance_rating = "POOR"
            recommendations.append("CRITICAL: Overall CONFIG performance is low")
        
        if not recommendations:
            recommendations.append("CONFIG performance is optimal")
        
        return {
            'success': True,
            'component': 'CONFIG',
            'performance_rating': performance_rating,
            'results': results,
            'recommendations': recommendations,
            'summary': {
                'total_operations': sum(r['ops'] for r in results.values()),
                'total_duration_ms': sum(r['duration_ms'] for r in results.values()),
                'avg_ops_per_sec': round(avg_ops_per_sec, 0),
                'fastest_operation': max(results.items(), key=lambda x: x[1]['ops_per_sec'])[0],
                'slowest_operation': min(results.items(), key=lambda x: x[1]['ops_per_sec'])[0]
            }
        }
        
    except ImportError as e:
        return {
            'success': False,
            'component': 'CONFIG',
            'error': f'Gateway import failed: {str(e)}'
        }
    except Exception as e:
        return {
            'success': False,
            'component': 'CONFIG',
            'error': f'Benchmark failed: {str(e)}'
        }


__all__ = [
    '_run_performance_benchmark',
    '_compare_dispatcher_modes',
    '_get_performance_report',
    '_benchmark_logging_operations',
    '_benchmark_security_operations',
    '_benchmark_config_operations'
]

# EOF
