"""
utility_validation.py
Version: 2025.09.30.01
Description: Generic validation functions for all interfaces

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

import re
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass


@dataclass
class ValidationResult:
    """Standardized validation result."""
    valid: bool
    errors: List[str]
    warnings: List[str]
    validated_data: Dict[str, Any]


def validate_required_params(params: List[str], data: Dict[str, Any]) -> ValidationResult:
    """
    Validate that all required parameters are present in data.
    """
    errors = []
    warnings = []
    validated_data = {}
    
    for param in params:
        if param not in data:
            errors.append(f"Missing required parameter: {param}")
        elif data[param] is None:
            errors.append(f"Required parameter '{param}' is None")
        else:
            validated_data[param] = data[param]
    
    for key, value in data.items():
        if key not in params:
            warnings.append(f"Unknown parameter: {key}")
    
    return ValidationResult(
        valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
        validated_data=validated_data
    )


def validate_param_types(schema: Dict[str, type], data: Dict[str, Any]) -> ValidationResult:
    """
    Validate parameter types against schema.
    Schema format: {'param_name': expected_type}
    """
    errors = []
    warnings = []
    validated_data = {}
    
    for param_name, expected_type in schema.items():
        if param_name in data:
            value = data[param_name]
            if value is not None and not isinstance(value, expected_type):
                errors.append(
                    f"Parameter '{param_name}' type mismatch: expected {expected_type.__name__}, "
                    f"got {type(value).__name__}"
                )
            else:
                validated_data[param_name] = value
        else:
            warnings.append(f"Parameter '{param_name}' not in data")
    
    return ValidationResult(
        valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
        validated_data=validated_data
    )


def validate_param_ranges(constraints: Dict[str, Dict[str, Any]], 
                         data: Dict[str, Any]) -> ValidationResult:
    """
    Validate numeric parameter ranges.
    Constraints format: {'param_name': {'min': x, 'max': y}}
    """
    errors = []
    warnings = []
    validated_data = {}
    
    for param_name, constraint in constraints.items():
        if param_name in data:
            value = data[param_name]
            
            if not isinstance(value, (int, float)):
                errors.append(f"Parameter '{param_name}' must be numeric")
                continue
            
            min_val = constraint.get('min')
            max_val = constraint.get('max')
            
            if min_val is not None and value < min_val:
                errors.append(f"Parameter '{param_name}' ({value}) below minimum ({min_val})")
            elif max_val is not None and value > max_val:
                errors.append(f"Parameter '{param_name}' ({value}) above maximum ({max_val})")
            else:
                validated_data[param_name] = value
        else:
            warnings.append(f"Parameter '{param_name}' not in data")
    
    return ValidationResult(
        valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
        validated_data=validated_data
    )


def validate_string_format(pattern: str, value: str, 
                          param_name: str = "value") -> ValidationResult:
    """
    Validate string format against regex pattern.
    """
    errors = []
    validated_data = {}
    
    if not isinstance(value, str):
        errors.append(f"Parameter '{param_name}' must be a string")
    else:
        try:
            if re.match(pattern, value):
                validated_data[param_name] = value
            else:
                errors.append(f"Parameter '{param_name}' does not match pattern: {pattern}")
        except re.error as e:
            errors.append(f"Invalid regex pattern: {e}")
    
    return ValidationResult(
        valid=len(errors) == 0,
        errors=errors,
        warnings=[],
        validated_data=validated_data
    )


def validate_numeric_range(min_val: float, max_val: float, value: Union[int, float],
                          param_name: str = "value") -> ValidationResult:
    """
    Validate numeric value is within range.
    """
    errors = []
    validated_data = {}
    
    if not isinstance(value, (int, float)):
        errors.append(f"Parameter '{param_name}' must be numeric")
    elif value < min_val:
        errors.append(f"Parameter '{param_name}' ({value}) below minimum ({min_val})")
    elif value > max_val:
        errors.append(f"Parameter '{param_name}' ({value}) above maximum ({max_val})")
    else:
        validated_data[param_name] = value
    
    return ValidationResult(
        valid=len(errors) == 0,
        errors=errors,
        warnings=[],
        validated_data=validated_data
    )


def validate_string_length(value: str, min_length: Optional[int] = None, 
                          max_length: Optional[int] = None,
                          param_name: str = "value") -> ValidationResult:
    """
    Validate string length constraints.
    """
    errors = []
    validated_data = {}
    
    if not isinstance(value, str):
        errors.append(f"Parameter '{param_name}' must be a string")
    else:
        length = len(value)
        if min_length is not None and length < min_length:
            errors.append(
                f"Parameter '{param_name}' length ({length}) below minimum ({min_length})"
            )
        elif max_length is not None and length > max_length:
            errors.append(
                f"Parameter '{param_name}' length ({length}) above maximum ({max_length})"
            )
        else:
            validated_data[param_name] = value
    
    return ValidationResult(
        valid=len(errors) == 0,
        errors=errors,
        warnings=[],
        validated_data=validated_data
    )


def validate_enum_value(value: Any, allowed_values: List[Any],
                       param_name: str = "value") -> ValidationResult:
    """
    Validate value is in allowed list.
    """
    errors = []
    validated_data = {}
    
    if value not in allowed_values:
        errors.append(
            f"Parameter '{param_name}' value '{value}' not in allowed values: {allowed_values}"
        )
    else:
        validated_data[param_name] = value
    
    return ValidationResult(
        valid=len(errors) == 0,
        errors=errors,
        warnings=[],
        validated_data=validated_data
    )


def validate_dict_structure(required_keys: List[str], data: Dict[str, Any],
                           optional_keys: Optional[List[str]] = None) -> ValidationResult:
    """
    Validate dictionary has required structure.
    """
    errors = []
    warnings = []
    validated_data = {}
    
    for key in required_keys:
        if key not in data:
            errors.append(f"Missing required key: {key}")
        else:
            validated_data[key] = data[key]
    
    all_expected_keys = set(required_keys + (optional_keys or []))
    for key in data.keys():
        if key not in all_expected_keys:
            warnings.append(f"Unexpected key: {key}")
    
    return ValidationResult(
        valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
        validated_data=validated_data
    )


__all__ = [
    'ValidationResult',
    'validate_required_params',
    'validate_param_types',
    'validate_param_ranges',
    'validate_string_format',
    'validate_numeric_range',
    'validate_string_length',
    'validate_enum_value',
    'validate_dict_structure',
]

# EOF
