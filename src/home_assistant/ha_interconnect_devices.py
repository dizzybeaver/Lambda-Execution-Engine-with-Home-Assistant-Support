# ha_interconnect_devices.py
"""
ha_interconnect_devices.py - Devices Interface Gateway
Version: 1.0.0
Date: 2025-11-05
Purpose: Gateway wrapper for Home Assistant device operations

SECURITY:
- Input validation on all functions
- Type checking for parameters
- Boundary validation for numeric inputs
- String sanitization for entity IDs
- Error handling for invalid inputs

Architecture:
ha_interconnect_devices.py → ha_interface_devices.py → ha_devices_*.py

Functions: 14 device operations
- Get states/status
- Update state
- Call services
- Cache management
- Performance reporting
- Diagnostics

Pattern:
Validates input → Routes to interface → Returns response

Copyright 2025 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

from typing import Dict, Any, Optional, List
from home_assistant.ha_interconnect_validation import (
    _validate_entity_id,
    _validate_domain,
    _validate_threshold,
    _validate_endpoint,
    _validate_http_method,
)
from gateway import create_error_response


def devices_get_states(entity_ids: Optional[List[str]] = None, 
                      use_cache: bool = True, **kwargs) -> Dict[str, Any]:
    """
    Get Home Assistant entity states.
    
    Gateway function for retrieving device states.
    Routes to: ha_interface_devices.get_states
    
    Args:
        entity_ids: Optional list of specific entity IDs
        use_cache: Whether to use cached states
        **kwargs: Additional options
        
    Returns:
        States response dictionary
        
    Security:
        - Validates entity_ids list format
        - Validates each entity_id format
        - Type checks use_cache parameter
        
    REF: INT-HA-02
    """
    # ADDED: Input validation (CRIT-03)
    if entity_ids is not None:
        if not isinstance(entity_ids, list):
            return create_error_response('entity_ids must be a list', 'INVALID_INPUT')
        for entity_id in entity_ids:
            if not _validate_entity_id(entity_id):
                return create_error_response(f'Invalid entity_id: {entity_id}', 'INVALID_INPUT')
    
    if not isinstance(use_cache, bool):
        use_cache = True
    
    import home_assistant.ha_interface_devices as ha_interface_devices
    return ha_interface_devices.get_states(entity_ids, use_cache, **kwargs)


def devices_get_by_id(entity_id: str, **kwargs) -> Dict[str, Any]:
    """
    Get specific device by entity ID.
    
    Gateway function for single device retrieval.
    Routes to: ha_interface_devices.get_by_id
    
    Args:
        entity_id: Entity ID to retrieve
        **kwargs: Additional options
        
    Returns:
        Device state dictionary
        
    Security:
        - Validates entity_id format
        - Sanitization via validation helper
        
    REF: INT-HA-02
    """
    # ADDED: Input validation (CRIT-03)
    if not _validate_entity_id(entity_id):
        return create_error_response(f'Invalid entity_id: {entity_id}', 'INVALID_INPUT')
    
    import home_assistant.ha_interface_devices as ha_interface_devices
    return ha_interface_devices.get_by_id(entity_id, **kwargs)


def devices_find_fuzzy(search_name: str, threshold: float = 0.6, **kwargs) -> Optional[str]:
    """
    Find device using fuzzy name matching.
    
    Gateway function for fuzzy device search.
    Routes to: ha_interface_devices.find_fuzzy
    
    Args:
        search_name: Name to search for
        threshold: Matching threshold (0.0-1.0)
        **kwargs: Additional options
        
    Returns:
        Best matching entity ID or None
        
    Security:
        - Validates search_name is non-empty string
        - Validates threshold bounds (0.0-1.0)
        - Defaults to safe threshold on invalid input
        
    REF: INT-HA-02
    """
    # ADDED: Input validation (CRIT-03)
    if not isinstance(search_name, str) or not search_name:
        return None
    if not _validate_threshold(threshold):
        threshold = 0.6  # Default safe value
    
    import home_assistant.ha_interface_devices as ha_interface_devices
    return ha_interface_devices.find_fuzzy(search_name, threshold, **kwargs)


def devices_update_state(entity_id: str, state_data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """
    Update device state.
    
    Gateway function for state updates.
    Routes to: ha_interface_devices.update_state
    
    Args:
        entity_id: Entity ID to update
        state_data: New state data
        **kwargs: Additional options
        
    Returns:
        Update response
        
    Security:
        - Validates entity_id format
        - Validates state_data is dictionary
        - Prevents invalid state updates
        
    REF: INT-HA-02
    """
    # ADDED: Input validation (CRIT-03)
    if not _validate_entity_id(entity_id):
        return create_error_response(f'Invalid entity_id: {entity_id}', 'INVALID_INPUT')
    if not isinstance(state_data, dict):
        return create_error_response('state_data must be a dictionary', 'INVALID_INPUT')
    
    import home_assistant.ha_interface_devices as ha_interface_devices
    return ha_interface_devices.update_state(entity_id, state_data, **kwargs)


def devices_call_service(domain: str, service: str, 
                        entity_id: Optional[str] = None,
                        service_data: Optional[Dict] = None, **kwargs) -> Dict[str, Any]:
    """
    Call Home Assistant service.
    
    Gateway function for service calls.
    Routes to: ha_interface_devices.call_service
    
    Args:
        domain: Service domain (e.g., 'light', 'switch')
        service: Service name (e.g., 'turn_on', 'turn_off')
        entity_id: Optional target entity ID
        service_data: Optional service data
        **kwargs: Additional options
        
    Returns:
        Service call response
        
    Security:
        - Validates domain format (alphanumeric + underscore)
        - Validates service name non-empty
        - Validates entity_id if provided
        - Validates service_data is dictionary if provided
        
    REF: INT-HA-02
    """
    # ADDED: Input validation (CRIT-03)
    if not _validate_domain(domain):
        return create_error_response(f'Invalid domain: {domain}', 'INVALID_INPUT')
    if not isinstance(service, str) or not service:
        return create_error_response('Invalid service name', 'INVALID_INPUT')
    if entity_id is not None and not _validate_entity_id(entity_id):
        return create_error_response(f'Invalid entity_id: {entity_id}', 'INVALID_INPUT')
    if service_data is not None and not isinstance(service_data, dict):
        return create_error_response('service_data must be a dictionary', 'INVALID_INPUT')
    
    import home_assistant.ha_interface_devices as ha_interface_devices
    return ha_interface_devices.call_service(domain, service, entity_id, service_data, **kwargs)


def devices_list_by_domain(domain: str, **kwargs) -> Dict[str, Any]:
    """
    List all devices in a domain.
    
    Gateway function for domain filtering.
    Routes to: ha_interface_devices.list_by_domain
    
    Args:
        domain: Domain to filter (e.g., 'light', 'switch', 'sensor')
        **kwargs: Additional options
        
    Returns:
        List of devices in domain
        
    Security:
        - Validates domain format
        - Prevents domain injection
        
    REF: INT-HA-02
    """
    # ADDED: Input validation (CRIT-03)
    if not _validate_domain(domain):
        return create_error_response(f'Invalid domain: {domain}', 'INVALID_INPUT')
    
    import home_assistant.ha_interface_devices as ha_interface_devices
    return ha_interface_devices.list_by_domain(domain, **kwargs)


def devices_check_status(**kwargs) -> Dict[str, Any]:
    """
    Check Home Assistant connection status.
    
    Gateway function for status checks.
    Routes to: ha_interface_devices.check_status
    
    Args:
        **kwargs: Additional options
        
    Returns:
        Connection status
        
    Security:
        - No input validation needed (no parameters)
        - Safe diagnostic function
        
    REF: INT-HA-02
    """
    import home_assistant.ha_interface_devices as ha_interface_devices
    return ha_interface_devices.check_status(**kwargs)


def devices_call_ha_api(endpoint: str, method: str = 'GET', 
                       data: Optional[Dict] = None, **kwargs) -> Dict[str, Any]:
    """
    Call Home Assistant API directly.
    
    Gateway function for direct HA API calls.
    Routes to: ha_interface_devices.call_ha_api
    
    Args:
        endpoint: API endpoint (e.g., '/api/states')
        method: HTTP method (default: 'GET')
        data: Optional request data
        **kwargs: Additional options
        
    Returns:
        API response dictionary
        
    Security:
        - Validates endpoint format (starts with /)
        - Validates endpoint for injection characters
        - Validates HTTP method against whitelist
        - Validates data is dictionary if provided
        
    REF: INT-HA-02
    """
    # ADDED: Input validation (CRIT-03)
    if not _validate_endpoint(endpoint):
        return create_error_response(f'Invalid endpoint: {endpoint}', 'INVALID_INPUT')
    if not _validate_http_method(method):
        return create_error_response(f'Invalid HTTP method: {method}', 'INVALID_INPUT')
    if data is not None and not isinstance(data, dict):
        return create_error_response('data must be a dictionary', 'INVALID_INPUT')
    
    import home_assistant.ha_interface_devices as ha_interface_devices
    return ha_interface_devices.call_ha_api(endpoint, method, data, **kwargs)


def devices_get_ha_config(force_reload: bool = False, **kwargs) -> Dict[str, Any]:
    """
    Get Home Assistant configuration.
    
    Gateway function for HA configuration.
    Routes to: ha_interface_devices.get_ha_config
    
    Args:
        force_reload: Force reload from sources
        **kwargs: Additional options
        
    Returns:
        Configuration dictionary
        
    Security:
        - Validates force_reload is boolean
        - Defaults to False on invalid input
        
    REF: INT-HA-02
    """
    # ADDED: Input validation (CRIT-03)
    if not isinstance(force_reload, bool):
        force_reload = False
    
    import home_assistant.ha_interface_devices as ha_interface_devices
    return ha_interface_devices.get_ha_config(force_reload, **kwargs)


def devices_warm_cache(**kwargs) -> Dict[str, Any]:
    """
    Pre-warm cache on cold start.
    
    Gateway function for cache warming.
    Routes to: ha_interface_devices.warm_cache
    
    Args:
        **kwargs: Additional options
        
    Returns:
        Warming status and statistics
        
    Security:
        - No input validation needed (no parameters)
        - Safe performance optimization function
        
    REF: INT-HA-02
    """
    import home_assistant.ha_interface_devices as ha_interface_devices
    return ha_interface_devices.warm_cache(**kwargs)


def devices_invalidate_entity_cache(entity_id: str, **kwargs) -> bool:
    """
    Invalidate cache for specific entity.
    
    Gateway function for smart cache invalidation.
    Routes to: ha_interface_devices.invalidate_entity_cache
    
    Args:
        entity_id: Entity ID to invalidate
        **kwargs: Additional options
        
    Returns:
        True if invalidated, False otherwise
        
    Security:
        - Validates entity_id format
        - Returns False on invalid input (safe)
        
    REF: INT-HA-02
    """
    # ADDED: Input validation (CRIT-03)
    if not _validate_entity_id(entity_id):
        return False
    
    import home_assistant.ha_interface_devices as ha_interface_devices
    return ha_interface_devices.invalidate_entity_cache(entity_id, **kwargs)


def devices_invalidate_domain_cache(domain: str, **kwargs) -> int:
    """
    Invalidate cache for entire domain.
    
    Gateway function for domain cache invalidation.
    Routes to: ha_interface_devices.invalidate_domain_cache
    
    Args:
        domain: Domain to invalidate (e.g., 'light', 'switch')
        **kwargs: Additional options
        
    Returns:
        Number of cache entries invalidated
        
    Security:
        - Validates domain format
        - Returns 0 on invalid input (safe)
        
    REF: INT-HA-02
    """
    # ADDED: Input validation (CRIT-03)
    if not _validate_domain(domain):
        return 0
    
    import home_assistant.ha_interface_devices as ha_interface_devices
    return ha_interface_devices.invalidate_domain_cache(domain, **kwargs)


def devices_get_performance_report(**kwargs) -> Dict[str, Any]:
    """
    Get comprehensive performance report.
    
    Gateway function for performance profiling.
    Routes to: ha_interface_devices.get_performance_report
    
    Args:
        **kwargs: Additional options
        
    Returns:
        Performance report with metrics analysis
        
    Security:
        - No input validation needed (no parameters)
        - Safe diagnostic function
        
    REF: INT-HA-02
    """
    import home_assistant.ha_interface_devices as ha_interface_devices
    return ha_interface_devices.get_performance_report(**kwargs)


def devices_get_diagnostic_info(**kwargs) -> Dict[str, Any]:
    """
    Get HA diagnostic information.
    
    Gateway function for diagnostics.
    Routes to: ha_interface_devices.get_diagnostic_info
    
    Args:
        **kwargs: Additional options
        
    Returns:
        Diagnostic information dictionary
        
    Security:
        - No input validation needed (no parameters)
        - Safe diagnostic function
        
    REF: INT-HA-02
    """
    import home_assistant.ha_interface_devices as ha_interface_devices
    return ha_interface_devices.get_diagnostic_info(**kwargs)


# ====================
# EXPORTS
# ====================

__all__ = [
    'devices_get_states',
    'devices_get_by_id',
    'devices_find_fuzzy',
    'devices_update_state',
    'devices_call_service',
    'devices_list_by_domain',
    'devices_check_status',
    'devices_call_ha_api',
    'devices_get_ha_config',
    'devices_warm_cache',
    'devices_invalidate_entity_cache',
    'devices_invalidate_domain_cache',
    'devices_get_performance_report',
    'devices_get_diagnostic_info',
]

# DEVICES GATEWAY WRAPPER:
# - 14 functions for device operations
# - Input validation via ha_interconnect_validation
# - Error responses via gateway.create_error_response
# - Routes to ha_interface_devices (interface layer)
# - Lazy imports for performance
# - Comprehensive security checks

# EOF
