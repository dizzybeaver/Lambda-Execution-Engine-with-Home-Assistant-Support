"""
debug_performance.py - Debug Performance Operations
Version: 2025.10.14.01
Description: Performance benchmarking operations for debug subsystem

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


def _benchmark_cache_operations(**kwargs) -> Dict[str, Any]:
    """
    Benchmark cache operations (CACHE Phase 3).
    
    Tests:
    - Simple cache_set throughput (1000 ops)
    - cache_get hit latency (100 calls)
    - cache_get miss latency (100 calls)
    - cache_exists latency (100 calls)
    
    Returns:
        Dict with:
        - success: bool
        - results: Dict with benchmark data
        - summary: Dict with key metrics
    """
    try:
        from gateway import cache_set, cache_get, cache_exists, cache_reset
        
        results = {}
        
        # Reset cache for clean benchmark
        cache_reset()
        
        # Benchmark 1: cache_set throughput
        start = time.perf_counter()
        for i in range(1000):
            cache_set(f'benchmark.set.{i}', f'value_{i}')
        duration_ms = (time.perf_counter() - start) * 1000
        
        results['cache_set'] = {
            'ops': 1000,
            'duration_ms': round(duration_ms, 2),
            'ops_per_sec': round(1000 / (duration_ms / 1000), 0)
        }
        
        # Benchmark 2: cache_get hit latency
        times = []
        for i in range(100):
            start = time.perf_counter()
            value = cache_get(f'benchmark.set.{i}')
            times.append((time.perf_counter() - start) * 1000)
        
        results['cache_get_hit'] = {
            'ops': 100,
            'avg_ms': round(sum(times) / len(times), 3),
            'min_ms': round(min(times), 3),
            'max_ms': round(max(times), 3),
            'p95_ms': round(sorted(times)[94], 3)
        }
        
        # Benchmark 3: cache_get miss latency
        times = []
        for i in range(100):
            start = time.perf_counter()
            value = cache_get(f'nonexistent.key.{i}')
            times.append((time.perf_counter() - start) * 1000)
        
        results['cache_get_miss'] = {
            'ops': 100,
            'avg_ms': round(sum(times) / len(times), 3),
            'min_ms': round(min(times), 3),
            'max_ms': round(max(times), 3),
            'p95_ms': round(sorted(times)[94], 3)
        }
        
        # Benchmark 4: cache_exists latency
        times = []
        for i in range(100):
            start = time.perf_counter()
            exists = cache_exists(f'benchmark.set.{i}')
            times.append((time.perf_counter() - start) * 1000)
        
        results['cache_exists'] = {
            'ops': 100,
            'avg_ms': round(sum(times) / len(times), 3),
            'min_ms': round(min(times), 3),
            'max_ms': round(max(times), 3),
            'p95_ms': round(sorted(times)[94], 3)
        }
        
        # Clean up
        cache_reset()
        
        # Generate summary
        summary = {
            'set_throughput': f"{results['cache_set']['ops_per_sec']:,.0f} ops/sec",
            'get_hit_latency': f"{results['cache_get_hit']['avg_ms']:.3f}ms",
            'get_miss_latency': f"{results['cache_get_miss']['avg_ms']:.3f}ms",
            'exists_latency': f"{results['cache_exists']['avg_ms']:.3f}ms"
        }
        
        return {
            'success': True,
            'results': results,
            'summary': summary
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


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
        'timestamp': '2025.10.14',
        'benchmark': benchmark_results,
        'dispatcher_stats': dispatcher_stats,
        'operation_metrics': operation_metrics
    }


__all__ = [
    '_run_performance_benchmark',
    '_benchmark_cache_operations',
    '_compare_dispatcher_modes',
    '_get_performance_report'
]

# EOF
