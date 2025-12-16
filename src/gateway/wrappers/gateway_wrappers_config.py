"""
gateway/wrappers/gateway_wrappers_config.py
Version: 2025-12-13_1
Purpose: Config interface wrappers
License: Apache 2.0

CHANGES (2025-12-13_1):
- FIXED: Import path from gateway_core (not gateway.gateway_core)
"""

from typing import Any, Dict
from gateway_core import GatewayInterface, execute_operation
# NEW: Add debug system for exact failure point identification
from debug import debug_log, debug_timing, generate_correlation_id


def config_initialize(correlation_id: str = None, **kwargs) -> Dict[str, Any]:
    """Initialize configuration system."""
    # NEW: Add debug tracing for exact failure point identification
    if correlation_id is None:
        correlation_id = generate_correlation_id()

    debug_log(correlation_id, "CONFIG", "config_initialize called")

    with debug_timing(correlation_id, "CONFIG", "config_initialize"):
        try:
            result = execute_operation(GatewayInterface.CONFIG, 'initialize', **kwargs)
            debug_log(correlation_id, "CONFIG", "config_initialize completed", success=True)
            return result
        except Exception as e:
            debug_log(correlation_id, "CONFIG", "config_initialize failed", error_type=type(e).__name__, error=str(e))
            raise


def config_get_parameter(key: str, default: Any = None, correlation_id: str = None) -> Any:
    """Get configuration parameter with SSM-first priority."""
    # NEW: Add debug tracing for exact failure point identification
    if correlation_id is None:
        correlation_id = generate_correlation_id()

    debug_log(correlation_id, "CONFIG", "config_get_parameter called", key=key, has_default=default is not None)

    with debug_timing(correlation_id, "CONFIG", "config_get_parameter", key=key):
        try:
            result = execute_operation(GatewayInterface.CONFIG, 'get_parameter',
                                   key=key, default=default)
            debug_log(correlation_id, "CONFIG", "config_get_parameter completed", success=True)
            return result
        except Exception as e:
            debug_log(correlation_id, "CONFIG", "config_get_parameter failed", error_type=type(e).__name__, error=str(e))
            raise


def config_set_parameter(key: str, value: Any, correlation_id: str = None) -> bool:
    """Set configuration parameter."""
    # NEW: Add debug tracing for exact failure point identification
    if correlation_id is None:
        correlation_id = generate_correlation_id()

    debug_log(correlation_id, "CONFIG", "config_set_parameter called", key=key, value_type=type(value).__name__)

    with debug_timing(correlation_id, "CONFIG", "config_set_parameter", key=key):
        try:
            result = execute_operation(GatewayInterface.CONFIG, 'set_parameter',
                                   key=key, value=value)
            debug_log(correlation_id, "CONFIG", "config_set_parameter completed", success=True)
            return result
        except Exception as e:
            debug_log(correlation_id, "CONFIG", "config_set_parameter failed", error_type=type(e).__name__, error=str(e))
            raise


def config_get_category(category: str, correlation_id: str = None) -> Dict[str, Any]:
    """Get configuration category."""
    # NEW: Add debug tracing for exact failure point identification
    if correlation_id is None:
        correlation_id = generate_correlation_id()

    debug_log(correlation_id, "CONFIG", "config_get_category called", category=category)

    with debug_timing(correlation_id, "CONFIG", "config_get_category", category=category):
        try:
            result = execute_operation(GatewayInterface.CONFIG, 'get_category',
                                   category=category)
            debug_log(correlation_id, "CONFIG", "config_get_category completed", success=True)
            return result
        except Exception as e:
            debug_log(correlation_id, "CONFIG", "config_get_category failed", error_type=type(e).__name__, error=str(e))
            raise


def config_get_state(correlation_id: str = None) -> Dict[str, Any]:
    """Get configuration state."""
    # NEW: Add debug tracing for exact failure point identification
    if correlation_id is None:
        correlation_id = generate_correlation_id()

    debug_log(correlation_id, "CONFIG", "config_get_state called")

    with debug_timing(correlation_id, "CONFIG", "config_get_state"):
        try:
            result = execute_operation(GatewayInterface.CONFIG, 'get_state')
            debug_log(correlation_id, "CONFIG", "config_get_state completed", success=True)
            return result
        except Exception as e:
            debug_log(correlation_id, "CONFIG", "config_get_state failed", error_type=type(e).__name__, error=str(e))
            raise


def config_reload(validate: bool = True, correlation_id: str = None) -> Dict[str, Any]:
    """Reload configuration."""
    # NEW: Add debug tracing for exact failure point identification
    if correlation_id is None:
        correlation_id = generate_correlation_id()

    debug_log(correlation_id, "CONFIG", "config_reload called", validate=validate)

    with debug_timing(correlation_id, "CONFIG", "config_reload", validate=validate):
        try:
            result = execute_operation(GatewayInterface.CONFIG, 'reload',
                                   validate=validate)
            debug_log(correlation_id, "CONFIG", "config_reload completed", success=True)
            return result
        except Exception as e:
            debug_log(correlation_id, "CONFIG", "config_reload failed", error_type=type(e).__name__, error=str(e))
            raise


