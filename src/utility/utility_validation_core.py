"""
utility_validation_core.py - Core Validation (Internal)
Version: 2025.10.16.04
Description: Core validation exceptions and basic validation implementations

Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any, Dict, List, Optional
from enum import Enum


# ===== VALIDATION OPERATIONS ENUM =====

class ValidationOperation(Enum):
    """Validation operations for utility interface."""
    VALIDATE_REQUIRED = "validate_required"
    VALIDATE_TYPE = "validate_type"
    VALIDATE_RANGE = "validate_range"
    VALIDATE_STRING_LENGTH = "validate_string_length"
    VALIDATE_ONE_OF = "validate_one_of"
    VALIDATE_REQUIRED_FIELDS = "validate_required_fields"
    VALIDATE_DICT_SCHEMA = "validate_dict_schema"
    SAFE_VALIDATE = "safe_validate"
    VALIDATE_ALL = "validate_all"
    CREATE_CACHE_KEY_VALIDATOR = "create_cache_key_validator"
    CREATE_TTL_VALIDATOR = "create_ttl_validator"
    CREATE_METRIC_VALIDATOR = "create_metric_validator"


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


# ===== CORE VALIDATION IMPLEMENTATIONS =====

def validate_required_impl(value: Any, field_name: str) -> None:
    """Validate field is present and not None."""
    if value is None:
        raise RequiredFieldError(field_name, "Required field is missing or null")


def validate_type_impl(value: Any, expected_type, field_name: str) -> None:
    """Validate value is of expected type (supports single type or tuple of types)."""
    if not isinstance(value, expected_type):
        if isinstance(expected_type, tuple):
            expected_names = ", ".join(t.__name__ for t in expected_type)
            raise TypeValidationError(
                field_name,
                f"Expected one of ({expected_names}), got {type(value).__name__}",
                value
            )
        else:
            raise TypeValidationError(
                field_name,
                f"Expected {expected_type.__name__}, got {type(value).__name__}",
                value
            )


def validate_range_impl(value: float, min_val: Optional[float], max_val: Optional[float], field_name: str) -> None:
    """Validate value is within range."""
    if min_val is not None and value < min_val:
        raise RangeValidationError(field_name, f"Value {value} below minimum {min_val}", value)
    if max_val is not None and value > max_val:
        raise RangeValidationError(field_name, f"Value {value} above maximum {max_val}", value)


def validate_string_length_impl(value: str, min_length: Optional[int], max_length: Optional[int], field_name: str) -> None:
    """Validate string length."""
    length = len(value)
    if min_length is not None and length < min_length:
        raise ValidationError(field_name, f"String length {length} below minimum {min_length}", value)
    if max_length is not None and length > max_length:
        raise ValidationError(field_name, f"String length {length} above maximum {max_length}", value)


def validate_one_of_impl(value: Any, allowed_values: List[Any], field_name: str) -> None:
    """Validate value is one of allowed values."""
    if value not in allowed_values:
        raise ValidationError(field_name, f"Value must be one of {allowed_values}, got {value}", value)


def validate_required_fields_impl(data: Dict[str, Any], required_fields: List[str]) -> None:
    """Validate all required fields present in dict."""
    for field in required_fields:
        if field not in data or data[field] is None:
            raise RequiredFieldError(field, "Required field is missing or null")


def validate_dict_schema_impl(data: Dict[str, Any], schema: Dict[str, Dict[str, Any]]) -> None:
    """Validate dict against schema."""
    for field_name, rules in schema.items():
        value = data.get(field_name)
        
        if rules.get('required', False):
            validate_required_impl(value, field_name)
        
        if value is None and not rules.get('required', False):
            continue
        
        if 'type' in rules:
            validate_type_impl(value, rules['type'], field_name)
        
        if isinstance(value, (int, float)):
            validate_range_impl(value, rules.get('min'), rules.get('max'), field_name)
        
        if isinstance(value, str):
            validate_string_length_impl(value, rules.get('min_length'), rules.get('max_length'), field_name)
        
        if 'allowed' in rules:
            validate_one_of_impl(value, rules['allowed'], field_name)


def safe_validate_impl(validator_func, *args, **kwargs) -> Dict[str, Any]:
    """Run validator and return structured result."""
    try:
        validator_func(*args, **kwargs)
        return {'valid': True, 'error': None}
    except ValidationError as e:
        return {'valid': False, 'error': str(e), 'field': e.field, 'message': e.message}
    except Exception as e:
        return {'valid': False, 'error': str(e), 'field': 'unknown', 'message': 'Unexpected validation error'}


def validate_all_impl(validators: List) -> Dict[str, Any]:
    """Run multiple validators and aggregate results."""
    results = []
    all_valid = True
    for validator in validators:
        result = safe_validate_impl(validator)
        results.append(result)
        if not result['valid']:
            all_valid = False
    return {'all_valid': all_valid, 'results': results, 'error_count': sum(1 for r in results if not r['valid'])}


# ===== PUBLIC INTERFACE FUNCTIONS =====

def validate_required(value: Any, field_name: str) -> None:
    """Validate field is present and not None."""
    validate_required_impl(value, field_name)


def validate_type(value: Any, expected_type, field_name: str) -> None:
    """Validate value is of expected type."""
    validate_type_impl(value, expected_type, field_name)


def validate_range(value: float, min_val: Optional[float] = None, 
                  max_val: Optional[float] = None, field_name: str = 'value') -> None:
    """Validate value is within range."""
    validate_range_impl(value, min_val, max_val, field_name)


def validate_string_length(value: str, min_length: Optional[int] = None,
                          max_length: Optional[int] = None, field_name: str = 'string') -> None:
    """Validate string length."""
    validate_string_length_impl(value, min_length, max_length, field_name)


def validate_one_of(value: Any, allowed_values: List[Any], field_name: str = 'value') -> None:
    """Validate value is one of allowed values."""
    validate_one_of_impl(value, allowed_values, field_name)


def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> None:
    """Validate all required fields present in dict."""
    validate_required_fields_impl(data, required_fields)


def validate_dict_schema(data: Dict[str, Any], schema: Dict[str, Dict[str, Any]]) -> None:
    """Validate dict against schema."""
    validate_dict_schema_impl(data, schema)


def safe_validate(validator_func, *args, **kwargs) -> Dict[str, Any]:
    """Run validator and return structured result."""
    return safe_validate_impl(validator_func, *args, **kwargs)


def validate_all(validators: List) -> Dict[str, Any]:
    """Run multiple validators and aggregate results."""
    return validate_all_impl(validators)


# ===== MODULE EXPORTS =====

__all__ = [
    'ValidationOperation',
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
    'safe_validate',
    'validate_all',
    # Internal implementations also exported for advanced module
    'validate_required_impl',
    'validate_type_impl',
    'validate_range_impl',
    'validate_string_length_impl',
    'validate_one_of_impl',
    'validate_required_fields_impl',
    'validate_dict_schema_impl',
    'safe_validate_impl',
    'validate_all_impl',
]

# EOF
