"""
interface_websocket.py - WebSocket CLIENT Interface Router (SUGA-ISP Architecture)
Version: 2025.10.22.02
Description: Firewall router for WebSocket CLIENT interface with free tier compliance.

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

from typing import Any, Dict, Callable

# Import protection for websocket_core
try:
    from websocket_core import (
        websocket_connect_implementation,
        websocket_send_implementation,
        websocket_receive_implementation,
        websocket_close_implementation,
        websocket_request_implementation,
        websocket_get_stats_implementation,
        websocket_reset_implementation
    )
    _WEBSOCKET_AVAILABLE = True
    _WEBSOCKET_IMPORT_ERROR = None
except ImportError as e:
    _WEBSOCKET_AVAILABLE = False
    _WEBSOCKET_IMPORT_ERROR = str(e)
    websocket_connect_implementation = None
    websocket_send_implementation = None
    websocket_receive_implementation = None
    websocket_close_implementation = None
    websocket_request_implementation = None
    websocket_get_stats_implementation = None
    websocket_reset_implementation = None


# ===== PARAMETER VALIDATION =====

def _validate_url_param(kwargs: Dict[str, Any], operation: str) -> None:
    """Validate url parameter exists."""
    if 'url' not in kwargs:
        raise ValueError(f"websocket.{operation} requires 'url' parameter")


def _validate_connection_param(kwargs: Dict[str, Any], operation: str) -> None:
    """Validate connection parameter exists."""
    if 'connection' not in kwargs:
        raise ValueError(f"websocket.{operation} requires 'connection' parameter")


def _validate_message_param(kwargs: Dict[str, Any], operation: str) -> None:
    """Validate message parameter exists."""
    if 'message' not in kwargs:
        raise ValueError(f"websocket.{operation} requires 'message' parameter")


def _validate_send_params(kwargs: Dict[str, Any]) -> None:
    """Validate send operation parameters."""
    _validate_connection_param(kwargs, 'send')
    _validate_message_param(kwargs, 'send')


def _validate_request_params(kwargs: Dict[str, Any]) -> None:
    """Validate request operation parameters."""
    _validate_url_param(kwargs, 'request')
    _validate_message_param(kwargs, 'request')


# ===== DISPATCH DICTIONARY =====

def _build_dispatch_dict() -> Dict[str, Callable]:
    """
    Build WebSocket operation dispatch dictionary.
    
    Uses Dispatch Dictionary Architecture (LEE.ARC.3) for O(1) operation routing.
    All operations are CLIENT-SIDE ONLY (outbound connections to external servers).
    """
    return {
        'connect': lambda **kwargs: (
            _validate_url_param(kwargs, 'connect'),
            websocket_connect_implementation(**kwargs)
        )[1],
        
        'send': lambda **kwargs: (
            _validate_send_params(kwargs),
            websocket_send_implementation(**kwargs)
        )[1],
        
        'receive': lambda **kwargs: (
            _validate_connection_param(kwargs, 'receive'),
            websocket_receive_implementation(**kwargs)
        )[1],
        
        'close': lambda **kwargs: (
            _validate_connection_param(kwargs, 'close'),
            websocket_close_implementation(**kwargs)
        )[1],
        
        'request': lambda **kwargs: (
            _validate_request_params(kwargs),
            websocket_request_implementation(**kwargs)
        )[1],
        
        'get_stats': lambda **kwargs: websocket_get_stats_implementation(),
        
        'reset': lambda **kwargs: websocket_reset_implementation(),
    }


_OPERATION_DISPATCH: Dict[str, Callable] = _build_dispatch_dict()


# ===== ROUTER FUNCTION =====

def execute_websocket_operation(operation: str, **kwargs) -> Any:
    """
    Route WebSocket CLIENT operation requests to internal implementations.
    This is called by the SUGA-ISP (gateway.py).
    
    Uses Dispatch Dictionary Architecture for O(1) operation routing.
    
    All operations are CLIENT-SIDE ONLY (outbound from Lambda to external servers).
    Does NOT accept inbound connections (would require API Gateway - PAID SERVICE).
    
    Args:
        operation: WebSocket operation to execute
        **kwargs: Operation-specific parameters
        
    Returns:
        Operation result
        
    Raises:
        RuntimeError: If WebSocket interface unavailable
        ValueError: If operation is unknown or required parameters missing
        
    Free tier: YES - all operations incur only standard Lambda execution costs
    """
    # Check WebSocket availability
    if not _WEBSOCKET_AVAILABLE:
        raise RuntimeError(
            f"WebSocket interface unavailable: {_WEBSOCKET_IMPORT_ERROR}. "
            "This may indicate missing websocket_core module or circular import."
        )
    
    # Validate operation exists
    if operation not in _OPERATION_DISPATCH:
        raise ValueError(
            f"Unknown WebSocket operation: '{operation}'. "
            f"Valid operations: {', '.join(sorted(_OPERATION_DISPATCH.keys()))}"
        )
    
    # Execute via dispatch dictionary (O(1) lookup)
    return _OPERATION_DISPATCH[operation](**kwargs)


__all__ = ['execute_websocket_operation']

# EOF
