"""
home_assistant_scripts.py - Script Execution
Version: 2025.09.30.05
Daily Revision: Ultra-Optimized

Home Assistant script execution via voice commands

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
            
            entity_id = resolve_entity_id(script_id, ha_config, "script", "scripts")
            if not entity_id:
                return create_error_response("Script not found", {"script_id": script_id})
            
            result = call_ha_service_generic(ha_config, "script", "turn_on", entity_id, variables)
            
            duration_ms = (time.time() - start_time) * 1000
            success = result.get("success", False)
            
            self._stats.record(success, duration_ms)
            self._record_metric("execute", success)
            
            if success:
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
                return create_error_response("Failed to execute script", {"result": result})
                
        except Exception as e:
            log_error(f"Script execution exception: {str(e)}")
            self._stats.record(False)
            self._record_metric("execute", False)
            return create_error_response("Script execution exception", {"error": str(e)})


_manager_singleton = SingletonManager(HAScriptManager)


def execute_script(
    script_id: str,
    ha_config: Dict[str, Any],
    variables: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Execute script."""
    return _manager_singleton.get().execute(script_id, ha_config, variables)


def get_script_stats() -> Dict[str, Any]:
    """Get script statistics."""
    return _manager_singleton.get().get_stats()


__all__ = ['execute_script', 'get_script_stats']
