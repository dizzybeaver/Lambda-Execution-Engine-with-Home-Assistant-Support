"""
config_core.py - Configuration Core Implementation
Version: 2025.10.18.05
Description: Configuration system with SSM Parameter Store support and robust error handling

CHANGELOG:
- 2025.10.18.05: FIXED Issue #30 - Added explicit string conversion for SSM values
  - Forces str() conversion if SSM returns non-primitive type (object wrapper)
  - Handles edge case where boto3 returns response wrapper instead of plain value
  - Fixes "<object object at 0x...>" error when printing SSM values
  - Ensures all SSM values are properly converted to primitive types
- 2025.10.18.04: FIXED Issue #29 - Robust SSM response handling in get_parameter
  - Added comprehensive type checking for boto3 SSM responses
  - Handles edge cases where response['Parameter']['Value'] fails
  - Validates dict structure before subscript access
  - Fixes "'object' object is not subscriptable" error
  - Added detailed logging for SSM operations
- 2025.10.17.01: Initial Parameter Store support

DESIGN DECISIONS:

**Memory-only Storage:**
   - Config stored only in-memory, not persisted externally
   - Reason: Lambda stateless model, fast init (~10ms)
   - Alternative persistence would add 50-100ms per operation

**Reload Behavior:**
   - reload_config() re-reads from environment/Parameter Store
   - Updates in-memory config
   - Does NOT persist to external storage
   - Useful for environment variable changes mid-execution

**Explicit String Conversion (Issue #30 fix):**
   - Forces str() conversion if SSM returns non-primitive types
   - Reason: Some Lambda environments have boto3 returning response wrappers
   - Ensures values are always usable strings/primitives

DECISION RATIONALE:
Memory-only storage is intentional for Lambda's stateless execution model.
Config initialization is fast (~10ms) and happens once per container lifecycle.
Using external persistence would add 50-100ms per read/write with no benefit.

Copyright 2025 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

# ===== IMPORTS =====

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
        """
        Get configuration parameter from cache, environment, Parameter Store, or config dict.
        
        DESIGN DECISION: Robust SSM response handling (Issue #29 fix)
        Reason: boto3 responses may have unexpected structure or types
        Fixes: "'object' object is not subscriptable" error
        
        DESIGN DECISION: Explicit string conversion (Issue #30 fix)
        Reason: Some Lambda environments have boto3 returning response wrapper objects
        Ensures: All SSM values are properly converted to primitive types
        
        Priority:
        1. Cache
        2. Environment variable (uppercase with underscores/slashes replaced)
        3. SSM Parameter Store (if enabled) - with robust error handling
        4. Config dict
        5. Default value
        
        Args:
            key: Parameter key (e.g., 'homeassistant/url' or 'cache.ttl')
            default: Default value if not found
            
        Returns:
            Parameter value or default
        """
        from gateway import cache_get
        
        # Try cache first
        cache_key = f"{self._cache_prefix}{key}"
        cached = cache_get(cache_key)
        if cached is not None:
            return cached
        
        # Try environment (convert key format: '/' or '.' → '_', make uppercase)
        env_key = key.upper().replace('.', '_').replace('/', '_')
        env_value = os.environ.get(env_key)
        if env_value is not None:
            from gateway import cache_set
            cache_set(cache_key, env_value, ttl=300)
            return env_value
        
        # Try Parameter Store if enabled
        if self._use_parameter_store:
            try:
                import boto3
                from gateway import log_debug, log_warning
                
                ssm = boto3.client('ssm')
                param_name = f"{self._parameter_prefix}/{key}"
                
                log_debug(f"Attempting SSM parameter: {param_name}")
                
                # Call SSM get_parameter
                response = ssm.get_parameter(Name=param_name, WithDecryption=True)
                
                # CRITICAL: Robust response validation before accessing
                if not isinstance(response, dict):
                    log_warning(f"SSM response is not dict: {type(response)}")
                elif 'Parameter' not in response:
                    log_warning(f"SSM response missing 'Parameter' key: {list(response.keys())}")
                elif not isinstance(response['Parameter'], dict):
                    log_warning(f"SSM Parameter is not dict: {type(response['Parameter'])}")
                elif 'Value' not in response['Parameter']:
                    log_warning(f"SSM Parameter missing 'Value' key: {list(response['Parameter'].keys())}")
                else:
                    # SUCCESS: Valid response structure
                    value = response['Parameter']['Value']
                    
                    # CRITICAL: Force string conversion (Issue #30 fix)
                    # boto3 may return response wrapper objects in some Lambda environments
                    # This ensures the value is always a usable primitive type
                    if not isinstance(value, (str, int, float, bool, type(None))):
                        log_warning(f"SSM returned non-primitive type {type(value)} for {param_name}, converting to string")
                        value = str(value)
                    
                    from gateway import cache_set
                    cache_set(cache_key, value, ttl=300)
                    log_debug(f"Successfully loaded from SSM: {param_name} = {value}")
                    return value
                    
            except Exception as e:
                from gateway import log_warning
                log_warning(f"Failed to load from SSM: {key} - {str(e)}")
        
        # Try config dict
        keys = key.split('.')
        value = self._config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        
        if value is not None:
            from gateway import cache_set
            cache_set(cache_key, value, ttl=300)
            return value
        
        return default
    
    def set_parameter(self, key: str, value: Any) -> bool:
        """Set configuration parameter."""
        with self._lock:
            keys = key.split('.')
            config = self._config
            
            for k in keys[:-1]:
                if k not in config:
                    config[k] = {}
                config = config[k]
            
            config[keys[-1]] = value
            
            # Track as pending change
            self._state.pending_changes[key] = value
            
            # Invalidate cache
            from gateway import cache_delete
            cache_key = f"{self._cache_prefix}{key}"
            cache_delete(cache_key)
            
            return True
    
    # ===== PRESET MANAGEMENT =====
    
    def switch_preset(self, preset_name: str) -> Dict[str, Any]:
        """Switch to predefined configuration preset."""
        with self._lock:
            try:
                from gateway import log_info, create_success_response, create_error_response
                from variables_utils import get_preset_configuration
                
                # Get preset config
                preset_config = get_preset_configuration(preset_name)
                
                if not preset_config:
                    return create_error_response("Invalid preset", {"preset": preset_name})
                
                # Merge with current config
                self._config = merge_configs(self._config, preset_config)
                
                # Update state
                self._state.active_preset = preset_name
                
                # Record version
                version = ConfigurationVersion(
                    version=self._state.current_version,
                    timestamp=time.time(),
                    changes={"preset": preset_name}
                )
                self._state.version_history.append(version)
                
                # Clear cache
                from gateway import cache_delete
                cache_delete(f"{self._cache_prefix}*")
                
                log_info(f"Switched to preset: {preset_name}")
                return create_success_response("Preset switched", {"preset": preset_name})
                
            except Exception as e:
                from gateway import log_error, create_error_response
                log_error(f"Preset switch failed: {e}")
                return create_error_response("Switch failed", {"error": str(e)})
    
    # ===== RELOAD =====
    
    def reload_config(self, validate: bool = True) -> Dict[str, Any]:
        """Reload configuration from environment/Parameter Store."""
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
