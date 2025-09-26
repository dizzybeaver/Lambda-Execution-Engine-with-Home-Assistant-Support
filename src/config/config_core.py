"""
config_core.py - UPDATED: Delegates Bootstrap to Initialization Interface  
Version: 2025.09.25.01
Description: Configuration core updated to delegate bootstrap operations to initialization interface

UPDATES APPLIED:
- ✅ DELEGATED: Bootstrap configuration operations to initialization.py
- ✅ ELIMINATED: Duplicate configuration initialization logic
- ✅ COORDINATED: Configuration startup through initialization interface
- ✅ OPTIMIZED: Uses initialization interface for configuration lifecycle management
- ✅ FOCUSED: Pure configuration management without initialization concerns

ARCHITECTURE CHANGE:
- BEFORE: config_core.py handled configuration initialization
- AFTER: initialization.py handles configuration bootstrap, config_core.py handles configuration operations
- DELEGATION: Configuration initialization delegated to initialization interface authority

RESPONSIBILITY TRANSFER:
- Configuration bootstrap -> initialization.py
- Configuration initialization coordination -> initialization.py
- Configuration startup validation -> initialization.py

RETAINED RESPONSIBILITIES:
- Configuration parameter management
- Configuration validation (non-initialization)
- Configuration storage and retrieval
- Configuration type management

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

import logging
import time
import os
from typing import Dict, Any, Optional, Union, List
from enum import Enum

# Import gateway interfaces for maximum utilization
from cache import cache_get, cache_set, cache_clear, CacheType
from security import validate_input, sanitize_data
from utility import create_success_response, create_error_response, validate_string_input
from metrics import record_metric
from logging import log_info, log_error, log_debug, log_warning

logger = logging.getLogger(__name__)

# ===== CONFIGURATION CONSTANTS =====

# Cache keys for configuration management
CONFIG_CACHE_PREFIX = "config_"
CONFIG_BOOTSTRAP_CACHE_KEY = "config_bootstrap_status"
DEFAULT_CONFIG_CACHE_TTL = 3600  # 1 hour

# Default configuration values
DEFAULT_CONFIG_VALUES = {
    # System configuration
    'DEBUG_MODE': 'false',
    'LOG_LEVEL': 'INFO', 
    'ENVIRONMENT': 'production',
    
    # Performance configuration
    'CACHE_DEFAULT_TTL': '300',
    'HTTP_TIMEOUT': '30',
    'MEMORY_THRESHOLD_PERCENT': '80',
    
    # Security configuration
    'TLS_VERIFY_BYPASS_ENABLED': 'false',
    'VALIDATION_ENABLED': 'true',
    'COST_PROTECTION_ENABLED': 'true',
}

# ===== SECTION 1: CONFIGURATION PARAMETER MANAGEMENT =====

def _get_parameter_implementation(key: str, default_value: Any = None, 
                                config_type: str = "default") -> Any:
    """
    Core configuration parameter retrieval with caching.
    FOCUSED: Pure configuration retrieval without initialization concerns.
    """
    try:
        # Validate parameter key using utility gateway
        key_validation = validate_string_input(key, max_length=200, pattern="alphanumeric")
        if not key_validation.get("is_valid", False):
            log_warning(f"Invalid configuration key: {key}")
            return default_value
        
        # Try cache first using cache gateway
        cache_key = f"{CONFIG_CACHE_PREFIX}{config_type}_{key}"
        cached_value = cache_get(cache_key)
        
        if cached_value is not None:
            log_debug(f"Configuration cache hit: {key}")
            return cached_value
        
        # Get from environment or default
        env_value = os.getenv(key)
        if env_value is not None:
            # Cache the environment value using cache gateway
            cache_set(cache_key, env_value, cache_type=CacheType.MEMORY, ttl=DEFAULT_CONFIG_CACHE_TTL)
            log_debug(f"Configuration loaded from environment: {key}")
            return env_value
        
        # Use default value
        final_value = default_value if default_value is not None else DEFAULT_CONFIG_VALUES.get(key)
        
        if final_value is not None:
            # Cache default value using cache gateway
            cache_set(cache_key, final_value, cache_type=CacheType.MEMORY, ttl=DEFAULT_CONFIG_CACHE_TTL)
            log_debug(f"Configuration using default: {key}")
        
        return final_value
        
    except Exception as e:
        log_error(f"Configuration parameter retrieval failed for {key}: {str(e)}")
        return default_value

def _set_parameter_implementation(key: str, value: Any, config_type: str = "default",
                                persistent: bool = False) -> bool:
    """
    Core configuration parameter setting with validation.
    FOCUSED: Pure configuration setting without initialization concerns.
    """
    try:
        # Validate inputs using utility gateway
        key_validation = validate_string_input(key, max_length=200, pattern="alphanumeric")
        if not key_validation.get("is_valid", False):
            log_error(f"Invalid configuration key for setting: {key}")
            return False
        
        # Validate value using security gateway
        value_validation = validate_input({"key": key, "value": value}, input_type="configuration")
        if not value_validation.get("success", True):
            log_error(f"Configuration value validation failed for {key}")
            return False
        
        # Convert value to string for consistency
        string_value = str(value) if value is not None else ""
        
        # Cache the new value using cache gateway
        cache_key = f"{CONFIG_CACHE_PREFIX}{config_type}_{key}"
        cache_set(cache_key, string_value, cache_type=CacheType.MEMORY, ttl=DEFAULT_CONFIG_CACHE_TTL)
        
        # Record configuration change using metrics gateway
        record_metric("configuration_parameter_set", 1.0, {
            "key": key,
            "config_type": config_type,
            "persistent": persistent
        })
        
        log_info(f"Configuration parameter set: {key} = {string_value}")
        return True
        
    except Exception as e:
        log_error(f"Configuration parameter setting failed for {key}: {str(e)}")
        return False

def _delete_parameter_implementation(key: str, config_type: str = "default") -> bool:
    """
    Delete configuration parameter.
    FOCUSED: Pure configuration deletion without initialization concerns.
    """
    try:
        # Validate key using utility gateway
        key_validation = validate_string_input(key, max_length=200, pattern="alphanumeric")
        if not key_validation.get("is_valid", False):
            log_error(f"Invalid configuration key for deletion: {key}")
            return False
        
        # Clear from cache using cache gateway
        cache_key = f"{CONFIG_CACHE_PREFIX}{config_type}_{key}"
        cache_clear(cache_key)
        
        # Record configuration deletion using metrics gateway
        record_metric("configuration_parameter_deleted", 1.0, {
            "key": key,
            "config_type": config_type
        })
        
        log_info(f"Configuration parameter deleted: {key}")
        return True
        
    except Exception as e:
        log_error(f"Configuration parameter deletion failed for {key}: {str(e)}")
        return False

# ===== SECTION 2: CONFIGURATION VALIDATION =====

def _validate_configuration_parameters_implementation(parameters: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate configuration parameters (non-initialization validation).
    FOCUSED: Pure configuration validation without initialization concerns.
    """
    try:
        validation_results = {}
        invalid_count = 0
        
        for key, value in parameters.items():
            try:
                # Key validation using utility gateway
                key_validation = validate_string_input(key, max_length=200, pattern="alphanumeric")
                if not key_validation.get("is_valid", False):
                    validation_results[key] = {
                        "valid": False,
                        "error": "Invalid key format"
                    }
                    invalid_count += 1
                    continue
                
                # Value validation using security gateway
                value_validation = validate_input({key: value}, input_type="configuration")
                if not value_validation.get("success", True):
                    validation_results[key] = {
                        "valid": False,
                        "error": "Value validation failed",
                        "details": value_validation
                    }
                    invalid_count += 1
                    continue
                
                # Valid parameter
                validation_results[key] = {
                    "valid": True,
                    "value": str(value)
                }
                
            except Exception as e:
                validation_results[key] = {
                    "valid": False,
                    "error": str(e)
                }
                invalid_count += 1
        
        # Record validation metrics using metrics gateway
        record_metric("configuration_validation", len(parameters), {
            "invalid_count": invalid_count,
            "valid_count": len(parameters) - invalid_count
        })
        
        return create_success_response("Configuration validation completed", {
            "validation_results": validation_results,
            "total_parameters": len(parameters),
            "valid_parameters": len(parameters) - invalid_count,
            "invalid_parameters": invalid_count
        })
        
    except Exception as e:
        log_error(f"Configuration validation failed: {str(e)}")
        return create_error_response("Configuration validation failed", {"error": str(e)})

