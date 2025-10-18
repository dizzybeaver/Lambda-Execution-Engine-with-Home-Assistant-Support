"""
interface_http.py - HTTP Interface Router (SUGA-ISP Architecture)
Version: 2025.10.17.14
Description: Firewall router for HTTP interface with parameter validation and import protection

CHANGELOG:
- 2025.10.17.14: FIXED Issue #20 - Added import error protection
  - Added try/except wrapper for http_client_core imports
  - Sets _HTTP_AVAILABLE flag on success/failure
  - Stores import error message for debugging
  - Provides clear error when HTTP unavailable
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

# Import protection
try:
    from http_client_core import (
        http_request_implementation,
        http_get_implementation,
        http_post_implementation,
        http_put_implementation,
        http_delete_implementation,
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
    get_state_implementation = None
    reset_state_implementation = None


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
    
    if operation not in _VALID_HTTP_OPERATIONS:
        raise ValueError(
            f"Unknown HTTP operation: '{operation}'. "
            f"Valid operations: {', '.join(_VALID_HTTP_OPERATIONS)}"
        )
    
    if operation == 'request':
        if 'url' not in kwargs:
            raise ValueError("http.request requires 'url' parameter")
        if 'method' not in kwargs:
            raise ValueError("http.request requires 'method' parameter")
        if not isinstance(kwargs['url'], str):
            raise TypeError(f"http.request 'url' must be str, got {type(kwargs['url']).__name__}")
        if not isinstance(kwargs['method'], str):
            raise TypeError(f"http.request 'method' must be str, got {type(kwargs['method']).__name__}")
        return http_request_implementation(**kwargs)
    
    elif operation == 'get':
        if 'url' not in kwargs:
            raise ValueError("http.get requires 'url' parameter")
        if not isinstance(kwargs['url'], str):
            raise TypeError(f"http.get 'url' must be str, got {type(kwargs['url']).__name__}")
        return http_get_implementation(**kwargs)
    
    elif operation == 'post':
        if 'url' not in kwargs:
            raise ValueError("http.post requires 'url' parameter")
        if not isinstance(kwargs['url'], str):
            raise TypeError(f"http.post 'url' must be str, got {type(kwargs['url']).__name__}")
        return http_post_implementation(**kwargs)
    
    elif operation == 'put':
        if 'url' not in kwargs:
            raise ValueError("http.put requires 'url' parameter")
        if not isinstance(kwargs['url'], str):
            raise TypeError(f"http.put 'url' must be str, got {type(kwargs['url']).__name__}")
        return http_put_implementation(**kwargs)
    
    elif operation == 'delete':
        if 'url' not in kwargs:
            raise ValueError("http.delete requires 'url' parameter")
        if not isinstance(kwargs['url'], str):
            raise TypeError(f"http.delete 'url' must be str, got {type(kwargs['url']).__name__}")
        return http_delete_implementation(**kwargs)
    
    elif operation == 'get_state':
        return get_state_implementation(**kwargs)
    
    elif operation == 'reset_state':
        return reset_state_implementation(**kwargs)
    
    elif operation == 'configure_retry':
        raise NotImplementedError(
            f"HTTP operation '{operation}' is not yet implemented. "
            "This operation will be added in a future version."
        )
    
    elif operation == 'get_statistics':
        raise NotImplementedError(
            f"HTTP operation '{operation}' is not yet implemented. "
            "This operation will be added in a future version."
        )
    
    else:
        raise ValueError(f"Unhandled HTTP operation: '{operation}'")


__all__ = ['execute_http_operation']

# EOF
