# ha_websocket.py
"""
ha_websocket.py - WebSocket Operations
Version: 3.0.0
Description: WebSocket communication with debug tracing and timing metrics

Copyright 2025 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

import os
import json
import time
from typing import Dict, Any, Optional, List
from gateway import (
    log_info, log_error, log_debug, log_warning,
    execute_operation, GatewayInterface,
    cache_get, cache_set,
    increment_counter, record_metric,
    create_success_response, create_error_response,
    generate_correlation_id
)

# Configuration
HA_WEBSOCKET_ENABLED = os.getenv('HA_WEBSOCKET_ENABLED', 'false').lower() == 'true'
HA_WEBSOCKET_TIMEOUT = int(os.getenv('HA_WEBSOCKET_TIMEOUT', '10'))
HA_WEBSOCKET_CACHE_TTL = 300

# ===== MODULE-LEVEL DEBUG MODE =====
_DEBUG_MODE_ENABLED = os.getenv('DEBUG_MODE', 'false').lower() == 'true'

# Timing thresholds
HA_SLOW_WEBSOCKET_CONNECT_THRESHOLD_MS = 3000  # 3 seconds
HA_SLOW_WEBSOCKET_SEND_THRESHOLD_MS = 1000     # 1 second
HA_SLOW_WEBSOCKET_RECEIVE_THRESHOLD_MS = 5000  # 5 seconds

def _debug_trace(correlation_id: str, step: str, **details):
    """
    Debug trace helper for WebSocket operations.
    
    Args:
        correlation_id: Correlation ID for request tracing
        step: Step description
        **details: Additional details to log
    """
    if _DEBUG_MODE_ENABLED:
        detail_str = ', '.join(f"{k}={v}" for k, v in details.items()) if details else ''
        log_info(f"[{correlation_id}] [WEBSOCKET-TRACE] {step}" + (f" ({detail_str})" if detail_str else ""))


# ===== WEBSOCKET CONNECTION =====

def establish_websocket_connection(url: str, timeout: int = 10) -> Dict[str, Any]:
    """Establish WebSocket connection using Gateway."""
    correlation_id = generate_correlation_id()
    start_time = time.perf_counter()
    
    _debug_trace(correlation_id, "establish_websocket_connection START", url=url[:50], timeout=timeout)
    
    try:
        log_debug(f"[{correlation_id}] Establishing WebSocket: {url}")
        
        # Use Gateway WebSocket interface
        result = execute_operation(
            GatewayInterface.WEBSOCKET,
            'connect',
            url=url,
            timeout=timeout,
            correlation_id=correlation_id
        )
        
        duration_ms = (time.perf_counter() - start_time) * 1000
        
        if result.get('success'):
            _debug_trace(correlation_id, "WebSocket connected", duration_ms=duration_ms)
            increment_counter('ha_websocket_connect_success')
            record_metric('ha_websocket_connect_duration_ms', duration_ms)
            log_info(f"[{correlation_id}] WebSocket connected")
            
            # Slow connection detection
            if duration_ms > HA_SLOW_WEBSOCKET_CONNECT_THRESHOLD_MS:
                log_warning(f"[{correlation_id}] Slow WebSocket connection: {duration_ms:.2f}ms")
                increment_counter('ha_websocket_slow_connect')
        else:
            _debug_trace(correlation_id, "WebSocket connection FAILED", duration_ms=duration_ms)
            increment_counter('ha_websocket_connect_failure')
            record_metric('ha_websocket_connect_error_duration_ms', duration_ms)
            log_error(f"[{correlation_id}] WebSocket connection failed")
        
        return result
        
    except Exception as e:
        duration_ms = (time.perf_counter() - start_time) * 1000
        _debug_trace(correlation_id, "establish_websocket_connection FAILED", error=str(e), duration_ms=duration_ms)
        log_error(f"[{correlation_id}] WebSocket establish failed: {str(e)}")
        
        if _DEBUG_MODE_ENABLED:
            import traceback
            log_error(f"[{correlation_id}] [TRACEBACK]\n{traceback.format_exc()}")
        
        increment_counter('ha_websocket_connect_error')
        record_metric('ha_websocket_connect_error_duration_ms', duration_ms)
        return create_error_response(str(e), 'WEBSOCKET_CONNECT_FAILED')


def send_websocket_message(connection: Any, message: Dict[str, Any]) -> Dict[str, Any]:
    """Send WebSocket message using Gateway."""
    correlation_id = generate_correlation_id()
    start_time = time.perf_counter()
    
    _debug_trace(correlation_id, "send_websocket_message START", message_type=message.get('type'))
    
    try:
        log_debug(f"[{correlation_id}] Sending WebSocket message")
        
        result = execute_operation(
            GatewayInterface.WEBSOCKET,
            'send',
            connection=connection,
            message=message,
            correlation_id=correlation_id
        )
        
        duration_ms = (time.perf_counter() - start_time) * 1000
        
        if result.get('success'):
            _debug_trace(correlation_id, "send_websocket_message SUCCESS", duration_ms=duration_ms)
            increment_counter('ha_websocket_send_success')
            record_metric('ha_websocket_send_duration_ms', duration_ms)
            
            # Slow send detection
            if duration_ms > HA_SLOW_WEBSOCKET_SEND_THRESHOLD_MS:
                log_warning(f"[{correlation_id}] Slow WebSocket send: {duration_ms:.2f}ms")
                increment_counter('ha_websocket_slow_send')
        else:
            _debug_trace(correlation_id, "send_websocket_message FAILED", duration_ms=duration_ms)
            increment_counter('ha_websocket_send_failure')
            record_metric('ha_websocket_send_error_duration_ms', duration_ms)
        
        return result
        
    except Exception as e:
        duration_ms = (time.perf_counter() - start_time) * 1000
        _debug_trace(correlation_id, "send_websocket_message FAILED", error=str(e), duration_ms=duration_ms)
        log_error(f"[{correlation_id}] WebSocket send failed: {str(e)}")
        
        if _DEBUG_MODE_ENABLED:
            import traceback
            log_error(f"[{correlation_id}] [TRACEBACK]\n{traceback.format_exc()}")
        
        increment_counter('ha_websocket_send_error')
        return create_error_response(str(e), 'WEBSOCKET_SEND_FAILED')


def receive_websocket_message(connection: Any, timeout: int = 10) -> Dict[str, Any]:
    """Receive WebSocket message using Gateway."""
    correlation_id = generate_correlation_id()
    start_time = time.perf_counter()
    
    _debug_trace(correlation_id, "receive_websocket_message START", timeout=timeout)
    
    try:
        log_debug(f"[{correlation_id}] Receiving WebSocket message")
        
        result = execute_operation(
            GatewayInterface.WEBSOCKET,
            'receive',
            connection=connection,
            timeout=timeout,
            correlation_id=correlation_id
        )
        
        duration_ms = (time.perf_counter() - start_time) * 1000
        
        if result.get('success'):
            _debug_trace(correlation_id, "receive_websocket_message SUCCESS", duration_ms=duration_ms)
            increment_counter('ha_websocket_receive_success')
            record_metric('ha_websocket_receive_duration_ms', duration_ms)
            
            # Slow receive detection
            if duration_ms > HA_SLOW_WEBSOCKET_RECEIVE_THRESHOLD_MS:
                log_warning(f"[{correlation_id}] Slow WebSocket receive: {duration_ms:.2f}ms")
                increment_counter('ha_websocket_slow_receive')
        else:
            _debug_trace(correlation_id, "receive_websocket_message FAILED", duration_ms=duration_ms)
            increment_counter('ha_websocket_receive_failure')
            record_metric('ha_websocket_receive_error_duration_ms', duration_ms)
        
        return result
        
    except Exception as e:
        duration_ms = (time.perf_counter() - start_time) * 1000
        _debug_trace(correlation_id, "receive_websocket_message FAILED", error=str(e), duration_ms=duration_ms)
        log_error(f"[{correlation_id}] WebSocket receive failed: {str(e)}")
        
        if _DEBUG_MODE_ENABLED:
            import traceback
            log_error(f"[{correlation_id}] [TRACEBACK]\n{traceback.format_exc()}")
        
        increment_counter('ha_websocket_receive_error')
        return create_error_response(str(e), 'WEBSOCKET_RECEIVE_FAILED')


def close_websocket_connection(connection: Any) -> Dict[str, Any]:
    """Close WebSocket connection using Gateway."""
    correlation_id = generate_correlation_id()
    start_time = time.perf_counter()
    
    _debug_trace(correlation_id, "close_websocket_connection START")
    
    try:
        log_debug(f"[{correlation_id}] Closing WebSocket connection")
        
        result = execute_operation(
            GatewayInterface.WEBSOCKET,
            'close',
            connection=connection,
            correlation_id=correlation_id
        )
        
        duration_ms = (time.perf_counter() - start_time) * 1000
        
        if result.get('success'):
            _debug_trace(correlation_id, "close_websocket_connection SUCCESS", duration_ms=duration_ms)
            increment_counter('ha_websocket_close_success')
            record_metric('ha_websocket_close_duration_ms', duration_ms)
        else:
            _debug_trace(correlation_id, "close_websocket_connection FAILED", duration_ms=duration_ms)
            increment_counter('ha_websocket_close_failure')
        
        return result
        
    except Exception as e:
        duration_ms = (time.perf_counter() - start_time) * 1000
        _debug_trace(correlation_id, "close_websocket_connection FAILED", error=str(e), duration_ms=duration_ms)
        log_error(f"[{correlation_id}] WebSocket close failed: {str(e)}")
        
        if _DEBUG_MODE_ENABLED:
            import traceback
            log_error(f"[{correlation_id}] [TRACEBACK]\n{traceback.format_exc()}")
        
        increment_counter('ha_websocket_close_error')
        return create_error_response(str(e), 'WEBSOCKET_CLOSE_FAILED')


# ===== WEBSOCKET AUTHENTICATION =====

def authenticate_websocket(connection: Any, access_token: str) -> Dict[str, Any]:
    """Authenticate WebSocket connection with Home Assistant."""
    correlation_id = generate_correlation_id()
    start_time = time.perf_counter()
    
    _debug_trace(correlation_id, "authenticate_websocket START")
    
    try:
        log_info(f"[{correlation_id}] Authenticating WebSocket")
        
        # Wait for auth_required message
        _debug_trace(correlation_id, "Waiting for auth_required")
        auth_req = receive_websocket_message(connection, timeout=5)
        if not auth_req.get('success'):
            return auth_req
        
        # Send auth message
        _debug_trace(correlation_id, "Sending auth message")
        auth_msg = {
            'type': 'auth',
            'access_token': access_token
        }
        
        send_result = send_websocket_message(connection, auth_msg)
        if not send_result.get('success'):
            return send_result
        
        # Wait for auth_ok or auth_invalid
        _debug_trace(correlation_id, "Waiting for auth response")
        auth_resp = receive_websocket_message(connection, timeout=5)
        if not auth_resp.get('success'):
            return auth_resp
        
        response_data = auth_resp.get('data', {}).get('message', {})
        msg_type = response_data.get('type', '')
        
        duration_ms = (time.perf_counter() - start_time) * 1000
        
        if msg_type == 'auth_ok':
            _debug_trace(correlation_id, "authenticate_websocket SUCCESS", duration_ms=duration_ms)
            increment_counter('ha_websocket_auth_success')
            record_metric('ha_websocket_auth_duration_ms', duration_ms)
            return create_success_response('WebSocket authenticated', {
                'authenticated': True,
                'ha_version': response_data.get('ha_version')
            })
        else:
            _debug_trace(correlation_id, "authenticate_websocket FAILED (auth_invalid)", duration_ms=duration_ms)
            increment_counter('ha_websocket_auth_failure')
            record_metric('ha_websocket_auth_error_duration_ms', duration_ms)
            return create_error_response('Authentication failed', 'AUTH_FAILED')
        
    except Exception as e:
        duration_ms = (time.perf_counter() - start_time) * 1000
        _debug_trace(correlation_id, "authenticate_websocket FAILED", error=str(e), duration_ms=duration_ms)
        log_error(f"[{correlation_id}] WebSocket auth failed: {str(e)}")
        
        if _DEBUG_MODE_ENABLED:
            import traceback
            log_error(f"[{correlation_id}] [TRACEBACK]\n{traceback.format_exc()}")
        
        increment_counter('ha_websocket_auth_error')
        return create_error_response(str(e), 'WEBSOCKET_AUTH_FAILED')


def websocket_request(connection: Any, message_type: str, 
                     params: Optional[Dict] = None,
                     request_id: Optional[int] = None) -> Dict[str, Any]:
    """Send WebSocket request and receive response."""
    correlation_id = generate_correlation_id()
    start_time = time.perf_counter()
    
    _debug_trace(correlation_id, "websocket_request START", message_type=message_type)
    
    try:
        if request_id is None:
            request_id = int(correlation_id[-8:], 16) % 1000000
        
        message = {
            'id': request_id,
            'type': message_type
        }
        
        if params:
            message.update(params)
        
        log_debug(f"[{correlation_id}] WebSocket request: {message_type}")
        
        # Send request
        _debug_trace(correlation_id, "Sending request")
        send_result = send_websocket_message(connection, message)
        if not send_result.get('success'):
            return send_result
        
        # Receive response
        _debug_trace(correlation_id, "Receiving response")
        response = receive_websocket_message(connection, timeout=HA_WEBSOCKET_TIMEOUT)
        if not response.get('success'):
            return response
        
        response_data = response.get('data', {}).get('message', {})
        
        duration_ms = (time.perf_counter() - start_time) * 1000
        
        # Check for error
        if response_data.get('type') == 'result':
            if response_data.get('success'):
                _debug_trace(correlation_id, "websocket_request SUCCESS", duration_ms=duration_ms)
                increment_counter(f'ha_websocket_request_{message_type}_success')
                record_metric(f'ha_websocket_request_{message_type}_duration_ms', duration_ms)
                return create_success_response('Request successful', 
                                              response_data.get('result'))
            else:
                _debug_trace(correlation_id, "websocket_request FAILED (result error)", duration_ms=duration_ms)
                increment_counter(f'ha_websocket_request_{message_type}_failure')
                return create_error_response(
                    response_data.get('error', {}).get('message', 'Unknown error'),
                    'WEBSOCKET_REQUEST_FAILED'
                )
        
        _debug_trace(correlation_id, "websocket_request COMPLETE", duration_ms=duration_ms)
        return create_success_response('Response received', response_data)
        
    except Exception as e:
        duration_ms = (time.perf_counter() - start_time) * 1000
        _debug_trace(correlation_id, "websocket_request FAILED", error=str(e), duration_ms=duration_ms)
        log_error(f"[{correlation_id}] WebSocket request failed: {str(e)}")
        
        if _DEBUG_MODE_ENABLED:
            import traceback
            log_error(f"[{correlation_id}] [TRACEBACK]\n{traceback.format_exc()}")
        
        increment_counter('ha_websocket_request_error')
        return create_error_response(str(e), 'WEBSOCKET_REQUEST_FAILED')


# ===== ENTITY REGISTRY =====

def get_entity_registry_via_websocket(use_cache: bool = True) -> Dict[str, Any]:
    """Get entity registry via WebSocket with caching."""
    correlation_id = generate_correlation_id()
    start_time = time.perf_counter()
    
    _debug_trace(correlation_id, "get_entity_registry_via_websocket START", use_cache=use_cache)
    
    if not HA_WEBSOCKET_ENABLED:
        return create_error_response('WebSocket not enabled', 'WEBSOCKET_DISABLED')
    
    # Check cache
    cache_key = 'ha_entity_registry_ws'
    if use_cache:
        cache_start = time.perf_counter()
        cached = cache_get(cache_key)
        cache_duration_ms = (time.perf_counter() - cache_start) * 1000
        
        if cached:
            duration_ms = (time.perf_counter() - start_time) * 1000
            _debug_trace(correlation_id, "get_entity_registry_via_websocket COMPLETE (CACHE)", 
                        duration_ms=duration_ms)
            log_debug(f"[{correlation_id}] Using cached entity registry")
            increment_counter('ha_entity_registry_cache_hit')
            record_metric('ha_entity_registry_duration_ms', duration_ms)
            return cached
    
    try:
        from home_assistant.ha_config import load_ha_config
        config = load_ha_config()
        
        if not config.get('enabled'):
            return create_error_response('HA not enabled', 'HA_DISABLED')
        
        # Build WebSocket URL
        base_url = config['base_url'].replace('http://', 'ws://').replace('https://', 'wss://')
        ws_url = f"{base_url}/api/websocket"
        
        log_info(f"[{correlation_id}] Fetching entity registry via WebSocket")
        
        # Connect
        _debug_trace(correlation_id, "Establishing connection")
        conn_result = establish_websocket_connection(ws_url, timeout=HA_WEBSOCKET_TIMEOUT)
        if not conn_result.get('success'):
            return conn_result
        
        connection = conn_result.get('data', {}).get('connection')
        
        if not connection:
            return create_error_response('No connection in result', 'WEBSOCKET_NO_CONNECTION')
        
        try:
            # Authenticate
            _debug_trace(correlation_id, "Authenticating")
            auth_result = authenticate_websocket(connection, config['access_token'])
            if not auth_result.get('success'):
                return auth_result
            
            # Request entity registry
            _debug_trace(correlation_id, "Requesting entity registry")
            registry_result = websocket_request(
                connection,
                'config/entity_registry/list'
            )
            
            if registry_result.get('success'):
                entities = registry_result.get('data', [])
                
                response = create_success_response('Entity registry retrieved', {
                    'entities': entities,
                    'count': len(entities),
                    'via': 'websocket'
                })
                
                # Cache result
                if use_cache:
                    cache_set(cache_key, response, ttl=HA_WEBSOCKET_CACHE_TTL)
                
                duration_ms = (time.perf_counter() - start_time) * 1000
                
                _debug_trace(correlation_id, "get_entity_registry_via_websocket SUCCESS",
                            entity_count=len(entities), duration_ms=duration_ms)
                increment_counter('ha_entity_registry_ws_success')
                record_metric('ha_entity_registry_duration_ms', duration_ms)
                log_info(f"[{correlation_id}] Retrieved {len(entities)} entities via WebSocket")
                
                return response
            
            return registry_result
            
        finally:
            # Always close connection
            _debug_trace(correlation_id, "Closing connection")
            close_websocket_connection(connection)
        
    except Exception as e:
        duration_ms = (time.perf_counter() - start_time) * 1000
        _debug_trace(correlation_id, "get_entity_registry_via_websocket FAILED", 
                    error=str(e), duration_ms=duration_ms)
        log_error(f"[{correlation_id}] Entity registry fetch failed: {str(e)}")
        
        if _DEBUG_MODE_ENABLED:
            import traceback
            log_error(f"[{correlation_id}] [TRACEBACK]\n{traceback.format_exc()}")
        
        increment_counter('ha_entity_registry_ws_error')
        record_metric('ha_entity_registry_error_duration_ms', duration_ms)
        return create_error_response(str(e), 'ENTITY_REGISTRY_FAILED')


def filter_exposed_entities(entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Filter entities to only exposed ones."""
    correlation_id = generate_correlation_id()
    
    _debug_trace(correlation_id, "filter_exposed_entities START", total=len(entities))
    
    try:
        exposed = []
        
        for entity in entities:
            # Check if entity is exposed to Alexa/Assist
            options = entity.get('options', {})
            
            # Check multiple exposure flags
            exposed_to_alexa = options.get('alexa', {}).get('should_expose', False)
            exposed_to_assist = options.get('conversation', {}).get('should_expose', False)
            
            if exposed_to_alexa or exposed_to_assist:
                exposed.append(entity)
        
        _debug_trace(correlation_id, "filter_exposed_entities COMPLETE", 
                    exposed=len(exposed), total=len(entities))
        log_info(f"[{correlation_id}] Filtered to {len(exposed)}/{len(entities)} exposed entities")
        return exposed
        
    except Exception as e:
        _debug_trace(correlation_id, "filter_exposed_entities FAILED", error=str(e))
        log_error(f"[{correlation_id}] Entity filtering failed: {str(e)}")
        
        if _DEBUG_MODE_ENABLED:
            import traceback
            log_error(f"[{correlation_id}] [TRACEBACK]\n{traceback.format_exc()}")
        
        return entities


# ===== FEATURE CHECK =====

def is_websocket_enabled() -> bool:
    """Check if WebSocket feature is enabled."""
    return HA_WEBSOCKET_ENABLED


# EOF
