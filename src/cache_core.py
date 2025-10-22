"""
cache_core.py - LUGS-Integrated Cache System
Version: 2025.10.21.01
Description: In-memory cache with LUGS tracking, metrics, TTL, rate limiting

CHANGELOG:
- 2025.10.21.01: PHASE 1 OPTIMIZATION
  - Added rate limiting (1000 ops/sec, similar to METRICS)
  - Added reset method for testing
  - Updated _get_cache_instance() for SINGLETON pattern
  - Improved documentation
  - No breaking changes

- 2025.10.20.05: Security validations, LUGS integration

DEPENDENCY RULES (SUGA-ISP):
- Cross-interface imports ONLY via gateway.py
- Metrics: via gateway.record_cache_metric(), gateway.increment_counter()
- Logging: via gateway.log_*()
- Security: via gateway.validate_*()

Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

import time
import sys
from collections import deque
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional, Set

# ===== CONFIGURATION =====

DEFAULT_CACHE_TTL = 300  # 5 minutes default TTL
MAX_CACHE_BYTES = 100 * 1024 * 1024  # 100MB limit
RATE_LIMIT_WINDOW_MS = 1000  # 1 second window
RATE_LIMIT_MAX_OPS = 1000  # Max operations per window

# ===== CACHE MISS SENTINEL =====

class _CacheMiss:
    """Sentinel value for cache misses."""
    def __repr__(self):
        return '<CACHE_MISS>'

_CACHE_MISS = _CacheMiss()

# ===== CACHE TYPES =====

class CacheOperation(str, Enum):
    """Cache operation types for metrics."""
    GET = 'get'
    SET = 'set'
    DELETE = 'delete'
    CLEAR = 'clear'
    CLEANUP = 'cleanup'

@dataclass
class CacheEntry:
    """Cache entry with metadata."""
    value: Any
    timestamp: float
    ttl: int
    source_module: Optional[str]
    access_count: int
    last_access: float
    value_size_bytes: int

# ===== CACHE IMPLEMENTATION =====

class LUGSIntegratedCache:
    """
    In-memory cache with LUGS integration, metrics, and rate limiting.
    
    Features:
    - TTL-based expiration
    - LRU eviction on memory pressure
    - Module dependency tracking for LUGS
    - Metrics integration via gateway
    - Memory-bounded (100MB default)
    - Rate limiting (1000 ops/sec)
    - DoS protection
    """
    
    def __init__(self, max_bytes: int = MAX_CACHE_BYTES):
        self._cache: Dict[str, CacheEntry] = {}
        self.max_bytes = max_bytes
        self.current_bytes = 0
        
        # Rate limiting (Phase 1 addition)
        self._rate_limiter = deque(maxlen=RATE_LIMIT_MAX_OPS)
        self._rate_limit_window_ms = RATE_LIMIT_WINDOW_MS
        self._rate_limited_count = 0
    
    def _check_rate_limit(self) -> bool:
        """
        Check if rate limit exceeded.
        
        Uses sliding window rate limiter (1000 ops/sec default).
        Same pattern as METRICS interface (LESS-21).
        
        Returns:
            True if operation allowed, False if rate limited
        """
        now = time.time() * 1000  # Convert to milliseconds
        
        # Clean old timestamps outside window
        while self._rate_limiter and (now - self._rate_limiter[0]) > self._rate_limit_window_ms:
            self._rate_limiter.popleft()
        
        # Check limit
        if len(self._rate_limiter) >= RATE_LIMIT_MAX_OPS:
            self._rate_limited_count += 1
            return False  # Rate limited
        
        self._rate_limiter.append(now)
        return True
    
    def _calculate_entry_size(self, key: str, value: Any) -> int:
        """Estimate memory size of cache entry."""
        try:
            key_size = sys.getsizeof(key)
            value_size = sys.getsizeof(value)
            metadata_size = 200  # Approximate overhead for CacheEntry
            return key_size + value_size + metadata_size
        except Exception:
            return 1024  # Default estimate
    
    def _check_memory_pressure(self) -> bool:
        """Check if cache is under memory pressure (>80% full)."""
        return self.current_bytes > (self.max_bytes * 0.8)
    
    def _evict_lru_entries(self, bytes_needed: int) -> int:
        """Evict least recently used entries to free memory."""
        if not self._cache:
            return 0
        
        # Sort by last access time
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
        
        # METRICS: Track evictions
        if evicted_count > 0:
            try:
                from gateway import increment_counter
                increment_counter('cache.entries_evicted', evicted_count)
            except (ImportError, Exception):
                pass
        
        return evicted_count
    
    def _handle_memory_pressure(self) -> None:
        """Handle memory pressure by evicting entries."""
        bytes_to_free = int(self.max_bytes * 0.2)  # Free 20%
        self._evict_lru_entries(bytes_to_free)
    
    def set(self, key: str, value: Any, ttl: int = DEFAULT_CACHE_TTL, source_module: Optional[str] = None) -> None:
        """
        Set cache entry with TTL and optional module tracking.
        
        SECURITY: Validation via security interface (CVE fixes applied).
        METRICS: All metrics via metrics interface.
        RATE LIMITING: DoS protection (Phase 1 addition).
        
        Args:
            key: Cache key (validated by security interface)
            value: Value to cache (any type including None)
            ttl: Time-to-live in seconds (validated by security interface)
            source_module: Optional module name for LUGS (validated by security interface)
            
        Raises:
            ValueError: If validation fails (raised by security interface)
        """
        # RATE LIMITING: Check before processing (Phase 1)
        if not self._check_rate_limit():
            return  # Silently drop (cache ops don't crash app)
        
        # SECURITY: Validate via security interface
        try:
            from gateway import validate_cache_key, validate_ttl, validate_module_name, increment_counter
            
            validate_cache_key(key)
            validate_ttl(ttl)
            
            if source_module:
                validate_module_name(source_module)
        except ImportError:
            # Gateway validators not available - skip validation
            from gateway import increment_counter
        
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
        
        # METRICS: Track operation
        try:
            increment_counter('cache.total_sets')
        except Exception:
            pass
        
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
        RATE LIMITING: DoS protection (Phase 1 addition).
        
        Args:
            key: Cache key
            
        Returns:
            Cached value, or special _CACHE_MISS sentinel if not found/expired.
        """
        # RATE LIMITING: Check before processing (Phase 1)
        if not self._check_rate_limit():
            return _CACHE_MISS  # Silently return miss
        
        try:
            from gateway import record_cache_metric, increment_counter
        except ImportError:
            return _CACHE_MISS
        
        if key not in self._cache:
            # METRICS: Track miss
            try:
                record_cache_metric(operation_name='get', hit=False)
            except Exception:
                pass
            return _CACHE_MISS
        
        entry = self._cache[key]
        current_time = time.time()
        age = current_time - entry.timestamp
        
        # Check expiration
        if age > entry.ttl:
            # Remove expired entry
            self.current_bytes -= entry.value_size_bytes
            del self._cache[key]
            
            # METRICS: Track expiration and miss
            try:
                increment_counter('cache.entries_expired')
                record_cache_metric(operation_name='get', hit=False)
            except Exception:
                pass
            return _CACHE_MISS
        
        # Update access metadata
        entry.access_count += 1
        entry.last_access = current_time
        
        # METRICS: Track hit
        try:
            record_cache_metric(operation_name='get', hit=True)
        except Exception:
            pass
        
        return entry.value
    
    def exists(self, key: str) -> bool:
        """Check if key exists and is not expired."""
        # RATE LIMITING: Check before processing
        if not self._check_rate_limit():
            return False  # Silently return false
        
        if key not in self._cache:
            return False
        
        entry = self._cache[key]
        current_time = time.time()
        age = current_time - entry.timestamp
        
        # Check expiration
        if age > entry.ttl:
            self.current_bytes -= entry.value_size_bytes
            del self._cache[key]
            
            # METRICS: Track expiration
            try:
                from gateway import increment_counter
                increment_counter('cache.entries_expired')
            except (ImportError, Exception):
                pass
            
            return False
        
        return True
    
    def delete(self, key: str) -> bool:
        """Delete cache entry if it exists."""
        # RATE LIMITING: Check before processing
        if not self._check_rate_limit():
            return False  # Silently return false
        
        if key in self._cache:
            entry = self._cache[key]
            self.current_bytes -= entry.value_size_bytes
            del self._cache[key]
            return True
        return False
    
    def clear(self) -> int:
        """Clear all cache entries."""
        # RATE LIMITING: Check before processing
        if not self._check_rate_limit():
            return 0  # Silently return 0
        
        count = len(self._cache)
        self._cache.clear()
        self.current_bytes = 0
        return count
    
    def reset(self) -> bool:
        """
        Reset cache to initial state (Phase 1 addition).
        
        Clears all entries and resets stats.
        Useful for testing and debugging.
        
        Returns:
            True on success
        """
        self._cache.clear()
        self.current_bytes = 0
        self._rate_limiter.clear()
        self._rate_limited_count = 0
        return True
    
    def cleanup_expired(self) -> int:
        """Remove all expired entries."""
        # RATE LIMITING: Check before processing
        if not self._check_rate_limit():
            return 0  # Silently return 0
        
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
        
        # METRICS: Track expirations
        if count > 0 and increment_counter:
            try:
                increment_counter('cache.entries_expired', count)
            except Exception:
                pass
        
        return count
    
    def get_metadata(self, key: str) -> Optional[Dict[str, Any]]:
        """Fast metadata retrieval without value access."""
        # RATE LIMITING: Check before processing
        if not self._check_rate_limit():
            return None  # Silently return None
        
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
        
        # Check expiration
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
        """
        Get cache statistics.
        
        Returns only cache-specific state data.
        For operation metrics, use METRICS interface.
        For memory stats, use SINGLETON interface.
        
        Phase 1 additions: rate_limited_count
        """
        return {
            'size': len(self._cache),
            'memory_bytes': self.current_bytes,
            'memory_mb': round(self.current_bytes / (1024 * 1024), 2),
            'max_bytes': self.max_bytes,
            'max_mb': round(self.max_bytes / (1024 * 1024), 2),
            'memory_utilization_percent': round((self.current_bytes / self.max_bytes) * 100, 2),
            'default_ttl_seconds': DEFAULT_CACHE_TTL,
            'rate_limited_count': self._rate_limited_count  # Phase 1 addition
        }
    
    def get_module_dependencies(self) -> Set[str]:
        """Get set of all module names that have cache dependencies."""
        modules = set()
        for entry in self._cache.values():
            if entry.source_module:
                modules.add(entry.source_module)
        return modules


