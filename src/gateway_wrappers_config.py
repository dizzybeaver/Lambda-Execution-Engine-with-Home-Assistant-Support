"""
gateway_wrappers_config.py - CONFIG Interface Wrappers
Version: 2025.10.22.02
Description: Convenience wrappers for CONFIG interface operations

Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any, Dict
from gateway_core import GatewayInterface, execute_operation


# ===== LEGACY CONFIG WRAPPERS =====

def initialize_config(**kwargs) -> Dict[str, Any]:
    """Initialize configuration system."""
    return execute_operation(GatewayInterface.CONFIG, 'initialize', **kwargs)


def get_cache_config() -> Dict[str, Any]:
    """Get cache configuration."""
    return execute_operation(GatewayInterface.CONFIG, 'get_category', category='cache')


def get_metrics_config() -> Dict[str, Any]:
    """Get metrics configuration."""
    return execute_operation(GatewayInterface.CONFIG, 'get_category', category='metrics')


def get_config(key: str, default: Any = None) -> Any:
    """Get configuration value."""
    return execute_operation(GatewayInterface.CONFIG, 'get', key=key, default=default)


def set_config(key: str, value: Any) -> None:
    """Set configuration value."""
    execute_operation(GatewayInterface.CONFIG, 'set', key=key, value=value)


def get_config_category(category: str) -> Dict[str, Any]:
    """Get configuration category."""
    return execute_operation(GatewayInterface.CONFIG, 'get_category', category=category)


def reload_config() -> None:
    """Reload configuration."""
    execute_operation(GatewayInterface.CONFIG, 'reload')


def switch_config_preset(preset: str) -> None:
    """Switch configuration preset."""
    execute_operation(GatewayInterface.CONFIG, 'switch_preset', preset=preset)


def get_config_state() -> Dict[str, Any]:
    """Get configuration state."""
    return execute_operation(GatewayInterface.CONFIG, 'get_state')


def load_config_from_environment() -> None:
    """Load configuration from environment variables."""
    execute_operation(GatewayInterface.CONFIG, 'load_from_environment')


def load_config_from_file(file_path: str) -> None:
    """Load configuration from file."""
    execute_operation(GatewayInterface.CONFIG, 'load_from_file', file_path=file_path)


def validate_all_config() -> Dict[str, Any]:
    """Validate all configuration."""
    return execute_operation(GatewayInterface.CONFIG, 'validate_all')


# ===== STANDARDIZED CONFIG WRAPPERS (2025.10.22.02) =====

def config_initialize(**kwargs) -> Dict[str, Any]:
    """Initialize configuration system."""
    return execute_operation(GatewayInterface.CONFIG, 'initialize', **kwargs)


def config_get_parameter(key: str, default: Any = None) -> Any:
    """
    Get configuration parameter with SSM-first priority.
    
    Priority:
    1. SSM Parameter Store (if USE_PARAMETER_STORE=true)
    2. Environment variable
    3. Default value
    """
    return execute_operation(GatewayInterface.CONFIG, 'get_parameter', key=key, default=default)


def config_set_parameter(key: str, value: Any) -> bool:
    """Set configuration parameter."""
    return execute_operation(GatewayInterface.CONFIG, 'set_parameter', key=key, value=value)


def config_delete_parameter(key: str) -> bool:
    """Delete configuration parameter."""
    return execute_operation(GatewayInterface.CONFIG, 'delete_parameter', key=key)


def config_validate_parameter(key: str, value: Any) -> Dict[str, Any]:
    """Validate a configuration parameter."""
    return execute_operation(GatewayInterface.CONFIG, 'validate_parameter', key=key, value=value)


def config_validate_all(config: Dict[str, Any] = None) -> Dict[str, Any]:
    """Validate entire configuration."""
    return execute_operation(GatewayInterface.CONFIG, 'validate_config', config=config)


def config_get_state() -> Dict[str, Any]:
    """
    Get configuration state including initialization status and rate limiting stats.
    
    Returns dict with:
    - initialized: bool
    - use_parameter_store: bool
    - parameter_prefix: str
    - config_keys: List[str]
    - rate_limited_count: int
    """
    return execute_operation(GatewayInterface.CONFIG, 'get_state')


def config_reset(**kwargs) -> bool:
    """
    Reset configuration state.
    
    Clears all configuration data and resets rate limiter.
    Part of Phase 1 optimization for lifecycle management.
    """
    return execute_operation(GatewayInterface.CONFIG, 'reset', **kwargs)


__all__ = [
    # Legacy wrappers
    'initialize_config',
    'get_cache_config',
    'get_metrics_config',
    'get_config',
    'set_config',
    'get_config_category',
    'reload_config',
    'switch_config_preset',
    'get_config_state',
    'load_config_from_environment',
    'load_config_from_file',
    'validate_all_config',
    
    # Standardized wrappers (2025.10.22.02)
    'config_initialize',
    'config_get_parameter',
    'config_set_parameter',
    'config_delete_parameter',
    'config_validate_parameter',
    'config_validate_all',
    'config_get_state',
    'config_reset',
]
