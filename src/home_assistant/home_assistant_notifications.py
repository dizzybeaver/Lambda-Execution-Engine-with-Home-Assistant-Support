"""
home_assistant_notifications.py - TTS & Notifications
Version: 2025.09.30.07
Daily Revision: Performance Optimization Phase 2

Phase 2: Consolidated cache + entity minimization

Licensed under the Apache License, Version 2.0
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
    HABaseManager,
    call_ha_service,
    SingletonManager,
    get_cache_section,
    set_cache_section,
    minimize_entity_list
)


class HANotificationManager(HABaseManager):
    """Manages Home Assistant TTS and notifications."""
    
    def __init__(self):
        super().__init__()
        self._tts_count = 0
        self._notification_count = 0
    
    def get_feature_name(self) -> str:
        return "notification"
    
    def send_tts(
        self,
        message: str,
        ha_config: Dict[str, Any],
        media_player_ids: Optional[List[str]] = None,
        language: str = "en"
    ) -> Dict[str, Any]:
        """Send TTS announcement."""
        start_time = time.time()
        correlation_id = generate_correlation_id()
        
        try:
            log_info(f"Sending TTS: {message[:50]}... [{correlation_id}]")
            increment_counter("ha_announcement_request")
            
            if not media_player_ids:
                media_players = self._get_media_players(ha_config)
                media_player_ids = [e["entity_id"] for e in media_players]
            
            if not media_player_ids:
                self.record_failure()
                return create_error_response("No media players found", {})
            
            service_data = {
                "entity_id": media_player_ids,
                "message": message,
                "language": language
            }
            
            result = call_ha_service("tts", "cloud_say", ha_config, None, service_data)
            
            duration_ms = (time.time() - start_time) * 1000
            
            if result.get("success", False):
                self.record_success()
                self._tts_count += 1
                log_info(f"TTS sent to {len(media_player_ids)} players [{correlation_id}]")
                return create_success_response(
                    "TTS announcement sent",
                    {
                        "media_players": media_player_ids,
                        "message_length": len(message),
                        "processing_time_ms": duration_ms,
                        "correlation_id": correlation_id
                    }
                )
            else:
                self.record_failure()
                return create_error_response("Failed to send TTS", {"result": result})
                
        except Exception as e:
            self.record_failure()
            log_error(f"Send TTS exception: {str(e)}")
            return create_error_response("Send TTS exception", {"error": str(e)})
    
    def send_notification(
        self,
        message: str,
        ha_config: Dict[str, Any],
        title: str = "Notification",
        notification_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send persistent notification."""
        correlation_id = generate_correlation_id()
        
        try:
            log_info(f"Sending notification: {title} [{correlation_id}]")
            
            service_data = {
                "message": message,
                "title": title
            }
            if notification_id:
                service_data["notification_id"] = notification_id
            
            result = call_ha_service("persistent_notification", "create", ha_config, None, service_data)
            
            if result.get("success", False):
                self.record_success()
                self._notification_count += 1
                log_info(f"Notification sent: {title} [{correlation_id}]")
                return create_success_response(
                    "Notification sent",
                    {
                        "title": title,
                        "notification_id": notification_id,
                        "correlation_id": correlation_id
                    }
                )
            else:
                self.record_failure()
                return create_error_response("Failed to send notification", {"result": result})
                
        except Exception as e:
            self.record_failure()
            log_error(f"Send notification exception: {str(e)}")
            return create_error_response("Send notification exception", {"error": str(e)})
    
    def _get_media_players(self, ha_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get media players with consolidated cache."""
        cached = get_cache_section("media_players", ttl=300)
        if cached:
            self.record_cache_hit()
            return cached
        
        self.record_cache_miss()
        from ha_common import call_ha_api
        response = call_ha_api("/api/states", ha_config)
        
        if not isinstance(response, list):
            return []
        
        media_players = [e for e in response if e.get("entity_id", "").startswith("media_player.")]
        minimized = minimize_entity_list(media_players)
        
        set_cache_section("media_players", minimized, ttl=300)
        return minimized


def send_tts_announcement(
    message: str,
    ha_config: Dict[str, Any],
    media_player_ids: Optional[List[str]] = None,
    language: str = "en"
) -> Dict[str, Any]:
    """Send TTS announcement."""
    manager = SingletonManager.get_instance(HANotificationManager)
    return manager.send_tts(message, ha_config, media_player_ids, language)


def send_persistent_notification(
    message: str,
    ha_config: Dict[str, Any],
    title: str = "Notification",
    notification_id: Optional[str] = None
) -> Dict[str, Any]:
    """Send persistent notification."""
    manager = SingletonManager.get_instance(HANotificationManager)
    return manager.send_notification(message, ha_config, title, notification_id)


def get_notification_stats() -> Dict[str, Any]:
    """Get notification statistics."""
    manager = SingletonManager.get_instance(HANotificationManager)
    stats = manager.get_stats()
    stats["tts_count"] = manager._tts_count
    stats["notification_count"] = manager._notification_count
    return stats


__all__ = ["send_tts_announcement", "send_persistent_notification", "get_notification_stats"]
