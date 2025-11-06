# ha_devices_core.py
"""
ha_devices_core.py - Core Device Operations (INT-HA-02)
Version: 3.0.0 - FILE SPLIT COMPLIANT
Date: 2025-11-05
Purpose: Core implementation for Home Assistant device operations

Split from v2.0.0 (866 lines) for SIMAv4 compliance.
This file contains ONLY the 7 core device operations.

Architecture:
ha_interconnect.py → ha_interface_devices.py → ha_devices_core.py (THIS FILE)
                                                  ├─ ha_devices_helpers.py (helpers)
                                                  └─ ha_devices_cache.py (cache mgmt)

Core Functions (7):
- get_states_impl: Get entity states
- get_by_id_impl: Get specific device by ID
- find_fuzzy_impl: Find device using fuzzy matching
- update_state_impl: Update device state
- call_service_impl: Call HA service
- list_by_domain_impl: List devices in domain
- check_status_impl: Check HA connection status

Copyright 2025 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

import time
import hashlib
from typing import Dict, Any, Optional, List
from difflib import SequenceMatcher

# Import gateway services
from gateway import (
    log_info, log_error, log_debug,
    cache_get, cache_set, cache_delete,
    increment_counter, record_metric,
    create_success_response, create_error_response,
    generate_correlation_id
)

# Import helpers from ha_devices_helpers
from ha_devices_helpers import (
    call_ha_api_impl,
    get_ha_config_impl,
    _extract_entity_list,
    _trace_step,
    DebugContext,
    HA_CACHE_TTL_STATE,
    HA_CACHE_TTL_FUZZY_MATCH
)

# Import cache functions (lazy import to avoid circular)
# Imported inside warm_cache_impl when needed


# ===== CORE DEVICE OPERATIONS (7 FUNCTIONS) =====

def get_states_impl(entity_ids: Optional[List[str]] = None, 
                   use_cache: bool = True, **kwargs) -> Dict[str, Any]:
    """
    Get Home Assistant entity states implementation.
    
    Core implementation for retrieving device states.
    
    Args:
        entity_ids: Optional list of specific entity IDs
        use_cache: Whether to use cached states
        **kwargs: Additional options
        
    Returns:
        States response dictionary with entity list
        
    Example:
        states = get_states_impl(['light.living_room'])
        
    REF: INT-HA-02
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
            result = call_ha_api_impl('/api/states')
            
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
                
                increment_counter('ha_states_retrieved')
                record_metric('ha_states_count', len(entity_list))
                record_metric('ha_states_cache_miss', 1.0)
                
                if entity_ids and isinstance(entity_ids, list):
                    entity_set = set(entity_ids)
                    filtered = [e for e in entity_list 
                               if isinstance(e, dict) and e.get('entity_id') in entity_set]
                    record_metric('ha_states_filtered_count', len(filtered))
                    return create_success_response('States retrieved', filtered)
                
                return normalized_result
            
            return result
            
    except Exception as e:
        log_error(f"[{correlation_id}] Get states failed: {str(e)}")
        increment_counter('ha_states_error')
        return create_error_response(str(e), 'GET_STATES_FAILED')


def get_by_id_impl(entity_id: str, **kwargs) -> Dict[str, Any]:
    """
    Get specific device by entity ID implementation.
    
    Core implementation for single device retrieval.
    
    Args:
        entity_id: Entity ID to retrieve
        **kwargs: Additional options
        
    Returns:
        Device state dictionary
        
    REF: INT-HA-02
    """
    correlation_id = generate_correlation_id()
    log_info(f"[{correlation_id}] Getting device by ID: {entity_id}")
    
    try:
        # Use get_states_impl with filtering
        result = get_states_impl(entity_ids=[entity_id], **kwargs)
        
        if result.get('success'):
            entities = result.get('data', [])
            if entities and len(entities) > 0:
                increment_counter('ha_devices_get_by_id_success')
                return create_success_response('Entity retrieved', entities[0])
            else:
                increment_counter('ha_devices_get_by_id_not_found')
                return create_error_response(f'Entity {entity_id} not found', 'ENTITY_NOT_FOUND')
        
        return result
        
    except Exception as e:
        log_error(f"[{correlation_id}] Get by ID failed: {str(e)}")
        increment_counter('ha_devices_get_by_id_error')
        return create_error_response(str(e), 'GET_BY_ID_FAILED')


