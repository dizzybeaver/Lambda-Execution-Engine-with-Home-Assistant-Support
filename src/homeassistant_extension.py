"""
homeassistant_extension.py - Home Assistant Extension SUGA Facade
Version: 2025.10.19.02
Description: Pure facade with extensive DEBUG logging

Copyright 2025 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

import os
from typing import Dict, Any, Optional, List

from gateway import (
    log_info, log_error, log_debug, log_warning,
    cache_get, cache_set, cache_delete,
    increment_counter, record_metric,
    create_success_response, create_error_response,
    generate_correlation_id, get_timestamp
)


def _debug(msg: str):
    """Print debug unconditionally."""
    print(f"[DEBUG] HA_EXT: {msg}")


def _is_debug_mode() -> bool:
    """Check if DEBUG_MODE is enabled."""
    return os.getenv('DEBUG_MODE', 'false').lower() == 'true'


# ===== EXTENSION CONTROL =====

def is_ha_extension_enabled() -> bool:
    """Check if Home Assistant extension is enabled."""
    _debug("is_ha_extension_enabled() called")
    enabled = os.getenv('HOME_ASSISTANT_ENABLED', 'false').lower() == 'true'
    _debug(f"is_ha_extension_enabled() returning: {enabled}")
    return enabled


def initialize_ha_extension(config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Initialize Home Assistant extension - delegates to ha_core."""
    _debug("initialize_ha_extension() called")
    
    if not is_ha_extension_enabled():
        _debug("initialize_ha_extension() - extension NOT enabled")
        return create_error_response('Extension not enabled', 'HA_DISABLED')
    
    try:
        _debug("initialize_ha_extension() - importing ha_core")
        from ha_core import initialize_ha_system
        _debug("initialize_ha_extension() - calling initialize_ha_system")
        log_info("Initializing Home Assistant extension")
        result = initialize_ha_system(config)
        _debug(f"initialize_ha_extension() - initialize_ha_system returned: {type(result)}")
        return result
    except Exception as e:
        _debug(f"initialize_ha_extension() - EXCEPTION: {type(e).__name__}: {e}")
        log_error(f"Extension initialization failed: {str(e)}")
        return create_error_response(str(e), 'INIT_FAILED')


def cleanup_ha_extension() -> Dict[str, Any]:
    """Cleanup Home Assistant extension resources."""
    _debug("cleanup_ha_extension() called")
    
    if not is_ha_extension_enabled():
        _debug("cleanup_ha_extension() - extension NOT enabled")
        return create_error_response('Extension not enabled', 'HA_DISABLED')
    
    try:
        _debug("cleanup_ha_extension() - importing ha_core")
        from ha_core import cleanup_ha_system
        _debug("cleanup_ha_extension() - calling cleanup_ha_system")
        result = cleanup_ha_system()
        _debug(f"cleanup_ha_extension() - cleanup_ha_system returned: {type(result)}")
        return result
    except Exception as e:
        _debug(f"cleanup_ha_extension() - EXCEPTION: {type(e).__name__}: {e}")
        log_error(f"Extension cleanup failed: {str(e)}")
        return create_error_response(str(e), 'CLEANUP_FAILED')


def get_ha_status() -> Dict[str, Any]:
    """Get Home Assistant extension status."""
    _debug("get_ha_status() called")
    
    if not is_ha_extension_enabled():
        _debug("get_ha_status() - extension NOT enabled")
        return create_error_response('Extension not enabled', 'HA_DISABLED')
    
    try:
        _debug("get_ha_status() - importing ha_core")
        from ha_core import get_ha_system_status
        _debug("get_ha_status() - calling get_ha_system_status")
        result = get_ha_system_status()
        _debug(f"get_ha_status() - returned: {type(result)}")
        return result
    except Exception as e:
        _debug(f"get_ha_status() - EXCEPTION: {type(e).__name__}: {e}")
        log_error(f"Get status failed: {str(e)}")
        return create_error_response(str(e), 'STATUS_FAILED')


