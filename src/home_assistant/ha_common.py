"""
ha_common.py - Home Assistant Common Utilities
Version: 2025.09.30.06
Daily Revision: Performance Optimization Phase 1

Shared utilities for all Home Assistant feature modules.
Eliminates 200-400 lines of duplicate code across 6 modules.

ARCHITECTURE: HOME ASSISTANT EXTENSION CORE
- Provides unified HA API interface
- Centralizes configuration management
- Standardizes error handling
- Enables consistent caching patterns
- 100% Free Tier AWS compliant

Licensed under the Apache License, Version 2.0
"""

from typing import Dict, Any, Optional, List
from difflib import SequenceMatcher

from gateway import (
    log_info, log_error, log_warning,
    create_success_response, create_error_response,
    make_get_request, make_post_request,
    cache_get, cache_set,
    generate_correlation_id,
    record_metric
)


class HABaseManager:
    """Base class for all HA feature managers with common functionality."""
    
    def __init__(self):
        self._stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "cache_hits": 0,
            "cache_misses": 0
        }
    
    def get_feature_name(self) -> str:
        """Override in subclass to provide feature name for metrics."""
        return "unknown"
    
    def record_success(self):
        """Record successful operation."""
        self._stats["total_requests"] += 1
        self._stats["successful_requests"] += 1
        record_metric(f"ha_{self.get_feature_name()}_success", 1.0)
    
    def record_failure(self):
        """Record failed operation."""
        self._stats["total_requests"] += 1
        self._stats["failed_requests"] += 1
        record_metric(f"ha_{self.get_feature_name()}_failure", 1.0)
    
    def record_cache_hit(self):
        """Record cache hit."""
        self._stats["cache_hits"] += 1
    
    def record_cache_miss(self):
        """Record cache miss."""
        self._stats["cache_misses"] += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Get feature statistics."""
        return self._stats.copy()


class SingletonManager:
    """Singleton pattern for feature managers."""
    _instances = {}
    
    @classmethod
    def get_instance(cls, manager_class):
        """Get or create singleton instance."""
        if manager_class not in cls._instances:
            cls._instances[manager_class] = manager_class()
        return cls._instances[manager_class]


def get_ha_config() -> Dict[str, Any]:
    """Get Home Assistant configuration with caching."""
    import os
    
    cache_key = "ha_config"
    cached = cache_get(cache_key)
    if cached:
        return cached
    
    config = {
        "base_url": os.environ.get("HOME_ASSISTANT_URL", "").rstrip("/"),
        "access_token": os.environ.get("HOME_ASSISTANT_TOKEN", ""),
        "timeout": int(os.environ.get("HOME_ASSISTANT_TIMEOUT", "30")),
        "verify_ssl": os.environ.get("HOME_ASSISTANT_VERIFY_SSL", "true").lower() == "true"
    }
    
    cache_set(cache_key, config, ttl=300)
    return config


def call_ha_api(
    endpoint: str,
    ha_config: Optional[Dict[str, Any]] = None,
    method: str = "GET",
    data: Optional[Dict[str, Any]] = None,
    timeout: Optional[int] = None
) -> Dict[str, Any]:
    """Unified Home Assistant API call with standard error handling."""
    if not ha_config:
        ha_config = get_ha_config()
    
    url = f"{ha_config['base_url']}{endpoint}"
    headers = {
        "Authorization": f"Bearer {ha_config['access_token']}",
        "Content-Type": "application/json"
    }
    
    timeout = timeout or ha_config.get("timeout", 30)
    
    if method == "GET":
        return make_get_request(url=url, headers=headers, timeout=timeout)
    else:
        return make_post_request(url=url, headers=headers, json_data=data, timeout=timeout)


def call_ha_service(
    domain: str,
    service: str,
    ha_config: Optional[Dict[str, Any]] = None,
    entity_id: Optional[str] = None,
    service_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Call Home Assistant service with standard pattern."""
    endpoint = f"/api/services/{domain}/{service}"
    
    payload = {}
    if entity_id:
        payload["entity_id"] = entity_id
    if service_data:
        payload.update(service_data)
    
    return call_ha_api(endpoint, ha_config, method="POST", data=payload)


