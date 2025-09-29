"""
config_core.py - Core Configuration Implementation for SUGA
Version: 2025.09.29.03
Daily Revision: 01

REVOLUTIONARY ARCHITECTURE - Optimized for Single Universal Gateway
FREE TIER COMPLIANCE: 100% - Configuration management
"""

import os
from typing import Any, Dict, Optional, List

_CONFIG_STORE: Dict[str, Any] = {}
_CONFIG_DEFAULTS: Dict[str, Any] = {
    "log_level": "INFO",
    "cache_ttl": 300,
    "max_retries": 3,
    "timeout": 30,
    "enable_metrics": True,
    "enable_caching": True,
    "max_memory_mb": 128
}

def get_config(key: str, default: Any = None) -> Any:
    """Get configuration value."""
    if key in _CONFIG_STORE:
        return _CONFIG_STORE[key]
    
    env_value = os.environ.get(key.upper())
    if env_value is not None:
        return env_value
    
    if key in _CONFIG_DEFAULTS:
        return _CONFIG_DEFAULTS[key]
    
    return default

def set_config(key: str, value: Any) -> bool:
    """Set configuration value."""
    _CONFIG_STORE[key] = value
    return True

def delete_config(key: str) -> bool:
    """Delete configuration value."""
    if key in _CONFIG_STORE:
        del _CONFIG_STORE[key]
        return True
    return False

def clear_config() -> int:
    """Clear all configuration."""
    count = len(_CONFIG_STORE)
    _CONFIG_STORE.clear()
    return count

def get_all_config() -> Dict[str, Any]:
    """Get all configuration."""
    config = _CONFIG_DEFAULTS.copy()
    config.update(_CONFIG_STORE)
    
    for key in _CONFIG_DEFAULTS.keys():
        env_key = key.upper()
        env_value = os.environ.get(env_key)
        if env_value is not None:
            config[key] = env_value
    
    return config

def set_defaults(defaults: Dict[str, Any]) -> None:
    """Set default configuration values."""
    _CONFIG_DEFAULTS.update(defaults)

def get_defaults() -> Dict[str, Any]:
    """Get default configuration values."""
    return _CONFIG_DEFAULTS.copy()

def reset_to_defaults() -> None:
    """Reset configuration to defaults."""
    _CONFIG_STORE.clear()

def config_exists(key: str) -> bool:
    """Check if configuration key exists."""
    return (
        key in _CONFIG_STORE or
        key.upper() in os.environ or
        key in _CONFIG_DEFAULTS
    )

def get_config_keys() -> List[str]:
    """Get all configuration keys."""
    keys = set()
    keys.update(_CONFIG_DEFAULTS.keys())
    keys.update(_CONFIG_STORE.keys())
    keys.update(k.lower() for k in os.environ.keys())
    return sorted(list(keys))

def get_config_source(key: str) -> str:
    """Get source of configuration value."""
    if key in _CONFIG_STORE:
        return "runtime"
    elif key.upper() in os.environ:
        return "environment"
    elif key in _CONFIG_DEFAULTS:
        return "default"
    else:
        return "none"

def validate_config(required_keys: List[str]) -> Dict[str, Any]:
    """Validate required configuration keys exist."""
    missing = []
    for key in required_keys:
        if not config_exists(key):
            missing.append(key)
    
    return {
        "valid": len(missing) == 0,
        "missing_keys": missing
    }

def export_config(format: str = "dict") -> Any:
    """Export configuration in specified format."""
    config = get_all_config()
    
    if format.lower() == "dict":
        return config
    elif format.lower() == "json":
        import json
        return json.dumps(config, indent=2)
    elif format.lower() == "env":
        return "\n".join(f"{k.upper()}={v}" for k, v in config.items())
    else:
        raise ValueError(f"Unsupported format: {format}")

def import_config(data: Dict[str, Any], overwrite: bool = False) -> int:
    """Import configuration from dictionary."""
    count = 0
    for key, value in data.items():
        if overwrite or key not in _CONFIG_STORE:
            set_config(key, value)
            count += 1
    return count

def get_config_stats() -> Dict[str, Any]:
    """Get configuration statistics."""
    return {
        "total_keys": len(get_config_keys()),
        "runtime_keys": len(_CONFIG_STORE),
        "default_keys": len(_CONFIG_DEFAULTS),
        "environment_keys": sum(1 for k in _CONFIG_DEFAULTS.keys() if k.upper() in os.environ)
    }
