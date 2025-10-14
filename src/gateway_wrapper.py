"""
gateway_wrapper.py
Version: 2025.10.13.01
Description: Ultra-optimized generic gateway dispatcher with fast-path support

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

import importlib
import time
from typing import Any, Dict, Optional
from enum import Enum


# ===== CONFIGURATION =====

_FAST_PATH_ENABLED = True
_CACHE_IMPLEMENTATIONS = True
_IMPLEMENTATION_CACHE = {}


# ===== FAST PATH STATISTICS =====

_FAST_PATH_STATS = {
    'total_calls': 0,
    'cache_hits': 0,
    'cache_misses': 0,
    'fast_path_time_saved_ms': 0.0
}


# ===== GENERIC DISPATCHER =====

def execute_generic_operation(interface: Enum, operation: str, **kwargs) -> Any:
    """
    Ultra-optimized generic dispatcher with lazy loading and caching.
    
    Replaces 500+ lines of routing code with single generic implementation.
    Supports fast-path optimization for frequently called operations.
    
    Args:
        interface: GatewayInterface enum value
        operation: Operation name (e.g., 'get', 'set', 'log_info')
        **kwargs: Operation-specific parameters
    
    Returns:
        Operation result
    """
    global _FAST_PATH_STATS
    _FAST_PATH_STATS['total_calls'] += 1
    
    start_time = time.time() if _FAST_PATH_ENABLED else None
    
    # Build cache key
    cache_key = f"{interface.value}_{operation}"
    
    # Fast path: check implementation cache
    if _CACHE_IMPLEMENTATIONS and cache_key in _IMPLEMENTATION_CACHE:
        _FAST_PATH_STATS['cache_hits'] += 1
        impl_func = _IMPLEMENTATION_CACHE[cache_key]
        result = impl_func(**kwargs)
        
        if _FAST_PATH_ENABLED:
            elapsed_ms = (time.time() - start_time) * 1000
            _FAST_PATH_STATS['fast_path_time_saved_ms'] += (2.0 - elapsed_ms)
        
        return result
    
    # Slow path: load and cache implementation
    _FAST_PATH_STATS['cache_misses'] += 1
    
    try:
        # Dynamic module import
        core_module_name = f"{interface.value}_core"
        core_module = importlib.import_module(core_module_name)
        
        # Get implementation function
        impl_func_name = f"_execute_{operation}_implementation"
        impl_func = getattr(core_module, impl_func_name, None)
        
        if impl_func is None:
            raise AttributeError(f"Implementation {impl_func_name} not found in {core_module_name}")
        
        # Cache for future calls
        if _CACHE_IMPLEMENTATIONS:
            _IMPLEMENTATION_CACHE[cache_key] = impl_func
        
        # Execute
        return impl_func(**kwargs)
    
    except Exception as e:
        # Fallback error handling
        return None


# ===== BATCH OPERATIONS =====

def execute_batch_operations(operations: list) -> list:
    """
    Execute multiple operations in batch for optimization.
    
    Args:
        operations: List of dicts with 'interface', 'operation', 'kwargs'
    
    Returns:
        List of results
    """
    results = []
    
    for op in operations:
        try:
            interface = op.get('interface')
            operation = op.get('operation')
            kwargs = op.get('kwargs', {})
            
            result = execute_generic_operation(interface, operation, **kwargs)
            results.append({'success': True, 'result': result})
        except Exception as e:
            results.append({'success': False, 'error': str(e)})
    
    return results


# ===== STATISTICS AND MONITORING =====

def get_wrapper_stats() -> Dict[str, Any]:
    """
    Get gateway wrapper performance statistics.
    
    Returns:
        Dictionary with performance metrics
    """
    total_calls = _FAST_PATH_STATS['total_calls']
    cache_hits = _FAST_PATH_STATS['cache_hits']
    cache_misses = _FAST_PATH_STATS['cache_misses']
    
    hit_rate = (cache_hits / total_calls * 100) if total_calls > 0 else 0.0
    avg_time_saved = (_FAST_PATH_STATS['fast_path_time_saved_ms'] / cache_hits) if cache_hits > 0 else 0.0
    
    return {
        'total_calls': total_calls,
        'cache_hits': cache_hits,
        'cache_misses': cache_misses,
        'hit_rate_percent': round(hit_rate, 2),
        'avg_time_saved_ms': round(avg_time_saved, 3),
        'cached_implementations': len(_IMPLEMENTATION_CACHE)
    }


def clear_implementation_cache():
    """Clear the implementation function cache."""
    global _IMPLEMENTATION_CACHE
    _IMPLEMENTATION_CACHE.clear()


def reset_stats():
    """Reset wrapper statistics."""
    global _FAST_PATH_STATS
    _FAST_PATH_STATS = {
        'total_calls': 0,
        'cache_hits': 0,
        'cache_misses': 0,
        'fast_path_time_saved_ms': 0.0
    }


# ===== CONFIGURATION =====

def configure_wrapper(
    fast_path_enabled: Optional[bool] = None,
    cache_implementations: Optional[bool] = None
) -> Dict[str, bool]:
    """
    Configure gateway wrapper behavior.
    
    Args:
        fast_path_enabled: Enable/disable fast path optimization
        cache_implementations: Enable/disable implementation caching
    
    Returns:
        Current configuration
    """
    global _FAST_PATH_ENABLED, _CACHE_IMPLEMENTATIONS
    
    if fast_path_enabled is not None:
        _FAST_PATH_ENABLED = fast_path_enabled
    
    if cache_implementations is not None:
        _CACHE_IMPLEMENTATIONS = cache_implementations
        if not cache_implementations:
            clear_implementation_cache()
    
    return {
        'fast_path_enabled': _FAST_PATH_ENABLED,
        'cache_implementations': _CACHE_IMPLEMENTATIONS
    }


# ===== EXPORTED FUNCTIONS =====

__all__ = [
    'execute_generic_operation',
    'execute_batch_operations',
    'get_wrapper_stats',
    'clear_implementation_cache',
    'reset_stats',
    'configure_wrapper'
]

# EOF
