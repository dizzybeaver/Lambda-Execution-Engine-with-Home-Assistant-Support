"""
home_assistant_areas.py - Area/Room Control
Version: 2025.09.30.05
Daily Revision: Ultra-Optimized

Home Assistant area-based device control

ARCHITECTURE: HOME ASSISTANT EXTENSION MODULE
- Uses ha_common for shared functionality
- Uses gateway.py for all operations
- Lazy loading compatible
- 100% Free Tier AWS compliant

Licensed under the Apache License, Version 2.0
"""

import time
from typing import Dict, Any, Optional, List

from gateway import (
    log_info, log_error, log_warning,
    make_get_request,
    create_success_response, create_error_response,
    generate_correlation_id,
    increment_counter,
    cache_get, cache_set
)

from ha_common import (
    HABaseManager,
    call_ha_service_generic,
    SingletonManager
)


class HAAreaManager(HABaseManager):
    """Manages Home Assistant area-based operations."""
    
    def __init__(self):
        super().__init__()
        self._devices_controlled = 0
        self._controllable_domains = {"light", "switch", "fan", "cover", "climate", "media_player"}
    
    def get_feature_name(self) -> str:
        return "area"
    
    def control_devices(
        self,
        area_name: str,
        action: str,
        ha_config: Dict[str, Any],
        domain_filter: Optional[str] = None
    ) -> Dict[str, Any]:
        """Control all devices in an area."""
        start_time = time.time()
        correlation_id = generate_correlation_id()
        
        try:
            log_info(f"Controlling area {area_name}: {action} [{correlation_id}]")
            increment_counter("ha_area_control_request")
            
            area_id = self._resolve_area(area_name, ha_config)
            if not area_id:
                return create_error_response("Area not found", {"area_name": area_name})
            
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
                
                result = call_ha_service_generic(ha_config, domain, action, entity_id)
                
                if result.get("success", False):
                    success_count += 1
                    self._devices_controlled += 1
                
                results.append({
                    "entity_id": entity_id,
                    "success": result.get("success", False)
                })
            
            duration_ms = (time.time() - start_time) * 1000
            overall_success = success_count > 0
            
            self._stats.record(overall_success, duration_ms)
            self._record_metric("control", overall_success)
            
            log_info(f"Area control: {success_count}/{len(devices)} succeeded [{correlation_id}]")
            
            return create_success_response(
                f"Controlled {success_count}/{len(devices)} devices in {area_name}",
                {
                    "area_name": area_name,
                    "action": action,
                    "total_devices": len(devices),
                    "successful": success_count,
                    "results": results,
                    "processing_time_ms": duration_ms,
                    "correlation_id": correlation_id
                }
            )
                
        except Exception as e:
            log_error(f"Area control exception: {str(e)}")
            self._stats.record(False)
            self._record_metric("control", False)
            return create_error_response("Area control exception", {"error": str(e)})
    
    def _resolve_area(self, area_name: str, ha_config: Dict[str, Any]) -> Optional[str]:
        """Resolve area ID from name."""
        areas = self._get_areas(ha_config)
        area_name_lower = area_name.lower()
        
        for area in areas:
            name = area.get("name", "").lower()
            if name == area_name_lower or area_name_lower in name:
                return area.get("area_id")
        
        return None
    
    def _get_areas(self, ha_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get all areas with caching."""
        cache_key = "ha_areas"
        cached = cache_get(cache_key)
        if cached:
            return cached
        
        try:
            url = f"{ha_config['base_url']}/api/config/area_registry/list"
            headers = {"Authorization": f"Bearer {ha_config['access_token']}"}
            
            result = make_get_request(url=url, headers=headers, timeout=ha_config.get('timeout', 30))
            
            if result.get("success", False):
                areas = result.get("data", [])
                cache_set(cache_key, areas, ttl=300)
                return areas
        except Exception as e:
            log_error(f"Get areas error: {str(e)}")
        
        return []
    
    def _get_area_devices(
        self,
        area_id: str,
        ha_config: Dict[str, Any],
        domain_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get devices in area with caching."""
        cache_key = f"ha_area_devices_{area_id}_{domain_filter or 'all'}"
        cached = cache_get(cache_key)
        if cached:
            return cached
        
        try:
            url = f"{ha_config['base_url']}/api/config/entity_registry/list"
            headers = {"Authorization": f"Bearer {ha_config['access_token']}"}
            
            result = make_get_request(url=url, headers=headers, timeout=ha_config.get('timeout', 30))
            
            if result.get("success", False):
                all_entities = result.get("data", [])
                
                devices = []
                for entity in all_entities:
                    if entity.get("area_id") == area_id:
                        entity_id = entity.get("entity_id", "")
                        domain = entity_id.split(".")[0]
                        
                        if domain in self._controllable_domains:
                            if domain_filter is None or domain == domain_filter:
                                devices.append(entity)
                
                cache_set(cache_key, devices, ttl=300)
                return devices
        except Exception as e:
            log_error(f"Get area devices error: {str(e)}")
        
        return []
    
    def get_stats(self) -> Dict[str, Any]:
        """Get area statistics."""
        base_stats = super().get_stats()
        base_stats["devices_controlled"] = self._devices_controlled
        return base_stats


_manager_singleton = SingletonManager(HAAreaManager)


def control_area_devices(
    area_name: str,
    action: str,
    ha_config: Dict[str, Any],
    domain_filter: Optional[str] = None
) -> Dict[str, Any]:
    """Control area devices."""
    return _manager_singleton.get().control_devices(area_name, action, ha_config, domain_filter)


def get_area_stats() -> Dict[str, Any]:
    """Get area statistics."""
    return _manager_singleton.get().get_stats()


__all__ = ['control_area_devices', 'get_area_stats']
