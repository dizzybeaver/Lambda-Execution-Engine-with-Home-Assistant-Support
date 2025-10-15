"""
home_assistant/ha_core.py - Home Assistant Core Operations
Version: 2025.10.14.01
Description: Core operations using Gateway services exclusively. No direct HTTP.

Copyright 2025 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

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

# ===== CONFIGURATION =====

def get_ha_config() -> Dict[str, Any]:
    """Get HA configuration using lazy import."""
    from ha_config import load_ha_config
    return load_ha_config()


# ===== CORE API OPERATIONS =====

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
        
        # Use Gateway HTTP_CLIENT through circuit breaker
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
            'execute',
            breaker_name=HA_CIRCUIT_BREAKER_NAME,
            func=_make_request
        )
        
        if result.get('success'):
            increment_counter('ha_api_success')
        else:
            increment_counter('ha_api_failure')
        
        return result
        
    except Exception as e:
        log_error(f"[{correlation_id}] HA API call failed: {str(e)}")
        increment_counter('ha_api_error')
        return create_error_response(str(e), 'API_CALL_FAILED')


# ===== STATE OPERATIONS =====

def get_states(entity_ids: Optional[List[str]] = None, 
               use_cache: bool = True) -> Dict[str, Any]:
    """Get entity states using Gateway services."""
    correlation_id = generate_correlation_id()
    
    try:
        cache_key = f"ha_states_{'_'.join(sorted(entity_ids)) if entity_ids else 'all'}"
        
        if use_cache:
            cached = cache_get(cache_key)
            if cached:
                log_debug(f"[{correlation_id}] Using cached states")
                increment_counter('ha_states_cache_hit')
                return cached
        
        result = call_ha_api('/api/states')
        
        if not result.get('success'):
            return result
        
        all_states = result.get('data', [])
        
        if entity_ids:
            entity_set = set(entity_ids)
            all_states = [s for s in all_states if s.get('entity_id') in entity_set]
        
        response = create_success_response('States retrieved', {
            'states': all_states,
            'count': len(all_states)
        })
        
        if use_cache:
            cache_set(cache_key, response, ttl=HA_CACHE_TTL_STATE)
        
        increment_counter('ha_states_retrieved')
        return response
        
    except Exception as e:
        log_error(f"[{correlation_id}] Get states failed: {str(e)}")
        return create_error_response(str(e), 'GET_STATES_FAILED')


def get_entity_state(entity_id: str, use_cache: bool = True) -> Dict[str, Any]:
    """Get single entity state using Gateway services."""
    correlation_id = generate_correlation_id()
    
    try:
        cache_key = f"ha_state_{entity_id}"
        
        if use_cache:
            cached = cache_get(cache_key)
            if cached:
                log_debug(f"[{correlation_id}] Using cached state for {entity_id}")
                increment_counter('ha_state_cache_hit')
                return cached
        
        result = call_ha_api(f'/api/states/{entity_id}')
        
        if result.get('success'):
            state_data = result.get('data', {})
            response = create_success_response('State retrieved', state_data)
            
            if use_cache:
                cache_set(cache_key, response, ttl=HA_CACHE_TTL_STATE)
            
            increment_counter('ha_state_retrieved')
            return response
        
        return result
        
    except Exception as e:
        log_error(f"[{correlation_id}] Get entity state failed: {str(e)}")
        return create_error_response(str(e), 'GET_STATE_FAILED')


# ===== SERVICE OPERATIONS =====

def call_service(domain: str, service: str, entity_id: Optional[str] = None,
                service_data: Optional[Dict] = None) -> Dict[str, Any]:
    """Call HA service using Gateway services."""
    correlation_id = generate_correlation_id()
    
    try:
        endpoint = f'/api/services/{domain}/{service}'
        
        data = service_data or {}
        if entity_id:
            data['entity_id'] = entity_id
        
        log_info(f"[{correlation_id}] Calling service: {domain}.{service}")
        
        result = call_ha_api(endpoint, method='POST', data=data)
        
        if result.get('success'):
            # Invalidate cache for affected entity
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


# ===== WRAPPER PATTERN =====

def ha_operation_wrapper(feature: str, operation: str, func: Callable,
                        config: Optional[Dict] = None, cache_key: Optional[str] = None,
                        cache_ttl: int = 300, **kwargs) -> Dict[str, Any]:
    """Generic wrapper for HA operations with circuit breaker and caching."""
    correlation_id = generate_correlation_id()
    
    try:
        log_debug(f"[{correlation_id}] HA operation: {feature}.{operation}")
        record_metric(f'ha_{feature}_{operation}_started', 1.0)
        
        # Check cache first
        if cache_key:
            cached = cache_get(cache_key)
            if cached:
                log_debug(f"[{correlation_id}] Using cached result")
                increment_counter(f'ha_{feature}_cache_hit')
                return cached
        
        # Get config
        ha_config = config or get_ha_config()
        
        # Execute through circuit breaker
        def _execute():
            return func(ha_config, **kwargs)
        
        result = execute_operation(
            GatewayInterface.CIRCUIT_BREAKER,
            'execute',
            breaker_name=HA_CIRCUIT_BREAKER_NAME,
            func=_execute
        )
        
        # Cache successful results
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


# ===== STATUS & DIAGNOSTICS =====

def check_ha_status() -> Dict[str, Any]:
    """Check HA connection status using Gateway services."""
    correlation_id = generate_correlation_id()
    
    try:
        log_debug(f"[{correlation_id}] Checking HA status")
        
        result = call_ha_api('/api/')
        
        if result.get('success'):
            return create_success_response('HA is available', {
                'available': True,
                'message': result.get('data', {}).get('message', 'Connected')
            })
        else:
            return create_error_response('HA unavailable', 'HA_UNAVAILABLE')
        
    except Exception as e:
        log_error(f"[{correlation_id}] Status check failed: {str(e)}")
        return create_error_response(str(e), 'STATUS_CHECK_FAILED')


def is_ha_available() -> bool:
    """Check if HA is available."""
    result = check_ha_status()
    return result.get('success', False)


def initialize_ha_system(config: Optional[Dict] = None) -> Dict[str, Any]:
    """Initialize HA system."""
    correlation_id = generate_correlation_id()
    
    try:
        log_info(f"[{correlation_id}] Initializing HA system")
        
        # Load config
        ha_config = config or get_ha_config()
        
        if not ha_config.get('enabled'):
            return create_error_response('HA not enabled', 'HA_DISABLED')
        
        # Check connection
        status = check_ha_status()
        
        if status.get('success'):
            increment_counter('ha_initialization_success')
            return create_success_response('HA system initialized', {
                'initialized': True,
                'timestamp': get_timestamp()
            })
        else:
            increment_counter('ha_initialization_failure')
            return status
        
    except Exception as e:
        log_error(f"[{correlation_id}] Initialization failed: {str(e)}")
        return create_error_response(str(e), 'INIT_FAILED')


def cleanup_ha_system() -> Dict[str, Any]:
    """Cleanup HA system resources."""
    correlation_id = generate_correlation_id()
    
    try:
        log_info(f"[{correlation_id}] Cleaning up HA system")
        
        # Clear HA-related cache
        cache_keys = ['ha_states_all', 'ha_automations', 'ha_scripts']
        for key in cache_keys:
            cache_delete(key)
        
        increment_counter('ha_cleanup_success')
        return create_success_response('HA system cleaned up', {
            'cleaned': True,
            'timestamp': get_timestamp()
        })
        
    except Exception as e:
        log_error(f"[{correlation_id}] Cleanup failed: {str(e)}")
        return create_error_response(str(e), 'CLEANUP_FAILED')


def get_diagnostic_info() -> Dict[str, Any]:
    """Get diagnostic information."""
    try:
        config = get_ha_config()
        status = check_ha_status()
        
        # Get circuit breaker state
        breaker_state = execute_operation(
            GatewayInterface.CIRCUIT_BREAKER,
            'get_state',
            breaker_name=HA_CIRCUIT_BREAKER_NAME
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


# ===== WEBSOCKET OPERATIONS =====

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
        
        # Fallback to getting all states
        log_debug("Using REST API for entity list")
        return get_states(use_cache=use_cache)
        
    except Exception as e:
        log_error(f"Entity registry fetch failed: {str(e)}")
        # Fallback to REST
        return get_states(use_cache=use_cache)


def filter_exposed_entities_wrapper(entities: Optional[List[Dict]] = None) -> Dict[str, Any]:
    """Filter entities to exposed ones with WebSocket support."""
    try:
        if entities is None:
            # Get entity registry
            registry_result = get_ha_entity_registry()
            if not registry_result.get('success'):
                return registry_result
            
            entities = registry_result.get('data', {}).get('entities', [])
            if not entities:
                entities = registry_result.get('data', {}).get('states', [])
        
        from ha_websocket import filter_exposed_entities
        exposed = filter_exposed_entities(entities)
        
        return create_success_response('Entities filtered', {
            'entities': exposed,
            'count': len(exposed),
            'total': len(entities)
        })
        
    except Exception as e:
        log_error(f"Entity filtering failed: {str(e)}")
        return create_error_response(str(e), 'FILTER_FAILED')


# ===== UTILITY FUNCTIONS =====

def fuzzy_match_name(query: str, names: List[str], threshold: int = 75) -> Optional[str]:
    """Fuzzy match name from list - uses simple matching."""
    query_lower = query.lower()
    
    # Exact match
    for name in names:
        if name.lower() == query_lower:
            return name
    
    # Contains match
    for name in names:
        if query_lower in name.lower() or name.lower() in query_lower:
            return name
    
    return None


# EOF
