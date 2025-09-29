"""
cache_core.py - Core Cache Implementation for SUGA
Version: 2025.09.29.03
Daily Revision: 01

REVOLUTIONARY ARCHITECTURE - Optimized for Single Universal Gateway
FREE TIER COMPLIANCE: 100% - Memory optimized within free tier limits
"""

import time
import json
from typing import Any, Dict, Optional, List
from collections import OrderedDict
from dataclasses import dataclass, field

@dataclass
class CacheEntry:
    """Cache entry with metadata."""
    value: Any
    timestamp: float
    ttl: int
    access_count: int = 0
    last_access: float = 0
    
    def is_expired(self) -> bool:
        """Check if entry is expired."""
        if self.ttl <= 0:
            return False
        return time.time() - self.timestamp > self.ttl
    
    def touch(self) -> None:
        """Update access metadata."""
        self.access_count += 1
        self.last_access = time.time()

@dataclass
class CacheStats:
    """Cache statistics."""
    hits: int = 0
    misses: int = 0
    sets: int = 0
    deletes: int = 0
    evictions: int = 0
    expired: int = 0
    total_size: int = 0
    memory_bytes: int = 0

_CACHE_NAMESPACES: Dict[str, OrderedDict] = {}
_CACHE_STATS: Dict[str, CacheStats] = {}
_CACHE_LOCK = None

def _get_lock():
    """Get or create cache lock."""
    global _CACHE_LOCK
    if _CACHE_LOCK is None:
        import threading
        _CACHE_LOCK = threading.RLock()
    return _CACHE_LOCK

def _get_namespace(namespace: str) -> OrderedDict:
    """Get or create cache namespace."""
    if namespace not in _CACHE_NAMESPACES:
        _CACHE_NAMESPACES[namespace] = OrderedDict()
        _CACHE_STATS[namespace] = CacheStats()
    return _CACHE_NAMESPACES[namespace]

def _get_stats(namespace: str) -> CacheStats:
    """Get namespace statistics."""
    if namespace not in _CACHE_STATS:
        _CACHE_STATS[namespace] = CacheStats()
    return _CACHE_STATS[namespace]

def _evict_expired(namespace: str, max_size: int = 1000) -> int:
    """Evict expired entries and enforce size limit."""
    cache = _get_namespace(namespace)
    stats = _get_stats(namespace)
    
    expired_keys = []
    for key, entry in cache.items():
        if entry.is_expired():
            expired_keys.append(key)
    
    for key in expired_keys:
        del cache[key]
        stats.expired += 1
    
    while len(cache) > max_size:
        cache.popitem(last=False)
        stats.evictions += 1
    
    stats.total_size = len(cache)
    return len(expired_keys)

def cache_get(key: str, default: Any = None, namespace: str = "default") -> Any:
    """Get value from cache."""
    with _get_lock():
        cache = _get_namespace(namespace)
        stats = _get_stats(namespace)
        
        if key in cache:
            entry = cache[key]
            if not entry.is_expired():
                entry.touch()
                cache.move_to_end(key)
                stats.hits += 1
                return entry.value
            else:
                del cache[key]
                stats.expired += 1
        
        stats.misses += 1
        return default

def cache_set(
    key: str,
    value: Any,
    ttl: Optional[int] = None,
    namespace: str = "default"
) -> bool:
    """Set value in cache."""
    with _get_lock():
        cache = _get_namespace(namespace)
        stats = _get_stats(namespace)
        
        if ttl is None:
            ttl = 300
        
        entry = CacheEntry(
            value=value,
            timestamp=time.time(),
            ttl=ttl
        )
        
        cache[key] = entry
        cache.move_to_end(key)
        stats.sets += 1
        stats.total_size = len(cache)
        
        _evict_expired(namespace)
        
        return True

def cache_delete(key: str, namespace: str = "default") -> bool:
    """Delete value from cache."""
    with _get_lock():
        cache = _get_namespace(namespace)
        stats = _get_stats(namespace)
        
        if key in cache:
            del cache[key]
            stats.deletes += 1
            stats.total_size = len(cache)
            return True
        
        return False

