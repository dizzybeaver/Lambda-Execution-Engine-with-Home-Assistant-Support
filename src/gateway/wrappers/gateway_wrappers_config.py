"""
gateway/wrappers/gateway_wrappers_config.py
Version: 2025-12-09_1
Purpose: Config interface wrappers
License: Apache 2.0
"""

from typing import Any, Dict
from gateway.gateway_core import GatewayInterface, execute_operation


def config_initialize(**kwargs) -> Dict[str, Any]:
    """Initialize configuration system."""
    return execute_operation(GatewayInterface.CONFIG, 'initialize', **kwargs)


def config_get_parameter(key: str, default: Any = None) -> Any:
    """Get configuration parameter with SSM-first priority."""
    return execute_operation(GatewayInterface.CONFIG, 'get_parameter', 
                           key=key, default=default)


def config_set_parameter(key: str, value: Any) -> bool:
    """Set configuration parameter."""
    return execute_operation(GatewayInterface.CONFIG, 'set_parameter', 
                           key=key, value=value)


def config_get_category(category: str) -> Dict[str, Any]:
    """Get configuration category."""
    return execute_operation(GatewayInterface.CONFIG, 'get_category', 
                           category=category)


def config_get_state() -> Dict[str, Any]:
    """Get configuration state."""
    return execute_operation(GatewayInterface.CONFIG, 'get_state')


def config_reload(validate: bool = True) -> Dict[str, Any]:
    """Reload configuration."""
    return execute_operation(GatewayInterface.CONFIG, 'reload', 
                           validate=validate)


def config_switch_preset(preset_name: str) -> Dict[str, Any]:
    """Switch configuration preset."""
    return execute_operation(GatewayInterface.CONFIG, 'switch_preset', 
                           preset_name=preset_name)


def config_load_environment() -> Dict[str, Any]:
    """Load configuration from environment variables."""
    return execute_operation(GatewayInterface.CONFIG, 'load_environment')


def config_load_file(filepath: str) -> Dict[str, Any]:
    """Load configuration from file."""
    return execute_operation(GatewayInterface.CONFIG, 'load_file', 
                           filepath=filepath)


def config_validate_all() -> Dict[str, Any]:
    """Validate all configuration."""
    return execute_operation(GatewayInterface.CONFIG, 'validate_all')


def config_reset(**kwargs) -> bool:
    """Reset configuration state."""
    return execute_operation(GatewayInterface.CONFIG, 'reset', **kwargs)


# Legacy aliases for backward compatibility
def initialize_config(**kwargs) -> Dict[str, Any]:
    """Initialize configuration system (legacy)."""
    return config_initialize(**kwargs)


def get_config(key: str, default: Any = None) -> Any:
    """Get configuration value (legacy)."""
    return config_get_parameter(key, default)


def set_config(key: str, value: Any) -> None:
    """Set configuration value (legacy)."""
    config_set_parameter(key, value)


def get_config_category(category: str) -> Dict[str, Any]:
    """Get configuration category (legacy)."""
    return config_get_category(category)


def get_config_state() -> Dict[str, Any]:
    """Get configuration state (legacy)."""
    return config_get_state()


def reload_config() -> None:
    """Reload configuration (legacy)."""
    config_reload()


def switch_config_preset(preset: str) -> None:
    """Switch configuration preset (legacy)."""
    config_switch_preset(preset)


def load_config_from_environment() -> None:
    """Load configuration from environment (legacy)."""
    config_load_environment()


def load_config_from_file(file_path: str) -> None:
    """Load configuration from file (legacy)."""
    config_load_file(file_path)


def validate_all_config() -> Dict[str, Any]:
    """Validate all configuration (legacy)."""
    return config_validate_all()


__all__ = [
    # Standardized wrappers
    'config_initialize',
    'config_get_parameter',
    'config_set_parameter',
    'config_get_category',
    'config_get_state',
    'config_reload',
    'config_switch_preset',
    'config_load_environment',
    'config_load_file',
    'config_validate_all',
    'config_reset',
    
    # Legacy wrappers
    'initialize_config',
    'get_config',
    'set_config',
    'get_config_category',
    'get_config_state',
    'reload_config',
    'switch_config_preset',
    'load_config_from_environment',
    'load_config_from_file',
    'validate_all_config'
]
