"""
cache_core.py - LUGS-Integrated Cache System
Version: 2025.10.20.05
Description: In-memory cache with LUGS tracking, metrics integration, and TTL expiration

DEPENDENCY RULES (SUGA-ISP):
- Cross-interface imports ONLY via gateway.py
- Metrics: via gateway.record_cache_metric(), gateway.increment_counter()
- Logging: via gateway.log_*()
- Security: via gateway.validate_*()

INTERFACE ACCESS:
- interface_cache.py imports THIS file's _execute_*_implementation functions
- External code imports ONLY from gateway.py

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
import sys
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional, Set

# ===== CONFIGURATION =====

DEFAULT_CACHE_TTL = 300  # 5 minutes default TTL
MAX_CACHE_BYTES = 100 * 1024 * 1024  # 100MB limit

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
    In-memory cache with LUGS integration and metrics.
    
    Features:
    - TTL-based expiration
    - LRU eviction on memory pressure
    - Module dependency tracking for LUGS
    - Metrics integration via gateway
    - Memory-bounded (100MB default)
    """
    
    def __init__(self, max_bytes: int = MAX_CACHE_BYTES):
        self._cache: Dict[str, CacheEntry] = {}
        self.max_bytes = max_bytes
        self.current_bytes = 0
    
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
        try:
            from gateway import validate_cache_key, validate_ttl, validate_module_name, increment_counter
            
            validate_cache_key(key)
            validate_ttl(ttl)
            
            if source_module:
                validate_module_name(source_module)
        except ImportError:
            # Gateway validators not available - skip validation
            # This allows cache to work even if security interface unavailable
            from gateway import increment_counter
        
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
        
        Args:
            key: Cache key
            
        Returns:
            Cached value, or special _CACHE_MISS sentinel if not found/expired.
        """
        try:
            from gateway import record_cache_metric, increment_counter
        except ImportError:
            # Gateway not available - return miss
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
        """
        Check if key exists and is not expired.
        
        Args:
            key: Cache key
            
        Returns:
            True if key exists and not expired, False otherwise
        """
        if key not in self._cache:
            return False
        
        entry = self._cache[key]
        current_time = time.time()
        age = current_time - entry.timestamp
        
        # Check expiration
        if age > entry.ttl:
            # Remove expired entry
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
        """
        Delete cache entry if it exists.
        
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
        """
        Fast metadata retrieval without value access (Issue #25).
        
        Args:
            key: Cache key
            
        Returns:
            Dictionary with metadata if key exists and not expired, None otherwise.
        """
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


# ===== CACHE OPERATIONS (for backward compatibility) =====

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


# ===== INTERFACE IMPLEMENTATION WRAPPERS =====
# These functions are imported by interface_cache.py

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
    
    # Types
    'CacheOperation',
    'CacheEntry',
    
    # Main class
    'LUGSIntegratedCache',
    
    # Module-level operations (backward compatibility)
    'cache_get',
    'cache_set',
    'cache_exists',
    'cache_delete',
    'cache_clear',
    'cache_cleanup_expired',
    'cache_get_stats',
    'cache_get_metadata',
    'cache_get_module_dependencies',
    
    # Interface implementation wrappers (for interface_cache.py)
    '_execute_get_implementation',
    '_execute_set_implementation',
    '_execute_exists_implementation',
    '_execute_delete_implementation',
    '_execute_clear_implementation',
    '_execute_cleanup_expired_implementation',
    '_execute_get_stats_implementation',
    '_execute_get_metadata_implementation',
    '_execute_get_module_dependencies_implementation',
]

# EOF
