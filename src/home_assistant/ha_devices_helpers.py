# ha_devices_helpers.py
"""
ha_devices_helpers.py - Device Helper Functions and Utilities
Version: 3.1.0
Date: 2025-11-05
Purpose: Helper functions and utilities for HA device operations

Architecture:
- Shared by ha_devices_core.py and ha_devices_cache.py
- NO imports from other ha_devices_* files (prevents circular)
- Uses gateway services only

Copyright 2025 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

import os
import time
from typing import Dict, Any, Optional, List
from collections import defaultdict, deque

# Import LEE services via gateway (ONLY way to access LEE)
from gateway import (
    log_info, log_error, log_debug, log_warning,
    execute_operation, GatewayInterface,
    cache_get, cache_set, cache_delete,
    increment_counter, record_metric,
    create_success_response, create_error_response,
    generate_correlation_id,
    execute_with_circuit_breaker
)

# ===== MODULE CONSTANTS =====

HA_CACHE_TTL_ENTITIES = 300
HA_CACHE_TTL_STATE = 60
HA_CACHE_TTL_CONFIG = 600
HA_CACHE_TTL_FUZZY_MATCH = 300
HA_CIRCUIT_BREAKER_NAME = "home_assistant"
HA_SLOW_OPERATION_THRESHOLD_MS = 1000
HA_CACHE_WARMING_ENABLED = os.getenv('HA_CACHE_WARMING_ENABLED', 'false').lower() == 'true'

HA_RATE_LIMIT_ENABLED = os.getenv('HA_RATE_LIMIT_ENABLED', 'true').lower() == 'true'
HA_RATE_LIMIT_PER_SECOND = int(os.getenv('HA_RATE_LIMIT_PER_SECOND', '10'))
HA_RATE_LIMIT_BURST = int(os.getenv('HA_RATE_LIMIT_BURST', '20'))
HA_RATE_LIMIT_WINDOW_SECONDS = 1.0

_DEBUG_MODE_ENABLED = os.getenv('DEBUG_MODE', 'false').lower() == 'true'
_SLOW_OPERATIONS = defaultdict(int)

class RateLimiter:
    """
    Token bucket rate limiter for HA API calls.
    
    Protects Home Assistant from overload while allowing bursts.
    Thread-safe for Lambda's single-threaded environment.
    """
    def __init__(self, rate: int, burst: int):
        """
        Initialize rate limiter.
        
        Args:
            rate: Requests per second
            burst: Maximum burst size
        """
        self.rate = rate
        self.burst = burst
        self.tokens = float(burst)
        self.last_update = time.time()
        self.request_times = deque(maxlen=burst)
        
    def allow_request(self, correlation_id: str) -> bool:
        """
        Check if request is allowed under rate limit.
        
        Uses token bucket algorithm with time-based refill.
        
        Args:
            correlation_id: Request correlation ID for logging
            
        Returns:
            True if request allowed, False if rate limited
        """
        now = time.time()
        
        # Refill tokens based on time elapsed
        elapsed = now - self.last_update
        self.tokens = min(self.burst, self.tokens + (elapsed * self.rate))
        self.last_update = now
        
        # Check if we have tokens available
        if self.tokens >= 1.0:
            self.tokens -= 1.0
            self.request_times.append(now)
            return True
        
        # Rate limited
        log_warning(f"[{correlation_id}] Rate limit exceeded: {self.rate} req/s")
        increment_counter('ha_api_rate_limited')
        return False
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get current rate limiter statistics.
        
        Returns:
            Dictionary with tokens, recent requests, etc.
        """
        now = time.time()
        recent = len([t for t in self.request_times if now - t < 10.0])
        
        return {
            'tokens_available': self.tokens,
            'rate_per_second': self.rate,
            'burst_size': self.burst,
            'recent_requests_10s': recent
        }

_rate_limiter = RateLimiter(
    rate=HA_RATE_LIMIT_PER_SECOND,
    burst=HA_RATE_LIMIT_BURST
)


# ===== HELPER FUNCTIONS =====

def _is_debug_mode() -> bool:
    """Check if DEBUG_MODE is enabled."""
    return _DEBUG_MODE_ENABLED


