"""
interface_websocket.py - WebSocket Interface Router (SUGA-ISP Architecture)
Version: 2025.10.15.01
Description: Firewall router for WebSocket interface

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

from typing import Any

# ✅ ALLOWED: Import internal files within same WebSocket interface
from websocket_core import (
    websocket_connect_implementation,
    websocket_send_implementation,
    websocket_receive_implementation,
    websocket_close_implementation,
    websocket_request_implementation
)


def execute_websocket_operation(operation: str, **kwargs) -> Any:
    """
    Route WebSocket operation requests to internal implementations.
    This is called by the SUGA-ISP (gateway.py).
    
    Args:
        operation: The WebSocket operation to execute ('connect', 'send', 'receive', etc.)
        **kwargs: Operation-specific parameters
        
    Returns:
        Operation result from internal implementation
        
    Raises:
        ValueError: If operation is unknown
    """
    
    if operation == 'connect':
        return websocket_connect_implementation(**kwargs)
    
    elif operation == 'send':
        return websocket_send_implementation(**kwargs)
    
    elif operation == 'receive':
        return websocket_receive_implementation(**kwargs)
    
    elif operation == 'close':
        return websocket_close_implementation(**kwargs)
    
    elif operation == 'request':
        return websocket_request_implementation(**kwargs)
    
    else:
        raise ValueError(f"Unknown WebSocket operation: {operation}")


__all__ = [
    'execute_websocket_operation'
]

# EOF
