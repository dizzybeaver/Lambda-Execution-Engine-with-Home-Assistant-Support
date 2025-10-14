"""
validation_wrapper.py
Version: 2025.10.13.01
Description: Unified validation patterns for all gateway operations

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

from typing import Any, Dict, List, Optional, Callable
import functools


# ===== VALIDATION EXCEPTIONS =====

class ValidationError(Exception):
    """Base validation error."""
    
    def __init__(self, field: str, message: str, value: Any = None):
        self.field = field
        self.message = message
        self.value = value
        super().__init__(f"Validation failed for {field}: {message}")


class RequiredFieldError(ValidationError):
    """Required field missing error."""
    pass


class TypeValidationError(ValidationError):
    """Type validation error."""
    pass


class RangeValidationError(ValidationError):
    """Range validation error."""
    pass


# ===== FIELD VALIDATORS =====

def validate_required(value: Any, field_name: str) -> None:
    """
    Validate field is present and not None.
    
    Args:
        value: Value to validate
        field_name: Name of field for error messages
    
    Raises:
        RequiredFieldError: If value is None
    """
    if value is None:
        raise RequiredFieldError(field_name, "Required field is missing or null")


def validate_type(value: Any, expected_type: type, field_name: str) -> None:
    """
    Validate value is of expected type.
    
    Args:
        value: Value to validate
        expected_type: Expected Python type
        field_name: Name of field for error messages
    
    Raises:
        TypeValidationError: If type doesn't match
    """
    if not isinstance(value, expected_type):
        raise TypeValidationError(
            field_name,
            f"Expected {expected_type.__name__}, got {type(value).__name__}",
            value
        )


def validate_range(value: float, min_val: Optional[float] = None, 
                  max_val: Optional[float] = None, field_name: str = "value") -> None:
    """
    Validate value is within range.
    
    Args:
        value: Numeric value to validate
        min_val: Minimum allowed value (inclusive)
        max_val: Maximum allowed value (inclusive)
        field_name: Name of field for error messages
    
    Raises:
        RangeValidationError: If value out of range
    """
    if min_val is not None and value < min_val:
        raise RangeValidationError(
            field_name,
            f"Value {value} below minimum {min_val}",
            value
        )
    
    if max_val is not None and value > max_val:
        raise RangeValidationError(
            field_name,
            f"Value {value} above maximum {max_val}",
            value
        )


def validate_string_length(value: str, min_length: Optional[int] = None,
                          max_length: Optional[int] = None, field_name: str = "string") -> None:
    """
    Validate string length.
    
    Args:
        value: String to validate
        min_length: Minimum length (inclusive)
        max_length: Maximum length (inclusive)
        field_name: Name of field for error messages
    
    Raises:
        ValidationError: If length invalid
    """
    length = len(value)
    
    if min_length is not None and length < min_length:
        raise ValidationError(
            field_name,
            f"String length {length} below minimum {min_length}",
            value
        )
    
    if max_length is not None and length > max_length:
        raise ValidationError(
            field_name,
            f"String length {length} above maximum {max_length}",
            value
        )


def validate_one_of(value: Any, allowed_values: List[Any], field_name: str = "value") -> None:
    """
    Validate value is one of allowed values.
    
    Args:
        value: Value to validate
        allowed_values: List of allowed values
        field_name: Name of field for error messages
    
    Raises:
        ValidationError: If value not in allowed list
    """
    if value not in allowed_values:
        raise ValidationError(
            field_name,
            f"Value must be one of {allowed_values}, got {value}",
            value
        )


# ===== DICT VALIDATORS =====

def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> None:
    """
    Validate all required fields present in dict.
    
    Args:
        data: Dictionary to validate
        required_fields: List of required field names
    
    Raises:
        RequiredFieldError: If any required field missing
    """
    for field in required_fields:
        if field not in data or data[field] is None:
            raise RequiredFieldError(field, "Required field is missing or null")


def validate_dict_schema(data: Dict[str, Any], schema: Dict[str, Dict[str, Any]]) -> None:
    """
    Validate dict against schema.
    
    Schema format:
    {
        'field_name': {
            'required': True,
            'type': str,
            'min': 0,
            'max': 100,
            'allowed': ['a', 'b', 'c']
        }
    }
    
    Args:
        data: Dictionary to validate
        schema: Validation schema
    
    Raises:
        ValidationError: If validation fails
    """
    for field_name, rules in schema.items():
        value = data.get(field_name)
        
        # Check required
        if rules.get('required', False):
            validate_required(value, field_name)
            
        # Skip further validation if not required and not present
        if value is None and not rules.get('required', False):
            continue
        
        # Check type
        if 'type' in rules:
            validate_type(value, rules['type'], field_name)
        
        # Check range for numeric types
        if isinstance(value, (int, float)):
            validate_range(
                value,
                rules.get('min'),
                rules.get('max'),
                field_name
            )
        
        # Check string length
        if isinstance(value, str):
            validate_string_length(
                value,
                rules.get('min_length'),
                rules.get('max_length'),
                field_name
            )
        
        # Check allowed values
        if 'allowed' in rules:
            validate_one_of(value, rules['allowed'], field_name)


# ===== DECORATORS =====

def validate_params(**validators):
    """
    Decorator to validate function parameters.
    
    Usage:
        @validate_params(
            key=lambda v: validate_required(v, 'key'),
            ttl=lambda v: validate_range(v, 0, 3600, 'ttl')
        )
        def cache_set(key, value, ttl=300):
            ...
    
    Args:
        **validators: Keyword validators mapping param names to validation functions
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Get function signature
            import inspect
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            
            # Validate each parameter
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
    
    Args:
        expected_type: Expected return type
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


