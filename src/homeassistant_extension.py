"""
homeassistant_extension.py - Home Assistant Extension SUGA Facade
Version: 2025.10.18.07
Description: Pure facade for Home Assistant extension - delegates all operations
             to internal modules. This is the ONLY file lambda_function.py imports.

CHANGELOG:
- 2025.10.18.07: Added DEBUG_MODE-controlled debug logging at entry points
  - Added _is_debug_mode() helper function
  - Added [DEBUG] logging controlled by DEBUG_MODE environment variable
  - Traces HA extension call path for troubleshooting
- 2025.10.16.01: Fixed all import names to match actual ha_core.py functions

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

# ===== DEBUG HELPER =====

def _is_debug_mode() -> bool:
    """Check if DEBUG_MODE is enabled."""
    return os.getenv('DEBUG_MODE', 'false').lower() == 'true'


# ===== EXTENSION CONTROL =====

def is_ha_extension_enabled() -> bool:
    """Check if Home Assistant extension is enabled."""
    enabled = os.getenv('HOME_ASSISTANT_ENABLED', 'false').lower() == 'true'
    if _is_debug_mode():
        log_info(f"[DEBUG] HOMEASSISTANT_EXTENSION: is_ha_extension_enabled called, result={enabled}")
    return enabled


def initialize_ha_extension(config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Initialize Home Assistant extension - delegates to ha_core."""
    if _is_debug_mode():
        log_info("[DEBUG] HOMEASSISTANT_EXTENSION: initialize_ha_extension called")
    
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
    if _is_debug_mode():
        log_info("[DEBUG] HOMEASSISTANT_EXTENSION: cleanup_ha_extension called")
    
    try:
        from ha_core import cleanup_ha_system
        log_info("Cleaning up Home Assistant extension")
        return cleanup_ha_system()
    except Exception as e:
        log_error(f"Extension cleanup failed: {str(e)}")
        return create_error_response(str(e), 'CLEANUP_FAILED')


def get_ha_status() -> Dict[str, Any]:
    """Get Home Assistant connection status - delegates to ha_core."""
    if _is_debug_mode():
        log_info("[DEBUG] HOMEASSISTANT_EXTENSION: get_ha_status called")
    
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
    if _is_debug_mode():
        log_info("[DEBUG] HOMEASSISTANT_EXTENSION: get_ha_diagnostic_info called")
    
    try:
        from ha_core import get_diagnostic_info
        return get_diagnostic_info()
    except Exception as e:
        log_error(f"Diagnostic info failed: {str(e)}")
        return create_error_response(str(e), 'DIAGNOSTIC_FAILED')


def get_assistant_name_status() -> Dict[str, Any]:
    """Get assistant name configuration status - delegates to ha_core."""
    if _is_debug_mode():
        log_info("[DEBUG] HOMEASSISTANT_EXTENSION: get_assistant_name_status called")
    
    try:
        from ha_core import get_assistant_name_info
        return get_assistant_name_info()
    except Exception as e:
        log_error(f"Assistant name check failed: {str(e)}")
        return create_error_response(str(e), 'ASSISTANT_NAME_CHECK_FAILED')


# ===== ALEXA OPERATIONS =====

def process_alexa_ha_request(event: Dict[str, Any]) -> Dict[str, Any]:
    """Process Alexa Smart Home directive - delegates to ha_alexa."""
    if _is_debug_mode():
        log_info("[DEBUG] HOMEASSISTANT_EXTENSION: process_alexa_ha_request called")
        log_info(f"[DEBUG] HOMEASSISTANT_EXTENSION: event keys: {list(event.keys())}")
    
    if not is_ha_extension_enabled():
        return _create_alexa_error_response(event, 'BRIDGE_UNREACHABLE', 
                                           'Home Assistant extension disabled')
    
    try:
        if _is_debug_mode():
            log_info("[DEBUG] HOMEASSISTANT_EXTENSION: Importing ha_alexa.process_alexa_directive")
        from ha_alexa import process_alexa_directive
        return process_alexa_directive(event)
    except Exception as e:
        log_error(f"Alexa request processing failed: {str(e)}")
        return _create_alexa_error_response(event, 'INTERNAL_ERROR', str(e))


def handle_alexa_discovery(directive: Dict[str, Any]) -> Dict[str, Any]:
    """Handle Alexa discovery - delegates to ha_alexa."""
    correlation_id = generate_correlation_id()
    
    if _is_debug_mode():
        log_info(f"[{correlation_id}] [DEBUG ENTRY] HOMEASSISTANT_EXTENSION: handle_alexa_discovery called")
        log_info(f"[{correlation_id}] [DEBUG] HOMEASSISTANT_EXTENSION: directive keys: {list(directive.keys()) if isinstance(directive, dict) else 'NOT_DICT'}")
    
    if not is_ha_extension_enabled():
        if _is_debug_mode():
            log_error(f"[{correlation_id}] [DEBUG] HOMEASSISTANT_EXTENSION: Extension not enabled")
        return _create_alexa_error_response(directive, 'BRIDGE_UNREACHABLE',
                                           'Home Assistant extension disabled')
    
    try:
        if _is_debug_mode():
            log_info(f"[{correlation_id}] [DEBUG] HOMEASSISTANT_EXTENSION: Importing ha_alexa.handle_discovery")
        
        from ha_alexa import handle_discovery
        
        if _is_debug_mode():
            log_info(f"[{correlation_id}] [DEBUG] HOMEASSISTANT_EXTENSION: Calling ha_alexa.handle_discovery")
        
        result = handle_discovery(directive)
        
        if _is_debug_mode():
            log_info(f"[{correlation_id}] [DEBUG] HOMEASSISTANT_EXTENSION: ha_alexa.handle_discovery returned")
            log_info(f"[{correlation_id}] [DEBUG] HOMEASSISTANT_EXTENSION: result type: {type(result)}")
        
        return result
        
    except Exception as e:
        if _is_debug_mode():
            log_error(f"[{correlation_id}] [DEBUG EXCEPTION] HOMEASSISTANT_EXTENSION: {type(e).__name__}: {str(e)}")
            import traceback
            log_error(f"[{correlation_id}] [DEBUG TRACEBACK] HOMEASSISTANT_EXTENSION:\n{traceback.format_exc()}")
        log_error(f"Alexa discovery failed: {str(e)}")
        return _create_alexa_error_response(directive, 'INTERNAL_ERROR', str(e))


