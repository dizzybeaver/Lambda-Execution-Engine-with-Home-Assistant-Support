"""
ha_alexa.py - Alexa Smart Home Integration
Version: 2025.10.14.01
Description: Alexa Smart Home integration using Gateway services exclusively.

Copyright 2025 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

from typing import Dict, Any, List, Optional
from gateway import (
    log_info, log_error, log_debug,
    increment_counter,
    generate_correlation_id,
    create_success_response, create_error_response
)
from ha_core import get_states, call_service, get_ha_config

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
    """Handle Alexa discovery request with WebSocket support."""
    correlation_id = generate_correlation_id()
    
    try:
        log_info(f"[{correlation_id}] Processing Alexa discovery")
        
        # Try WebSocket entity registry first (if enabled)
        try:
            from ha_websocket import is_websocket_enabled
            from ha_core import get_ha_entity_registry, filter_exposed_entities_wrapper
            
            if is_websocket_enabled():
                log_debug(f"[{correlation_id}] Using WebSocket for discovery")
                
                # Get entity registry
                registry_result = get_ha_entity_registry()
                if registry_result.get('success'):
                    # Filter to exposed entities only
                    filter_result = filter_exposed_entities_wrapper(
                        registry_result.get('data', {}).get('entities', [])
                    )
                    
                    if filter_result.get('success'):
                        entities = filter_result.get('data', {}).get('entities', [])
                        
                        # Convert registry entities to state format for endpoint building
                        states = []
                        for entity in entities:
                            entity_id = entity.get('entity_id', '')
                            states.append({
                                'entity_id': entity_id,
                                'attributes': {
                                    'friendly_name': entity.get('original_name', entity_id)
                                }
                            })
                        
                        log_info(f"[{correlation_id}] Using {len(states)} exposed entities from WebSocket")
                    else:
                        # Fallback to all states
                        log_warning(f"[{correlation_id}] Entity filtering failed, using all states")
                        response = get_states()
                        states = response.get('data', {}).get('states', [])
                else:
                    # Fallback to REST
                    log_warning(f"[{correlation_id}] WebSocket registry failed, using REST")
                    response = get_states()
                    states = response.get('data', {}).get('states', [])
            else:
                # WebSocket disabled, use REST
                response = get_states()
                states = response.get('data', {}).get('states', [])
        except ImportError:
            # WebSocket module not available, use REST
            log_debug(f"[{correlation_id}] WebSocket module not available, using REST")
            response = get_states()
            states = response.get('data', {}).get('states', [])
        
        if not states:
            return _create_error_response(
                directive.get('header', {}),
                'BRIDGE_UNREACHABLE',
                'Cannot reach Home Assistant'
            )
        
        # Build Alexa endpoints
        endpoints = []
        for state in states:
            entity_id = state.get('entity_id', '')
            domain = entity_id.split('.')[0] if '.' in entity_id else ''
            
            # Only expose controllable devices
            if domain in DEVICE_CAPABILITIES:
                endpoint = _build_endpoint(state, domain)
                if endpoint:
                    endpoints.append(endpoint)
        
        log_info(f"[{correlation_id}] Discovered {len(endpoints)} endpoints")
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
        result = call_service(domain, service, entity_id)
        
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
        result = call_service('light', 'turn_on', entity_id, service_data)
        
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
        
        result = call_service('climate', service, entity_id, service_data)
        
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
    
    capabilities = DEVICE_CAPABILITIES.get(domain, [])
    if not capabilities:
        return None
    
    return {
        'endpointId': entity_id,
        'manufacturerName': 'Home Assistant',
        'friendlyName': friendly_name,
        'description': f'{domain.title()} controlled by Home Assistant',
        'displayCategories': [_get_display_category(domain)],
        'capabilities': [
            {
                'type': 'AlexaInterface',
                'interface': cap,
                'version': '3'
            }
            for cap in capabilities
        ] + [
            {
                'type': 'AlexaInterface',
                'interface': 'Alexa.EndpointHealth',
                'version': '3',
                'properties': {
                    'supported': [{'name': 'connectivity'}],
                    'proactivelyReported': False,
                    'retrievable': True
                }
            }
        ]
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
    correlation_id = header.get('correlationToken', generate_correlation_id())
    
    return {
        'event': {
            'header': {
                'namespace': 'Alexa',
                'name': 'Response',
                'messageId': generate_correlation_id(),
                'correlationToken': correlation_id,
                'payloadVersion': '3'
            },
            'endpoint': endpoint,
            'payload': {}
        }
    }


def _create_error_response(header: Dict[str, Any], error_type: str,
                          message: str) -> Dict[str, Any]:
    """Create Alexa error response."""
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


# EOF
