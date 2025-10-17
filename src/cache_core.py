"""
cache_core.py - LUGS-Integrated Cache Core Implementation
Version: 2025.10.16.05
Description: Thread-safe cache with LUGS metadata tracking

CHANGELOG:
- 2025.10.16.05: Removed duplicate gateway functions, removed generic operation wrapper,
                 simplified implementation wrappers to directly call cache instance
- 2025.10.16.04: Bug fixes - added cache_exists() convenience function, parameter validation,
                 TTL validation, key validation, improved None handling documentation
- 2025.10.16.03: Bug fixes - added EXISTS enum, DEFAULT_CACHE_TTL constant, improved
                 LUGS failure logging, added documentation for intentional behaviors
- 2025.10.16.02: Fixed exists() implementation, TTL defaults, error handling, type hints
- 2025.10.15.02: Added dispatcher timing integration
- 2025.10.15.01: Initial LUGS-integrated cache implementation

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
import sys
import time
import threading
from typing import Dict, Any, Optional, Set
from dataclasses import dataclass
from enum import Enum


# ===== CACHE CONSTANTS =====

DEFAULT_CACHE_TTL = 300  # seconds (5 minutes)

# Sentinel value for cache misses to distinguish from cached None
_CACHE_MISS = object()


# ===== CACHE OPERATION ENUM =====

class CacheOperation(Enum):
    """Enumeration of all cache operations."""
    GET = "get"
    SET = "set"
    EXISTS = "exists"
    DELETE = "delete"
    CLEAR = "clear"
    CLEANUP_EXPIRED = "cleanup_expired"
    GET_STATS = "get_stats"
    GET_MODULE_DEPENDENCIES = "get_module_dependencies"


# ===== VALIDATION HELPERS =====

def _validate_cache_key(key: str) -> None:
    """
    Validate cache key is non-empty string.
    
    Args:
        key: Cache key to validate
        
    Raises:
        ValueError: If key is empty or not a string
    """
    if not isinstance(key, str):
        raise ValueError(f"Cache key must be a string, got {type(key).__name__}")
    if not key:
        raise ValueError("Cache key cannot be empty string")


def _validate_ttl(ttl: float) -> None:
    """
    Validate TTL is positive number.
    
    Args:
        ttl: Time-to-live in seconds
        
    Raises:
        ValueError: If TTL is not positive
    """
    if ttl <= 0:
        raise ValueError(f"TTL must be positive, got {ttl}")


# ===== CACHE ENTRY =====

@dataclass
class CacheEntry:
    """Cache entry with LUGS metadata and type hints."""
    value: Any
    timestamp: float
    ttl: float
    source_module: Optional[str] = None
    access_count: int = 0
    last_access: float = 0.0


# ===== LUGS-INTEGRATED CACHE =====

class LUGSIntegratedCache:
    """
    Thread-safe cache with LUGS dependency tracking.
    
    INTENTIONAL DESIGN NOTES:
    - Thread safety: All operations use self._lock for atomic operations
    - Entry modification: Direct modification of entry fields is safe because
      lock is held during entire get() operation
    - Expiration cleanup: Happens inline during get() and exists() to avoid
      stale data without requiring separate cleanup thread
    - LUGS integration: Optional - cache operations continue even if LUGS
      registration fails (logged but not fatal)
    - None handling: Can cache None values safely (use exists() to check presence)
    """
    
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
    
    def set(self, key: str, value: Any, ttl: float = DEFAULT_CACHE_TTL, source_module: Optional[str] = None) -> None:
        """
        Set cache value with LUGS tracking.
        
        Args:
            key: Cache key (non-empty string)
            value: Value to cache (can be None)
            ttl: Time-to-live in seconds (must be positive, default: 300)
            source_module: Module name for LUGS dependency tracking
            
        Raises:
            ValueError: If key is empty or ttl is not positive
            
        Notes:
            - LUGS registration failure is logged but not fatal
            - Cache operation succeeds even if LUGS is unavailable
        """
        _validate_cache_key(key)
        _validate_ttl(ttl)
        
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
        
        # Notify LUGS of cache dependency
        # INTENTIONAL: Failure here is non-fatal - cache operation continues
        if source_module:
            try:
                from gateway import add_cache_module_dependency
                add_cache_module_dependency(key, source_module)
            except ImportError as e:
                print(
                    f"[CACHE] Warning: Could not register LUGS dependency for key '{key}' "
                    f"from module '{source_module}': {e}", 
                    file=sys.stderr
                )
            except Exception as e:
                print(
                    f"[CACHE] Warning: LUGS dependency registration failed for key '{key}': {e}", 
                    file=sys.stderr
                )
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get cache entry with access tracking.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value (can be None if None was cached) or None if not found/expired
            
        Notes:
            - Updates access metadata (count, timestamp) on hit
            - Expired entries are automatically removed during lookup
            - Thread-safe: entry modification happens while holding lock
            - Returns None for both cache miss AND cached None value
              (use exists() to distinguish if needed)
        """
        _validate_cache_key(key)
        current_time = time.time()
        
        with self._lock:
            self._stats['total_gets'] += 1
            
            if key not in self._cache:
                self._stats['cache_misses'] += 1
                return None
            
            entry = self._cache[key]
            
            # Check expiration - inline cleanup
            if current_time - entry.timestamp > entry.ttl:
                del self._cache[key]
                self._stats['cache_misses'] += 1
                self._stats['entries_expired'] += 1
                return None
            
            # Update access metadata
            # INTENTIONAL: Modifying entry while holding lock is thread-safe
            entry.access_count += 1
            entry.last_access = current_time
            self._stats['cache_hits'] += 1
            
            return entry.value
    
    def exists(self, key: str) -> bool:
        """
        Check if key exists without updating access metadata.
        
        Args:
            key: Cache key
            
        Returns:
            True if key exists and not expired, False otherwise
            
        Notes:
            - Does NOT update access count or last_access time
            - Expired entries are removed during check
            - Use this for existence checks that shouldn't affect LRU metrics
            - Use this to distinguish between cached None and cache miss
        """
        _validate_cache_key(key)
        current_time = time.time()
        
        with self._lock:
            if key not in self._cache:
                return False
            
            entry = self._cache[key]
            
            # Check expiration without updating access metadata
            if current_time - entry.timestamp > entry.ttl:
                del self._cache[key]
                self._stats['entries_expired'] += 1
                return False
            
            return True
    
    def delete(self, key: str) -> bool:
        """
        Delete cache entry.
        
        Args:
            key: Cache key
            
        Returns:
            True if entry was deleted, False if key didn't exist
        """
        _validate_cache_key(key)
        
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False
    
    def clear(self) -> int:
        """
        Clear all cache entries.
        
        Returns:
            Number of entries cleared
        """
        with self._lock:
            count = len(self._cache)
            self._cache.clear()
            return count
    
    def cleanup_expired(self) -> int:
        """
        Clean up expired entries.
        
        Returns:
            Number of entries cleaned up
            
        Notes:
            - Explicit cleanup operation for batch expiration removal
            - Also happens automatically during get() and exists()
        """
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
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache statistics including hit rate
        """
        with self._lock:
            stats = self._stats.copy()
            stats.update({
                'entries_count': len(self._cache),
                'cache_hit_rate': (
                    (self._stats['cache_hits'] / self._stats['total_gets'] * 100)
                    if self._stats['total_gets'] > 0
                    else 0.0
                )
            })
        
        return stats
    
    def get_module_dependencies(self) -> Dict[str, Set[str]]:
        """
        Get all cache entries by source module for LUGS integration.
        
        Returns:
            Dictionary mapping module names to sets of cache keys
            
        Notes:
            - Used by LUGS to track which modules have cached data
            - Prevents unloading modules with active cache dependencies
        """
        dependencies = {}
        
        with self._lock:
            for key, entry in self._cache.items():
                if entry.source_module:
                    if entry.source_module not in dependencies:
                        dependencies[entry.source_module] = set()
                    dependencies[entry.source_module].add(key)
        
        return dependencies


# Global cache instance
_cache_instance = LUGSIntegratedCache()


# ===== IMPLEMENTATION WRAPPERS FOR INTERFACE =====
# These are called by interface_cache.py and directly invoke cache instance methods

def _execute_get_implementation(key: str, default: Any = None, **kwargs) -> Optional[Any]:
    """Execute get operation."""
    result = _cache_instance.get(key)
    return result if result is not None else default


def _execute_set_implementation(key: str, value: Any, ttl: float = DEFAULT_CACHE_TTL, source_module: Optional[str] = None, **kwargs) -> None:
    """Execute set operation with default TTL."""
    _cache_instance.set(key, value, ttl, source_module)


def _execute_delete_implementation(key: str, **kwargs) -> bool:
    """Execute delete operation."""
    return _cache_instance.delete(key)


def _execute_clear_implementation(**kwargs) -> int:
    """Execute clear operation."""
    return _cache_instance.clear()


def _execute_cleanup_expired_implementation(**kwargs) -> int:
    """Execute cleanup expired operation."""
    return _cache_instance.cleanup_expired()


def _execute_get_stats_implementation(**kwargs) -> Dict[str, Any]:
    """Execute get stats operation."""
    return _cache_instance.get_stats()


def _execute_exists_implementation(key: str, **kwargs) -> bool:
    """Execute exists operation - checks without updating access metadata."""
    return _cache_instance.exists(key)


# ===== EXPORTS =====

__all__ = [
    'CacheOperation',
    'LUGSIntegratedCache',
    '_execute_get_implementation',
    '_execute_set_implementation',
    '_execute_delete_implementation',
    '_execute_clear_implementation',
    '_execute_cleanup_expired_implementation',
    '_execute_get_stats_implementation',
    '_execute_exists_implementation',
    'DEFAULT_CACHE_TTL',
]

# EOF
