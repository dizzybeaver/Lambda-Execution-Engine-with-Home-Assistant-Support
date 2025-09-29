"""
debug.py - Debug, Testing, and Validation Primary Gateway Interface - COMPLETE IMPLEMENTATION
Version: 2025.09.28.03
Description: Ultra-pure gateway for debug operations - pure delegation only

CORRECTIONS APPLIED (2025.09.28.03):
- ✅ RENAMED: validate_configuration → validate_system_configuration (clarifies system-level validation)
- ✅ ADDED: get_system_diagnostic_info (comprehensive system diagnostics)
- ✅ CLARIFIED: Debug handles system-level operations, utility handles input-level operations

ARCHITECTURE: PRIMARY GATEWAY INTERFACE - SPECIAL STATUS
- Function declarations ONLY - no implementation code
- Pure delegation to debug_core.py, debug_test.py, debug_validation.py, debug_troubleshooting.py
- External access point for all debug, testing, validation, and troubleshooting operations
- Ultra-optimized for 128MB Lambda constraint
- Special status as central debug repository (similar to config.py)

GATEWAY FUNCTIONS OVERVIEW:
- Testing Operations: Comprehensive testing, interface testing, integration testing, performance testing
- Validation Operations: System architecture validation, AWS constraints, gateway compliance, system configuration validation
- Troubleshooting Operations: System health diagnosis, performance analysis, resource problem detection, diagnostic reporting
- Debug Coordination: Full system debug, debug mode management, debug configuration
- Integration Operations: Cross-interface testing, migration coordination, unified test running
- Automation Operations: Continuous validation, intelligent diagnostics, automated optimization
- Reporting Operations: Comprehensive reporting, real-time monitoring, analytics dashboard

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

from typing import Dict, Any, List, Optional, Callable
from .debug_core import get_debug_coordinator, DebugOperation

# ===== SECTION 1: SINGLETON ACCESSOR =====

def _get_debug_coordinator():
    """Get debug coordinator singleton instance."""
    return get_debug_coordinator()

# ===== SECTION 2: TESTING OPERATIONS GATEWAY =====

def run_comprehensive_tests(test_scope: str = "all",
                           test_depth: str = "standard",
                           parallel_execution: bool = False) -> Dict[str, Any]:
    """Run comprehensive system tests across all interfaces and components."""
    coordinator = _get_debug_coordinator()
    return coordinator.execute_debug_operation(
        DebugOperation.RUN_COMPREHENSIVE_TESTS,
        test_scope=test_scope,
        test_depth=test_depth,
        parallel_execution=parallel_execution
    )

def run_interface_tests(interface_name: str,
                       test_categories: List[str] = None,
                       validation_level: str = "standard") -> Dict[str, Any]:
    """Run tests for a specific interface with configurable validation levels."""
    coordinator = _get_debug_coordinator()
    return coordinator.execute_debug_operation(
        DebugOperation.RUN_INTERFACE_TESTS,
        interface_name=interface_name,
        test_categories=test_categories or ["functionality", "performance", "security"],
        validation_level=validation_level
    )

def run_integration_tests(integration_scope: str = "cross_interface",
                         mock_external: bool = True,
                         timeout_seconds: int = 30) -> Dict[str, Any]:
    """Run integration tests to validate cross-interface coordination and communication."""
    coordinator = _get_debug_coordinator()
    return coordinator.execute_debug_operation(
        DebugOperation.RUN_INTEGRATION_TESTS,
        integration_scope=integration_scope,
        mock_external=mock_external,
        timeout_seconds=timeout_seconds
    )

def run_performance_tests(performance_scope: str = "system_wide",
                         load_level: str = "standard",
                         benchmark_comparison: bool = True) -> Dict[str, Any]:
    """Run performance tests with benchmarking and load testing capabilities."""
    coordinator = _get_debug_coordinator()
    return coordinator.execute_debug_operation(
        DebugOperation.RUN_PERFORMANCE_TESTS,
        performance_scope=performance_scope,
        load_level=load_level,
        benchmark_comparison=benchmark_comparison
    )

def get_test_results(result_filter: str = "all",
                    result_format: str = "summary",
                    include_history: bool = False) -> Dict[str, Any]:
    """Retrieve test results with flexible filtering and formatting options."""
    coordinator = _get_debug_coordinator()
    return coordinator.execute_debug_operation(
        DebugOperation.GET_TEST_RESULTS,
        result_filter=result_filter,
        result_format=result_format,
        include_history=include_history
    )

# ===== SECTION 3: VALIDATION OPERATIONS GATEWAY =====

def validate_system_architecture(validation_depth: str = "comprehensive",
                                strict_mode: bool = True,
                                generate_report: bool = False) -> Dict[str, Any]:
    """
    Validate system architecture against design patterns and best practices.
    RENAMED from validate_architecture - handles comprehensive system validation.
    """
    coordinator = _get_debug_coordinator()
    return coordinator.execute_debug_operation(
        DebugOperation.VALIDATE_SYSTEM_ARCHITECTURE,
        validation_depth=validation_depth,
        strict_mode=strict_mode,
        generate_report=generate_report
    )

def validate_aws_constraints(constraint_scope: str = "all",
                            include_recommendations: bool = True,
                            projection_analysis: bool = False) -> Dict[str, Any]:
    """Validate compliance with AWS Lambda 128MB and CloudWatch 10-metric constraints."""
    coordinator = _get_debug_coordinator()
    return coordinator.execute_debug_operation(
        DebugOperation.VALIDATE_AWS_CONSTRAINTS,
        constraint_scope=constraint_scope,
        include_recommendations=include_recommendations,
        projection_analysis=projection_analysis
    )

def validate_gateway_compliance(gateway_name: str = "all",
                               compliance_level: str = "strict",
                               audit_trail: bool = False) -> Dict[str, Any]:
    """Validate gateway interface compliance with architectural standards."""
    coordinator = _get_debug_coordinator()
    return coordinator.execute_debug_operation(
        DebugOperation.VALIDATE_GATEWAY_COMPLIANCE,
        gateway_name=gateway_name,
        compliance_level=compliance_level,
        audit_trail=audit_trail
    )

def validate_system_configuration(config_scope: str = "complete",
                                 validation_level: str = "thorough",
                                 auto_correct: bool = False) -> Dict[str, Any]:
    """
    Validate system-level configuration (architecture, AWS compliance, gateway patterns).
    RENAMED from validate_configuration - handles comprehensive system validation.
    For input-level configuration validation, use utility.validate_input_configuration().
    """
    coordinator = _get_debug_coordinator()
    return coordinator.execute_debug_operation(
        DebugOperation.VALIDATE_SYSTEM_CONFIGURATION,
        config_scope=config_scope,
        validation_level=validation_level,
        auto_correct=auto_correct
    )

def get_validation_status(status_scope: str = "all",
                         include_history: bool = False,
                         aggregate_metrics: bool = True) -> Dict[str, Any]:
    """Get validation status with historical data and aggregated metrics."""
    coordinator = _get_debug_coordinator()
    return coordinator.execute_debug_operation(
        DebugOperation.GET_VALIDATION_STATUS,
        status_scope=status_scope,
        include_history=include_history,
        aggregate_metrics=aggregate_metrics
    )

# ===== SECTION 4: TROUBLESHOOTING OPERATIONS GATEWAY =====

def diagnose_system_health(diagnostic_depth: str = "comprehensive",
                          real_time_analysis: bool = True,
                          predictive_insights: bool = False) -> Dict[str, Any]:
    """Diagnose system health with real-time analysis and predictive insights."""
    coordinator = _get_debug_coordinator()
    return coordinator.execute_debug_operation(
        DebugOperation.DIAGNOSE_SYSTEM_HEALTH,
        diagnostic_depth=diagnostic_depth,
        real_time_analysis=real_time_analysis,
        predictive_insights=predictive_insights
    )

def analyze_performance_issues(analysis_scope: str = "system_wide",
                              issue_threshold: str = "warning",
                              root_cause_analysis: bool = True) -> Dict[str, Any]:
    """Analyze performance issues with root cause analysis and recommendations."""
    coordinator = _get_debug_coordinator()
    return coordinator.execute_debug_operation(
        DebugOperation.ANALYZE_PERFORMANCE_ISSUES,
        analysis_scope=analysis_scope,
        issue_threshold=issue_threshold,
        root_cause_analysis=root_cause_analysis
    )

def detect_resource_problems(resource_type: str = "all",
                            detection_sensitivity: str = "standard",
                            proactive_alerts: bool = True) -> Dict[str, Any]:
    """Detect resource problems (memory, metrics, cache) with proactive alerting."""
    coordinator = _get_debug_coordinator()
    return coordinator.execute_debug_operation(
        DebugOperation.DETECT_RESOURCE_PROBLEMS,
        resource_type=resource_type,
        detection_sensitivity=detection_sensitivity,
        proactive_alerts=proactive_alerts
    )

def generate_diagnostic_report(report_scope: str = "comprehensive",
                              report_format: str = "detailed",
                              include_visualizations: bool = False) -> Dict[str, Any]:
    """Generate comprehensive diagnostic report with optional visualizations."""
    coordinator = _get_debug_coordinator()
    return coordinator.execute_debug_operation(
        DebugOperation.GENERATE_DIAGNOSTIC_REPORT,
        report_scope=report_scope,
        report_format=report_format,
        include_visualizations=include_visualizations
    )

def get_troubleshooting_recommendations(problem_category: str = "all",
                                       recommendation_depth: str = "detailed",
                                       prioritize_actions: bool = True) -> Dict[str, Any]:
    """Get troubleshooting recommendations with prioritized action items."""
    coordinator = _get_debug_coordinator()
    return coordinator.execute_debug_operation(
        DebugOperation.GET_TROUBLESHOOTING_RECOMMENDATIONS,
        problem_category=problem_category,
        recommendation_depth=recommendation_depth,
        prioritize_actions=prioritize_actions
    )

def get_system_diagnostic_info(diagnostic_level: str = "standard",
                               include_cache: bool = True,
                               include_performance: bool = True) -> Dict[str, Any]:
    """
    Get comprehensive system diagnostic information.
    NEW: Consolidated from utility per debug.py special status for diagnostics.
    """
    coordinator = _get_debug_coordinator()
    return coordinator.execute_debug_operation(
        DebugOperation.GET_SYSTEM_DIAGNOSTIC_INFO,
        diagnostic_level=diagnostic_level,
        include_cache=include_cache,
        include_performance=include_performance
    )

# ===== SECTION 5: DEBUG COORDINATION GATEWAY =====

def run_full_system_debug(debug_level: str = "comprehensive",
                         include_automation: bool = True,
                         generate_reports: bool = True) -> Dict[str, Any]:
    """Run full system debug with automation and comprehensive reporting."""
    coordinator = _get_debug_coordinator()
    return coordinator.execute_debug_operation(
        DebugOperation.RUN_FULL_SYSTEM_DEBUG,
        debug_level=debug_level,
        include_automation=include_automation,
        generate_reports=generate_reports
    )

def get_debug_status(status_detail: str = "summary",
                    include_metrics: bool = True,
                    real_time_data: bool = True) -> Dict[str, Any]:
    """Get current debug system status with real-time metrics."""
    coordinator = _get_debug_coordinator()
    return coordinator.execute_debug_operation(
        DebugOperation.GET_DEBUG_STATUS,
        status_detail=status_detail,
        include_metrics=include_metrics,
        real_time_data=real_time_data
    )

def enable_debug_mode(debug_level: str = "standard",
                     enhanced_logging: bool = True,
                     performance_monitoring: bool = True) -> Dict[str, Any]:
    """Enable detailed debug mode with enhanced logging and monitoring."""
    coordinator = _get_debug_coordinator()
    return coordinator.execute_debug_operation(
        DebugOperation.ENABLE_DEBUG_MODE,
        debug_level=debug_level,
        enhanced_logging=enhanced_logging,
        performance_monitoring=performance_monitoring
    )

def disable_debug_mode(preserve_data: bool = True,
                      generate_summary: bool = True) -> Dict[str, Any]:
    """Disable debug mode and return to normal operation with optional summary."""
    coordinator = _get_debug_coordinator()
    return coordinator.execute_debug_operation(
        DebugOperation.DISABLE_DEBUG_MODE,
        preserve_data=preserve_data,
        generate_summary=generate_summary
    )

def get_debug_configuration(config_scope: str = "complete",
                           include_recommendations: bool = False) -> Dict[str, Any]:
    """Get current debug configuration and settings with optimization recommendations."""
    coordinator = _get_debug_coordinator()
    return coordinator.execute_debug_operation(
        DebugOperation.GET_DEBUG_CONFIGURATION,
        config_scope=config_scope,
        include_recommendations=include_recommendations
    )

# ===== MODULE EXPORTS =====

__all__ = [
    # Testing operations
    'run_comprehensive_tests',
    'run_interface_tests',
    'run_integration_tests',
    'run_performance_tests',
    'get_test_results',
    
    # Validation operations (system-level)
    'validate_system_architecture',
    'validate_aws_constraints',
    'validate_gateway_compliance',
    'validate_system_configuration',  # RENAMED
    'get_validation_status',
    
    # Troubleshooting operations
    'diagnose_system_health',
    'analyze_performance_issues',
    'detect_resource_problems',
    'generate_diagnostic_report',
    'get_troubleshooting_recommendations',
    'get_system_diagnostic_info',  # NEW
    
    # Debug coordination
    'run_full_system_debug',
    'get_debug_status',
    'enable_debug_mode',
    'disable_debug_mode',
    'get_debug_configuration'
]

# EOF
