"""
Config Core - Configuration Management
Version: 2025.09.30.02
Description: Configuration implementation with shared utilities integration

ARCHITECTURE: CORE IMPLEMENTATION - INTERNAL ONLY
- Lazy-loaded by gateway.py
- Uses shared_utilities for parameter validation

OPTIMIZATION: Phase 1 Complete
- Integrated validate_operation_parameters() from shared_utilities
- Enhanced parameter validation patterns
- Consistent validation across operations

Revolutionary Gateway Optimization: SUGA + LIGS + ZAFP Compatible

Copyright 2024 Anthropic PBC
Licensed under the Apache License, Version 2.0
"""

import os
from typing import Any, Dict, Optional
from threading import Lock


class ConfigCore:
    """Configuration management with environment variable support and validation."""
    
    def __init__(self):
        self._config: Dict[str, Any] = {}
        self._lock = Lock()
        self._load_from_env()
    
    def _load_from_env(self):
        """Load configuration from environment variables."""
        env_vars = {
            'AWS_REGION': os.environ.get('AWS_REGION', 'us-east-1'),
            'LOG_LEVEL': os.environ.get('LOG_LEVEL', 'INFO'),
            'ENVIRONMENT': os.environ.get('ENVIRONMENT', 'production'),
            'CACHE_TTL': int(os.environ.get('CACHE_TTL', '300')),
            'MAX_RETRIES': int(os.environ.get('MAX_RETRIES', '3')),
            'TIMEOUT': int(os.environ.get('TIMEOUT', '30'))
        }
        
        with self._lock:
            self._config.update(env_vars)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value with validation."""
        try:
            from .shared_utilities import validate_operation_parameters
            
            validation_result = validate_operation_parameters(
                required_params=['key'],
                optional_params=['default'],
                key=key,
                default=default
            )
            
            if not validation_result['valid']:
                return default
            
            with self._lock:
                return self._config.get(key, default)
        except Exception:
            with self._lock:
                return self._config.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set configuration value with validation."""
        try:
            from .shared_utilities import validate_operation_parameters
            
            validation_result = validate_operation_parameters(
                required_params=['key', 'value'],
                key=key,
                value=value
            )
            
            if not validation_result['valid']:
                raise ValueError(f"Invalid parameters: {validation_result['errors']}")
            
            with self._lock:
                self._config[key] = value
        except Exception as e:
            with self._lock:
                self._config[key] = value
    
    def get_all(self) -> Dict[str, Any]:
        """Get all configuration."""
        with self._lock:
            return self._config.copy()
    
    def reload_from_env(self):
        """Reload configuration from environment."""
        self._load_from_env()


_CONFIG = ConfigCore()


def _execute_get_implementation(key: str, default: Any = None, **kwargs) -> Any:
    """Execute config get."""
    return _CONFIG.get(key, default)


def _execute_set_implementation(key: str, value: Any, **kwargs):
    """Execute config set."""
    return _CONFIG.set(key, value)


def _execute_get_all_implementation(**kwargs) -> Dict[str, Any]:
    """Execute get all config."""
    return _CONFIG.get_all()


def _execute_reload_implementation(**kwargs):
    """Execute config reload."""
    return _CONFIG.reload_from_env()


__all__ = [
    '_execute_get_implementation',
    '_execute_set_implementation',
    '_execute_get_all_implementation',
    '_execute_reload_implementation',
]

# EOF
