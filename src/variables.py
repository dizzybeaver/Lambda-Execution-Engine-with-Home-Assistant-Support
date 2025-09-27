"""
variables.py - Ultra-Optimized Configuration System Core Data Structure
Version: 2025.09.26.03
Description: Four-tier configuration system with inheritance, override management, and resource constraint validation

PHASE 3 IMPLEMENTATION: Pure Data Structures Only
- Configuration tier definitions and interface types
- Phase 2: Cache, Logging, Metrics, Security configurations
- Phase 3: Circuit Breaker, Singleton configurations
- Configuration presets for common use cases

ARCHITECTURE: EXTERNAL DATA FILE - PURE DATA STRUCTURE
- Accessed ONLY through config.py gateway
- Contains configuration data structures ONLY - no functions
- All utility functions moved to variables_utils.py
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

# ===== PHASE 3: SPECIALIZED INTERFACE CONFIGURATIONS =====

# Circuit Breaker Interface Configuration - Service-specific policies and failure pattern recognition
CIRCUIT_BREAKER_INTERFACE_CONFIG = {
    ConfigurationTier.MINIMUM: {
        # Survival mode - basic circuit breaker protection
        "circuit_breaker_policies": {
            "cloudwatch_api": {
                "failure_threshold": 5,
                "recovery_timeout": 60,
                "half_open_max_calls": 1,
                "timeout": 10
            },
            "home_assistant_devices": {
                "failure_threshold": 3,
                "recovery_timeout": 30,
                "half_open_max_calls": 1,
                "timeout": 5
            },
            "external_http": {
                "failure_threshold": 3,
                "recovery_timeout": 30,
                "half_open_max_calls": 1,
                "timeout": 10
            }
        },
        "failure_detection": {
            "pattern_recognition_enabled": False,
            "cascade_prevention_enabled": False,
            "intelligent_recovery_enabled": False,
            "failure_pattern_analysis": "basic"
        },
        "resource_allocation": {
            "circuit_breaker_memory_mb": 1,
            "failure_tracking_memory_mb": 0.5,
            "total_circuit_breaker_memory_mb": 1.5
        }
    },
    
    ConfigurationTier.STANDARD: {
        # Production balance - smart circuit breaker policies
        "circuit_breaker_policies": {
            "cloudwatch_api": {
                "failure_threshold": 3,
                "recovery_timeout": 45,
                "half_open_max_calls": 2,
                "timeout": 15,
                "slow_call_threshold": 10
            },
            "home_assistant_devices": {
                "failure_threshold": 2,
                "recovery_timeout": 20,
                "half_open_max_calls": 2,
                "timeout": 8,
                "slow_call_threshold": 5
            },
            "external_http": {
                "failure_threshold": 2,
                "recovery_timeout": 25,
                "half_open_max_calls": 2,
                "timeout": 12,
                "slow_call_threshold": 8
            }
        },
        "failure_detection": {
            "pattern_recognition_enabled": True,
            "cascade_prevention_enabled": True,
            "intelligent_recovery_enabled": True,
            "failure_pattern_analysis": "standard",
            "rolling_window_size": 100
        },
        "resource_allocation": {
            "circuit_breaker_memory_mb": 3,
            "failure_tracking_memory_mb": 2,
            "pattern_analysis_memory_mb": 1,
            "total_circuit_breaker_memory_mb": 6
        }
    },
    
    ConfigurationTier.MAXIMUM: {
        # Performance mode - advanced circuit breaker intelligence
        "circuit_breaker_policies": {
            "cloudwatch_api": {
                "failure_threshold": 2,
                "recovery_timeout": 30,
                "half_open_max_calls": 3,
                "timeout": 20,
                "slow_call_threshold": 15,
                "adaptive_timeout_enabled": True
            },
            "home_assistant_devices": {
                "failure_threshold": 1,
                "recovery_timeout": 15,
                "half_open_max_calls": 3,
                "timeout": 10,
                "slow_call_threshold": 3,
                "adaptive_timeout_enabled": True
            },
            "external_http": {
                "failure_threshold": 1,
                "recovery_timeout": 20,
                "half_open_max_calls": 3,
                "timeout": 15,
                "slow_call_threshold": 5,
                "adaptive_timeout_enabled": True
            }
        },
        "failure_detection": {
            "pattern_recognition_enabled": True,
            "cascade_prevention_enabled": True,
            "intelligent_recovery_enabled": True,
            "failure_pattern_analysis": "advanced",
            "rolling_window_size": 500,
            "ml_pattern_detection_enabled": True,
            "predictive_circuit_breaking_enabled": True
        },
        "resource_allocation": {
            "circuit_breaker_memory_mb": 8,
            "failure_tracking_memory_mb": 6,
            "pattern_analysis_memory_mb": 4,
            "ml_detection_memory_mb": 3,
            "total_circuit_breaker_memory_mb": 21
        }
    }
}

# Singleton Interface Configuration - Memory coordination and lifecycle management
SINGLETON_INTERFACE_CONFIG = {
    ConfigurationTier.MINIMUM: {
        # Survival mode - essential singletons only
        "singleton_registry": {
            "max_singletons": 5,
            "memory_pressure_threshold": 0.95,
            "cleanup_interval": 60,
            "emergency_cleanup_enabled": True
        },
        "singleton_types": {
            "cache_manager": {
                "memory_allocation_mb": 1,
                "priority": "critical",
                "cleanup_strategy": "maintain"
            },
            "security_validator": {
                "memory_allocation_mb": 0.5,
                "priority": "critical", 
                "cleanup_strategy": "maintain"
            },
            "config_manager": {
                "memory_allocation_mb": 0.3,
                "priority": "high",
                "cleanup_strategy": "reduce"
            }
        },
        "memory_coordination": {
            "pressure_response_enabled": True,
            "voluntary_reduction_enabled": False,
            "suspension_enabled": False,
            "coordinated_cleanup_enabled": True
        },
        "resource_allocation": {
            "singleton_registry_memory_mb": 0.5,
            "coordination_memory_mb": 0.2,
            "total_singleton_overhead_mb": 0.7
        }
    },
    
    ConfigurationTier.STANDARD: {
        # Production balance - managed singleton coordination
        "singleton_registry": {
            "max_singletons": 10,
            "memory_pressure_threshold": 0.85,
            "cleanup_interval": 120,
            "emergency_cleanup_enabled": True,
            "proactive_management_enabled": True
        },
        "singleton_types": {
            "cache_manager": {
                "memory_allocation_mb": 2,
                "priority": "critical",
                "cleanup_strategy": "maintain"
            },
            "security_validator": {
                "memory_allocation_mb": 1,
                "priority": "critical",
                "cleanup_strategy": "maintain"
            },
            "config_manager": {
                "memory_allocation_mb": 0.5,
                "priority": "high",
                "cleanup_strategy": "reduce"
            },
            "response_processor": {
                "memory_allocation_mb": 1.5,
                "priority": "high",
                "cleanup_strategy": "reduce"
            },
            "lambda_optimizer": {
                "memory_allocation_mb": 1,
                "priority": "medium",
                "cleanup_strategy": "suspend"
            }
        },
        "memory_coordination": {
            "pressure_response_enabled": True,
            "voluntary_reduction_enabled": True,
            "suspension_enabled": True,
            "coordinated_cleanup_enabled": True,
            "priority_based_management": True
        },
        "resource_allocation": {
            "singleton_registry_memory_mb": 1,
            "coordination_memory_mb": 1,
            "management_overhead_mb": 0.5,
            "total_singleton_overhead_mb": 2.5
        }
    },
    
    ConfigurationTier.MAXIMUM: {
        # Performance mode - advanced singleton orchestration
        "singleton_registry": {
            "max_singletons": 15,
            "memory_pressure_threshold": 0.75,
            "cleanup_interval": 300,
            "emergency_cleanup_enabled": True,
            "proactive_management_enabled": True,
            "predictive_coordination_enabled": True
        },
        "singleton_types": {
            "cache_manager": {
                "memory_allocation_mb": 4,
                "priority": "critical",
                "cleanup_strategy": "maintain"
            },
            "security_validator": {
                "memory_allocation_mb": 2,
                "priority": "critical",
                "cleanup_strategy": "maintain"
            },
            "config_manager": {
                "memory_allocation_mb": 1,
                "priority": "high",
                "cleanup_strategy": "reduce"
            },
            "response_processor": {
                "memory_allocation_mb": 3,
                "priority": "high",
                "cleanup_strategy": "reduce"
            },
            "lambda_optimizer": {
                "memory_allocation_mb": 2,
                "priority": "medium",
                "cleanup_strategy": "suspend"
            },
            "memory_manager": {
                "memory_allocation_mb": 2,
                "priority": "medium",
                "cleanup_strategy": "suspend"
            },
            "metrics_manager": {
                "memory_allocation_mb": 1.5,
                "priority": "low",
                "cleanup_strategy": "suspend"
            }
        },
        "memory_coordination": {
            "pressure_response_enabled": True,
            "voluntary_reduction_enabled": True,
            "suspension_enabled": True,
            "coordinated_cleanup_enabled": True,
            "priority_based_management": True,
            "predictive_memory_management": True,
            "dynamic_allocation_enabled": True
        },
        "resource_allocation": {
            "singleton_registry_memory_mb": 2,
            "coordination_memory_mb": 2,
            "management_overhead_mb": 1,
            "predictive_system_mb": 1,
            "total_singleton_overhead_mb": 6
        }
    }
}

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
    },
    
    "circuit_breaker_optimized": {
        "base_tier": ConfigurationTier.MINIMUM,
        "overrides": {
            InterfaceType.CIRCUIT_BREAKER: ConfigurationTier.MAXIMUM,
            InterfaceType.CACHE: ConfigurationTier.STANDARD,
        },
        "description": "Advanced circuit breaker protection with standard caching",
        "memory_estimate": 36,
        "metric_estimate": 5
    },
    
    "singleton_managed": {
        "base_tier": ConfigurationTier.MINIMUM,
        "overrides": {
            InterfaceType.SINGLETON: ConfigurationTier.MAXIMUM,
            InterfaceType.SECURITY: ConfigurationTier.STANDARD,
        },
        "description": "Advanced singleton coordination with standard security",
        "memory_estimate": 42,
        "metric_estimate": 5
    },
    
    "specialized_optimized": {
        "base_tier": ConfigurationTier.STANDARD,
        "overrides": {
            InterfaceType.CIRCUIT_BREAKER: ConfigurationTier.MAXIMUM,
            InterfaceType.SINGLETON: ConfigurationTier.MAXIMUM,
        },
        "description": "Maximum specialized interface performance",
        "memory_estimate": 72,
        "metric_estimate": 7
    },
    
    "reliability_focused": {
        "base_tier": ConfigurationTier.MINIMUM,
        "overrides": {
            InterfaceType.CIRCUIT_BREAKER: ConfigurationTier.MAXIMUM,
            InterfaceType.SECURITY: ConfigurationTier.MAXIMUM,
            InterfaceType.LOGGING: ConfigurationTier.STANDARD,
        },
        "description": "Maximum reliability and security with circuit breaker protection",
        "memory_estimate": 52,
        "metric_estimate": 6
    }
}

# ===== END OF PURE DATA STRUCTURES =====
