"""
ha_config.py
Version: 2025.10.11.01
Description: Home Assistant Extension Configuration

Copyright 2025 Joseph Hersey

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

import os
from typing import Dict, Any, Optional
from enum import Enum


class HAPresetLevel(Enum):
    """Home Assistant preset levels."""
    MINIMAL = "minimal"
    STANDARD = "standard"
    MAXIMUM = "maximum"
    CUSTOM = "custom"


HA_PRESET_CONFIGURATIONS = {
    HAPresetLevel.MINIMAL: {
        "memory_allocation_mb": 15.0,
        "feature_flags": {
            "device_control": True,
            "scene_activation": False,
            "automation_trigger": False,
            "service_calls": True,
            "state_queries": True,
            "batch_operations": False,
            "area_control": False
        },
        "performance": {
            "cache_enabled": False,
            "cache_ttl_seconds": 0,
            "max_retries": 1,
            "timeout_seconds": 15,
            "circuit_breaker_threshold": 10,
            "batch_size": 1
        },
        "logging": {
            "log_level": "ERROR",
            "log_requests": False,
            "log_responses": False,
            "log_errors": True
        }
    },
    
    HAPresetLevel.STANDARD: {
        "memory_allocation_mb": 25.0,
        "feature_flags": {
            "device_control": True,
            "scene_activation": True,
            "automation_trigger": True,
            "service_calls": True,
            "state_queries": True,
            "batch_operations": True,
            "area_control": True
        },
        "performance": {
            "cache_enabled": True,
            "cache_ttl_seconds": 300,
            "max_retries": 3,
            "timeout_seconds": 30,
            "circuit_breaker_threshold": 5,
            "batch_size": 10
        },
        "logging": {
            "log_level": "INFO",
            "log_requests": True,
            "log_responses": False,
            "log_errors": True
        }
    },
    
    HAPresetLevel.MAXIMUM: {
        "memory_allocation_mb": 40.0,
        "feature_flags": {
            "device_control": True,
            "scene_activation": True,
            "automation_trigger": True,
            "service_calls": True,
            "state_queries": True,
            "batch_operations": True,
            "area_control": True
        },
        "performance": {
            "cache_enabled": True,
            "cache_ttl_seconds": 600,
            "max_retries": 5,
            "timeout_seconds": 45,
            "circuit_breaker_threshold": 3,
            "batch_size": 25
        },
        "logging": {
            "log_level": "DEBUG",
            "log_requests": True,
            "log_responses": True,
            "log_errors": True
        }
    }
}


def get_ha_preset() -> HAPresetLevel:
    """Get Home Assistant preset from environment variable."""
    preset_value = os.getenv("HA_PRESET", "").lower()
    
    if preset_value == "minimal":
        return HAPresetLevel.MINIMAL
    elif preset_value == "standard":
        return HAPresetLevel.STANDARD
    elif preset_value == "maximum":
        return HAPresetLevel.MAXIMUM
    else:
        return HAPresetLevel.CUSTOM


def load_ha_preset_config(preset: HAPresetLevel) -> Dict[str, Any]:
    """Load preset configuration for Home Assistant."""
    if preset == HAPresetLevel.CUSTOM:
        return {}
    
    return HA_PRESET_CONFIGURATIONS.get(preset, {}).copy()


def load_ha_connection_config() -> Dict[str, Any]:
    """Load Home Assistant connection configuration from Parameter Store or environment."""
    return {
        "ha_url": os.getenv("HA_URL", ""),
        "ha_token": os.getenv("HA_TOKEN", ""),
        "ha_timeout": int(os.getenv("HA_TIMEOUT", "30")),
        "ha_verify_ssl": os.getenv("HA_VERIFY_SSL", "true").lower() == "true",
        "ha_assistant_name": os.getenv("HA_ASSISTANT_NAME", "Home Assistant")
    }


def load_ha_config() -> Dict[str, Any]:
    """Load complete Home Assistant extension configuration."""
    enabled = os.getenv("HOME_ASSISTANT_ENABLED", "false").lower() == "true"
    
    if not enabled:
        return {
            "enabled": False,
            "preset": "none",
            "connection": {},
            "settings": {}
        }
    
    preset = get_ha_preset()
    preset_config = load_ha_preset_config(preset)
    connection_config = load_ha_connection_config()
    
    config = {
        "enabled": True,
        "preset": preset.value,
        "connection": connection_config,
        "settings": preset_config
    }
    
    if preset == HAPresetLevel.CUSTOM:
        config["settings"] = HA_USER_CUSTOM_CONFIG.copy()
    
    return config


def validate_ha_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """Validate Home Assistant configuration."""
    validation = {
        "valid": True,
        "errors": [],
        "warnings": []
    }
    
    if not config.get("enabled"):
        return validation
    
    connection = config.get("connection", {})
    
    if not connection.get("ha_url"):
        validation["valid"] = False
        validation["errors"].append("Home Assistant URL not configured")
    
    if not connection.get("ha_token"):
        validation["valid"] = False
        validation["errors"].append("Home Assistant token not configured")
    
    settings = config.get("settings", {})
    memory_allocation = settings.get("memory_allocation_mb", 0)
    
    if memory_allocation > 50:
        validation["warnings"].append(f"High memory allocation ({memory_allocation}MB) may impact system performance")
    
    return validation


HA_USER_CUSTOM_CONFIG = {
    "memory_allocation_mb": 25.0,
    
    "feature_flags": {
        "device_control": True,
        "scene_activation": True,
        "automation_trigger": True,
        "service_calls": True,
        "state_queries": True,
        "batch_operations": True,
        "area_control": True
    },
    
    "performance": {
        "cache_enabled": True,
        "cache_ttl_seconds": 300,
        "max_retries": 3,
        "timeout_seconds": 30,
        "circuit_breaker_threshold": 5,
        "batch_size": 10
    },
    
    "logging": {
        "log_level": "INFO",
        "log_requests": True,
        "log_responses": False,
        "log_errors": True
    },
    
    "entity_filters": {
        "include_domains": ["light", "switch", "climate", "cover", "lock", "fan", "media_player"],
        "exclude_domains": [],
        "include_entities": [],
        "exclude_entities": []
    },
    
    "optimization": {
        "enable_state_caching": True,
        "state_cache_ttl_seconds": 60,
        "enable_batch_state_fetch": True,
        "enable_service_call_batching": True,
        "parallel_execution_enabled": False,
        "max_parallel_calls": 5
    }
}
