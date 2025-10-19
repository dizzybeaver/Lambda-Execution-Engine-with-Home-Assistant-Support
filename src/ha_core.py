"""
ha_core.py - Home Assistant Core Operations (CACHE VALIDATION FIX)
Version: 2025.10.19.CACHE_FIX
Description: Core operations with CACHE VALIDATION to prevent object() sentinel bug

CRITICAL FIX: Added cache validation in get_ha_config()
- BEFORE: Returned cached value without validation (returned object() sentinels!)
- AFTER: Validates cached value is dict before returning
- Prevents "Config is not dict" error from object() sentinels
- Module-level ha_config import for performance (no lazy loading)

Design Decision: Module-level ha_config import
Reason: Lazy import defeats the entire performance optimization strategy.
        ha_config imports config_param_store, which uses preloaded boto3 from lambda_preload.
        If we lazy load ha_config, we miss the optimization window and load during first request.

Copyright 2025 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

import os
from typing import Dict, Any, Optional, List, Callable

# CRITICAL: Import ha_config at MODULE LEVEL (not lazy!)
# This ensures config_param_store (and preloaded boto3) loads during Lambda INIT
from ha_config import load_ha_config, validate_ha_config

from gateway import (
    log_info, log_error, log_debug, log_warning,
    execute_operation, GatewayInterface,
    cache_get, cache_set, cache_delete,
    increment_counter, record_metric,
    create_success_response, create_error_response,
    generate_correlation_id, get_timestamp,
    parse_json
)

# Cache TTL Constants
HA_CACHE_TTL_ENTITIES = 300
HA_CACHE_TTL_STATE = 60
HA_CACHE_TTL_CONFIG = 600
HA_CIRCUIT_BREAKER_NAME = "home_assistant"


def _is_debug_mode() -> bool:
    """Check if DEBUG_MODE is enabled."""
    return os.getenv('DEBUG_MODE', 'false').lower() == 'true'


def _extract_entity_list(data: Any, context: str = "states") -> List[Dict[str, Any]]:
    """
    Extract entity list from various response formats.
    
    HA /api/states returns different formats depending on how it's called.
    This function handles all common formats robustly.
    """
    if data is None:
        log_debug(f"Data is None in {context}")
        return []
    
    # Already a list
    if isinstance(data, list):
        log_debug(f"Data is already a list with {len(data)} items")
        return [item for item in data if isinstance(item, dict)]
    
    # JSON string - parse it
    if isinstance(data, str):
        try:
            parsed = parse_json(data)
            log_debug(f"Parsed JSON string in {context}")
            return _extract_entity_list(parsed, context)
        except Exception as e:
            log_warning(f"Failed to parse JSON string in {context}: {str(e)}")
            return []
    
    # Dict - check for common entity list keys
    if isinstance(data, dict):
        for key in ['entities', 'data', 'states', 'body', 'result']:
            if key in data:
                value = data[key]
                if isinstance(value, list):
                    log_debug(f"Found entity list in data['{key}'] with {len(value)} items")
                    return [item for item in value if isinstance(item, dict)]
                elif isinstance(value, (str, dict)):
                    return _extract_entity_list(value, f"{context}.{key}")
    
    log_warning(f"Could not extract entity list from {type(data).__name__} in {context}")
    return []


# ===== CONFIGURATION =====

def get_ha_config(force_reload: bool = False) -> Dict[str, Any]:
    """
    Get Home Assistant configuration with CACHE VALIDATION.
    
    PERFORMANCE: Uses module-level import (no lazy loading!)
    CRITICAL FIX: Validates cached value before returning (prevents object() sentinel bug)
    """
    correlation_id = generate_correlation_id()
    
    if _is_debug_mode():
        log_info(f"[{correlation_id}] [DEBUG ENTRY] HA_CORE: get_ha_config called")
    
    cache_key = 'ha_config'
    
    if not force_reload:
        cached = cache_get(cache_key)
        if cached is not None:
            # CRITICAL: Validate cached value before returning
            # Cache can return object() sentinels or invalid types
            if type(cached).__name__ == 'object' and str(cached).startswith('<object object'):
                log_error(f"[{correlation_id}] Cached config is object() sentinel, invalidating")
                cache_delete(cache_key)
            elif not isinstance(cached, dict):
                log_error(f"[{correlation_id}] Cached config is {type(cached).__name__}, not dict, invalidating")
                cache_delete(cache_key)
            else:
                # Validate it has required keys
                if 'enabled' not in cached:
                    log_error(f"[{correlation_id}] Cached config missing 'enabled' key, invalidating")
                    cache_delete(cache_key)
                else:
                    # Cache is valid!
                    log_debug(f"[{correlation_id}] Using validated cached HA config")
                    return cached
    
    # Cache miss or invalid - load fresh config
    log_debug(f"[{correlation_id}] Loading fresh HA config")
    config = load_ha_config()
    
    if not isinstance(config, dict):
        log_error(f"[{correlation_id}] Invalid HA config type: {type(config)}")
        return {
            'enabled': False,
            'error': 'Invalid config type'
        }
    
    cache_set(cache_key, config, ttl=HA_CACHE_TTL_CONFIG)
    log_debug(f"[{correlation_id}] HA config loaded and cached")
    
    return config


# ===== API OPERATIONS =====

def call_ha_api(endpoint: str, method: str = 'GET', data: Optional[Dict] = None,
                config: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Call Home Assistant API endpoint.
    
    Args:
        endpoint: API endpoint (e.g., '/api/states')
        method: HTTP method (GET, POST, etc.)
        data: Request body data
        config: Optional HA config (will load if not provided)
        
    Returns:
        Response dict with success flag and data
    """
    correlation_id = generate_correlation_id()
    
    try:
        if _is_debug_mode():
            log_info(f"[{correlation_id}] [DEBUG STEP 1] HA_CORE: Starting call_ha_api for {endpoint}")
        
        if not isinstance(endpoint, str) or not endpoint:
            if _is_debug_mode():
                log_error(f"[{correlation_id}] [DEBUG] HA_CORE: Invalid endpoint")
            return create_error_response('Invalid endpoint', 'INVALID_ENDPOINT')
        
        if not isinstance(method, str):
            method = 'GET'
        
        if _is_debug_mode():
            log_info(f"[{correlation_id}] [DEBUG STEP 2] HA_CORE: Loading HA config")
        
        config = config or get_ha_config()
        
        if _is_debug_mode():
            log_info(f"[{correlation_id}] [DEBUG] HA_CORE: Config type: {type(config)}")
        
        if not isinstance(config, dict):
            if _is_debug_mode():
                log_error(f"[{correlation_id}] [DEBUG] HA_CORE: Config is not dict")
            return create_error_response('Invalid config', 'INVALID_CONFIG')
        
        if _is_debug_mode():
            log_info(f"[{correlation_id}] [DEBUG STEP 3] HA_CORE: Checking if HA enabled")
        
        enabled = config.get('enabled')
        
        if _is_debug_mode():
            log_info(f"[{correlation_id}] [DEBUG] HA_CORE: HA enabled: {enabled}")
        
        if not enabled:
            if _is_debug_mode():
                log_error(f"[{correlation_id}] [DEBUG] HA_CORE: HA not enabled")
            return create_error_response('HA not enabled', 'HA_DISABLED')
        
        base_url = config.get('base_url', '')
        token = config.get('access_token', '')
        
        if _is_debug_mode():
            log_info(f"[{correlation_id}] [DEBUG STEP 4] HA_CORE: Validating credentials")
            log_info(f"[{correlation_id}] [DEBUG] HA_CORE: Base URL present: {bool(base_url)}")
            log_info(f"[{correlation_id}] [DEBUG] HA_CORE: Token present: {bool(token)}")
        
        if not base_url or not token:
            if _is_debug_mode():
                log_error(f"[{correlation_id}] [DEBUG] HA_CORE: Missing URL or token")
            return create_error_response('Missing HA URL or token', 'INVALID_CONFIG')
        
        url = f"{base_url}{endpoint}"
        headers = {
            'Authorization': f"Bearer {token}",
            'Content-Type': 'application/json'
        }
        
        if _is_debug_mode():
            log_info(f"[{correlation_id}] [DEBUG STEP 5] HA_CORE: Making HTTP request to: {url}")
        
        # Use Gateway HTTP client (which uses preloaded urllib3!)
        http_result = execute_operation(
            GatewayInterface.HTTP_CLIENT,
            method.lower(),
            url=url,
            headers=headers,
            json=data,
            timeout=config.get('timeout', 30)
        )
        
        if _is_debug_mode():
            log_info(f"[{correlation_id}] [DEBUG] HA_CORE: HTTP result type: {type(http_result)}")
            log_info(f"[{correlation_id}] [DEBUG] HA_CORE: HTTP result keys: {list(http_result.keys()) if isinstance(http_result, dict) else 'NOT_DICT'}")
        
        if http_result.get('success'):
            if _is_debug_mode():
                log_info(f"[{correlation_id}] [DEBUG] HA_CORE: SUCCESS - Data type: {type(http_result.get('data'))}")
            increment_counter('ha_api_success')
        else:
            if _is_debug_mode():
                log_error(f"[{correlation_id}] [DEBUG] HA_CORE: FAILURE")
                log_error(f"[{correlation_id}] [DEBUG] HA_CORE: Error: {http_result.get('error', 'NO_ERROR_FIELD')}")
                log_error(f"[{correlation_id}] [DEBUG] HA_CORE: Error code: {http_result.get('error_code', 'NO_ERROR_CODE')}")
            increment_counter('ha_api_failure')
        
        return http_result
        
    except Exception as e:
        if _is_debug_mode():
            log_error(f"[{correlation_id}] [DEBUG EXCEPTION] HA_CORE: {type(e).__name__}: {str(e)}")
            import traceback
            log_error(f"[{correlation_id}] [DEBUG TRACEBACK] HA_CORE:\n{traceback.format_exc()}")
        increment_counter('ha_api_error')
        return create_error_response(str(e), 'API_CALL_FAILED')


