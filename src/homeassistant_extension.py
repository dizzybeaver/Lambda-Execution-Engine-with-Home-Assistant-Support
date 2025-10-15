"""
homeassistant_extension.py - Home Assistant Extension Facade
Version: 2025.10.14.01
Copyright 2025 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

import os
from typing import Dict, Any, Optional, Union
from gateway import (
    log_info, log_error, log_debug, cache_get, cache_set,
    get_parameter, create_success_response, create_error_response
)

HA_ASSISTANT_NAME_CACHE_KEY = "ha_assistant_name"

# ===== EXTENSION STATUS =====

def is_ha_extension_enabled() -> bool:
    """Check if Home Assistant extension is enabled."""
    return os.getenv('HOME_ASSISTANT_ENABLED', 'false').lower() == 'true'

# ===== ALEXA SMART HOME =====

def process_alexa_ha_request(event: Dict[str, Any]) -> Dict[str, Any]:
    """Process Alexa Smart Home directive."""
    try:
        from ha_alexa import AlexaSmartHomeManager
        
        directive = event.get('directive', {})
        header = directive.get('header', {})
        namespace = header.get('namespace', '')
        name = header.get('name', '')
        
        log_info(f"Processing Alexa directive: {namespace}.{name}")
        
        manager = AlexaSmartHomeManager()
        
        if namespace == 'Alexa.Discovery' and name == 'Discover':
            result = manager.handle_discovery()
            return _format_discovery_response(result, header)
            
        elif namespace == 'Alexa.PowerController':
            result = manager.handle_power_control(directive)
            return result
            
        elif namespace == 'Alexa.BrightnessController':
            result = manager.handle_brightness_control(directive)
            return result
            
        elif namespace == 'Alexa.ThermostatController':
            result = manager.handle_thermostat_control(directive)
            return result
            
        elif namespace == 'Alexa.Authorization' and name == 'AcceptGrant':
            result = manager.handle_accept_grant(directive)
            return result
            
        else:
            log_error(f"Unsupported directive: {namespace}.{name}")
            return _create_error_response(
                header,
                'INVALID_DIRECTIVE',
                f'Directive {namespace}.{name} not supported'
            )
            
    except Exception as e:
        log_error(f"Alexa request processing failed: {str(e)}")
        return _create_error_response(
            event.get('directive', {}).get('header', {}),
            'INTERNAL_ERROR',
            str(e)
        )

def _format_discovery_response(result: Dict[str, Any], header: Dict[str, Any]) -> Dict[str, Any]:
    """Format discovery result as Alexa response."""
    if not result.get('success'):
        return _create_error_response(header, 'INTERNAL_ERROR', 
                                     result.get('message', 'Discovery failed'))
    
    endpoints = result.get('data', {}).get('endpoints', [])
    
    return {
        'event': {
            'header': {
                'namespace': 'Alexa.Discovery',
                'name': 'Discover.Response',
                'messageId': header.get('messageId', 'unknown'),
                'payloadVersion': '3'
            },
            'payload': {
                'endpoints': endpoints
            }
        }
    }

def _create_error_response(header: Dict[str, Any], error_type: str, message: str) -> Dict[str, Any]:
    """Create Alexa error response."""
    return {
        'event': {
            'header': {
                'namespace': 'Alexa',
                'name': 'ErrorResponse',
                'messageId': header.get('messageId', 'unknown'),
                'payloadVersion': '3'
            },
            'payload': {
                'type': error_type,
                'message': message
            }
        }
    }

# ===== CONFIGURATION & STATUS =====

def get_ha_assistant_name() -> str:
    """Get configured assistant name with caching."""
    cached = cache_get(HA_ASSISTANT_NAME_CACHE_KEY)
    if cached:
        return cached
    
    name = os.getenv('HA_ASSISTANT_NAME', '')
    
    if not name:
        name = get_parameter('home_assistant_assistant_name', 'Home Assistant')
    
    cache_set(HA_ASSISTANT_NAME_CACHE_KEY, name, ttl=3600)
    return name

def get_ha_status() -> Dict[str, Any]:
    """Get Home Assistant connection status."""
    from ha_core import is_ha_available
    
    try:
        if not is_ha_extension_enabled():
            return create_error_response('disabled', 'Extension not enabled')
        
        available = is_ha_available()
        
        if available:
            return create_success_response('HA is available', {'available': True})
        else:
            return create_error_response('unavailable', 'HA temporarily unavailable')
            
    except Exception as e:
        log_error(f"HA status check failed: {str(e)}")
        return create_error_response('error', str(e))

def get_ha_diagnostic_info() -> Dict[str, Any]:
    """Get comprehensive diagnostic information."""
    from ha_core import is_ha_available, get_ha_config
    
    try:
        config = get_ha_config()
        
        diagnostic_data = {
            'ha_enabled': is_ha_extension_enabled(),
            'ha_available': is_ha_available(),
            'connection_status': 'connected' if is_ha_available() else 'disconnected',
            'base_url_configured': bool(config.get('base_url')),
            'token_configured': bool(config.get('access_token')),
            'timeout': config.get('timeout', 30),
            'assistant_name': get_ha_assistant_name()
        }
        
        return create_success_response('Diagnostics retrieved', diagnostic_data)
        
    except Exception as e:
        log_error(f"Diagnostic retrieval failed: {str(e)}")
        return create_error_response('error', str(e))

def get_assistant_name_status() -> Dict[str, Any]:
    """Get assistant name configuration status."""
    try:
        name = get_ha_assistant_name()
        
        return create_success_response('Assistant name retrieved', {
            'assistant_name': name,
            'configured': bool(name and name != 'Home Assistant'),
            'source': 'environment' if os.getenv('HA_ASSISTANT_NAME') else 'parameter_store'
        })
        
    except Exception as e:
        log_error(f"Assistant name status failed: {str(e)}")
        return create_error_response('error', str(e))

def get_ha_config_summary(show_sensitive: bool = False) -> Dict[str, Any]:
    """Get HA configuration summary for diagnostics."""
    from ha_core import get_ha_config
    
    try:
        config = get_ha_config()
        
        summary = {
            'enabled': is_ha_extension_enabled(),
            'base_url_configured': bool(config.get('base_url')),
            'token_configured': bool(config.get('access_token')),
            'timeout': config.get('timeout', 30),
            'verify_ssl': config.get('verify_ssl', True)
        }
        
        if show_sensitive:
            base_url = config.get('base_url', '')
            token = config.get('access_token', '')
            summary['base_url'] = base_url[:30] + '...' if len(base_url) > 30 else base_url
            summary['token'] = token[:20] + '...' if len(token) > 20 else token
        
        return summary
        
    except Exception as e:
        log_error(f"Config summary failed: {str(e)}")
        return {'error': str(e)}

# ===== CONVERSATION =====

def process_conversation(query: str, ha_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Process conversation query with Home Assistant.
    
    Args:
        query: User query text
        ha_config: Optional HA configuration
        
    Returns:
        Dict with success status and response text
    """
    from ha_features import process_conversation as _process
    
    try:
        if not is_ha_extension_enabled():
            return create_error_response('disabled', 'Extension not enabled')
        
        log_info(f"Processing conversation: {query}")
        return _process(query, ha_config)
        
    except Exception as e:
        log_error(f"Conversation processing failed: {str(e)}")
        return create_error_response('error', str(e))

