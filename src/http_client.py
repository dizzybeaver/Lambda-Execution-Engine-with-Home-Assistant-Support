"""
http_client.py - HTTP Client Interface (SUGA Gateway Pattern)
Version: 2025.10.14.01
Description: Single interface file for all HTTP client operations.
             Gateway calls only this file. Internal implementations in network/ submodules.

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

from typing import Dict, Any, Optional

# ===== GATEWAY INTERFACE FUNCTIONS =====
# These are called directly by gateway.py
# Implementations are in http_client_core

def http_request(**kwargs) -> Dict[str, Any]:
    """
    Execute HTTP request (any method).
    Gateway operation: HTTP_CLIENT.request
    """
    from http_client_core import http_request_implementation
    return http_request_implementation(**kwargs)


def http_get(**kwargs) -> Dict[str, Any]:
    """
    Execute HTTP GET request.
    Gateway operation: HTTP_CLIENT.get
    """
    from http_client_core import http_get_implementation
    return http_get_implementation(**kwargs)


def http_post(**kwargs) -> Dict[str, Any]:
    """
    Execute HTTP POST request.
    Gateway operation: HTTP_CLIENT.post
    """
    from http_client_core import http_post_implementation
    return http_post_implementation(**kwargs)


def http_put(**kwargs) -> Dict[str, Any]:
    """
    Execute HTTP PUT request.
    Gateway operation: HTTP_CLIENT.put
    """
    from http_client_core import http_put_implementation
    return http_put_implementation(**kwargs)


def http_delete(**kwargs) -> Dict[str, Any]:
    """
    Execute HTTP DELETE request.
    Gateway operation: HTTP_CLIENT.delete
    """
    from http_client_core import http_delete_implementation
    return http_delete_implementation(**kwargs)


def get_state(**kwargs) -> Dict[str, Any]:
    """
    Get HTTP client state.
    Gateway operation: HTTP_CLIENT.get_state
    """
    from http_client_state import get_client_state
    return get_client_state(**kwargs)


def reset_state(**kwargs) -> Dict[str, Any]:
    """
    Reset HTTP client state.
    Gateway operation: HTTP_CLIENT.reset_state
    """
    from http_client_state import reset_client_state
    return reset_client_state(**kwargs)


# ===== PUBLIC API (non-gateway) =====
# These can be imported directly by other modules

def get_http_client():
    """Get singleton HTTP client instance."""
    from http_client_core import get_http_client
    return get_http_client()


def configure_retry(**kwargs) -> Dict[str, Any]:
    """Configure HTTP retry behavior."""
    from http_client_state import configure_http_retry
    return configure_http_retry(**kwargs)


def get_statistics() -> Dict[str, Any]:
    """Get HTTP client statistics."""
    from http_client_state import get_connection_statistics
    return get_connection_statistics()


# ===== EXPORTS =====

__all__ = [
    # Gateway operations
    'http_request',
    'http_get',
    'http_post',
    'http_put',
    'http_delete',
    'get_state',
    'reset_state',
    
    # Public API
    'get_http_client',
    'configure_retry',
    'get_statistics',
]

# EOF
