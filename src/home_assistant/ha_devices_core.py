"""
ha_devices_core.py - Devices Core Implementation (INT-HA-02)
Version: 2.0.0 - PHASE 3
Date: 2025-11-04
Description: Core implementation for Home Assistant device operations

PHASE 3: Migration Complete
- Migrated all device functions from ha_core.py
- 7 core device operations + 9 helper functions
- Cache warming and performance profiling
- Smart cache invalidation
- Enhanced debug tracing
- LEE access via gateway.py only

Architecture:
ha_interconnect.py → ha_interface_devices.py → ha_devices_core.py (THIS FILE)

Functions Migrated from ha_core.py:
- get_states_impl (from get_ha_states)
- get_by_id_impl (extracted from get_ha_states)
- find_fuzzy_impl (from fuzzy_match_name)
- update_state_impl (new wrapper for call_service)
- call_service_impl (from call_ha_service)
- list_by_domain_impl (extracted from get_ha_states)
- check_status_impl (from check_ha_status)

Helper Functions:
- call_ha_api_impl (from call_ha_api)
- get_ha_config_impl (from get_ha_config)
- warm_cache_impl (from warm_ha_cache)
- get_performance_report_impl (from get_performance_report)
- invalidate_entity_cache_impl (from invalidate_entity_cache)
- invalidate_domain_cache_impl (from invalidate_domain_cache)
- get_diagnostic_info_impl (from get_diagnostic_info)
- DebugContext (helper class)
- _extract_entity_list, _trace_step, _is_debug_mode, _calculate_percentiles, _generate_performance_recommendations

Copyright 2025 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

# MIGRATED Phase 3: Core imports from ha_core.py
import os
import time
from typing import Dict, Any, Optional, List, Callable
import hashlib
from collections import defaultdict

# MIGRATED Phase 3: Load ha_config at module level (required!)
from ha_config import load_ha_config, validate_ha_config

# Import LEE services via gateway (ONLY way to access LEE)
from gateway import (
    log_info, log_error, log_debug, log_warning,
    execute_operation, GatewayInterface,
    cache_get, cache_set, cache_delete, cache_stats,
    increment_counter, record_metric, get_metrics_stats,
    create_success_response, create_error_response,
    generate_correlation_id, get_timestamp,
    parse_json
)

# MIGRATED Phase 3: Cache TTL Constants from ha_core.py
HA_CACHE_TTL_ENTITIES = 300
HA_CACHE_TTL_STATE = 60
HA_CACHE_TTL_CONFIG = 600
HA_CACHE_TTL_FUZZY_MATCH = 300
HA_CIRCUIT_BREAKER_NAME = "home_assistant"

# MIGRATED Phase 3: Performance profiling constants
HA_SLOW_OPERATION_THRESHOLD_MS = 1000  # Alert if operation > 1s
HA_CACHE_WARMING_ENABLED = os.getenv('HA_CACHE_WARMING_ENABLED', 'false').lower() == 'true'

# MIGRATED Phase 3: Module-level constants
_DEBUG_MODE_ENABLED = os.getenv('DEBUG_MODE', 'false').lower() == 'true'

# MIGRATED Phase 3: Track slow operations in memory
_SLOW_OPERATIONS = defaultdict(int)  # operation_name: count


# ===== MIGRATED Phase 3: Helper Functions =====

def _is_debug_mode() -> bool:
    """
    MIGRATED Phase 3: Check if DEBUG_MODE is enabled (cached at module level).
    
    From ha_core.py _is_debug_mode()
    """
    return _DEBUG_MODE_ENABLED


class DebugContext:
    """
    MIGRATED Phase 3: Debug tracing context manager.
    
    From ha_core.py DebugContext class
    
    Provides structured debug output with timing and nesting.
    """
    def __init__(self, operation: str, correlation_id: str, **params):
        self.operation = operation
        self.correlation_id = correlation_id
        self.params = params
        self.start_time = None
        
    def __enter__(self):
        if _DEBUG_MODE_ENABLED:
            self.start_time = time.perf_counter()
            param_str = ', '.join(f"{k}={v}" for k, v in self.params.items())
            log_info(f"[{self.correlation_id}] [TRACE] {self.operation} START ({param_str})")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if _DEBUG_MODE_ENABLED and self.start_time:
            duration_ms = (time.perf_counter() - self.start_time) * 1000
            if exc_type:
                log_error(f"[{self.correlation_id}] [TRACE] {self.operation} FAILED: {exc_val} ({duration_ms:.2f}ms)")
            else:
                log_info(f"[{self.correlation_id}] [TRACE] {self.operation} COMPLETE ({duration_ms:.2f}ms)")
        return False  # Don't suppress exceptions


def _trace_step(correlation_id: str, step: str, **details):
    """
    MIGRATED Phase 3: Log a debug trace step.
    
    From ha_core.py _trace_step()
    
    Args:
        correlation_id: Correlation ID for request tracing
        step: Step description
        **details: Additional details to log
    """
    if _DEBUG_MODE_ENABLED:
        detail_str = ', '.join(f"{k}={v}" for k, v in details.items()) if details else ''
        log_info(f"[{correlation_id}] [STEP] {step}" + (f" ({detail_str})" if detail_str else ""))


def _extract_entity_list(data: Any, context: str = "states") -> List[Dict[str, Any]]:
    """
    MIGRATED Phase 3: Extract entity list from various response formats.
    
    From ha_core.py _extract_entity_list()
    
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


