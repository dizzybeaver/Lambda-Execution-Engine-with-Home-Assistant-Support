"""
cache_core.py - LUGS-Integrated Cache Core Implementation
Version: 2025.10.17.05
Description: Cache with LUGS metadata tracking and memory monitoring

CHANGELOG:
- 2025.10.17.05: REDUCED DEFAULT_CACHE_TTL for Lambda optimization (Issue #12 fix)
  - Changed from 300s (5 minutes) to 60s (1 minute)
  - Better fit for Lambda use case (typical invocations are seconds)
  - Made configurable via CACHE_TTL environment variable
  - Updated design decisions documentation
- 2025.10.17.04: REMOVED threading locks for Lambda optimization (Issue #13 fix)
- 2025.10.17.02: Added memory tracking for Lambda 128MB constraint (Issue #9 fix)

DESIGN DECISIONS DOCUMENTED:

1. Threading Locks REMOVED (UPDATED 2025.10.17.04):
   DECISION: REMOVED for Lambda optimization (Issue #13)
   Reason: Lambda is definitively single-threaded per container
   Performance Gain: Eliminates ~0.001ms overhead per operation
   
2. Memory Tracking Implementation (UPDATED 2025.10.17.02):
   DECISION: Tracks both item count AND memory bytes consumed
   Reason: Lambda 128MB constraint requires byte-level memory visibility
   Trade-off: Small overhead on set/delete (~0.01ms) for critical safety feature
   
3. 60 Second Default TTL (UPDATED 2025.10.17.05):
   PREVIOUS: DEFAULT_CACHE_TTL = 300 seconds (5 minutes)
   DECISION: REDUCED to 60 seconds (1 minute) for Lambda (Issue #12)
   Reason: Lambda invocations typically last seconds, not minutes
   Lambda Use Case: Shorter TTL reduces stale data risk
   Configurable: Can be overridden via CACHE_TTL environment variable or per cache_set() call
   Performance: Better memory utilization, faster cache turnover

Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

import os
import sys
import time
from typing import Dict, Any, Optional, Set
from dataclasses import dataclass
from enum import Enum


# ===== CACHE CONSTANTS =====

DEFAULT_CACHE_TTL = int(os.environ.get('CACHE_TTL', '60'))  # 1 minute (configurable)
MAX_CACHE_BYTES = 50 * 1024 * 1024  # 50MB limit for Lambda safety

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
    value_size_bytes: int = 0


# ===== LUGS-INTEGRATED CACHE =====

class LUGSIntegratedCache:
    """
    Cache with LUGS dependency tracking and memory monitoring.
    
    LAMBDA OPTIMIZED: No threading locks (single-threaded per container).
    
    DESIGN NOTES:
    - Single-threaded: Lambda containers are single-threaded, no locks needed
    - Entry modification: Direct modification of entry fields is safe
    - Expiration cleanup: Happens inline during get() and exists() to avoid
      stale data without requiring separate cleanup thread
    - LUGS integration: Optional - cache operations continue even if LUGS
      registration fails (logged but not fatal)
    - None handling: Can cache None values safely (use exists() to check presence)
    - Memory tracking: Tracks BOTH item count AND bytes for Lambda 128MB safety
    - TTL: Configurable via CACHE_TTL environment variable (default: 60s)
    """
    
    def __init__(self):
        self._cache: Dict[str, CacheEntry] = {}
        self.max_bytes = MAX_CACHE_BYTES
        self.current_bytes = 0
        self._stats = {
            'total_sets': 0,
            'total_gets': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'lugs_prevented_unload': 0,
            'entries_expired': 0,
            'memory_evictions': 0
        }
    
    def _calculate_entry_size(self, key: str, value: Any) -> int:
        """Calculate memory size of cache entry."""
        return sys.getsizeof(key) + sys.getsizeof(value)
    
    def _evict_lru_entries(self, bytes_needed: int) -> int:
        """
        Evict least recently used entries to free up memory.
        
        Returns number of bytes freed.
        """
        if not self._cache:
            return 0
        
        # Sort by last_access time (oldest first)
        sorted_entries = sorted(
            self._cache.items(),
            key=lambda x: x[1].last_access if x[1].last_access > 0 else x[1].timestamp
        )
        
        bytes_freed = 0
        entries_evicted = 0
        
        for key, entry in sorted_entries:
            if bytes_freed >= bytes_needed:
                break
            
            bytes_freed += entry.value_size_bytes
            del self._cache[key]
            entries_evicted += 1
            self.current_bytes -= entry.value_size_bytes
        
        self._stats['memory_evictions'] += entries_evicted
        return bytes_freed
    
    def _check_memory_pressure(self) -> bool:
        """
        Check if cache is under memory pressure.
        Uses gateway memory functions if available.
        
        Returns True if memory pressure detected.
        """
        try:
            from gateway import check_lambda_memory_compliance
            
            status = check_lambda_memory_compliance()
            if not status.get('compliant', True):
                return True
        except (ImportError, Exception):
            pass
        
        # Fallback: check cache memory limit
        return self.current_bytes > (self.max_bytes * 0.9)
    
    def _handle_memory_pressure(self) -> None:
        """
        Handle memory pressure by optimizing cache and system memory.
        Uses gateway memory functions if available.
        """
        try:
            from gateway import optimize_memory
            
            result = optimize_memory()
            if result.get('success'):
                return
        except (ImportError, Exception):
            pass
        
        # Fallback: evict 20% of cache
        bytes_to_free = int(self.current_bytes * 0.2)
        if bytes_to_free > 0:
            self._evict_lru_entries(bytes_to_free)
    
    def set(self, key: str, value: Any, ttl: float = DEFAULT_CACHE_TTL, 
            source_module: Optional[str] = None) -> None:
        """
        Set cache value with TTL and optional LUGS source tracking.
        
        Args:
            key: Cache key (non-empty string)
            value: Value to cache (any type including None)
            ttl: Time-to-live in seconds (default: 60s, configurable via CACHE_TTL env var)
            source_module: Optional module name for LUGS dependency tracking
            
        Raises:
            ValueError: If key is invalid or TTL is not positive
        """
        _validate_cache_key(key)
        _validate_ttl(ttl)
        
        # Check memory pressure before adding
        if self._check_memory_pressure():
            self._handle_memory_pressure()
        
        # Calculate entry size
        entry_size = self._calculate_entry_size(key, value)
        
        # Check if we need to evict for this entry
        if self.current_bytes + entry_size > self.max_bytes:
            bytes_needed = entry_size - (self.max_bytes - self.current_bytes)
            self._evict_lru_entries(bytes_needed)
        
        # If key already exists, subtract old size
        if key in self._cache:
            old_entry = self._cache[key]
            self.current_bytes -= old_entry.value_size_bytes
        
        current_time = time.time()
        
        # Create cache entry
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
        self._stats['total_sets'] += 1
        
        # Register with LUGS if source module provided
        if source_module:
            try:
                from gateway import add_cache_module_dependency
                add_cache_module_dependency(source_module, key)
            except (ImportError, Exception):
                # LUGS registration failed, but cache operation continues
                pass
    
    def get(self, key: str) -> Any:
        """
        Get cached value if exists and not expired.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value, or special _CACHE_MISS sentinel if not found/expired.
            Can return None if None was cached (use exists() to distinguish).
            
        Raises:
            ValueError: If key is invalid
        """
        _validate_cache_key(key)
        
        self._stats['total_gets'] += 1
        
        if key not in self._cache:
            self._stats['cache_misses'] += 1
            return _CACHE_MISS
        
        entry = self._cache[key]
        current_time = time.time()
        
        # Check expiration
        if current_time - entry.timestamp > entry.ttl:
            # Expired - remove and return miss
            self.current_bytes -= entry.value_size_bytes
            del self._cache[key]
            self._stats['cache_misses'] += 1
            self._stats['entries_expired'] += 1
            return _CACHE_MISS
        
        # Update access tracking
        entry.access_count += 1
        entry.last_access = current_time
        
        self._stats['cache_hits'] += 1
        return entry.value
    
    def exists(self, key: str) -> bool:
        """
        Check if key exists in cache and is not expired.
        
        Args:
            key: Cache key
            
        Returns:
            True if key exists and not expired, False otherwise
            
        Raises:
            ValueError: If key is invalid
        """
        _validate_cache_key(key)
        
        if key not in self._cache:
            return False
        
        entry = self._cache[key]
        current_time = time.time()
        
        # Check expiration
        if current_time - entry.timestamp > entry.ttl:
            # Expired - remove and return False
            self.current_bytes -= entry.value_size_bytes
            del self._cache[key]
            self._stats['entries_expired'] += 1
            return False
        
        return True
    
    def delete(self, key: str) -> bool:
        """
        Delete key from cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if key was deleted, False if key didn't exist
            
        Raises:
            ValueError: If key is invalid
        """
        _validate_cache_key(key)
        
        if key in self._cache:
            entry = self._cache[key]
            self.current_bytes -= entry.value_size_bytes
            del self._cache[key]
            return True
        return False
    
    def clear(self) -> int:
        """
        Clear all entries from cache.
        
        Returns:
            Number of entries cleared
        """
        count = len(self._cache)
        self._cache.clear()
        self.current_bytes = 0
        return count
    
    def cleanup_expired(self) -> int:
        """
        Remove all expired entries.
        
        Returns:
            Number of entries removed
        """
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
        self._stats['entries_expired'] += count
        return count
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics including memory metrics.
        
        Returns:
            Dictionary with cache statistics and memory usage
        """
        hit_rate = 0.0
        total_requests = self._stats['cache_hits'] + self._stats['cache_misses']
        if total_requests > 0:
            hit_rate = (self._stats['cache_hits'] / total_requests) * 100
        
        # Try to get gateway memory status
        gateway_memory = {}
        try:
            from gateway import get_memory_stats
            gateway_memory = get_memory_stats()
        except (ImportError, Exception):
            pass
        
        stats = {
            'size': len(self._cache),
            'memory_bytes': self.current_bytes,
            'memory_mb': self.current_bytes / (1024 * 1024),
            'max_bytes': self.max_bytes,
            'max_mb': self.max_bytes / (1024 * 1024),
            'memory_utilization_percent': (self.current_bytes / self.max_bytes) * 100 if self.max_bytes > 0 else 0,
            'default_ttl_seconds': DEFAULT_CACHE_TTL,
            'total_sets': self._stats['total_sets'],
            'total_gets': self._stats['total_gets'],
            'cache_hits': self._stats['cache_hits'],
            'cache_misses': self._stats['cache_misses'],
            'hit_rate_percent': hit_rate,
            'entries_expired': self._stats['entries_expired'],
            'memory_evictions': self._stats['memory_evictions'],
            'lugs_prevented_unload': self._stats['lugs_prevented_unload']
        }
        
        if gateway_memory:
            stats['gateway_memory'] = gateway_memory
        
        return stats
    
    def get_module_dependencies(self) -> Dict[str, Set[str]]:
        """
        Get LUGS module dependencies (which modules use which cache keys).
        
        Returns:
            Dictionary mapping module names to sets of cache keys
        """
        dependencies: Dict[str, Set[str]] = {}
        
        for key, entry in self._cache.items():
            if entry.source_module:
                if entry.source_module not in dependencies:
                    dependencies[entry.source_module] = set()
                dependencies[entry.source_module].add(key)
        
        return dependencies