# ===== AUTOMATIONS =====

def trigger_automation(automation_name: str, ha_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Trigger Home Assistant automation.
    
    Args:
        automation_name: Automation name or ID
        ha_config: Optional HA configuration
        
    Returns:
        Dict with success status
    """
    from ha_features import trigger_automation as _trigger
    
    try:
        if not is_ha_extension_enabled():
            return create_error_response('disabled', 'Extension not enabled')
        
        log_info(f"Triggering automation: {automation_name}")
        return _trigger(automation_name, ha_config)
        
    except Exception as e:
        log_error(f"Automation trigger failed: {str(e)}")
        return create_error_response('error', str(e))

# ===== SCRIPTS =====

def run_script(script_name: str, ha_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Run Home Assistant script.
    
    Args:
        script_name: Script name or ID
        ha_config: Optional HA configuration
        
    Returns:
        Dict with success status
    """
    from ha_features import run_script as _run
    
    try:
        if not is_ha_extension_enabled():
            return create_error_response('disabled', 'Extension not enabled')
        
        log_info(f"Running script: {script_name}")
        return _run(script_name, ha_config)
        
    except Exception as e:
        log_error(f"Script execution failed: {str(e)}")
        return create_error_response('error', str(e))

# ===== INPUT HELPERS =====

def set_input_helper(helper_id: str, value: Union[str, int, float, bool], 
                    ha_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Set Home Assistant input helper value.
    
    Args:
        helper_id: Helper entity ID (e.g., 'input_boolean.test')
        value: Value to set
        ha_config: Optional HA configuration
        
    Returns:
        Dict with success status
    """
    from ha_features import set_input_helper as _set
    
    try:
        if not is_ha_extension_enabled():
            return create_error_response('disabled', 'Extension not enabled')
        
        log_info(f"Setting input helper {helper_id} to {value}")
        return _set(helper_id, value, ha_config)
        
    except Exception as e:
        log_error(f"Input helper set failed: {str(e)}")
        return create_error_response('error', str(e))

# ===== NOTIFICATIONS =====

def send_notification(message: str, title: str = "", 
                     ha_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Send notification through Home Assistant.
    
    Args:
        message: Notification message
        title: Optional notification title
        ha_config: Optional HA configuration
        
    Returns:
        Dict with success status
    """
    from ha_features import send_notification as _send
    
    try:
        if not is_ha_extension_enabled():
            return create_error_response('disabled', 'Extension not enabled')
        
        log_info(f"Sending notification: {title or 'Untitled'}")
        return _send(message, title, ha_config)
        
    except Exception as e:
        log_error(f"Notification send failed: {str(e)}")
        return create_error_response('error', str(e))

# ===== TIMERS =====

def start_timer(timer_name: str, duration: int, 
               ha_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Start Home Assistant timer.
    
    Args:
        timer_name: Timer entity name
        duration: Duration in seconds
        ha_config: Optional HA configuration
        
    Returns:
        Dict with success status
    """
    from ha_core import call_ha_service, get_ha_config as _get_config
    
    try:
        if not is_ha_extension_enabled():
            return create_error_response('disabled', 'Extension not enabled')
        
        config = ha_config or _get_config()
        log_info(f"Starting timer {timer_name} for {duration}s")
        
        return call_ha_service(
            'timer',
            'start',
            config,
            f'timer.{timer_name}',
            {'duration': duration}
        )
        
    except Exception as e:
        log_error(f"Timer start failed: {str(e)}")
        return create_error_response('error', str(e))

def cancel_timer(timer_name: str, ha_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Cancel Home Assistant timer.
    
    Args:
        timer_name: Timer entity name
        ha_config: Optional HA configuration
        
    Returns:
        Dict with success status
    """
    from ha_core import call_ha_service, get_ha_config as _get_config
    
    try:
        if not is_ha_extension_enabled():
            return create_error_response('disabled', 'Extension not enabled')
        
        config = ha_config or _get_config()
        log_info(f"Cancelling timer {timer_name}")
        
        return call_ha_service('timer', 'cancel', config, f'timer.{timer_name}')
        
    except Exception as e:
        log_error(f"Timer cancel failed: {str(e)}")
        return create_error_response('error', str(e))

def pause_timer(timer_name: str, ha_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Pause Home Assistant timer.
    
    Args:
        timer_name: Timer entity name
        ha_config: Optional HA configuration
        
    Returns:
        Dict with success status
    """
    from ha_core import call_ha_service, get_ha_config as _get_config
    
    try:
        if not is_ha_extension_enabled():
            return create_error_response('disabled', 'Extension not enabled')
        
        config = ha_config or _get_config()
        log_info(f"Pausing timer {timer_name}")
        
        return call_ha_service('timer', 'pause', config, f'timer.{timer_name}')
        
    except Exception as e:
        log_error(f"Timer pause failed: {str(e)}")
        return create_error_response('error', str(e))

# ===== DEVICE & AREA CONTROL =====

def control_device(entity_id: str, action: str, 
                  service_data: Optional[Dict[str, Any]] = None,
                  ha_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Control Home Assistant device.
    
    Args:
        entity_id: Device entity ID
        action: Action/service to call (e.g., 'turn_on', 'turn_off')
        service_data: Optional service data
        ha_config: Optional HA configuration
        
    Returns:
        Dict with success status
    """
    from ha_core import call_ha_service, get_ha_config as _get_config
    
    try:
        if not is_ha_extension_enabled():
            return create_error_response('disabled', 'Extension not enabled')
        
        if '.' not in entity_id:
            return create_error_response('invalid_entity', 'Entity ID must include domain')
        
        domain = entity_id.split('.')[0]
        config = ha_config or _get_config()
        
        log_info(f"Controlling device {entity_id}: {action}")
        
        return call_ha_service(domain, action, config, entity_id, service_data)
        
    except Exception as e:
        log_error(f"Device control failed: {str(e)}")
        return create_error_response('error', str(e))

def get_area_devices(area_name: str, ha_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Get devices in a Home Assistant area.
    
    Args:
        area_name: Area name
        ha_config: Optional HA configuration
        
    Returns:
        Dict with success status and device list
    """
    from ha_core import batch_get_states, get_ha_config as _get_config
    
    try:
        if not is_ha_extension_enabled():
            return create_error_response('disabled', 'Extension not enabled')
        
        config = ha_config or _get_config()
        log_info(f"Getting devices for area: {area_name}")
        
        # Get all states
        states_result = batch_get_states(None, config, use_cache=True)
        
        if not states_result.get('success'):
            return states_result
        
        states = states_result.get('data', [])
        
        # Filter by area (area info typically in attributes)
        area_devices = [
            state for state in states
            if state.get('attributes', {}).get('area_id') == area_name.lower().replace(' ', '_')
            or state.get('attributes', {}).get('friendly_name', '').lower().startswith(area_name.lower())
        ]
        
        return create_success_response(
            f'Found {len(area_devices)} devices in {area_name}',
            {'devices': area_devices, 'count': len(area_devices)}
        )
        
    except Exception as e:
        log_error(f"Area device retrieval failed: {str(e)}")
        return create_error_response('error', str(e))

# ===== EXPORTS =====

__all__ = [
    # Status
    'is_ha_extension_enabled',
    'get_ha_status',
    'get_ha_assistant_name',
    'get_ha_diagnostic_info',
    'get_assistant_name_status',
    'get_ha_config_summary',
    
    # Alexa Smart Home
    'process_alexa_ha_request',
    
    # Conversation
    'process_conversation',
    
    # Automations
    'trigger_automation',
    
    # Scripts
    'run_script',
    
    # Input Helpers
    'set_input_helper',
    
    # Notifications
    'send_notification',
    
    # Timers
    'start_timer',
    'cancel_timer',
    'pause_timer',
    
    # Device & Area Control
    'control_device',
    'get_area_devices',
]

# EOF
