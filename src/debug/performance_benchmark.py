"""
Performance Benchmark - Measure Interface Performance
Version: 2025.09.29.01
Daily Revision: 001
"""

import time
from typing import Dict, Callable, Any
from gateway import (
    cache_get, cache_set,
    log_info,
    validate_request,
    record_metric,
    get_singleton,
    format_response,
    get_gateway_stats
)

def benchmark_operation(name: str, operation: Callable, iterations: int = 1000, **kwargs) -> Dict[str, Any]:
    """Benchmark an operation."""
    times = []
    
    for _ in range(iterations):
        start = time.perf_counter()
        try:
            operation(**kwargs)
        except Exception:
            pass
        end = time.perf_counter()
        times.append(end - start)
    
    total_time = sum(times)
    avg_time = total_time / iterations
    min_time = min(times)
    max_time = max(times)
    
    return {
        'operation': name,
        'iterations': iterations,
        'total_time_ms': total_time * 1000,
        'avg_time_ms': avg_time * 1000,
        'min_time_ms': min_time * 1000,
        'max_time_ms': max_time * 1000,
        'ops_per_second': 1 / avg_time if avg_time > 0 else 0
    }

def benchmark_cache():
    """Benchmark cache operations."""
    results = {}
    
    results['cache_set'] = benchmark_operation(
        'cache_set',
        cache_set,
        iterations=1000,
        key='bench_key',
        value='bench_value'
    )
    
    cache_set('bench_key', 'bench_value')
    results['cache_get'] = benchmark_operation(
        'cache_get',
        cache_get,
        iterations=1000,
        key='bench_key'
    )
    
    return results

def benchmark_logging():
    """Benchmark logging operations."""
    results = {}
    
    results['log_info'] = benchmark_operation(
        'log_info',
        log_info,
        iterations=100,
        message='Benchmark message'
    )
    
    return results

def benchmark_security():
    """Benchmark security operations."""
    results = {}
    
    request = {'requestType': 'test', 'data': 'value'}
    results['validate_request'] = benchmark_operation(
        'validate_request',
        validate_request,
        iterations=1000,
        request=request
    )
    
    return results

def benchmark_metrics():
    """Benchmark metrics operations."""
    results = {}
    
    results['record_metric'] = benchmark_operation(
        'record_metric',
        record_metric,
        iterations=100,
        name='bench_metric',
        value=100.0
    )
    
    return results

def benchmark_utility():
    """Benchmark utility operations."""
    results = {}
    
    results['format_response'] = benchmark_operation(
        'format_response',
        format_response,
        iterations=1000,
        status_code=200,
        body={'message': 'success'}
    )
    
    return results

def run_all_benchmarks() -> Dict[str, Any]:
    """Run all benchmarks and collect results."""
    benchmarks = {
        'cache': benchmark_cache(),
        'logging': benchmark_logging(),
        'security': benchmark_security(),
        'metrics': benchmark_metrics(),
        'utility': benchmark_utility()
    }
    
    gateway_stats = get_gateway_stats()
    
    return {
        'benchmarks': benchmarks,
        'gateway_stats': gateway_stats
    }

def analyze_performance(results: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze performance results."""
    all_operations = []
    
    for category, ops in results['benchmarks'].items():
        for op_name, metrics in ops.items():
            all_operations.append({
                'category': category,
                'operation': op_name,
                'avg_time_ms': metrics['avg_time_ms'],
                'ops_per_second': metrics['ops_per_second']
            })
    
    all_operations.sort(key=lambda x: x['avg_time_ms'])
    
    fastest = all_operations[:3]
    slowest = all_operations[-3:]
    
    return {
        'fastest_operations': fastest,
        'slowest_operations': slowest,
        'total_operations': len(all_operations)
    }

#EOF
