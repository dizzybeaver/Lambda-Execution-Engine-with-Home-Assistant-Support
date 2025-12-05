"""
ha_interconnect_core.py - HA Interconnect Core Registry
Version: 6.0.0
Date: 2025-12-05
Description: Central registry for HA operations (CR-1 pattern)

CHANGES (6.0.0 - LWA MIGRATION):
- MODIFIED: execute_ha_operation passes oauth_token to implementations
- All HA operations now support oauth_token parameter

Copyright 2025 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

from enum import Enum
from typing import Dict, Any, Callable
import importlib

from gateway import log_error


# ===== HA INTERFACE REGISTRY =====

class HAInterface(Enum):
    """HA interface enumeration."""
    ALEXA = "alexa"
    DEVICES = "devices"
    ASSIST = "assist"


# ===== INTERFACE ROUTERS =====

_INTERFACE_ROUTERS = {
    HAInterface.ALEXA: ('home_assistant.ha_alexa_core', {
        'process_directive': 'process_directive_impl',
        'handle_discovery': 'handle_discovery_impl',
        'handle_control': 'handle_control_impl',
        'handle_power_control': 'handle_power_control_impl',
        'handle_brightness_control': 'handle_brightness_control_impl',
        'handle_thermostat_control': 'handle_thermostat_control_impl',
        'handle_accept_grant': 'handle_accept_grant_impl',
    }),
    HAInterface.DEVICES: ('home_assistant.ha_devices_core', {
        'get_states': 'get_states_impl',
        'get_by_id': 'get_by_id_impl',
        'find_fuzzy': 'find_fuzzy_impl',
        'update_state': 'update_state_impl',
        'call_service': 'call_service_impl',
        'list_by_domain': 'list_by_domain_impl',
        'check_status': 'check_status_impl',
    }),
    HAInterface.ASSIST: ('home_assistant.ha_assist_core', {
        'send_message': 'send_message_impl',
        'get_response': 'get_response_impl',
        'process_conversation': 'process_conversation_impl',
        'handle_pipeline': 'handle_pipeline_impl',
    }),
}


# ===== FAST PATH CACHE =====

_fast_path_cache: Dict[tuple, Callable] = {}
_fast_path_enabled = True


# ===== OPERATION EXECUTOR =====

def execute_ha_operation(interface: HAInterface, operation: str, **kwargs) -> Any:
    """
    Execute HA operation through interface router.
    
    LWA Migration: Passes oauth_token through to implementations.
    
    Args:
        interface: HA interface enum
        operation: Operation name
        **kwargs: Operation parameters (including oauth_token)
        
    Returns:
        Operation result
    """
    # Fast path check
    cache_key = (interface, operation)
    if _fast_path_enabled and cache_key in _fast_path_cache:
        func = _fast_path_cache[cache_key]
        return func(**kwargs)
    
    # Slow path: Lookup and cache
    if interface not in _INTERFACE_ROUTERS:
        raise ValueError(f"Unknown HA interface: {interface.value}")
    
    module_name, operations = _INTERFACE_ROUTERS[interface]
    
    if operation not in operations:
        raise ValueError(f"Unknown operation '{operation}' for interface {interface.value}")
    
    impl_name = operations[operation]
    
    # Lazy import
    try:
        module = importlib.import_module(module_name)
    except ImportError as e:
        raise RuntimeError(f"Failed to import {module_name}: {str(e)}") from e
    
    try:
        func = getattr(module, impl_name)
    except AttributeError as e:
        raise RuntimeError(f"Function '{impl_name}' not found in {module_name}: {str(e)}") from e
    
    # Cache for fast path
    if _fast_path_enabled:
        _fast_path_cache[cache_key] = func
    
    # Execute operation (oauth_token passed through kwargs)
    return func(**kwargs)


# ===== REGISTRY STATS =====

def get_ha_registry_stats() -> Dict[str, Any]:
    """Get HA registry statistics."""
    return {
        'total_interfaces': len(_INTERFACE_ROUTERS),
        'fast_path_entries': len(_fast_path_cache),
        'fast_path_enabled': _fast_path_enabled,
    }


def clear_ha_cache() -> Dict[str, Any]:
    """Clear HA fast path cache."""
    global _fast_path_cache
    count = len(_fast_path_cache)
    _fast_path_cache.clear()
    return {
        'cleared': count,
        'success': True
    }


__all__ = [
    'HAInterface',
    'execute_ha_operation',
    'get_ha_registry_stats',
    'clear_ha_cache',
]

# EOF
