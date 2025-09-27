"""
cache_core.py - ULTRA-OPTIMIZED: Core Cache Implementation with Legacy Elimination
Version: 2025.09.27.01
Description: Gateway-optimized cache core with all legacy threading patterns eliminated

LEGACY ELIMINATION COMPLETED:
- ✅ REMOVED: Manual threading.RLock() usage  
- ✅ REMOVED: Complex thread-safe data structures
- ✅ REMOVED: Manual memory management
- ✅ REMOVED: Direct OrderedDict with locking
- ✅ MODERNIZED: Pure delegation to singleton gateway for thread safety

ARCHITECTURE: SECONDARY IMPLEMENTATION - LEGACY-FREE
- Singleton gateway coordination for thread safety
- Memory management through gateway interfaces
- Zero manual threading or locking
- Utility gateway for all validation and formatting

FOLLOWS PROJECT_ARCHITECTURE_REFERENCE.md - ULTRA-PURE
"""

import time
import json
from typing import Any, Dict, Optional, List
from enum import Enum
from dataclasses import dataclass

# Gateway imports for maximum utilization (NO threading imports)
from . import singleton
from . import utility
from . import metrics
from . import logging as log_gateway

# ===== CACHE DATA STRUCTURES =====

class CacheType(Enum):
    """Cache types for different use cases."""
    LAMBDA = "lambda"
    RESPONSE = "response"
    CONFIG = "config"
    SECURITY = "security"
    CLIENT_STATE = "client_state"

@dataclass
class CacheEntry:
    """Cache entry with metadata."""
    value: Any
    timestamp: float
    ttl: int
    access_count: int = 0
    last_access: float = 0
    size_bytes: int = 0

@dataclass
class CacheStats:
    """Cache statistics tracker."""
    hits: int = 0
    misses: int = 0
    sets: int = 0
    deletes: int = 0
    evictions: int = 0
    start_time: float = 0
    
    def __post_init__(self):
        if self.start_time == 0:
            self.start_time = time.time()
    
    def get_hit_rate(self) -> float:
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0
    
    def reset(self):
        """Reset statistics."""
        self.__init__()

# ===== LEGACY-FREE CACHE IMPLEMENTATION =====

