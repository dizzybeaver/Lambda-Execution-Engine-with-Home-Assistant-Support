"""
variables_utils.py - Ultra-Optimized Configuration System Utility Functions
Version: 2025.09.26.03
Description: Utility functions for configuration estimation, validation, and management

PHASE 3 IMPLEMENTATION: Configuration Utility Functions
- Resource estimation functions for all interfaces
- Configuration validation and constraint checking
- Configuration access and override management
- Preset management and recommendation utilities

ARCHITECTURE: UTILITY MODULE - PURE FUNCTIONS
- Accessed ONLY through config.py gateway
- Contains all configuration utility functions
- Imports data structures from variables.py
- No direct access from other files

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
from .variables import (
    ConfigurationTier, InterfaceType,
    CACHE_INTERFACE_CONFIG, LOGGING_INTERFACE_CONFIG, 
    METRICS_INTERFACE_CONFIG, SECURITY_INTERFACE_CONFIG,
    CIRCUIT_BREAKER_INTERFACE_CONFIG, SINGLETON_INTERFACE_CONFIG,
    CONFIGURATION_PRESETS
)

# ===== RESOURCE ESTIMATION FUNCTIONS =====

def estimate_cache_memory_usage(tier: ConfigurationTier) -> float:
    """Estimate memory usage for cache configuration tier."""
    config = CACHE_INTERFACE_CONFIG.get(tier, CACHE_INTERFACE_CONFIG[ConfigurationTier.MINIMUM])
    return config["cache_pools"]["total_cache_allocation_mb"]

def estimate_logging_memory_usage(tier: ConfigurationTier) -> float:
    """Estimate memory usage for logging configuration tier."""
    base_memory = {
        ConfigurationTier.MINIMUM: 0.5,
        ConfigurationTier.STANDARD: 2.0,
        ConfigurationTier.MAXIMUM: 6.0
    }
    return base_memory.get(tier, 0.5)

def estimate_metrics_memory_usage(tier: ConfigurationTier) -> float:
    """Estimate memory usage for metrics configuration tier."""
    base_memory = {
        ConfigurationTier.MINIMUM: 1.0,
        ConfigurationTier.STANDARD: 3.0,
        ConfigurationTier.MAXIMUM: 8.0
    }
    return base_memory.get(tier, 1.0)

def estimate_security_memory_usage(tier: ConfigurationTier) -> float:
    """Estimate memory usage for security configuration tier."""
    config = SECURITY_INTERFACE_CONFIG.get(tier, SECURITY_INTERFACE_CONFIG[ConfigurationTier.MINIMUM])
    return config["resource_allocation"]["total_security_memory_mb"]

def estimate_circuit_breaker_memory_usage(tier: ConfigurationTier) -> float:
    """Estimate memory usage for circuit breaker configuration tier."""
    config = CIRCUIT_BREAKER_INTERFACE_CONFIG.get(tier, CIRCUIT_BREAKER_INTERFACE_CONFIG[ConfigurationTier.MINIMUM])
    return config["resource_allocation"]["total_circuit_breaker_memory_mb"]

def estimate_singleton_memory_usage(tier: ConfigurationTier) -> float:
    """Estimate memory usage for singleton configuration tier."""
    config = SINGLETON_INTERFACE_CONFIG.get(tier, SINGLETON_INTERFACE_CONFIG[ConfigurationTier.MINIMUM])
    
    # Calculate total singleton memory (overhead + individual singleton allocations)
    overhead_memory = config["resource_allocation"]["total_singleton_overhead_mb"]
    singleton_memory = sum(
        singleton_config["memory_allocation_mb"] 
        for singleton_config in config["singleton_types"].values()
    )
    
    return overhead_memory + singleton_memory

def estimate_metrics_count(tier: ConfigurationTier) -> int:
    """Estimate CloudWatch metrics usage for metrics configuration tier."""
    config = METRICS_INTERFACE_CONFIG.get(tier, METRICS_INTERFACE_CONFIG[ConfigurationTier.MINIMUM])
    return config["metric_allocation"]["total_metrics_used"]

# ===== INTERFACE CONFIGURATION ACCESS FUNCTIONS =====

def get_cache_configuration(tier: ConfigurationTier) -> Dict[str, Any]:
    """Get cache interface configuration for specified tier."""
    return CACHE_INTERFACE_CONFIG.get(tier, CACHE_INTERFACE_CONFIG[ConfigurationTier.MINIMUM]).copy()

def get_logging_configuration(tier: ConfigurationTier) -> Dict[str, Any]:
    """Get logging interface configuration for specified tier."""
    return LOGGING_INTERFACE_CONFIG.get(tier, LOGGING_INTERFACE_CONFIG[ConfigurationTier.MINIMUM]).copy()

def get_metrics_configuration(tier: ConfigurationTier) -> Dict[str, Any]:
    """Get metrics interface configuration for specified tier."""
    return METRICS_INTERFACE_CONFIG.get(tier, METRICS_INTERFACE_CONFIG[ConfigurationTier.MINIMUM]).copy()

def get_security_configuration(tier: ConfigurationTier) -> Dict[str, Any]:
    """Get security interface configuration for specified tier."""
    return SECURITY_INTERFACE_CONFIG.get(tier, SECURITY_INTERFACE_CONFIG[ConfigurationTier.MINIMUM]).copy()

def get_circuit_breaker_configuration(tier: ConfigurationTier) -> Dict[str, Any]:
    """Get circuit breaker interface configuration for specified tier."""
    return CIRCUIT_BREAKER_INTERFACE_CONFIG.get(tier, CIRCUIT_BREAKER_INTERFACE_CONFIG[ConfigurationTier.MINIMUM]).copy()

def get_singleton_configuration(tier: ConfigurationTier) -> Dict[str, Any]:
    """Get singleton interface configuration for specified tier."""
    return SINGLETON_INTERFACE_CONFIG.get(tier, SINGLETON_INTERFACE_CONFIG[ConfigurationTier.MINIMUM]).copy()

def get_interface_configuration(interface: InterfaceType, tier: ConfigurationTier) -> Dict[str, Any]:
    """
    Get configuration for a specific interface at specified tier.
    Enhanced for Phase 2+3 interfaces.
    """
    interface_getters = {
        InterfaceType.CACHE: get_cache_configuration,
        InterfaceType.LOGGING: get_logging_configuration,
        InterfaceType.METRICS: get_metrics_configuration,
        InterfaceType.SECURITY: get_security_configuration,
        InterfaceType.CIRCUIT_BREAKER: get_circuit_breaker_configuration,
        InterfaceType.SINGLETON: get_singleton_configuration
    }
    
    getter = interface_getters.get(interface)
    if getter:
        return getter(tier)
    else:
        # Placeholder for interfaces not yet implemented
        return {
            "tier": tier.value,
            "status": "placeholder",
            "message": f"Interface {interface.value} configuration pending implementation"
        }

# ===== VALIDATION FUNCTIONS =====

def validate_phase2_memory_constraints(cache_tier: ConfigurationTier = ConfigurationTier.STANDARD,
                                     logging_tier: ConfigurationTier = ConfigurationTier.STANDARD,
                                     metrics_tier: ConfigurationTier = ConfigurationTier.STANDARD,
                                     security_tier: ConfigurationTier = ConfigurationTier.STANDARD) -> Dict[str, Any]:
    """Validate that Phase 2 interface combinations don't exceed 128MB constraint."""
    
    cache_memory = estimate_cache_memory_usage(cache_tier)
    logging_memory = estimate_logging_memory_usage(logging_tier)
    metrics_memory = estimate_metrics_memory_usage(metrics_tier) 
    security_memory = estimate_security_memory_usage(security_tier)
    
    # Reserve memory for base system, other interfaces, and Lambda runtime
    reserved_memory = 40  # Base system + other interfaces + Lambda runtime
    
    total_phase2_memory = cache_memory + logging_memory + metrics_memory + security_memory
    total_system_memory = total_phase2_memory + reserved_memory
    
    metrics_count = estimate_metrics_count(metrics_tier)
    
    validation_result = {
        "is_valid": total_system_memory <= 128 and metrics_count <= 10,
        "memory_usage": {
            "cache_mb": cache_memory,
            "logging_mb": logging_memory,
            "metrics_mb": metrics_memory,
            "security_mb": security_memory,
            "phase2_total_mb": total_phase2_memory,
            "reserved_mb": reserved_memory,
            "system_total_mb": total_system_memory,
            "memory_limit_mb": 128
        },
        "metrics_usage": {
            "metrics_used": metrics_count,
            "metrics_limit": 10
        },
        "warnings": []
    }
    
    if total_system_memory > 128:
        validation_result["warnings"].append(f"Memory usage ({total_system_memory}MB) exceeds 128MB limit")
    
    if metrics_count > 10:
        validation_result["warnings"].append(f"Metrics usage ({metrics_count}) exceeds 10 metric limit")
    
    if total_system_memory > 100:
        validation_result["warnings"].append(f"Memory usage approaching limit: {total_system_memory}MB/128MB")
    
    return validation_result

