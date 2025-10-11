"""
home_assistant_devices.py
Version: 2025.10.11.01
Description: Home Assistant Device Control

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
from typing import Dict, Any, List, Optional

from gateway import (
    log_info, log_error,
    create_success_response, create_error_response,
    generate_correlation_id,
    increment_counter
)

from ha_common import (
    get_ha_config,
    call_ha_service,
    get_entity_state,
    batch_get_states,
    is_ha_available,
    get_cache_section,
    set_cache_section,
    HA_CACHE_TTL_ENTITIES,
    HA_CACHE_TTL_STATE
)


class HADeviceManager:
    """Manages Home Assistant device control with circuit breaker protection."""
    
    def __init__(self):
        self._stats = {
            'operations': 0,
            'successes': 0,
            'failures': 0
        }
    
    def get_feature_name(self) -> str:
        return "device"
    
    def control_device(
        self,
        device_id: str,
        action: str,
        ha_config: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Control device with circuit breaker and operation context."""
        from shared_utilities import (
            create_operation_context, close_operation_context, handle_operation_error
        )
        
        context = create_operation_context('ha_device', 'control', 
                                          device_id=device_id, action=action)
        
        try:
            if not is_ha_available():
                close_operation_context(context, success=False)
                return handle_operation_error(
                    'ha_device', 'control',
                    Exception("Home Assistant circuit breaker open"),
                    context['correlation_id']
                )
            
            config = ha_config or get_ha_config()
            entity_id = self._resolve_entity_id(device_id, config)
            
            if not entity_id:
                close_operation_context(context, success=False)
                return handle_operation_error(
                    'ha_device', 'control',
                    ValueError(f"Device not found: {device_id}"),
                    context['correlation_id']
                )
            
            domain = entity_id.split('.')[0]
            result = call_ha_service(domain, action, config, entity_id, kwargs)
            
            self._stats['operations'] += 1
            if result.get('success'):
                self._stats['successes'] += 1
            else:
                self._stats['failures'] += 1
            
            close_operation_context(context, success=result.get('success', False), result=result)
            
            increment_counter(f'ha_device_{domain}_{action}')
            
            return create_success_response(
                f"Device {entity_id} controlled: {action}",
                {
                    'entity_id': entity_id,
                    'domain': domain,
                    'action': action,
                    'result': result
                }
            )
            
        except Exception as e:
            self._stats['failures'] += 1
            close_operation_context(context, success=False)
            return handle_operation_error('ha_device', 'control', e, context['correlation_id'])
    
    def set_device_state(
        self,
        device_id: str,
        state: str,
        ha_config: Optional[Dict[str, Any]] = None,
        **attributes
    ) -> Dict[str, Any]:
        """Set device state with circuit breaker protection."""
        from shared_utilities import (
            create_operation_context, close_operation_context, handle_operation_error
        )
        
        context = create_operation_context('ha_device', 'set_state',
                                          device_id=device_id, state=state)
        
        try:
            if not is_ha_available():
                close_operation_context(context, success=False)
                return handle_operation_error(
                    'ha_device', 'set_state',
                    Exception("Home Assistant circuit breaker open"),
                    context['correlation_id']
                )
            
            config = ha_config or get_ha_config()
            entity_id = self._resolve_entity_id(device_id, config)
            
            if not entity_id:
                close_operation_context(context, success=False)
                return handle_operation_error(
                    'ha_device', 'set_state',
                    ValueError(f"Device not found: {device_id}"),
                    context['correlation_id']
                )
            
            domain = entity_id.split('.')[0]
            
            if domain == "light":
                result = self._set_light_state(entity_id, state, config, **attributes)
            elif domain in ["switch", "fan"]:
                result = self._set_switch_fan_state(entity_id, state, config)
            elif domain == "climate":
                result = self._set_climate_state(entity_id, state, config, **attributes)
            else:
                result = call_ha_service(
                    "homeassistant", "set_state",
                    config, entity_id,
                    {"state": state, **attributes}
                )
            
            self._stats['operations'] += 1
            if result.get('success'):
                self._stats['successes'] += 1
            else:
                self._stats['failures'] += 1
            
            close_operation_context(context, success=result.get('success', False), result=result)
            
            return create_success_response(
                f"Device {entity_id} state set to {state}",
                {
                    'entity_id': entity_id,
                    'domain': domain,
                    'state': state,
                    'attributes': attributes,
                    'result': result
                }
            )
            
        except Exception as e:
            self._stats['failures'] += 1
            close_operation_context(context, success=False)
            return handle_operation_error('ha_device', 'set_state', e, context['correlation_id'])
    
    def get_device_state(
        self,
        device_id: str,
        ha_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Get device state with circuit breaker and caching."""
        from shared_utilities import (
            create_operation_context, close_operation_context, 
            handle_operation_error, cache_operation_result
        )
        
        context = create_operation_context('ha_device', 'get_state', device_id=device_id)
        
        try:
            if not is_ha_available():
                close_operation_context(context, success=False)
                return handle_operation_error(
                    'ha_device', 'get_state',
                    Exception("Home Assistant circuit breaker open"),
                    context['correlation_id']
                )
            
            config = ha_config or get_ha_config()
            entity_id = self._resolve_entity_id(device_id, config)
            
            if not entity_id:
                close_operation_context(context, success=False)
                return handle_operation_error(
                    'ha_device', 'get_state',
                    ValueError(f"Device not found: {device_id}"),
                    context['correlation_id']
                )
            
            state_data = get_entity_state(entity_id, config, use_cache=True)
            
            close_operation_context(context, success=True, result=state_data)
            
            domain = entity_id.split('.')[0]
            
            return create_success_response(
                f"Retrieved state for {entity_id}",
                {
                    'entity_id': entity_id,
                    'domain': domain,
                    'state': state_data.get('state'),
                    'attributes': state_data.get('attributes', {}),
                    'last_changed': state_data.get('last_changed'),
                    'last_updated': state_data.get('last_updated')
                }
            )
            
        except Exception as e:
            self._stats['failures'] += 1
            close_operation_context(context, success=False)
            return handle_operation_error('ha_device', 'get_state', e, context['correlation_id'])
    
    def list_devices_by_domain(
        self,
        domain: str,
        ha_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """List devices by domain with caching and circuit breaker."""
        from shared_utilities import (
            create_operation_context, close_operation_context,
            handle_operation_error, cache_operation_result
        )
        
        context = create_operation_context('ha_device', 'list', domain=domain)
        
        try:
            if not is_ha_available():
                close_operation_context(context, success=False)
                return handle_operation_error(
                    'ha_device', 'list',
                    Exception("Home Assistant circuit breaker open"),
                    context['correlation_id']
                )
            
            config = ha_config or get_ha_config()
            
            def _get_devices():
                response = batch_get_states(None, config, use_cache=True)
                if not response.get('success'):
                    return []
                
                states = response.get('data', [])
                return [
                    {
                        'entity_id': state.get('entity_id'),
                        'name': state.get('attributes', {}).get('friendly_name', state.get('entity_id')),
                        'state': state.get('state')
                    }
                    for state in states
                    if state.get('entity_id', '').startswith(f"{domain}.")
                ]
            
            devices = cache_operation_result(
                operation_name=f"list_devices_{domain}",
                func=_get_devices,
                ttl=HA_CACHE_TTL_ENTITIES,
                cache_key_prefix=f"ha_devices_{domain}"
            )
            
            close_operation_context(context, success=True)
            
            return create_success_response(
                f"Retrieved {len(devices)} {domain} devices",
                {
                    'domain': domain,
                    'devices': devices,
                    'count': len(devices)
                }
            )
            
        except Exception as e:
            close_operation_context(context, success=False)
            return handle_operation_error('ha_device', 'list', e, context['correlation_id'])
    
    def _set_light_state(self, entity_id: str, state: str, config: Dict[str, Any], **attributes) -> Dict[str, Any]:
        """Set light state with attributes."""
        if state.lower() in ["on", "true", "1"]:
            service_data = {"entity_id": entity_id, **attributes}
            return call_ha_service("light", "turn_on", config, entity_id, service_data)
        else:
            return call_ha_service("light", "turn_off", config, entity_id)
    
    def _set_switch_fan_state(self, entity_id: str, state: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Set switch or fan state."""
        domain = entity_id.split('.')[0]
        if state.lower() in ["on", "true", "1"]:
            return call_ha_service(domain, "turn_on", config, entity_id)
        else:
            return call_ha_service(domain, "turn_off", config, entity_id)
    
    def _set_climate_state(self, entity_id: str, state: str, config: Dict[str, Any], **attributes) -> Dict[str, Any]:
        """Set climate state with attributes."""
        service_data = {"entity_id": entity_id, "hvac_mode": state, **attributes}
        return call_ha_service("climate", "set_hvac_mode", config, entity_id, service_data)
    
    def _resolve_entity_id(self, device_id: str, config: Dict[str, Any]) -> Optional[str]:
        """Resolve device ID to entity ID."""
        if '.' in device_id:
            return device_id
        
        response = batch_get_states(None, config, use_cache=True)
        if not response.get('success'):
            return None
        
        states = response.get('data', [])
        device_id_lower = device_id.lower()
        
        for state in states:
            entity_id = state.get('entity_id', '')
            friendly_name = state.get('attributes', {}).get('friendly_name', '').lower()
            
            if entity_id.lower() == device_id_lower or friendly_name == device_id_lower:
                return entity_id
        
        return None
    
    def get_stats(self) -> Dict[str, Any]:
        """Get device manager statistics."""
        return {
            "feature": self.get_feature_name(),
            **self._stats,
            "success_rate": (self._stats['successes'] / self._stats['operations'] * 100)
                           if self._stats['operations'] > 0 else 0.0
        }


_device_manager = HADeviceManager()


def control_device(device_id: str, action: str, ha_config: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
    """Control device via manager."""
    return _device_manager.control_device(device_id, action, ha_config, **kwargs)


def set_device_state(device_id: str, state: str, ha_config: Optional[Dict[str, Any]] = None, **attributes) -> Dict[str, Any]:
    """Set device state via manager."""
    return _device_manager.set_device_state(device_id, state, ha_config, **attributes)


def get_device_state(device_id: str, ha_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Get device state via manager."""
    return _device_manager.get_device_state(device_id, ha_config)


def list_devices_by_domain(domain: str, ha_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """List devices by domain via manager."""
    return _device_manager.list_devices_by_domain(domain, ha_config)


def get_device_stats() -> Dict[str, Any]:
    """Get device manager statistics."""
    return _device_manager.get_stats()


__all__ = [
    'HADeviceManager',
    'control_device',
    'set_device_state',
    'get_device_state',
    'list_devices_by_domain',
    'get_device_stats',
]

# EOF
