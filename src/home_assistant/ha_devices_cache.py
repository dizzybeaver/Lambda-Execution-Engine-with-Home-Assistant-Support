# ha_devices_cache.py
"""
ha_devices_cache.py - Cache Management Functions
Version: 3.0.1
Date: 2025-12-05
Purpose: Cache management and performance reporting for HA devices

MODIFIED (3.0.1 - LWA MIGRATION):
- ADDED: oauth_token parameter to warm_cache_impl
- ADDED: oauth_token passing to get_ha_config_impl and get_states_impl

Architecture:
- Uses ha_devices_helpers for shared utilities
- Uses gateway services for cache operations
- NO imports from ha_devices_core (prevents circular)

Functions:
- warm_cache_impl: Pre-warm cache on cold start
- invalidate_entity_cache_impl: Smart cache invalidation for entity
- invalidate_domain_cache_impl: Invalidate cache for entire domain
- get_performance_report_impl: Comprehensive performance report
- get_diagnostic_info_impl: Diagnostic information

Copyright 2025 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

import time
from typing import Dict, Any

# Import gateway services
from gateway import (
    log_info, log_error, log_debug,
    cache_get, cache_set, cache_delete, cache_stats,
    increment_counter, record_metric, get_metrics_stats,
    create_success_response, create_error_response,
    generate_correlation_id, get_timestamp
)

# Import helpers from home_assistant.ha_devices_helpers
from home_assistant.ha_devices_helpers import (
    get_ha_config_impl,
    _calculate_percentiles,
    _generate_performance_recommendations,
    HA_CACHE_TTL_CONFIG,
    HA_SLOW_OPERATION_THRESHOLD_MS,
    HA_CACHE_WARMING_ENABLED,
    _SLOW_OPERATIONS
)


# ===== CACHE MANAGEMENT =====

def warm_cache_impl(oauth_token: str = None, **kwargs) -> Dict[str, Any]:
    """
    Pre-warm cache on cold start.
    
    LWA Migration: Accepts oauth_token and passes to HA API calls.
    
    Loads frequently accessed data into cache during Lambda initialization
    to eliminate first-request penalties.
    
    Args:
        oauth_token: OAuth token from Alexa directive (LWA)
        **kwargs: Additional options
    
    Returns:
        Dict with warming status and statistics
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
            from home_assistant.ha_devices_core import get_states_impl
            
            config = get_ha_config_impl(oauth_token=oauth_token)
            cache_set('ha_config', config, ttl=HA_CACHE_TTL_CONFIG)
            warmed_count += 1
            log_debug(f"[{correlation_id}] Warmed: ha_config")
        except Exception as e:
            errors.append(f"Config warming failed: {str(e)}")
            log_error(f"[{correlation_id}] Config warming error: {e}")
        
        # 2. Pre-fetch HA states if enabled and configured
        try:
            if config and config.get('enabled'):
                from home_assistant.ha_devices_core import get_states_impl
                
                states_result = get_states_impl(use_cache=False, oauth_token=oauth_token)
                if states_result.get('success'):
                    warmed_count += 1
                    log_debug(f"[{correlation_id}] Warmed: ha_all_states")
        except Exception as e:
            errors.append(f"States warming failed: {str(e)}")
            log_error(f"[{correlation_id}] States warming error: {e}")
        
        # 3. Record warming metrics
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
    
    Event-based invalidation: only clear affected entity, not entire cache.
    Uses existing cache_delete() from INT-01.
    
    Args:
        entity_id: Entity ID to invalidate
        **kwargs: Additional options
        
    Returns:
        True if invalidated, False otherwise
    """
    try:
        result = cache_delete(f"ha_state_{entity_id}")
        
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
    
    Example: Invalidate all 'light.*' entities after group operation.
    Uses existing cache_stats() and cache_delete() from INT-01.
    
    Args:
        domain: Domain to invalidate (e.g., 'light', 'switch')
        **kwargs: Additional options
        
    Returns:
        Number of cache entries invalidated
    """
    try:
        stats = cache_stats()
        keys = stats.get('keys', [])
        
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


# ===== PERFORMANCE REPORTING =====

def get_performance_report_impl(**kwargs) -> Dict[str, Any]:
    """
    Get comprehensive performance report.
    
    Builds on existing INT-04 (METRICS) interface - uses get_metrics_stats()
    to analyze performance data and generate insights.
    
    Returns:
        Performance report with timing analysis, cache efficiency, bottlenecks
    """
    try:
        raw_metrics = get_metrics_stats()
        cache_info = cache_stats()
        
        ha_operations = {}
        slow_operations_list = []
        
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
                    
                    if percentiles['p95'] > HA_SLOW_OPERATION_THRESHOLD_MS:
                        slow_operations_list.append({
                            'operation': operation,
                            'p95_ms': percentiles['p95'],
                            'max_ms': max(values)
                        })
        
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
        
        report = {
            'timestamp': get_timestamp(),
            'ha_core_version': '3.0.1-LWA-MIGRATION',
            'operations': ha_operations,
            'cache_efficiency': cache_efficiency,
            'slow_operations': sorted(slow_operations_list, 
                                     key=lambda x: x['p95_ms'], 
                                     reverse=True)[:5],
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
    
    Returns diagnostic information about devices cache module.
    
    Returns:
        Diagnostic information dictionary
    """
    from home_assistant.ha_devices_helpers import (
        HA_CACHE_TTL_ENTITIES,
        HA_CACHE_TTL_STATE,
        HA_CACHE_TTL_FUZZY_MATCH,
        HA_CIRCUIT_BREAKER_NAME,
        _DEBUG_MODE_ENABLED
    )
    
    return {
        'ha_devices_cache_version': '3.0.1-LWA-MIGRATION',
        'migration_source': 'ha_devices_core.py v2.0.0',
        'cache_ttl_entities': HA_CACHE_TTL_ENTITIES,
        'cache_ttl_state': HA_CACHE_TTL_STATE,
        'cache_ttl_config': HA_CACHE_TTL_CONFIG,
        'cache_ttl_fuzzy_match': HA_CACHE_TTL_FUZZY_MATCH,
        'circuit_breaker_name': HA_CIRCUIT_BREAKER_NAME,
        'debug_mode': _DEBUG_MODE_ENABLED,
        'cache_warming_enabled': HA_CACHE_WARMING_ENABLED,
        'slow_operation_threshold_ms': HA_SLOW_OPERATION_THRESHOLD_MS,
        'slow_operations_detected': len(_SLOW_OPERATIONS),
        'lwa_migration': {
            'complete': True,
            'oauth_token_support': True,
            'warm_cache_supports_oauth': True
        },
        'file_split': {
            'complete': True,
            'from_file': 'ha_devices_core.py',
            'split_reason': 'SIMAv4 350-line limit compliance',
            'files': [
                'ha_devices_core.py',
                'ha_devices_helpers.py',
                'ha_devices_cache.py'
            ]
        },
        'features': {
            'cache_warming': HA_CACHE_WARMING_ENABLED,
            'smart_invalidation': True,
            'performance_profiling': True,
            'predictive_preloading': True,
            'lwa_oauth_support': True
        }
    }


__all__ = [
    'warm_cache_impl',
    'invalidate_entity_cache_impl',
    'invalidate_domain_cache_impl',
    'get_performance_report_impl',
    'get_diagnostic_info_impl',
]

# EOF