def get_ha_diagnostic_info() -> Dict[str, Any]:
    """Get diagnostic information."""
    _debug("get_ha_diagnostic_info() called")
    
    if not is_ha_extension_enabled():
        _debug("get_ha_diagnostic_info() - extension NOT enabled")
        return {}
    
    try:
        _debug("get_ha_diagnostic_info() - importing ha_core")
        from ha_core import get_diagnostic_information
        _debug("get_ha_diagnostic_info() - calling get_diagnostic_information")
        result = get_diagnostic_information()
        _debug(f"get_ha_diagnostic_info() - returned: {type(result)}")
        return result
    except Exception as e:
        _debug(f"get_ha_diagnostic_info() - EXCEPTION: {type(e).__name__}: {e}")
        log_error(f"Diagnostic info failed: {str(e)}")
        return {}


def get_assistant_name_status() -> Dict[str, Any]:
    """Check assistant name availability."""
    _debug("get_assistant_name_status() called")
    
    try:
        _debug("get_assistant_name_status() - importing ha_core")
        from ha_core import get_assistant_name_info
        _debug("get_assistant_name_status() - calling get_assistant_name_info")
        result = get_assistant_name_info()
        _debug(f"get_assistant_name_status() - returned: {type(result)}")
        return result
    except Exception as e:
        _debug(f"get_assistant_name_status() - EXCEPTION: {type(e).__name__}: {e}")
        log_error(f"Assistant name check failed: {str(e)}")
        return create_error_response(str(e), 'ASSISTANT_NAME_CHECK_FAILED')


# ===== ALEXA OPERATIONS =====

def process_alexa_ha_request(event: Dict[str, Any]) -> Dict[str, Any]:
    """Process Alexa Smart Home directive."""
    _debug("═══════════════════════════════════════════")
    _debug("process_alexa_ha_request() called")
    _debug(f"process_alexa_ha_request() - event keys: {list(event.keys())}")
    
    if not is_ha_extension_enabled():
        _debug("process_alexa_ha_request() - extension NOT enabled")
        return _create_alexa_error_response(event, 'BRIDGE_UNREACHABLE', 
                                           'Home Assistant extension disabled')
    
    try:
        _debug("process_alexa_ha_request() - importing ha_alexa")
        from ha_alexa import process_alexa_directive
        _debug("process_alexa_ha_request() - calling process_alexa_directive")
        result = process_alexa_directive(event)
        _debug(f"process_alexa_ha_request() - returned: {type(result)}")
        return result
    except Exception as e:
        _debug(f"process_alexa_ha_request() - EXCEPTION: {type(e).__name__}: {e}")
        import traceback
        _debug(f"process_alexa_ha_request() - TRACEBACK:\n{traceback.format_exc()}")
        log_error(f"Alexa request processing failed: {str(e)}")
        return _create_alexa_error_response(event, 'INTERNAL_ERROR', str(e))


def handle_alexa_discovery(event: Dict[str, Any]) -> Dict[str, Any]:
    """Handle Alexa discovery."""
    correlation_id = generate_correlation_id()
    
    _debug("═══════════════════════════════════════════")
    _debug(f"[{correlation_id}] handle_alexa_discovery() ENTRY")
    _debug(f"[{correlation_id}] handle_alexa_discovery() - event type: {type(event)}")
    _debug(f"[{correlation_id}] handle_alexa_discovery() - event keys: {list(event.keys())}")
    
    directive = event.get('directive', {})
    _debug(f"[{correlation_id}] handle_alexa_discovery() - directive type: {type(directive)}")
    _debug(f"[{correlation_id}] handle_alexa_discovery() - directive keys: {list(directive.keys()) if isinstance(directive, dict) else 'NOT_DICT'}")
    
    if not is_ha_extension_enabled():
        _debug(f"[{correlation_id}] handle_alexa_discovery() - extension NOT enabled")
        return _create_alexa_error_response(event, 'BRIDGE_UNREACHABLE',
                                           'Home Assistant extension disabled')
    
    try:
        _debug(f"[{correlation_id}] handle_alexa_discovery() - importing ha_alexa.handle_discovery")
        from ha_alexa import handle_discovery
        _debug(f"[{correlation_id}] handle_alexa_discovery() - ha_alexa imported successfully")
        
        _debug(f"[{correlation_id}] handle_alexa_discovery() - calling handle_discovery(event)")
        result = handle_discovery(event)
        _debug(f"[{correlation_id}] handle_alexa_discovery() - handle_discovery returned")
        _debug(f"[{correlation_id}] handle_alexa_discovery() - result type: {type(result)}")
        _debug(f"[{correlation_id}] handle_alexa_discovery() - result keys: {list(result.keys()) if isinstance(result, dict) else 'NOT_DICT'}")
        
        return result
        
    except Exception as e:
        _debug(f"[{correlation_id}] handle_alexa_discovery() - EXCEPTION: {type(e).__name__}: {e}")
        import traceback
        _debug(f"[{correlation_id}] handle_alexa_discovery() - TRACEBACK:\n{traceback.format_exc()}")
        log_error(f"[{correlation_id}] Alexa discovery failed: {str(e)}")
        return _create_alexa_error_response(event, 'INTERNAL_ERROR', str(e))


