"""
websocket.py - WebSocket Interface (SUGA Gateway Pattern)
Version: 2025.10.14.01
Description: Single interface file for all WebSocket operations.
             Gateway calls only this file. Internal implementations in websocket_core.

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

def websocket_connect(**kwargs) -> Dict[str, Any]:
    """
    Establish WebSocket connection.
    Gateway operation: WEBSOCKET.connect
    """
    from websocket_core import websocket_connect_implementation
    return websocket_connect_implementation(**kwargs)


def websocket_send(**kwargs) -> Dict[str, Any]:
    """
    Send message via WebSocket.
    Gateway operation: WEBSOCKET.send
    """
    from websocket_core import websocket_send_implementation
    return websocket_send_implementation(**kwargs)


def websocket_receive(**kwargs) -> Dict[str, Any]:
    """
    Receive message from WebSocket.
    Gateway operation: WEBSOCKET.receive
    """
    from websocket_core import websocket_receive_implementation
    return websocket_receive_implementation(**kwargs)


def websocket_close(**kwargs) -> Dict[str, Any]:
    """
    Close WebSocket connection.
    Gateway operation: WEBSOCKET.close
    """
    from websocket_core import websocket_close_implementation
    return websocket_close_implementation(**kwargs)


def websocket_request(**kwargs) -> Dict[str, Any]:
    """
    Execute WebSocket request (send + receive).
    Gateway operation: WEBSOCKET.request
    """
    from websocket_core import websocket_request_implementation
    return websocket_request_implementation(**kwargs)


__all__ = [
    'websocket_connect',
    'websocket_send',
    'websocket_receive',
    'websocket_close',
    'websocket_request',
]

# EOF
