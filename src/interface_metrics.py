"""
interface_metrics.py - Metrics Interface Router (SUGA-ISP Architecture)
Version: 2025.10.17.05
Description: Firewall router for Metrics interface with parameter validation

CHANGELOG:
- 2025.10.17.05: Added parameter validation for all operations (Issue #18 fix)
  - Validates 'name' parameter for metric operations
  - Validates 'value' parameter for record operations
  - Type checking for name (string) and value (numeric)
  - Clear error messages for missing/invalid parameters
- 2025.10.16.01: Fixed missing operation handlers and imports
- 2025.10.15.01: Initial SUGA-ISP router implementation

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

from typing import Any

from metrics_operations import (
    _execute_record_metric_implementation,
    _execute_increment_counter_implementation,
    _execute_get_stats_implementation,
    _execute_record_operation_metric_implementation,
    _execute_record_error_response_metric_implementation,
    _execute_record_cache_metric_implementation,
    _execute_record_api_metric_implementation,
    _execute_record_response_metric_implementation,
    _execute_record_http_metric_implementation,
    _execute_record_circuit_breaker_metric_implementation,
    _execute_get_response_metrics_implementation,
    _execute_get_http_metrics_implementation,
    _execute_get_circuit_breaker_metrics_implementation,
    _execute_record_dispatcher_timing_implementation,
    _execute_get_dispatcher_stats_implementation,
    _execute_get_operation_metrics_implementation
)


_VALID_METRICS_OPERATIONS = [
    'record', 'record_metric', 'increment', 'increment_counter', 'get_stats',
    'record_operation', 'record_error', 'record_cache', 'record_api',
    'record_response', 'record_http', 'record_circuit_breaker',
    'get_response_metrics', 'get_http_metrics', 'get_circuit_breaker_metrics',
    'record_dispatcher_timing', 'get_dispatcher_stats', 'get_operation_metrics'
]


def execute_metrics_operation(operation: str, **kwargs) -> Any:
    """
    Route metrics operation requests to internal implementations with parameter validation.
    This is called by the SUGA-ISP (gateway.py).
    
    Args:
        operation: The metrics operation to execute
        **kwargs: Operation-specific parameters
        
    Returns:
        Operation result from internal implementation
        
    Raises:
        ValueError: If operation is unknown or required parameters are missing/invalid
    """
    
    if operation == 'record' or operation == 'record_metric':
        _validate_record_metric_params(kwargs, operation)
        return _execute_record_metric_implementation(**kwargs)
    
    elif operation == 'increment' or operation == 'increment_counter':
        _validate_metric_name_param(kwargs, operation)
        return _execute_increment_counter_implementation(**kwargs)
    
    elif operation == 'get_stats':
        return _execute_get_stats_implementation(**kwargs)
    
    elif operation == 'record_operation' or operation == 'record_operation_metric':
        _validate_operation_param(kwargs, operation)
        return _execute_record_operation_metric_implementation(**kwargs)
    
    elif operation == 'record_error' or operation == 'record_error_metric':
        _validate_error_type_param(kwargs, operation)
        return _execute_record_error_response_metric_implementation(**kwargs)
    
    elif operation == 'record_cache' or operation == 'record_cache_metric':
        _validate_operation_param(kwargs, operation)
        return _execute_record_cache_metric_implementation(**kwargs)
    
    elif operation == 'record_api' or operation == 'record_api_metric':
        _validate_api_param(kwargs, operation)
        return _execute_record_api_metric_implementation(**kwargs)
    
    elif operation == 'record_response' or operation == 'record_response_metric':
        return _execute_record_response_metric_implementation(**kwargs)
    
    elif operation == 'record_http' or operation == 'record_http_metric':
        _validate_http_metric_params(kwargs, operation)
        return _execute_record_http_metric_implementation(**kwargs)
    
    elif operation == 'record_circuit_breaker' or operation == 'record_circuit_breaker_metric':
        _validate_circuit_breaker_params(kwargs, operation)
        return _execute_record_circuit_breaker_metric_implementation(**kwargs)
    
    elif operation == 'get_response_metrics':
        return _execute_get_response_metrics_implementation(**kwargs)
    
    elif operation == 'get_http_metrics':
        return _execute_get_http_metrics_implementation(**kwargs)
    
    elif operation == 'get_circuit_breaker_metrics':
        return _execute_get_circuit_breaker_metrics_implementation(**kwargs)
    
    elif operation == 'record_dispatcher_timing':
        _validate_dispatcher_timing_params(kwargs, operation)
        return _execute_record_dispatcher_timing_implementation(**kwargs)
    
    elif operation == 'get_dispatcher_stats' or operation == 'get_dispatcher_metrics':
        return _execute_get_dispatcher_stats_implementation(**kwargs)
    
    elif operation == 'get_operation_metrics':
        return _execute_get_operation_metrics_implementation(**kwargs)
    
    else:
        raise ValueError(
            f"Unknown metrics operation: '{operation}'. "
            f"Valid operations: {', '.join(_VALID_METRICS_OPERATIONS)}"
        )


def _validate_metric_name_param(kwargs: dict, operation: str) -> None:
    """Validate name parameter for metric operations."""
    if 'name' not in kwargs:
        raise ValueError(f"Metrics operation '{operation}' requires parameter 'name'")
    
    name = kwargs.get('name')
    if not isinstance(name, str):
        raise ValueError(
            f"Metrics operation '{operation}' parameter 'name' must be string, "
            f"got {type(name).__name__}"
        )
    
    if not name.strip():
        raise ValueError(f"Metrics operation '{operation}' parameter 'name' cannot be empty")


def _validate_record_metric_params(kwargs: dict, operation: str) -> None:
    """Validate parameters for record metric operation."""
    _validate_metric_name_param(kwargs, operation)
    
    if 'value' not in kwargs:
        raise ValueError(f"Metrics operation '{operation}' requires parameter 'value'")
    
    value = kwargs.get('value')
    if not isinstance(value, (int, float)):
        raise ValueError(
            f"Metrics operation '{operation}' parameter 'value' must be numeric, "
            f"got {type(value).__name__}"
        )


def _validate_operation_param(kwargs: dict, operation: str) -> None:
    """Validate operation parameter."""
    if 'operation' not in kwargs:
        raise ValueError(f"Metrics operation '{operation}' requires parameter 'operation'")
    
    op_value = kwargs.get('operation')
    if not isinstance(op_value, str) or not op_value.strip():
        raise ValueError(
            f"Metrics operation '{operation}' parameter 'operation' must be non-empty string"
        )


def _validate_error_type_param(kwargs: dict, operation: str) -> None:
    """Validate error_type parameter."""
    if 'error_type' not in kwargs:
        raise ValueError(f"Metrics operation '{operation}' requires parameter 'error_type'")
    
    error_type = kwargs.get('error_type')
    if not isinstance(error_type, str) or not error_type.strip():
        raise ValueError(
            f"Metrics operation '{operation}' parameter 'error_type' must be non-empty string"
        )


def _validate_api_param(kwargs: dict, operation: str) -> None:
    """Validate api parameter."""
    if 'api' not in kwargs:
        raise ValueError(f"Metrics operation '{operation}' requires parameter 'api'")
    
    api = kwargs.get('api')
    if not isinstance(api, str) or not api.strip():
        raise ValueError(
            f"Metrics operation '{operation}' parameter 'api' must be non-empty string"
        )


def _validate_http_metric_params(kwargs: dict, operation: str) -> None:
    """Validate parameters for HTTP metric operation."""
    required = ['method', 'url', 'status_code', 'duration_ms']
    missing = [p for p in required if p not in kwargs]
    if missing:
        raise ValueError(
            f"Metrics operation '{operation}' missing required parameters: {', '.join(missing)}"
        )


def _validate_circuit_breaker_params(kwargs: dict, operation: str) -> None:
    """Validate parameters for circuit breaker metric operation."""
    required = ['circuit_name', 'event_type']
    missing = [p for p in required if p not in kwargs]
    if missing:
        raise ValueError(
            f"Metrics operation '{operation}' missing required parameters: {', '.join(missing)}"
        )


def _validate_dispatcher_timing_params(kwargs: dict, operation: str) -> None:
    """Validate parameters for dispatcher timing operation."""
    required = ['interface_name', 'operation_name', 'duration_ms']
    missing = [p for p in required if p not in kwargs]
    if missing:
        raise ValueError(
            f"Metrics operation '{operation}' missing required parameters: {', '.join(missing)}"
        )


__all__ = [
    'execute_metrics_operation'
]

# EOF
