"""
gateway/wrappers/gateway_wrappers_metrics.py

Version: 2025-12-11_1
Purpose: METRICS interface gateway wrappers
Project: LEE
License: Apache 2.0
"""

from typing import Any, Dict, Optional
from gateway_core import GatewayInterface, execute_operation


def record_metric(name: str, value: float, dimensions: Optional[Dict[str, str]] = None, **kwargs) -> bool:
    """Record metric value."""
    return execute_operation(GatewayInterface.METRICS, 'record', name=name, value=value, dimensions=dimensions, **kwargs)


def increment_counter(name: str, value: int = 1, **kwargs) -> int:
    """Increment counter."""
    return execute_operation(GatewayInterface.METRICS, 'increment', name=name, value=value, **kwargs)


def get_metrics_stats(**kwargs) -> Dict[str, Any]:
    """Get metrics statistics."""
    return execute_operation(GatewayInterface.METRICS, 'get_stats', **kwargs)


def record_operation_metric(operation_name: str, success: bool = True, duration_ms: float = 0, error_type: Optional[str] = None, **kwargs) -> bool:
    """Record operation metric."""
    return execute_operation(GatewayInterface.METRICS, 'record_operation', operation_name=operation_name, success=success, duration_ms=duration_ms, error_type=error_type, **kwargs)


def record_error_metric(error_type: str, severity: str = 'medium', category: str = 'internal', **kwargs) -> bool:
    """Record error metric."""
    return execute_operation(GatewayInterface.METRICS, 'record_error', error_type=error_type, severity=severity, category=category, **kwargs)


def record_cache_metric(operation_name: str, hit: bool = False, miss: bool = False, duration_ms: float = 0, **kwargs) -> bool:
    """Record cache metric."""
    return execute_operation(GatewayInterface.METRICS, 'record_cache', operation_name=operation_name, hit=hit, miss=miss, duration_ms=duration_ms, **kwargs)


def record_api_metric(api_name: str, endpoint: str, success: bool = True, duration_ms: float = 0, status_code: Optional[int] = None, **kwargs) -> bool:
    """Record API metric."""
    return execute_operation(GatewayInterface.METRICS, 'record_api', api_name=api_name, endpoint=endpoint, success=success, duration_ms=duration_ms, status_code=status_code, **kwargs)


def record_response_metric(response_type: str, success: bool = True, error_type: Optional[str] = None, **kwargs) -> bool:
    """Record response metric."""
    return execute_operation(GatewayInterface.METRICS, 'record_response', response_type=response_type, success=success, error_type=error_type, **kwargs)


def record_http_metric(method: str, url: str, status_code: int, duration_ms: float, response_size: int = 0, **kwargs) -> bool:
    """Record HTTP metric."""
    return execute_operation(GatewayInterface.METRICS, 'record_http', method=method, url=url, status_code=status_code, duration_ms=duration_ms, response_size=response_size, **kwargs)


def record_circuit_breaker_metric(circuit_name: str, event_type: str, success: bool = True, **kwargs) -> bool:
    """Record circuit breaker metric."""
    return execute_operation(GatewayInterface.METRICS, 'record_circuit_breaker', circuit_name=circuit_name, event_type=event_type, success=success, **kwargs)


def get_response_metrics(**kwargs) -> Dict[str, Any]:
    """Get response metrics."""
    return execute_operation(GatewayInterface.METRICS, 'get_response_metrics', **kwargs)


def get_http_metrics(**kwargs) -> Dict[str, Any]:
    """Get HTTP metrics."""
    return execute_operation(GatewayInterface.METRICS, 'get_http_metrics', **kwargs)


def get_circuit_breaker_metrics(circuit_name: Optional[str] = None, **kwargs) -> Dict[str, Any]:
    """Get circuit breaker metrics."""
    return execute_operation(GatewayInterface.METRICS, 'get_circuit_breaker_metrics', circuit_name=circuit_name, **kwargs)


def record_dispatcher_timing(interface_name: str, operation_name: str, duration_ms: float, **kwargs) -> bool:
    """Record dispatcher timing."""
    return execute_operation(GatewayInterface.METRICS, 'record_dispatcher_timing', interface_name=interface_name, operation_name=operation_name, duration_ms=duration_ms, **kwargs)


def get_dispatcher_stats(**kwargs) -> Dict[str, Any]:
    """Get dispatcher stats."""
    return execute_operation(GatewayInterface.METRICS, 'get_dispatcher_stats', **kwargs)


def get_operation_metrics(**kwargs) -> Dict[str, Any]:
    """Get operation metrics."""
    return execute_operation(GatewayInterface.METRICS, 'get_operation_metrics', **kwargs)


def get_performance_report(slow_threshold_ms: float = 100.0, **kwargs) -> Dict[str, Any]:
    """Get comprehensive performance report."""
    return execute_operation(GatewayInterface.METRICS, 'get_performance_report', slow_threshold_ms=slow_threshold_ms, **kwargs)


def reset_metrics(**kwargs) -> bool:
    """Reset all metrics."""
    return execute_operation(GatewayInterface.METRICS, 'reset', **kwargs)


__all__ = [
    'record_metric',
    'increment_counter',
    'get_metrics_stats',
    'record_operation_metric',
    'record_error_metric',
    'record_cache_metric',
    'record_api_metric',
    'record_response_metric',
    'record_http_metric',
    'record_circuit_breaker_metric',
    'get_response_metrics',
    'get_http_metrics',
    'get_circuit_breaker_metrics',
    'record_dispatcher_timing',
    'get_dispatcher_stats',
    'get_operation_metrics',
    'get_performance_report',
    'reset_metrics',
]
