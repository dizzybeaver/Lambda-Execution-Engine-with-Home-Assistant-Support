"""
websocket/websocket_core.py
Version: 2025-12-13_1
Purpose: Gateway implementation functions for websocket interface
License: Apache 2.0
"""

from typing import Dict, Any

from websocket.websocket_manager import get_websocket_manager


def websocket_connect_implementation(url: str, timeout: int = 10, 
                                     correlation_id: str = None, **kwargs) -> Dict[str, Any]:
    """
    Connect to WebSocket server using manager.
    
    Args:
        url: WebSocket URL (ws:// or wss://)
        timeout: Connection timeout in seconds
        correlation_id: Optional correlation ID for debug tracking
    
    Returns:
        Success response with connection object, or error response
    """
    # ADDED: Debug integration
    from gateway import debug_log, generate_correlation_id
    
    if correlation_id is None:
        correlation_id = generate_correlation_id()
    
    debug_log(correlation_id, "WEBSOCKET",
             "websocket_connect_implementation called", url=url, timeout=timeout)
    
    manager = get_websocket_manager()
    return manager.connect(url, timeout, correlation_id)


def websocket_send_implementation(connection: Any, message: Dict[str, Any],
                                  correlation_id: str = None, **kwargs) -> Dict[str, Any]:
    """
    Send message via WebSocket using manager.
    
    Args:
        connection: Active WebSocket connection object
        message: Dictionary to send
        correlation_id: Optional correlation ID for debug tracking
    
    Returns:
        Success response or error response
    """
    # ADDED: Debug integration
    from gateway import debug_log, generate_correlation_id
    
    if correlation_id is None:
        correlation_id = generate_correlation_id()
    
    debug_log(correlation_id, "WEBSOCKET",
             "websocket_send_implementation called",
             has_connection=connection is not None,
             has_message=message is not None)
    
    manager = get_websocket_manager()
    return manager.send(connection, message, correlation_id)


def websocket_receive_implementation(connection: Any, timeout: int = 10,
                                     correlation_id: str = None, **kwargs) -> Dict[str, Any]:
    """
    Receive message from WebSocket using manager.
    
    Args:
        connection: Active WebSocket connection object
        timeout: Receive timeout in seconds
        correlation_id: Optional correlation ID for debug tracking
    
    Returns:
        Success response with received message, or error response
    """
    # ADDED: Debug integration
    from gateway import debug_log, generate_correlation_id
    
    if correlation_id is None:
        correlation_id = generate_correlation_id()
    
    debug_log(correlation_id, "WEBSOCKET",
             "websocket_receive_implementation called",
             has_connection=connection is not None, timeout=timeout)
    
    manager = get_websocket_manager()
    return manager.receive(connection, timeout, correlation_id)


def websocket_close_implementation(connection: Any, correlation_id: str = None,
                                   **kwargs) -> Dict[str, Any]:
    """
    Close WebSocket connection using manager.
    
    Args:
        connection: Active WebSocket connection object
        correlation_id: Optional correlation ID for debug tracking
    
    Returns:
        Success response or error response
    """
    # ADDED: Debug integration
    from gateway import debug_log, generate_correlation_id
    
    if correlation_id is None:
        correlation_id = generate_correlation_id()
    
    debug_log(correlation_id, "WEBSOCKET",
             "websocket_close_implementation called",
             has_connection=connection is not None)
    
    manager = get_websocket_manager()
    return manager.close(connection, correlation_id)


def websocket_request_implementation(url: str, message: Dict[str, Any], 
                                     timeout: int = 10, correlation_id: str = None,
                                     **kwargs) -> Dict[str, Any]:
    """
    Execute complete WebSocket request using manager.
    
    Args:
        url: WebSocket URL (ws:// or wss://)
        message: Dictionary to send
        timeout: Connection and receive timeout in seconds
        correlation_id: Optional correlation ID for debug tracking
    
    Returns:
        Success response with server's response, or error response
    """
    # ADDED: Debug integration
    from gateway import debug_log, generate_correlation_id
    
    if correlation_id is None:
        correlation_id = generate_correlation_id()
    
    debug_log(correlation_id, "WEBSOCKET",
             "websocket_request_implementation called",
             url=url, timeout=timeout, has_message=message is not None)
    
    manager = get_websocket_manager()
    return manager.request(url, message, timeout, correlation_id)


def websocket_get_stats_implementation(correlation_id: str = None, **kwargs) -> Dict[str, Any]:
    """
    Get WebSocket statistics using manager.
    
    Args:
        correlation_id: Optional correlation ID for debug tracking
    
    Returns:
        Statistics dict
    """
    # ADDED: Debug integration
    from gateway import debug_log, generate_correlation_id
    
    if correlation_id is None:
        correlation_id = generate_correlation_id()
    
    debug_log(correlation_id, "WEBSOCKET", "websocket_get_stats_implementation called")
    
    manager = get_websocket_manager()
    return manager.get_stats(correlation_id)


def websocket_reset_implementation(correlation_id: str = None, **kwargs) -> Dict[str, Any]:
    """
    Reset WebSocket manager state.
    
    Args:
        correlation_id: Optional correlation ID for debug tracking
    
    Returns:
        Success/error response dict
    """
    # ADDED: Debug integration
    from gateway import debug_log, generate_correlation_id, create_success_response, create_error_response
    
    if correlation_id is None:
        correlation_id = generate_correlation_id()
    
    debug_log(correlation_id, "WEBSOCKET", "websocket_reset_implementation called")
    
    manager = get_websocket_manager()
    success = manager.reset(correlation_id)
    
    if success:
        debug_log(correlation_id, "WEBSOCKET", "Manager reset successful")
        return create_success_response("WebSocket manager reset", {
            'reset': True
        })
    else:
        debug_log(correlation_id, "WEBSOCKET", "Manager reset failed - rate limited")
        return create_error_response('Reset rate limited', 'RATE_LIMIT_EXCEEDED')


__all__ = [
    'websocket_connect_implementation',
    'websocket_send_implementation',
    'websocket_receive_implementation',
    'websocket_close_implementation',
    'websocket_request_implementation',
    'websocket_get_stats_implementation',
    'websocket_reset_implementation',
]
