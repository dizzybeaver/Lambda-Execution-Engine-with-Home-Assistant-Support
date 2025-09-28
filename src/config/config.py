"""
config.py - Ultra-Optimized Configuration System Gateway Interface
Version: 2025.09.28.03
Description: Primary gateway interface for ultra-optimized four-tier configuration management

ULTRA-OPTIMIZED GATEWAY INTERFACE - SPECIAL STATUS
- Central configuration repository with gateway pattern compliance
- Pure delegation to config_core.py and variables_utils.py implementations
- Complete Variables System Simplified Configuration Reference compliance
- Four-tier system with presets, overrides, and intelligent optimization
- AWS Lambda 128MB constraint validation and cost protection

CONFIGURATION SYSTEM FEATURES:
- Four-tier configuration system (MINIMUM, STANDARD, MAXIMUM, USER)
- 11 configuration presets for common use cases
- Interface-specific overrides with constraint validation
- Memory and cost optimization with AWS free tier protection
- Real-time performance analysis and optimization recommendations

GATEWAY ARCHITECTURE COMPLIANCE:
- Primary gateway interface - external files access ONLY through this interface
- Pure delegation pattern - no implementation code in gateway
- All implementation delegated to config_core.py and variables_utils.py
- Maintains ultra-optimization status with maximum gateway utilization

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

# Import configuration enums and types from variables.py data structures
from .variables import ConfigurationTier, InterfaceType

# Import all implementation functions from config_core.py and variables_utils.py
from .config_core import (
    _get_parameter_implementation,
    _set_parameter_implementation,
    _get_all_parameters_for_type_implementation,
    _get_configuration_types_implementation,
    _create_configuration_type_implementation,
    _clear_configuration_cache_implementation
)

from .variables_utils import (
    # Resource estimation functions
    estimate_cache_memory_usage,
    estimate_logging_memory_usage,
    estimate_metrics_memory_usage,
    estimate_security_memory_usage,
    estimate_circuit_breaker_memory_usage,
    estimate_singleton_memory_usage,
    estimate_metrics_count,
    
    # Configuration access functions
    get_cache_configuration,
    get_logging_configuration,
    get_metrics_configuration,
    get_security_configuration,
    get_circuit_breaker_configuration,
    get_singleton_configuration,
    
    # Configuration management functions
    validate_override_combination,
    apply_configuration_overrides,
    get_full_system_configuration,
    validate_phase3_memory_constraints,
    
    # Preset management functions
    get_preset_configuration,
    list_configuration_presets,
    
    # Analysis functions
    get_tier_memory_breakdown
)

# ===== SECTION 1: CORE CONFIGURATION PARAMETER MANAGEMENT =====

def get_parameter(key: str, default_value: Any = None, config_type: str = "default") -> Any:
    """
    Get configuration parameter with caching and validation.
    GATEWAY: Delegates to config_core._get_parameter_implementation
    """
    return _get_parameter_implementation(key, default_value, config_type)

def set_parameter(key: str, value: Any, config_type: str = "default", persistent: bool = False) -> bool:
    """
    Set configuration parameter with validation and caching.
    GATEWAY: Delegates to config_core._set_parameter_implementation
    """
    return _set_parameter_implementation(key, value, config_type, persistent)

def get_all_parameters(config_type: str = "default") -> Dict[str, Any]:
    """
    Get all parameters for a configuration type.
    GATEWAY: Delegates to config_core._get_all_parameters_for_type_implementation
    """
    return _get_all_parameters_for_type_implementation(config_type)

def get_configuration_types() -> List[str]:
    """
    Get available configuration types.
    GATEWAY: Delegates to config_core._get_configuration_types_implementation
    """
    return _get_configuration_types_implementation()

def create_configuration_type(config_type: str) -> Dict[str, Any]:
    """
    Create new configuration type.
    GATEWAY: Delegates to config_core._create_configuration_type_implementation
    """
    return _create_configuration_type_implementation(config_type)

def clear_configuration_cache(config_type: str = None) -> Dict[str, Any]:
    """
    Clear configuration cache.
    GATEWAY: Delegates to config_core._clear_configuration_cache_implementation
    """
    return _clear_configuration_cache_implementation(config_type)

# ===== SECTION 2: CONFIGURATION TIER MANAGEMENT =====

def get_interface_configuration(interface: InterfaceType, tier: ConfigurationTier) -> Dict[str, Any]:
    """
    Get configuration for specific interface and tier.
    GATEWAY: Delegates to appropriate variables_utils interface configuration function
    """
    if interface == InterfaceType.CACHE:
        return get_cache_configuration(tier)
    elif interface == InterfaceType.LOGGING:
        return get_logging_configuration(tier)
    elif interface == InterfaceType.METRICS:
        return get_metrics_configuration(tier)
    elif interface == InterfaceType.SECURITY:
        return get_security_configuration(tier)
    elif interface == InterfaceType.CIRCUIT_BREAKER:
        return get_circuit_breaker_configuration(tier)
    elif interface == InterfaceType.SINGLETON:
        return get_singleton_configuration(tier)
    else:
        # Placeholder for future interfaces
        return {"tier": tier.value, "status": "placeholder", "interface": interface.value}

def get_system_configuration(base_tier: ConfigurationTier, 
                           overrides: Optional[Dict[InterfaceType, ConfigurationTier]] = None) -> Dict[str, Any]:
    """
    Get complete system configuration with tier inheritance and overrides.
    GATEWAY: Delegates to variables_utils.get_full_system_configuration
    """
    return get_full_system_configuration(base_tier, overrides)

def validate_configuration(base_tier: ConfigurationTier, 
                         overrides: Optional[Dict[InterfaceType, ConfigurationTier]] = None) -> Dict[str, Any]:
    """
    Validate configuration combination against AWS constraints.
    GATEWAY: Delegates to variables_utils.validate_override_combination
    """
    return validate_override_combination(base_tier, overrides or {})

def apply_configuration_overrides_to_base(base_tier: ConfigurationTier, 
                                        overrides: Dict[InterfaceType, ConfigurationTier]) -> Dict[str, Any]:
    """
    Apply interface-specific overrides to base tier configuration.
    GATEWAY: Delegates to variables_utils.apply_configuration_overrides
    """
    return apply_configuration_overrides(base_tier, overrides)

# ===== SECTION 3: CONFIGURATION PRESETS =====

def get_available_presets() -> List[Dict[str, Any]]:
    """
    Get list of all available configuration presets.
    GATEWAY: Delegates to variables_utils.list_configuration_presets
    """
    return list_configuration_presets()

def get_preset_details(preset_name: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific preset.
    GATEWAY: Delegates to variables_utils.get_preset_configuration
    """
    return get_preset_configuration(preset_name)