def get_ha_states(entity_ids: Optional[List[str]] = None, 
                  use_cache: bool = True) -> Dict[str, Any]:
    """Get entity states using Gateway services."""
    correlation_id = generate_correlation_id()
    
    try:
        if _is_debug_mode():
            log_info(f"[{correlation_id}] [DEBUG ENTRY] HA_CORE: get_ha_states called")
            log_info(f"[{correlation_id}] [DEBUG] HA_CORE: entity_ids={entity_ids}, use_cache={use_cache}")
        
        cache_key = 'ha_all_states'
        
        if use_cache:
            cached = cache_get(cache_key)
            if cached and isinstance(cached, dict):
                if _is_debug_mode():
                    log_info(f"[{correlation_id}] [DEBUG] HA_CORE: Using cached states")
                log_debug(f"[{correlation_id}] Using cached states")
                increment_counter('ha_state_cache_hit')
                
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
        
        if _is_debug_mode():
            log_info(f"[{correlation_id}] [DEBUG] HA_CORE: Calling call_ha_api('/api/states')")
        
        result = call_ha_api('/api/states')
        
        if not isinstance(result, dict):
            log_error(f"[{correlation_id}] call_ha_api returned {type(result)}, not dict")
            return create_error_response(f'API returned invalid type: {type(result).__name__}', 'INVALID_API_RESPONSE')
        
        if _is_debug_mode():
            log_info(f"[{correlation_id}] [DEBUG] HA_CORE: call_ha_api result keys: {list(result.keys())}")
            log_info(f"[{correlation_id}] [DEBUG] HA_CORE: success: {result.get('success')}")
        
        if result.get('success'):
            raw_data = result.get('data', [])
            
            if _is_debug_mode():
                log_info(f"[{correlation_id}] [DEBUG] HA_CORE: Raw data type: {type(raw_data)}")
            
            entity_list = _extract_entity_list(raw_data, 'api_states')
            
            if _is_debug_mode():
                log_info(f"[{correlation_id}] [DEBUG] HA_CORE: Extracted {len(entity_list)} entities")
            
            log_info(f"[{correlation_id}] Retrieved {len(entity_list)} entities from HA")
            
            normalized_result = create_success_response('States retrieved', entity_list)
            
            if use_cache:
                cache_set(cache_key, normalized_result, ttl=HA_CACHE_TTL_STATE)
            
            increment_counter('ha_states_retrieved')
            
            if entity_ids and isinstance(entity_ids, list):
                entity_set = set(entity_ids)
                filtered = [e for e in entity_list 
                           if isinstance(e, dict) and e.get('entity_id') in entity_set]
                return create_success_response('States retrieved', filtered)
            
            return normalized_result
        
        if _is_debug_mode():
            log_error(f"[{correlation_id}] [DEBUG] HA_CORE: Returning failed result from call_ha_api")
        log_error(f"[{correlation_id}] Returning failed result from call_ha_api")
        return result
        
    except Exception as e:
        if _is_debug_mode():
            log_error(f"[{correlation_id}] [DEBUG EXCEPTION] HA_CORE: Get states failed: {str(e)}")
        log_error(f"[{correlation_id}] Get states failed: {str(e)}")
        return create_error_response(str(e), 'GET_STATES_FAILED')


