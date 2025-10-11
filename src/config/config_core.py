"""
config_core.py
Version: 2025.10.12.03
Description: COMPLETE consolidated configuration implementation - ENGINE CORE ONLY
Consolidates: config_core.py + config_manager.py + config_loader.py + config_extensions.py
Preserves: Parameter Store, validators, version tracking, preset loading, ALL functionality
NOTE: HA-specific config (ha_config.py) remains in Home Assistant Extension

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
import json
import time
from typing import Dict, Any, Optional, Callable, List, Set
from dataclasses import dataclass, field
from threading import Lock
from variables import ConfigurationTier


# ===== STATE MANAGEMENT =====

@dataclass
class ConfigurationVersion:
    """Track configuration version history."""
    version: str
    timestamp: float
    changes: Dict[str, Any]


@dataclass
class ConfigurationState:
    """Track configuration state."""
    current_version: str = "1.0.0"
    active_tier: ConfigurationTier = ConfigurationTier.STANDARD
    active_preset: Optional[str] = None
    version_history: List[ConfigurationVersion] = field(default_factory=list)
    pending_changes: Dict[str, Any] = field(default_factory=dict)
    last_reload_time: float = 0.0
    reload_count: int = 0
    validation_failures: int = 0


# ===== VALIDATION =====

class ConfigurationValidator:
    """Validates configuration changes with custom validators."""
    
    def __init__(self):
        self._validators: Dict[str, Callable] = {}
        self._critical_keys: Set[str] = {
            'aws_region', 'lambda_timeout', 'memory_limit',
            'configuration_tier', 'parameter_prefix'
        }
    
    def register_validator(self, key: str, validator: Callable):
        """Register custom validator for configuration key."""
        self._validators[key] = validator
    
    def validate_change(self, key: str, value: Any) -> tuple:
        """Validate configuration change."""
        if key in self._validators:
            return self._validators[key](value)
        return True, None
    
    def is_critical(self, key: str) -> bool:
        """Check if key is critical (requires restart)."""
        return key in self._critical_keys
    
    def validate_all_sections(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate all engine configuration sections."""
        validation = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "sections_validated": []
        }
        
        # Validate core categories
        core_categories = [
            'cache', 'logging', 'metrics', 'security', 
            'circuit_breaker', 'singleton', 'http_client',
            'lambda_opt', 'cost_protection', 'utility', 'initialization'
        ]
        
        for category in core_categories:
            if category in config:
                validation["sections_validated"].append(category)
                # Add specific validation logic per category if needed
        
        # Check for required system settings
        if 'system' in config:
            if 'aws_region' not in config['system']:
                validation["warnings"].append("aws_region not specified, using default")
        
        return validation


# ===== CORE IMPLEMENTATION =====

