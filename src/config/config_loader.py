"""
config_loader.py
Version: 2025.10.11.01
Description: Load configuration from environment variables and config files with preset support

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
from typing import Dict, Any, Optional
from enum import Enum


class PresetLevel(Enum):
    """Preset levels for configuration categories."""
    MINIMAL = "minimal"
    STANDARD = "standard"
    MAXIMUM = "maximum"
    CUSTOM = "custom"


class ConfigCategory(Enum):
    """Configuration categories."""
    CACHE = "cache"
    LOGGING = "logging"
    METRICS = "metrics"
    SECURITY = "security"
    CIRCUIT_BREAKER = "circuit_breaker"
    SINGLETON = "singleton"
    HTTP_CLIENT = "http_client"
    LAMBDA_OPT = "lambda_opt"
    COST_PROTECTION = "cost_protection"
    UTILITY = "utility"
    INITIALIZATION = "initialization"


PRESET_CONFIGURATIONS = {
    ConfigCategory.CACHE: {
        PresetLevel.MINIMAL: {
            "total_cache_allocation_mb": 2.0,
            "lambda_cache_mb": 1.0,
            "response_cache_mb": 1.0,
            "utility_cache_mb": 0.0,
            "default_ttl_seconds": 60,
            "max_entries_per_pool": 50,
            "eviction_policy": "lru",
            "background_cleanup_enabled": False,
            "compression_enabled": False,
            "serialization_method": "pickle",
            "concurrent_access_enabled": False,
            "enable_pressure_monitoring": True,
            "pressure_check_interval_seconds": 30,
            "warning_threshold_percent": 85,
            "critical_threshold_percent": 95,
            "emergency_cleanup_threshold": 98
        },
        PresetLevel.STANDARD: {
            "total_cache_allocation_mb": 8.0,
            "lambda_cache_mb": 4.0,
            "response_cache_mb": 3.0,
            "utility_cache_mb": 1.0,
            "default_ttl_seconds": 300,
            "max_entries_per_pool": 200,
            "eviction_policy": "lru",
            "background_cleanup_enabled": True,
            "compression_enabled": True,
            "serialization_method": "json",
            "concurrent_access_enabled": True,
            "enable_pressure_monitoring": True,
            "pressure_check_interval_seconds": 10,
            "warning_threshold_percent": 75,
            "critical_threshold_percent": 85,
            "emergency_cleanup_threshold": 95
        },
        PresetLevel.MAXIMUM: {
            "total_cache_allocation_mb": 24.0,
            "lambda_cache_mb": 12.0,
            "response_cache_mb": 8.0,
            "utility_cache_mb": 4.0,
            "default_ttl_seconds": 600,
            "max_entries_per_pool": 500,
            "eviction_policy": "advanced_lru",
            "background_cleanup_enabled": True,
            "compression_enabled": True,
            "serialization_method": "optimized_json",
            "concurrent_access_enabled": True,
            "enable_pressure_monitoring": True,
            "pressure_check_interval_seconds": 5,
            "warning_threshold_percent": 70,
            "critical_threshold_percent": 80,
            "emergency_cleanup_threshold": 90
        }
    },
    
    ConfigCategory.LOGGING: {
        PresetLevel.MINIMAL: {
            "default_level": "ERROR",
            "interface_levels": {"cache": "ERROR", "security": "ERROR", "metrics": "ERROR"},
            "include_timestamps": True,
            "include_caller_info": False,
            "structured_logging": False,
            "console_enabled": True,
            "file_enabled": False,
            "cloudwatch_enabled": False,
            "enable_batching": True,
            "batch_size": 5,
            "flush_interval_seconds": 60
        },
        PresetLevel.STANDARD: {
            "default_level": "INFO",
            "interface_levels": {"cache": "INFO", "security": "INFO", "metrics": "INFO", "circuit_breaker": "INFO"},
            "include_timestamps": True,
            "include_caller_info": True,
            "structured_logging": True,
            "console_enabled": True,
            "file_enabled": False,
            "cloudwatch_enabled": True,
            "enable_batching": True,
            "batch_size": 10,
            "flush_interval_seconds": 30
        },
        PresetLevel.MAXIMUM: {
            "default_level": "DEBUG",
            "interface_levels": {"cache": "DEBUG", "security": "DEBUG", "metrics": "DEBUG", "circuit_breaker": "DEBUG", "singleton": "DEBUG"},
            "include_timestamps": True,
            "include_caller_info": True,
            "structured_logging": True,
            "console_enabled": True,
            "file_enabled": True,
            "cloudwatch_enabled": True,
            "enable_batching": True,
            "batch_size": 20,
            "flush_interval_seconds": 15
        }
    },
    
    ConfigCategory.METRICS: {
        PresetLevel.MINIMAL: {
            "total_metrics_used": 4,
            "core_metrics": ["memory_usage", "error_count", "invocation_count", "duration"],
            "optional_metrics": [],
            "custom_metrics": [],
            "collection_interval_seconds": 60,
            "batch_submission": True,
            "metric_buffering": False,
            "namespace": "Lambda/Ultra-Optimized",
            "dimension_strategy": "minimal",
            "api_call_optimization": True
        },
        PresetLevel.STANDARD: {
            "total_metrics_used": 6,
            "core_metrics": ["memory_usage", "error_count", "invocation_count", "duration"],
            "optional_metrics": ["cache_hit_rate", "cost_protection_status"],
            "custom_metrics": [],
            "collection_interval_seconds": 30,
            "batch_submission": True,
            "metric_buffering": True,
            "namespace": "Lambda/Ultra-Optimized",
            "dimension_strategy": "standard",
            "api_call_optimization": True
        },
        PresetLevel.MAXIMUM: {
            "total_metrics_used": 10,
            "core_metrics": ["memory_usage", "error_count", "invocation_count", "duration"],
            "optional_metrics": ["cache_hit_rate", "cost_protection_status", "security_events", "circuit_breaker_status"],
            "custom_metrics": ["performance_score", "optimization_events"],
            "collection_interval_seconds": 15,
            "batch_submission": True,
            "metric_buffering": True,
            "namespace": "Lambda/Ultra-Optimized",
            "dimension_strategy": "comprehensive",
            "api_call_optimization": True
        }
    },
    
    ConfigCategory.SECURITY: {
        PresetLevel.MINIMAL: {
            "total_security_memory_mb": 1.0,
            "validation_memory_mb": 0.5,
            "threat_detection_memory_mb": 0.5,
            "validation_level": "basic",
            "sanitization_enabled": True,
            "pattern_matching_enabled": False,
            "anomaly_detection_enabled": False,
            "rate_limiting_enabled": True,
            "behavioral_analysis_enabled": False,
            "security_events_logged": False,
            "audit_trail_enabled": False,
            "security_metrics_enabled": False
        },
        PresetLevel.STANDARD: {
            "total_security_memory_mb": 4.0,
            "validation_memory_mb": 2.0,
            "threat_detection_memory_mb": 2.0,
            "validation_level": "standard",
            "sanitization_enabled": True,
            "pattern_matching_enabled": True,
            "anomaly_detection_enabled": True,
            "rate_limiting_enabled": True,
            "behavioral_analysis_enabled": False,
            "security_events_logged": True,
            "audit_trail_enabled": True,
            "security_metrics_enabled": True
        },
        PresetLevel.MAXIMUM: {
            "total_security_memory_mb": 12.0,
            "validation_memory_mb": 6.0,
            "threat_detection_memory_mb": 6.0,
            "validation_level": "comprehensive",
            "sanitization_enabled": True,
            "pattern_matching_enabled": True,
            "anomaly_detection_enabled": True,
            "rate_limiting_enabled": True,
            "behavioral_analysis_enabled": True,
            "security_events_logged": True,
            "audit_trail_enabled": True,
            "security_metrics_enabled": True
        }
    },
    
    ConfigCategory.CIRCUIT_BREAKER: {
        PresetLevel.MINIMAL: {
            "total_circuit_breaker_memory_mb": 0.5,
            "state_management_memory_mb": 0.3,
            "metrics_memory_mb": 0.2,
            "default_failure_threshold": 3,
            "default_recovery_timeout": 60,
            "failure_detection_window": 300,
            "cloudwatch_api": {"failure_threshold": 3, "recovery_timeout_seconds": 60, "max_test_calls": 1},
            "home_assistant": {"failure_threshold": 2, "recovery_timeout_seconds": 30, "max_test_calls": 1}
        },
        PresetLevel.STANDARD: {
            "total_circuit_breaker_memory_mb": 2.0,
            "state_management_memory_mb": 1.2,
            "metrics_memory_mb": 0.8,
            "default_failure_threshold": 3,
            "default_recovery_timeout": 45,
            "failure_detection_window": 300,
            "cloudwatch_api": {"failure_threshold": 3, "recovery_timeout_seconds": 45, "max_test_calls": 2},
            "home_assistant": {"failure_threshold": 2, "recovery_timeout_seconds": 20, "max_test_calls": 1},
            "external_http": {"failure_threshold": 3, "recovery_timeout_seconds": 30, "max_test_calls": 2}
        },
        PresetLevel.MAXIMUM: {
            "total_circuit_breaker_memory_mb": 6.0,
            "state_management_memory_mb": 3.6,
            "metrics_memory_mb": 2.4,
            "default_failure_threshold": 3,
            "default_recovery_timeout": 30,
            "failure_detection_window": 180,
            "cloudwatch_api": {"failure_threshold": 3, "recovery_timeout_seconds": 45, "max_test_calls": 2},
            "home_assistant": {"failure_threshold": 2, "recovery_timeout_seconds": 20, "max_test_calls": 1},
            "external_http": {"failure_threshold": 3, "recovery_timeout_seconds": 30, "max_test_calls": 2},
            "database": {"failure_threshold": 2, "recovery_timeout_seconds": 60, "max_test_calls": 1}
        }
    },
    
    ConfigCategory.SINGLETON: {
        PresetLevel.MINIMAL: {
            "total_singleton_overhead_mb": 2.0,
            "max_singletons": 5,
            "cleanup_threshold_percent": 95,
            "enable_lazy_initialization": True,
            "enable_automatic_disposal": True,
            "disposal_idle_timeout_seconds": 300,
            "enable_reference_counting": False,
            "pressure_response_enabled": True,
            "voluntary_reduction_enabled": False,
            "predictive_memory_management": False
        },
        PresetLevel.STANDARD: {
            "total_singleton_overhead_mb": 4.0,
            "max_singletons": 20,
            "cleanup_threshold_percent": 85,
            "enable_lazy_initialization": True,
            "enable_automatic_disposal": True,
            "disposal_idle_timeout_seconds": 600,
            "enable_reference_counting": True,
            "pressure_response_enabled": True,
            "voluntary_reduction_enabled": True,
            "predictive_memory_management": False
        },
        PresetLevel.MAXIMUM: {
            "total_singleton_overhead_mb": 6.0,
            "max_singletons": 50,
            "cleanup_threshold_percent": 75,
            "enable_lazy_initialization": True,
            "enable_automatic_disposal": True,
            "disposal_idle_timeout_seconds": 600,
            "enable_reference_counting": True,
            "pressure_response_enabled": True,
            "voluntary_reduction_enabled": True,
            "predictive_memory_management": True
        }
    },
    
    ConfigCategory.HTTP_CLIENT: {
        PresetLevel.MINIMAL: {
            "default_timeout_seconds": 15,
            "connect_timeout_seconds": 5,
            "read_timeout_seconds": 15,
            "pool_connections": 2,
            "pool_maxsize": 2,
            "pool_block": False,
            "max_retries": 1,
            "backoff_base_ms": 100,
            "backoff_multiplier": 2.0,
            "max_backoff_seconds": 30,
            "ssl_verify": True,
            "allow_redirects": True,
            "max_redirects": 3,
            "enable_dns_cache": False,
            "dns_cache_ttl_seconds": 300
        },
        PresetLevel.STANDARD: {
            "default_timeout_seconds": 30,
            "connect_timeout_seconds": 10,
            "read_timeout_seconds": 30,
            "pool_connections": 10,
            "pool_maxsize": 10,
            "pool_block": False,
            "max_retries": 3,
            "backoff_base_ms": 100,
            "backoff_multiplier": 2.0,
            "max_backoff_seconds": 120,
            "ssl_verify": True,
            "allow_redirects": True,
            "max_redirects": 5,
            "enable_dns_cache": True,
            "dns_cache_ttl_seconds": 300
        },
        PresetLevel.MAXIMUM: {
            "default_timeout_seconds": 60,
            "connect_timeout_seconds": 15,
            "read_timeout_seconds": 60,
            "pool_connections": 25,
            "pool_maxsize": 25,
            "pool_block": False,
            "max_retries": 5,
            "backoff_base_ms": 100,
            "backoff_multiplier": 2.0,
            "max_backoff_seconds": 300,
            "ssl_verify": True,
            "allow_redirects": True,
            "max_redirects": 10,
            "enable_dns_cache": True,
            "dns_cache_ttl_seconds": 600
        }
    },
    
    ConfigCategory.LAMBDA_OPT: {
        PresetLevel.MINIMAL: {
            "enable_lazy_loading": False,
            "enable_module_unloading": False,
            "module_unload_threshold_seconds": 300,
            "enable_aggressive_gc": False,
            "gc_threshold_percent": 90,
            "enable_memory_profiling": False,
            "enable_fast_path": False,
            "fast_path_threshold": 50,
            "max_concurrent_executions": 5,
            "reserved_concurrency": 0
        },
        PresetLevel.STANDARD: {
            "enable_lazy_loading": True,
            "enable_module_unloading": False,
            "module_unload_threshold_seconds": 300,
            "enable_aggressive_gc": False,
            "gc_threshold_percent": 80,
            "enable_memory_profiling": False,
            "enable_fast_path": True,
            "fast_path_threshold": 10,
            "max_concurrent_executions": 10,
            "reserved_concurrency": 0
        },
        PresetLevel.MAXIMUM: {
            "enable_lazy_loading": True,
            "enable_module_unloading": True,
            "module_unload_threshold_seconds": 300,
            "enable_aggressive_gc": True,
            "gc_threshold_percent": 75,
            "enable_memory_profiling": False,
            "enable_fast_path": True,
            "fast_path_threshold": 5,
            "max_concurrent_executions": 20,
            "reserved_concurrency": 0
        }
    },
    
    ConfigCategory.COST_PROTECTION: {
        PresetLevel.MINIMAL: {
            "lambda_invocations_monthly": 1000000,
            "lambda_compute_seconds_monthly": 400000,
            "cloudwatch_metrics_limit": 10,
            "cloudwatch_api_calls_monthly": 1000000,
            "warning_threshold_percent": 85.0,
            "critical_threshold_percent": 95.0,
            "emergency_threshold_percent": 98.0,
            "enable_emergency_mode": True,
            "emergency_mode_duration_seconds": 3600,
            "emergency_reset_threshold_percent": 80.0,
            "enable_real_time_tracking": False,
            "tracking_interval_seconds": 300,
            "enable_projected_usage": False
        },
        PresetLevel.STANDARD: {
            "lambda_invocations_monthly": 1000000,
            "lambda_compute_seconds_monthly": 400000,
            "cloudwatch_metrics_limit": 10,
            "cloudwatch_api_calls_monthly": 1000000,
            "warning_threshold_percent": 75.0,
            "critical_threshold_percent": 90.0,
            "emergency_threshold_percent": 95.0,
            "enable_emergency_mode": True,
            "emergency_mode_duration_seconds": 3600,
            "emergency_reset_threshold_percent": 70.0,
            "enable_real_time_tracking": True,
            "tracking_interval_seconds": 60,
            "enable_projected_usage": True
        },
        PresetLevel.MAXIMUM: {
            "lambda_invocations_monthly": 1000000,
            "lambda_compute_seconds_monthly": 400000,
            "cloudwatch_metrics_limit": 10,
            "cloudwatch_api_calls_monthly": 1000000,
            "warning_threshold_percent": 70.0,
            "critical_threshold_percent": 85.0,
            "emergency_threshold_percent": 92.0,
            "enable_emergency_mode": True,
            "emergency_mode_duration_seconds": 7200,
            "emergency_reset_threshold_percent": 65.0,
            "enable_real_time_tracking": True,
            "tracking_interval_seconds": 30,
            "enable_projected_usage": True
        }
    },
    
    ConfigCategory.UTILITY: {
        PresetLevel.MINIMAL: {
            "json_max_depth": 10,
            "json_max_size_kb": 50,
            "enable_response_transformation": False,
            "transformation_pipeline": ["validate"],
            "enable_correlation_id": False,
            "correlation_id_format": "uuid",
            "enable_detailed_errors": False,
            "error_retry_strategy": "immediate"
        },
        PresetLevel.STANDARD: {
            "json_max_depth": 20,
            "json_max_size_kb": 100,
            "enable_response_transformation": True,
            "transformation_pipeline": ["validate", "normalize"],
            "enable_correlation_id": True,
            "correlation_id_format": "uuid",
            "enable_detailed_errors": False,
            "error_retry_strategy": "backoff"
        },
        PresetLevel.MAXIMUM: {
            "json_max_depth": 50,
            "json_max_size_kb": 500,
            "enable_response_transformation": True,
            "transformation_pipeline": ["validate", "sanitize", "normalize", "enrich"],
            "enable_correlation_id": True,
            "correlation_id_format": "uuid",
            "enable_detailed_errors": True,
            "error_retry_strategy": "circuit_breaker"
        }
    },
    
    ConfigCategory.INITIALIZATION: {
        PresetLevel.MINIMAL: {
            "enable_warm_start_optimization": False,
            "preload_modules": [],
            "enable_startup_health_check": False,
            "health_check_timeout_seconds": 2,
            "health_check_services": [],
            "log_initialization_stages": False,
            "initialization_log_level": "ERROR"
        },
        PresetLevel.STANDARD: {
            "enable_warm_start_optimization": True,
            "preload_modules": [],
            "enable_startup_health_check": True,
            "health_check_timeout_seconds": 5,
            "health_check_services": ["cache", "logging"],
            "log_initialization_stages": True,
            "initialization_log_level": "INFO"
        },
        PresetLevel.MAXIMUM: {
            "enable_warm_start_optimization": True,
            "preload_modules": ["cache", "logging", "security"],
            "enable_startup_health_check": True,
            "health_check_timeout_seconds": 10,
            "health_check_services": ["cache", "logging", "security", "metrics"],
            "log_initialization_stages": True,
            "initialization_log_level": "DEBUG"
        }
    }
}


def get_env_preset(category: ConfigCategory) -> PresetLevel:
    """Get preset level from environment variable for a category."""
    env_var = f"{category.value.upper()}_PRESET"
    preset_value = os.getenv(env_var, "").lower()
    
    if preset_value == "minimal":
        return PresetLevel.MINIMAL
    elif preset_value == "standard":
        return PresetLevel.STANDARD
    elif preset_value == "maximum":
        return PresetLevel.MAXIMUM
    else:
        return PresetLevel.CUSTOM


def load_preset_config(category: ConfigCategory, preset: PresetLevel) -> Dict[str, Any]:
    """Load preset configuration for a category."""
    if preset == PresetLevel.CUSTOM:
        return {}
    
    return PRESET_CONFIGURATIONS.get(category, {}).get(preset, {}).copy()


def load_system_config() -> Dict[str, Any]:
    """Load complete system configuration from environment and presets."""
    config = {
        "system": {
            "aws_region": os.getenv("AWS_REGION", "us-east-1"),
            "parameter_prefix": os.getenv("PARAMETER_PREFIX", "/lambda-execution-engine"),
            "pythonnodebugranges": os.getenv("PYTHONNODEBUGRANGES", "") == "1"
        }
    }
    
    for category in ConfigCategory:
        preset = get_env_preset(category)
        category_config = load_preset_config(category, preset)
        
        config[category.value] = {
            "preset": preset.value,
            "settings": category_config
        }
    
    return config


def validate_configuration(config: Dict[str, Any]) -> Dict[str, Any]:
    """Validate configuration for memory and metric constraints."""
    validation = {
        "valid": True,
        "errors": [],
        "warnings": [],
        "memory_estimate_mb": 0.0,
        "metrics_count": 0
    }
    
    memory_allocations = {
        "application_base": 25.0,
        "buffer": 15.0
    }
    
    if "cache" in config and "settings" in config["cache"]:
        memory_allocations["cache"] = config["cache"]["settings"].get("total_cache_allocation_mb", 0)
    
    if "security" in config and "settings" in config["security"]:
        memory_allocations["security"] = config["security"]["settings"].get("total_security_memory_mb", 0)
    
    if "circuit_breaker" in config and "settings" in config["circuit_breaker"]:
        memory_allocations["circuit_breaker"] = config["circuit_breaker"]["settings"].get("total_circuit_breaker_memory_mb", 0)
    
    if "singleton" in config and "settings" in config["singleton"]:
        memory_allocations["singleton"] = config["singleton"]["settings"].get("total_singleton_overhead_mb", 0)
    
    memory_allocations["http_client"] = 5.0
    memory_allocations["logging"] = 3.0
    
    total_memory = sum(memory_allocations.values())
    validation["memory_estimate_mb"] = total_memory
    
    if total_memory > 128:
        validation["valid"] = False
        validation["errors"].append(f"Total memory allocation ({total_memory:.1f}MB) exceeds Lambda limit (128MB)")
    elif total_memory > 115:
        validation["warnings"].append(f"Total memory allocation ({total_memory:.1f}MB) approaching limit")
    
    if "metrics" in config and "settings" in config["metrics"]:
        metrics_count = config["metrics"]["settings"].get("total_metrics_used", 0)
        validation["metrics_count"] = metrics_count
        
        if metrics_count > 10:
            validation["valid"] = False
            validation["errors"].append(f"Metrics count ({metrics_count}) exceeds CloudWatch limit (10)")
    
    return validation


def get_category_config(config: Dict[str, Any], category: ConfigCategory) -> Dict[str, Any]:
    """Get configuration for a specific category."""
    category_data = config.get(category.value, {})
    return category_data.get("settings", {})


def merge_custom_config(base_config: Dict[str, Any], custom_config: Dict[str, Any]) -> Dict[str, Any]:
    """Merge custom configuration with base preset configuration."""
    merged = base_config.copy()
    
    for category, settings in custom_config.items():
        if category in merged:
            if "settings" in merged[category] and isinstance(settings, dict):
                merged[category]["settings"].update(settings)
            else:
                merged[category] = {"preset": "custom", "settings": settings}
    
    return merged
