"""
ha_alexa.py - Alexa Smart Home Integration
Version: 2025.10.18.05
Description: Alexa Smart Home integration using Gateway services exclusively.

CHANGELOG:
- 2025.10.18.05: Added comprehensive debug logging for discovery troubleshooting
  - Log response structure from get_ha_states
  - Log data field type and content
  - Log entity processing details
  - Log why endpoints are/aren't added
- 2025.10.16.01: Fixed import names - get_states → get_ha_states, call_service → call_ha_service

Copyright 2025 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

from typing import Dict, Any, List, Optional
from gateway import (
    log_info, log_error, log_debug, log_warning,
    increment_counter,
    generate_correlation_id,
    create_success_response, create_error_response
)
from ha_core import get_ha_states, call_ha_service, get_ha_config

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

# ===== ALEXA DIRECTIVE PROCESSING =====

def process_alexa_directive(event: Dict[str, Any]) -> Dict[str, Any]:
    """Process Alexa Smart Home directive."""
    correlation_id = generate_correlation_id()
    
    try:
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
        log_error(f"[{correlation_id}] Directive processing failed: {str(e)}")
        return _create_error_response({}, 'INTERNAL_ERROR', str(e))


def handle_discovery(directive: Dict[str, Any]) -> Dict[str, Any]:
    """Handle Alexa discovery request."""
    correlation_id = generate_correlation_id()
    
    try:
        log_info(f"[{correlation_id}] Processing Alexa discovery")
        
        # Get states from HA
        response = get_ha_states()
        
        # DEBUG: Log response structure
        log_debug(f"[{correlation_id}] get_ha_states response type: {type(response)}")
        log_debug(f"[{correlation_id}] get_ha_states response keys: {list(response.keys()) if isinstance(response, dict) else 'NOT_A_DICT'}")
        
        if not response.get('success'):
            log_error(f"[{correlation_id}] get_ha_states failed: {response.get('error', 'Unknown')}")
            return _create_error_response(
                directive.get('header', {}),
                'BRIDGE_UNREACHABLE',
                'Cannot reach Home Assistant'
            )
        
        # Get data field
        states = response.get('data', [])
        
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
        
        return {
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
        
    except Exception as e:
        log_error(f"[{correlation_id}] Discovery failed: {str(e)}")
        return _create_error_response({}, 'INTERNAL_ERROR', str(e))


def handle_control(directive: Dict[str, Any]) -> Dict[str, Any]:
    """Handle Alexa control directive."""
    header = directive.get('header', {})
    namespace = header.get('namespace', '')
    
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
        service = 'turn_on' if name == 'TurnOn' else 'turn_off'
        
        log_info(f"[{correlation_id}] Power control: {service} on {entity_id}")
        
        domain = entity_id.split('.')[0] if '.' in entity_id else ''
        result = call_ha_service(domain, service, entity_id)
        
        if result.get('success'):
            increment_counter(f'alexa_power_{service}')
            return _create_success_response(header, endpoint)
        else:
            return _create_error_response(header, 'ENDPOINT_UNREACHABLE',
                                         'Device control failed')
        
    except Exception as e:
        log_error(f"[{correlation_id}] Power control failed: {str(e)}")
        return _create_error_response(header, 'INTERNAL_ERROR', str(e))


def handle_brightness_control(directive: Dict[str, Any]) -> Dict[str, Any]:
    """Handle brightness control."""
    correlation_id = generate_correlation_id()
    
    try:
        header = directive.get('header', {})
        endpoint = directive.get('endpoint', {})
        payload = directive.get('payload', {})
        entity_id = endpoint.get('endpointId', '')
        
        brightness = payload.get('brightness', 100)
        
        log_info(f"[{correlation_id}] Brightness control: {brightness} on {entity_id}")
        
        service_data = {'brightness_pct': brightness}
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
    """Handle thermostat control."""
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
    try:
        entity_id = state.get('entity_id', '')
        attributes = state.get('attributes', {})
        friendly_name = attributes.get('friendly_name', entity_id)
        
        # Build capabilities based on domain
        capabilities = []
        for capability in DEVICE_CAPABILITIES.get(domain, []):
            capabilities.append({
                'type': 'AlexaInterface',
                'interface': capability,
                'version': '3'
            })
        
        # Always include Alexa interface
        capabilities.append({
            'type': 'AlexaInterface',
            'interface': 'Alexa',
            'version': '3'
        })
        
        endpoint = {
            'endpointId': entity_id,
            'manufacturerName': 'Home Assistant',
            'friendlyName': friendly_name,
            'description': f'{domain} controlled by Home Assistant',
            'displayCategories': [_get_display_category(domain)],
            'capabilities': capabilities
        }
        
        return endpoint
        
    except Exception as e:
        log_error(f"Failed to build endpoint for {state.get('entity_id', 'unknown')}: {str(e)}")
        return None


def _get_display_category(domain: str) -> str:
    """Get Alexa display category for domain."""
    category_map = {
        'light': 'LIGHT',
        'switch': 'SWITCH',
        'fan': 'FAN',
        'lock': 'SMARTLOCK',
        'climate': 'THERMOSTAT',
        'cover': 'DOOR',
        'media_player': 'TV'
    }
    return category_map.get(domain, 'OTHER')


def _create_success_response(header: Dict[str, Any], endpoint: Dict[str, Any]) -> Dict[str, Any]:
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
            'endpoint': {
                'endpointId': endpoint.get('endpointId')
            },
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
            'endpoint': {},
            'payload': {
                'type': error_type,
                'message': error_message
            }
        }
    }

# EOF
