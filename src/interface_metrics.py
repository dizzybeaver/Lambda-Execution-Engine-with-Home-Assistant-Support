"""
interface_metrics.py - Metrics Interface Router (SUGA-ISP Architecture)
Version: 2025.10.21.01
Description: PHASE 2 TASK 2.4 - Use validate_required_param() helper to eliminate validation duplication

CHANGELOG:
- 2025.10.21.01: PHASE 2 TASK 2.4 - Genericize validation pattern
  - Updated 7 validation functions to use validate_required_param() helper
  - Eliminated ~70 LOC of duplicated validation logic
  - Functions simplified:
    * _validate_metric_name_param
    * _validate_record_metric_params
    * _validate_operation_param
    * _validate_error_type_param
    * _validate_api_param
    * _validate_http_metric_params
    * _validate_circuit_breaker_params
    * _validate_dispatcher_timing_params

- 2025.10.20.02: CRITICAL FIX - Renamed 'operation' to 'operation_name' in validation function
  - Fixed _validate_operation_param() to expect 'operation_name' instead of 'operation'
  - Resolves RuntimeError: "got multiple values for argument 'operation'"
  - Matches gateway_wrappers.py and interface_logging.py parameter rename

Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any, Callable, Dict

from metrics_helper import validate_required_param

# ===== IMPORT PROTECTION =====

try:
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
    _METRICS_AVAILABLE = True
    _METRICS_IMPORT_ERROR = None
except ImportError as e:
    _METRICS_AVAILABLE = False
    _METRICS_IMPORT_ERROR = str(e)
    # Stub all implementations
    _execute_record_metric_implementation = None
    _execute_increment_counter_implementation = None
    _execute_get_stats_implementation = None
    _execute_record_operation_metric_implementation = None
    _execute_record_error_response_metric_implementation = None
    _execute_record_cache_metric_implementation = None
    _execute_record_api_metric_implementation = None
    _execute_record_response_metric_implementation = None
    _execute_record_http_metric_implementation = None
    _execute_record_circuit_breaker_metric_implementation = None
    _execute_get_response_metrics_implementation = None
    _execute_get_http_metrics_implementation = None
    _execute_get_circuit_breaker_metrics_implementation = None
    _execute_record_dispatcher_timing_implementation = None
    _execute_get_dispatcher_stats_implementation = None
    _execute_get_operation_metrics_implementation = None


# ===== VALIDATION HELPERS =====

def _validate_metric_name_param(kwargs: Dict[str, Any], operation: str) -> None:
    """Validate name parameter for metric operations."""
    validate_required_param(
        kwargs, 'name', str, operation,
        validator=lambda v: bool(v.strip()),
        error_message=f"Metrics operation '{operation}' parameter 'name' cannot be empty"
    )


def _validate_record_metric_params(kwargs: Dict[str, Any], operation: str) -> None:
    """Validate parameters for record metric operation."""
    _validate_metric_name_param(kwargs, operation)
    validate_required_param(kwargs, 'value', (int, float), operation)


def _validate_operation_param(kwargs: Dict[str, Any], operation: str) -> None:
    """Validate operation_name parameter."""
    validate_required_param(
        kwargs, 'operation_name', str, operation,
        validator=lambda v: bool(v.strip()),
        error_message=f"Metrics operation '{operation}' parameter 'operation_name' must be non-empty string"
    )


def _validate_error_type_param(kwargs: Dict[str, Any], operation: str) -> None:
    """Validate error_type parameter."""
    validate_required_param(kwargs, 'error_type', None, operation)


def _validate_api_param(kwargs: Dict[str, Any], operation: str) -> None:
    """Validate API parameter."""
    validate_required_param(kwargs, 'endpoint', None, operation)


def _validate_http_metric_params(kwargs: Dict[str, Any], operation: str) -> None:
    """Validate HTTP metric parameters."""
    for param in ['method', 'url', 'status_code']:
        validate_required_param(kwargs, param, None, operation)


def _validate_circuit_breaker_params(kwargs: Dict[str, Any], operation: str) -> None:
    """Validate circuit breaker metric parameters."""
    validate_required_param(kwargs, 'circuit_name', None, operation)
    validate_required_param(kwargs, 'event_type', None, operation)


def _validate_dispatcher_timing_params(kwargs: Dict[str, Any], operation: str) -> None:
    """Validate dispatcher timing parameters."""
    for param in ['interface_name', 'operation_name', 'duration_ms']:
        validate_required_param(kwargs, param, None, operation)


# ===== OPERATION DISPATCH =====

def _build_dispatch_dict() -> Dict[str, Callable]:
    """Build dispatch dictionary for metrics operations. Only called if metrics available."""
    return {
        # Record metric with aliases
        'record': lambda **kwargs: (
            _validate_record_metric_params(kwargs, 'record'),
            _execute_record_metric_implementation(**kwargs)
        )[1],
        'record_metric': lambda **kwargs: (
            _validate_record_metric_params(kwargs, 'record_metric'),
            _execute_record_metric_implementation(**kwargs)
        )[1],
        
        # Increment counter with aliases
        'increment': lambda **kwargs: (
            _validate_metric_name_param(kwargs, 'increment'),
            _execute_increment_counter_implementation(**kwargs)
        )[1],
        'increment_counter': lambda **kwargs: (
            _validate_metric_name_param(kwargs, 'increment_counter'),
            _execute_increment_counter_implementation(**kwargs)
        )[1],
        
        # Stats operations
        'get_stats': _execute_get_stats_implementation,
        
        # Record operation metric with aliases
        'record_operation': lambda **kwargs: (
            _validate_operation_param(kwargs, 'record_operation'),
            _execute_record_operation_metric_implementation(**kwargs)
        )[1],
        'record_operation_metric': lambda **kwargs: (
            _validate_operation_param(kwargs, 'record_operation_metric'),
            _execute_record_operation_metric_implementation(**kwargs)
        )[1],
        
        # Record error metric with aliases
        'record_error': lambda **kwargs: (
            _validate_error_type_param(kwargs, 'record_error'),
            _execute_record_error_response_metric_implementation(**kwargs)
        )[1],
        'record_error_metric': lambda **kwargs: (
            _validate_error_type_param(kwargs, 'record_error_metric'),
            _execute_record_error_response_metric_implementation(**kwargs)
        )[1],
        
        # Record cache metric with aliases
        'record_cache': lambda **kwargs: (
            _validate_operation_param(kwargs, 'record_cache'),
            _execute_record_cache_metric_implementation(**kwargs)
        )[1],
        'record_cache_metric': lambda **kwargs: (
            _validate_operation_param(kwargs, 'record_cache_metric'),
            _execute_record_cache_metric_implementation(**kwargs)
        )[1],
        
        # Record API metric with aliases
        'record_api': lambda **kwargs: (
            _validate_api_param(kwargs, 'record_api'),
            _execute_record_api_metric_implementation(**kwargs)
        )[1],
        'record_api_metric': lambda **kwargs: (
            _validate_api_param(kwargs, 'record_api_metric'),
            _execute_record_api_metric_implementation(**kwargs)
        )[1],
        
        # Record response metric with aliases
        'record_response': _execute_record_response_metric_implementation,
        'record_response_metric': _execute_record_response_metric_implementation,
        
        # Record HTTP metric with aliases
        'record_http': lambda **kwargs: (
            _validate_http_metric_params(kwargs, 'record_http'),
            _execute_record_http_metric_implementation(**kwargs)
        )[1],
        'record_http_metric': lambda **kwargs: (
            _validate_http_metric_params(kwargs, 'record_http_metric'),
            _execute_record_http_metric_implementation(**kwargs)
        )[1],
        
        # Record circuit breaker metric with aliases
        'record_circuit_breaker': lambda **kwargs: (
            _validate_circuit_breaker_params(kwargs, 'record_circuit_breaker'),
            _execute_record_circuit_breaker_metric_implementation(**kwargs)
        )[1],
        'record_circuit_breaker_metric': lambda **kwargs: (
            _validate_circuit_breaker_params(kwargs, 'record_circuit_breaker_metric'),
            _execute_record_circuit_breaker_metric_implementation(**kwargs)
        )[1],
        
        # Get metrics operations
        'get_response_metrics': _execute_get_response_metrics_implementation,
        'get_http_metrics': _execute_get_http_metrics_implementation,
        'get_circuit_breaker_metrics': _execute_get_circuit_breaker_metrics_implementation,
        
        # Dispatcher timing with alias
        'record_dispatcher_timing': lambda **kwargs: (
            _validate_dispatcher_timing_params(kwargs, 'record_dispatcher_timing'),
            _execute_record_dispatcher_timing_implementation(**kwargs)
        )[1],
        
        # Get dispatcher stats with alias
        'get_dispatcher_stats': _execute_get_dispatcher_stats_implementation,
        'get_dispatcher_metrics': _execute_get_dispatcher_stats_implementation,
        
        # Get operation metrics
        'get_operation_metrics': _execute_get_operation_metrics_implementation,
    }

_OPERATION_DISPATCH = _build_dispatch_dict() if _METRICS_AVAILABLE else {}


# ===== MAIN ROUTER FUNCTION =====

def execute_metrics_operation(operation: str, **kwargs) -> Any:
    """
    Route metrics operation requests using dispatch dictionary pattern.
    
    Args:
        operation: The metrics operation to execute
        **kwargs: Operation-specific parameters
        
    Returns:
        Operation result from internal implementation
        
    Raises:
        RuntimeError: If Metrics interface unavailable
        ValueError: If operation is unknown or required parameters are missing/invalid
    """
    # Check Metrics availability
    if not _METRICS_AVAILABLE:
        raise RuntimeError(
            f"Metrics interface unavailable: {_METRICS_IMPORT_ERROR}. "
            "This may indicate missing metrics_operations module or circular import."
        )
    
    # Validate operation exists
    if operation not in _OPERATION_DISPATCH:
        raise ValueError(
            f"Unknown metrics operation: '{operation}'. "
            f"Valid operations: {', '.join(_OPERATION_DISPATCH.keys())}"
        )
    
    # Dispatch using dictionary lookup (O(1))
    return _OPERATION_DISPATCH[operation](**kwargs)


__all__ = ['execute_metrics_operation']

# EOF
