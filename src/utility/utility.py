"""
utility.py - Testing, Validation, and Debugging Primary Gateway Interface
Version: 2025.09.27.02
Description: Ultra-pure gateway for utility operations - pure delegation only

ARCHITECTURE: PRIMARY GATEWAY INTERFACE
- Function declarations ONLY - no implementation code
- Pure delegation to utility_core.py
- External access point for utility operations
- Ultra-optimized for 128MB Lambda constraint

UPDATES APPLIED:
- ✅ ADDED: Import validation functions for circular import detection
- ✅ UPDATED: Gateway interface exports with new function declarations
- ✅ MAINTAINED: Pure delegation pattern for all operations

PRIMARY GATEWAY FUNCTIONS:
- validate_string_input() - String input validation and sanitization
- create_success_response() - Success response formatting
- create_error_response() - Error response formatting
- sanitize_response_data() - Response data sanitization
- get_current_timestamp() - Timestamp generation
- detect_circular_imports() - Circular import pattern detection
- validate_import_architecture() - Import architecture validation
- monitor_imports_runtime() - Runtime import monitoring
- apply_immediate_fixes() - Automatic import issue fixes

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

from typing import Dict, Any
from .utility_core import generic_utility_operation, UtilityOperation

# ===== SECTION 1: PRIMARY GATEWAY INTERFACE FUNCTIONS =====

def validate_string_input(value: str, min_length: int = 0, max_length: int = 1000) -> bool:
    """
    Primary gateway function for string input validation.
    Pure delegation to utility_core implementation.
    """
    result = generic_utility_operation(
        UtilityOperation.VALIDATE_STRING,
        value=value,
        min_length=min_length,
        max_length=max_length
    )
    return result.get("valid", False)

def create_success_response(message: str, data: Any = None) -> Dict[str, Any]:
    """
    Primary gateway function for success response creation.
    Pure delegation to utility_core implementation.
    """
    return generic_utility_operation(
        UtilityOperation.CREATE_SUCCESS_RESPONSE,
        message=message,
        data=data
    )

def create_error_response(message: str, error_code: str = "GENERIC_ERROR") -> Dict[str, Any]:
    """
    Primary gateway function for error response creation.
    Pure delegation to utility_core implementation.
    """
    return generic_utility_operation(
        UtilityOperation.CREATE_ERROR_RESPONSE,
        message=message,
        error_code=error_code
    )

def sanitize_response_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Primary gateway function for response data sanitization.
    Pure delegation to utility_core implementation.
    """
    return generic_utility_operation(
        UtilityOperation.SANITIZE_DATA,
        data=data
    )

def get_current_timestamp() -> str:
    """
    Primary gateway function for timestamp generation.
    Pure delegation to utility_core implementation.
    """
    result = generic_utility_operation(UtilityOperation.GET_TIMESTAMP)
    return result.get("timestamp", "")

# ===== SECTION 2: IMPORT VALIDATION GATEWAY FUNCTIONS =====

def detect_circular_imports(project_path: str = ".") -> Dict[str, Any]:
    """
    Primary gateway function for circular import detection.
    Pure delegation to utility_import_validation implementation.
    """
    return generic_utility_operation(
        UtilityOperation.DETECT_CIRCULAR_IMPORTS,
        project_path=project_path
    )

def validate_import_architecture(project_path: str = ".") -> Dict[str, Any]:
    """
    Primary gateway function for import architecture validation.
    Pure delegation to utility_import_validation implementation.
    """
    return generic_utility_operation(
        UtilityOperation.VALIDATE_IMPORT_ARCHITECTURE,
        project_path=project_path
    )

def monitor_imports_runtime() -> Dict[str, Any]:
    """
    Primary gateway function for runtime import monitoring.
    Pure delegation to utility_import_validation implementation.
    """
    return generic_utility_operation(
        UtilityOperation.MONITOR_IMPORTS_RUNTIME
    )

def apply_immediate_fixes() -> Dict[str, Any]:
    """
    Primary gateway function for immediate import issue fixes.
    Pure delegation to utility_import_validation implementation.
    """
    return generic_utility_operation(
        UtilityOperation.APPLY_IMMEDIATE_FIXES
    )

# ===== SECTION 3: MODULE EXPORTS =====

__all__ = [
    'validate_string_input',
    'create_success_response',
    'create_error_response', 
    'sanitize_response_data',
    'get_current_timestamp',
    'detect_circular_imports',
    'validate_import_architecture',
    'monitor_imports_runtime',
    'apply_immediate_fixes'
]

# EOF