def call_ha_service(domain: str, service: str, 
                   entity_id: Optional[str] = None,
                   service_data: Optional[Dict] = None) -> Dict[str, Any]:
    """Call Home Assistant service."""
    correlation_id = generate_correlation_id()
    
    try:
        if _is_debug_mode():
            log_info(f"[{correlation_id}] [DEBUG ENTRY] HA_CORE: call_ha_service called")
            log_info(f"[{correlation_id}] [DEBUG] HA_CORE: domain={domain}, service={service}, entity_id={entity_id}")
        
        if not isinstance(domain, str) or not domain:
            return create_error_response('Invalid domain', 'INVALID_DOMAIN')
        
        if not isinstance(service, str) or not service:
            return create_error_response('Invalid service', 'INVALID_SERVICE')
        
        endpoint = f'/api/services/{domain}/{service}'
        
        data = service_data if isinstance(service_data, dict) else {}
        if entity_id and isinstance(entity_id, str):
            data['entity_id'] = entity_id
        
        log_info(f"[{correlation_id}] Calling service: {domain}.{service}")
        
        result = call_ha_api(endpoint, method='POST', data=data)
        
        if result.get('success'):
            if entity_id:
                cache_delete(f"ha_state_{entity_id}")
            
            increment_counter(f'ha_service_{domain}_{service}')
            return create_success_response('Service called', {
                'domain': domain,
                'service': service,
                'entity_id': entity_id
            })
        
        return result
        
    except Exception as e:
        log_error(f"[{correlation_id}] Service call failed: {str(e)}")
        return create_error_response(str(e), 'SERVICE_CALL_FAILED')