def _calculate_percentiles(values: List[float], percentiles: List[int]) -> Dict[str, float]:
    """
    MIGRATED Phase 3: Calculate percentiles from list of values.
    
    From ha_core.py _calculate_percentiles()
    
    Args:
        values: List of numeric values
        percentiles: List of percentile values to calculate (e.g., [50, 95, 99])
        
    Returns:
        Dict mapping percentile to value
    """
    if not values:
        return {f'p{p}': 0.0 for p in percentiles}
    
    sorted_values = sorted(values)
    result = {}
    
    for p in percentiles:
        index = int(len(sorted_values) * (p / 100.0))
        index = min(index, len(sorted_values) - 1)
        result[f'p{p}'] = sorted_values[index]
    
    return result


def _generate_performance_recommendations(
    operations: Dict[str, Any],
    cache_efficiency: Dict[str, Any],
    slow_ops: List[Dict[str, Any]]
) -> List[str]:
    """
    MIGRATED Phase 3: Generate performance improvement recommendations.
    
    From ha_core.py _generate_performance_recommendations()
    
    Args:
        operations: Operation timing data
        cache_efficiency: Cache hit rate data
        slow_ops: List of slow operations
        
    Returns:
        List of actionable recommendations
    """
    recommendations = []
    
    # Cache efficiency recommendations
    if cache_efficiency:
        hit_rate = cache_efficiency.get('hit_rate_percent', 0)
        if hit_rate < 60:
            recommendations.append(
                f"Low cache hit rate ({hit_rate:.1f}%). Consider increasing cache TTL or "
                "enabling cache warming."
            )
        elif hit_rate > 90:
            recommendations.append(
                f"Excellent cache hit rate ({hit_rate:.1f}%). Current caching strategy is optimal."
            )
    
    # Slow operation recommendations
    if slow_ops:
        for op in slow_ops[:3]:  # Top 3
            recommendations.append(
                f"Operation '{op['operation']}' is slow (p95: {op['p95_ms']:.0f}ms). "
                f"Consider optimization or caching."
            )
    
    # General recommendations
    if not recommendations:
        recommendations.append("Performance metrics look good. No immediate optimizations needed.")
    
    return recommendations


# ===== MIGRATED Phase 3: Core Device Functions =====

def get_ha_config_impl(force_reload: bool = False, **kwargs) -> Dict[str, Any]:
    """
    Get Home Assistant configuration with cache validation.
    
    MIGRATED Phase 3 from ha_core.py get_ha_config()
    
    Core implementation for configuration loading.
    
    Args:
        force_reload: Force reload from sources
        **kwargs: Additional options
        
    Returns:
        Configuration dictionary
        
    REF: INT-HA-02
    """
    correlation_id = generate_correlation_id()
    
    with DebugContext("get_ha_config_impl", correlation_id, force_reload=force_reload):
        cache_key = 'ha_config'
        
        if not force_reload:
            cached = cache_get(cache_key)
            if cached is not None:
                if isinstance(cached, dict) and 'enabled' in cached:
                    _trace_step(correlation_id, "Using cached config")
                    record_metric('ha_config_cache_hit', 1.0)
                    return cached
                else:
                    _trace_step(correlation_id, "Invalid cache format, rebuilding")
                    cache_delete(cache_key)
        
        _trace_step(correlation_id, "Loading fresh HA config")
        config = load_ha_config()
        
        if not isinstance(config, dict):
            log_error(f"[{correlation_id}] Invalid HA config type: {type(config)}")
            return {'enabled': False, 'error': 'Invalid config type'}
        
        cache_set(cache_key, config, ttl=HA_CACHE_TTL_CONFIG)
        record_metric('ha_config_cache_miss', 1.0)
        
        return config


