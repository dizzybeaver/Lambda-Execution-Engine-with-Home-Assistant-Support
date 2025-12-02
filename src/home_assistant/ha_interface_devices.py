"""
ha_interface_devices.py - Devices Interface Layer (INT-HA-02)
Version: 1.1.0
Date: 2025-12-01
Description: Interface layer for Home Assistant device operations

FIXED: Added missing routing functions for call_ha_api, get_ha_config, warm_cache,
       invalidate_entity_cache, invalidate_domain_cache, get_performance_report,
       get_diagnostic_info

Architecture:
ha_interconnect.py → ha_interface_devices.py → ha_devices_core.py
                                              ├─ ha_devices_helpers.py
                                              └─ ha_devices_cache.py

Copyright 2025 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

from typing import Dict, Any, Optional, List


# ===== CORE DEVICE OPERATIONS (7 FUNCTIONS) =====

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


# ===== HELPER/API FUNCTIONS (2 FUNCTIONS) - ADDED =====

def call_ha_api(endpoint: str, method: str = 'GET', 
               data: Optional[Dict] = None, **kwargs) -> Dict[str, Any]:
    """
    Call Home Assistant API directly.
    
    Interface layer routing.
    Routes to: ha_devices_helpers.call_ha_api_impl
    
    Args:
        endpoint: API endpoint
        method: HTTP method
        data: Optional request data
        **kwargs: Additional options
        
    Returns:
        API response
    """
    import home_assistant.ha_devices_helpers as ha_devices_helpers
    return ha_devices_helpers.call_ha_api_impl(endpoint, method, data, **kwargs)


def get_ha_config(force_reload: bool = False, **kwargs) -> Dict[str, Any]:
    """
    Get Home Assistant configuration.
    
    Interface layer routing.
    Routes to: ha_devices_helpers.get_ha_config_impl
    
    Args:
        force_reload: Force reload from sources
        **kwargs: Additional options
        
    Returns:
        Configuration dictionary
    """
    import home_assistant.ha_devices_helpers as ha_devices_helpers
    return ha_devices_helpers.get_ha_config_impl(force_reload, **kwargs)


# ===== CACHE MANAGEMENT FUNCTIONS (3 FUNCTIONS) - ADDED =====

def warm_cache(**kwargs) -> Dict[str, Any]:
    """
    Pre-warm cache on cold start.
    
    Interface layer routing.
    Routes to: ha_devices_cache.warm_cache_impl
    
    Args:
        **kwargs: Additional options
        
    Returns:
        Warming status and statistics
    """
    import home_assistant.ha_devices_cache as ha_devices_cache
    return ha_devices_cache.warm_cache_impl(**kwargs)


def invalidate_entity_cache(entity_id: str, **kwargs) -> bool:
    """
    Invalidate cache for specific entity.
    
    Interface layer routing.
    Routes to: ha_devices_cache.invalidate_entity_cache_impl
    
    Args:
        entity_id: Entity ID to invalidate
        **kwargs: Additional options
        
    Returns:
        True if invalidated
    """
    import home_assistant.ha_devices_cache as ha_devices_cache
    return ha_devices_cache.invalidate_entity_cache_impl(entity_id, **kwargs)


def invalidate_domain_cache(domain: str, **kwargs) -> int:
    """
    Invalidate cache for entire domain.
    
    Interface layer routing.
    Routes to: ha_devices_cache.invalidate_domain_cache_impl
    
    Args:
        domain: Domain to invalidate
        **kwargs: Additional options
        
    Returns:
        Number of entries invalidated
    """
    import home_assistant.ha_devices_cache as ha_devices_cache
    return ha_devices_cache.invalidate_domain_cache_impl(domain, **kwargs)


# ===== DIAGNOSTIC FUNCTIONS (2 FUNCTIONS) - ADDED =====

def get_performance_report(**kwargs) -> Dict[str, Any]:
    """
    Get comprehensive performance report.
    
    Interface layer routing.
    Routes to: ha_devices_cache.get_performance_report_impl
    
    Args:
        **kwargs: Additional options
        
    Returns:
        Performance report
    """
    import home_assistant.ha_devices_cache as ha_devices_cache
    return ha_devices_cache.get_performance_report_impl(**kwargs)


def get_diagnostic_info(**kwargs) -> Dict[str, Any]:
    """
    Get diagnostic information.
    
    Interface layer routing.
    Routes to: ha_devices_cache.get_diagnostic_info_impl
    
    Args:
        **kwargs: Additional options
        
    Returns:
        Diagnostic information
    """
    import home_assistant.ha_devices_cache as ha_devices_cache
    return ha_devices_cache.get_diagnostic_info_impl(**kwargs)


# ===== EXPORTS =====

__all__ = [
    # Core device operations (7)
    'get_states',
    'get_by_id',
    'find_fuzzy',
    'update_state',
    'call_service',
    'list_by_domain',
    'check_status',
    # Helper/API functions (2) - ADDED
    'call_ha_api',
    'get_ha_config',
    # Cache management (3) - ADDED
    'warm_cache',
    'invalidate_entity_cache',
    'invalidate_domain_cache',
    # Diagnostics (2) - ADDED
    'get_performance_report',
    'get_diagnostic_info',
]

# EOF
