"""
Home Assistant Alexa - Gateway-Optimized Alexa Smart Home Integration
Version: 2025.10.03.02
Description: Alexa Smart Home API integration with full gateway pattern compliance

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

from ha_common import (
    HABaseManager, call_ha_api, call_ha_service, batch_get_states,
    SingletonManager, is_ha_available, get_ha_config, HA_CACHE_TTL_ENTITIES
)


class AlexaSmartHomeManager(HABaseManager):
    """Manages Alexa Smart Home API integration with gateway pattern."""
    
    def __init__(self):
        super().__init__()
        self._stats = {
            'total_directives': 0,
            'successful_directives': 0,
            'failed_directives': 0,
            'discoveries': 0
        }
    
    def get_feature_name(self) -> str:
        return "alexa_smarthome"
    
    def handle_discovery(
        self,
        ha_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Handle Alexa device discovery with circuit breaker."""
        from .shared_utilities import (
            create_operation_context, close_operation_context,
            handle_operation_error, cache_operation_result
        )
        
        context = create_operation_context('alexa', 'discovery')
        
        try:
            if not is_ha_available():
                close_operation_context(context, success=False)
                return handle_operation_error(
                    'alexa', 'discovery',
                    Exception("Home Assistant circuit breaker open"),
                    context['correlation_id']
                )
            
            config = ha_config or get_ha_config()
            
            def _discover_devices():
                response = batch_get_states(None, config, use_cache=True)
                
                if not response.get('success'):
                    return []
                
                states = response.get('data', [])
                endpoints = []
                
                for state in states:
                    entity_id = state.get('entity_id', '')
                    domain = entity_id.split('.')[0] if '.' in entity_id else ''
                    
                    if domain in ['light', 'switch', 'fan', 'climate', 'cover', 'lock', 'media_player']:
                        endpoint = self._build_endpoint(state, domain)
                        if endpoint:
                            endpoints.append(endpoint)
                
                return endpoints
            
            endpoints = cache_operation_result(
                operation_name="alexa_discovery",
                func=_discover_devices,
                ttl=HA_CACHE_TTL_ENTITIES,
                cache_key_prefix="alexa_endpoints"
            )
            
            self._stats['discoveries'] += 1
            self._stats['total_directives'] += 1
            self._stats['successful_directives'] += 1
            
            close_operation_context(context, success=True)
            
            increment_counter('alexa_discovery')
            
            return create_success_response(
                f"Discovered {len(endpoints)} devices",
                {'endpoints': endpoints, 'count': len(endpoints)}
            )
            
        except Exception as e:
            self._stats['failed_directives'] += 1
            close_operation_context(context, success=False)
            return handle_operation_error('alexa', 'discovery', e, context['correlation_id'])
    
    def handle_power_control(
        self,
        directive: Dict[str, Any],
        ha_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Handle Alexa power control directive with circuit breaker."""
        from .shared_utilities import (
            create_operation_context, close_operation_context, handle_operation_error
        )
        
        endpoint = directive.get('endpoint', {})
        entity_id = endpoint.get('endpointId', '')
        header = directive.get('header', {})
        name = header.get('name', '')
        
        context = create_operation_context('alexa', 'power_control',
                                          entity_id=entity_id, directive=name)
        
        try:
            if not is_ha_available():
                close_operation_context(context, success=False)
                return handle_operation_error(
                    'alexa', 'power_control',
                    Exception("Home Assistant circuit breaker open"),
                    context['correlation_id']
                )
            
            config = ha_config or get_ha_config()
            domain = entity_id.split('.')[0] if '.' in entity_id else ''
            service = 'turn_on' if name == 'TurnOn' else 'turn_off'
            
            result = call_ha_service(domain, service, config, entity_id)
            
            self._stats['total_directives'] += 1
            if result.get('success'):
                self._stats['successful_directives'] += 1
            else:
                self._stats['failed_directives'] += 1
            
            close_operation_context(context, success=result.get('success', False), result=result)
            
            increment_counter('alexa_power_control')
            
            return self._create_alexa_response(
                entity_id,
                "Alexa.PowerController",
                "powerState",
                {"value": "ON" if service == "turn_on" else "OFF"}
            )
            
        except Exception as e:
            self._stats['failed_directives'] += 1
            close_operation_context(context, success=False)
            return handle_operation_error('alexa', 'power_control', e, context['correlation_id'])
    
    def handle_brightness_control(
        self,
        directive: Dict[str, Any],
        ha_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Handle Alexa brightness control with circuit breaker."""
        from .shared_utilities import (
            create_operation_context, close_operation_context, handle_operation_error
        )
        
        endpoint = directive.get('endpoint', {})
        entity_id = endpoint.get('endpointId', '')
        payload = directive.get('payload', {})
        brightness = payload.get('brightness', 100)
        
        context = create_operation_context('alexa', 'brightness_control',
                                          entity_id=entity_id, brightness=brightness)
        
        try:
            if not is_ha_available():
                close_operation_context(context, success=False)
                return handle_operation_error(
                    'alexa', 'brightness_control',
                    Exception("Home Assistant circuit breaker open"),
                    context['correlation_id']
                )
            
            config = ha_config or get_ha_config()
            
            service_data = {"brightness_pct": brightness}
            result = call_ha_service("light", "turn_on", config, entity_id, service_data)
            
            self._stats['total_directives'] += 1
            if result.get('success'):
                self._stats['successful_directives'] += 1
            else:
                self._stats['failed_directives'] += 1
            
            close_operation_context(context, success=result.get('success', False), result=result)
            
            increment_counter('alexa_brightness_control')
            
            return self._create_alexa_response(
                entity_id,
                "Alexa.BrightnessController",
                "brightness",
                {"value": brightness}
            )
            
        except Exception as e:
            self._stats['failed_directives'] += 1
            close_operation_context(context, success=False)
            return handle_operation_error('alexa', 'brightness_control', e, context['correlation_id'])
    
    def handle_thermostat_control(
        self,
        directive: Dict[str, Any],
        ha_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Handle Alexa thermostat control with circuit breaker."""
        from .shared_utilities import (
            create_operation_context, close_operation_context, handle_operation_error
        )
        
        endpoint = directive.get('endpoint', {})
        entity_id = endpoint.get('endpointId', '')
        payload = directive.get('payload', {})
        
        context = create_operation_context('alexa', 'thermostat_control',
                                          entity_id=entity_id)
        
        try:
            if not is_ha_available():
                close_operation_context(context, success=False)
                return handle_operation_error(
                    'alexa', 'thermostat_control',
                    Exception("Home Assistant circuit breaker open"),
                    context['correlation_id']
                )
            
            config = ha_config or get_ha_config()
            
            target_temp = payload.get('targetSetpoint', {}).get('value')
            service_data = {"temperature": target_temp} if target_temp else {}
            
            result = call_ha_service("climate", "set_temperature", config, entity_id, service_data)
            
            self._stats['total_directives'] += 1
            if result.get('success'):
                self._stats['successful_directives'] += 1
            else:
                self._stats['failed_directives'] += 1
            
            close_operation_context(context, success=result.get('success', False), result=result)
            
            increment_counter('alexa_thermostat_control')
            
            return self._create_alexa_response(
                entity_id,
                "Alexa.ThermostatController",
                "targetSetpoint",
                {"value": target_temp, "scale": "CELSIUS"}
            )
            
        except Exception as e:
            self._stats['failed_directives'] += 1
            close_operation_context(context, success=False)
            return handle_operation_error('alexa', 'thermostat_control', e, context['correlation_id'])
    
    def _build_endpoint(self, state: Dict[str, Any], domain: str) -> Optional[Dict[str, Any]]:
        """Build Alexa endpoint from HA state."""
        entity_id = state.get('entity_id')
        attributes = state.get('attributes', {})
        
        capabilities = []
        display_categories = []
        
        if domain == 'light':
            capabilities.append(self._power_capability())
            capabilities.append(self._brightness_capability())
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
        
        capabilities.append({
            "type": "AlexaInterface",
            "interface": "Alexa",
            "version": "3"
        })
        
        return {
            "endpointId": entity_id,
            "friendlyName": attributes.get('friendly_name', entity_id),
            "manufacturerName": "Home Assistant",
            "description": f"HA {domain}",
            "displayCategories": display_categories,
            "capabilities": capabilities
        }
    
    def _power_capability(self) -> Dict[str, Any]:
        """Build power controller capability."""
        return {
            "type": "AlexaInterface",
            "interface": "Alexa.PowerController",
            "version": "3",
            "properties": {
                "supported": [{"name": "powerState"}],
                "proactivelyReported": False,
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
                "proactivelyReported": False,
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
                "proactivelyReported": False,
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
                "proactivelyReported": False,
                "retrievable": True
            }
        }
    
    def _create_alexa_response(
        self,
        endpoint_id: str,
        interface: str,
        property_name: str,
        property_value: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create standardized Alexa response."""
        return {
            "event": {
                "header": {
                    "namespace": interface,
                    "name": "Response",
                    "payloadVersion": "3",
                    "messageId": generate_correlation_id()
                },
                "endpoint": {
                    "endpointId": endpoint_id
                },
                "payload": {}
            },
            "context": {
                "properties": [{
                    "namespace": interface,
                    "name": property_name,
                    "value": property_value,
                    "timeOfSample": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    "uncertaintyInMilliseconds": 500
                }]
            }
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get Alexa integration statistics."""
        base_stats = super().get_stats()
        base_stats.update(self._stats)
        
        if self._stats['total_directives'] > 0:
            base_stats['success_rate'] = (
                self._stats['successful_directives'] / self._stats['total_directives'] * 100
            )
        
        return base_stats


_singleton_manager = SingletonManager()


def get_alexa_manager() -> AlexaSmartHomeManager:
    """Get or create Alexa manager singleton."""
    return _singleton_manager.get_or_create(
        'alexa_manager',
        AlexaSmartHomeManager
    )


def handle_alexa_directive(
    directive: Dict[str, Any],
    ha_config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Handle any Alexa directive with routing."""
    from .shared_utilities import create_operation_context, close_operation_context
    
    context = create_operation_context('alexa', 'directive_router')
    
    try:
        manager = get_alexa_manager()
        
        header = directive.get('header', {})
        namespace = header.get('namespace', '')
        name = header.get('name', '')
        
        if namespace == 'Alexa.Discovery' and name == 'Discover':
            result = manager.handle_discovery(ha_config)
        elif namespace == 'Alexa.PowerController':
            result = manager.handle_power_control(directive, ha_config)
        elif namespace == 'Alexa.BrightnessController':
            result = manager.handle_brightness_control(directive, ha_config)
        elif namespace == 'Alexa.ThermostatController':
            result = manager.handle_thermostat_control(directive, ha_config)
        else:
            result = create_error_response(
                f"Unsupported directive: {namespace}.{name}",
                {'directive': directive}
            )
        
        close_operation_context(context, success=result.get('success', False))
        return result
        
    except Exception as e:
        close_operation_context(context, success=False)
        log_error(f"Alexa directive handling failed: {str(e)}")
        return create_error_response("Directive handling failed", {"error": str(e)})


def get_alexa_stats() -> Dict[str, Any]:
    """Get Alexa integration statistics."""
    manager = get_alexa_manager()
    return manager.get_stats()


def cleanup_alexa() -> Dict[str, Any]:
    """Cleanup Alexa manager resources."""
    try:
        _singleton_manager.cleanup('alexa_manager')
        return create_success_response("Alexa manager cleaned up successfully", {})
    except Exception as e:
        return create_error_response("Cleanup failed", {"error": str(e)})


__all__ = [
    'AlexaSmartHomeManager',
    'get_alexa_manager',
    'handle_alexa_directive',
    'get_alexa_stats',
    'cleanup_alexa'
]
