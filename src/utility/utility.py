"""
utility.py - ULTRA-PURE: Testing, Validation, and Debugging Gateway Interface
Version: 2025.09.26.01
Description: Pure delegation gateway for testing, validation, and debugging operations

ARCHITECTURE: PRIMARY GATEWAY - PURE DELEGATION ONLY
- utility.py (this file) = Gateway/Firewall - function declarations ONLY
- utility_core.py = Core utility implementation logic
- utility_validation.py = Data validation and testing utilities
- utility_debug.py = Debugging and diagnostic utilities

ULTRA-OPTIMIZED OPERATIONS:
- Data validation and sanitization
- Testing framework integration
- Debugging and diagnostic utilities
- Response formatting and correlation ID management

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

from typing import Dict, Any, Optional, Union, List
from enum import Enum

# Ultra-pure delegation imports
from .utility_core import (
    _validation_implementation,
    _testing_implementation,
    _debug_implementation,
    _response_formatting_implementation
)

# ===== SECTION 1: VALIDATION OPERATIONS =====

def validate_data(data: Any, validation_rules: Dict[str, Any]) -> Dict[str, Any]:
    """Validate data against rules - pure delegation to core."""
    return _validation_implementation(data, validation_rules)

def sanitize_input(data: Any, sanitization_level: str = "standard") -> Dict[str, Any]:
    """Sanitize input data - pure delegation to core."""
    from .utility_core import _sanitization_implementation
    return _sanitization_implementation(data, sanitization_level)

def validate_configuration(config: Dict[str, Any]) -> Dict[str, Any]:
    """Validate configuration - pure delegation to core."""
    from .utility_core import _config_validation_implementation
    return _config_validation_implementation(config)

# ===== SECTION 2: TESTING OPERATIONS =====

def run_health_check(component: str = "all") -> Dict[str, Any]:
    """Run system health check - pure delegation to core."""
    return _testing_implementation("health_check", component)

def run_performance_test(test_type: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Run performance test - pure delegation to core."""
    return _testing_implementation("performance", test_type, parameters)

def validate_system_state() -> Dict[str, Any]:
    """Validate system state - pure delegation to core."""
    return _testing_implementation("system_state")

# EOS

# ===== SECTION 3: DEBUGGING OPERATIONS =====

def generate_correlation_id() -> str:
    """Generate correlation ID - pure delegation to core."""
    return _debug_implementation("correlation_id")

def get_system_diagnostics() -> Dict[str, Any]:
    """Get system diagnostics - pure delegation to core."""
    return _debug_implementation("diagnostics")

def trace_operation(operation: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """Trace operation - pure delegation to core."""
    return _debug_implementation("trace", operation, context)

# ===== SECTION 4: RESPONSE FORMATTING OPERATIONS =====

def format_response(data: Any, format_type: str = "standard") -> Dict[str, Any]:
    """Format response - pure delegation to core."""
    return _response_formatting_implementation(data, format_type)

def create_error_response(error: Exception, correlation_id: str) -> Dict[str, Any]:
    """Create error response - pure delegation to core."""
    return _response_formatting_implementation("error", error, correlation_id)

def get_utility_statistics() -> Dict[str, Any]:
    """Get utility statistics - pure delegation to core."""
    from .utility_core import _utility_statistics_implementation
    return _utility_statistics_implementation()

# EOF
