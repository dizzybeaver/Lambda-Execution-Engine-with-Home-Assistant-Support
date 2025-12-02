"""
ha_interconnect_core.py - HA Interconnect Core Registry (CR-1 Pattern)
Version: 1.0.0
Date: 2025-12-02
Description: Cache Registry pattern for HA interface routing

Provides fast path caching and centralized dispatch.

Copyright 2025 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

from enum import Enum
import importlib
from typing import Any, Dict, Tuple


class HAInterface(Enum):
    """HA functional area enumeration."""
    VALIDATION = "validation"
    ALEXA = "alexa"
    DEVICES = "devices"
    ASSIST = "assist"


_HA_INTERFACE_ROUTERS: Dict[HAInterface, Tuple[str, str]] = {
    HAInterface.VALIDATION: (
        'home_assistant.ha_interface_validation',
        'execute_validation_operation'
    ),
    HAInterface.ALEXA: (
        'home_assistant.ha_interface_alexa',
        'execute_alexa_operation'
    ),
    HAInterface.DEVICES: (
        'home_assistant.ha_interface_devices',
        'execute_devices_operation'
    ),
    HAInterface.ASSIST: (
        'home_assistant.ha_interface_assist',
        'execute_assist_operation'
    ),
}

_HA_ROUTER_CACHE: Dict[Tuple[HAInterface, str], Any] = {}


def execute_ha_operation(interface: HAInterface, operation: str, **kwargs) -> Any:
    """
    Execute HA operation through interface router.
    
    Pattern-based routing with fast path caching.
    First call: ~2ms (import + lookup)
    Subsequent: ~0.05ms (cached router)
    
    Args:
        interface: HA interface enum
        operation: Operation name
        **kwargs: Operation parameters
        
    Returns:
        Operation result
        
    Raises:
        ValueError: Unknown interface or operation
    """
    # Fast path check
    cache_key = (interface, operation)
    if cache_key in _HA_ROUTER_CACHE:
        router = _HA_ROUTER_CACHE[cache_key]
        return router(operation, **kwargs)
    
    # Slow path: Import and cache
    if interface not in _HA_INTERFACE_ROUTERS:
        raise ValueError(f"Unknown HA interface: {interface.value}")
    
    module_name, func_name = _HA_INTERFACE_ROUTERS[interface]
    module = importlib.import_module(module_name)
    router = getattr(module, func_name)
    
    # Cache for next call
    _HA_ROUTER_CACHE[cache_key] = router
    
    return router(operation, **kwargs)


def get_ha_registry_stats() -> Dict[str, Any]:
    """
    Get HA registry statistics.
    
    Returns:
        Registry stats including cache hit rate
    """
    return {
        'total_interfaces': len(_HA_INTERFACE_ROUTERS),
        'cached_routers': len(_HA_ROUTER_CACHE),
        'interfaces': [i.value for i in HAInterface],
        'cache_hit_potential': f"{(len(_HA_ROUTER_CACHE) / max(len(_HA_INTERFACE_ROUTERS), 1)) * 100:.1f}%"
    }


def clear_ha_cache() -> int:
    """
    Clear fast path cache.
    
    Returns:
        Number of cached entries cleared
    """
    count = len(_HA_ROUTER_CACHE)
    _HA_ROUTER_CACHE.clear()
    return count


__all__ = [
    'HAInterface',
    'execute_ha_operation',
    'get_ha_registry_stats',
    'clear_ha_cache',
]
