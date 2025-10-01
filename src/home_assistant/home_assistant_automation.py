"""
home_assistant_automation.py - Automation Triggering
Version: 2025.09.30.06
Daily Revision: Performance Optimization Phase 1

Home Assistant automation triggering via voice commands

ARCHITECTURE: HOME ASSISTANT EXTENSION MODULE
- Uses ha_common for shared functionality
- Lazy loading compatible
- 100% Free Tier AWS compliant

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
    SingletonManager
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
            
            entity_id = resolve_entity_id(automation_id, "automation", ha_config)
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


def trigger_automation(
    automation_id: str,
    ha_config: Dict[str, Any],
    skip_condition: bool = False
) -> Dict[str, Any]:
    """Trigger automation."""
    manager = SingletonManager.get_instance(HAAutomationManager)
    return manager.trigger(automation_id, ha_config, skip_condition)


def get_automation_stats() -> Dict[str, Any]:
    """Get automation statistics."""
    manager = SingletonManager.get_instance(HAAutomationManager)
    return manager.get_stats()


__all__ = ["trigger_automation", "get_automation_stats"]
