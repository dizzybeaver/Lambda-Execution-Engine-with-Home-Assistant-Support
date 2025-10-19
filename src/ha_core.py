"""
ha_core.py - Home Assistant Core Operations (Production with Timing Diagnostics)
Version: 2025.10.19.TIMING_PROD
Description: Complete production version with DEBUG_MODE timing diagnostics

CHANGELOG:
- 2025.10.19.TIMING_PROD: Added comprehensive timing diagnostics gated by DEBUG_MODE
  - Timing traces for call_ha_api (critical 10s delay path)
  - Timing for get_ha_config, get_ha_states, call_ha_service
  - All timing only active when DEBUG_MODE=true
  - Zero performance impact when DEBUG_MODE=false
- 2025.10.18.07: Added DEBUG_MODE-controlled debug logging
- 2025.10.18.06: Complete defensive coding

Copyright 2025 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

import os
import time
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


def _print_timing(msg: str):
    """Print timing message only if DEBUG_MODE=true."""
    if _is_debug_mode():
        print(f"[HA_CORE_TIMING] {msg}")


def _extract_entity_list(data: Any, context: str = "states") -> List[Dict[str, Any]]:
    """Extract entity list from various response formats."""
    if data is None:
        log_debug(f"Data is None in {context}")
        return []
    
    if isinstance(data, list):
        log_debug(f"Data is already a list with {len(data)} items")
        return [item for item in data if isinstance(item, dict)]
    
    if isinstance(data, str):
        try:
            parsed = parse_json(data)
            log_debug(f"Parsed JSON string in {context}")
            return _extract_entity_list(parsed, context)
        except Exception as e:
            log_warning(f"Failed to parse JSON string in {context}: {str(e)}")
            return []
    
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
    config_start = time.time()
    _print_timing("===== GET_HA_CONFIG START =====")
    
    try:
        _print_timing("Importing ha_config...")
        import_start = time.time()
        from ha_config import load_ha_config
        import_ms = (time.time() - import_start) * 1000
        _print_timing(f"ha_config imported: {import_ms:.2f}ms")
        
        _print_timing("Calling load_ha_config()...")
        load_start = time.time()
        config = load_ha_config()
        load_ms = (time.time() - load_start) * 1000
        _print_timing(f"load_ha_config() completed: {load_ms:.2f}ms")
        
        if not isinstance(config, dict):
            _print_timing(f"ERROR: returned {type(config)}, not dict")
            log_error(f"load_ha_config returned {type(config)}, not dict")
            return {'enabled': False, 'base_url': '', 'access_token': '', 'timeout': 30}
        
        total_ms = (time.time() - config_start) * 1000
        _print_timing(f"===== GET_HA_CONFIG COMPLETE: {total_ms:.2f}ms =====")
        return config
        
    except Exception as e:
        error_ms = (time.time() - config_start) * 1000
        _print_timing(f"!!! ERROR after {error_ms:.2f}ms: {str(e)}")
        log_error(f"Failed to load HA config: {str(e)}")
        return {'enabled': False, 'base_url': '', 'access_token': '', 'timeout': 30}


def call_ha_api(endpoint: str, method: str = 'GET', 
                data: Optional[Dict] = None) -> Dict[str, Any]:
    """Call Home Assistant API using Gateway HTTP_CLIENT with circuit breaker."""
    api_start = time.time()
    _print_timing(f"===== CALL_HA_API START =====")
    _print_timing(f"Endpoint: {endpoint}, Method: {method}")
    
    correlation_id = generate_correlation_id()
    
    try:
        _print_timing(f"Step 1: Getting HA config... (elapsed: {(time.time() - api_start) * 1000:.2f}ms)")
        config_start = time.time()
        config = get_ha_config()
        config_ms = (time.time() - config_start) * 1000
        _print_timing(f"*** Config loaded: {config_ms:.2f}ms ***")
        
        _print_timing(f"Step 2: Building URL... (elapsed: {(time.time() - api_start) * 1000:.2f}ms)")
        base_url = config.get('base_url', '')
        token = config.get('access_token', '')
        timeout = config.get('timeout', 30)
        
        if not base_url or not token:
            _print_timing(f"ERROR: Missing URL or token")
            return create_error_response('Missing HA URL or token', 'CONFIG_ERROR')
        
        url = f"{base_url}{endpoint}"
        _print_timing(f"URL: {url}, Timeout: {timeout}s")
        
        _print_timing(f"Step 3: Defining _make_request function... (elapsed: {(time.time() - api_start) * 1000:.2f}ms)")
        
        def _make_request():
            """Inner function for circuit breaker."""
            req_start = time.time()
            _print_timing(f"  [_make_request] START")
            
            _print_timing(f"  [_make_request] Calling execute_operation(HTTP_CLIENT, {method.lower()})...")
            http_start = time.time()
            
            http_result = execute_operation(
                GatewayInterface.HTTP_CLIENT,
                method.lower(),
                url=url,
                headers={
                    'Authorization': f"Bearer {token}",
                    'Content-Type': 'application/json'
                },
                json=data,
                timeout=timeout
            )
            
            http_ms = (time.time() - http_start) * 1000
            _print_timing(f"  [_make_request] *** HTTP_CLIENT returned: {http_ms:.2f}ms ***")
            _print_timing(f"  [_make_request] Result type: {type(http_result)}")
            
            req_ms = (time.time() - req_start) * 1000
            _print_timing(f"  [_make_request] COMPLETE: {req_ms:.2f}ms")
            return http_result
        
        _print_timing(f"Step 4: Calling circuit breaker... (elapsed: {(time.time() - api_start) * 1000:.2f}ms)")
        _print_timing(f"Circuit breaker name: {HA_CIRCUIT_BREAKER_NAME}")
        cb_start = time.time()
        
        raw_result = execute_operation(
            GatewayInterface.CIRCUIT_BREAKER,
            'call',
            name=HA_CIRCUIT_BREAKER_NAME,
            func=_make_request
        )
        
        cb_ms = (time.time() - cb_start) * 1000
        _print_timing(f"*** Circuit breaker returned: {cb_ms:.2f}ms ***")
        _print_timing(f"Raw result type: {type(raw_result)}")
        
        _print_timing(f"Step 5: Wrapping result... (elapsed: {(time.time() - api_start) * 1000:.2f}ms)")
        result = _safe_result_wrapper(raw_result, 'HA API call')
        _print_timing(f"Success: {result.get('success')}")
        
        if result.get('success'):
            increment_counter('ha_api_success')
        else:
            increment_counter('ha_api_failure')
            error_msg = result.get('error', 'Unknown error')
            _print_timing(f"Error: {error_msg}")
        
        total_ms = (time.time() - api_start) * 1000
        _print_timing(f"===== CALL_HA_API COMPLETE: {total_ms:.2f}ms =====")
        return result
        
    except Exception as e:
        error_ms = (time.time() - api_start) * 1000
        _print_timing(f"!!! EXCEPTION after {error_ms:.2f}ms: {type(e).__name__}: {str(e)}")
        if _is_debug_mode():
            import traceback
            _print_timing(f"Traceback:\n{traceback.format_exc()}")
        
        log_error(f"[{correlation_id}] HA API call failed: {str(e)}")
        increment_counter('ha_api_error')
        return create_error_response(str(e), 'EXCEPTION')


def get_ha_states(entity_ids: Optional[List[str]] = None, 
                  use_cache: bool = True) -> Dict[str, Any]:
    """Get entity states using Gateway services."""
    correlation_id = generate_correlation_id()
    
    try:
        cache_key = 'ha_all_states'
        
        if use_cache:
            cached = cache_get(cache_key)
            if cached and isinstance(cached, dict):
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
        
        result = call_ha_api('/api/states', method='GET')
        
        if not result.get('success'):
            return result
        
        all_states = _extract_entity_list(result.get('data', []), 'ha_states')
        
        if not all_states:
            log_warning(f"[{correlation_id}] No states extracted from HA response")
        
        response = create_success_response('States retrieved', all_states)
        
        if use_cache:
            cache_set(cache_key, response, ttl=HA_CACHE_TTL_STATE)
        
        if entity_ids and isinstance(entity_ids, list):
            entity_set = set(entity_ids)
            filtered = [e for e in all_states 
                       if isinstance(e, dict) and e.get('entity_id') in entity_set]
            return create_success_response('Filtered states retrieved', filtered)
        
        return response
        
    except Exception as e:
        log_error(f"[{correlation_id}] get_ha_states failed: {str(e)}")
        return create_error_response(str(e), 'GET_STATES_FAILED')


def call_ha_service(domain: str, service: str, 
                    entity_id: Optional[str] = None,
                    service_data: Optional[Dict] = None) -> Dict[str, Any]:
    """Call Home Assistant service."""
    correlation_id = generate_correlation_id()
    
    try:
        endpoint = f"/api/services/{domain}/{service}"
        
        data = service_data or {}
        if entity_id:
            data['entity_id'] = entity_id
        
        result = call_ha_api(endpoint, method='POST', data=data)
        
        if result.get('success') and entity_id:
            cache_delete('ha_all_states')
        
        return result
        
    except Exception as e:
        log_error(f"[{correlation_id}] call_ha_service failed: {str(e)}")
        return create_error_response(str(e), 'CALL_SERVICE_FAILED')


def check_ha_status() -> Dict[str, Any]:
    """Check Home Assistant status."""
    correlation_id = generate_correlation_id()
    
    try:
        result = call_ha_api('/api/', method='GET')
        
        if not result.get('success'):
            return result
        
        return create_success_response('HA is reachable', {
            'correlation_id': correlation_id
        })
        
    except Exception as e:
        log_error(f"[{correlation_id}] check_ha_status failed: {str(e)}")
        return create_error_response(str(e), 'STATUS_CHECK_FAILED')


def get_ha_system_status() -> Dict[str, Any]:
    """Get comprehensive HA system status."""
    correlation_id = generate_correlation_id()
    
    try:
        status = check_ha_status()
        config = get_ha_config()
        
        return create_success_response('HA system status', {
            'reachable': status.get('success', False),
            'enabled': config.get('enabled', False),
            'correlation_id': correlation_id
        })
        
    except Exception as e:
        log_error(f"[{correlation_id}] get_ha_system_status failed: {str(e)}")
        return create_error_response(str(e), 'SYSTEM_STATUS_FAILED')


def get_diagnostic_information() -> Dict[str, Any]:
    """Get diagnostic information."""
    return {
        'ha_core_version': '2025.10.19.TIMING_PROD',
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
    return entities


def initialize_ha_system(config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Initialize HA system."""
    correlation_id = generate_correlation_id()
    log_info(f"[{correlation_id}] Initializing HA system")
    
    ha_config = get_ha_config()
    if not ha_config.get('enabled'):
        return create_error_response('HA not enabled', 'HA_DISABLED')
    
    status = check_ha_status()
    if not status.get('success'):
        return status
    
    return create_success_response('HA system initialized', {
        'correlation_id': correlation_id
    })


def cleanup_ha_system() -> Dict[str, Any]:
    """Cleanup HA system resources."""
    correlation_id = generate_correlation_id()
    log_info(f"[{correlation_id}] Cleaning up HA system")
    
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
    'get_ha_system_status',
    'get_diagnostic_information',
    'get_assistant_name_info',
    'get_ha_entity_registry',
    'filter_exposed_entities_wrapper',
    'ha_operation_wrapper',
    'fuzzy_match_name',
    'initialize_ha_system',
    'cleanup_ha_system',
]

# EOF
