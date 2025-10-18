"""
interface_websocket.py - WebSocket Interface Router (SUGA-ISP Architecture)
Version: 2025.10.17.14
Description: Firewall router for WebSocket interface with parameter validation and import protection

CHANGELOG:
- 2025.10.17.14: FIXED Issue #20 - Added import error protection
  - Added try/except wrapper for websocket_core imports
  - Sets _WEBSOCKET_AVAILABLE flag on success/failure
  - Stores import error message for debugging
  - Provides clear error when WebSocket unavailable
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

from typing import Any

# Import protection
try:
    from websocket_core import (
        _execute_connect_implementation,
        _execute_send_implementation,
        _execute_disconnect_implementation,
        _execute_get_state_implementation
    )
    _WEBSOCKET_AVAILABLE = True
    _WEBSOCKET_IMPORT_ERROR = None
except ImportError as e:
    _WEBSOCKET_AVAILABLE = False
    _WEBSOCKET_IMPORT_ERROR = str(e)
    _execute_connect_implementation = None
    _execute_send_implementation = None
    _execute_disconnect_implementation = None
    _execute_get_state_implementation = None


_VALID_WEBSOCKET_OPERATIONS = [
    'connect', 'send', 'disconnect', 'get_state'
]


def execute_websocket_operation(operation: str, **kwargs) -> Any:
    """
    Route WebSocket operation requests to internal implementations with parameter validation.
    This is called by the SUGA-ISP (gateway.py).
    
    Args:
        operation: WebSocket operation to execute
        **kwargs: Operation-specific parameters
        
    Returns:
        Operation result
        
    Raises:
        RuntimeError: If WebSocket interface unavailable
        ValueError: If operation is unknown or required parameters missing
    """
    # Check WebSocket availability
    if not _WEBSOCKET_AVAILABLE:
        raise RuntimeError(
            f"WebSocket interface unavailable: {_WEBSOCKET_IMPORT_ERROR}. "
            "This may indicate missing websocket_core module or circular import."
        )
    
    if operation not in _VALID_WEBSOCKET_OPERATIONS:
        raise ValueError(
            f"Unknown WebSocket operation: '{operation}'. "
            f"Valid operations: {', '.join(_VALID_WEBSOCKET_OPERATIONS)}"
        )
    
    if operation == 'connect':
        if 'url' not in kwargs:
            raise ValueError("websocket.connect requires 'url' parameter")
        if not isinstance(kwargs['url'], str):
            raise TypeError(f"websocket.connect 'url' must be str, got {type(kwargs['url']).__name__}")
        return _execute_connect_implementation(**kwargs)
    
    elif operation == 'send':
        if 'connection_id' not in kwargs:
            raise ValueError("websocket.send requires 'connection_id' parameter")
        if 'message' not in kwargs:
            raise ValueError("websocket.send requires 'message' parameter")
        if not isinstance(kwargs['connection_id'], str):
            raise TypeError(f"websocket.send 'connection_id' must be str, got {type(kwargs['connection_id']).__name__}")
        return _execute_send_implementation(**kwargs)
    
    elif operation == 'disconnect':
        if 'connection_id' not in kwargs:
            raise ValueError("websocket.disconnect requires 'connection_id' parameter")
        if not isinstance(kwargs['connection_id'], str):
            raise TypeError(f"websocket.disconnect 'connection_id' must be str, got {type(kwargs['connection_id']).__name__}")
        return _execute_disconnect_implementation(**kwargs)
    
    elif operation == 'get_state':
        return _execute_get_state_implementation(**kwargs)
    
    else:
        raise ValueError(f"Unhandled WebSocket operation: '{operation}'")


__all__ = ['execute_websocket_operation']

# EOF