def validate_phase3_memory_constraints(circuit_breaker_tier: ConfigurationTier = ConfigurationTier.STANDARD,
                                     singleton_tier: ConfigurationTier = ConfigurationTier.STANDARD,
                                     cache_tier: ConfigurationTier = ConfigurationTier.STANDARD,
                                     logging_tier: ConfigurationTier = ConfigurationTier.STANDARD,
                                     metrics_tier: ConfigurationTier = ConfigurationTier.STANDARD,
                                     security_tier: ConfigurationTier = ConfigurationTier.STANDARD) -> Dict[str, Any]:
    """Validate that Phase 2+3 interface combinations don't exceed 128MB constraint."""
    
    # Phase 2 interfaces
    cache_memory = estimate_cache_memory_usage(cache_tier)
    logging_memory = estimate_logging_memory_usage(logging_tier)
    metrics_memory = estimate_metrics_memory_usage(metrics_tier)
    security_memory = estimate_security_memory_usage(security_tier)
    
    # Phase 3 interfaces
    circuit_breaker_memory = estimate_circuit_breaker_memory_usage(circuit_breaker_tier)
    singleton_memory = estimate_singleton_memory_usage(singleton_tier)
    
    # Reserve memory for remaining interfaces and Lambda runtime
    reserved_memory = 25  # Reduced reserve as we've implemented more interfaces
    
    total_implemented_memory = (cache_memory + logging_memory + metrics_memory + 
                              security_memory + circuit_breaker_memory + singleton_memory)
    total_system_memory = total_implemented_memory + reserved_memory
    
    metrics_count = estimate_metrics_count(metrics_tier)
    
    validation_result = {
        "is_valid": total_system_memory <= 128 and metrics_count <= 10,
        "memory_usage": {
            "cache_mb": cache_memory,
            "logging_mb": logging_memory,
            "metrics_mb": metrics_memory,
            "security_mb": security_memory,
            "circuit_breaker_mb": circuit_breaker_memory,
            "singleton_mb": singleton_memory,
            "implemented_total_mb": total_implemented_memory,
            "reserved_mb": reserved_memory,
            "system_total_mb": total_system_memory,
            "memory_limit_mb": 128
        },
        "metrics_usage": {
            "metrics_used": metrics_count,
            "metrics_limit": 10
        },
        "warnings": []
    }
    
    if total_system_memory > 128:
        validation_result["warnings"].append(f"Memory usage ({total_system_memory}MB) exceeds 128MB limit")
    
    if metrics_count > 10:
        validation_result["warnings"].append(f"Metrics usage ({metrics_count}) exceeds 10 metric limit")
    
    if total_system_memory > 110:
        validation_result["warnings"].append(f"Memory usage approaching limit: {total_system_memory}MB/128MB")
    
    return validation_result

