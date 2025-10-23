"""
debug_performance.py - Debug Performance Operations
Version: 2025.10.22.01
Description: Performance benchmarking operations for debug subsystem

CHANGELOG:
- 2025.10.22.01: Added INITIALIZATION, UTILITY, and SINGLETON benchmarks
  - Added _benchmark_initialization_operations()
  - Added _benchmark_utility_operations()
  - Added _benchmark_singleton_operations()

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


def _benchmark_initialization_operations(**kwargs) -> Dict[str, Any]:
    """
    Benchmark INITIALIZATION interface operations.
    
    Benchmarks:
    - initialize
    - is_initialized
    - get_config
    - get_status
    - get_stats
    - set_flag
    - get_flag
    - reset
    
    Returns:
        Benchmark results with timing and throughput
    """
    try:
        from gateway import (
            initialization_initialize, initialization_is_initialized,
            initialization_get_config, initialization_get_status, initialization_get_stats,
            initialization_set_flag, initialization_get_flag, initialization_reset
        )
        
        benchmark = {
            'interface': 'INITIALIZATION',
            'timestamp': time.time(),
            'operations': {},
            'summary': {}
        }
        
        iterations = 100
        
        # Benchmark: initialize (idempotent, should return cached after first)
        start = time.perf_counter()
        for i in range(10):  # Fewer iterations for initialization
            initialization_initialize({'benchmark': True})
        duration = time.perf_counter() - start
        benchmark['operations']['initialize'] = {
            'iterations': 10,
            'total_seconds': duration,
            'avg_ms': (duration / 10) * 1000,
            'ops_per_sec': 10 / duration if duration > 0 else 0
        }
        
        # Benchmark: is_initialized
        start = time.perf_counter()
        for i in range(iterations):
            initialization_is_initialized()
        duration = time.perf_counter() - start
        benchmark['operations']['is_initialized'] = {
            'iterations': iterations,
            'total_seconds': duration,
            'avg_ms': (duration / iterations) * 1000,
            'ops_per_sec': iterations / duration if duration > 0 else 0
        }
        
        # Benchmark: get_config
        start = time.perf_counter()
        for i in range(iterations):
            initialization_get_config()
        duration = time.perf_counter() - start
        benchmark['operations']['get_config'] = {
            'iterations': iterations,
            'total_seconds': duration,
            'avg_ms': (duration / iterations) * 1000,
            'ops_per_sec': iterations / duration if duration > 0 else 0
        }
        
        # Benchmark: get_status
        start = time.perf_counter()
        for i in range(iterations):
            initialization_get_status()
        duration = time.perf_counter() - start
        benchmark['operations']['get_status'] = {
            'iterations': iterations,
            'total_seconds': duration,
            'avg_ms': (duration / iterations) * 1000,
            'ops_per_sec': iterations / duration if duration > 0 else 0
        }
        
        # Benchmark: get_stats
        start = time.perf_counter()
        for i in range(iterations):
            initialization_get_stats()
        duration = time.perf_counter() - start
        benchmark['operations']['get_stats'] = {
            'iterations': iterations,
            'total_seconds': duration,
            'avg_ms': (duration / iterations) * 1000,
            'ops_per_sec': iterations / duration if duration > 0 else 0
        }
        
        # Benchmark: set_flag
        start = time.perf_counter()
        for i in range(iterations):
            initialization_set_flag(f'bench_flag_{i}', f'value_{i}')
        duration = time.perf_counter() - start
        benchmark['operations']['set_flag'] = {
            'iterations': iterations,
            'total_seconds': duration,
            'avg_ms': (duration / iterations) * 1000,
            'ops_per_sec': iterations / duration if duration > 0 else 0
        }
        
        # Benchmark: get_flag
        start = time.perf_counter()
        for i in range(iterations):
            initialization_get_flag(f'bench_flag_{i}')
        duration = time.perf_counter() - start
        benchmark['operations']['get_flag'] = {
            'iterations': iterations,
            'total_seconds': duration,
            'avg_ms': (duration / iterations) * 1000,
            'ops_per_sec': iterations / duration if duration > 0 else 0
        }
        
        # Benchmark: reset
        start = time.perf_counter()
        for i in range(10):  # Fewer iterations for reset
            initialization_reset()
            initialization_initialize({'benchmark': True})  # Re-initialize after reset
        duration = time.perf_counter() - start
        benchmark['operations']['reset'] = {
            'iterations': 10,
            'total_seconds': duration,
            'avg_ms': (duration / 10) * 1000,
            'ops_per_sec': 10 / duration if duration > 0 else 0
        }
        
        # Summary
        total_ops = 10 + iterations * 6 + 10  # initialize, 6 ops × iterations, reset
        total_time = sum(op['total_seconds'] for op in benchmark['operations'].values())
        
        benchmark['summary'] = {
            'total_operations': total_ops,
            'total_time_seconds': total_time,
            'overall_ops_per_sec': total_ops / total_time if total_time > 0 else 0,
            'fastest_operation': min(
                benchmark['operations'].items(), 
                key=lambda x: x[1]['avg_ms']
            )[0],
            'slowest_operation': max(
                benchmark['operations'].items(), 
                key=lambda x: x[1]['avg_ms']
            )[0]
        }
        
        return benchmark
        
    except Exception as e:
        return {
            'interface': 'INITIALIZATION',
            'status': 'error',
            'error': str(e),
            'timestamp': time.time()
        }


def _benchmark_utility_operations(**kwargs) -> Dict[str, Any]:
    """Benchmark UTILITY interface operations."""
    try:
        from gateway import (
            utility_generate_uuid, utility_get_timestamp, utility_parse_json,
            utility_deep_merge, utility_validate_string, utility_sanitize_data,
            utility_get_performance_stats, utility_cleanup_cache, utility_reset
        )
        
        benchmark = {
            'interface': 'UTILITY',
            'timestamp': time.time(),
            'operations': {},
            'summary': {}
        }
        
        iterations = 100
        
        # Benchmark: generate_uuid
        start = time.perf_counter()
        for i in range(iterations):
            utility_generate_uuid()
        duration = time.perf_counter() - start
        benchmark['operations']['generate_uuid'] = {
            'iterations': iterations,
            'total_seconds': duration,
            'avg_ms': (duration / iterations) * 1000,
            'ops_per_sec': iterations / duration if duration > 0 else 0
        }
        
        # Benchmark: get_timestamp
        start = time.perf_counter()
        for i in range(iterations):
            utility_get_timestamp()
        duration = time.perf_counter() - start
        benchmark['operations']['get_timestamp'] = {
            'iterations': iterations,
            'total_seconds': duration,
            'avg_ms': (duration / iterations) * 1000,
            'ops_per_sec': iterations / duration if duration > 0 else 0
        }
        
        # Benchmark: parse_json
        test_json = '{"test": "data", "number": 123}'
        start = time.perf_counter()
        for i in range(iterations):
            utility_parse_json(test_json)
        duration = time.perf_counter() - start
        benchmark['operations']['parse_json'] = {
            'iterations': iterations,
            'total_seconds': duration,
            'avg_ms': (duration / iterations) * 1000,
            'ops_per_sec': iterations / duration if duration > 0 else 0
        }
        
        # Benchmark: deep_merge
        dict1 = {'a': 1, 'b': {'c': 2}}
        dict2 = {'b': {'d': 3}, 'e': 4}
        start = time.perf_counter()
        for i in range(iterations):
            utility_deep_merge(dict1, dict2)
        duration = time.perf_counter() - start
        benchmark['operations']['deep_merge'] = {
            'iterations': iterations,
            'total_seconds': duration,
            'avg_ms': (duration / iterations) * 1000,
            'ops_per_sec': iterations / duration if duration > 0 else 0
        }
        
        # Benchmark: validate_string
        test_string = "test_string_value"
        start = time.perf_counter()
        for i in range(iterations):
            utility_validate_string(test_string)
        duration = time.perf_counter() - start
        benchmark['operations']['validate_string'] = {
            'iterations': iterations,
            'total_seconds': duration,
            'avg_ms': (duration / iterations) * 1000,
            'ops_per_sec': iterations / duration if duration > 0 else 0
        }
        
        # Benchmark: sanitize_data
        test_data = {'password': 'secret', 'data': 'value'}
        start = time.perf_counter()
        for i in range(iterations):
            utility_sanitize_data(test_data)
        duration = time.perf_counter() - start
        benchmark['operations']['sanitize_data'] = {
            'iterations': iterations,
            'total_seconds': duration,
            'avg_ms': (duration / iterations) * 1000,
            'ops_per_sec': iterations / duration if duration > 0 else 0
        }
        
        # Benchmark: get_performance_stats
        start = time.perf_counter()
        for i in range(10):  # Fewer iterations for stats
            utility_get_performance_stats()
        duration = time.perf_counter() - start
        benchmark['operations']['get_performance_stats'] = {
            'iterations': 10,
            'total_seconds': duration,
            'avg_ms': (duration / 10) * 1000,
            'ops_per_sec': 10 / duration if duration > 0 else 0
        }
        
        # Benchmark: cleanup_cache
        start = time.perf_counter()
        utility_cleanup_cache()
        duration = time.perf_counter() - start
        benchmark['operations']['cleanup_cache'] = {
            'iterations': 1,
            'total_seconds': duration,
            'avg_ms': duration * 1000,
            'ops_per_sec': 1 / duration if duration > 0 else 0
        }
        
        # Benchmark: reset
        start = time.perf_counter()
        for i in range(10):
            utility_reset()
        duration = time.perf_counter() - start
        benchmark['operations']['reset'] = {
            'iterations': 10,
            'total_seconds': duration,
            'avg_ms': (duration / 10) * 1000,
            'ops_per_sec': 10 / duration if duration > 0 else 0
        }
        
        # Summary
        total_ops = iterations * 6 + 10 + 1 + 10
        total_time = sum(op['total_seconds'] for op in benchmark['operations'].values())
        
        benchmark['summary'] = {
            'total_operations': total_ops,
            'total_time_seconds': total_time,
            'overall_ops_per_sec': total_ops / total_time if total_time > 0 else 0,
            'fastest_operation': min(
                benchmark['operations'].items(), 
                key=lambda x: x[1]['avg_ms']
            )[0],
            'slowest_operation': max(
                benchmark['operations'].items(), 
                key=lambda x: x[1]['avg_ms']
            )[0]
        }
        
        return benchmark
        
    except Exception as e:
        return {
            'interface': 'UTILITY',
            'status': 'error',
            'error': str(e),
            'timestamp': time.time()
        }


def _benchmark_singleton_operations(**kwargs) -> Dict[str, Any]:
    """
    Benchmark SINGLETON interface operations.
    
    Benchmarks:
    - get (with and without factory)
    - set
    - has
    - delete
    - clear
    - get_stats
    - reset
    
    Returns:
        Benchmark results with timing and throughput
    """
    try:
        from gateway import (
            singleton_get, singleton_set, singleton_has, 
            singleton_delete, singleton_clear, singleton_get_stats, singleton_reset
        )
        
        benchmark = {
            'interface': 'SINGLETON',
            'timestamp': time.time(),
            'operations': {},
            'summary': {}
        }
        
        iterations = 100
        
        # Benchmark: set
        start = time.perf_counter()
        for i in range(iterations):
            singleton_set(f'bench_test_{i}', f'value_{i}')
        duration = time.perf_counter() - start
        benchmark['operations']['set'] = {
            'iterations': iterations,
            'total_seconds': duration,
            'avg_ms': (duration / iterations) * 1000,
            'ops_per_sec': iterations / duration if duration > 0 else 0
        }
        
        # Benchmark: get (existing)
        start = time.perf_counter()
        for i in range(iterations):
            singleton_get(f'bench_test_{i}')
        duration = time.perf_counter() - start
        benchmark['operations']['get_existing'] = {
            'iterations': iterations,
            'total_seconds': duration,
            'avg_ms': (duration / iterations) * 1000,
            'ops_per_sec': iterations / duration if duration > 0 else 0
        }
        
        # Benchmark: get (with factory)
        def factory_func():
            return {'test': 'data'}
        
        start = time.perf_counter()
        for i in range(iterations):
            singleton_get(f'bench_factory_{i}', factory_func=factory_func)
        duration = time.perf_counter() - start
        benchmark['operations']['get_with_factory'] = {
            'iterations': iterations,
            'total_seconds': duration,
            'avg_ms': (duration / iterations) * 1000,
            'ops_per_sec': iterations / duration if duration > 0 else 0
        }
        
        # Benchmark: has
        start = time.perf_counter()
        for i in range(iterations):
            singleton_has(f'bench_test_{i}')
        duration = time.perf_counter() - start
        benchmark['operations']['has'] = {
            'iterations': iterations,
            'total_seconds': duration,
            'avg_ms': (duration / iterations) * 1000,
            'ops_per_sec': iterations / duration if duration > 0 else 0
        }
        
        # Benchmark: delete
        start = time.perf_counter()
        for i in range(iterations):
            singleton_delete(f'bench_test_{i}')
        duration = time.perf_counter() - start
        benchmark['operations']['delete'] = {
            'iterations': iterations,
            'total_seconds': duration,
            'avg_ms': (duration / iterations) * 1000,
            'ops_per_sec': iterations / duration if duration > 0 else 0
        }
        
        # Benchmark: get_stats
        start = time.perf_counter()
        for i in range(10):  # Fewer iterations for stats
            singleton_get_stats()
        duration = time.perf_counter() - start
        benchmark['operations']['get_stats'] = {
            'iterations': 10,
            'total_seconds': duration,
            'avg_ms': (duration / 10) * 1000,
            'ops_per_sec': 10 / duration if duration > 0 else 0
        }
        
        # Benchmark: clear
        singleton_set('bench_clear_1', 'value1')
        singleton_set('bench_clear_2', 'value2')
        start = time.perf_counter()
        singleton_clear()
        duration = time.perf_counter() - start
        benchmark['operations']['clear'] = {
            'iterations': 1,
            'total_seconds': duration,
            'avg_ms': duration * 1000,
            'ops_per_sec': 1 / duration if duration > 0 else 0
        }
        
        # Benchmark: reset
        start = time.perf_counter()
        for i in range(10):
            singleton_reset()
        duration = time.perf_counter() - start
        benchmark['operations']['reset'] = {
            'iterations': 10,
            'total_seconds': duration,
            'avg_ms': (duration / 10) * 1000,
            'ops_per_sec': 10 / duration if duration > 0 else 0
        }
        
        # Summary
        total_ops = iterations * 5 + 10 + 1 + 10  # set, get_existing, get_factory, has, delete, stats, clear, reset
        total_time = sum(op['total_seconds'] for op in benchmark['operations'].values())
        
        benchmark['summary'] = {
            'total_operations': total_ops,
            'total_time_seconds': total_time,
            'overall_ops_per_sec': total_ops / total_time if total_time > 0 else 0,
            'fastest_operation': min(
                benchmark['operations'].items(), 
                key=lambda x: x[1]['avg_ms']
            )[0],
            'slowest_operation': max(
                benchmark['operations'].items(), 
                key=lambda x: x[1]['avg_ms']
            )[0]
        }
        
        return benchmark
        
    except Exception as e:
        return {
            'interface': 'SINGLETON',
            'status': 'error',
            'error': str(e),
            'timestamp': time.time()
        }


__all__ = [
    '_run_performance_benchmark',
    '_compare_dispatcher_modes',
    '_get_performance_report',
    '_benchmark_initialization_operations',
    '_benchmark_utility_operations',
    '_benchmark_singleton_operations'
]

# EOF
