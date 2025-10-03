"""
Home Assistant Scripts - Gateway-Optimized Script Execution
Version: 2025.10.03.02
Description: Revolutionary gateway-integrated script management with zero custom error handling

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
    fuzzy_match_name,
    HA_CACHE_TTL_ENTITIES
)


class HAScriptManager:
    """Manages Home Assistant script execution with circuit breaker protection."""
    
    def __init__(self):
        self._stats = {
            'total_executions': 0,
            'successful_executions': 0,
            'failed_executions': 0
        }
    
    def get_feature_name(self) -> str:
        return "script"
    
    def execute_script(
        self,
        script_id: str,
        ha_config: Optional[Dict[str, Any]] = None,
        variables: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute script with circuit breaker and operation context."""
        from .shared_utilities import (
            create_operation_context, close_operation_context, handle_operation_error
        )
        
        context = create_operation_context('ha_script', 'execute',
                                          script_id=script_id,
                                          has_variables=bool(variables))
        
        try:
            if not is_ha_available():
                close_operation_context(context, success=False)
                return handle_operation_error(
                    'ha_script', 'execute',
                    Exception("Home Assistant circuit breaker open"),
                    context['correlation_id']
                )
            
            config = ha_config or get_ha_config()
            entity_id = self._resolve_script_id(script_id, config)
            
            if not entity_id:
                close_operation_context(context, success=False)
                return handle_operation_error(
                    'ha_script', 'execute',
                    ValueError(f"Script not found: {script_id}"),
                    context['correlation_id']
                )
            
            service_data = {"entity_id": entity_id}
            if variables:
                service_data.update(variables)
            
            result = call_ha_service("script", "turn_on", config, entity_id, service_data)
            
            self._stats['total_executions'] += 1
            if result.get('success'):
                self._stats['successful_executions'] += 1
            else:
                self._stats['failed_executions'] += 1
            
            close_operation_context(context, success=result.get('success', False), result=result)
            
            increment_counter('ha_script_execute')
            
            return create_success_response(
                f"Script {entity_id} executed successfully",
                {
                    'entity_id': entity_id,
                    'variables': variables,
                    'result': result
                }
            )
            
        except Exception as e:
            self._stats['failed_executions'] += 1
            close_operation_context(context, success=False)
            return handle_operation_error('ha_script', 'execute', e, context['correlation_id'])
    
    def list_scripts(
        self,
        ha_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """List all scripts with caching and circuit breaker."""
        from .shared_utilities import (
            create_operation_context, close_operation_context,
            handle_operation_error, cache_operation_result
        )
        
        context = create_operation_context('ha_script', 'list')
        
        try:
            if not is_ha_available():
                close_operation_context(context, success=False)
                return handle_operation_error(
                    'ha_script', 'list',
                    Exception("Home Assistant circuit breaker open"),
                    context['correlation_id']
                )
            
            config = ha_config or get_ha_config()
            
            def _get_scripts():
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
                    if state.get('entity_id', '').startswith('script.')
                ]
            
            scripts = cache_operation_result(
                operation_name="list_scripts",
                func=_get_scripts,
                ttl=HA_CACHE_TTL_ENTITIES,
                cache_key_prefix="ha_scripts"
            )
            
            close_operation_context(context, success=True)
            
            return create_success_response(
                f"Retrieved {len(scripts)} scripts",
                {
                    'scripts': scripts,
                    'count': len(scripts)
                }
            )
            
        except Exception as e:
            close_operation_context(context, success=False)
            return handle_operation_error('ha_script', 'list', e, context['correlation_id'])
    
    def _resolve_script_id(self, script_id: str, config: Dict[str, Any]) -> Optional[str]:
        """Resolve script ID or name to entity ID."""
        if script_id.startswith('script.'):
            return script_id
        
        scripts_response = self.list_scripts(config)
        if not scripts_response.get('success'):
            return None
        
        scripts = scripts_response.get('data', {}).get('scripts', [])
        
        script_id_lower = script_id.lower()
        for script in scripts:
            entity_id = script.get('entity_id', '')
            name = script.get('name', '').lower()
            
            if entity_id.lower() == script_id_lower or name == script_id_lower:
                return entity_id
        
        names = [script.get('name', '') for script in scripts]
        matched_name = fuzzy_match_name(script_id, names)
        
        if matched_name:
            for script in scripts:
                if script.get('name') == matched_name:
                    return script.get('entity_id')
        
        return None
    
    def get_stats(self) -> Dict[str, Any]:
        """Get script manager statistics."""
        return {
            "feature": self.get_feature_name(),
            **self._stats,
            "success_rate": (self._stats['successful_executions'] / self._stats['total_executions'] * 100)
                           if self._stats['total_executions'] > 0 else 0.0
        }


_script_manager = HAScriptManager()


def execute_script(script_id: str, ha_config: Optional[Dict[str, Any]] = None,
                  variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Execute script via manager."""
    return _script_manager.execute_script(script_id, ha_config, variables)


def list_scripts(ha_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """List scripts via manager."""
    return _script_manager.list_scripts(ha_config)


def get_script_stats() -> Dict[str, Any]:
    """Get script manager statistics."""
    return _script_manager.get_stats()


__all__ = [
    'HAScriptManager',
    'execute_script',
    'list_scripts',
    'get_script_stats',
]

# EOF
