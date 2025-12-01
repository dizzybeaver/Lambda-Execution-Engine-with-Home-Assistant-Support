"""
ha_interface_devices.py - Devices Interface Layer (INT-HA-02)
Version: 1.0.0
Date: 2025-11-03
Description: Interface layer for Home Assistant device operations

Architecture:
ha_interconnect.py → ha_interface_devices.py → ha_devices_core.py

Copyright 2025 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

from typing import Dict, Any, Optional, List


def get_states(entity_ids: Optional[List[str]] = None, 
               use_cache: bool = True, **kwargs) -> Dict[str, Any]:
    """
    Get Home Assistant entity states.
    
    Interface layer routing.
    Routes to: ha_devices_core.get_states_impl
    
    Args:
        entity_ids: Optional list of entity IDs
        use_cache: Whether to use cache
        **kwargs: Additional options
        
    Returns:
        States response
    """

    import home_assistant.ha_devices_core as ha_devices_core
    return ha_devices_core.get_states_impl(entity_ids, use_cache, **kwargs)


def get_by_id(entity_id: str, **kwargs) -> Dict[str, Any]:
    """
    Get specific device by ID.
    
    Interface layer routing.
    Routes to: ha_devices_core.get_by_id_impl
    
    Args:
        entity_id: Entity ID
        **kwargs: Additional options
        
    Returns:
        Device state
    """
    import home_assistant.ha_devices_core as ha_devices_core
    return ha_devices_core.get_by_id_impl(entity_id, **kwargs)


def find_fuzzy(search_name: str, threshold: float = 0.6, **kwargs) -> Optional[str]:
    """
    Find device using fuzzy matching.
    
    Interface layer routing.
    Routes to: ha_devices_core.find_fuzzy_impl
    
    Args:
        search_name: Name to search
        threshold: Match threshold
        **kwargs: Additional options
        
    Returns:
        Best match entity ID or None
    """
    import home_assistant.ha_devices_core as ha_devices_core
    return ha_devices_core.find_fuzzy_impl(search_name, threshold, **kwargs)


def update_state(entity_id: str, state_data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """
    Update device state.
    
    Interface layer routing.
    Routes to: ha_devices_core.update_state_impl
    
    Args:
        entity_id: Entity to update
        state_data: New state data
        **kwargs: Additional options
        
    Returns:
        Update response
    """
    import home_assistant.ha_devices_core as ha_devices_core
    return ha_devices_core.update_state_impl(entity_id, state_data, **kwargs)


def call_service(domain: str, service: str, 
                entity_id: Optional[str] = None,
                service_data: Optional[Dict] = None, **kwargs) -> Dict[str, Any]:
    """
    Call Home Assistant service.
    
    Interface layer routing.
    Routes to: ha_devices_core.call_service_impl
    
    Args:
        domain: Service domain
        service: Service name
        entity_id: Optional entity ID
        service_data: Optional service data
        **kwargs: Additional options
        
    Returns:
        Service response
    """
    import home_assistant.ha_devices_core as ha_devices_core
    return ha_devices_core.call_service_impl(domain, service, entity_id, service_data, **kwargs)


def list_by_domain(domain: str, **kwargs) -> Dict[str, Any]:
    """
    List devices by domain.
    
    Interface layer routing.
    Routes to: ha_devices_core.list_by_domain_impl
    
    Args:
        domain: Domain to filter
        **kwargs: Additional options
        
    Returns:
        Device list
    """
    import home_assistant.ha_devices_core as ha_devices_core
    return ha_devices_core.list_by_domain_impl(domain, **kwargs)


def check_status(**kwargs) -> Dict[str, Any]:
    """
    Check HA connection status.
    
    Interface layer routing.
    Routes to: ha_devices_core.check_status_impl
    
    Args:
        **kwargs: Additional options
        
    Returns:
        Connection status
    """
    import home_assistant.ha_devices_core as ha_devices_core
    return ha_devices_core.check_status_impl(**kwargs)


__all__ = [
    'get_states',
    'get_by_id',
    'find_fuzzy',
    'update_state',
    'call_service',
    'list_by_domain',
    'check_status',
]

# EOF
