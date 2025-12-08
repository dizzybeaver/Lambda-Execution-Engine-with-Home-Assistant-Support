"""
cache/cache_core.py
Version: 2025-12-08_1
Purpose: LUGS-integrated cache with TTL, rate limiting, and metrics
License: Apache 2.0
"""

import time
import sys
from collections import deque
from typing import Any, Dict, Optional, Set

from cache import (
    CacheEntry,
    _CACHE_MISS,
    DEFAULT_CACHE_TTL,
    MAX_CACHE_BYTES,
    RATE_LIMIT_WINDOW_MS,
    RATE_LIMIT_MAX_OPS,
)


class LUGSIntegratedCache:
    """In-memory cache with LUGS integration, metrics, and rate limiting."""
    
    def __init__(self, max_bytes: int = MAX_CACHE_BYTES):
        self._cache: Dict[str, CacheEntry] = {}
        self.max_bytes = max_bytes
        self.current_bytes = 0
        self._rate_limiter = deque(maxlen=RATE_LIMIT_MAX_OPS)
        self._rate_limit_window_ms = RATE_LIMIT_WINDOW_MS
        self._rate_limited_count = 0
    
    def _check_rate_limit(self) -> bool:
        """Check if rate limit exceeded using sliding window."""
        now = time.time() * 1000
        
        while self._rate_limiter and (now - self._rate_limiter[0]) > self._rate_limit_window_ms:
            self._rate_limiter.popleft()
        
        if len(self._rate_limiter) >= RATE_LIMIT_MAX_OPS:
            self._rate_limited_count += 1
            return False
        
        self._rate_limiter.append(now)
        return True
    
    def _calculate_entry_size(self, key: str, value: Any) -> int:
        """Estimate memory size of cache entry."""
        try:
            key_size = sys.getsizeof(key)
            value_size = sys.getsizeof(value)
            metadata_size = 200
            return key_size + value_size + metadata_size
        except Exception:
            return 1024
    
    def _check_memory_pressure(self) -> bool:
        """Check if cache is under memory pressure (>80% full)."""
        return self.current_bytes > (self.max_bytes * 0.8)
    
    def _evict_lru_entries(self, bytes_needed: int) -> int:
        """Evict least recently used entries to free memory."""
        if not self._cache:
            return 0
        
        sorted_entries = sorted(
            self._cache.items(),
            key=lambda x: x[1].last_access
        )
        
        bytes_freed = 0
        evicted_count = 0
        
        for key, entry in sorted_entries:
            if bytes_freed >= bytes_needed:
                break
            
            bytes_freed += entry.value_size_bytes
            self.current_bytes -= entry.value_size_bytes
            del self._cache[key]
            evicted_count += 1
        
        if evicted_count > 0:
            try:
                from gateway import increment_counter
                increment_counter('cache.entries_evicted', evicted_count)
            except (ImportError, Exception):
                pass
        
        return evicted_count
    
    def _handle_memory_pressure(self) -> None:
        """Handle memory pressure by evicting entries."""
        bytes_to_free = int(self.max_bytes * 0.2)
        self._evict_lru_entries(bytes_to_free)
    
    def set(self, key: str, value: Any, ttl: int = DEFAULT_CACHE_TTL, source_module: Optional[str] = None) -> None:
        """Set cache entry with TTL and optional module tracking."""
        if not self._check_rate_limit():
            return
        
        try:
            from gateway import validate_cache_key, validate_ttl, validate_module_name, increment_counter
            
            validate_cache_key(key)
            validate_ttl(ttl)
            
            if source_module:
                validate_module_name(source_module)
        except ImportError:
            from gateway import increment_counter
        
        if self._check_memory_pressure():
            self._handle_memory_pressure()
        
        entry_size = self._calculate_entry_size(key, value)
        
        if self.current_bytes + entry_size > self.max_bytes:
            bytes_needed = entry_size - (self.max_bytes - self.current_bytes)
            self._evict_lru_entries(bytes_needed)
        
        if key in self._cache:
            old_entry = self._cache[key]
            self.current_bytes -= old_entry.value_size_bytes
        
        current_time = time.time()
        
        entry = CacheEntry(
            value=value,
            timestamp=current_time,
            ttl=ttl,
            source_module=source_module,
            access_count=0,
            last_access=current_time,
            value_size_bytes=entry_size
        )
        
        self._cache[key] = entry
        self.current_bytes += entry_size
        
        try:
            increment_counter('cache.total_sets')
        except Exception:
            pass
        
        if source_module:
            try:
                from gateway import add_cache_module_dependency
                add_cache_module_dependency(source_module, key)
            except (ImportError, Exception):
                pass
    
    def get(self, key: str) -> Any:
        """Get cached value if exists and not expired."""
        if not self._check_rate_limit():
            return _CACHE_MISS
        
        try:
            from gateway import record_cache_metric, increment_counter
        except ImportError:
            return _CACHE_MISS
        
        if key not in self._cache:
            try:
                record_cache_metric(operation_name='get', hit=False)
            except Exception:
                pass
            return _CACHE_MISS
        
        entry = self._cache[key]
        current_time = time.time()
        age = current_time - entry.timestamp
        
        if age > entry.ttl:
            self.current_bytes -= entry.value_size_bytes
            del self._cache[key]
            
            try:
                increment_counter('cache.entries_expired')
                record_cache_metric(operation_name='get', hit=False)
            except Exception:
                pass
            return _CACHE_MISS
        
        entry.access_count += 1
        entry.last_access = current_time
        
        try:
            record_cache_metric(operation_name='get', hit=True)
        except Exception:
            pass
        
        return entry.value
    
    def exists(self, key: str) -> bool:
        """Check if key exists and is not expired."""
        if not self._check_rate_limit():
            return False
        
        if key not in self._cache:
            return False
        
        entry = self._cache[key]
        current_time = time.time()
        age = current_time - entry.timestamp
        
        if age > entry.ttl:
            self.current_bytes -= entry.value_size_bytes
            del self._cache[key]
            
            try:
                from gateway import increment_counter
                increment_counter('cache.entries_expired')
            except (ImportError, Exception):
                pass
            
            return False
        
        return True
    
    def delete(self, key: str) -> bool:
        """Delete cache entry if it exists."""
        if not self._check_rate_limit():
            return False
        
        if key in self._cache:
            entry = self._cache[key]
            self.current_bytes -= entry.value_size_bytes
            del self._cache[key]
            return True
        return False
    
    def clear(self) -> int:
        """Clear all cache entries."""
        if not self._check_rate_limit():
            return 0
        
        count = len(self._cache)
        self._cache.clear()
        self.current_bytes = 0
        return count
    
    def reset(self) -> bool:
        """Reset cache to initial state."""
        self._cache.clear()
        self.current_bytes = 0
        self._rate_limiter.clear()
        self._rate_limited_count = 0
        return True
    
    def cleanup_expired(self) -> int:
        """Remove all expired entries."""
        if not self._check_rate_limit():
            return 0
        
        try:
            from gateway import increment_counter
        except ImportError:
            increment_counter = None
        
        current_time = time.time()
        expired_keys = [
            key for key, entry in self._cache.items()
            if current_time - entry.timestamp > entry.ttl
        ]
        
        for key in expired_keys:
            entry = self._cache[key]
            self.current_bytes -= entry.value_size_bytes
            del self._cache[key]
        
        count = len(expired_keys)
        
        if count > 0 and increment_counter:
            try:
                increment_counter('cache.entries_expired', count)
            except Exception:
                pass
        
        return count
    
    def get_metadata(self, key: str) -> Optional[Dict[str, Any]]:
        """Get cache entry metadata without accessing value."""
        if not self._check_rate_limit():
            return None
        
        try:
            from gateway import increment_counter
            increment_counter('cache.metadata_queries')
        except (ImportError, Exception):
            pass
        
        if key not in self._cache:
            return None
        
        entry = self._cache[key]
        current_time = time.time()
        age = current_time - entry.timestamp
        
        if age > entry.ttl:
            self.current_bytes -= entry.value_size_bytes
            del self._cache[key]
            try:
                from gateway import increment_counter
                increment_counter('cache.entries_expired')
            except (ImportError, Exception):
                pass
            return None
        
        return {
            'source_module': entry.source_module,
            'timestamp': entry.timestamp,
            'age_seconds': age,
            'ttl': entry.ttl,
            'ttl_remaining': max(0, entry.ttl - age),
            'access_count': entry.access_count,
            'last_access': entry.last_access,
            'size_bytes': entry.value_size_bytes,
            'is_expired': False
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            'size': len(self._cache),
            'memory_bytes': self.current_bytes,
            'memory_mb': round(self.current_bytes / (1024 * 1024), 2),
            'max_bytes': self.max_bytes,
            'max_mb': round(self.max_bytes / (1024 * 1024), 2),
            'memory_utilization_percent': round((self.current_bytes / self.max_bytes) * 100, 2),
            'default_ttl_seconds': DEFAULT_CACHE_TTL,
            'rate_limited_count': self._rate_limited_count
        }
    
    def get_module_dependencies(self) -> Set[str]:
        """Get set of all module names that have cache dependencies."""
        modules = set()
        for entry in self._cache.values():
            if entry.source_module:
                modules.add(entry.source_module)
        return modules


_cache_instance = None


def _get_cache_instance() -> LUGSIntegratedCache:
    """Get or create cache singleton instance via SINGLETON interface."""
    global _cache_instance
    
    try:
        from gateway import singleton_get, singleton_register
        
        manager = singleton_get('cache_manager')
        if manager is None:
            manager = LUGSIntegratedCache()
            singleton_register('cache_manager', manager)
        
        return manager
    except (ImportError, Exception):
        if _cache_instance is None:
            _cache_instance = LUGSIntegratedCache()
        return _cache_instance


__all__ = [
    'LUGSIntegratedCache',
    '_get_cache_instance',
]

# EOF