def find_fuzzy_impl(search_name: str, threshold: float = 0.6, **kwargs) -> Optional[str]:
    """
    Find device using fuzzy name matching implementation.
    
    Core implementation for fuzzy device search.
    
    Args:
        search_name: Name to search for
        threshold: Matching threshold (0.0-1.0)
        **kwargs: Additional options
        
    Returns:
        Best matching entity ID or None
        
    REF: INT-HA-02
    """
    correlation_id = generate_correlation_id()
    
    try:
        # Get all entity states
        states_result = get_states_impl(use_cache=True)
        
        if not states_result.get('success'):
            log_error(f"[{correlation_id}] Failed to get states for fuzzy match")
            return None
        
        entities = states_result.get('data', [])
        names = [e.get('entity_id', '') for e in entities if isinstance(e, dict)]
        
        # Cache fuzzy match results (entity names rarely change)
        names_hash = hashlib.md5('|'.join(sorted(names)).encode()).hexdigest()[:8]
        cache_key = f"fuzzy_match_{search_name}_{names_hash}"
        
        cached_result = cache_get(cache_key)
        if cached_result is not None:
            log_debug(f"Fuzzy match cache hit: {search_name}")
            record_metric('fuzzy_match_cache_hit', 1.0)
            increment_counter('ha_devices_find_fuzzy_cache_hit')
            return cached_result if cached_result != '' else None
        
        search_lower = search_name.lower()
        best_match = None
        best_ratio = threshold
        
        for name in names:
            ratio = SequenceMatcher(None, search_lower, name.lower()).ratio()
            if ratio > best_ratio:
                best_ratio = ratio
                best_match = name
        
        cache_value = best_match if best_match else ''
        cache_set(cache_key, cache_value, ttl=HA_CACHE_TTL_FUZZY_MATCH)
        
        record_metric('fuzzy_match_cache_miss', 1.0)
        if best_match:
            record_metric('fuzzy_match_success', 1.0)
            record_metric('fuzzy_match_ratio', best_ratio)
            increment_counter('ha_devices_find_fuzzy_success')
        else:
            record_metric('fuzzy_match_no_match', 1.0)
            increment_counter('ha_devices_find_fuzzy_no_match')
        
        return best_match
        
    except Exception as e:
        log_error(f"[{correlation_id}] Fuzzy match failed: {str(e)}")
        increment_counter('ha_devices_find_fuzzy_error')
        return None


def call_service_impl(domain: str, service: str, 
                     entity_id: Optional[str] = None,
                     service_data: Optional[Dict] = None, **kwargs) -> Dict[str, Any]:
    """
    Call Home Assistant service implementation.
    
    Core implementation for service calls.
    
    Args:
        domain: Service domain (e.g., 'light', 'switch')
        service: Service name (e.g., 'turn_on', 'turn_off')
        entity_id: Optional target entity ID
        service_data: Optional service data
        **kwargs: Additional options
        
    Returns:
        Service call response
        
    Example:
        result = call_service_impl('light', 'turn_on', 'light.living_room')
        
    REF: INT-HA-02
    """
    # Lazy import to avoid circular dependency
    from ha_devices_cache import invalidate_entity_cache_impl
    
    correlation_id = generate_correlation_id()
    
    try:
        with DebugContext("call_service_impl", correlation_id,
                         domain=domain, service=service, entity_id=entity_id):
            
            if not isinstance(domain, str) or not domain:
                return create_error_response('Invalid domain', 'INVALID_DOMAIN')
            
            if not isinstance(service, str) or not service:
                return create_error_response('Invalid service', 'INVALID_SERVICE')
            
            endpoint = f'/api/services/{domain}/{service}'
            
            data = service_data if isinstance(service_data, dict) else {}
            if entity_id and isinstance(entity_id, str):
                data['entity_id'] = entity_id
            
            _trace_step(correlation_id, "Calling service", service=f"{domain}.{service}")
            
            result = call_ha_api_impl(endpoint, method='POST', data=data)
            
            if result.get('success'):
                # Smart cache invalidation
                if entity_id:
                    invalidate_entity_cache_impl(entity_id)
                
                increment_counter(f'ha_service_{domain}_{service}')
                record_metric(f'ha_service_{domain}_success', 1.0)
                increment_counter('ha_devices_call_service_success')
                
                return create_success_response('Service called', {
                    'domain': domain,
                    'service': service,
                    'entity_id': entity_id
                })
            
            increment_counter('ha_devices_call_service_error')
            return result
            
    except Exception as e:
        log_error(f"[{correlation_id}] Service call failed: {str(e)}")
        increment_counter('ha_devices_call_service_error')
        return create_error_response(str(e), 'SERVICE_CALL_FAILED')


