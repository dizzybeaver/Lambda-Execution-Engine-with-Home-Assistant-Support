"""
aws/metrics_operations.py - Gateway implementation functions for metrics
Version: 2025.10.14.04
Description: Gateway-compatible implementation functions for metrics operations

Copyright 2025 Joseph Hersey

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

from typing import Dict, Any, Optional

from metrics_core import _MANAGER
from metrics_types import MetricOperation, ResponseType


# ===== GATEWAY IMPLEMENTATION FUNCTIONS =====

def _execute_record_metric_implementation(name: str, value: float, dimensions: Optional[Dict[str, str]] = None, **kwargs) -> bool:
    """Execute record metric operation."""
    return _MANAGER.execute_metric_operation(MetricOperation.RECORD, name, value, dimensions)


def _execute_increment_counter_implementation(name: str, value: int = 1, **kwargs) -> int:
    """Execute increment counter operation."""
    return _MANAGER.execute_metric_operation(MetricOperation.INCREMENT, name, value)


def _execute_get_stats_implementation(**kwargs) -> Dict[str, Any]:
    """Execute get stats operation."""
    return _MANAGER.execute_metric_operation(MetricOperation.GET_STATS)


def _execute_record_operation_metric_implementation(operation: str, success: bool = True, duration_ms: float = 0, error_type: Optional[str] = None, **kwargs) -> bool:
    """Execute record operation metric."""
    dimensions = {'operation': operation, 'success': str(success)}
    if error_type:
        dimensions['error_type'] = error_type
    _MANAGER.record_metric(f'operation.{operation}.count', 1.0, dimensions)
    if duration_ms > 0:
        _MANAGER.record_metric(f'operation.{operation}.duration_ms', duration_ms, dimensions)
    return True


def _execute_record_error_response_metric_implementation(error_type: str, severity: str = 'medium', category: str = 'internal', context: Optional[Dict] = None, **kwargs) -> bool:
    """Execute record error response metric."""
    dimensions = {'error_type': error_type, 'severity': severity, 'category': category}
    _MANAGER.record_metric('error.response.count', 1.0, dimensions)
    return True


def _execute_record_cache_metric_implementation(operation: str, hit: bool = False, miss: bool = False, eviction: bool = False, duration_ms: float = 0, **kwargs) -> bool:
    """Execute record cache metric."""
    dimensions = {'operation': operation}
    if hit:
        _MANAGER.record_metric('cache.hit', 1.0, dimensions)
    if miss:
        _MANAGER.record_metric('cache.miss', 1.0, dimensions)
    if eviction:
        _MANAGER.record_metric('cache.eviction', 1.0, dimensions)
    if duration_ms > 0:
        _MANAGER.record_metric('cache.operation.duration_ms', duration_ms, dimensions)
    return True


def _execute_record_api_metric_implementation(endpoint: str, method: str, status_code: int, duration_ms: float, success: bool = True, **kwargs) -> bool:
    """Execute record API metric."""
    dimensions = {'endpoint': endpoint, 'method': method, 'status_code': str(status_code), 'success': str(success)}
    _MANAGER.record_metric('api.request.count', 1.0, dimensions)
    _MANAGER.record_metric('api.request.duration_ms', duration_ms, dimensions)
    _MANAGER.record_metric(f'api.status.{status_code}', 1.0, dimensions)
    return True


def _execute_record_response_metric_implementation(response_type: str, response_time_ms: float = 0.0, **kwargs) -> None:
    """Execute record response metric."""
    try:
        response_type_enum = ResponseType(response_type)
        _MANAGER.record_response_metric(response_type_enum, response_time_ms)
    except ValueError:
        pass


def _execute_record_http_metric_implementation(success: bool, response_time_ms: float = 0.0, method: Optional[str] = None, status_code: Optional[int] = None, **kwargs) -> None:
    """Execute record HTTP metric."""
    _MANAGER.record_http_request(success, response_time_ms, method, status_code)


def _execute_record_circuit_breaker_metric_implementation(circuit_name: str, event_type: str, success: Optional[bool] = None, **kwargs) -> None:
    """Execute record circuit breaker metric."""
    _MANAGER.record_circuit_breaker_event(circuit_name, event_type, success)


def _execute_get_response_metrics_implementation(**kwargs) -> Dict[str, Any]:
    """Execute get response metrics operation."""
    return _MANAGER.get_response_metrics()


def _execute_get_http_metrics_implementation(**kwargs) -> Dict[str, Any]:
    """Execute get HTTP metrics operation."""
    return _MANAGER.get_http_metrics()


def _execute_get_circuit_breaker_metrics_implementation(circuit_name: Optional[str] = None, **kwargs) -> Dict[str, Any]:
    """Execute get circuit breaker metrics operation."""
    return _MANAGER.get_circuit_breaker_metrics(circuit_name)


def _execute_record_dispatcher_timing_implementation(interface_name: str, operation_name: str, duration_ms: float, **kwargs) -> bool:
    """Execute record dispatcher timing operation."""
    return _MANAGER.record_dispatcher_timing(interface_name, operation_name, duration_ms)


def _execute_get_dispatcher_stats_implementation(**kwargs) -> Dict[str, Any]:
    """Execute get dispatcher stats operation."""
    return _MANAGER.get_dispatcher_stats()


def _execute_get_operation_metrics_implementation(**kwargs) -> Dict[str, Any]:
    """Execute get operation metrics operation."""
    return _MANAGER.get_operation_metrics()


# ===== HELPER FUNCTIONS =====

def execute_metrics_operation(operation: MetricOperation, **kwargs) -> Any:
    """Execute metrics operation via MetricsCore."""
    return _MANAGER.execute_metric_operation(operation, **kwargs)


def get_metrics_summary() -> Dict[str, Any]:
    """Get comprehensive metrics summary."""
    return {
        'stats': _MANAGER.get_stats(),
        'response_metrics': _MANAGER.get_response_metrics(),
        'http_metrics': _MANAGER.get_http_metrics(),
        'circuit_breaker_metrics': _MANAGER.get_circuit_breaker_metrics(),
        'dispatcher_stats': _MANAGER.get_dispatcher_stats()
    }


__all__ = [
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
    'execute_metrics_operation',
    'get_metrics_summary',
]

# EOF