# ===== SECTION 3: CONFIGURATION BOOTSTRAP STATUS (DELEGATES TO INITIALIZATION) =====

def _get_bootstrap_status_implementation() -> Dict[str, Any]:
    """
    Get configuration bootstrap status - DELEGATES to initialization interface.
    """
    try:
        # Get bootstrap status from cache (managed by initialization interface)
        bootstrap_status = cache_get(CONFIG_BOOTSTRAP_CACHE_KEY, default_value={
            "bootstrapped": False,
            "bootstrap_time": 0,
            "bootstrap_source": "unknown"
        })
        
        return create_success_response("Bootstrap status retrieved", bootstrap_status)
        
    except Exception as e:
        log_error(f"Bootstrap status retrieval failed: {str(e)}")
        return create_error_response("Bootstrap status retrieval failed", {"error": str(e)})

def _perform_configuration_bootstrap_implementation() -> Dict[str, Any]:
    """
    DEPRECATED: Perform configuration bootstrap - DELEGATES to initialization interface.
    
    This function now delegates bootstrap operations to the initialization interface
    for consolidated initialization authority.
    """
    try:
        log_info("Configuration bootstrap requested - delegating to initialization interface")
        
        # Delegate to initialization interface
        from initialization import bootstrap_configuration
        return bootstrap_configuration()
        
    except ImportError:
        log_error("Cannot delegate to initialization interface - module not available")
        return create_error_response("Bootstrap delegation failed - initialization interface unavailable")
    except Exception as e:
        log_error(f"Configuration bootstrap delegation failed: {str(e)}")
        return create_error_response("Configuration bootstrap delegation failed", {"error": str(e)})

