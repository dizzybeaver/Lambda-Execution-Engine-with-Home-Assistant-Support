"""
config_manager.py
Version: 2025.10.11.01
Description: Manages loading, validation, and access to all system configuration

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

import json
from typing import Dict, Any, Optional
from config_loader import (
    load_system_config,
    validate_configuration,
    get_category_config,
    merge_custom_config,
    ConfigCategory
)
from ha_config import load_ha_config, validate_ha_config


class ConfigurationManager:
    """Manages all system configuration with caching and validation."""
    
    def __init__(self):
        self._system_config: Optional[Dict[str, Any]] = None
        self._ha_config: Optional[Dict[str, Any]] = None
        self._validation_results: Optional[Dict[str, Any]] = None
        self._initialized = False
    
    def initialize(self) -> Dict[str, Any]:
        """Initialize configuration system."""
        if self._initialized:
            return {
                "success": True,
                "message": "Configuration already initialized",
                "cached": True
            }
        
        try:
            self._system_config = load_system_config()
            self._ha_config = load_ha_config()
            
            from user_config import USER_CUSTOM_CONFIG
            self._system_config = merge_custom_config(self._system_config, USER_CUSTOM_CONFIG)
            
            self._validation_results = self._validate_all()
            
            self._initialized = True
            
            return {
                "success": True,
                "message": "Configuration initialized successfully",
                "validation": self._validation_results
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Configuration initialization failed: {str(e)}",
                "error": str(e)
            }
    
    def _validate_all(self) -> Dict[str, Any]:
        """Validate all configuration sections."""
        system_validation = validate_configuration(self._system_config)
        ha_validation = validate_ha_config(self._ha_config)
        
        return {
            "system": system_validation,
            "home_assistant": ha_validation,
            "overall_valid": system_validation["valid"] and ha_validation["valid"]
        }
    
    def get_system_config(self) -> Dict[str, Any]:
        """Get complete system configuration."""
        if not self._initialized:
            self.initialize()
        
        return self._system_config.copy() if self._system_config else {}
    
    def get_ha_config(self) -> Dict[str, Any]:
        """Get Home Assistant configuration."""
        if not self._initialized:
            self.initialize()
        
        return self._ha_config.copy() if self._ha_config else {}
    
    def get_category(self, category: str) -> Dict[str, Any]:
        """Get configuration for specific category."""
        if not self._initialized:
            self.initialize()
        
        try:
            cat_enum = ConfigCategory(category)
            return get_category_config(self._system_config, cat_enum)
        except (ValueError, KeyError):
            return {}
    
    def get_setting(self, category: str, key: str, default: Any = None) -> Any:
        """Get specific setting from category."""
        category_config = self.get_category(category)
        return category_config.get(key, default)
    
    def get_validation_results(self) -> Dict[str, Any]:
        """Get validation results."""
        if not self._initialized:
            self.initialize()
        
        return self._validation_results.copy() if self._validation_results else {}
    
    def reload(self) -> Dict[str, Any]:
        """Reload all configuration."""
        self._initialized = False
        self._system_config = None
        self._ha_config = None
        self._validation_results = None
        
        return self.initialize()
    
    def export_config(self, include_validation: bool = True) -> str:
        """Export configuration as JSON string."""
        if not self._initialized:
            self.initialize()
        
        export_data = {
            "system": self._system_config,
            "home_assistant": self._ha_config
        }
        
        if include_validation:
            export_data["validation"] = self._validation_results
        
        return json.dumps(export_data, indent=2, default=str)
    
    def get_memory_summary(self) -> Dict[str, Any]:
        """Get memory allocation summary."""
        if not self._initialized:
            self.initialize()
        
        validation = self._validation_results.get("system", {})
        
        return {
            "total_estimated_mb": validation.get("memory_estimate_mb", 0),
            "lambda_limit_mb": 128,
            "remaining_mb": 128 - validation.get("memory_estimate_mb", 0),
            "utilization_percent": (validation.get("memory_estimate_mb", 0) / 128) * 100
        }
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get metrics allocation summary."""
        if not self._initialized:
            self.initialize()
        
        validation = self._validation_results.get("system", {})
        
        return {
            "total_metrics": validation.get("metrics_count", 0),
            "cloudwatch_limit": 10,
            "remaining": 10 - validation.get("metrics_count", 0),
            "utilization_percent": (validation.get("metrics_count", 0) / 10) * 100
        }


_CONFIG_MANAGER = ConfigurationManager()


def initialize_configuration() -> Dict[str, Any]:
    """Initialize configuration system."""
    return _CONFIG_MANAGER.initialize()


def get_system_configuration() -> Dict[str, Any]:
    """Get complete system configuration."""
    return _CONFIG_MANAGER.get_system_config()


def get_ha_configuration() -> Dict[str, Any]:
    """Get Home Assistant configuration."""
    return _CONFIG_MANAGER.get_ha_config()


def get_category_configuration(category: str) -> Dict[str, Any]:
    """Get configuration for specific category."""
    return _CONFIG_MANAGER.get_category(category)


def get_configuration_setting(category: str, key: str, default: Any = None) -> Any:
    """Get specific configuration setting."""
    return _CONFIG_MANAGER.get_setting(category, key, default)


def reload_configuration() -> Dict[str, Any]:
    """Reload all configuration."""
    return _CONFIG_MANAGER.reload()


def export_configuration(include_validation: bool = True) -> str:
    """Export configuration as JSON."""
    return _CONFIG_MANAGER.export_config(include_validation)


def get_memory_allocation_summary() -> Dict[str, Any]:
    """Get memory allocation summary."""
    return _CONFIG_MANAGER.get_memory_summary()


def get_metrics_allocation_summary() -> Dict[str, Any]:
    """Get metrics allocation summary."""
    return _CONFIG_MANAGER.get_metrics_summary()


def get_validation_status() -> Dict[str, Any]:
    """Get configuration validation status."""
    return _CONFIG_MANAGER.get_validation_results()
