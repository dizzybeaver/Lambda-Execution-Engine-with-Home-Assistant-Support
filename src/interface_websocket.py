"""
interface_websocket.py - WebSocket CLIENT Interface Router (SUGA-ISP Architecture)
Version: 2025.10.18.01
Description: Firewall router for WebSocket CLIENT interface with free tier compliance.
             Gateway calls only this file. Internal implementations in websocket_core.

FREE TIER COMPLIANCE NOTICE:
============================
This WebSocket interface provides CLIENT functionality ONLY.
Lambda acts as a WebSocket client connecting TO external WebSocket servers (e.g., Home Assistant).

✅ FREE TIER COMPLIANT - Client operations incur only standard Lambda costs:
   - Lambda execution time (400,000 GB-seconds/month free)
   - Lambda invocations (1 million/month free)
   - Data transfer OUT (1GB/month free, then $0.09/GB)

❌ NOT IMPLEMENTED - WebSocket SERVER functionality (would require AWS API Gateway):
   - Accepting inbound WebSocket connections from external clients
   - Maintaining persistent connections between Lambda invocations
   - Acting as WebSocket endpoint/server

COST WARNING:
=============
If WebSocket SERVER functionality is ever needed:
   - Requires AWS API Gateway WebSocket APIs
   - Free tier: 1M messages + 750K connection-minutes for FIRST 12 MONTHS ONLY
   - After 12 months: PAID SERVICE ($1.00/million messages + connection-minute charges)
   - Violates "free tier only" constraint after initial 12-month period

To maintain permanent free tier compliance, this implementation is CLIENT-ONLY.

CHANGELOG:
- 2025.10.18.01: Added free tier compliance documentation
- 2025.10.17.14: FIXED Issue #20 - Added import error protection
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

# Import protection for websocket_core
try:
    from websocket_core import (
        websocket_connect_implementation,
        websocket_send_implementation,
        websocket_receive_implementation,
        websocket_close_implementation,
        websocket_request_implementation
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


_VALID_WEBSOCKET_OPERATIONS = [
    'connect', 'send', 'receive', 'close', 'request'
]


def execute_websocket_operation(operation: str, **kwargs) -> Any:
    """
    Route WebSocket CLIENT operation requests to internal implementations.
    This is called by the SUGA-ISP (gateway.py).
    
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
    
    if operation not in _VALID_WEBSOCKET_OPERATIONS:
        raise ValueError(
            f"Unknown WebSocket operation: '{operation}'. "
            f"Valid operations: {', '.join(_VALID_WEBSOCKET_OPERATIONS)}"
        )
    
    # Route to appropriate implementation
    if operation == 'connect':
        if 'url' not in kwargs:
            raise ValueError("websocket.connect requires 'url' parameter")
        return websocket_connect_implementation(**kwargs)
    
    elif operation == 'send':
        if 'connection' not in kwargs:
            raise ValueError("websocket.send requires 'connection' parameter")
        if 'message' not in kwargs:
            raise ValueError("websocket.send requires 'message' parameter")
        return websocket_send_implementation(**kwargs)
    
    elif operation == 'receive':
        if 'connection' not in kwargs:
            raise ValueError("websocket.receive requires 'connection' parameter")
        return websocket_receive_implementation(**kwargs)
    
    elif operation == 'close':
        if 'connection' not in kwargs:
            raise ValueError("websocket.close requires 'connection' parameter")
        return websocket_close_implementation(**kwargs)
    
    elif operation == 'request':
        if 'url' not in kwargs:
            raise ValueError("websocket.request requires 'url' parameter")
        if 'message' not in kwargs:
            raise ValueError("websocket.request requires 'message' parameter")
        return websocket_request_implementation(**kwargs)
    
    else:
        raise ValueError(f"Unhandled WebSocket operation: '{operation}'")


__all__ = ['execute_websocket_operation']

# EOF
