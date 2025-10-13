"""
ha_core.py
Version: 2025.10.13.03
Description: Home Assistant core utilities with WebSocket support (SUGA Compliant)
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
from typing import Dict, Any, Optional, List
from difflib import SequenceMatcher
from gateway import (
    log_info, log_error, log_debug, create_success_response, create_error_response,
    generate_correlation_id, cache_get, cache_set, make_request, execute_with_circuit_breaker,
    record_metric, increment_counter, get_parameter, 
    websocket_connect, websocket_send, websocket_receive, websocket_close, make_websocket_request
)

# ===== CONSTANTS =====
HA_CIRCUIT_BREAKER_NAME = "home_assistant"
HA_CACHE_TTL_STATE = 60
HA_CACHE_TTL_ENTITIES = 300
HA_CACHE_TTL_REGISTRY = 600
HA_CONSOLIDATED_CACHE_KEY = "ha_consolidated"
HA_REGISTRY_CACHE_KEY = "ha_entity_registry"

# ===== CONFIGURATION MANAGEMENT =====

def get_ha_config() -> Dict[str, Any]:
    """Get Home Assistant configuration using gateway."""
    correlation_id = generate_correlation_id()
    
    try:
        base_url = get_parameter('homeassistant/url')
        token = get_parameter('homeassistant/token')
        timeout = get_parameter('homeassistant/timeout', 30)
        verify_ssl = get_parameter('homeassistant/verify_ssl', True)
        
        if not base_url or not token:
            log_error(f"[{correlation_id}] Missing HA configuration")
            return {}
        
        config = {
            'base_url': base_url.rstrip('/'),
            'access_token': token,
            'timeout': int(timeout),
            'verify_ssl': verify_ssl
        }
        
        log_debug(f"[{correlation_id}] HA config retrieved")
        return config
        
    except Exception as e:
        log_error(f"[{correlation_id}] Failed to get HA config: {str(e)}")
        return {}

# ===== CACHE MANAGEMENT =====

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

def call_ha_api(endpoint: str, ha_config: Optional[Dict[str, Any]] = None, 
                method: str = 'GET', data: Optional[Dict] = None) -> Dict[str, Any]:
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

def batch_get_states(entity_ids: Optional[List[str]] = None,
                    ha_config: Optional[Dict[str, Any]] = None,
                    use_cache: bool = True,
                    cache_ttl: int = HA_CACHE_TTL_STATE) -> Dict[str, Any]:
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

def call_ha_service(domain: str, service: str, 
                   ha_config: Optional[Dict[str, Any]] = None,
                   entity_id: Optional[str] = None,
                   service_data: Optional[Dict] = None) -> Dict[str, Any]:
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

def get_entity_state(entity_id: str,
                    ha_config: Optional[Dict[str, Any]] = None,
                    use_cache: bool = True) -> Dict[str, Any]:
    """Get entity state using gateway services."""
    correlation_id = generate_correlation_id()
    
    try:
        if use_cache:
            cache_data = get_consolidated_cache()
            cached_state = cache_data.get("entity_states", {}).get(entity_id)
            if cached_state and time.time() - cached_state.get("timestamp", 0) < HA_CACHE_TTL_STATE:
                return cached_state.get("data", {})
        
        endpoint = f"/api/states/{entity_id}"
        response = call_ha_api(endpoint, ha_config)
        
        if not response.get('success'):
            return {}
        
        entity_data = response.get('data', {})
        
        if use_cache:
            cache_data = get_consolidated_cache()
            if "entity_states" not in cache_data:
                cache_data["entity_states"] = {}
            cache_data["entity_states"][entity_id] = {
                "data": entity_data,
                "timestamp": time.time()
            }
            set_consolidated_cache(cache_data)
        
        return entity_data
        
    except Exception as e:
        log_error(f"[{correlation_id}] Get entity state failed: {str(e)}")
        return {}

def is_ha_available(ha_config: Optional[Dict[str, Any]] = None) -> bool:
    """Check if Home Assistant is available using gateway services."""
    correlation_id = generate_correlation_id()
    
    try:
        result = call_ha_api("/api/", ha_config)
        is_available = result.get('success', False) and result.get('status_code') == 200
        
        log_debug(f"[{correlation_id}] HA availability: {is_available}")
        return is_available
        
    except Exception:
        log_error(f"[{correlation_id}] HA availability check failed")
        return False

# ===== WEBSOCKET OPERATIONS =====

def get_ha_entity_registry(ha_config: Optional[Dict[str, Any]] = None,
                          use_cache: bool = True,
                          force_refresh: bool = False) -> Dict[str, Any]:
    """
    Get Home Assistant entity registry with exposure settings via WebSocket.
    Uses gateway WebSocket functions with circuit breaker protection.
    """
    correlation_id = generate_correlation_id()
    
    try:
        if use_cache and not force_refresh:
            cached = cache_get(HA_REGISTRY_CACHE_KEY)
            if cached:
                log_debug(f"[{correlation_id}] Using cached entity registry")
                return cached
        
        config = ha_config or get_ha_config()
        if not config:
            log_error(f"[{correlation_id}] No HA configuration")
            return create_error_response('No HA configuration')
        
        ws_url = config['base_url'].replace('http://', 'ws://').replace('https://', 'wss://') + '/api/websocket'
        
        log_info(f"[{correlation_id}] Fetching entity registry via WebSocket")
        
        def _get_registry():
            # Connect to WebSocket
            conn_result = websocket_connect(ws_url, timeout=10, correlation_id=correlation_id)
            if not conn_result.get('success'):
                return conn_result
            
            connection = conn_result['data']['connection']
            
            try:
                # Receive auth_required message
                auth_req = websocket_receive(connection, timeout=5, correlation_id=correlation_id)
                if not auth_req.get('success'):
                    websocket_close(connection, correlation_id)
                    return auth_req
                
                # Send auth message
                auth_msg = {
                    'type': 'auth',
                    'access_token': config['access_token']
                }
                auth_send = websocket_send(connection, auth_msg, correlation_id)
                if not auth_send.get('success'):
                    websocket_close(connection, correlation_id)
                    return auth_send
                
                # Receive auth_ok
                auth_ok = websocket_receive(connection, timeout=5, correlation_id=correlation_id)
                if not auth_ok.get('success'):
                    websocket_close(connection, correlation_id)
                    return auth_ok
                
                # Request entity registry
                registry_msg = {
                    'id': 1,
                    'type': 'config/entity_registry/list'
                }
                reg_send = websocket_send(connection, registry_msg, correlation_id)
                if not reg_send.get('success'):
                    websocket_close(connection, correlation_id)
                    return reg_send
                
                # Receive registry response
                reg_response = websocket_receive(connection, timeout=10, correlation_id=correlation_id)
                websocket_close(connection, correlation_id)
                
                if not reg_response.get('success'):
                    return reg_response
                
                registry_data = reg_response['data']['message'].get('result', [])
                
                log_info(f"[{correlation_id}] Retrieved {len(registry_data)} registry entries")
                record_metric('ha_registry_fetches', 1.0)
                
                return create_success_response("Entity registry retrieved", {
                    'entities': registry_data,
                    'count': len(registry_data)
                })
                
            except Exception as e:
                websocket_close(connection, correlation_id)
                raise e
        
        result = execute_with_circuit_breaker(HA_CIRCUIT_BREAKER_NAME, _get_registry)
        
        if result.get('success') and use_cache:
            cache_set(HA_REGISTRY_CACHE_KEY, result, ttl=HA_CACHE_TTL_REGISTRY)
        
        return result
        
    except Exception as e:
        log_error(f"[{correlation_id}] Failed to get entity registry: {str(e)}")
        record_metric('ha_registry_errors', 1.0)
        return create_error_response(str(e))

def filter_exposed_entities(entities: List[Dict[str, Any]], 
                           ha_config: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """
    Filter entities by Assist exposure settings using entity registry.
    Returns only entities exposed to Alexa/voice assistants.
    """
    correlation_id = generate_correlation_id()
    
    try:
        log_info(f"[{correlation_id}] Filtering {len(entities)} entities by exposure")
        
        registry_result = get_ha_entity_registry(ha_config, use_cache=True)
        
        if not registry_result.get('success'):
            log_error(f"[{correlation_id}] Could not get registry, returning all entities")
            return entities
        
        registry_entities = registry_result['data']['entities']
        
        exposed_entity_ids = set()
        for reg_entity in registry_entities:
            options = reg_entity.get('options', {})
            conversation_options = options.get('conversation', {})
            
            # Check if exposed to Alexa/conversation
            if conversation_options.get('should_expose', False):
                exposed_entity_ids.add(reg_entity.get('entity_id'))
        
        filtered = [e for e in entities if e.get('entity_id') in exposed_entity_ids]
        
        log_info(f"[{correlation_id}] Filtered to {len(filtered)} exposed entities")
        record_metric('ha_exposure_filter', 1.0)
        
        return filtered
        
    except Exception as e:
        log_error(f"[{correlation_id}] Exposure filtering failed: {str(e)}, returning all")
        return entities

# ===== UTILITY FUNCTIONS =====

def fuzzy_match_name(search: str, options: List[str], threshold: float = 0.6) -> Optional[str]:
    """Fuzzy match name against options."""
    if not search or not options:
        return None
    
    search_lower = search.lower()
    best_match = None
    best_ratio = 0.0
    
    for option in options:
        option_lower = option.lower()
        ratio = SequenceMatcher(None, search_lower, option_lower).ratio()
        
        if ratio > best_ratio and ratio >= threshold:
            best_ratio = ratio
            best_match = option
    
    return best_match

def minimize_entity(entity: Dict[str, Any]) -> Dict[str, Any]:
    """Minimize entity data for memory optimization."""
    return {
        'entity_id': entity.get('entity_id'),
        'state': entity.get('state'),
        'attributes': {
            'friendly_name': entity.get('attributes', {}).get('friendly_name'),
            'device_class': entity.get('attributes', {}).get('device_class')
        }
    }

def minimize_entity_list(entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Minimize entity list for memory optimization."""
    return [minimize_entity(e) for e in entities if isinstance(e, dict)]

# ===== EXPORTS =====

__all__ = [
    'HA_CIRCUIT_BREAKER_NAME',
    'HA_CACHE_TTL_STATE',
    'HA_CACHE_TTL_ENTITIES',
    'HA_CACHE_TTL_REGISTRY',
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
]

# EOF