def validate_override_combination(base_tier: ConfigurationTier, 
                                overrides: Dict[InterfaceType, ConfigurationTier]) -> Dict[str, Any]:
    """Enhanced validation with Phase 2+3 interface constraint checking."""
    
    # Get effective tiers for each interface
    cache_tier = overrides.get(InterfaceType.CACHE, base_tier)
    logging_tier = overrides.get(InterfaceType.LOGGING, base_tier)
    metrics_tier = overrides.get(InterfaceType.METRICS, base_tier)
    security_tier = overrides.get(InterfaceType.SECURITY, base_tier)
    circuit_breaker_tier = overrides.get(InterfaceType.CIRCUIT_BREAKER, base_tier)
    singleton_tier = overrides.get(InterfaceType.SINGLETON, base_tier)
    
    # Validate Phase 2+3 constraints
    phase3_validation = validate_phase3_memory_constraints(
        circuit_breaker_tier, singleton_tier, cache_tier, logging_tier, metrics_tier, security_tier
    )
    
    # Calculate comprehensive resource estimates
    total_memory = phase3_validation["memory_usage"]["system_total_mb"]
    total_metrics = phase3_validation["metrics_usage"]["metrics_used"]
    
    validation_result = {
        "is_valid": phase3_validation["is_valid"],
        "memory_estimate": total_memory,
        "metric_estimate": total_metrics,
        "interface_breakdown": {
            "cache": {"tier": cache_tier.value, "memory_mb": phase3_validation["memory_usage"]["cache_mb"]},
            "logging": {"tier": logging_tier.value, "memory_mb": phase3_validation["memory_usage"]["logging_mb"]},
            "metrics": {"tier": metrics_tier.value, "memory_mb": phase3_validation["memory_usage"]["metrics_mb"]},
            "security": {"tier": security_tier.value, "memory_mb": phase3_validation["memory_usage"]["security_mb"]},
            "circuit_breaker": {"tier": circuit_breaker_tier.value, "memory_mb": phase3_validation["memory_usage"]["circuit_breaker_mb"]},
            "singleton": {"tier": singleton_tier.value, "memory_mb": phase3_validation["memory_usage"]["singleton_mb"]}
        },
        "warnings": phase3_validation["warnings"],
        "recommendations": []
    }
    
    # Add intelligent recommendations
    if not phase3_validation["is_valid"]:
        if total_memory > 128:
            validation_result["recommendations"].append("Consider reducing singleton or circuit breaker tiers to lower memory usage")
        if total_metrics > 10:
            validation_result["recommendations"].append("Reduce metrics tier or enable metric rotation")
    
    return validation_result

