"""
shared_utilities_validation.py
Version: 2025.10.14.01
Description: Unified validation extension for SUGA utility interface

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
from enum import Enum
import functools


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


# ===== VALIDATION CORE =====

def _validate_required_impl(value: Any, field_name: str) -> None:
    """Validate field is present and not None."""
    if value is None:
        raise RequiredFieldError(field_name, "Required field is missing or null")


def _validate_type_impl(value: Any, expected_type: type, field_name: str) -> None:
    """Validate value is of expected type."""
    if not isinstance(value, expected_type):
        raise TypeValidationError(
            field_name,
            f"Expected {expected_type.__name__}, got {type(value).__name__}",
            value
        )


def _validate_range_impl(value: float, min_val: Optional[float], max_val: Optional[float], field_name: str) -> None:
    """Validate value is within range."""
    if min_val is not None and value < min_val:
        raise RangeValidationError(field_name, f"Value {value} below minimum {min_val}", value)
    if max_val is not None and value > max_val:
        raise RangeValidationError(field_name, f"Value {value} above maximum {max_val}", value)


def _validate_string_length_impl(value: str, min_length: Optional[int], max_length: Optional[int], field_name: str) -> None:
    """Validate string length."""
    length = len(value)
    if min_length is not None and length < min_length:
        raise ValidationError(field_name, f"String length {length} below minimum {min_length}", value)
    if max_length is not None and length > max_length:
        raise ValidationError(field_name, f"String length {length} above maximum {max_length}", value)


def _validate_one_of_impl(value: Any, allowed_values: List[Any], field_name: str) -> None:
    """Validate value is one of allowed values."""
    if value not in allowed_values:
        raise ValidationError(field_name, f"Value must be one of {allowed_values}, got {value}", value)


def _validate_required_fields_impl(data: Dict[str, Any], required_fields: List[str]) -> None:
    """Validate all required fields present in dict."""
    for field in required_fields:
        if field not in data or data[field] is None:
            raise RequiredFieldError(field, "Required field is missing or null")


def _validate_dict_schema_impl(data: Dict[str, Any], schema: Dict[str, Dict[str, Any]]) -> None:
    """Validate dict against schema."""
    for field_name, rules in schema.items():
        value = data.get(field_name)
        
        if rules.get('required', False):
            _validate_required_impl(value, field_name)
        
        if value is None and not rules.get('required', False):
            continue
        
        if 'type' in rules:
            _validate_type_impl(value, rules['type'], field_name)
        
        if isinstance(value, (int, float)):
            _validate_range_impl(value, rules.get('min'), rules.get('max'), field_name)
        
        if isinstance(value, str):
            _validate_string_length_impl(value, rules.get('min_length'), rules.get('max_length'), field_name)
        
        if 'allowed' in rules:
            _validate_one_of_impl(value, rules['allowed'], field_name)


def _safe_validate_impl(validator_func: Callable, *args, **kwargs) -> Dict[str, Any]:
    """Run validator and return structured result."""
    try:
        validator_func(*args, **kwargs)
        return {'valid': True, 'error': None}
    except ValidationError as e:
        return {'valid': False, 'error': str(e), 'field': e.field, 'message': e.message}
    except Exception as e:
        return {'valid': False, 'error': str(e), 'field': 'unknown', 'message': 'Unexpected validation error'}


def _validate_all_impl(validators: List[Callable]) -> Dict[str, Any]:
    """Run multiple validators and aggregate results."""
    results = []
    all_valid = True
    for validator in validators:
        result = _safe_validate_impl(validator)
        results.append(result)
        if not result['valid']:
            all_valid = False
    return {'all_valid': all_valid, 'results': results, 'error_count': sum(1 for r in results if not r['valid'])}


def _create_cache_key_validator_impl(min_length: int, max_length: int) -> Callable:
    """Create validator for cache keys."""
    def validator(key: str) -> None:
        _validate_required_impl(key, 'key')
        _validate_type_impl(key, str, 'key')
        _validate_string_length_impl(key, min_length, max_length, 'key')
    return validator


def _create_ttl_validator_impl(min_ttl: int, max_ttl: int) -> Callable:
    """Create validator for TTL values."""
    def validator(ttl: int) -> None:
        if ttl is not None:
            _validate_type_impl(ttl, int, 'ttl')
            _validate_range_impl(ttl, min_ttl, max_ttl, 'ttl')
    return validator


def _create_metric_validator_impl() -> Callable:
    """Create validator for metric recording."""
    def validator(name: str, value: float) -> None:
        _validate_required_impl(name, 'name')
        _validate_type_impl(name, str, 'name')
        _validate_string_length_impl(name, 1, 255, 'name')
        _validate_required_impl(value, 'value')
        _validate_type_impl(value, (int, float), 'value')
    return validator


# ===== GENERIC VALIDATION DISPATCHER =====

def execute_validation_operation(operation: ValidationOperation, **kwargs) -> Any:
    """Generic validation operation dispatcher."""
    
    if operation == ValidationOperation.VALIDATE_REQUIRED:
        _validate_required_impl(kwargs['value'], kwargs['field_name'])
        return None
    
    elif operation == ValidationOperation.VALIDATE_TYPE:
        _validate_type_impl(kwargs['value'], kwargs['expected_type'], kwargs['field_name'])
        return None
    
    elif operation == ValidationOperation.VALIDATE_RANGE:
        _validate_range_impl(kwargs['value'], kwargs.get('min_val'), kwargs.get('max_val'), kwargs.get('field_name', 'value'))
        return None
    
    elif operation == ValidationOperation.VALIDATE_STRING_LENGTH:
        _validate_string_length_impl(kwargs['value'], kwargs.get('min_length'), kwargs.get('max_length'), kwargs.get('field_name', 'string'))
        return None
    
    elif operation == ValidationOperation.VALIDATE_ONE_OF:
        _validate_one_of_impl(kwargs['value'], kwargs['allowed_values'], kwargs.get('field_name', 'value'))
        return None
    
    elif operation == ValidationOperation.VALIDATE_REQUIRED_FIELDS:
        _validate_required_fields_impl(kwargs['data'], kwargs['required_fields'])
        return None
    
    elif operation == ValidationOperation.VALIDATE_DICT_SCHEMA:
        _validate_dict_schema_impl(kwargs['data'], kwargs['schema'])
        return None
    
    elif operation == ValidationOperation.SAFE_VALIDATE:
        return _safe_validate_impl(kwargs['validator_func'], *kwargs.get('args', ()), **kwargs.get('vkwargs', {}))
    
    elif operation == ValidationOperation.VALIDATE_ALL:
        return _validate_all_impl(kwargs['validators'])
    
    elif operation == ValidationOperation.CREATE_CACHE_KEY_VALIDATOR:
        return _create_cache_key_validator_impl(kwargs.get('min_length', 1), kwargs.get('max_length', 255))
    
    elif operation == ValidationOperation.CREATE_TTL_VALIDATOR:
        return _create_ttl_validator_impl(kwargs.get('min_ttl', 0), kwargs.get('max_ttl', 86400))
    
    elif operation == ValidationOperation.CREATE_METRIC_VALIDATOR:
        return _create_metric_validator_impl()
    
    else:
        raise ValueError(f"Unknown validation operation: {operation}")


# ===== PUBLIC INTERFACE =====

def validate_required(value: Any, field_name: str) -> None:
    """Validate field is present and not None."""
    execute_validation_operation(ValidationOperation.VALIDATE_REQUIRED, value=value, field_name=field_name)


def validate_type(value: Any, expected_type: type, field_name: str) -> None:
    """Validate value is of expected type."""
    execute_validation_operation(ValidationOperation.VALIDATE_TYPE, value=value, expected_type=expected_type, field_name=field_name)


def validate_range(value: float, min_val: Optional[float] = None, max_val: Optional[float] = None, field_name: str = "value") -> None:
    """Validate value is within range."""
    execute_validation_operation(ValidationOperation.VALIDATE_RANGE, value=value, min_val=min_val, max_val=max_val, field_name=field_name)


def validate_string_length(value: str, min_length: Optional[int] = None, max_length: Optional[int] = None, field_name: str = "string") -> None:
    """Validate string length."""
    execute_validation_operation(ValidationOperation.VALIDATE_STRING_LENGTH, value=value, min_length=min_length, max_length=max_length, field_name=field_name)


def validate_one_of(value: Any, allowed_values: List[Any], field_name: str = "value") -> None:
    """Validate value is one of allowed values."""
    execute_validation_operation(ValidationOperation.VALIDATE_ONE_OF, value=value, allowed_values=allowed_values, field_name=field_name)


def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> None:
    """Validate all required fields present in dict."""
    execute_validation_operation(ValidationOperation.VALIDATE_REQUIRED_FIELDS, data=data, required_fields=required_fields)


def validate_dict_schema(data: Dict[str, Any], schema: Dict[str, Dict[str, Any]]) -> None:
    """Validate dict against schema."""
    execute_validation_operation(ValidationOperation.VALIDATE_DICT_SCHEMA, data=data, schema=schema)


def safe_validate(validator_func: Callable, *args, **kwargs) -> Dict[str, Any]:
    """Run validator and return structured result."""
    return execute_validation_operation(ValidationOperation.SAFE_VALIDATE, validator_func=validator_func, args=args, vkwargs=kwargs)


def validate_all(validators: List[Callable]) -> Dict[str, Any]:
    """Run multiple validators and aggregate results."""
    return execute_validation_operation(ValidationOperation.VALIDATE_ALL, validators=validators)


def create_cache_key_validator(min_length: int = 1, max_length: int = 255) -> Callable:
    """Create validator for cache keys."""
    return execute_validation_operation(ValidationOperation.CREATE_CACHE_KEY_VALIDATOR, min_length=min_length, max_length=max_length)


def create_ttl_validator(min_ttl: int = 0, max_ttl: int = 86400) -> Callable:
    """Create validator for TTL values."""
    return execute_validation_operation(ValidationOperation.CREATE_TTL_VALIDATOR, min_ttl=min_ttl, max_ttl=max_ttl)


def create_metric_validator() -> Callable:
    """Create validator for metric recording."""
    return execute_validation_operation(ValidationOperation.CREATE_METRIC_VALIDATOR)


# ===== DECORATORS =====

def validate_params(**validators):
    """Decorator to validate function parameters."""
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
    """Decorator to validate function return type."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            if result is not None and not isinstance(result, expected_type):
                raise TypeValidationError('return_value', f"Expected {expected_type.__name__}, got {type(result).__name__}", result)
            return result
        return wrapper
    return decorator


__all__ = [
    'ValidationOperation',
    'ValidationError',
    'RequiredFieldError',
    'TypeValidationError',
    'RangeValidationError',
    'execute_validation_operation',
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