# ===== MODULE-LEVEL CACHE INSTANCE =====

_cache_instance = None


def _get_cache_instance() -> LUGSIntegratedCache:
    """
    Get or create cache singleton instance.
    
    SINGLETON Pattern (Phase 1 addition):
    Tries to use SINGLETON interface for lifecycle management.
    Falls back to module-level singleton if SINGLETON unavailable.
    
    Returns:
        LUGSIntegratedCache instance
    """
    global _cache_instance
    
    # Try SINGLETON interface first (Phase 1)
    try:
        from gateway import singleton_get, singleton_register
        
        manager = singleton_get('cache_manager')
        if manager is None:
            manager = LUGSIntegratedCache()
            singleton_register('cache_manager', manager)
        
        return manager
    except (ImportError, Exception):
        # Fallback to module-level singleton
        if _cache_instance is None:
            _cache_instance = LUGSIntegratedCache()
        return _cache_instance


# ===== CACHE OPERATIONS (backward compatibility) =====

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


def cache_reset() -> bool:
    """Reset cache (Phase 1 addition)."""
    cache = _get_cache_instance()
    return cache.reset()


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


# ===== INTERFACE IMPLEMENTATION WRAPPERS =====

def _execute_get_implementation(key: str, **kwargs) -> Any:
    """Implementation wrapper for cache get operation."""
    cache = _get_cache_instance()
    return cache.get(key)


