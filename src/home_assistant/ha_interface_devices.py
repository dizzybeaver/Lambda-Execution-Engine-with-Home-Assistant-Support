"""
ha_interface_devices.py - Devices Interface Layer (INT-HA-02)
Version: 3.0.0
Date: 2025-12-05
Description: Interface layer for Home Assistant device operations

CHANGES (3.0.0 - LWA MIGRATION):
- ADDED: oauth_token parameter support throughout
- KEPT: All DISPATCH entries, impl functions, backward compatibility

Copyright 2025 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

from typing import Dict, Any, Optional, List


def _get_states_impl(entity_ids: Optional[List[str]] = None, use_cache: bool = True, oauth_token: str = None, **kwargs) -> Dict[str, Any]:
    """Get entity states."""
    import home_assistant.ha_devices_core as ha_devices_core
    return ha_devices_core.get_states_impl(entity_ids, use_cache, oauth_token=oauth_token, **kwargs)


def _get_by_id_impl(entity_id: str, oauth_token: str = None, **kwargs) -> Dict[str, Any]:
    """Get device by ID."""
    import home_assistant.ha_devices_core as ha_devices_core
    return ha_devices_core.get_by_id_impl(entity_id, oauth_token=oauth_token, **kwargs)


def _find_fuzzy_impl(search_name: str, threshold: float = 0.6, oauth_token: str = None, **kwargs) -> Optional[str]:
    """Find device via fuzzy matching."""
    import home_assistant.ha_devices_core as ha_devices_core
    return ha_devices_core.find_fuzzy_impl(search_name, threshold, oauth_token=oauth_token, **kwargs)


def _update_state_impl(entity_id: str, state_data: Dict[str, Any], oauth_token: str = None, **kwargs) -> Dict[str, Any]:
    """Update device state."""
    import home_assistant.ha_devices_core as ha_devices_core
    return ha_devices_core.update_state_impl(entity_id, state_data, oauth_token=oauth_token, **kwargs)


def _call_service_impl(domain: str, service: str, entity_id: Optional[str] = None, 
                       service_data: Optional[Dict] = None, oauth_token: str = None, **kwargs) -> Dict[str, Any]:
    """Call HA service."""
    import home_assistant.ha_devices_core as ha_devices_core
    return ha_devices_core.call_service_impl(domain, service, entity_id, service_data, oauth_token=oauth_token, **kwargs)


def _list_by_domain_impl(domain: str, oauth_token: str = None, **kwargs) -> Dict[str, Any]:
    """List devices by domain."""
    import home_assistant.ha_devices_core as ha_devices_core
    return ha_devices_core.list_by_domain_impl(domain, oauth_token=oauth_token, **kwargs)


def _check_status_impl(oauth_token: str = None, **kwargs) -> Dict[str, Any]:
    """Check HA connection status."""
    import home_assistant.ha_devices_core as ha_devices_core
    return ha_devices_core.check_status_impl(oauth_token=oauth_token, **kwargs)


def _call_ha_api_impl(endpoint: str, method: str = 'GET', data: Optional[Dict] = None, oauth_token: str = None, **kwargs) -> Dict[str, Any]:
    """Call HA API directly."""
    import home_assistant.ha_devices_helpers as ha_devices_helpers
    return ha_devices_helpers.call_ha_api_impl(endpoint, method, data, oauth_token=oauth_token, **kwargs)


def _get_ha_config_impl(force_reload: bool = False, **kwargs) -> Dict[str, Any]:
    """Get HA configuration."""
    import home_assistant.ha_devices_helpers as ha_devices_helpers
    return ha_devices_helpers.get_ha_config_impl(force_reload, **kwargs)


def _warm_cache_impl(oauth_token: str = None, **kwargs) -> Dict[str, Any]:
    """Pre-warm cache."""
    import home_assistant.ha_devices_cache as ha_devices_cache
    return ha_devices_cache.warm_cache_impl(oauth_token=oauth_token, **kwargs)


def _invalidate_entity_cache_impl(entity_id: str, **kwargs) -> bool:
    """Invalidate entity cache."""
    import home_assistant.ha_devices_cache as ha_devices_cache
    return ha_devices_cache.invalidate_entity_cache_impl(entity_id, **kwargs)


def _invalidate_domain_cache_impl(domain: str, **kwargs) -> int:
    """Invalidate domain cache."""
    import home_assistant.ha_devices_cache as ha_devices_cache
    return ha_devices_cache.invalidate_domain_cache_impl(domain, **kwargs)


def _get_performance_report_impl(oauth_token: str = None, **kwargs) -> Dict[str, Any]:
    """Get performance report."""
    import home_assistant.ha_devices_cache as ha_devices_cache
    return ha_devices_cache.get_performance_report_impl(oauth_token=oauth_token, **kwargs)


def _get_diagnostic_info_impl(oauth_token: str = None, **kwargs) -> Dict[str, Any]:
    """Get diagnostic info."""
    import home_assistant.ha_devices_cache as ha_devices_cache
    return ha_devices_cache.get_diagnostic_info_impl(oauth_token=oauth_token, **kwargs)


# DISPATCH dictionary (CR-1 pattern)
DISPATCH = {
    'get_states': _get_states_impl,
    'get_by_id': _get_by_id_impl,
    'find_fuzzy': _find_fuzzy_impl,
    'update_state': _update_state_impl,
    'call_service': _call_service_impl,
    'list_by_domain': _list_by_domain_impl,
    'check_status': _check_status_impl,
    'call_ha_api': _call_ha_api_impl,
    'get_ha_config': _get_ha_config_impl,
    'warm_cache': _warm_cache_impl,
    'invalidate_entity_cache': _invalidate_entity_cache_impl,
    'invalidate_domain_cache': _invalidate_domain_cache_impl,
    'get_performance_report': _get_performance_report_impl,
    'get_diagnostic_info': _get_diagnostic_info_impl,
}


# Execute operation router (CR-1 pattern)
def execute_devices_operation(operation: str, **kwargs):
    """Execute devices operation via dispatch."""
    if operation not in DISPATCH:
        raise ValueError(f"Unknown devices operation: {operation}")
    
    handler = DISPATCH[operation]
    return handler(**kwargs)


# Maintain backward compatibility
def get_states(entity_ids: Optional[List[str]] = None, use_cache: bool = True, **kwargs) -> Dict[str, Any]:
    """Get states."""
    return _get_states_impl(entity_ids, use_cache, **kwargs)


def get_by_id(entity_id: str, **kwargs) -> Dict[str, Any]:
    """Get by ID."""
    return _get_by_id_impl(entity_id, **kwargs)


def find_fuzzy(search_name: str, threshold: float = 0.6, **kwargs) -> Optional[str]:
    """Find fuzzy."""
    return _find_fuzzy_impl(search_name, threshold, **kwargs)


def update_state(entity_id: str, state_data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """Update state."""
    return _update_state_impl(entity_id, state_data, **kwargs)


def call_service(domain: str, service: str, entity_id: Optional[str] = None,
                service_data: Optional[Dict] = None, **kwargs) -> Dict[str, Any]:
    """Call service."""
    return _call_service_impl(domain, service, entity_id, service_data, **kwargs)


def list_by_domain(domain: str, **kwargs) -> Dict[str, Any]:
    """List by domain."""
    return _list_by_domain_impl(domain, **kwargs)


def check_status(**kwargs) -> Dict[str, Any]:
    """Check status."""
    return _check_status_impl(**kwargs)


def call_ha_api(endpoint: str, method: str = 'GET', data: Optional[Dict] = None, **kwargs) -> Dict[str, Any]:
    """Call HA API."""
    return _call_ha_api_impl(endpoint, method, data, **kwargs)


def get_ha_config(force_reload: bool = False, **kwargs) -> Dict[str, Any]:
    """Get HA config."""
    return _get_ha_config_impl(force_reload, **kwargs)


def warm_cache(**kwargs) -> Dict[str, Any]:
    """Warm cache."""
    return _warm_cache_impl(**kwargs)


def invalidate_entity_cache(entity_id: str, **kwargs) -> bool:
    """Invalidate entity cache."""
    return _invalidate_entity_cache_impl(entity_id, **kwargs)


def invalidate_domain_cache(domain: str, **kwargs) -> int:
    """Invalidate domain cache."""
    return _invalidate_domain_cache_impl(domain, **kwargs)


def get_performance_report(**kwargs) -> Dict[str, Any]:
    """Get performance report."""
    return _get_performance_report_impl(**kwargs)


def get_diagnostic_info(**kwargs) -> Dict[str, Any]:
    """Get diagnostic info."""
    return _get_diagnostic_info_impl(**kwargs)


__all__ = [
    'execute_devices_operation',
    'get_states',
    'get_by_id',
    'find_fuzzy',
    'update_state',
    'call_service',
    'list_by_domain',
    'check_status',
    'call_ha_api',
    'get_ha_config',
    'warm_cache',
    'invalidate_entity_cache',
    'invalidate_domain_cache',
    'get_performance_report',
    'get_diagnostic_info',
]