def cache_clear(namespace: str = "default") -> int:
    """Clear cache namespace."""
    with _get_lock():
        cache = _get_namespace(namespace)
        count = len(cache)
        cache.clear()
        
        stats = _get_stats(namespace)
        stats.total_size = 0
        
        return count

def cache_exists(key: str, namespace: str = "default") -> bool:
    """Check if key exists in cache."""
    with _get_lock():
        cache = _get_namespace(namespace)
        
        if key in cache:
            entry = cache[key]
            if not entry.is_expired():
                return True
            else:
                del cache[key]
                _get_stats(namespace).expired += 1
        
        return False

def cache_keys(namespace: str = "default") -> List[str]:
    """Get all keys in namespace."""
    with _get_lock():
        cache = _get_namespace(namespace)
        return list(cache.keys())

def cache_size(namespace: str = "default") -> int:
    """Get cache size."""
    with _get_lock():
        cache = _get_namespace(namespace)
        return len(cache)

def cache_stats(namespace: str = "default") -> Dict[str, Any]:
    """Get cache statistics."""
    with _get_lock():
        stats = _get_stats(namespace)
        return {
            "hits": stats.hits,
            "misses": stats.misses,
            "sets": stats.sets,
            "deletes": stats.deletes,
            "evictions": stats.evictions,
            "expired": stats.expired,
            "total_size": stats.total_size,
            "hit_rate": stats.hits / (stats.hits + stats.misses) if (stats.hits + stats.misses) > 0 else 0.0
        }

def cache_cleanup(namespace: str = "default", max_age: int = 3600) -> int:
    """Cleanup old entries."""
    with _get_lock():
        cache = _get_namespace(namespace)
        stats = _get_stats(namespace)
        
        current_time = time.time()
        old_keys = []
        
        for key, entry in cache.items():
            if current_time - entry.timestamp > max_age:
                old_keys.append(key)
        
        for key in old_keys:
            del cache[key]
            stats.deletes += 1
        
        stats.total_size = len(cache)
        return len(old_keys)

def cache_optimize(namespace: str = "default") -> Dict[str, Any]:
    """Optimize cache by removing expired entries."""
    with _get_lock():
        expired_count = _evict_expired(namespace)
        stats = cache_stats(namespace)
        
        return {
            "expired_removed": expired_count,
            "current_size": stats["total_size"],
            "hit_rate": stats["hit_rate"]
        }

def cache_warmup(data: Dict[str, Any], namespace: str = "default", ttl: int = 300) -> int:
    """Warmup cache with data."""
    count = 0
    for key, value in data.items():
        if cache_set(key, value, ttl, namespace):
            count += 1
    return count

def cache_backup(namespace: str = "default") -> Dict[str, Any]:
    """Backup cache data."""
    with _get_lock():
        cache = _get_namespace(namespace)
        
        backup_data = {}
        for key, entry in cache.items():
            if not entry.is_expired():
                backup_data[key] = {
                    "value": entry.value,
                    "ttl": entry.ttl,
                    "age": time.time() - entry.timestamp
                }
        
        return backup_data

def cache_restore(backup_data: Dict[str, Any], namespace: str = "default") -> int:
    """Restore cache from backup."""
    count = 0
    for key, data in backup_data.items():
        remaining_ttl = max(0, data["ttl"] - int(data.get("age", 0)))
        if remaining_ttl > 0:
            if cache_set(key, data["value"], remaining_ttl, namespace):
                count += 1
    return count

def cache_get_all_stats() -> Dict[str, Any]:
    """Get statistics for all namespaces."""
    with _get_lock():
        all_stats = {}
        for namespace in _CACHE_NAMESPACES.keys():
            all_stats[namespace] = cache_stats(namespace)
        
        total_entries = sum(stats["total_size"] for stats in all_stats.values())
        total_hits = sum(stats["hits"] for stats in all_stats.values())
        total_misses = sum(stats["misses"] for stats in all_stats.values())
        
        return {
            "namespaces": all_stats,
            "total_entries": total_entries,
            "total_hits": total_hits,
            "total_misses": total_misses,
            "overall_hit_rate": total_hits / (total_hits + total_misses) if (total_hits + total_misses) > 0 else 0.0
        }
