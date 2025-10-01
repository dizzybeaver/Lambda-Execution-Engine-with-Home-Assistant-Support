"""
home_assistant_notifications.py - TTS and Notifications
Version: 2025.09.30.04
Daily Revision: 001

Home Assistant TTS and notification services
Supports whole-home announcements via media players

ARCHITECTURE: HOME ASSISTANT EXTENSION MODULE
- Uses gateway.py for all operations
- Lazy loading compatible
- 100% Free Tier AWS compliant
- Self-contained within extension

Licensed under the Apache License, Version 2.0
"""

import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

from gateway import (
    log_info, log_error, log_warning, log_debug,
    make_post_request, make_get_request,
    create_success_response, create_error_response,
    generate_correlation_id,
    record_metric, increment_counter,
    cache_get, cache_set
)


@dataclass
class NotificationStats:
    """Statistics for notification operations."""
    total_sent: int = 0
    successful_sent: int = 0
    failed_sent: int = 0
    tts_sent: int = 0
    persistent_sent: int = 0


class HANotificationManager:
    """Manages Home Assistant notifications and TTS."""
    
    def __init__(self):
        self._stats = NotificationStats()
        self._initialized_time = time.time()
    
    def send_tts_announcement(self,
                             message: str,
                             ha_config: Dict[str, Any],
                             media_player_ids: Optional[List[str]] = None,
                             language: str = "en") -> Dict[str, Any]:
        """
        Send TTS announcement to media players.
        
        Args:
            message: Message to announce
            ha_config: HA configuration dict
            media_player_ids: Optional list of media player entity_ids (all if None)
            language: TTS language code
            
        Returns:
            Result dict with success status
        """
        start_time = time.time()
        correlation_id = generate_correlation_id()
        
        try:
            log_info(f"Sending TTS announcement: {message[:50]}... [{correlation_id}]")
            increment_counter("ha_tts_announcement_request")
            
            if media_player_ids is None:
                media_players = self._get_all_media_players(ha_config)
                if not media_players:
                    return create_error_response("No media players found", {})
                media_player_ids = [mp["entity_id"] for mp in media_players]
            
            url = f"{ha_config['base_url']}/api/services/tts/cloud_say"
            headers = {
                "Authorization": f"Bearer {ha_config['access_token']}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "entity_id": media_player_ids,
                "message": message,
                "language": language
            }
            
            result = make_post_request(
                url=url,
                headers=headers,
                json_data=payload,
                timeout=ha_config.get('timeout', 30)
            )
            
            processing_time = (time.time() - start_time) * 1000
            
            if result.get("success", False):
                log_info(f"TTS announcement sent [{correlation_id}]")
                record_metric("ha_tts_announcement_success", 1.0)
                self._update_stats(True, "tts")
                
                return create_success_response(
                    "Announcement sent successfully",
                    {
                        "media_players": media_player_ids,
                        "message_length": len(message),
                        "processing_time_ms": processing_time,
                        "correlation_id": correlation_id
                    }
                )
            else:
                log_error(f"TTS announcement failed: {result}")
                self._update_stats(False, "tts")
                return create_error_response(
                    "Failed to send announcement",
                    {"result": result}
                )
                
        except Exception as e:
            log_error(f"TTS announcement exception: {str(e)}")
            record_metric("ha_tts_announcement_error", 1.0)
            self._update_stats(False, "tts")
            return create_error_response(
                "TTS announcement exception",
                {"error": str(e)}
            )
    
    def send_persistent_notification(self,
                                    message: str,
                                    ha_config: Dict[str, Any],
                                    title: Optional[str] = None,
                                    notification_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Send persistent notification to Home Assistant.
        
        Args:
            message: Notification message
            ha_config: HA configuration dict
            title: Optional notification title
            notification_id: Optional notification ID
            
        Returns:
            Result dict with success status
        """
        start_time = time.time()
        correlation_id = generate_correlation_id()
        
        try:
            log_info(f"Sending persistent notification [{correlation_id}]")
            increment_counter("ha_persistent_notification_request")
            
            url = f"{ha_config['base_url']}/api/services/persistent_notification/create"
            headers = {
                "Authorization": f"Bearer {ha_config['access_token']}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "message": message
            }
            
            if title:
                payload["title"] = title
            
            if notification_id:
                payload["notification_id"] = notification_id
            
            result = make_post_request(
                url=url,
                headers=headers,
                json_data=payload,
                timeout=ha_config.get('timeout', 30)
            )
            
            processing_time = (time.time() - start_time) * 1000
            
            if result.get("success", False):
                log_info(f"Persistent notification sent [{correlation_id}]")
                record_metric("ha_persistent_notification_success", 1.0)
                self._update_stats(True, "persistent")
                
                return create_success_response(
                    "Notification sent successfully",
                    {
                        "title": title,
                        "notification_id": notification_id,
                        "processing_time_ms": processing_time,
                        "correlation_id": correlation_id
                    }
                )
            else:
                log_error(f"Persistent notification failed: {result}")
                self._update_stats(False, "persistent")
                return create_error_response(
                    "Failed to send notification",
                    {"result": result}
                )
                
        except Exception as e:
            log_error(f"Persistent notification exception: {str(e)}")
            record_metric("ha_persistent_notification_error", 1.0)
            self._update_stats(False, "persistent")
            return create_error_response(
                "Persistent notification exception",
                {"error": str(e)}
            )
    
    def dismiss_notification(self,
                           notification_id: str,
                           ha_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Dismiss persistent notification.
        
        Args:
            notification_id: Notification ID to dismiss
            ha_config: HA configuration dict
            
        Returns:
            Result dict with success status
        """
        try:
            log_info(f"Dismissing notification: {notification_id}")
            
            url = f"{ha_config['base_url']}/api/services/persistent_notification/dismiss"
            headers = {
                "Authorization": f"Bearer {ha_config['access_token']}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "notification_id": notification_id
            }
            
            result = make_post_request(
                url=url,
                headers=headers,
                json_data=payload,
                timeout=ha_config.get('timeout', 30)
            )
            
            if result.get("success", False):
                return create_success_response(
                    "Notification dismissed",
                    {"notification_id": notification_id}
                )
            else:
                return create_error_response(
                    "Failed to dismiss notification",
                    {"result": result}
                )
                
        except Exception as e:
            log_error(f"Dismiss notification exception: {str(e)}")
            return create_error_response(
                "Dismiss notification exception",
                {"error": str(e)}
            )
    
    def _get_all_media_players(self, ha_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get all available media players."""
        try:
            cache_key = "ha_media_players"
            cached = cache_get(cache_key)
            if cached:
                return cached
            
            url = f"{ha_config['base_url']}/api/states"
            headers = {
                "Authorization": f"Bearer {ha_config['access_token']}"
            }
            
            result = make_get_request(
                url=url,
                headers=headers,
                timeout=ha_config.get('timeout', 30)
            )
            
            if not result.get("success", False):
                return []
            
            states = result.get("data", [])
            media_players = [
                {
                    "entity_id": state.get("entity_id"),
                    "friendly_name": state.get("attributes", {}).get("friendly_name", ""),
                    "state": state.get("state")
                }
                for state in states
                if state.get("entity_id", "").startswith("media_player.")
            ]
            
            cache_set(cache_key, media_players, ttl=300)
            
            return media_players
            
        except Exception as e:
            log_error(f"Get media players exception: {str(e)}")
            return []
    
    def _update_stats(self, success: bool, notification_type: str) -> None:
        """Update notification statistics."""
        self._stats.total_sent += 1
        
        if success:
            self._stats.successful_sent += 1
        else:
            self._stats.failed_sent += 1
        
        if notification_type == "tts":
            self._stats.tts_sent += 1
        elif notification_type == "persistent":
            self._stats.persistent_sent += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Get notification statistics."""
        return {
            "total_sent": self._stats.total_sent,
            "successful_sent": self._stats.successful_sent,
            "failed_sent": self._stats.failed_sent,
            "success_rate": (self._stats.successful_sent / self._stats.total_sent * 100
                           if self._stats.total_sent > 0 else 0.0),
            "tts_sent": self._stats.tts_sent,
            "persistent_sent": self._stats.persistent_sent,
            "uptime_seconds": time.time() - self._initialized_time
        }


_notification_manager: Optional[HANotificationManager] = None


def _get_notification_manager() -> HANotificationManager:
    """Get or create notification manager singleton."""
    global _notification_manager
    if _notification_manager is None:
        _notification_manager = HANotificationManager()
    return _notification_manager


def send_tts_announcement(message: str,
                         ha_config: Dict[str, Any],
                         media_player_ids: Optional[List[str]] = None,
                         language: str = "en") -> Dict[str, Any]:
    """Send TTS announcement."""
    manager = _get_notification_manager()
    return manager.send_tts_announcement(message, ha_config, media_player_ids, language)


def send_persistent_notification(message: str,
                                 ha_config: Dict[str, Any],
                                 title: Optional[str] = None,
                                 notification_id: Optional[str] = None) -> Dict[str, Any]:
    """Send persistent notification."""
    manager = _get_notification_manager()
    return manager.send_persistent_notification(message, ha_config, title, notification_id)


def dismiss_notification(notification_id: str, ha_config: Dict[str, Any]) -> Dict[str, Any]:
    """Dismiss persistent notification."""
    manager = _get_notification_manager()
    return manager.dismiss_notification(notification_id, ha_config)


def get_notification_stats() -> Dict[str, Any]:
    """Get notification statistics."""
    manager = _get_notification_manager()
    return manager.get_stats()


__all__ = [
    'send_tts_announcement',
    'send_persistent_notification',
    'dismiss_notification',
    'get_notification_stats',
]

#EOF
