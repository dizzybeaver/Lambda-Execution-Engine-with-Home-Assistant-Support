"""
debug_performance.py - Debug Performance Operations
Version: 2025.10.21.01
Description: Performance benchmarking operations for debug subsystem
CHANGELOG:
- 2025.10.21.01: Added _benchmark_metrics_operations() for METRICS Phase 3

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


def _benchmark_metrics_operations(**kwargs) -> Dict[str, Any]:
    """
    Benchmark METRICS operations performance.
    
    Tests:
    - record_metric throughput (1000 ops)
    - record_metric with dimensions (1000 ops)
    - get_stats latency (100 calls)
    - Fast path vs normal path comparison (if available)
    
    Returns:
        Dict with:
        - success: bool
        - results: dict with benchmark data
        - summary: dict with human-readable metrics
        
    Example:
        result = _benchmark_metrics_operations()
        # {
        #     'success': True,
        #     'results': {
        #         'record_simple': {
        #             'ops': 1000,
        #             'duration_ms': 50.0,
        #             'ops_per_sec': 20000
        #         },
        #         'record_dimensions': {...},
        #         'get_stats': {
        #             'avg_ms': 1.2,
        #             'min_ms': 0.8,
        #             'max_ms': 2.5,
        #             'p95_ms': 2.0
        #         }
        #     },
        #     'summary': {
        #         'throughput': '20000 ops/sec',
        #         'stats_latency': '1.20ms'
        #     }
        # }
    """
    try:
        from metrics_core import _MANAGER
        
        results = {}
        
        # Benchmark 1: Simple record_metric throughput
        start = time.perf_counter()
        for i in range(1000):
            _MANAGER.record_metric('benchmark.test', float(i))
        duration_ms = (time.perf_counter() - start) * 1000
        
        results['record_simple'] = {
            'ops': 1000,
            'duration_ms': round(duration_ms, 3),
            'ops_per_sec': int(1000 / (duration_ms / 1000))
        }
        
        # Benchmark 2: record_metric with dimensions
        start = time.perf_counter()
        for i in range(1000):
            _MANAGER.record_metric(
                'benchmark.test_dims',
                float(i),
                dimensions={'type': 'test', 'iter': str(i % 10)}
            )
        duration_ms = (time.perf_counter() - start) * 1000
        
        results['record_dimensions'] = {
            'ops': 1000,
            'duration_ms': round(duration_ms, 3),
            'ops_per_sec': int(1000 / (duration_ms / 1000))
        }
        
        # Benchmark 3: get_stats latency
        times = []
        for _ in range(100):
            start = time.perf_counter()
            _MANAGER.get_stats()
            times.append((time.perf_counter() - start) * 1000)
        
        times_sorted = sorted(times)
        results['get_stats'] = {
            'calls': 100,
            'avg_ms': round(sum(times) / len(times), 3),
            'min_ms': round(min(times), 3),
            'max_ms': round(max(times), 3),
            'p95_ms': round(times_sorted[94], 3)
        }
        
        # Benchmark 4: Fast path comparison (if enabled)
        fast_path_enabled = hasattr(_MANAGER, '_HOT_METRICS') and len(_MANAGER._HOT_METRICS) > 0
        
        if fast_path_enabled:
            # Test hot metric (fast path)
            hot_metric = list(_MANAGER._HOT_METRICS)[0] if _MANAGER._HOT_METRICS else 'operation.count'
            
            start = time.perf_counter()
            for i in range(1000):
                _MANAGER.record_metric(hot_metric, float(i))
            fast_duration = (time.perf_counter() - start) * 1000
            
            # Test cold metric (normal path)
            start = time.perf_counter()
            for i in range(1000):
                _MANAGER.record_metric('cold.metric.path', float(i))
            normal_duration = (time.perf_counter() - start) * 1000
            
            improvement = ((normal_duration - fast_duration) / normal_duration) * 100
            
            results['fast_path_comparison'] = {
                'fast_path_ms': round(fast_duration, 3),
                'normal_path_ms': round(normal_duration, 3),
                'improvement_percent': round(improvement, 1),
                'fast_path_enabled': True
            }
        else:
            results['fast_path_comparison'] = {
                'fast_path_enabled': False,
                'note': 'Fast path not configured'
            }
        
        # Generate summary
        summary = {
            'simple_throughput': f"{results['record_simple']['ops_per_sec']:,} ops/sec",
            'dims_throughput': f"{results['record_dimensions']['ops_per_sec']:,} ops/sec",
            'stats_latency': f"{results['get_stats']['avg_ms']:.2f}ms"
        }
        
        if fast_path_enabled:
            summary['fast_path_improvement'] = f"{results['fast_path_comparison']['improvement_percent']:.1f}%"
        
        return {
            'success': True,
            'results': results,
            'summary': summary,
            'timestamp': time.strftime('%Y.%m.%d %H:%M:%S')
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def _get_performance_report(**kwargs) -> Dict[str, Any]:
    """Get comprehensive performance report."""
    from debug.debug_stats import _get_dispatcher_stats, _get_operation_metrics
    
    benchmark_results = _run_performance_benchmark()
    metrics_benchmark = _benchmark_metrics_operations()
    
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
        'timestamp': time.strftime('%Y.%m.%d %H:%M:%S'),
        'benchmark': benchmark_results,
        'metrics_benchmark': metrics_benchmark,
        'dispatcher_stats': dispatcher_stats,
        'operation_metrics': operation_metrics
    }


__all__ = [
    '_run_performance_benchmark',
    '_compare_dispatcher_modes',
    '_benchmark_metrics_operations',
    '_get_performance_report'
]

# EOF
