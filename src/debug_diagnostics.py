"""
debug_diagnostics.py - Debug Diagnostic Operations
Version: 2025.10.14.01
Description: System diagnostic operations for debug subsystem

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


def _diagnose_cache_performance(**kwargs) -> Dict[str, Any]:
    """
    Deep performance diagnostics for cache subsystem (CACHE Phase 3).
    
    Analysis:
    - Memory distribution analysis
    - Entry size analysis
    - TTL distribution
    - Module dependency mapping
    - Optimization recommendations
    
    Returns:
        Dict with:
        - success: bool
        - memory_analysis: Dict
        - module_dependencies: Set[str]
        - recommendations: List[str]
    """
    try:
        from gateway import cache_get_stats, cache_get_module_dependencies
        
        stats = cache_get_stats()
        modules = cache_get_module_dependencies()
        
        # Memory analysis
        memory_bytes = stats.get('memory_bytes', 0)
        memory_mb = stats.get('memory_mb', 0)
        memory_utilization = stats.get('memory_utilization_percent', 0)
        max_mb = stats.get('max_mb', 100)
        
        # Generate recommendations
        recommendations = []
        
        # Memory recommendations
        if memory_utilization > 80:
            recommendations.append(
                f"High memory utilization ({memory_utilization:.1f}%), consider increasing MAX_CACHE_BYTES"
            )
        
        if memory_mb > 50:
            recommendations.append(
                f"Cache using {memory_mb:.1f}MB, monitor for memory pressure"
            )
        
        # Entry count recommendations
        entry_count = stats.get('size', 0)
        if entry_count > 5000:
            recommendations.append(
                f"High entry count ({entry_count}), consider shorter TTL or cleanup"
            )
        
        # Rate limiting recommendations
        rate_limited = stats.get('rate_limited_count', 0)
        if rate_limited > 0:
            recommendations.append(
                f"Rate limiting active ({rate_limited} drops), possible DoS or bug"
            )
        
        # Module dependencies
        if len(modules) > 10:
            recommendations.append(
                f"Many module dependencies ({len(modules)}), LUGS may unload frequently"
            )
        
        return {
            'success': True,
            'memory_analysis': {
                'current_mb': memory_mb,
                'max_mb': max_mb,
                'utilization_percent': memory_utilization,
                'entry_count': entry_count
            },
            'module_dependencies': list(modules),
            'module_count': len(modules),
            'rate_limited_count': rate_limited,
            'recommendations': recommendations if recommendations else ['Cache healthy, no optimization needed']
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
    '_diagnose_cache_performance'
]

# EOF