def _execute_set_implementation(key: str, value: Any, ttl: int = DEFAULT_CACHE_TTL, source_module: Optional[str] = None, **kwargs) -> None:
    """Implementation wrapper for cache set operation."""
    cache = _get_cache_instance()
    cache.set(key, value, ttl, source_module)


def _execute_exists_implementation(key: str, **kwargs) -> bool:
    """Implementation wrapper for cache exists operation."""
    cache = _get_cache_instance()
    return cache.exists(key)


def _execute_delete_implementation(key: str, **kwargs) -> bool:
    """Implementation wrapper for cache delete operation."""
    cache = _get_cache_instance()
    return cache.delete(key)


def _execute_clear_implementation(**kwargs) -> int:
    """Implementation wrapper for cache clear operation."""
    cache = _get_cache_instance()
    return cache.clear()


def _execute_reset_implementation(**kwargs) -> bool:
    """Implementation wrapper for cache reset operation (Phase 1 addition)."""
    cache = _get_cache_instance()
    return cache.reset()


def _execute_cleanup_expired_implementation(**kwargs) -> int:
    """Implementation wrapper for cache cleanup operation."""
    cache = _get_cache_instance()
    return cache.cleanup_expired()


def _execute_get_stats_implementation(**kwargs) -> Dict[str, Any]:
    """Implementation wrapper for cache stats operation."""
    cache = _get_cache_instance()
    return cache.get_stats()


def _execute_get_metadata_implementation(key: str, **kwargs) -> Optional[Dict[str, Any]]:
    """Implementation wrapper for cache metadata operation."""
    cache = _get_cache_instance()
    return cache.get_metadata(key)


def _execute_get_module_dependencies_implementation(**kwargs) -> Set[str]:
    """Implementation wrapper for module dependencies operation."""
    cache = _get_cache_instance()
    return cache.get_module_dependencies()


# ===== MODULE EXPORTS =====

__all__ = [
    # Constants
    'DEFAULT_CACHE_TTL',
    'MAX_CACHE_BYTES',
    'RATE_LIMIT_WINDOW_MS',
    'RATE_LIMIT_MAX_OPS',
    
    # Types
    'CacheOperation',
    'CacheEntry',
    
    # Main class
    'LUGSIntegratedCache',
    
    # Module-level operations
    'cache_get',
    'cache_set',
    'cache_exists',
    'cache_delete',
    'cache_clear',
    'cache_reset',
    'cache_cleanup_expired',
    'cache_get_stats',
    'cache_get_metadata',
    'cache_get_module_dependencies',
    
    # Interface implementation wrappers
    '_execute_get_implementation',
    '_execute_set_implementation',
    '_execute_exists_implementation',
    '_execute_delete_implementation',
    '_execute_clear_implementation',
    '_execute_reset_implementation',
    '_execute_cleanup_expired_implementation',
    '_execute_get_stats_implementation',
    '_execute_get_metadata_implementation',
    '_execute_get_module_dependencies_implementation',
]

# EOF
