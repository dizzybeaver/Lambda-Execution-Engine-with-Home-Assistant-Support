"""
home_assistant_areas.py - Area/Room Control
Version: 2025.09.30.04
Daily Revision: 001

Home Assistant area-based device control
Allows controlling all devices in a room/area at once

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
class AreaStats:
    """Statistics for area operations."""
    total_operations: int = 0
    successful_operations: int = 0
    failed_operations: int = 0
    devices_controlled: int = 0


class HAAreaManager:
    """Manages Home Assistant area-based operations."""
    
    def __init__(self):
        self._stats = AreaStats()
        self._initialized_time = time.time()
    
    def control_area_devices(self,
                           area_name: str,
                           action: str,
                           ha_config: Dict[str, Any],
                           domain_filter: Optional[str] = None) -> Dict[str, Any]:
        """
        Control all devices in an area.
        
        Args:
            area_name: Area/room name
            action: Action to perform (turn_on, turn_off, toggle)
            ha_config: HA configuration dict
            domain_filter: Optional domain filter (light, switch, etc.)
            
        Returns:
            Result dict with success status
        """
        start_time = time.time()
        correlation_id = generate_correlation_id()
        
        try:
            log_info(f"Controlling area {area_name}: {action} [{correlation_id}]")
            increment_counter("ha_area_control_request")
            
            area_id = self._resolve_area_id(area_name, ha_config)
            if not area_id:
                log_warning(f"Area not found: {area_name}")
                return create_error_response(
                    "Area not found",
                    {"area_name": area_name}
                )
            
            devices = self._get_area_devices(area_id, ha_config, domain_filter)
            if not devices:
                return create_error_response(
                    "No devices found in area",
                    {"area_name": area_name, "domain_filter": domain_filter}
                )
            
            results = []
            success_count = 0
            
            for device in devices:
                entity_id = device["entity_id"]
                domain = entity_id.split(".")[0]
                
                result = self._control_device(domain, action, entity_id, ha_config)
                results.append({
                    "entity_id": entity_id,
                    "success": result.get("success", False)
                })
                
                if result.get("success", False):
                    success_count += 1
            
            processing_time = (time.time() - start_time) * 1000
            
            all_success = success_count == len(devices)
            
            if all_success:
                log_info(f"Area control successful: {area_name} [{correlation_id}]")
                record_metric("ha_area_control_success", 1.0)
                self._update_stats(True, len(devices))
            else:
                log_warning(f"Area control partial success: {success_count}/{len(devices)}")
                self._update_stats(False, len(devices))
            
            return create_success_response(
                f"Area {area_name} control completed",
                {
                    "area_id": area_id,
                    "action": action,
                    "total_devices": len(devices),
                    "successful": success_count,
                    "failed": len(devices) - success_count,
                    "results": results,
                    "processing_time_ms": processing_time,
                    "correlation_id": correlation_id
                }
            )
                
        except Exception as e:
            log_error(f"Area control exception: {str(e)}")
            record_metric("ha_area_control_error", 1.0)
            self._update_stats(False, 0)
            return create_error_response(
                "Area control exception",
                {"error": str(e)}
            )
    
    def list_areas(self, ha_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        List all available areas.
        
        Args:
            ha_config: HA configuration dict
            
        Returns:
            List of areas
        """
        try:
            correlation_id = generate_correlation_id()
            log_debug(f"Listing areas [{correlation_id}]")
            
            cache_key = "ha_area_list"
            cached = cache_get(cache_key)
            if cached:
                return cached
            
            url = f"{ha_config['base_url']}/api/config/area_registry/list"
            headers = {
                "Authorization": f"Bearer {ha_config['access_token']}"
            }
            
            result = make_get_request(
                url=url,
                headers=headers,
                timeout=ha_config.get('timeout', 30)
            )
            
            if not result.get("success", False):
                return create_error_response("Failed to list areas", {"result": result})
            
            areas = result.get("data", [])
            
            response = create_success_response(
                "Areas listed successfully",
                {"areas": areas, "count": len(areas)}
            )
            
            cache_set(cache_key, response, ttl=300)
            
            return response
            
        except Exception as e:
            log_error(f"List areas exception: {str(e)}")
            return create_error_response("List areas exception", {"error": str(e)})
    
    def _resolve_area_id(self,
                        area_name: str,
                        ha_config: Dict[str, Any]) -> Optional[str]:
        """
        Resolve area name to area_id.
        
        Args:
            area_name: Area name
            ha_config: HA configuration
            
        Returns:
            Area ID or None if not found
        """
        areas_result = self.list_areas(ha_config)
        if not areas_result.get("success", False):
            return None
        
        areas = areas_result.get("data", {}).get("areas", [])
        
        area_name_lower = area_name.lower()
        for area in areas:
            name = area.get("name", "").lower()
            if name == area_name_lower:
                return area.get("area_id")
            
            if area_name_lower in name:
                return area.get("area_id")
        
        return None
    
    def _get_area_devices(self,
                         area_id: str,
                         ha_config: Dict[str, Any],
                         domain_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get devices in area.
        
        Args:
            area_id: Area ID
            ha_config: HA configuration
            domain_filter: Optional domain filter
            
        Returns:
            List of device entities
        """
        try:
            cache_key = f"ha_area_devices_{area_id}_{domain_filter or 'all'}"
            cached = cache_get(cache_key)
            if cached:
                return cached
            
            url = f"{ha_config['base_url']}/api/config/entity_registry/list"
            headers = {
                "Authorization": f"Bearer {ha_config['access_token']}"
            }
            
            result = make_get_request(
                url=url,
                headers=headers,
                timeout=ha_config.get('timeout', 30)
            )
            
            if not result.get("success", False):
                return []
            
            entities = result.get("data", [])
            
            controllable_domains = ["light", "switch", "fan", "cover", "climate", "media_player"]
            
            area_devices = [
                {
                    "entity_id": entity.get("entity_id"),
                    "domain": entity.get("entity_id", "").split(".")[0]
                }
                for entity in entities
                if entity.get("area_id") == area_id
                and entity.get("entity_id", "").split(".")[0] in controllable_domains
                and (domain_filter is None or entity.get("entity_id", "").startswith(f"{domain_filter}."))
                and not entity.get("disabled_by")
            ]
            
            cache_set(cache_key, area_devices, ttl=300)
            
            return area_devices
            
        except Exception as e:
            log_error(f"Get area devices exception: {str(e)}")
            return []
    
    def _control_device(self,
                       domain: str,
                       action: str,
                       entity_id: str,
                       ha_config: Dict[str, Any]) -> Dict[str, Any]:
        """Control individual device."""
        try:
            url = f"{ha_config['base_url']}/api/services/{domain}/{action}"
            headers = {
                "Authorization": f"Bearer {ha_config['access_token']}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "entity_id": entity_id
            }
            
            result = make_post_request(
                url=url,
                headers=headers,
                json_data=payload,
                timeout=ha_config.get('timeout', 30)
            )
            
            return result
            
        except Exception as e:
            log_error(f"Control device exception: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _update_stats(self, success: bool, device_count: int) -> None:
        """Update area operation statistics."""
        self._stats.total_operations += 1
        self._stats.devices_controlled += device_count
        
        if success:
            self._stats.successful_operations += 1
        else:
            self._stats.failed_operations += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Get area operation statistics."""
        return {
            "total_operations": self._stats.total_operations,
            "successful_operations": self._stats.successful_operations,
            "failed_operations": self._stats.failed_operations,
            "success_rate": (self._stats.successful_operations / self._stats.total_operations * 100
                           if self._stats.total_operations > 0 else 0.0),
            "devices_controlled": self._stats.devices_controlled,
            "uptime_seconds": time.time() - self._initialized_time
        }


_area_manager: Optional[HAAreaManager] = None


def _get_area_manager() -> HAAreaManager:
    """Get or create area manager singleton."""
    global _area_manager
    if _area_manager is None:
        _area_manager = HAAreaManager()
    return _area_manager


def control_area_devices(area_name: str,
                        action: str,
                        ha_config: Dict[str, Any],
                        domain_filter: Optional[str] = None) -> Dict[str, Any]:
    """Control all devices in an area."""
    manager = _get_area_manager()
    return manager.control_area_devices(area_name, action, ha_config, domain_filter)


def list_areas(ha_config: Dict[str, Any]) -> Dict[str, Any]:
    """List available areas."""
    manager = _get_area_manager()
    return manager.list_areas(ha_config)


def get_area_stats() -> Dict[str, Any]:
    """Get area operation statistics."""
    manager = _get_area_manager()
    return manager.get_stats()


__all__ = [
    'control_area_devices',
    'list_areas',
    'get_area_stats',
]

#EOF
