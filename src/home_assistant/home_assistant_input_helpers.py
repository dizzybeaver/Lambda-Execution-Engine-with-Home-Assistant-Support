"""
home_assistant_input_helpers.py - Input Helper Management
Version: 2025.09.30.05
Daily Revision: Ultra-Optimized

Home Assistant input helper management via voice commands

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
    log_info, log_error, log_warning,
    create_success_response, create_error_response,
    generate_correlation_id,
    increment_counter
)

from ha_common import (
    HABaseManager,
    resolve_entity_id,
    call_ha_service_generic,
    get_entity_state,
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
                return create_error_response("Input helper not found", {"helper_id": helper_id})
            
            helper_type = entity_id.split(".")[0]
            result = self._set_by_type(entity_id, helper_type, value, ha_config)
            
            duration_ms = (time.time() - start_time) * 1000
            success = result.get("success", False)
            
            self._stats.record(success, duration_ms)
            self._record_metric("set", success)
            self._update_type_stats(helper_type)
            
            if success:
                log_info(f"Input helper set: {entity_id} [{correlation_id}]")
                return create_success_response(
                    f"Input helper {helper_id} set to {value}",
                    {
                        "entity_id": entity_id,
                        "value": value,
                        "processing_time_ms": duration_ms,
                        "correlation_id": correlation_id
                    }
                )
            else:
                return create_error_response("Failed to set input helper", {"result": result})
                
        except Exception as e:
            log_error(f"Input helper set exception: {str(e)}")
            self._stats.record(False)
            self._record_metric("set", False)
            return create_error_response("Input helper set exception", {"error": str(e)})
    
    def _resolve_helper(self, helper_id: str, ha_config: Dict[str, Any]) -> Optional[str]:
        """Resolve helper ID across all input types."""
        if "." in helper_id:
            prefix = helper_id.split(".")[0]
            if prefix in ["input_boolean", "input_select", "input_number", "input_text"]:
                return helper_id
        
        for domain in ["input_boolean", "input_select", "input_number", "input_text"]:
            entity_id = resolve_entity_id(helper_id, ha_config, domain, f"input_helpers_{domain}")
            if entity_id:
                return entity_id
        
        return None
    
    def _set_by_type(
        self,
        entity_id: str,
        helper_type: str,
        value: Any,
        ha_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Set helper value based on type."""
        if helper_type == "input_boolean":
            service = "turn_on" if parse_boolean_value(value) else "turn_off"
            return call_ha_service_generic(ha_config, "input_boolean", service, entity_id)
        
        elif helper_type == "input_select":
            return call_ha_service_generic(
                ha_config, "input_select", "select_option",
                entity_id, {"option": str(value)}
            )
        
        elif helper_type == "input_number":
            return call_ha_service_generic(
                ha_config, "input_number", "set_value",
                entity_id, {"value": float(value)}
            )
        
        elif helper_type == "input_text":
            return call_ha_service_generic(
                ha_config, "input_text", "set_value",
                entity_id, {"value": str(value)}
            )
        
        return {"success": False, "error": "Unknown helper type"}
    
    def get_helper_value(
        self,
        helper_id: str,
        ha_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Get input helper value."""
        try:
            entity_id = self._resolve_helper(helper_id, ha_config)
            if not entity_id:
                return create_error_response("Helper not found", {"helper_id": helper_id})
            
            return get_entity_state(ha_config, entity_id)
            
        except Exception as e:
            log_error(f"Get helper value exception: {str(e)}")
            return create_error_response("Get helper value exception", {"error": str(e)})
    
    def _update_type_stats(self, helper_type: str):
        """Update statistics by type."""
        self._type_stats[helper_type] = self._type_stats.get(helper_type, 0) + 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Get input helper statistics."""
        base_stats = super().get_stats()
        base_stats["by_type"] = self._type_stats
        return base_stats


_manager_singleton = SingletonManager(HAInputHelperManager)


def set_input_helper(
    helper_id: str,
    value: Any,
    ha_config: Dict[str, Any]
) -> Dict[str, Any]:
    """Set input helper value."""
    return _manager_singleton.get().set_helper(helper_id, value, ha_config)


def get_input_helper_value(
    helper_id: str,
    ha_config: Dict[str, Any]
) -> Dict[str, Any]:
    """Get input helper value."""
    return _manager_singleton.get().get_helper_value(helper_id, ha_config)


def get_input_helper_stats() -> Dict[str, Any]:
    """Get input helper statistics."""
    return _manager_singleton.get().get_stats()


__all__ = ['set_input_helper', 'get_input_helper_value', 'get_input_helper_stats']