def handle_alexa_control(directive: Dict[str, Any]) -> Dict[str, Any]:
    """Handle Alexa control directive - delegates to ha_alexa."""
    if _is_debug_mode():
        log_info("[DEBUG] HOMEASSISTANT_EXTENSION: handle_alexa_control called")
    
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

def call_ha_service(domain: str, service: str, 
                   entity_id: Optional[str] = None,
                   service_data: Optional[Dict] = None) -> Dict[str, Any]:
    """Call Home Assistant service - delegates to ha_core."""
    if _is_debug_mode():
        log_info(f"[DEBUG] HOMEASSISTANT_EXTENSION: call_ha_service called: {domain}.{service}")
    
    if not is_ha_extension_enabled():
        return create_error_response('Extension not enabled', 'HA_DISABLED')
    
    try:
        from ha_core import call_ha_service as _call_ha_service
        return _call_ha_service(domain, service, entity_id, service_data)
    except Exception as e:
        log_error(f"Service call failed: {str(e)}")
        return create_error_response(str(e), 'SERVICE_CALL_FAILED')


def get_ha_states(entity_ids: Optional[List[str]] = None) -> Dict[str, Any]:
    """Get Home Assistant entity states - delegates to ha_core."""
    if _is_debug_mode():
        log_info(f"[DEBUG] HOMEASSISTANT_EXTENSION: get_ha_states called with entity_ids={entity_ids}")
    
    if not is_ha_extension_enabled():
        return create_error_response('Extension not enabled', 'HA_DISABLED')
    
    try:
        from ha_core import get_ha_states as _get_ha_states
        return _get_ha_states(entity_ids)
    except Exception as e:
        log_error(f"Get states failed: {str(e)}")
        return create_error_response(str(e), 'GET_STATES_FAILED')


def get_ha_entity_state(entity_id: str) -> Dict[str, Any]:
    """Get single entity state - delegates to ha_common."""
    if _is_debug_mode():
        log_info(f"[DEBUG] HOMEASSISTANT_EXTENSION: get_ha_entity_state called for {entity_id}")
    
    if not is_ha_extension_enabled():
        return create_error_response('Extension not enabled', 'HA_DISABLED')
    
    try:
        from ha_common import get_entity_state
        return get_entity_state(entity_id)
    except Exception as e:
        log_error(f"Get entity state failed: {str(e)}")
        return create_error_response(str(e), 'GET_ENTITY_STATE_FAILED')


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
        return _trigger_automation(automation_id, skip_condition)
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


def run_script(script_id: str, variables: Optional[Dict] = None) -> Dict[str, Any]:
    """Run script - delegates to ha_features."""
    if not is_ha_extension_enabled():
        return create_error_response('Extension not enabled', 'HA_DISABLED')
    
    try:
        from ha_features import run_script as _run_script
        return _run_script(script_id, variables)
    except Exception as e:
        log_error(f"Run script failed: {str(e)}")
        return create_error_response(str(e), 'RUN_SCRIPT_FAILED')


# ===== COMMUNICATION OPERATIONS =====

def process_conversation(text: str, conversation_id: Optional[str] = None) -> Dict[str, Any]:
    """Process conversation - delegates to ha_features."""
    if not is_ha_extension_enabled():
        return create_error_response('Extension not enabled', 'HA_DISABLED')
    
    try:
        from ha_features import process_conversation as _process_conversation
        return _process_conversation(text, conversation_id)
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


# ===== UTILITY FUNCTIONS =====

def _create_alexa_error_response(event: Dict[str, Any], error_type: str,
                                error_message: str) -> Dict[str, Any]:
    """Create Alexa-formatted error response."""
    directive = event.get("directive", {})
    header = directive.get("header", {})
    
    return {
        "event": {
            "header": {
                "namespace": "Alexa",
                "name": "ErrorResponse",
                "messageId": header.get("messageId"),
                "correlationToken": header.get("correlationToken"),
                "payloadVersion": "3"
            },
            "endpoint": {},
            "payload": {
                "type": error_type,
                "message": error_message
            }
        }
    }


# Export public API
__all__ = [
    # Control
    'is_ha_extension_enabled',
    'initialize_ha_extension',
    'cleanup_ha_extension',
    'get_ha_status',
    'get_ha_diagnostic_info',
    'get_assistant_name_status',
    
    # Alexa
    'process_alexa_ha_request',
    'handle_alexa_discovery',
    'handle_alexa_control',
    
    # Services
    'call_ha_service',
    'get_ha_states',
    'get_ha_entity_state',
    
    # Automations
    'list_automations',
    'trigger_automation',
    
    # Scripts
    'list_scripts',
    'run_script',
    
    # Communication
    'process_conversation',
    'send_notification',
    
    # Input Helpers
    'list_input_helpers',
    'set_input_helper',
    
    # Entity Management
    'list_entities_by_domain',
    'manage_device',
    'manage_area',
]

# EOF