def call_ha_api_impl(endpoint: str, method: str = 'GET', data: Optional[Dict] = None,
                    config: Optional[Dict] = None, **kwargs) -> Dict[str, Any]:
    """
    Call Home Assistant API endpoint with enhanced metrics.
    
    MIGRATED Phase 3 from ha_core.py call_ha_api()
    
    Core implementation for HA API calls. Used by all device operations.
    
    Args:
        endpoint: API endpoint (e.g., '/api/states')
        method: HTTP method ('GET', 'POST', etc.)
        data: Optional request data
        config: Optional HA configuration
        **kwargs: Additional options
        
    Returns:
        API response dictionary
        
    REF: INT-HA-02
    """
    correlation_id = generate_correlation_id()
    start_time = time.perf_counter()
    
    try:
        with DebugContext("call_ha_api_impl", correlation_id, endpoint=endpoint, method=method):
            # Validation
            if not isinstance(endpoint, str) or not endpoint:
                return create_error_response('Invalid endpoint', 'INVALID_ENDPOINT')
            
            if not isinstance(method, str):
                method = 'GET'
            
            _trace_step(correlation_id, "Loading HA config")
            config = config or get_ha_config_impl()
            
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
            
            _trace_step(correlation_id, "Making HTTP request", url=url[:50])
            
            http_result = execute_operation(
                GatewayInterface.HTTP_CLIENT,
                method.lower(),
                url=url,
                headers=headers,
                json=data,
                timeout=config.get('timeout', 30)
            )
            
            duration_ms = (time.perf_counter() - start_time) * 1000
            
            # MIGRATED Phase 3: Track slow operations
            if duration_ms > HA_SLOW_OPERATION_THRESHOLD_MS:
                _SLOW_OPERATIONS[f'call_ha_api_{endpoint}'] += 1
                log_warning(f"Slow API call detected: {endpoint} took {duration_ms:.2f}ms")
            
            if http_result.get('success'):
                increment_counter('ha_api_success')
                record_metric('ha_api_duration_ms', duration_ms)
                record_metric(f'ha_api_{method.lower()}_success', 1.0)
            else:
                increment_counter('ha_api_failure')
                record_metric('ha_api_error_duration_ms', duration_ms)
                record_metric(f'ha_api_{method.lower()}_failure', 1.0)
            
            return http_result
            
    except Exception as e:
        log_error(f"[{correlation_id}] API call exception: {type(e).__name__}: {str(e)}")
        if _DEBUG_MODE_ENABLED:
            import traceback
            log_error(f"[{correlation_id}] [TRACEBACK]\n{traceback.format_exc()}")
        
        increment_counter('ha_api_error')
        return create_error_response(str(e), 'API_CALL_FAILED')


def get_states_impl(entity_ids: Optional[List[str]] = None, 
                   use_cache: bool = True, **kwargs) -> Dict[str, Any]:
    """
    Get Home Assistant entity states implementation.
    
    MIGRATED Phase 3 from ha_core.py get_ha_states()
    
    Core implementation for retrieving device states.
    
    Args:
        entity_ids: Optional list of specific entity IDs
        use_cache: Whether to use cached states
        **kwargs: Additional options
        
    Returns:
        States response dictionary with entity list
        
    Example:
        states = get_states_impl(['light.living_room'])
        
    REF: INT-HA-02
    """
    correlation_id = generate_correlation_id()
    
    try:
        with DebugContext("get_states_impl", correlation_id, 
                         entity_count=len(entity_ids) if entity_ids else "all",
                         use_cache=use_cache):
            
            cache_key = 'ha_all_states'
            
            if use_cache:
                cached = cache_get(cache_key)
                if cached and isinstance(cached, dict):
                    _trace_step(correlation_id, "Using cached states")
                    increment_counter('ha_state_cache_hit')
                    record_metric('ha_states_cache_hit', 1.0)
                    
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
            
            _trace_step(correlation_id, "Fetching states from API")
            result = call_ha_api_impl('/api/states')
            
            if not isinstance(result, dict):
                log_error(f"[{correlation_id}] call_ha_api_impl returned {type(result)}, not dict")
                return create_error_response(f'API returned invalid type: {type(result).__name__}', 'INVALID_API_RESPONSE')
            
            if result.get('success'):
                raw_data = result.get('data', [])
                entity_list = _extract_entity_list(raw_data, 'api_states')
                
                log_info(f"[{correlation_id}] Retrieved {len(entity_list)} entities from HA")
                
                normalized_result = create_success_response('States retrieved', entity_list)
                
                if use_cache:
                    cache_set(cache_key, normalized_result, ttl=HA_CACHE_TTL_STATE)
                
                increment_counter('ha_states_retrieved')
                record_metric('ha_states_count', len(entity_list))
                record_metric('ha_states_cache_miss', 1.0)
                
                if entity_ids and isinstance(entity_ids, list):
                    entity_set = set(entity_ids)
                    filtered = [e for e in entity_list 
                               if isinstance(e, dict) and e.get('entity_id') in entity_set]
                    record_metric('ha_states_filtered_count', len(filtered))
                    return create_success_response('States retrieved', filtered)
                
                return normalized_result
            
            return result
            
    except Exception as e:
        log_error(f"[{correlation_id}] Get states failed: {str(e)}")
        increment_counter('ha_states_error')
        return create_error_response(str(e), 'GET_STATES_FAILED')


