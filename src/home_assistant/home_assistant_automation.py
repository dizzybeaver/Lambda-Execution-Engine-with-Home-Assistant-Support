"""
home_assistant_automation.py - Automation Triggering
Version: 2025.09.30.07
Daily Revision: Performance Optimization Phase 2

Phase 2: Consolidated cache + entity minimization

Licensed under the Apache License, Version 2.0
"""

import time
from typing import Dict, Any

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


class HAAutomationManager(HABaseManager):
    """Manages Home Assistant automation triggering."""
    
    def get_feature_name(self) -> str:
        return "automation"
    
    def trigger(
        self,
        automation_id: str,
        ha_config: Dict[str, Any],
        skip_condition: bool = False
    ) -> Dict[str, Any]:
        """Trigger automation by ID or name."""
        start_time = time.time()
        correlation_id = generate_correlation_id()
        
        try:
            log_info(f"Triggering automation: {automation_id} [{correlation_id}]")
            increment_counter("ha_automation_trigger_request")
            
            entity_id = automation_id if "." in automation_id else resolve_entity_id(automation_id, "automation", ha_config)
            if not entity_id:
                self.record_failure()
                return create_error_response("Automation not found", {"automation_id": automation_id})
            
            service_data = {"skip_condition": skip_condition} if skip_condition else None
            result = call_ha_service("automation", "trigger", ha_config, entity_id, service_data)
            
            duration_ms = (time.time() - start_time) * 1000
            
            if result.get("success", False):
                self.record_success()
                log_info(f"Automation triggered: {entity_id} [{correlation_id}]")
                return create_success_response(
                    f"Automation {automation_id} triggered",
                    {
                        "entity_id": entity_id,
                        "processing_time_ms": duration_ms,
                        "correlation_id": correlation_id
                    }
                )
            else:
                self.record_failure()
                return create_error_response("Failed to trigger automation", {"result": result})
                
        except Exception as e:
            self.record_failure()
            log_error(f"Automation trigger exception: {str(e)}")
            return create_error_response("Automation trigger exception", {"error": str(e)})
    
    def list(self, ha_config: Dict[str, Any]) -> Dict[str, Any]:
        """List all automations with consolidated cache."""
        try:
            cached = get_cache_section("automations", ttl=300)
            if cached:
                self.record_cache_hit()
                return create_success_response("Automations retrieved from cache", {"automations": cached})
            
            self.record_cache_miss()
            from ha_common import call_ha_api
            response = call_ha_api("/api/states", ha_config)
            
            if not isinstance(response, list):
                return create_error_response("Invalid API response", {})
            
            automations = [e for e in response if e.get("entity_id", "").startswith("automation.")]
            minimized = minimize_entity_list(automations)
            
            set_cache_section("automations", minimized, ttl=300)
            
            return create_success_response("Automations retrieved", {"automations": minimized})
            
        except Exception as e:
            log_error(f"List automations exception: {str(e)}")
            return create_error_response("List automations exception", {"error": str(e)})


def trigger_automation(
    automation_id: str,
    ha_config: Dict[str, Any],
    skip_condition: bool = False
) -> Dict[str, Any]:
    """Trigger automation."""
    manager = SingletonManager.get_instance(HAAutomationManager)
    return manager.trigger(automation_id, ha_config, skip_condition)


def list_automations(ha_config: Dict[str, Any]) -> Dict[str, Any]:
    """List all automations."""
    manager = SingletonManager.get_instance(HAAutomationManager)
    return manager.list(ha_config)


def get_automation_stats() -> Dict[str, Any]:
    """Get automation statistics."""
    manager = SingletonManager.get_instance(HAAutomationManager)
    return manager.get_stats()


__all__ = ["trigger_automation", "list_automations", "get_automation_stats"]
