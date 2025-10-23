"""
interface_config.py - Config Interface Router (SUGA-ISP Architecture)
Version: 2025.10.22.01
Description: Router for Config interface with dispatch dictionary pattern

CHANGES (2025.10.22.01):
- Added 'reset' operation for lifecycle management (Phase 1)

CHANGELOG:
- 2025.10.18.01: FIXED Issue #28 - Added 'get_parameter' and 'set_parameter' aliases
  - Added 'get_parameter' as alias for 'get' (maps to _get_parameter_implementation)
  - Added 'set_parameter' as alias for 'set' (maps to _set_parameter_implementation)
  - Fixes diagnostic test failure in lambda_ha_connection.py
  - Maintains consistency with config_core.py method names and gateway_wrappers.py
  - Required by SSM Parameter Store integration
- 2025.10.17.17: MODERNIZED with dispatch dictionary pattern
  - Converted from elif chain (10 operations) to dispatch dictionary
  - O(1) operation lookup vs O(n) elif chain
  - Reduced code from ~190 lines to ~170 lines
  - Easier to maintain and extend (add operation = 1 line)
  - Follows pattern from interface_utility.py v2025.10.17.16
  - All validation logic preserved in helper functions
- 2025.10.17.14: FIXED Issue #20 - Added import error protection
- 2025.10.17.05: Added parameter validation for all operations

Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any, Callable, Dict

# ===== IMPORT PROTECTION =====

try:
    from config_core import (
        _initialize_implementation,
        _get_parameter_implementation,
        _set_parameter_implementation,
        _get_category_implementation,
        _reload_implementation,
        _switch_preset_implementation,
        _get_state_implementation,
        _load_environment_implementation,
        _load_file_implementation,
        _validate_all_implementation,
        _reset_config_implementation
    )
    _CONFIG_AVAILABLE = True
    _CONFIG_IMPORT_ERROR = None
except ImportError as e:
    _CONFIG_AVAILABLE = False
    _CONFIG_IMPORT_ERROR = str(e)
    _initialize_implementation = None
    _get_parameter_implementation = None
    _set_parameter_implementation = None
    _get_category_implementation = None
    _reload_implementation = None
    _switch_preset_implementation = None
    _get_state_implementation = None
    _load_environment_implementation = None
    _load_file_implementation = None
    _validate_all_implementation = None
    _reset_config_implementation = None


# ===== VALIDATION HELPERS =====

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


# ===== IMPLEMENTATION WRAPPERS =====

def _reset_implementation(**kwargs) -> bool:
    """Reset configuration state implementation."""
    try:
        return _reset_config_implementation(**kwargs)
    except Exception as e:
        # Log error if logging available
        try:
            import gateway
            gateway.log_error(f"Config reset failed: {str(e)}")
        except:
            pass
        return False


# ===== OPERATION DISPATCH =====

def _build_dispatch_dict() -> Dict[str, Callable]:
    """Build dispatch dictionary for config operations. Only called if config available."""
    return {
        'initialize': _initialize_implementation,
        
        'get': lambda **kwargs: (
            _validate_key_param(kwargs, 'get'),
            _get_parameter_implementation(**kwargs)
        )[1],
        
        # Alias: get_parameter → get (Issue #28)
        'get_parameter': lambda **kwargs: (
            _validate_key_param(kwargs, 'get_parameter'),
            _get_parameter_implementation(**kwargs)
        )[1],
        
        'set': lambda **kwargs: (
            _validate_set_params(kwargs),
            _set_parameter_implementation(**kwargs)
        )[1],
        
        # Alias: set_parameter → set (Issue #28)
        'set_parameter': lambda **kwargs: (
            _validate_set_params(kwargs),
            _set_parameter_implementation(**kwargs)
        )[1],
        
        'get_category': lambda **kwargs: (
            _validate_category_param(kwargs),
            _get_category_implementation(**kwargs)
        )[1],
        
        'reload': _reload_implementation,
        
        'switch_preset': lambda **kwargs: (
            _validate_preset_param(kwargs),
            _switch_preset_implementation(**kwargs)
        )[1],
        
        'get_state': _get_state_implementation,
        'load_environment': _load_environment_implementation,
        
        'load_file': lambda **kwargs: (
            _validate_filepath_param(kwargs),
            _load_file_implementation(**kwargs)
        )[1],
        
        'validate_all': _validate_all_implementation,
        
        # PHASE 1 ADDITION: Reset operation for lifecycle management
        'reset': _reset_implementation,
    }

_OPERATION_DISPATCH = _build_dispatch_dict() if _CONFIG_AVAILABLE else {}


# ===== MAIN ROUTER FUNCTION =====

def execute_config_operation(operation: str, **kwargs) -> Any:
    """
    Route config operation requests using dispatch dictionary pattern.
    
    Operations:
    - initialize: Initialize configuration system
    - get/get_parameter: Get configuration parameter (aliases)
    - set/set_parameter: Set configuration parameter (aliases)
    - get_category: Get category configuration
    - reload: Reload configuration from environment/Parameter Store
    - switch_preset: Switch to predefined configuration preset
    - get_state: Get current configuration state
    - load_environment: Load configuration from environment variables
    - load_file: Load configuration from file
    - validate_all: Validate all configuration sections
    - reset: Reset configuration state (PHASE 1 ADDITION)
    
    Args:
        operation: Config operation to execute
        **kwargs: Operation-specific parameters
        
    Returns:
        Operation result
        
    Raises:
        RuntimeError: If Config interface unavailable
        ValueError: If operation is unknown or required parameters missing
    """
    # Check Config availability
    if not _CONFIG_AVAILABLE:
        raise RuntimeError(
            f"Config interface unavailable: {_CONFIG_IMPORT_ERROR}. "
            "This may indicate missing config_core module or circular import."
        )
    
    # Validate operation exists
    if operation not in _OPERATION_DISPATCH:
        raise ValueError(
            f"Unknown config operation: '{operation}'. "
            f"Valid operations: {', '.join(_OPERATION_DISPATCH.keys())}"
        )
    
    # Dispatch using dictionary lookup (O(1))
    return _OPERATION_DISPATCH[operation](**kwargs)


__all__ = ['execute_config_operation']

# EOF
