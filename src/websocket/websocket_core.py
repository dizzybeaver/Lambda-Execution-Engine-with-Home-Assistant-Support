"""
websocket_core.py - WebSocket CLIENT Core Implementation
Version: 2025.10.22.01 
Description: WebSocket CLIENT operations implementation with manager pattern.
             Internal module - accessed via interface_websocket.py router.

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
import time
from typing import Dict, Any, Optional
from collections import deque


class WebSocketCore:
    """
    WebSocket CLIENT operations manager.
    
    Provides OUTBOUND WebSocket client functionality from Lambda to external servers.
    Does NOT accept inbound connections (would require API Gateway).
    
    COMPLIANCE:
    - AP-08: No threading locks (Lambda single-threaded)
    - DEC-04: Lambda single-threaded model
    - LESS-18: SINGLETON pattern via get_websocket_manager()
    - LESS-21: Rate limiting (300 ops/sec)
    """
    
    def __init__(self):
        """
        Initialize WebSocket manager.
        
        Uses rate limiting instead of threading locks (AP-08, DEC-04).
        Lambda is single-threaded, so locks are unnecessary and harmful.
        """
        # Rate limiting (300 ops/sec - lower for WebSocket)
        # LESS-21: Rate limiting essential for DoS protection
        self._rate_limiter = deque(maxlen=300)  # 300 ops/sec window
        self._rate_limit_window_ms = 1000  # 1 second window
        self._rate_limited_count = 0
        
        # Statistics
        self._total_operations = 0
        self._connections_count = 0
        self._messages_sent_count = 0
        self._messages_received_count = 0
        self._errors_count = 0
    
    def _check_rate_limit(self) -> bool:
        """
        Check if operation is within rate limit.
        
        LESS-21: Uses deque for efficient rate limiting.
        No threading locks needed (AP-08, DEC-04).
        
        Returns:
            bool: True if operation allowed, False if rate limited
        """
        now = time.time() * 1000  # milliseconds
        
        # Remove expired timestamps
        while self._rate_limiter and (now - self._rate_limiter[0]) > self._rate_limit_window_ms:
            self._rate_limiter.popleft()
        
        # Check if over limit
        if len(self._rate_limiter) >= 300:  # 300 ops/sec
            self._rate_limited_count += 1
            return False
        
        # Add current timestamp
        self._rate_limiter.append(now)
        return True
    
    def connect(self, url: str, timeout: int = 10, **kwargs) -> Dict[str, Any]:
        """
        Establish WebSocket CLIENT connection (outbound to external server).
        
        This creates an OUTBOUND connection FROM Lambda TO an external WebSocket server.
        Does NOT accept inbound connections (would require API Gateway).
        
        Args:
            url: WebSocket URL to connect to (ws:// or wss://)
            timeout: Connection timeout in seconds
            **kwargs: Additional parameters including optional correlation_id
            
        Returns:
            Success response with connection object, or error response
            
        Free tier: YES - standard Lambda execution costs only
        """
        if not self._check_rate_limit():
            from gateway import create_error_response
            return create_error_response('Rate limit exceeded', 'RATE_LIMIT_EXCEEDED')
        
        from gateway import log_info, log_error, create_success_response, create_error_response, generate_correlation_id, record_metric
        
        self._total_operations += 1
        correlation_id = kwargs.get('correlation_id')
        if correlation_id is None:
            correlation_id = generate_correlation_id()
        
        if not url:
            log_error(f"[{correlation_id}] WebSocket connect failed: URL is required")
            self._errors_count += 1
            return create_error_response('URL parameter is required', 'WEBSOCKET_NO_URL')
        
        try:
            import websocket
            
            log_info(f"[{correlation_id}] Establishing WebSocket CLIENT connection to {url}")
            
            ws = websocket.WebSocket()
            ws.connect(url, timeout=timeout)
            
            self._connections_count += 1
            record_metric('websocket.connections', 1.0)
            log_info(f"[{correlation_id}] WebSocket CLIENT connected successfully")
            
            return create_success_response("WebSocket connected", {
                'connection': ws,
                'correlation_id': correlation_id,
                'url': url
            })
            
        except ImportError as e:
            log_error(f"[{correlation_id}] WebSocket library not available: {str(e)}")
            self._errors_count += 1
            record_metric('websocket.connection_errors', 1.0)
            return create_error_response('WebSocket library not installed', 'WEBSOCKET_LIBRARY_MISSING')
        except Exception as e:
            log_error(f"[{correlation_id}] WebSocket connection failed: {str(e)}")
            self._errors_count += 1
            record_metric('websocket.connection_errors', 1.0)
            return create_error_response(f'Connection failed: {str(e)}', 'WEBSOCKET_CONNECT_FAILED')
    
    def send(self, connection: Any, message: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        Send message via WebSocket CLIENT connection.
        
        Sends a message FROM Lambda TO the connected external WebSocket server.
        
        Args:
            connection: Active WebSocket connection object
            message: Dictionary to send (will be JSON serialized)
            **kwargs: Additional parameters including optional correlation_id
            
        Returns:
            Success response or error response
            
        Free tier: YES - standard Lambda execution costs only
        """
        if not self._check_rate_limit():
            from gateway import create_error_response
            return create_error_response('Rate limit exceeded', 'RATE_LIMIT_EXCEEDED')
        
        from gateway import log_info, log_error, create_success_response, create_error_response, record_metric, generate_correlation_id
        
        self._total_operations += 1
        correlation_id = kwargs.get('correlation_id')
        if correlation_id is None:
            correlation_id = generate_correlation_id()
        
        if not connection:
            log_error(f"[{correlation_id}] WebSocket send failed: No connection provided")
            self._errors_count += 1
            return create_error_response('Connection parameter is required', 'WEBSOCKET_NO_CONNECTION')
        
        if message is None:
            log_error(f"[{correlation_id}] WebSocket send failed: No message provided")
            self._errors_count += 1
            return create_error_response('Message parameter is required', 'WEBSOCKET_NO_MESSAGE')
        
        if not isinstance(message, dict):
            log_error(f"[{correlation_id}] WebSocket send failed: Message must be a dictionary")
            self._errors_count += 1
            return create_error_response('Message must be a dictionary', 'WEBSOCKET_INVALID_MESSAGE')
        
        try:
            log_info(f"[{correlation_id}] Sending WebSocket message to external server")
            
            message_str = json.dumps(message)
            connection.send(message_str)
            
            self._messages_sent_count += 1
            record_metric('websocket.messages_sent', 1.0)
            log_info(f"[{correlation_id}] Message sent successfully")
            
            return create_success_response("Message sent", {
                'correlation_id': correlation_id
            })
            
        except (TypeError, ValueError) as e:
            log_error(f"[{correlation_id}] Failed to serialize message: {str(e)}")
            self._errors_count += 1
            record_metric('websocket.send_errors', 1.0)
            return create_error_response(f'Message serialization failed: {str(e)}', 'WEBSOCKET_SERIALIZE_FAILED')
        except Exception as e:
            log_error(f"[{correlation_id}] Failed to send message: {str(e)}")
            self._errors_count += 1
            record_metric('websocket.send_errors', 1.0)
            return create_error_response(f'Send failed: {str(e)}', 'WEBSOCKET_SEND_FAILED')
    
    def receive(self, connection: Any, timeout: int = 10, **kwargs) -> Dict[str, Any]:
        """
        Receive message from WebSocket CLIENT connection.
        
        Receives a response FROM the connected external WebSocket server TO Lambda.
        
        Args:
            connection: Active WebSocket connection object
            timeout: Receive timeout in seconds
            **kwargs: Additional parameters including optional correlation_id
            
        Returns:
            Success response with received message, or error response
            
        Free tier: YES - standard Lambda execution costs only
        """
        if not self._check_rate_limit():
            from gateway import create_error_response
            return create_error_response('Rate limit exceeded', 'RATE_LIMIT_EXCEEDED')
        
        from gateway import log_info, log_error, create_success_response, create_error_response, record_metric, generate_correlation_id
        
        self._total_operations += 1
        correlation_id = kwargs.get('correlation_id')
        if correlation_id is None:
            correlation_id = generate_correlation_id()
        
        if not connection:
            log_error(f"[{correlation_id}] WebSocket receive failed: No connection provided")
            self._errors_count += 1
            return create_error_response('Connection parameter is required', 'WEBSOCKET_NO_CONNECTION')
        
        try:
            log_info(f"[{correlation_id}] Receiving WebSocket message from external server")
            
            message_str = connection.recv()
            message = json.loads(message_str)
            
            self._messages_received_count += 1
            record_metric('websocket.messages_received', 1.0)
            log_info(f"[{correlation_id}] Message received successfully")
            
            return create_success_response("Message received", {
                'message': message,
                'correlation_id': correlation_id
            })
            
        except json.JSONDecodeError as e:
            log_error(f"[{correlation_id}] Failed to parse message: {str(e)}")
            self._errors_count += 1
            record_metric('websocket.receive_errors', 1.0)
            return create_error_response(f'Message parsing failed: {str(e)}', 'WEBSOCKET_PARSE_FAILED')
        except Exception as e:
            log_error(f"[{correlation_id}] Failed to receive message: {str(e)}")
            self._errors_count += 1
            record_metric('websocket.receive_errors', 1.0)
            return create_error_response(f'Receive failed: {str(e)}', 'WEBSOCKET_RECEIVE_FAILED')
    
    def close(self, connection: Any, **kwargs) -> Dict[str, Any]:
        """
        Close WebSocket CLIENT connection.
        
        Closes the connection FROM Lambda TO the external WebSocket server.
        
        Args:
            connection: Active WebSocket connection object to close
            **kwargs: Additional parameters including optional correlation_id
            
        Returns:
            Success response or error response
            
        Free tier: YES - standard Lambda execution costs only
        """
        if not self._check_rate_limit():
            from gateway import create_error_response
            return create_error_response('Rate limit exceeded', 'RATE_LIMIT_EXCEEDED')
        
        from gateway import log_info, log_error, create_success_response, create_error_response, record_metric, generate_correlation_id
        
        self._total_operations += 1
        correlation_id = kwargs.get('correlation_id')
        if correlation_id is None:
            correlation_id = generate_correlation_id()
        
        if not connection:
            log_error(f"[{correlation_id}] WebSocket close failed: No connection provided")
            self._errors_count += 1
            return create_error_response('Connection parameter is required', 'WEBSOCKET_NO_CONNECTION')
        
        try:
            log_info(f"[{correlation_id}] Closing WebSocket CLIENT connection")
            connection.close()
            record_metric('websocket.disconnections', 1.0)
            log_info(f"[{correlation_id}] Connection closed successfully")
            return create_success_response("Connection closed", {
                'correlation_id': correlation_id
            })
        except Exception as e:
            log_error(f"[{correlation_id}] Failed to close connection: {str(e)}")
            self._errors_count += 1
            return create_error_response(f'Close failed: {str(e)}', 'WEBSOCKET_CLOSE_FAILED')
    
    def request(self, url: str, message: Dict[str, Any], timeout: int = 10, **kwargs) -> Dict[str, Any]:
        """
        Execute complete WebSocket CLIENT request (connect + send + receive + close).
        
        Convenience function that performs a complete request cycle:
        1. Connect FROM Lambda TO external WebSocket server
        2. Send message TO server
        3. Receive response FROM server
        4. Close connection
        
        This is the recommended pattern for one-shot WebSocket requests.
        
        Args:
            url: WebSocket URL to connect to (ws:// or wss://)
            message: Dictionary to send (will be JSON serialized)
            timeout: Connection and receive timeout in seconds
            **kwargs: Additional parameters including optional correlation_id
            
        Returns:
            Success response with server's response, or error response
            
        Free tier: YES - standard Lambda execution costs only
        """
        if not self._check_rate_limit():
            from gateway import create_error_response
            return create_error_response('Rate limit exceeded', 'RATE_LIMIT_EXCEEDED')
        
        from gateway import log_info, log_error, generate_correlation_id, create_success_response, create_error_response
        
        self._total_operations += 1
        correlation_id = kwargs.get('correlation_id')
        if correlation_id is None:
            correlation_id = generate_correlation_id()
        
        if not url:
            log_error(f"[{correlation_id}] WebSocket request failed: URL is required")
            self._errors_count += 1
            return create_error_response('URL parameter is required', 'WEBSOCKET_NO_URL')
        
        if message is None:
            log_error(f"[{correlation_id}] WebSocket request failed: Message is required")
            self._errors_count += 1
            return create_error_response('Message parameter is required', 'WEBSOCKET_NO_MESSAGE')
        
        log_info(f"[{correlation_id}] Executing WebSocket CLIENT request to {url}")
        
        # Step 1: Connect
        connect_result = self.connect(url=url, timeout=timeout, correlation_id=correlation_id)
        if not connect_result.get('success'):
            log_error(f"[{correlation_id}] WebSocket request failed at connect stage")
            return connect_result
        
        connection = connect_result.get('data', {}).get('connection')
        
        # Step 2: Send
        send_result = self.send(connection=connection, message=message, correlation_id=correlation_id)
        if not send_result.get('success'):
            log_error(f"[{correlation_id}] WebSocket request failed at send stage, closing connection")
            self.close(connection=connection, correlation_id=correlation_id)
            return send_result
        
        # Step 3: Receive
        receive_result = self.receive(connection=connection, timeout=timeout, correlation_id=correlation_id)
        
        # Step 4: Close (always attempt to close)
        close_result = self.close(connection=connection, correlation_id=correlation_id)
        
        # Step 5: Check receive result AFTER closing
        if not receive_result.get('success'):
            log_error(f"[{correlation_id}] WebSocket request failed at receive stage")
            return receive_result
        
        # Step 6: Check close result
        if not close_result.get('success'):
            log_error(f"[{correlation_id}] WebSocket request completed but close failed")
        
        log_info(f"[{correlation_id}] WebSocket CLIENT request completed successfully")
        return create_success_response("WebSocket request completed", {
            'response': receive_result.get('data', {}).get('message'),
            'correlation_id': correlation_id
        })
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get WebSocket manager statistics.
        
        Returns:
            Dictionary with current statistics
        """
        if not self._check_rate_limit():
            from gateway import create_error_response
            return create_error_response('Rate limit exceeded', 'RATE_LIMIT_EXCEEDED')
        
        from gateway import create_success_response
        
        return create_success_response("WebSocket statistics", {
            'total_operations': self._total_operations,
            'connections_count': self._connections_count,
            'messages_sent_count': self._messages_sent_count,
            'messages_received_count': self._messages_received_count,
            'errors_count': self._errors_count,
            'rate_limited_count': self._rate_limited_count,
            'rate_limit_window_ms': self._rate_limit_window_ms,
            'current_rate_limit_size': len(self._rate_limiter),
            'max_rate_limit': self._rate_limiter.maxlen
        })
    
    def reset(self) -> bool:
        """
        Reset WebSocket manager state.
        
        LESS-18: Provides lifecycle management capability.
        Clears all statistics and rate limiting state.
        
        Returns:
            bool: True if reset successful, False if rate limited
        """
        if not self._check_rate_limit():
            return False
        
        try:
            # Reset statistics
            self._total_operations = 0
            self._connections_count = 0
            self._messages_sent_count = 0
            self._messages_received_count = 0
            self._errors_count = 0
            
            # Reset rate limiting
            self._rate_limiter.clear()
            self._rate_limited_count = 0
            
            return True
        except Exception:
            return False


# SINGLETON pattern for lifecycle management (LESS-18)
# Prevents multiple instances and provides global state management
_websocket_core = None


def get_websocket_manager() -> WebSocketCore:
    """
    Get SINGLETON WebSocket manager instance.
    
    LESS-18: SINGLETON pattern provides lifecycle management.
    Uses gateway SINGLETON registry with fallback to module-level instance.
    
    Returns:
        WebSocketCore: The singleton manager instance
        
    REF-IDs:
    - LESS-18: SINGLETON pattern for lifecycle management
    - DEC-04: No threading locks needed (Lambda single-threaded)
    """
    global _websocket_core
    
    try:
        # Try to use gateway SINGLETON registry
        from gateway import singleton_get, singleton_register
        
        manager = singleton_get('websocket_manager')
        if manager is None:
            # Create new instance and register
            if _websocket_core is None:
                _websocket_core = WebSocketCore()
            singleton_register('websocket_manager', _websocket_core)
            manager = _websocket_core
        
        return manager
        
    except (ImportError, Exception):
        # Fallback to module-level singleton
        if _websocket_core is None:
            _websocket_core = WebSocketCore()
        return _websocket_core


# Implementation wrappers using SINGLETON manager
def websocket_connect_implementation(url: str, timeout: int = 10, **kwargs) -> Dict[str, Any]:
    """Connect to WebSocket server using manager."""
    manager = get_websocket_manager()
    return manager.connect(url=url, timeout=timeout, **kwargs)


def websocket_send_implementation(connection: Any, message: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """Send message via WebSocket using manager."""
    manager = get_websocket_manager()
    return manager.send(connection=connection, message=message, **kwargs)


def websocket_receive_implementation(connection: Any, timeout: int = 10, **kwargs) -> Dict[str, Any]:
    """Receive message from WebSocket using manager."""
    manager = get_websocket_manager()
    return manager.receive(connection=connection, timeout=timeout, **kwargs)


def websocket_close_implementation(connection: Any, **kwargs) -> Dict[str, Any]:
    """Close WebSocket connection using manager."""
    manager = get_websocket_manager()
    return manager.close(connection=connection, **kwargs)


def websocket_request_implementation(url: str, message: Dict[str, Any], timeout: int = 10, **kwargs) -> Dict[str, Any]:
    """Execute complete WebSocket request using manager."""
    manager = get_websocket_manager()
    return manager.request(url=url, message=message, timeout=timeout, **kwargs)


def websocket_get_stats_implementation() -> Dict[str, Any]:
    """Get WebSocket statistics using manager."""
    manager = get_websocket_manager()
    return manager.get_stats()


def websocket_reset_implementation() -> Dict[str, Any]:
    """Reset WebSocket manager state."""
    manager = get_websocket_manager()
    success = manager.reset()
    
    from gateway import create_success_response, create_error_response
    
    if success:
        return create_success_response("WebSocket manager reset", {
            'reset': True
        })
    else:
        return create_error_response('Reset rate limited', 'RATE_LIMIT_EXCEEDED')


__all__ = [
    'WebSocketCore',
    'get_websocket_manager',
    'websocket_connect_implementation',
    'websocket_send_implementation',
    'websocket_receive_implementation',
    'websocket_close_implementation',
    'websocket_request_implementation',
    'websocket_get_stats_implementation',
    'websocket_reset_implementation',
]

# EOF
