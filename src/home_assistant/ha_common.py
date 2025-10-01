"""
ha_common.py - Home Assistant Extension Common Utilities
Version: 2025.09.30.05
Daily Revision: Ultra-Optimized

Shared utilities for all Home Assistant extension modules
Provides generic functions, base classes, and common patterns

ARCHITECTURE: HOME ASSISTANT EXTENSION CORE
- Generic entity resolution
- Shared statistics tracking
- Common API wrapper functions
- Base manager class
- Singleton pattern implementation

Licensed under the Apache License, Version 2.0
"""

import time
import re
from typing import Dict, Any, Optional, List, TypeVar, Generic
from dataclasses import dataclass
from abc import ABC, abstractmethod

from gateway import (
    log_info, log_error, log_warning, log_debug,
    make_post_request, make_get_request,
    create_success_response, create_error_response,
    generate_correlation_id,
    record_metric, increment_counter,
    cache_get, cache_set
)


@dataclass
class OperationStats:
    """Generic statistics for operations."""
    total: int = 0
    successful: int = 0
    failed: int = 0
    avg_response_ms: float = 0.0
    last_operation: float = 0.0
    
    def record(self, success: bool, duration_ms: float = 0.0):
        """Record an operation."""
        self.total += 1
        if success:
            self.successful += 1
        else:
            self.failed += 1
        
        if duration_ms > 0:
            self.avg_response_ms = (
                (self.avg_response_ms * (self.total - 1) + duration_ms) / self.total
            )
        self.last_operation = time.time()
    
    def get_success_rate(self) -> float:
        """Get success rate percentage."""
        return (self.successful / self.total * 100) if self.total > 0 else 0.0


class HABaseManager(ABC):
    """Base class for all HA feature managers."""
    
    def __init__(self):
        self._stats = OperationStats()
        self._initialized_time = time.time()
        self._cache_ttl = 300
    
    @abstractmethod
    def get_feature_name(self) -> str:
        """Return feature name for metrics."""
        pass
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics for this manager."""
        return {
            "total_operations": self._stats.total,
            "successful_operations": self._stats.successful,
            "failed_operations": self._stats.failed,
            "success_rate": self._stats.get_success_rate(),
            "avg_response_time_ms": self._stats.avg_response_ms,
            "uptime_seconds": time.time() - self._initialized_time
        }
    
    def _record_metric(self, operation: str, success: bool):
        """Record metric for operation."""
        metric_name = f"ha_{self.get_feature_name()}_{operation}"
        metric_name += "_success" if success else "_error"
        record_metric(metric_name, 1.0)


def resolve_entity_id(
    search_term: str,
    ha_config: Dict[str, Any],
    domain: str,
    cache_key_prefix: str = "entities"
) -> Optional[str]:
    """
    Resolve entity ID from name or ID using fuzzy matching.
    
    Args:
        search_term: Entity ID or friendly name to search
        ha_config: HA configuration dict
        domain: Entity domain (automation, script, etc.)
        cache_key_prefix: Cache key prefix for entity list
        
    Returns:
        Resolved entity_id or None
    """
    if "." in search_term and search_term.startswith(f"{domain}."):
        return search_term
    
    entities = _get_domain_entities(ha_config, domain, cache_key_prefix)
    if not entities:
        return None
    
    search_lower = search_term.lower()
    
    for entity in entities:
        entity_id = entity.get("entity_id", "")
        friendly_name = entity.get("attributes", {}).get("friendly_name", "").lower()
        
        if friendly_name == search_lower or search_lower in friendly_name:
            return entity_id
    
    return None


def _get_domain_entities(
    ha_config: Dict[str, Any],
    domain: str,
    cache_key_prefix: str
) -> List[Dict[str, Any]]:
    """Get all entities for a domain with caching."""
    cache_key = f"{cache_key_prefix}_{domain}"
    cached = cache_get(cache_key)
    if cached:
        return cached
    
    try:
        url = f"{ha_config['base_url']}/api/states"
        headers = {"Authorization": f"Bearer {ha_config['access_token']}"}
        
        result = make_get_request(url=url, headers=headers, timeout=ha_config.get('timeout', 30))
        
        if result.get("success", False):
            all_states = result.get("data", [])
            entities = [s for s in all_states if s.get("entity_id", "").startswith(f"{domain}.")]
            cache_set(cache_key, entities, ttl=300)
            return entities
    except Exception as e:
        log_error(f"Get domain entities error: {str(e)}")
    
    return []


def call_ha_service_generic(
    ha_config: Dict[str, Any],
    domain: str,
    service: str,
    entity_id: Optional[str] = None,
    service_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Generic HA service call wrapper.
    
    Args:
        ha_config: HA configuration dict
        domain: Service domain
        service: Service name
        entity_id: Optional entity ID
        service_data: Optional service data
        
    Returns:
        Result dict
    """
    try:
        url = f"{ha_config['base_url']}/api/services/{domain}/{service}"
        headers = {
            "Authorization": f"Bearer {ha_config['access_token']}",
            "Content-Type": "application/json"
        }
        
        payload = {}
        if entity_id:
            payload["entity_id"] = entity_id
        if service_data:
            payload.update(service_data)
        
        result = make_post_request(
            url=url,
            headers=headers,
            json_data=payload,
            timeout=ha_config.get('timeout', 30)
        )
        
        return result
        
    except Exception as e:
        log_error(f"Service call error: {str(e)}")
        return {"success": False, "error": str(e)}


