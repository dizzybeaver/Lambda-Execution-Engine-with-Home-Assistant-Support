"""
debug_diagnostics.py - Debug Diagnostic Operations
Version: 2025.10.21.01
Description: System diagnostic operations for debug subsystem
CHANGELOG:
- 2025.10.21.01: Added _diagnose_metrics_performance() for METRICS Phase 3

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
import gc
import sys


def _diagnose_system_health(**kwargs) -> Dict[str, Any]:
    """Comprehensive system health diagnosis."""
    from debug.debug_health import _check_component_health, _check_gateway_health
    
    component_health = _check_component_health()
    gateway_health = _check_gateway_health()
    memory_info = _diagnose_memory()
    
    return {
        'success': True,
        'component_health': component_health,
        'gateway_health': gateway_health,
        'memory': memory_info
    }


def _diagnose_performance(**kwargs) -> Dict[str, Any]:
    """Performance diagnosis."""
    try:
        from gateway import get_gateway_stats
        gateway_stats = get_gateway_stats()
        
        return {
            'success': True,
            'gateway_operations': gateway_stats.get('operations_count', 0),
            'fast_path_enabled': gateway_stats.get('fast_path_enabled', False),
            'call_counts': gateway_stats.get('call_counts', {})
        }
    except:
        return {'success': False, 'error': 'Could not diagnose performance'}


def _diagnose_memory(**kwargs) -> Dict[str, Any]:
    """Memory usage diagnosis."""
    gc_stats = gc.get_stats() if hasattr(gc, 'get_stats') else []
    
    return {
        'success': True,
        'objects': len(gc.get_objects()),
        'garbage': len(gc.garbage),
        'collections': gc.get_count()
    }


def _diagnose_metrics_performance(**kwargs) -> Dict[str, Any]:
    """
    Deep performance diagnostics for METRICS interface.
    
    Analyzes:
    - Hot metrics (most frequent)
    - Memory breakdown per metric
    - Slow operations
    - Optimization recommendations
    
    Returns:
        Dict with:
        - success: bool
        - hot_metrics: list of (name, count) tuples
        - largest_metrics: list of (name, bytes) tuples
        - total_memory_bytes: int
        - recommendations: list of optimization suggestions
        
    Example:
        result = _diagnose_metrics_performance()
        # {
        #     'success': True,
        #     'hot_metrics': [('operation.count', 5000), ...],
        #     'largest_metrics': [('http.requests', 128000), ...],
        #     'total_memory_bytes': 450000,
        #     'recommendations': [
        #         'Fast path candidates: operation.count, cache.hit',
        #         'High memory (450KB), consider limits'
        #     ]
        # }
    """
    try:
        from metrics_core import _MANAGER
        
        # Analyze metric distribution (frequency)
        metric_sizes = {
            name: len(values)
            for name, values in _MANAGER._metrics.items()
        }
        
        # Top 10 hot metrics (by call count)
        hot_metrics = sorted(
            metric_sizes.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        # Memory analysis per metric
        memory_per_metric = {
            name: sys.getsizeof(values)
            for name, values in _MANAGER._metrics.items()
        }
        
        # Top 10 largest metrics (by memory)
        largest = sorted(
            memory_per_metric.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        total_memory = sum(memory_per_metric.values())
        
        # Generate optimization recommendations
        recommendations = []
        
        # Recommend fast path for hot metrics
        if hot_metrics:
            top_3 = ', '.join(m[0] for m in hot_metrics[:3])
            recommendations.append(
                f"Fast path candidates: {top_3}"
            )
        
        # Memory warning
        if total_memory > 1_000_000:
            recommendations.append(
                f"High memory ({total_memory/1024:.1f}KB), consider limits"
            )
        
        # Check for metrics with excessive value counts
        excessive = [
            name for name, count in metric_sizes.items()
            if count > 1000
        ]
        if excessive:
            recommendations.append(
                f"Metrics exceeding 1000 values: {len(excessive)} metrics"
            )
        
        # Check for large individual metrics
        large_metrics = [
            name for name, size in memory_per_metric.items()
            if size > 100_000
        ]
        if large_metrics:
            recommendations.append(
                f"Large metrics (>100KB): {', '.join(large_metrics[:3])}"
            )
        
        return {
            'success': True,
            'hot_metrics': hot_metrics,
            'largest_metrics': largest,
            'total_memory_bytes': total_memory,
            'unique_metrics': len(metric_sizes),
            'recommendations': recommendations
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


__all__ = [
    '_diagnose_system_health',
    '_diagnose_performance',
    '_diagnose_memory',
    '_diagnose_metrics_performance'
]

# EOF
