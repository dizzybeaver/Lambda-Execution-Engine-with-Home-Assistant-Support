"""
config_core.py
Version: 2025.10.14.01
Description: Configuration core implementation for Lambda Execution Engine - REFACTORED
Split from monolithic file into: config_state.py, config_validator.py, config_loader.py, config_core.py

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
import time
from typing import Dict, Any
from threading import Lock

# Import helper modules from same directory
from config_state import ConfigurationState, ConfigurationVersion
from config_validator import ConfigurationValidator
from config_loader import (
    load_from_environment,
    load_from_file,
    apply_user_overrides,
    merge_configs
)


# ===== CORE IMPLEMENTATION =====

class ConfigurationCore:
    """Configuration system for Lambda Execution Engine core."""
    
    def __init__(self):
        self._config: Dict[str, Any] = {}
        self._state = ConfigurationState()
        self._validator = ConfigurationValidator()
        self._lock = Lock()
        self._cache_prefix = "config_"
        self._initialized = False
        self._use_parameter_store = False
        self._parameter_prefix = "/lambda-execution-engine"
    
    # ===== INITIALIZATION =====
    
    def initialize(self) -> Dict[str, Any]:
        """Initialize complete configuration system."""
        if self._initialized:
            from gateway import create_success_response
            return create_success_response("Already initialized", {
                "cached": True, 
                "version": self._state.current_version
            })
        
        try:
            from gateway import log_info, record_metric, create_success_response, create_error_response
            
            log_info("Initializing configuration system")
            
            # Load Parameter Store setting
            self._use_parameter_store = os.environ.get('USE_PARAMETER_STORE', 'false').lower() == 'true'
            self._parameter_prefix = os.environ.get('PARAMETER_PREFIX', '/lambda-execution-engine')
            
            # Load from environment using loader module
            system_config = load_from_environment(
                self._state.active_tier,
                self._use_parameter_store,
                self._parameter_prefix
            )
            
            # Apply user overrides using loader module
            self._config = apply_user_overrides(system_config)
            
            # Validate
            validation = self._validator.validate_all_sections(self._config)
            
            if validation.get("valid"):
                self._initialized = True
                self._state.last_reload_time = time.time()
                
                # Record version
                version = ConfigurationVersion(
                    version=self._state.current_version,
                    timestamp=time.time(),
                    changes={"initialized": True}
                )
                self._state.version_history.append(version)
                
                record_metric("config_initialization", 1.0, {
                    "success": True,
                    "version": self._state.current_version
                })
                
                log_info(f"Config initialized v{self._state.current_version}")
                return create_success_response("Initialized", {
                    "version": self._state.current_version,
                    "tier": self._state.active_tier.value,
                    "validation": validation,
                    "use_parameter_store": self._use_parameter_store
                })
            else:
                self._state.validation_failures += 1
                return create_error_response("Validation failed", validation)
                
        except Exception as e:
            from gateway import log_error, create_error_response
            log_error(f"Config initialization failed: {e}")
            self._state.validation_failures += 1
            return create_error_response("Init failed", {"error": str(e)})
    
    # ===== PARAMETER ACCESS WITH PARAMETER STORE SUPPORT =====
    
    def get_parameter(self, key: str, default: Any = None) -> Any:
        """Get configuration parameter from cache, environment, Parameter Store, or config dict."""
        from gateway import cache_get, cache_set
        
        # Try cache first
        cache_key = f"{self._cache_prefix}param_{key}"
        cached = cache_get(cache_key)
        if cached is not None:
            return cached
        
        # Try environment variable (highest priority)
        env_key = key.upper().replace('.', '_')
        env_value = os.environ.get(env_key)
        if env_value is not None:
            cache_set(cache_key, env_value, ttl=300)
            return env_value
        
        # Try Parameter Store if enabled
        if self._use_parameter_store:
            try:
                import boto3
                ssm = boto3.client('ssm')
                param_key = f"{self._parameter_prefix}/{key}"
                response = ssm.get_parameter(Name=param_key, WithDecryption=True)
                value = response['Parameter']['Value']
                cache_set(cache_key, value, ttl=300)
                return value
            except Exception:
                pass  # Fall through to config dict
        
        # Try nested config dict
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set_parameter(self, key: str, value: Any) -> bool:
        """Set configuration parameter with validation."""
        try:
            with self._lock:
                # Validate change
                is_valid, error = self._validator.validate_change(key, value)
                if not is_valid:
                    from gateway import log_warning
                    log_warning(f"Validation failed for {key}: {error}")
                    return False
                
                # Track as pending if critical
                if self._validator.is_critical(key):
                    self._state.pending_changes[key] = value
                    from gateway import log_info
                    log_info(f"Critical parameter {key} marked as pending (requires restart)")
                
                # Set value
                self._config[key] = value
                
                # Invalidate cache
                from gateway import cache_delete
                cache_delete(f"{self._cache_prefix}param_{key}")
                
                return True
                
        except Exception as e:
            from gateway import log_error
            log_error(f"Failed to set parameter {key}: {e}")
            return False
    
    # ===== PRESET MANAGEMENT =====
    
    def switch_preset(self, preset_name: str) -> Dict[str, Any]:
        """Switch to configuration preset."""
        try:
            from variables_utils import get_preset_configuration
            from gateway import log_info, create_success_response, create_error_response
            
            preset_config = get_preset_configuration(preset_name)
            
            if not preset_config:
                return create_error_response(f"Preset '{preset_name}' not found", {
                    "preset": preset_name
                })
            
            with self._lock:
                # Merge preset into current config using loader module
                self._config = merge_configs(self._config, preset_config)
                self._state.active_preset = preset_name
                
                # Record version change
                version = ConfigurationVersion(
                    version=self._state.current_version,
                    timestamp=time.time(),
                    changes={"preset_switch": preset_name}
                )
                self._state.version_history.append(version)
            
            log_info(f"Switched to preset: {preset_name}")
            return create_success_response(f"Switched to {preset_name}", {
                "preset": preset_name,
                "tier": self._state.active_tier.value
            })
            
        except Exception as e:
            from gateway import log_error, create_error_response
            log_error(f"Failed to switch preset: {e}")
            return create_error_response("Preset switch failed", {"error": str(e)})
    
    # ===== RELOAD =====
    
    def reload_config(self, validate: bool = True) -> Dict[str, Any]:
        """Reload configuration from all sources."""
        with self._lock:
            try:
                from gateway import log_info, create_success_response, create_error_response
                
                # Reload from environment using loader module
                system_config = load_from_environment(
                    self._state.active_tier,
                    self._use_parameter_store,
                    self._parameter_prefix
                )
                
                # Reapply user overrides using loader module
                new_config = apply_user_overrides(system_config)
                
                # Validate if requested
                if validate:
                    validation = self._validator.validate_all_sections(new_config)
                    if not validation.get("valid"):
                        self._state.validation_failures += 1
                        return create_error_response("Validation failed after reload", validation)
                
                # Apply new config
                self._config = new_config
                
                # Update state
                self._state.reload_count += 1
                self._state.last_reload_time = time.time()
                
                # Record version
                version = ConfigurationVersion(
                    version=self._state.current_version,
                    timestamp=time.time(),
                    changes={"reload": self._state.reload_count}
                )
                self._state.version_history.append(version)
                
                # Clear cache
                from gateway import cache_delete
                cache_delete(f"{self._cache_prefix}*")
                
                log_info(f"Configuration reloaded (count: {self._state.reload_count})")
                return create_success_response("Reloaded", {
                    "reload_count": self._state.reload_count,
                    "version": self._state.current_version
                })
                
            except Exception as e:
                from gateway import log_error, create_error_response
                log_error(f"Config reload failed: {e}")
                self._state.validation_failures += 1
                return create_error_response("Reload failed", {"error": str(e)})
    
    # ===== CATEGORY ACCESS =====
    
    def get_category_config(self, category: str) -> Dict[str, Any]:
        """Get configuration for specific category."""
        from gateway import cache_get, cache_set
        
        # Try cache first
        cache_key = f"{self._cache_prefix}category_{category}"
        cached = cache_get(cache_key)
        if cached is not None:
            return cached
        
        # Get from config
        category_config = self._config.get(category, {})
        
        # Cache result
        cache_set(cache_key, category_config, ttl=300)
        
        return category_config
    
    # ===== STATE =====
    
    def get_state(self) -> Dict[str, Any]:
        """Get current configuration state."""
        return {
            "version": self._state.current_version,
            "tier": self._state.active_tier.value,
            "preset": self._state.active_preset,
            "reload_count": self._state.reload_count,
            "last_reload": self._state.last_reload_time,
            "validation_failures": self._state.validation_failures,
            "initialized": self._initialized,
            "categories": list(self._config.keys()),
            "pending_changes": len(self._state.pending_changes),
            "version_history_count": len(self._state.version_history),
            "use_parameter_store": self._use_parameter_store
        }
    
    # ===== VALIDATION =====
    
    def validate_all_sections(self) -> Dict[str, Any]:
        """Validate all configuration sections."""
        return self._validator.validate_all_sections(self._config)
    
    # ===== FILE LOADING =====
    
    def load_from_file(self, filepath: str) -> Dict[str, Any]:
        """Load configuration from file using loader module."""
        return load_from_file(filepath)
    
    def load_from_environment(self) -> Dict[str, Any]:
        """Load configuration from environment using loader module."""
        return load_from_environment(
            self._state.active_tier,
            self._use_parameter_store,
            self._parameter_prefix
        )


# ===== SINGLETON INSTANCE =====

_config_core = ConfigurationCore()


# ===== GATEWAY IMPLEMENTATION FUNCTIONS =====

def _initialize_implementation() -> Dict[str, Any]:
    """Initialize configuration system."""
    return _config_core.initialize()


def _get_parameter_implementation(key: str, default: Any = None) -> Any:
    """Get configuration parameter."""
    return _config_core.get_parameter(key, default)


def _set_parameter_implementation(key: str, value: Any) -> bool:
    """Set configuration parameter."""
    return _config_core.set_parameter(key, value)


def _get_category_implementation(category: str) -> Dict[str, Any]:
    """Get category configuration."""
    return _config_core.get_category_config(category)


def _reload_implementation(validate: bool = True) -> Dict[str, Any]:
    """Reload configuration."""
    return _config_core.reload_config(validate)


def _switch_preset_implementation(preset_name: str) -> Dict[str, Any]:
    """Switch configuration preset."""
    return _config_core.switch_preset(preset_name)


def _get_state_implementation() -> Dict[str, Any]:
    """Get configuration state."""
    return _config_core.get_state()


def _load_environment_implementation() -> Dict[str, Any]:
    """Load configuration from environment."""
    return _config_core.load_from_environment()


def _load_file_implementation(filepath: str) -> Dict[str, Any]:
    """Load configuration from file."""
    return _config_core.load_from_file(filepath)


def _validate_all_implementation() -> Dict[str, Any]:
    """Validate all configuration sections."""
    return _config_core.validate_all_sections()


# ===== EXPORTS =====

__all__ = [
    'ConfigurationCore',
    '_config_core',
    '_initialize_implementation',
    '_get_parameter_implementation',
    '_set_parameter_implementation',
    '_get_category_implementation',
    '_reload_implementation',
    '_switch_preset_implementation',
    '_get_state_implementation',
    '_load_environment_implementation',
    '_load_file_implementation',
    '_validate_all_implementation'
]

# EOF
