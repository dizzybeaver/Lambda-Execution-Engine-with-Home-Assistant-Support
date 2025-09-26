"""
variables.py - Ultra-Optimized Configuration System Core Data Structure
Version: 2025.09.26.01
Description: Four-tier configuration system with inheritance, override management, and resource constraint validation

ARCHITECTURE: EXTERNAL DATA FILE - PURE DATA STRUCTURE
- Accessed ONLY through config.py gateway
- Contains configuration data structures and constraint definitions
- No direct access from other files

CONFIGURATION TIER SYSTEM:
- MINIMUM: Survival mode - absolute lowest functional levels
- STANDARD: Production balance - proven configurations for typical use
- MAXIMUM: Performance mode - highest settings within 128MB constraint
- USER: Manual control - expert-level parameter-by-parameter configuration

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

from typing import Dict, Any, List, Optional, Union
from enum import Enum

# ===== CONFIGURATION TIER DEFINITIONS =====

class ConfigurationTier(Enum):
    """Configuration tier enumeration for four-tier system."""
    MINIMUM = "minimum"
    STANDARD = "standard" 
    MAXIMUM = "maximum"
    USER = "user"

class InterfaceType(Enum):
    """Interface type enumeration for configuration organization."""
    CACHE = "cache"
    LOGGING = "logging"
    METRICS = "metrics"
    SECURITY = "security"
    CIRCUIT_BREAKER = "circuit_breaker"
    SINGLETON = "singleton"
    LAMBDA = "lambda"
    HTTP_CLIENT = "http_client"
    UTILITY = "utility"
    INITIALIZATION = "initialization"

# ===== MEMORY CONSTRAINT DEFINITIONS =====

# AWS Lambda memory constraints (bytes)
AWS_LAMBDA_MEMORY_LIMIT = 128 * 1024 * 1024  # 128MB
AWS_MEMORY_SAFETY_BUFFER = 8 * 1024 * 1024   # 8MB safety buffer
AWS_AVAILABLE_MEMORY = AWS_LAMBDA_MEMORY_LIMIT - AWS_MEMORY_SAFETY_BUFFER  # 120MB usable

# CloudWatch constraints
AWS_CLOUDWATCH_METRIC_LIMIT = 10  # Maximum custom metrics per month (free tier)

# Memory allocation estimates (bytes) per interface component
INTERFACE_MEMORY_ESTIMATES = {
    InterfaceType.CACHE: {
        ConfigurationTier.MINIMUM: 1024 * 1024,      # 1MB
        ConfigurationTier.STANDARD: 4 * 1024 * 1024,  # 4MB
        ConfigurationTier.MAXIMUM: 16 * 1024 * 1024,  # 16MB
    },
    InterfaceType.LOGGING: {
        ConfigurationTier.MINIMUM: 512 * 1024,        # 512KB
        ConfigurationTier.STANDARD: 2 * 1024 * 1024,  # 2MB
        ConfigurationTier.MAXIMUM: 8 * 1024 * 1024,   # 8MB
    },
    InterfaceType.METRICS: {
        ConfigurationTier.MINIMUM: 256 * 1024,        # 256KB
        ConfigurationTier.STANDARD: 1024 * 1024,      # 1MB
        ConfigurationTier.MAXIMUM: 4 * 1024 * 1024,   # 4MB
    },
    InterfaceType.SECURITY: {
        ConfigurationTier.MINIMUM: 512 * 1024,        # 512KB
        ConfigurationTier.STANDARD: 1024 * 1024,      # 1MB
        ConfigurationTier.MAXIMUM: 3 * 1024 * 1024,   # 3MB
    },
    InterfaceType.CIRCUIT_BREAKER: {
        ConfigurationTier.MINIMUM: 256 * 1024,        # 256KB
        ConfigurationTier.STANDARD: 512 * 1024,       # 512KB
        ConfigurationTier.MAXIMUM: 1024 * 1024,       # 1MB
    },
    InterfaceType.SINGLETON: {
        ConfigurationTier.MINIMUM: 256 * 1024,        # 256KB
        ConfigurationTier.STANDARD: 512 * 1024,       # 512KB
        ConfigurationTier.MAXIMUM: 1024 * 1024,       # 1MB
    },
    InterfaceType.LAMBDA: {
        ConfigurationTier.MINIMUM: 512 * 1024,        # 512KB
        ConfigurationTier.STANDARD: 1024 * 1024,      # 1MB
        ConfigurationTier.MAXIMUM: 2 * 1024 * 1024,   # 2MB
    },
    InterfaceType.HTTP_CLIENT: {
        ConfigurationTier.MINIMUM: 512 * 1024,        # 512KB
        ConfigurationTier.STANDARD: 1024 * 1024,      # 1MB
        ConfigurationTier.MAXIMUM: 3 * 1024 * 1024,   # 3MB
    },
    InterfaceType.UTILITY: {
        ConfigurationTier.MINIMUM: 256 * 1024,        # 256KB
        ConfigurationTier.STANDARD: 512 * 1024,       # 512KB
        ConfigurationTier.MAXIMUM: 1024 * 1024,       # 1MB
    },
    InterfaceType.INITIALIZATION: {
        ConfigurationTier.MINIMUM: 256 * 1024,        # 256KB
        ConfigurationTier.STANDARD: 512 * 1024,       # 512KB
        ConfigurationTier.MAXIMUM: 1024 * 1024,       # 1MB
    }
}

# ===== CIRCUIT_BREAKER INTERFACE CONFIGURATION =====

CIRCUIT_BREAKER_CONFIGURATIONS = {
    ConfigurationTier.MINIMUM: {
        "circuit_breaker_enabled": True,
        "circuit_breaker_max_memory_mb": 0.25, # 256KB
        "failure_threshold": 10,          # Trips after 10 failures
        "recovery_timeout": 60,           # 1 minute recovery time
        "half_open_max_calls": 3,         # 3 test calls in half-open state
        "timeout_duration": 30,           # 30 second operation timeout
        "metrics_window": 60,             # 1 minute metrics window
        "minimum_throughput": 5,          # Minimum 5 calls before evaluation
        "error_threshold_percentage": 80, # 80% error rate trips breaker
        "slow_call_threshold": 10,        # 10 second slow call threshold
        "circuit_breaker_logging": False,
    },
    ConfigurationTier.STANDARD: {
        "circuit_breaker_enabled": True,
        "circuit_breaker_max_memory_mb": 0.5, # 512KB
        "failure_threshold": 5,           # Trips after 5 failures
        "recovery_timeout": 30,           # 30 second recovery time
        "half_open_max_calls": 5,         # 5 test calls in half-open state
        "timeout_duration": 20,           # 20 second operation timeout
        "metrics_window": 60,             # 1 minute metrics window
        "minimum_throughput": 10,         # Minimum 10 calls before evaluation
        "error_threshold_percentage": 60, # 60% error rate trips breaker
        "slow_call_threshold": 8,         # 8 second slow call threshold
        "circuit_breaker_logging": True,
    },
    ConfigurationTier.MAXIMUM: {
        "circuit_breaker_enabled": True,
        "circuit_breaker_max_memory_mb": 1,   # 1MB
        "failure_threshold": 3,           # Trips after 3 failures
        "recovery_timeout": 15,           # 15 second recovery time
        "half_open_max_calls": 10,        # 10 test calls in half-open state
        "timeout_duration": 15,           # 15 second operation timeout
        "metrics_window": 30,             # 30 second metrics window
        "minimum_throughput": 20,         # Minimum 20 calls before evaluation
        "error_threshold_percentage": 40, # 40% error rate trips breaker
        "slow_call_threshold": 5,         # 5 second slow call threshold
        "circuit_breaker_logging": True,
    }
}

# ===== SINGLETON INTERFACE CONFIGURATION =====

SINGLETON_CONFIGURATIONS = {
    ConfigurationTier.MINIMUM: {
        "singleton_enabled": True,
        "singleton_max_memory_mb": 0.25,  # 256KB
        "thread_safety_enabled": True,
        "memory_management_enabled": False,
        "lifecycle_management_enabled": False,
        "singleton_caching_enabled": False,
        "singleton_validation_enabled": False,
        "singleton_cleanup_enabled": False,
        "singleton_monitoring_enabled": False,
        "timeout_coordination": 10,       # 10 seconds
        "max_singleton_instances": 5,     # Limit singleton types
    },
    ConfigurationTier.STANDARD: {
        "singleton_enabled": True,
        "singleton_max_memory_mb": 0.5,   # 512KB
        "thread_safety_enabled": True,
        "memory_management_enabled": True,
        "lifecycle_management_enabled": True,
        "singleton_caching_enabled": True,
        "singleton_validation_enabled": True,
        "singleton_cleanup_enabled": True,
        "singleton_monitoring_enabled": False,
        "timeout_coordination": 15,       # 15 seconds
        "max_singleton_instances": 10,    # Standard singleton limit
    },
    ConfigurationTier.MAXIMUM: {
        "singleton_enabled": True,
        "singleton_max_memory_mb": 1,     # 1MB
        "thread_safety_enabled": True,
        "memory_management_enabled": True,
        "lifecycle_management_enabled": True,
        "singleton_caching_enabled": True,
        "singleton_validation_enabled": True,
        "singleton_cleanup_enabled": True,
        "singleton_monitoring_enabled": True,
        "timeout_coordination": 30,       # 30 seconds
        "max_singleton_instances": 15,    # Maximum singleton types
    }
}

# ===== LAMBDA INTERFACE CONFIGURATION =====

LAMBDA_CONFIGURATIONS = {
    ConfigurationTier.MINIMUM: {
        "lambda_enabled": True,
        "lambda_max_memory_mb": 0.5,      # 512KB
        "alexa_response_caching": False,
        "alexa_session_management": False,
        "response_templating": "simple",
        "error_handling_level": "basic",
        "lambda_optimization": False,
        "cold_start_optimization": False,
        "response_compression": False,
        "lambda_logging_level": "error",
        "alexa_context_preservation": False,
        "lambda_timeout": 10,             # 10 seconds
    },
    ConfigurationTier.STANDARD: {
        "lambda_enabled": True,
        "lambda_max_memory_mb": 1,        # 1MB
        "alexa_response_caching": True,
        "alexa_session_management": True,
        "response_templating": "standard",
        "error_handling_level": "standard",
        "lambda_optimization": True,
        "cold_start_optimization": True,
        "response_compression": True,
        "lambda_logging_level": "warning",
        "alexa_context_preservation": True,
        "lambda_timeout": 20,             # 20 seconds
    },
    ConfigurationTier.MAXIMUM: {
        "lambda_enabled": True,
        "lambda_max_memory_mb": 2,        # 2MB
        "alexa_response_caching": True,
        "alexa_session_management": True,
        "response_templating": "advanced",
        "error_handling_level": "comprehensive",
        "lambda_optimization": True,
        "cold_start_optimization": True,
        "response_compression": True,
        "lambda_logging_level": "info",
        "alexa_context_preservation": True,
        "lambda_timeout": 30,             # 30 seconds
    }
}

# ===== HTTP_CLIENT INTERFACE CONFIGURATION =====

HTTP_CLIENT_CONFIGURATIONS = {
    ConfigurationTier.MINIMUM: {
        "http_client_enabled": True,
        "http_client_max_memory_mb": 0.5, # 512KB
        "connection_pool_size": 2,        # Minimal connections
        "connection_timeout": 10,         # 10 seconds
        "read_timeout": 15,              # 15 seconds
        "retry_attempts": 1,             # Minimal retries
        "retry_backoff": "linear",
        "ssl_verification": False,        # Allow TLS bypass
        "http_compression": False,
        "connection_keepalive": False,
        "http_caching": False,
        "response_streaming": False,
        "aws_integration": True,
        "http_logging_level": "error",
    },
    ConfigurationTier.STANDARD: {
        "http_client_enabled": True,
        "http_client_max_memory_mb": 1,   # 1MB
        "connection_pool_size": 5,        # Standard connections
        "connection_timeout": 15,         # 15 seconds
        "read_timeout": 30,              # 30 seconds
        "retry_attempts": 3,             # Standard retries
        "retry_backoff": "exponential",
        "ssl_verification": False,        # Allow TLS bypass
        "http_compression": True,
        "connection_keepalive": True,
        "http_caching": True,
        "response_streaming": False,
        "aws_integration": True,
        "http_logging_level": "warning",
    },
    ConfigurationTier.MAXIMUM: {
        "http_client_enabled": True,
        "http_client_max_memory_mb": 3,   # 3MB
        "connection_pool_size": 10,       # Maximum connections
        "connection_timeout": 20,         # 20 seconds
        "read_timeout": 45,              # 45 seconds
        "retry_attempts": 5,             # Maximum retries
        "retry_backoff": "adaptive",
        "ssl_verification": False,        # Allow TLS bypass
        "http_compression": True,
        "connection_keepalive": True,
        "http_caching": True,
        "response_streaming": True,
        "aws_integration": True,
        "http_logging_level": "info",
    }
}

# ===== UTILITY INTERFACE CONFIGURATION =====

UTILITY_CONFIGURATIONS = {
    ConfigurationTier.MINIMUM: {
        "utility_enabled": True,
        "utility_max_memory_mb": 0.25,   # 256KB
        "validation_enabled": True,
        "validation_level": "basic",
        "response_formatting": "simple",
        "debugging_enabled": False,
        "testing_utilities": False,
        "utility_caching": False,
        "performance_utilities": False,
        "data_sanitization": "basic",
        "utility_logging_level": "error",
        "timeout_utilities": True,
        "memory_utilities": False,
    },
    ConfigurationTier.STANDARD: {
        "utility_enabled": True,
        "utility_max_memory_mb": 0.5,    # 512KB
        "validation_enabled": True,
        "validation_level": "standard",
        "response_formatting": "standard",
        "debugging_enabled": True,
        "testing_utilities": True,
        "utility_caching": True,
        "performance_utilities": True,
        "data_sanitization": "standard",
        "utility_logging_level": "warning",
        "timeout_utilities": True,
        "memory_utilities": True,
    },
    ConfigurationTier.MAXIMUM: {
        "utility_enabled": True,
        "utility_max_memory_mb": 1,      # 1MB
        "validation_enabled": True,
        "validation_level": "comprehensive",
        "response_formatting": "advanced",
        "debugging_enabled": True,
        "testing_utilities": True,
        "utility_caching": True,
        "performance_utilities": True,
        "data_sanitization": "comprehensive",
        "utility_logging_level": "info",
        "timeout_utilities": True,
        "memory_utilities": True,
    }
}

# ===== INITIALIZATION INTERFACE CONFIGURATION =====

INITIALIZATION_CONFIGURATIONS = {
    ConfigurationTier.MINIMUM: {
        "initialization_enabled": True,
        "initialization_max_memory_mb": 0.25, # 256KB
        "startup_optimization": "basic",
        "dependency_validation": False,
        "health_checks": "basic",
        "cold_start_optimization": False,
        "memory_initialization": False,
        "configuration_validation": "basic",
        "initialization_logging": "error",
        "cleanup_on_exit": False,
        "initialization_timeout": 10,    # 10 seconds
        "dependency_timeout": 5,         # 5 seconds
    },
    ConfigurationTier.STANDARD: {
        "initialization_enabled": True,
        "initialization_max_memory_mb": 0.5, # 512KB
        "startup_optimization": "standard",
        "dependency_validation": True,
        "health_checks": "standard",
        "cold_start_optimization": True,
        "memory_initialization": True,
        "configuration_validation": "standard",
        "initialization_logging": "warning",
        "cleanup_on_exit": True,
        "initialization_timeout": 20,    # 20 seconds
        "dependency_timeout": 10,        # 10 seconds
    },
    ConfigurationTier.MAXIMUM: {
        "initialization_enabled": True,
        "initialization_max_memory_mb": 1, # 1MB
        "startup_optimization": "advanced",
        "dependency_validation": True,
        "health_checks": "comprehensive",
        "cold_start_optimization": True,
        "memory_initialization": True,
        "configuration_validation": "comprehensive",
        "initialization_logging": "info",
        "cleanup_on_exit": True,
        "initialization_timeout": 30,    # 30 seconds
        "dependency_timeout": 15,        # 15 seconds
    }
}

# ===== CONFIGURATION VALIDATION FRAMEWORK =====

# Configuration compatibility matrix - defines which combinations are valid
CONFIGURATION_COMPATIBILITY_MATRIX = {
    # Memory constraint validation
    "memory_combinations": {
        "all_minimum": 8 * 1024 * 1024,      # 8MB - safe for all minimum
        "all_standard": 32 * 1024 * 1024,    # 32MB - safe for all standard  
        "all_maximum": 64 * 1024 * 1024,     # 64MB - safe for all maximum
        "mixed_safe": 48 * 1024 * 1024,      # 48MB - safe for mixed configs
        "danger_threshold": 100 * 1024 * 1024, # 100MB - approaching limit
    },
    
    # CloudWatch metric validation
    "metric_combinations": {
        "all_minimum": 3,     # All interfaces at minimum = 3 total metrics
        "all_standard": 7,    # All interfaces at standard = 7 total metrics
        "all_maximum": 10,    # All interfaces at maximum = 10 total metrics (limit)
    },
    
    # Performance impact validation
    "performance_combinations": {
        "low_impact": ["minimum", "standard_cache", "minimum_logging"],
        "medium_impact": ["standard", "maximum_cache", "standard_logging"],
        "high_impact": ["maximum", "maximum_cache", "maximum_logging"],
    }
}

# Invalid configuration combinations that exceed constraints
INVALID_COMBINATIONS = [
    # Memory constraint violations
    {
        "description": "All maximum tier exceeds memory limit",
        "pattern": {"all_interfaces": ConfigurationTier.MAXIMUM},
        "estimated_memory": 80 * 1024 * 1024,  # 80MB+ estimate
        "reason": "Exceeds 120MB usable memory limit"
    },
    
    # CloudWatch metric violations  
    {
        "description": "Too many high-metric configurations",
        "pattern": {"metrics_total": ">10"},
        "reason": "Exceeds 10 custom metric limit"
    },
    
    # Performance constraint violations
    {
        "description": "Conflicting performance requirements",
        "pattern": {"cache": ConfigurationTier.MAXIMUM, "memory_pressure": "high"},
        "reason": "High cache usage incompatible with memory pressure"
    }
]

# Configuration warnings for approaching limits
CONFIGURATION_WARNINGS = [
    {
        "threshold": "memory_90_percent",
        "message": "Configuration approaching 90% memory limit",
        "recommendation": "Consider reducing cache or logging memory allocation"
    },
    {
        "threshold": "metrics_8_plus",
        "message": "Using 8+ CloudWatch metrics approaching limit",
        "recommendation": "Consider metric rotation or reduction"
    },
    {
        "threshold": "performance_high",
        "message": "High performance configuration may impact cold starts",
        "recommendation": "Consider standard tier for better cold start performance"
    }
]

# ===== RESOURCE CONSTRAINT VALIDATION =====

def estimate_memory_usage(configuration_overrides: Dict[InterfaceType, ConfigurationTier]) -> int:
    """
    Estimate total memory usage for a configuration combination.
    Returns estimated memory usage in bytes.
    """
    total_memory = 0
    
    for interface_type, tier in configuration_overrides.items():
        if interface_type in INTERFACE_MEMORY_ESTIMATES:
            memory_estimate = INTERFACE_MEMORY_ESTIMATES[interface_type].get(tier, 0)
            total_memory += memory_estimate
    
    return total_memory

def estimate_cloudwatch_metrics(configuration_overrides: Dict[InterfaceType, ConfigurationTier]) -> int:
    """
    Estimate total CloudWatch metrics for a configuration combination.
    Returns estimated metric count.
    """
    total_metrics = 0
    
    for interface_type, tier in configuration_overrides.items():
        if interface_type == InterfaceType.METRICS:
            if tier == ConfigurationTier.MINIMUM:
                total_metrics += 3
            elif tier == ConfigurationTier.STANDARD:
                total_metrics += 7
            elif tier == ConfigurationTier.MAXIMUM:
                total_metrics += 10
    
    return total_metrics

def validate_configuration_constraints(configuration_overrides: Dict[InterfaceType, ConfigurationTier]) -> Dict[str, Any]:
    """
    Validate configuration against AWS constraints.
    Returns validation result with warnings and errors.
    """
    result = {
        "is_valid": True,
        "warnings": [],
        "errors": [],
        "memory_estimate": 0,
        "metric_estimate": 0
    }
    
    # Estimate resource usage
    memory_usage = estimate_memory_usage(configuration_overrides)
    metric_usage = estimate_cloudwatch_metrics(configuration_overrides)
    
    result["memory_estimate"] = memory_usage
    result["metric_estimate"] = metric_usage
    
    # Check memory constraints
    if memory_usage > AWS_AVAILABLE_MEMORY:
        result["is_valid"] = False
        result["errors"].append(f"Memory usage {memory_usage / 1024 / 1024:.1f}MB exceeds limit")
    elif memory_usage > (AWS_AVAILABLE_MEMORY * 0.9):
        result["warnings"].append(f"Memory usage {memory_usage / 1024 / 1024:.1f}MB approaching limit")
    
    # Check CloudWatch metric constraints
    if metric_usage > AWS_CLOUDWATCH_METRIC_LIMIT:
        result["is_valid"] = False
        result["errors"].append(f"Metric usage {metric_usage} exceeds {AWS_CLOUDWATCH_METRIC_LIMIT} limit")
    elif metric_usage > (AWS_CLOUDWATCH_METRIC_LIMIT * 0.8):
        result["warnings"].append(f"Metric usage {metric_usage} approaching limit")
    
    return result

# ===== OVERRIDE SYSTEM IMPLEMENTATION =====

def apply_configuration_overrides(base_tier: ConfigurationTier, 
                                overrides: Dict[InterfaceType, ConfigurationTier]) -> Dict[str, Any]:
    """
    Apply interface-specific tier overrides to a base configuration tier.
    Returns the merged configuration with overrides applied.
    """
    # Start with base tier configuration for all interfaces
    merged_config = {}
    
    # Get all configuration mappings
    config_mappings = {
        InterfaceType.CACHE: CACHE_CONFIGURATIONS,
        InterfaceType.LOGGING: LOGGING_CONFIGURATIONS,
        InterfaceType.METRICS: METRICS_CONFIGURATIONS,
        InterfaceType.SECURITY: SECURITY_CONFIGURATIONS,
        InterfaceType.CIRCUIT_BREAKER: CIRCUIT_BREAKER_CONFIGURATIONS,
        InterfaceType.SINGLETON: SINGLETON_CONFIGURATIONS,
        InterfaceType.LAMBDA: LAMBDA_CONFIGURATIONS,
        InterfaceType.HTTP_CLIENT: HTTP_CLIENT_CONFIGURATIONS,
        InterfaceType.UTILITY: UTILITY_CONFIGURATIONS,
        InterfaceType.INITIALIZATION: INITIALIZATION_CONFIGURATIONS,
    }
    
    # Apply base tier to all interfaces
    for interface_type, config_map in config_mappings.items():
        interface_name = interface_type.value
        tier_to_use = overrides.get(interface_type, base_tier)
        
        if tier_to_use in config_map:
            merged_config[interface_name] = config_map[tier_to_use].copy()
        else:
            # Fallback to standard if tier not found
            merged_config[interface_name] = config_map[ConfigurationTier.STANDARD].copy()
    
    return merged_config

def validate_override_combination(base_tier: ConfigurationTier,
                                overrides: Dict[InterfaceType, ConfigurationTier]) -> Dict[str, Any]:
    """
    Validate that an override combination is valid and safe.
    Returns validation result with compatibility assessment.
    """
    # Create full configuration map including base tier
    full_config = {interface: base_tier for interface in InterfaceType}
    full_config.update(overrides)
    
    # Validate against constraints
    constraint_validation = validate_configuration_constraints(full_config)
    
    # Additional override-specific validation
    result = {
        "is_valid": constraint_validation["is_valid"],
        "warnings": constraint_validation["warnings"].copy(),
        "errors": constraint_validation["errors"].copy(),
        "override_conflicts": [],
        "recommendations": []
    }
    
    # Check for specific override conflicts
    if (InterfaceType.CACHE in overrides and 
        overrides[InterfaceType.CACHE] == ConfigurationTier.MAXIMUM and
        InterfaceType.LOGGING in overrides and
        overrides[InterfaceType.LOGGING] == ConfigurationTier.MAXIMUM):
        result["override_conflicts"].append("Maximum cache + maximum logging may exceed memory")
        result["recommendations"].append("Consider standard tier for one of these interfaces")
    
    if (InterfaceType.METRICS in overrides and
        overrides[InterfaceType.METRICS] == ConfigurationTier.MAXIMUM):
        result["warnings"].append("Maximum metrics uses all 10 CloudWatch metric allowance")
        result["recommendations"].append("No other interfaces can use CloudWatch metrics")
    
    return result

# ===== TIER INHERITANCE SYSTEM =====

def get_interface_configuration(interface_type: InterfaceType, 
                              tier: ConfigurationTier) -> Dict[str, Any]:
    """
    Get configuration for a specific interface at a specific tier.
    Returns the configuration dictionary for the interface/tier combination.
    """
    config_mappings = {
        InterfaceType.CACHE: CACHE_CONFIGURATIONS,
        InterfaceType.LOGGING: LOGGING_CONFIGURATIONS,
        InterfaceType.METRICS: METRICS_CONFIGURATIONS,
        InterfaceType.SECURITY: SECURITY_CONFIGURATIONS,
        InterfaceType.CIRCUIT_BREAKER: CIRCUIT_BREAKER_CONFIGURATIONS,
        InterfaceType.SINGLETON: SINGLETON_CONFIGURATIONS,
        InterfaceType.LAMBDA: LAMBDA_CONFIGURATIONS,
        InterfaceType.HTTP_CLIENT: HTTP_CLIENT_CONFIGURATIONS,
        InterfaceType.UTILITY: UTILITY_CONFIGURATIONS,
        InterfaceType.INITIALIZATION: INITIALIZATION_CONFIGURATIONS,
    }
    
    if interface_type in config_mappings:
        config_map = config_mappings[interface_type]
        return config_map.get(tier, config_map[ConfigurationTier.STANDARD]).copy()
    
    return {}

def get_full_system_configuration(base_tier: ConfigurationTier = ConfigurationTier.STANDARD,
                                overrides: Optional[Dict[InterfaceType, ConfigurationTier]] = None) -> Dict[str, Any]:
    """
    Get complete system configuration with optional interface-specific overrides.
    Returns the full system configuration ready for use.
    """
    if overrides is None:
        overrides = {}
    
    # Validate the configuration combination
    validation = validate_override_combination(base_tier, overrides)
    
    if not validation["is_valid"]:
        # Return safe fallback configuration if invalid
        return get_full_system_configuration(ConfigurationTier.MINIMUM, {})
    
    # Apply overrides to get final configuration
    final_config = apply_configuration_overrides(base_tier, overrides)
    
    # Add metadata about the configuration
    final_config["_metadata"] = {
        "base_tier": base_tier.value,
        "overrides": {k.value: v.value for k, v in overrides.items()},
        "validation": validation,
        "memory_estimate": validation.get("memory_estimate", 0),
        "metric_estimate": validation.get("metric_estimate", 0),
        "generated_at": "runtime"
    }
    
    return final_config

# ===== CONFIGURATION PRESETS =====

# Predefined configurations for common use cases
CONFIGURATION_PRESETS = {
    "ultra_conservative": {
        "base_tier": ConfigurationTier.MINIMUM,
        "overrides": {},
        "description": "Absolute minimum resource usage - survival mode"
    },
    
    "production_balanced": {
        "base_tier": ConfigurationTier.STANDARD,
        "overrides": {},
        "description": "Balanced production configuration - recommended default"
    },
    
    "performance_optimized": {
        "base_tier": ConfigurationTier.STANDARD,
        "overrides": {
            InterfaceType.CACHE: ConfigurationTier.MAXIMUM,
            InterfaceType.METRICS: ConfigurationTier.MAXIMUM,
        },
        "description": "High performance with maximum cache and metrics"
    },
    
    "development_debug": {
        "base_tier": ConfigurationTier.STANDARD,
        "overrides": {
            InterfaceType.LOGGING: ConfigurationTier.MAXIMUM,
            InterfaceType.UTILITY: ConfigurationTier.MAXIMUM,
        },
        "description": "Enhanced logging and debugging for development"
    },
    
    "security_focused": {
        "base_tier": ConfigurationTier.STANDARD,
        "overrides": {
            InterfaceType.SECURITY: ConfigurationTier.MAXIMUM,
            InterfaceType.LOGGING: ConfigurationTier.MAXIMUM,
        },
        "description": "Maximum security validation and audit logging"
    },
    
    "resource_constrained": {
        "base_tier": ConfigurationTier.MINIMUM,
        "overrides": {
            InterfaceType.CACHE: ConfigurationTier.STANDARD,
        },
        "description": "Minimal resources with standard caching"
    }
}

# ===== RUNTIME CONFIGURATION SELECTION =====

def get_preset_configuration(preset_name: str) -> Dict[str, Any]:
    """
    Get a predefined configuration preset.
    Returns the complete configuration for the specified preset.
    """
    if preset_name not in CONFIGURATION_PRESETS:
        # Return default if preset not found
        preset_name = "production_balanced"
    
    preset = CONFIGURATION_PRESETS[preset_name]
    return get_full_system_configuration(
        preset["base_tier"],
        preset.get("overrides", {})
    )

def list_available_presets() -> List[Dict[str, str]]:
    """
    List all available configuration presets with descriptions.
    Returns list of preset information.
    """
    return [
        {
            "name": name,
            "description": preset["description"],
            "base_tier": preset["base_tier"].value
        }
        for name, preset in CONFIGURATION_PRESETS.items()
    ]

# EOF

# ===== CACHE INTERFACE CONFIGURATION =====

CACHE_CONFIGURATIONS = {
    ConfigurationTier.MINIMUM: {
        "cache_enabled": True,
        "cache_default_ttl": 60,          # 1 minute
        "cache_max_memory_mb": 1,         # 1MB total
        "cache_eviction_policy": "lru",
        "cache_cleanup_interval": 30,     # 30 seconds
        "cache_compression_enabled": False,
        "cache_encryption_enabled": False,
        "cache_statistics_enabled": False,
        "cache_prefetch_enabled": False,
        "cache_background_cleanup": False,
        "memory_pressure_threshold": 0.7,  # 70% memory usage triggers cleanup
    },
    ConfigurationTier.STANDARD: {
        "cache_enabled": True,
        "cache_default_ttl": 300,         # 5 minutes
        "cache_max_memory_mb": 4,         # 4MB total
        "cache_eviction_policy": "lru",
        "cache_cleanup_interval": 60,     # 1 minute
        "cache_compression_enabled": True,
        "cache_encryption_enabled": False,
        "cache_statistics_enabled": True,
        "cache_prefetch_enabled": True,
        "cache_background_cleanup": True,
        "memory_pressure_threshold": 0.8,  # 80% memory usage triggers cleanup
    },
    ConfigurationTier.MAXIMUM: {
        "cache_enabled": True,
        "cache_default_ttl": 1800,        # 30 minutes
        "cache_max_memory_mb": 16,        # 16MB total
        "cache_eviction_policy": "adaptive",
        "cache_cleanup_interval": 120,    # 2 minutes
        "cache_compression_enabled": True,
        "cache_encryption_enabled": True,
        "cache_statistics_enabled": True,
        "cache_prefetch_enabled": True,
        "cache_background_cleanup": True,
        "memory_pressure_threshold": 0.9,  # 90% memory usage triggers cleanup
    }
}

# ===== LOGGING INTERFACE CONFIGURATION =====

LOGGING_CONFIGURATIONS = {
    ConfigurationTier.MINIMUM: {
        "log_level": "ERROR",
        "log_format": "simple",
        "log_max_memory_mb": 0.5,         # 512KB
        "log_buffer_size": 10,            # 10 messages
        "log_flush_interval": 10,         # 10 seconds
        "structured_logging": False,
        "context_logging": False,
        "performance_logging": False,
        "debug_logging": False,
        "audit_logging": False,
        "cloudwatch_logging": True,
        "local_logging": False,
        "log_compression": False,
        "log_rotation_enabled": False,
    },
    ConfigurationTier.STANDARD: {
        "log_level": "WARNING",
        "log_format": "standard",
        "log_max_memory_mb": 2,           # 2MB
        "log_buffer_size": 50,            # 50 messages
        "log_flush_interval": 30,         # 30 seconds
        "structured_logging": True,
        "context_logging": True,
        "performance_logging": True,
        "debug_logging": False,
        "audit_logging": True,
        "cloudwatch_logging": True,
        "local_logging": False,
        "log_compression": True,
        "log_rotation_enabled": True,
    },
    ConfigurationTier.MAXIMUM: {
        "log_level": "INFO",
        "log_format": "detailed",
        "log_max_memory_mb": 8,           # 8MB
        "log_buffer_size": 200,           # 200 messages
        "log_flush_interval": 60,         # 1 minute
        "structured_logging": True,
        "context_logging": True,
        "performance_logging": True,
        "debug_logging": True,
        "audit_logging": True,
        "cloudwatch_logging": True,
        "local_logging": True,
        "log_compression": True,
        "log_rotation_enabled": True,
    }
}

# ===== METRICS INTERFACE CONFIGURATION =====

# Critical constraint: Only 10 CloudWatch metrics allowed per month (free tier)
METRICS_CONFIGURATIONS = {
    ConfigurationTier.MINIMUM: {
        "metrics_enabled": True,
        "metrics_max_memory_mb": 0.25,    # 256KB
        "cloudwatch_metrics_enabled": True,
        "cloudwatch_metric_count": 3,     # Only most critical metrics
        "local_metrics_enabled": False,
        "performance_metrics_enabled": False,
        "detailed_metrics_enabled": False,
        "cost_metrics_enabled": True,
        "health_metrics_enabled": True,
        "debug_metrics_enabled": False,
        "metric_collection_interval": 300, # 5 minutes
        "metric_buffer_size": 10,
        "metric_compression_enabled": False,
        "metric_aggregation_enabled": False,
        "priority_metrics": ["lambda_duration", "memory_usage", "error_rate"]
    },
    ConfigurationTier.STANDARD: {
        "metrics_enabled": True,
        "metrics_max_memory_mb": 1,       # 1MB
        "cloudwatch_metrics_enabled": True,
        "cloudwatch_metric_count": 7,     # Balanced metric usage
        "local_metrics_enabled": True,
        "performance_metrics_enabled": True,
        "detailed_metrics_enabled": False,
        "cost_metrics_enabled": True,
        "health_metrics_enabled": True,
        "debug_metrics_enabled": False,
        "metric_collection_interval": 180, # 3 minutes
        "metric_buffer_size": 50,
        "metric_compression_enabled": True,
        "metric_aggregation_enabled": True,
        "priority_metrics": ["lambda_duration", "memory_usage", "error_rate", "cache_hit_rate", 
                           "response_time", "cost_tracking", "invocation_count"]
    },
    ConfigurationTier.MAXIMUM: {
        "metrics_enabled": True,
        "metrics_max_memory_mb": 4,       # 4MB
        "cloudwatch_metrics_enabled": True,
        "cloudwatch_metric_count": 10,    # Full metric allowance
        "local_metrics_enabled": True,
        "performance_metrics_enabled": True,
        "detailed_metrics_enabled": True,
        "cost_metrics_enabled": True,
        "health_metrics_enabled": True,
        "debug_metrics_enabled": True,
        "metric_collection_interval": 60,  # 1 minute
        "metric_buffer_size": 200,
        "metric_compression_enabled": True,
        "metric_aggregation_enabled": True,
        "priority_metrics": ["lambda_duration", "memory_usage", "error_rate", "cache_hit_rate",
                           "response_time", "cost_tracking", "invocation_count", "optimization_score",
                           "resource_efficiency", "performance_index"]
    }
}

# ===== SECURITY INTERFACE CONFIGURATION =====

SECURITY_CONFIGURATIONS = {
    ConfigurationTier.MINIMUM: {
        "security_enabled": True,
        "security_max_memory_mb": 0.5,    # 512KB
        "input_validation_enabled": True,
        "input_validation_level": "basic",
        "threat_detection_enabled": False,
        "security_audit_enabled": False,
        "encryption_enabled": False,
        "tls_verify_bypass_enabled": True, # Allow bypass for compatibility
        "rate_limiting_enabled": False,
        "authentication_caching": False,
        "security_logging_level": "error",
        "sanitization_enabled": True,
        "sanitization_level": "basic",
        "security_timeout": 5,            # 5 seconds
        "pattern_matching_complexity": "simple",
    },
    ConfigurationTier.STANDARD: {
        "security_enabled": True,
        "security_max_memory_mb": 1,      # 1MB
        "input_validation_enabled": True,
        "input_validation_level": "standard",
        "threat_detection_enabled": True,
        "security_audit_enabled": True,
        "encryption_enabled": False,
        "tls_verify_bypass_enabled": True, # Allow bypass for compatibility
        "rate_limiting_enabled": True,
        "authentication_caching": True,
        "security_logging_level": "warning",
        "sanitization_enabled": True,
        "sanitization_level": "standard",
        "security_timeout": 10,           # 10 seconds
        "pattern_matching_complexity": "standard",
    },
    ConfigurationTier.MAXIMUM: {
        "security_enabled": True,
        "security_max_memory_mb": 3,      # 3MB
        "input_validation_enabled": True,
        "input_validation_level": "comprehensive",
        "threat_detection_enabled": True,
        "security_audit_enabled": True,
        "encryption_enabled": True,
        "tls_verify_bypass_enabled": True, # Allow bypass for compatibility
        "rate_limiting_enabled": True,
        "authentication_caching": True,
        "security_logging_level": "info",
        "sanitization_enabled": True,
        "sanitization_level": "comprehensive",
        "security_timeout": 15,           # 15 seconds
        "pattern_matching_complexity": "advanced",
    }
}

# EOS