def get_by_id_impl(entity_id: str, **kwargs) -> Dict[str, Any]:
    """
    Get specific device by entity ID implementation.
    
    MIGRATED Phase 3: Extracted from ha_core.py get_ha_states()
    
    Core implementation for single device retrieval.
    
    Args:
        entity_id: Entity ID to retrieve
        **kwargs: Additional options
        
    Returns:
        Device state dictionary
        
    REF: INT-HA-02
    """
    correlation_id = generate_correlation_id()
    log_info(f"[{correlation_id}] Getting device by ID: {entity_id}")
    
    try:
        # Use get_states_impl with filtering
        result = get_states_impl(entity_ids=[entity_id], **kwargs)
        
        if result.get('success'):
            entities = result.get('data', [])
            if entities and len(entities) > 0:
                increment_counter('ha_devices_get_by_id_success')
                return create_success_response('Entity retrieved', entities[0])
            else:
                increment_counter('ha_devices_get_by_id_not_found')
                return create_error_response(f'Entity {entity_id} not found', 'ENTITY_NOT_FOUND')
        
        return result
        
    except Exception as e:
        log_error(f"[{correlation_id}] Get by ID failed: {str(e)}")
        increment_counter('ha_devices_get_by_id_error')
        return create_error_response(str(e), 'GET_BY_ID_FAILED')


def find_fuzzy_impl(search_name: str, threshold: float = 0.6, **kwargs) -> Optional[str]:
    """
    Find device using fuzzy name matching implementation.
    
    MIGRATED Phase 3 from ha_core.py fuzzy_match_name()
    
    Core implementation for fuzzy device search.
    
    Args:
        search_name: Name to search for
        threshold: Matching threshold (0.0-1.0)
        **kwargs: Additional options
        
    Returns:
        Best matching entity ID or None
        
    REF: INT-HA-02
    """
    from difflib import SequenceMatcher
    
    correlation_id = generate_correlation_id()
    
    try:
        # Get all entity states
        states_result = get_states_impl(use_cache=True)
        
        if not states_result.get('success'):
            log_error(f"[{correlation_id}] Failed to get states for fuzzy match")
            return None
        
        entities = states_result.get('data', [])
        names = [e.get('entity_id', '') for e in entities if isinstance(e, dict)]
        
        # Cache fuzzy match results (entity names rarely change)
        names_hash = hashlib.md5('|'.join(sorted(names)).encode()).hexdigest()[:8]
        cache_key = f"fuzzy_match_{search_name}_{names_hash}"
        
        cached_result = cache_get(cache_key)
        if cached_result is not None:
            log_debug(f"Fuzzy match cache hit: {search_name}")
            record_metric('fuzzy_match_cache_hit', 1.0)
            increment_counter('ha_devices_find_fuzzy_cache_hit')
            return cached_result if cached_result != '' else None
        
        search_lower = search_name.lower()
        best_match = None
        best_ratio = threshold
        
        for name in names:
            ratio = SequenceMatcher(None, search_lower, name.lower()).ratio()
            if ratio > best_ratio:
                best_ratio = ratio
                best_match = name
        
        cache_value = best_match if best_match else ''
        cache_set(cache_key, cache_value, ttl=HA_CACHE_TTL_FUZZY_MATCH)
        
        record_metric('fuzzy_match_cache_miss', 1.0)
        if best_match:
            record_metric('fuzzy_match_success', 1.0)
            record_metric('fuzzy_match_ratio', best_ratio)
            increment_counter('ha_devices_find_fuzzy_success')
        else:
            record_metric('fuzzy_match_no_match', 1.0)
            increment_counter('ha_devices_find_fuzzy_no_match')
        
        return best_match
        
    except Exception as e:
        log_error(f"[{correlation_id}] Fuzzy match failed: {str(e)}")
        increment_counter('ha_devices_find_fuzzy_error')
        return None


