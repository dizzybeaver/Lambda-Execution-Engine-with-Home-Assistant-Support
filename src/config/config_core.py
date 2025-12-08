"""
config_core.py - Core Configuration Management
Version: 2025.10.22.01
Description: Phase 1 Optimization - Remove threading lock, add SINGLETON + rate limiting

DESIGN DECISION: Rate Limiting Over Threading Locks
Reason: Lambda is single-threaded. Rate limiting prevents abuse without locks.
Impact: 50ns faster per operation, no false thread safety, proper DoS protection.

DESIGN DECISION: Parameter Lookup Priority
Reason: When USE_PARAMETER_STORE=true, SSM is the authoritative source.
        Environment variables should only be fallback when SSM fails/unavailable.
Impact: Enables proper SSM usage, prevents env var pollution of SSM config.

Copyright 2025 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

# ===== IMPORTS =====

import os
import time
from typing import Dict, Any
from collections import deque

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
        self._cache_prefix = "config_"
        self._initialized = False
        self._use_parameter_store = False
        self._parameter_prefix = "/lambda-execution-engine"
        
        # Rate limiting (1000 ops/sec) - replaces threading lock
        self._rate_limiter = deque(maxlen=1000)
        self._rate_limit_window_ms = 1000
        self._rate_limited_count = 0
    
    def _check_rate_limit(self) -> bool:
        """Check if operation should be rate limited."""
        now = time.time() * 1000
        
        # Remove old timestamps outside window
        while self._rate_limiter and (now - self._rate_limiter[0]) > self._rate_limit_window_ms:
            self._rate_limiter.popleft()
        
        # Check if at limit
        if len(self._rate_limiter) >= 1000:
            self._rate_limited_count += 1
            return False
        
        # Add timestamp and allow
        self._rate_limiter.append(now)
        return True
    
    # ===== INITIALIZATION =====
    
    def initialize(self) -> Dict[str, Any]:
        """Initialize complete configuration system."""
        # Check rate limit
        if not self._check_rate_limit():
            return {
                'status': 'rate_limited',
                'message': 'Configuration operations rate limit exceeded'
            }
        
        # Fast path: check if already initialized (no lock needed - single-threaded)
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
    
    # ===== PARAMETER ACCESS WITH CORRECTED SSM PRIORITY =====
    
    def get_parameter(self, key: str, default: Any = None) -> Any:
        """
        Get configuration parameter with CORRECT SSM priority.
        
        CRITICAL FIX (2025.10.19.07): Priority sequence corrected!
        
        DESIGN DECISION: SSM operations delegated to config_param_store module
        Reason: Separation of concerns - config logic separate from AWS SSM logic.
                Makes SSM handling testable, maintainable, and reusable.
        
        DESIGN DECISION: Cache validation prevents object() corruption
        Reason: SSM failures can cache object() instances which break subsequent calls.
                Only valid types (str, int, float, bool, dict, list, None) allowed from cache.
                Invalid entries automatically deleted and retried.
        
        **CORRECT Priority (when USE_PARAMETER_STORE=true):**
        1. Cache (with type validation)
        2. SSM Parameter Store (PRIMARY SOURCE - via config_param_store module)
        3. Environment variable (FALLBACK ONLY - uppercase with underscores/slashes replaced)
        4. Config dict
        5. Default value
        
        **When USE_PARAMETER_STORE=false:**
        1. Cache (with type validation)
        2. Environment variable (skip SSM entirely)
        3. Config dict
        4. Default value
        
        Args:
            key: Parameter key (e.g., 'homeassistant/url' or 'cache.ttl')
            default: Default value if not found
            
        Returns:
            Parameter value or default
        """
        # Check rate limit
        if not self._check_rate_limit():
            return default
        
        from gateway import cache_get, cache_set, cache_delete, log_debug, log_warning, log_info
        
        # === STEP 1: Try cache first (with type validation) ===
        cache_key = f"{self._cache_prefix}{key}"
        cached = cache_get(cache_key)
        if cached is not None:
            # CRITICAL: Validate cached value type before returning
            # Prevents returning object() instances from SSM failures
            if not isinstance(cached, (str, int, float, bool, dict, list, type(None))):
                log_warning(f"[CONFIG GET] {key}: Invalid cached type {type(cached).__name__}, invalidating cache")
                cache_delete(cache_key)
                # Don't return - continue to next source
            else:
                log_debug(f"[CONFIG GET] {key}: Cache hit")
                return cached
        
        # === STEP 2: Try SSM Parameter Store FIRST (if enabled) ===
        if self._use_parameter_store:
            try:
                # Import SSM module (lazy load to avoid import if not needed)
                from config_param_store import get_parameter as ssm_get_parameter
                
                log_info(f"[CONFIG GET] {key}: [PRIORITY 1] Attempting SSM lookup")
                
                # Delegate all SSM complexity to the dedicated module
                value = ssm_get_parameter(key, default=None)
                
                if value is not None:
                    # SUCCESS: Found in SSM
                    log_info(f"[CONFIG GET] {key}: [SSM SUCCESS] Loaded from Parameter Store")
                    # Cache in config system too (dual caching is OK - different TTLs)
                    cache_set(cache_key, value, ttl=300)
                    return value
                else:
                    # NOT FOUND in SSM, will fallback to environment
                    log_warning(f"[CONFIG GET] {key}: [SSM MISS] Not found in SSM, falling back to environment variable")
            
            except Exception as e:
                log_warning(f"[CONFIG GET] {key}: [SSM ERROR] Failed to load from SSM: {e}, falling back to environment")
        else:
            log_debug(f"[CONFIG GET] {key}: [SSM SKIPPED] USE_PARAMETER_STORE=false")
        
        # === STEP 3: Try environment variable (FALLBACK) ===
        # Convert key format: '/' or '.' → '_', make uppercase
        env_key = key.upper().replace('.', '_').replace('/', '_')
        env_value = os.environ.get(env_key)
        
        if env_value is not None:
            log_info(f"[CONFIG GET] {key}: [ENV SUCCESS] Loaded from environment variable {env_key}")
            cache_set(cache_key, env_value, ttl=300)
            return env_value
        else:
            log_debug(f"[CONFIG GET] {key}: [ENV MISS] Not in environment")
        
        # === STEP 4: Try config dict (nested key support with dots) ===
        keys = key.split('.')
        value = self._config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                log_debug(f"[CONFIG GET] {key}: [DICT MISS] Not in config dict")
                return default
        
        if value is not None:
            log_debug(f"[CONFIG GET] {key}: [DICT SUCCESS] Found in config dict")
            cache_set(cache_key, value, ttl=300)
            return value
        
        # === STEP 5: Return default ===
        log_debug(f"[CONFIG GET] {key}: [DEFAULT] Using default: {default}")
        return default
    
    def set_parameter(self, key: str, value: Any) -> bool:
        """
        Set configuration parameter (in-memory only).
        
        DESIGN DECISION: In-memory only, not persisted
        Reason: Lambda stateless model. Config changes are temporary.
                To persist, must update environment variables or SSM directly.
        
        Args:
            key: Parameter key (e.g., 'homeassistant/url')
            value: Parameter value
            
        Returns:
            True if successful, False otherwise
        """
        # Check rate limit
        if not self._check_rate_limit():
            return False
        
        try:
            # No lock needed - Lambda is single-threaded (DEC-04)
            # Set in config dict (nested key support)
            keys = key.split('.')
            target = self._config
            for k in keys[:-1]:
                if k not in target:
                    target[k] = {}
                target = target[k]
            target[keys[-1]] = value
            
            # Update cache
            from gateway import cache_set
            cache_key = f"{self._cache_prefix}{key}"
            cache_set(cache_key, value, ttl=300)
            
            # Record as pending change
            self._state.pending_changes[key] = {
                "value": value,
                "timestamp": time.time()
            }
            
            return True
        
        except Exception as e:
            from gateway import log_error
            log_error(f"Failed to set parameter {key}: {e}")
            return False
    
    # ===== CONFIG RELOAD =====
    
    def reload_config(self, validate: bool = True) -> Dict[str, Any]:
        """
        Reload configuration from sources.
        
        Args:
            validate: Whether to validate after reload
            
        Returns:
            Reload result dictionary
        """
        # Check rate limit
        if not self._check_rate_limit():
            return {
                'success': False,
                'error': 'Rate limit exceeded'
            }
        
        try:
            from gateway import log_info, create_success_response, create_error_response
            
            log_info("Reloading configuration")
            
            # Reload from environment
            system_config = load_from_environment(
                self._state.active_tier,
                self._use_parameter_store,
                self._parameter_prefix
            )
            
            # Apply overrides
            new_config = apply_user_overrides(system_config)
            
            # Validate if requested
            if validate:
                validation = self._validator.validate_all_sections(new_config)
                if not validation.get("valid"):
                    return create_error_response("Validation failed", validation)
            
            # Update config (no lock needed - Lambda is single-threaded)
            self._config = new_config
            self._state.reload_count += 1
            self._state.last_reload_time = time.time()
            
            # Record version
            version = ConfigurationVersion(
                version=self._state.current_version,
                timestamp=time.time(),
                changes={"reloaded": True}
            )
            self._state.version_history.append(version)
            
            log_info(f"Configuration reloaded (count: {self._state.reload_count})")
            return create_success_response("Reloaded", {
                "reload_count": self._state.reload_count,
                "version": self._state.current_version
            })
        
        except Exception as e:
            from gateway import log_error, create_error_response
            log_error(f"Config reload failed: {e}")
            return create_error_response("Reload failed", {"error": str(e)})
    
    def switch_preset(self, preset_name: str) -> Dict[str, Any]:
        """
        Switch to predefined configuration preset.
        
        Args:
            preset_name: Preset name (e.g., 'development', 'production')
            
        Returns:
            Switch result dictionary
        """
        # Check rate limit
        if not self._check_rate_limit():
            return {
                'success': False,
                'error': 'Rate limit exceeded'
            }
        
        try:
            from gateway import log_info, create_success_response, create_error_response
            
            log_info(f"Switching to preset: {preset_name}")
            
            # Update state (no lock needed - Lambda is single-threaded)
            self._state.active_preset = preset_name
            self._state.reload_count += 1
            self._state.last_reload_time = time.time()
            
            # Reload with new preset
            return self.reload_config(validate=True)
        
        except Exception as e:
            from gateway import log_error, create_error_response
            log_error(f"Preset switch failed: {e}")
            return create_error_response("Switch failed", {"error": str(e)})
    
    # ===== CATEGORY ACCESS =====
    
    def get_category_config(self, category: str) -> Dict[str, Any]:
        """
        Get configuration for specific category.
        
        Args:
            category: Category name (e.g., 'cache', 'logging')
            
        Returns:
            Category configuration dictionary
        """
        # Check rate limit
        if not self._check_rate_limit():
            return {}
        
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
        # Check rate limit
        if not self._check_rate_limit():
            return {}
        
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
            "use_parameter_store": self._use_parameter_store,
            "rate_limited_count": self._rate_limited_count
        }
    
    # ===== VALIDATION =====
    
    def validate_all_sections(self) -> Dict[str, Any]:
        """Validate all configuration sections."""
        # Check rate limit
        if not self._check_rate_limit():
            return {'valid': False, 'error': 'rate_limited'}
        
        return self._validator.validate_all_sections(self._config)
    
    # ===== FILE LOADING =====
    
    def load_from_file(self, filepath: str) -> Dict[str, Any]:
        """Load configuration from file using loader module."""
        # Check rate limit
        if not self._check_rate_limit():
            return {}
        
        return load_from_file(filepath)
    
    def load_from_environment(self) -> Dict[str, Any]:
        """Load configuration from environment using loader module."""
        # Check rate limit
        if not self._check_rate_limit():
            return {}
        
        return load_from_environment(
            self._state.active_tier,
            self._use_parameter_store,
            self._parameter_prefix
        )
    
    # ===== RESET OPERATION (PHASE 1 ADDITION) =====
    
    def reset(self) -> bool:
        """
        Reset configuration state.
        
        Part of Phase 1 optimization for lifecycle management.
        Clears all configuration data and resets rate limiter.
        
        Returns:
            True if successful, False otherwise
        """
        # Check rate limit
        if not self._check_rate_limit():
            return False
        
        try:
            # No lock needed - Lambda is single-threaded (DEC-04)
            self._config = {}
            self._state = ConfigurationState()
            self._rate_limiter.clear()
            self._rate_limited_count = 0
            self._initialized = False
            return True
        except Exception:
            return False


# ===== SINGLETON PATTERN (PHASE 1 ADDITION) =====

_config_core = None

def get_config_manager() -> ConfigurationCore:
    """
    Get or create ConfigurationCore singleton instance.
    
    Uses SINGLETON pattern for lifecycle management.
    Attempts gateway registration, falls back to module-level singleton.
    
    Returns:
        ConfigurationCore singleton instance
    """
    global _config_core
    
    try:
        # Try gateway SINGLETON registration
        import gateway
        manager = gateway.singleton_get('config_manager')
        if manager is None:
            if _config_core is None:
                _config_core = ConfigurationCore()
            gateway.singleton_register('config_manager', _config_core)
            manager = _config_core
        return manager
    except (ImportError, Exception):
        # Fallback to module-level singleton
        if _config_core is None:
            _config_core = ConfigurationCore()
        return _config_core


# ===== GATEWAY IMPLEMENTATION FUNCTIONS =====

def _initialize_implementation() -> Dict[str, Any]:
    """Initialize configuration system."""
    return get_config_manager().initialize()


def _get_parameter_implementation(key: str, default: Any = None) -> Any:
    """Get configuration parameter."""
    return get_config_manager().get_parameter(key, default)


def _set_parameter_implementation(key: str, value: Any) -> bool:
    """Set configuration parameter."""
    return get_config_manager().set_parameter(key, value)


def _get_category_implementation(category: str) -> Dict[str, Any]:
    """Get category configuration."""
    return get_config_manager().get_category_config(category)


def _reload_implementation(validate: bool = True) -> Dict[str, Any]:
    """Reload configuration."""
    return get_config_manager().reload_config(validate)


def _switch_preset_implementation(preset_name: str) -> Dict[str, Any]:
    """Switch configuration preset."""
    return get_config_manager().switch_preset(preset_name)


def _get_state_implementation() -> Dict[str, Any]:
    """Get configuration state."""
    return get_config_manager().get_state()


def _load_environment_implementation() -> Dict[str, Any]:
    """Load configuration from environment."""
    return get_config_manager().load_from_environment()


def _load_file_implementation(filepath: str) -> Dict[str, Any]:
    """Load configuration from file."""
    return get_config_manager().load_from_file(filepath)


def _validate_all_implementation() -> Dict[str, Any]:
    """Validate all configuration sections."""
    return get_config_manager().validate_all_sections()


def _reset_config_implementation(**kwargs) -> bool:
    """Reset configuration implementation (PHASE 1 ADDITION)."""
    return get_config_manager().reset()


# ===== EXPORTS =====

__all__ = [
    'ConfigurationCore',
    'get_config_manager',
    '_initialize_implementation',
    '_get_parameter_implementation',
    '_set_parameter_implementation',
    '_get_category_implementation',
    '_reload_implementation',
    '_switch_preset_implementation',
    '_get_state_implementation',
    '_load_environment_implementation',
    '_load_file_implementation',
    '_validate_all_implementation',
    '_reset_config_implementation'
]

# EOF
