"""
ha_common.py
Version: 2025.10.22.02
Description: Home Assistant common utilities

CHANGELOG:
- 2025.10.22.02: CRITICAL FIX - Corrected gateway import names
  - Fixed: make_request → http_request
  - Fixed: make_get_request → http_get
  - Fixed: make_post_request → http_post
  - Resolves ImportError on deployment
- 2025.10.19.04: ARCHITECTURE FIX - Removed duplicate get_ha_config()

Copyright 2025 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

import time
from typing import Dict, Any, Optional, List
from difflib import SequenceMatcher

HA_CONSOLIDATED_CACHE_KEY = "ha_consolidated_cache"
HA_CACHE_VERSION = "2.0"
HA_CIRCUIT_BREAKER_NAME = "home_assistant"

HA_CACHE_TTL_STATE = 60
HA_CACHE_TTL_ENTITIES = 300
HA_CACHE_TTL_MAPPINGS = 600


def get_consolidated_cache() -> Dict[str, Any]:
    """Get consolidated Home Assistant cache."""
    from gateway import cache_get
    
    cached = cache_get(HA_CONSOLIDATED_CACHE_KEY)
    if cached and isinstance(cached, dict) and cached.get("version") == HA_CACHE_VERSION:
        return cached
    
    return {
        "version": HA_CACHE_VERSION,
        "config": None,
        "entity_states": {},
        "timestamp": time.time()
    }


def set_consolidated_cache(cache_data: Dict[str, Any], ttl: int = 600):
    """Update consolidated Home Assistant cache."""
    from gateway import cache_set
    
    cache_data["version"] = HA_CACHE_VERSION
    cache_data["timestamp"] = time.time()
    cache_set(HA_CONSOLIDATED_CACHE_KEY, cache_data, ttl=ttl)


def get_cache_section(section: str, ttl: int = 300) -> Optional[Any]:
    """Get specific section from consolidated cache with TTL check."""
    cache_data = get_consolidated_cache()
    section_data = cache_data.get(section, {})
    
    if isinstance(section_data, dict) and "timestamp" in section_data:
        if time.time() - section_data["timestamp"] < ttl:
            return section_data.get("data")
    
    return None


def set_cache_section(section: str, data: Any, ttl: int = 300):
    """Update specific section in consolidated cache."""
    cache_data = get_consolidated_cache()
    cache_data[section] = {
        "data": data,
        "timestamp": time.time()
    }
    set_consolidated_cache(cache_data, ttl)


def invalidate_cache_section(section: str):
    """Invalidate specific cache section."""
    cache_data = get_consolidated_cache()
    if section in cache_data:
        del cache_data[section]
        set_consolidated_cache(cache_data)


def get_ha_config() -> Dict[str, Any]:
    """
    Get Home Assistant configuration - delegates to ha_config.py.
    
    ARCHITECTURE NOTE (2025.10.19.04):
    This function now delegates to ha_config.load_ha_config() to ensure
    single source of truth for HA configuration.
    
    Returns:
        Dict containing:
        - base_url: Home Assistant URL
        - access_token: Long-lived access token
        - timeout: Request timeout
        - verify_ssl: SSL verification flag
    """
    from ha_config import load_ha_config
    return load_ha_config()


def call_ha_api(
    endpoint: str,
    ha_config: Optional[Dict[str, Any]] = None,
    method: str = 'GET',
    data: Optional[Dict] = None
) -> Dict[str, Any]:
    """Call Home Assistant API with circuit breaker protection."""
    from gateway import http_request, http_get, http_post, execute_with_circuit_breaker
    from shared_utilities import (
        create_operation_context, close_operation_context, 
        handle_operation_error, cache_operation_result
    )
    
    context = create_operation_context('ha_common', 'api_call', endpoint=endpoint, method=method)
    
    try:
        config = ha_config or get_ha_config()
        url = f"{config['base_url']}{endpoint}"
        
        headers = {
            "Authorization": f"Bearer {config['access_token']}",
            "Content-Type": "application/json"
        }
        
        def _make_ha_request():
            if method.upper() == 'GET':
                return http_get(url=url, headers=headers, timeout=config.get('timeout', 30))
            elif method.upper() == 'POST':
                return http_post(url=url, json=data or {}, headers=headers, timeout=config.get('timeout', 30))
            else:
                return http_request(method, url=url, headers=headers, json=data, timeout=config.get('timeout', 30))
        
        result = execute_with_circuit_breaker(HA_CIRCUIT_BREAKER_NAME, _make_ha_request)
        
        close_operation_context(context, success=result.get('success', False), result=result)
        return result
        
    except Exception as e:
        close_operation_context(context, success=False)
        return handle_operation_error('ha_common', 'api_call', e, context['correlation_id'])


def batch_get_states(
    entity_ids: Optional[List[str]] = None,
    ha_config: Optional[Dict[str, Any]] = None,
    use_cache: bool = True,
    cache_ttl: int = HA_CACHE_TTL_STATE
) -> Dict[str, Any]:
    """Batch retrieve entity states with circuit breaker."""
    from shared_utilities import (
        create_operation_context, close_operation_context, 
        handle_operation_error, cache_operation_result
    )
    
    context = create_operation_context('ha_common', 'batch_get_states', 
                                      count=len(entity_ids) if entity_ids else 'all')
    
    try:
        if use_cache:
            result = cache_operation_result(
                operation_name="batch_get_states",
                func=lambda: call_ha_api("/api/states", ha_config),
                ttl=cache_ttl,
                cache_key_prefix="ha_batch_states"
            )
        else:
            result = call_ha_api("/api/states", ha_config)
        
        if not result.get('success'):
            close_operation_context(context, success=False)
            return result
        
        all_states = result.get('data', [])
        
        if entity_ids:
            entity_set = set(entity_ids)
            filtered_states = [
                state for state in all_states 
                if state.get('entity_id') in entity_set
            ]
            result['data'] = filtered_states
        
        close_operation_context(context, success=True, result=result)
        return result
        
    except Exception as e:
        close_operation_context(context, success=False)
        return handle_operation_error('ha_common', 'batch_get_states', e, context['correlation_id'])


def call_ha_service(
    domain: str,
    service: str,
    ha_config: Optional[Dict[str, Any]] = None,
    entity_id: Optional[str] = None,
    service_data: Optional[Dict] = None
) -> Dict[str, Any]:
    """Call Home Assistant service with circuit breaker."""
    from shared_utilities import create_operation_context, close_operation_context, handle_operation_error
    
    context = create_operation_context('ha_common', 'call_service', 
                                      domain=domain, service=service, entity_id=entity_id)
    
    try:
        endpoint = f"/api/services/{domain}/{service}"
        
        data = service_data or {}
        if entity_id:
            data['entity_id'] = entity_id
        
        result = call_ha_api(endpoint, ha_config, method='POST', data=data)
        
        if result.get('success'):
            if entity_id:
                cache_data = get_consolidated_cache()
                if entity_id in cache_data.get("entity_states", {}):
                    del cache_data["entity_states"][entity_id]
                    set_consolidated_cache(cache_data)
        
        close_operation_context(context, success=result.get('success', False), result=result)
        return result
        
    except Exception as e:
        close_operation_context(context, success=False)
        return handle_operation_error('ha_common', 'call_service', e, context['correlation_id'])


def batch_call_service(
    operations: List[Dict[str, Any]],
    ha_config: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """Batch call multiple services with circuit breaker."""
    from shared_utilities import create_operation_context, close_operation_context, handle_operation_error
    
    context = create_operation_context('ha_common', 'batch_call_service', count=len(operations))
    
    try:
        results = []
        
        for op in operations:
            result = call_ha_service(
                domain=op.get('domain'),
                service=op.get('service'),
                ha_config=ha_config,
                entity_id=op.get('entity_id'),
                service_data=op.get('service_data')
            )
            results.append(result)
        
        close_operation_context(context, success=True)
        return results
        
    except Exception as e:
        close_operation_context(context, success=False)
        return [handle_operation_error('ha_common', 'batch_call_service', e, context['correlation_id'])]


def get_entity_state(
    entity_id: str,
    ha_config: Optional[Dict[str, Any]] = None,
    use_cache: bool = True
) -> Dict[str, Any]:
    """Get entity state with circuit breaker and caching."""
    from shared_utilities import cache_operation_result
    
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


def is_ha_available(ha_config: Optional[Dict[str, Any]] = None) -> bool:
    """Check if Home Assistant is available using circuit breaker."""
    from shared_utilities import create_operation_context, close_operation_context
    
    context = create_operation_context('ha_common', 'availability_check')
    
    try:
        result = call_ha_api("/api/", ha_config)
        is_available = result.get('success', False) and result.get('status_code') == 200
        
        close_operation_context(context, success=is_available)
        return is_available
        
    except Exception:
        close_operation_context(context, success=False)
        return False


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


__all__ = [
    'HA_CONSOLIDATED_CACHE_KEY',
    'HA_CACHE_VERSION',
    'HA_CIRCUIT_BREAKER_NAME',
    'HA_CACHE_TTL_STATE',
    'HA_CACHE_TTL_ENTITIES',
    'HA_CACHE_TTL_MAPPINGS',
    'get_consolidated_cache',
    'set_consolidated_cache',
    'get_cache_section',
    'set_cache_section',
    'invalidate_cache_section',
    'get_ha_config',
    'call_ha_api',
    'batch_get_states',
    'call_ha_service',
    'batch_call_service',
    'get_entity_state',
    'is_ha_available',
    'fuzzy_match_name',
    'minimize_entity',
    'minimize_entity_list',
]

# EOF
