"""
ha_core.py
Version: 2025.10.13.05
Description: HA Core utilities with generic wrapper pattern (Phase 2)
Copyright 2025 Joseph Hersey

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

import time
import json
from typing import Dict, Any, List, Optional, Callable
from difflib import SequenceMatcher

from gateway import (
    log_info,
    log_error,
    log_debug,
    create_success_response,
    create_error_response,
    cache_get,
    cache_set,
    generate_correlation_id,
    execute_with_circuit_breaker,
    increment_counter,
    record_metric,
    get_parameter,
    make_request,
    websocket_connect,
    websocket_send,
    websocket_receive,
    websocket_close,
    make_websocket_request
)

# ===== CONSTANTS =====

HA_CIRCUIT_BREAKER_NAME = "home_assistant"
HA_CACHE_TTL_STATE = 30
HA_CACHE_TTL_ENTITIES = 300
HA_CONSOLIDATED_CACHE_KEY = "ha_consolidated_cache"

# ===== PHASE 2: GENERIC WRAPPER PATTERN =====

def ha_operation_wrapper(
    feature_name: str,
    operation_name: str,
    operation_func: Callable,
    cache_key: Optional[str] = None,
    cache_ttl: int = 300,
    **kwargs
) -> Dict[str, Any]:
    """
    Generic wrapper for HA operations using ONLY gateway services.
    Eliminates 40+ duplicate code blocks across feature files.
    
    Args:
        feature_name: Feature name for logging (e.g., 'script', 'automation')
        operation_name: Operation name for logging (e.g., 'list', 'trigger')
        operation_func: Function to execute
        cache_key: Optional cache key for result caching
        cache_ttl: Cache TTL in seconds (default 300)
        **kwargs: Arguments passed to operation_func
    
    Returns:
        Dict with success/error response using gateway functions
    """
    correlation_id = generate_correlation_id()
    log_info(f"[{correlation_id}] {feature_name}.{operation_name} starting")
    
    try:
        # Check circuit breaker using gateway function
        if not is_ha_available():
            log_error(f"[{correlation_id}] Circuit breaker open for {feature_name}")
            increment_counter(f'ha_{feature_name}_circuit_breaker_open')
            return create_error_response(
                'circuit_breaker_open',
                'Home Assistant temporarily unavailable'
            )
        
        # Check cache if key provided
        if cache_key:
            cached = cache_get(cache_key)
            if cached:
                log_debug(f"[{correlation_id}] Cache hit: {cache_key}")
                increment_counter(f'ha_{feature_name}_cache_hit')
                return create_success_response("Cached result", cached)
        
        # Get config if not provided
        if 'config' not in kwargs or kwargs['config'] is None:
            kwargs['config'] = get_ha_config()
        
        # Execute operation
        start_time = time.time()
        result = operation_func(**kwargs)
        execution_time = (time.time() - start_time) * 1000
        
        # Record metrics using gateway
        record_metric(f'ha_{feature_name}_{operation_name}_time', execution_time)
        increment_counter(f'ha_{feature_name}_{operation_name}')
        
        # Cache result if successful and cache key provided
        if cache_key and result.get('success'):
            cache_set(cache_key, result.get('data'), ttl=cache_ttl)
            log_debug(f"[{correlation_id}] Cached result: {cache_key}")
        
        # Log result
        if result.get('success'):
            log_info(f"[{correlation_id}] {feature_name}.{operation_name} succeeded in {execution_time:.2f}ms")
            increment_counter(f'ha_{feature_name}_success')
        else:
            log_error(f"[{correlation_id}] {feature_name}.{operation_name} failed: {result.get('error')}")
            increment_counter(f'ha_{feature_name}_failure')
        
        return result
        
    except Exception as e:
        log_error(f"[{correlation_id}] {feature_name}.{operation_name} exception: {str(e)}")
        increment_counter(f'ha_{feature_name}_exception')
        record_metric(f'ha_{feature_name}_errors', 1.0)
        return create_error_response(f'{feature_name}_error', str(e))


# ===== PHASE 2: RESPONSE FORMATTING (from home_assistant_response.py) =====

def format_ha_success_response(
    message: str,
    data: Any = None,
    response_data: Optional[Dict] = None
) -> Dict[str, Any]:
    """Format successful HA response using gateway patterns."""
    response = create_success_response(message, data)
    if response_data:
        response['ha_response'] = response_data
    return response


def format_ha_error_response(
    error_message: str,
    error_details: Optional[Dict] = None,
    status_code: Optional[int] = None
) -> Dict[str, Any]:
    """Format HA error response using gateway patterns."""
    response = create_error_response(error_message)
    if error_details:
        response['error_details'] = error_details
    if status_code:
        response['status_code'] = status_code
    return response


def validate_ha_response(
    response: Dict[str, Any],
    required_fields: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Validate HA response structure."""
    if not isinstance(response, dict):
        return {
            'valid': False,
            'error': 'Response is not a dictionary'
        }
    
    if required_fields:
        missing = [f for f in required_fields if f not in response]
        if missing:
            return {
                'valid': False,
                'error': f'Missing required fields: {", ".join(missing)}'
            }
    
    return {'valid': True}


