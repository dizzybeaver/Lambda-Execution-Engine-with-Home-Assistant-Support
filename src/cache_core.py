"""
cache_core.py - Cache Core Implementation
Version: 2025.10.20.04
Description: FIXED metrics parameter name - operation_name kwarg (Bug Fix)

CHANGELOG:
- 2025.10.20.04: BUG FIX - Parameter name mismatch
  - FIXED: record_cache_metric() calls now use operation_name= kwarg explicitly
  - Previously: record_cache_metric('get', hit=True) - positional arg
  - Now: record_cache_metric(operation_name='get', hit=True) - keyword arg
  - Reason: Wrapper expects operation_name, not positional operation
  - This fixes CloudWatch error: "missing 1 required positional argument: 'operation'"

Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

import sys
import time
from typing import Any, Dict, Optional, Set
from dataclasses import dataclass
from enum import Enum


# ===== CONSTANTS =====

DEFAULT_CACHE_TTL = 60  # seconds
MAX_CACHE_BYTES = 50 * 1024 * 1024  # 50MB


# ===== CACHE MISS SENTINEL =====

_CACHE_MISS = object()  # Sentinel for cache miss detection


# ===== CACHE OPERATIONS ENUM =====

class CacheOperation(Enum):
    """Cache operations enumeration."""
    GET = "get"
    SET = "set"
    EXISTS = "exists"
    DELETE = "delete"
    CLEAR = "clear"
    CLEANUP_EXPIRED = "cleanup_expired"
    GET_STATS = "get_stats"
    GET_METADATA = "get_metadata"
    GET_MODULE_DEPENDENCIES = "get_module_dependencies"


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
    
    PURIFIED: No validation logic (security interface handles validation).
    PURE CACHE: Only cache operations - no metrics, no validation.
    METRICS: All metrics via METRICS interface (no internal tracking).
    
    LAMBDA OPTIMIZED: No threading locks (single-threaded per container).
    SECURITY: All validation via security interface (CVE fixes applied).
    
    DESIGN NOTES:
    - Single-threaded: Lambda containers are single-threaded, no locks needed
    - Entry modification: Direct modification of entry fields is safe
    - Expiration cleanup: Happens inline during get() and exists()
    - LUGS integration: Optional - cache operations continue if LUGS fails
    - None handling: Can cache None values safely (use exists() to check)
    - Memory tracking: Tracks both item count AND bytes for Lambda 128MB safety
    - TTL: Configurable via CACHE_TTL environment variable (default: 60s)
    - Fast metadata: get_metadata() provides O(1) access without gateway routing
    - Validation: ALL validation via security interface
    - Metrics: ALL metrics via metrics interface (no internal _stats)
    """
    
    def __init__(self):
        self._cache: Dict[str, CacheEntry] = {}
        self.max_bytes = MAX_CACHE_BYTES
        self.current_bytes = 0
        # NO MORE _stats dictionary - all metrics via METRICS interface
    
    def _calculate_entry_size(self, key: str, value: Any) -> int:
        """Calculate memory size of cache entry."""
        try:
            key_size = sys.getsizeof(key)
            value_size = sys.getsizeof(value)
            overhead = sys.getsizeof(CacheEntry)
            return key_size + value_size + overhead
        except Exception:
            return 1024  # Default estimate
    
    def _evict_lru_entries(self, bytes_to_free: int) -> None:
        """Evict least recently used entries to free memory."""
        if not self._cache:
            return
        
        # Import metrics functions
        from gateway import increment_counter
        
        # Sort by last_access (oldest first)
        sorted_entries = sorted(
            self._cache.items(),
            key=lambda item: item[1].last_access
        )
        
        freed = 0
        evicted_count = 0
        for key, entry in sorted_entries:
            if freed >= bytes_to_free:
                break
            
            freed += entry.value_size_bytes
            self.current_bytes -= entry.value_size_bytes
            del self._cache[key]
            evicted_count += 1
        
        # METRICS: Track evictions via metrics interface
        increment_counter('cache.memory_evictions', evicted_count)
    
    def _check_memory_pressure(self) -> bool:
        """Check if cache is under memory pressure (>90% full)."""
        return self.current_bytes > (self.max_bytes * 0.9)
    
    def _handle_memory_pressure(self) -> None:
        """Handle memory pressure by cleaning up expired entries first."""
        from gateway import log_warning
        
        # Try expired cleanup first
        expired_count = self.cleanup_expired()
        
        # Still under pressure after cleanup?
        if self._check_memory_pressure():
            log_warning(
                f"Cache memory pressure after cleanup: {self.current_bytes}/{self.max_bytes} bytes "
                f"({(self.current_bytes/self.max_bytes)*100:.1f}% full, {expired_count} expired cleared)"
            )
    
    def set(self, key: str, value: Any, ttl: int = DEFAULT_CACHE_TTL, source_module: Optional[str] = None) -> None:
        """
        Set cache entry with validation via security interface.
        
        PURIFIED: No validation in cache - delegates to security interface.
        SECURITY: Validation via security interface (CVE fixes applied).
        METRICS: All metrics via metrics interface.
        
        Args:
            key: Cache key (validated by security interface)
            value: Value to cache (any type including None)
            ttl: Time-to-live in seconds (validated by security interface)
            source_module: Optional module name for LUGS (validated by security interface)
            
        Raises:
            ValueError: If validation fails (raised by security interface)
        """
        # SECURITY: Validate via security interface
        from gateway import validate_cache_key, validate_ttl, validate_module_name, increment_counter
        
        validate_cache_key(key)
        validate_ttl(ttl)
        
        if source_module:
            validate_module_name(source_module)
        
        # PURE CACHE LOGIC BEGINS HERE
        
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
        
        # METRICS: Track operation via metrics interface
        increment_counter('cache.total_sets')
        
        # Register with LUGS if source module provided
        if source_module:
            try:
                from gateway import add_cache_module_dependency
                add_cache_module_dependency(source_module, key)
            except (ImportError, Exception):
                pass
    
    def get(self, key: str) -> Any:
        """
        Get cached value if exists and not expired.
        
        METRICS: All metrics via metrics interface.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value, or special _CACHE_MISS sentinel if not found/expired.
        """
        from gateway import increment_counter, record_cache_metric
        
        # METRICS: Track total gets
        increment_counter('cache.total_gets')
        
        if key not in self._cache:
            # METRICS: Track cache miss (FIXED: use operation_name kwarg)
            record_cache_metric(operation_name='get', hit=False)
            return _CACHE_MISS
        
        entry = self._cache[key]
        current_time = time.time()
        
        # Check expiration
        if current_time - entry.timestamp > entry.ttl:
            self.current_bytes -= entry.value_size_bytes
            del self._cache[key]
            
            # METRICS: Track cache miss and expiration (FIXED: use operation_name kwarg)
            record_cache_metric(operation_name='get', hit=False)
            increment_counter('cache.entries_expired')
            return _CACHE_MISS
        
        # Update access tracking
        entry.access_count += 1
        entry.last_access = current_time
        
        # METRICS: Track cache hit (FIXED: use operation_name kwarg)
        record_cache_metric(operation_name='get', hit=True)
        return entry.value
    
    def exists(self, key: str) -> bool:
        """
        Check if key exists in cache and is not expired.
        
        Args:
            key: Cache key
            
        Returns:
            True if key exists and not expired, False otherwise
        """
        if key not in self._cache:
            return False
        
        entry = self._cache[key]
        current_time = time.time()
        
        # Check expiration
        if current_time - entry.timestamp > entry.ttl:
            from gateway import increment_counter
            
            self.current_bytes -= entry.value_size_bytes
            del self._cache[key]
            
            # METRICS: Track expiration
            increment_counter('cache.entries_expired')
            return False
        
        return True
    
    def delete(self, key: str) -> bool:
        """
        Delete cache entry.
        
        Args:
            key: Cache key
            
        Returns:
            True if key existed and was deleted, False if key didn't exist
        """
        if key in self._cache:
            entry = self._cache[key]
            self.current_bytes -= entry.value_size_bytes
            del self._cache[key]
            return True
        return False
    
    def clear(self) -> int:
        """
        Clear all cache entries.
        
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
        from gateway import increment_counter
        
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
        
        # METRICS: Track expirations
        if count > 0:
            increment_counter('cache.entries_expired', count)
        
        return count
    
    def get_metadata(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Fast metadata retrieval without value access (Issue #25).
        
        Args:
            key: Cache key
            
        Returns:
            Dictionary with metadata if key exists and not expired, None otherwise.
        """
        from gateway import increment_counter
        
        # METRICS: Track metadata queries
        increment_counter('cache.metadata_queries')
        
        if key not in self._cache:
            return None
        
        entry = self._cache[key]
        current_time = time.time()
        age = current_time - entry.timestamp
        
        # Check expiration
        if age > entry.ttl:
            self.current_bytes -= entry.value_size_bytes
            del self._cache[key]
            increment_counter('cache.entries_expired')
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
        """
        Get cache statistics (PURIFIED - only pure cache data).
        
        SIMPLIFIED: Returns ONLY cache-specific state data.
        For operation metrics (hits, misses, etc), use METRICS interface.
        For memory stats, use SINGLETON interface.
        
        Returns:
            Dictionary with cache state:
            - size: Number of entries
            - memory_bytes: Current memory usage
            - memory_mb: Current memory usage in MB
            - max_bytes: Maximum memory capacity
            - max_mb: Maximum capacity in MB
            - memory_utilization_percent: Memory utilization percentage
            - default_ttl_seconds: Default TTL value
        """
        return {
            'size': len(self._cache),
            'memory_bytes': self.current_bytes,
            'memory_mb': round(self.current_bytes / (1024 * 1024), 2),
            'max_bytes': self.max_bytes,
            'max_mb': round(self.max_bytes / (1024 * 1024), 2),
            'memory_utilization_percent': round((self.current_bytes / self.max_bytes) * 100, 2),
            'default_ttl_seconds': DEFAULT_CACHE_TTL
        }
    
    def get_module_dependencies(self) -> Set[str]:
        """
        Get set of all module names that have cache dependencies (LUGS tracking).
        
        Returns:
            Set of module names that have cached data
        """
        modules = set()
        for entry in self._cache.values():
            if entry.source_module:
                modules.add(entry.source_module)
        return modules