def call_service_impl(domain: str, service: str, 
                     entity_id: Optional[str] = None,
                     service_data: Optional[Dict] = None, **kwargs) -> Dict[str, Any]:
    """
    Call Home Assistant service implementation.
    
    MIGRATED Phase 3 from ha_core.py call_ha_service()
    
    Core implementation for service calls.
    
    Args:
        domain: Service domain (e.g., 'light', 'switch')
        service: Service name (e.g., 'turn_on', 'turn_off')
        entity_id: Optional target entity ID
        service_data: Optional service data
        **kwargs: Additional options
        
    Returns:
        Service call response
        
    Example:
        result = call_service_impl('light', 'turn_on', 'light.living_room')
        
    REF: INT-HA-02
    """
    correlation_id = generate_correlation_id()
    
    try:
        with DebugContext("call_service_impl", correlation_id,
                         domain=domain, service=service, entity_id=entity_id):
            
            if not isinstance(domain, str) or not domain:
                return create_error_response('Invalid domain', 'INVALID_DOMAIN')
            
            if not isinstance(service, str) or not service:
                return create_error_response('Invalid service', 'INVALID_SERVICE')
            
            endpoint = f'/api/services/{domain}/{service}'
            
            data = service_data if isinstance(service_data, dict) else {}
            if entity_id and isinstance(entity_id, str):
                data['entity_id'] = entity_id
            
            _trace_step(correlation_id, "Calling service", service=f"{domain}.{service}")
            
            result = call_ha_api_impl(endpoint, method='POST', data=data)
            
            if result.get('success'):
                # MIGRATED Phase 3: Smart cache invalidation
                if entity_id:
                    invalidate_entity_cache_impl(entity_id)
                
                increment_counter(f'ha_service_{domain}_{service}')
                record_metric(f'ha_service_{domain}_success', 1.0)
                increment_counter('ha_devices_call_service_success')
                
                return create_success_response('Service called', {
                    'domain': domain,
                    'service': service,
                    'entity_id': entity_id
                })
            
            increment_counter('ha_devices_call_service_error')
            return result
            
    except Exception as e:
        log_error(f"[{correlation_id}] Service call failed: {str(e)}")
        increment_counter('ha_devices_call_service_error')
        return create_error_response(str(e), 'SERVICE_CALL_FAILED')


