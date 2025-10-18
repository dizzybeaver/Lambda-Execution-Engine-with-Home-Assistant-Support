"""
interface_utility.py - Utility Interface Router (SUGA-ISP)
Version: 2025.10.17.16
Description: Router/Firewall for utility interface with dispatch dictionary pattern

CHANGELOG:
- 2025.10.17.16: COMPLETED Issue #20 + Modernized with dispatch dictionary
  - Added complete import protection for ALL utility modules
  - Converted from elif chain to dispatch dictionary pattern
  - Reduced code from ~400 lines to ~200 lines
  - O(1) operation lookup vs O(n) elif chain
  - Easier to maintain and extend
  - Consistent with new architecture pattern

Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

import os
from typing import Dict, Any, Optional, List, Callable
import logging as stdlib_logging

logger = stdlib_logging.getLogger(__name__)

# ===== IMPORT PROTECTION =====

# Types module
try:
    from utility_types import UtilityOperation, DEFAULT_USE_GENERIC_OPERATIONS
    _TYPES_AVAILABLE = True
except ImportError as e:
    _TYPES_AVAILABLE = False
    logger.error(f"Utility types unavailable: {e}")
    UtilityOperation = None
    DEFAULT_USE_GENERIC_OPERATIONS = None

# Core utility module
try:
    from utility_core import SharedUtilityCore
    _CORE_AVAILABLE = True
except ImportError as e:
    _CORE_AVAILABLE = False
    logger.error(f"Utility core unavailable: {e}")
    SharedUtilityCore = None

# Response formatting
try:
    from utility_response import (
        format_response_fast,
        format_response,
        create_success_response,
        create_error_response
    )
    _RESPONSE_AVAILABLE = True
except ImportError as e:
    _RESPONSE_AVAILABLE = False
    logger.error(f"Utility response unavailable: {e}")
    format_response_fast = None
    format_response = None
    create_success_response = None
    create_error_response = None

# Cross-interface utilities
try:
    from utility_cross_interface import (
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
    _CROSS_INTERFACE_AVAILABLE = True
except ImportError as e:
    _CROSS_INTERFACE_AVAILABLE = False
    logger.error(f"Cross-interface utilities unavailable: {e}")
    cache_operation_result = None
    record_operation_metrics = None
    handle_operation_error = None
    create_operation_context = None
    close_operation_context = None
    batch_cache_operations = None
    parallel_operation_execution = None
    aggregate_interface_metrics = None
    optimize_interface_memory = None
    validate_aws_free_tier_compliance = None

# Validation modules
try:
    from utility_validation_core import (
        ValidationError, RequiredFieldError, TypeValidationError, RangeValidationError,
        validate_required, validate_type, validate_range, validate_string_length,
        validate_one_of, validate_required_fields, validate_dict_schema
    )
    from utility_validation_advanced import (
        validate_params, validate_return_type, safe_validate, validate_all,
        create_cache_key_validator, create_ttl_validator, create_metric_validator
    )
    _VALIDATION_AVAILABLE = True
except ImportError as e:
    _VALIDATION_AVAILABLE = False
    logger.error(f"Validation utilities unavailable: {e}")
    ValidationError = RequiredFieldError = TypeValidationError = RangeValidationError = None
    validate_required = validate_type = validate_range = validate_string_length = None
    validate_one_of = validate_required_fields = validate_dict_schema = None
    validate_params = validate_return_type = safe_validate = validate_all = None
    create_cache_key_validator = create_ttl_validator = create_metric_validator = None

# ===== UTILITY CORE INITIALIZATION =====

if _CORE_AVAILABLE:
    _UTILITY = SharedUtilityCore()
else:
    _UTILITY = None

# ===== OPERATION DISPATCH DICTIONARY =====

def _build_dispatch_dict():
    """Build operation dispatch dictionary. Only called if _UTILITY available."""
    if not _UTILITY:
        return {}
    
    return {
        # Core operations
        'generate_uuid': _UTILITY.generate_uuid,
        'get_timestamp': _UTILITY.get_timestamp,
        'format_bytes': _UTILITY.format_bytes,
        'deep_merge': _UTILITY.deep_merge,
        'parse_json': _UTILITY.parse_json_safely,
        'safe_get': _UTILITY.safe_get,
        
        # Response formatting (delegates to utility_response functions)
        'format_response': lambda **kwargs: format_response(**kwargs) if _RESPONSE_AVAILABLE else None,
        'format_response_fast': lambda **kwargs: format_response_fast(**kwargs) if _RESPONSE_AVAILABLE else None,
        'create_success_response': lambda **kwargs: create_success_response(**kwargs) if _RESPONSE_AVAILABLE else None,
        'create_error_response': lambda **kwargs: create_error_response(**kwargs) if _RESPONSE_AVAILABLE else None,
        
        # Utility core methods
        'generate_correlation_id': _UTILITY.generate_correlation_id,
        'validate_data_structure': _UTILITY.validate_data_structure,
        'format_data_for_response': _UTILITY.format_data_for_response,
        'cleanup_utility_cache': _UTILITY.cleanup_utility_cache,
        'get_utility_performance_stats': _UTILITY.get_utility_performance_stats,
        'optimize_utility_performance': _UTILITY.optimize_utility_performance,
        'configure_utility_caching': _UTILITY.configure_utility_caching,
        'safe_string_conversion': _UTILITY.safe_string_conversion,
        'merge_dictionaries': _UTILITY.merge_dictionaries,
        'extract_error_details': _UTILITY.extract_error_details,
        'validate_operation_parameters': _UTILITY.validate_operation_parameters,
    }

_OPERATION_DISPATCH = _build_dispatch_dict() if _CORE_AVAILABLE else {}

# ===== MAIN ROUTER FUNCTION =====

def execute_utility_operation(operation: str, **kwargs) -> Any:
    """
    Route utility operations using dispatch dictionary pattern.
    
    Args:
        operation: Operation name to execute
        **kwargs: Operation-specific parameters
        
    Returns:
        Operation result
        
    Raises:
        RuntimeError: If utility core unavailable
        ValueError: If operation unknown
    """
    # Check availability
    if not _CORE_AVAILABLE:
        raise RuntimeError(
            "Utility interface unavailable: core module import failed. "
            "Cannot execute utility operations."
        )
    
    # Validate operation exists
    if operation not in _OPERATION_DISPATCH:
        raise ValueError(
            f"Unknown utility operation: '{operation}'. "
            f"Valid operations: {', '.join(sorted(_OPERATION_DISPATCH.keys()))}"
        )
    
    # Parameter validation for operations that require it
    if operation == 'parse_json' and 'data' not in kwargs:
        raise ValueError("parse_json requires 'data' parameter")
    if operation == 'safe_get':
        if 'dictionary' not in kwargs:
            raise ValueError("safe_get requires 'dictionary' parameter")
        if 'key_path' not in kwargs:
            raise ValueError("safe_get requires 'key_path' parameter")
    if operation == 'format_bytes' and 'size' not in kwargs:
        raise ValueError("format_bytes requires 'size' parameter")
    if operation == 'deep_merge':
        if 'dict1' not in kwargs or 'dict2' not in kwargs:
            raise ValueError("deep_merge requires 'dict1' and 'dict2' parameters")
    
    # Dispatch to operation
    return _OPERATION_DISPATCH[operation](**kwargs)

# ===== GATEWAY COMPATIBILITY LAYER =====

def _generate_uuid_implementation():
    """Execute UUID generation."""
    return execute_utility_operation('generate_uuid')

def _get_timestamp_implementation():
    """Execute timestamp generation."""
    return execute_utility_operation('get_timestamp')

def _format_bytes_implementation(size: int):
    """Execute bytes formatting."""
    return execute_utility_operation('format_bytes', size=size)

def _deep_merge_implementation(dict1: Dict, dict2: Dict):
    """Execute deep merge."""
    return execute_utility_operation('deep_merge', dict1=dict1, dict2=dict2)

def _execute_format_response_implementation(status_code: int, body: Any, 
                                          headers: Optional[Dict] = None, 
                                          use_template: bool = True, **kwargs) -> Dict:
    """Execute response formatting."""
    if use_template and not headers:
        return execute_utility_operation('format_response_fast', 
                                        status_code=status_code, body=body)
    else:
        return execute_utility_operation('format_response', 
                                        status_code=status_code, body=body, headers=headers)

def _execute_parse_json_implementation(data: str, **kwargs) -> Dict:
    """Execute JSON parsing."""
    return execute_utility_operation('parse_json', data=data)

def _execute_safe_get_implementation(dictionary: Dict, key_path: str, default: Any = None, **kwargs) -> Any:
    """Execute safe get."""
    return execute_utility_operation('safe_get', dictionary=dictionary, 
                                    key_path=key_path, default=default)

# ===== PUBLIC INTERFACE FUNCTIONS =====

def generate_correlation_id(prefix: Optional[str] = None) -> str:
    """Generate correlation ID."""
    return _UTILITY.generate_correlation_id(prefix) if _UTILITY else None

def parse_json_safely(json_str: str, use_cache: bool = True) -> Optional[Dict[str, Any]]:
    """Parse JSON safely with optional caching."""
    return _UTILITY.parse_json_safely(json_str, use_cache) if _UTILITY else None

def validate_data_structure(data: Any, expected_type: type,
                           required_fields: Optional[List[str]] = None) -> bool:
    """Validate data structure."""
    return _UTILITY.validate_data_structure(data, expected_type, required_fields) if _UTILITY else False

def format_data_for_response(data: Any, format_type: str = "json",
                            include_metadata: bool = True) -> Dict[str, Any]:
    """Format data for response."""
    return _UTILITY.format_data_for_response(data, format_type, include_metadata) if _UTILITY else {}

def cleanup_utility_cache() -> int:
    """Cleanup utility cache."""
    return _UTILITY.cleanup_utility_cache() if _UTILITY else 0

def get_utility_performance_stats() -> Dict[str, Any]:
    """Get utility performance stats."""
    return _UTILITY.get_utility_performance_stats() if _UTILITY else {}

def optimize_utility_performance() -> Dict[str, Any]:
    """Optimize utility performance."""
    return _UTILITY.optimize_utility_performance() if _UTILITY else {}

def configure_utility_caching(enabled: bool, ttl: int = 300) -> None:
    """Configure utility caching."""
    if _UTILITY:
        _UTILITY.configure_utility_caching(enabled, ttl)

def safe_string_conversion(value: Any, max_length: Optional[int] = None) -> str:
    """Safe string conversion."""
    return _UTILITY.safe_string_conversion(value, max_length) if _UTILITY else str(value)

def merge_dictionaries(*dicts: Dict) -> Dict:
    """Merge dictionaries."""
    return _UTILITY.merge_dictionaries(*dicts) if _UTILITY else {}

def extract_error_details(error: Exception) -> Dict[str, Any]:
    """Extract error details."""
    return _UTILITY.extract_error_details(error) if _UTILITY else {}

def validate_operation_parameters(required_params: List[str], 
                                 optional_params: Optional[List[str]] = None,
                                 **kwargs) -> Dict[str, Any]:
    """Validate operation parameters."""
    return _UTILITY.validate_operation_parameters(required_params, optional_params, **kwargs) if _UTILITY else {}

# ===== MODULE EXPORTS =====

__all__ = [
    'execute_utility_operation',
    '_generate_uuid_implementation',
    '_get_timestamp_implementation',
    '_format_bytes_implementation',
    '_deep_merge_implementation',
    '_execute_format_response_implementation',
    '_execute_parse_json_implementation',
    '_execute_safe_get_implementation',
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
]

# Response formatting exports (if available)
if _RESPONSE_AVAILABLE:
    __all__.extend(['format_response_fast', 'format_response', 
                    'create_success_response', 'create_error_response'])

# Cross-interface exports (if available)
if _CROSS_INTERFACE_AVAILABLE:
    __all__.extend(['cache_operation_result', 'record_operation_metrics', 
                    'handle_operation_error', 'create_operation_context',
                    'close_operation_context', 'batch_cache_operations',
                    'parallel_operation_execution', 'aggregate_interface_metrics',
                    'optimize_interface_memory', 'validate_aws_free_tier_compliance'])

# Validation exports (if available)
if _VALIDATION_AVAILABLE:
    __all__.extend(['ValidationError', 'RequiredFieldError', 'TypeValidationError',
                    'RangeValidationError', 'validate_required', 'validate_type',
                    'validate_range', 'validate_string_length', 'validate_one_of',
                    'validate_required_fields', 'validate_dict_schema', 'validate_params',
                    'validate_return_type', 'safe_validate', 'validate_all',
                    'create_cache_key_validator', 'create_ttl_validator', 
                    'create_metric_validator'])

# EOF
