"""
homeassistant_extension.py - Home Assistant Extension SUGA Facade
Version: 2025.10.14.01
Description: Pure facade for Home Assistant extension - delegates all operations
             to internal modules. This is the ONLY file lambda_function.py imports.

Copyright 2025 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

import os
from typing import Dict, Any, Optional, List

# Only import from Gateway and lazy import internals
from gateway import (
    log_info, log_error, log_debug, log_warning,
    cache_get, cache_set, cache_delete,
    increment_counter, record_metric,
    create_success_response, create_error_response,
    generate_correlation_id, get_timestamp
)

# ===== EXTENSION CONTROL =====

def is_ha_extension_enabled() -> bool:
    """Check if Home Assistant extension is enabled."""
    return os.getenv('HOME_ASSISTANT_ENABLED', 'false').lower() == 'true'


def initialize_ha_extension(config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Initialize Home Assistant extension - delegates to ha_core."""
    if not is_ha_extension_enabled():
        return create_error_response('Extension not enabled', 'HA_DISABLED')
    
    try:
        from ha_core import initialize_ha_system
        log_info("Initializing Home Assistant extension")
        return initialize_ha_system(config)
    except Exception as e:
        log_error(f"Extension initialization failed: {str(e)}")
        return create_error_response(str(e), 'INIT_FAILED')


def cleanup_ha_extension() -> Dict[str, Any]:
    """Cleanup Home Assistant extension resources - delegates to ha_core."""
    try:
        from ha_core import cleanup_ha_system
        log_info("Cleaning up Home Assistant extension")
        return cleanup_ha_system()
    except Exception as e:
        log_error(f"Extension cleanup failed: {str(e)}")
        return create_error_response(str(e), 'CLEANUP_FAILED')


def get_ha_status() -> Dict[str, Any]:
    """Get Home Assistant connection status - delegates to ha_core."""
    if not is_ha_extension_enabled():
        return create_success_response("Extension disabled", {'enabled': False})
    
    try:
        from ha_core import check_ha_status
        return check_ha_status()
    except Exception as e:
        log_error(f"Status check failed: {str(e)}")
        return create_error_response(str(e), 'STATUS_CHECK_FAILED')


def get_ha_diagnostic_info() -> Dict[str, Any]:
    """Get diagnostic information - delegates to ha_core."""
    try:
        from ha_core import get_diagnostic_info
        return get_diagnostic_info()
    except Exception as e:
        log_error(f"Diagnostic info failed: {str(e)}")
        return create_error_response(str(e), 'DIAGNOSTIC_FAILED')


# ===== ALEXA OPERATIONS =====

def process_alexa_ha_request(event: Dict[str, Any]) -> Dict[str, Any]:
    """Process Alexa Smart Home directive - delegates to ha_alexa."""
    if not is_ha_extension_enabled():
        return _create_alexa_error_response(event, 'BRIDGE_UNREACHABLE', 
                                           'Home Assistant extension disabled')
    
    try:
        from ha_alexa import process_alexa_directive
        return process_alexa_directive(event)
    except Exception as e:
        log_error(f"Alexa request processing failed: {str(e)}")
        return _create_alexa_error_response(event, 'INTERNAL_ERROR', str(e))


def handle_alexa_discovery(directive: Dict[str, Any]) -> Dict[str, Any]:
    """Handle Alexa discovery - delegates to ha_alexa."""
    if not is_ha_extension_enabled():
        return _create_alexa_error_response(directive, 'BRIDGE_UNREACHABLE',
                                           'Home Assistant extension disabled')
    
    try:
        from ha_alexa import handle_discovery
        return handle_discovery(directive)
    except Exception as e:
        log_error(f"Alexa discovery failed: {str(e)}")
        return _create_alexa_error_response(directive, 'INTERNAL_ERROR', str(e))


def handle_alexa_control(directive: Dict[str, Any]) -> Dict[str, Any]:
    """Handle Alexa control directive - delegates to ha_alexa."""
    if not is_ha_extension_enabled():
        return _create_alexa_error_response(directive, 'ENDPOINT_UNREACHABLE',
                                           'Home Assistant extension disabled')
    
    try:
        from ha_alexa import handle_control
        return handle_control(directive)
    except Exception as e:
        log_error(f"Alexa control failed: {str(e)}")
        return _create_alexa_error_response(directive, 'INTERNAL_ERROR', str(e))


# ===== SERVICE OPERATIONS =====