class ConfigurationCore:
    """COMPLETE consolidated configuration system for Lambda Execution Engine core."""
    
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
            
            # Load from environment
            system_config = self.load_from_environment()
            
            # Apply user overrides
            self._config = self.apply_user_overrides(system_config)
            
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
    
    # ===== LOADING FROM SOURCES =====
    
    def load_from_environment(self) -> Dict[str, Any]:
        """Load configuration from environment variables with tier support."""
        config = {
            "system": {
                "aws_region": os.environ.get('AWS_REGION', 'us-east-1'),
                "debug_mode": os.environ.get('DEBUG_MODE', 'false').lower() == 'true',
                "configuration_tier": os.environ.get('CONFIGURATION_TIER', 'standard'),
                "use_parameter_store": self._use_parameter_store,
                "parameter_prefix": self._parameter_prefix
            }
        }
        
        # Load tier configuration
        try:
            tier_name = config["system"]["configuration_tier"]
            self._state.active_tier = ConfigurationTier(tier_name)
            
            # Load tier-specific settings from variables.py
            from variables_utils import get_full_system_configuration
            tier_config = get_full_system_configuration(self._state.active_tier, {})
            
            # Merge tier config into base config (excluding metadata)
            for category, settings in tier_config.items():
                if category != '_metadata' and isinstance(settings, dict):
                    if category not in config:
                        config[category] = {}
                    config[category].update(settings)
            
        except Exception as e:
            from gateway import log_warning
            log_warning(f"Failed to load tier config: {e}")
        
        return config
    
    def load_from_file(self, filepath: str) -> Dict[str, Any]:
        """Load configuration from JSON file."""
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            from gateway import log_error
            log_error(f"Config file not found: {filepath}")
            return {}
        except json.JSONDecodeError as e:
            from gateway import log_error
            log_error(f"Invalid JSON in config file: {e}")
            return {}
        except Exception as e:
            from gateway import log_error
            log_error(f"Failed to load config file: {e}")
            return {}
    
    # ===== PARAMETER ACCESS WITH PARAMETER STORE SUPPORT =====
    
    def get_parameter(self, key: str, default: Any = None) -> Any:
        """Get configuration parameter from cache, environment, Parameter Store, or config dict."""
        from gateway import cache_get, cache_set
        
        # Try cache first
        cache_key = f"{self._cache_prefix}param_{key}"
        cached = cache_get(cache_key)
        if cached is not None:
            return cached
        
        # Try environment variable
        env_value = os.environ.get(key)
        if env_value is not None:
            cache_set(cache_key, env_value, ttl=300)
            return env_value
        
        # Try Parameter Store if enabled
        if self._use_parameter_store:
            param_value = self._get_from_parameter_store(key)
            if param_value is not None:
                cache_set(cache_key, param_value, ttl=300)
                return param_value
        
        # Try nested config value
        value = self._get_nested_value(self._config, key, default)
        
        # Cache if not default
        if value != default:
            cache_set(cache_key, value, ttl=300)
        
        return value
    
    def _get_from_parameter_store(self, key: str) -> Optional[Any]:
        """Get parameter from AWS Parameter Store."""
        try:
            import boto3
            
            # Build parameter name
            param_name = f"{self._parameter_prefix}/{key}"
            
            # Get parameter
            ssm = boto3.client('ssm', region_name=self._config.get('system', {}).get('aws_region', 'us-east-1'))
            response = ssm.get_parameter(
                Name=param_name,
                WithDecryption=True  # Always decrypt for security
            )
            
            return response['Parameter']['Value']
            
        except Exception as e:
            from gateway import log_debug
            log_debug(f"Parameter Store lookup failed for {key}: {e}")
            return None
    
    def _get_nested_value(self, config: Dict[str, Any], key: str, default: Any = None) -> Any:
        """Get nested value from config dictionary using dot notation."""
        keys = key.split('.')
        value = config
        
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
    
    # ===== USER OVERRIDES =====
    
    def apply_user_overrides(self, base_config: Dict[str, Any]) -> Dict[str, Any]:
        """Apply user custom configuration overrides."""
        try:
            from user_config import USER_CUSTOM_CONFIG
            
            if USER_CUSTOM_CONFIG:
                from gateway import log_info
                merged = self._merge_configs(base_config, USER_CUSTOM_CONFIG)
                log_info(f"Applied user config overrides: {len(USER_CUSTOM_CONFIG)} categories")
                return merged
                
        except ImportError:
            pass
        except Exception as e:
            from gateway import log_error
            log_error(f"Error applying user overrides: {e}")
        
        return base_config
    
    def _merge_configs(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """Deep merge configuration dictionaries."""
        merged = base.copy()
        
        for key, value in override.items():
            if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                merged[key] = self._merge_configs(merged[key], value)
            else:
                merged[key] = value
        
        return merged
    
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
                # Merge preset into current config
                self._config = self._merge_configs(self._config, preset_config)
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
                
                # Reload from environment
                system_config = self.load_from_environment()
                
                # Reapply user overrides
                new_config = self.apply_user_overrides(system_config)
                
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


# EOF
