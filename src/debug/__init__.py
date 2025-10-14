"""
debug/__init__.py - Debug Package Interface and Gateway
Version: 2025.10.14.01
Description: Debug package interface with gateway functions and shared enums

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

from enum import Enum
from typing import Dict, Any, Optional
import sys
import re
import gc
import time


class DebugOperation(Enum):
    """Debug operation types."""
    CHECK_COMPONENT_HEALTH = "check_component_health"
    CHECK_GATEWAY_HEALTH = "check_gateway_health"
    DIAGNOSE_SYSTEM_HEALTH = "diagnose_system_health"
    DIAGNOSE_PERFORMANCE = "diagnose_performance"
    DIAGNOSE_MEMORY = "diagnose_memory"
    VALIDATE_SYSTEM_ARCHITECTURE = "validate_system_architecture"
    VALIDATE_IMPORTS = "validate_imports"
    VALIDATE_GATEWAY_ROUTING = "validate_gateway_routing"
    GET_SYSTEM_STATS = "get_system_stats"
    GET_OPTIMIZATION_STATS = "get_optimization_stats"
    RUN_PERFORMANCE_BENCHMARK = "run_performance_benchmark"
    GENERATE_HEALTH_REPORT = "generate_health_report"
    VERIFY_REGISTRY_OPERATIONS = "verify_registry_operations"
    ANALYZE_NAMING_PATTERNS = "analyze_naming_patterns"
    GENERATE_VERIFICATION_REPORT = "generate_verification_report"
    RUN_CONFIG_UNIT_TESTS = "run_config_unit_tests"
    RUN_CONFIG_INTEGRATION_TESTS = "run_config_integration_tests"
    RUN_CONFIG_PERFORMANCE_TESTS = "run_config_performance_tests"
    RUN_CONFIG_COMPATIBILITY_TESTS = "run_config_compatibility_tests"
    RUN_CONFIG_GATEWAY_TESTS = "run_config_gateway_tests"
    GET_DISPATCHER_STATS = "get_dispatcher_stats"
    GET_OPERATION_METRICS = "get_operation_metrics"
    COMPARE_DISPATCHER_MODES = "compare_dispatcher_modes"
    GET_PERFORMANCE_REPORT = "get_performance_report"


# Import dispatcher after enum definition
from debug.debug_core import generic_debug_operation


# Gateway interface functions
def execute_debug_operation(operation: DebugOperation, **kwargs) -> Dict[str, Any]:
    """Primary gateway function for debug operations."""
    return generic_debug_operation(operation, **kwargs)


def health_check() -> Dict[str, Any]:
    """Primary gateway function for health checks."""
    return generic_debug_operation(DebugOperation.CHECK_COMPONENT_HEALTH, component='all')


def diagnostics() -> Dict[str, Any]:
    """Primary gateway function for diagnostics."""
    return generic_debug_operation(DebugOperation.DIAGNOSE_SYSTEM_HEALTH)


def run_tests(test_type: str = "comprehensive") -> Dict[str, Any]:
    """Primary gateway function for test execution."""
    operation_map = {
        'performance': DebugOperation.RUN_PERFORMANCE_BENCHMARK,
        'validation': DebugOperation.VALIDATE_SYSTEM_ARCHITECTURE,
        'config': DebugOperation.RUN_CONFIG_UNIT_TESTS
    }
    operation = operation_map.get(test_type, DebugOperation.VALIDATE_SYSTEM_ARCHITECTURE)
    return generic_debug_operation(operation)


def analyze_system() -> Dict[str, Any]:
    """Primary gateway function for system analysis."""
    return generic_debug_operation(DebugOperation.VALIDATE_SYSTEM_ARCHITECTURE)


__all__ = [
    'DebugOperation',
    'generic_debug_operation',
    'execute_debug_operation',
    'health_check',
    'diagnostics',
    'run_tests',
    'analyze_system',
    'Dict',
    'Any',
    'Optional',
    'sys',
    're',
    'gc',
    'time'
]

# EOF
