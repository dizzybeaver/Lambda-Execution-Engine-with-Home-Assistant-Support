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


def _benchmark_http_client_operations(**kwargs) -> Dict[str, Any]:
    """
    Benchmark HTTP_CLIENT interface operations.
    
    Benchmarks:
    1. GET request (100 ops) - Basic HTTP GET
    2. POST request (100 ops) - HTTP POST with JSON
    3. Connection setup (50 ops) - New connection overhead
    4. get_stats (200 ops) - Statistics retrieval
    5. reset (10 ops) - Reset operation
    
    Total: 460 operations
    
    NOTE: Actual HTTP requests are NOT made during benchmark.
    This tests the client infrastructure, not network performance.
    
    Returns:
        Dict with benchmark results for each operation
        
    REF: LESS-21 (Rate limiting performance impact)
    """
    from http_client_core import get_http_client_manager
    
    benchmark = {
        'interface': 'HTTP_CLIENT',
        'timestamp': time.time(),
        'operations': {},
        'total_operations': 460
    }
    
    try:
        manager = get_http_client_manager()
        
        # Benchmark 1: GET Request Infrastructure (not actual network call)
        operation_count = 100
        start = time.perf_counter()
        
        for _ in range(operation_count):
            _ = {
                'method': 'GET',
                'url': 'http://test.local/api',
                'headers': {'Content-Type': 'application/json'}
            }
        
        elapsed = time.perf_counter() - start
        
        benchmark['operations']['get_request_setup'] = {
            'operation_count': operation_count,
            'total_time_ms': round(elapsed * 1000, 3),
            'avg_time_ms': round((elapsed * 1000) / operation_count, 3),
            'ops_per_second': round(operation_count / elapsed, 2),
            'description': 'GET request parameter setup (no network)'
        }
        
        # Benchmark 2: POST Request Infrastructure
        operation_count = 100
        start = time.perf_counter()
        
        for _ in range(operation_count):
            _ = {
                'method': 'POST',
                'url': 'http://test.local/api',
                'json': {'test': 'data'},
                'headers': {'Content-Type': 'application/json'}
            }
        
        elapsed = time.perf_counter() - start
        
        benchmark['operations']['post_request_setup'] = {
            'operation_count': operation_count,
            'total_time_ms': round(elapsed * 1000, 3),
            'avg_time_ms': round((elapsed * 1000) / operation_count, 3),
            'ops_per_second': round(operation_count / elapsed, 2),
            'description': 'POST request parameter setup with JSON (no network)'
        }
        
        # Benchmark 3: Manager Retrieval (SINGLETON lookup)
        operation_count = 50
        start = time.perf_counter()
        
        for _ in range(operation_count):
            _ = get_http_client_manager()
        
        elapsed = time.perf_counter() - start
        
        benchmark['operations']['manager_retrieval'] = {
            'operation_count': operation_count,
            'total_time_ms': round(elapsed * 1000, 3),
            'avg_time_ms': round((elapsed * 1000) / operation_count, 3),
            'ops_per_second': round(operation_count / elapsed, 2),
            'description': 'SINGLETON manager retrieval'
        }
        
        # Benchmark 4: Get Statistics
        operation_count = 200
        start = time.perf_counter()
        
        for _ in range(operation_count):
            _ = manager.get_stats()
        
        elapsed = time.perf_counter() - start
        
        benchmark['operations']['get_stats'] = {
            'operation_count': operation_count,
            'total_time_ms': round(elapsed * 1000, 3),
            'avg_time_ms': round((elapsed * 1000) / operation_count, 3),
            'ops_per_second': round(operation_count / elapsed, 2),
            'description': 'Statistics retrieval'
        }
        
        # Benchmark 5: Reset Operation
        operation_count = 10
        start = time.perf_counter()
        
        for _ in range(operation_count):
            manager.reset()
        
        elapsed = time.perf_counter() - start
        
        benchmark['operations']['reset'] = {
            'operation_count': operation_count,
            'total_time_ms': round(elapsed * 1000, 3),
            'avg_time_ms': round((elapsed * 1000) / operation_count, 3),
            'ops_per_second': round(operation_count / elapsed, 2),
            'description': 'Reset operation (recreates connection pool)'
        }
        
        # Calculate totals
        total_time = sum(op['total_time_ms'] for op in benchmark['operations'].values())
        total_ops = sum(op['operation_count'] for op in benchmark['operations'].values())
        
        benchmark['summary'] = {
            'total_operations': total_ops,
            'total_time_ms': round(total_time, 3),
            'avg_time_per_op_ms': round(total_time / total_ops, 3),
            'overall_ops_per_second': round((total_ops / total_time) * 1000, 2),
            'fastest_operation': min(
                benchmark['operations'].items(),
                key=lambda x: x[1]['avg_time_ms']
            )[0],
            'slowest_operation': max(
                benchmark['operations'].items(),
                key=lambda x: x[1]['avg_time_ms']
            )[0]
        }
        
        # Performance assessment
        avg_time = benchmark['summary']['avg_time_per_op_ms']
        if avg_time < 0.1:
            assessment = 'EXCELLENT - Sub-100μs per operation'
        elif avg_time < 1.0:
            assessment = 'GOOD - Sub-millisecond per operation'
        elif avg_time < 10.0:
            assessment = 'ACCEPTABLE - Single-digit milliseconds'
        else:
            assessment = 'SLOW - Consider optimization'
        
        benchmark['summary']['performance_assessment'] = assessment
        
        # Note about network operations
        benchmark['note'] = (
            'This benchmark tests HTTP client infrastructure only, '
            'not actual network performance. Real HTTP requests will be '
            'significantly slower due to network latency, DNS resolution, '
            'and remote server processing time.'
        )
        
    except Exception as e:
        benchmark['error'] = str(e)
        benchmark['error_type'] = type(e).__name__
    
    return benchmark


__all__ = [
    '_run_performance_benchmark',
    '_compare_dispatcher_modes',
    '_get_performance_report',
    '_benchmark_http_client_operations'
]

# EOF
