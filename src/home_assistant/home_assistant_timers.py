"""
home_assistant_timers.py - Timer Management
Version: 2025.09.30.05
Daily Revision: Ultra-Optimized

Home Assistant timer entity management

ARCHITECTURE: HOME ASSISTANT EXTENSION MODULE
- Uses ha_common for shared functionality
- Uses gateway.py for all operations
- Lazy loading compatible
- 100% Free Tier AWS compliant

Licensed under the Apache License, Version 2.0
"""

import time
from typing import Dict, Any, Optional

from gateway import (
    log_info, log_error,
    create_success_response, create_error_response,
    generate_correlation_id,
    increment_counter
)

from ha_common import (
    HABaseManager,
    call_ha_service_generic,
    get_entity_state,
    parse_duration_string,
    format_duration_seconds,
    SingletonManager
)


class HATimerManager(HABaseManager):
    """Manages Home Assistant timer operations."""
    
    def __init__(self):
        super().__init__()
        self._operation_counts = {
            "started": 0,
            "paused": 0,
            "cancelled": 0,
            "finished": 0
        }
    
    def get_feature_name(self) -> str:
        return "timer"
    
    def start(
        self,
        timer_id: str,
        duration: str,
        ha_config: Dict[str, Any],
        friendly_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Start a timer."""
        start_time = time.time()
        correlation_id = generate_correlation_id()
        
        try:
            log_info(f"Starting timer {timer_id} for {duration} [{correlation_id}]")
            increment_counter("ha_timer_start_request")
            
            duration_seconds = parse_duration_string(duration)
            if duration_seconds is None:
                return create_error_response("Invalid duration format", {"duration": duration})
            
            entity_id = f"timer.{timer_id}" if not timer_id.startswith("timer.") else timer_id
            duration_str = format_duration_seconds(duration_seconds)
            
            service_data = {"duration": duration_str}
            if friendly_name:
                service_data["friendly_name"] = friendly_name
            
            result = call_ha_service_generic(ha_config, "timer", "start", entity_id, service_data)
            
            duration_ms = (time.time() - start_time) * 1000
            success = result.get("success", False)
            
            self._stats.record(success, duration_ms)
            self._record_metric("start", success)
            
            if success:
                self._operation_counts["started"] += 1
                log_info(f"Timer started: {entity_id} [{correlation_id}]")
                return create_success_response(
                    f"Timer {timer_id} started for {duration}",
                    {
                        "entity_id": entity_id,
                        "duration": duration_str,
                        "duration_seconds": duration_seconds,
                        "processing_time_ms": duration_ms,
                        "correlation_id": correlation_id
                    }
                )
            else:
                return create_error_response("Failed to start timer", {"result": result})
                
        except Exception as e:
            log_error(f"Timer start exception: {str(e)}")
            self._stats.record(False)
            self._record_metric("start", False)
            return create_error_response("Timer start exception", {"error": str(e)})
    
    def pause(self, timer_id: str, ha_config: Dict[str, Any]) -> Dict[str, Any]:
        """Pause a timer."""
        return self._timer_action(timer_id, "pause", ha_config)
    
    def cancel(self, timer_id: str, ha_config: Dict[str, Any]) -> Dict[str, Any]:
        """Cancel a timer."""
        return self._timer_action(timer_id, "cancel", ha_config)
    
    def finish(self, timer_id: str, ha_config: Dict[str, Any]) -> Dict[str, Any]:
        """Finish a timer immediately."""
        return self._timer_action(timer_id, "finish", ha_config)
    
    def _timer_action(
        self,
        timer_id: str,
        action: str,
        ha_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute timer action."""
        try:
            increment_counter(f"ha_timer_{action}_request")
            
            entity_id = f"timer.{timer_id}" if not timer_id.startswith("timer.") else timer_id
            
            result = call_ha_service_generic(ha_config, "timer", action, entity_id)
            
            success = result.get("success", False)
            self._stats.record(success)
            self._record_metric(action, success)
            
            if success:
                self._operation_counts[f"{action}d" if action.endswith("e") else f"{action}ed"] += 1
                return create_success_response(
                    f"Timer {action}ed",
                    {"entity_id": entity_id, "action": action}
                )
            else:
                return create_error_response(f"Failed to {action} timer", {"result": result})
                
        except Exception as e:
            log_error(f"Timer {action} exception: {str(e)}")
            self._stats.record(False)
            self._record_metric(action, False)
            return create_error_response(f"Timer {action} exception", {"error": str(e)})
    
    def get_status(self, timer_id: str, ha_config: Dict[str, Any]) -> Dict[str, Any]:
        """Get timer status."""
        try:
            entity_id = f"timer.{timer_id}" if not timer_id.startswith("timer.") else timer_id
            return get_entity_state(ha_config, entity_id)
            
        except Exception as e:
            log_error(f"Get timer status exception: {str(e)}")
            return create_error_response("Get timer status exception", {"error": str(e)})
    
    def get_stats(self) -> Dict[str, Any]:
        """Get timer statistics."""
        base_stats = super().get_stats()
        base_stats.update(self._operation_counts)
        return base_stats


_manager_singleton = SingletonManager(HATimerManager)


def start_timer(
    timer_id: str,
    duration: str,
    ha_config: Dict[str, Any],
    friendly_name: Optional[str] = None
) -> Dict[str, Any]:
    """Start timer."""
    return _manager_singleton.get().start(timer_id, duration, ha_config, friendly_name)


def pause_timer(timer_id: str, ha_config: Dict[str, Any]) -> Dict[str, Any]:
    """Pause timer."""
    return _manager_singleton.get().pause(timer_id, ha_config)


def cancel_timer(timer_id: str, ha_config: Dict[str, Any]) -> Dict[str, Any]:
    """Cancel timer."""
    return _manager_singleton.get().cancel(timer_id, ha_config)


def finish_timer(timer_id: str, ha_config: Dict[str, Any]) -> Dict[str, Any]:
    """Finish timer."""
    return _manager_singleton.get().finish(timer_id, ha_config)


def get_timer_status(timer_id: str, ha_config: Dict[str, Any]) -> Dict[str, Any]:
    """Get timer status."""
    return _manager_singleton.get().get_status(timer_id, ha_config)


def get_timer_stats() -> Dict[str, Any]:
    """Get timer statistics."""
    return _manager_singleton.get().get_stats()


__all__ = [
    'start_timer',
    'pause_timer',
    'cancel_timer',
    'finish_timer',
    'get_timer_status',
    'get_timer_stats'
]
