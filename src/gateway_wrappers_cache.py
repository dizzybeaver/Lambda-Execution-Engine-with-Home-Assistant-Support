"""
gateway_wrappers_cache.py - CACHE Interface Wrappers
Version: 2025.10.22.02
Description: Convenience wrappers for CACHE interface operations

Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any, Dict, Optional
from gateway_core import GatewayInterface, execute_operation


def cache_get(key: str) -> Any:
    """Get cached value."""
    return execute_operation(GatewayInterface.CACHE, 'get', key=key)


def cache_set(key: str, value: Any, ttl: Optional[float] = None, **kwargs) -> None:
    """Set cached value."""
    execute_operation(GatewayInterface.CACHE, 'set', key=key, value=value, ttl=ttl, **kwargs)


def cache_exists(key: str) -> bool:
    """Check if cache key exists."""
    return execute_operation(GatewayInterface.CACHE, 'exists', key=key)


def cache_delete(key: str) -> bool:
    """Delete cache key."""
    return execute_operation(GatewayInterface.CACHE, 'delete', key=key)


def cache_clear() -> None:
    """Clear all cache."""
    execute_operation(GatewayInterface.CACHE, 'clear')


def cache_stats() -> Dict[str, Any]:
    """Get cache statistics."""
    return execute_operation(GatewayInterface.CACHE, 'get_stats')


__all__ = [
    'cache_get',
    'cache_set',
    'cache_exists',
    'cache_delete',
    'cache_clear',
    'cache_stats',
]