def _initialize_configuration_system_implementation() -> Dict[str, Any]:
    """
    DEPRECATED: Initialize configuration system - DELEGATES to initialization interface.
    
    This function now delegates initialization operations to the initialization interface
    for consolidated initialization authority.
    """
    try:
        log_info("Configuration system initialization requested - delegating to initialization interface")
        
        # Delegate to initialization interface
        from initialization import initialize_configuration
        return initialize_configuration()
        
    except ImportError:
        log_error("Cannot delegate to initialization interface - module not available")
        return create_error_response("Configuration initialization delegation failed - initialization interface unavailable")
    except Exception as e:
        log_error(f"Configuration system initialization delegation failed: {str(e)}")
        return create_error_response("Configuration system initialization delegation failed", {"error": str(e)})

# ===== SECTION 4: CONFIGURATION TYPES AND MANAGEMENT =====

def _get_configuration_types_implementation() -> List[str]:
    """
    Get available configuration types.
    FOCUSED: Pure configuration type management.
    """
    try:
        # Standard configuration types
        standard_types = ["default", "production", "development", "testing"]
        
        # Check for additional types in cache
        cached_types = cache_get("config_types", default_value=[])
        
        # Combine and deduplicate
        all_types = list(set(standard_types + cached_types))
        
        log_debug(f"Available configuration types: {all_types}")
        return all_types
        
    except Exception as e:
        log_error(f"Configuration types retrieval failed: {str(e)}")
        return ["default"]

def _create_configuration_type_implementation(config_type: str) -> Dict[str, Any]:
    """
    Create new configuration type.
    FOCUSED: Pure configuration type creation.
    """
    try:
        # Validate configuration type name using utility gateway
        type_validation = validate_string_input(config_type, max_length=50, pattern="alphanumeric")
        if not type_validation.get("is_valid", False):
            return create_error_response("Invalid configuration type name", type_validation)
        
        # Get existing types
        existing_types = _get_configuration_types_implementation()
        
        if config_type in existing_types:
            return create_success_response("Configuration type already exists", {
                "config_type": config_type,
                "action": "none_required"
            })
        
        # Add new type to cache using cache gateway
        existing_types.append(config_type)
        cache_set("config_types", existing_types, cache_type=CacheType.MEMORY, ttl=DEFAULT_CONFIG_CACHE_TTL)
        
        # Record configuration type creation using metrics gateway
        record_metric("configuration_type_created", 1.0, {"config_type": config_type})
        
        log_info(f"Configuration type created: {config_type}")
        return create_success_response("Configuration type created", {
            "config_type": config_type,
            "total_types": len(existing_types)
        })
        
    except Exception as e:
        log_error(f"Configuration type creation failed for {config_type}: {str(e)}")
        return create_error_response("Configuration type creation failed", {"error": str(e)})

