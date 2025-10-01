"""
home_assistant_automation.py - Automation Triggering
Version: 2025.09.30.05
Daily Revision: Ultra-Optimized

Home Assistant automation triggering via voice commands

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
    resolve_entity_id,
    call_ha_service_generic,
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
            
            entity_id = resolve_entity_id(automation_id, ha_config, "automation", "automations")
            if not entity_id:
                return create_error_response("Automation not found", {"automation_id": automation_id})
            
            service_data = {"skip_condition": True} if skip_condition else None
            result = call_ha_service_generic(ha_config, "automation", "trigger", entity_id, service_data)
            
            duration_ms = (time.time() - start_time) * 1000
            success = result.get("success", False)
            
            self._stats.record(success, duration_ms)
            self._record_metric("trigger", success)
            
            if success:
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
                return create_error_response("Failed to trigger automation", {"result": result})
                
        except Exception as e:
            log_error(f"Automation trigger exception: {str(e)}")
            self._stats.record(False)
            self._record_metric("trigger", False)
            return create_error_response("Automation trigger exception", {"error": str(e)})


_manager_singleton = SingletonManager(HAAutomationManager)


def trigger_automation(
    automation_id: str,
    ha_config: Dict[str, Any],
    skip_condition: bool = False
) -> Dict[str, Any]:
    """Trigger automation."""
    return _manager_singleton.get().trigger(automation_id, ha_config, skip_condition)


def get_automation_stats() -> Dict[str, Any]:
    """Get automation statistics."""
    return _manager_singleton.get().get_stats()


__all__ = ['trigger_automation', 'get_automation_stats']
