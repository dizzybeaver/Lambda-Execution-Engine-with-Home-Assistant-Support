"""
shared_utilities.py - Main Utility Interface
Version: 2025.10.16.03
Description: Main interface file that consolidates all utility modules

Part of shared_utilities modularization (File 7 of 7 - Main Interface)

MODULAR ARCHITECTURE:
- shared_utilities_types.py: Types, enums, constants
- shared_utilities_core.py: Core SharedUtilityCore class
- shared_utilities_response.py: Response formatting
- shared_utilities_validation_core.py: Core validation
- shared_utilities_validation_advanced.py: Decorators, factory validators
- shared_utilities_cross_interface.py: Cross-interface helpers
- shared_utilities.py: THIS FILE - Main interface and exports

Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

import os
from typing import Dict, Any, Optional, List
import logging as stdlib_logging

# Import from modular files
from shared_utilities_types import UtilityOperation, DEFAULT_USE_GENERIC_OPERATIONS
from shared_utilities_core import SharedUtilityCore
from shared_utilities_response import (
    format_response_fast,
    format_response,
    create_success_response,
    create_error_response
)
from shared_utilities_cross_interface import (
    cache_operation_result,
    record_operation_metrics,
    handle_operation_error,
    create_operation_context,
    close_operation_context,
    batch_cache_operations,
    parallel_operation_execution,
    aggregate_interface_metrics,
    optimize_interface_memory,
    validate_aws_free_tier_compliance
)

# Validation imports with fallback
try:
    from shared_utilities_validation_core import (
        ValidationError,
        RequiredFieldError,
        TypeValidationError,
        RangeValidationError,
        validate_required,
        validate_type,
        validate_range,
        validate_string_length,
        validate_one_of,
        validate_required_fields,
        validate_dict_schema,
        safe_validate,
        validate_all
    )
    from shared_utilities_validation_advanced import (
        create_cache_key_validator,
        create_ttl_validator,
        create_metric_validator,
        validate_params,
        validate_return_type
    )
    _VALIDATION_AVAILABLE = True
except ImportError:
    _VALIDATION_AVAILABLE = False
    
    # Provide minimal fallback stubs
    class ValidationError(Exception):
        def __init__(self, field: str, message: str, value: Any = None):
            self.field = field
            self.message = message
            self.value = value
            super().__init__(f"Validation failed for {field}: {message}")
    
    class RequiredFieldError(ValidationError):
        pass
    
    class TypeValidationError(ValidationError):
        pass
    
    class RangeValidationError(ValidationError):
        pass
    
    def validate_required(value: Any, field_name: str) -> None:
        pass
    
    def validate_type(value: Any, expected_type: type, field_name: str) -> None:
        pass
    
    def validate_range(value: float, min_val: Optional[float] = None, 
                      max_val: Optional[float] = None, field_name: str = 'value') -> None:
        pass
    
    def validate_string_length(value: str, min_length: Optional[int] = None,
                              max_length: Optional[int] = None, field_name: str = 'string') -> None:
        pass
    
    def validate_one_of(value: Any, allowed_values: List[Any], field_name: str = 'value') -> None:
        pass
    
    def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> None:
        pass
    
    def validate_dict_schema(data: Dict[str, Any], schema: Dict[str, Dict[str, Any]]) -> None:
        pass
    
    def safe_validate(validator_func, *args, **kwargs) -> Dict[str, Any]:
        return {'valid': True, 'error': None}
    
    def validate_all(validators: List) -> Dict[str, Any]:
        return {'all_valid': True, 'results': [], 'error_count': 0}
    
    def create_cache_key_validator(min_length: int = 1, max_length: int = 255):
        return lambda key: None
    
    def create_ttl_validator(min_ttl: int = 0, max_ttl: int = 86400):
        return lambda ttl: None
    
    def create_metric_validator():
        return lambda name, value: None
    
    def validate_params(**validators):
        def decorator(func): return func
        return decorator
    
    def validate_return_type(expected_type: type):
        def decorator(func): return func
        return decorator

logger = stdlib_logging.getLogger(__name__)

# Runtime configuration
_USE_GENERIC_OPERATIONS = os.environ.get('USE_GENERIC_OPERATIONS', 'true').lower() == 'true'


# ===== SINGLETON INSTANCE =====

_UTILITY = SharedUtilityCore()


# ===== GENERIC OPERATION DISPATCHER =====

def execute_utility_operation(operation: UtilityOperation, **kwargs):
    """
    Universal utility operation dispatcher.
    Raises errors instead of returning None on configuration failures.
    """
    if not _USE_GENERIC_OPERATIONS:
        return _execute_legacy_operation(operation, **kwargs)
    
    try:
        method_name = operation.value
        method = getattr(_UTILITY, method_name, None)
        
        if method is None:
            raise ValueError(f"Unknown utility operation: {operation.value}")
        
        return method(**kwargs)
    
    except (ValueError, AttributeError) as e:
        logger.error(f"Operation {operation.value} configuration error: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Operation {operation.value} failed: {str(e)}")
        return {
            'error': str(e),
            'operation': operation.value,
            'success': False
        }


def _execute_legacy_operation(operation: UtilityOperation, **kwargs):
    """Legacy operation execution for rollback compatibility."""
    try:
        method = getattr(_UTILITY, operation.value)
        return method(**kwargs)
    except Exception as e:
        logger.error(f"Legacy operation {operation.value} failed: {str(e)}")
        raise


# ===== GATEWAY COMPATIBILITY LAYER =====

def _generate_uuid_implementation():
    """Execute UUID generation."""
    return execute_utility_operation(UtilityOperation.GENERATE_UUID)


def _get_timestamp_implementation():
    """Execute timestamp generation."""
    return execute_utility_operation(UtilityOperation.GET_TIMESTAMP)


def _format_bytes_implementation(size: int):
    """Execute bytes formatting."""
    return execute_utility_operation(UtilityOperation.FORMAT_BYTES, size=size)


def _deep_merge_implementation(dict1: Dict, dict2: Dict):
    """Execute deep merge."""
    return execute_utility_operation(UtilityOperation.DEEP_MERGE, dict1=dict1, dict2=dict2)


def _execute_format_response_implementation(status_code: int, body: Any, 
                                          headers: Optional[Dict] = None, 
                                          use_template: bool = True, **kwargs) -> Dict:
    """Execute response formatting."""
    from shared_utilities_types import DEFAULT_HEADERS_DICT
    if use_template and (headers is None or headers == DEFAULT_HEADERS_DICT):
        return execute_utility_operation(UtilityOperation.FORMAT_RESPONSE_FAST, 
                                        status_code=status_code, body=body)
    else:
        return execute_utility_operation(UtilityOperation.FORMAT_RESPONSE, 
                                        status_code=status_code, body=body, headers=headers)


def _execute_parse_json_implementation(data: str, **kwargs) -> Dict:
    """Execute JSON parsing."""
    return execute_utility_operation(UtilityOperation.PARSE_JSON, data=data)


def _execute_safe_get_implementation(dictionary: Dict, key_path: str, default: Any = None, **kwargs) -> Any:
    """Execute safe get."""
    return execute_utility_operation(UtilityOperation.SAFE_GET, 
                                    dictionary=dictionary, key_path=key_path, default=default)


# ===== PUBLIC INTERFACE FUNCTIONS =====

def generate_correlation_id(prefix: Optional[str] = None) -> str:
    """Generate correlation ID."""
    return _UTILITY.generate_correlation_id(prefix)


def parse_json_safely(json_str: str, use_cache: bool = True) -> Optional[Dict[str, Any]]:
    """Parse JSON safely with optional caching."""
    return _UTILITY.parse_json_safely(json_str, use_cache)


def validate_data_structure(data: Any, expected_type: type,
                           required_fields: Optional[List[str]] = None) -> bool:
    """Validate data structure."""
    return _UTILITY.validate_data_structure(data, expected_type, required_fields)


def format_data_for_response(data: Any, format_type: str = "json",
                            include_metadata: bool = True) -> Dict[str, Any]:
    """Format data for response."""
    return _UTILITY.format_data_for_response(data, format_type, include_metadata)


def cleanup_utility_cache(max_age_seconds: int = 3600) -> int:
    """Clean up old cached utility data."""
    return _UTILITY.cleanup_cache(max_age_seconds)


def get_utility_performance_stats() -> Dict[str, Any]:
    """Get utility performance statistics."""
    return _UTILITY.get_performance_stats()


def optimize_utility_performance() -> Dict[str, Any]:
    """Optimize utility performance based on usage patterns."""
    return _UTILITY.optimize_performance()


def configure_utility_caching(enabled: bool, ttl: int = 300) -> bool:
    """Configure utility caching settings."""
    return _UTILITY.configure_caching(enabled, ttl)


def safe_string_conversion(data: Any, max_length: int = 10000) -> str:
    """Safely convert data to string with length limits."""
    return _UTILITY.safe_string_conversion(data, max_length)


def merge_dictionaries(*dicts: Dict[str, Any]) -> Dict[str, Any]:
    """Merge multiple dictionaries safely."""
    return _UTILITY.merge_dictionaries(*dicts)


def extract_error_details(error: Exception) -> Dict[str, Any]:
    """Extract detailed error information."""
    return _UTILITY.extract_error_details(error)


def validate_operation_parameters(required_params: List[str], 
                                 optional_params: Optional[List[str]] = None,
                                 **kwargs) -> Dict[str, Any]:
    """Generic parameter validation for any interface operation."""
    return _UTILITY.validate_operation_parameters(required_params, optional_params, **kwargs)


# ===== MODULE EXPORTS =====

__all__ = [
    # Core classes
    'UtilityOperation',
    'SharedUtilityCore',
    'execute_utility_operation',
    
    # Gateway compatibility
    '_generate_uuid_implementation',
    '_get_timestamp_implementation',
    '_format_bytes_implementation',
    '_deep_merge_implementation',
    '_execute_format_response_implementation',
    '_execute_parse_json_implementation',
    '_execute_safe_get_implementation',
    
    # Response formatting
    'format_response_fast',
    'format_response',
    'create_success_response',
    'create_error_response',
    
    # Public interface
    'generate_correlation_id',
    'parse_json_safely',
    'validate_data_structure',
    'format_data_for_response',
    'cleanup_utility_cache',
    'get_utility_performance_stats',
    'optimize_utility_performance',
    'configure_utility_caching',
    'safe_string_conversion',
    'merge_dictionaries',
    'extract_error_details',
    'validate_operation_parameters',
    
    # Cross-interface utilities
    'cache_operation_result',
    'record_operation_metrics',
    'handle_operation_error',
    'create_operation_context',
    'close_operation_context',
    'batch_cache_operations',
    'parallel_operation_execution',
    'aggregate_interface_metrics',
    'optimize_interface_memory',
    'validate_aws_free_tier_compliance',
]

# Conditionally add validation exports only if available
if _VALIDATION_AVAILABLE:
    __all__.extend([
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
        'create_metric_validator',
    ])

# EOF