def config_switch_preset(preset_name: str, correlation_id: str = None) -> Dict[str, Any]:
    """Switch configuration preset."""
    # NEW: Add debug tracing for exact failure point identification
    if correlation_id is None:
        correlation_id = generate_correlation_id()

    debug_log(correlation_id, "CONFIG", "config_switch_preset called", preset_name=preset_name)

    with debug_timing(correlation_id, "CONFIG", "config_switch_preset", preset_name=preset_name):
        try:
            result = execute_operation(GatewayInterface.CONFIG, 'switch_preset',
                                   preset_name=preset_name)
            debug_log(correlation_id, "CONFIG", "config_switch_preset completed", success=True)
            return result
        except Exception as e:
            debug_log(correlation_id, "CONFIG", "config_switch_preset failed", error_type=type(e).__name__, error=str(e))
            raise


def config_load_environment(correlation_id: str = None) -> Dict[str, Any]:
    """Load configuration from environment variables."""
    # NEW: Add debug tracing for exact failure point identification
    if correlation_id is None:
        correlation_id = generate_correlation_id()

    debug_log(correlation_id, "CONFIG", "config_load_environment called")

    with debug_timing(correlation_id, "CONFIG", "config_load_environment"):
        try:
            result = execute_operation(GatewayInterface.CONFIG, 'load_environment')
            debug_log(correlation_id, "CONFIG", "config_load_environment completed", success=True)
            return result
        except Exception as e:
            debug_log(correlation_id, "CONFIG", "config_load_environment failed", error_type=type(e).__name__, error=str(e))
            raise


def config_load_file(filepath: str, correlation_id: str = None) -> Dict[str, Any]:
    """Load configuration from file."""
    # NEW: Add debug tracing for exact failure point identification
    if correlation_id is None:
        correlation_id = generate_correlation_id()

    debug_log(correlation_id, "CONFIG", "config_load_file called", filepath=filepath)

    with debug_timing(correlation_id, "CONFIG", "config_load_file", filepath=filepath):
        try:
            result = execute_operation(GatewayInterface.CONFIG, 'load_file',
                                   filepath=filepath)
            debug_log(correlation_id, "CONFIG", "config_load_file completed", success=True)
            return result
        except Exception as e:
            debug_log(correlation_id, "CONFIG", "config_load_file failed", error_type=type(e).__name__, error=str(e))
            raise


def config_validate_all(correlation_id: str = None) -> Dict[str, Any]:
    """Validate all configuration."""
    # NEW: Add debug tracing for exact failure point identification
    if correlation_id is None:
        correlation_id = generate_correlation_id()

    debug_log(correlation_id, "CONFIG", "config_validate_all called")

    with debug_timing(correlation_id, "CONFIG", "config_validate_all"):
        try:
            result = execute_operation(GatewayInterface.CONFIG, 'validate_all')
            debug_log(correlation_id, "CONFIG", "config_validate_all completed", success=True)
            return result
        except Exception as e:
            debug_log(correlation_id, "CONFIG", "config_validate_all failed", error_type=type(e).__name__, error=str(e))
            raise


def config_reset(correlation_id: str = None, **kwargs) -> bool:
    """Reset configuration state."""
    # NEW: Add debug tracing for exact failure point identification
    if correlation_id is None:
        correlation_id = generate_correlation_id()

    debug_log(correlation_id, "CONFIG", "config_reset called", kwargs_keys=list(kwargs.keys()))

    with debug_timing(correlation_id, "CONFIG", "config_reset"):
        try:
            result = execute_operation(GatewayInterface.CONFIG, 'reset', **kwargs)
            debug_log(correlation_id, "CONFIG", "config_reset completed", success=True)
            return result
        except Exception as e:
            debug_log(correlation_id, "CONFIG", "config_reset failed", error_type=type(e).__name__, error=str(e))
            raise


# Legacy aliases for backward compatibility
def initialize_config(correlation_id: str = None, **kwargs) -> Dict[str, Any]:
    """Initialize configuration system (legacy)."""
    return config_initialize(correlation_id=correlation_id, **kwargs)


def get_config(key: str, default: Any = None, correlation_id: str = None) -> Any:
    """Get configuration value (legacy)."""
    return config_get_parameter(key, default, correlation_id)


def set_config(key: str, value: Any, correlation_id: str = None) -> None:
    """Set configuration value (legacy)."""
    config_set_parameter(key, value, correlation_id)


def get_config_category(category: str, correlation_id: str = None) -> Dict[str, Any]:
    """Get configuration category (legacy)."""
    return config_get_category(category, correlation_id)


def get_config_state(correlation_id: str = None) -> Dict[str, Any]:
    """Get configuration state (legacy)."""
    return config_get_state(correlation_id)


def reload_config(correlation_id: str = None) -> None:
    """Reload configuration (legacy)."""
    config_reload(correlation_id=correlation_id)


def switch_config_preset(preset: str, correlation_id: str = None) -> None:
    """Switch configuration preset (legacy)."""
    config_switch_preset(preset, correlation_id)


def load_config_from_environment(correlation_id: str = None) -> None:
    """Load configuration from environment (legacy)."""
    config_load_environment(correlation_id)


def load_config_from_file(file_path: str, correlation_id: str = None) -> None:
    """Load configuration from file (legacy)."""
    config_load_file(file_path, correlation_id)


def validate_all_config(correlation_id: str = None) -> Dict[str, Any]:
    """Validate all configuration (legacy)."""
    return config_validate_all(correlation_id)


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