def apply_preset(preset_name: str) -> Dict[str, Any]:
    """
    Apply a configuration preset and return the complete configuration.
    GATEWAY: Delegates to variables_utils.get_preset_configuration
    """
    return get_preset_configuration(preset_name)

def list_preset_names() -> List[str]:
    """
    Get list of available preset names.
    GATEWAY: Delegates to variables_utils.list_configuration_presets and extracts names
    """
    presets = list_configuration_presets()
    return [preset["name"] for preset in presets]

# ===== SECTION 4: RESOURCE ESTIMATION AND CONSTRAINT VALIDATION =====

def estimate_memory_usage(tier: ConfigurationTier, interface: InterfaceType = None) -> float:
    """
    Estimate memory usage for configuration tier and optional interface.
    GATEWAY: Delegates to appropriate variables_utils estimation functions
    """
    if interface is None:
        # Estimate total system memory
        breakdown = get_tier_memory_breakdown(tier)
        return sum(breakdown.values())
    
    # Estimate specific interface memory
    if interface == InterfaceType.CACHE:
        return estimate_cache_memory_usage(tier)
    elif interface == InterfaceType.LOGGING:
        return estimate_logging_memory_usage(tier)
    elif interface == InterfaceType.METRICS:
        return estimate_metrics_memory_usage(tier)
    elif interface == InterfaceType.SECURITY:
        return estimate_security_memory_usage(tier)
    elif interface == InterfaceType.CIRCUIT_BREAKER:
        return estimate_circuit_breaker_memory_usage(tier)
    elif interface == InterfaceType.SINGLETON:
        return estimate_singleton_memory_usage(tier)
    else:
        return 0.0

def estimate_metrics_usage(tier: ConfigurationTier) -> int:
    """
    Estimate CloudWatch metrics usage for configuration tier.
    GATEWAY: Delegates to variables_utils.estimate_metrics_count
    """
    return estimate_metrics_count(tier)

