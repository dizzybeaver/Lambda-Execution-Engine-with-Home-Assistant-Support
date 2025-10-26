"""
ha_core.py - Home Assistant Core Operations
Version: 2025.10.26.PHASE1
Description: PHASE 1 SECURITY IMPROVEMENTS - Circuit breaker, validation, sanitization, rate limiting

CHANGELOG:
- 2025.10.26.PHASE1: PHASE 1 SECURITY IMPROVEMENTS (CRITICAL)
  - ADDED: Circuit breaker protection for all HA API calls
  - ADDED: Input validation using gateway security functions
  - ADDED: Token sanitization in all debug logs
  - ADDED: Rate limiting for HA API calls (100 calls/minute)
  - ADDED: Entity ID format validation
  - ADDED: Endpoint path validation (prevent path traversal)
  - ADDED: Service name validation
  - Gateway functions used: execute_with_circuit_breaker, validate_string, 
    sanitize_for_log, validate_url, validate_cache_key
  - Related: DEC-16, AP-18, CVE-LOG-001, CVE-SUGA-2025-001
- 2025.10.19.22: REMOVED scattered sentinel validation (SUGA compliance)

Design Decision: Module-level ha_config import
Reason: Lazy import defeats the entire performance optimization strategy.
        ha_config imports config_param_store, which uses preloaded boto3 from lambda_preload.
        If we lazy load ha_config, we miss the optimization window and load during first request.
        
Design Decision: Gateway handles sentinels
Reason: SUGA principle - infrastructure concerns (sanitization) belong in gateway layer.

Copyright 2025 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

import os
import re
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime, timedelta

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
    # PHASE 1: Security functions
    execute_with_circuit_breaker,
    validate_string,
    validate_url,
    sanitize_for_log,
    validate_cache_key
)

# Cache TTL Constants
HA_CACHE_TTL_ENTITIES = 300
HA_CACHE_TTL_STATE = 60
HA_CACHE_TTL_CONFIG = 600
HA_CIRCUIT_BREAKER_NAME = "home_assistant"

# PHASE 1: Rate limiting constants
HA_RATE_LIMIT_WINDOW = 60  # seconds
HA_RATE_LIMIT_MAX_CALLS = 100  # calls per window
_RATE_LIMIT_CACHE_KEY = 'ha_api_rate_limit'

# DEBUG_MODE cached at module level (performance optimization)
_DEBUG_MODE_ENABLED = os.getenv('DEBUG_MODE', 'false').lower() == 'true'


def _is_debug_mode() -> bool:
    """Check if DEBUG_MODE is enabled (cached at module load)."""
    return _DEBUG_MODE_ENABLED


# ===== PHASE 1: INPUT VALIDATION =====

def _validate_entity_id(entity_id: str) -> None:
    """
    Validate entity_id format: domain.name
    
    Args:
        entity_id: Entity ID to validate
        
    Raises:
        ValueError: If entity_id format is invalid
        
    Related: CVE-SUGA-2025-001 (Input validation)
    """
    if not entity_id or not isinstance(entity_id, str):
        raise ValueError("Entity ID must be a non-empty string")
    
    # Entity IDs must match pattern: domain.name
    if not re.match(r'^[a-z_]+\.[a-z0-9_]+$', entity_id):
        raise ValueError(f"Invalid entity_id format: {entity_id}. Must be domain.name")
    
    if len(entity_id) > 255:
        raise ValueError(f"Entity ID too long: {len(entity_id)} chars (max 255)")


def _validate_endpoint(endpoint: str) -> None:
    """
    Validate API endpoint path (prevent path traversal).
    
    Args:
        endpoint: API endpoint path
        
    Raises:
        ValueError: If endpoint contains dangerous patterns
        
    Related: AP-18 (Security), CVE input validation
    """
    if not endpoint or not isinstance(endpoint, str):
        raise ValueError("Endpoint must be a non-empty string")
    
    # Must start with /api/
    if not endpoint.startswith('/api/'):
        raise ValueError(f"Endpoint must start with /api/: {endpoint}")
    
    # Check for path traversal attempts
    if '..' in endpoint or '//' in endpoint:
        raise ValueError(f"Invalid endpoint path: {endpoint}")
    
    # Check length
    if len(endpoint) > 500:
        raise ValueError(f"Endpoint too long: {len(endpoint)} chars")


def _validate_domain(domain: str) -> None:
    """
    Validate Home Assistant domain name.
    
    Args:
        domain: Domain name (e.g., 'light', 'switch')
        
    Raises:
        ValueError: If domain format is invalid
    """
    if not domain or not isinstance(domain, str):
        raise ValueError("Domain must be a non-empty string")
    
    # Domains are lowercase with underscores
    if not re.match(r'^[a-z][a-z0-9_]*$', domain):
        raise ValueError(f"Invalid domain format: {domain}")
    
    if len(domain) > 50:
        raise ValueError(f"Domain too long: {len(domain)} chars")


def _validate_service(service: str) -> None:
    """
    Validate Home Assistant service name.
    
    Args:
        service: Service name (e.g., 'turn_on', 'toggle')
        
    Raises:
        ValueError: If service format is invalid
    """
    if not service or not isinstance(service, str):
        raise ValueError("Service must be a non-empty string")
    
    # Services are lowercase with underscores
    if not re.match(r'^[a-z][a-z0-9_]*$', service):
        raise ValueError(f"Invalid service format: {service}")
    
    if len(service) > 50:
        raise ValueError(f"Service too long: {len(service)} chars")


# ===== PHASE 1: RATE LIMITING =====

def _check_rate_limit() -> bool:
    """
    Check if rate limit has been exceeded.
    
    Returns:
        True if within rate limit, False if exceeded
        
    Related: Phase 1 - Rate limiting implementation
    """
    try:
        # Get current rate limit data
        rate_data = cache_get(_RATE_LIMIT_CACHE_KEY)
        
        now = datetime.utcnow()
        
        if not rate_data or not isinstance(rate_data, dict):
            # Initialize rate limit tracking
            rate_data = {
                'window_start': now.isoformat(),
                'call_count': 1
            }
            cache_set(_RATE_LIMIT_CACHE_KEY, rate_data, ttl=HA_RATE_LIMIT_WINDOW)
            return True
        
        # Parse window start time
        window_start = datetime.fromisoformat(rate_data['window_start'])
        window_age = (now - window_start).total_seconds()
        
        # Reset window if expired
        if window_age >= HA_RATE_LIMIT_WINDOW:
            rate_data = {
                'window_start': now.isoformat(),
                'call_count': 1
            }
            cache_set(_RATE_LIMIT_CACHE_KEY, rate_data, ttl=HA_RATE_LIMIT_WINDOW)
            return True
        
        # Check call count
        call_count = rate_data.get('call_count', 0)
        
        if call_count >= HA_RATE_LIMIT_MAX_CALLS:
            # Rate limit exceeded
            log_warning(f"HA API rate limit exceeded: {call_count} calls in {window_age:.1f}s")
            increment_counter('ha_api_rate_limit_exceeded')
            return False
        
        # Increment call count
        rate_data['call_count'] = call_count + 1
        cache_set(_RATE_LIMIT_CACHE_KEY, rate_data, ttl=HA_RATE_LIMIT_WINDOW)
        
        return True
        
    except Exception as e:
        # On error, allow the call (fail open)
        log_error(f"Rate limit check failed: {e}")
        return True


def _extract_entity_list(data: Any, context: str = "states") -> List[Dict[str, Any]]:
    """
    Extract entity list from various response formats.
    
    HA /api/states returns different formats depending on how it's called.
    This function handles all common formats robustly.
    """
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
        
        log_debug(f"Dict format in {context} not recognized: {list(data.keys())[:5]}")
    
    log_warning(f"Could not extract entity list from {type(data).__name__} in {context}")
    return []


# ===== CONFIGURATION =====

def get_ha_config(force_reload: bool = False) -> Dict[str, Any]:
    """
    Get Home Assistant configuration with cache validation.
    
    PHASE 1: Added token sanitization in debug logs
    
    NOTE: Gateway (interface_cache.py) handles sentinel sanitization.
    """
    correlation_id = generate_correlation_id()
    
    if _is_debug_mode():
        log_info(f"[{correlation_id}] get_ha_config called (force_reload={force_reload})")
    
    cache_key = 'ha_config'
    
    if not force_reload:
        cached = cache_get(cache_key)
        if cached is not None:
            if isinstance(cached, dict) and 'enabled' in cached:
                log_debug(f"[{correlation_id}] Using cached HA config")
                return cached
            else:
                log_warning(f"[{correlation_id}] Cached config invalid, rebuilding")
                cache_delete(cache_key)
    
    log_debug(f"[{correlation_id}] Loading fresh HA config")
    config = load_ha_config()
    
    if not isinstance(config, dict):
        log_error(f"[{correlation_id}] Invalid HA config type: {type(config)}")
        return {
            'enabled': False,
            'error': 'Invalid config type'
        }
    
    cache_set(cache_key, config, ttl=HA_CACHE_TTL_CONFIG)
    
    # PHASE 1: Sanitized debug logging
    if _is_debug_mode():
        sanitized_config = sanitize_for_log(config)
        log_debug(f"[{correlation_id}] HA config loaded: {sanitized_config}")
    
    return config


# ===== API OPERATIONS =====

def call_ha_api(endpoint: str, method: str = 'GET', data: Optional[Dict] = None,
                config: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Call Home Assistant API endpoint with circuit breaker protection.
    
    PHASE 1 IMPROVEMENTS:
    - Circuit breaker protection (prevents cascade failures)
    - Input validation (endpoint, method)
    - Rate limiting (100 calls/minute)
    - Token sanitization in logs
    
    Args:
        endpoint: API endpoint (e.g., '/api/states')
        method: HTTP method (GET, POST, etc.)
        data: Request body data
        config: Optional HA config (will load if not provided)
        
    Returns:
        Response dict with success flag and data
        
    Related: DEC-16, Phase 1 improvements
    """
    correlation_id = generate_correlation_id()
    
    try:
        # PHASE 1: Validate endpoint format
        _validate_endpoint(endpoint)
        
        # PHASE 1: Check rate limit
        if not _check_rate_limit():
            return create_error_response(
                f'Rate limit exceeded: {HA_RATE_LIMIT_MAX_CALLS} calls per {HA_RATE_LIMIT_WINDOW}s',
                'RATE_LIMIT_EXCEEDED'
            )
        
        if not isinstance(method, str):
            method = 'GET'
        
        config = config or get_ha_config()
        
        if not isinstance(config, dict):
            return create_error_response('Invalid config', 'INVALID_CONFIG')
        
        if not config.get('enabled'):
            return create_error_response('HA not enabled', 'HA_DISABLED')
        
        base_url = config.get('base_url', '')
        token = config.get('access_token', '')
        
        if not base_url or not token:
            return create_error_response('Missing HA URL or token', 'INVALID_CONFIG')
        
        # PHASE 1: Validate base_url format
        try:
            validate_url(base_url)
        except ValueError as e:
            return create_error_response(f'Invalid base_url: {e}', 'INVALID_URL')
        
        url = f"{base_url}{endpoint}"
        headers = {
            'Authorization': f"Bearer {token}",
            'Content-Type': 'application/json'
        }
        
        # PHASE 1: Sanitized debug logging (no token exposure)
        if _is_debug_mode():
            safe_headers = sanitize_for_log(headers)
            log_debug(f"[{correlation_id}] HA API call: {method} {endpoint} (headers sanitized)")
        
        # PHASE 1: Wrap HTTP call in circuit breaker
        def _http_call():
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
            _http_call,
            args=()
        )
        
        if http_result.get('success'):
            increment_counter('ha_api_success')
        else:
            increment_counter('ha_api_failure')
        
        return http_result
        
    except ValueError as e:
        # Validation error
        log_error(f"[{correlation_id}] Validation error: {e}")
        return create_error_response(str(e), 'VALIDATION_ERROR')
    except Exception as e:
        log_error(f"[{correlation_id}] API call failed: {e}")
        increment_counter('ha_api_error')
        return create_error_response(str(e), 'API_CALL_FAILED')