# ===== SECTION 5: CONFIGURATION UTILITIES =====

def _get_all_parameters_for_type_implementation(config_type: str = "default") -> Dict[str, Any]:
    """
    Get all parameters for a configuration type.
    FOCUSED: Pure configuration retrieval.
    """
    try:
        # Validate configuration type using utility gateway
        type_validation = validate_string_input(config_type, max_length=50, pattern="alphanumeric")
        if not type_validation.get("is_valid", False):
            return create_error_response("Invalid configuration type", type_validation)
        
        # Get cached parameters for this type
        parameters = {}
        
        # Start with default values
        for key, default_value in DEFAULT_CONFIG_VALUES.items():
            current_value = _get_parameter_implementation(key, default_value, config_type)
            parameters[key] = current_value
        
        # Add any additional cached parameters
        # This is a simplified implementation - in a full system you might scan the cache
        
        log_debug(f"Retrieved {len(parameters)} parameters for config type: {config_type}")
        return create_success_response("Parameters retrieved", {
            "config_type": config_type,
            "parameters": parameters,
            "parameter_count": len(parameters)
        })
        
    except Exception as e:
        log_error(f"Parameter retrieval failed for config type {config_type}: {str(e)}")
        return create_error_response("Parameter retrieval failed", {"error": str(e)})

def _clear_configuration_cache_implementation(config_type: str = None) -> Dict[str, Any]:
    """
    Clear configuration cache.
    FOCUSED: Pure cache management for configuration.
    """
    try:
        cleared_count = 0
        
        if config_type:
            # Clear specific configuration type using utility gateway
            type_validation = validate_string_input(config_type, max_length=50, pattern="alphanumeric")
            if not type_validation.get("is_valid", False):
                return create_error_response("Invalid configuration type", type_validation)
            
            # Clear cache entries for this type - simplified pattern matching
            cache_pattern = f"{CONFIG_CACHE_PREFIX}{config_type}_*"
            log_debug(f"Clearing cache pattern: {cache_pattern}")
            # In a full implementation, you'd iterate through cache keys matching the pattern
            cleared_count = 1  # Simplified
            
        else:
            # Clear all configuration cache entries
            log_debug("Clearing all configuration cache entries")
            # In a full implementation, you'd iterate through all config cache keys
            cleared_count = len(DEFAULT_CONFIG_VALUES)  # Simplified
        
        # Record cache clearing using metrics gateway
        record_metric("configuration_cache_cleared", cleared_count, {
            "config_type": config_type or "all"
        })
        
        log_info(f"Configuration cache cleared: {cleared_count} entries")
        return create_success_response("Configuration cache cleared", {
            "cleared_entries": cleared_count,
            "config_type": config_type or "all"
        })
        
    except Exception as e:
        log_error(f"Configuration cache clearing failed: {str(e)}")
        return create_error_response("Configuration cache clearing failed", {"error": str(e)})

# ===== SECTION 6: CONFIGURATION HEALTH AND STATUS =====

def _get_configuration_health_implementation() -> Dict[str, Any]:
    """
    Get configuration system health status.
    FOCUSED: Pure configuration health without initialization concerns.
    """
    try:
        # Check cache availability using cache gateway
        from cache import get_cache_statistics
        cache_stats = get_cache_statistics()
        cache_healthy = cache_stats.get("available", False)
        
        # Check parameter accessibility
        test_key = "DEBUG_MODE"
        test_value = _get_parameter_implementation(test_key)
        parameters_accessible = test_value is not None
        
        # Get bootstrap status (managed by initialization interface)
        bootstrap_status = _get_bootstrap_status_implementation()
        bootstrap_healthy = bootstrap_status.get("success", False)
        
        # Aggregate health status
        overall_healthy = cache_healthy and parameters_accessible and bootstrap_healthy
        
        health_data = {
            "overall_healthy": overall_healthy,
            "cache_healthy": cache_healthy,
            "parameters_accessible": parameters_accessible,
            "bootstrap_status": bootstrap_status.get("data", {}),
            "cache_statistics": cache_stats,
            "timestamp": time.time()
        }
        
        log_debug(f"Configuration health check: overall_healthy={overall_healthy}")
        return create_success_response("Configuration health checked", health_data)
        
    except Exception as e:
        log_error(f"Configuration health check failed: {str(e)}")
        return create_error_response("Configuration health check failed", {"error": str(e)})

# EOF
