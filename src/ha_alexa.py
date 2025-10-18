"""
ha_alexa.py - Alexa Smart Home Integration
Version: 2025.10.18.08
Description: Alexa Smart Home integration using Gateway services exclusively.

CHANGELOG:
- 2025.10.18.08: FIXED - Added proper error handling for missing ha_core imports
  - Added try/except around ha_core imports with detailed error logging
  - Added fallback error responses when imports fail
  - This fixes the "error: NO_ERROR" issue

Copyright 2025 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

import os
from typing import Dict, Any, List, Optional
from gateway import (
    log_info, log_error, log_debug, log_warning,
    increment_counter,
    generate_correlation_id,
    create_success_response, create_error_response
)

# Try to import ha_core functions with error handling
try:
    from ha_core import get_ha_states, call_ha_service, get_ha_config
    HA_CORE_AVAILABLE = True
    log_info("[HA_ALEXA] Successfully imported ha_core functions")
except Exception as e:
    HA_CORE_AVAILABLE = False
    log_error(f"[HA_ALEXA] CRITICAL: Failed to import ha_core: {type(e).__name__}: {str(e)}")
    import traceback
    log_error(f"[HA_ALEXA] Import traceback:\n{traceback.format_exc()}")
    
    # Create stub functions that return proper errors
    def get_ha_states(*args, **kwargs):
        return create_error_response(f'ha_core import failed: {str(e)}', 'HA_CORE_IMPORT_FAILED')
    
    def call_ha_service(*args, **kwargs):
        return create_error_response(f'ha_core import failed: {str(e)}', 'HA_CORE_IMPORT_FAILED')
    
    def get_ha_config(*args, **kwargs):
        return {}

# Alexa capability mappings
DEVICE_CAPABILITIES = {
    'light': ['Alexa.PowerController', 'Alexa.BrightnessController', 'Alexa.ColorController'],
    'switch': ['Alexa.PowerController'],
    'fan': ['Alexa.PowerController', 'Alexa.RangeController'],
    'lock': ['Alexa.LockController'],
    'climate': ['Alexa.ThermostatController', 'Alexa.TemperatureSensor'],
    'cover': ['Alexa.ModeController'],
    'media_player': ['Alexa.PowerController', 'Alexa.PlaybackController']
}


def _is_debug_mode() -> bool:
    """Check if DEBUG_MODE is enabled."""
    return os.getenv('DEBUG_MODE', 'false').lower() == 'true'


# ===== ALEXA DIRECTIVE PROCESSING =====

def process_alexa_directive(event: Dict[str, Any]) -> Dict[str, Any]:
    """Process Alexa Smart Home directive."""
    correlation_id = generate_correlation_id()
    
    try:
        if _is_debug_mode():
            log_info(f"[{correlation_id}] [DEBUG ENTRY] HA_ALEXA: process_alexa_directive called")
        
        directive = event.get('directive', {})
        header = directive.get('header', {})
        namespace = header.get('namespace', '')
        name = header.get('name', '')
        
        log_info(f"[{correlation_id}] Alexa directive: {namespace}.{name}")
        
        if namespace == 'Alexa.Discovery' and name == 'Discover':
            return handle_discovery(directive)
        elif namespace == 'Alexa.PowerController':
            return handle_power_control(directive)
        elif namespace == 'Alexa.BrightnessController':
            return handle_brightness_control(directive)
        elif namespace == 'Alexa.ThermostatController':
            return handle_thermostat_control(directive)
        elif namespace == 'Alexa.Authorization' and name == 'AcceptGrant':
            return handle_accept_grant(directive)
        else:
            log_error(f"[{correlation_id}] Unsupported directive: {namespace}.{name}")
            return _create_error_response(header, 'INVALID_DIRECTIVE',
                                         f'Unsupported: {namespace}.{name}')
        
    except Exception as e:
        if _is_debug_mode():
            log_error(f"[{correlation_id}] [DEBUG EXCEPTION] HA_ALEXA: {type(e).__name__}: {str(e)}")
        log_error(f"[{correlation_id}] Directive processing failed: {str(e)}")
        return _create_error_response({}, 'INTERNAL_ERROR', str(e))


def handle_discovery(directive: Dict[str, Any]) -> Dict[str, Any]:
    """Handle Alexa discovery request."""
    correlation_id = generate_correlation_id()
    
    try:
        if _is_debug_mode():
            log_info(f"[{correlation_id}] [DEBUG ENTRY] HA_ALEXA: handle_discovery called")
            log_info(f"[{correlation_id}] [DEBUG] HA_ALEXA: HA_CORE_AVAILABLE={HA_CORE_AVAILABLE}")
        
        if not HA_CORE_AVAILABLE:
            log_error(f"[{correlation_id}] ha_core not available - cannot process discovery")
            return _create_error_response(
                directive.get('header', {}),
                'INTERNAL_ERROR',
                'Home Assistant core module failed to load'
            )
        
        log_info(f"[{correlation_id}] Processing Alexa discovery")
        
        if _is_debug_mode():
            log_info(f"[{correlation_id}] [DEBUG] HA_ALEXA: Calling get_ha_states()")
        
        # Get states from HA
        response = get_ha_states()
        
        if _is_debug_mode():
            log_info(f"[{correlation_id}] [DEBUG] HA_ALEXA: get_ha_states returned")
            log_info(f"[{correlation_id}] [DEBUG] HA_ALEXA: response type: {type(response)}")
            if isinstance(response, dict):
                log_info(f"[{correlation_id}] [DEBUG] HA_ALEXA: response keys: {list(response.keys())}")
                log_info(f"[{correlation_id}] [DEBUG] HA_ALEXA: success: {response.get('success')}")
                log_info(f"[{correlation_id}] [DEBUG] HA_ALEXA: error: {response.get('error', 'NO_ERROR_FIELD')}")
                log_info(f"[{correlation_id}] [DEBUG] HA_ALEXA: error_code: {response.get('error_code', 'NO_CODE_FIELD')}")
            else:
                log_error(f"[{correlation_id}] [DEBUG] HA_ALEXA: response is NOT A DICT")
        
        # DEBUG: Log response structure
        log_debug(f"[{correlation_id}] get_ha_states response type: {type(response)}")
        log_debug(f"[{correlation_id}] get_ha_states response keys: {list(response.keys()) if isinstance(response, dict) else 'NOT_A_DICT'}")
        
        if not response.get('success'):
            error_msg = response.get('error', 'Unknown error from get_ha_states')
            error_code = response.get('error_code', 'UNKNOWN_ERROR')
            
            if _is_debug_mode():
                log_error(f"[{correlation_id}] [DEBUG] HA_ALEXA: get_ha_states failed")
                log_error(f"[{correlation_id}] [DEBUG] HA_ALEXA: error: {error_msg}")
                log_error(f"[{correlation_id}] [DEBUG] HA_ALEXA: error_code: {error_code}")
                log_error(f"[{correlation_id}] [DEBUG] HA_ALEXA: Full response: {response}")
            
            log_error(f"[{correlation_id}] get_ha_states failed: {error_msg} (code: {error_code})")
            
            return _create_error_response(
                directive.get('header', {}),
                'BRIDGE_UNREACHABLE',
                f'Cannot reach Home Assistant: {error_msg}'
            )
        
        # Get data field
        states = response.get('data', [])
        
        if _is_debug_mode():
            log_info(f"[{correlation_id}] [DEBUG] HA_ALEXA: states type: {type(states)}")
            log_info(f"[{correlation_id}] [DEBUG] HA_ALEXA: states count: {len(states) if isinstance(states, list) else 'NOT_A_LIST'}")
        
        # DEBUG: Log data field details
        log_info(f"[{correlation_id}] States data type: {type(states)}")
        log_info(f"[{correlation_id}] States count: {len(states) if isinstance(states, list) else 'NOT_A_LIST'}")
        
        if isinstance(states, list) and len(states) > 0:
            # Log first few entities
            sample_count = min(3, len(states))
            log_info(f"[{correlation_id}] First {sample_count} entities:")
            for i in range(sample_count):
                entity = states[i]
                log_info(f"[{correlation_id}]   Entity {i}: {entity.get('entity_id', 'NO_ID')} (type: {type(entity)})")
        elif isinstance(states, list):
            log_warning(f"[{correlation_id}] States list is EMPTY")
        else:
            log_error(f"[{correlation_id}] States is not a list: {type(states)}")
        
        if _is_debug_mode():
            log_info(f"[{correlation_id}] [DEBUG] HA_ALEXA: Building Alexa endpoints")
        
        # Build Alexa endpoints
        endpoints = []
        processed = 0
        skipped_no_domain = 0
        skipped_unsupported = 0
        
        for state in states:
            processed += 1
            
            if not isinstance(state, dict):
                log_warning(f"[{correlation_id}] Skipping non-dict state: {type(state)}")
                continue
            
            entity_id = state.get('entity_id', '')
            if not entity_id:
                log_warning(f"[{correlation_id}] Skipping state with no entity_id")
                skipped_no_domain += 1
                continue
            
            domain = entity_id.split('.')[0] if '.' in entity_id else ''
            if not domain:
                log_warning(f"[{correlation_id}] Skipping {entity_id}: no domain")
                skipped_no_domain += 1
                continue
            
            # Only expose controllable devices
            if domain in DEVICE_CAPABILITIES:
                log_debug(f"[{correlation_id}] Building endpoint for {entity_id} (domain: {domain})")
                endpoint = _build_endpoint(state, domain)
                if endpoint:
                    endpoints.append(endpoint)
                    log_debug(f"[{correlation_id}]   ✓ Added {entity_id}")
                else:
                    log_warning(f"[{correlation_id}]   ✗ Failed to build endpoint for {entity_id}")
            else:
                skipped_unsupported += 1
                if processed <= 10:  # Only log first 10
                    log_debug(f"[{correlation_id}] Skipping {entity_id}: unsupported domain '{domain}'")
        
        # Summary
        log_info(f"[{correlation_id}] Discovery summary:")
        log_info(f"[{correlation_id}]   Processed: {processed}")
        log_info(f"[{correlation_id}]   Skipped (no domain): {skipped_no_domain}")
        log_info(f"[{correlation_id}]   Skipped (unsupported): {skipped_unsupported}")
        log_info(f"[{correlation_id}]   Discovered endpoints: {len(endpoints)}")
        
        if len(endpoints) == 0:
            log_warning(f"[{correlation_id}] No controllable devices found!")
            log_warning(f"[{correlation_id}] Supported domains: {list(DEVICE_CAPABILITIES.keys())}")
        
        increment_counter('alexa_discovery')
        
        discovery_response = {
            'event': {
                'header': {
                    'namespace': 'Alexa.Discovery',
                    'name': 'Discover.Response',
                    'messageId': correlation_id,
                    'payloadVersion': '3'
                },
                'payload': {
                    'endpoints': endpoints
                }
            }
        }
        
        if _is_debug_mode():
            log_info(f"[{correlation_id}] [DEBUG] HA_ALEXA: Returning discovery response")
            log_info(f"[{correlation_id}] [DEBUG] HA_ALEXA: response has {len(endpoints)} endpoints")
        
        return discovery_response
        
    except Exception as e:
        if _is_debug_mode():
            log_error(f"[{correlation_id}] [DEBUG EXCEPTION] HA_ALEXA: {type(e).__name__}: {str(e)}")
            import traceback
            log_error(f"[{correlation_id}] [DEBUG TRACEBACK] HA_ALEXA:\n{traceback.format_exc()}")
        log_error(f"[{correlation_id}] Discovery failed: {str(e)}")
        return _create_error_response({}, 'INTERNAL_ERROR', str(e))


def handle_control(directive: Dict[str, Any]) -> Dict[str, Any]:
    """Handle Alexa control directive."""
    header = directive.get('header', {})
    namespace = header.get('namespace', '')
    
    if _is_debug_mode():
        log_info(f"[DEBUG] HA_ALEXA: handle_control called for {namespace}")
    
    if namespace == 'Alexa.PowerController':
        return handle_power_control(directive)
    elif namespace == 'Alexa.BrightnessController':
        return handle_brightness_control(directive)
    elif namespace == 'Alexa.ThermostatController':
        return handle_thermostat_control(directive)
    else:
        return _create_error_response(header, 'INVALID_DIRECTIVE', 
                                     f'Unsupported control: {namespace}')


def handle_power_control(directive: Dict[str, Any]) -> Dict[str, Any]:
    """Handle power control (TurnOn/TurnOff)."""
    correlation_id = generate_correlation_id()
    
    try:
        header = directive.get('header', {})
        endpoint = directive.get('endpoint', {})
        entity_id = endpoint.get('endpointId', '')
        
        name = header.get('name', '')
        
        log_info(f"[{correlation_id}] Power control: {name} on {entity_id}")
        
        service = 'turn_on' if name == 'TurnOn' else 'turn_off'
        domain = entity_id.split('.')[0] if '.' in entity_id else ''
        
        result = call_ha_service(domain, service, entity_id)
        
        if result.get('success'):
            increment_counter('alexa_power_control')
            return _create_success_response(header, endpoint)
        else:
            return _create_error_response(header, 'ENDPOINT_UNREACHABLE',
                                         'Power control failed')
        
    except Exception as e:
        log_error(f"[{correlation_id}] Power control failed: {str(e)}")
        return _create_error_response(header, 'INTERNAL_ERROR', str(e))


def handle_brightness_control(directive: Dict[str, Any]) -> Dict[str, Any]:
    """Handle brightness control (SetBrightness, AdjustBrightness)."""
    correlation_id = generate_correlation_id()
    
    try:
        header = directive.get('header', {})
        endpoint = directive.get('endpoint', {})
        payload = directive.get('payload', {})
        entity_id = endpoint.get('endpointId', '')
        
        name = header.get('name', '')
        
        log_info(f"[{correlation_id}] Brightness control: {name} on {entity_id}")
        
        if name == 'SetBrightness':
            brightness = payload.get('brightness', 100)
            service_data = {'brightness_pct': brightness}
        elif name == 'AdjustBrightness':
            delta = payload.get('brightnessDelta', 0)
            service_data = {'brightness_step_pct': delta}
        else:
            return _create_error_response(header, 'INVALID_DIRECTIVE',
                                         f'Unsupported brightness: {name}')
        
        result = call_ha_service('light', 'turn_on', entity_id, service_data)
        
        if result.get('success'):
            increment_counter('alexa_brightness')
            return _create_success_response(header, endpoint)
        else:
            return _create_error_response(header, 'ENDPOINT_UNREACHABLE',
                                         'Brightness control failed')
        
    except Exception as e:
        log_error(f"[{correlation_id}] Brightness control failed: {str(e)}")
        return _create_error_response(header, 'INTERNAL_ERROR', str(e))


def handle_thermostat_control(directive: Dict[str, Any]) -> Dict[str, Any]:
    """Handle thermostat control (SetTargetTemperature, SetThermostatMode)."""
    correlation_id = generate_correlation_id()
    
    try:
        header = directive.get('header', {})
        endpoint = directive.get('endpoint', {})
        payload = directive.get('payload', {})
        entity_id = endpoint.get('endpointId', '')
        
        name = header.get('name', '')
        
        log_info(f"[{correlation_id}] Thermostat control: {name} on {entity_id}")
        
        service_data = {}
        
        if name == 'SetTargetTemperature':
            temp = payload.get('targetSetpoint', {}).get('value', 20)
            service_data['temperature'] = temp
            service = 'set_temperature'
        elif name == 'SetThermostatMode':
            mode = payload.get('thermostatMode', {}).get('value', 'AUTO').lower()
            service_data['hvac_mode'] = mode
            service = 'set_hvac_mode'
        else:
            return _create_error_response(header, 'INVALID_DIRECTIVE',
                                         f'Unsupported thermostat: {name}')
        
        result = call_ha_service('climate', service, entity_id, service_data)
        
        if result.get('success'):
            increment_counter('alexa_thermostat')
            return _create_success_response(header, endpoint)
        else:
            return _create_error_response(header, 'ENDPOINT_UNREACHABLE',
                                         'Thermostat control failed')
        
    except Exception as e:
        log_error(f"[{correlation_id}] Thermostat control failed: {str(e)}")
        return _create_error_response(header, 'INTERNAL_ERROR', str(e))


def handle_accept_grant(directive: Dict[str, Any]) -> Dict[str, Any]:
    """Handle AcceptGrant (authorization)."""
    correlation_id = generate_correlation_id()
    
    log_info(f"[{correlation_id}] Alexa AcceptGrant received")
    increment_counter('alexa_accept_grant')
    
    header = directive.get('header', {})
    
    return {
        'event': {
            'header': {
                'namespace': 'Alexa.Authorization',
                'name': 'AcceptGrant.Response',
                'messageId': correlation_id,
                'payloadVersion': '3'
            },
            'payload': {}
        }
    }


# ===== HELPER FUNCTIONS =====

def _build_endpoint(state: Dict[str, Any], domain: str) -> Optional[Dict[str, Any]]:
    """Build Alexa endpoint from HA entity state."""
    entity_id = state.get('entity_id', '')
    attributes = state.get('attributes', {})
    friendly_name = attributes.get('friendly_name', entity_id)
    
    # Get capabilities for this domain
    capabilities = []
    for cap in DEVICE_CAPABILITIES.get(domain, []):
        capabilities.append({
            'type': 'AlexaInterface',
            'interface': cap,
            'version': '3'
        })
    
    if not capabilities:
        return None
    
    return {
        'endpointId': entity_id,
        'manufacturerName': 'Home Assistant',
        'friendlyName': friendly_name,
        'description': f'{domain} via Home Assistant',
        'displayCategories': [_get_display_category(domain)],
        'capabilities': capabilities
    }


def _get_display_category(domain: str) -> str:
    """Get Alexa display category for domain."""
    categories = {
        'light': 'LIGHT',
        'switch': 'SWITCH',
        'fan': 'FAN',
        'lock': 'SMARTLOCK',
        'climate': 'THERMOSTAT',
        'cover': 'DOOR',
        'media_player': 'TV'
    }
    return categories.get(domain, 'OTHER')


def _create_success_response(header: Dict[str, Any], 
                            endpoint: Dict[str, Any]) -> Dict[str, Any]:
    """Create Alexa success response."""
    correlation_id = generate_correlation_id()
    
    return {
        'event': {
            'header': {
                'namespace': 'Alexa',
                'name': 'Response',
                'messageId': correlation_id,
                'correlationToken': header.get('correlationToken'),
                'payloadVersion': '3'
            },
            'endpoint': endpoint,
            'payload': {}
        }
    }


def _create_error_response(header: Dict[str, Any], error_type: str,
                          error_message: str) -> Dict[str, Any]:
    """Create Alexa error response."""
    correlation_id = generate_correlation_id()
    
    return {
        'event': {
            'header': {
                'namespace': 'Alexa',
                'name': 'ErrorResponse',
                'messageId': correlation_id,
                'correlationToken': header.get('correlationToken'),
                'payloadVersion': '3'
            },
            'payload': {
                'type': error_type,
                'message': error_message
            }
        }
    }


__all__ = [
    'process_alexa_directive',
    'handle_discovery',
    'handle_control',
    'handle_power_control',
    'handle_brightness_control',
    'handle_thermostat_control',
    'handle_accept_grant',
]

# EOF
