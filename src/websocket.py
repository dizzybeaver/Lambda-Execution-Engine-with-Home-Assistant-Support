"""
websocket.py - WebSocket CLIENT Interface (SUGA Gateway Pattern)
Version: 2025.10.18.01
Description: WebSocket CLIENT operations for outbound connections.
             Gateway calls only this file. Internal implementations in websocket_core.

FREE TIER COMPLIANCE NOTICE:
============================
This implementation provides WebSocket CLIENT functionality ONLY.
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
    Establish WebSocket CLIENT connection (outbound to external server).
    Gateway operation: WEBSOCKET.connect
    
    Use case: Connect FROM Lambda TO external WebSocket server (e.g., Home Assistant).
    Free tier: YES - standard Lambda execution costs only.
    """
    from websocket_core import websocket_connect_implementation
    return websocket_connect_implementation(**kwargs)


def websocket_send(**kwargs) -> Dict[str, Any]:
    """
    Send message via WebSocket CLIENT connection.
    Gateway operation: WEBSOCKET.send
    
    Use case: Send message FROM Lambda TO external WebSocket server.
    Free tier: YES - standard Lambda execution costs only.
    """
    from websocket_core import websocket_send_implementation
    return websocket_send_implementation(**kwargs)


def websocket_receive(**kwargs) -> Dict[str, Any]:
    """
    Receive message from WebSocket CLIENT connection.
    Gateway operation: WEBSOCKET.receive
    
    Use case: Receive response FROM external WebSocket server TO Lambda.
    Free tier: YES - standard Lambda execution costs only.
    """
    from websocket_core import websocket_receive_implementation
    return websocket_receive_implementation(**kwargs)


def websocket_close(**kwargs) -> Dict[str, Any]:
    """
    Close WebSocket CLIENT connection.
    Gateway operation: WEBSOCKET.close
    
    Use case: Close connection FROM Lambda TO external WebSocket server.
    Free tier: YES - standard Lambda execution costs only.
    """
    from websocket_core import websocket_close_implementation
    return websocket_close_implementation(**kwargs)


def websocket_request(**kwargs) -> Dict[str, Any]:
    """
    Execute complete WebSocket CLIENT request (connect + send + receive + close).
    Gateway operation: WEBSOCKET.request
    
    Use case: One-shot request FROM Lambda TO external WebSocket server.
    Free tier: YES - standard Lambda execution costs only.
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