def get_ha_states(entity_ids: Optional[List[str]] = None, 
                  use_cache: bool = True) -> Dict[str, Any]:
    """
    Get entity states using Gateway services.
    
    PHASE 1: Added entity_id validation
    """
    correlation_id = generate_correlation_id()
    
    try:
        # PHASE 1: Validate entity_ids if provided
        if entity_ids:
            if not isinstance(entity_ids, list):
                return create_error_response('entity_ids must be a list', 'INVALID_INPUT')
            
            for entity_id in entity_ids:
                try:
                    _validate_entity_id(entity_id)
                except ValueError as e:
                    return create_error_response(f'Invalid entity_id: {e}', 'INVALID_ENTITY_ID')
        
        cache_key = 'ha_all_states'
        
        if use_cache:
            cached = cache_get(cache_key)
            if cached and isinstance(cached, dict):
                log_debug(f"[{correlation_id}] Using cached states")
                increment_counter('ha_state_cache_hit')
                
                if entity_ids:
                    entity_set = set(entity_ids)
                    cached_data = _extract_entity_list(cached.get('data', []), 'cached_states')
                    filtered = [e for e in cached_data 
                               if isinstance(e, dict) and e.get('entity_id') in entity_set]
                    return create_success_response('States retrieved from cache', filtered)
                
                return cached
            elif cached:
                log_warning(f"[{correlation_id}] Cached data invalid, refreshing")
                cache_delete(cache_key)
        
        result = call_ha_api('/api/states')
        
        if not isinstance(result, dict):
            return create_error_response(
                f'API returned invalid type: {type(result).__name__}',
                'INVALID_API_RESPONSE'
            )
        
        if result.get('success'):
            raw_data = result.get('data', [])
            entity_list = _extract_entity_list(raw_data, 'api_states')
            
            log_info(f"[{correlation_id}] Retrieved {len(entity_list)} entities from HA")
            
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
        log_error(f"[{correlation_id}] Get states failed: {e}")
        return create_error_response(str(e), 'GET_STATES_FAILED')


