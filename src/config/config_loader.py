"""
config/config_loader.py
Version: 2025-12-09_1
Purpose: Configuration loading from various sources
License: Apache 2.0
"""

import os
import json
from typing import Dict, Any
from config.config_core import get_config_manager


def load_from_environment() -> Dict[str, Any]:
    """Load configuration from environment variables."""
    import gateway
    
    try:
        with gateway.debug_timing("CONFIG", "CONFIG", "load_environment"):
            config = {}
            
            # Load common config patterns
            env_prefixes = ['LEE_', 'HA_', 'LAMBDA_', 'AWS_', 'CONFIG_']
            
            for key, value in os.environ.items():
                # Check if key matches known patterns
                for prefix in env_prefixes:
                    if key.startswith(prefix):
                        config[key] = value
                        break
            
            gateway.debug_log("CONFIG", "CONFIG", "Environment loaded",
                            key_count=len(config))
            
            return config
            
    except Exception as e:
        gateway.log_error(f"Load from environment failed: {e}")
        return {}


def load_from_file(filepath: str) -> Dict[str, Any]:
    """Load configuration from file."""
    import gateway
    
    try:
        with gateway.debug_timing("CONFIG", "CONFIG", "load_file"):
            gateway.debug_log("CONFIG", "CONFIG", "Loading file", filepath=filepath)
            
            with open(filepath, 'r') as f:
                if filepath.endswith('.json'):
                    config = json.load(f)
                else:
                    # Simple key=value format
                    config = {}
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            if '=' in line:
                                key, value = line.split('=', 1)
                                config[key.strip()] = value.strip()
            
            gateway.debug_log("CONFIG", "CONFIG", "File loaded",
                            filepath=filepath, key_count=len(config))
            
            return config
            
    except Exception as e:
        gateway.log_error(f"Load from file failed ({filepath}): {e}")
        return {}


def reload_config(validate: bool = True) -> Dict[str, Any]:
    """Reload configuration from environment."""
    import gateway
    
    manager = get_config_manager()
    
    try:
        with gateway.debug_timing("CONFIG", "CONFIG", "reload"):
            gateway.debug_log("CONFIG", "CONFIG", "Reloading config", validate=validate)
            
            # Clear existing config
            manager._config.clear()
            
            # Reload from environment
            env_config = load_from_environment()
            manager._config.update(env_config)
            
            # Validate if requested
            if validate:
                from config.config_validator import validate_all_sections
                validation = validate_all_sections()
                
                if not validation.get('valid', True):
                    gateway.log_warning("Config validation failed after reload")
                    return {
                        'success': False,
                        'error': 'Validation failed',
                        'validation': validation
                    }
            
            return {
                'success': True,
                'parameter_count': len(manager._config)
            }
            
    except Exception as e:
        gateway.log_error(f"Config reload failed: {e}")
        return {'success': False, 'error': str(e)}


def merge_configs(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """Merge two configuration dictionaries."""
    merged = base.copy()
    merged.update(override)
    return merged


__all__ = [
    'load_from_environment',
    'load_from_file',
    'reload_config',
    'merge_configs'
]
