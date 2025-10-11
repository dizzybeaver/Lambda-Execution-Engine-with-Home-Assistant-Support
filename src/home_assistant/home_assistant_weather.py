"""
home_assistant_weather.py
Version: 2025.10.11.01
Description: Home Assistant Weather entity Data Management

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


class HAWeatherManager(HABaseManager):
    """Manages Home Assistant weather data with gateway pattern compliance."""
    
    def __init__(self):
        super().__init__()
        self._stats = {
            'total_queries': 0,
            'successful_queries': 0,
            'failed_queries': 0,
            'cache_hits': 0
        }
    
    def get_feature_name(self) -> str:
        return "weather"
    
    def get_weather(
        self,
        entity_id: str,
        ha_config: Optional[Dict[str, Any]] = None,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """Get weather data with circuit breaker and caching."""
        from shared_utilities import (
            create_operation_context, close_operation_context, handle_operation_error
        )
        
        context = create_operation_context('ha_weather', 'get',
                                          entity_id=entity_id, use_cache=use_cache)
        
        try:
            if not is_ha_available():
                close_operation_context(context, success=False)
                return handle_operation_error(
                    'ha_weather', 'get',
                    Exception("Home Assistant circuit breaker open"),
                    context['correlation_id']
                )
            
            config = ha_config or get_ha_config()
            
            state = get_entity_state(entity_id, config, use_cache=use_cache)
            
            if not state:
                close_operation_context(context, success=False)
                return create_error_response(
                    f"Weather entity {entity_id} not found",
                    {'entity_id': entity_id}
                )
            
            attributes = state.get('attributes', {})
            
            weather_data = {
                'entity_id': entity_id,
                'condition': state.get('state'),
                'temperature': attributes.get('temperature'),
                'temperature_unit': attributes.get('temperature_unit'),
                'humidity': attributes.get('humidity'),
                'pressure': attributes.get('pressure'),
                'pressure_unit': attributes.get('pressure_unit'),
                'wind_speed': attributes.get('wind_speed'),
                'wind_speed_unit': attributes.get('wind_speed_unit'),
                'wind_bearing': attributes.get('wind_bearing'),
                'visibility': attributes.get('visibility'),
                'visibility_unit': attributes.get('visibility_unit'),
                'forecast': attributes.get('forecast', []),
                'friendly_name': attributes.get('friendly_name', entity_id)
            }
            
            self._stats['total_queries'] += 1
            self._stats['successful_queries'] += 1
            
            close_operation_context(context, success=True)
            
            increment_counter('ha_weather_get')
            
            return create_success_response(
                f"Retrieved weather data for {entity_id}",
                weather_data
            )
            
        except Exception as e:
            self._stats['failed_queries'] += 1
            close_operation_context(context, success=False)
            return handle_operation_error('ha_weather', 'get', e, context['correlation_id'])
    
    def get_forecast(
        self,
        entity_id: str,
        ha_config: Optional[Dict[str, Any]] = None,
        days: int = 5
    ) -> Dict[str, Any]:
        """Get weather forecast with circuit breaker."""
        from shared_utilities import (
            create_operation_context, close_operation_context, handle_operation_error
        )
        
        context = create_operation_context('ha_weather', 'forecast',
                                          entity_id=entity_id, days=days)
        
        try:
            if not is_ha_available():
                close_operation_context(context, success=False)
                return handle_operation_error(
                    'ha_weather', 'forecast',
                    Exception("Home Assistant circuit breaker open"),
                    context['correlation_id']
                )
            
            weather_result = self.get_weather(entity_id, ha_config, use_cache=True)
            
            if not weather_result.get('success'):
                close_operation_context(context, success=False)
                return weather_result
            
            weather_data = weather_result.get('data', {})
            forecast = weather_data.get('forecast', [])
            
            limited_forecast = forecast[:days] if days > 0 else forecast
            
            close_operation_context(context, success=True)
            
            return create_success_response(
                f"Retrieved {len(limited_forecast)}-day forecast for {entity_id}",
                {
                    'entity_id': entity_id,
                    'forecast': limited_forecast,
                    'days': len(limited_forecast)
                }
            )
            
        except Exception as e:
            close_operation_context(context, success=False)
            return handle_operation_error('ha_weather', 'forecast', e, context['correlation_id'])
    
    def get_current_conditions(
        self,
        entity_id: str,
        ha_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Get current weather conditions only (no forecast)."""
        from shared_utilities import (
            create_operation_context, close_operation_context, handle_operation_error
        )
        
        context = create_operation_context('ha_weather', 'current', entity_id=entity_id)
        
        try:
            weather_result = self.get_weather(entity_id, ha_config, use_cache=True)
            
            if not weather_result.get('success'):
                close_operation_context(context, success=False)
                return weather_result
            
            weather_data = weather_result.get('data', {})
            
            current_conditions = {
                'entity_id': entity_id,
                'condition': weather_data.get('condition'),
                'temperature': weather_data.get('temperature'),
                'temperature_unit': weather_data.get('temperature_unit'),
                'humidity': weather_data.get('humidity'),
                'pressure': weather_data.get('pressure'),
                'wind_speed': weather_data.get('wind_speed'),
                'friendly_name': weather_data.get('friendly_name')
            }
            
            close_operation_context(context, success=True)
            
            return create_success_response(
                f"Retrieved current conditions for {entity_id}",
                current_conditions
            )
            
        except Exception as e:
            close_operation_context(context, success=False)
            return handle_operation_error('ha_weather', 'current', e, context['correlation_id'])
    
    def list_weather_entities(
        self,
        ha_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """List all weather entities with caching."""
        from shared_utilities import (
            create_operation_context, close_operation_context,
            handle_operation_error, cache_operation_result
        )
        
        context = create_operation_context('ha_weather', 'list')
        
        try:
            if not is_ha_available():
                close_operation_context(context, success=False)
                return handle_operation_error(
                    'ha_weather', 'list',
                    Exception("Home Assistant circuit breaker open"),
                    context['correlation_id']
                )
            
            config = ha_config or get_ha_config()
            
            def _get_weather_entities():
                response = batch_get_states(None, config, use_cache=True)
                if not response.get('success'):
                    return []
                
                states = response.get('data', [])
                return [
                    {
                        'entity_id': state.get('entity_id'),
                        'name': state.get('attributes', {}).get('friendly_name', state.get('entity_id')),
                        'condition': state.get('state'),
                        'temperature': state.get('attributes', {}).get('temperature')
                    }
                    for state in states
                    if state.get('entity_id', '').startswith('weather.')
                ]
            
            entities = cache_operation_result(
                operation_name="list_weather_entities",
                func=_get_weather_entities,
                ttl=HA_CACHE_TTL_ENTITIES,
                cache_key_prefix="ha_weather_entities"
            )
            
            close_operation_context(context, success=True)
            
            return create_success_response(
                f"Retrieved {len(entities)} weather entities",
                {
                    'entities': entities,
                    'count': len(entities)
                }
            )
            
        except Exception as e:
            close_operation_context(context, success=False)
            return handle_operation_error('ha_weather', 'list', e, context['correlation_id'])
    
    def get_stats(self) -> Dict[str, Any]:
        """Get weather query statistics."""
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


def get_weather_manager() -> HAWeatherManager:
    """Get or create weather manager singleton."""
    return _singleton_manager.get_or_create(
        'weather_manager',
        HAWeatherManager
    )


def get_weather(
    entity_id: str,
    ha_config: Optional[Dict[str, Any]] = None,
    use_cache: bool = True
) -> Dict[str, Any]:
    """Get complete weather data including forecast."""
    manager = get_weather_manager()
    return manager.get_weather(entity_id, ha_config, use_cache)


def get_forecast(
    entity_id: str,
    ha_config: Optional[Dict[str, Any]] = None,
    days: int = 5
) -> Dict[str, Any]:
    """Get weather forecast for specified days."""
    manager = get_weather_manager()
    return manager.get_forecast(entity_id, ha_config, days)


def get_current_conditions(
    entity_id: str,
    ha_config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Get current weather conditions only."""
    manager = get_weather_manager()
    return manager.get_current_conditions(entity_id, ha_config)


def list_weather_entities(
    ha_config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """List all weather entities."""
    manager = get_weather_manager()
    return manager.list_weather_entities(ha_config)


def get_weather_stats() -> Dict[str, Any]:
    """Get weather query statistics."""
    manager = get_weather_manager()
    return manager.get_stats()


def cleanup_weather() -> Dict[str, Any]:
    """Cleanup weather manager resources."""
    try:
        _singleton_manager.cleanup('weather_manager')
        return create_success_response("Weather manager cleaned up successfully", {})
    except Exception as e:
        return create_error_response("Cleanup failed", {"error": str(e)})


__all__ = [
    'HAWeatherManager',
    'get_weather_manager',
    'get_weather',
    'get_forecast',
    'get_current_conditions',
    'list_weather_entities',
    'get_weather_stats',
    'cleanup_weather'
]
