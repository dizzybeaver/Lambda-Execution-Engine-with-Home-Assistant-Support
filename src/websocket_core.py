"""
websocket_core.py - WebSocket Core Implementation
Version: 2025.10.14.01
Description: WebSocket operations implementation (relocated from http_client_core.py).
             Internal module - accessed via websocket.py interface.

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


def websocket_connect_implementation(url: str = None, timeout: int = 10, **kwargs) -> Dict[str, Any]:
    """Establish WebSocket connection."""
    from gateway import log_info, log_error, create_success_response, create_error_response, generate_correlation_id, record_metric
    
    if not url:
        url = kwargs.get('url')
    
    correlation_id = kwargs.get('correlation_id') or generate_correlation_id()
    
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
        
    except Exception as e:
        log_error(f"[{correlation_id}] WebSocket connection failed: {str(e)}")
        record_metric('websocket.connection_errors', 1.0)
        return create_error_response(f'Connection failed: {str(e)}')


def websocket_send_implementation(connection=None, message: Dict[str, Any] = None, 
                                  correlation_id: Optional[str] = None, **kwargs) -> Dict[str, Any]:
    """Send message via WebSocket."""
    from gateway import log_info, log_error, create_success_response, create_error_response, record_metric
    
    if not connection:
        connection = kwargs.get('connection')
    if not message:
        message = kwargs.get('message', {})
    
    try:
        log_info(f"[{correlation_id}] Sending WebSocket message")
        
        message_str = json.dumps(message)
        connection.send(message_str)
        
        record_metric('websocket.messages_sent', 1.0)
        log_info(f"[{correlation_id}] Message sent successfully")
        
        return create_success_response("Message sent", {
            'correlation_id': correlation_id
        })
        
    except Exception as e:
        log_error(f"[{correlation_id}] Failed to send message: {str(e)}")
        record_metric('websocket.send_errors', 1.0)
        return create_error_response(f'Send failed: {str(e)}')


def websocket_receive_implementation(connection=None, timeout: int = 10, 
                                     correlation_id: Optional[str] = None, **kwargs) -> Dict[str, Any]:
    """Receive message from WebSocket."""
    from gateway import log_info, log_error, create_success_response, create_error_response, record_metric
    
    if not connection:
        connection = kwargs.get('connection')
    
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
        
    except Exception as e:
        log_error(f"[{correlation_id}] Failed to receive message: {str(e)}")
        record_metric('websocket.receive_errors', 1.0)
        return create_error_response(f'Receive failed: {str(e)}')


def websocket_close_implementation(connection=None, correlation_id: Optional[str] = None, **kwargs) -> Dict[str, Any]:
    """Close WebSocket connection."""
    from gateway import log_info, create_success_response, record_metric
    
    if not connection:
        connection = kwargs.get('connection')
    
    try:
        log_info(f"[{correlation_id}] Closing WebSocket connection")
        connection.close()
        record_metric('websocket.disconnections', 1.0)
        return create_success_response("Connection closed", {
            'correlation_id': correlation_id
        })
    except Exception as e:
        from gateway import log_error, create_error_response
        log_error(f"[{correlation_id}] Failed to close connection: {str(e)}")
        return create_error_response(f'Close failed: {str(e)}')


def websocket_request_implementation(url: str = None, message: Dict[str, Any] = None, 
                                     timeout: int = 10, **kwargs) -> Dict[str, Any]:
    """Execute WebSocket request (connect + send + receive + close)."""
    from gateway import log_info, log_error, generate_correlation_id
    
    if not url:
        url = kwargs.get('url')
    if not message:
        message = kwargs.get('message', {})
    
    correlation_id = kwargs.get('correlation_id') or generate_correlation_id()
    
    log_info(f"[{correlation_id}] Executing WebSocket request to {url}")
    
    connect_result = websocket_connect_implementation(url=url, timeout=timeout, correlation_id=correlation_id)
    if not connect_result.get('success'):
        return connect_result
    
    connection = connect_result.get('data', {}).get('connection')
    
    send_result = websocket_send_implementation(connection=connection, message=message, correlation_id=correlation_id)
    if not send_result.get('success'):
        websocket_close_implementation(connection=connection, correlation_id=correlation_id)
        return send_result
    
    receive_result = websocket_receive_implementation(connection=connection, timeout=timeout, correlation_id=correlation_id)
    
    close_result = websocket_close_implementation(connection=connection, correlation_id=correlation_id)
    
    if not receive_result.get('success'):
        return receive_result
    
    from gateway import create_success_response
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