def call_ha_service(domain: str, service: str, entity_id: Optional[str] = None,
                   service_data: Optional[Dict] = None) -> Dict[str, Any]:
    """Call Home Assistant service - delegates to ha_core."""
    if not is_ha_extension_enabled():
        return create_error_response('Extension not enabled', 'HA_DISABLED')
    
    try:
        from ha_core import call_service
        return call_service(domain, service, entity_id, service_data)
    except Exception as e:
        log_error(f"Service call failed: {str(e)}")
        return create_error_response(str(e), 'SERVICE_CALL_FAILED')


def get_ha_states(entity_ids: Optional[List[str]] = None) -> Dict[str, Any]:
    """Get Home Assistant entity states - delegates to ha_core."""
    if not is_ha_extension_enabled():
        return create_error_response('Extension not enabled', 'HA_DISABLED')
    
    try:
        from ha_core import get_states
        return get_states(entity_ids)
    except Exception as e:
        log_error(f"Get states failed: {str(e)}")
        return create_error_response(str(e), 'GET_STATES_FAILED')


def get_ha_entity_state(entity_id: str) -> Dict[str, Any]:
    """Get single entity state - delegates to ha_core."""
    if not is_ha_extension_enabled():
        return create_error_response('Extension not enabled', 'HA_DISABLED')
    
    try:
        from ha_core import get_entity_state
        return get_entity_state(entity_id)
    except Exception as e:
        log_error(f"Get entity state failed: {str(e)}")
        return create_error_response(str(e), 'GET_STATE_FAILED')


# ===== AUTOMATION OPERATIONS =====

def list_automations() -> Dict[str, Any]:
    """List automations - delegates to ha_features."""
    if not is_ha_extension_enabled():
        return create_error_response('Extension not enabled', 'HA_DISABLED')
    
    try:
        from ha_features import list_automations as _list_automations
        return _list_automations()
    except Exception as e:
        log_error(f"List automations failed: {str(e)}")
        return create_error_response(str(e), 'LIST_AUTOMATIONS_FAILED')


def trigger_automation(automation_id: str, skip_condition: bool = False) -> Dict[str, Any]:
    """Trigger automation - delegates to ha_features."""
    if not is_ha_extension_enabled():
        return create_error_response('Extension not enabled', 'HA_DISABLED')
    
    try:
        from ha_features import trigger_automation as _trigger_automation
        return _trigger_automation(automation_id, skip_condition=skip_condition)
    except Exception as e:
        log_error(f"Trigger automation failed: {str(e)}")
        return create_error_response(str(e), 'TRIGGER_AUTOMATION_FAILED')


# ===== SCRIPT OPERATIONS =====

def list_scripts() -> Dict[str, Any]:
    """List scripts - delegates to ha_features."""
    if not is_ha_extension_enabled():
        return create_error_response('Extension not enabled', 'HA_DISABLED')
    
    try:
        from ha_features import list_scripts as _list_scripts
        return _list_scripts()
    except Exception as e:
        log_error(f"List scripts failed: {str(e)}")
        return create_error_response(str(e), 'LIST_SCRIPTS_FAILED')


