"""
Cache Core - In-Memory Caching Implementation
Version: 2025.09.30.02
Description: Cache implementation with shared utilities integration

ARCHITECTURE: CORE IMPLEMENTATION - INTERNAL ONLY
- Lazy-loaded by gateway.py
- Uses shared_utilities for operation metrics

OPTIMIZATION: Phase 1 Complete
- Integrated record_operation_metrics() from shared_utilities
- Consistent metric recording patterns
- Enhanced observability

Revolutionary Gateway Optimization: SUGA + LIGS + ZAFP Compatible

Copyright 2024 Anthropic PBC
Licensed under the Apache License, Version 2.0
"""

import time
from typing import Any, Optional, Dict
from threading import Lock


class CacheCore:
    """Thread-safe in-memory cache with TTL support and metrics integration."""
    
    def __init__(self):
        self._cache: Dict[str, tuple] = {}
        self._lock = Lock()
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get value from cache with metrics tracking."""
        start_time = time.time()
        success = True
        
        try:
            with self._lock:
                if key in self._cache:
                    value, expiry = self._cache[key]
                    if expiry is None or expiry > time.time():
                        return value
                    else:
                        del self._cache[key]
                        success = False
                else:
                    success = False
                return default
        finally:
            execution_time = (time.time() - start_time) * 1000
            self._record_metrics("get", execution_time, success)
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache with optional TTL and metrics tracking."""
        start_time = time.time()
        success = True
        
        try:
            with self._lock:
                expiry = None if ttl is None else time.time() + ttl
                self._cache[key] = (value, expiry)
                return True
        except Exception:
            success = False
            return False
        finally:
            execution_time = (time.time() - start_time) * 1000
            self._record_metrics("set", execution_time, success)
    
    def delete(self, key: str) -> bool:
        """Delete key from cache with metrics tracking."""
        start_time = time.time()
        success = False
        
        try:
            with self._lock:
                if key in self._cache:
                    del self._cache[key]
                    success = True
                return success
        finally:
            execution_time = (time.time() - start_time) * 1000
            self._record_metrics("delete", execution_time, success)
    
    def clear(self) -> bool:
        """Clear all cache entries with metrics tracking."""
        start_time = time.time()
        success = True
        
        try:
            with self._lock:
                self._cache.clear()
                return True
        except Exception:
            success = False
            return False
        finally:
            execution_time = (time.time() - start_time) * 1000
            self._record_metrics("clear", execution_time, success)
    
    def cleanup_expired(self) -> int:
        """Remove expired entries with metrics tracking."""
        start_time = time.time()
        count = 0
        success = True
        
        try:
            with self._lock:
                expired_keys = [
                    k for k, (_, exp) in self._cache.items()
                    if exp is not None and exp <= time.time()
                ]
                for key in expired_keys:
                    del self._cache[key]
                    count += 1
            return count
        except Exception:
            success = False
            return 0
        finally:
            execution_time = (time.time() - start_time) * 1000
            self._record_metrics("cleanup", execution_time, success, cleaned=count)
    
    def _record_metrics(self, operation: str, execution_time: float, success: bool, **dimensions):
        """Record operation metrics using shared utilities."""
        try:
            from .shared_utilities import record_operation_metrics
            record_operation_metrics(
                interface="cache",
                operation=operation,
                execution_time=execution_time,
                success=success,
                **dimensions
            )
        except Exception:
            pass


_CACHE = CacheCore()


def _execute_get_implementation(key: str, default: Any = None, **kwargs) -> Any:
    """Execute cache get operation."""
    return _CACHE.get(key, default)


def _execute_set_implementation(key: str, value: Any, ttl: Optional[int] = None, **kwargs) -> bool:
    """Execute cache set operation."""
    return _CACHE.set(key, value, ttl)


def _execute_delete_implementation(key: str, **kwargs) -> bool:
    """Execute cache delete operation."""
    return _CACHE.delete(key)


def _execute_clear_implementation(**kwargs) -> bool:
    """Execute cache clear operation."""
    return _CACHE.clear()


def _execute_cleanup_implementation(**kwargs) -> int:
    """Execute cache cleanup operation."""
    return _CACHE.cleanup_expired()


__all__ = [
    '_execute_get_implementation',
    '_execute_set_implementation',
    '_execute_delete_implementation',
    '_execute_clear_implementation',
    '_execute_cleanup_implementation',
]

# EOF
