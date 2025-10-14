"""
debug.py - Debug Gateway Interface
Version: 2025.10.14.01
Description: Debug gateway interface that delegates to debug_core.py dispatcher

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

from typing import Dict, Any
from debug_core import generic_debug_operation, DebugOperation


def execute_debug_operation(operation: DebugOperation, **kwargs) -> Dict[str, Any]:
    """
    Primary gateway function for debug operations.
    Pure delegation to debug_core implementation.
    """
    return generic_debug_operation(operation, **kwargs)


def health_check() -> Dict[str, Any]:
    """
    Primary gateway function for health checks.
    Pure delegation to debug_core implementation.
    """
    return generic_debug_operation(DebugOperation.CHECK_COMPONENT_HEALTH, component='all')


def diagnostics() -> Dict[str, Any]:
    """
    Primary gateway function for diagnostics.
    Pure delegation to debug_core implementation.
    """
    return generic_debug_operation(DebugOperation.DIAGNOSE_SYSTEM_HEALTH)


def run_tests(test_type: str = "comprehensive") -> Dict[str, Any]:
    """
    Primary gateway function for test execution.
    Pure delegation to debug_core implementation.
    """
    operation_map = {
        'performance': DebugOperation.RUN_PERFORMANCE_BENCHMARK,
        'validation': DebugOperation.VALIDATE_SYSTEM_ARCHITECTURE,
        'config': DebugOperation.RUN_CONFIG_UNIT_TESTS
    }
    
    operation = operation_map.get(test_type, DebugOperation.VALIDATE_SYSTEM_ARCHITECTURE)
    return generic_debug_operation(operation)


def analyze_system() -> Dict[str, Any]:
    """
    Primary gateway function for system analysis.
    Pure delegation to debug_core implementation.
    """
    return generic_debug_operation(DebugOperation.VALIDATE_SYSTEM_ARCHITECTURE)


__all__ = [
    'execute_debug_operation',
    'health_check',
    'diagnostics', 
    'run_tests',
    'analyze_system',
    'DebugOperation'
]

# EOF
