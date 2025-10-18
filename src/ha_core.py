"""
ha_core.py - Home Assistant Core Operations
Version: 2025.10.18.07
Description: Core operations using Gateway services exclusively. No direct HTTP.

CHANGELOG:
- 2025.10.18.07: Added DEBUG_MODE-controlled debug logging at entry points
  - Added _is_debug_mode() helper function
  - Added [DEBUG] logging controlled by DEBUG_MODE environment variable
  - Traces HA extension call path for troubleshooting
- 2025.10.18.06: FINAL - Complete defensive coding for all edge cases

Copyright 2025 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

import os
from typing import Dict, Any, Optional, List, Callable
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
        
        log_warning(f"Dict in {context} has keys: {list(data.keys())}, but no entity list found")
        return []
    
    log_warning(f"Unexpected type in {context}: {type(data)}")
    return []


def _ensure_dict(value: Any, context: str = "data") -> Dict[str, Any]:
    """Ensure value is a dict, parsing JSON strings if needed."""
    if value is None:
        return {}
    
    if isinstance(value, dict):
        return value
    
    if isinstance(value, str):
        try:
            parsed = parse_json(value)
            if isinstance(parsed, dict):
                log_debug(f"Parsed JSON string in {context}")
                return parsed
        except Exception as e:
            log_warning(f"Failed to parse JSON string in {context}: {str(e)}")
    
    log_warning(f"Value in {context} is {type(value)}, returning empty dict")
    return {}


def _safe_result_wrapper(result: Any, operation_name: str = "operation") -> Dict[str, Any]:
    """Safely wrap circuit breaker results to ensure dict response."""
    if result is None:
        return create_error_response(f'{operation_name} returned None', 'NULL_RESULT')
    
    if isinstance(result, Exception):
        return create_error_response(str(result), 'EXCEPTION_RESULT')
    
    if isinstance(result, dict):
        if 'success' in result or 'error' in result:
            return result
        return create_success_response(f'{operation_name} completed', result)
    
    if hasattr(result, '__dict__'):
        return create_error_response(
            f'{operation_name} returned unexpected object type: {type(result).__name__}',
            'INVALID_RESULT_TYPE'
        )
    
    try:
        return create_success_response(f'{operation_name} completed', {'result': result})
    except Exception as e:
        return create_error_response(f'Failed to wrap {operation_name} result: {str(e)}', 'RESULT_WRAP_FAILED')


def get_ha_config() -> Dict[str, Any]:
    """Get HA configuration using lazy import."""
    try:
        from ha_config import load_ha_config
        config = load_ha_config()
        if not isinstance(config, dict):
            log_error(f"load_ha_config returned {type(config)}, not dict")
            return {'enabled': False, 'base_url': '', 'access_token': '', 'timeout': 30}
        return config
    except Exception as e:
        log_error(f"Failed to load HA config: {str(e)}")
        return {'enabled': False, 'base_url': '', 'access_token': '', 'timeout': 30}


def call_ha_api(endpoint: str, method: str = 'GET', 
                data: Optional[Dict] = None) -> Dict[str, Any]:
    """Call Home Assistant API using Gateway HTTP_CLIENT with circuit breaker."""
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
        
        config = get_ha_config()
        
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
            'Authorization': f"Bearer {token[:10]}...",
            'Content-Type': 'application/json'
        }
        
        if _is_debug_mode():
            log_info(f"[{correlation_id}] [DEBUG STEP 5] HA_CORE: Making HTTP request to: {url}")
        
        def _make_request():
            if _is_debug_mode():
                log_info(f"[{correlation_id}] [DEBUG STEP 5a] HA_CORE: Calling HTTP_CLIENT.{method.lower()}")
            
            http_result = execute_operation(
                GatewayInterface.HTTP_CLIENT,
                method.lower(),
                url=url,
                headers={'Authorization': f"Bearer {token}", 'Content-Type': 'application/json'},
                json=data,
                timeout=config.get('timeout', 30)
            )
            
            if _is_debug_mode():
                log_info(f"[{correlation_id}] [DEBUG STEP 5b] HA_CORE: HTTP_CLIENT returned type: {type(http_result)}")
                log_info(f"[{correlation_id}] [DEBUG] HA_CORE: HTTP result keys: {list(http_result.keys()) if isinstance(http_result, dict) else 'NOT_DICT'}")
            
            return http_result
        
        if _is_debug_mode():
            log_info(f"[{correlation_id}] [DEBUG STEP 6] HA_CORE: Calling circuit breaker")
        
        raw_result = execute_operation(
            GatewayInterface.CIRCUIT_BREAKER,
            'call',
            name=HA_CIRCUIT_BREAKER_NAME,
            func=_make_request
        )
        
        if _is_debug_mode():
            log_info(f"[{correlation_id}] [DEBUG STEP 7] HA_CORE: Circuit breaker returned type: {type(raw_result)}")
            log_info(f"[{correlation_id}] [DEBUG] HA_CORE: Raw result: {raw_result if not isinstance(raw_result, dict) else list(raw_result.keys())}")
        
        if _is_debug_mode():
            log_info(f"[{correlation_id}] [DEBUG STEP 8] HA_CORE: Wrapping result")
        
        result = _safe_result_wrapper(raw_result, 'HA API call')
        
        if _is_debug_mode():
            log_info(f"[{correlation_id}] [DEBUG STEP 9] HA_CORE: Wrapped result type: {type(result)}")
            log_info(f"[{correlation_id}] [DEBUG] HA_CORE: Wrapped result keys: {list(result.keys())}")
            log_info(f"[{correlation_id}] [DEBUG] HA_CORE: Success: {result.get('success')}")
        
        if result.get('success'):
            if _is_debug_mode():
                log_info(f"[{correlation_id}] [DEBUG STEP 10] HA_CORE: SUCCESS - Data type: {type(result.get('data'))}")
            increment_counter('ha_api_success')
        else:
            if _is_debug_mode():
                log_error(f"[{correlation_id}] [DEBUG STEP 10] HA_CORE: FAILURE")
                log_error(f"[{correlation_id}] [DEBUG] HA_CORE: Error: {result.get('error', 'NO_ERROR_FIELD')}")
                log_error(f"[{correlation_id}] [DEBUG] HA_CORE: Error code: {result.get('error_code', 'NO_ERROR_CODE')}")
                log_error(f"[{correlation_id}] [DEBUG] HA_CORE: Full result: {result}")
            increment_counter('ha_api_failure')
        
        return result
        
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
        
        if not result.get('success'):
            if _is_debug_mode():
                log_error(f"[{correlation_id}] [DEBUG] HA_CORE: API call failed - full result: {result}")
            log_error(f"[{correlation_id}] API call failed - full result: {result}")
        
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
        'ha_core_version': '2025.10.18.07',
        'cache_ttl_entities': HA_CACHE_TTL_ENTITIES,
        'cache_ttl_state': HA_CACHE_TTL_STATE,
        'circuit_breaker_name': HA_CIRCUIT_BREAKER_NAME,
        'debug_mode': _is_debug_mode()
    }


def get_assistant_name_info() -> Dict[str, Any]:
    """Get assistant name configuration info."""
    config = get_ha_config()
    assistant_name = config.get('assistant_name', 'Unknown')
    
    return create_success_response('Assistant name info', {
        'assistant_name': assistant_name,
        'configured': bool(assistant_name and assistant_name != 'Unknown')
    })


def get_ha_entity_registry() -> Dict[str, Any]:
    """Get entity registry from HA."""
    return call_ha_api('/api/config/entity_registry/list')


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


def filter_exposed_entities_wrapper(entities: List[Dict[str, Any]], 
                                    config: Optional[Dict] = None) -> List[Dict[str, Any]]:
    """Filter entities for Alexa exposure."""
    # For now, return all entities - implement filtering logic as needed
    return entities


def initialize_ha_system(config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Initialize HA system."""
    correlation_id = generate_correlation_id()
    
    if _is_debug_mode():
        log_info(f"[{correlation_id}] [DEBUG ENTRY] HA_CORE: initialize_ha_system called")
    
    log_info(f"[{correlation_id}] Initializing HA system")
    
    # Validate config
    ha_config = get_ha_config()
    if not ha_config.get('enabled'):
        return create_error_response('HA not enabled', 'HA_DISABLED')
    
    # Test connection
    status = check_ha_status()
    if not status.get('success'):
        return status
    
    return create_success_response('HA system initialized', {
        'correlation_id': correlation_id
    })


def cleanup_ha_system() -> Dict[str, Any]:
    """Cleanup HA system resources."""
    correlation_id = generate_correlation_id()
    
    if _is_debug_mode():
        log_info(f"[{correlation_id}] [DEBUG ENTRY] HA_CORE: cleanup_ha_system called")
    
    log_info(f"[{correlation_id}] Cleaning up HA system")
    
    # Clear caches
    cache_delete('ha_all_states')
    
    return create_success_response('HA system cleaned up', {
        'correlation_id': correlation_id
    })


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
    'get_assistant_name_info',
    'get_ha_entity_registry',
    'filter_exposed_entities_wrapper',
    'ha_operation_wrapper',
    'fuzzy_match_name',
    'initialize_ha_system',
    'cleanup_ha_system',
]

# EOF