# ===== CONFIGURATION =====

def get_ha_config() -> Optional[Dict[str, Any]]:
    """Get HA configuration using gateway parameter store."""
    try:
        base_url = get_parameter('/homeassistant/base_url')
        access_token = get_parameter('/homeassistant/access_token')
        
        if not base_url or not access_token:
            log_error("Missing HA configuration parameters")
            return None
        
        return {
            'base_url': base_url.rstrip('/'),
            'access_token': access_token,
            'timeout': int(get_parameter('/homeassistant/timeout') or 30)
        }
    except Exception as e:
        log_error(f"Failed to get HA config: {str(e)}")
        return None


def get_consolidated_cache() -> Dict[str, Any]:
    """Get consolidated HA cache."""
    cached = cache_get(HA_CONSOLIDATED_CACHE_KEY)
    if cached:
        return cached
    return {
        'entity_states': {},
        'entity_list': [],
        'entity_registry': {},
        'timestamp': time.time()
    }


def set_consolidated_cache(data: Dict[str, Any]):
    """Set consolidated HA cache."""
    data['timestamp'] = time.time()
    cache_set(HA_CONSOLIDATED_CACHE_KEY, data, ttl=HA_CACHE_TTL_ENTITIES)


# ===== API COMMUNICATION =====

def call_ha_api(
    endpoint: str,
    ha_config: Optional[Dict[str, Any]] = None,
    method: str = 'GET',
    data: Optional[Dict] = None
) -> Dict[str, Any]:
    """Call Home Assistant API using gateway services."""
    correlation_id = generate_correlation_id()
    
    try:
        config = ha_config or get_ha_config()
        if not config:
            log_error(f"[{correlation_id}] No HA configuration available")
            return create_error_response('No HA configuration available')
        
        url = f"{config['base_url']}{endpoint}"
        headers = {
            "Authorization": f"Bearer {config['access_token']}",
            "Content-Type": "application/json"
        }
        
        log_info(f"[{correlation_id}] HA API call: {method} {endpoint}")
        
        def _make_ha_request():
            return make_request(
                method=method,
                url=url,
                headers=headers,
                data=data,
                timeout=config.get('timeout', 30)
            )
        
        result = execute_with_circuit_breaker(HA_CIRCUIT_BREAKER_NAME, _make_ha_request)
        
        record_metric('ha_api_calls', 1.0)
        
        if result.get('success'):
            log_info(f"[{correlation_id}] HA API call successful")
        else:
            log_error(f"[{correlation_id}] HA API call failed: {result.get('error')}")
        
        return result
        
    except Exception as e:
        log_error(f"[{correlation_id}] HA API call exception: {str(e)}")
        record_metric('ha_api_errors', 1.0)
        return create_error_response(str(e))


