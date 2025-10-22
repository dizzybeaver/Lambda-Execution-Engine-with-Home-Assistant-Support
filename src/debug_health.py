"""
debug_health.py - Debug Health Check Operations
Version: 2025.10.14.01
Description: Health check operations for debug subsystem

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


def _check_cache_health(**kwargs) -> Dict[str, Any]:
    """
    Check cache subsystem health (CACHE Phase 3).
    
    Validates:
    - Cache manager available
    - Memory within bounds (< 80MB threshold)
    - Entry count reasonable (< 10,000 threshold)
    - Rate limiting stats
    - Eviction stats
    
    Returns:
        Dict with:
        - component: 'cache'
        - healthy: bool
        - issues: List[str]
        - stats: Dict with health metrics
    """
    try:
        # Import via gateway (SUGA pattern)
        from gateway import cache_get_stats
        
        stats = cache_get_stats()
        
        healthy = True
        issues = []
        
        # Check memory usage
        memory_bytes = stats.get('memory_bytes', 0)
        if memory_bytes > 80_000_000:  # 80MB threshold
            healthy = False
            issues.append(f"High memory: {memory_bytes/1024/1024:.1f}MB")
        
        # Check entry count
        entry_count = stats.get('size', 0)
        if entry_count > 10000:
            healthy = False
            issues.append(f"Too many entries: {entry_count}")
        
        # Check rate limiting
        rate_limited = stats.get('rate_limited_count', 0)
        if rate_limited > 100:
            issues.append(f"Rate limiting active: {rate_limited} requests dropped")
        
        return {
            'component': 'cache',
            'healthy': healthy,
            'issues': issues,
            'stats': {
                'entry_count': entry_count,
                'memory_bytes': memory_bytes,
                'memory_mb': stats.get('memory_mb', 0),
                'memory_utilization_percent': stats.get('memory_utilization_percent', 0),
                'rate_limited_count': rate_limited
            }
        }
    except Exception as e:
        return {
            'component': 'cache',
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
        'timestamp': '2025.10.14',
        'system_health': _diagnose_system_health(),
        'validation': {
            'architecture': _validate_system_architecture(),
            'imports': _validate_imports(),
            'gateway_routing': _validate_gateway_routing(),
            'registry_operations': _verify_registry_operations()
        },
        'stats': _get_system_stats(),
        'optimization': _get_optimization_stats(),
        'dispatcher_performance': dispatcher_stats
    }


__all__ = [
    '_check_component_health',
    '_check_gateway_health',
    '_check_cache_health',
    '_generate_health_report'
]

# EOF
