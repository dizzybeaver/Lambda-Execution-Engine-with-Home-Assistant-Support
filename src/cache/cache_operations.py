"""
cache/cache_operations.py
Version: 2025-12-08_1
Purpose: Module-level cache operations and interface wrappers
License: Apache 2.0
"""

from typing import Any, Dict, Optional, Set

from cache.cache_core import _get_cache_instance
from cache import DEFAULT_CACHE_TTL


def cache_get(key: str) -> Any:
    """Get value from cache."""
    cache = _get_cache_instance()
    return cache.get(key)


def cache_set(key: str, value: Any, ttl: int = DEFAULT_CACHE_TTL, source_module: Optional[str] = None) -> None:
    """Set cache entry."""
    cache = _get_cache_instance()
    cache.set(key, value, ttl, source_module)


def cache_exists(key: str) -> bool:
    """Check if key exists in cache."""
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
    """Reset cache to initial state."""
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
    """Get cache entry metadata."""
    cache = _get_cache_instance()
    return cache.get_metadata(key)


def cache_get_module_dependencies() -> Set[str]:
    """Get module dependencies."""
    cache = _get_cache_instance()
    return cache.get_module_dependencies()


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
    """Implementation wrapper for cache reset operation."""
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


__all__ = [
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
