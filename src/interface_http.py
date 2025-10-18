"""
interface_http.py - HTTP Interface Router (SUGA-ISP Architecture)
Version: 2025.10.17.07
Description: Firewall router for HTTP interface with parameter validation

CHANGELOG:
- 2025.10.17.07: Fixed fake success responses for unimplemented operations (Issue #17 fix)
  - configure_retry: Now raises NotImplementedError instead of fake success
  - get_statistics: Now raises NotImplementedError instead of fake success
  - Clear error messages indicating operations are not yet implemented
- 2025.10.17.05: Added parameter validation for all operations (Issue #18 fix)
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

from typing import Dict, Any

from http_client_core import (
    http_request_implementation,
    http_get_implementation,
    http_post_implementation,
    http_put_implementation,
    http_delete_implementation,
    get_state_implementation,
    reset_state_implementation
)


_VALID_HTTP_OPERATIONS = [
    'request', 'get', 'post', 'put', 'delete',
    'get_state', 'reset_state', 'configure_retry', 'get_statistics'
]


def execute_http_operation(operation: str, **kwargs) -> Any:
    """
    Route HTTP operation requests to internal implementations with parameter validation.
    This is called by the SUGA-ISP (gateway.py).
    
    Args:
        operation: HTTP operation to execute
        **kwargs: Operation-specific parameters
        
    Returns:
        Operation result
        
    Raises:
        ValueError: If operation is unknown or required parameters missing
        NotImplementedError: If operation is not yet implemented
    """
    if operation not in _VALID_HTTP_OPERATIONS:
        raise ValueError(
            f"Unknown HTTP operation: '{operation}'. "
            f"Valid operations: {', '.join(_VALID_HTTP_OPERATIONS)}"
        )
    
    if operation == 'request':
        _validate_url_param(kwargs, operation)
        _validate_method_param(kwargs, operation)
        return http_request_implementation(**kwargs)
    
    elif operation == 'get':
        _validate_url_param(kwargs, operation)
        return http_get_implementation(**kwargs)
    
    elif operation == 'post':
        _validate_url_param(kwargs, operation)
        return http_post_implementation(**kwargs)
    
    elif operation == 'put':
        _validate_url_param(kwargs, operation)
        return http_put_implementation(**kwargs)
    
    elif operation == 'delete':
        _validate_url_param(kwargs, operation)
        return http_delete_implementation(**kwargs)
    
    elif operation == 'get_state':
        # No required parameters
        return get_state_implementation(**kwargs)
    
    elif operation == 'reset_state':
        # No required parameters
        return reset_state_implementation(**kwargs)
    
    elif operation == 'configure_retry':
        # FIXED (Issue #17): Raise NotImplementedError instead of fake success
        raise NotImplementedError(
            f"HTTP operation '{operation}' is not yet implemented. "
            "This operation will be added in a future version."
        )
    
    elif operation == 'get_statistics':
        # FIXED (Issue #17): Raise NotImplementedError instead of fake success
        raise NotImplementedError(
            f"HTTP operation '{operation}' is not yet implemented. "
            "This operation will be added in a future version."
        )
    
    else:
        raise ValueError(f"Unknown HTTP operation: '{operation}'")


def _validate_url_param(kwargs: dict, operation: str) -> None:
    """
    Validate that url parameter exists and is a valid string.
    
    Args:
        kwargs: Parameter dictionary
        operation: Operation name (for error context)
        
    Raises:
        ValueError: If url is missing, not a string, or empty
    """
    if 'url' not in kwargs:
        raise ValueError(f"HTTP operation '{operation}' requires parameter 'url'")
    
    url = kwargs.get('url')
    if not isinstance(url, str):
        raise ValueError(
            f"HTTP operation '{operation}' parameter 'url' must be string, "
            f"got {type(url).__name__}"
        )
    
    if not url.strip():
        raise ValueError(f"HTTP operation '{operation}' parameter 'url' cannot be empty")


def _validate_method_param(kwargs: dict, operation: str) -> None:
    """
    Validate that method parameter exists and is a valid string.
    
    Args:
        kwargs: Parameter dictionary
        operation: Operation name (for error context)
        
    Raises:
        ValueError: If method is missing, not a string, or invalid
    """
    if 'method' not in kwargs:
        raise ValueError(f"HTTP operation '{operation}' requires parameter 'method'")
    
    method = kwargs.get('method')
    if not isinstance(method, str):
        raise ValueError(
            f"HTTP operation '{operation}' parameter 'method' must be string, "
            f"got {type(method).__name__}"
        )
    
    valid_methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS']
    if method.upper() not in valid_methods:
        raise ValueError(
            f"HTTP operation '{operation}' parameter 'method' must be one of {valid_methods}, "
            f"got '{method}'"
        )


__all__ = [
    'execute_http_operation'
]

# EOF