def batch_get_states(
    entity_ids: Optional[List[str]] = None,
    ha_config: Optional[Dict[str, Any]] = None,
    use_cache: bool = True,
    cache_ttl: int = HA_CACHE_TTL_STATE
) -> Dict[str, Any]:
    """Batch retrieve entity states using gateway services."""
    correlation_id = generate_correlation_id()
    
    try:
        log_info(f"[{correlation_id}] Batch get states: {len(entity_ids) if entity_ids else 'all'} entities")
        
        if use_cache:
            cache_key = f"ha_batch_states_{'_'.join(sorted(entity_ids)) if entity_ids else 'all'}"
            cached = cache_get(cache_key)
            if cached:
                log_debug(f"[{correlation_id}] Using cached states")
                return cached
        
        result = call_ha_api("/api/states", ha_config)
        
        if not result.get('success'):
            return result
        
        all_states = result.get('data', [])
        
        if entity_ids:
            entity_set = set(entity_ids)
            filtered_states = [
                state for state in all_states 
                if state.get('entity_id') in entity_set
            ]
            result['data'] = filtered_states
        
        if use_cache:
            cache_set(cache_key, result, ttl=cache_ttl)
        
        log_info(f"[{correlation_id}] Retrieved {len(result.get('data', []))} states")
        return result
        
    except Exception as e:
        log_error(f"[{correlation_id}] Batch get states failed: {str(e)}")
        return create_error_response(str(e))


def call_ha_service(
    domain: str,
    service: str,
    ha_config: Optional[Dict[str, Any]] = None,
    entity_id: Optional[str] = None,
    service_data: Optional[Dict] = None
) -> Dict[str, Any]:
    """Call Home Assistant service using gateway services."""
    correlation_id = generate_correlation_id()
    
    try:
        log_info(f"[{correlation_id}] Calling service: {domain}.{service} for {entity_id}")
        
        endpoint = f"/api/services/{domain}/{service}"
        
        data = service_data or {}
        if entity_id:
            data['entity_id'] = entity_id
        
        result = call_ha_api(endpoint, ha_config, method='POST', data=data)
        
        if result.get('success') and entity_id:
            cache_data = get_consolidated_cache()
            if entity_id in cache_data.get("entity_states", {}):
                del cache_data["entity_states"][entity_id]
                set_consolidated_cache(cache_data)
        
        increment_counter(f'ha_service_{domain}_{service}')
        return result
        
    except Exception as e:
        log_error(f"[{correlation_id}] Service call failed: {str(e)}")
        return create_error_response(str(e))


def get_entity_state(
    entity_id: str,
    ha_config: Optional[Dict[str, Any]] = None,
    use_cache: bool = True
) -> Dict[str, Any]:
    """Get entity state using gateway services."""
    correlation_id = generate_correlation_id()
    
    try:
        if use_cache:
            cache_data = get_consolidated_cache()
            if entity_id in cache_data.get("entity_states", {}):
                log_debug(f"[{correlation_id}] Using cached state for {entity_id}")
                return create_success_response(
                    f"Entity state for {entity_id}",
                    cache_data["entity_states"][entity_id]
                )
        
        endpoint = f"/api/states/{entity_id}"
        result = call_ha_api(endpoint, ha_config)
        
        if result.get('success') and use_cache:
            cache_data = get_consolidated_cache()
            cache_data["entity_states"][entity_id] = result.get('data')
            set_consolidated_cache(cache_data)
        
        return result
        
    except Exception as e:
        log_error(f"[{correlation_id}] Get entity state failed: {str(e)}")
        return create_error_response(str(e))


def is_ha_available() -> bool:
    """Check if HA is available using gateway circuit breaker."""
    try:
        from gateway import is_circuit_breaker_open
        return not is_circuit_breaker_open(HA_CIRCUIT_BREAKER_NAME)
    except:
        return True


# ===== WEBSOCKET SUPPORT (Phase 1) =====

