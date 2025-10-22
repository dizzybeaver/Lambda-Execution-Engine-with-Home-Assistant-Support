"""
debug_performance.py - Debug Performance Operations
Version: 2025.10.22.02
Description: Performance benchmarking operations for debug subsystem

CHANGELOG:
- 2025.10.22.02: Added WEBSOCKET and CIRCUIT_BREAKER interface benchmarks
  - Added _benchmark_websocket_operations (infrastructure overhead tests)
  - Added _benchmark_circuit_breaker_operations (manager operations)
  - Both test SINGLETON overhead and rate limiting impact
  - Focus on infrastructure, not external network/function calls

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


def _benchmark_websocket_operations(**kwargs) -> Dict[str, Any]:
    """
    Benchmark WEBSOCKET interface operations.
    
    Tests:
    - Manager retrieval overhead (50 ops)
    - Statistics retrieval (200 ops)
    - Reset operation (10 ops)
    - Rate limiting overhead (50 ops)
    
    Note: Does NOT benchmark actual WebSocket connections (external network dependency).
    Focuses on infrastructure overhead and internal operations.
    
    REF-IDs:
    - LESS-18: SINGLETON pattern overhead
    - LESS-21: Rate limiting overhead
    
    Returns:
        Benchmark results with timing analysis
    """
    from gateway import create_success_response, create_error_response
    import time
    
    results = {
        'interface': 'WEBSOCKET',
        'benchmarks': {},
        'total_operations': 0,
        'total_duration_ms': 0
    }
    
    try:
        from websocket_core import get_websocket_manager
        
        # Benchmark 1: Manager retrieval (SINGLETON overhead)
        iterations_1 = 50
        start = time.time()
        for _ in range(iterations_1):
            manager = get_websocket_manager()
        duration_1 = (time.time() - start) * 1000
        
        results['benchmarks']['manager_retrieval'] = {
            'iterations': iterations_1,
            'total_duration_ms': round(duration_1, 3),
            'avg_per_op_ms': round(duration_1 / iterations_1, 6),
            'ops_per_second': round(iterations_1 / (duration_1 / 1000), 2)
        }
        results['total_operations'] += iterations_1
        results['total_duration_ms'] += duration_1
        
        # Get manager for subsequent tests
        manager = get_websocket_manager()
        
        # Benchmark 2: Get statistics (200 ops)
        iterations_2 = 200
        start = time.time()
        for _ in range(iterations_2):
            stats = manager.get_stats()
        duration_2 = (time.time() - start) * 1000
        
        results['benchmarks']['get_stats'] = {
            'iterations': iterations_2,
            'total_duration_ms': round(duration_2, 3),
            'avg_per_op_ms': round(duration_2 / iterations_2, 6),
            'ops_per_second': round(iterations_2 / (duration_2 / 1000), 2)
        }
        results['total_operations'] += iterations_2
        results['total_duration_ms'] += duration_2
        
        # Benchmark 3: Reset operation (10 ops)
        iterations_3 = 10
        start = time.time()
        for _ in range(iterations_3):
            success = manager.reset()
        duration_3 = (time.time() - start) * 1000
        
        results['benchmarks']['reset'] = {
            'iterations': iterations_3,
            'total_duration_ms': round(duration_3, 3),
            'avg_per_op_ms': round(duration_3 / iterations_3, 6),
            'ops_per_second': round(iterations_3 / (duration_3 / 1000), 2)
        }
        results['total_operations'] += iterations_3
        results['total_duration_ms'] += duration_3
        
        # Benchmark 4: Rate limit checking (50 ops)
        iterations_4 = 50
        start = time.time()
        for _ in range(iterations_4):
            allowed = manager._check_rate_limit()
        duration_4 = (time.time() - start) * 1000
        
        results['benchmarks']['rate_limit_check'] = {
            'iterations': iterations_4,
            'total_duration_ms': round(duration_4, 3),
            'avg_per_op_ms': round(duration_4 / iterations_4, 6),
            'ops_per_second': round(iterations_4 / (duration_4 / 1000), 2)
        }
        results['total_operations'] += iterations_4
        results['total_duration_ms'] += duration_4
        
        # Overall statistics
        results['overall'] = {
            'total_operations': results['total_operations'],
            'total_duration_ms': round(results['total_duration_ms'], 3),
            'avg_per_op_ms': round(results['total_duration_ms'] / results['total_operations'], 6),
            'ops_per_second': round(results['total_operations'] / (results['total_duration_ms'] / 1000), 2)
        }
        
        # Performance assessment
        avg_op_time = results['overall']['avg_per_op_ms']
        if avg_op_time < 0.1:
            results['performance_rating'] = 'excellent'
        elif avg_op_time < 0.5:
            results['performance_rating'] = 'good'
        elif avg_op_time < 1.0:
            results['performance_rating'] = 'fair'
        else:
            results['performance_rating'] = 'needs_improvement'
        
        # Notes
        results['notes'] = [
            'Benchmarks test infrastructure overhead only',
            'Actual WebSocket operations depend on network conditions',
            'Use for comparing SINGLETON and rate limiting overhead',
            'Does not include external network latency'
        ]
        
        return create_success_response('WEBSOCKET operations benchmark complete', results)
        
    except Exception as e:
        return create_error_response(f'Benchmark failed: {str(e)}', 'BENCHMARK_FAILED')


def _benchmark_circuit_breaker_operations(**kwargs) -> Dict[str, Any]:
    """
    Benchmark CIRCUIT_BREAKER interface operations.
    
    Tests:
    - Manager retrieval overhead (50 ops)
    - Circuit breaker creation (100 ops)
    - get_all_states (100 ops)
    - get_stats (200 ops)
    - reset operation (10 ops)
    - Rate limiting overhead (50 ops)
    
    Note: Does NOT benchmark actual protected function calls.
    Focuses on infrastructure overhead and internal operations.
    
    REF-IDs:
    - LESS-18: SINGLETON pattern overhead
    - LESS-21: Rate limiting overhead
    
    Returns:
        Benchmark results with timing analysis
    """
    from gateway import create_success_response, create_error_response
    import time
    
    results = {
        'interface': 'CIRCUIT_BREAKER',
        'benchmarks': {},
        'total_operations': 0,
        'total_duration_ms': 0
    }
    
    try:
        from circuit_breaker_core import get_circuit_breaker_manager
        
        # Benchmark 1: Manager retrieval (SINGLETON overhead)
        iterations_1 = 50
        start = time.time()
        for _ in range(iterations_1):
            manager = get_circuit_breaker_manager()
        duration_1 = (time.time() - start) * 1000
        
        results['benchmarks']['manager_retrieval'] = {
            'iterations': iterations_1,
            'total_duration_ms': round(duration_1, 3),
            'avg_per_op_ms': round(duration_1 / iterations_1, 6),
            'ops_per_second': round(iterations_1 / (duration_1 / 1000), 2)
        }
        results['total_operations'] += iterations_1
        results['total_duration_ms'] += duration_1
        
        # Get manager for subsequent tests
        manager = get_circuit_breaker_manager()
        
        # Benchmark 2: Circuit breaker creation (100 ops)
        iterations_2 = 100
        start = time.time()
        for i in range(iterations_2):
            breaker = manager.get(f'benchmark_breaker_{i}', failure_threshold=5, timeout=60)
        duration_2 = (time.time() - start) * 1000
        
        results['benchmarks']['breaker_creation'] = {
            'iterations': iterations_2,
            'total_duration_ms': round(duration_2, 3),
            'avg_per_op_ms': round(duration_2 / iterations_2, 6),
            'ops_per_second': round(iterations_2 / (duration_2 / 1000), 2)
        }
        results['total_operations'] += iterations_2
        results['total_duration_ms'] += duration_2
        
        # Benchmark 3: get_all_states (100 ops)
        iterations_3 = 100
        start = time.time()
        for _ in range(iterations_3):
            states = manager.get_all_states()
        duration_3 = (time.time() - start) * 1000
        
        results['benchmarks']['get_all_states'] = {
            'iterations': iterations_3,
            'total_duration_ms': round(duration_3, 3),
            'avg_per_op_ms': round(duration_3 / iterations_3, 6),
            'ops_per_second': round(iterations_3 / (duration_3 / 1000), 2)
        }
        results['total_operations'] += iterations_3
        results['total_duration_ms'] += duration_3
        
        # Benchmark 4: Get statistics (200 ops)
        iterations_4 = 200
        start = time.time()
        for _ in range(iterations_4):
            stats = manager.get_stats()
        duration_4 = (time.time() - start) * 1000
        
        results['benchmarks']['get_stats'] = {
            'iterations': iterations_4,
            'total_duration_ms': round(duration_4, 3),
            'avg_per_op_ms': round(duration_4 / iterations_4, 6),
            'ops_per_second': round(iterations_4 / (duration_4 / 1000), 2)
        }
        results['total_operations'] += iterations_4
        results['total_duration_ms'] += duration_4
        
        # Benchmark 5: Reset operation (10 ops)
        iterations_5 = 10
        start = time.time()
        for _ in range(iterations_5):
            success = manager.reset()
            # Recreate test breakers after reset
            for i in range(10):
                manager.get(f'benchmark_breaker_{i}', failure_threshold=5, timeout=60)
        duration_5 = (time.time() - start) * 1000
        
        results['benchmarks']['reset'] = {
            'iterations': iterations_5,
            'total_duration_ms': round(duration_5, 3),
            'avg_per_op_ms': round(duration_5 / iterations_5, 6),
            'ops_per_second': round(iterations_5 / (duration_5 / 1000), 2)
        }
        results['total_operations'] += iterations_5
        results['total_duration_ms'] += duration_5
        
        # Benchmark 6: Rate limit checking (50 ops)
        iterations_6 = 50
        start = time.time()
        for _ in range(iterations_6):
            allowed = manager._check_rate_limit()
        duration_6 = (time.time() - start) * 1000
        
        results['benchmarks']['rate_limit_check'] = {
            'iterations': iterations_6,
            'total_duration_ms': round(duration_6, 3),
            'avg_per_op_ms': round(duration_6 / iterations_6, 6),
            'ops_per_second': round(iterations_6 / (duration_6 / 1000), 2)
        }
        results['total_operations'] += iterations_6
        results['total_duration_ms'] += duration_6
        
        # Overall statistics
        results['overall'] = {
            'total_operations': results['total_operations'],
            'total_duration_ms': round(results['total_duration_ms'], 3),
            'avg_per_op_ms': round(results['total_duration_ms'] / results['total_operations'], 6),
            'ops_per_second': round(results['total_operations'] / (results['total_duration_ms'] / 1000), 2)
        }
        
        # Performance assessment
        avg_op_time = results['overall']['avg_per_op_ms']
        if avg_op_time < 0.1:
            results['performance_rating'] = 'excellent'
        elif avg_op_time < 0.5:
            results['performance_rating'] = 'good'
        elif avg_op_time < 1.0:
            results['performance_rating'] = 'fair'
        else:
            results['performance_rating'] = 'needs_improvement'
        
        # Clean up test breakers
        manager.reset()
        
        # Notes
        results['notes'] = [
            'Benchmarks test infrastructure overhead only',
            'Does not benchmark protected function execution',
            'Use for comparing SINGLETON and rate limiting overhead',
            'Circuit breaker call() overhead depends on protected function'
        ]
        
        return create_success_response('CIRCUIT_BREAKER operations benchmark complete', results)
        
    except Exception as e:
        return create_error_response(f'Benchmark failed: {str(e)}', 'BENCHMARK_FAILED')


__all__ = [
    '_run_performance_benchmark',
    '_compare_dispatcher_modes',
    '_get_performance_report',
    '_benchmark_websocket_operations',
    '_benchmark_circuit_breaker_operations'
]

# EOF