def call_ha_service_generic(
    domain: str,
    service: str,
    entity_id: str,
    ha_config: Dict[str, Any],
    service_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Generic service call wrapper for feature modules."""
    return call_ha_service(domain, service, ha_config, entity_id, service_data)


def get_entity_state(
    entity_id: str,
    ha_config: Optional[Dict[str, Any]] = None,
    use_cache: bool = True
) -> Dict[str, Any]:
    """Get Home Assistant entity state with optional caching."""
    if use_cache:
        cache_key = f"ha_state_{entity_id}"
        cached = cache_get(cache_key)
        if cached:
            return create_success_response("State retrieved from cache", {"state": cached})
    
    endpoint = f"/api/states/{entity_id}"
    result = call_ha_api(endpoint, ha_config)
    
    if result.get("success", False):
        state_data = result.get("data", {})
        if use_cache:
            cache_set(f"ha_state_{entity_id}", state_data, ttl=60)
        return create_success_response("State retrieved", {"state": state_data})
    
    return result


def list_entities_by_domain(
    domain: str,
    ha_config: Optional[Dict[str, Any]] = None,
    cache_ttl: int = 300
) -> List[Dict[str, Any]]:
    """List all entities of a specific domain with caching."""
    cache_key = f"ha_{domain}_list"
    cached = cache_get(cache_key)
    if cached:
        return cached
    
    endpoint = "/api/states"
    result = call_ha_api(endpoint, ha_config)
    
    if result.get("success", False):
        all_entities = result.get("data", [])
        filtered = [e for e in all_entities if e.get("entity_id", "").startswith(f"{domain}.")]
        cache_set(cache_key, filtered, ttl=cache_ttl)
        return filtered
    
    return []


def resolve_entity_id(
    identifier: str,
    domain: str,
    ha_config: Optional[Dict[str, Any]] = None,
    similarity_threshold: float = 0.6
) -> Optional[str]:
    """Resolve entity ID from friendly name or partial match."""
    if identifier.startswith(f"{domain}."):
        return identifier
    
    entities = list_entities_by_domain(domain, ha_config)
    
    for entity in entities:
        entity_id = entity.get("entity_id", "")
        friendly_name = entity.get("attributes", {}).get("friendly_name", "").lower()
        
        if identifier.lower() == friendly_name:
            return entity_id
        
        if identifier.lower() in friendly_name:
            return entity_id
    
    best_match = None
    best_score = 0
    
    for entity in entities:
        friendly_name = entity.get("attributes", {}).get("friendly_name", "").lower()
        score = SequenceMatcher(None, identifier.lower(), friendly_name).ratio()
        
        if score > best_score and score >= similarity_threshold:
            best_score = score
            best_match = entity.get("entity_id")
    
    return best_match


def parse_entity_id(entity_id: str) -> Dict[str, str]:
    """Parse entity ID into domain and object_id."""
    if "." not in entity_id:
        return {"domain": "", "object_id": entity_id, "valid": False}
    
    domain, object_id = entity_id.split(".", 1)
    return {
        "domain": domain,
        "object_id": object_id,
        "valid": True
    }


def parse_boolean_value(value: Any) -> bool:
    """Parse various boolean representations."""
    if isinstance(value, bool):
        return value
    
    if isinstance(value, str):
        value = value.lower().strip()
        return value in ["true", "yes", "on", "1", "enable", "enabled"]
    
    return bool(value)


def format_ha_error(operation: str, error: Any, correlation_id: Optional[str] = None) -> Dict[str, Any]:
    """Consistent error response formatting."""
    error_data = {
        "operation": operation,
        "error": str(error)
    }
    
    if correlation_id:
        error_data["correlation_id"] = correlation_id
    
    log_error(f"HA operation failed: {operation} - {str(error)}")
    return create_error_response(f"HA {operation} failed", error_data)


def validate_ha_config(ha_config: Dict[str, Any]) -> bool:
    """Validate Home Assistant configuration."""
    required_fields = ["base_url", "access_token"]
    
    for field in required_fields:
        if not ha_config.get(field):
            log_error(f"Missing required HA config field: {field}")
            return False
    
    if not ha_config["base_url"].startswith("http"):
        log_error("Invalid base_url: must start with http or https")
        return False
    
    return True


def build_cache_key(prefix: str, *parts: str) -> str:
    """Build standardized cache key."""
    return "_".join([prefix] + list(parts))


def get_list_from_cache_or_api(
    cache_key: str,
    domain: str,
    ha_config: Optional[Dict[str, Any]] = None,
    cache_ttl: int = 300
) -> List[Dict[str, Any]]:
    """Get entity list from cache or API."""
    cached = cache_get(cache_key)
    if cached:
        return cached
    
    entities = list_entities_by_domain(domain, ha_config, cache_ttl)
    return entities


__all__ = [
    "HABaseManager",
    "SingletonManager",
    "get_ha_config",
    "call_ha_api",
    "call_ha_service",
    "call_ha_service_generic",
    "get_entity_state",
    "list_entities_by_domain",
    "resolve_entity_id",
    "parse_entity_id",
    "parse_boolean_value",
    "format_ha_error",
    "validate_ha_config",
    "build_cache_key",
    "get_list_from_cache_or_api"
]
