"""
interface_metrics.py - Metrics interface layer (SUGA compliant)

Version: 2025.11.29.1
Description: PHASE 2 - Rewrite to proper SUGA pattern

Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any, Dict, Optional


def execute_metrics_operation(operation: str, **kwargs) -> Any:
    """
    Execute metrics operation via SUGA pattern.
    
    Pattern: Interface → Core (lazy import)
    
    Args:
        operation: Operation name (string)
        **kwargs: Operation-specific parameters
        
    Returns:
        Operation result
        
    Raises:
        ValueError: Unknown operation
    """
    import metrics_core
    
    # Dispatch dictionary maps operation names to metrics_core public functions
    DISPATCH = {
        'record': metrics_core.record_metric,
        'record_metric': metrics_core.record_metric,
        'increment': metrics_core.increment_counter,
        'increment_counter': metrics_core.increment_counter,
        'get_stats': metrics_core.get_stats,
        'record_operation': metrics_core.record_operation_metric,
        'record_operation_metric': metrics_core.record_operation_metric,
        'record_error': metrics_core.record_error_response,
        'record_error_response': metrics_core.record_error_response,
        'record_cache': metrics_core.record_cache_metric,
        'record_cache_metric': metrics_core.record_cache_metric,
        'record_api': metrics_core.record_api_metric,
        'record_api_metric': metrics_core.record_api_metric,
        'record_response': metrics_core.record_response_metric,
        'record_response_metric': metrics_core.record_response_metric,
        'record_http': metrics_core.record_http_metric,
        'record_http_metric': metrics_core.record_http_metric,
        'record_circuit_breaker': metrics_core.record_circuit_breaker_event,
        'record_circuit_breaker_metric': metrics_core.record_circuit_breaker_event,
        'get_response_metrics': metrics_core.get_response_metrics,
        'get_http_metrics': metrics_core.get_http_metrics,
        'get_circuit_breaker_metrics': metrics_core.get_circuit_breaker_metrics,
        'record_dispatcher_timing': metrics_core.record_dispatcher_timing,
        'get_dispatcher_stats': metrics_core.get_dispatcher_stats,
        'get_dispatcher_metrics': metrics_core.get_dispatcher_stats,
        'get_operation_metrics': metrics_core.get_operation_metrics,
        'get_performance_report': metrics_core.get_performance_report,
        'reset': metrics_core.reset_metrics,
        'reset_metrics': metrics_core.reset_metrics,
    }
    
    # Validate operation
    handler = DISPATCH.get(operation)
    if not handler:
        raise ValueError(
            f"Unknown metrics operation: '{operation}'. "
            f"Valid operations: {', '.join(sorted(set(DISPATCH.keys())))}"
        )
    
    # Execute via metrics_core public API
    return handler(**kwargs)


__all__ = ['execute_metrics_operation']

# EOF