def call_ha_service(domain: str, service: str, 
                   entity_id: Optional[str] = None,
                   service_data: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Call Home Assistant service.
    
    PHASE 1: Added input validation for domain, service, entity_id
    """
    correlation_id = generate_correlation_id()
    
    try:
        # PHASE 1: Validate inputs
        _validate_domain(domain)
        _validate_service(service)
        
        if entity_id:
            _validate_entity_id(entity_id)
        
        endpoint = f'/api/services/{domain}/{service}'
        
        data = service_data if isinstance(service_data, dict) else {}
        if entity_id:
            data['entity_id'] = entity_id
        
        log_info(f"[{correlation_id}] Calling service: {domain}.{service}")
        
        result = call_ha_api(endpoint, method='POST', data=data)
        
        if result.get('success'):
            if entity_id:
                # Invalidate cached state for this entity
                cache_key = f"ha_state_{entity_id}"
                try:
                    validate_cache_key(cache_key)
                    cache_delete(cache_key)
                except ValueError:
                    pass  # Invalid cache key, skip deletion
            
            increment_counter(f'ha_service_{domain}_{service}')
            return create_success_response('Service called', {
                'domain': domain,
                'service': service,
                'entity_id': entity_id
            })
        
        return result
        
    except ValueError as e:
        log_error(f"[{correlation_id}] Validation error: {e}")
        return create_error_response(str(e), 'VALIDATION_ERROR')
    except Exception as e:
        log_error(f"[{correlation_id}] Service call failed: {e}")
        return create_error_response(str(e), 'SERVICE_CALL_FAILED')


def check_ha_status() -> Dict[str, Any]:
    """Check HA connection status using Gateway services."""
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
        log_error(f"[{correlation_id}] Status check failed: {e}")
        return create_error_response(str(e), 'STATUS_CHECK_FAILED')


def get_diagnostic_info() -> Dict[str, Any]:
    """
    Get HA diagnostic information.
    
    PHASE 1: Added circuit breaker and rate limit info
    """
    from gateway import get_circuit_breaker_state
    
    diagnostic_info = {
        'ha_core_version': '2025.10.26.PHASE1',
        'cache_ttl_entities': HA_CACHE_TTL_ENTITIES,
        'cache_ttl_state': HA_CACHE_TTL_STATE,
        'circuit_breaker_name': HA_CIRCUIT_BREAKER_NAME,
        'debug_mode': _is_debug_mode(),
        'sentinel_sanitization': 'Handled by gateway (interface_cache.py)',
        # PHASE 1: New diagnostic fields
        'phase1_improvements': {
            'circuit_breaker_enabled': True,
            'input_validation_enabled': True,
            'rate_limiting_enabled': True,
            'rate_limit_window': HA_RATE_LIMIT_WINDOW,
            'rate_limit_max_calls': HA_RATE_LIMIT_MAX_CALLS,
            'token_sanitization': 'Enabled in all logs'
        }
    }
    
    # Add circuit breaker state
    try:
        cb_state = get_circuit_breaker_state(HA_CIRCUIT_BREAKER_NAME)
        diagnostic_info['circuit_breaker_state'] = cb_state
    except Exception:
        diagnostic_info['circuit_breaker_state'] = 'unavailable'
    
    # Add rate limit status
    try:
        rate_data = cache_get(_RATE_LIMIT_CACHE_KEY)
        if rate_data and isinstance(rate_data, dict):
            diagnostic_info['rate_limit_status'] = {
                'current_calls': rate_data.get('call_count', 0),
                'max_calls': HA_RATE_LIMIT_MAX_CALLS,
                'window_start': rate_data.get('window_start'),
                'within_limit': rate_data.get('call_count', 0) < HA_RATE_LIMIT_MAX_CALLS
            }
    except Exception:
        pass
    
    return diagnostic_info


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
        log_info(f"[{correlation_id}] HA operation: {feature}.{operation}")
        
        if not config:
            config = get_ha_config()
        
        if cache_key:
            # PHASE 1: Validate cache key format
            try:
                validate_cache_key(cache_key)
                cached = cache_get(cache_key)
                if cached:
                    log_debug(f"[{correlation_id}] Using cached result for {feature}.{operation}")
                    return cached
            except ValueError as e:
                log_warning(f"[{correlation_id}] Invalid cache key {cache_key}: {e}")
        
        result = func(config)
        
        log_info(f"[{correlation_id}] HA operation {feature}.{operation} completed")
        
        if result.get('success') and cache_key:
            try:
                validate_cache_key(cache_key)
                cache_set(cache_key, result, ttl=cache_ttl)
            except ValueError:
                pass  # Skip caching if key invalid
        
        if result.get('success'):
            record_metric(f'ha_{feature}_{operation}_success', 1.0)
        else:
            record_metric(f'ha_{feature}_{operation}_failure', 1.0)
        
        return result
        
    except Exception as e:
        log_error(f"[{correlation_id}] Operation wrapper failed: {e}")
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
