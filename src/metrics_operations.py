"""
metrics_operations.py - Gateway implementation functions for metrics
Version: 2025.10.21.01
Description: SINGLETON registration + parameter fixes

CHANGELOG:
- 2025.10.21.01: CRITICAL FIX - SINGLETON Interface Registration
  - ADDED: get_metrics_manager() function for proper singleton management
  - CHANGED: _MANAGER now uses SINGLETON interface (INT-06)
  - COMPLIANCE: Enables memory tracking and LUGS lifecycle management
  - REF: Finding 2.1 (Register with SINGLETON interface)
  
- 2025.10.20.03: BUG FIX - Parameter name mismatch
  - FIXED: _execute_record_cache_metric_implementation() signature
  - Changed: operation: str → operation_name: str
  - Reason: Gateway wrapper sends operation_name, not operation
  - This fixes CloudWatch error: "missing 1 required positional argument: 'operation'"

Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Dict, Any, Optional

from metrics_types import MetricOperation, ResponseType

# CIRCULAR IMPORT FIX: Do NOT import _MANAGER at module level
# Import it inside each function instead to avoid:
# interface_metrics → metrics_operations → metrics_core → metrics_operations


# ===== SINGLETON MANAGEMENT =====

def get_metrics_manager():
    """
    Get MetricsCore singleton instance via SINGLETON interface.
    
    This ensures:
    1. Proper registration with SINGLETON interface (INT-06)
    2. Memory tracking by singleton_core
    3. LUGS lifecycle management capability
    4. Consistent with other core managers (cache_core, logging_core, etc.)
    
    REF: Finding 2.1 (Register with SINGLETON interface)
    REF: INT-06 (SINGLETON Interface)
    REF: ARCH-07 (LMMS - Memory management)
    
    Returns:
        MetricsCore singleton instance
    """
    try:
        # Try to get from SINGLETON interface first
        from gateway_core import execute_operation, GatewayInterface
        manager = execute_operation(GatewayInterface.SINGLETON, 'get', key='metrics_core_manager')
        
        if manager is not None:
            return manager
        
        # Not registered yet - create and register
        from metrics_core import MetricsCore
        manager = MetricsCore()
        
        # Register with SINGLETON interface for memory tracking
        execute_operation(
            GatewayInterface.SINGLETON,
            'set',
            key='metrics_core_manager',
            value=manager
        )
        
        return manager
        
    except ImportError:
        # Fallback if gateway not available (initialization phase)
        from metrics_core import MetricsCore
        return MetricsCore()


# ===== GATEWAY IMPLEMENTATION FUNCTIONS =====

def _execute_record_metric_implementation(name: str, value: float, dimensions: Optional[Dict[str, str]] = None, **kwargs) -> bool:
    """Execute record metric operation."""
    manager = get_metrics_manager()
    return manager.execute_metric_operation(MetricOperation.RECORD, name, value, dimensions)


def _execute_increment_counter_implementation(name: str, value: int = 1, **kwargs) -> int:
    """Execute increment counter operation."""
    manager = get_metrics_manager()
    return manager.execute_metric_operation(MetricOperation.INCREMENT, name, value)


def _execute_get_stats_implementation(**kwargs) -> Dict[str, Any]:
    """Execute get stats operation."""
    manager = get_metrics_manager()
    return manager.execute_metric_operation(MetricOperation.GET_STATS)


def _execute_record_operation_metric_implementation(operation_name: str, success: bool = True, duration_ms: float = 0, error_type: Optional[str] = None, **kwargs) -> bool:
    """
    Execute record operation metric.
    
    FIXED 2025.10.20.03: Changed parameter from 'operation' to 'operation_name'
    to match gateway wrapper signature and avoid parameter conflicts.
    """
    manager = get_metrics_manager()
    dimensions = {'operation': operation_name, 'success': str(success)}
    if error_type:
        dimensions['error_type'] = error_type
    manager.record_metric(f'operation.{operation_name}.count', 1.0, dimensions)
    if duration_ms > 0:
        manager.record_metric(f'operation.{operation_name}.duration_ms', duration_ms, dimensions)
    return True


def _execute_record_error_response_metric_implementation(error_type: str, severity: str = 'medium', category: str = 'internal', context: Optional[Dict] = None, **kwargs) -> bool:
    """Execute record error response metric."""
    manager = get_metrics_manager()
    dimensions = {'error_type': error_type, 'severity': severity, 'category': category}
    manager.record_metric('error.response.count', 1.0, dimensions)
    return True


def _execute_record_cache_metric_implementation(operation_name: str, hit: bool = False, miss: bool = False, eviction: bool = False, duration_ms: float = 0, **kwargs) -> bool:
    """
    Execute record cache metric.
    
    FIXED 2025.10.20.03: Changed parameter from 'operation' to 'operation_name'
    to match gateway wrapper signature and avoid parameter conflicts.
    
    Args:
        operation_name: Name of cache operation (e.g., 'get', 'set')
        hit: Whether operation resulted in cache hit
        miss: Whether operation resulted in cache miss
        eviction: Whether operation caused eviction
        duration_ms: Operation duration in milliseconds
        **kwargs: Additional parameters (ignored)
        
    Returns:
        True if metric recorded successfully
    """
    manager = get_metrics_manager()
    dimensions = {'operation': operation_name}
    if hit:
        dimensions['result'] = 'hit'
        manager.record_metric('cache.hit', 1.0, dimensions)
    if miss:
        dimensions['result'] = 'miss'
        manager.record_metric('cache.miss', 1.0, dimensions)
    if eviction:
        manager.record_metric('cache.eviction', 1.0, dimensions)
    if duration_ms > 0:
        manager.record_metric('cache.duration_ms', duration_ms, dimensions)
    return True


def _execute_record_api_metric_implementation(api: str, method: str = 'GET', status_code: int = 200, duration_ms: float = 0, **kwargs) -> bool:
    """Execute record API metric."""
    manager = get_metrics_manager()
    dimensions = {'api': api, 'method': method, 'status': str(status_code)}
    manager.record_metric('api.request', 1.0, dimensions)
    if duration_ms > 0:
        manager.record_metric('api.duration_ms', duration_ms, dimensions)
    return True


def _execute_record_response_metric_implementation(response_type: ResponseType, status_code: int, duration_ms: float = 0, **kwargs) -> bool:
    """Execute record response metric."""
    manager = get_metrics_manager()
    manager.record_response_metric(response_type, status_code, duration_ms)
    return True


def _execute_record_http_metric_implementation(method: str, url: str, status_code: int, duration_ms: float, response_size: Optional[int] = None, **kwargs) -> bool:
    """Execute record HTTP metric."""
    manager = get_metrics_manager()
    manager.record_http_metric(method, url, status_code, duration_ms, response_size)
    return True


def _execute_record_circuit_breaker_metric_implementation(circuit_name: str, event_type: str, success: bool = True, **kwargs) -> bool:
    """Execute record circuit breaker metric."""
    manager = get_metrics_manager()
    manager.record_circuit_breaker_event(circuit_name, event_type, success)
    return True


def _execute_get_response_metrics_implementation(**kwargs) -> Dict[str, Any]:
    """Execute get response metrics operation."""
    manager = get_metrics_manager()
    return manager.get_response_metrics()


def _execute_get_http_metrics_implementation(**kwargs) -> Dict[str, Any]:
    """Execute get HTTP metrics operation."""
    manager = get_metrics_manager()
    return manager.get_http_metrics()


def _execute_get_circuit_breaker_metrics_implementation(circuit_name: Optional[str] = None, **kwargs) -> Dict[str, Any]:
    """Execute get circuit breaker metrics operation."""
    manager = get_metrics_manager()
    return manager.get_circuit_breaker_metrics(circuit_name)


def _execute_record_dispatcher_timing_implementation(interface_name: str, operation_name: str, duration_ms: float, **kwargs) -> bool:
    """Execute record dispatcher timing operation."""
    manager = get_metrics_manager()
    return manager.record_dispatcher_timing(interface_name, operation_name, duration_ms)


def _execute_get_dispatcher_stats_implementation(**kwargs) -> Dict[str, Any]:
    """Execute get dispatcher stats operation."""
    manager = get_metrics_manager()
    return manager.get_dispatcher_stats()


def _execute_get_operation_metrics_implementation(**kwargs) -> Dict[str, Any]:
    """Execute get operation metrics operation."""
    manager = get_metrics_manager()
    return manager.get_operation_metrics()


def _execute_reset_metrics_implementation(**kwargs) -> bool:
    """
    Execute reset metrics operation (testing/debug only).
    
    REF: Finding 7.5 (Debug reset operation)
    """
    manager = get_metrics_manager()
    return manager.reset_metrics()


# ===== HELPER FUNCTIONS =====

def execute_metrics_operation(operation: MetricOperation, **kwargs) -> Any:
    """Execute metrics operation via MetricsCore."""
    manager = get_metrics_manager()
    return manager.execute_metric_operation(operation, **kwargs)


def get_metrics_summary() -> Dict[str, Any]:
    """Get comprehensive metrics summary."""
    manager = get_metrics_manager()
    return {
        'stats': manager.get_stats(),
        'response_metrics': manager.get_response_metrics(),
        'http_metrics': manager.get_http_metrics(),
        'circuit_breaker_metrics': manager.get_circuit_breaker_metrics(),
        'dispatcher_stats': manager.get_dispatcher_stats()
    }


__all__ = [
    'get_metrics_manager',
    '_execute_record_metric_implementation',
    '_execute_increment_counter_implementation',
    '_execute_get_stats_implementation',
    '_execute_record_operation_metric_implementation',
    '_execute_record_error_response_metric_implementation',
    '_execute_record_cache_metric_implementation',
    '_execute_record_api_metric_implementation',
    '_execute_record_response_metric_implementation',
    '_execute_record_http_metric_implementation',
    '_execute_record_circuit_breaker_metric_implementation',
    '_execute_get_response_metrics_implementation',
    '_execute_get_http_metrics_implementation',
    '_execute_get_circuit_breaker_metrics_implementation',
    '_execute_record_dispatcher_timing_implementation',
    '_execute_get_dispatcher_stats_implementation',
    '_execute_get_operation_metrics_implementation',
    '_execute_reset_metrics_implementation',
    'execute_metrics_operation',
    'get_metrics_summary',
]

# EOF