class DebugContext:
    """Debug tracing context manager."""
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
        return False


def _trace_step(correlation_id: str, step: str, **details):
    """Log a debug trace step."""
    if _DEBUG_MODE_ENABLED:
        detail_str = ', '.join(f"{k}={v}" for k, v in details.items()) if details else ''
        log_info(f"[{correlation_id}] [STEP] {step}" + (f" ({detail_str})" if detail_str else ""))


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
        
        log_debug(f"Dict format in {context} not recognized: {list(data.keys())[:5]}")
    
    log_warning(f"Could not extract entity list from {type(data).__name__} in {context}")
    return []


def _calculate_percentiles(values: List[float], percentiles: List[int]) -> Dict[str, float]:
    """Calculate percentiles from list of values."""
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
    """Generate performance improvement recommendations."""
    recommendations = []
    
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
    
    if slow_ops:
        for op in slow_ops[:3]:
            recommendations.append(
                f"Operation '{op['operation']}' is slow (p95: {op['p95_ms']:.0f}ms). "
                f"Consider optimization or caching."
            )
    
    if not recommendations:
        recommendations.append("Performance metrics look good. No immediate optimizations needed.")
    
    return recommendations


def _check_rate_limit(correlation_id: str) -> bool:
    """
    Check if request should be allowed under rate limit.
    
    Args:
        correlation_id: Request correlation ID
        
    Returns:
        True if allowed, False if rate limited
    """
    if not HA_RATE_LIMIT_ENABLED:
        return True
    
    return _rate_limiter.allow_request(correlation_id)

def get_rate_limit_stats() -> Dict[str, Any]:
    """
    Get current rate limiter statistics.
    
    Returns:
        Dictionary with rate limit stats
    """
    if not HA_RATE_LIMIT_ENABLED:
        return {
            'enabled': False,
            'message': 'Rate limiting disabled'
        }
    
    stats = _rate_limiter.get_stats()
    stats['enabled'] = True
    return stats


# ===== CORE HELPER IMPLEMENTATIONS =====

def get_ha_config_impl(force_reload: bool = False, **kwargs) -> Dict[str, Any]:
    """
    Get Home Assistant configuration.
    FIXES CRIT-01: Uses lazy import.
    """
    import home_assistant.ha_config
    
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
                    _trace_step(correlation_id, "Invalid cache format")
                    cache_delete(cache_key)
        
        _trace_step(correlation_id, "Loading fresh HA config")
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
    Call Home Assistant API endpoint.
    
    Args:
        endpoint: API endpoint
        method: HTTP method
        data: Optional request data
        config: Optional HA configuration
        **kwargs: Additional options
        
    Returns:
        API response dictionary
    """
    correlation_id = generate_correlation_id()
    start_time = time.perf_counter()
    
    try:
        with DebugContext("call_ha_api_impl", correlation_id, endpoint=endpoint, method=method):
            if not _check_rate_limit(correlation_id):
                return create_error_response(
                    f'Rate limit exceeded: {HA_RATE_LIMIT_PER_SECOND} req/s',
                    'RATE_LIMIT_EXCEEDED'
                )
            
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
            
            # Circuit breaker protection
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
            
            if duration_ms > HA_SLOW_OPERATION_THRESHOLD_MS:
                _SLOW_OPERATIONS[f'call_ha_api_{endpoint}'] += 1
                log_warning(f"Slow API call: {endpoint} took {duration_ms:.2f}ms")
            
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
    'call_ha_api_impl',
    'get_ha_config_impl',
    'get_rate_limit_stats',
    '_extract_entity_list',
    '_trace_step',
    '_is_debug_mode',
    '_calculate_percentiles',
    '_generate_performance_recommendations',
    'DebugContext',
    'HA_CACHE_TTL_ENTITIES',
    'HA_CACHE_TTL_STATE',
    'HA_CACHE_TTL_CONFIG',
    'HA_CACHE_TTL_FUZZY_MATCH',
    'HA_CIRCUIT_BREAKER_NAME',
    'HA_SLOW_OPERATION_THRESHOLD_MS',
    'HA_CACHE_WARMING_ENABLED',
    '_SLOW_OPERATIONS',
]

# EOF