def handle_alexa_authorization(event: Dict[str, Any]) -> Dict[str, Any]:
    """Handle Alexa authorization (AcceptGrant)."""
    correlation_id = generate_correlation_id()
    
    _debug("═══════════════════════════════════════════")
    _debug(f"[{correlation_id}] handle_alexa_authorization() ENTRY")
    
    if not is_ha_extension_enabled():
        _debug(f"[{correlation_id}] handle_alexa_authorization() - extension NOT enabled")
        return _create_alexa_error_response(event, 'BRIDGE_UNREACHABLE',
                                           'Home Assistant extension disabled')
    
    try:
        _debug(f"[{correlation_id}] handle_alexa_authorization() - importing ha_alexa.handle_accept_grant")
        from ha_alexa import handle_accept_grant
        _debug(f"[{correlation_id}] handle_alexa_authorization() - calling handle_accept_grant")
        result = handle_accept_grant(event)
        _debug(f"[{correlation_id}] handle_alexa_authorization() - returned: {type(result)}")
        return result
    except Exception as e:
        _debug(f"[{correlation_id}] handle_alexa_authorization() - EXCEPTION: {type(e).__name__}: {e}")
        log_error(f"[{correlation_id}] Alexa authorization failed: {str(e)}")
        return _create_alexa_error_response(event, 'INTERNAL_ERROR', str(e))


def handle_alexa_control(event: Dict[str, Any]) -> Dict[str, Any]:
    """Handle Alexa control directive."""
    correlation_id = generate_correlation_id()
    
    _debug("═══════════════════════════════════════════")
    _debug(f"[{correlation_id}] handle_alexa_control() ENTRY")
    
    if not is_ha_extension_enabled():
        _debug(f"[{correlation_id}] handle_alexa_control() - extension NOT enabled")
        return _create_alexa_error_response(event, 'ENDPOINT_UNREACHABLE',
                                           'Home Assistant extension disabled')
    
    try:
        _debug(f"[{correlation_id}] handle_alexa_control() - importing ha_alexa.handle_control")
        from ha_alexa import handle_control
        _debug(f"[{correlation_id}] handle_alexa_control() - calling handle_control")
        result = handle_control(event)
        _debug(f"[{correlation_id}] handle_alexa_control() - returned: {type(result)}")
        return result
    except Exception as e:
        _debug(f"[{correlation_id}] handle_alexa_control() - EXCEPTION: {type(e).__name__}: {e}")
        log_error(f"[{correlation_id}] Alexa control failed: {str(e)}")
        return _create_alexa_error_response(event, 'INTERNAL_ERROR', str(e))


# ===== UTILITY FUNCTIONS =====

def _create_alexa_error_response(event: Dict[str, Any], error_type: str,
                                error_message: str) -> Dict[str, Any]:
    """Create Alexa-formatted error response."""
    _debug(f"_create_alexa_error_response() called: {error_type} - {error_message}")
    
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
    'is_ha_extension_enabled',
    'initialize_ha_extension',
    'cleanup_ha_extension',
    'get_ha_status',
    'get_ha_diagnostic_info',
    'get_assistant_name_status',
    'process_alexa_ha_request',
    'handle_alexa_discovery',
    'handle_alexa_authorization',
    'handle_alexa_control',
]

# EOF
