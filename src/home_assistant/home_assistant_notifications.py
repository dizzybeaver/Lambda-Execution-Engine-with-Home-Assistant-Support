"""
Home Assistant Notifications - Gateway-Optimized Notification & TTS Management
Version: 2025.10.03.02
Description: Revolutionary gateway-integrated notification management with zero custom error handling

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
    log_info, log_warning,
    create_success_response,
    increment_counter
)

from ha_common import (
    get_ha_config,
    call_ha_service,
    batch_get_states,
    is_ha_available,
    HA_CACHE_TTL_ENTITIES
)


class HANotificationManager:
    """Manages Home Assistant notifications and TTS with circuit breaker protection."""
    
    def __init__(self):
        self._stats = {
            'operations': 0,
            'successes': 0,
            'failures': 0,
            'by_type': {
                'tts': {'operations': 0, 'successes': 0},
                'persistent': {'operations': 0, 'successes': 0},
                'dismiss': {'operations': 0, 'successes': 0}
            }
        }
    
    def get_feature_name(self) -> str:
        return "notification"
    
    def send_tts_announcement(
        self,
        message: str,
        ha_config: Optional[Dict[str, Any]] = None,
        media_players: Optional[List[str]] = None,
        language: str = "en-US"
    ) -> Dict[str, Any]:
        """Send TTS announcement with circuit breaker and operation context."""
        from .shared_utilities import (
            create_operation_context, close_operation_context, handle_operation_error
        )
        
        context = create_operation_context('ha_notification', 'tts',
                                          message_length=len(message), language=language)
        
        try:
            if not is_ha_available():
                close_operation_context(context, success=False)
                return handle_operation_error(
                    'ha_notification', 'tts',
                    Exception("Home Assistant circuit breaker open"),
                    context['correlation_id']
                )
            
            config = ha_config or get_ha_config()
            
            if media_players:
                target_entities = self._resolve_media_players(media_players, config)
                if not target_entities:
                    close_operation_context(context, success=False)
                    return handle_operation_error(
                        'ha_notification', 'tts',
                        ValueError("No valid media players found"),
                        context['correlation_id']
                    )
            else:
                target_entities = self._get_available_media_players(config)
                if not target_entities:
                    close_operation_context(context, success=False)
                    return handle_operation_error(
                        'ha_notification', 'tts',
                        ValueError("No media players available"),
                        context['correlation_id']
                    )
            
            service_data = {
                "entity_id": target_entities,
                "message": message,
                "language": language
            }
            
            result = call_ha_service("tts", "cloud_say", config, None, service_data)
            
            self._stats['operations'] += 1
            if result.get('success'):
                self._stats['successes'] += 1
                self._stats['by_type']['tts']['operations'] += 1
                self._stats['by_type']['tts']['successes'] += 1
            else:
                self._stats['failures'] += 1
            
            close_operation_context(context, success=result.get('success', False), result=result)
            
            increment_counter(f'ha_tts_announcement')
            
            return create_success_response(
                f"TTS announcement sent to {len(target_entities)} media players",
                {
                    'message': message,
                    'target_entities': target_entities,
                    'language': language,
                    'result': result
                }
            )
            
        except Exception as e:
            self._stats['failures'] += 1
            close_operation_context(context, success=False)
            return handle_operation_error('ha_notification', 'tts', e, context['correlation_id'])
    
    def send_persistent_notification(
        self,
        message: str,
        ha_config: Optional[Dict[str, Any]] = None,
        title: Optional[str] = None,
        notification_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send persistent notification with circuit breaker and operation context."""
        from .shared_utilities import (
            create_operation_context, close_operation_context, handle_operation_error
        )
        
        context = create_operation_context('ha_notification', 'persistent',
                                          message_length=len(message), has_title=bool(title))
        
        try:
            if not is_ha_available():
                close_operation_context(context, success=False)
                return handle_operation_error(
                    'ha_notification', 'persistent',
                    Exception("Home Assistant circuit breaker open"),
                    context['correlation_id']
                )
            
            config = ha_config or get_ha_config()
            
            service_data = {"message": message}
            if title:
                service_data["title"] = title
            if notification_id:
                service_data["notification_id"] = notification_id
            
            result = call_ha_service("persistent_notification", "create", config, None, service_data)
            
            self._stats['operations'] += 1
            if result.get('success'):
                self._stats['successes'] += 1
                self._stats['by_type']['persistent']['operations'] += 1
                self._stats['by_type']['persistent']['successes'] += 1
            else:
                self._stats['failures'] += 1
            
            close_operation_context(context, success=result.get('success', False), result=result)
            
            increment_counter('ha_persistent_notification')
            
            return create_success_response(
                "Persistent notification created",
                {
                    'message': message,
                    'title': title,
                    'notification_id': notification_id,
                    'result': result
                }
            )
            
        except Exception as e:
            self._stats['failures'] += 1
            close_operation_context(context, success=False)
            return handle_operation_error('ha_notification', 'persistent', e, context['correlation_id'])
    
    def dismiss_notification(
        self,
        notification_id: str,
        ha_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Dismiss notification with circuit breaker and operation context."""
        from .shared_utilities import (
            create_operation_context, close_operation_context, handle_operation_error
        )
        
        context = create_operation_context('ha_notification', 'dismiss',
                                          notification_id=notification_id)
        
        try:
            if not is_ha_available():
                close_operation_context(context, success=False)
                return handle_operation_error(
                    'ha_notification', 'dismiss',
                    Exception("Home Assistant circuit breaker open"),
                    context['correlation_id']
                )
            
            config = ha_config or get_ha_config()
            
            service_data = {"notification_id": notification_id}
            result = call_ha_service("persistent_notification", "dismiss", config, None, service_data)
            
            self._stats['operations'] += 1
            if result.get('success'):
                self._stats['successes'] += 1
                self._stats['by_type']['dismiss']['operations'] += 1
                self._stats['by_type']['dismiss']['successes'] += 1
            else:
                self._stats['failures'] += 1
            
            close_operation_context(context, success=result.get('success', False), result=result)
            
            increment_counter('ha_dismiss_notification')
            
            return create_success_response(
                f"Notification {notification_id} dismissed",
                {
                    'notification_id': notification_id,
                    'result': result
                }
            )
            
        except Exception as e:
            self._stats['failures'] += 1
            close_operation_context(context, success=False)
            return handle_operation_error('ha_notification', 'dismiss', e, context['correlation_id'])
    
    def _resolve_media_players(self, player_ids: List[str], config: Dict[str, Any]) -> List[str]:
        """Resolve media player IDs to entity IDs."""
        response = batch_get_states(None, config, use_cache=True)
        if not response.get('success'):
            return []
        
        states = response.get('data', [])
        all_players = [
            state.get('entity_id')
            for state in states
            if state.get('entity_id', '').startswith('media_player.')
        ]
        
        resolved = []
        for player_id in player_ids:
            if player_id in all_players:
                resolved.append(player_id)
            else:
                player_id_lower = player_id.lower()
                for entity_id in all_players:
                    if player_id_lower in entity_id.lower():
                        resolved.append(entity_id)
                        break
        
        return resolved
    
    def _get_available_media_players(self, config: Dict[str, Any]) -> List[str]:
        """Get available media players with caching."""
        from .shared_utilities import cache_operation_result
        
        def _get_players():
            response = batch_get_states(None, config, use_cache=True)
            if not response.get('success'):
                return []
            
            states = response.get('data', [])
            players = []
            
            for state in states:
                entity_id = state.get('entity_id', '')
                if not entity_id.startswith('media_player.'):
                    continue
                
                if any(keyword in entity_id.lower() for keyword in ['chromecast', 'google', 'alexa', 'sonos']):
                    players.append(entity_id)
            
            if not players:
                players = [
                    state.get('entity_id')
                    for state in states
                    if state.get('entity_id', '').startswith('media_player.')
                ]
            
            return players
        
        return cache_operation_result(
            operation_name="get_media_players",
            func=_get_players,
            ttl=HA_CACHE_TTL_ENTITIES,
            cache_key_prefix="ha_media_players"
        )
    
    def get_stats(self) -> Dict[str, Any]:
        """Get notification manager statistics."""
        return {
            "feature": self.get_feature_name(),
            **self._stats,
            "success_rate": (self._stats['successes'] / self._stats['operations'] * 100)
                           if self._stats['operations'] > 0 else 0.0
        }


_notification_manager = HANotificationManager()


def send_tts_announcement(message: str, ha_config: Optional[Dict[str, Any]] = None,
                         media_players: Optional[List[str]] = None,
                         language: str = "en-US") -> Dict[str, Any]:
    """Send TTS announcement via manager."""
    return _notification_manager.send_tts_announcement(message, ha_config, media_players, language)


def send_persistent_notification(message: str, ha_config: Optional[Dict[str, Any]] = None,
                                 title: Optional[str] = None,
                                 notification_id: Optional[str] = None) -> Dict[str, Any]:
    """Send persistent notification via manager."""
    return _notification_manager.send_persistent_notification(message, ha_config, title, notification_id)


def dismiss_notification(notification_id: str, ha_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Dismiss notification via manager."""
    return _notification_manager.dismiss_notification(notification_id, ha_config)


def get_notification_stats() -> Dict[str, Any]:
    """Get notification manager statistics."""
    return _notification_manager.get_stats()


__all__ = [
    'HANotificationManager',
    'send_tts_announcement',
    'send_persistent_notification',
    'dismiss_notification',
    'get_notification_stats',
]

# EOF
