"""
debug_health.py - Debug Health Check Operations
Version: 2025.10.21.01
Description: Health check operations for debug subsystem
CHANGELOG:
- 2025.10.21.01: Added _check_metrics_health() for METRICS Phase 3

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
import sys


def _check_component_health(**kwargs) -> Dict[str, Any]:
    """Check component health."""
    try:
        from gateway import check_all_components
        return check_all_components()
    except ImportError:
        return {'success': False, 'error': 'Gateway not available'}


def _check_gateway_health(**kwargs) -> Dict[str, Any]:
    """Check gateway health."""
    try:
        from gateway import get_gateway_stats
        stats = get_gateway_stats()
        return {
            'success': True,
            'stats': stats,
            'healthy': stats.get('operations_count', 0) > 0
        }
    except ImportError:
        return {'success': False, 'error': 'Gateway not available'}


def _check_metrics_health(**kwargs) -> Dict[str, Any]:
    """
    Check metrics subsystem health.
    
    Validates:
    - Manager available
    - Memory within bounds (< 500KB)
    - Rate limiting working
    - Stats accessible
    - Unique metrics count reasonable (< 10,000)
    
    Returns:
        Dict with:
        - component: 'metrics'
        - healthy: bool
        - issues: list of problems
        - stats: performance metrics
        
    Example:
        result = _check_metrics_health()
        # {
        #     'component': 'metrics',
        #     'healthy': True,
        #     'issues': [],
        #     'stats': {
        #         'total_metrics': 1234,
        #         'memory_bytes': 450000,
        #         'rate_limited': 0
        #     }
        # }
    """
    try:
        from metrics_core import _MANAGER
        
        # Get current stats
        stats = _MANAGER.get_stats()
        
        # Calculate memory usage
        memory_bytes = sum([
            sys.getsizeof(_MANAGER._metrics),
            sys.getsizeof(_MANAGER._counters),
            sys.getsizeof(_MANAGER._gauges)
        ])
        
        healthy = True
        issues = []
        
        # Check memory threshold (500KB)
        if memory_bytes > 500_000:
            healthy = False
            issues.append(f"High memory: {memory_bytes/1024:.1f}KB")
        
        # Check unique metrics count (10,000 max)
        unique_count = stats.get('unique_metrics', 0)
        if unique_count > 10_000:
            healthy = False
            issues.append(f"Too many metrics: {unique_count}")
        
        # Check rate limiting working
        rate_limited = stats.get('rate_limited_count', 0)
        if rate_limited > 1000:
            issues.append(f"High rate limiting: {rate_limited} dropped")
        
        return {
            'component': 'metrics',
            'healthy': healthy,
            'issues': issues,
            'stats': {
                'total_metrics': stats.get('total_metrics', 0),
                'unique_metrics': unique_count,
                'memory_bytes': memory_bytes,
                'rate_limited': rate_limited
            }
        }
    except Exception as e:
        return {
            'component': 'metrics',
            'healthy': False,
            'error': str(e)
        }


def _generate_health_report(**kwargs) -> Dict[str, Any]:
    """Generate comprehensive health report with dispatcher metrics."""
    from debug.debug_diagnostics import _diagnose_system_health
    from debug.debug_validation import _validate_system_architecture, _validate_imports, _validate_gateway_routing
    from debug.debug_verification import _verify_registry_operations
    from debug.debug_stats import _get_system_stats, _get_optimization_stats, _get_dispatcher_stats
    
    try:
        dispatcher_stats = _get_dispatcher_stats()
    except:
        dispatcher_stats = {'error': 'dispatcher stats not available'}
    
    return {
        'timestamp': '2025.10.21',
        'system_health': _diagnose_system_health(),
        'validation': {
            'architecture': _validate_system_architecture(),
            'imports': _validate_imports(),
            'gateway_routing': _validate_gateway_routing(),
            'registry_operations': _verify_registry_operations()
        },
        'stats': _get_system_stats(),
        'optimization': _get_optimization_stats(),
        'dispatcher_performance': dispatcher_stats,
        'metrics_health': _check_metrics_health()
    }


__all__ = [
    '_check_component_health',
    '_check_gateway_health',
    '_check_metrics_health',
    '_generate_health_report'
]

# EOF