# ===== CONFIGURATION MANAGEMENT FUNCTIONS =====

def apply_configuration_overrides(base_tier: ConfigurationTier, 
                                overrides: Dict[InterfaceType, ConfigurationTier]) -> Dict[str, Any]:
    """
    Apply interface-specific overrides to base tier configuration.
    Enhanced for Phase 2+3 interfaces.
    """
    configuration = {}
    
    # Apply Phase 2 configurations
    cache_tier = overrides.get(InterfaceType.CACHE, base_tier)
    configuration["cache"] = get_cache_configuration(cache_tier)
    
    logging_tier = overrides.get(InterfaceType.LOGGING, base_tier)
    configuration["logging"] = get_logging_configuration(logging_tier)
    
    metrics_tier = overrides.get(InterfaceType.METRICS, base_tier)
    configuration["metrics"] = get_metrics_configuration(metrics_tier)
    
    security_tier = overrides.get(InterfaceType.SECURITY, base_tier)
    configuration["security"] = get_security_configuration(security_tier)
    
    # Apply Phase 3 configurations
    circuit_breaker_tier = overrides.get(InterfaceType.CIRCUIT_BREAKER, base_tier)
    configuration["circuit_breaker"] = get_circuit_breaker_configuration(circuit_breaker_tier)
    
    singleton_tier = overrides.get(InterfaceType.SINGLETON, base_tier)
    configuration["singleton"] = get_singleton_configuration(singleton_tier)
    
    # Placeholder for future phases - these will be implemented in subsequent phases
    placeholder_config = {"tier": base_tier.value, "status": "placeholder"}
    
    configuration["lambda"] = placeholder_config
    configuration["http_client"] = placeholder_config
    configuration["utility"] = placeholder_config
    configuration["initialization"] = placeholder_config
    
    return configuration

