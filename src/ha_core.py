"""
ha_core.py - Home Assistant Core Operations
Version: 2025.10.26.PHASE3
Description: Core operations + Phase 3 optimizations

CHANGELOG:
- 2025.10.26.PHASE3: Code quality improvements
  * ADDED: Module-level DEBUG_MODE caching (eliminates repeated os.getenv calls)
  * ADDED: Fuzzy match result caching (300s TTL)
  * REMOVED: Excessive debug logging clutter (kept essential logs)
  * SIMPLIFIED: Correlation ID usage patterns
  * TOTAL REDUCTION: ~40 lines of debug logging removed, performance improved
- 2025.10.26.PHASE1: Security enhancements (circuit breaker, validation, rate limiting)
- 2025.10.19.22: REMOVED scattered sentinel validation (SUGA compliance)

Design Decision: Module-level ha_config import
Reason: Lazy import defeats performance optimization. ha_config imports config_param_store,
        which uses preloaded boto3 from lambda_preload.
        
Design Decision: Gateway handles sentinels
Reason: SUGA principle - infrastructure concerns (sanitization) belong in gateway layer.

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
    parse_json,
    # ADDED: Phase 1 security enhancements
    execute_with_circuit_breaker,
    validate_string, validate_url, sanitize_for_log
)

# Cache TTL Constants
HA_CACHE_TTL_ENTITIES = 300
HA_CACHE_TTL_STATE = 60
HA_CACHE_TTL_CONFIG = 600
HA_CACHE_TTL_FUZZY_MATCH = 300  # ADDED: Phase 3
HA_CIRCUIT_BREAKER_NAME = "home_assistant"

# ADDED: Phase 3 - Cache DEBUG_MODE at module level
_DEBUG_MODE_ENABLED = os.getenv('DEBUG_MODE', 'false').lower() == 'true'

# ADDED: Phase 1 - Rate limiting constants
HA_RATE_LIMIT_WINDOW = 60  # seconds
HA_RATE_LIMIT_MAX_CALLS = 100  # calls per window


def _is_debug_mode() -> bool:
    """Check if DEBUG_MODE is enabled (cached at module load)."""
    return _DEBUG_MODE_ENABLED


# ADDED: Phase 1 - Input validation functions
def _validate_entity_id(entity_id: str) -> None:
    """Validate entity_id format (domain.name)."""
    if not validate_string(entity_id, min_length=3, pattern=r'^[a-z_]+\.[a-z0-9_]+$'):
        raise ValueError(f"Invalid entity_id format: {entity_id}")


def _validate_endpoint(endpoint: str) -> None:
    """Validate API endpoint path."""
    if not endpoint.startswith('/'):
        raise ValueError("Endpoint must start with /")
    if '..' in endpoint or '~' in endpoint:
        raise ValueError("Invalid characters in endpoint")


def _validate_domain(domain: str) -> None:
    """Validate service domain."""
    if not validate_string(domain, min_length=2, pattern=r'^[a-z_]+$'):
        raise ValueError(f"Invalid domain: {domain}")


def _validate_service(service: str) -> None:
    """Validate service name."""
    if not validate_string(service, min_length=2, pattern=r'^[a-z_]+$'):
        raise ValueError(f"Invalid service: {service}")


# ADDED: Phase 1 - Rate limiting
def _check_rate_limit() -> bool:
    """Check if rate limit has been exceeded."""
    cache_key = 'ha_rate_limit'
    current_calls = cache_get(cache_key) or 0
    
    if isinstance(current_calls, int) and current_calls >= HA_RATE_LIMIT_MAX_CALLS:
        record_metric('ha_api_rate_limit_exceeded', 1.0)
        return False
    
    cache_set(cache_key, current_calls + 1, ttl=HA_RATE_LIMIT_WINDOW)
    return True


def _extract_entity_list(data: Any, context: str = "states") -> List[Dict[str, Any]]:
    """Extract entity list from various response formats."""
    if isinstance(data, list):
        return [item for item in data if isinstance(item, dict)]
    
    if isinstance(data, dict):
        if 'entity_id' in data:
            return [data]
        
        if 'data' in data and isinstance(data['data'], list):
            return [item for item in data['data'] if isinstance(item, dict)]
        
        keys_to_try = ['states', 'entities', 'items', 'results']
        for key in keys_to_try:
            if key in data and isinstance(data[key], list):
                return [item for item in data[key] if isinstance(item, dict)]
    
    return []


# ===== CONFIGURATION =====

def get_ha_config(force_reload: bool = False) -> Dict[str, Any]:
    """
    Get Home Assistant configuration.
    
    Gateway (interface_cache.py) handles sentinel sanitization.
    """
    correlation_id = generate_correlation_id()
    cache_key = 'ha_config'
    
    if not force_reload:
        cached = cache_get(cache_key)
        if cached is not None and isinstance(cached, dict) and 'enabled' in cached:
            log_debug(f"[{correlation_id}] Using cached HA config")
            return cached
        
        if cached is not None:
            log_warning(f"[{correlation_id}] Cached config invalid, rebuilding")
            cache_delete(cache_key)
    
    log_debug(f"[{correlation_id}] Loading fresh HA config")
    config = load_ha_config()
    
    if not isinstance(config, dict):
        log_error(f"[{correlation_id}] Invalid HA config type: {type(config)}")
        return {'enabled': False, 'error': 'Invalid config type'}
    
    cache_set(cache_key, config, ttl=HA_CACHE_TTL_CONFIG)
    return config


# ===== API OPERATIONS =====

def call_ha_api(endpoint: str, method: str = 'GET', data: Optional[Dict] = None,
                config: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Call Home Assistant API endpoint.
    
    ADDED Phase 1: Circuit breaker, input validation, rate limiting, token sanitization.
    
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
        # ADDED: Phase 1 - Input validation
        _validate_endpoint(endpoint)
        
        if not isinstance(method, str):
            method = 'GET'
        
        # ADDED: Phase 1 - Rate limiting
        if not _check_rate_limit():
            log_error(f"[{correlation_id}] Rate limit exceeded")
            return create_error_response('Rate limit exceeded', 'RATE_LIMIT_EXCEEDED')
        
        config = config or get_ha_config()
        
        if not isinstance(config, dict):
            return create_error_response('Invalid config', 'INVALID_CONFIG')
        
        if not config.get('enabled'):
            return create_error_response('HA not enabled', 'HA_DISABLED')
        
        base_url = config.get('base_url', '')
        token = config.get('access_token', '')
        
        if not base_url or not token:
            return create_error_response('Missing HA URL or token', 'INVALID_CONFIG')
        
        url = f"{base_url}{endpoint}"
        headers = {
            'Authorization': f"Bearer {token}",
            'Content-Type': 'application/json'
        }
        
        # ADDED: Phase 1 - Sanitize headers for logging
        if _is_debug_mode():
            sanitized_headers = sanitize_for_log(headers)
            log_debug(f"[{correlation_id}] Request to {url}, headers: {sanitized_headers}")
        
        # ADDED: Phase 1 - Wrap in circuit breaker
        def _make_request():
            return execute_operation(
                GatewayInterface.HTTP_CLIENT,
                method.lower(),
                url=url,
                headers=headers,
                json=data,
                timeout=config.get('timeout', 30)
            )
        
        http_result = execute_with_circuit_breaker(
            HA_CIRCUIT_BREAKER_NAME,
            _make_request
        )
        
        if http_result.get('success'):
            increment_counter('ha_api_success')
        else:
            increment_counter('ha_api_failure')
        
        return http_result
        
    except ValueError as e:
        # Validation errors
        log_error(f"[{correlation_id}] Validation error: {str(e)}")
        increment_counter('ha_api_validation_error')
        return create_error_response(str(e), 'VALIDATION_ERROR')
        
    except Exception as e:
        log_error(f"[{correlation_id}] API call failed: {str(e)}")
        increment_counter('ha_api_error')
        return create_error_response(str(e), 'API_CALL_FAILED')


def get_ha_states(entity_ids: Optional[List[str]] = None, 
                  use_cache: bool = True) -> Dict[str, Any]:
    """Get entity states."""
    correlation_id = generate_correlation_id()
    
    try:
        # ADDED: Phase 1 - Validate entity_ids if provided
        if entity_ids:
            for entity_id in entity_ids:
                _validate_entity_id(entity_id)
        
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
                log_warning(f"[{correlation_id}] Cached data invalid - invalidating")
                cache_delete(cache_key)
        
        result = call_ha_api('/api/states')
        
        if not isinstance(result, dict):
            return create_error_response(f'API returned invalid type: {type(result).__name__}', 
                                        'INVALID_API_RESPONSE')
        
        if result.get('success'):
            raw_data = result.get('data', [])
            entity_list = _extract_entity_list(raw_data, 'api_states')
            
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
        
        return result
        
    except ValueError as e:
        # Validation errors
        log_error(f"[{correlation_id}] Entity validation error: {str(e)}")
        return create_error_response(str(e), 'VALIDATION_ERROR')
        
    except Exception as e:
        log_error(f"[{correlation_id}] Get states failed: {str(e)}")
        return create_error_response(str(e), 'GET_STATES_FAILED')


def call_ha_service(domain: str, service: str, 
                   entity_id: Optional[str] = None,
                   service_data: Optional[Dict] = None) -> Dict[str, Any]:
    """Call Home Assistant service."""
    correlation_id = generate_correlation_id()
    
    try:
        # ADDED: Phase 1 - Input validation
        _validate_domain(domain)
        _validate_service(service)
        
        if entity_id:
            _validate_entity_id(entity_id)
        
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
        
    except ValueError as e:
        # Validation errors
        log_error(f"[{correlation_id}] Service validation error: {str(e)}")
        return create_error_response(str(e), 'VALIDATION_ERROR')
        
    except Exception as e:
        log_error(f"[{correlation_id}] Service call failed: {str(e)}")
        return create_error_response(str(e), 'SERVICE_CALL_FAILED')


def check_ha_status() -> Dict[str, Any]:
    """Check HA connection status."""
    correlation_id = generate_correlation_id()
    
    try:
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
    # ADDED: Phase 1 - Include circuit breaker and rate limit status
    from gateway import get_circuit_breaker_state
    
    circuit_state = get_circuit_breaker_state(HA_CIRCUIT_BREAKER_NAME)
    rate_limit_calls = cache_get('ha_rate_limit') or 0
    
    return {
        'ha_core_version': '2025.10.26.PHASE3',
        'cache_ttl_entities': HA_CACHE_TTL_ENTITIES,
        'cache_ttl_state': HA_CACHE_TTL_STATE,
        'circuit_breaker': {
            'name': HA_CIRCUIT_BREAKER_NAME,
            'state': circuit_state.get('state', 'unknown'),
            'failure_count': circuit_state.get('failure_count', 0)
        },
        'rate_limit': {
            'max_calls': HA_RATE_LIMIT_MAX_CALLS,
            'window_seconds': HA_RATE_LIMIT_WINDOW,
            'current_calls': rate_limit_calls
        },
        'debug_mode': _is_debug_mode(),
        'sentinel_sanitization': 'Handled by gateway (interface_cache.py)'
    }


def fuzzy_match_name(search_name: str, names: List[str], threshold: float = 0.6) -> Optional[str]:
    """
    Fuzzy match a name against a list.
    
    ADDED Phase 3: Result caching for performance.
    """
    from difflib import SequenceMatcher
    
    # ADDED: Phase 3 - Cache fuzzy match results
    cache_key = f"fuzzy_match_{hash(search_name)}_{hash(tuple(sorted(names)))}"
    
    cached_result = cache_get(cache_key)
    if cached_result is not None:
        return cached_result
    
    search_lower = search_name.lower()
    best_match = None
    best_ratio = threshold
    
    for name in names:
        ratio = SequenceMatcher(None, search_lower, name.lower()).ratio()
        if ratio > best_ratio:
            best_ratio = ratio
            best_match = name
    
    # Cache the result
    cache_set(cache_key, best_match, ttl=HA_CACHE_TTL_FUZZY_MATCH)
    
    return best_match


def ha_operation_wrapper(feature: str, operation: str, func: Callable,
                         cache_key: Optional[str] = None,
                         cache_ttl: int = HA_CACHE_TTL_ENTITIES,
                         config: Optional[Dict] = None) -> Dict[str, Any]:
    """Generic operation wrapper for HA features."""
    correlation_id = generate_correlation_id()
    
    try:
        # ADDED: Phase 1 - Validate cache key format
        if cache_key and not validate_string(cache_key, pattern=r'^[a-zA-Z0-9_:]+$'):
            log_warning(f"[{correlation_id}] Invalid cache key format: {cache_key}")
            cache_key = None
        
        log_info(f"[{correlation_id}] HA operation: {feature}.{operation}")
        
        if not config:
            config = get_ha_config()
        
        if cache_key:
            cached = cache_get(cache_key)
            if cached:
                log_debug(f"[{correlation_id}] Using cached result for {feature}.{operation}")
                return cached
        
        result = func(config)
        
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
