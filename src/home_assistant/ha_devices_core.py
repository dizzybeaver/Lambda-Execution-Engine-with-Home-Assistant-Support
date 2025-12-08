# ha_devices_core.py
"""
ha_devices_core.py - Core Device Operations (INT-HA-02)
Version: 3.1.0
Date: 2025-12-06
Purpose: Core implementation for Home Assistant device operations

Architecture:
ha_interconnect.py → ha_interface_devices.py → ha_devices_core.py (THIS FILE)
                                                  ├─ ha_devices_helpers.py (helpers)
                                                  └─ ha_devices_cache.py (cache mgmt)

Core Functions (14):
Core Operations (7):
- get_states_impl: Get entity states
- get_by_id_impl: Get specific device by ID
- find_fuzzy_impl: Find device using fuzzy matching
- update_state_impl: Update device state
- call_service_impl: Call HA service
- list_by_domain_impl: List devices in domain
- check_status_impl: Check HA connection status

Helper/Cache Wrappers (7):
- call_ha_api_impl: Call HA API directly
- get_ha_config_impl: Get HA configuration
- warm_cache_impl: Pre-warm cache
- invalidate_entity_cache_impl: Invalidate entity cache
- invalidate_domain_cache_impl: Invalidate domain cache
- get_performance_report_impl: Get performance report
- get_diagnostic_info_impl: Get diagnostic info

Copyright 2025 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

import time
import hashlib
from typing import Dict, Any, Optional, List
from difflib import SequenceMatcher

# Import gateway services
from gateway import (
    log_info, log_error, log_debug, log_warning,
    cache_get, cache_set, cache_delete,
    increment_counter, record_metric,
    create_success_response, create_error_response,
    generate_correlation_id
)

# Import helpers from ha_devices_helpers
from home_assistant.ha_devices_helpers import (
    call_ha_api_impl as _helper_call_ha_api_impl,
    get_ha_config_impl as _helper_get_ha_config_impl,
    _extract_entity_list,
    _trace_step,
    DebugContext,
    HA_CACHE_TTL_STATE,
    HA_CACHE_TTL_FUZZY_MATCH
)


# ===== CORE DEVICE OPERATIONS (7 FUNCTIONS) =====

def get_states_impl(entity_ids: Optional[List[str]] = None, use_cache: bool = True,
                   oauth_token: str = None, **kwargs) -> Dict[str, Any]:
    """
    Get Home Assistant entity states implementation.
    
    LWA Migration: Accepts oauth_token and passes to call_ha_api_impl.
    
    Args:
        entity_ids: Optional list of specific entity IDs
        use_cache: Whether to use cached states
        oauth_token: OAuth token from Alexa directive (LWA)
        **kwargs: Additional options
        
    Returns:
        States response dictionary with entity list
    """
    correlation_id = generate_correlation_id()
    
    try:
        with DebugContext("get_states_impl", correlation_id, 
                         entity_count=len(entity_ids) if entity_ids else "all",
                         use_cache=use_cache):
            
            cache_key = 'ha_all_states'
            
            if use_cache:
                cached = cache_get(cache_key)
                if cached and isinstance(cached, dict):
                    _trace_step(correlation_id, "Using cached states")
                    increment_counter('ha_state_cache_hit')
                    record_metric('ha_states_cache_hit', 1.0)
                    
                    if entity_ids and isinstance(entity_ids, list):
                        entity_set = set(entity_ids)
                        cached_data = _extract_entity_list(cached.get('data', []), 'cached_states')
                        filtered = [e for e in cached_data 
                                   if isinstance(e, dict) and e.get('entity_id') in entity_set]
                        return create_success_response('States retrieved from cache', filtered)
                    
                    return cached
                elif cached:
                    log_warning(f"[{correlation_id}] Cached data is {type(cached)}, not dict - invalidating")
                    cache_delete(cache_key)
            
            _trace_step(correlation_id, "Fetching states from API")
            result = _helper_call_ha_api_impl('/api/states', oauth_token=oauth_token)
            
            if not isinstance(result, dict):
                log_error(f"[{correlation_id}] call_ha_api_impl returned {type(result)}, not dict")
                return create_error_response(f'API returned invalid type: {type(result).__name__}', 'INVALID_API_RESPONSE')
            
            if result.get('success'):
                raw_data = result.get('data', [])
                entity_list = _extract_entity_list(raw_data, 'api_states')
                
                log_info(f"[{correlation_id}] Retrieved {len(entity_list)} entities from HA")
                
                normalized_result = create_success_response('States retrieved', entity_list)
                
                if use_cache:
                    cache_set(cache_key, normalized_result, ttl=HA_CACHE_TTL_STATE)
                    _trace_step(correlation_id, "States cached")
                    _trace_step(correlation_id, "States cached")
                
                if entity_ids and isinstance(entity_ids, list):
                    entity_set = set(entity_ids)
                    filtered = [e for e in entity_list 
                               if isinstance(e, dict) and e.get('entity_id') in entity_set]
                    return create_success_response('States retrieved', filtered)
                
                increment_counter('ha_devices_get_states_success')
                return normalized_result
            
            increment_counter('ha_devices_get_states_error')
            return result
            
    except Exception as e:
        log_error(f"[{correlation_id}] Get states failed: {str(e)}")
        increment_counter('ha_devices_get_states_error')
        return create_error_response(str(e), 'GET_STATES_FAILED')


def get_by_id_impl(entity_id: str, oauth_token: str = None, **kwargs) -> Dict[str, Any]:
    """
    Get single entity by ID implementation.
    
    LWA Migration: Accepts oauth_token and passes to call_ha_api_impl.
    
    Args:
        entity_id: Entity ID
        oauth_token: OAuth token from Alexa directive (LWA)
        **kwargs: Additional options
        
    Returns:
        Entity data dictionary
    """
    correlation_id = generate_correlation_id()
    
    try:
        with DebugContext("get_by_id_impl", correlation_id, entity_id=entity_id):
            result = _helper_call_ha_api_impl(f'/api/states/{entity_id}', oauth_token=oauth_token)
            
            if result.get('success'):
                increment_counter('ha_devices_get_by_id_success')
                return create_success_response(f'Entity {entity_id} retrieved', result.get('data'))
            
            increment_counter('ha_devices_get_by_id_error')
            return result
            
    except Exception as e:
        log_error(f"[{correlation_id}] Get by ID failed: {str(e)}")
        increment_counter('ha_devices_get_by_id_error')
        return create_error_response(str(e), 'GET_BY_ID_FAILED')


def find_fuzzy_impl(search_name: str, threshold: float = 0.6, oauth_token: str = None, **kwargs) -> Optional[str]:
    """Find entity using fuzzy name matching."""
    correlation_id = generate_correlation_id()
    
    try:
        cache_key = f'fuzzy_match:{hashlib.md5(search_name.encode()).hexdigest()}'
        cached_entity_id = cache_get(cache_key)
        if cached_entity_id:
            increment_counter('ha_fuzzy_cache_hit')
            return cached_entity_id
        
        states_result = get_states_impl(oauth_token=oauth_token)
        if not states_result.get('success'):
            return None
        
        entities = states_result.get('data', [])
        best_match = None
        best_ratio = threshold
        
        for entity in entities:
            if not isinstance(entity, dict):
                continue
                
            entity_id = entity.get('entity_id', '')
            friendly_name = entity.get('attributes', {}).get('friendly_name', '')
            
            name_ratio = SequenceMatcher(None, search_name.lower(), friendly_name.lower()).ratio()
            id_ratio = SequenceMatcher(None, search_name.lower(), entity_id.lower()).ratio()
            
            ratio = max(name_ratio, id_ratio)
            
            if ratio > best_ratio:
                best_ratio = ratio
                best_match = entity_id
        
        if best_match:
            cache_set(cache_key, best_match, ttl=HA_CACHE_TTL_FUZZY_MATCH)
            increment_counter('ha_devices_find_fuzzy_success')
        
        return best_match
        
    except Exception as e:
        log_error(f"[{correlation_id}] Fuzzy find failed: {str(e)}")
        return None


def update_state_impl(entity_id: str, state_data: Dict[str, Any], oauth_token: str = None, **kwargs) -> Dict[str, Any]:
    """Update entity state."""
    correlation_id = generate_correlation_id()
    
    try:
        result = _helper_call_ha_api_impl(
            f'/api/states/{entity_id}',
            method='POST',
            data=state_data,
            oauth_token=oauth_token
        )
        
        if result.get('success'):
            cache_delete('ha_all_states')
            increment_counter('ha_devices_update_state_success')
        else:
            increment_counter('ha_devices_update_state_error')
        
        return result
        
    except Exception as e:
        log_error(f"[{correlation_id}] Update state failed: {str(e)}")
        increment_counter('ha_devices_update_state_error')
        return create_error_response(str(e), 'UPDATE_STATE_FAILED')


def call_service_impl(domain: str, service: str, entity_id: Optional[str] = None,
                     service_data: Optional[Dict] = None, oauth_token: str = None, **kwargs) -> Dict[str, Any]:
    """Call HA service."""
    correlation_id = generate_correlation_id()
    
    try:
        data = service_data.copy() if service_data else {}
        if entity_id:
            data['entity_id'] = entity_id
        
        result = _helper_call_ha_api_impl(
            f'/api/services/{domain}/{service}',
            method='POST',
            data=data,
            oauth_token=oauth_token
        )
        
        if result.get('success'):
            cache_delete('ha_all_states')
            increment_counter('ha_devices_call_service_success')
        else:
            increment_counter('ha_devices_call_service_error')
        
        return result
        
    except Exception as e:
        log_error(f"[{correlation_id}] Call service failed: {str(e)}")
        increment_counter('ha_devices_call_service_error')
        return create_error_response(str(e), 'CALL_SERVICE_FAILED')


def list_by_domain_impl(domain: str, oauth_token: str = None, **kwargs) -> Dict[str, Any]:
    """List entities by domain."""
    correlation_id = generate_correlation_id()
    
    try:
        result = get_states_impl(oauth_token=oauth_token)
        
        if result.get('success'):
            all_entities = result.get('data', [])
            filtered = [e for e in all_entities 
                       if isinstance(e, dict) and e.get('entity_id', '').startswith(f'{domain}.')]
            
            log_info(f"[{correlation_id}] Found {len(filtered)} entities in domain {domain}")
            increment_counter('ha_devices_list_by_domain_success')
            record_metric(f'ha_devices_domain_{domain}_count', len(filtered))
            
            return create_success_response(f'Entities in domain {domain}', filtered)
        
        increment_counter('ha_devices_list_by_domain_error')
        return result
        
    except Exception as e:
        log_error(f"[{correlation_id}] List by domain failed: {str(e)}")
        increment_counter('ha_devices_list_by_domain_error')
        return create_error_response(str(e), 'LIST_BY_DOMAIN_FAILED')


def check_status_impl(oauth_token: str = None, **kwargs) -> Dict[str, Any]:
    """Check HA connection status."""
    correlation_id = generate_correlation_id()
    
    try:
        with DebugContext("check_status_impl", correlation_id):
            result = _helper_call_ha_api_impl('/api/', oauth_token=oauth_token)
            
            if result.get('success'):
                record_metric('ha_status_check_success', 1.0)
                increment_counter('ha_devices_check_status_success')
                return create_success_response('Connected to Home Assistant', {
                    'connected': True,
                    'message': result.get('data', {}).get('message', 'API running')
                })
            
            record_metric('ha_status_check_failure', 1.0)
            increment_counter('ha_devices_check_status_error')
            return create_error_response('Failed to connect to HA', 'CONNECTION_FAILED', result)
            
    except Exception as e:
        log_error(f"[{correlation_id}] Status check failed: {str(e)}")
        increment_counter('ha_devices_check_status_error')
        return create_error_response(str(e), 'STATUS_CHECK_FAILED')


# ===== HELPER/CACHE WRAPPER FUNCTIONS (7 FUNCTIONS) =====
# FIXED: Added missing wrapper functions

def call_ha_api_impl(endpoint: str, method: str = 'GET', data: Optional[Dict] = None, 
                    oauth_token: str = None, **kwargs) -> Dict[str, Any]:
    """Call HA API directly - wrapper for helper function."""
    return _helper_call_ha_api_impl(endpoint, method, data, oauth_token=oauth_token, **kwargs)


def get_ha_config_impl(force_reload: bool = False, **kwargs) -> Dict[str, Any]:
    """Get HA configuration - wrapper for helper function."""
    return _helper_get_ha_config_impl(force_reload, **kwargs)


def warm_cache_impl(oauth_token: str = None, **kwargs) -> Dict[str, Any]:
    """Pre-warm cache - wrapper for cache function."""
    import home_assistant.ha_devices_cache as ha_devices_cache
    return ha_devices_cache.warm_cache_impl(oauth_token=oauth_token, **kwargs)


def invalidate_entity_cache_impl(entity_id: str, **kwargs) -> bool:
    """Invalidate entity cache - wrapper for cache function."""
    import home_assistant.ha_devices_cache as ha_devices_cache
    return ha_devices_cache.invalidate_entity_cache_impl(entity_id, **kwargs)


def invalidate_domain_cache_impl(domain: str, **kwargs) -> int:
    """Invalidate domain cache - wrapper for cache function."""
    import home_assistant.ha_devices_cache as ha_devices_cache
    return ha_devices_cache.invalidate_domain_cache_impl(domain, **kwargs)


def get_performance_report_impl(oauth_token: str = None, **kwargs) -> Dict[str, Any]:
    """Get performance report - wrapper for cache function."""
    import home_assistant.ha_devices_cache as ha_devices_cache
    return ha_devices_cache.get_performance_report_impl(oauth_token=oauth_token, **kwargs)


def get_diagnostic_info_impl(oauth_token: str = None, **kwargs) -> Dict[str, Any]:
    """Get diagnostic info - wrapper for cache function."""
    import home_assistant.ha_devices_cache as ha_devices_cache
    return ha_devices_cache.get_diagnostic_info_impl(oauth_token=oauth_token, **kwargs)


__all__ = [
    # Core operations (7)
    'get_states_impl',
    'get_by_id_impl',
    'find_fuzzy_impl',
    'update_state_impl',
    'call_service_impl',
    'list_by_domain_impl',
    'check_status_impl',
    # FIXED: Added helper/cache wrappers (7)
    'call_ha_api_impl',
    'get_ha_config_impl',
    'warm_cache_impl',
    'invalidate_entity_cache_impl',
    'invalidate_domain_cache_impl',
    'get_performance_report_impl',
    'get_diagnostic_info_impl',
]

# EOF
