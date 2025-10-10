"""
cache_core.py - LUGS-Integrated Caching System
Version: 2025.10.09.01
Description: Dynamic caching with LUGS module dependency tracking

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
import threading
from typing import Dict, Any, Optional, Callable, Set
from dataclasses import dataclass


@dataclass
class CacheEntry:
    """Cache entry with LUGS metadata."""
    value: Any
    timestamp: float
    ttl: float
    source_module: Optional[str] = None
    access_count: int = 0
    last_access: float = 0.0


class LUGSIntegratedCache:
    """Cache with LUGS module dependency tracking."""
    
    def __init__(self):
        self._lock = threading.Lock()
        self._cache: Dict[str, CacheEntry] = {}
        self._stats = {
            'total_sets': 0,
            'total_gets': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'lugs_prevented_unload': 0,
            'entries_expired': 0
        }
    
    def set(
        self,
        key: str,
        value: Any,
        ttl: float = 300,
        source_module: Optional[str] = None
    ) -> None:
        """Set cache value with LUGS tracking."""
        current_time = time.time()
        
        with self._lock:
            entry = CacheEntry(
                value=value,
                timestamp=current_time,
                ttl=ttl,
                source_module=source_module,
                access_count=0,
                last_access=current_time
            )
            
            self._cache[key] = entry
            self._stats['total_sets'] += 1
        
        if source_module:
            try:
                from gateway import add_cache_module_dependency
                add_cache_module_dependency(key, source_module)
            except ImportError:
                pass
    
    def get(self, key: str) -> Optional[Any]:
        """Get cache value with LUGS awareness."""
        current_time = time.time()
        
        with self._lock:
            self._stats['total_gets'] += 1
            
            if key not in self._cache:
                self._stats['cache_misses'] += 1
                return None
            
            entry = self._cache[key]
            
            if current_time - entry.timestamp > entry.ttl:
                del self._cache[key]
                self._stats['cache_misses'] += 1
                self._stats['entries_expired'] += 1
                return None
            
            entry.access_count += 1
            entry.last_access = current_time
            self._stats['cache_hits'] += 1
            
            return entry.value
    
    def delete(self, key: str) -> bool:
        """Delete cache entry."""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False
    
    def clear(self) -> int:
        """Clear all cache entries."""
        with self._lock:
            count = len(self._cache)
            self._cache.clear()
            return count
    
    def cleanup_expired(self) -> int:
        """Clean up expired entries."""
        current_time = time.time()
        expired_keys = []
        
        with self._lock:
            for key, entry in self._cache.items():
                if current_time - entry.timestamp > entry.ttl:
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self._cache[key]
            
            self._stats['entries_expired'] += len(expired_keys)
        
        return len(expired_keys)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self._lock:
            stats = self._stats.copy()
            stats.update({
                'entries_count': len(self._cache),
                'cache_hit_rate': (
                    self._stats['cache_hits'] / max(self._stats['total_gets'], 1) * 100
                ) if self._stats['total_gets'] > 0 else 0
            })
        
        return stats
    
    def get_module_dependencies(self) -> Dict[str, Set[str]]:
        """Get all cache entries by source module."""
        dependencies = {}
        
        with self._lock:
            for key, entry in self._cache.items():
                if entry.source_module:
                    if entry.source_module not in dependencies:
                        dependencies[entry.source_module] = set()
                    dependencies[entry.source_module].add(key)
        
        return dependencies


_cache_instance = LUGSIntegratedCache()


# ===== CONVENIENCE FUNCTIONS =====

def cache_set(key: str, value: Any, ttl: float = 300, source_module: Optional[str] = None) -> None:
    """Set cache value with LUGS tracking."""
    _cache_instance.set(key, value, ttl, source_module)


def cache_get(key: str) -> Optional[Any]:
    """Get cache value."""
    return _cache_instance.get(key)


def cache_delete(key: str) -> bool:
    """Delete cache entry."""
    return _cache_instance.delete(key)


def cache_clear() -> int:
    """Clear all cache entries."""
    return _cache_instance.clear()


def cache_cleanup() -> int:
    """Clean up expired entries."""
    return _cache_instance.cleanup_expired()


def cache_get_stats() -> Dict[str, Any]:
    """Get cache statistics."""
    return _cache_instance.get_stats()


def cache_operation_result(
    operation_name: str,
    func: Callable,
    ttl: int = 300,
    cache_key_prefix: str = "",
    source_module: Optional[str] = None
) -> Any:
    """Cache operation result with LUGS tracking."""
    cache_key = f"{cache_key_prefix}_{operation_name}" if cache_key_prefix else operation_name
    
    cached = cache_get(cache_key)
    if cached is not None:
        try:
            from gateway import get_lugs_manager
            manager = get_lugs_manager()
            manager._stats['cache_hit_no_load'] += 1
        except ImportError:
            pass
        
        return cached
    
    result = func()
    
    cache_set(cache_key, result, ttl, source_module)
    
    return result


# ===== GATEWAY IMPLEMENTATION FUNCTIONS =====

def _execute_get_implementation(key: str, default: Any = None) -> Optional[Any]:
    """Execute cache get operation."""
    result = _cache_instance.get(key)
    return result if result is not None else default


def _execute_set_implementation(key: str, value: Any, ttl: Optional[float] = None) -> None:
    """Execute cache set operation."""
    _cache_instance.set(key, value, ttl or 300)


def _execute_delete_implementation(key: str) -> bool:
    """Execute cache delete operation."""
    return _cache_instance.delete(key)


def _execute_clear_implementation() -> int:
    """Execute cache clear operation."""
    return _cache_instance.clear()


__all__ = [
    'LUGSIntegratedCache',
    'cache_set',
    'cache_get',
    'cache_delete',
    'cache_clear',
    'cache_cleanup',
    'cache_get_stats',
    'cache_operation_result',
    '_execute_get_implementation',
    '_execute_set_implementation',
    '_execute_delete_implementation',
    '_execute_clear_implementation'
]

# EOF