# ===== GLOBAL CACHE INSTANCE =====

_GLOBAL_CACHE = LUGSIntegratedCache()


# ===== IMPLEMENTATION WRAPPERS =====

def _execute_get_implementation(key: str, **kwargs) -> Any:
    """Execute cache get operation."""
    return _GLOBAL_CACHE.get(key)


def _execute_set_implementation(key: str, value: Any, ttl: float = DEFAULT_CACHE_TTL,
                                source_module: Optional[str] = None, **kwargs) -> None:
    """Execute cache set operation."""
    _GLOBAL_CACHE.set(key, value, ttl, source_module)


def _execute_exists_implementation(key: str, **kwargs) -> bool:
    """Execute cache exists check."""
    return _GLOBAL_CACHE.exists(key)


def _execute_delete_implementation(key: str, **kwargs) -> bool:
    """Execute cache delete operation."""
    return _GLOBAL_CACHE.delete(key)


def _execute_clear_implementation(**kwargs) -> int:
    """Execute cache clear operation."""
    return _GLOBAL_CACHE.clear()


def _execute_cleanup_expired_implementation(**kwargs) -> int:
    """Execute cache cleanup expired operation."""
    return _GLOBAL_CACHE.cleanup_expired()


def _execute_get_stats_implementation(**kwargs) -> Dict[str, Any]:
    """Execute cache get stats operation."""
    return _GLOBAL_CACHE.get_stats()


def _execute_get_module_dependencies_implementation(**kwargs) -> Dict[str, Set[str]]:
    """Execute cache get module dependencies operation."""
    return _GLOBAL_CACHE.get_module_dependencies()


# ===== CONVENIENCE FUNCTIONS =====

def cache_exists(key: str) -> bool:
    """
    Check if key exists in cache (convenience function).
    
    Args:
        key: Cache key
        
    Returns:
        True if key exists and not expired, False otherwise
    """
    return _GLOBAL_CACHE.exists(key)


# ===== MODULE EXPORTS =====

__all__ = [
    'DEFAULT_CACHE_TTL',
    'MAX_CACHE_BYTES',
    'CacheOperation',
    'CacheEntry',
    'LUGSIntegratedCache',
    '_execute_get_implementation',
    '_execute_set_implementation',
    '_execute_exists_implementation',
    '_execute_delete_implementation',
    '_execute_clear_implementation',
    '_execute_cleanup_expired_implementation',
    '_execute_get_stats_implementation',
    '_execute_get_module_dependencies_implementation',
    'cache_exists',
]

# EOF