def update_state_impl(entity_id: str, state_data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """
    Update device state implementation.
    
    Core implementation for state updates. Uses call_service_impl
    to apply state changes via HA services.
    
    Args:
        entity_id: Entity ID to update
        state_data: New state data (e.g., {'state': 'on', 'brightness': 255})
        **kwargs: Additional options
        
    Returns:
        Update response
        
    REF: INT-HA-02
    """
    correlation_id = generate_correlation_id()
    log_info(f"[{correlation_id}] Updating state for {entity_id}")
    
    try:
        # Extract domain from entity_id (e.g., 'light' from 'light.living_room')
        if '.' not in entity_id:
            return create_error_response('Invalid entity_id format', 'INVALID_ENTITY_ID')
        
        domain = entity_id.split('.')[0]
        
        # Determine service based on state_data
        state = state_data.get('state', '').lower()
        service = 'turn_on' if state == 'on' else 'turn_off' if state == 'off' else None
        
        if not service:
            return create_error_response('Unable to determine service from state_data', 'INVALID_STATE')
        
        # Call service with state data
        result = call_service_impl(domain, service, entity_id, state_data)
        
        if result.get('success'):
            increment_counter('ha_devices_update_state_success')
        else:
            increment_counter('ha_devices_update_state_error')
        
        return result
        
    except Exception as e:
        log_error(f"[{correlation_id}] Update state failed: {str(e)}")
        increment_counter('ha_devices_update_state_error')
        return create_error_response(str(e), 'UPDATE_STATE_FAILED')


def list_by_domain_impl(domain: str, **kwargs) -> Dict[str, Any]:
    """
    List all devices in a domain implementation.
    
    Core implementation for domain filtering.
    
    Args:
        domain: Domain to filter (e.g., 'light', 'switch', 'sensor')
        **kwargs: Additional options
        
    Returns:
        List of devices in domain
        
    REF: INT-HA-02
    """
    correlation_id = generate_correlation_id()
    log_info(f"[{correlation_id}] Listing devices in domain: {domain}")
    
    try:
        # Get all states
        result = get_states_impl(use_cache=True)
        
        if result.get('success'):
            entities = result.get('data', [])
            # Filter by domain
            filtered = [e for e in entities 
                       if isinstance(e, dict) and 
                       e.get('entity_id', '').startswith(f"{domain}.")]
            
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


def check_status_impl(**kwargs) -> Dict[str, Any]:
    """
    Check Home Assistant connection status implementation.
    
    Core implementation for status checks.
    
    Args:
        **kwargs: Additional options
        
    Returns:
        Connection status dictionary
        
    REF: INT-HA-02
    """
    correlation_id = generate_correlation_id()
    
    try:
        with DebugContext("check_status_impl", correlation_id):
            result = call_ha_api_impl('/api/')
            
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


__all__ = [
    # Core device operations (7)
    'get_states_impl',
    'get_by_id_impl',
    'find_fuzzy_impl',
    'update_state_impl',
    'call_service_impl',
    'list_by_domain_impl',
    'check_status_impl',
]

# FILE SPLIT NOTES:
# - Split from v2.0.0 (866 lines) to v3.0.0 (320 lines)
# - Helpers moved to ha_devices_helpers.py
# - Cache management moved to ha_devices_cache.py
# - CRIT-01 fixed in ha_devices_helpers.py
# - All files ≤400 lines (SIMAv4 compliant)
# - SUGA pattern maintained
# - No circular imports

# EOF
