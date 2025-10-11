"""
homeassistant_alexa.py
Version: 2025.10.11.01
Description: Alexa Smart Home API integration using REST API
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
import time
from typing import Dict, Any, Optional, List
from gateway import (
    log_info, log_error, create_success_response, create_error_response,
    generate_correlation_id, record_metric, increment_counter
)
try:
    from ha_common import (
        batch_get_states, call_ha_service, is_ha_available, get_ha_config,
        HA_CACHE_TTL_ENTITIES
    )
except ImportError:
    # Fallback if ha_common doesn't exist
    def batch_get_states(*args, **kwargs):
        return {'success': False, 'error': 'ha_common not available'}
    def call_ha_service(*args, **kwargs):
        return {'success': False, 'error': 'ha_common not available'}
    def is_ha_available():
        return False
    def get_ha_config():
        return {}
    HA_CACHE_TTL_ENTITIES = 300

class AlexaSmartHomeManager:
    """Manages Alexa Smart Home API integration."""

    def __init__(self):
        self._stats = {
            'total_directives': 0,
            'successful_directives': 0,
            'failed_directives': 0,
            'discoveries': 0
        }

    def handle_discovery(self, ha_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Handle Alexa device discovery."""
        try:
            if not is_ha_available():
                return create_error_response(
                    'discovery_failed',
                    'Home Assistant circuit breaker open'
                )

            config = ha_config or get_ha_config()

            # Get all states from /api/states
            response = batch_get_states(None, config, use_cache=True)

            if not response.get('success'):
                return create_error_response(
                    'discovery_failed',
                    response.get('error', 'Failed to get states')
                )

            states = response.get('data', [])
            endpoints = []

            # Transform HA entities to Alexa endpoints
            for state in states:
                entity_id = state.get('entity_id', '')
                domain = entity_id.split('.')[0] if '.' in entity_id else ''

                if domain in ['light', 'switch', 'fan', 'climate', 'cover', 'lock', 'media_player']:
                    endpoint = self._build_endpoint(state, domain)
                    if endpoint:
                        endpoints.append(endpoint)

            self._stats['discoveries'] += 1
            self._stats['total_directives'] += 1
            self._stats['successful_directives'] += 1

            increment_counter('alexa_discovery')

            log_info(f"Discovered {len(endpoints)} devices")

            return create_success_response(
                f"Discovered {len(endpoints)} devices",
                {'endpoints': endpoints, 'count': len(endpoints)}
            )

        except Exception as e:
            self._stats['failed_directives'] += 1
            log_error(f"Discovery failed: {str(e)}")
            return create_error_response('discovery_failed', str(e))

    def handle_power_control(
        self,
        directive: Dict[str, Any],
        ha_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Handle Alexa power control directive."""
        try:
            endpoint = directive.get('endpoint', {})
            entity_id = endpoint.get('endpointId', '')
            header = directive.get('header', {})
            name = header.get('name', '')

            if not entity_id:
                return self._create_error_response(header, 'INVALID_DIRECTIVE', 'Missing entity ID')

            if not is_ha_available():
                return self._create_error_response(header, 'ENDPOINT_UNREACHABLE', 'Home Assistant unavailable')

            config = ha_config or get_ha_config()
            domain = entity_id.split('.')[0] if '.' in entity_id else ''

            # Determine service based on directive
            if name == 'TurnOn':
                service = 'turn_on'
                power_state = 'ON'
            elif name == 'TurnOff':
                service = 'turn_off'
                power_state = 'OFF'
            else:
                return self._create_error_response(header, 'INVALID_DIRECTIVE', f'Unknown power command: {name}')

            # Call HA service via /api/services/domain/service
            result = call_ha_service(domain, service, config, entity_id)

            self._stats['total_directives'] += 1

            if result.get('success'):
                self._stats['successful_directives'] += 1
                return self._create_alexa_response(
                    entity_id,
                    'Alexa.PowerController',
                    'powerState',
                    power_state,
                    header.get('messageId')
                )
            else:
                self._stats['failed_directives'] += 1
                return self._create_error_response(header, 'ENDPOINT_UNREACHABLE', result.get('error', 'Service call failed'))

        except Exception as e:
            self._stats['failed_directives'] += 1
            log_error(f"Power control failed: {str(e)}")
            return self._create_error_response(
                directive.get('header', {}),
                'INTERNAL_ERROR',
                str(e)
            )

    def handle_brightness_control(
        self,
        directive: Dict[str, Any],
        ha_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Handle Alexa brightness control directive."""
        try:
            endpoint = directive.get('endpoint', {})
            entity_id = endpoint.get('endpointId', '')
            header = directive.get('header', {})
            name = header.get('name', '')
            payload = directive.get('payload', {})

            if not is_ha_available():
                return self._create_error_response(header, 'ENDPOINT_UNREACHABLE', 'Home Assistant unavailable')

            config = ha_config or get_ha_config()

            if name == 'SetBrightness':
                brightness = payload.get('brightness', 100)
                service_data = {'brightness_pct': brightness}
            elif name == 'AdjustBrightness':
                brightness_delta = payload.get('brightnessDelta', 0)
                # For adjust, we'd need current state first
                service_data = {'brightness_step_pct': brightness_delta}
            else:
                return self._create_error_response(header, 'INVALID_DIRECTIVE', f'Unknown brightness command: {name}')

            result = call_ha_service('light', 'turn_on', config, entity_id, service_data)

            self._stats['total_directives'] += 1

            if result.get('success'):
                self._stats['successful_directives'] += 1
                return self._create_alexa_response(
                    entity_id,
                    'Alexa.BrightnessController',
                    'brightness',
                    payload.get('brightness', 100),
                    header.get('messageId')
                )
            else:
                self._stats['failed_directives'] += 1
                return self._create_error_response(header, 'ENDPOINT_UNREACHABLE', result.get('error', 'Service call failed'))

        except Exception as e:
            self._stats['failed_directives'] += 1
            log_error(f"Brightness control failed: {str(e)}")
            return self._create_error_response(
                directive.get('header', {}),
                'INTERNAL_ERROR',
                str(e)
            )

    def handle_thermostat_control(
        self,
        directive: Dict[str, Any],
        ha_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Handle Alexa thermostat control directive."""
        try:
            endpoint = directive.get('endpoint', {})
            entity_id = endpoint.get('endpointId', '')
            payload = directive.get('payload', {})
            header = directive.get('header', {})

            if not is_ha_available():
                return self._create_error_response(header, 'ENDPOINT_UNREACHABLE', 'Home Assistant unavailable')

            config = ha_config or get_ha_config()

            target_temp = payload.get('targetSetpoint', {}).get('value')
            service_data = {"temperature": target_temp} if target_temp else {}

            result = call_ha_service("climate", "set_temperature", config, entity_id, service_data)

            self._stats['total_directives'] += 1

            if result.get('success'):
                self._stats['successful_directives'] += 1
                return self._create_alexa_response(
                    entity_id,
                    'Alexa.ThermostatController',
                    'targetSetpoint',
                    {"value": target_temp, "scale": "CELSIUS"},
                    header.get('messageId')
                )
            else:
                self._stats['failed_directives'] += 1
                return self._create_error_response(header, 'ENDPOINT_UNREACHABLE', result.get('error', 'Service call failed'))

        except Exception as e:
            self._stats['failed_directives'] += 1
            log_error(f"Thermostat control failed: {str(e)}")
            return self._create_error_response(
                directive.get('header', {}),
                'INTERNAL_ERROR',
                str(e)
            )

    def handle_accept_grant(
        self,
        directive: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle OAuth AcceptGrant directive."""
        try:
            from config_manager import store_parameter

            payload = directive.get('payload', {})
            grant = payload.get('grant', {})
            code = grant.get('code', '')

            # Store grant code in Parameter Store
            store_parameter('alexa_grant_code', code)

            log_info("AcceptGrant processed successfully")

            return {
                "event": {
                    "header": {
                        "namespace": "Alexa.Authorization",
                        "name": "AcceptGrant.Response",
                        "payloadVersion": "3",
                        "messageId": directive.get('header', {}).get('messageId')
                    },
                    "payload": {}
                }
            }

        except Exception as e:
            log_error(f"AcceptGrant failed: {str(e)}")
            return self._create_error_response(
                directive.get('header', {}),
                'ACCEPT_GRANT_FAILED',
                str(e)
            )

    def _build_endpoint(self, state: Dict[str, Any], domain: str) -> Optional[Dict[str, Any]]:
        """Build Alexa endpoint from HA state."""
        entity_id = state.get('entity_id')
        attributes = state.get('attributes', {})

        capabilities = []
        display_categories = []

        if domain == 'light':
            capabilities.append(self._power_capability())
            capabilities.append(self._brightness_capability())

            # Add color if supported
            if attributes.get('supported_color_modes'):
                capabilities.append(self._color_capability())
                capabilities.append(self._color_temperature_capability())

            display_categories = ["LIGHT"]

        elif domain == 'switch':
            capabilities.append(self._power_capability())
            display_categories = ["SWITCH"]

        elif domain == 'fan':
            capabilities.append(self._power_capability())
            display_categories = ["FAN"]

        elif domain == 'climate':
            capabilities.append(self._thermostat_capability())
            display_categories = ["THERMOSTAT"]

        elif domain == 'cover':
            capabilities.append(self._power_capability())
            display_categories = ["DOOR"]

        elif domain == 'lock':
            capabilities.append(self._lock_capability())
            display_categories = ["SMARTLOCK"]

        elif domain == 'media_player':
            capabilities.append(self._power_capability())
            display_categories = ["SPEAKER"]

        if not capabilities:
            return None

        # Add endpoint health capability
        capabilities.append({
            "type": "AlexaInterface",
            "interface": "Alexa.EndpointHealth",
            "version": "3",
            "properties": {
                "supported": [{"name": "connectivity"}],
                "proactivelyReported": True,
                "retrievable": True
            }
        })

        # Add Alexa interface
        capabilities.append({
            "type": "AlexaInterface",
            "interface": "Alexa",
            "version": "3"
        })

        return {
            "endpointId": entity_id,
            "friendlyName": attributes.get('friendly_name', entity_id),
            "description": f"{entity_id} via Home Assistant",
            "manufacturerName": "Home Assistant",
            "displayCategories": display_categories,
            "cookie": {},
            "capabilities": capabilities,
            "additionalAttributes": {
                "manufacturer": "Home Assistant",
                "model": domain,
                "softwareVersion": "2025.9.4",
                "customIdentifier": f"-{entity_id}"
            }
        }

    def _power_capability(self) -> Dict[str, Any]:
        """Build power controller capability."""
        return {
            "type": "AlexaInterface",
            "interface": "Alexa.PowerController",
            "version": "3",
            "properties": {
                "supported": [{"name": "powerState"}],
                "proactivelyReported": True,
                "retrievable": True
            }
        }

    def _brightness_capability(self) -> Dict[str, Any]:
        """Build brightness controller capability."""
        return {
            "type": "AlexaInterface",
            "interface": "Alexa.BrightnessController",
            "version": "3",
            "properties": {
                "supported": [{"name": "brightness"}],
                "proactivelyReported": True,
                "retrievable": True
            }
        }

    def _color_capability(self) -> Dict[str, Any]:
        """Build color controller capability."""
        return {
            "type": "AlexaInterface",
            "interface": "Alexa.ColorController",
            "version": "3",
            "properties": {
                "supported": [{"name": "color"}],
                "proactivelyReported": True,
                "retrievable": True
            }
        }

    def _color_temperature_capability(self) -> Dict[str, Any]:
        """Build color temperature controller capability."""
        return {
            "type": "AlexaInterface",
            "interface": "Alexa.ColorTemperatureController",
            "version": "3",
            "properties": {
                "supported": [{"name": "colorTemperatureInKelvin"}],
                "proactivelyReported": True,
                "retrievable": True
            }
        }

    def _thermostat_capability(self) -> Dict[str, Any]:
        """Build thermostat controller capability."""
        return {
            "type": "AlexaInterface",
            "interface": "Alexa.ThermostatController",
            "version": "3",
            "properties": {
                "supported": [
                    {"name": "targetSetpoint"},
                    {"name": "thermostatMode"}
                ],
                "proactivelyReported": True,
                "retrievable": True
            }
        }

    def _lock_capability(self) -> Dict[str, Any]:
        """Build lock controller capability."""
        return {
            "type": "AlexaInterface",
            "interface": "Alexa.LockController",
            "version": "3",
            "properties": {
                "supported": [{"name": "lockState"}],
                "proactivelyReported": True,
                "retrievable": True
            }
        }

    def _create_alexa_response(
        self,
        endpoint_id: str,
        namespace: str,
        name: str,
        value: Any,
        correlation_token: str = None
    ) -> Dict[str, Any]:
        """Create Alexa response."""
        return {
            "event": {
                "header": {
                    "namespace": "Alexa",
                    "name": "Response",
                    "messageId": correlation_token or generate_correlation_id(),
                    "correlationToken": correlation_token,
                    "payloadVersion": "3"
                },
                "endpoint": {
                    "endpointId": endpoint_id
                },
                "payload": {}
            },
            "context": {
                "properties": [
                    {
                        "namespace": namespace,
                        "name": name,
                        "value": value,
                        "timeOfSample": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                        "uncertaintyInMilliseconds": 500
                    }
                ]
            }
        }

    def _create_error_response(self, header: Dict[str, Any], error_type: str, message: str) -> Dict[str, Any]:
        """Create Alexa error response."""
        return {
            "event": {
                "header": {
                    "namespace": "Alexa",
                    "name": "ErrorResponse",
                    "messageId": header.get('messageId', generate_correlation_id()),
                    "payloadVersion": "3"
                },
                "payload": {
                    "type": error_type,
                    "message": message
                }
            }
        }
# EOF
