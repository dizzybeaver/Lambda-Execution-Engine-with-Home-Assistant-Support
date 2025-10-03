"""
Home Assistant Sensors - Gateway-Optimized Sensor Data Management
Version: 2025.10.03.02
Description: Sensor and binary sensor data retrieval with full gateway integration

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
    HABaseManager, get_entity_state, batch_get_states, SingletonManager,
    is_ha_available, get_ha_config, HA_CACHE_TTL_STATE, HA_CACHE_TTL_ENTITIES
)


class HASensorsManager(HABaseManager):
    """Manages Home Assistant sensors with gateway pattern compliance."""
    
    def __init__(self):
        super().__init__()
        self._stats = {
            'total_queries': 0,
            'successful_queries': 0,
            'failed_queries': 0,
            'cache_hits': 0
        }
    
    def get_feature_name(self) -> str:
        return "sensor"
    
    def get_sensor_value(
        self,
        entity_id: str,
        ha_config: Optional[Dict[str, Any]] = None,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """Get sensor value with circuit breaker and caching."""
        from .shared_utilities import (
            create_operation_context, close_operation_context, handle_operation_error
        )
        
        context = create_operation_context('ha_sensor', 'get_value',
                                          entity_id=entity_id, use_cache=use_cache)
        
        try:
            if not is_ha_available():
                close_operation_context(context, success=False)
                return handle_operation_error(
                    'ha_sensor', 'get_value',
                    Exception("Home Assistant circuit breaker open"),
                    context['correlation_id']
                )
            
            config = ha_config or get_ha_config()
            
            state = get_entity_state(entity_id, config, use_cache=use_cache)
            
            if not state:
                close_operation_context(context, success=False)
                return create_error_response(
                    f"Sensor {entity_id} not found",
                    {'entity_id': entity_id}
                )
            
            attributes = state.get('attributes', {})
            
            sensor_data = {
                'entity_id': entity_id,
                'state': state.get('state'),
                'unit_of_measurement': attributes.get('unit_of_measurement'),
                'device_class': attributes.get('device_class'),
                'friendly_name': attributes.get('friendly_name', entity_id),
                'last_changed': state.get('last_changed'),
                'last_updated': state.get('last_updated')
            }
            
            self._stats['total_queries'] += 1
            self._stats['successful_queries'] += 1
            
            close_operation_context(context, success=True)
            
            increment_counter('ha_sensor_get_value')
            
            return create_success_response(
                f"Retrieved sensor value for {entity_id}",
                sensor_data
            )
            
        except Exception as e:
            self._stats['failed_queries'] += 1
            close_operation_context(context, success=False)
            return handle_operation_error('ha_sensor', 'get_value', e, context['correlation_id'])
    
    def get_binary_sensor_state(
        self,
        entity_id: str,
        ha_config: Optional[Dict[str, Any]] = None,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """Get binary sensor state with circuit breaker and caching."""
        from .shared_utilities import (
            create_operation_context, close_operation_context, handle_operation_error
        )
        
        context = create_operation_context('ha_sensor', 'get_binary_state',
                                          entity_id=entity_id, use_cache=use_cache)
        
        try:
            if not is_ha_available():
                close_operation_context(context, success=False)
                return handle_operation_error(
                    'ha_sensor', 'get_binary_state',
                    Exception("Home Assistant circuit breaker open"),
                    context['correlation_id']
                )
            
            config = ha_config or get_ha_config()
            
            state = get_entity_state(entity_id, config, use_cache=use_cache)
            
            if not state:
                close_operation_context(context, success=False)
                return create_error_response(
                    f"Binary sensor {entity_id} not found",
                    {'entity_id': entity_id}
                )
            
            attributes = state.get('attributes', {})
            current_state = state.get('state', '').lower()
            
            binary_data = {
                'entity_id': entity_id,
                'state': current_state,
                'is_on': current_state == 'on',
                'device_class': attributes.get('device_class'),
                'friendly_name': attributes.get('friendly_name', entity_id),
                'last_changed': state.get('last_changed')
            }
            
            self._stats['total_queries'] += 1
            self._stats['successful_queries'] += 1
            
            close_operation_context(context, success=True)
            
            increment_counter('ha_binary_sensor_get_state')
            
            return create_success_response(
                f"Retrieved binary sensor state for {entity_id}",
                binary_data
            )
            
        except Exception as e:
            self._stats['failed_queries'] += 1
            close_operation_context(context, success=False)
            return handle_operation_error('ha_sensor', 'get_binary_state', e, context['correlation_id'])
    
    def list_sensors(
        self,
        domain: str = 'sensor',
        ha_config: Optional[Dict[str, Any]] = None,
        device_class: Optional[str] = None
    ) -> Dict[str, Any]:
        """List all sensors with optional filtering."""
        from .shared_utilities import (
            create_operation_context, close_operation_context,
            handle_operation_error, cache_operation_result
        )
        
        context = create_operation_context('ha_sensor', 'list',
                                          domain=domain, device_class=device_class)
        
        try:
            if not is_ha_available():
                close_operation_context(context, success=False)
                return handle_operation_error(
                    'ha_sensor', 'list',
                    Exception("Home Assistant circuit breaker open"),
                    context['correlation_id']
                )
            
            config = ha_config or get_ha_config()
            
            cache_suffix = f"_{device_class}" if device_class else ""
            
            def _get_sensors():
                response = batch_get_states(None, config, use_cache=True)
                if not response.get('success'):
                    return []
                
                states = response.get('data', [])
                sensors = []
                
                for state in states:
                    entity_id = state.get('entity_id', '')
                    if not entity_id.startswith(f"{domain}."):
                        continue
                    
                    attributes = state.get('attributes', {})
                    if device_class and attributes.get('device_class') != device_class:
                        continue
                    
                    sensors.append({
                        'entity_id': entity_id,
                        'name': attributes.get('friendly_name', entity_id),
                        'state': state.get('state'),
                        'unit_of_measurement': attributes.get('unit_of_measurement'),
                        'device_class': attributes.get('device_class')
                    })
                
                return sensors
            
            sensors = cache_operation_result(
                operation_name=f"list_sensors_{domain}{cache_suffix}",
                func=_get_sensors,
                ttl=HA_CACHE_TTL_ENTITIES,
                cache_key_prefix=f"ha_sensors_{domain}{cache_suffix}"
            )
            
            close_operation_context(context, success=True)
            
            return create_success_response(
                f"Retrieved {len(sensors)} {domain} sensors",
                {
                    'sensors': sensors,
                    'count': len(sensors),
                    'domain': domain,
                    'device_class': device_class
                }
            )
            
        except Exception as e:
            close_operation_context(context, success=False)
            return handle_operation_error('ha_sensor', 'list', e, context['correlation_id'])
    
    def get_sensors_by_class(
        self,
        device_class: str,
        ha_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Get all sensors of a specific device class."""
        return self.list_sensors('sensor', ha_config, device_class)
    
    def get_multiple_sensors(
        self,
        entity_ids: List[str],
        ha_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Get values for multiple sensors in one call."""
        from .shared_utilities import (
            create_operation_context, close_operation_context, handle_operation_error
        )
        
        context = create_operation_context('ha_sensor', 'get_multiple',
                                          count=len(entity_ids))
        
        try:
            if not is_ha_available():
                close_operation_context(context, success=False)
                return handle_operation_error(
                    'ha_sensor', 'get_multiple',
                    Exception("Home Assistant circuit breaker open"),
                    context['correlation_id']
                )
            
            config = ha_config or get_ha_config()
            
            response = batch_get_states(entity_ids, config, use_cache=True)
            
            if not response.get('success'):
                close_operation_context(context, success=False)
                return response
            
            states = response.get('data', [])
            sensors = {}
            
            for state in states:
                entity_id = state.get('entity_id')
                attributes = state.get('attributes', {})
                
                sensors[entity_id] = {
                    'state': state.get('state'),
                    'unit_of_measurement': attributes.get('unit_of_measurement'),
                    'friendly_name': attributes.get('friendly_name', entity_id),
                    'device_class': attributes.get('device_class')
                }
            
            close_operation_context(context, success=True)
            
            return create_success_response(
                f"Retrieved {len(sensors)} sensor values",
                {
                    'sensors': sensors,
                    'count': len(sensors)
                }
            )
            
        except Exception as e:
            close_operation_context(context, success=False)
            return handle_operation_error('ha_sensor', 'get_multiple', e, context['correlation_id'])
    
    def get_stats(self) -> Dict[str, Any]:
        """Get sensor query statistics."""
        base_stats = super().get_stats()
        base_stats.update(self._stats)
        
        if self._stats['total_queries'] > 0:
            base_stats['success_rate'] = (
                self._stats['successful_queries'] / self._stats['total_queries'] * 100
            )
            base_stats['cache_hit_rate'] = (
                self._stats['cache_hits'] / self._stats['total_queries'] * 100
            )
        
        return base_stats


_singleton_manager = SingletonManager()


def get_sensors_manager() -> HASensorsManager:
    """Get or create sensors manager singleton."""
    return _singleton_manager.get_or_create(
        'sensors_manager',
        HASensorsManager
    )


def get_sensor_value(
    entity_id: str,
    ha_config: Optional[Dict[str, Any]] = None,
    use_cache: bool = True
) -> Dict[str, Any]:
    """Get sensor value."""
    manager = get_sensors_manager()
    return manager.get_sensor_value(entity_id, ha_config, use_cache)


def get_binary_sensor_state(
    entity_id: str,
    ha_config: Optional[Dict[str, Any]] = None,
    use_cache: bool = True
) -> Dict[str, Any]:
    """Get binary sensor state."""
    manager = get_sensors_manager()
    return manager.get_binary_sensor_state(entity_id, ha_config, use_cache)


def list_sensors(
    domain: str = 'sensor',
    ha_config: Optional[Dict[str, Any]] = None,
    device_class: Optional[str] = None
) -> Dict[str, Any]:
    """List sensors with optional filtering."""
    manager = get_sensors_manager()
    return manager.list_sensors(domain, ha_config, device_class)


def get_sensors_by_class(
    device_class: str,
    ha_config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Get sensors by device class (temperature, humidity, etc.)."""
    manager = get_sensors_manager()
    return manager.get_sensors_by_class(device_class, ha_config)


def get_multiple_sensors(
    entity_ids: List[str],
    ha_config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Get multiple sensor values in one call."""
    manager = get_sensors_manager()
    return manager.get_multiple_sensors(entity_ids, ha_config)


def get_sensor_stats() -> Dict[str, Any]:
    """Get sensor query statistics."""
    manager = get_sensors_manager()
    return manager.get_stats()


def cleanup_sensors() -> Dict[str, Any]:
    """Cleanup sensors manager resources."""
    try:
        _singleton_manager.cleanup('sensors_manager')
        return create_success_response("Sensors manager cleaned up successfully", {})
    except Exception as e:
        return create_error_response("Cleanup failed", {"error": str(e)})


__all__ = [
    'HASensorsManager',
    'get_sensors_manager',
    'get_sensor_value',
    'get_binary_sensor_state',
    'list_sensors',
    'get_sensors_by_class',
    'get_multiple_sensors',
    'get_sensor_stats',
    'cleanup_sensors'
]
