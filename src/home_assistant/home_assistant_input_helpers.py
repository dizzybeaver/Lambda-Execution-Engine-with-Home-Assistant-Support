"""
home_assistant_input_helpers.py - Input Helper Management
Version: 2025.09.30.06
Daily Revision: Performance Optimization Phase 1

Home Assistant input helper management via voice commands

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
    parse_boolean_value,
    SingletonManager
)


class HAInputHelperManager(HABaseManager):
    """Manages Home Assistant input helper operations."""
    
    def __init__(self):
        super().__init__()
        self._type_stats = {}
    
    def get_feature_name(self) -> str:
        return "input_helper"
    
    def set_helper(
        self,
        helper_id: str,
        value: Any,
        ha_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Set input helper value."""
        start_time = time.time()
        correlation_id = generate_correlation_id()
        
        try:
            log_info(f"Setting input helper: {helper_id} = {value} [{correlation_id}]")
            increment_counter("ha_input_helper_set_request")
            
            entity_id = self._resolve_helper(helper_id, ha_config)
            if not entity_id:
                self.record_failure()
                return create_error_response("Input helper not found", {"helper_id": helper_id})
            
            helper_type = entity_id.split(".")[0]
            service = self._get_service_for_type(helper_type, value)
            service_data = self._prepare_service_data(helper_type, value)
            
            result = call_ha_service(helper_type, service, ha_config, entity_id, service_data)
            
            duration_ms = (time.time() - start_time) * 1000
            
            if result.get("success", False):
                self.record_success()
                self._record_type_stat(helper_type, True)
                log_info(f"Input helper set: {entity_id} [{correlation_id}]")
                return create_success_response(
                    f"Input helper {helper_id} set to {value}",
                    {
                        "entity_id": entity_id,
                        "type": helper_type,
                        "value": value,
                        "processing_time_ms": duration_ms,
                        "correlation_id": correlation_id
                    }
                )
            else:
                self.record_failure()
                self._record_type_stat(helper_type, False)
                return create_error_response("Failed to set input helper", {"result": result})
                
        except Exception as e:
            self.record_failure()
            log_error(f"Set input helper exception: {str(e)}")
            return create_error_response("Set input helper exception", {"error": str(e)})
    
    def _resolve_helper(self, helper_id: str, ha_config: Dict[str, Any]) -> str:
        """Resolve input helper ID."""
        if helper_id.startswith("input_"):
            return helper_id
        
        for domain in ["input_boolean", "input_select", "input_number", "input_text"]:
            entity_id = resolve_entity_id(helper_id, domain, ha_config)
            if entity_id:
                return entity_id
        
        return None
    
    def _get_service_for_type(self, helper_type: str, value: Any) -> str:
        """Get service name for helper type."""
        if helper_type == "input_boolean":
            return "turn_on" if parse_boolean_value(value) else "turn_off"
        elif helper_type == "input_select":
            return "select_option"
        elif helper_type == "input_number":
            return "set_value"
        elif helper_type == "input_text":
            return "set_value"
        return "turn_on"
    
    def _prepare_service_data(self, helper_type: str, value: Any) -> Dict[str, Any]:
        """Prepare service data for helper type."""
        if helper_type == "input_boolean":
            return None
        elif helper_type == "input_select":
            return {"option": str(value)}
        elif helper_type == "input_number":
            return {"value": float(value)}
        elif helper_type == "input_text":
            return {"value": str(value)}
        return None
    
    def _record_type_stat(self, helper_type: str, success: bool):
        """Record statistics by type."""
        if helper_type not in self._type_stats:
            self._type_stats[helper_type] = {"success": 0, "failure": 0}
        
        if success:
            self._type_stats[helper_type]["success"] += 1
        else:
            self._type_stats[helper_type]["failure"] += 1


def set_input_helper(
    helper_id: str,
    value: Any,
    ha_config: Dict[str, Any]
) -> Dict[str, Any]:
    """Set input helper value."""
    manager = SingletonManager.get_instance(HAInputHelperManager)
    return manager.set_helper(helper_id, value, ha_config)


def get_input_helper_stats() -> Dict[str, Any]:
    """Get input helper statistics."""
    manager = SingletonManager.get_instance(HAInputHelperManager)
    stats = manager.get_stats()
    stats["by_type"] = manager._type_stats
    return stats


__all__ = ["set_input_helper", "get_input_helper_stats"]
