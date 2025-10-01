"""
home_assistant_timers.py - Timer Management
Version: 2025.09.30.07
Daily Revision: Performance Optimization Phase 2

Phase 2: Consolidated cache + entity minimization

Licensed under the Apache License, Version 2.0
"""

import time
import re
from typing import Dict, Any, Optional

from gateway import (
    log_info, log_error,
    create_success_response, create_error_response,
    generate_correlation_id,
    increment_counter
)

from ha_common import (
    HABaseManager,
    resolve_entity_id,
    call_ha_service,
    SingletonManager,
    get_cache_section,
    set_cache_section,
    minimize_entity_list
)


class HATimerManager(HABaseManager):
    """Manages Home Assistant timer operations."""
    
    def get_feature_name(self) -> str:
        return "timer"
    
    def start(
        self,
        timer_name: str,
        duration: str,
        ha_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Start timer with duration."""
        correlation_id = generate_correlation_id()
        
        try:
            log_info(f"Starting timer: {timer_name} for {duration} [{correlation_id}]")
            increment_counter("ha_timer_start_request")
            
            entity_id = timer_name if "." in timer_name else resolve_entity_id(timer_name, "timer", ha_config)
            if not entity_id:
                self.record_failure()
                return create_error_response("Timer not found", {"timer_name": timer_name})
            
            duration_seconds = self._parse_duration(duration)
            if duration_seconds <= 0:
                self.record_failure()
                return create_error_response("Invalid duration", {"duration": duration})
            
            service_data = {"duration": duration_seconds}
            result = call_ha_service("timer", "start", ha_config, entity_id, service_data)
            
            if result.get("success", False):
                self.record_success()
                log_info(f"Timer started: {entity_id} [{correlation_id}]")
                return create_success_response(
                    f"Timer {timer_name} started for {duration}",
                    {
                        "entity_id": entity_id,
                        "duration_seconds": duration_seconds,
                        "correlation_id": correlation_id
                    }
                )
            else:
                self.record_failure()
                return create_error_response("Failed to start timer", {"result": result})
                
        except Exception as e:
            self.record_failure()
            log_error(f"Start timer exception: {str(e)}")
            return create_error_response("Start timer exception", {"error": str(e)})
    
    def cancel(
        self,
        timer_id: str,
        ha_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Cancel running timer."""
        correlation_id = generate_correlation_id()
        
        try:
            log_info(f"Canceling timer: {timer_id} [{correlation_id}]")
            increment_counter("ha_timer_cancel_request")
            
            entity_id = timer_id if "." in timer_id else resolve_entity_id(timer_id, "timer", ha_config)
            if not entity_id:
                self.record_failure()
                return create_error_response("Timer not found", {"timer_id": timer_id})
            
            result = call_ha_service("timer", "cancel", ha_config, entity_id)
            
            if result.get("success", False):
                self.record_success()
                log_info(f"Timer canceled: {entity_id} [{correlation_id}]")
                return create_success_response(
                    f"Timer {timer_id} canceled",
                    {
                        "entity_id": entity_id,
                        "correlation_id": correlation_id
                    }
                )
            else:
                self.record_failure()
                return create_error_response("Failed to cancel timer", {"result": result})
                
        except Exception as e:
            self.record_failure()
            log_error(f"Cancel timer exception: {str(e)}")
            return create_error_response("Cancel timer exception", {"error": str(e)})
    
    def pause(
        self,
        timer_id: str,
        ha_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Pause running timer."""
        correlation_id = generate_correlation_id()
        
        try:
            log_info(f"Pausing timer: {timer_id} [{correlation_id}]")
            
            entity_id = timer_id if "." in timer_id else resolve_entity_id(timer_id, "timer", ha_config)
            if not entity_id:
                self.record_failure()
                return create_error_response("Timer not found", {"timer_id": timer_id})
            
            result = call_ha_service("timer", "pause", ha_config, entity_id)
            
            if result.get("success", False):
                self.record_success()
                log_info(f"Timer paused: {entity_id} [{correlation_id}]")
                return create_success_response(
                    f"Timer {timer_id} paused",
                    {"entity_id": entity_id, "correlation_id": correlation_id}
                )
            else:
                self.record_failure()
                return create_error_response("Failed to pause timer", {"result": result})
                
        except Exception as e:
            self.record_failure()
            log_error(f"Pause timer exception: {str(e)}")
            return create_error_response("Pause timer exception", {"error": str(e)})
    
    def finish(
        self,
        timer_id: str,
        ha_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Finish timer immediately."""
        correlation_id = generate_correlation_id()
        
        try:
            log_info(f"Finishing timer: {timer_id} [{correlation_id}]")
            
            entity_id = timer_id if "." in timer_id else resolve_entity_id(timer_id, "timer", ha_config)
            if not entity_id:
                self.record_failure()
                return create_error_response("Timer not found", {"timer_id": timer_id})
            
            result = call_ha_service("timer", "finish", ha_config, entity_id)
            
            if result.get("success", False):
                self.record_success()
                log_info(f"Timer finished: {entity_id} [{correlation_id}]")
                return create_success_response(
                    f"Timer {timer_id} finished",
                    {"entity_id": entity_id, "correlation_id": correlation_id}
                )
            else:
                self.record_failure()
                return create_error_response("Failed to finish timer", {"result": result})
                
        except Exception as e:
            self.record_failure()
            log_error(f"Finish timer exception: {str(e)}")
            return create_error_response("Finish timer exception", {"error": str(e)})
    
    def list(self, ha_config: Dict[str, Any]) -> Dict[str, Any]:
        """List all timers with consolidated cache."""
        try:
            cached = get_cache_section("timers", ttl=60)
            if cached:
                self.record_cache_hit()
                return create_success_response("Timers retrieved from cache", {"timers": cached})
            
            self.record_cache_miss()
            from ha_common import call_ha_api
            response = call_ha_api("/api/states", ha_config)
            
            if not isinstance(response, list):
                return create_error_response("Invalid API response", {})
            
            timers = [e for e in response if e.get("entity_id", "").startswith("timer.")]
            minimized = minimize_entity_list(timers)
            
            set_cache_section("timers", minimized, ttl=60)
            
            return create_success_response("Timers retrieved", {"timers": minimized})
            
        except Exception as e:
            log_error(f"List timers exception: {str(e)}")
            return create_error_response("List timers exception", {"error": str(e)})
    
    def _parse_duration(self, duration_str: str) -> int:
        """Parse duration string to seconds."""
        duration_str = duration_str.lower().strip()
        total_seconds = 0
        
        if ':' in duration_str:
            parts = duration_str.split(':')
            if len(parts) == 3:
                total_seconds = int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
            elif len(parts) == 2:
                total_seconds = int(parts[0]) * 60 + int(parts[1])
            return total_seconds
        
        hours_match = re.search(r'(\d+)\s*(?:hour|hr|h)', duration_str)
        if hours_match:
            total_seconds += int(hours_match.group(1)) * 3600
        
        minutes_match = re.search(r'(\d+)\s*(?:minute|min|m)', duration_str)
        if minutes_match:
            total_seconds += int(minutes_match.group(1)) * 60
        
        seconds_match = re.search(r'(\d+)\s*(?:second|sec|s)', duration_str)
        if seconds_match:
            total_seconds += int(seconds_match.group(1))
        
        if total_seconds == 0:
            number_match = re.search(r'(\d+)', duration_str)
            if number_match:
                total_seconds = int(number_match.group(1)) * 60
        
        return total_seconds


def start_timer(
    timer_name: str,
    duration: str,
    ha_config: Dict[str, Any]
) -> Dict[str, Any]:
    """Start timer."""
    manager = SingletonManager.get_instance(HATimerManager)
    return manager.start(timer_name, duration, ha_config)


def cancel_timer(
    timer_id: str,
    ha_config: Dict[str, Any]
) -> Dict[str, Any]:
    """Cancel timer."""
    manager = SingletonManager.get_instance(HATimerManager)
    return manager.cancel(timer_id, ha_config)


def pause_timer(
    timer_id: str,
    ha_config: Dict[str, Any]
) -> Dict[str, Any]:
    """Pause timer."""
    manager = SingletonManager.get_instance(HATimerManager)
    return manager.pause(timer_id, ha_config)


def finish_timer(
    timer_id: str,
    ha_config: Dict[str, Any]
) -> Dict[str, Any]:
    """Finish timer."""
    manager = SingletonManager.get_instance(HATimerManager)
    return manager.finish(timer_id, ha_config)


def list_timers(ha_config: Dict[str, Any]) -> Dict[str, Any]:
    """List all timers."""
    manager = SingletonManager.get_instance(HATimerManager)
    return manager.list(ha_config)


def get_timer_stats() -> Dict[str, Any]:
    """Get timer statistics."""
    manager = SingletonManager.get_instance(HATimerManager)
    return manager.get_stats()


__all__ = ["start_timer", "cancel_timer", "pause_timer", "finish_timer", "list_timers", "get_timer_stats"]
