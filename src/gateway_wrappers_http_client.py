"""
gateway_wrappers_http_client.py - HTTP_CLIENT Interface Wrappers
Version: 2025.10.22.02
Description: Convenience wrappers for HTTP_CLIENT interface operations

Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any, Dict
from gateway_core import GatewayInterface, execute_operation


def http_request(method: str, url: str, **kwargs) -> Dict[str, Any]:
    """
    Execute HTTP request with specified method.
    
    Args:
        method: HTTP method (GET, POST, PUT, DELETE)
        url: Target URL
        **kwargs: Additional parameters (headers, json, body, timeout)
        
    Returns:
        Dict with success status, data, and metadata
    """
    return execute_operation(GatewayInterface.HTTP_CLIENT, 'request', method=method, url=url, **kwargs)


def http_get(url: str, **kwargs) -> Dict[str, Any]:
    """
    Execute HTTP GET request.
    
    Args:
        url: Target URL
        **kwargs: Additional parameters (headers, timeout)
        
    Returns:
        Dict with success status, data, and metadata
    """
    return execute_operation(GatewayInterface.HTTP_CLIENT, 'get', url=url, **kwargs)


def http_post(url: str, **kwargs) -> Dict[str, Any]:
    """
    Execute HTTP POST request.
    
    Args:
        url: Target URL
        **kwargs: Additional parameters (json, body, headers, timeout)
        
    Returns:
        Dict with success status, data, and metadata
    """
    return execute_operation(GatewayInterface.HTTP_CLIENT, 'post', url=url, **kwargs)


def http_put(url: str, **kwargs) -> Dict[str, Any]:
    """
    Execute HTTP PUT request.
    
    Args:
        url: Target URL
        **kwargs: Additional parameters (json, body, headers, timeout)
        
    Returns:
        Dict with success status, data, and metadata
    """
    return execute_operation(GatewayInterface.HTTP_CLIENT, 'put', url=url, **kwargs)


def http_delete(url: str, **kwargs) -> Dict[str, Any]:
    """
    Execute HTTP DELETE request.
    
    Args:
        url: Target URL
        **kwargs: Additional parameters (headers, timeout)
        
    Returns:
        Dict with success status, data, and metadata
    """
    return execute_operation(GatewayInterface.HTTP_CLIENT, 'delete', url=url, **kwargs)


def http_reset() -> Dict[str, Any]:
    """
    Reset HTTP client state.
    
    Resets:
    - Connection pool (closes all connections)
    - Statistics counters
    - Rate limiter state
    
    Returns:
        Dict with success status and reset confirmation
        
    REF: LESS-18 (Reset operation for lifecycle management)
    """
    return execute_operation(GatewayInterface.HTTP_CLIENT, 'reset')


def http_get_state(**kwargs) -> Dict[str, Any]:
    """
    Get HTTP client state.
    
    Returns:
        Dict with client state information
    """
    return execute_operation(GatewayInterface.HTTP_CLIENT, 'get_state', **kwargs)


def http_reset_state(**kwargs) -> Dict[str, Any]:
    """
    Reset HTTP client state (legacy operation).
    
    Returns:
        Dict with reset status
    """
    return execute_operation(GatewayInterface.HTTP_CLIENT, 'reset_state', **kwargs)


__all__ = [
    'http_request',
    'http_get',
    'http_post',
    'http_put',
    'http_delete',
    'http_reset',
    'http_get_state',
    'http_reset_state',
]