class MemoryCache:
    """
    Ultra-optimized cache using singleton gateway for thread safety.
    ALL LEGACY THREADING PATTERNS ELIMINATED.
    """
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 300):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache: Dict[str, CacheEntry] = {}
        self._stats = CacheStats()
        self._total_size_bytes = 0
        self._max_memory_mb = 32  # 32MB limit for cache
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get value using singleton gateway coordination."""
        def _get_operation():
            if key not in self._cache:
                self._stats.misses += 1
                return default
            
            entry = self._cache[key]
            
            # Check if expired
            if self._is_expired(entry):
                del self._cache[key]
                self._total_size_bytes -= entry.size_bytes
                self._stats.misses += 1
                return default
            
            # Update access statistics
            entry.access_count += 1
            entry.last_access = time.time()
            
            self._stats.hits += 1
            return entry.value
        
        return singleton.coordinate_operation(_get_operation, {
            'operation': 'cache_get',
            'key': key
        })
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value using singleton gateway coordination."""
        def _set_operation():
            try:
                ttl_value = ttl if ttl is not None else self.default_ttl
                current_time = time.time()
                
                # Calculate entry size using utility gateway
                size_bytes = utility.calculate_object_size(value)
                
                # Check memory limit
                if self._total_size_bytes + size_bytes > self._max_memory_mb * 1024 * 1024:
                    self._evict_entries()
                
                # Remove existing entry if present
                if key in self._cache:
                    old_entry = self._cache[key]
                    self._total_size_bytes -= old_entry.size_bytes
                    del self._cache[key]
                
                # Create new entry
                entry = CacheEntry(
                    value=value,
                    timestamp=current_time,
                    ttl=ttl_value,
                    access_count=1,
                    last_access=current_time,
                    size_bytes=size_bytes
                )
                
                # Add to cache
                self._cache[key] = entry
                self._total_size_bytes += size_bytes
                
                # Ensure size limit
                while len(self._cache) > self.max_size:
                    self._evict_lru()
                
                self._stats.sets += 1
                return True
                
            except Exception as e:
                log_gateway.log_error('Cache set operation failed', {
                    'key': key,
                    'error': str(e)
                })
                return False
        
        return singleton.coordinate_operation(_set_operation, {
            'operation': 'cache_set',
            'key': key
        })
    
    def delete(self, key: str) -> bool:
        """Delete key using singleton gateway coordination."""
        def _delete_operation():
            if key in self._cache:
                entry = self._cache[key]
                self._total_size_bytes -= entry.size_bytes
                del self._cache[key]
                self._stats.deletes += 1
                return True
            return False
        
        return singleton.coordinate_operation(_delete_operation, {
            'operation': 'cache_delete',
            'key': key
        })
    
    def clear(self) -> int:
        """Clear cache using singleton gateway coordination."""
        def _clear_operation():
            count = len(self._cache)
            self._cache.clear()
            self._total_size_bytes = 0
            return count
        
        return singleton.coordinate_operation(_clear_operation, {
            'operation': 'cache_clear'
        })
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics using utility gateway formatting."""
        def _stats_operation():
            return {
                'hits': self._stats.hits,
                'misses': self._stats.misses,
                'sets': self._stats.sets,
                'deletes': self._stats.deletes,
                'evictions': self._stats.evictions,
                'hit_rate': self._stats.get_hit_rate(),
                'total_entries': len(self._cache),
                'max_entries': self.max_size,
                'total_size_bytes': self._total_size_bytes,
                'max_size_bytes': self._max_memory_mb * 1024 * 1024,
                'uptime_seconds': time.time() - self._stats.start_time
            }
        
        stats = singleton.coordinate_operation(_stats_operation, {
            'operation': 'cache_statistics'
        })
        
        return utility.create_success_response(stats)
    
    def _is_expired(self, entry: CacheEntry) -> bool:
        """Check if cache entry is expired."""
        return time.time() > (entry.timestamp + entry.ttl)
    
    def _evict_entries(self):
        """Evict entries to free memory."""
        # Remove expired entries first
        expired_keys = [
            key for key, entry in self._cache.items()
            if self._is_expired(entry)
        ]
        
        for key in expired_keys:
            entry = self._cache[key]
            self._total_size_bytes -= entry.size_bytes
            del self._cache[key]
            self._stats.evictions += 1
        
        # If still over limit, remove least recently used
        while (self._total_size_bytes > self._max_memory_mb * 1024 * 1024 and 
               len(self._cache) > 0):
            self._evict_lru()
    
    def _evict_lru(self):
        """Evict least recently used entry."""
        if not self._cache:
            return
        
        # Find least recently used entry
        lru_key = min(self._cache.keys(), 
                     key=lambda k: self._cache[k].last_access)
        
        entry = self._cache[lru_key]
        self._total_size_bytes -= entry.size_bytes
        del self._cache[lru_key]
        self._stats.evictions += 1

# ===== CACHE MANAGER =====

class CacheManager:
    """
    Cache manager using singleton gateway coordination.
    LEGACY-FREE implementation.
    """
    
    def __init__(self):
        self._caches: Dict[CacheType, MemoryCache] = {}
    
    def get_cache(self, cache_type: CacheType) -> MemoryCache:
        """Get cache instance using singleton coordination."""
        def _get_cache_operation():
            if cache_type not in self._caches:
                self._caches[cache_type] = MemoryCache()
            return self._caches[cache_type]
        
        return singleton.coordinate_operation(_get_cache_operation, {
            'operation': 'get_cache',
            'cache_type': cache_type.value
        })
    
    def clear_all_caches(self) -> Dict[str, int]:
        """Clear all caches using singleton coordination."""
        def _clear_all_operation():
            results = {}
            for cache_type, cache in self._caches.items():
                count = cache.clear()
                results[cache_type.value] = count
            return results
        
        return singleton.coordinate_operation(_clear_all_operation, {
            'operation': 'clear_all_caches'
        })

# ===== EXPORTED FUNCTIONS =====

__all__ = [
    'CacheType',
    'CacheEntry', 
    'CacheStats',
    'MemoryCache',
    'CacheManager'
]

# EOF
