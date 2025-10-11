"""
home_assistant_input_helpers.py
Version: 2025.10.11.01
Description: Home Assistant Input Helpers Management

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
from typing import Dict, Any, Optional, Union

from gateway import (
    log_info,
    create_success_response,
    increment_counter
)

from ha_common import (
    get_ha_config,
    call_ha_service,
    get_entity_state,
    batch_get_states,
    is_ha_available,
    HA_CACHE_TTL_ENTITIES
)


class HAInputHelperManager:
    """Manages Home Assistant input helpers with circuit breaker protection."""
    
    def __init__(self):
        self._stats = {
            'operations': 0,
            'successes': 0,
            'failures': 0,
            'by_type': {
                'input_boolean': {'operations': 0, 'successes': 0},
                'input_select': {'operations': 0, 'successes': 0},
                'input_number': {'operations': 0, 'successes': 0},
                'input_text': {'operations': 0, 'successes': 0}
            }
        }
    
    def get_feature_name(self) -> str:
        return "input_helper"
    
    def set_helper(
        self,
        helper_id: str,
        value: Union[str, int, float, bool],
        ha_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Set input helper value with circuit breaker and operation context."""
        from shared_utilities import (
            create_operation_context, close_operation_context, handle_operation_error
        )
        
        context = create_operation_context('ha_input_helper', 'set',
                                          helper_id=helper_id, value=str(value))
        
        try:
            if not is_ha_available():
                close_operation_context(context, success=False)
                return handle_operation_error(
                    'ha_input_helper', 'set',
                    Exception("Home Assistant circuit breaker open"),
                    context['correlation_id']
                )
            
            config = ha_config or get_ha_config()
            entity_id = self._resolve_helper_id(helper_id, config)
            
            if not entity_id:
                close_operation_context(context, success=False)
                return handle_operation_error(
                    'ha_input_helper', 'set',
                    ValueError(f"Input helper not found: {helper_id}"),
                    context['correlation_id']
                )
            
            domain = entity_id.split('.')[0]
            
            if domain == 'input_boolean':
                result = self._set_boolean_helper(entity_id, value, config)
            elif domain == 'input_select':
                result = self._set_select_helper(entity_id, value, config)
            elif domain == 'input_number':
                result = self._set_number_helper(entity_id, value, config)
            elif domain == 'input_text':
                result = self._set_text_helper(entity_id, value, config)
            else:
                close_operation_context(context, success=False)
                return handle_operation_error(
                    'ha_input_helper', 'set',
                    ValueError(f"Unsupported input helper type: {domain}"),
                    context['correlation_id']
                )
            
            self._stats['operations'] += 1
            if result.get('success'):
                self._stats['successes'] += 1
                self._stats['by_type'][domain]['operations'] += 1
                self._stats['by_type'][domain]['successes'] += 1
            else:
                self._stats['failures'] += 1
            
            close_operation_context(context, success=result.get('success', False), result=result)
            
            increment_counter(f'ha_input_helper_{domain}_set')
            
            return create_success_response(
                f"Input helper {entity_id} set to {value}",
                {
                    'entity_id': entity_id,
                    'domain': domain,
                    'value': value,
                    'result': result
                }
            )
            
        except Exception as e:
            self._stats['failures'] += 1
            close_operation_context(context, success=False)
            return handle_operation_error('ha_input_helper', 'set', e, context['correlation_id'])
    
    def get_helper_value(
        self,
        helper_id: str,
        ha_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Get input helper value with circuit breaker and caching."""
        from shared_utilities import (
            create_operation_context, close_operation_context, handle_operation_error
        )
        
        context = create_operation_context('ha_input_helper', 'get', helper_id=helper_id)
        
        try:
            if not is_ha_available():
                close_operation_context(context, success=False)
                return handle_operation_error(
                    'ha_input_helper', 'get',
                    Exception("Home Assistant circuit breaker open"),
                    context['correlation_id']
                )
            
            config = ha_config or get_ha_config()
            entity_id = self._resolve_helper_id(helper_id, config)
            
            if not entity_id:
                close_operation_context(context, success=False)
                return handle_operation_error(
                    'ha_input_helper', 'get',
                    ValueError(f"Input helper not found: {helper_id}"),
                    context['correlation_id']
                )
            
            state_data = get_entity_state(entity_id, config, use_cache=True)
            
            close_operation_context(context, success=True, result=state_data)
            
            return create_success_response(
                f"Retrieved value for {entity_id}",
                {
                    'entity_id': entity_id,
                    'state': state_data.get('state'),
                    'attributes': state_data.get('attributes', {})
                }
            )
            
        except Exception as e:
            close_operation_context(context, success=False)
            return handle_operation_error('ha_input_helper', 'get', e, context['correlation_id'])
    
    def list_helpers(
        self,
        helper_type: Optional[str] = None,
        ha_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """List input helpers with caching and circuit breaker."""
        from shared_utilities import (
            create_operation_context, close_operation_context,
            handle_operation_error, cache_operation_result
        )
        
        context = create_operation_context('ha_input_helper', 'list', helper_type=helper_type)
        
        try:
            if not is_ha_available():
                close_operation_context(context, success=False)
                return handle_operation_error(
                    'ha_input_helper', 'list',
                    Exception("Home Assistant circuit breaker open"),
                    context['correlation_id']
                )
            
            config = ha_config or get_ha_config()
            
            domains = ['input_boolean', 'input_select', 'input_number', 'input_text']
            if helper_type:
                if helper_type not in domains:
                    close_operation_context(context, success=False)
                    return handle_operation_error(
                        'ha_input_helper', 'list',
                        ValueError(f"Invalid helper type: {helper_type}"),
                        context['correlation_id']
                    )
                domains = [helper_type]
            
            def _get_helpers():
                response = batch_get_states(None, config, use_cache=True)
                if not response.get('success'):
                    return {}
                
                states = response.get('data', [])
                all_helpers = {}
                
                for domain in domains:
                    all_helpers[domain] = [
                        {
                            'entity_id': state.get('entity_id'),
                            'name': state.get('attributes', {}).get('friendly_name', state.get('entity_id')),
                            'state': state.get('state')
                        }
                        for state in states
                        if state.get('entity_id', '').startswith(f"{domain}.")
                    ]
                
                return all_helpers
            
            helpers = cache_operation_result(
                operation_name=f"list_helpers_{helper_type or 'all'}",
                func=_get_helpers,
                ttl=HA_CACHE_TTL_ENTITIES,
                cache_key_prefix=f"ha_input_helpers_{helper_type or 'all'}"
            )
            
            total_count = sum(len(h) for h in helpers.values())
            
            close_operation_context(context, success=True)
            
            return create_success_response(
                f"Retrieved {total_count} input helpers",
                {
                    'helpers': helpers,
                    'domains': domains,
                    'total_count': total_count
                }
            )
            
        except Exception as e:
            close_operation_context(context, success=False)
            return handle_operation_error('ha_input_helper', 'list', e, context['correlation_id'])
    
    def _set_boolean_helper(self, entity_id: str, value: Union[str, bool], config: Dict[str, Any]) -> Dict[str, Any]:
        """Set input_boolean value."""
        if isinstance(value, bool):
            service = "turn_on" if value else "turn_off"
        elif isinstance(value, str):
            value_lower = value.lower()
            if value_lower in ["true", "on", "yes", "1"]:
                service = "turn_on"
            elif value_lower in ["false", "off", "no", "0"]:
                service = "turn_off"
            else:
                raise ValueError(f"Invalid boolean value: {value}")
        else:
            raise ValueError(f"Invalid boolean value type: {type(value)}")
        
        return call_ha_service("input_boolean", service, config, entity_id)
    
    def _set_select_helper(self, entity_id: str, value: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Set input_select option."""
        service_data = {"entity_id": entity_id, "option": str(value)}
        return call_ha_service("input_select", "select_option", config, entity_id, service_data)
    
    def _set_number_helper(self, entity_id: str, value: Union[str, int, float], config: Dict[str, Any]) -> Dict[str, Any]:
        """Set input_number value."""
        try:
            numeric_value = float(value)
        except (ValueError, TypeError):
            raise ValueError(f"Invalid numeric value: {value}")
        
        service_data = {"entity_id": entity_id, "value": numeric_value}
        return call_ha_service("input_number", "set_value", config, entity_id, service_data)
    
    def _set_text_helper(self, entity_id: str, value: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Set input_text value."""
        service_data = {"entity_id": entity_id, "value": str(value)}
        return call_ha_service("input_text", "set_value", config, entity_id, service_data)
    
    def _resolve_helper_id(self, helper_id: str, config: Dict[str, Any]) -> Optional[str]:
        """Resolve helper ID to entity ID."""
        if '.' in helper_id and helper_id.startswith(('input_boolean.', 'input_select.', 'input_number.', 'input_text.')):
            return helper_id
        
        response = batch_get_states(None, config, use_cache=True)
        if not response.get('success'):
            return None
        
        states = response.get('data', [])
        helper_id_lower = helper_id.lower()
        
        for state in states:
            entity_id = state.get('entity_id', '')
            if not entity_id.startswith(('input_boolean.', 'input_select.', 'input_number.', 'input_text.')):
                continue
            
            friendly_name = state.get('attributes', {}).get('friendly_name', '').lower()
            
            if entity_id.lower() == helper_id_lower or friendly_name == helper_id_lower:
                return entity_id
        
        return None
    
    def get_stats(self) -> Dict[str, Any]:
        """Get input helper manager statistics."""
        return {
            "feature": self.get_feature_name(),
            **self._stats,
            "success_rate": (self._stats['successes'] / self._stats['operations'] * 100)
                           if self._stats['operations'] > 0 else 0.0
        }


_input_helper_manager = HAInputHelperManager()


def set_input_helper(helper_id: str, value: Union[str, int, float, bool],
                    ha_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Set input helper value via manager."""
    return _input_helper_manager.set_helper(helper_id, value, ha_config)


def get_input_helper_value(helper_id: str, ha_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Get input helper value via manager."""
    return _input_helper_manager.get_helper_value(helper_id, ha_config)


def list_input_helpers(helper_type: Optional[str] = None,
                      ha_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """List input helpers via manager."""
    return _input_helper_manager.list_helpers(helper_type, ha_config)


def get_input_helper_stats() -> Dict[str, Any]:
    """Get input helper manager statistics."""
    return _input_helper_manager.get_stats()


__all__ = [
    'HAInputHelperManager',
    'set_input_helper',
    'get_input_helper_value',
    'list_input_helpers',
    'get_input_helper_stats',
]

# EOF
