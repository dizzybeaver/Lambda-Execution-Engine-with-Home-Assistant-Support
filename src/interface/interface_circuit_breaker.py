"""
interface_circuit_breaker.py - Circuit Breaker Interface Router
Version: 2025.10.22.02
Description: Router/Firewall for circuit breaker interface with import protection

Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any, Callable, Dict

# Import protection
try:
    from circuit_breaker_core import (
        get_breaker_implementation,
        execute_with_breaker_implementation,
        get_all_states_implementation,
        reset_all_implementation,
        get_stats_implementation,
        reset_implementation
    )
    _CIRCUIT_BREAKER_AVAILABLE = True
    _CIRCUIT_BREAKER_IMPORT_ERROR = None
except ImportError as e:
    _CIRCUIT_BREAKER_AVAILABLE = False
    _CIRCUIT_BREAKER_IMPORT_ERROR = str(e)
    get_breaker_implementation = None
    execute_with_breaker_implementation = None
    get_all_states_implementation = None
    reset_all_implementation = None
    get_stats_implementation = None
    reset_implementation = None


_VALID_CIRCUIT_BREAKER_OPERATIONS = ['get', 'call', 'get_all_states', 'reset_all', 'get_stats', 'reset']


def execute_circuit_breaker_operation(operation: str, **kwargs) -> Any:
    """
    Route circuit breaker operations to internal implementations with parameter validation.
    
    Args:
        operation: Operation name
        **kwargs: Operation-specific parameters
        
    Returns:
        Operation result
        
    Raises:
        RuntimeError: If Circuit Breaker interface unavailable
        ValueError: If operation is unknown or required parameters are missing/invalid
    """
    # Check Circuit Breaker availability
    if not _CIRCUIT_BREAKER_AVAILABLE:
        raise RuntimeError(
            f"Circuit Breaker interface unavailable: {_CIRCUIT_BREAKER_IMPORT_ERROR}. "
            "This may indicate missing circuit_breaker_core module or circular import."
        )
    
    if operation not in _VALID_CIRCUIT_BREAKER_OPERATIONS:
        raise ValueError(
            f"Unknown circuit breaker operation: '{operation}'. "
            f"Valid operations: {', '.join(_VALID_CIRCUIT_BREAKER_OPERATIONS)}"
        )
    
    if operation == 'get':
        if 'name' not in kwargs:
            raise ValueError("circuit_breaker.get requires 'name' parameter")
        if not isinstance(kwargs['name'], str):
            raise TypeError(f"circuit_breaker.get 'name' must be str, got {type(kwargs['name']).__name__}")
        return get_breaker_implementation(**kwargs)
    
    elif operation == 'call':
        if 'name' not in kwargs:
            raise ValueError("circuit_breaker.call requires 'name' parameter")
        if 'func' not in kwargs:
            raise ValueError("circuit_breaker.call requires 'func' parameter")
        if not isinstance(kwargs['name'], str):
            raise TypeError(f"circuit_breaker.call 'name' must be str, got {type(kwargs['name']).__name__}")
        if not callable(kwargs['func']):
            raise TypeError(f"circuit_breaker.call 'func' must be callable, got {type(kwargs['func']).__name__}")
        return execute_with_breaker_implementation(**kwargs)
    
    elif operation == 'get_all_states':
        return get_all_states_implementation(**kwargs)
    
    elif operation == 'reset_all':
        return reset_all_implementation(**kwargs)
    
    elif operation == 'get_stats':
        return get_stats_implementation(**kwargs)
    
    elif operation == 'reset':
        return reset_implementation(**kwargs)
    
    else:
        raise ValueError(f"Unhandled circuit breaker operation: '{operation}'")


__all__ = ['execute_circuit_breaker_operation']

# EOF
