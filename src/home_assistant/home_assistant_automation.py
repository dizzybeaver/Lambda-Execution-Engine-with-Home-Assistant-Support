"""
home_assistant_automation.py - Automation Triggering
Version: 2025.09.30.04
Daily Revision: 001

Home Assistant automation triggering via voice commands
Allows Alexa to trigger HA automations by entity_id or friendly name

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
class AutomationStats:
    """Statistics for automation triggering."""
    total_triggers: int = 0
    successful_triggers: int = 0
    failed_triggers: int = 0
    avg_response_time_ms: float = 0.0
    last_trigger_time: float = 0.0


class HAAutomationManager:
    """Manages Home Assistant automation triggering."""
    
    def __init__(self):
        self._stats = AutomationStats()
        self._initialized_time = time.time()
    
    def trigger_automation(self,
                          automation_id: str,
                          ha_config: Dict[str, Any],
                          skip_condition: bool = False) -> Dict[str, Any]:
        """
        Trigger Home Assistant automation.
        
        Args:
            automation_id: Automation entity_id or friendly name
            ha_config: HA configuration dict
            skip_condition: Whether to skip automation conditions
            
        Returns:
            Result dict with success status
        """
        start_time = time.time()
        correlation_id = generate_correlation_id()
        
        try:
            log_info(f"Triggering automation: {automation_id} [{correlation_id}]")
            increment_counter("ha_automation_trigger_request")
            
            # Validate automation exists
            entity_id = self._resolve_automation_id(automation_id, ha_config)
            if not entity_id:
                log_warning(f"Automation not found: {automation_id}")
                return create_error_response(
                    "Automation not found",
                    {"automation_id": automation_id}
                )
            
            # Trigger automation
            url = f"{ha_config['base_url']}/api/services/automation/trigger"
            headers = {
                "Authorization": f"Bearer {ha_config['access_token']}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "entity_id": entity_id
            }
            
            if skip_condition:
                payload["skip_condition"] = True
            
            result = make_post_request(
                url=url,
                headers=headers,
                json_data=payload,
                timeout=ha_config.get('timeout', 30)
            )
            
            processing_time = (time.time() - start_time) * 1000
            
            if result.get("success", False):
                log_info(f"Automation triggered successfully: {entity_id} [{correlation_id}]")
                record_metric("ha_automation_trigger_success", 1.0)
                self._update_stats(True, processing_time)
                
                return create_success_response(
                    f"Automation {automation_id} triggered successfully",
                    {
                        "entity_id": entity_id,
                        "processing_time_ms": processing_time,
                        "correlation_id": correlation_id
                    }
                )
            else:
                log_error(f"Automation trigger failed: {result}")
                self._update_stats(False, processing_time)
                return create_error_response(
                    "Failed to trigger automation",
                    {"result": result}
                )
                
        except Exception as e:
            log_error(f"Automation trigger exception: {str(e)}")
            record_metric("ha_automation_trigger_error", 1.0)
            processing_time = (time.time() - start_time) * 1000
            self._update_stats(False, processing_time)
            return create_error_response(
                "Automation trigger exception",
                {"error": str(e)}
            )
    
    def list_automations(self, ha_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        List all available automations.
        
        Args:
            ha_config: HA configuration dict
            
        Returns:
            List of automation entities
        """
        try:
            correlation_id = generate_correlation_id()
            log_debug(f"Listing automations [{correlation_id}]")
            
            # Check cache first
            cache_key = "ha_automation_list"
            cached = cache_get(cache_key)
            if cached:
                log_debug("Returning cached automation list")
                return cached
            
            # Fetch from HA
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
                return create_error_response("Failed to list automations", {"result": result})
            
            # Filter automation entities
            states = result.get("data", [])
            automations = [
                {
                    "entity_id": state.get("entity_id"),
                    "friendly_name": state.get("attributes", {}).get("friendly_name", ""),
                    "state": state.get("state")
                }
                for state in states
                if state.get("entity_id", "").startswith("automation.")
            ]
            
            response = create_success_response(
                "Automations listed successfully",
                {"automations": automations, "count": len(automations)}
            )
            
            # Cache for 5 minutes
            cache_set(cache_key, response, ttl=300)
            
            return response
            
        except Exception as e:
            log_error(f"List automations exception: {str(e)}")
            return create_error_response("List automations exception", {"error": str(e)})
    
    def _resolve_automation_id(self,
                               automation_id: str,
                               ha_config: Dict[str, Any]) -> Optional[str]:
        """
        Resolve automation friendly name to entity_id.
        
        Args:
            automation_id: Entity ID or friendly name
            ha_config: HA configuration
            
        Returns:
            Entity ID or None if not found
        """
        # If already entity_id format
        if automation_id.startswith("automation."):
            return automation_id
        
        # Try to find by friendly name
        automations_result = self.list_automations(ha_config)
        if not automations_result.get("success", False):
            return None
        
        automations = automations_result.get("data", {}).get("automations", [])
        
        # Case-insensitive search
        automation_id_lower = automation_id.lower()
        for automation in automations:
            friendly_name = automation.get("friendly_name", "").lower()
            if friendly_name == automation_id_lower:
                return automation["entity_id"]
            
            # Try partial match
            if automation_id_lower in friendly_name:
                return automation["entity_id"]
        
        # If not found, assume it's entity_id without prefix
        return f"automation.{automation_id}"
    
    def _update_stats(self, success: bool, processing_time_ms: float) -> None:
        """Update automation statistics."""
        self._stats.total_triggers += 1
        self._stats.last_trigger_time = time.time()
        
        if success:
            self._stats.successful_triggers += 1
        else:
            self._stats.failed_triggers += 1
        
        if self._stats.total_triggers > 0:
            current_avg = self._stats.avg_response_time_ms
            new_avg = ((current_avg * (self._stats.total_triggers - 1)) + 
                      processing_time_ms) / self._stats.total_triggers
            self._stats.avg_response_time_ms = new_avg
    
    def get_stats(self) -> Dict[str, Any]:
        """Get automation triggering statistics."""
        return {
            "total_triggers": self._stats.total_triggers,
            "successful_triggers": self._stats.successful_triggers,
            "failed_triggers": self._stats.failed_triggers,
            "success_rate": (self._stats.successful_triggers / self._stats.total_triggers * 100
                           if self._stats.total_triggers > 0 else 0.0),
            "avg_response_time_ms": self._stats.avg_response_time_ms,
            "last_trigger_time": self._stats.last_trigger_time,
            "uptime_seconds": time.time() - self._initialized_time
        }


# Singleton instance
_automation_manager: Optional[HAAutomationManager] = None


def _get_automation_manager() -> HAAutomationManager:
    """Get or create automation manager singleton."""
    global _automation_manager
    if _automation_manager is None:
        _automation_manager = HAAutomationManager()
    return _automation_manager


# Public interface functions
def trigger_automation(automation_id: str,
                      ha_config: Dict[str, Any],
                      skip_condition: bool = False) -> Dict[str, Any]:
    """Trigger Home Assistant automation."""
    manager = _get_automation_manager()
    return manager.trigger_automation(automation_id, ha_config, skip_condition)


def list_automations(ha_config: Dict[str, Any]) -> Dict[str, Any]:
    """List available automations."""
    manager = _get_automation_manager()
    return manager.list_automations(ha_config)


def get_automation_stats() -> Dict[str, Any]:
    """Get automation manager statistics."""
    manager = _get_automation_manager()
    return manager.get_stats()


__all__ = [
    'trigger_automation',
    'list_automations',
    'get_automation_stats',
]

#EOF
