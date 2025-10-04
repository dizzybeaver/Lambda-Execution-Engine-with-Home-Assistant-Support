"""
Configuration Helpers - Utility Functions for Configuration Access
Version: 2025.10.03.01
Description: Helper functions for accessing configuration throughout the system

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

from typing import Any, Dict, List, Optional
from config_manager import (
    get_category_configuration,
    get_configuration_setting,
    get_system_configuration
)


def get_cache_config(key: str, default: Any = None) -> Any:
    """Get cache configuration setting."""
    return get_configuration_setting("cache", key, default)


def get_logging_config(key: str, default: Any = None) -> Any:
    """Get logging configuration setting."""
    return get_configuration_setting("logging", key, default)


def get_metrics_config(key: str, default: Any = None) -> Any:
    """Get metrics configuration setting."""
    return get_configuration_setting("metrics", key, default)


def get_security_config(key: str, default: Any = None) -> Any:
    """Get security configuration setting."""
    return get_configuration_setting("security", key, default)


def get_circuit_breaker_config(key: str, default: Any = None) -> Any:
    """Get circuit breaker configuration setting."""
    return get_configuration_setting("circuit_breaker", key, default)


def get_singleton_config(key: str, default: Any = None) -> Any:
    """Get singleton configuration setting."""
    return get_configuration_setting("singleton", key, default)


def get_http_client_config(key: str, default: Any = None) -> Any:
    """Get HTTP client configuration setting."""
    return get_configuration_setting("http_client", key, default)


def get_lambda_opt_config(key: str, default: Any = None) -> Any:
    """Get Lambda optimization configuration setting."""
    return get_configuration_setting("lambda_opt", key, default)


def get_cost_protection_config(key: str, default: Any = None) -> Any:
    """Get cost protection configuration setting."""
    return get_configuration_setting("cost_protection", key, default)


def get_utility_config(key: str, default: Any = None) -> Any:
    """Get utility configuration setting."""
    return get_configuration_setting("utility", key, default)


def get_initialization_config(key: str, default: Any = None) -> Any:
    """Get initialization configuration setting."""
    return get_configuration_setting("initialization", key, default)


def is_feature_enabled(category: str, feature: str) -> bool:
    """Check if a feature is enabled in configuration."""
    value = get_configuration_setting(category, feature, False)
    
    if isinstance(value, bool):
        return value
    
    if isinstance(value, str):
        return value.lower() in ["true", "yes", "1", "enabled"]
    
    return bool(value)


def get_log_level(interface: str = "default") -> str:
    """Get log level for specific interface."""
    logging_config = get_category_configuration("logging")
    
    if interface == "default":
        return logging_config.get("default_level", "INFO")
    
    interface_levels = logging_config.get("interface_levels", {})
    return interface_levels.get(interface, logging_config.get("default_level", "INFO"))


def get_timeout_config(service: str = "default") -> int:
    """Get timeout configuration for service."""
    http_config = get_category_configuration("http_client")
    
    if service == "default":
        return http_config.get("default_timeout_seconds", 30)
    
    circuit_config = get_category_configuration("circuit_breaker")
    service_config = circuit_config.get(service, {})
    
    if isinstance(service_config, dict):
        return service_config.get("timeout_seconds", http_config.get("default_timeout_seconds", 30))
    
    return http_config.get("default_timeout_seconds", 30)


def get_retry_config() -> Dict[str, Any]:
    """Get retry configuration."""
    http_config = get_category_configuration("http_client")
    
    return {
        "max_retries": http_config.get("max_retries", 3),
        "backoff_base_ms": http_config.get("backoff_base_ms", 100),
        "backoff_multiplier": http_config.get("backoff_multiplier", 2.0),
        "max_backoff_seconds": http_config.get("max_backoff_seconds", 120)
    }


def get_circuit_breaker_settings(service: str) -> Dict[str, Any]:
    """Get circuit breaker settings for specific service."""
    circuit_config = get_category_configuration("circuit_breaker")
    service_config = circuit_config.get(service, {})
    
    if not service_config:
        return {
            "failure_threshold": circuit_config.get("default_failure_threshold", 3),
            "recovery_timeout_seconds": circuit_config.get("default_recovery_timeout", 45),
            "max_test_calls": 2
        }
    
    return service_config


def get_cache_ttl(cache_type: str = "default") -> int:
    """Get cache TTL for specific cache type."""
    cache_config = get_category_configuration("cache")
    return cache_config.get("default_ttl_seconds", 300)


def get_metrics_list() -> List[str]:
    """Get list of enabled metrics."""
    metrics_config = get_category_configuration("metrics")
    
    all_metrics = []
    all_metrics.extend(metrics_config.get("core_metrics", []))
    all_metrics.extend(metrics_config.get("optional_metrics", []))
    all_metrics.extend(metrics_config.get("custom_metrics", []))
    
    return all_metrics


def is_cost_protection_enabled() -> bool:
    """Check if cost protection is enabled."""
    cost_config = get_category_configuration("cost_protection")
    return cost_config.get("enable_real_time_tracking", True)


def get_cost_thresholds() -> Dict[str, float]:
    """Get cost protection thresholds."""
    cost_config = get_category_configuration("cost_protection")
    
    return {
        "warning": cost_config.get("warning_threshold_percent", 75.0),
        "critical": cost_config.get("critical_threshold_percent", 90.0),
        "emergency": cost_config.get("emergency_threshold_percent", 95.0)
    }


def get_memory_thresholds() -> Dict[str, int]:
    """Get memory pressure thresholds."""
    cache_config = get_category_configuration("cache")
    
    return {
        "warning": cache_config.get("warning_threshold_percent", 75),
        "critical": cache_config.get("critical_threshold_percent", 85),
        "emergency": cache_config.get("emergency_cleanup_threshold", 95)
    }


def should_enable_lazy_loading() -> bool:
    """Check if lazy loading should be enabled."""
    lambda_config = get_category_configuration("lambda_opt")
    return lambda_config.get("enable_lazy_loading", True)


def should_enable_fast_path() -> bool:
    """Check if fast path optimization should be enabled."""
    lambda_config = get_category_configuration("lambda_opt")
    return lambda_config.get("enable_fast_path", True)


def get_fast_path_threshold() -> int:
    """Get threshold for fast path activation."""
    lambda_config = get_category_configuration("lambda_opt")
    return lambda_config.get("fast_path_threshold", 10)


def get_aws_region() -> str:
    """Get AWS region from system config."""
    system_config = get_system_configuration()
    return system_config.get("system", {}).get("aws_region", "us-east-1")


def get_parameter_prefix() -> str:
    """Get parameter store prefix from system config."""
    system_config = get_system_configuration()
    return system_config.get("system", {}).get("parameter_prefix", "/lambda-execution-engine")


def get_security_validation_level() -> str:
    """Get security validation level."""
    security_config = get_category_configuration("security")
    return security_config.get("validation_level", "standard")


def should_log_security_events() -> bool:
    """Check if security events should be logged."""
    security_config = get_category_configuration("security")
    return security_config.get("security_events_logged", True)


def get_connection_pool_size() -> int:
    """Get HTTP connection pool size."""
    http_config = get_category_configuration("http_client")
    return http_config.get("pool_maxsize", 10)


def should_verify_ssl() -> bool:
    """Check if SSL verification is enabled."""
    http_config = get_category_configuration("http_client")
    return http_config.get("ssl_verify", True)


def get_batch_size(operation_type: str = "default") -> int:
    """Get batch size for operations."""
    if operation_type == "logging":
        logging_config = get_category_configuration("logging")
        return logging_config.get("batch_size", 10)
    
    http_config = get_category_configuration("http_client")
    return http_config.get("pool_maxsize", 10)


def should_enable_compression() -> bool:
    """Check if cache compression is enabled."""
    cache_config = get_category_configuration("cache")
    return cache_config.get("compression_enabled", True)


def get_serialization_method() -> str:
    """Get cache serialization method."""
    cache_config = get_category_configuration("cache")
    return cache_config.get("serialization_method", "json")


def get_health_check_services() -> List[str]:
    """Get list of services to health check on startup."""
    init_config = get_category_configuration("initialization")
    return init_config.get("health_check_services", ["cache", "logging"])


def should_preload_modules() -> List[str]:
    """Get list of modules to preload on startup."""
    init_config = get_category_configuration("initialization")
    return init_config.get("preload_modules", [])


def get_json_validation_limits() -> Dict[str, int]:
    """Get JSON validation limits."""
    utility_config = get_category_configuration("utility")
    
    return {
        "max_depth": utility_config.get("json_max_depth", 20),
        "max_size_kb": utility_config.get("json_max_size_kb", 100)
    }


def should_enable_correlation_id() -> bool:
    """Check if correlation ID generation is enabled."""
    utility_config = get_category_configuration("utility")
    return utility_config.get("enable_correlation_id", True)


def get_error_retry_strategy() -> str:
    """Get error retry strategy."""
    utility_config = get_category_configuration("utility")
    return utility_config.get("error_retry_strategy", "backoff")
