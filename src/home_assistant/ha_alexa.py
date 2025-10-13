"""
ha_alexa.py
Version: 2025.10.13.03
Description: Alexa Smart Home API integration with entity registry filtering

Copyright 2025 Joseph Hersey

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at
   
       http://www.apache.org/licenses/LICENSE-2.0
   
   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

from typing import Dict, Any, Optional, List
from gateway import (
    log_info, log_error, log_debug, create_success_response, create_error_response,
    generate_correlation_id, record_metric, increment_counter
)
from ha_core import (
    batch_get_states, call_ha_service, is_ha_available, get_ha_config,
    filter_exposed_entities, HA_CACHE_TTL_ENTITIES
)

class AlexaSmartHomeManager:
    """Manages Alexa Smart Home API integration with entity registry filtering."""

    def __init__(self):
        self._stats = {
            'total_directives': 0,
            'successful_directives': 0,
            'failed_directives': 0,
            'discoveries': 0,
            'filtered_entities': 0
        }

    def handle_discovery(self, ha_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Handle Alexa device discovery with entity registry filtering."""
        correlation_id = generate_correlation_id()
        
        try:
            log_info(f"[{correlation_id}] Starting Alexa discovery with registry filtering")
            
            if not is_ha_available():
                log_error(f"[{correlation_id}] HA circuit breaker open")
                return create_error_response('Home Assistant circuit breaker open')

            config = ha_config or get_ha_config()

            # Get all states from /api/states
            response = batch_get_states(None, config, use_cache=True)

            if not response.get('success'):
                log_error(f"[{correlation_id}] Failed to get states")
                return create_error_response(response.get('error', 'Failed to get states'))

            all_states = response.get('data', [])
            log_info(f"[{correlation_id}] Retrieved {len(all_states)} total entities")
            
            # Filter by entity registry exposure settings
            exposed_states = filter_exposed_entities(all_states, config)
            log_info(f"[{correlation_id}] Filtered to {len(exposed_states)} exposed entities")
            
            self._stats['filtered_entities'] = len(all_states) - len(exposed_states)
            
            endpoints = []

            # Transform HA entities to Alexa endpoints
            for state in exposed_states:
                entity_id = state.get('entity_id', '')
                domain = entity_id.split('.')[0] if '.' in entity_id else ''

                if domain in ['light', 'switch', 'fan', 'climate', 'lock', 'cover']:
                    endpoint = self._build_alexa_endpoint(state)
                    if endpoint:
                        endpoints.append(endpoint)

            self._stats['discoveries'] += 1
            record_metric('alexa_discovery', 1.0)
            record_metric('alexa_endpoints_exposed', float(len(endpoints)))
            record_metric('alexa_entities_filtered', float(self._stats['filtered_entities']))
            
            log_info(f"[{correlation_id}] Discovery complete: {len(endpoints)} endpoints")

            return create_success_response("Discovery successful", {
                'endpoints': endpoints,
                'total_entities': len(all_states),
                'exposed_entities': len(exposed_states),
                'filtered_count': self._stats['filtered_entities']
            })

        except Exception as e:
            log_error(f"[{correlation_id}] Discovery failed: {str(e)}")
            return create_error_response(str(e))

    def _build_alexa_endpoint(self, state: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Build Alexa endpoint from HA state."""
        entity_id = state.get('entity_id', '')
        domain = entity_id.split('.')[0] if '.' in entity_id else ''
        
        attributes = state.get('attributes', {})
        friendly_name = attributes.get('friendly_name', entity_id)

        endpoint = {
            'endpointId': entity_id,
            'manufacturerName': 'Home Assistant',
            'friendlyName': friendly_name,
            'description': f'{domain.title()} controlled by Home Assistant',
            'displayCategories': self._get_display_categories(domain),
            'capabilities': self._get_capabilities(domain, attributes)
        }

        return endpoint

    def _get_display_categories(self, domain: str) -> List[str]:
        """Get Alexa display categories for domain."""
        category_map = {
            'light': ['LIGHT'],
            'switch': ['SWITCH'],
            'fan': ['FAN'],
            'climate': ['THERMOSTAT'],
            'lock': ['SMARTLOCK'],
            'cover': ['DOOR']
        }
        return category_map.get(domain, ['OTHER'])

    def _get_capabilities(self, domain: str, attributes: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get Alexa capabilities for domain."""
        capabilities = [
            {
                'type': 'AlexaInterface',
                'interface': 'Alexa',
                'version': '3'
            }
        ]

        if domain in ['light', 'switch', 'fan']:
            capabilities.append({
                'type': 'AlexaInterface',
                'interface': 'Alexa.PowerController',
                'version': '3',
                'properties': {
                    'supported': [{'name': 'powerState'}],
                    'proactivelyReported': False,
                    'retrievable': True
                }
            })

        if domain == 'light' and attributes.get('supported_color_modes'):
            capabilities.append({
                'type': 'AlexaInterface',
                'interface': 'Alexa.BrightnessController',
                'version': '3',
                'properties': {
                    'supported': [{'name': 'brightness'}],
                    'proactivelyReported': False,
                    'retrievable': True
                }
            })

        if domain == 'climate':
            capabilities.append({
                'type': 'AlexaInterface',
                'interface': 'Alexa.ThermostatController',
                'version': '3',
                'properties': {
                    'supported': [
                        {'name': 'targetSetpoint'},
                        {'name': 'thermostatMode'}
                    ],
                    'proactivelyReported': False,
                    'retrievable': True
                }
            })

        if domain == 'lock':
            capabilities.append({
                'type': 'AlexaInterface',
                'interface': 'Alexa.LockController',
                'version': '3',
                'properties': {
                    'supported': [{'name': 'lockState'}],
                    'proactivelyReported': False,
                    'retrievable': True
                }
            })

        return capabilities

    def handle_power_control(self, directive: Dict[str, Any], 
                            ha_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Handle Alexa PowerController directives."""
        correlation_id = generate_correlation_id()
        
        try:
            self._stats['total_directives'] += 1
            
            endpoint = directive.get('endpoint', {})
            entity_id = endpoint.get('endpointId')
            header = directive.get('header', {})
            name = header.get('name')

            log_info(f"[{correlation_id}] Power control: {name} for {entity_id}")

            if not entity_id:
                return self._create_error_response(header, 'INVALID_VALUE', 'Missing entity ID')

            domain = entity_id.split('.')[0]
            service = 'turn_on' if name == 'TurnOn' else 'turn_off'

            result = call_ha_service(domain, service, ha_config, entity_id)

            if result.get('success'):
                self._stats['successful_directives'] += 1
                increment_counter(f'alexa_power_{service}')
                return self._create_power_response(header, entity_id, name == 'TurnOn')
            else:
                self._stats['failed_directives'] += 1
                return self._create_error_response(header, 'ENDPOINT_UNREACHABLE', 
                                                  result.get('error', 'Service call failed'))

        except Exception as e:
            log_error(f"[{correlation_id}] Power control failed: {str(e)}")
            self._stats['failed_directives'] += 1
            return self._create_error_response(directive.get('header', {}), 'INTERNAL_ERROR', str(e))

    def handle_brightness_control(self, directive: Dict[str, Any],
                                  ha_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Handle Alexa BrightnessController directives."""
        correlation_id = generate_correlation_id()
        
        try:
            self._stats['total_directives'] += 1
            
            endpoint = directive.get('endpoint', {})
            entity_id = endpoint.get('endpointId')
            header = directive.get('header', {})
            payload = directive.get('payload', {})
            brightness = payload.get('brightness', 100)

            log_info(f"[{correlation_id}] Brightness control: {brightness}% for {entity_id}")

            service_data = {'brightness_pct': brightness}
            result = call_ha_service('light', 'turn_on', ha_config, entity_id, service_data)

            if result.get('success'):
                self._stats['successful_directives'] += 1
                increment_counter('alexa_brightness_set')
                return self._create_brightness_response(header, entity_id, brightness)
            else:
                self._stats['failed_directives'] += 1
                return self._create_error_response(header, 'ENDPOINT_UNREACHABLE',
                                                  result.get('error', 'Service call failed'))

        except Exception as e:
            log_error(f"[{correlation_id}] Brightness control failed: {str(e)}")
            self._stats['failed_directives'] += 1
            return self._create_error_response(directive.get('header', {}), 'INTERNAL_ERROR', str(e))

    def handle_thermostat_control(self, directive: Dict[str, Any],
                                  ha_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Handle Alexa ThermostatController directives."""
        correlation_id = generate_correlation_id()
        
        try:
            self._stats['total_directives'] += 1
            
            endpoint = directive.get('endpoint', {})
            entity_id = endpoint.get('endpointId')
            header = directive.get('header', {})
            payload = directive.get('payload', {})

            log_info(f"[{correlation_id}] Thermostat control for {entity_id}")

            service_data = {}
            if 'targetSetpoint' in payload:
                service_data['temperature'] = payload['targetSetpoint'].get('value')
            if 'thermostatMode' in payload:
                service_data['hvac_mode'] = payload['thermostatMode'].get('value', '').lower()

            result = call_ha_service('climate', 'set_temperature', ha_config, entity_id, service_data)

            if result.get('success'):
                self._stats['successful_directives'] += 1
                increment_counter('alexa_thermostat_set')
                return self._create_thermostat_response(header, entity_id, service_data)
            else:
                self._stats['failed_directives'] += 1
                return self._create_error_response(header, 'ENDPOINT_UNREACHABLE',
                                                  result.get('error', 'Service call failed'))

        except Exception as e:
            log_error(f"[{correlation_id}] Thermostat control failed: {str(e)}")
            self._stats['failed_directives'] += 1
            return self._create_error_response(directive.get('header', {}), 'INTERNAL_ERROR', str(e))

    def handle_accept_grant(self, directive: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Alexa Authorization AcceptGrant."""
        correlation_id = generate_correlation_id()
        
        log_info(f"[{correlation_id}] Handling AcceptGrant")
        increment_counter('alexa_accept_grant')
        
        header = directive.get('header', {})
        return {
            'event': {
                'header': {
                    'namespace': 'Alexa.Authorization',
                    'name': 'AcceptGrant.Response',
                    'messageId': header.get('messageId', 'unknown'),
                    'payloadVersion': '3'
                },
                'payload': {}
            }
        }

    def _create_power_response(self, header: Dict[str, Any], entity_id: str, 
                              is_on: bool) -> Dict[str, Any]:
        """Create Alexa power control response."""
        return {
            'event': {
                'header': {
                    'namespace': 'Alexa',
                    'name': 'Response',
                    'messageId': header.get('messageId', 'unknown'),
                    'correlationToken': header.get('correlationToken'),
                    'payloadVersion': '3'
                },
                'endpoint': {
                    'endpointId': entity_id
                },
                'payload': {}
            },
            'context': {
                'properties': [{
                    'namespace': 'Alexa.PowerController',
                    'name': 'powerState',
                    'value': 'ON' if is_on else 'OFF',
                    'timeOfSample': '2024-01-01T00:00:00Z',
                    'uncertaintyInMilliseconds': 500
                }]
            }
        }

    def _create_brightness_response(self, header: Dict[str, Any], entity_id: str,
                                    brightness: int) -> Dict[str, Any]:
        """Create Alexa brightness control response."""
        return {
            'event': {
                'header': {
                    'namespace': 'Alexa',
                    'name': 'Response',
                    'messageId': header.get('messageId', 'unknown'),
                    'correlationToken': header.get('correlationToken'),
                    'payloadVersion': '3'
                },
                'endpoint': {
                    'endpointId': entity_id
                },
                'payload': {}
            },
            'context': {
                'properties': [{
                    'namespace': 'Alexa.BrightnessController',
                    'name': 'brightness',
                    'value': brightness,
                    'timeOfSample': '2024-01-01T00:00:00Z',
                    'uncertaintyInMilliseconds': 500
                }]
            }
        }

    def _create_thermostat_response(self, header: Dict[str, Any], entity_id: str,
                                    service_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create Alexa thermostat control response."""
        return {
            'event': {
                'header': {
                    'namespace': 'Alexa',
                    'name': 'Response',
                    'messageId': header.get('messageId', 'unknown'),
                    'correlationToken': header.get('correlationToken'),
                    'payloadVersion': '3'
                },
                'endpoint': {
                    'endpointId': entity_id
                },
                'payload': {}
            }
        }

    def _create_error_response(self, header: Dict[str, Any], error_type: str,
                              message: str) -> Dict[str, Any]:
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

    def get_stats(self) -> Dict[str, Any]:
        """Get Alexa manager statistics."""
        return {
            **self._stats,
            'success_rate': (self._stats['successful_directives'] / self._stats['total_directives'] * 100)
                           if self._stats['total_directives'] > 0 else 0.0
        }

# EOF
