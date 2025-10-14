"""
debug/debug_diagnostics.py - Debug Diagnostic Operations
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

from debug import Dict, Any, gc


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


__all__ = [
    '_diagnose_system_health',
    '_diagnose_performance',
    '_diagnose_memory'
]

# EOF