# ===== SAFE VALIDATORS =====

def safe_validate(validator_func: Callable, *args, **kwargs) -> Dict[str, Any]:
    """
    Run validator and return structured result.
    
    Args:
        validator_func: Validation function to run
        *args, **kwargs: Arguments to validator
    
    Returns:
        Dictionary with validation results
    """
    try:
        validator_func(*args, **kwargs)
        return {'valid': True, 'error': None}
    except ValidationError as e:
        return {
            'valid': False,
            'error': str(e),
            'field': e.field,
            'message': e.message
        }
    except Exception as e:
        return {
            'valid': False,
            'error': str(e),
            'field': 'unknown',
            'message': 'Unexpected validation error'
        }


def validate_all(validators: List[Callable]) -> Dict[str, Any]:
    """
    Run multiple validators and aggregate results.
    
    Args:
        validators: List of validation functions
    
    Returns:
        Dictionary with all validation results
    """
    results = []
    all_valid = True
    
    for validator in validators:
        result = safe_validate(validator)
        results.append(result)
        
        if not result['valid']:
            all_valid = False
    
    return {
        'all_valid': all_valid,
        'results': results,
        'error_count': sum(1 for r in results if not r['valid'])
    }


# ===== COMMON VALIDATION PATTERNS =====

def create_cache_key_validator(min_length: int = 1, max_length: int = 255) -> Callable:
    """Create validator for cache keys."""
    def validator(key: str) -> None:
        validate_required(key, 'key')
        validate_type(key, str, 'key')
        validate_string_length(key, min_length, max_length, 'key')
    
    return validator


def create_ttl_validator(min_ttl: int = 0, max_ttl: int = 86400) -> Callable:
    """Create validator for TTL values."""
    def validator(ttl: int) -> None:
        if ttl is not None:
            validate_type(ttl, int, 'ttl')
            validate_range(ttl, min_ttl, max_ttl, 'ttl')
    
    return validator


def create_metric_validator() -> Callable:
    """Create validator for metric recording."""
    def validator(name: str, value: float) -> None:
        validate_required(name, 'name')
        validate_type(name, str, 'name')
        validate_string_length(name, 1, 255, 'name')
        validate_required(value, 'value')
        validate_type(value, (int, float), 'value')
    
    return validator


# ===== EXPORTED FUNCTIONS =====

__all__ = [
    'ValidationError',
    'RequiredFieldError',
    'TypeValidationError',
    'RangeValidationError',
    'validate_required',
    'validate_type',
    'validate_range',
    'validate_string_length',
    'validate_one_of',
    'validate_required_fields',
    'validate_dict_schema',
    'validate_params',
    'validate_return_type',
    'safe_validate',
    'validate_all',
    'create_cache_key_validator',
    'create_ttl_validator',
    'create_metric_validator'
]

# EOF