# ===== MODULE-LEVEL CACHE INSTANCE =====

_cache_instance = None


def _get_cache_instance() -> LUGSIntegratedCache:
    """Get or create cache singleton instance."""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = LUGSIntegratedCache()
    return _cache_instance


# ===== CACHE OPERATIONS =====

def cache_get(key: str) -> Any:
    """Get from cache."""
    cache = _get_cache_instance()
    return cache.get(key)


def cache_set(key: str, value: Any, ttl: int = DEFAULT_CACHE_TTL, source_module: Optional[str] = None) -> None:
    """Set cache entry."""
    cache = _get_cache_instance()
    cache.set(key, value, ttl, source_module)


def cache_exists(key: str) -> bool:
    """Check if key exists."""
    cache = _get_cache_instance()
    return cache.exists(key)


def cache_delete(key: str) -> bool:
    """Delete cache entry."""
    cache = _get_cache_instance()
    return cache.delete(key)


def cache_clear() -> int:
    """Clear all cache entries."""
    cache = _get_cache_instance()
    return cache.clear()


def cache_cleanup_expired() -> int:
    """Remove expired entries."""
    cache = _get_cache_instance()
    return cache.cleanup_expired()


def cache_get_stats() -> Dict[str, Any]:
    """Get cache statistics."""
    cache = _get_cache_instance()
    return cache.get_stats()


def cache_get_metadata(key: str) -> Optional[Dict[str, Any]]:
    """Get cache metadata."""
    cache = _get_cache_instance()
    return cache.get_metadata(key)


def cache_get_module_dependencies() -> Set[str]:
    """Get module dependencies."""
    cache = _get_cache_instance()
    return cache.get_module_dependencies()


# EOF