def get_entity_state(
    ha_config: Dict[str, Any],
    entity_id: str
) -> Dict[str, Any]:
    """
    Get entity state from HA.
    
    Args:
        ha_config: HA configuration dict
        entity_id: Entity ID
        
    Returns:
        Result dict with state data
    """
    try:
        url = f"{ha_config['base_url']}/api/states/{entity_id}"
        headers = {"Authorization": f"Bearer {ha_config['access_token']}"}
        
        result = make_get_request(url=url, headers=headers, timeout=ha_config.get('timeout', 30))
        
        if result.get("success", False):
            return create_success_response(
                "State retrieved",
                {"state": result.get("data", {})}
            )
        else:
            return create_error_response("Failed to get state", {"result": result})
            
    except Exception as e:
        log_error(f"Get state error: {str(e)}")
        return create_error_response("Get state exception", {"error": str(e)})


def parse_duration_string(duration: str) -> Optional[int]:
    """
    Parse duration string to seconds.
    
    Supports:
    - HH:MM:SS format
    - MM:SS format
    - Text: "10 minutes", "2 hours", "30 seconds"
    - Plain number (assumed minutes)
    
    Args:
        duration: Duration string
        
    Returns:
        Duration in seconds or None if invalid
    """
    duration = duration.strip()
    
    time_pattern = r'^(\d{1,2}):(\d{2}):(\d{2})$'
    match = re.match(time_pattern, duration)
    if match:
        hours, minutes, seconds = map(int, match.groups())
        return hours * 3600 + minutes * 60 + seconds
    
    short_pattern = r'^(\d{1,2}):(\d{2})$'
    match = re.match(short_pattern, duration)
    if match:
        minutes, seconds = map(int, match.groups())
        return minutes * 60 + seconds
    
    if duration.isdigit():
        return int(duration) * 60
    
    text_pattern = r'(\d+)\s*(hour|hr|minute|min|second|sec)s?'
    match = re.search(text_pattern, duration.lower())
    if match:
        value = int(match.group(1))
        unit = match.group(2)
        
        if unit in ['hour', 'hr']:
            return value * 3600
        elif unit in ['minute', 'min']:
            return value * 60
        elif unit in ['second', 'sec']:
            return value
    
    return None


def format_duration_seconds(seconds: int) -> str:
    """Format seconds as HH:MM:SS."""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def parse_boolean_value(value: Any) -> bool:
    """Parse various boolean representations."""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in ["true", "on", "yes", "1", "enabled", "enable"]
    return bool(value)


T = TypeVar('T')

class SingletonManager(Generic[T]):
    """Generic singleton manager wrapper."""
    
    def __init__(self, manager_class: type):
        self._manager_class = manager_class
        self._instance: Optional[T] = None
    
    def get(self) -> T:
        """Get or create singleton instance."""
        if self._instance is None:
            self._instance = self._manager_class()
        return self._instance
    
    def reset(self):
        """Reset singleton (for testing)."""
        self._instance = None


__all__ = [
    'OperationStats',
    'HABaseManager',
    'resolve_entity_id',
    'call_ha_service_generic',
    'get_entity_state',
    'parse_duration_string',
    'format_duration_seconds',
    'parse_boolean_value',
    'SingletonManager',
]
