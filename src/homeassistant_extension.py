"""
homeassistant_extension.py - Home Assistant Extension SUGA Facade
Version: 2025.10.19.03
Description: Pure facade for Home Assistant extension

CHANGELOG:
- 2025.10.19.03: Removed debug logging statements
- 2025.10.19.02: Added extensive DEBUG logging
- 2025.10.19.01: Initial version with SUGA-ISP compliance

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


def _is_debug_mode() -> bool:
    """Check if DEBUG_MODE is enabled."""
    return os.getenv('DEBUG_MODE', 'false').lower() == 'true'


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
    """Cleanup Home Assistant extension resources."""
    
    if not is_ha_extension_enabled():
        return create_error_response('Extension not enabled', 'HA_DISABLED')
    
    try:
        from ha_core import cleanup_ha_system
        result = cleanup_ha_system()
        return result
    except Exception as e:
        log_error(f"Extension cleanup failed: {str(e)}")
        return create_error_response(str(e), 'CLEANUP_FAILED')


def get_ha_status() -> Dict[str, Any]:
    """Get Home Assistant extension status."""
    
    if not is_ha_extension_enabled():
        return create_error_response('Extension not enabled', 'HA_DISABLED')
    
    try:
        from ha_core import get_ha_system_status
        return get_ha_system_status()
    except Exception as e:
        log_error(f"Get status failed: {str(e)}")
        return create_error_response(str(e), 'STATUS_FAILED')


def get_ha_diagnostic_info() -> Dict[str, Any]:
    """Get diagnostic information."""
    
    if not is_ha_extension_enabled():
        return {}
    
    try:
        from ha_core import get_diagnostic_information
        return get_diagnostic_information()
    except Exception as e:
        log_error(f"Diagnostic info failed: {str(e)}")
        return {}


def get_assistant_name_status() -> Dict[str, Any]:
    """Check assistant name availability."""
    
    try:
        from ha_core import get_assistant_name_info
        return get_assistant_name_info()
    except Exception as e:
        log_error(f"Assistant name check failed: {str(e)}")
        return create_error_response(str(e), 'ASSISTANT_NAME_CHECK_FAILED')


# ===== ALEXA OPERATIONS =====

def process_alexa_ha_request(event: Dict[str, Any]) -> Dict[str, Any]:
    """Process Alexa Smart Home directive."""
    
    if not is_ha_extension_enabled():
        return _create_alexa_error_response(event, 'BRIDGE_UNREACHABLE', 
                                           'Home Assistant extension disabled')
    
    try:
        from ha_alexa import process_alexa_directive
        return process_alexa_directive(event)
    except Exception as e:
        log_error(f"Alexa request processing failed: {str(e)}")
        return _create_alexa_error_response(event, 'INTERNAL_ERROR', str(e))


def handle_alexa_discovery(event: Dict[str, Any]) -> Dict[str, Any]:
    """Handle Alexa discovery."""
    correlation_id = generate_correlation_id()
    
    if not is_ha_extension_enabled():
        return _create_alexa_error_response(event, 'BRIDGE_UNREACHABLE',
                                           'Home Assistant extension disabled')
    
    try:
        from ha_alexa import handle_discovery
        return handle_discovery(event)
    except Exception as e:
        log_error(f"[{correlation_id}] Alexa discovery failed: {str(e)}")
        return _create_alexa_error_response(event, 'INTERNAL_ERROR', str(e))


def handle_alexa_authorization(event: Dict[str, Any]) -> Dict[str, Any]:
    """Handle Alexa authorization (AcceptGrant)."""
    correlation_id = generate_correlation_id()
    
    if not is_ha_extension_enabled():
        return _create_alexa_error_response(event, 'BRIDGE_UNREACHABLE',
                                           'Home Assistant extension disabled')
    
    try:
        from ha_alexa import handle_accept_grant
        return handle_accept_grant(event)
    except Exception as e:
        log_error(f"[{correlation_id}] Alexa authorization failed: {str(e)}")
        return _create_alexa_error_response(event, 'INTERNAL_ERROR', str(e))


def handle_alexa_control(event: Dict[str, Any]) -> Dict[str, Any]:
    """Handle Alexa control directive."""
    correlation_id = generate_correlation_id()
    
    if not is_ha_extension_enabled():
        return _create_alexa_error_response(event, 'ENDPOINT_UNREACHABLE',
                                           'Home Assistant extension disabled')
    
    try:
        from ha_alexa import handle_control
        return handle_control(event)
    except Exception as e:
        log_error(f"[{correlation_id}] Alexa control failed: {str(e)}")
        return _create_alexa_error_response(event, 'INTERNAL_ERROR', str(e))


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
