"""
home_assistant_input_helpers.py - Input Helper Management
Version: 2025.09.30.04
Daily Revision: 001

Home Assistant input helper management via voice commands
Supports input_boolean, input_select, input_number, input_text

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
class InputHelperStats:
    """Statistics for input helper operations."""
    total_operations: int = 0
    successful_operations: int = 0
    failed_operations: int = 0
    by_type: Dict[str, int] = None
    
    def __post_init__(self):
        if self.by_type is None:
            self.by_type = {}


class HAInputHelperManager:
    """Manages Home Assistant input helper operations."""
    
    def __init__(self):
        self._stats = InputHelperStats()
        self._initialized_time = time.time()
    
    def set_input_helper(self,
                        helper_id: str,
                        value: Any,
                        ha_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Set input helper value.
        
        Args:
            helper_id: Helper entity_id or friendly name
            value: Value to set
            ha_config: HA configuration dict
            
        Returns:
            Result dict with success status
        """
        start_time = time.time()
        correlation_id = generate_correlation_id()
        
        try:
            log_info(f"Setting input helper: {helper_id} = {value} [{correlation_id}]")
            increment_counter("ha_input_helper_set_request")
            
            entity_id = self._resolve_helper_id(helper_id, ha_config)
            if not entity_id:
                log_warning(f"Input helper not found: {helper_id}")
                return create_error_response(
                    "Input helper not found",
                    {"helper_id": helper_id}
                )
            
            helper_type = entity_id.split(".")[0]
            result = self._set_helper_by_type(entity_id, helper_type, value, ha_config)
            
            processing_time = (time.time() - start_time) * 1000
            
            if result.get("success", False):
                log_info(f"Input helper set successfully: {entity_id} [{correlation_id}]")
                record_metric("ha_input_helper_set_success", 1.0)
                self._update_stats(True, helper_type)
                
                return create_success_response(
                    f"Input helper {helper_id} set to {value}",
                    {
                        "entity_id": entity_id,
                        "value": value,
                        "processing_time_ms": processing_time,
                        "correlation_id": correlation_id
                    }
                )
            else:
                log_error(f"Input helper set failed: {result}")
                self._update_stats(False, helper_type)
                return create_error_response(
                    "Failed to set input helper",
                    {"result": result}
                )
                
        except Exception as e:
            log_error(f"Input helper set exception: {str(e)}")
            record_metric("ha_input_helper_set_error", 1.0)
            self._update_stats(False, "unknown")
            return create_error_response(
                "Input helper set exception",
                {"error": str(e)}
            )
    
    def _set_helper_by_type(self,
                           entity_id: str,
                           helper_type: str,
                           value: Any,
                           ha_config: Dict[str, Any]) -> Dict[str, Any]:
        """Set helper value based on type."""
        headers = {
            "Authorization": f"Bearer {ha_config['access_token']}",
            "Content-Type": "application/json"
        }
        
        if helper_type == "input_boolean":
            service = "turn_on" if self._parse_boolean(value) else "turn_off"
            url = f"{ha_config['base_url']}/api/services/input_boolean/{service}"
            payload = {"entity_id": entity_id}
            
        elif helper_type == "input_select":
            url = f"{ha_config['base_url']}/api/services/input_select/select_option"
            payload = {
                "entity_id": entity_id,
                "option": str(value)
            }
            
        elif helper_type == "input_number":
            url = f"{ha_config['base_url']}/api/services/input_number/set_value"
            payload = {
                "entity_id": entity_id,
                "value": float(value)
            }
            
        elif helper_type == "input_text":
            url = f"{ha_config['base_url']}/api/services/input_text/set_value"
            payload = {
                "entity_id": entity_id,
                "value": str(value)
            }
            
        else:
            return create_error_response(
                "Unsupported input helper type",
                {"helper_type": helper_type}
            )
        
        return make_post_request(
            url=url,
            headers=headers,
            json_data=payload,
            timeout=ha_config.get('timeout', 30)
        )
    
    def get_input_helper_value(self,
                              helper_id: str,
                              ha_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get input helper current value.
        
        Args:
            helper_id: Helper entity_id
            ha_config: HA configuration dict
            
        Returns:
            Current value
        """
        try:
            entity_id = self._resolve_helper_id(helper_id, ha_config)
            if not entity_id:
                return create_error_response("Helper not found", {"helper_id": helper_id})
            
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
                    "Helper value retrieved",
                    {
                        "entity_id": entity_id,
                        "value": state_data.get("state"),
                        "attributes": state_data.get("attributes", {})
                    }
                )
            else:
                return create_error_response("Failed to get helper value", {"result": result})
                
        except Exception as e:
            log_error(f"Get helper value exception: {str(e)}")
            return create_error_response("Get helper value exception", {"error": str(e)})
    
    def list_input_helpers(self,
                          ha_config: Dict[str, Any],
                          helper_type: Optional[str] = None) -> Dict[str, Any]:
        """
        List input helpers.
        
        Args:
            ha_config: HA configuration dict
            helper_type: Optional filter by type
            
        Returns:
            List of input helpers
        """
        try:
            correlation_id = generate_correlation_id()
            log_debug(f"Listing input helpers [{correlation_id}]")
            
            cache_key = f"ha_input_helper_list_{helper_type or 'all'}"
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
                return create_error_response("Failed to list helpers", {"result": result})
            
            states = result.get("data", [])
            
            valid_types = ["input_boolean", "input_select", "input_number", "input_text"]
            
            helpers = [
                {
                    "entity_id": state.get("entity_id"),
                    "friendly_name": state.get("attributes", {}).get("friendly_name", ""),
                    "state": state.get("state"),
                    "type": state.get("entity_id", "").split(".")[0]
                }
                for state in states
                if state.get("entity_id", "").split(".")[0] in valid_types
                and (helper_type is None or state.get("entity_id", "").startswith(f"{helper_type}."))
            ]
            
            response = create_success_response(
                "Input helpers listed successfully",
                {"helpers": helpers, "count": len(helpers)}
            )
            
            cache_set(cache_key, response, ttl=300)
            
            return response
            
        except Exception as e:
            log_error(f"List input helpers exception: {str(e)}")
            return create_error_response("List input helpers exception", {"error": str(e)})
    
    def _resolve_helper_id(self,
                          helper_id: str,
                          ha_config: Dict[str, Any]) -> Optional[str]:
        """Resolve helper friendly name to entity_id."""
        if "." in helper_id and helper_id.split(".")[0] in ["input_boolean", "input_select", "input_number", "input_text"]:
            return helper_id
        
        helpers_result = self.list_input_helpers(ha_config)
        if not helpers_result.get("success", False):
            return None
        
        helpers = helpers_result.get("data", {}).get("helpers", [])
        
        helper_id_lower = helper_id.lower()
        for helper in helpers:
            friendly_name = helper.get("friendly_name", "").lower()
            if friendly_name == helper_id_lower or helper_id_lower in friendly_name:
                return helper["entity_id"]
        
        return None
    
    def _parse_boolean(self, value: Any) -> bool:
        """Parse value as boolean."""
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ["true", "on", "yes", "1", "enabled"]
        return bool(value)
    
    def _update_stats(self, success: bool, helper_type: str) -> None:
        """Update input helper statistics."""
        self._stats.total_operations += 1
        
        if success:
            self._stats.successful_operations += 1
        else:
            self._stats.failed_operations += 1
        
        if helper_type not in self._stats.by_type:
            self._stats.by_type[helper_type] = 0
        self._stats.by_type[helper_type] += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Get input helper statistics."""
        return {
            "total_operations": self._stats.total_operations,
            "successful_operations": self._stats.successful_operations,
            "failed_operations": self._stats.failed_operations,
            "success_rate": (self._stats.successful_operations / self._stats.total_operations * 100
                           if self._stats.total_operations > 0 else 0.0),
            "by_type": self._stats.by_type,
            "uptime_seconds": time.time() - self._initialized_time
        }


_input_helper_manager: Optional[HAInputHelperManager] = None


def _get_input_helper_manager() -> HAInputHelperManager:
    """Get or create input helper manager singleton."""
    global _input_helper_manager
    if _input_helper_manager is None:
        _input_helper_manager = HAInputHelperManager()
    return _input_helper_manager


def set_input_helper(helper_id: str, value: Any, ha_config: Dict[str, Any]) -> Dict[str, Any]:
    """Set input helper value."""
    manager = _get_input_helper_manager()
    return manager.set_input_helper(helper_id, value, ha_config)


def get_input_helper_value(helper_id: str, ha_config: Dict[str, Any]) -> Dict[str, Any]:
    """Get input helper value."""
    manager = _get_input_helper_manager()
    return manager.get_input_helper_value(helper_id, ha_config)


def list_input_helpers(ha_config: Dict[str, Any], helper_type: Optional[str] = None) -> Dict[str, Any]:
    """List input helpers."""
    manager = _get_input_helper_manager()
    return manager.list_input_helpers(ha_config, helper_type)


def get_input_helper_stats() -> Dict[str, Any]:
    """Get input helper statistics."""
    manager = _get_input_helper_manager()
    return manager.get_stats()


__all__ = [
    'set_input_helper',
    'get_input_helper_value',
    'list_input_helpers',
    'get_input_helper_stats',
]

#EOF
