"""
websocket_core.py - WebSocket Core Implementation
Version: 2025.10.16.01
Description: WebSocket operations implementation (relocated from http_client_core.py).
             Internal module - accessed via interface_websocket.py router.

FIXES APPLIED (2025.10.16):
- BUG #2: Added automatic correlation_id generation when missing
- BUG #4: Made url parameter required (not optional) to match wrapper contract
- BUG #6: Added validation for missing connection parameter
- BUG #7: Fixed error handling logic in websocket_request (check before close)
- EDGE CASE #1: Added message validation before serialization

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

import json
from typing import Dict, Any, Optional


def websocket_connect_implementation(url: str, timeout: int = 10, **kwargs) -> Dict[str, Any]:
    """Establish WebSocket connection."""
    from gateway import log_info, log_error, create_success_response, create_error_response, generate_correlation_id, record_metric
    
    correlation_id = kwargs.get('correlation_id')
    if correlation_id is None:
        correlation_id = generate_correlation_id()
    
    if not url:
        log_error(f"[{correlation_id}] WebSocket connect failed: URL is required")
        return create_error_response('URL parameter is required', 'WEBSOCKET_NO_URL')
    
    try:
        import websocket
        
        log_info(f"[{correlation_id}] Establishing WebSocket connection to {url}")
        
        ws = websocket.WebSocket()
        ws.connect(url, timeout=timeout)
        
        record_metric('websocket.connections', 1.0)
        log_info(f"[{correlation_id}] WebSocket connected successfully")
        
        return create_success_response("WebSocket connected", {
            'connection': ws,
            'correlation_id': correlation_id,
            'url': url
        })
        
    except ImportError as e:
        log_error(f"[{correlation_id}] WebSocket library not available: {str(e)}")
        record_metric('websocket.connection_errors', 1.0)
        return create_error_response('WebSocket library not installed', 'WEBSOCKET_LIBRARY_MISSING')
    except Exception as e:
        log_error(f"[{correlation_id}] WebSocket connection failed: {str(e)}")
        record_metric('websocket.connection_errors', 1.0)
        return create_error_response(f'Connection failed: {str(e)}', 'WEBSOCKET_CONNECT_FAILED')


def websocket_send_implementation(connection: Any, message: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """Send message via WebSocket."""
    from gateway import log_info, log_error, create_success_response, create_error_response, record_metric, generate_correlation_id
    
    correlation_id = kwargs.get('correlation_id')
    if correlation_id is None:
        correlation_id = generate_correlation_id()
    
    if not connection:
        log_error(f"[{correlation_id}] WebSocket send failed: No connection provided")
        return create_error_response('Connection parameter is required', 'WEBSOCKET_NO_CONNECTION')
    
    if message is None:
        log_error(f"[{correlation_id}] WebSocket send failed: No message provided")
        return create_error_response('Message parameter is required', 'WEBSOCKET_NO_MESSAGE')
    
    if not isinstance(message, dict):
        log_error(f"[{correlation_id}] WebSocket send failed: Message must be a dictionary")
        return create_error_response('Message must be a dictionary', 'WEBSOCKET_INVALID_MESSAGE')
    
    try:
        log_info(f"[{correlation_id}] Sending WebSocket message")
        
        message_str = json.dumps(message)
        connection.send(message_str)
        
        record_metric('websocket.messages_sent', 1.0)
        log_info(f"[{correlation_id}] Message sent successfully")
        
        return create_success_response("Message sent", {
            'correlation_id': correlation_id
        })
        
    except (TypeError, ValueError) as e:
        log_error(f"[{correlation_id}] Failed to serialize message: {str(e)}")
        record_metric('websocket.send_errors', 1.0)
        return create_error_response(f'Message serialization failed: {str(e)}', 'WEBSOCKET_SERIALIZE_FAILED')
    except Exception as e:
        log_error(f"[{correlation_id}] Failed to send message: {str(e)}")
        record_metric('websocket.send_errors', 1.0)
        return create_error_response(f'Send failed: {str(e)}', 'WEBSOCKET_SEND_FAILED')


def websocket_receive_implementation(connection: Any, timeout: int = 10, **kwargs) -> Dict[str, Any]:
    """Receive message from WebSocket."""
    from gateway import log_info, log_error, create_success_response, create_error_response, record_metric, generate_correlation_id
    
    correlation_id = kwargs.get('correlation_id')
    if correlation_id is None:
        correlation_id = generate_correlation_id()
    
    if not connection:
        log_error(f"[{correlation_id}] WebSocket receive failed: No connection provided")
        return create_error_response('Connection parameter is required', 'WEBSOCKET_NO_CONNECTION')
    
    try:
        log_info(f"[{correlation_id}] Receiving WebSocket message")
        
        message_str = connection.recv()
        message = json.loads(message_str)
        
        record_metric('websocket.messages_received', 1.0)
        log_info(f"[{correlation_id}] Message received successfully")
        
        return create_success_response("Message received", {
            'message': message,
            'correlation_id': correlation_id
        })
        
    except json.JSONDecodeError as e:
        log_error(f"[{correlation_id}] Failed to parse message: {str(e)}")
        record_metric('websocket.receive_errors', 1.0)
        return create_error_response(f'Message parsing failed: {str(e)}', 'WEBSOCKET_PARSE_FAILED')
    except Exception as e:
        log_error(f"[{correlation_id}] Failed to receive message: {str(e)}")
        record_metric('websocket.receive_errors', 1.0)
        return create_error_response(f'Receive failed: {str(e)}', 'WEBSOCKET_RECEIVE_FAILED')


def websocket_close_implementation(connection: Any, **kwargs) -> Dict[str, Any]:
    """Close WebSocket connection."""
    from gateway import log_info, log_error, create_success_response, create_error_response, record_metric, generate_correlation_id
    
    correlation_id = kwargs.get('correlation_id')
    if correlation_id is None:
        correlation_id = generate_correlation_id()
    
    if not connection:
        log_error(f"[{correlation_id}] WebSocket close failed: No connection provided")
        return create_error_response('Connection parameter is required', 'WEBSOCKET_NO_CONNECTION')
    
    try:
        log_info(f"[{correlation_id}] Closing WebSocket connection")
        connection.close()
        record_metric('websocket.disconnections', 1.0)
        log_info(f"[{correlation_id}] Connection closed successfully")
        return create_success_response("Connection closed", {
            'correlation_id': correlation_id
        })
    except Exception as e:
        log_error(f"[{correlation_id}] Failed to close connection: {str(e)}")
        return create_error_response(f'Close failed: {str(e)}', 'WEBSOCKET_CLOSE_FAILED')


def websocket_request_implementation(url: str, message: Dict[str, Any], timeout: int = 10, **kwargs) -> Dict[str, Any]:
    """Execute WebSocket request (connect + send + receive + close)."""
    from gateway import log_info, log_error, generate_correlation_id
    
    correlation_id = kwargs.get('correlation_id')
    if correlation_id is None:
        correlation_id = generate_correlation_id()
    
    if not url:
        log_error(f"[{correlation_id}] WebSocket request failed: URL is required")
        from gateway import create_error_response
        return create_error_response('URL parameter is required', 'WEBSOCKET_NO_URL')
    
    if message is None:
        log_error(f"[{correlation_id}] WebSocket request failed: Message is required")
        from gateway import create_error_response
        return create_error_response('Message parameter is required', 'WEBSOCKET_NO_MESSAGE')
    
    log_info(f"[{correlation_id}] Executing WebSocket request to {url}")
    
    # Step 1: Connect
    connect_result = websocket_connect_implementation(url=url, timeout=timeout, correlation_id=correlation_id)
    if not connect_result.get('success'):
        log_error(f"[{correlation_id}] WebSocket request failed at connect stage")
        return connect_result
    
    connection = connect_result.get('data', {}).get('connection')
    
    # Step 2: Send
    send_result = websocket_send_implementation(connection=connection, message=message, correlation_id=correlation_id)
    if not send_result.get('success'):
        log_error(f"[{correlation_id}] WebSocket request failed at send stage, closing connection")
        websocket_close_implementation(connection=connection, correlation_id=correlation_id)
        return send_result
    
    # Step 3: Receive
    receive_result = websocket_receive_implementation(connection=connection, timeout=timeout, correlation_id=correlation_id)
    
    # Step 4: Close (always attempt to close)
    close_result = websocket_close_implementation(connection=connection, correlation_id=correlation_id)
    
    # Step 5: Check receive result AFTER closing
    if not receive_result.get('success'):
        log_error(f"[{correlation_id}] WebSocket request failed at receive stage")
        return receive_result
    
    # Step 6: Check close result
    if not close_result.get('success'):
        log_error(f"[{correlation_id}] WebSocket request completed but close failed")
    
    from gateway import create_success_response
    log_info(f"[{correlation_id}] WebSocket request completed successfully")
    return create_success_response("WebSocket request completed", {
        'response': receive_result.get('data', {}).get('message'),
        'correlation_id': correlation_id
    })


__all__ = [
    'websocket_connect_implementation',
    'websocket_send_implementation',
    'websocket_receive_implementation',
    'websocket_close_implementation',
    'websocket_request_implementation',
]

# EOF
