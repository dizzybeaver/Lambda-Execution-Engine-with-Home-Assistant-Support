"""
config.py  
Version: 2025.10.12.01
Description: Pure SUGA interface for configuration - all functions delegate to gateway
Consolidates: config.py + config_helpers.py (legacy functions)

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

from typing import Dict, Any, Optional


# ===== CORE CONFIGURATION OPERATIONS =====

def config_initialize() -> Dict[str, Any]:
    """Initialize configuration system."""
    from gateway import execute_operation, GatewayInterface
    return execute_operation(GatewayInterface.CONFIG, 'initialize')


def config_get_parameter(key: str, default: Any = None) -> Any:
    """Get configuration parameter."""
    from gateway import execute_operation, GatewayInterface
    return execute_operation(GatewayInterface.CONFIG, 'get_parameter', key=key, default=default)


def config_set_parameter(key: str, value: Any) -> bool:
    """Set configuration parameter."""
    from gateway import execute_operation, GatewayInterface
    return execute_operation(GatewayInterface.CONFIG, 'set_parameter', key=key, value=value)


def config_get_category(category: str) -> Dict[str, Any]:
    """Get configuration for specific category."""
    from gateway import execute_operation, GatewayInterface
    return execute_operation(GatewayInterface.CONFIG, 'get_category_config', category=category)


def config_reload(validate: bool = True) -> Dict[str, Any]:
    """Reload configuration from all sources."""
    from gateway import execute_operation, GatewayInterface
    return execute_operation(GatewayInterface.CONFIG, 'reload_config', validate=validate)


def config_switch_preset(preset_name: str) -> Dict[str, Any]:
    """Switch to different configuration preset."""
    from gateway import execute_operation, GatewayInterface
    return execute_operation(GatewayInterface.CONFIG, 'switch_preset', preset_name=preset_name)


def config_get_state() -> Dict[str, Any]:
    """Get current configuration state."""
    from gateway import execute_operation, GatewayInterface
    return execute_operation(GatewayInterface.CONFIG, 'get_state')


# ===== SOURCE-SPECIFIC OPERATIONS =====

def config_load_from_environment() -> Dict[str, Any]:
    """Load configuration from environment variables."""
    from gateway import execute_operation, GatewayInterface
    return execute_operation(GatewayInterface.CONFIG, 'load_from_environment')


def config_load_from_file(filepath: str) -> Dict[str, Any]:
    """Load configuration from file."""
    from gateway import execute_operation, GatewayInterface
    return execute_operation(GatewayInterface.CONFIG, 'load_from_file', filepath=filepath)


def config_load_ha_config() -> Dict[str, Any]:
    """Load Home Assistant configuration."""
    from gateway import execute_operation, GatewayInterface
    return execute_operation(GatewayInterface.CONFIG, 'load_ha_config')


def config_validate_ha_config(ha_config: Dict[str, Any]) -> Dict[str, Any]:
    """Validate Home Assistant configuration."""
    from gateway import execute_operation, GatewayInterface
    return execute_operation(GatewayInterface.CONFIG, 'validate_ha_config', ha_config=ha_config)


def config_validate_all() -> Dict[str, Any]:
    """Validate all configuration sections."""
    from gateway import execute_operation, GatewayInterface
    return execute_operation(GatewayInterface.CONFIG, 'validate_all_sections')


# ===== CATEGORY-SPECIFIC HELPERS =====
# These are convenience wrappers around config_get_category

def config_get_cache() -> Dict[str, Any]:
    """Get cache configuration."""
    return config_get_category('cache')


def config_get_logging() -> Dict[str, Any]:
    """Get logging configuration."""
    return config_get_category('logging')


def config_get_metrics() -> Dict[str, Any]:
    """Get metrics configuration."""
    return config_get_category('metrics')


def config_get_security() -> Dict[str, Any]:
    """Get security configuration."""
    return config_get_category('security')


def config_get_circuit_breaker() -> Dict[str, Any]:
    """Get circuit breaker configuration."""
    return config_get_category('circuit_breaker')


def config_get_singleton() -> Dict[str, Any]:
    """Get singleton configuration."""
    return config_get_category('singleton')


def config_get_http_client() -> Dict[str, Any]:
    """Get HTTP client configuration."""
    return config_get_category('http_client')


def config_get_lambda_opt() -> Dict[str, Any]:
    """Get Lambda optimization configuration."""
    return config_get_category('lambda_opt')


def config_get_cost_protection() -> Dict[str, Any]:
    """Get cost protection configuration."""
    return config_get_category('cost_protection')


def config_get_utility() -> Dict[str, Any]:
    """Get utility configuration."""
    return config_get_category('utility')


def config_get_initialization() -> Dict[str, Any]:
    """Get initialization configuration."""
    return config_get_category('initialization')


# ===== BACKWARD COMPATIBILITY ALIASES =====
# Maintains compatibility with old function names

def get_parameter(key: str, default: Any = None) -> Any:
    """Get configuration parameter (backward compatibility)."""
    return config_get_parameter(key, default)


def set_parameter(key: str, value: Any) -> bool:
    """Set configuration parameter (backward compatibility)."""
    return config_set_parameter(key, value)


def get_category_config(category: str) -> Dict[str, Any]:
    """Get category configuration (backward compatibility)."""
    return config_get_category(category)


def reload_config(validate: bool = True) -> Dict[str, Any]:
    """Reload configuration (backward compatibility)."""
    return config_reload(validate)


def switch_preset(preset_name: str) -> Dict[str, Any]:
    """Switch preset (backward compatibility)."""
    return config_switch_preset(preset_name)


def get_config_state() -> Dict[str, Any]:
    """Get configuration state (backward compatibility)."""
    return config_get_state()


# ===== LEGACY HELPER FUNCTIONS =====
# Absorbed from config_helpers.py - maintains full backward compatibility

def get_cache_config(key: str, default: Any = None) -> Any:
    """Get cache configuration setting (legacy)."""
    cache_config = config_get_cache()
    return cache_config.get(key, default)


def get_logging_config(key: str, default: Any = None) -> Any:
    """Get logging configuration setting (legacy)."""
    logging_config = config_get_logging()
    return logging_config.get(key, default)


def get_metrics_config(key: str, default: Any = None) -> Any:
    """Get metrics configuration setting (legacy)."""
    metrics_config = config_get_metrics()
    return metrics_config.get(key, default)


def get_security_config(key: str, default: Any = None) -> Any:
    """Get security configuration setting (legacy)."""
    security_config = config_get_security()
    return security_config.get(key, default)


def get_circuit_breaker_config(key: str, default: Any = None) -> Any:
    """Get circuit breaker configuration setting (legacy)."""
    cb_config = config_get_circuit_breaker()
    return cb_config.get(key, default)


def get_singleton_config(key: str, default: Any = None) -> Any:
    """Get singleton configuration setting (legacy)."""
    singleton_config = config_get_singleton()
    return singleton_config.get(key, default)


def get_http_client_config(key: str, default: Any = None) -> Any:
    """Get HTTP client configuration setting (legacy)."""
    http_config = config_get_http_client()
    return http_config.get(key, default)


def get_lambda_opt_config(key: str, default: Any = None) -> Any:
    """Get Lambda optimization configuration setting (legacy)."""
    lambda_config = config_get_lambda_opt()
    return lambda_config.get(key, default)


def get_cost_protection_config(key: str, default: Any = None) -> Any:
    """Get cost protection configuration setting (legacy)."""
    cost_config = config_get_cost_protection()
    return cost_config.get(key, default)


def get_utility_config(key: str, default: Any = None) -> Any:
    """Get utility configuration setting (legacy)."""
    utility_config = config_get_utility()
    return utility_config.get(key, default)


def get_initialization_config(key: str, default: Any = None) -> Any:
    """Get initialization configuration setting (legacy)."""
    init_config = config_get_initialization()
    return init_config.get(key, default)


# EOF
