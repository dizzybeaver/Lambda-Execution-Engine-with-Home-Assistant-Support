"""
interface_websocket.py - WebSocket Interface Router (SUGA-ISP Architecture)
Version: 2025.10.17.05
Description: Firewall router for WebSocket interface with parameter validation

CHANGELOG:
- 2025.10.17.05: Added parameter validation for all operations (Issue #18 fix)
  - Validates 'url' parameter for connect operation
  - Validates 'connection_id' parameter for send/receive/close operations
  - Validates 'message' parameter for send operation
  - Type checking for all string parameters
  - Clear error messages for missing/invalid parameters
- 2025.10.15.01: Initial SUGA-ISP router implementation

NOTE: WebSocket requires API Gateway WebSocket APIs for Lambda deployment.
Free tier: 1M messages/month for first 12 months, then paid service.
See Bug Analysis Report Issue #45 for details.

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

from typing import Any

from websocket_core import (
    websocket_connect_implementation,
    websocket_send_implementation,
    websocket_receive_implementation,
    websocket_close_implementation,
    websocket_request_implementation
)


_VALID_WEBSOCKET_OPERATIONS = [
    'connect', 'send', 'receive', 'close', 'request'
]


def execute_websocket_operation(operation: str, **kwargs) -> Any:
    """
    Route WebSocket operation requests to internal implementations with parameter validation.
    This is called by the SUGA-ISP (gateway.py).
    
    Args:
        operation: The WebSocket operation to execute
        **kwargs: Operation-specific parameters
        
    Returns:
        Operation result from internal implementation
        
    Raises:
        ValueError: If operation is unknown or required parameters are missing/invalid
        
    Note:
        WebSocket requires API Gateway WebSocket APIs for Lambda.
        Not a pure Lambda solution - requires additional AWS infrastructure.
    """
    
    if operation == 'connect':
        _validate_url_param(kwargs, operation)
        return websocket_connect_implementation(**kwargs)
    
    elif operation == 'send':
        _validate_send_params(kwargs, operation)
        return websocket_send_implementation(**kwargs)
    
    elif operation == 'receive':
        _validate_connection_id_param(kwargs, operation)
        return websocket_receive_implementation(**kwargs)
    
    elif operation == 'close':
        _validate_connection_id_param(kwargs, operation)
        return websocket_close_implementation(**kwargs)
    
    elif operation == 'request':
        _validate_url_param(kwargs, operation)
        return websocket_request_implementation(**kwargs)
    
    else:
        raise ValueError(
            f"Unknown WebSocket operation: '{operation}'. "
            f"Valid operations: {', '.join(_VALID_WEBSOCKET_OPERATIONS)}"
        )


def _validate_url_param(kwargs: dict, operation: str) -> None:
    """Validate url parameter for WebSocket operations."""
    if 'url' not in kwargs:
        raise ValueError(f"WebSocket operation '{operation}' requires parameter 'url'")
    
    url = kwargs.get('url')
    if not isinstance(url, str):
        raise ValueError(
            f"WebSocket operation '{operation}' parameter 'url' must be string, "
            f"got {type(url).__name__}"
        )
    
    if not url.strip():
        raise ValueError(f"WebSocket operation '{operation}' parameter 'url' cannot be empty")
    
    if not (url.startswith('ws://') or url.startswith('wss://')):
        raise ValueError(
            f"WebSocket operation '{operation}' parameter 'url' must start with 'ws://' or 'wss://', "
            f"got '{url[:10]}...'"
        )


def _validate_connection_id_param(kwargs: dict, operation: str) -> None:
    """Validate connection_id parameter."""
    if 'connection_id' not in kwargs:
        raise ValueError(f"WebSocket operation '{operation}' requires parameter 'connection_id'")
    
    connection_id = kwargs.get('connection_id')
    if not isinstance(connection_id, str):
        raise ValueError(
            f"WebSocket operation '{operation}' parameter 'connection_id' must be string, "
            f"got {type(connection_id).__name__}"
        )
    
    if not connection_id.strip():
        raise ValueError(f"WebSocket operation '{operation}' parameter 'connection_id' cannot be empty")


def _validate_send_params(kwargs: dict, operation: str) -> None:
    """Validate parameters for WebSocket send operation."""
    _validate_connection_id_param(kwargs, operation)
    
    if 'message' not in kwargs:
        raise ValueError(f"WebSocket operation '{operation}' requires parameter 'message'")
    
    message = kwargs.get('message')
    if not isinstance(message, (str, bytes, dict)):
        raise ValueError(
            f"WebSocket operation '{operation}' parameter 'message' must be string, bytes, or dict, "
            f"got {type(message).__name__}"
        )


__all__ = [
    'execute_websocket_operation'
]

# EOF
