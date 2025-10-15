"""
home_assistant/ha_websocket.py - WebSocket Operations
Version: 2025.10.14.01
Description: WebSocket communication with Home Assistant using Gateway services.

Copyright 2025 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

import os
import json
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

# ===== WEBSOCKET CONNECTION =====

def establish_websocket_connection(url: str, timeout: int = 10) -> Dict[str, Any]:
    """Establish WebSocket connection using Gateway."""
    correlation_id = generate_correlation_id()
    
    try:
        log_debug(f"[{correlation_id}] Establishing WebSocket: {url}")
        
        # Use Gateway WebSocket interface
        result = execute_operation(
            GatewayInterface.WEBSOCKET,
            'connect',
            url=url,
            timeout=timeout
        )
        
        if result.get('success'):
            increment_counter('ha_websocket_connect_success')
            log_info(f"[{correlation_id}] WebSocket connected")
        else:
            increment_counter('ha_websocket_connect_failure')
            log_error(f"[{correlation_id}] WebSocket connection failed")
        
        return result
        
    except Exception as e:
        log_error(f"[{correlation_id}] WebSocket establish failed: {str(e)}")
        increment_counter('ha_websocket_connect_error')
        return create_error_response(str(e), 'WEBSOCKET_CONNECT_FAILED')


def send_websocket_message(ws_id: str, message: Dict[str, Any]) -> Dict[str, Any]:
    """Send WebSocket message using Gateway."""
    correlation_id = generate_correlation_id()
    
    try:
        log_debug(f"[{correlation_id}] Sending WebSocket message")
        
        result = execute_operation(
            GatewayInterface.WEBSOCKET,
            'send',
            ws_id=ws_id,
            message=json.dumps(message)
        )
        
        if result.get('success'):
            increment_counter('ha_websocket_send_success')
        else:
            increment_counter('ha_websocket_send_failure')
        
        return result
        
    except Exception as e:
        log_error(f"[{correlation_id}] WebSocket send failed: {str(e)}")
        return create_error_response(str(e), 'WEBSOCKET_SEND_FAILED')


def receive_websocket_message(ws_id: str, timeout: int = 10) -> Dict[str, Any]:
    """Receive WebSocket message using Gateway."""
    correlation_id = generate_correlation_id()
    
    try:
        log_debug(f"[{correlation_id}] Receiving WebSocket message")
        
        result = execute_operation(
            GatewayInterface.WEBSOCKET,
            'receive',
            ws_id=ws_id,
            timeout=timeout
        )
        
        if result.get('success'):
            increment_counter('ha_websocket_receive_success')
            
            # Parse JSON response
            data = result.get('data', '')
            if isinstance(data, str):
                try:
                    result['data'] = json.loads(data)
                except json.JSONDecodeError:
                    pass
        else:
            increment_counter('ha_websocket_receive_failure')
        
        return result
        
    except Exception as e:
        log_error(f"[{correlation_id}] WebSocket receive failed: {str(e)}")
        return create_error_response(str(e), 'WEBSOCKET_RECEIVE_FAILED')


def close_websocket_connection(ws_id: str) -> Dict[str, Any]:
    """Close WebSocket connection using Gateway."""
    correlation_id = generate_correlation_id()
    
    try:
        log_debug(f"[{correlation_id}] Closing WebSocket")
        
        result = execute_operation(
            GatewayInterface.WEBSOCKET,
            'close',
            ws_id=ws_id
        )
        
        if result.get('success'):
            increment_counter('ha_websocket_close_success')
            log_info(f"[{correlation_id}] WebSocket closed")
        
        return result
        
    except Exception as e:
        log_error(f"[{correlation_id}] WebSocket close failed: {str(e)}")
        return create_error_response(str(e), 'WEBSOCKET_CLOSE_FAILED')


# ===== HOME ASSISTANT WEBSOCKET API =====

def authenticate_websocket(ws_id: str, access_token: str) -> Dict[str, Any]:
    """Authenticate WebSocket connection with HA."""
    correlation_id = generate_correlation_id()
    
    try:
        log_info(f"[{correlation_id}] Authenticating WebSocket")
        
        # Wait for auth_required message
        auth_req = receive_websocket_message(ws_id, timeout=5)
        if not auth_req.get('success'):
            return auth_req
        
        # Send auth message
        auth_msg = {
            'type': 'auth',
            'access_token': access_token
        }
        
        send_result = send_websocket_message(ws_id, auth_msg)
        if not send_result.get('success'):
            return send_result
        
        # Wait for auth_ok or auth_invalid
        auth_resp = receive_websocket_message(ws_id, timeout=5)
        if not auth_resp.get('success'):
            return auth_resp
        
        response_data = auth_resp.get('data', {})
        msg_type = response_data.get('type', '')
        
        if msg_type == 'auth_ok':
            increment_counter('ha_websocket_auth_success')
            return create_success_response('WebSocket authenticated', {
                'authenticated': True,
                'ha_version': response_data.get('ha_version')
            })
        else:
            increment_counter('ha_websocket_auth_failure')
            return create_error_response('Authentication failed', 'AUTH_FAILED')
        
    except Exception as e:
        log_error(f"[{correlation_id}] WebSocket auth failed: {str(e)}")
        return create_error_response(str(e), 'WEBSOCKET_AUTH_FAILED')


def websocket_request(ws_id: str, message_type: str, 
                     params: Optional[Dict] = None,
                     request_id: Optional[int] = None) -> Dict[str, Any]:
    """Send WebSocket request and receive response."""
    correlation_id = generate_correlation_id()
    
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
        send_result = send_websocket_message(ws_id, message)
        if not send_result.get('success'):
            return send_result
        
        # Receive response
        response = receive_websocket_message(ws_id, timeout=HA_WEBSOCKET_TIMEOUT)
        if not response.get('success'):
            return response
        
        response_data = response.get('data', {})
        
        # Check for error
        if response_data.get('type') == 'result':
            if response_data.get('success'):
                increment_counter(f'ha_websocket_request_{message_type}_success')
                return create_success_response('Request successful', 
                                              response_data.get('result'))
            else:
                increment_counter(f'ha_websocket_request_{message_type}_failure')
                return create_error_response(
                    response_data.get('error', {}).get('message', 'Unknown error'),
                    'WEBSOCKET_REQUEST_FAILED'
                )
        
        return create_success_response('Response received', response_data)
        
    except Exception as e:
        log_error(f"[{correlation_id}] WebSocket request failed: {str(e)}")
        return create_error_response(str(e), 'WEBSOCKET_REQUEST_FAILED')


# ===== ENTITY REGISTRY =====

def get_entity_registry_via_websocket(use_cache: bool = True) -> Dict[str, Any]:
    """Get entity registry via WebSocket with caching."""
    correlation_id = generate_correlation_id()
    
    if not HA_WEBSOCKET_ENABLED:
        return create_error_response('WebSocket not enabled', 'WEBSOCKET_DISABLED')
    
    # Check cache
    cache_key = 'ha_entity_registry_ws'
    if use_cache:
        cached = cache_get(cache_key)
        if cached:
            log_debug(f"[{correlation_id}] Using cached entity registry")
            increment_counter('ha_entity_registry_cache_hit')
            return cached
    
    try:
        from ha_config import load_ha_config
        config = load_ha_config()
        
        if not config.get('enabled'):
            return create_error_response('HA not enabled', 'HA_DISABLED')
        
        # Build WebSocket URL
        base_url = config['base_url'].replace('http://', 'ws://').replace('https://', 'wss://')
        ws_url = f"{base_url}/api/websocket"
        
        log_info(f"[{correlation_id}] Fetching entity registry via WebSocket")
        
        # Connect
        conn_result = establish_websocket_connection(ws_url, timeout=HA_WEBSOCKET_TIMEOUT)
        if not conn_result.get('success'):
            return conn_result
        
        ws_id = conn_result.get('data', {}).get('ws_id')
        
        try:
            # Authenticate
            auth_result = authenticate_websocket(ws_id, config['access_token'])
            if not auth_result.get('success'):
                return auth_result
            
            # Request entity registry
            registry_result = websocket_request(
                ws_id,
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
                
                increment_counter('ha_entity_registry_ws_success')
                log_info(f"[{correlation_id}] Retrieved {len(entities)} entities via WebSocket")
                
                return response
            
            return registry_result
            
        finally:
            # Always close connection
            close_websocket_connection(ws_id)
        
    except Exception as e:
        log_error(f"[{correlation_id}] Entity registry fetch failed: {str(e)}")
        increment_counter('ha_entity_registry_ws_error')
        return create_error_response(str(e), 'ENTITY_REGISTRY_FAILED')


def filter_exposed_entities(entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Filter entities to only exposed ones."""
    correlation_id = generate_correlation_id()
    
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
        
        log_info(f"[{correlation_id}] Filtered to {len(exposed)}/{len(entities)} exposed entities")
        return exposed
        
    except Exception as e:
        log_error(f"[{correlation_id}] Entity filtering failed: {str(e)}")
        return entities


# ===== FEATURE CHECK =====

def is_websocket_enabled() -> bool:
    """Check if WebSocket feature is enabled."""
    return HA_WEBSOCKET_ENABLED


# EOF
