"""
ha_core.py - Home Assistant Core Operations
Version: 2025.10.18.05
Description: Core operations using Gateway services exclusively. No direct HTTP.

CHANGELOG:
- 2025.10.18.05: FIXED Issue #32 - Handle dict response when expecting list
  - Added _extract_entity_list() to handle various response formats
  - Supports: direct list, dict with entities key, nested data structures
  - Fixes Discovery returning 0 endpoints
- 2025.10.18.04: FIXED Issue #31 - Fixed 'str' object has no attribute 'get'
- 2025.10.18.03: FIXED Issue #30 - Fixed 'object has no attribute get' in get_ha_states
- 2025.10.18.02: Fixed 'object has no attribute get' errors
- 2025.10.16.01: Fixed circuit breaker calls

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


def _extract_entity_list(data: Any, context: str = "states") -> List[Dict[str, Any]]:
    """
    Extract entity list from various response formats.
    
    HA /api/states returns different formats depending on how it's called:
    - Direct: [{entity1}, {entity2}, ...]
    - Wrapped: {'entities': [...]} or {'data': [...]}
    - HTTP response: {'body': [...]} or string JSON
    
    Args:
        data: Response data in various formats
        context: Description for logging
        
    Returns:
        List of entity dicts, or empty list if extraction fails
    """
    # Already a list
    if isinstance(data, list):
        log_debug(f"Data is already a list with {len(data)} items")
        return data
    
    # JSON string - parse it
    if isinstance(data, str):
        try:
            parsed = parse_json(data)
            log_debug(f"Parsed JSON string in {context}")
            return _extract_entity_list(parsed, context)  # Recurse
        except Exception as e:
            log_warning(f"Failed to parse JSON string in {context}: {str(e)}")
            return []
    
    # Dict - check for common entity list keys
    if isinstance(data, dict):
        # Try common keys where entity lists might be
        for key in ['entities', 'data', 'states', 'body', 'result']:
            if key in data:
                value = data[key]
                if isinstance(value, list):
                    log_debug(f"Found entity list in data['{key}'] with {len(value)} items")
                    return value
                elif isinstance(value, (str, dict)):
                    # Recurse in case it's nested
                    return _extract_entity_list(value, f"{context}.{key}")
        
        # No known keys - log what we got
        log_warning(f"Dict in {context} has keys: {list(data.keys())}, but no entity list found")
        return []
    
    # Unknown type
    log_warning(f"Unexpected type in {context}: {type(data)}")
    return []


def _ensure_dict(value: Any, context: str = "data") -> Dict[str, Any]:
    """
    Ensure value is a dict, parsing JSON strings if needed.
    
    CRITICAL: Prevents 'str' object has no attribute 'get' errors.
    """
    # Already a dict
    if isinstance(value, dict):
        return value
    
    # None or empty
    if value is None:
        return {}
    
    # JSON string - parse it
    if isinstance(value, str):
        try:
            parsed = parse_json(value)
            if isinstance(parsed, dict):
                log_debug(f"Parsed JSON string in {context}")
                return parsed
            else:
                log_warning(f"Parsed JSON in {context} is {type(parsed)}, not dict")
                return {}
        except Exception as e:
            log_warning(f"Failed to parse JSON string in {context}: {str(e)}")
            return {}
    
    # List or other type
    log_warning(f"Value in {context} is {type(value)}, returning empty dict")
    return {}


def _safe_result_wrapper(result: Any, operation_name: str = "operation") -> Dict[str, Any]:
    """
    Safely wrap circuit breaker results to ensure dict response.
    
    Circuit breaker returns whatever the wrapped function returns,
    which could be a dict, object, or exception. This ensures we
    always return a proper dict response.
    """
    # Already a dict - validate structure
    if isinstance(result, dict):
        # CRITICAL: Ensure 'data' field is present
        if 'data' in result:
            # Data could be a list (entities) or dict (single entity) or string (JSON)
            # Don't force it to dict - let caller handle appropriately
            pass
        
        # Ensure it has standard response fields
        if 'success' in result or 'error' in result:
            return result
        # Has data but no success flag - wrap it
        return create_success_response(f'{operation_name} completed', result)
    
    # None result
    if result is None:
        return create_error_response(
            f'{operation_name} returned None',
            'NULL_RESULT'
        )
    
    # Exception object
    if isinstance(result, Exception):
        return create_error_response(str(result), 'EXCEPTION_RESULT')
    
    # Some other object with attributes
    if hasattr(result, '__dict__'):
        return create_error_response(
            f'{operation_name} returned unexpected object type: {type(result).__name__}',
            'INVALID_RESULT_TYPE',
            details={'object_type': type(result).__name__}
        )
    
    # Primitive or unknown type - try to convert
    try:
        return create_success_response(f'{operation_name} completed', {'result': result})
    except Exception as e:
        return create_error_response(
            f'Failed to wrap {operation_name} result: {str(e)}',
            'RESULT_WRAP_FAILED'
        )


def get_ha_config() -> Dict[str, Any]:
    """Get HA configuration using lazy import."""
    from ha_config import load_ha_config
    return load_ha_config()


def call_ha_api(endpoint: str, method: str = 'GET', 
                data: Optional[Dict] = None) -> Dict[str, Any]:
    """Call Home Assistant API using Gateway HTTP_CLIENT with circuit breaker."""
    correlation_id = generate_correlation_id()
    
    try:
        config = get_ha_config()
        if not config.get('enabled'):
            return create_error_response('HA not enabled', 'HA_DISABLED')
        
        url = f"{config['base_url']}{endpoint}"
        headers = {
            'Authorization': f"Bearer {config['access_token']}",
            'Content-Type': 'application/json'
        }
        
        log_debug(f"[{correlation_id}] HA API: {method} {endpoint}")
        
        def _make_request():
            return execute_operation(
                GatewayInterface.HTTP_CLIENT,
                method.lower(),
                url=url,
                headers=headers,
                json=data,
                timeout=config.get('timeout', 30)
            )
        
        # Circuit breaker returns whatever _make_request returns
        raw_result = execute_operation(
            GatewayInterface.CIRCUIT_BREAKER,
            'call',
            name=HA_CIRCUIT_BREAKER_NAME,
            func=_make_request
        )
        
        # CRITICAL: Wrap result to ensure it's a dict
        result = _safe_result_wrapper(raw_result, 'HA API call')
        
        if result.get('success'):
            increment_counter('ha_api_success')
        else:
            increment_counter('ha_api_failure')
            log_warning(f"[{correlation_id}] HA API failed: {result.get('error', 'Unknown')}")
        
        return result
        
    except Exception as e:
        log_error(f"[{correlation_id}] HA API call failed: {str(e)}")
        increment_counter('ha_api_error')
        return create_error_response(str(e), 'API_CALL_FAILED')


def get_ha_states(entity_ids: Optional[List[str]] = None, 
                  use_cache: bool = True) -> Dict[str, Any]:
    """Get entity states using Gateway services."""
    correlation_id = generate_correlation_id()
    
    try:
        cache_key = 'ha_all_states'
        
        if use_cache:
            cached = cache_get(cache_key)
            # FIXED: Validate cached is a dict before using .get()
            if cached and isinstance(cached, dict):
                log_debug(f"[{correlation_id}] Using cached states")
                increment_counter('ha_state_cache_hit')
                
                if entity_ids:
                    entity_set = set(entity_ids)
                    # Extract entity list from cached data
                    cached_data = _extract_entity_list(cached.get('data', []), 'cached_states')
                    filtered = [e for e in cached_data 
                               if isinstance(e, dict) and e.get('entity_id') in entity_set]
                    return create_success_response('States retrieved from cache', filtered)
                
                return cached
            elif cached:
                # Invalid cache type - delete it
                log_warning(f"[{correlation_id}] Cached data is {type(cached)}, not dict - invalidating")
                cache_delete(cache_key)
        
        # Fetch fresh data
        result = call_ha_api('/api/states')
        
        # FIXED: Validate result is a dict
        if not isinstance(result, dict):
            log_error(f"[{correlation_id}] call_ha_api returned {type(result)}, not dict")
            return create_error_response(
                f'API returned invalid type: {type(result).__name__}',
                'INVALID_API_RESPONSE'
            )
        
        if result.get('success'):
            # CRITICAL: Extract entity list from response data
            raw_data = result.get('data', [])
            entity_list = _extract_entity_list(raw_data, 'api_states')
            
            # Store entity list in proper format
            normalized_result = create_success_response('States retrieved', entity_list)
            
            if use_cache:
                cache_set(cache_key, normalized_result, ttl=HA_CACHE_TTL_STATE)
            
            increment_counter('ha_states_retrieved')
            
            if entity_ids:
                entity_set = set(entity_ids)
                filtered = [e for e in entity_list 
                           if isinstance(e, dict) and e.get('entity_id') in entity_set]
                return create_success_response('States retrieved', filtered)
            
            return normalized_result
        
        return result
        
    except Exception as e:
        log_error(f"[{correlation_id}] Get states failed: {str(e)}")
        return create_error_response(str(e), 'GET_STATES_FAILED')


def call_ha_service(domain: str, service: str, 
                   entity_id: Optional[str] = None,
                   service_data: Optional[Dict] = None) -> Dict[str, Any]:
    """Call Home Assistant service."""
    correlation_id = generate_correlation_id()
    
    try:
        endpoint = f'/api/services/{domain}/{service}'
        
        data = service_data or {}
        if entity_id:
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
    try:
        result = call_ha_api('/api/')
        
        if result.get('success'):
            # FIXED: Ensure data is dict before calling .get()
            data = _ensure_dict(result.get('data', {}), 'status_check')
            return create_success_response('HA is available', {
                'message': data.get('message', 'API Running')
            })
        
        return result
        
    except Exception as e:
        log_error(f"HA status check failed: {str(e)}")
        return create_error_response(str(e), 'STATUS_CHECK_FAILED')


def get_diagnostic_info() -> Dict[str, Any]:
    """Get comprehensive diagnostic info about HA integration."""
    try:
        config = get_ha_config()
        status = check_ha_status()
        
        breaker_state = execute_operation(
            GatewayInterface.CIRCUIT_BREAKER,
            'get',
            name=HA_CIRCUIT_BREAKER_NAME
        )
        
        return create_success_response('Diagnostic info retrieved', {
            'timestamp': get_timestamp(),
            'ha_enabled': config.get('enabled', False),
            'connection_status': status.get('success', False),
            'assistant_name': config.get('assistant_name', 'Unknown'),
            'circuit_breaker': breaker_state,
            'configuration': {
                'base_url': config.get('base_url', 'Not set'),
                'timeout': config.get('timeout', 30)
            }
        })
        
    except Exception as e:
        log_error(f"Diagnostic info failed: {str(e)}")
        return create_error_response(str(e), 'DIAGNOSTIC_FAILED')


def get_assistant_name_info() -> Dict[str, Any]:
    """Get assistant name configuration status."""
    try:
        config = get_ha_config()
        assistant_name = config.get('assistant_name', 'Not configured')
        
        return create_success_response('Assistant name info retrieved', {
            'assistant_name': assistant_name,
            'configured': bool(assistant_name and assistant_name != 'Not configured'),
            'source': 'environment' if os.getenv('HA_ASSISTANT_NAME') else 'parameter_store'
        })
        
    except Exception as e:
        log_error(f"Assistant name check failed: {str(e)}")
        return create_error_response(str(e), 'ASSISTANT_NAME_CHECK_FAILED')


def get_ha_entity_registry(use_cache: bool = True) -> Dict[str, Any]:
    """Get entity registry via WebSocket if enabled, fallback to REST."""
    try:
        from ha_websocket import is_websocket_enabled, get_entity_registry_via_websocket
        
        if is_websocket_enabled():
            log_debug("Attempting WebSocket entity registry fetch")
            result = get_entity_registry_via_websocket(use_cache=use_cache)
            
            if result.get('success'):
                return result
            else:
                log_warning("WebSocket registry fetch failed, falling back to REST")
        
        log_debug("Using REST API for entity list")
        return get_ha_states(use_cache=use_cache)
        
    except Exception as e:
        log_error(f"Entity registry fetch failed: {str(e)}")
        return get_ha_states(use_cache=use_cache)


def filter_exposed_entities_wrapper(entities: Optional[List[Dict]] = None) -> Dict[str, Any]:
    """Filter entities to exposed ones with WebSocket support."""
    try:
        from ha_websocket import is_websocket_enabled, filter_exposed_entities
        
        if entities is None:
            result = get_ha_entity_registry(use_cache=True)
            if not result.get('success'):
                return result
            entities = result.get('data', [])
        
        if is_websocket_enabled():
            filtered = filter_exposed_entities(entities)
            return create_success_response('Entities filtered', filtered)
        
        return create_success_response('All entities returned (WebSocket disabled)', entities)
        
    except Exception as e:
        log_error(f"Filter exposed entities failed: {str(e)}")
        return create_error_response(str(e), 'FILTER_ENTITIES_FAILED')


def ha_operation_wrapper(feature: str, operation: str, func: Callable,
                        config: Optional[Dict] = None, cache_key: Optional[str] = None,
                        cache_ttl: int = 300, **kwargs) -> Dict[str, Any]:
    """Generic wrapper for HA operations with circuit breaker and caching."""
    correlation_id = generate_correlation_id()
    
    try:
        log_debug(f"[{correlation_id}] HA operation: {feature}.{operation}")
        record_metric(f'ha_{feature}_{operation}_started', 1.0)
        
        if cache_key:
            cached = cache_get(cache_key)
            if cached:
                log_debug(f"[{correlation_id}] Using cached result")
                increment_counter(f'ha_{feature}_cache_hit')
                return cached
        
        ha_config = config or get_ha_config()
        
        def _execute():
            return func(ha_config, **kwargs)
        
        # Circuit breaker returns raw result
        raw_result = execute_operation(
            GatewayInterface.CIRCUIT_BREAKER,
            'call',
            name=HA_CIRCUIT_BREAKER_NAME,
            func=_execute
        )
        
        # CRITICAL: Wrap result to ensure it's a dict
        result = _safe_result_wrapper(raw_result, f'{feature}.{operation}')
        
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
]

# EOF
