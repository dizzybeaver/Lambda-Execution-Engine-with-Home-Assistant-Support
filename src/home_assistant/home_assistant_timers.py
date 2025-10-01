"""
home_assistant_timers.py - Timer Management
Version: 2025.09.30.04
Daily Revision: 001

Home Assistant timer entity management
Create, start, pause, cancel, and query timers

ARCHITECTURE: HOME ASSISTANT EXTENSION MODULE
- Uses gateway.py for all operations
- Lazy loading compatible
- 100% Free Tier AWS compliant
- Self-contained within extension

Licensed under the Apache License, Version 2.0
"""

import time
import re
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
class TimerStats:
    """Statistics for timer operations."""
    total_created: int = 0
    total_started: int = 0
    total_paused: int = 0
    total_cancelled: int = 0
    total_finished: int = 0


class HATimerManager:
    """Manages Home Assistant timer operations."""
    
    def __init__(self):
        self._stats = TimerStats()
        self._initialized_time = time.time()
    
    def start_timer(self,
                   timer_id: str,
                   duration: str,
                   ha_config: Dict[str, Any],
                   friendly_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Start a timer.
        
        Args:
            timer_id: Timer entity_id (without domain)
            duration: Duration string (e.g., "00:10:00", "10 minutes")
            ha_config: HA configuration dict
            friendly_name: Optional friendly name for the timer
            
        Returns:
            Result dict with success status
        """
        start_time = time.time()
        correlation_id = generate_correlation_id()
        
        try:
            log_info(f"Starting timer {timer_id} for {duration} [{correlation_id}]")
            increment_counter("ha_timer_start_request")
            
            duration_seconds = self._parse_duration(duration)
            if duration_seconds is None:
                return create_error_response(
                    "Invalid duration format",
                    {"duration": duration}
                )
            
            entity_id = f"timer.{timer_id}" if not timer_id.startswith("timer.") else timer_id
            
            url = f"{ha_config['base_url']}/api/services/timer/start"
            headers = {
                "Authorization": f"Bearer {ha_config['access_token']}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "entity_id": entity_id,
                "duration": self._seconds_to_hms(duration_seconds)
            }
            
            result = make_post_request(
                url=url,
                headers=headers,
                json_data=payload,
                timeout=ha_config.get('timeout', 30)
            )
            
            processing_time = (time.time() - start_time) * 1000
            
            if result.get("success", False):
                log_info(f"Timer started: {entity_id} [{correlation_id}]")
                record_metric("ha_timer_start_success", 1.0)
                self._stats.total_started += 1
                
                return create_success_response(
                    f"Timer {timer_id} started for {duration}",
                    {
                        "entity_id": entity_id,
                        "duration_seconds": duration_seconds,
                        "processing_time_ms": processing_time,
                        "correlation_id": correlation_id
                    }
                )
            else:
                log_error(f"Timer start failed: {result}")
                return create_error_response(
                    "Failed to start timer",
                    {"result": result}
                )
                
        except Exception as e:
            log_error(f"Timer start exception: {str(e)}")
            record_metric("ha_timer_start_error", 1.0)
            return create_error_response(
                "Timer start exception",
                {"error": str(e)}
            )
    
    def pause_timer(self,
                   timer_id: str,
                   ha_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Pause a running timer.
        
        Args:
            timer_id: Timer entity_id
            ha_config: HA configuration dict
            
        Returns:
            Result dict with success status
        """
        try:
            log_info(f"Pausing timer: {timer_id}")
            
            entity_id = f"timer.{timer_id}" if not timer_id.startswith("timer.") else timer_id
            
            url = f"{ha_config['base_url']}/api/services/timer/pause"
            headers = {
                "Authorization": f"Bearer {ha_config['access_token']}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "entity_id": entity_id
            }
            
            result = make_post_request(
                url=url,
                headers=headers,
                json_data=payload,
                timeout=ha_config.get('timeout', 30)
            )
            
            if result.get("success", False):
                log_info(f"Timer paused: {entity_id}")
                self._stats.total_paused += 1
                return create_success_response(
                    f"Timer {timer_id} paused",
                    {"entity_id": entity_id}
                )
            else:
                return create_error_response(
                    "Failed to pause timer",
                    {"result": result}
                )
                
        except Exception as e:
            log_error(f"Timer pause exception: {str(e)}")
            return create_error_response(
                "Timer pause exception",
                {"error": str(e)}
            )
    
    def cancel_timer(self,
                    timer_id: str,
                    ha_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Cancel a timer.
        
        Args:
            timer_id: Timer entity_id
            ha_config: HA configuration dict
            
        Returns:
            Result dict with success status
        """
        try:
            log_info(f"Cancelling timer: {timer_id}")
            
            entity_id = f"timer.{timer_id}" if not timer_id.startswith("timer.") else timer_id
            
            url = f"{ha_config['base_url']}/api/services/timer/cancel"
            headers = {
                "Authorization": f"Bearer {ha_config['access_token']}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "entity_id": entity_id
            }
            
            result = make_post_request(
                url=url,
                headers=headers,
                json_data=payload,
                timeout=ha_config.get('timeout', 30)
            )
            
            if result.get("success", False):
                log_info(f"Timer cancelled: {entity_id}")
                self._stats.total_cancelled += 1
                return create_success_response(
                    f"Timer {timer_id} cancelled",
                    {"entity_id": entity_id}
                )
            else:
                return create_error_response(
                    "Failed to cancel timer",
                    {"result": result}
                )
                
        except Exception as e:
            log_error(f"Timer cancel exception: {str(e)}")
            return create_error_response(
                "Timer cancel exception",
                {"error": str(e)}
            )
    
    def finish_timer(self,
                    timer_id: str,
                    ha_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Finish a timer immediately.
        
        Args:
            timer_id: Timer entity_id
            ha_config: HA configuration dict
            
        Returns:
            Result dict with success status
        """
        try:
            log_info(f"Finishing timer: {timer_id}")
            
            entity_id = f"timer.{timer_id}" if not timer_id.startswith("timer.") else timer_id
            
            url = f"{ha_config['base_url']}/api/services/timer/finish"
            headers = {
                "Authorization": f"Bearer {ha_config['access_token']}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "entity_id": entity_id
            }
            
            result = make_post_request(
                url=url,
                headers=headers,
                json_data=payload,
                timeout=ha_config.get('timeout', 30)
            )
            
            if result.get("success", False):
                log_info(f"Timer finished: {entity_id}")
                self._stats.total_finished += 1
                return create_success_response(
                    f"Timer {timer_id} finished",
                    {"entity_id": entity_id}
                )
            else:
                return create_error_response(
                    "Failed to finish timer",
                    {"result": result}
                )
                
        except Exception as e:
            log_error(f"Timer finish exception: {str(e)}")
            return create_error_response(
                "Timer finish exception",
                {"error": str(e)}
            )
    
    def get_timer_status(self,
                        timer_id: str,
                        ha_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get timer status.
        
        Args:
            timer_id: Timer entity_id
            ha_config: HA configuration dict
            
        Returns:
            Timer status
        """
        try:
            entity_id = f"timer.{timer_id}" if not timer_id.startswith("timer.") else timer_id
            
            url = f"{ha_config['base_url']}/api/states/{entity_id}"
            headers = {
                "Authorization": f"Bearer {ha_config['access_token']}"
            }
            
            result = make_get_request(
                url=url,
                headers=headers,
                timeout=ha_config.get('timeout', 30)
            )
            
            if result.get("success", False):
                state_data = result.get("data", {})
                return create_success_response(
                    "Timer status retrieved",
                    {
                        "entity_id": entity_id,
                        "state": state_data.get("state"),
                        "duration": state_data.get("attributes", {}).get("duration"),
                        "remaining": state_data.get("attributes", {}).get("remaining"),
                        "finishes_at": state_data.get("attributes", {}).get("finishes_at")
                    }
                )
            else:
                return create_error_response(
                    "Failed to get timer status",
                    {"result": result}
                )
                
        except Exception as e:
            log_error(f"Get timer status exception: {str(e)}")
            return create_error_response(
                "Get timer status exception",
                {"error": str(e)}
            )
    
    def list_timers(self, ha_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        List all timers.
        
        Args:
            ha_config: HA configuration dict
            
        Returns:
            List of timers
        """
        try:
            cache_key = "ha_timer_list"
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
                return create_error_response("Failed to list timers", {"result": result})
            
            states = result.get("data", [])
            timers = [
                {
                    "entity_id": state.get("entity_id"),
                    "friendly_name": state.get("attributes", {}).get("friendly_name", ""),
                    "state": state.get("state"),
                    "duration": state.get("attributes", {}).get("duration"),
                    "remaining": state.get("attributes", {}).get("remaining")
                }
                for state in states
                if state.get("entity_id", "").startswith("timer.")
            ]
            
            response = create_success_response(
                "Timers listed successfully",
                {"timers": timers, "count": len(timers)}
            )
            
            cache_set(cache_key, response, ttl=60)
            
            return response
            
        except Exception as e:
            log_error(f"List timers exception: {str(e)}")
            return create_error_response("List timers exception", {"error": str(e)})
    
    def _parse_duration(self, duration: str) -> Optional[int]:
        """
        Parse duration string to seconds.
        
        Supports formats:
        - HH:MM:SS
        - MM:SS
        - "X minutes", "X mins", "X hours", "X hrs", "X seconds", "X secs"
        
        Args:
            duration: Duration string
            
        Returns:
            Duration in seconds or None if invalid
        """
        duration = duration.strip().lower()
        
        hms_match = re.match(r'^(\d{1,2}):(\d{2})(?::(\d{2}))?$', duration)
        if hms_match:
            hours = int(hms_match.group(1))
            minutes = int(hms_match.group(2))
            seconds = int(hms_match.group(3) or 0)
            
            if hms_match.group(3) is None:
                minutes, seconds = hours, minutes
                hours = 0
            
            return hours * 3600 + minutes * 60 + seconds
        
        text_match = re.match(r'^(\d+)\s*(hour|hr|hours|hrs|minute|min|minutes|mins|second|sec|seconds|secs)$', duration)
        if text_match:
            value = int(text_match.group(1))
            unit = text_match.group(2)
            
            if unit in ['hour', 'hr', 'hours', 'hrs']:
                return value * 3600
            elif unit in ['minute', 'min', 'minutes', 'mins']:
                return value * 60
            elif unit in ['second', 'sec', 'seconds', 'secs']:
                return value
        
        if duration.isdigit():
            return int(duration) * 60
        
        return None
    
    def _seconds_to_hms(self, seconds: int) -> str:
        """Convert seconds to HH:MM:SS format."""
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    
    def get_stats(self) -> Dict[str, Any]:
        """Get timer operation statistics."""
        return {
            "total_created": self._stats.total_created,
            "total_started": self._stats.total_started,
            "total_paused": self._stats.total_paused,
            "total_cancelled": self._stats.total_cancelled,
            "total_finished": self._stats.total_finished,
            "uptime_seconds": time.time() - self._initialized_time
        }


_timer_manager: Optional[HATimerManager] = None


def _get_timer_manager() -> HATimerManager:
    """Get or create timer manager singleton."""
    global _timer_manager
    if _timer_manager is None:
        _timer_manager = HATimerManager()
    return _timer_manager


def start_timer(timer_id: str,
               duration: str,
               ha_config: Dict[str, Any],
               friendly_name: Optional[str] = None) -> Dict[str, Any]:
    """Start a timer."""
    manager = _get_timer_manager()
    return manager.start_timer(timer_id, duration, ha_config, friendly_name)


def pause_timer(timer_id: str, ha_config: Dict[str, Any]) -> Dict[str, Any]:
    """Pause a timer."""
    manager = _get_timer_manager()
    return manager.pause_timer(timer_id, ha_config)


def cancel_timer(timer_id: str, ha_config: Dict[str, Any]) -> Dict[str, Any]:
    """Cancel a timer."""
    manager = _get_timer_manager()
    return manager.cancel_timer(timer_id, ha_config)


def finish_timer(timer_id: str, ha_config: Dict[str, Any]) -> Dict[str, Any]:
    """Finish a timer immediately."""
    manager = _get_timer_manager()
    return manager.finish_timer(timer_id, ha_config)


def get_timer_status(timer_id: str, ha_config: Dict[str, Any]) -> Dict[str, Any]:
    """Get timer status."""
    manager = _get_timer_manager()
    return manager.get_timer_status(timer_id, ha_config)


def list_timers(ha_config: Dict[str, Any]) -> Dict[str, Any]:
    """List all timers."""
    manager = _get_timer_manager()
    return manager.list_timers(ha_config)


def get_timer_stats() -> Dict[str, Any]:
    """Get timer operation statistics."""
    manager = _get_timer_manager()
    return manager.get_stats()


__all__ = [
    'start_timer',
    'pause_timer',
    'cancel_timer',
    'finish_timer',
    'get_timer_status',
    'list_timers',
    'get_timer_stats',
]

#EOF
