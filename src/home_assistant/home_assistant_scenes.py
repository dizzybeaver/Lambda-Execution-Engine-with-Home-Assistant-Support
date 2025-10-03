"""
Home Assistant Scenes - Gateway-Optimized Scene Management
Version: 2025.10.03.02
Description: Scene activation and management with full gateway integration

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
from difflib import SequenceMatcher

from gateway import (
    log_info, create_success_response, create_error_response, increment_counter
)

from ha_common import (
    HABaseManager, call_ha_service, batch_get_states, SingletonManager,
    is_ha_available, get_ha_config, fuzzy_match_name, HA_CACHE_TTL_ENTITIES
)


class HAScenesManager(HABaseManager):
    """Manages Home Assistant scenes with gateway pattern compliance."""
    
    def __init__(self):
        super().__init__()
        self._stats = {
            'total_activations': 0,
            'successful_activations': 0,
            'failed_activations': 0
        }
    
    def get_feature_name(self) -> str:
        return "scene"
    
    def activate_scene(
        self,
        scene_id: str,
        ha_config: Optional[Dict[str, Any]] = None,
        transition: Optional[int] = None
    ) -> Dict[str, Any]:
        """Activate scene with circuit breaker and operation context."""
        from .shared_utilities import (
            create_operation_context, close_operation_context, handle_operation_error
        )
        
        context = create_operation_context('ha_scene', 'activate',
                                          scene_id=scene_id,
                                          has_transition=bool(transition))
        
        try:
            if not is_ha_available():
                close_operation_context(context, success=False)
                return handle_operation_error(
                    'ha_scene', 'activate',
                    Exception("Home Assistant circuit breaker open"),
                    context['correlation_id']
                )
            
            config = ha_config or get_ha_config()
            entity_id = self._resolve_scene_id(scene_id, config)
            
            if not entity_id:
                close_operation_context(context, success=False)
                return handle_operation_error(
                    'ha_scene', 'activate',
                    ValueError(f"Scene not found: {scene_id}"),
                    context['correlation_id']
                )
            
            service_data = {"entity_id": entity_id}
            if transition is not None:
                service_data["transition"] = transition
            
            result = call_ha_service("scene", "turn_on", config, entity_id, service_data)
            
            self._stats['total_activations'] += 1
            if result.get('success'):
                self._stats['successful_activations'] += 1
            else:
                self._stats['failed_activations'] += 1
            
            close_operation_context(context, success=result.get('success', False), result=result)
            
            increment_counter('ha_scene_activate')
            
            return create_success_response(
                f"Scene {entity_id} activated successfully",
                {
                    'entity_id': entity_id,
                    'transition': transition,
                    'result': result
                }
            )
            
        except Exception as e:
            self._stats['failed_activations'] += 1
            close_operation_context(context, success=False)
            return handle_operation_error('ha_scene', 'activate', e, context['correlation_id'])
    
    def list_scenes(
        self,
        ha_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """List all scenes with caching and circuit breaker."""
        from .shared_utilities import (
            create_operation_context, close_operation_context,
            handle_operation_error, cache_operation_result
        )
        
        context = create_operation_context('ha_scene', 'list')
        
        try:
            if not is_ha_available():
                close_operation_context(context, success=False)
                return handle_operation_error(
                    'ha_scene', 'list',
                    Exception("Home Assistant circuit breaker open"),
                    context['correlation_id']
                )
            
            config = ha_config or get_ha_config()
            
            def _get_scenes():
                response = batch_get_states(None, config, use_cache=True)
                if not response.get('success'):
                    return []
                
                states = response.get('data', [])
                return [
                    {
                        'entity_id': state.get('entity_id'),
                        'name': state.get('attributes', {}).get('friendly_name', state.get('entity_id')),
                        'icon': state.get('attributes', {}).get('icon')
                    }
                    for state in states
                    if state.get('entity_id', '').startswith('scene.')
                ]
            
            scenes = cache_operation_result(
                operation_name="list_scenes",
                func=_get_scenes,
                ttl=HA_CACHE_TTL_ENTITIES,
                cache_key_prefix="ha_scenes"
            )
            
            close_operation_context(context, success=True)
            
            return create_success_response(
                f"Retrieved {len(scenes)} scenes",
                {
                    'scenes': scenes,
                    'count': len(scenes)
                }
            )
            
        except Exception as e:
            close_operation_context(context, success=False)
            return handle_operation_error('ha_scene', 'list', e, context['correlation_id'])
    
    def _resolve_scene_id(self, scene_id: str, config: Dict[str, Any]) -> Optional[str]:
        """Resolve scene ID or name to entity ID."""
        if scene_id.startswith('scene.'):
            return scene_id
        
        scenes_response = self.list_scenes(config)
        if not scenes_response.get('success'):
            return None
        
        scenes = scenes_response.get('data', {}).get('scenes', [])
        scene_names = {s['name'].lower(): s['entity_id'] for s in scenes}
        
        scene_id_lower = scene_id.lower()
        if scene_id_lower in scene_names:
            return scene_names[scene_id_lower]
        
        fuzzy_name = fuzzy_match_name(scene_id, list(scene_names.keys()))
        if fuzzy_name:
            return scene_names[fuzzy_name]
        
        return None
    
    def get_stats(self) -> Dict[str, Any]:
        """Get scene management statistics."""
        base_stats = super().get_stats()
        base_stats.update(self._stats)
        
        if self._stats['total_activations'] > 0:
            base_stats['success_rate'] = (
                self._stats['successful_activations'] / self._stats['total_activations'] * 100
            )
        
        return base_stats


_singleton_manager = SingletonManager()


def get_scenes_manager() -> HAScenesManager:
    """Get or create scenes manager singleton."""
    return _singleton_manager.get_or_create(
        'scenes_manager',
        HAScenesManager
    )


def activate_scene(
    scene_id: str,
    ha_config: Optional[Dict[str, Any]] = None,
    transition: Optional[int] = None
) -> Dict[str, Any]:
    """Activate a scene by ID or name."""
    manager = get_scenes_manager()
    return manager.activate_scene(scene_id, ha_config, transition)


def list_scenes(
    ha_config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """List all available scenes."""
    manager = get_scenes_manager()
    return manager.list_scenes(ha_config)


def get_scene_stats() -> Dict[str, Any]:
    """Get scene management statistics."""
    manager = get_scenes_manager()
    return manager.get_stats()


def cleanup_scenes() -> Dict[str, Any]:
    """Cleanup scenes manager resources."""
    try:
        _singleton_manager.cleanup('scenes_manager')
        return create_success_response("Scenes manager cleaned up successfully", {})
    except Exception as e:
        return create_error_response("Cleanup failed", {"error": str(e)})


__all__ = [
    'HAScenesManager',
    'get_scenes_manager',
    'activate_scene',
    'list_scenes',
    'get_scene_stats',
    'cleanup_scenes'
]
