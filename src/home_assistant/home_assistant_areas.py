"""
home_assistant_areas.py - Area Control
Version: 2025.09.30.06
Daily Revision: Performance Optimization Phase 1

Home Assistant area-based device control

ARCHITECTURE: HOME ASSISTANT EXTENSION MODULE
- Uses ha_common for shared functionality
- Lazy loading compatible
- 100% Free Tier AWS compliant

Licensed under the Apache License, Version 2.0
"""

import time
from typing import Dict, Any, List, Optional

from gateway import (
    log_info, log_error,
    create_success_response, create_error_response,
    generate_correlation_id,
    increment_counter
)

from ha_common import (
    HABaseManager,
    call_ha_api,
    call_ha_service,
    SingletonManager
)


class HAAreaManager(HABaseManager):
    """Manages Home Assistant area operations."""
    
    def get_feature_name(self) -> str:
        return "area"
    
    def control_area(
        self,
        area_name: str,
        action: str,
        ha_config: Dict[str, Any],
        domain: Optional[str] = None
    ) -> Dict[str, Any]:
        """Control all devices in area."""
        start_time = time.time()
        correlation_id = generate_correlation_id()
        
        try:
            log_info(f"Controlling area: {area_name} -> {action} [{correlation_id}]")
            increment_counter("ha_area_control_request")
            
            area_id = self._find_area_id(area_name, ha_config)
            if not area_id:
                self.record_failure()
                return create_error_response("Area not found", {"area_name": area_name})
            
            devices = self._get_area_devices(area_id, ha_config, domain)
            if not devices:
                self.record_failure()
                return create_error_response("No controllable devices in area", {"area_name": area_name})
            
            results = self._control_devices(devices, action, ha_config)
            
            duration_ms = (time.time() - start_time) * 1000
            success_count = sum(1 for r in results if r.get("success", False))
            
            if success_count > 0:
                self.record_success()
                log_info(f"Area control: {success_count}/{len(devices)} successful [{correlation_id}]")
                return create_success_response(
                    f"Controlled {success_count} devices in {area_name}",
                    {
                        "area_name": area_name,
                        "action": action,
                        "devices_controlled": success_count,
                        "total_devices": len(devices),
                        "processing_time_ms": duration_ms,
                        "correlation_id": correlation_id
                    }
                )
            else:
                self.record_failure()
                return create_error_response("Failed to control area devices", {})
                
        except Exception as e:
            self.record_failure()
            log_error(f"Control area exception: {str(e)}")
            return create_error_response("Control area exception", {"error": str(e)})
    
    def _find_area_id(self, area_name: str, ha_config: Dict[str, Any]) -> Optional[str]:
        """Find area ID by name."""
        result = call_ha_api("/api/config/area_registry/list", ha_config)
        if not result.get("success", False):
            return None
        
        areas = result.get("data", [])
        for area in areas:
            if area.get("name", "").lower() == area_name.lower():
                return area.get("area_id")
        
        return None
    
    def _get_area_devices(self, area_id: str, ha_config: Dict[str, Any], domain: Optional[str]) -> List[str]:
        """Get controllable devices in area."""
        result = call_ha_api("/api/states", ha_config)
        if not result.get("success", False):
            return []
        
        entities = result.get("data", [])
        area_entities = []
        
        for entity in entities:
            entity_id = entity.get("entity_id", "")
            entity_domain = entity_id.split(".")[0]
            entity_area = entity.get("attributes", {}).get("area_id")
            
            if entity_area == area_id:
                if domain is None or entity_domain == domain:
                    if entity_domain in ["light", "switch", "fan", "cover"]:
                        area_entities.append(entity_id)
        
        return area_entities
    
    def _control_devices(self, devices: List[str], action: str, ha_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Control multiple devices."""
        results = []
        for device in devices:
            domain = device.split(".")[0]
            service = self._action_to_service(action)
            result = call_ha_service(domain, service, ha_config, device)
            results.append(result)
        
        return results
    
    def _action_to_service(self, action: str) -> str:
        """Convert action to service name."""
        action = action.lower()
        if action in ["on", "turn_on", "enable"]:
            return "turn_on"
        elif action in ["off", "turn_off", "disable"]:
            return "turn_off"
        elif action in ["toggle"]:
            return "toggle"
        return "turn_on"


def control_area(
    area_name: str,
    action: str,
    ha_config: Dict[str, Any],
    domain: Optional[str] = None
) -> Dict[str, Any]:
    """Control devices in area."""
    manager = SingletonManager.get_instance(HAAreaManager)
    return manager.control_area(area_name, action, ha_config, domain)


def get_area_stats() -> Dict[str, Any]:
    """Get area statistics."""
    manager = SingletonManager.get_instance(HAAreaManager)
    return manager.get_stats()


__all__ = ["control_area", "get_area_stats"]
