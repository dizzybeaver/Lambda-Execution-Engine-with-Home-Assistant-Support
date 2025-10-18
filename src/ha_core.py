"""
ha_core.py - Home Assistant Core Operations
Version: 2025.10.18.01
Description: Core HA operations using Gateway exclusively. NO direct HTTP.

SUGA-ISP COMPLIANT:
- All infrastructure via gateway.py
- All HTTP via Gateway HTTP_CLIENT interface
- No direct urllib3/requests imports
- Circuit breaker protection via Gateway CIRCUIT_BREAKER interface

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
    generate_correlation_id, get_timestamp
)

# Cache TTL Constants
HA_CACHE_TTL_ENTITIES = 300
HA_CACHE_TTL_STATE = 60
HA_CACHE_TTL_CONFIG = 600
HA_CIRCUIT_BREAKER_NAME = "home_assistant"


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
        
        result = execute_operation(
            GatewayInterface.CIRCUIT_BREAKER,
            'call',
            name=HA_CIRCUIT_BREAKER_NAME,
            func=_make_request
        )
        
        if isinstance(result, dict) and result.get('success'):
            increment_counter('ha_api_success')
        else:
            increment_counter('ha_api_failure')
        
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
            if cached:
                log_debug(f"[{correlation_id}] Using cached states")
                increment_counter('ha_state_cache_hit')
                
                if entity_ids:
                    entity_set = set(entity_ids)
                    filtered = [e for e in cached.get('data', []) 
                               if e.get('entity_id') in entity_set]
                    return create_success_response('States retrieved from cache', filtered)
                
                return cached
        
        result = call_ha_api('/api/states')
        
        if result.get('success'):
            if use_cache:
                cache_set(cache_key, result, ttl=HA_CACHE_TTL_STATE)
            
            increment_counter('ha_states_retrieved')
            
            if entity_ids:
                entity_set = set(entity_ids)
                filtered = [e for e in result.get('data', []) 
                           if e.get('entity_id') in entity_set]
                return create_success_response('States retrieved', filtered)
        
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
            return create_success_response('HA is available', {
                'message': result.get('data', {}).get('message', 'API Running')
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
        
        result = execute_operation(
            GatewayInterface.CIRCUIT_BREAKER,
            'call',
            name=HA_CIRCUIT_BREAKER_NAME,
            func=_execute
        )
        
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
