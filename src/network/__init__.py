"""
network/__init__.py - Network Package Exports
Version: 2025.10.14.01
Description: Exports for network package (HTTP client, WebSocket, Circuit Breaker).

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

# Interface files (gateway-facing)
from network.http_client import (
    http_request,
    http_get,
    http_post,
    http_put,
    http_delete,
    get_state,
    reset_state,
    get_http_client,
    configure_retry,
    get_statistics,
)

from network.websocket import (
    websocket_connect,
    websocket_send,
    websocket_receive,
    websocket_close,
    websocket_request,
)

# Circuit Breaker
from network.circuit_breaker_core import (
    CircuitBreaker,
    CircuitState,
    get_breaker_implementation,
    execute_with_breaker_implementation,
    get_all_states_implementation,
    reset_all_implementation,
)

__all__ = [
    # HTTP Client Interface
    'http_request',
    'http_get',
    'http_post',
    'http_put',
    'http_delete',
    'get_state',
    'reset_state',
    'get_http_client',
    'configure_retry',
    'get_statistics',
    
    # WebSocket Interface
    'websocket_connect',
    'websocket_send',
    'websocket_receive',
    'websocket_close',
    'websocket_request',
    
    # Circuit Breaker
    'CircuitBreaker',
    'CircuitState',
    'get_breaker_implementation',
    'execute_with_breaker_implementation',
    'get_all_states_implementation',
    'reset_all_implementation',
]

# EOF
