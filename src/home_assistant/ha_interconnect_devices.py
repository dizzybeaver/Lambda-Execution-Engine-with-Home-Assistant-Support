"""
ha_interconnect_devices.py - Devices Interface Gateway
Version: 3.0.0
Date: 2025-12-05
Description: Gateway wrapper for Home Assistant device operations

CHANGES (3.0.0 - LWA MIGRATION):
- ADDED: oauth_token parameter support to all functions
- KEPT: All validation and 14 device functions

Copyright 2025 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

from typing import Dict, Any, Optional, List
from gateway import create_error_response
from home_assistant.ha_config import HA_ENTITY_ID_PATTERN, HA_DOMAIN_PATTERN
import re


def _validate_entity_id(entity_id: str) -> bool:
    """Validate entity ID format."""
    if not isinstance(entity_id, str) or not entity_id:
        return False
    return re.match(HA_ENTITY_ID_PATTERN, entity_id) is not None


def _validate_domain(domain: str) -> bool:
    """Validate domain format."""
    if not isinstance(domain, str) or not domain:
        return False
    return re.match(HA_DOMAIN_PATTERN, domain) is not None


def devices_get_states(entity_ids: Optional[List[str]] = None, 
                      use_cache: bool = True, oauth_token: str = None, **kwargs) -> Dict[str, Any]:
    """Get device states."""
    if entity_ids is not None:
        if not isinstance(entity_ids, list):
            return create_error_response('entity_ids must be a list', 'INVALID_INPUT')
        for entity_id in entity_ids:
            if not _validate_entity_id(entity_id):
                return create_error_response(f'Invalid entity_id: {entity_id}', 'INVALID_INPUT')
    
    from home_assistant.ha_interconnect_core import execute_ha_operation, HAInterface
    return execute_ha_operation(
        HAInterface.DEVICES,
        'get_states',
        entity_ids=entity_ids,
        use_cache=use_cache,
        oauth_token=oauth_token,
        **kwargs
    )


def devices_get_by_id(entity_id: str, oauth_token: str = None, **kwargs) -> Dict[str, Any]:
    """Get device by entity ID."""
    if not _validate_entity_id(entity_id):
        return create_error_response(f'Invalid entity_id: {entity_id}', 'INVALID_INPUT')
    
    from home_assistant.ha_interconnect_core import execute_ha_operation, HAInterface
    return execute_ha_operation(
        HAInterface.DEVICES,
        'get_by_id',
        entity_id=entity_id,
        oauth_token=oauth_token,
        **kwargs
    )


def devices_find_fuzzy(search_name: str, threshold: float = 0.6, oauth_token: str = None, **kwargs) -> Optional[str]:
    """Find device using fuzzy matching."""
    if not isinstance(search_name, str) or not search_name:
        return None
    if not (0.0 <= threshold <= 1.0):
        threshold = 0.6
    
    from home_assistant.ha_interconnect_core import execute_ha_operation, HAInterface
    return execute_ha_operation(
        HAInterface.DEVICES,
        'find_fuzzy',
        search_name=search_name,
        threshold=threshold,
        oauth_token=oauth_token,
        **kwargs
    )


def devices_update_state(entity_id: str, state_data: Dict[str, Any], oauth_token: str = None, **kwargs) -> Dict[str, Any]:
    """Update device state."""
    if not _validate_entity_id(entity_id):
        return create_error_response(f'Invalid entity_id: {entity_id}', 'INVALID_INPUT')
    if not isinstance(state_data, dict):
        return create_error_response('state_data must be a dictionary', 'INVALID_INPUT')
    
    from home_assistant.ha_interconnect_core import execute_ha_operation, HAInterface
    return execute_ha_operation(
        HAInterface.DEVICES,
        'update_state',
        entity_id=entity_id,
        state_data=state_data,
        oauth_token=oauth_token,
        **kwargs
    )


def devices_call_service(domain: str, service: str, 
                        entity_id: Optional[str] = None,
                        service_data: Optional[Dict] = None, oauth_token: str = None, **kwargs) -> Dict[str, Any]:
    """Call Home Assistant service."""
    if not _validate_domain(domain):
        return create_error_response(f'Invalid domain: {domain}', 'INVALID_INPUT')
    if not isinstance(service, str) or not service:
        return create_error_response('Invalid service name', 'INVALID_INPUT')
    if entity_id is not None and not _validate_entity_id(entity_id):
        return create_error_response(f'Invalid entity_id: {entity_id}', 'INVALID_INPUT')
    if service_data is not None and not isinstance(service_data, dict):
        return create_error_response('service_data must be a dictionary', 'INVALID_INPUT')
    
    from home_assistant.ha_interconnect_core import execute_ha_operation, HAInterface
    return execute_ha_operation(
        HAInterface.DEVICES,
        'call_service',
        domain=domain,
        service=service,
        entity_id=entity_id,
        service_data=service_data,
        oauth_token=oauth_token,
        **kwargs
    )


def devices_list_by_domain(domain: str, oauth_token: str = None, **kwargs) -> Dict[str, Any]:
    """List all devices in a domain."""
    if not _validate_domain(domain):
        return create_error_response(f'Invalid domain: {domain}', 'INVALID_INPUT')
    
    from home_assistant.ha_interconnect_core import execute_ha_operation, HAInterface
    return execute_ha_operation(
        HAInterface.DEVICES,
        'list_by_domain',
        domain=domain,
        oauth_token=oauth_token,
        **kwargs
    )


def devices_check_status(oauth_token: str = None, **kwargs) -> Dict[str, Any]:
    """Check Home Assistant connection status."""
    from home_assistant.ha_interconnect_core import execute_ha_operation, HAInterface
    return execute_ha_operation(
        HAInterface.DEVICES,
        'check_status',
        oauth_token=oauth_token,
        **kwargs
    )


def devices_call_ha_api(endpoint: str, method: str = 'GET', 
                       data: Optional[Dict] = None, oauth_token: str = None, **kwargs) -> Dict[str, Any]:
    """Call Home Assistant API directly."""
    if not isinstance(endpoint, str) or not endpoint.startswith('/'):
        return create_error_response(f'Invalid endpoint: {endpoint}', 'INVALID_INPUT')
    if method.upper() not in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']:
        return create_error_response(f'Invalid HTTP method: {method}', 'INVALID_INPUT')
    if data is not None and not isinstance(data, dict):
        return create_error_response('data must be a dictionary', 'INVALID_INPUT')
    
    from home_assistant.ha_interconnect_core import execute_ha_operation, HAInterface
    return execute_ha_operation(
        HAInterface.DEVICES,
        'call_ha_api',
        endpoint=endpoint,
        method=method,
        data=data,
        oauth_token=oauth_token,
        **kwargs
    )


def devices_get_ha_config(force_reload: bool = False, **kwargs) -> Dict[str, Any]:
    """Get Home Assistant configuration."""
    if not isinstance(force_reload, bool):
        force_reload = False
    
    from home_assistant.ha_interconnect_core import execute_ha_operation, HAInterface
    return execute_ha_operation(
        HAInterface.DEVICES,
        'get_ha_config',
        force_reload=force_reload,
        **kwargs
    )


def devices_warm_cache(oauth_token: str = None, **kwargs) -> Dict[str, Any]:
    """Pre-warm cache on cold start."""
    from home_assistant.ha_interconnect_core import execute_ha_operation, HAInterface
    return execute_ha_operation(
        HAInterface.DEVICES,
        'warm_cache',
        oauth_token=oauth_token,
        **kwargs
    )


def devices_invalidate_entity_cache(entity_id: str, **kwargs) -> bool:
    """Invalidate cache for specific entity."""
    if not _validate_entity_id(entity_id):
        return False
    
    from home_assistant.ha_interconnect_core import execute_ha_operation, HAInterface
    return execute_ha_operation(
        HAInterface.DEVICES,
        'invalidate_entity_cache',
        entity_id=entity_id,
        **kwargs
    )


def devices_invalidate_domain_cache(domain: str, **kwargs) -> int:
    """Invalidate cache for entire domain."""
    if not _validate_domain(domain):
        return 0
    
    from home_assistant.ha_interconnect_core import execute_ha_operation, HAInterface
    return execute_ha_operation(
        HAInterface.DEVICES,
        'invalidate_domain_cache',
        domain=domain,
        **kwargs
    )


def devices_get_performance_report(oauth_token: str = None, **kwargs) -> Dict[str, Any]:
    """Get comprehensive performance report."""
    from home_assistant.ha_interconnect_core import execute_ha_operation, HAInterface
    return execute_ha_operation(
        HAInterface.DEVICES,
        'get_performance_report',
        oauth_token=oauth_token,
        **kwargs
    )


def devices_get_diagnostic_info(oauth_token: str = None, **kwargs) -> Dict[str, Any]:
    """Get HA diagnostic information."""
    from home_assistant.ha_interconnect_core import execute_ha_operation, HAInterface
    return execute_ha_operation(
        HAInterface.DEVICES,
        'get_diagnostic_info',
        oauth_token=oauth_token,
        **kwargs
    )


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
