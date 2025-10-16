"""
interface_http.py - HTTP Interface Router (SUGA-ISP Architecture)
Version: 2025.10.15.01
Description: Firewall router for HTTP interface

This file acts as the interface router (firewall) between the SUGA-ISP
and internal implementation files. Only this file may be accessed by
gateway.py. Internal files are isolated.

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

# âœ… ALLOWED: Import internal files within same HTTP interface
from http_client_core import (
    http_request_implementation,
    http_get_implementation,
    http_post_implementation,
    http_put_implementation,
    http_delete_implementation
)
from http_client_state import (
    get_client_state,
    reset_client_state,
    configure_http_retry,
    get_connection_statistics
)


def execute_http_operation(operation: str, **kwargs) -> Any:
    """
    Route HTTP operation requests to internal implementations.
    This is called by the SUGA-ISP (gateway.py).
    
    Args:
        operation: The HTTP operation to execute ('request', 'get', 'post', etc.)
        **kwargs: Operation-specific parameters
        
    Returns:
        Operation result from internal implementation
        
    Raises:
        ValueError: If operation is unknown
    """
    
    if operation == 'request':
        return http_request_implementation(**kwargs)
    
    elif operation == 'get':
        return http_get_implementation(**kwargs)
    
    elif operation == 'post':
        return http_post_implementation(**kwargs)
    
    elif operation == 'put':
        return http_put_implementation(**kwargs)
    
    elif operation == 'delete':
        return http_delete_implementation(**kwargs)
    
    elif operation == 'get_state':
        return get_client_state(**kwargs)
    
    elif operation == 'reset_state':
        return reset_client_state(**kwargs)
    
    elif operation == 'configure_retry':
        return configure_http_retry(**kwargs)
    
    elif operation == 'get_statistics':
        return get_connection_statistics(**kwargs)
    
    else:
        raise ValueError(f"Unknown HTTP operation: {operation}")


__all__ = [
    'execute_http_operation'
]

# EOF
