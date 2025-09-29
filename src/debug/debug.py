"""
debug.py - Debug, Testing, and Validation Primary Gateway Interface
Version: 2025.09.28.01
Description: Ultra-pure gateway for debug operations - pure delegation only

ARCHITECTURE: PRIMARY GATEWAY INTERFACE - SPECIAL STATUS
- Function declarations ONLY - no implementation code
- Pure delegation to debug_core.py, debug_test.py, debug_validation.py, debug_troubleshooting.py
- External access point for all debug, testing, validation, and troubleshooting operations
- Ultra-optimized for 128MB Lambda constraint
- Special status as central debug repository (similar to config.py)

GATEWAY FUNCTIONS OVERVIEW:
- Testing Operations: Comprehensive testing, interface testing, integration testing, performance testing
- Validation Operations: System architecture validation, AWS constraints, gateway compliance, configuration validation
- Troubleshooting Operations: System health diagnosis, performance analysis, resource problem detection, diagnostic reporting
- Debug Coordination: Full system debug, debug mode management, debug configuration

PRIMARY GATEWAY FUNCTIONS:
- run_comprehensive_tests() - Execute comprehensive system-wide tests
- run_interface_tests() - Test specific gateway interface functionality
- run_integration_tests() - Run integration workflows across interfaces
- run_performance_tests() - Execute performance benchmarking tests
- get_test_results() - Retrieve stored test results and analysis
- validate_system_architecture() - Validate architecture compliance against PROJECT_ARCHITECTURE_REFERENCE.md
- validate_aws_constraints() - Validate AWS Lambda constraint compliance
- validate_gateway_compliance() - Validate gateway pattern compliance
- validate_configuration() - Validate configuration schema and data integrity
- get_validation_status() - Retrieve validation results and status
- diagnose_system_health() - Comprehensive system health diagnosis
- analyze_performance_issues() - Detect and analyze performance bottlenecks
- detect_resource_problems() - Detect memory leaks and resource issues
- generate_diagnostic_report() - Generate comprehensive diagnostic reports
- get_troubleshooting_recommendations() - Get prioritized troubleshooting recommendations
- run_full_system_debug() - Execute complete system debug analysis
- get_debug_status() - Get current debug system status
- enable_debug_mode() - Enable detailed debug mode with enhanced logging
- disable_debug_mode() - Disable debug mode and return to normal operation
- get_debug_configuration() - Get current debug configuration and settings

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

from typing import Dict, Any, List, Optional
from .debug_core import generic_debug_operation, DebugOperation

# ===== SECTION 1: TESTING OPERATIONS GATEWAY =====

def run_comprehensive_tests(test_suite: str = "all", parallel: bool = True, max_workers: int = 4) -> Dict[str, Any]:
    """
    Primary gateway function for comprehensive system-wide testing.
    Pure delegation to debug_core implementation.
    
    Args:
        test_suite: Test suite to run ("all", "interfaces", "integration", "performance")
        parallel: Whether to run tests in parallel
        max_workers: Maximum number of parallel workers
        
    Returns:
        Comprehensive test results with summary and recommendations
    """
    return generic_debug_operation(
        DebugOperation.RUN_COMPREHENSIVE_TESTS,
        test_suite=test_suite,
        parallel=parallel,
        max_workers=max_workers
    )

def run_interface_tests(interface_name: str = "all", test_types: List[str] = None) -> Dict[str, Any]:
    """
    Primary gateway function for interface-specific testing.
    Pure delegation to debug_test implementation.
    
    Args:
        interface_name: Interface to test ("cache", "security", "logging", etc. or "all")
        test_types: Types of tests to run (["functionality", "performance", "memory"])
        
    Returns:
        Interface test results with performance metrics and compliance status
    """
    if test_types is None:
        test_types = ["functionality", "performance", "memory"]
        
    return generic_debug_operation(
        DebugOperation.RUN_INTERFACE_TESTS,
        interface_name=interface_name,
        test_types=test_types
    )

def run_integration_tests(workflows: List[str] = None) -> Dict[str, Any]:
    """
    Primary gateway function for integration workflow testing.
    Pure delegation to debug_test implementation.
    
    Args:
        workflows: Integration workflows to test (["end_to_end", "gateway_compliance", "memory_constraints"])
        
    Returns:
        Integration test results with workflow analysis and compliance metrics
    """
    if workflows is None:
        workflows = ["end_to_end", "gateway_compliance", "memory_constraints"]
        
    return generic_debug_operation(
        DebugOperation.RUN_INTEGRATION_TESTS,
        workflows=workflows
    )

def run_performance_tests(benchmark_types: List[str] = None, iterations: int = 100) -> Dict[str, Any]:
    """
    Primary gateway function for performance benchmarking.
    Pure delegation to debug_test implementation.
    
    Args:
        benchmark_types: Types of benchmarks to run (["response_time", "memory_usage", "throughput"])
        iterations: Number of iterations for each benchmark
        
    Returns:
        Performance benchmark results with statistical analysis and recommendations
    """
    if benchmark_types is None:
        benchmark_types = ["response_time", "memory_usage", "throughput"]
        
    return generic_debug_operation(
        DebugOperation.RUN_PERFORMANCE_TESTS,
        benchmark_types=benchmark_types,
        iterations=iterations
    )

def get_test_results(test_category: str = "all", limit: int = 100) -> Dict[str, Any]:
    """
    Primary gateway function for retrieving test results.
    Pure delegation to debug_core implementation.
    
    Args:
        test_category: Category of tests to retrieve ("all", "comprehensive", "interface", "integration")
        limit: Maximum number of results to return
        
    Returns:
        Stored test results with filtering and analysis
    """
    return generic_debug_operation(
        DebugOperation.GET_TEST_RESULTS,
        test_category=test_category,
        limit=limit
    )

# ===== SECTION 2: VALIDATION OPERATIONS GATEWAY =====

def validate_system_architecture(project_path: str = ".", checks: List[str] = None) -> Dict[str, Any]:
    """
    Primary gateway function for system architecture validation.
    Pure delegation to debug_validation implementation.
    
    Args:
        project_path: Path to project directory for analysis
        checks: Architecture checks to perform (["gateway_pattern", "import_dependencies", "file_structure"])
        
    Returns:
        Architecture compliance results with detailed analysis and recommendations
    """
    if checks is None:
        checks = ["gateway_pattern", "import_dependencies", "file_structure"]
        
    return generic_debug_operation(
        DebugOperation.VALIDATE_SYSTEM_ARCHITECTURE,
        project_path=project_path,
        checks=checks
    )

def validate_aws_constraints(constraints: List[str] = None) -> Dict[str, Any]:
    """
    Primary gateway function for AWS Lambda constraint validation.
    Pure delegation to debug_validation implementation.
    
    Args:
        constraints: AWS constraints to validate (["memory_limits", "execution_time", "cost_protection"])
        
    Returns:
        AWS constraint compliance results with optimization recommendations
    """
    if constraints is None:
        constraints = ["memory_limits", "execution_time", "cost_protection"]
        
    return generic_debug_operation(
        DebugOperation.VALIDATE_AWS_CONSTRAINTS,
        constraints=constraints
    )

def validate_gateway_compliance(interfaces: List[str] = None) -> Dict[str, Any]:
    """
    Primary gateway function for gateway pattern compliance validation.
    Pure delegation to debug_validation implementation.
    
    Args:
        interfaces: Interfaces to validate (["cache", "security", "logging", etc.] or ["all"])
        
    Returns:
        Gateway compliance results with pattern analysis and scoring
    """
    if interfaces is None:
        interfaces = ["all"]
        
    return generic_debug_operation(
        DebugOperation.VALIDATE_GATEWAY_COMPLIANCE,
        interfaces=interfaces
    )

def validate_configuration(validation_types: List[str] = None) -> Dict[str, Any]:
    """
    Primary gateway function for configuration validation.
    Pure delegation to debug_validation implementation.
    
    Args:
        validation_types: Types of validation to perform (["schema", "security", "aws_constraints"])
        
    Returns:
        Configuration validation results with compliance status and recommendations
    """
    if validation_types is None:
        validation_types = ["schema", "security", "aws_constraints"]
        
    return generic_debug_operation(
        DebugOperation.VALIDATE_CONFIGURATION,
        validation_types=validation_types
    )

def get_validation_status(validation_category: str = "all") -> Dict[str, Any]:
    """
    Primary gateway function for retrieving validation status.
    Pure delegation to debug_core implementation.
    
    Args:
        validation_category: Category of validations to retrieve ("all", "architecture", "aws", "gateway")
        
    Returns:
        Current validation status with historical trends and compliance metrics
    """
    return generic_debug_operation(
        DebugOperation.GET_VALIDATION_STATUS,
        validation_category=validation_category
    )

# ===== SECTION 3: TROUBLESHOOTING OPERATIONS GATEWAY =====

def diagnose_system_health() -> Dict[str, Any]:
    """
    Primary gateway function for system health diagnosis.
    Pure delegation to debug_troubleshooting implementation.
    
    Returns:
        Comprehensive system health analysis with status, metrics, and recommendations
    """
    return generic_debug_operation(
        DebugOperation.DIAGNOSE_SYSTEM_HEALTH
    )

def analyze_performance_issues() -> Dict[str, Any]:
    """
    Primary gateway function for performance issue analysis.
    Pure delegation to debug_troubleshooting implementation.
    
    Returns:
        Performance bottleneck analysis with impact assessment and optimization recommendations
    """
    return generic_debug_operation(
        DebugOperation.ANALYZE_PERFORMANCE_ISSUES
    )

def detect_resource_problems() -> Dict[str, Any]:
    """
    Primary gateway function for resource problem detection.
    Pure delegation to debug_troubleshooting implementation.
    
    Returns:
        Resource analysis including memory leaks, usage trends, and optimization recommendations
    """
    return generic_debug_operation(
        DebugOperation.DETECT_RESOURCE_PROBLEMS
    )

def generate_diagnostic_report() -> Dict[str, Any]:
    """
    Primary gateway function for comprehensive diagnostic report generation.
    Pure delegation to debug_troubleshooting implementation.
    
    Returns:
        Executive diagnostic report with comprehensive analysis and actionable recommendations
    """
    return generic_debug_operation(
        DebugOperation.GENERATE_DIAGNOSTIC_REPORT
    )

def get_troubleshooting_recommendations() -> Dict[str, Any]:
    """
    Primary gateway function for troubleshooting recommendations.
    Pure delegation to debug_troubleshooting implementation.
    
    Returns:
        Prioritized list of troubleshooting recommendations based on current system state
    """
    return generic_debug_operation(
        DebugOperation.GET_TROUBLESHOOTING_RECOMMENDATIONS
    )

# ===== SECTION 4: DEBUG COORDINATION GATEWAY =====

def run_full_system_debug(include_tests: bool = True, include_validation: bool = True, include_diagnostics: bool = True) -> Dict[str, Any]:
    """
    Primary gateway function for complete system debug analysis.
    Pure delegation to debug_core implementation.
    
    Args:
        include_tests: Whether to include comprehensive testing
        include_validation: Whether to include validation checks
        include_diagnostics: Whether to include diagnostic analysis
        
    Returns:
        Complete system debug results with executive summary and comprehensive recommendations
    """
    return generic_debug_operation(
        DebugOperation.RUN_FULL_SYSTEM_DEBUG,
        include_tests=include_tests,
        include_validation=include_validation,
        include_diagnostics=include_diagnostics
    )

def get_debug_status() -> Dict[str, Any]:
    """
    Primary gateway function for debug system status.
    Pure delegation to debug_core implementation.
    
    Returns:
        Current debug system status including mode, configuration, and recent activity
    """
    return generic_debug_operation(
        DebugOperation.GET_DEBUG_STATUS
    )

def enable_debug_mode(debug_level: str = "standard") -> Dict[str, Any]:
    """
    Primary gateway function for enabling debug mode.
    Pure delegation to debug_core implementation.
    
    Args:
        debug_level: Debug level to enable ("minimal", "standard", "verbose", "comprehensive")
        
    Returns:
        Debug mode activation result with configuration details
    """
    return generic_debug_operation(
        DebugOperation.ENABLE_DEBUG_MODE,
        debug_level=debug_level
    )

def disable_debug_mode() -> Dict[str, Any]:
    """
    Primary gateway function for disabling debug mode.
    Pure delegation to debug_core implementation.
    
    Returns:
        Debug mode deactivation result with cleanup status
    """
    return generic_debug_operation(
        DebugOperation.DISABLE_DEBUG_MODE
    )

def get_debug_configuration() -> Dict[str, Any]:
    """
    Primary gateway function for debug configuration retrieval.
    Pure delegation to debug_core implementation.
    
    Returns:
        Current debug configuration including settings, thresholds, and operational parameters
    """
    return generic_debug_operation(
        DebugOperation.GET_DEBUG_CONFIGURATION
    )

# ===== SECTION 5: MODULE EXPORTS =====

__all__ = [
    # Testing Operations
    'run_comprehensive_tests',
    'run_interface_tests',
    'run_integration_tests',
    'run_performance_tests',
    'get_test_results',
    
    # Validation Operations
    'validate_system_architecture',
    'validate_aws_constraints',
    'validate_gateway_compliance',
    'validate_configuration',
    'get_validation_status',
    
    # Troubleshooting Operations
    'diagnose_system_health',
    'analyze_performance_issues',
    'detect_resource_problems',
    'generate_diagnostic_report',
    'get_troubleshooting_recommendations',
    
    # Debug Coordination
    'run_full_system_debug',
    'get_debug_status',
    'enable_debug_mode',
    'disable_debug_mode',
    'get_debug_configuration'
]

# EOF
