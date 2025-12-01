# ha_health.py
"""
ha_health.py - Health Check and Monitoring
Version: 1.0.0
Date: 2025-11-05
Purpose: Health checks for Home Assistant integration

Architecture:
Provides health check endpoints for monitoring and diagnostics.

Copyright 2025 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

import time
from typing import Dict, Any
from gateway import (
    log_info, log_error, log_debug,
    cache_get,
    create_success_response, create_error_response,
    generate_correlation_id,
    get_circuit_breaker_stats
)

# Import HA modules
import home_assistant.ha_interconnect
from ha_devices_helpers import get_rate_limit_stats


def check_ha_connectivity(timeout: int = 5) -> Dict[str, Any]:
    """
    Check Home Assistant connectivity.
    
    Tests basic connectivity to HA API.
    
    Args:
        timeout: Connection timeout in seconds
        
    Returns:
        Health check result with status and details
    """
    correlation_id = generate_correlation_id()
    start_time = time.perf_counter()
    
    try:
        # Try to get HA config (tests config loading and caching)
        result = ha_interconnect.devices_get_ha_config()
        
        duration_ms = (time.perf_counter() - start_time) * 1000
        
        if result.get('success'):
            config = result.get('data', {})
            
            return {
                'status': 'healthy' if config.get('enabled') else 'disabled',
                'enabled': config.get('enabled', False),
                'has_url': bool(config.get('base_url')),
                'has_token': bool(config.get('access_token')),
                'check_duration_ms': duration_ms,
                'timestamp': time.time()
            }
        else:
            return {
                'status': 'unhealthy',
                'error': result.get('error', 'Unknown error'),
                'check_duration_ms': duration_ms,
                'timestamp': time.time()
            }
            
    except Exception as e:
        duration_ms = (time.perf_counter() - start_time) * 1000
        log_error(f"[{correlation_id}] Health check failed: {str(e)}")
        
        return {
            'status': 'error',
            'error': str(e),
            'check_duration_ms': duration_ms,
            'timestamp': time.time()
        }


def check_circuit_breaker_health() -> Dict[str, Any]:
    """
    Check circuit breaker status.
    
    Returns circuit breaker state and statistics.
    
    Returns:
        Circuit breaker health information
    """
    try:
        # Get circuit breaker stats for HA
        stats = get_circuit_breaker_stats('home_assistant')
        
        if not stats:
            return {
                'status': 'unknown',
                'message': 'Circuit breaker stats not available'
            }
        
        state = stats.get('state', 'unknown')
        
        return {
            'status': 'healthy' if state == 'closed' else 'degraded',
            'state': state,
            'failure_count': stats.get('failure_count', 0),
            'success_count': stats.get('success_count', 0),
            'last_failure': stats.get('last_failure_time'),
            'timestamp': time.time()
        }
        
    except Exception as e:
        log_error(f"Circuit breaker health check failed: {str(e)}")
        
        return {
            'status': 'error',
            'error': str(e),
            'timestamp': time.time()
        }


def check_rate_limiter_health() -> Dict[str, Any]:
    """
    Check rate limiter status.
    
    Returns rate limiter statistics and health.
    
    Returns:
        Rate limiter health information
    """
    try:
        stats = get_rate_limit_stats()
        
        if not stats.get('enabled'):
            return {
                'status': 'disabled',
                'message': 'Rate limiting not enabled'
            }
        
        tokens = stats.get('tokens_available', 0)
        rate = stats.get('rate_per_second', 0)
        
        # Consider healthy if we have >50% tokens available
        is_healthy = tokens > (rate * 0.5)
        
        return {
            'status': 'healthy' if is_healthy else 'throttled',
            'tokens_available': tokens,
            'rate_per_second': rate,
            'burst_size': stats.get('burst_size', 0),
            'recent_requests': stats.get('recent_requests_10s', 0),
            'timestamp': time.time()
        }
        
    except Exception as e:
        log_error(f"Rate limiter health check failed: {str(e)}")
        
        return {
            'status': 'error',
            'error': str(e),
            'timestamp': time.time()
        }


def check_cache_health() -> Dict[str, Any]:
    """
    Check cache system health.
    
    Tests cache connectivity and basic operations.
    
    Returns:
        Cache health information
    """
    correlation_id = generate_correlation_id()
    
    try:
        # Test cache read
        test_key = f'health_check_{correlation_id}'
        start_time = time.perf_counter()
        
        # Try to get (should be None)
        result = cache_get(test_key)
        
        read_duration_ms = (time.perf_counter() - start_time) * 1000
        
        return {
            'status': 'healthy',
            'read_duration_ms': read_duration_ms,
            'operational': True,
            'timestamp': time.time()
        }
        
    except Exception as e:
        log_error(f"Cache health check failed: {str(e)}")
        
        return {
            'status': 'error',
            'error': str(e),
            'operational': False,
            'timestamp': time.time()
        }


def get_overall_health(include_details: bool = True) -> Dict[str, Any]:
    """
    Get overall system health.
    
    Aggregates health checks from all components.
    
    Args:
        include_details: Include detailed health info for each component
        
    Returns:
        Overall health status with component details
    """
    correlation_id = generate_correlation_id()
    start_time = time.perf_counter()
    
    try:
        log_debug(f"[{correlation_id}] Running overall health check")
        
        # Run all health checks
        ha_health = check_ha_connectivity()
        cb_health = check_circuit_breaker_health()
        rl_health = check_rate_limiter_health()
        cache_health = check_cache_health()
        
        # Determine overall status
        statuses = [
            ha_health.get('status'),
            cb_health.get('status'),
            rl_health.get('status'),
            cache_health.get('status')
        ]
        
        # Overall health logic:
        # - healthy: all components healthy
        # - degraded: some components degraded but functional
        # - unhealthy: critical component unhealthy
        # - error: any component in error state
        
        if 'error' in statuses:
            overall_status = 'error'
        elif 'unhealthy' in statuses:
            overall_status = 'unhealthy'
        elif 'degraded' in statuses or 'throttled' in statuses:
            overall_status = 'degraded'
        elif all(s in ['healthy', 'disabled'] for s in statuses):
            overall_status = 'healthy'
        else:
            overall_status = 'unknown'
        
        duration_ms = (time.perf_counter() - start_time) * 1000
        
        result = {
            'status': overall_status,
            'check_duration_ms': duration_ms,
            'timestamp': time.time()
        }
        
        if include_details:
            result['components'] = {
                'home_assistant': ha_health,
                'circuit_breaker': cb_health,
                'rate_limiter': rl_health,
                'cache': cache_health
            }
        
        log_info(f"[{correlation_id}] Health check complete: {overall_status}")
        
        return create_success_response('Health check complete', result)
        
    except Exception as e:
        duration_ms = (time.perf_counter() - start_time) * 1000
        log_error(f"[{correlation_id}] Overall health check failed: {str(e)}")
        
        return create_error_response(
            str(e),
            'HEALTH_CHECK_FAILED',
            {
                'check_duration_ms': duration_ms,
                'timestamp': time.time()
            }
        )


def get_health_summary() -> Dict[str, Any]:
    """
    Get brief health summary.
    
    Quick health check without detailed component info.
    
    Returns:
        Brief health summary
    """
    result = get_overall_health(include_details=False)
    
    if result.get('success'):
        data = result.get('data', {})
        return {
            'healthy': data.get('status') == 'healthy',
            'status': data.get('status'),
            'timestamp': data.get('timestamp')
        }
    
    return {
        'healthy': False,
        'status': 'error',
        'error': result.get('error'),
        'timestamp': time.time()
    }


__all__ = [
    'check_ha_connectivity',
    'check_circuit_breaker_health',
    'check_rate_limiter_health',
    'check_cache_health',
    'get_overall_health',
    'get_health_summary'
]

# EOF
