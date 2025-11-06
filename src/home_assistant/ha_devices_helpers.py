# ha_devices_helpers.py
"""
ha_devices_helpers.py - Device Helper Functions and Utilities
Version: 3.0.0 - FILE SPLIT COMPLIANT
Date: 2025-11-05
Purpose: Helper functions and utilities for HA device operations

Split from ha_devices_core.py v2.0.0 (866 lines) for SIMAv4 compliance.
This file contains shared utilities used by core and cache modules.

Architecture:
- Shared by ha_devices_core.py and ha_devices_cache.py
- NO imports from other ha_devices_* files (prevents circular)
- Uses gateway services only

Functions:
- call_ha_api_impl: HTTP operations for HA API
- get_ha_config_impl: Config loading (FIXES CRIT-01)
- _extract_entity_list: Parse entity lists from responses
- _trace_step: Debug tracing
- _is_debug_mode: Check debug mode
- _calculate_percentiles: Statistical calculations
- _generate_performance_recommendations: Performance analysis

Classes:
- DebugContext: Debug tracing context manager

Constants:
- HA_CACHE_TTL_* values
- HA_CIRCUIT_BREAKER_NAME
- HA_SLOW_OPERATION_THRESHOLD_MS

Copyright 2025 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

import os
import time
from typing import Dict, Any, Optional, List
from collections import defaultdict

# Import LEE services via gateway (ONLY way to access LEE)
from gateway import (
    log_info, log_error, log_debug, log_warning,
    execute_operation, GatewayInterface,
    cache_get, cache_set, cache_delete,
    increment_counter, record_metric,
    create_success_response, create_error_response,
    generate_correlation_id,
    execute_with_circuit_breaker  # ADDED: CRIT-08 fix
)

# ===== MODULE CONSTANTS =====

HA_CACHE_TTL_ENTITIES = 300
HA_CACHE_TTL_STATE = 60
HA_CACHE_TTL_CONFIG = 600
HA_CACHE_TTL_FUZZY_MATCH = 300
HA_CIRCUIT_BREAKER_NAME = "home_assistant"
HA_SLOW_OPERATION_THRESHOLD_MS = 1000  # Alert if operation > 1s
HA_CACHE_WARMING_ENABLED = os.getenv('HA_CACHE_WARMING_ENABLED', 'false').lower() == 'true'

_DEBUG_MODE_ENABLED = os.getenv('DEBUG_MODE', 'false').lower() == 'true'

# Track slow operations in memory (shared across modules)
_SLOW_OPERATIONS = defaultdict(int)  # operation_name: count


# ===== HELPER FUNCTIONS =====

def _is_debug_mode() -> bool:
    """
    Check if DEBUG_MODE is enabled (cached at module level).
    
    Returns:
        True if debug mode enabled, False otherwise
    """
    return _DEBUG_MODE_ENABLED


class DebugContext:
    """
    Debug tracing context manager.
    
    Provides structured debug output with timing and nesting.
    
    Example:
        with DebugContext("operation", corr_id, param1="value"):
            # operation code
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
    Log a debug trace step.
    
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
    Extract entity list from various response formats.
    
    HA /api/states returns different formats depending on how it's called.
    This function handles all common formats robustly.
    
    Args:
        data: Response data to extract from
        context: Context for logging
        
    Returns:
        List of entity dictionaries
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
    Calculate percentiles from list of values.
    
    Args:
        values: List of numeric values
        percentiles: List of percentile values to calculate (e.g., [50, 95, 99])
        
    Returns:
        Dict mapping percentile to value (e.g., {'p50': 123.4, 'p95': 456.7})
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
    Generate performance improvement recommendations.
    
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


# ===== CORE HELPER IMPLEMENTATIONS =====

def get_ha_config_impl(force_reload: bool = False, **kwargs) -> Dict[str, Any]:
    """
    Get Home Assistant configuration with cache validation.
    
    Core implementation for configuration loading.
    FIXES CRIT-01: Uses lazy import instead of module-level import.
    
    Args:
        force_reload: Force reload from sources
        **kwargs: Additional options
        
    Returns:
        Configuration dictionary
        
    REF: INT-HA-02, FIXES CRIT-01
    """
    # FIXED CRIT-01: Lazy import instead of module-level
    import ha_config
    
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
        # Use lazy-imported module
        config = ha_config.load_ha_config()
        
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
            
            # ADDED CRIT-08: Circuit breaker protection for HA API calls
            http_result = execute_with_circuit_breaker(
                HA_CIRCUIT_BREAKER_NAME,
                execute_operation,
                GatewayInterface.HTTP_CLIENT,
                method.lower(),
                url=url,
                headers=headers,
                json=data,
                timeout=config.get('timeout', 30)
            )
            
            duration_ms = (time.perf_counter() - start_time) * 1000
            
            # Track slow operations
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


__all__ = [
    # Helper functions
    'call_ha_api_impl',
    'get_ha_config_impl',
    '_extract_entity_list',
    '_trace_step',
    '_is_debug_mode',
    '_calculate_percentiles',
    '_generate_performance_recommendations',
    # Class
    'DebugContext',
    # Constants
    'HA_CACHE_TTL_ENTITIES',
    'HA_CACHE_TTL_STATE',
    'HA_CACHE_TTL_CONFIG',
    'HA_CACHE_TTL_FUZZY_MATCH',
    'HA_CIRCUIT_BREAKER_NAME',
    'HA_SLOW_OPERATION_THRESHOLD_MS',
    'HA_CACHE_WARMING_ENABLED',
    '_SLOW_OPERATIONS',
]

# FILE SPLIT NOTES:
# - Split from ha_devices_core.py v2.0.0 (866 lines)
# - This file: ~280 lines (within 400-line limit)
# - CRIT-01 FIXED: Lazy import in get_ha_config_impl()
# - No imports from ha_devices_core or ha_devices_cache (prevents circular)
# - Shared by core and cache modules

# EOF
