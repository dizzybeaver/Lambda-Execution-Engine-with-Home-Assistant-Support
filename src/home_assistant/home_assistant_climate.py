"""
Home Assistant Climate - Gateway-Optimized Climate Control
Version: 2025.10.03.02
Description: HVAC and climate device control with full gateway integration

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
    log_info, create_success_response, create_error_response, increment_counter
)

from ha_common import (
    HABaseManager, call_ha_service, get_entity_state, batch_get_states,
    SingletonManager, is_ha_available, get_ha_config, HA_CACHE_TTL_STATE,
    HA_CACHE_TTL_ENTITIES
)


class HAClimateManager(HABaseManager):
    """Manages Home Assistant climate devices with gateway pattern compliance."""
    
    def __init__(self):
        super().__init__()
        self._stats = {
            'total_operations': 0,
            'successful_operations': 0,
            'failed_operations': 0,
            'temperature_changes': 0,
            'mode_changes': 0
        }
    
    def get_feature_name(self) -> str:
        return "climate"
    
    def set_temperature(
        self,
        entity_id: str,
        temperature: float,
        ha_config: Optional[Dict[str, Any]] = None,
        target_temp_high: Optional[float] = None,
        target_temp_low: Optional[float] = None
    ) -> Dict[str, Any]:
        """Set climate device temperature with circuit breaker."""
        from .shared_utilities import (
            create_operation_context, close_operation_context, handle_operation_error
        )
        
        context = create_operation_context('ha_climate', 'set_temperature',
                                          entity_id=entity_id, temperature=temperature)
        
        try:
            if not is_ha_available():
                close_operation_context(context, success=False)
                return handle_operation_error(
                    'ha_climate', 'set_temperature',
                    Exception("Home Assistant circuit breaker open"),
                    context['correlation_id']
                )
            
            config = ha_config or get_ha_config()
            
            service_data = {
                "entity_id": entity_id,
                "temperature": temperature
            }
            
            if target_temp_high is not None:
                service_data["target_temp_high"] = target_temp_high
            if target_temp_low is not None:
                service_data["target_temp_low"] = target_temp_low
            
            result = call_ha_service("climate", "set_temperature", config, entity_id, service_data)
            
            self._stats['total_operations'] += 1
            self._stats['temperature_changes'] += 1
            if result.get('success'):
                self._stats['successful_operations'] += 1
            else:
                self._stats['failed_operations'] += 1
            
            close_operation_context(context, success=result.get('success', False), result=result)
            
            increment_counter('ha_climate_set_temperature')
            
            return create_success_response(
                f"Temperature set to {temperature}° for {entity_id}",
                {
                    'entity_id': entity_id,
                    'temperature': temperature,
                    'target_temp_high': target_temp_high,
                    'target_temp_low': target_temp_low,
                    'result': result
                }
            )
            
        except Exception as e:
            self._stats['failed_operations'] += 1
            close_operation_context(context, success=False)
            return handle_operation_error('ha_climate', 'set_temperature', e, context['correlation_id'])
    
    def set_hvac_mode(
        self,
        entity_id: str,
        hvac_mode: str,
        ha_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Set HVAC mode with circuit breaker."""
        from .shared_utilities import (
            create_operation_context, close_operation_context, handle_operation_error
        )
        
        context = create_operation_context('ha_climate', 'set_hvac_mode',
                                          entity_id=entity_id, mode=hvac_mode)
        
        try:
            if not is_ha_available():
                close_operation_context(context, success=False)
                return handle_operation_error(
                    'ha_climate', 'set_hvac_mode',
                    Exception("Home Assistant circuit breaker open"),
                    context['correlation_id']
                )
            
            config = ha_config or get_ha_config()
            
            service_data = {
                "entity_id": entity_id,
                "hvac_mode": hvac_mode
            }
            
            result = call_ha_service("climate", "set_hvac_mode", config, entity_id, service_data)
            
            self._stats['total_operations'] += 1
            self._stats['mode_changes'] += 1
            if result.get('success'):
                self._stats['successful_operations'] += 1
            else:
                self._stats['failed_operations'] += 1
            
            close_operation_context(context, success=result.get('success', False), result=result)
            
            increment_counter('ha_climate_set_hvac_mode')
            
            return create_success_response(
                f"HVAC mode set to {hvac_mode} for {entity_id}",
                {
                    'entity_id': entity_id,
                    'hvac_mode': hvac_mode,
                    'result': result
                }
            )
            
        except Exception as e:
            self._stats['failed_operations'] += 1
            close_operation_context(context, success=False)
            return handle_operation_error('ha_climate', 'set_hvac_mode', e, context['correlation_id'])
    
    def set_preset_mode(
        self,
        entity_id: str,
        preset_mode: str,
        ha_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Set climate preset mode with circuit breaker."""
        from .shared_utilities import (
            create_operation_context, close_operation_context, handle_operation_error
        )
        
        context = create_operation_context('ha_climate', 'set_preset_mode',
                                          entity_id=entity_id, preset=preset_mode)
        
        try:
            if not is_ha_available():
                close_operation_context(context, success=False)
                return handle_operation_error(
                    'ha_climate', 'set_preset_mode',
                    Exception("Home Assistant circuit breaker open"),
                    context['correlation_id']
                )
            
            config = ha_config or get_ha_config()
            
            service_data = {
                "entity_id": entity_id,
                "preset_mode": preset_mode
            }
            
            result = call_ha_service("climate", "set_preset_mode", config, entity_id, service_data)
            
            self._stats['total_operations'] += 1
            if result.get('success'):
                self._stats['successful_operations'] += 1
            else:
                self._stats['failed_operations'] += 1
            
            close_operation_context(context, success=result.get('success', False), result=result)
            
            increment_counter('ha_climate_set_preset_mode')
            
            return create_success_response(
                f"Preset mode set to {preset_mode} for {entity_id}",
                {
                    'entity_id': entity_id,
                    'preset_mode': preset_mode,
                    'result': result
                }
            )
            
        except Exception as e:
            self._stats['failed_operations'] += 1
            close_operation_context(context, success=False)
            return handle_operation_error('ha_climate', 'set_preset_mode', e, context['correlation_id'])
    
    def get_climate_state(
        self,
        entity_id: str,
        ha_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Get current climate device state with caching."""
        from .shared_utilities import (
            create_operation_context, close_operation_context, handle_operation_error
        )
        
        context = create_operation_context('ha_climate', 'get_state', entity_id=entity_id)
        
        try:
            if not is_ha_available():
                close_operation_context(context, success=False)
                return handle_operation_error(
                    'ha_climate', 'get_state',
                    Exception("Home Assistant circuit breaker open"),
                    context['correlation_id']
                )
            
            config = ha_config or get_ha_config()
            
            state = get_entity_state(entity_id, config, use_cache=True)
            
            if not state:
                close_operation_context(context, success=False)
                return create_error_response(
                    f"Climate device {entity_id} not found",
                    {'entity_id': entity_id}
                )
            
            attributes = state.get('attributes', {})
            
            climate_state = {
                'entity_id': entity_id,
                'current_temperature': attributes.get('current_temperature'),
                'temperature': attributes.get('temperature'),
                'target_temp_high': attributes.get('target_temp_high'),
                'target_temp_low': attributes.get('target_temp_low'),
                'hvac_mode': state.get('state'),
                'hvac_modes': attributes.get('hvac_modes', []),
                'preset_mode': attributes.get('preset_mode'),
                'preset_modes': attributes.get('preset_modes', []),
                'friendly_name': attributes.get('friendly_name', entity_id)
            }
            
            close_operation_context(context, success=True)
            
            return create_success_response(
                f"Retrieved state for {entity_id}",
                climate_state
            )
            
        except Exception as e:
            close_operation_context(context, success=False)
            return handle_operation_error('ha_climate', 'get_state', e, context['correlation_id'])
    
    def list_climate_devices(
        self,
        ha_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """List all climate devices with caching."""
        from .shared_utilities import (
            create_operation_context, close_operation_context,
            handle_operation_error, cache_operation_result
        )
        
        context = create_operation_context('ha_climate', 'list')
        
        try:
            if not is_ha_available():
                close_operation_context(context, success=False)
                return handle_operation_error(
                    'ha_climate', 'list',
                    Exception("Home Assistant circuit breaker open"),
                    context['correlation_id']
                )
            
            config = ha_config or get_ha_config()
            
            def _get_climate_devices():
                response = batch_get_states(None, config, use_cache=True)
                if not response.get('success'):
                    return []
                
                states = response.get('data', [])
                return [
                    {
                        'entity_id': state.get('entity_id'),
                        'name': state.get('attributes', {}).get('friendly_name', state.get('entity_id')),
                        'current_temperature': state.get('attributes', {}).get('current_temperature'),
                        'temperature': state.get('attributes', {}).get('temperature'),
                        'hvac_mode': state.get('state')
                    }
                    for state in states
                    if state.get('entity_id', '').startswith('climate.')
                ]
            
            devices = cache_operation_result(
                operation_name="list_climate_devices",
                func=_get_climate_devices,
                ttl=HA_CACHE_TTL_ENTITIES,
                cache_key_prefix="ha_climate_devices"
            )
            
            close_operation_context(context, success=True)
            
            return create_success_response(
                f"Retrieved {len(devices)} climate devices",
                {
                    'devices': devices,
                    'count': len(devices)
                }
            )
            
        except Exception as e:
            close_operation_context(context, success=False)
            return handle_operation_error('ha_climate', 'list', e, context['correlation_id'])
    
    def get_stats(self) -> Dict[str, Any]:
        """Get climate management statistics."""
        base_stats = super().get_stats()
        base_stats.update(self._stats)
        
        if self._stats['total_operations'] > 0:
            base_stats['success_rate'] = (
                self._stats['successful_operations'] / self._stats['total_operations'] * 100
            )
        
        return base_stats


_singleton_manager = SingletonManager()


def get_climate_manager() -> HAClimateManager:
    """Get or create climate manager singleton."""
    return _singleton_manager.get_or_create(
        'climate_manager',
        HAClimateManager
    )


def set_temperature(
    entity_id: str,
    temperature: float,
    ha_config: Optional[Dict[str, Any]] = None,
    target_temp_high: Optional[float] = None,
    target_temp_low: Optional[float] = None
) -> Dict[str, Any]:
    """Set climate device temperature."""
    manager = get_climate_manager()
    return manager.set_temperature(entity_id, temperature, ha_config, target_temp_high, target_temp_low)


def set_hvac_mode(
    entity_id: str,
    hvac_mode: str,
    ha_config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Set HVAC mode (heat, cool, auto, off, etc.)."""
    manager = get_climate_manager()
    return manager.set_hvac_mode(entity_id, hvac_mode, ha_config)


def set_preset_mode(
    entity_id: str,
    preset_mode: str,
    ha_config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Set climate preset mode (eco, comfort, etc.)."""
    manager = get_climate_manager()
    return manager.set_preset_mode(entity_id, preset_mode, ha_config)


def get_climate_state(
    entity_id: str,
    ha_config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Get current climate device state."""
    manager = get_climate_manager()
    return manager.get_climate_state(entity_id, ha_config)


def list_climate_devices(
    ha_config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """List all climate devices."""
    manager = get_climate_manager()
    return manager.list_climate_devices(ha_config)


def get_climate_stats() -> Dict[str, Any]:
    """Get climate management statistics."""
    manager = get_climate_manager()
    return manager.get_stats()


def cleanup_climate() -> Dict[str, Any]:
    """Cleanup climate manager resources."""
    try:
        _singleton_manager.cleanup('climate_manager')
        return create_success_response("Climate manager cleaned up successfully", {})
    except Exception as e:
        return create_error_response("Cleanup failed", {"error": str(e)})


__all__ = [
    'HAClimateManager',
    'get_climate_manager',
    'set_temperature',
    'set_hvac_mode',
    'set_preset_mode',
    'get_climate_state',
    'list_climate_devices',
    'get_climate_stats',
    'cleanup_climate'
]
