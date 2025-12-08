"""
interface_diagnosis.py
Version: 2025-12-08_1
Purpose: DIAGNOSIS interface router (INT-13)
License: Apache 2.0
"""

from typing import Any, Dict

_DIAGNOSIS_AVAILABLE = True
_DIAGNOSIS_IMPORT_ERROR = None

try:
    from diagnosis_imports import (
        test_module_import,
        test_import_sequence,
        format_diagnostic_response,
        diagnose_import_failure
    )
    from diagnosis_performance import (
        diagnose_system_health,
        diagnose_component_performance,
        diagnose_memory_usage,
        diagnose_initialization_performance,
        diagnose_utility_performance,
        diagnose_singleton_performance
    )
    from diagnosis_core import (
        validate_system_architecture,
        validate_imports,
        validate_gateway_routing,
        run_diagnostic_suite
    )
    from diagnosis_health_checks import (
        check_component_health,
        check_gateway_health,
        generate_health_report
    )
    from diagnosis_health_interface import (
        check_initialization_health,
        check_utility_health,
        check_singleton_health
    )
    from diagnosis_health_system import check_system_health
except ImportError as e:
    _DIAGNOSIS_AVAILABLE = False
    _DIAGNOSIS_IMPORT_ERROR = str(e)


_DISPATCH = {
    'test_module_import': test_module_import,
    'test_import_sequence': test_import_sequence,
    'format_diagnostic_response': format_diagnostic_response,
    'diagnose_import_failure': diagnose_import_failure,
    'diagnose_system_health': diagnose_system_health,
    'diagnose_component_performance': diagnose_component_performance,
    'diagnose_memory_usage': diagnose_memory_usage,
    'diagnose_initialization_performance': diagnose_initialization_performance,
    'diagnose_utility_performance': diagnose_utility_performance,
    'diagnose_singleton_performance': diagnose_singleton_performance,
    'validate_system_architecture': validate_system_architecture,
    'validate_imports': validate_imports,
    'validate_gateway_routing': validate_gateway_routing,
    'run_diagnostic_suite': run_diagnostic_suite,
    'check_component_health': check_component_health,
    'check_gateway_health': check_gateway_health,
    'generate_health_report': generate_health_report,
    'check_initialization_health': check_initialization_health,
    'check_utility_health': check_utility_health,
    'check_singleton_health': check_singleton_health,
    'check_system_health': check_system_health
} if _DIAGNOSIS_AVAILABLE else {}


def execute_diagnosis_operation(operation: str, **kwargs) -> Any:
    """Route diagnosis operations to core implementations."""
    if not _DIAGNOSIS_AVAILABLE:
        raise RuntimeError(f"DIAGNOSIS unavailable: {_DIAGNOSIS_IMPORT_ERROR}")
    
    handler = _DISPATCH.get(operation)
    if not handler:
        raise ValueError(f"Unknown diagnosis operation: {operation}")
    
    return handler(**kwargs)


__all__ = ['execute_diagnosis_operation']
