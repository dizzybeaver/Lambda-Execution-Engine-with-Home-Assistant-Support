"""
interface_http.py - HTTP Interface Router (SUGA-ISP Architecture)
Version: 2025.10.17.17
Description: Router for HTTP interface with dispatch dictionary pattern

Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any, Callable, Dict

# ===== IMPORT PROTECTION =====

try:
    from http_client_core import (
        http_request_implementation,
        http_get_implementation,
        http_post_implementation,
        http_put_implementation,
        http_delete_implementation,
        http_reset_implementation,
        get_state_implementation,
        reset_state_implementation
    )
    _HTTP_AVAILABLE = True
    _HTTP_IMPORT_ERROR = None
except ImportError as e:
    _HTTP_AVAILABLE = False
    _HTTP_IMPORT_ERROR = str(e)
    http_request_implementation = None
    http_get_implementation = None
    http_post_implementation = None
    http_put_implementation = None
    http_delete_implementation = None
    http_reset_implementation = None
    get_state_implementation = None
    reset_state_implementation = None


# ===== VALIDATION HELPERS =====

def _validate_url_param(kwargs: Dict[str, Any], operation: str) -> None:
    """Validate url parameter exists and is string."""
    if 'url' not in kwargs:
        raise ValueError(f"http.{operation} requires 'url' parameter")
    if not isinstance(kwargs['url'], str):
        raise TypeError(
            f"http.{operation} 'url' must be str, got {type(kwargs['url']).__name__}"
        )


def _validate_request_params(kwargs: Dict[str, Any]) -> None:
    """Validate request operation parameters."""
    if 'url' not in kwargs:
        raise ValueError("http.request requires 'url' parameter")
    if 'method' not in kwargs:
        raise ValueError("http.request requires 'method' parameter")
    if not isinstance(kwargs['url'], str):
        raise TypeError(
            f"http.request 'url' must be str, got {type(kwargs['url']).__name__}"
        )
    if not isinstance(kwargs['method'], str):
        raise TypeError(
            f"http.request 'method' must be str, got {type(kwargs['method']).__name__}"
        )


def _not_implemented_operation(operation: str):
    """Return function that raises NotImplementedError for unimplemented operations."""
    def _raise_not_implemented(**kwargs):
        raise NotImplementedError(
            f"HTTP operation '{operation}' is not yet implemented. "
            "This operation will be added in a future version."
        )
    return _raise_not_implemented


# ===== OPERATION DISPATCH =====

def _build_dispatch_dict() -> Dict[str, Callable]:
    """Build dispatch dictionary for HTTP operations. Only called if HTTP available."""
    return {
        'request': lambda **kwargs: (
            _validate_request_params(kwargs),
            http_request_implementation(**kwargs)
        )[1],
        
        'get': lambda **kwargs: (
            _validate_url_param(kwargs, 'get'),
            http_get_implementation(**kwargs)
        )[1],
        
        'post': lambda **kwargs: (
            _validate_url_param(kwargs, 'post'),
            http_post_implementation(**kwargs)
        )[1],
        
        'put': lambda **kwargs: (
            _validate_url_param(kwargs, 'put'),
            http_put_implementation(**kwargs)
        )[1],
        
        'delete': lambda **kwargs: (
            _validate_url_param(kwargs, 'delete'),
            http_delete_implementation(**kwargs)
        )[1],
        
        'reset': http_reset_implementation,
        'get_state': get_state_implementation,
        'reset_state': reset_state_implementation,
        
        # Not yet implemented operations (Issue #17 fix)
        'configure_retry': _not_implemented_operation('configure_retry'),
        'get_statistics': _not_implemented_operation('get_statistics'),
    }

_OPERATION_DISPATCH = _build_dispatch_dict() if _HTTP_AVAILABLE else {}


# ===== MAIN ROUTER FUNCTION =====

def execute_http_operation(operation: str, **kwargs) -> Any:
    """
    Route HTTP operation requests using dispatch dictionary pattern.
    
    Args:
        operation: HTTP operation to execute
        **kwargs: Operation-specific parameters
        
    Returns:
        Operation result
        
    Raises:
        RuntimeError: If HTTP interface unavailable
        ValueError: If operation is unknown or required parameters missing
        NotImplementedError: If operation is not yet implemented
    """
    # Check HTTP availability
    if not _HTTP_AVAILABLE:
        raise RuntimeError(
            f"HTTP interface unavailable: {_HTTP_IMPORT_ERROR}. "
            "This may indicate missing http_client_core module or circular import."
        )
    
    # Validate operation exists
    if operation not in _OPERATION_DISPATCH:
        raise ValueError(
            f"Unknown HTTP operation: '{operation}'. "
            f"Valid operations: {', '.join(_OPERATION_DISPATCH.keys())}"
        )
    
    # Dispatch using dictionary lookup (O(1))
    return _OPERATION_DISPATCH[operation](**kwargs)


__all__ = ['execute_http_operation']

# EOF
