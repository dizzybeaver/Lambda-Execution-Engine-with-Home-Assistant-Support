"""
home_assistant_scripts.py - Script Execution
Version: 2025.09.30.04
Daily Revision: 001

Home Assistant script execution via voice commands
Allows Alexa to run HA scripts by entity_id or friendly name

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
class ScriptStats:
    """Statistics for script execution."""
    total_executions: int = 0
    successful_executions: int = 0
    failed_executions: int = 0
    avg_response_time_ms: float = 0.0
    last_execution_time: float = 0.0


class HAScriptManager:
    """Manages Home Assistant script execution."""
    
    def __init__(self):
        self._stats = ScriptStats()
        self._initialized_time = time.time()
    
    def execute_script(self,
                      script_id: str,
                      ha_config: Dict[str, Any],
                      script_variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute Home Assistant script.
        
        Args:
            script_id: Script entity_id or friendly name
            ha_config: HA configuration dict
            script_variables: Optional variables to pass to script
            
        Returns:
            Result dict with success status
        """
        start_time = time.time()
        correlation_id = generate_correlation_id()
        
        try:
            log_info(f"Executing script: {script_id} [{correlation_id}]")
            increment_counter("ha_script_execution_request")
            
            entity_id = self._resolve_script_id(script_id, ha_config)
            if not entity_id:
                log_warning(f"Script not found: {script_id}")
                return create_error_response(
                    "Script not found",
                    {"script_id": script_id}
                )
            
            url = f"{ha_config['base_url']}/api/services/script/turn_on"
            headers = {
                "Authorization": f"Bearer {ha_config['access_token']}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "entity_id": entity_id
            }
            
            if script_variables:
                payload["variables"] = script_variables
            
            result = make_post_request(
                url=url,
                headers=headers,
                json_data=payload,
                timeout=ha_config.get('timeout', 30)
            )
            
            processing_time = (time.time() - start_time) * 1000
            
            if result.get("success", False):
                log_info(f"Script executed successfully: {entity_id} [{correlation_id}]")
                record_metric("ha_script_execution_success", 1.0)
                self._update_stats(True, processing_time)
                
                return create_success_response(
                    f"Script {script_id} executed successfully",
                    {
                        "entity_id": entity_id,
                        "processing_time_ms": processing_time,
                        "correlation_id": correlation_id
                    }
                )
            else:
                log_error(f"Script execution failed: {result}")
                self._update_stats(False, processing_time)
                return create_error_response(
                    "Failed to execute script",
                    {"result": result}
                )
                
        except Exception as e:
            log_error(f"Script execution exception: {str(e)}")
            record_metric("ha_script_execution_error", 1.0)
            processing_time = (time.time() - start_time) * 1000
            self._update_stats(False, processing_time)
            return create_error_response(
                "Script execution exception",
                {"error": str(e)}
            )
    
    def list_scripts(self, ha_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        List all available scripts.
        
        Args:
            ha_config: HA configuration dict
            
        Returns:
            List of script entities
        """
        try:
            correlation_id = generate_correlation_id()
            log_debug(f"Listing scripts [{correlation_id}]")
            
            cache_key = "ha_script_list"
            cached = cache_get(cache_key)
            if cached:
                log_debug("Returning cached script list")
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
                return create_error_response("Failed to list scripts", {"result": result})
            
            states = result.get("data", [])
            scripts = [
                {
                    "entity_id": state.get("entity_id"),
                    "friendly_name": state.get("attributes", {}).get("friendly_name", ""),
                    "state": state.get("state")
                }
                for state in states
                if state.get("entity_id", "").startswith("script.")
            ]
            
            response = create_success_response(
                "Scripts listed successfully",
                {"scripts": scripts, "count": len(scripts)}
            )
            
            cache_set(cache_key, response, ttl=300)
            
            return response
            
        except Exception as e:
            log_error(f"List scripts exception: {str(e)}")
            return create_error_response("List scripts exception", {"error": str(e)})
    
    def _resolve_script_id(self,
                          script_id: str,
                          ha_config: Dict[str, Any]) -> Optional[str]:
        """
        Resolve script friendly name to entity_id.
        
        Args:
            script_id: Entity ID or friendly name
            ha_config: HA configuration
            
        Returns:
            Entity ID or None if not found
        """
        if script_id.startswith("script."):
            return script_id
        
        scripts_result = self.list_scripts(ha_config)
        if not scripts_result.get("success", False):
            return None
        
        scripts = scripts_result.get("data", {}).get("scripts", [])
        
        script_id_lower = script_id.lower()
        for script in scripts:
            friendly_name = script.get("friendly_name", "").lower()
            if friendly_name == script_id_lower:
                return script["entity_id"]
            
            if script_id_lower in friendly_name:
                return script["entity_id"]
        
        return f"script.{script_id}"
    
    def _update_stats(self, success: bool, processing_time_ms: float) -> None:
        """Update script execution statistics."""
        self._stats.total_executions += 1
        self._stats.last_execution_time = time.time()
        
        if success:
            self._stats.successful_executions += 1
        else:
            self._stats.failed_executions += 1
        
        if self._stats.total_executions > 0:
            current_avg = self._stats.avg_response_time_ms
            new_avg = ((current_avg * (self._stats.total_executions - 1)) + 
                      processing_time_ms) / self._stats.total_executions
            self._stats.avg_response_time_ms = new_avg
    
    def get_stats(self) -> Dict[str, Any]:
        """Get script execution statistics."""
        return {
            "total_executions": self._stats.total_executions,
            "successful_executions": self._stats.successful_executions,
            "failed_executions": self._stats.failed_executions,
            "success_rate": (self._stats.successful_executions / self._stats.total_executions * 100
                           if self._stats.total_executions > 0 else 0.0),
            "avg_response_time_ms": self._stats.avg_response_time_ms,
            "last_execution_time": self._stats.last_execution_time,
            "uptime_seconds": time.time() - self._initialized_time
        }


_script_manager: Optional[HAScriptManager] = None


def _get_script_manager() -> HAScriptManager:
    """Get or create script manager singleton."""
    global _script_manager
    if _script_manager is None:
        _script_manager = HAScriptManager()
    return _script_manager


def execute_script(script_id: str,
                   ha_config: Dict[str, Any],
                   script_variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Execute Home Assistant script."""
    manager = _get_script_manager()
    return manager.execute_script(script_id, ha_config, script_variables)


def list_scripts(ha_config: Dict[str, Any]) -> Dict[str, Any]:
    """List available scripts."""
    manager = _get_script_manager()
    return manager.list_scripts(ha_config)


def get_script_stats() -> Dict[str, Any]:
    """Get script manager statistics."""
    manager = _get_script_manager()
    return manager.get_stats()


__all__ = [
    'execute_script',
    'list_scripts',
    'get_script_stats',
]

#EOF
