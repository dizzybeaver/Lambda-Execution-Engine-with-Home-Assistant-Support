"""
variables.py - Ultra-Optimized Configuration System Core Data Structure
Version: 2025.09.26.02
Description: Four-tier configuration system with inheritance, override management, and resource constraint validation

PHASE 2 IMPLEMENTATION: Primary Interface Configuration Complete
- Cache Interface: Memory allocation strategies and eviction policies
- Logging Interface: CloudWatch cost management and granular controls  
- Metrics Interface: 10-metric limit management with intelligent rotation
- Security Interface: Protection scaling without compromising security

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

# ===== PHASE 2: PRIMARY INTERFACE CONFIGURATIONS =====

# Cache Interface Configuration - Memory allocation and eviction strategies
CACHE_INTERFACE_CONFIG = {
    ConfigurationTier.MINIMUM: {
        # Survival mode - absolute minimum cache allocation
        "cache_pools": {
            "lambda_cache_size_mb": 1,
            "response_cache_size_mb": 1,
            "session_cache_size_mb": 0.5,
            "total_cache_allocation_mb": 2.5
        },
        "eviction_policies": {
            "default_policy": "immediate_lru",
            "memory_pressure_threshold": 0.95,
            "emergency_cleanup_enabled": True,
            "aggressive_cleanup_interval": 30
        },
        "cache_operations": {
            "default_ttl": 60,
            "max_ttl": 300,
            "cache_validation_enabled": False,
            "cache_encryption_enabled": False,
            "background_cleanup_enabled": False
        }
    },
    
    ConfigurationTier.STANDARD: {
        # Production balance - proven cache configurations
        "cache_pools": {
            "lambda_cache_size_mb": 4,
            "response_cache_size_mb": 3,
            "session_cache_size_mb": 1,
            "total_cache_allocation_mb": 8
        },
        "eviction_policies": {
            "default_policy": "smart_lru",
            "memory_pressure_threshold": 0.85,
            "emergency_cleanup_enabled": True,
            "aggressive_cleanup_interval": 120
        },
        "cache_operations": {
            "default_ttl": 300,
            "max_ttl": 1800,
            "cache_validation_enabled": True,
            "cache_encryption_enabled": True,
            "background_cleanup_enabled": True
        }
    },
    
    ConfigurationTier.MAXIMUM: {
        # Performance mode - maximum cache within constraints
        "cache_pools": {
            "lambda_cache_size_mb": 12,
            "response_cache_size_mb": 8,
            "session_cache_size_mb": 4,
            "total_cache_allocation_mb": 24
        },
        "eviction_policies": {
            "default_policy": "adaptive_lru_with_frequency",
            "memory_pressure_threshold": 0.75,
            "emergency_cleanup_enabled": True,
            "aggressive_cleanup_interval": 300
        },
        "cache_operations": {
            "default_ttl": 600,
            "max_ttl": 3600,
            "cache_validation_enabled": True,
            "cache_encryption_enabled": True,
            "background_cleanup_enabled": True,
            "pre_warming_enabled": True,
            "cache_analytics_enabled": True
        }
    }
}

# Logging Interface Configuration - CloudWatch cost management and granular controls
LOGGING_INTERFACE_CONFIG = {
    ConfigurationTier.MINIMUM: {
        # Survival mode - critical logging only
        "log_levels": {
            "default_level": "ERROR",
            "security_level": "WARNING", 
            "performance_level": "CRITICAL",
            "debug_level": "OFF",
            "operational_level": "ERROR"
        },
        "log_categories": {
            "security_logging_enabled": True,
            "performance_logging_enabled": False,
            "debug_logging_enabled": False,
            "operational_logging_enabled": True,
            "audit_logging_enabled": False
        },
        "cost_management": {
            "log_sampling_rate": 0.1,
            "batch_size": 1,
            "flush_interval": 300,
            "retention_days": 1,
            "cloudwatch_cost_limit_mb": 50
        }
    },
    
    ConfigurationTier.STANDARD: {
        # Production balance - essential logging with cost awareness
        "log_levels": {
            "default_level": "INFO",
            "security_level": "INFO",
            "performance_level": "WARNING", 
            "debug_level": "OFF",
            "operational_level": "INFO"
        },
        "log_categories": {
            "security_logging_enabled": True,
            "performance_logging_enabled": True,
            "debug_logging_enabled": False,
            "operational_logging_enabled": True,
            "audit_logging_enabled": True
        },
        "cost_management": {
            "log_sampling_rate": 0.5,
            "batch_size": 10,
            "flush_interval": 120,
            "retention_days": 7,
            "cloudwatch_cost_limit_mb": 200
        }
    },
    
    ConfigurationTier.MAXIMUM: {
        # Performance mode - comprehensive logging for analysis
        "log_levels": {
            "default_level": "DEBUG",
            "security_level": "DEBUG",
            "performance_level": "DEBUG",
            "debug_level": "DEBUG", 
            "operational_level": "DEBUG"
        },
        "log_categories": {
            "security_logging_enabled": True,
            "performance_logging_enabled": True,
            "debug_logging_enabled": True,
            "operational_logging_enabled": True,
            "audit_logging_enabled": True,
            "analytics_logging_enabled": True,
            "trace_logging_enabled": True
        },
        "cost_management": {
            "log_sampling_rate": 1.0,
            "batch_size": 25,
            "flush_interval": 60,
            "retention_days": 14,
            "cloudwatch_cost_limit_mb": 500
        }
    }
}

# Metrics Interface Configuration - CloudWatch 10-metric limit management
METRICS_INTERFACE_CONFIG = {
    ConfigurationTier.MINIMUM: {
        # Survival mode - mission-critical metrics only
        "metric_priorities": {
            "mission_critical": ["lambda_duration", "memory_usage", "error_rate", "invocation_count"],
            "performance_optimization": [],
            "business_intelligence": [],
            "development_debug": []
        },
        "metric_allocation": {
            "total_metrics_used": 4,
            "metrics_available": 6,
            "rotation_enabled": False,
            "temporary_metrics_slots": 0
        },
        "metric_settings": {
            "collection_interval": 300,
            "aggregation_period": 900,
            "retention_period": 2592000,  # 30 days
            "cost_protection_enabled": True
        }
    },
    
    ConfigurationTier.STANDARD: {
        # Production balance - core metrics with selective optimization
        "metric_priorities": {
            "mission_critical": ["lambda_duration", "memory_usage", "error_rate", "invocation_count"],
            "performance_optimization": ["cache_hit_rate", "response_time"],
            "business_intelligence": [],
            "development_debug": []
        },
        "metric_allocation": {
            "total_metrics_used": 6,
            "metrics_available": 4,
            "rotation_enabled": True,
            "temporary_metrics_slots": 2
        },
        "metric_settings": {
            "collection_interval": 180,
            "aggregation_period": 600,
            "retention_period": 2592000,  # 30 days
            "cost_protection_enabled": True
        }
    },
    
    ConfigurationTier.MAXIMUM: {
        # Performance mode - full metric utilization with intelligent rotation
        "metric_priorities": {
            "mission_critical": ["lambda_duration", "memory_usage", "error_rate", "invocation_count"],
            "performance_optimization": ["cache_hit_rate", "response_time", "optimization_score"],
            "business_intelligence": ["usage_patterns", "cost_efficiency"],
            "development_debug": ["debug_counter"]
        },
        "metric_allocation": {
            "total_metrics_used": 10,
            "metrics_available": 0,
            "rotation_enabled": True,
            "temporary_metrics_slots": 3
        },
        "metric_settings": {
            "collection_interval": 60,
            "aggregation_period": 300,
            "retention_period": 5184000,  # 60 days
            "cost_protection_enabled": True,
            "intelligent_rotation_enabled": True,
            "analytics_enabled": True
        }
    }
}

# Security Interface Configuration - Protection scaling without compromise
SECURITY_INTERFACE_CONFIG = {
    ConfigurationTier.MINIMUM: {
        # Survival mode - essential security only
        "validation_settings": {
            "input_validation_level": "basic",
            "threat_detection_level": "critical_only",
            "authentication_caching_enabled": False,
            "authorization_caching_enabled": False,
            "comprehensive_audit_enabled": False
        },
        "security_operations": {
            "tls_verification_bypass_allowed": True,
            "certificate_validation_level": "minimal",
            "rate_limiting_enabled": False,
            "threat_detection_algorithms": ["basic_pattern_match"],
            "security_response_time_priority": "fast"
        },
        "resource_allocation": {
            "validation_memory_mb": 1,
            "threat_detection_memory_mb": 0.5,
            "cache_allocation_mb": 0,
            "total_security_memory_mb": 1.5
        }
    },
    
    ConfigurationTier.STANDARD: {
        # Production balance - robust security with efficiency
        "validation_settings": {
            "input_validation_level": "standard",
            "threat_detection_level": "standard",
            "authentication_caching_enabled": True,
            "authorization_caching_enabled": True,
            "comprehensive_audit_enabled": True
        },
        "security_operations": {
            "tls_verification_bypass_allowed": True,
            "certificate_validation_level": "standard",
            "rate_limiting_enabled": True,
            "threat_detection_algorithms": ["pattern_match", "anomaly_detection"],
            "security_response_time_priority": "balanced"
        },
        "resource_allocation": {
            "validation_memory_mb": 3,
            "threat_detection_memory_mb": 2,
            "cache_allocation_mb": 1,
            "total_security_memory_mb": 6
        }
    },
    
    ConfigurationTier.MAXIMUM: {
        # Performance mode - comprehensive security analysis
        "validation_settings": {
            "input_validation_level": "comprehensive",
            "threat_detection_level": "advanced",
            "authentication_caching_enabled": True,
            "authorization_caching_enabled": True,
            "comprehensive_audit_enabled": True,
            "behavioral_analysis_enabled": True
        },
        "security_operations": {
            "tls_verification_bypass_allowed": False,
            "certificate_validation_level": "strict",
            "rate_limiting_enabled": True,
            "threat_detection_algorithms": ["pattern_match", "anomaly_detection", "ml_behavior_analysis"],
            "security_response_time_priority": "thorough",
            "advanced_threat_protection_enabled": True
        },
        "resource_allocation": {
            "validation_memory_mb": 8,
            "threat_detection_memory_mb": 6,
            "cache_allocation_mb": 3,
            "behavioral_analysis_mb": 2,
            "total_security_memory_mb": 19
        }
    }
}

# ===== PHASE 2: RESOURCE ESTIMATION FUNCTIONS =====

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

def estimate_metrics_count(tier: ConfigurationTier) -> int:
    """Estimate CloudWatch metrics usage for metrics configuration tier."""
    config = METRICS_INTERFACE_CONFIG.get(tier, METRICS_INTERFACE_CONFIG[ConfigurationTier.MINIMUM])
    return config["metric_allocation"]["total_metrics_used"]

# ===== PHASE 2: INTERFACE CONFIGURATION ACCESS FUNCTIONS =====

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

# ===== PHASE 2: VALIDATION ENHANCEMENT FUNCTIONS =====

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

def validate_override_combination(base_tier: ConfigurationTier, 
                                overrides: Dict[InterfaceType, ConfigurationTier]) -> Dict[str, Any]:
    """Enhanced validation with Phase 2 interface constraint checking."""
    
    # Get effective tiers for each interface
    cache_tier = overrides.get(InterfaceType.CACHE, base_tier)
    logging_tier = overrides.get(InterfaceType.LOGGING, base_tier)
    metrics_tier = overrides.get(InterfaceType.METRICS, base_tier)
    security_tier = overrides.get(InterfaceType.SECURITY, base_tier)
    
    # Validate Phase 2 constraints
    phase2_validation = validate_phase2_memory_constraints(cache_tier, logging_tier, metrics_tier, security_tier)
    
    # Calculate comprehensive resource estimates
    total_memory = phase2_validation["memory_usage"]["system_total_mb"]
    total_metrics = phase2_validation["metrics_usage"]["metrics_used"]
    
    validation_result = {
        "is_valid": phase2_validation["is_valid"],
        "memory_estimate": total_memory,
        "metric_estimate": total_metrics,
        "interface_breakdown": {
            "cache": {"tier": cache_tier.value, "memory_mb": phase2_validation["memory_usage"]["cache_mb"]},
            "logging": {"tier": logging_tier.value, "memory_mb": phase2_validation["memory_usage"]["logging_mb"]},
            "metrics": {"tier": metrics_tier.value, "memory_mb": phase2_validation["memory_usage"]["metrics_mb"]},
            "security": {"tier": security_tier.value, "memory_mb": phase2_validation["memory_usage"]["security_mb"]}
        },
        "warnings": phase2_validation["warnings"],
        "recommendations": []
    }
    
    # Add intelligent recommendations
    if not phase2_validation["is_valid"]:
        if total_memory > 128:
            validation_result["recommendations"].append("Consider reducing cache or security tiers to lower memory usage")
        if total_metrics > 10:
            validation_result["recommendations"].append("Reduce metrics tier or enable metric rotation")
    
    return validation_result

# ===== CONFIGURATION PRESETS =====

# Predefined configurations for common use cases
CONFIGURATION_PRESETS = {
    "ultra_conservative": {
        "base_tier": ConfigurationTier.MINIMUM,
        "overrides": {},
        "description": "Absolute minimum resource usage - survival mode",
        "memory_estimate": 8,
        "metric_estimate": 4
    },
    
    "production_balanced": {
        "base_tier": ConfigurationTier.STANDARD,
        "overrides": {},
        "description": "Balanced production configuration - recommended default",
        "memory_estimate": 32,
        "metric_estimate": 6
    },
    
    "performance_optimized": {
        "base_tier": ConfigurationTier.STANDARD,
        "overrides": {
            InterfaceType.CACHE: ConfigurationTier.MAXIMUM,
            InterfaceType.METRICS: ConfigurationTier.MAXIMUM,
        },
        "description": "High performance with maximum cache and metrics",
        "memory_estimate": 56,
        "metric_estimate": 10
    },
    
    "development_debug": {
        "base_tier": ConfigurationTier.STANDARD,
        "overrides": {
            InterfaceType.LOGGING: ConfigurationTier.MAXIMUM,
            InterfaceType.UTILITY: ConfigurationTier.MAXIMUM,
        },
        "description": "Enhanced logging and debugging for development", 
        "memory_estimate": 48,
        "metric_estimate": 7
    },
    
    "security_focused": {
        "base_tier": ConfigurationTier.STANDARD,
        "overrides": {
            InterfaceType.SECURITY: ConfigurationTier.MAXIMUM,
            InterfaceType.LOGGING: ConfigurationTier.MAXIMUM,
        },
        "description": "Maximum security validation and audit logging",
        "memory_estimate": 64,
        "metric_estimate": 8
    },
    
    "resource_constrained": {
        "base_tier": ConfigurationTier.MINIMUM,
        "overrides": {
            InterfaceType.CACHE: ConfigurationTier.STANDARD,
        },
        "description": "Minimal resources with standard caching",
        "memory_estimate": 16,
        "metric_estimate": 5
    },
    
    "cache_optimized": {
        "base_tier": ConfigurationTier.MINIMUM,
        "overrides": {
            InterfaceType.CACHE: ConfigurationTier.MAXIMUM,
        },
        "description": "Maximum cache performance with minimal other resources",
        "memory_estimate": 32,
        "metric_estimate": 5
    },
    
    "logging_intensive": {
        "base_tier": ConfigurationTier.MINIMUM,
        "overrides": {
            InterfaceType.LOGGING: ConfigurationTier.MAXIMUM,
            InterfaceType.SECURITY: ConfigurationTier.STANDARD,
        },
        "description": "Comprehensive logging for troubleshooting and analysis",
        "memory_estimate": 24,
        "metric_estimate": 6
    },
    
    "metrics_monitoring": {
        "base_tier": ConfigurationTier.MINIMUM,
        "overrides": {
            InterfaceType.METRICS: ConfigurationTier.MAXIMUM,
            InterfaceType.CACHE: ConfigurationTier.STANDARD,
        },
        "description": "Maximum metrics collection for performance monitoring",
        "memory_estimate": 20,
        "metric_estimate": 10
    },
    
    "security_hardened": {
        "base_tier": ConfigurationTier.MINIMUM,
        "overrides": {
            InterfaceType.SECURITY: ConfigurationTier.MAXIMUM,
        },
        "description": "Maximum security validation with minimal resource usage",
        "memory_estimate": 28,
        "metric_estimate": 4
    }
}

# ===== RUNTIME CONFIGURATION SELECTION =====

def get_preset_configuration(preset_name: str) -> Dict[str, Any]:
    """
    Get a predefined configuration preset.
    Returns the complete configuration for the specified preset.
    """
    if preset_name not in CONFIGURATION_PRESETS:
        return get_full_system_configuration(ConfigurationTier.STANDARD, {})
    
    preset = CONFIGURATION_PRESETS[preset_name]
    return get_full_system_configuration(preset["base_tier"], preset["overrides"])

def apply_configuration_overrides(base_tier: ConfigurationTier, 
                                overrides: Dict[InterfaceType, ConfigurationTier]) -> Dict[str, Any]:
    """
    Apply interface-specific overrides to base tier configuration.
    Enhanced for Phase 2 primary interfaces.
    """
    configuration = {}
    
    # Apply Cache configuration
    cache_tier = overrides.get(InterfaceType.CACHE, base_tier)
    configuration["cache"] = get_cache_configuration(cache_tier)
    
    # Apply Logging configuration  
    logging_tier = overrides.get(InterfaceType.LOGGING, base_tier)
    configuration["logging"] = get_logging_configuration(logging_tier)
    
    # Apply Metrics configuration
    metrics_tier = overrides.get(InterfaceType.METRICS, base_tier)
    configuration["metrics"] = get_metrics_configuration(metrics_tier)
    
    # Apply Security configuration
    security_tier = overrides.get(InterfaceType.SECURITY, base_tier)
    configuration["security"] = get_security_configuration(security_tier)
    
    # Placeholder for future phases - these will be implemented in subsequent phases
    placeholder_config = {"tier": base_tier.value, "status": "placeholder"}
    
    configuration["circuit_breaker"] = placeholder_config
    configuration["singleton"] = placeholder_config  
    configuration["lambda"] = placeholder_config
    configuration["http_client"] = placeholder_config
    configuration["utility"] = placeholder_config
    configuration["initialization"] = placeholder_config
    
    return configuration

def get_full_system_configuration(base_tier: ConfigurationTier, 
                                overrides: Optional[Dict[InterfaceType, ConfigurationTier]] = None) -> Dict[str, Any]:
    """
    Get complete system configuration with tier inheritance and overrides.
    Enhanced for Phase 2 with full validation and resource estimation.
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
        "phase2_status": "implemented",
        "interfaces_implemented": ["cache", "logging", "metrics", "security"],
        "interfaces_pending": ["circuit_breaker", "singleton", "lambda", "http_client", "utility", "initialization"]
    }
    
    return final_config

