"""
performance_benchmark.py
Version: 2025.10.13.01
Description: Performance benchmarking utilities for optimization validation

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

import time
from typing import Dict, Any, Callable, List
from gateway import execute_operation, GatewayInterface


# ===== BENCHMARK UTILITIES =====

def benchmark_operation(func: Callable, iterations: int = 1000, warmup: int = 100) -> Dict[str, Any]:
    """
    Benchmark a function's performance.
    
    Args:
        func: Function to benchmark
        iterations: Number of iterations
        warmup: Warmup iterations
    
    Returns:
        Benchmark results
    """
    # Warmup
    for _ in range(warmup):
        try:
            func()
        except:
            pass
    
    # Benchmark
    times = []
    errors = 0
    
    for _ in range(iterations):
        start = time.time()
        try:
            func()
            elapsed_ms = (time.time() - start) * 1000
            times.append(elapsed_ms)
        except:
            errors += 1
    
    if not times:
        return {
            'error': 'All iterations failed',
            'errors': errors
        }
    
    times.sort()
    
    return {
        'iterations': iterations,
        'successful': len(times),
        'errors': errors,
        'min_ms': round(min(times), 3),
        'max_ms': round(max(times), 3),
        'avg_ms': round(sum(times) / len(times), 3),
        'median_ms': round(times[len(times) // 2], 3),
        'p95_ms': round(times[int(len(times) * 0.95)], 3),
        'p99_ms': round(times[int(len(times) * 0.99)], 3)
    }


# ===== GATEWAY BENCHMARKS =====

def benchmark_gateway_routing() -> Dict[str, Any]:
    """Benchmark gateway routing performance."""
    
    def cache_get():
        execute_operation(GatewayInterface.CACHE, 'get', key='benchmark_key')
    
    return benchmark_operation(cache_get, iterations=1000)


def benchmark_gateway_wrapper() -> Dict[str, Any]:
    """Benchmark gateway wrapper performance."""
    try:
        from gateway_wrapper import execute_generic_operation
        
        def wrapper_cache_get():
            execute_generic_operation(GatewayInterface.CACHE, 'get', key='benchmark_key')
        
        return benchmark_operation(wrapper_cache_get, iterations=1000)
    
    except ImportError:
        return {'error': 'gateway_wrapper not available'}


def benchmark_fast_path() -> Dict[str, Any]:
    """Benchmark fast-path optimizer performance."""
    try:
        from fast_path_optimizer import execute_fast_path
        
        def test_func():
            return True
        
        def fast_path_call():
            execute_fast_path('benchmark_op', test_func)
        
        return benchmark_operation(fast_path_call, iterations=1000)
    
    except ImportError:
        return {'error': 'fast_path_optimizer not available'}


# ===== BATCH BENCHMARKS =====

def benchmark_batch_operations() -> Dict[str, Any]:
    """Benchmark batch operation performance."""
    try:
        from batch_operations import execute_batch
        
        operations = [
            {'interface': GatewayInterface.CACHE, 'operation': 'get', 'params': {'key': f'key{i}'}}
            for i in range(10)
        ]
        
        def batch_exec():
            execute_batch(operations)
        
        return benchmark_operation(batch_exec, iterations=100)
    
    except ImportError:
        return {'error': 'batch_operations not available'}


def benchmark_batch_vs_sequential() -> Dict[str, Any]:
    """Compare batch vs sequential performance."""
    try:
        from batch_operations import execute_batch
        
        # Sequential
        def sequential():
            for i in range(10):
                execute_operation(GatewayInterface.CACHE, 'get', key=f'key{i}')
        
        # Batch
        operations = [
            {'interface': GatewayInterface.CACHE, 'operation': 'get', 'params': {'key': f'key{i}'}}
            for i in range(10)
        ]
        
        def batch():
            execute_batch(operations)
        
        sequential_results = benchmark_operation(sequential, iterations=100)
        batch_results = benchmark_operation(batch, iterations=100)
        
        speedup = sequential_results['avg_ms'] / batch_results['avg_ms'] if batch_results.get('avg_ms') else 0
        
        return {
            'sequential': sequential_results,
            'batch': batch_results,
            'speedup': round(speedup, 2)
        }
    
    except ImportError:
        return {'error': 'batch_operations not available'}


# ===== CACHE BENCHMARKS =====

def benchmark_cache_operations() -> Dict[str, Any]:
    """Benchmark cache operations."""
    
    results = {}
    
    # GET
    def cache_get():
        execute_operation(GatewayInterface.CACHE, 'get', key='benchmark_key')
    
    results['get'] = benchmark_operation(cache_get, iterations=1000)
    
    # SET
    def cache_set():
        execute_operation(GatewayInterface.CACHE, 'set', key='benchmark_key', value='value', ttl=300)
    
    results['set'] = benchmark_operation(cache_set, iterations=1000)
    
    # DELETE
    def cache_delete():
        execute_operation(GatewayInterface.CACHE, 'delete', key='benchmark_key')
    
    results['delete'] = benchmark_operation(cache_delete, iterations=1000)
    
    return results


# ===== METRICS BENCHMARKS =====

def benchmark_metrics_operations() -> Dict[str, Any]:
    """Benchmark metrics operations."""
    
    results = {}
    
    # Record metric
    def record_metric():
        execute_operation(GatewayInterface.METRICS, 'record_metric', name='benchmark_metric', value=1.0)
    
    results['record_metric'] = benchmark_operation(record_metric, iterations=1000)
    
    # Increment counter
    def increment_counter():
        execute_operation(GatewayInterface.METRICS, 'increment_counter', name='benchmark_counter', value=1)
    
    results['increment_counter'] = benchmark_operation(increment_counter, iterations=1000)
    
    return results


# ===== LOGGING BENCHMARKS =====

def benchmark_logging_operations() -> Dict[str, Any]:
    """Benchmark logging operations."""
    
    results = {}
    
    # Log info
    def log_info():
        execute_operation(GatewayInterface.LOGGING, 'log_info', message='Benchmark message')
    
    results['log_info'] = benchmark_operation(log_info, iterations=1000)
    
    # Log error
    def log_error():
        execute_operation(GatewayInterface.LOGGING, 'log_error', message='Benchmark error')
    
    results['log_error'] = benchmark_operation(log_error, iterations=1000)
    
    return results


# ===== OPTIMIZATION COMPARISON =====

def compare_optimizations() -> Dict[str, Any]:
    """Compare performance before and after optimizations."""
    
    results = {
        'gateway_routing': {},
        'fast_path': {},
        'batch_operations': {}
    }
    
    # Gateway routing
    results['gateway_routing']['standard'] = benchmark_gateway_routing()
    results['gateway_routing']['wrapper'] = benchmark_gateway_wrapper()
    
    if 'avg_ms' in results['gateway_routing']['standard'] and 'avg_ms' in results['gateway_routing']['wrapper']:
        improvement = (
            (results['gateway_routing']['standard']['avg_ms'] - 
             results['gateway_routing']['wrapper']['avg_ms']) /
            results['gateway_routing']['standard']['avg_ms'] * 100
        )
        results['gateway_routing']['improvement_percent'] = round(improvement, 2)
    
    # Fast-path
    results['fast_path']['benchmark'] = benchmark_fast_path()
    
    # Batch operations
    batch_comparison = benchmark_batch_vs_sequential()
    results['batch_operations'] = batch_comparison
    
    return results


# ===== COMPREHENSIVE BENCHMARK =====

def run_comprehensive_benchmark() -> Dict[str, Any]:
    """Run comprehensive performance benchmark suite."""
    
    results = {
        'timestamp': time.time(),
        'benchmarks': {}
    }
    
    # Gateway benchmarks
    results['benchmarks']['gateway_routing'] = benchmark_gateway_routing()
    results['benchmarks']['gateway_wrapper'] = benchmark_gateway_wrapper()
    results['benchmarks']['fast_path'] = benchmark_fast_path()
    
    # Component benchmarks
    results['benchmarks']['cache'] = benchmark_cache_operations()
    results['benchmarks']['metrics'] = benchmark_metrics_operations()
    results['benchmarks']['logging'] = benchmark_logging_operations()
    
    # Batch benchmarks
    results['benchmarks']['batch'] = benchmark_batch_operations()
    results['benchmarks']['batch_vs_sequential'] = benchmark_batch_vs_sequential()
    
    # Optimization comparison
    results['optimization_comparison'] = compare_optimizations()
    
    return results


# ===== REPORT GENERATION =====

def generate_benchmark_report(results: Dict[str, Any]) -> str:
    """
    Generate human-readable benchmark report.
    
    Args:
        results: Benchmark results
    
    Returns:
        Formatted report string
    """
    lines = [
        "=" * 80,
        "PERFORMANCE BENCHMARK REPORT",
        "=" * 80,
        ""
    ]
    
    if 'benchmarks' in results:
        lines.append("COMPONENT BENCHMARKS:")
        lines.append("-" * 80)
        
        for component, data in results['benchmarks'].items():
            if isinstance(data, dict) and 'avg_ms' in data:
                lines.append(f"\n{component.upper()}:")
                lines.append(f"  Average: {data['avg_ms']}ms")
                lines.append(f"  Median: {data.get('median_ms', 'N/A')}ms")
                lines.append(f"  P95: {data.get('p95_ms', 'N/A')}ms")
                lines.append(f"  P99: {data.get('p99_ms', 'N/A')}ms")
    
    if 'optimization_comparison' in results:
        lines.append("\n" + "=" * 80)
        lines.append("OPTIMIZATION IMPACT:")
        lines.append("-" * 80)
        
        comp = results['optimization_comparison']
        
        if 'gateway_routing' in comp and 'improvement_percent' in comp['gateway_routing']:
            improvement = comp['gateway_routing']['improvement_percent']
            lines.append(f"\nGateway Wrapper: {improvement}% performance improvement")
        
        if 'batch_operations' in comp and 'speedup' in comp['batch_operations']:
            speedup = comp['batch_operations']['speedup']
            lines.append(f"Batch Operations: {speedup}x faster than sequential")
    
    lines.append("\n" + "=" * 80)
    
    return "\n".join(lines)


# ===== EXPORTED FUNCTIONS =====

__all__ = [
    'benchmark_operation',
    'benchmark_gateway_routing',
    'benchmark_gateway_wrapper',
    'benchmark_fast_path',
    'benchmark_batch_operations',
    'benchmark_batch_vs_sequential',
    'benchmark_cache_operations',
    'benchmark_metrics_operations',
    'benchmark_logging_operations',
    'compare_optimizations',
    'run_comprehensive_benchmark',
    'generate_benchmark_report'
]

# EOF
