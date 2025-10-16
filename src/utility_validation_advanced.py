"""
utility_validation_advanced.py - Advanced Validation (Internal)
Version: 2025.10.16.04
Description: Decorators and factory validators for complex validation scenarios

SUGA-ISP: Internal module - only accessed via interface_utility.py

Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Callable
import functools

from utility_validation_core import (
    ValidationError,
    TypeValidationError,
    validate_required_impl,
    validate_type_impl,
    validate_string_length_impl,
    validate_range_impl
)


# ===== FACTORY VALIDATORS =====

def create_cache_key_validator(min_length: int = 1, max_length: int = 255) -> Callable:
    """Create validator for cache keys."""
    def validator(key: str) -> None:
        validate_required_impl(key, 'key')
        validate_type_impl(key, str, 'key')
        validate_string_length_impl(key, min_length, max_length, 'key')
    return validator


def create_ttl_validator(min_ttl: int = 0, max_ttl: int = 86400) -> Callable:
    """Create validator for TTL values."""
    def validator(ttl: int) -> None:
        if ttl is not None:
            validate_type_impl(ttl, int, 'ttl')
            validate_range_impl(ttl, min_ttl, max_ttl, 'ttl')
    return validator


def create_metric_validator() -> Callable:
    """Create validator for metric recording."""
    def validator(name: str, value: float) -> None:
        validate_required_impl(name, 'name')
        validate_type_impl(name, str, 'name')
        validate_string_length_impl(name, 1, 255, 'name')
        validate_required_impl(value, 'value')
        validate_type_impl(value, (int, float), 'value')
    return validator


# ===== DECORATORS =====

def validate_params(**validators):
    """
    Decorator to validate function parameters.
    
    Usage:
        @validate_params(
            name=lambda x: validate_required(x, 'name'),
            age=lambda x: validate_range(x, 0, 150, 'age')
        )
        def create_user(name, age):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            import inspect
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            
            for param_name, validator_func in validators.items():
                if param_name in bound_args.arguments:
                    value = bound_args.arguments[param_name]
                    try:
                        validator_func(value)
                    except ValidationError:
                        raise
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


def validate_return_type(expected_type: type):
    """
    Decorator to validate function return type.
    
    Usage:
        @validate_return_type(dict)
        def get_config():
            return {"key": "value"}
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            if result is not None and not isinstance(result, expected_type):
                raise TypeValidationError(
                    'return_value', 
                    f"Expected {expected_type.__name__}, got {type(result).__name__}", 
                    result
                )
            return result
        return wrapper
    return decorator


# ===== MODULE EXPORTS =====

__all__ = [
    'create_cache_key_validator',
    'create_ttl_validator',
    'create_metric_validator',
    'validate_params',
    'validate_return_type',
]

# EOF