def get_memory_allocation_summary(base_tier: ConfigurationTier = ConfigurationTier.STANDARD,
                                overrides: Optional[Dict[InterfaceType, ConfigurationTier]] = None) -> Dict[str, Any]:
    """
    Get detailed memory allocation summary for configuration.
    GATEWAY: Delegates to variables_utils validation and combines with breakdown
    """
    validation = validate_configuration(base_tier, overrides)
    return {
        "total_memory_mb": validation.get("memory_estimate", 0),
        "memory_limit_mb": 128,
        "memory_available_mb": 128 - validation.get("memory_estimate", 0),
        "utilization_percent": (validation.get("memory_estimate", 0) / 128) * 100,
        "interface_breakdown": validation.get("interface_breakdown", {}),
        "within_constraints": validation.get("is_valid", False),
        "warnings": validation.get("warnings", []),
        "recommendations": validation.get("recommendations", [])
    }

def validate_aws_constraints(base_tier: ConfigurationTier,
                           overrides: Optional[Dict[InterfaceType, ConfigurationTier]] = None) -> Dict[str, Any]:
    """
    Validate configuration against all AWS Lambda constraints.
    GATEWAY: Delegates to variables_utils.validate_override_combination with enhanced validation
    """
    validation = validate_configuration(base_tier, overrides)
    
    # Enhanced constraint checking
    memory_mb = validation.get("memory_estimate", 0)
    metrics_count = validation.get("metric_estimate", 0)
    
    constraints = {
        "memory_constraint": {
            "limit_mb": 128,
            "usage_mb": memory_mb,
            "within_limit": memory_mb <= 128,
            "utilization_percent": (memory_mb / 128) * 100
        },
        "metrics_constraint": {
            "limit_count": 10,
            "usage_count": metrics_count,
            "within_limit": metrics_count <= 10,
            "utilization_percent": (metrics_count / 10) * 100
        },
        "overall_compliance": validation.get("is_valid", False)
    }
    
    return {
        "constraints": constraints,
        "validation_details": validation,
        "compliance_status": "compliant" if constraints["overall_compliance"] else "non_compliant"
    }

# ===== SECTION 5: OPTIMIZATION FUNCTIONS =====

def optimize_for_memory_constraint(target_memory_mb: float = 64,
                                 preserve_interfaces: List[InterfaceType] = None) -> Dict[str, Any]:
    """
    Optimize configuration to meet memory constraint while preserving functionality.
    GATEWAY: Implements optimization logic using existing validation functions
    """
    preserve_interfaces = preserve_interfaces or []
    
    # Start with minimum tier and gradually increase until constraint met
    for base_tier in [ConfigurationTier.MINIMUM, ConfigurationTier.STANDARD]:
        # Try base tier first
        validation = validate_configuration(base_tier, {})
        if validation["memory_estimate"] <= target_memory_mb:
            config = get_system_configuration(base_tier, {})
            return {
                "optimized_configuration": config,
                "optimization_result": "success",
                "memory_usage_mb": validation["memory_estimate"],
                "target_memory_mb": target_memory_mb,
                "optimization_strategy": f"base_tier_{base_tier.value}"
            }
        
        # Try selective upgrades for preserved interfaces
        best_overrides = {}
        for interface in preserve_interfaces:
            test_overrides = best_overrides.copy()
            test_overrides[interface] = ConfigurationTier.STANDARD
            test_validation = validate_configuration(base_tier, test_overrides)
            if test_validation["memory_estimate"] <= target_memory_mb:
                best_overrides = test_overrides
        
        if best_overrides:
            config = get_system_configuration(base_tier, best_overrides)
            final_validation = validate_configuration(base_tier, best_overrides)
            return {
                "optimized_configuration": config,
                "optimization_result": "success_with_overrides",
                "memory_usage_mb": final_validation["memory_estimate"],
                "target_memory_mb": target_memory_mb,
                "optimization_strategy": f"base_{base_tier.value}_with_overrides",
                "preserved_interfaces": [iface.value for iface in preserve_interfaces],
                "applied_overrides": {k.value: v.value for k, v in best_overrides.items()}
            }
    
    # Fallback to ultra conservative
    config = apply_preset("ultra_conservative")
    return {
        "optimized_configuration": config,
        "optimization_result": "fallback_ultra_conservative",
        "memory_usage_mb": config.get("memory_estimate", 8),
        "target_memory_mb": target_memory_mb,
        "optimization_strategy": "emergency_fallback"
    }