def get_ha_entity_registry(
    ha_config: Optional[Dict[str, Any]] = None,
    use_cache: bool = True,
    cache_ttl: int = 600
) -> Dict[str, Any]:
    """Get HA entity registry via WebSocket using gateway services."""
    correlation_id = generate_correlation_id()
    
    try:
        log_info(f"[{correlation_id}] Getting entity registry via WebSocket")
        
        if use_cache:
            cached = cache_get("ha_entity_registry")
            if cached:
                log_debug(f"[{correlation_id}] Using cached entity registry")
                return create_success_response("Cached entity registry", cached)
        
        config = ha_config or get_ha_config()
        if not config:
            return create_error_response("No HA configuration available")
        
        ws_url = config['base_url'].replace('http://', 'ws://').replace('https://', 'wss://') + '/api/websocket'
        
        auth_message = {
            'type': 'auth',
            'access_token': config['access_token']
        }
        
        registry_message = {
            'id': 1,
            'type': 'config/entity_registry/list'
        }
        
        result = make_websocket_request(
            url=ws_url,
            message=registry_message,
            auth_message=auth_message,
            timeout=config.get('timeout', 30)
        )
        
        if result.get('success'):
            registry_data = result.get('data', {}).get('result', [])
            
            if use_cache:
                cache_set("ha_entity_registry", registry_data, ttl=cache_ttl)
            
            log_info(f"[{correlation_id}] Retrieved {len(registry_data)} registry entries")
            return create_success_response("Entity registry retrieved", registry_data)
        else:
            log_error(f"[{correlation_id}] WebSocket request failed: {result.get('error')}")
            return result
        
    except Exception as e:
        log_error(f"[{correlation_id}] Entity registry retrieval failed: {str(e)}")
        return create_error_response(str(e))


def filter_exposed_entities(
    entities: List[Dict[str, Any]],
    registry: Optional[List[Dict[str, Any]]] = None,
    ha_config: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """Filter entities by HA Assist exposure settings."""
    correlation_id = generate_correlation_id()
    
    try:
        if not registry:
            registry_result = get_ha_entity_registry(ha_config)
            if not registry_result.get('success'):
                log_error(f"[{correlation_id}] Could not get registry, returning all entities")
                return entities
            registry = registry_result.get('data', [])
        
        registry_map = {
            entry.get('entity_id'): entry.get('options', {}).get('conversation', {}).get('should_expose', True)
            for entry in registry
            if entry.get('entity_id')
        }
        
        filtered = [
            entity for entity in entities
            if registry_map.get(entity.get('entity_id'), True)
        ]
        
        log_info(f"[{correlation_id}] Filtered {len(entities)} entities to {len(filtered)} exposed entities")
        return filtered
        
    except Exception as e:
        log_error(f"[{correlation_id}] Entity filtering failed: {str(e)}, returning all entities")
        return entities


# ===== UTILITIES =====

def fuzzy_match_name(search_name: str, entity_names: List[str], threshold: float = 0.6) -> Optional[str]:
    """Fuzzy match entity name."""
    best_match = None
    best_ratio = 0.0
    
    search_lower = search_name.lower()
    
    for name in entity_names:
        name_lower = name.lower()
        ratio = SequenceMatcher(None, search_lower, name_lower).ratio()
        
        if ratio > best_ratio and ratio >= threshold:
            best_ratio = ratio
            best_match = name
    
    return best_match


def minimize_entity(entity: Dict[str, Any]) -> Dict[str, Any]:
    """Minimize entity data for response."""
    return {
        'entity_id': entity.get('entity_id'),
        'state': entity.get('state'),
        'name': entity.get('attributes', {}).get('friendly_name', entity.get('entity_id'))
    }


def minimize_entity_list(entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Minimize list of entities."""
    return [minimize_entity(e) for e in entities]


__all__ = [
    'ha_operation_wrapper',
    'format_ha_success_response',
    'format_ha_error_response',
    'validate_ha_response',
    'get_ha_config',
    'get_consolidated_cache',
    'set_consolidated_cache',
    'call_ha_api',
    'batch_get_states',
    'call_ha_service',
    'get_entity_state',
    'is_ha_available',
    'get_ha_entity_registry',
    'filter_exposed_entities',
    'fuzzy_match_name',
    'minimize_entity',
    'minimize_entity_list',
    'HA_CIRCUIT_BREAKER_NAME',
    'HA_CACHE_TTL_STATE',
    'HA_CACHE_TTL_ENTITIES'
]

# EOF
