"""
interface_debug.py - Debug Interface Router
Version: 2025.10.17.15
Description: Router/Firewall for debug interface with import protection

Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any, Dict

# Import protection
try:
    from debug_core import generic_debug_operation
    _DEBUG_AVAILABLE = True
    _DEBUG_IMPORT_ERROR = None
except ImportError as e:
    _DEBUG_AVAILABLE = False
    _DEBUG_IMPORT_ERROR = str(e)
    generic_debug_operation = None


_VALID_DEBUG_OPERATIONS = [
    'check_component_health',
    'check_gateway_health',
    'check_http_client_health',
    'diagnose_http_client_performance',
    'diagnose_system_health',
    'run_debug_tests',
    'validate_http_client_configuration',
    'validate_system_architecture',
    'benchmark_http_client_operations',
    'get_system_stats',
    'get_optimization_stats',
    'get_dispatcher_stats',
    'get_operation_metrics',
    'get_gateway_stats',
    'verify_registry_operations',
    'validate_operation_signatures',
    'validate_interface_compliance',
    'check_circular_dependencies',
    'measure_execution_times',
    'run_performance_profile',
    'run_memory_profile',
    'check_memory_usage'
]


def execute_debug_operation(operation: str, **kwargs) -> Any:
    """
    Route debug operations to internal implementation with operation validation.
    
    Args:
        operation: Debug operation to execute
        **kwargs: Operation-specific parameters
        
    Returns:
        Operation result
        
    Raises:
        RuntimeError: If Debug interface unavailable
        ValueError: If operation is unknown
    """
    # Check Debug availability
    if not _DEBUG_AVAILABLE:
        raise RuntimeError(
            f"Debug interface unavailable: {_DEBUG_IMPORT_ERROR}. "
            "This may indicate missing debug_core module or circular import."
        )
    
    if operation not in _VALID_DEBUG_OPERATIONS:
        raise ValueError(
            f"Unknown debug operation: '{operation}'. "
            f"Valid operations: {', '.join(_VALID_DEBUG_OPERATIONS)}"
        )
    
    # Route to generic debug operation handler
    return generic_debug_operation(operation, **kwargs)


__all__ = ['execute_debug_operation']

# EOF
