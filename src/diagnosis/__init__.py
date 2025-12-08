"""
diagnosis/__init__.py
Version: 2025-12-08_1
Purpose: DIAGNOSIS interface package exports
License: Apache 2.0
"""

from diagnosis.diagnosis_imports import (
    test_module_import,
    test_import_sequence,
    format_diagnostic_response,
    diagnose_import_failure
)

from diagnosis.diagnosis_performance import (
    diagnose_system_health,
    diagnose_component_performance,
    diagnose_memory_usage,
    diagnose_initialization_performance,
    diagnose_utility_performance,
    diagnose_singleton_performance
)

from diagnosis.diagnosis_core import (
    validate_system_architecture,
    validate_imports,
    validate_gateway_routing,
    run_diagnostic_suite
)

from diagnosis.health import (
    check_component_health,
    check_gateway_health,
    generate_health_report,
    check_initialization_health,
    check_utility_health,
    check_singleton_health,
    check_system_health
)

__all__ = [
    'test_module_import',
    'test_import_sequence',
    'format_diagnostic_response',
    'diagnose_import_failure',
    'diagnose_system_health',
    'diagnose_component_performance',
    'diagnose_memory_usage',
    'diagnose_initialization_performance',
    'diagnose_utility_performance',
    'diagnose_singleton_performance',
    'validate_system_architecture',
    'validate_imports',
    'validate_gateway_routing',
    'run_diagnostic_suite',
    'check_component_health',
    'check_gateway_health',
    'generate_health_report',
    'check_initialization_health',
    'check_utility_health',
    'check_singleton_health',
    'check_system_health'
]
