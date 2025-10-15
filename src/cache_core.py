"""
cache_core.py - Dynamic caching with dispatcher timing integration
Version: 2025.10.15.02
Description: Dynamic caching with LUGS integration and dispatcher timing (Phase 4 Task #7)

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

import os
import time
import threading
from typing import Dict, Any, Optional, Set, Callable
from dataclasses import dataclass
from enum import Enum

_USE_GENERIC_OPERATIONS = os.environ.get('USE_GENERIC_OPERATIONS', 'true').lower() == 'true'


# ===== CACHE OPERATION ENUM =====

class CacheOperation(Enum):
    """Enumeration of all cache operations."""
    GET = "get"
    SET = "set"
    DELETE = "delete"
    CLEAR = "clear"
    CLEANUP_EXPIRED = "cleanup_expired"
    GET_STATS = "get_stats"
    GET_MODULE_DEPENDENCIES = "get_module_dependencies"


# ===== CACHE ENTRY =====

@dataclass
class CacheEntry:
    """Cache entry with LUGS metadata."""
    value: Any
    timestamp: float
    ttl: float
    source_module: Optional[str] = None
    access_count: int = 0
    last_access: float = 0.0


# ===== LUGS INTEGRATED CACHE =====

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
    
    def set(self, key: str, value: Any, ttl: float = 300, source_module: Optional[str] = None) -> None:
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
            
            # Check expiration
            if current_time - entry.timestamp > entry.ttl:
                del self._cache[key]
                self._stats['cache_misses'] += 1
                self._stats['entries_expired'] += 1
                return None
            
            # Update access metadata
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


# ===== GENERIC OPERATION EXECUTION =====

def execute_cache_operation(operation: CacheOperation, *args, **kwargs):
    """Universal cache operation executor with dispatcher performance monitoring."""
    start_time = time.time()
    
    if not _USE_GENERIC_OPERATIONS:
        result = _execute_legacy_operation(operation, *args, **kwargs)
    else:
        result = _execute_generic_operation(operation, *args, **kwargs)
    
    duration_ms = (time.time() - start_time) * 1000
    _record_dispatcher_metric(operation, duration_ms)
    
    return result


def _execute_generic_operation(operation: CacheOperation, *args, **kwargs):
    """Execute cache operation using generic dispatcher."""
    if operation == CacheOperation.GET:
        key = args[0] if args else kwargs.get('key')
        return _cache_instance.get(key)
    elif operation == CacheOperation.SET:
        key = args[0] if args else kwargs.get('key')
        value = args[1] if len(args) > 1 else kwargs.get('value')
        ttl = args[2] if len(args) > 2 else kwargs.get('ttl', 300)
        source_module = kwargs.get('source_module')
        _cache_instance.set(key, value, ttl, source_module)
        return None
    elif operation == CacheOperation.DELETE:
        key = args[0] if args else kwargs.get('key')
        return _cache_instance.delete(key)
    elif operation == CacheOperation.CLEAR:
        return _cache_instance.clear()
    elif operation == CacheOperation.CLEANUP_EXPIRED:
        return _cache_instance.cleanup_expired()
    elif operation == CacheOperation.GET_STATS:
        return _cache_instance.get_stats()
    elif operation == CacheOperation.GET_MODULE_DEPENDENCIES:
        return _cache_instance.get_module_dependencies()
    
    return None


def _execute_legacy_operation(operation: CacheOperation, *args, **kwargs):
    """Legacy operation execution for rollback compatibility."""
    # Fallback to direct method calls
    if operation == CacheOperation.GET:
        return _cache_instance.get(args[0] if args else kwargs.get('key'))
    elif operation == CacheOperation.SET:
        return _cache_instance.set(
            args[0] if args else kwargs.get('key'),
            args[1] if len(args) > 1 else kwargs.get('value'),
            args[2] if len(args) > 2 else kwargs.get('ttl', 300),
            kwargs.get('source_module')
        )
    elif operation == CacheOperation.DELETE:
        return _cache_instance.delete(args[0] if args else kwargs.get('key'))
    elif operation == CacheOperation.CLEAR:
        return _cache_instance.clear()
    elif operation == CacheOperation.CLEANUP_EXPIRED:
        return _cache_instance.cleanup_expired()
    elif operation == CacheOperation.GET_STATS:
        return _cache_instance.get_stats()
    elif operation == CacheOperation.GET_MODULE_DEPENDENCIES:
        return _cache_instance.get_module_dependencies()
    
    return None


def _record_dispatcher_metric(operation: CacheOperation, duration_ms: float):
    """Record dispatcher performance metric using centralized METRICS operation (Phase 4 Task #7)."""
    try:
        from gateway import execute_operation, GatewayInterface
        execute_operation(
            GatewayInterface.METRICS,
            'record_dispatcher_timing',
            interface_name='CacheCore',
            operation_name=operation.value,
            duration_ms=duration_ms
        )
    except Exception:
        pass


# ===== CONVENIENCE FUNCTIONS =====

def cache_set(key: str, value: Any, ttl: float = 300, source_module: Optional[str] = None) -> None:
    """Set cache value with LUGS tracking."""
    execute_cache_operation(CacheOperation.SET, key, value, ttl, source_module=source_module)


def cache_get(key: str, default: Any = None) -> Optional[Any]:
    """Get cache value."""
    result = execute_cache_operation(CacheOperation.GET, key)
    return result if result is not None else default


def cache_delete(key: str) -> bool:
    """Delete cache entry."""
    return execute_cache_operation(CacheOperation.DELETE, key)


def cache_clear() -> int:
    """Clear all cache entries."""
    return execute_cache_operation(CacheOperation.CLEAR)


def cache_cleanup() -> int:
    """Clean up expired entries."""
    return execute_cache_operation(CacheOperation.CLEANUP_EXPIRED)


def cache_get_stats() -> Dict[str, Any]:
    """Get cache statistics."""
    return execute_cache_operation(CacheOperation.GET_STATS)


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


# ===== IMPLEMENTATION WRAPPERS =====

def _execute_get_implementation(key: str, default: Any = None, **kwargs) -> Optional[Any]:
    """Execute get operation."""
    result = execute_cache_operation(CacheOperation.GET, key, **kwargs)
    return result if result is not None else default


def _execute_set_implementation(key: str, value: Any, ttl: Optional[float] = None, source_module: Optional[str] = None, **kwargs) -> None:
    """Execute set operation."""
    ttl = ttl if ttl is not None else 300
    execute_cache_operation(CacheOperation.SET, key, value, ttl, source_module=source_module, **kwargs)


def _execute_delete_implementation(key: str, **kwargs) -> bool:
    """Execute delete operation."""
    return execute_cache_operation(CacheOperation.DELETE, key, **kwargs)


def _execute_clear_implementation(**kwargs) -> int:
    """Execute clear operation."""
    return execute_cache_operation(CacheOperation.CLEAR, **kwargs)


def _execute_cleanup_expired_implementation(**kwargs) -> int:
    """Execute cleanup expired operation."""
    return execute_cache_operation(CacheOperation.CLEANUP_EXPIRED, **kwargs)


def _execute_get_stats_implementation(**kwargs) -> Dict[str, Any]:
    """Execute get stats operation."""
    return execute_cache_operation(CacheOperation.GET_STATS, **kwargs)


def _execute_exists_implementation(key: str, **kwargs) -> bool:
    """Execute exists operation - legacy wrapper."""
    return execute_cache_operation(CacheOperation.GET, key, **kwargs) is not None


# ===== EXPORTS =====

__all__ = [
    'CacheOperation',
    'LUGSIntegratedCache',
    'execute_cache_operation',
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
    '_execute_clear_implementation',
    '_execute_cleanup_expired_implementation',
    '_execute_get_stats_implementation',
    '_execute_exists_implementation',
]

# EOF
