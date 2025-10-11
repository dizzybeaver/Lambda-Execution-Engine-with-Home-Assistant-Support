"""
home_assistant_automation.py
Version: 2025.10.11.01
Description: Home Assistant Automation Management

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
    batch_get_states,
    is_ha_available,
    get_cache_section,
    set_cache_section,
    fuzzy_match_name,
    HA_CACHE_TTL_ENTITIES
)


class HAAutomationManager:
    """Manages Home Assistant automation triggers with circuit breaker protection."""
    
    def __init__(self):
        self._stats = {
            'total_triggers': 0,
            'successful_triggers': 0,
            'failed_triggers': 0
        }
    
    def get_feature_name(self) -> str:
        return "automation"
    
    def trigger_automation(
        self,
        automation_id: str,
        ha_config: Optional[Dict[str, Any]] = None,
        skip_condition: bool = False
    ) -> Dict[str, Any]:
        """Trigger automation with circuit breaker and operation context."""
        from shared_utilities import (
            create_operation_context, close_operation_context, handle_operation_error
        )
        
        context = create_operation_context('ha_automation', 'trigger',
                                          automation_id=automation_id,
                                          skip_condition=skip_condition)
        
        try:
            if not is_ha_available():
                close_operation_context(context, success=False)
                return handle_operation_error(
                    'ha_automation', 'trigger',
                    Exception("Home Assistant circuit breaker open"),
                    context['correlation_id']
                )
            
            config = ha_config or get_ha_config()
            entity_id = self._resolve_automation_id(automation_id, config)
            
            if not entity_id:
                close_operation_context(context, success=False)
                return handle_operation_error(
                    'ha_automation', 'trigger',
                    ValueError(f"Automation not found: {automation_id}"),
                    context['correlation_id']
                )
            
            service_data = {
                "entity_id": entity_id,
                "skip_condition": skip_condition
            }
            
            result = call_ha_service("automation", "trigger", config, entity_id, service_data)
            
            self._stats['total_triggers'] += 1
            if result.get('success'):
                self._stats['successful_triggers'] += 1
            else:
                self._stats['failed_triggers'] += 1
            
            close_operation_context(context, success=result.get('success', False), result=result)
            
            increment_counter('ha_automation_trigger')
            
            return create_success_response(
                f"Automation {entity_id} triggered successfully",
                {
                    'entity_id': entity_id,
                    'skip_condition': skip_condition,
                    'result': result
                }
            )
            
        except Exception as e:
            self._stats['failed_triggers'] += 1
            close_operation_context(context, success=False)
            return handle_operation_error('ha_automation', 'trigger', e, context['correlation_id'])
    
    def list_automations(
        self,
        ha_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """List all automations with caching and circuit breaker."""
        from shared_utilities import (
            create_operation_context, close_operation_context,
            handle_operation_error, cache_operation_result
        )
        
        context = create_operation_context('ha_automation', 'list')
        
        try:
            if not is_ha_available():
                close_operation_context(context, success=False)
                return handle_operation_error(
                    'ha_automation', 'list',
                    Exception("Home Assistant circuit breaker open"),
                    context['correlation_id']
                )
            
            config = ha_config or get_ha_config()
            
            def _get_automations():
                response = batch_get_states(None, config, use_cache=True)
                if not response.get('success'):
                    return []
                
                states = response.get('data', [])
                return [
                    {
                        'entity_id': state.get('entity_id'),
                        'name': state.get('attributes', {}).get('friendly_name', state.get('entity_id')),
                        'state': state.get('state'),
                        'last_triggered': state.get('attributes', {}).get('last_triggered')
                    }
                    for state in states
                    if state.get('entity_id', '').startswith('automation.')
                ]
            
            automations = cache_operation_result(
                operation_name="list_automations",
                func=_get_automations,
                ttl=HA_CACHE_TTL_ENTITIES,
                cache_key_prefix="ha_automations"
            )
            
            close_operation_context(context, success=True)
            
            return create_success_response(
                f"Retrieved {len(automations)} automations",
                {
                    'automations': automations,
                    'count': len(automations)
                }
            )
            
        except Exception as e:
            close_operation_context(context, success=False)
            return handle_operation_error('ha_automation', 'list', e, context['correlation_id'])
    
    def _resolve_automation_id(self, automation_id: str, config: Dict[str, Any]) -> Optional[str]:
        """Resolve automation ID or name to entity ID."""
        if automation_id.startswith('automation.'):
            return automation_id
        
        automations_response = self.list_automations(config)
        if not automations_response.get('success'):
            return None
        
        automations = automations_response.get('data', {}).get('automations', [])
        
        automation_id_lower = automation_id.lower()
        for auto in automations:
            entity_id = auto.get('entity_id', '')
            name = auto.get('name', '').lower()
            
            if entity_id.lower() == automation_id_lower or name == automation_id_lower:
                return entity_id
        
        names = [auto.get('name', '') for auto in automations]
        matched_name = fuzzy_match_name(automation_id, names)
        
        if matched_name:
            for auto in automations:
                if auto.get('name') == matched_name:
                    return auto.get('entity_id')
        
        return None
    
    def get_stats(self) -> Dict[str, Any]:
        """Get automation manager statistics."""
        return {
            "feature": self.get_feature_name(),
            **self._stats,
            "success_rate": (self._stats['successful_triggers'] / self._stats['total_triggers'] * 100)
                           if self._stats['total_triggers'] > 0 else 0.0
        }


_automation_manager = HAAutomationManager()


def trigger_automation(automation_id: str, ha_config: Optional[Dict[str, Any]] = None, 
                      skip_condition: bool = False) -> Dict[str, Any]:
    """Trigger automation via manager."""
    return _automation_manager.trigger_automation(automation_id, ha_config, skip_condition)


def list_automations(ha_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """List automations via manager."""
    return _automation_manager.list_automations(ha_config)


def get_automation_stats() -> Dict[str, Any]:
    """Get automation manager statistics."""
    return _automation_manager.get_stats()


__all__ = [
    'HAAutomationManager',
    'trigger_automation',
    'list_automations',
    'get_automation_stats',
]

# EOF
