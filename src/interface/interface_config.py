"""
interfaces/interface_config.py
Version: 2025-12-09_1
Purpose: Config interface router with dispatch dictionary
License: Apache 2.0
"""

from typing import Any, Callable, Dict

_CONFIG_AVAILABLE = True
_CONFIG_IMPORT_ERROR = None

try:
    from config.config_parameters import (
        initialize_config,
        get_parameter,
        set_parameter,
        get_category_config,
        get_state
    )
    from config.config_loader import (
        load_from_environment,
        load_from_file,
        reload_config
    )
    from config.config_presets import (
        switch_preset
    )
    from config.config_validator import (
        validate_all_sections
    )
    from config.config_core import (
        get_config_manager
    )
except ImportError as e:
    _CONFIG_AVAILABLE = False
    _CONFIG_IMPORT_ERROR = str(e)
    initialize_config = None
    get_parameter = None
    set_parameter = None
    get_category_config = None
    get_state = None
    load_from_environment = None
    load_from_file = None
    reload_config = None
    switch_preset = None
    validate_all_sections = None


def _validate_key_param(kwargs: Dict[str, Any], operation: str) -> None:
    """Validate key parameter exists and is string."""
    if 'key' not in kwargs:
        raise ValueError(f"config.{operation} requires 'key' parameter")
    if not isinstance(kwargs['key'], str):
        raise TypeError(
            f"config.{operation} 'key' must be str, got {type(kwargs['key']).__name__}"
        )


def _validate_set_params(kwargs: Dict[str, Any]) -> None:
    """Validate set operation parameters."""
    _validate_key_param(kwargs, 'set')
    if 'value' not in kwargs:
        raise ValueError("config.set requires 'value' parameter")


def _validate_category_param(kwargs: Dict[str, Any]) -> None:
    """Validate category parameter."""
    if 'category' not in kwargs:
        raise ValueError("config.get_category requires 'category' parameter")
    if not isinstance(kwargs['category'], str):
        raise TypeError(
            f"config.get_category 'category' must be str, got {type(kwargs['category']).__name__}"
        )


def _validate_preset_param(kwargs: Dict[str, Any]) -> None:
    """Validate preset_name parameter."""
    if 'preset_name' not in kwargs:
        raise ValueError("config.switch_preset requires 'preset_name' parameter")
    if not isinstance(kwargs['preset_name'], str):
        raise TypeError(
            f"config.switch_preset 'preset_name' must be str, got {type(kwargs['preset_name']).__name__}"
        )


def _validate_filepath_param(kwargs: Dict[str, Any]) -> None:
    """Validate filepath parameter."""
    if 'filepath' not in kwargs:
        raise ValueError("config.load_file requires 'filepath' parameter")
    if not isinstance(kwargs['filepath'], str):
        raise TypeError(
            f"config.load_file 'filepath' must be str, got {type(kwargs['filepath']).__name__}"
        )


def _build_dispatch_dict() -> Dict[str, Callable]:
    """Build dispatch dictionary for config operations."""
    return {
        'initialize': lambda **kwargs: initialize_config(),
        'get': lambda **kwargs: (
            _validate_key_param(kwargs, 'get'),
            get_parameter(kwargs['key'], kwargs.get('default'))
        )[1],
        'get_parameter': lambda **kwargs: (
            _validate_key_param(kwargs, 'get_parameter'),
            get_parameter(kwargs['key'], kwargs.get('default'))
        )[1],
        'set': lambda **kwargs: (
            _validate_set_params(kwargs),
            set_parameter(kwargs['key'], kwargs['value'])
        )[1],
        'set_parameter': lambda **kwargs: (
            _validate_set_params(kwargs),
            set_parameter(kwargs['key'], kwargs['value'])
        )[1],
        'get_category': lambda **kwargs: (
            _validate_category_param(kwargs),
            get_category_config(kwargs['category'])
        )[1],
        'get_state': lambda **kwargs: get_state(),
        'reload': lambda **kwargs: reload_config(kwargs.get('validate', True)),
        'switch_preset': lambda **kwargs: (
            _validate_preset_param(kwargs),
            switch_preset(kwargs['preset_name'])
        )[1],
        'load_environment': lambda **kwargs: load_from_environment(),
        'load_file': lambda **kwargs: (
            _validate_filepath_param(kwargs),
            load_from_file(kwargs['filepath'])
        )[1],
        'validate_all': lambda **kwargs: validate_all_sections(),
        'reset': lambda **kwargs: get_config_manager().reset()
    }


_OPERATION_DISPATCH = _build_dispatch_dict() if _CONFIG_AVAILABLE else {}


def execute_config_operation(operation: str, **kwargs) -> Any:
    """
    Route config operations to implementations.
    
    Operations:
        - initialize: Initialize configuration system
        - get/get_parameter: Get configuration parameter
        - set/set_parameter: Set configuration parameter
        - get_category: Get category configuration
        - reload: Reload configuration
        - switch_preset: Switch to preset
        - get_state: Get configuration state
        - load_environment: Load from environment
        - load_file: Load from file
        - validate_all: Validate all sections
        - reset: Reset configuration
    """
    if not _CONFIG_AVAILABLE:
        raise RuntimeError(
            f"Config interface unavailable: {_CONFIG_IMPORT_ERROR}"
        )
    
    if operation not in _OPERATION_DISPATCH:
        raise ValueError(
            f"Unknown config operation: '{operation}'. "
            f"Valid operations: {', '.join(_OPERATION_DISPATCH.keys())}"
        )
    
    return _OPERATION_DISPATCH[operation](**kwargs)


__all__ = ['execute_config_operation']