def check_ha_status() -> Dict[str, Any]:
    """Check HA connection status using Gateway services."""
    correlation_id = generate_correlation_id()
    
    try:
        if _is_debug_mode():
            log_info(f"[{correlation_id}] [DEBUG ENTRY] HA_CORE: check_ha_status called")
        
        result = call_ha_api('/api/')
        
        if result.get('success'):
            return create_success_response('Connected to Home Assistant', {
                'connected': True,
                'message': result.get('data', {}).get('message', 'API running')
            })
        
        return create_error_response('Failed to connect to HA', 'CONNECTION_FAILED', result)
        
    except Exception as e:
        log_error(f"[{correlation_id}] Status check failed: {str(e)}")
        return create_error_response(str(e), 'STATUS_CHECK_FAILED')


def get_diagnostic_info() -> Dict[str, Any]:
    """Get HA diagnostic information."""
    return {
        'ha_core_version': '2025.10.19.CACHE_FIX',
        'cache_ttl_entities': HA_CACHE_TTL_ENTITIES,
        'cache_ttl_state': HA_CACHE_TTL_STATE,
        'circuit_breaker_name': HA_CIRCUIT_BREAKER_NAME,
        'debug_mode': _is_debug_mode()
    }


def fuzzy_match_name(search_name: str, names: List[str], threshold: float = 0.6) -> Optional[str]:
    """Fuzzy match a name against a list."""
    from difflib import SequenceMatcher
    
    search_lower = search_name.lower()
    best_match = None
    best_ratio = threshold
    
    for name in names:
        ratio = SequenceMatcher(None, search_lower, name.lower()).ratio()
        if ratio > best_ratio:
            best_ratio = ratio
            best_match = name
    
    return best_match


def ha_operation_wrapper(feature: str, operation: str, func: Callable,
                         cache_key: Optional[str] = None,
                         cache_ttl: int = HA_CACHE_TTL_ENTITIES,
                         config: Optional[Dict] = None) -> Dict[str, Any]:
    """Generic operation wrapper for HA features."""
    correlation_id = generate_correlation_id()
    
    try:
        if _is_debug_mode():
            log_info(f"[{correlation_id}] [DEBUG ENTRY] HA_CORE: ha_operation_wrapper called")
            log_info(f"[{correlation_id}] [DEBUG] HA_CORE: feature={feature}, operation={operation}")
        
        log_info(f"[{correlation_id}] HA operation: {feature}.{operation}")
        
        if not config:
            config = get_ha_config()
        
        if cache_key:
            cached = cache_get(cache_key)
            if cached:
                log_debug(f"[{correlation_id}] Using cached result for {feature}.{operation}")
                return cached
        
        result = func(config)
        
        log_info(f"[{correlation_id}] HA operation {feature}.{operation} completed")
        
        if result.get('success') and cache_key:
            cache_set(cache_key, result, ttl=cache_ttl)
        
        if result.get('success'):
            record_metric(f'ha_{feature}_{operation}_success', 1.0)
        else:
            record_metric(f'ha_{feature}_{operation}_failure', 1.0)
        
        return result
        
    except Exception as e:
        log_error(f"[{correlation_id}] Operation wrapper failed: {str(e)}")
        record_metric(f'ha_{feature}_{operation}_error', 1.0)
        return create_error_response(str(e), 'OPERATION_FAILED')


__all__ = [
    'get_ha_config',
    'call_ha_api',
    'get_ha_states',
    'call_ha_service',
    'check_ha_status',
    'get_diagnostic_info',
    'ha_operation_wrapper',
    'fuzzy_match_name',
]

# EOF