def optimize_for_performance(priority_interfaces: List[InterfaceType] = None) -> Dict[str, Any]:
    """
    Optimize configuration for maximum performance within constraints.
    GATEWAY: Implements performance optimization using existing functions
    """
    priority_interfaces = priority_interfaces or [InterfaceType.CACHE, InterfaceType.METRICS]
    
    # Start with performance_optimized preset
    config = apply_preset("performance_optimized")
    validation = validate_configuration(ConfigurationTier.STANDARD, config.get("overrides", {}))
    
    if validation["is_valid"]:
        return {
            "optimized_configuration": config,
            "optimization_result": "preset_performance_optimized",
            "memory_usage_mb": validation["memory_estimate"],
            "optimization_strategy": "preset_based"
        }
    
    # Try selective maximum upgrades for priority interfaces
    base_tier = ConfigurationTier.STANDARD
    overrides = {}
    
    for interface in priority_interfaces:
        test_overrides = overrides.copy()
        test_overrides[interface] = ConfigurationTier.MAXIMUM
        test_validation = validate_configuration(base_tier, test_overrides)
        if test_validation["is_valid"]:
            overrides = test_overrides
    
    config = get_system_configuration(base_tier, overrides)
    final_validation = validate_configuration(base_tier, overrides)
    
    return {
        "optimized_configuration": config,
        "optimization_result": "selective_maximum_upgrade",
        "memory_usage_mb": final_validation["memory_estimate"],
        "optimization_strategy": "priority_based",
        "upgraded_interfaces": [iface.value for iface in priority_interfaces if iface in overrides]
    }

def optimize_for_cost_protection() -> Dict[str, Any]:
    """
    Optimize configuration for AWS free tier cost protection.
    GATEWAY: Applies cost-focused optimization using existing presets
    """
    # Use resource_constrained preset for maximum cost protection
    config = apply_preset("resource_constrained")
    validation = validate_configuration(ConfigurationTier.MINIMUM, config.get("overrides", {}))
    
    return {
        "optimized_configuration": config,
        "optimization_result": "cost_protection_optimized",
        "memory_usage_mb": validation["memory_estimate"],
        "metrics_usage": validation["metric_estimate"],
        "optimization_strategy": "free_tier_protection",
        "cost_protection_features": [
            "minimal_memory_usage",
            "reduced_metrics_count",
            "aggressive_resource_conservation"
        ]
    }

