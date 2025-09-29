"""
utility_core.py - ULTRA-OPTIMIZED: Maximum Gateway Utilization Utility Implementation
Version: 2025.09.28.03
Description: Ultra-lightweight utility core with maximum gateway utilization and validation consolidation

CORRECTIONS APPLIED (2025.09.28.03):
- ✅ RENAMED: VALIDATE_CONFIGURATION → VALIDATE_INPUT_CONFIGURATION (clarifies input-level validation)
- ✅ REMOVED: GET_DIAGNOSTIC_INFO (moved to debug_core.py per special status)
- ✅ CLARIFIED: Utility handles basic/generic operations, debug handles system diagnostics

ARCHITECTURE: SECONDARY IMPLEMENTATION - ULTRA-OPTIMIZED
- Maximum delegation to gateway interfaces
- Generic operation patterns eliminate code duplication
- Intelligent caching for validation results
- Single-threaded Lambda optimized with zero threading overhead

GATEWAY UTILIZATION STRATEGY (MAXIMIZED):
- cache.py: Validation result caching, correlation ID cache
- singleton.py: Utility manager access, system coordination
- metrics.py: Utility metrics, validation timing
- logging.py: All utility logging with context and correlation
- security.py: Input validation, data sanitization
- config.py: Utility configuration, validation rules

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

import logging
import time
import json
import uuid
import hashlib
import re
from typing import Dict, Any, Optional, Union, List
from enum import Enum

# Ultra-pure gateway imports for maximum utilization
from . import cache
from . import singleton  
from . import metrics
from . import logging as log_gateway
from . import security
from . import config

logger = logging.getLogger(__name__)

# ===== SECTION 1: CACHE KEYS AND CONSTANTS =====

UTILITY_CACHE_PREFIX = "util_"
VALIDATION_CACHE_PREFIX = "valid_"
IMPORT_VALIDATION_CACHE_PREFIX = "import_"
UTILITY_CACHE_TTL = 300  # 5 minutes

# Validation patterns
EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
URL_PATTERN = re.compile(r'^https?://[^\s]+$')
UUID_PATTERN = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', re.IGNORECASE)

# ===== SECTION 2: UTILITY OPERATION ENUM =====

class UtilityOperation(Enum):
    """Ultra-generic utility operations for basic/generic utilities."""
    # Core utility operations
    VALIDATE_STRING = "validate_string"
    CREATE_SUCCESS_RESPONSE = "create_success_response"
    CREATE_ERROR_RESPONSE = "create_error_response"
    SANITIZE_DATA = "sanitize_data"
    GET_TIMESTAMP = "get_timestamp"
    
    # Import validation operations
    DETECT_CIRCULAR_IMPORTS = "detect_circular_imports"
    VALIDATE_IMPORT_ARCHITECTURE = "validate_import_architecture"
    MONITOR_IMPORTS_RUNTIME = "monitor_imports_runtime"
    APPLY_IMMEDIATE_FIXES = "apply_immediate_fixes"
    
    # Additional utility operations (basic input-level)
    VALIDATE_INPUT = "validate_input"
    SANITIZE_RESPONSE = "sanitize_response"
    GENERATE_CORRELATION_ID = "generate_correlation_id"
    VALIDATE_INPUT_CONFIGURATION = "validate_input_configuration"  # RENAMED: Input-level validation only

# ===== SECTION 3: GENERIC UTILITY OPERATION FUNCTION =====

def generic_utility_operation(operation: UtilityOperation, **kwargs) -> Any:
    """
    ULTRA-GENERIC: Execute any utility operation using operation type.
    Consolidates all utility functions into single ultra-optimized function.
    """
    try:
        # Generate correlation ID for tracking
        correlation_id = _generate_correlation_id_core()
        
        # Start timing for metrics
        start_time = time.time()
        
        # Log operation start
        log_gateway.log_debug(f"Utility operation started: {operation.value}", {
            "correlation_id": correlation_id,
            "operation": operation.value
        })
        
        # Check cache for cacheable operations
        cache_key = f"{UTILITY_CACHE_PREFIX}{operation.value}_{hash(str(kwargs))}"
        if operation in [UtilityOperation.DETECT_CIRCULAR_IMPORTS, UtilityOperation.VALIDATE_IMPORT_ARCHITECTURE]:
            cached_result = cache.cache_get(cache_key)
            if cached_result:
                log_gateway.log_debug(f"Cache hit for utility operation: {operation.value}")
                metrics.record_metric("utility_cache_hit", 1.0)
                return cached_result
        
        # Execute operation based on type
        if operation == UtilityOperation.VALIDATE_STRING:
            result = _validate_string_implementation(**kwargs)
        elif operation == UtilityOperation.CREATE_SUCCESS_RESPONSE:
            result = _create_success_response_implementation(**kwargs)
        elif operation == UtilityOperation.CREATE_ERROR_RESPONSE:
            result = _create_error_response_implementation(**kwargs)
        elif operation == UtilityOperation.SANITIZE_DATA:
            result = _sanitize_data_implementation(**kwargs)
        elif operation == UtilityOperation.GET_TIMESTAMP:
            result = _get_timestamp_implementation(**kwargs)
        elif operation == UtilityOperation.DETECT_CIRCULAR_IMPORTS:
            result = _detect_circular_imports_implementation(**kwargs)
        elif operation == UtilityOperation.VALIDATE_IMPORT_ARCHITECTURE:
            result = _validate_import_architecture_implementation(**kwargs)
        elif operation == UtilityOperation.MONITOR_IMPORTS_RUNTIME:
            result = _monitor_imports_runtime_implementation(**kwargs)
        elif operation == UtilityOperation.APPLY_IMMEDIATE_FIXES:
            result = _apply_immediate_fixes_implementation(**kwargs)
        elif operation == UtilityOperation.VALIDATE_INPUT_CONFIGURATION:  # RENAMED
            result = _validate_input_configuration_implementation(**kwargs)
        else:
            result = _default_utility_operation(operation, **kwargs)
        
        # Cache successful results for import validation operations
        if result.get("success", True) and operation in [UtilityOperation.DETECT_CIRCULAR_IMPORTS, UtilityOperation.VALIDATE_IMPORT_ARCHITECTURE]:
            cache.cache_set(cache_key, result, ttl=UTILITY_CACHE_TTL)
        
        # Record metrics
        execution_time = time.time() - start_time
        metrics.record_metric("utility_execution_time", execution_time)
        metrics.record_metric("utility_operation_count", 1.0)
        
        return result
        
    except Exception as e:
        log_gateway.log_error(f"Utility operation failed: {operation.value}", {
            "correlation_id": correlation_id if 'correlation_id' in locals() else "unknown",
            "error": str(e)
        })
        
        return {"success": False, "error": str(e), "type": "utility_error"}

# ===== SECTION 4: CORE UTILITY IMPLEMENTATIONS =====

def _validate_string_implementation(**kwargs) -> Dict[str, Any]:
    """Validate string input using security gateway."""
    value = kwargs.get("value", "")
    min_length = kwargs.get("min_length", 0)
    max_length = kwargs.get("max_length", 1000)
    
    try:
        if not isinstance(value, str):
            return {"valid": False, "error": "Value must be a string"}
        
        if len(value) < min_length:
            return {"valid": False, "error": f"String too short (minimum {min_length})"}
        
        if len(value) > max_length:
            return {"valid": False, "error": f"String too long (maximum {max_length})"}
        
        # Use security gateway for additional validation
        security_result = security.validate_input({"value": value}, input_type="string")
        
        return {
            "valid": security_result.get("valid", True),
            "length": len(value),
            "security_validated": True
        }
        
    except Exception as e:
        return {"valid": False, "error": f"Validation failed: {str(e)}"}

def _create_success_response_implementation(**kwargs) -> Dict[str, Any]:
    """Create success response using utility patterns."""
    message = kwargs.get("message", "Operation completed successfully")
    data = kwargs.get("data")
    
    try:
        response = {
            "success": True,
            "message": str(message),
            "timestamp": _get_timestamp_value(),
            "correlation_id": _generate_correlation_id_core()
        }
        
        if data is not None:
            response["data"] = data
        
        return response
        
    except Exception as e:
        return {"success": False, "error": f"Response creation failed: {str(e)}"}

def _create_error_response_implementation(**kwargs) -> Dict[str, Any]:
    """Create error response using utility patterns."""
    message = kwargs.get("message", "An error occurred")
    error_code = kwargs.get("error_code", "GENERIC_ERROR")
    
    try:
        return {
            "success": False,
            "error": {
                "message": str(message),
                "code": str(error_code),
                "timestamp": _get_timestamp_value()
            },
            "correlation_id": _generate_correlation_id_core()
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": {
                "message": "Error response creation failed",
                "code": "RESPONSE_ERROR"
            }
        }

def _sanitize_data_implementation(**kwargs) -> Dict[str, Any]:
    """Sanitize data using security gateway."""
    data = kwargs.get("data", {})
    
    try:
        # Use security gateway for data sanitization
        sanitized = security.sanitize_sensitive_data(data)
        
        return {
            "success": True,
            "sanitized_data": sanitized,
            "sanitization_applied": True
        }
        
    except Exception as e:
        return {"success": False, "error": f"Sanitization failed: {str(e)}"}

def _get_timestamp_implementation(**kwargs) -> Dict[str, Any]:
    """Get current timestamp."""
    try:
        timestamp = _get_timestamp_value()
        return {
            "success": True,
            "timestamp": timestamp,
            "format": "ISO8601"
        }
        
    except Exception as e:
        return {"success": False, "error": f"Timestamp generation failed: {str(e)}"}

# ===== SECTION 5: IMPORT VALIDATION IMPLEMENTATIONS =====

def _detect_circular_imports_implementation(**kwargs) -> Dict[str, Any]:
    """Detect circular imports using utility_import_validation."""
    project_path = kwargs.get("project_path", ".")
    
    try:
        # Import the validation module
        from .utility_import_validation import detect_circular_imports
        
        # Execute detection
        result = detect_circular_imports(project_path)
        
        # Add metadata
        result["operation"] = "detect_circular_imports"
        result["timestamp"] = _get_timestamp_value()
        result["correlation_id"] = _generate_correlation_id_core()
        
        return result
        
    except Exception as e:
        log_gateway.log_error(f"Circular import detection failed: {str(e)}")
        return {
            "circular_imports_detected": False,
            "error": str(e),
            "operation": "detect_circular_imports",
            "timestamp": _get_timestamp_value()
        }

def _validate_import_architecture_implementation(**kwargs) -> Dict[str, Any]:
    """Validate import architecture using utility_import_validation."""
    project_path = kwargs.get("project_path", ".")
    
    try:
        from .utility_import_validation import validate_import_architecture
        
        result = validate_import_architecture(project_path)
        
        result["operation"] = "validate_import_architecture"
        result["timestamp"] = _get_timestamp_value()
        result["correlation_id"] = _generate_correlation_id_core()
        
        return result
        
    except Exception as e:
        log_gateway.log_error(f"Import architecture validation failed: {str(e)}")
        return {
            "architecture_valid": False,
            "error": str(e),
            "operation": "validate_import_architecture",
            "timestamp": _get_timestamp_value()
        }

def _monitor_imports_runtime_implementation(**kwargs) -> Dict[str, Any]:
    """Monitor imports at runtime using utility_import_validation."""
    try:
        from .utility_import_validation import monitor_imports_runtime
        
        result = monitor_imports_runtime()
        
        result["operation"] = "monitor_imports_runtime"
        result["timestamp"] = _get_timestamp_value()
        result["correlation_id"] = _generate_correlation_id_core()
        
        return result
        
    except Exception as e:
        log_gateway.log_error(f"Runtime import monitoring failed: {str(e)}")
        return {
            "monitoring_active": False,
            "error": str(e),
            "operation": "monitor_imports_runtime",
            "timestamp": _get_timestamp_value()
        }

def _apply_immediate_fixes_implementation(**kwargs) -> Dict[str, Any]:
    """Apply immediate fixes using utility_import_validation."""
    try:
        from .utility_import_validation import apply_immediate_fixes
        
        result = apply_immediate_fixes()
        
        result["operation"] = "apply_immediate_fixes"
        result["timestamp"] = _get_timestamp_value()
        result["correlation_id"] = _generate_correlation_id_core()
        
        return result
        
    except Exception as e:
        log_gateway.log_error(f"Immediate fixes application failed: {str(e)}")
        return {
            "fixes_applied": False,
            "error": str(e),
            "operation": "apply_immediate_fixes",
            "timestamp": _get_timestamp_value()
        }

def _validate_input_configuration_implementation(**kwargs) -> Dict[str, Any]:
    """
    Validate input-level configuration data structures.
    RENAMED from validate_configuration - handles basic input validation only.
    For system-level configuration validation, use debug.py functions.
    """
    config_data = kwargs.get("config_data", {})
    
    try:
        # Basic input validation
        if not isinstance(config_data, dict):
            return {
                "valid": False,
                "error": "Configuration must be a dictionary",
                "timestamp": _get_timestamp_value()
            }
        
        # Validate required structure using security gateway
        validation_result = security.validate_input(config_data, input_type="config")
        
        return {
            "valid": validation_result.get("valid", True),
            "validation_type": "input_configuration",
            "timestamp": _get_timestamp_value(),
            "note": "For system configuration validation, use debug.validate_system_configuration()"
        }
        
    except Exception as e:
        return {
            "valid": False,
            "error": f"Input configuration validation failed: {str(e)}",
            "timestamp": _get_timestamp_value()
        }

# ===== SECTION 6: HELPER FUNCTIONS =====

def _generate_correlation_id_core() -> str:
    """Generate unique correlation ID."""
    return f"util-{int(time.time() * 1000)}-{str(uuid.uuid4())[:8]}"

def _get_timestamp_value() -> str:
    """Get ISO8601 timestamp."""
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat()

def _default_utility_operation(operation: UtilityOperation, **kwargs) -> Dict[str, Any]:
    """Handle unknown operations."""
    return {
        "success": False,
        "error": f"Unknown utility operation: {operation.value}",
        "operation": operation.value,
        "timestamp": _get_timestamp_value()
    }

# EOF
