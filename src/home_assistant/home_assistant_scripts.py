"""
home_assistant_scripts.py - Script Execution
Version: 2025.09.30.07
Daily Revision: Performance Optimization Phase 2

Phase 2: Consolidated cache + entity minimization

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
    call_ha_service,
    SingletonManager,
    get_cache_section,
    set_cache_section,
    minimize_entity_list
)


class HAScriptManager(HABaseManager):
    """Manages Home Assistant script execution."""
    
    def get_feature_name(self) -> str:
        return "script"
    
    def execute(
        self,
        script_id: str,
        ha_config: Dict[str, Any],
        variables: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute script by ID or name."""
        start_time = time.time()
        correlation_id = generate_correlation_id()
        
        try:
            log_info(f"Executing script: {script_id} [{correlation_id}]")
            increment_counter("ha_script_execution_request")
            
            entity_id = script_id if "." in script_id else resolve_entity_id(script_id, "script", ha_config)
            if not entity_id:
                self.record_failure()
                return create_error_response("Script not found", {"script_id": script_id})
            
            result = call_ha_service("script", "turn_on", ha_config, entity_id, variables)
            
            duration_ms = (time.time() - start_time) * 1000
            
            if result.get("success", False):
                self.record_success()
                log_info(f"Script executed: {entity_id} [{correlation_id}]")
                return create_success_response(
                    f"Script {script_id} executed",
                    {
                        "entity_id": entity_id,
                        "processing_time_ms": duration_ms,
                        "correlation_id": correlation_id
                    }
                )
            else:
                self.record_failure()
                return create_error_response("Failed to execute script", {"result": result})
                
        except Exception as e:
            self.record_failure()
            log_error(f"Script execution exception: {str(e)}")
            return create_error_response("Script execution exception", {"error": str(e)})
    
    def list(self, ha_config: Dict[str, Any]) -> Dict[str, Any]:
        """List all scripts with consolidated cache."""
        try:
            cached = get_cache_section("scripts", ttl=300)
            if cached:
                self.record_cache_hit()
                return create_success_response("Scripts retrieved from cache", {"scripts": cached})
            
            self.record_cache_miss()
            from ha_common import call_ha_api
            response = call_ha_api("/api/states", ha_config)
            
            if not isinstance(response, list):
                return create_error_response("Invalid API response", {})
            
            scripts = [e for e in response if e.get("entity_id", "").startswith("script.")]
            minimized = minimize_entity_list(scripts)
            
            set_cache_section("scripts", minimized, ttl=300)
            
            return create_success_response("Scripts retrieved", {"scripts": minimized})
            
        except Exception as e:
            log_error(f"List scripts exception: {str(e)}")
            return create_error_response("List scripts exception", {"error": str(e)})


def execute_script(
    script_id: str,
    ha_config: Dict[str, Any],
    variables: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Execute script."""
    manager = SingletonManager.get_instance(HAScriptManager)
    return manager.execute(script_id, ha_config, variables)


def list_scripts(ha_config: Dict[str, Any]) -> Dict[str, Any]:
    """List all scripts."""
    manager = SingletonManager.get_instance(HAScriptManager)
    return manager.list(ha_config)


def get_script_stats() -> Dict[str, Any]:
    """Get script statistics."""
    manager = SingletonManager.get_instance(HAScriptManager)
    return manager.get_stats()


__all__ = ["execute_script", "list_scripts", "get_script_stats"]
