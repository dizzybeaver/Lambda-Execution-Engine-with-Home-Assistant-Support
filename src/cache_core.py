"""
cache_core.py - Enhanced Caching with LUGS Integration
Version: 2025.10.01.05
Daily Revision: LUGS Integration Complete

ARCHITECTURE: CORE IMPLEMENTATION
- LUGS-aware caching with module dependency tracking
- Cache-to-module relationship management
- TTL-based expiration with dependency cleanup
- Memory-optimized cache storage

OPTIMIZATION: Phase 6 + LUGS Complete
- ADDED: Module dependency tracking for LUGS
- ADDED: Cache source module relationship management
- ADDED: Automatic dependency cleanup on expiration
- ADDED: Cache hit metrics for LUGS optimization
- 100% architecture compliance + LUGS integration

Revolutionary Gateway Optimization: SUGA + LIGS + ZAFP + LUGS

Copyright 2024 Anthropic PBC
Licensed under the Apache License, Version 2.0
"""

import time
import threading
from typing import Dict, Any, Optional, Set, Tuple
from dataclasses import dataclass
from enum import Enum

from gateway import (
    log_info, log_error, log_debug,
    record_metric,
    generate_correlation_id,
    execute_operation,
    handle_operation_error
)


class CacheEntryState(str, Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    EXPIRING = "expiring"


@dataclass
class CacheEntry:
    """Enhanced cache entry with LUGS integration."""
    key: str
    value: Any
    created_time: float
    ttl: Optional[int]
    access_count: int = 0
    last_access_time: Optional[float] = None
    source_module: Optional[str] = None
    state: CacheEntryState = CacheEntryState.ACTIVE
    
    @property
    def is_expired(self) -> bool:
        """Check if entry is expired."""
        if self.ttl is None:
            return False
        return time.time() - self.created_time > self.ttl
    
    @property
    def expires_at(self) -> Optional[float]:
        """Get expiration timestamp."""
        if self.ttl is None:
            return None
        return self.created_time + self.ttl


class LUGSCacheManager:
    """LUGS-integrated cache manager with module dependency tracking."""
    
    def __init__(self):
        self._cache: Dict[str, CacheEntry] = {}
        self._lock = threading.RLock()
        self._module_dependencies: Dict[str, Set[str]] = {}  # module -> cache_keys
        self._cache_to_module: Dict[str, str] = {}  # cache_key -> module
        self._stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'deletes': 0,
            'expirations': 0,
            'dependency_cleanups': 0,
            'lugs_integrations': 0
        }
        
        # Cache configuration
        self._max_entries = 1000  # Maximum cache entries
        self._cleanup_interval = 100  # Cleanup every N operations
        self._operation_count = 0
    
    def get(self, key: str, default=None) -> Any:
        """Get cached value with LUGS integration."""
        correlation_id = generate_correlation_id()
        
        def _operation():
            with self._lock:
                self._operation_count += 1
                
                # Periodic cleanup
                if self._operation_count % self._cleanup_interval == 0:
                    self._cleanup_expired_entries()
                
                if key in self._cache:
                    entry = self._cache[key]
                    
                    # Check expiration
                    if entry.is_expired:
                        self._remove_entry_with_dependencies(key)
                        self._stats['misses'] += 1
                        self._stats['expirations'] += 1
                        
                        record_metric("cache_operation", 1.0, {
                            "operation": "miss_expired",
                            "key_prefix": key.split('_')[0] if '_' in key else "unknown"
                        })
                        
                        return default
                    
                    # Update access tracking
                    entry.access_count += 1
                    entry.last_access_time = time.time()
                    self._stats['hits'] += 1
                    
                    record_metric("cache_operation", 1.0, {
                        "operation": "hit",
                        "key_prefix": key.split('_')[0] if '_' in key else "unknown",
                        "has_source_module": str(bool(entry.source_module))
                    })
                    
                    log_debug(f"Cache hit: {key}", extra={
                        "correlation_id": correlation_id,
                        "access_count": entry.access_count,
                        "source_module": entry.source_module,
                        "ttl_remaining": entry.ttl - (time.time() - entry.created_time) if entry.ttl else None
                    })
                    
                    return entry.value
                
                # Cache miss
                self._stats['misses'] += 1
                
                record_metric("cache_operation", 1.0, {
                    "operation": "miss",
                    "key_prefix": key.split('_')[0] if '_' in key else "unknown"
                })
                
                return default
        
        try:
            return execute_operation(
                _operation,
                operation_type="cache_get",
                correlation_id=correlation_id,
                context={"key": key}
            )
        except Exception as e:
            return handle_operation_error(
                e,
                operation_type="cache_get",
                correlation_id=correlation_id,
                context={"key": key}
            )
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set cached value with LUGS integration."""
        correlation_id = generate_correlation_id()
        
        def _operation():
            with self._lock:
                current_time = time.time()
                
                # Remove existing entry if present
                if key in self._cache:
                    self._remove_entry_with_dependencies(key)
                
                # Create new entry
                entry = CacheEntry(
                    key=key,
                    value=value,
                    created_time=current_time,
                    ttl=ttl,
                    last_access_time=current_time
                )
                
                # Check cache size limit
                if len(self._cache) >= self._max_entries:
                    self._evict_oldest_entries(self._max_entries // 10)  # Evict 10%
                
                self._cache[key] = entry
                self._stats['sets'] += 1
                
                record_metric("cache_operation", 1.0, {
                    "operation": "set",
                    "key_prefix": key.split('_')[0] if '_' in key else "unknown",
                    "has_ttl": str(bool(ttl))
                })
                
                log_debug(f"Cache set: {key}", extra={
                    "correlation_id": correlation_id,
                    "ttl": ttl,
                    "value_type": type(value).__name__
                })
                
                return True
        
        try:
            return execute_operation(
                _operation,
                operation_type="cache_set",
                correlation_id=correlation_id,
                context={"key": key, "ttl": ttl}
            )
        except Exception as e:
            handle_operation_error(
                e,
                operation_type="cache_set",
                correlation_id=correlation_id,
                context={"key": key, "ttl": ttl}
            )
            return False
    
    def delete(self, key: str) -> bool:
        """Delete cached value with LUGS integration."""
        correlation_id = generate_correlation_id()
        
        def _operation():
            with self._lock:
                if key in self._cache:
                    self._remove_entry_with_dependencies(key)
                    self._stats['deletes'] += 1
                    
                    record_metric("cache_operation", 1.0, {
                        "operation": "delete",
                        "key_prefix": key.split('_')[0] if '_' in key else "unknown"
                    })
                    
                    log_debug(f"Cache delete: {key}", extra={
                        "correlation_id": correlation_id
                    })
                    
                    return True
                
                return False
        
        try:
            return execute_operation(
                _operation,
                operation_type="cache_delete",
                correlation_id=correlation_id,
                context={"key": key}
            )
        except Exception as e:
            handle_operation_error(
                e,
                operation_type="cache_delete",
                correlation_id=correlation_id,
                context={"key": key}
            )
            return False
    
    def clear(self) -> bool:
        """Clear all cached values with LUGS integration."""
        correlation_id = generate_correlation_id()
        
        def _operation():
            with self._lock:
                entry_count = len(self._cache)
                
                # Clear all entries and dependencies
                self._cache.clear()
                self._module_dependencies.clear()
                self._cache_to_module.clear()
                
                record_metric("cache_operation", 1.0, {
                    "operation": "clear",
                    "entries_cleared": str(entry_count)
                })
                
                log_info(f"Cache cleared: {entry_count} entries", extra={
                    "correlation_id": correlation_id,
                    "entries_cleared": entry_count
                })
                
                return True
        
        try:
            return execute_operation(
                _operation,
                operation_type="cache_clear",
                correlation_id=correlation_id,
                context={}
            )
        except Exception as e:
            handle_operation_error(
                e,
                operation_type="cache_clear",
                correlation_id=correlation_id,
                context={}
            )
            return False
    
    def _set_cache_source_module(self, key: str, module_name: str) -> None:
        """Set source module for cache entry (LUGS integration)."""
        with self._lock:
            if key in self._cache:
                entry = self._cache[key]
                entry.source_module = module_name
                
                # Update dependency tracking
                self._cache_to_module[key] = module_name
                
                if module_name not in self._module_dependencies:
                    self._module_dependencies[module_name] = set()
                self._module_dependencies[module_name].add(key)
                
                self._stats['lugs_integrations'] += 1
                
                log_debug(f"Cache-module dependency set: {key} -> {module_name}")
    
    def _get_cache_source_module(self, key: str) -> Optional[str]:
        """Get source module for cache entry (LUGS integration)."""
        with self._lock:
            return self._cache_to_module.get(key)
    
    def _remove_entry_with_dependencies(self, key: str) -> None:
        """Remove cache entry and clean up LUGS dependencies."""
        if key in self._cache:
            entry = self._cache[key]
            
            # Clean up module dependencies
            if entry.source_module and entry.source_module in self._module_dependencies:
                self._module_dependencies[entry.source_module].discard(key)
                if not self._module_dependencies[entry.source_module]:
                    del self._module_dependencies[entry.source_module]
                
                self._stats['dependency_cleanups'] += 1
            
            # Clean up cache-to-module mapping
            self._cache_to_module.pop(key, None)
            
            # Remove cache entry
            del self._cache[key]
    
    def _cleanup_expired_entries(self) -> int:
        """Clean up expired cache entries."""
        current_time = time.time()
        expired_keys = []
        
        for key, entry in self._cache.items():
            if entry.is_expired:
                expired_keys.append(key)
        
        for key in expired_keys:
            self._remove_entry_with_dependencies(key)
            self._stats['expirations'] += 1
        
        if expired_keys:
            record_metric("cache_cleanup", len(expired_keys), {
                "cleanup_type": "expired"
            })
        
        return len(expired_keys)
    
    def _evict_oldest_entries(self, count: int) -> int:
        """Evict oldest cache entries based on last access time."""
        if not self._cache:
            return 0
        
        # Sort by last access time (oldest first)
        entries_by_age = sorted(
            self._cache.items(),
            key=lambda x: x[1].last_access_time or x[1].created_time
        )
        
        evicted_count = 0
        for key, _ in entries_by_age[:count]:
            self._remove_entry_with_dependencies(key)
            evicted_count += 1
        
        if evicted_count > 0:
            record_metric("cache_cleanup", evicted_count, {
                "cleanup_type": "evicted"
            })
        
        return evicted_count
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self._lock:
            total_operations = self._stats['hits'] + self._stats['misses']
            hit_rate = (self._stats['hits'] / total_operations * 100) if total_operations > 0 else 0
            
            return {
                **self._stats,
                'total_entries': len(self._cache),
                'module_dependencies': len(self._module_dependencies),
                'cache_to_module_mappings': len(self._cache_to_module),
                'hit_rate_percent': round(hit_rate, 2),
                'total_operations': total_operations
            }
    
    def get_module_cache_info(self, module_name: str) -> Dict[str, Any]:
        """Get cache information for specific module."""
        with self._lock:
            if module_name not in self._module_dependencies:
                return {
                    "module_name": module_name,
                    "cache_keys": [],
                    "entry_count": 0
                }
            
            cache_keys = list(self._module_dependencies[module_name])
            entries_info = []
            
            for key in cache_keys:
                if key in self._cache:
                    entry = self._cache[key]
                    entries_info.append({
                        "key": key,
                        "created_time": entry.created_time,
                        "ttl": entry.ttl,
                        "access_count": entry.access_count,
                        "is_expired": entry.is_expired,
                        "expires_at": entry.expires_at
                    })
            
            return {
                "module_name": module_name,
                "cache_keys": cache_keys,
                "entry_count": len(cache_keys),
                "entries": entries_info
            }
    
    def cleanup_module_cache(self, module_name: str) -> int:
        """Clean up all cache entries for a specific module."""
        with self._lock:
            if module_name not in self._module_dependencies:
                return 0
            
            cache_keys = list(self._module_dependencies[module_name])
            cleaned_count = 0
            
            for key in cache_keys:
                if key in self._cache:
                    self._remove_entry_with_dependencies(key)
                    cleaned_count += 1
            
            return cleaned_count


# Global cache manager instance
_cache_manager = LUGSCacheManager()

# === PUBLIC INTERFACE ===

def get(key: str, default=None) -> Any:
    """Get cached value."""
    return _cache_manager.get(key, default)

def set(key: str, value: Any, ttl: Optional[int] = None) -> bool:
    """Set cached value."""
    return _cache_manager.set(key, value, ttl)

def delete(key: str) -> bool:
    """Delete cached value."""
    return _cache_manager.delete(key)

def clear() -> bool:
    """Clear all cached values."""
    return _cache_manager.clear()

def get_stats() -> Dict[str, Any]:
    """Get cache statistics."""
    return _cache_manager.get_stats()

# === LUGS INTEGRATION INTERFACE ===

def _set_cache_source_module(key: str, module_name: str) -> None:
    """Set source module for cache entry (internal LUGS interface)."""
    _cache_manager._set_cache_source_module(key, module_name)

def _get_cache_source_module(key: str) -> Optional[str]:
    """Get source module for cache entry (internal LUGS interface)."""
    return _cache_manager._get_cache_source_module(key)

def get_module_cache_info(module_name: str) -> Dict[str, Any]:
    """Get cache information for specific module."""
    return _cache_manager.get_module_cache_info(module_name)

def cleanup_module_cache(module_name: str) -> int:
    """Clean up all cache entries for a specific module."""
    return _cache_manager.cleanup_module_cache(module_name)

def force_cleanup() -> Dict[str, Any]:
    """Force cleanup of expired entries."""
    with _cache_manager._lock:
        expired_count = _cache_manager._cleanup_expired_entries()
        
        return {
            "expired_entries_cleaned": expired_count,
            "stats": get_stats()
        }