def run_script(script_id: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Run script - delegates to ha_features."""
    if not is_ha_extension_enabled():
        return create_error_response('Extension not enabled', 'HA_DISABLED')
    
    try:
        from ha_features import run_script as _run_script
        return _run_script(script_id, variables)
    except Exception as e:
        log_error(f"Run script failed: {str(e)}")
        return create_error_response(str(e), 'RUN_SCRIPT_FAILED')


# ===== CONVERSATION & NOTIFICATIONS =====

def process_conversation(query: str) -> Dict[str, Any]:
    """Process conversation query - delegates to ha_features."""
    if not is_ha_extension_enabled():
        return create_error_response('Extension not enabled', 'HA_DISABLED')
    
    try:
        from ha_features import process_conversation as _process_conversation
        return _process_conversation(query)
    except Exception as e:
        log_error(f"Process conversation failed: {str(e)}")
        return create_error_response(str(e), 'CONVERSATION_FAILED')


def send_notification(message: str, title: Optional[str] = None,
                     target: Optional[str] = None) -> Dict[str, Any]:
    """Send notification - delegates to ha_features."""
    if not is_ha_extension_enabled():
        return create_error_response('Extension not enabled', 'HA_DISABLED')
    
    try:
        from ha_features import send_notification as _send_notification
        return _send_notification(message, title, target)
    except Exception as e:
        log_error(f"Send notification failed: {str(e)}")
        return create_error_response(str(e), 'NOTIFICATION_FAILED')


# ===== INPUT HELPER OPERATIONS =====

def list_input_helpers(helper_type: Optional[str] = None) -> Dict[str, Any]:
    """List input helpers - delegates to ha_features."""
    if not is_ha_extension_enabled():
        return create_error_response('Extension not enabled', 'HA_DISABLED')
    
    try:
        from ha_features import list_input_helpers as _list_input_helpers
        return _list_input_helpers(helper_type)
    except Exception as e:
        log_error(f"List input helpers failed: {str(e)}")
        return create_error_response(str(e), 'LIST_HELPERS_FAILED')


def set_input_helper(helper_id: str, value: Any) -> Dict[str, Any]:
    """Set input helper value - delegates to ha_features."""
    if not is_ha_extension_enabled():
        return create_error_response('Extension not enabled', 'HA_DISABLED')
    
    try:
        from ha_features import set_input_helper as _set_input_helper
        return _set_input_helper(helper_id, value)
    except Exception as e:
        log_error(f"Set input helper failed: {str(e)}")
        return create_error_response(str(e), 'SET_HELPER_FAILED')


# ===== ENTITY MANAGEMENT =====

def list_entities_by_domain(domain: str, filters: Optional[Dict] = None) -> Dict[str, Any]:
    """List entities by domain - delegates to ha_managers."""
    if not is_ha_extension_enabled():
        return create_error_response('Extension not enabled', 'HA_DISABLED')
    
    try:
        from ha_managers import list_entities_by_domain as _list_entities
        return _list_entities(domain, filters)
    except Exception as e:
        log_error(f"List entities failed: {str(e)}")
        return create_error_response(str(e), 'LIST_ENTITIES_FAILED')


def manage_device(entity_id: str, action: str, parameters: Optional[Dict] = None) -> Dict[str, Any]:
    """Manage device - delegates to ha_managers."""
    if not is_ha_extension_enabled():
        return create_error_response('Extension not enabled', 'HA_DISABLED')
    
    try:
        from ha_managers import manage_device as _manage_device
        return _manage_device(entity_id, action, parameters)
    except Exception as e:
        log_error(f"Manage device failed: {str(e)}")
        return create_error_response(str(e), 'MANAGE_DEVICE_FAILED')


def manage_area(area_name: str, action: str, parameters: Optional[Dict] = None) -> Dict[str, Any]:
    """Manage area - delegates to ha_managers."""
    if not is_ha_extension_enabled():
        return create_error_response('Extension not enabled', 'HA_DISABLED')
    
    try:
        from ha_managers import manage_area as _manage_area
        return _manage_area(area_name, action, parameters)
    except Exception as e:
        log_error(f"Manage area failed: {str(e)}")
        return create_error_response(str(e), 'MANAGE_AREA_FAILED')


# ===== CONFIGURATION =====

def get_ha_assistant_name() -> str:
    """Get assistant name from configuration."""
    return os.getenv('HA_ASSISTANT_NAME', 'Jarvis')


def validate_assistant_name(name: str) -> Dict[str, Any]:
    """Validate assistant name."""
    if not name or not name.strip():
        return {'is_valid': False, 'error': 'Name cannot be empty'}
    
    if len(name) < 2:
        return {'is_valid': False, 'error': 'Name too short (min 2 characters)'}
    
    if len(name) > 25:
        return {'is_valid': False, 'error': 'Name too long (max 25 characters)'}
    
    reserved = ['alexa', 'amazon', 'echo']
    if name.lower() in reserved:
        return {'is_valid': False, 'error': f'Reserved name: {name}'}
    
    return {'is_valid': True}


# ===== INTERNAL HELPERS =====

def _create_alexa_error_response(event: Dict[str, Any], error_type: str, 
                                 message: str) -> Dict[str, Any]:
    """Create Alexa error response."""
    header = event.get('directive', {}).get('header', {})
    message_id = header.get('messageId', generate_correlation_id())
    
    return {
        'event': {
            'header': {
                'namespace': 'Alexa',
                'name': 'ErrorResponse',
                'messageId': message_id,
                'payloadVersion': '3'
            },
            'payload': {
                'type': error_type,
                'message': message
            }
        }
    }


def _get_ha_config_gateway() -> Dict[str, Any]:
    """Get HA config using gateway - internal helper."""
    from ha_config import load_ha_config
    return load_ha_config()


# EOF
