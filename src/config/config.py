"""
config.py - ULTRA-OPTIMIZED: Configuration Gateway with Four-Tier Configuration System
Version: 2025.09.26.01
Description: Enhanced configuration gateway with ultra-optimized four-tier configuration system and TLS configurability

ARCHITECTURE: PRIMARY GATEWAY - ULTRA-PURE DELEGATION
- config.py (this file) = Gateway/Firewall - function declarations ONLY
- config_core.py = Core configuration logic using all gateway interfaces
- config_http.py = HTTP-specific configuration implementation
- variables.py = External data file with configuration structures

PHASE 1 ENHANCEMENTS:
- Four-tier configuration system (MINIMUM/STANDARD/MAXIMUM/USER)
- Interface-specific configuration overrides
- Resource constraint validation (128MB memory, 10 CloudWatch metrics)
- Configuration presets for common use cases
- Memory estimation and AWS limit checking
- Override validation and conflict detection

ENHANCED SECURITY CONFIGURATION VARIABLES:
- SECURITY_STRICT_CERT_VALIDATION: Force certificate chain validation (true/false)
- SECURITY_SANITIZE_ERRORS: Remove sensitive details from error responses (true/false)
- RATE_LIMITING_ENABLED: Enable authentication rate limiting (true/false)
- CACHE_ENCRYPTION_ENABLED: Encrypt sensitive cached data (true/false)
- TLS_VERIFY_BYPASS_ENABLED: Allow TLS verification bypass for certificates (true/false)
- SECURITY_THREAT_DETECTION_ENABLED: Enable enhanced threat pattern detection (true/false)
- AUTH_TOKEN_EXPIRATION_CHECK: Enable token expiration validation (true/false)
- SECURITY_AUDIT_COMPREHENSIVE: Enable comprehensive security audit logging (true/false)

RATE LIMITING CONFIGURATION:
- RATE_LIMIT_PER_MINUTE: Request rate limit per minute (10-1000)
- RATE_LIMIT_PER_HOUR: Hourly rate limit (100-10000)
- RATE_LIMIT_AUTHENTICATION_PER_MINUTE: Auth-specific per-minute limit (5-100)
- RATE_LIMIT_EMERGENCY_THRESHOLD: Threshold for emergency rate limiting (1000-10000)

CACHE SECURITY CONFIGURATION:
- CACHE_ENCRYPTION_KEY_ROTATION_DAYS: Encryption key rotation interval (7-365)
- CACHE_SECURE_TTL_OVERRIDE: Override TTL for secure cache types (300-7200)

ULTRA-OPTIMIZED CONFIGURATION SYSTEM USAGE:
- get_tier_configuration(tier, overrides) - Get full system configuration
- get_interface_configuration(interface, tier) - Get specific interface config
- validate_configuration(base_tier, overrides) - Validate configuration constraints
- get_preset_configuration(preset_name) - Get predefined configuration
- estimate_resource_usage(overrides) - Estimate memory and metric usage
- list_configuration_presets() - List available presets

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

from typing import Dict, Any, Optional, Union, List
from enum import Enum

# Import configuration data structures from variables.py
from .variables import (
    ConfigurationTier,
    InterfaceType,
    get_full_system_configuration,
    get_interface_configuration,
    validate_override_combination,
    get_preset_configuration,
    list_available_presets,
    estimate_memory_usage,
    estimate_cloudwatch_metrics,
    validate_configuration_constraints
)

# ===== SECTION 1: EXISTING CONFIGURATION FUNCTIONS =====

# Configuration Manager
def get_configuration_manager():
    """PURE DELEGATION: Get configuration manager singleton."""
    from .config_core import _get_configuration_manager_implementation
    return _get_configuration_manager_implementation()

def reset_configuration_manager():
    """PURE DELEGATION: Reset configuration manager."""
    from .config_core import _reset_configuration_manager_implementation
    return _reset_configuration_manager_implementation()

def reload_configuration():
    """PURE DELEGATION: Reload configuration from sources."""
    from .config_core import _reload_configuration_implementation
    return _reload_configuration_implementation()

# Parameter Management
def get_parameter(key: str, default_value: Any = None, config_type: str = "default") -> Any:
    """PURE DELEGATION: Get configuration parameter."""
    from .config_core import _get_parameter_implementation
    return _get_parameter_implementation(key, default_value, config_type)

def set_parameter(key: str, value: Any, config_type: str = "default", persistent: bool = False) -> bool:
    """PURE DELEGATION: Set configuration parameter."""
    from .config_core import _set_parameter_implementation
    return _set_parameter_implementation(key, value, config_type, persistent)

def delete_parameter(key: str, config_type: str = "default") -> bool:
    """PURE DELEGATION: Delete configuration parameter."""
    from .config_core import _delete_parameter_implementation
    return _delete_parameter_implementation(key, config_type)

def get_all_parameters(config_type: str = "default") -> Dict[str, Any]:
    """PURE DELEGATION: Get all configuration parameters."""
    from .config_core import _get_all_parameters_implementation
    return _get_all_parameters_implementation(config_type)

def validate_parameter(key: str, value: Any) -> Dict[str, Any]:
    """PURE DELEGATION: Validate configuration parameter."""
    from .config_core import _validate_parameter_implementation
    return _validate_parameter_implementation(key, value)

# Environment Configuration
def get_environment() -> str:
    """PURE DELEGATION: Get current environment."""
    from .config_core import _get_environment_implementation
    return _get_environment_implementation()

def set_environment(environment: str) -> bool:
    """PURE DELEGATION: Set current environment."""
    from .config_core import _set_environment_implementation
    return _set_environment_implementation(environment)

def is_production() -> bool:
    """PURE DELEGATION: Check if production environment."""
    from .config_core import _is_production_implementation
    return _is_production_implementation()

def is_debug_mode() -> bool:
    """PURE DELEGATION: Check if debug mode enabled."""
    from .config_core import _is_debug_mode_implementation
    return _is_debug_mode_implementation()

def set_debug_mode(enabled: bool) -> bool:
    """PURE DELEGATION: Set debug mode."""
    from .config_core import _set_debug_mode_implementation
    return _set_debug_mode_implementation(enabled)

def get_debug_level() -> str:
    """PURE DELEGATION: Get debug level."""
    from .config_core import _get_debug_level_implementation
    return _get_debug_level_implementation()

def set_debug_level(level: str) -> bool:
    """PURE DELEGATION: Set debug level."""
    from .config_core import _set_debug_level_implementation
    return _set_debug_level_implementation(level)

# AWS Configuration
def get_aws_region() -> str:
    """PURE DELEGATION: Get AWS region."""
    from .config_core import _get_aws_region_implementation
    return _get_aws_region_implementation()

def set_aws_region(region: str) -> bool:
    """PURE DELEGATION: Set AWS region."""
    from .config_core import _set_aws_region_implementation
    return _set_aws_region_implementation(region)

def get_aws_profile() -> str:
    """PURE DELEGATION: Get AWS profile."""
    from .config_core import _get_aws_profile_implementation
    return _get_aws_profile_implementation()

def set_aws_profile(profile: str) -> bool:
    """PURE DELEGATION: Set AWS profile."""
    from .config_core import _set_aws_profile_implementation
    return _set_aws_profile_implementation(profile)

def get_aws_config() -> Dict[str, Any]:
    """PURE DELEGATION: Get AWS configuration."""
    from .config_core import _get_aws_config_implementation
    return _get_aws_config_implementation()

def validate_aws_region(region: str) -> bool:
    """PURE DELEGATION: Validate AWS region."""
    from .config_core import _validate_aws_region_implementation
    return _validate_aws_region_implementation(region)

def get_supported_regions() -> List[str]:
    """PURE DELEGATION: Get supported AWS regions."""
    from .config_core import _get_supported_regions_implementation
    return _get_supported_regions_implementation()

# HTTP Client Configuration
def get_http_timeout() -> int:
    """PURE DELEGATION: Get HTTP timeout."""
    from .config_http import _get_global_http_timeout_implementation
    return _get_global_http_timeout_implementation()

def set_http_timeout(timeout: int) -> bool:
    """PURE DELEGATION: Set HTTP timeout."""
    from .config_http import _set_global_http_timeout_implementation
    return _set_global_http_timeout_implementation(timeout)

def get_http_retry_policy() -> Dict[str, Any]:
    """PURE DELEGATION: Get HTTP retry policy."""
    from .config_http import _get_retry_policy_implementation
    return _get_retry_policy_implementation()

def set_http_retry_policy(policy: Dict[str, Any]) -> bool:
    """PURE DELEGATION: Set HTTP retry policy."""
    from .config_http import _set_retry_policy_implementation
    return _set_retry_policy_implementation(policy)

def get_http_connection_pool_size() -> int:
    """PURE DELEGATION: Get HTTP connection pool size."""
    from .config_http import _get_connection_pool_size_implementation
    return _get_connection_pool_size_implementation()

def set_http_connection_pool_size(size: int) -> bool:
    """PURE DELEGATION: Set HTTP connection pool size."""
    from .config_http import _set_connection_pool_size_implementation
    return _set_connection_pool_size_implementation(size)

def should_verify_ssl() -> bool:
    """PURE DELEGATION: Check SSL verification setting."""
    from .config_http import _should_verify_ssl_implementation
    return _should_verify_ssl_implementation()

def set_ssl_verification(verify: bool) -> bool:
    """PURE DELEGATION: Set SSL verification."""
    from .config_http import _set_ssl_verification_implementation
    return _set_ssl_verification_implementation(verify)

def get_http_headers() -> Dict[str, str]:
    """PURE DELEGATION: Get default HTTP headers."""
    from .config_http import _get_default_headers_implementation
    return _get_default_headers_implementation()

def set_http_header(key: str, value: str) -> bool:
    """PURE DELEGATION: Set HTTP header."""
    from .config_http import _add_default_header_implementation
    return _add_default_header_implementation(key, value)

# Cache Configuration
def get_cache_ttl() -> int:
    """PURE DELEGATION: Get cache TTL."""
    from .config_core import _get_cache_ttl_implementation
    return _get_cache_ttl_implementation()

def set_cache_ttl(ttl: int) -> bool:
    """PURE DELEGATION: Set cache TTL."""
    from .config_core import _set_cache_ttl_implementation
    return _set_cache_ttl_implementation(ttl)

def get_cache_max_size() -> int:
    """PURE DELEGATION: Get cache max size."""
    from .config_core import _get_cache_max_size_implementation
    return _get_cache_max_size_implementation()

def set_cache_max_size(size: int) -> bool:
    """PURE DELEGATION: Set cache max size."""
    from .config_core import _set_cache_max_size_implementation
    return _set_cache_max_size_implementation(size)

def get_cache_eviction_policy() -> str:
    """PURE DELEGATION: Get cache eviction policy."""
    from .config_core import _get_cache_eviction_policy_implementation
    return _get_cache_eviction_policy_implementation()

def set_cache_eviction_policy(policy: str) -> bool:
    """PURE DELEGATION: Set cache eviction policy."""
    from .config_core import _set_cache_eviction_policy_implementation
    return _set_cache_eviction_policy_implementation(policy)

def is_cache_enabled() -> bool:
    """PURE DELEGATION: Check if cache is enabled."""
    from .config_core import _is_cache_enabled_implementation
    return _is_cache_enabled_implementation()

def set_cache_enabled(enabled: bool) -> bool:
    """PURE DELEGATION: Set cache enabled."""
    from .config_core import _set_cache_enabled_implementation
    return _set_cache_enabled_implementation(enabled)

# Logging Configuration
def get_log_level() -> str:
    """PURE DELEGATION: Get log level."""
    from .config_core import _get_log_level_implementation
    return _get_log_level_implementation()

def set_log_level(level: str) -> bool:
    """PURE DELEGATION: Set log level."""
    from .config_core import _set_log_level_implementation
    return _set_log_level_implementation(level)

def get_log_format() -> str:
    """PURE DELEGATION: Get log format."""
    from .config_core import _get_log_format_implementation
    return _get_log_format_implementation()

def set_log_format(format_str: str) -> bool:
    """PURE DELEGATION: Set log format."""
    from .config_core import _set_log_format_implementation
    return _set_log_format_implementation(format_str)

def is_structured_logging_enabled() -> bool:
    """PURE DELEGATION: Check if structured logging is enabled."""
    from .config_core import _is_structured_logging_enabled_implementation
    return _is_structured_logging_enabled_implementation()

def set_structured_logging(enabled: bool) -> bool:
    """PURE DELEGATION: Set structured logging."""
    from .config_core import _set_structured_logging_implementation
    return _set_structured_logging_implementation(enabled)

# Performance Configuration
def get_memory_threshold_percent() -> int:
    """PURE DELEGATION: Get memory threshold percentage."""
    from .config_core import _get_memory_threshold_percent_implementation
    return _get_memory_threshold_percent_implementation()

def set_memory_threshold_percent(percent: int) -> bool:
    """PURE DELEGATION: Set memory threshold percentage."""
    from .config_core import _set_memory_threshold_percent_implementation
    return _set_memory_threshold_percent_implementation(percent)

def get_cleanup_interval() -> int:
    """PURE DELEGATION: Get cleanup interval."""
    from .config_core import _get_cleanup_interval_implementation
    return _get_cleanup_interval_implementation()

def set_cleanup_interval(interval: int) -> bool:
    """PURE DELEGATION: Set cleanup interval."""
    from .config_core import _set_cleanup_interval_implementation
    return _set_cleanup_interval_implementation(interval)

def is_performance_monitoring_enabled() -> bool:
    """PURE DELEGATION: Check if performance monitoring is enabled."""
    from .config_core import _is_performance_monitoring_enabled_implementation
    return _is_performance_monitoring_enabled_implementation()

def set_performance_monitoring(enabled: bool) -> bool:
    """PURE DELEGATION: Set performance monitoring."""
    from .config_core import _set_performance_monitoring_implementation
    return _set_performance_monitoring_implementation(enabled)

# Cost Protection Configuration
def is_cost_protection_active() -> bool:
    """PURE DELEGATION: Check if cost protection is active."""
    from .config_core import _is_cost_protection_active_implementation
    return _is_cost_protection_active_implementation()

def set_cost_protection_active(active: bool) -> bool:
    """PURE DELEGATION: Set cost protection active."""
    from .config_core import _set_cost_protection_active_implementation
    return _set_cost_protection_active_implementation(active)

def get_rate_limit_per_minute() -> int:
    """PURE DELEGATION: Get rate limit per minute."""
    from .config_core import _get_rate_limit_per_minute_implementation
    return _get_rate_limit_per_minute_implementation()

def set_rate_limit_per_minute(limit: int) -> bool:
    """PURE DELEGATION: Set rate limit per minute."""
    from .config_core import _set_rate_limit_per_minute_implementation
    return _set_rate_limit_per_minute_implementation(limit)

def get_cost_threshold() -> float:
    """PURE DELEGATION: Get cost threshold."""
    from .config_core import _get_cost_threshold_implementation
    return _get_cost_threshold_implementation()

def set_cost_threshold(threshold: float) -> bool:
    """PURE DELEGATION: Set cost threshold."""
    from .config_core import _set_cost_threshold_implementation
    return _set_cost_threshold_implementation(threshold)

def get_alert_channels() -> List[str]:
    """PURE DELEGATION: Get alert channels."""
    from .config_core import _get_alert_channels_implementation
    return _get_alert_channels_implementation()

def set_alert_channels(channels: List[str]) -> bool:
    """PURE DELEGATION: Set alert channels."""
    from .config_core import _set_alert_channels_implementation
    return _set_alert_channels_implementation(channels)

# EOS

# ===== SECTION 2: ULTRA-OPTIMIZED CONFIGURATION SYSTEM =====

def get_tier_configuration(base_tier: ConfigurationTier = ConfigurationTier.STANDARD,
                          overrides: Optional[Dict[InterfaceType, ConfigurationTier]] = None) -> Dict[str, Any]:
    """
    PURE DELEGATION: Get complete system configuration for specified tier with optional overrides.
    
    Args:
        base_tier: Base configuration tier (MINIMUM/STANDARD/MAXIMUM/USER)
        overrides: Optional interface-specific tier overrides
        
    Returns:
        Complete system configuration with all interface settings
        
    Example:
        # Get standard configuration with maximum cache
        config = get_tier_configuration(
            ConfigurationTier.STANDARD,
            {InterfaceType.CACHE: ConfigurationTier.MAXIMUM}
        )
    """
    return get_full_system_configuration(base_tier, overrides)

def get_interface_configuration(interface_type: InterfaceType, 
                              tier: ConfigurationTier = ConfigurationTier.STANDARD) -> Dict[str, Any]:
    """
    PURE DELEGATION: Get configuration for specific interface at specified tier.
    
    Args:
        interface_type: Interface to configure (CACHE/LOGGING/METRICS/etc.)
        tier: Configuration tier for the interface
        
    Returns:
        Interface-specific configuration dictionary
        
    Example:
        # Get maximum cache configuration
        cache_config = get_interface_configuration(InterfaceType.CACHE, ConfigurationTier.MAXIMUM)
    """
    return get_interface_configuration(interface_type, tier)

def validate_configuration(base_tier: ConfigurationTier,
                         overrides: Optional[Dict[InterfaceType, ConfigurationTier]] = None) -> Dict[str, Any]:
    """
    PURE DELEGATION: Validate configuration against AWS constraints and resource limits.
    
    Args:
        base_tier: Base configuration tier
        overrides: Optional interface-specific overrides
        
    Returns:
        Validation result with warnings, errors, and resource estimates
        
    Example:
        # Validate if maximum everything fits in 128MB
        validation = validate_configuration(
            ConfigurationTier.MAXIMUM,
            {InterfaceType.CACHE: ConfigurationTier.MAXIMUM}
        )
        if not validation["is_valid"]:
            print("Configuration exceeds AWS limits")
    """
    if overrides is None:
        overrides = {}
    return validate_override_combination(base_tier, overrides)

def get_preset_configuration(preset_name: str = "production_balanced") -> Dict[str, Any]:
    """
    PURE DELEGATION: Get predefined configuration preset.
    
    Args:
        preset_name: Name of preset configuration
        
    Returns:
        Complete system configuration for the preset
        
    Available presets:
        - ultra_conservative: Minimum resource usage
        - production_balanced: Recommended default
        - performance_optimized: High performance with maximum cache
        - development_debug: Enhanced logging and debugging
        - security_focused: Maximum security validation
        - resource_constrained: Minimal resources with standard caching
        
    Example:
        # Get high-performance configuration
        config = get_preset_configuration("performance_optimized")
    """
    return get_preset_configuration(preset_name)

def list_configuration_presets() -> List[Dict[str, str]]:
    """
    PURE DELEGATION: List all available configuration presets with descriptions.
    
    Returns:
        List of preset information including names and descriptions
        
    Example:
        presets = list_configuration_presets()
        for preset in presets:
            print(f"{preset['name']}: {preset['description']}")
    """
    return list_available_presets()

def estimate_resource_usage(base_tier: ConfigurationTier = ConfigurationTier.STANDARD,
                          overrides: Optional[Dict[InterfaceType, ConfigurationTier]] = None) -> Dict[str, Any]:
    """
    PURE DELEGATION: Estimate memory and CloudWatch metric usage for configuration.
    
    Args:
        base_tier: Base configuration tier
        overrides: Optional interface-specific overrides
        
    Returns:
        Resource usage estimates including memory and metrics
        
    Example:
        # Check if configuration fits in AWS limits
        estimates = estimate_resource_usage(
            ConfigurationTier.MAXIMUM,
            {InterfaceType.CACHE: ConfigurationTier.MAXIMUM}
        )
        print(f"Memory: {estimates['memory_mb']:.1f}MB")
        print(f"Metrics: {estimates['metric_count']}")
    """
    if overrides is None:
        overrides = {}
    
    # Create full configuration map
    full_config = {interface: base_tier for interface in InterfaceType}
    full_config.update(overrides)
    
    memory_bytes = estimate_memory_usage(full_config)
    metric_count = estimate_cloudwatch_metrics(full_config)
    
    return {
        "memory_bytes": memory_bytes,
        "memory_mb": memory_bytes / (1024 * 1024),
        "memory_percent": (memory_bytes / (128 * 1024 * 1024)) * 100,
        "metric_count": metric_count,
        "metric_percent": (metric_count / 10) * 100,
        "within_limits": memory_bytes <= (120 * 1024 * 1024) and metric_count <= 10,
        "base_tier": base_tier.value,
        "overrides": {k.value: v.value for k, v in overrides.items()}
    }

def validate_resource_constraints(base_tier: ConfigurationTier,
                                overrides: Optional[Dict[InterfaceType, ConfigurationTier]] = None) -> Dict[str, Any]:
    """
    PURE DELEGATION: Validate configuration against AWS free tier resource constraints.
    
    Args:
        base_tier: Base configuration tier
        overrides: Optional interface-specific overrides
        
    Returns:
        Validation result with constraint checking
        
    Example:
        # Validate configuration before deployment
        validation = validate_resource_constraints(
            ConfigurationTier.MAXIMUM,
            {InterfaceType.METRICS: ConfigurationTier.MAXIMUM}
        )
        if validation["errors"]:
            print("Configuration violates AWS constraints")
    """
    if overrides is None:
        overrides = {}
    
    # Create full configuration map
    full_config = {interface: base_tier for interface in InterfaceType}
    full_config.update(overrides)
    
    return validate_configuration_constraints(full_config)

# ===== SECTION 3: CONFIGURATION CONVENIENCE FUNCTIONS =====

def get_optimized_configuration_for_memory_limit(memory_limit_mb: int = 120) -> Dict[str, Any]:
    """
    PURE DELEGATION: Get optimized configuration that fits within specified memory limit.
    
    Args:
        memory_limit_mb: Memory limit in megabytes (default: 120MB for Lambda)
        
    Returns:
        Optimized configuration that fits within memory limit
    """
    memory_limit_bytes = memory_limit_mb * 1024 * 1024
    
    # Try different configurations in order of preference
    configurations_to_try = [
        (ConfigurationTier.MAXIMUM, {}),
        (ConfigurationTier.STANDARD, {InterfaceType.CACHE: ConfigurationTier.MAXIMUM}),
        (ConfigurationTier.STANDARD, {}),
        (ConfigurationTier.MINIMUM, {InterfaceType.CACHE: ConfigurationTier.STANDARD}),
        (ConfigurationTier.MINIMUM, {})
    ]
    
    for base_tier, overrides in configurations_to_try:
        full_config = {interface: base_tier for interface in InterfaceType}
        full_config.update(overrides)
        
        estimated_memory = estimate_memory_usage(full_config)
        
        if estimated_memory <= memory_limit_bytes:
            config = get_full_system_configuration(base_tier, overrides)
            config["_optimization"] = {
                "memory_limit_mb": memory_limit_mb,
                "estimated_memory_mb": estimated_memory / (1024 * 1024),
                "memory_utilization": (estimated_memory / memory_limit_bytes) * 100,
                "base_tier": base_tier.value,
                "overrides": {k.value: v.value for k, v in overrides.items()}
            }
            return config
    
    # Fallback to absolute minimum
    return get_preset_configuration("ultra_conservative")

def get_development_configuration() -> Dict[str, Any]:
    """
    PURE DELEGATION: Get configuration optimized for development with enhanced debugging.
    
    Returns:
        Development-optimized configuration with enhanced logging and debugging
    """
    return get_preset_configuration("development_debug")

def get_production_configuration() -> Dict[str, Any]:
    """
    PURE DELEGATION: Get configuration optimized for production deployment.
    
    Returns:
        Production-optimized configuration with balanced performance and resource usage
    """
    return get_preset_configuration("production_balanced")

def get_high_performance_configuration() -> Dict[str, Any]:
    """
    PURE DELEGATION: Get configuration optimized for maximum performance.
    
    Returns:
        High-performance configuration with optimized cache and metrics
    """
    return get_preset_configuration("performance_optimized")

def get_security_focused_configuration() -> Dict[str, Any]:
    """
    PURE DELEGATION: Get configuration with maximum security validation.
    
    Returns:
        Security-focused configuration with comprehensive validation and audit logging
    """
    return get_preset_configuration("security_focused")

# EOF