def get_full_system_configuration(base_tier: ConfigurationTier, 
                                overrides: Optional[Dict[InterfaceType, ConfigurationTier]] = None) -> Dict[str, Any]:
    """
    Get complete system configuration with tier inheritance and overrides.
    Enhanced for Phase 2+3 with full validation and resource estimation.
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
        "generated_at": "runtime",
        "phase3_status": "implemented",
        "interfaces_implemented": ["cache", "logging", "metrics", "security", "circuit_breaker", "singleton"],
        "interfaces_pending": ["lambda", "http_client", "utility", "initialization"]
    }
    
    return final_config

# ===== PRESET MANAGEMENT FUNCTIONS =====

def get_preset_configuration(preset_name: str) -> Dict[str, Any]:
    """
    Get a predefined configuration preset.
    Returns the complete configuration for the specified preset.
    """
    if preset_name not in CONFIGURATION_PRESETS:
        return get_full_system_configuration(ConfigurationTier.STANDARD, {})
    
    preset = CONFIGURATION_PRESETS[preset_name]
    return get_full_system_configuration(preset["base_tier"], preset["overrides"])

def list_configuration_presets() -> List[Dict[str, Any]]:
    """List all available configuration presets with Phase 2+3 resource estimates."""
    preset_list = []
    for name, preset in CONFIGURATION_PRESETS.items():
        preset_info = {
            "name": name,
            "description": preset["description"],
            "base_tier": preset["base_tier"].value,
            "overrides": {k.value: v.value for k, v in preset["overrides"].items()},
            "memory_estimate": preset.get("memory_estimate", 0),
            "metric_estimate": preset.get("metric_estimate", 0)
        }
        preset_list.append(preset_info)
    return preset_list

# ===== UTILITY AND ANALYSIS FUNCTIONS =====

def get_tier_memory_breakdown(tier: ConfigurationTier) -> Dict[str, float]:
    """Get detailed memory breakdown for a specific tier across Phase 2+3 interfaces."""
    return {
        "cache_mb": estimate_cache_memory_usage(tier),
        "logging_mb": estimate_logging_memory_usage(tier),
        "metrics_mb": estimate_metrics_memory_usage(tier),
        "security_mb": estimate_security_memory_usage(tier),
        "circuit_breaker_mb": estimate_circuit_breaker_memory_usage(tier),
        "singleton_mb": estimate_singleton_memory_usage(tier),
        "total_implemented_mb": (estimate_cache_memory_usage(tier) + 
                               estimate_logging_memory_usage(tier) + 
                               estimate_metrics_memory_usage(tier) + 
                               estimate_security_memory_usage(tier) +
                               estimate_circuit_breaker_memory_usage(tier) +
                               estimate_singleton_memory_usage(tier))
    }

def recommend_configuration_for_memory_limit(target_memory_mb: int) -> Dict[str, Any]:
    """Recommend optimal configuration combination for specified memory limit with Phase 3 interfaces."""
    recommendations = []
    
    # Try different tier combinations to find optimal fit
    for cache_tier in [ConfigurationTier.MINIMUM, ConfigurationTier.STANDARD, ConfigurationTier.MAXIMUM]:
        for security_tier in [ConfigurationTier.MINIMUM, ConfigurationTier.STANDARD, ConfigurationTier.MAXIMUM]:
            for circuit_breaker_tier in [ConfigurationTier.MINIMUM, ConfigurationTier.STANDARD]:
                for singleton_tier in [ConfigurationTier.MINIMUM, ConfigurationTier.STANDARD]:
                    for logging_tier in [ConfigurationTier.MINIMUM, ConfigurationTier.STANDARD]:
                        for metrics_tier in [ConfigurationTier.MINIMUM, ConfigurationTier.STANDARD]:
                            
                            validation = validate_phase3_memory_constraints(
                                circuit_breaker_tier, singleton_tier, cache_tier, 
                                logging_tier, metrics_tier, security_tier
                            )
                            total_memory = validation["memory_usage"]["system_total_mb"]
                            
                            if total_memory <= target_memory_mb and validation["is_valid"]:
                                recommendations.append({
                                    "configuration": {
                                        "cache": cache_tier.value,
                                        "logging": logging_tier.value,
                                        "metrics": metrics_tier.value,
                                        "security": security_tier.value,
                                        "circuit_breaker": circuit_breaker_tier.value,
                                        "singleton": singleton_tier.value
                                    },
                                    "memory_usage": total_memory,
                                    "metrics_usage": validation["metrics_usage"]["metrics_used"],
                                    "efficiency_score": (total_memory / target_memory_mb) * 100
                                })
    
    # Sort by efficiency (closest to target without exceeding)
    recommendations.sort(key=lambda x: x["efficiency_score"], reverse=True)
    
    return {
        "target_memory_mb": target_memory_mb,
        "recommendations": recommendations[:5],  # Top 5 recommendations
        "total_combinations_evaluated": len(recommendations)
    }

def get_specialized_interface_summary(tier: ConfigurationTier) -> Dict[str, Any]:
    """Get summary of Phase 3 specialized interface configurations for specified tier."""
    circuit_breaker_config = get_circuit_breaker_configuration(tier)
    singleton_config = get_singleton_configuration(tier)
    
    return {
        "tier": tier.value,
        "circuit_breaker": {
            "memory_mb": estimate_circuit_breaker_memory_usage(tier),
            "service_policies": len(circuit_breaker_config["circuit_breaker_policies"]),
            "pattern_recognition": circuit_breaker_config["failure_detection"]["pattern_recognition_enabled"],
            "cascade_prevention": circuit_breaker_config["failure_detection"]["cascade_prevention_enabled"]
        },
        "singleton": {
            "memory_mb": estimate_singleton_memory_usage(tier),
            "max_singletons": singleton_config["singleton_registry"]["max_singletons"],
            "memory_coordination": singleton_config["memory_coordination"]["pressure_response_enabled"],
            "predictive_management": singleton_config["memory_coordination"].get("predictive_memory_management", False)
        },
        "combined_memory_mb": estimate_circuit_breaker_memory_usage(tier) + estimate_singleton_memory_usage(tier)
    }

# ===== END OF UTILITY FUNCTIONS =====