def get_optimization_recommendations(current_config: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """
    Get intelligent optimization recommendations based on current configuration.
    GATEWAY: Analyzes configuration and provides recommendations
    """
    if current_config is None:
        current_config = apply_preset("production_balanced")
    
    recommendations = []
    
    # Analyze memory usage
    memory_usage = current_config.get("memory_estimate", 32)
    if memory_usage > 100:
        recommendations.append({
            "type": "memory_optimization",
            "priority": "high",
            "recommendation": "Consider reducing configuration tiers to lower memory usage",
            "action": "optimize_for_memory_constraint",
            "estimated_savings_mb": memory_usage - 64
        })
    elif memory_usage < 20:
        recommendations.append({
            "type": "performance_opportunity",
            "priority": "medium", 
            "recommendation": "Memory headroom available - consider upgrading cache or metrics tiers",
            "action": "optimize_for_performance",
            "available_memory_mb": 128 - memory_usage
        })
    
    # Analyze metrics usage
    metrics_usage = current_config.get("metric_estimate", 6)
    if metrics_usage > 8:
        recommendations.append({
            "type": "metrics_optimization",
            "priority": "high",
            "recommendation": "Approaching CloudWatch metrics limit - prioritize critical metrics",
            "action": "reduce_metrics_tier",
            "metrics_over_limit": metrics_usage - 10
        })
    
    # Preset recommendations
    if not recommendations:
        recommendations.append({
            "type": "configuration_status",
            "priority": "info",
            "recommendation": "Current configuration is well-balanced",
            "action": "monitor_performance",
            "status": "optimal"
        })
    
    return recommendations

# ===== SECTION 6: ANALYSIS AND MONITORING =====

def analyze_configuration_compliance(base_tier: ConfigurationTier,
                                   overrides: Optional[Dict[InterfaceType, ConfigurationTier]] = None) -> Dict[str, Any]:
    """
    Comprehensive configuration compliance analysis.
    GATEWAY: Combines validation with detailed analysis
    """
    validation = validate_configuration(base_tier, overrides)
    constraints = validate_aws_constraints(base_tier, overrides)
    memory_summary = get_memory_allocation_summary(base_tier, overrides)
    
    return {
        "compliance_status": constraints["compliance_status"],
        "validation_results": validation,
        "constraint_analysis": constraints,
        "memory_analysis": memory_summary,
        "recommendations": get_optimization_recommendations({
            "memory_estimate": validation.get("memory_estimate", 0),
            "metric_estimate": validation.get("metric_estimate", 0)
        }),
        "analysis_timestamp": "runtime_generated"
    }

def get_configuration_health_status() -> Dict[str, Any]:
    """
    Get overall configuration system health status.
    GATEWAY: Provides system health analysis
    """
    # Analyze current default configuration
    default_config = apply_preset("production_balanced")
    validation = validate_configuration(ConfigurationTier.STANDARD, {})
    
    health_status = "healthy"
    if validation["memory_estimate"] > 100:
        health_status = "warning"
    if validation["memory_estimate"] > 120:
        health_status = "critical"
    
    return {
        "health_status": health_status,
        "system_configuration": default_config,
        "resource_utilization": {
            "memory_utilization_percent": (validation["memory_estimate"] / 128) * 100,
            "metrics_utilization_percent": (validation["metric_estimate"] / 10) * 100
        },
        "available_presets": len(list_configuration_presets()),
        "supported_interfaces": [iface.value for iface in InterfaceType],
        "system_version": "2025.09.28.03"
    }

# ===== SECTION 7: UTILITY AND CONVENIENCE FUNCTIONS =====

def create_custom_configuration(name: str, base_tier: ConfigurationTier,
                               overrides: Dict[InterfaceType, ConfigurationTier],
                               description: str = "") -> Dict[str, Any]:
    """
    Create custom configuration with validation and save capability.
    GATEWAY: Creates custom configuration using existing functions
    """
    validation = validate_configuration(base_tier, overrides)
    
    if not validation["is_valid"]:
        return {
            "creation_result": "failed",
            "error": "Configuration validation failed",
            "validation_details": validation
        }
    
    config = get_system_configuration(base_tier, overrides)
    custom_config = {
        "name": name,
        "description": description,
        "base_tier": base_tier,
        "overrides": overrides,
        "configuration": config,
        "validation": validation,
        "created_at": "runtime"
    }
    
    return {
        "creation_result": "success",
        "custom_configuration": custom_config,
        "memory_estimate": validation["memory_estimate"],
        "metric_estimate": validation["metric_estimate"]
    }

def compare_configurations(config1: Dict[str, Any], config2: Dict[str, Any]) -> Dict[str, Any]:
    """
    Compare two configurations and highlight differences.
    GATEWAY: Provides configuration comparison analysis
    """
    comparison = {
        "memory_difference_mb": config1.get("memory_estimate", 0) - config2.get("memory_estimate", 0),
        "metric_difference": config1.get("metric_estimate", 0) - config2.get("metric_estimate", 0),
        "tier_differences": {},
        "performance_impact": "neutral"
    }
    
    # Determine performance impact
    if comparison["memory_difference_mb"] > 0:
        comparison["performance_impact"] = "config1_higher_performance"
    elif comparison["memory_difference_mb"] < 0:
        comparison["performance_impact"] = "config2_higher_performance"
    
    return comparison

# ===== EXPORTED FUNCTIONS =====

__all__ = [
    # Core parameter management
    'get_parameter', 'set_parameter', 'get_all_parameters',
    'get_configuration_types', 'create_configuration_type', 'clear_configuration_cache',
    
    # Configuration tier management
    'get_interface_configuration', 'get_system_configuration', 'validate_configuration',
    'apply_configuration_overrides_to_base',
    
    # Preset management
    'get_available_presets', 'get_preset_details', 'apply_preset', 'list_preset_names',
    
    # Resource estimation and validation
    'estimate_memory_usage', 'estimate_metrics_usage', 'get_memory_allocation_summary',
    'validate_aws_constraints',
    
    # Optimization functions
    'optimize_for_memory_constraint', 'optimize_for_performance', 'optimize_for_cost_protection',
    'get_optimization_recommendations',
    
    # Analysis and monitoring
    'analyze_configuration_compliance', 'get_configuration_health_status',
    
    # Utility functions
    'create_custom_configuration', 'compare_configurations',
    
    # Configuration enums and types
    'ConfigurationTier', 'InterfaceType'
]