# ===== PHASE 2: INTERFACE-SPECIFIC GETTER FUNCTIONS =====

def get_interface_configuration(interface: InterfaceType, tier: ConfigurationTier) -> Dict[str, Any]:
    """
    Get configuration for a specific interface at specified tier.
    Enhanced for Phase 2 primary interfaces.
    """
    interface_getters = {
        InterfaceType.CACHE: get_cache_configuration,
        InterfaceType.LOGGING: get_logging_configuration,
        InterfaceType.METRICS: get_metrics_configuration,
        InterfaceType.SECURITY: get_security_configuration
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

# ===== PHASE 2: CONFIGURATION UTILITY FUNCTIONS =====

def list_configuration_presets() -> List[Dict[str, Any]]:
    """List all available configuration presets with Phase 2 resource estimates."""
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

def get_tier_memory_breakdown(tier: ConfigurationTier) -> Dict[str, float]:
    """Get detailed memory breakdown for a specific tier across Phase 2 interfaces."""
    return {
        "cache_mb": estimate_cache_memory_usage(tier),
        "logging_mb": estimate_logging_memory_usage(tier),
        "metrics_mb": estimate_metrics_memory_usage(tier),
        "security_mb": estimate_security_memory_usage(tier),
        "total_phase2_mb": (estimate_cache_memory_usage(tier) + 
                           estimate_logging_memory_usage(tier) + 
                           estimate_metrics_memory_usage(tier) + 
                           estimate_security_memory_usage(tier))
    }

def recommend_configuration_for_memory_limit(target_memory_mb: int) -> Dict[str, Any]:
    """Recommend optimal configuration combination for specified memory limit."""
    recommendations = []
    
    # Try different tier combinations to find optimal fit
    for cache_tier in [ConfigurationTier.MINIMUM, ConfigurationTier.STANDARD, ConfigurationTier.MAXIMUM]:
        for security_tier in [ConfigurationTier.MINIMUM, ConfigurationTier.STANDARD, ConfigurationTier.MAXIMUM]:
            for logging_tier in [ConfigurationTier.MINIMUM, ConfigurationTier.STANDARD]:
                for metrics_tier in [ConfigurationTier.MINIMUM, ConfigurationTier.STANDARD]:
                    
                    validation = validate_phase2_memory_constraints(cache_tier, logging_tier, metrics_tier, security_tier)
                    total_memory = validation["memory_usage"]["system_total_mb"]
                    
                    if total_memory <= target_memory_mb and validation["is_valid"]:
                        recommendations.append({
                            "configuration": {
                                "cache": cache_tier.value,
                                "logging": logging_tier.value,
                                "metrics": metrics_tier.value,
                                "security": security_tier.value
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

# ===== END OF PHASE 2 IMPLEMENTATION =====