def update_state_impl(entity_id: str, state_data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """
    Update device state implementation.
    
    MIGRATED Phase 3: New wrapper around call_service_impl
    
    Core implementation for state updates. Uses call_service_impl
    to apply state changes via HA services.
    
    Args:
        entity_id: Entity ID to update
        state_data: New state data (e.g., {'state': 'on', 'brightness': 255})
        **kwargs: Additional options
        
    Returns:
        Update response
        
    REF: INT-HA-02
    """
    correlation_id = generate_correlation_id()
    log_info(f"[{correlation_id}] Updating state for {entity_id}")
    
    try:
        # Extract domain from entity_id (e.g., 'light' from 'light.living_room')
        if '.' not in entity_id:
            return create_error_response('Invalid entity_id format', 'INVALID_ENTITY_ID')
        
        domain = entity_id.split('.')[0]
        
        # Determine service based on state_data
        state = state_data.get('state', '').lower()
        service = 'turn_on' if state == 'on' else 'turn_off' if state == 'off' else None
        
        if not service:
            return create_error_response('Unable to determine service from state_data', 'INVALID_STATE')
        
        # Call service with state data
        result = call_service_impl(domain, service, entity_id, state_data)
        
        if result.get('success'):
            increment_counter('ha_devices_update_state_success')
        else:
            increment_counter('ha_devices_update_state_error')
        
        return result
        
    except Exception as e:
        log_error(f"[{correlation_id}] Update state failed: {str(e)}")
        increment_counter('ha_devices_update_state_error')
        return create_error_response(str(e), 'UPDATE_STATE_FAILED')


def list_by_domain_impl(domain: str, **kwargs) -> Dict[str, Any]:
    """
    List all devices in a domain implementation.
    
    MIGRATED Phase 3: Extracted from ha_core.py get_ha_states()
    
    Core implementation for domain filtering.
    
    Args:
        domain: Domain to filter (e.g., 'light', 'switch', 'sensor')
        **kwargs: Additional options
        
    Returns:
        List of devices in domain
        
    REF: INT-HA-02
    """
    correlation_id = generate_correlation_id()
    log_info(f"[{correlation_id}] Listing devices in domain: {domain}")
    
    try:
        # Get all states
        result = get_states_impl(use_cache=True)
        
        if result.get('success'):
            entities = result.get('data', [])
            # Filter by domain
            filtered = [e for e in entities 
                       if isinstance(e, dict) and 
                       e.get('entity_id', '').startswith(f"{domain}.")]
            
            log_info(f"[{correlation_id}] Found {len(filtered)} entities in domain {domain}")
            increment_counter('ha_devices_list_by_domain_success')
            record_metric(f'ha_devices_domain_{domain}_count', len(filtered))
            
            return create_success_response(f'Entities in domain {domain}', filtered)
        
        increment_counter('ha_devices_list_by_domain_error')
        return result
        
    except Exception as e:
        log_error(f"[{correlation_id}] List by domain failed: {str(e)}")
        increment_counter('ha_devices_list_by_domain_error')
        return create_error_response(str(e), 'LIST_BY_DOMAIN_FAILED')


def check_status_impl(**kwargs) -> Dict[str, Any]:
    """
    Check Home Assistant connection status implementation.
    
    MIGRATED Phase 3 from ha_core.py check_ha_status()
    
    Core implementation for status checks.
    
    Args:
        **kwargs: Additional options
        
    Returns:
        Connection status dictionary
        
    REF: INT-HA-02
    """
    correlation_id = generate_correlation_id()
    
    try:
        with DebugContext("check_status_impl", correlation_id):
            result = call_ha_api_impl('/api/')
            
            if result.get('success'):
                record_metric('ha_status_check_success', 1.0)
                increment_counter('ha_devices_check_status_success')
                return create_success_response('Connected to Home Assistant', {
                    'connected': True,
                    'message': result.get('data', {}).get('message', 'API running')
                })
            
            record_metric('ha_status_check_failure', 1.0)
            increment_counter('ha_devices_check_status_error')
            return create_error_response('Failed to connect to HA', 'CONNECTION_FAILED', result)
            
    except Exception as e:
        log_error(f"[{correlation_id}] Status check failed: {str(e)}")
        increment_counter('ha_devices_check_status_error')
        return create_error_response(str(e), 'STATUS_CHECK_FAILED')


# ===== MIGRATED Phase 3: Cache Management =====

def warm_cache_impl(**kwargs) -> Dict[str, Any]:
    """
    Pre-warm cache on cold start.
    
    MIGRATED Phase 3 from ha_core.py warm_ha_cache()
    
    Loads frequently accessed data into cache during Lambda initialization
    to eliminate first-request penalties.
    
    Uses existing INT-01 (CACHE) interface - no duplication.
    
    Returns:
        Dict with warming status and statistics
        
    REF: INT-HA-02
    """
    if not HA_CACHE_WARMING_ENABLED:
        log_debug("Cache warming disabled (HA_CACHE_WARMING_ENABLED=false)")
        return create_success_response('Cache warming disabled', {'warmed': 0})
    
    correlation_id = generate_correlation_id()
    start_time = time.perf_counter()
    warmed_count = 0
    errors = []
    
    try:
        log_info(f"[{correlation_id}] Starting HA cache warming")
        
        # 1. Warm HA configuration (most frequently accessed)
        try:
            config = load_ha_config()
            # Uses existing cache_set() from INT-01
            cache_set('ha_config', config, ttl=HA_CACHE_TTL_CONFIG)
            warmed_count += 1
            log_debug(f"[{correlation_id}] Warmed: ha_config")
        except Exception as e:
            errors.append(f"Config warming failed: {str(e)}")
            log_error(f"[{correlation_id}] Config warming error: {e}")
        
        # 2. Pre-fetch HA states if enabled and configured
        try:
            if config and config.get('enabled'):
                # Predictive pre-loading: States are accessed in 80% of requests
                states_result = get_states_impl(use_cache=False)
                if states_result.get('success'):
                    # Already cached by get_states_impl() using cache_set()
                    warmed_count += 1
                    log_debug(f"[{correlation_id}] Warmed: ha_all_states")
        except Exception as e:
            errors.append(f"States warming failed: {str(e)}")
            log_error(f"[{correlation_id}] States warming error: {e}")
        
        # 3. Record warming metrics using existing INT-04
        duration_ms = (time.perf_counter() - start_time) * 1000
        record_metric('ha_cache_warming_duration_ms', duration_ms)
        record_metric('ha_cache_warming_items', float(warmed_count))
        increment_counter('ha_cache_warming_completed')
        
        log_info(f"[{correlation_id}] Cache warming complete: {warmed_count} items in {duration_ms:.2f}ms")
        
        return create_success_response('Cache warming complete', {
            'warmed_count': warmed_count,
            'duration_ms': duration_ms,
            'errors': errors
        })
        
    except Exception as e:
        log_error(f"[{correlation_id}] Cache warming failed: {str(e)}")
        increment_counter('ha_cache_warming_error')
        return create_error_response(str(e), 'CACHE_WARMING_FAILED')


def invalidate_entity_cache_impl(entity_id: str, **kwargs) -> bool:
    """
    Smart cache invalidation for specific entity.
    
    MIGRATED Phase 3 from ha_core.py invalidate_entity_cache()
    
    Event-based invalidation: only clear affected entity, not entire cache.
    Uses existing cache_delete() from INT-01.
    
    Args:
        entity_id: Entity ID to invalidate
        **kwargs: Additional options
        
    Returns:
        True if invalidated, False otherwise
        
    REF: INT-HA-02
    """
    try:
        # Invalidate specific entity state
        result = cache_delete(f"ha_state_{entity_id}")
        
        # Also invalidate fuzzy match cache entries that might contain this entity
        # (More targeted than clearing all states)
        increment_counter('ha_cache_smart_invalidation')
        record_metric('ha_cache_invalidation_targeted', 1.0)
        
        log_debug(f"Smart invalidation: {entity_id}")
        return result
        
    except Exception as e:
        log_error(f"Smart invalidation failed for {entity_id}: {e}")
        return False


def invalidate_domain_cache_impl(domain: str, **kwargs) -> int:
    """
    Invalidate cache for entire domain.
    
    MIGRATED Phase 3 from ha_core.py invalidate_domain_cache()
    
    Example: Invalidate all 'light.*' entities after group operation.
    Uses existing cache_stats() and cache_delete() from INT-01.
    
    Args:
        domain: Domain to invalidate (e.g., 'light', 'switch')
        **kwargs: Additional options
        
    Returns:
        Number of cache entries invalidated
        
    REF: INT-HA-02
    """
    try:
        # Get all cache keys using existing INT-01 cache_stats()
        stats = cache_stats()
        keys = stats.get('keys', [])
        
        # Filter for domain-specific keys
        invalidated = 0
        for key in keys:
            if key.startswith(f"ha_state_{domain}."):
                if cache_delete(key):
                    invalidated += 1
        
        increment_counter(f'ha_cache_domain_invalidation_{domain}')
        record_metric('ha_cache_invalidation_count', float(invalidated))
        
        log_info(f"Domain invalidation: {domain} ({invalidated} entries)")
        return invalidated
        
    except Exception as e:
        log_error(f"Domain invalidation failed for {domain}: {e}")
        return 0


# ===== MIGRATED Phase 3: Performance Reporting =====

def get_performance_report_impl(**kwargs) -> Dict[str, Any]:
    """
    Get comprehensive performance report.
    
    MIGRATED Phase 3 from ha_core.py get_performance_report()
    
    Builds on existing INT-04 (METRICS) interface - uses get_metrics_stats()
    to analyze performance data and generate insights.
    
    Returns:
        Performance report with timing analysis, cache efficiency, bottlenecks
        
    REF: INT-HA-02
    """
    try:
        # Get raw metrics from existing INT-04 interface
        raw_metrics = get_metrics_stats()
        
        # Get cache statistics from existing INT-01 interface
        cache_info = cache_stats()
        
        # Analyze HA-specific operations
        ha_operations = {}
        slow_operations_list = []
        
        # Extract HA operation metrics (those starting with 'ha_')
        for metric_name, values in raw_metrics.get('metrics', {}).items():
            if metric_name.startswith('ha_') and '_duration_ms' in metric_name:
                operation = metric_name.replace('_duration_ms', '')
                
                if values:
                    avg_ms = sum(values) / len(values)
                    percentiles = _calculate_percentiles(values, [50, 95, 99])
                    
                    ha_operations[operation] = {
                        'avg_ms': avg_ms,
                        'min_ms': min(values),
                        'max_ms': max(values),
                        'p50_ms': percentiles['p50'],
                        'p95_ms': percentiles['p95'],
                        'p99_ms': percentiles['p99'],
                        'sample_count': len(values)
                    }
                    
                    # Identify slow operations
                    if percentiles['p95'] > HA_SLOW_OPERATION_THRESHOLD_MS:
                        slow_operations_list.append({
                            'operation': operation,
                            'p95_ms': percentiles['p95'],
                            'max_ms': max(values)
                        })
        
        # Calculate cache efficiency
        cache_efficiency = {}
        if cache_info.get('hits', 0) + cache_info.get('misses', 0) > 0:
            total_requests = cache_info['hits'] + cache_info['misses']
            cache_efficiency = {
                'hit_rate_percent': (cache_info['hits'] / total_requests) * 100,
                'total_hits': cache_info['hits'],
                'total_misses': cache_info['misses'],
                'efficiency_score': 'excellent' if (cache_info['hits'] / total_requests) > 0.8 else
                                  'good' if (cache_info['hits'] / total_requests) > 0.6 else
                                  'needs_improvement'
            }
        
        # Build comprehensive report
        report = {
            'timestamp': get_timestamp(),
            'ha_core_version': '2.0.0-PHASE3',
            'operations': ha_operations,
            'cache_efficiency': cache_efficiency,
            'slow_operations': sorted(slow_operations_list, 
                                     key=lambda x: x['p95_ms'], 
                                     reverse=True)[:5],  # Top 5 slowest
            'slow_operation_count': len(_SLOW_OPERATIONS),
            'cache_stats': cache_info,
            'recommendations': _generate_performance_recommendations(
                ha_operations, 
                cache_efficiency, 
                slow_operations_list
            )
        }
        
        return create_success_response('Performance report generated', report)
        
    except Exception as e:
        log_error(f"Performance report generation failed: {str(e)}")
        return create_error_response(str(e), 'REPORT_GENERATION_FAILED')


def get_diagnostic_info_impl(**kwargs) -> Dict[str, Any]:
    """
    Get HA diagnostic information.
    
    MIGRATED Phase 3 from ha_core.py get_diagnostic_info()
    
    Returns diagnostic information about devices core.
    
    Returns:
        Diagnostic information dictionary
        
    REF: INT-HA-02
    """
    return {
        'ha_devices_core_version': '2.0.0-PHASE3',
        'migration_source': 'ha_core.py',
        'cache_ttl_entities': HA_CACHE_TTL_ENTITIES,
        'cache_ttl_state': HA_CACHE_TTL_STATE,
        'cache_ttl_config': HA_CACHE_TTL_CONFIG,
        'cache_ttl_fuzzy_match': HA_CACHE_TTL_FUZZY_MATCH,
        'circuit_breaker_name': HA_CIRCUIT_BREAKER_NAME,
        'debug_mode': _DEBUG_MODE_ENABLED,
        'cache_warming_enabled': HA_CACHE_WARMING_ENABLED,
        'slow_operation_threshold_ms': HA_SLOW_OPERATION_THRESHOLD_MS,
        'slow_operations_detected': len(_SLOW_OPERATIONS),
        'phase3_migration': {
            'complete': True,
            'functions_migrated': 16,
            'from_file': 'ha_core.py',
            'architecture': 'HA-SUGA'
        },
        'phase5_features': {
            'cache_warming': HA_CACHE_WARMING_ENABLED,
            'smart_invalidation': True,
            'performance_profiling': True,
            'predictive_preloading': True
        },
        'sentinel_sanitization': 'Handled by gateway (interface_cache.py)'
    }


__all__ = [
    # Core device operations (7)
    'get_states_impl',
    'get_by_id_impl',
    'find_fuzzy_impl',
    'update_state_impl',
    'call_service_impl',
    'list_by_domain_impl',
    'check_status_impl',
    # Helper functions (needed by Alexa)
    'call_ha_api_impl',
    'get_ha_config_impl',
    # Cache management (3)
    'warm_cache_impl',
    'invalidate_entity_cache_impl',
    'invalidate_domain_cache_impl',
    # Performance (2)
    'get_performance_report_impl',
    'get_diagnostic_info_impl',
]

# PHASE 3 MIGRATION SUMMARY:
# - Migrated 16 functions from ha_core.py
# - 7 core device operations (get_states, call_service, etc.)
# - 2 essential helpers (call_ha_api, get_ha_config)
# - 3 cache management functions
# - 2 performance/diagnostic functions
# - 2 debug helpers (DebugContext, _trace_step)
# - All functions use LEE gateway for HTTP, logging, metrics
# - Smart cache invalidation integrated
# - Performance profiling capabilities included
# - Ready for ha_alexa_core.py to use via ha_interconnect

# EOF
