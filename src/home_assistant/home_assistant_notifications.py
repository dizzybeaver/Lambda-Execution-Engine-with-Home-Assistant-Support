"""
home_assistant_notifications.py - TTS and Notifications
Version: 2025.09.30.05
Daily Revision: Ultra-Optimized

Home Assistant TTS and notification services

ARCHITECTURE: HOME ASSISTANT EXTENSION MODULE
- Uses ha_common for shared functionality
- Uses gateway.py for all operations
- Lazy loading compatible
- 100% Free Tier AWS compliant

Licensed under the Apache License, Version 2.0
"""

import time
from typing import Dict, Any, Optional, List

from gateway import (
    log_info, log_error,
    make_get_request,
    create_success_response, create_error_response,
    generate_correlation_id,
    increment_counter,
    cache_get, cache_set
)

from ha_common import (
    HABaseManager,
    call_ha_service_generic,
    SingletonManager
)


class HANotificationManager(HABaseManager):
    """Manages Home Assistant notifications and TTS."""
    
    def __init__(self):
        super().__init__()
        self._tts_count = 0
        self._persistent_count = 0
    
    def get_feature_name(self) -> str:
        return "notification"
    
    def send_tts(
        self,
        message: str,
        ha_config: Dict[str, Any],
        media_player_ids: Optional[List[str]] = None,
        language: str = "en"
    ) -> Dict[str, Any]:
        """Send TTS announcement to media players."""
        start_time = time.time()
        correlation_id = generate_correlation_id()
        
        try:
            log_info(f"Sending TTS: {message[:50]}... [{correlation_id}]")
            increment_counter("ha_tts_announcement_request")
            
            if media_player_ids is None:
                players = self._get_media_players(ha_config)
                if not players:
                    return create_error_response("No media players found", {})
                media_player_ids = [p["entity_id"] for p in players]
            
            service_data = {
                "entity_id": media_player_ids,
                "message": message,
                "language": language
            }
            
            result = call_ha_service_generic(ha_config, "tts", "cloud_say", None, service_data)
            
            duration_ms = (time.time() - start_time) * 1000
            success = result.get("success", False)
            
            self._stats.record(success, duration_ms)
            self._record_metric("tts", success)
            if success:
                self._tts_count += 1
            
            if success:
                log_info(f"TTS sent [{correlation_id}]")
                return create_success_response(
                    "Announcement sent",
                    {
                        "media_players": media_player_ids,
                        "message_length": len(message),
                        "processing_time_ms": duration_ms,
                        "correlation_id": correlation_id
                    }
                )
            else:
                return create_error_response("Failed to send announcement", {"result": result})
                
        except Exception as e:
            log_error(f"TTS exception: {str(e)}")
            self._stats.record(False)
            self._record_metric("tts", False)
            return create_error_response("TTS exception", {"error": str(e)})
    
    def send_persistent(
        self,
        message: str,
        ha_config: Dict[str, Any],
        title: Optional[str] = None,
        notification_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send persistent notification."""
        try:
            increment_counter("ha_persistent_notification_request")
            
            service_data = {"message": message}
            if title:
                service_data["title"] = title
            if notification_id:
                service_data["notification_id"] = notification_id
            
            result = call_ha_service_generic(
                ha_config, "persistent_notification", "create",
                None, service_data
            )
            
            success = result.get("success", False)
            self._stats.record(success)
            self._record_metric("persistent", success)
            
            if success:
                self._persistent_count += 1
                return create_success_response(
                    "Notification created",
                    {"notification_id": notification_id or "auto"}
                )
            else:
                return create_error_response("Failed to create notification", {"result": result})
                
        except Exception as e:
            log_error(f"Persistent notification exception: {str(e)}")
            self._stats.record(False)
            self._record_metric("persistent", False)
            return create_error_response("Notification exception", {"error": str(e)})
    
    def dismiss(
        self,
        notification_id: str,
        ha_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Dismiss persistent notification."""
        try:
            result = call_ha_service_generic(
                ha_config, "persistent_notification", "dismiss",
                None, {"notification_id": notification_id}
            )
            
            if result.get("success", False):
                return create_success_response("Notification dismissed", {"notification_id": notification_id})
            else:
                return create_error_response("Failed to dismiss notification", {"result": result})
                
        except Exception as e:
            log_error(f"Dismiss notification exception: {str(e)}")
            return create_error_response("Dismiss exception", {"error": str(e)})
    
    def _get_media_players(self, ha_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get all media players with caching."""
        cache_key = "ha_media_players"
        cached = cache_get(cache_key)
        if cached:
            return cached
        
        try:
            url = f"{ha_config['base_url']}/api/states"
            headers = {"Authorization": f"Bearer {ha_config['access_token']}"}
            
            result = make_get_request(url=url, headers=headers, timeout=ha_config.get('timeout', 30))
            
            if result.get("success", False):
                all_states = result.get("data", [])
                players = [s for s in all_states if s.get("entity_id", "").startswith("media_player.")]
                cache_set(cache_key, players, ttl=300)
                return players
        except Exception as e:
            log_error(f"Get media players error: {str(e)}")
        
        return []
    
    def get_stats(self) -> Dict[str, Any]:
        """Get notification statistics."""
        base_stats = super().get_stats()
        base_stats["tts_sent"] = self._tts_count
        base_stats["persistent_sent"] = self._persistent_count
        return base_stats


_manager_singleton = SingletonManager(HANotificationManager)


def send_tts_announcement(
    message: str,
    ha_config: Dict[str, Any],
    media_player_ids: Optional[List[str]] = None,
    language: str = "en"
) -> Dict[str, Any]:
    """Send TTS announcement."""
    return _manager_singleton.get().send_tts(message, ha_config, media_player_ids, language)


def send_persistent_notification(
    message: str,
    ha_config: Dict[str, Any],
    title: Optional[str] = None,
    notification_id: Optional[str] = None
) -> Dict[str, Any]:
    """Send persistent notification."""
    return _manager_singleton.get().send_persistent(message, ha_config, title, notification_id)


def dismiss_notification(
    notification_id: str,
    ha_config: Dict[str, Any]
) -> Dict[str, Any]:
    """Dismiss persistent notification."""
    return _manager_singleton.get().dismiss(notification_id, ha_config)


def get_notification_stats() -> Dict[str, Any]:
    """Get notification statistics."""
    return _manager_singleton.get().get_stats()


__all__ = [
    'send_tts_announcement',
    'send_persistent_notification',
    'dismiss_notification',
    'get_notification_stats'
]
