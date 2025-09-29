"""
debug.py - Debug, Testing, and Validation Primary Gateway Interface - INTEGRATED IMPLEMENTATION
Version: 2025.09.29.01
Description: Comprehensive testing, validation, and troubleshooting gateway with all functions integrated

INTEGRATIONS COMPLETED (2025.09.29.01):
- ✅ INTEGRATED: ultra_optimization_tester.py (29 tests across 6 interfaces)
- ✅ INTEGRATED: performance_benchmark.py (comprehensive benchmarking suite)
- ✅ INTEGRATED: gateway_utilization_validator.py (57 gateway functions tracked)
- ✅ INTEGRATED: legacy_elimination_patterns.py (7 legacy pattern types)
- ✅ INTEGRATED: debug_validation.py (architecture/config/security validators)
- ✅ INTEGRATED: config_testing.py (configuration system test suite)
- ✅ INTEGRATED: debug_integration.py (test migration & unification)
- ✅ INTEGRATED: utility_import_validation.py (circular import detection)

ARCHITECTURE: PRIMARY GATEWAY INTERFACE - SPECIAL STATUS
- Pure delegation to debug_core.py, debug_test.py, debug_validation.py
- External access point for all debug, testing, validation, troubleshooting operations
- Ultra-optimized for 128MB Lambda constraint
- Central repository for all testing and validation functionality

GATEWAY FUNCTIONS OVERVIEW (100+ operations):
- Ultra-Optimization Testing: 29 automated tests, gateway utilization validation
- Performance Benchmarking: 4 interface benchmarks, memory usage tracking
- Gateway Utilization: 57 gateway functions tracked, utilization scoring
- Legacy Pattern Detection: 7 pattern types, automated replacement
- Architecture Validation: System compliance, naming conventions, access patterns
- Configuration Testing: Preset validation, AWS constraint compliance
- Import Validation: Circular import detection, architecture compliance
- Integration Testing: Cross-interface testing, migration coordination

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

def _get_debug_coordinator():
    """Get debug coordinator singleton instance."""
    return get_debug_coordinator()

# ===== SECTION 1: ULTRA-OPTIMIZATION TESTING OPERATIONS =====

def run_ultra_optimization_tests(test_filter: Optional[str] = None,
                                 verbose: bool = True,
                                 parallel: bool = False) -> Dict[str, Any]:
    """Run comprehensive ultra-optimization test suite (29 tests across 6 interfaces)."""
    coordinator = _get_debug_coordinator()
    return coordinator.execute_debug_operation(
        DebugOperation.RUN_ULTRA_OPTIMIZATION_TESTS,
        test_filter=test_filter,
        verbose=verbose,
        parallel=parallel
    )

def test_metrics_gateway_optimization(detailed: bool = False) -> Dict[str, Any]:
    """Test metrics interface ultra-optimization (6 tests)."""
    coordinator = _get_debug_coordinator()
    return coordinator.execute_debug_operation(
        DebugOperation.TEST_METRICS_GATEWAY_OPTIMIZATION,
        detailed=detailed
    )

def test_singleton_gateway_optimization(detailed: bool = False) -> Dict[str, Any]:
    """Test singleton interface ultra-optimization (6 tests)."""
    coordinator = _get_debug_coordinator()
    return coordinator.execute_debug_operation(
        DebugOperation.TEST_SINGLETON_GATEWAY_OPTIMIZATION,
        detailed=detailed
    )

def test_cache_gateway_integration(detailed: bool = False) -> Dict[str, Any]:
    """Test cache interface gateway integration (5 tests)."""
    coordinator = _get_debug_coordinator()
    return coordinator.execute_debug_operation(
        DebugOperation.TEST_CACHE_GATEWAY_INTEGRATION,
        detailed=detailed
    )

def test_security_gateway_integration(detailed: bool = False) -> Dict[str, Any]:
    """Test security interface gateway integration (4 tests)."""
    coordinator = _get_debug_coordinator()
    return coordinator.execute_debug_operation(
        DebugOperation.TEST_SECURITY_GATEWAY_INTEGRATION,
        detailed=detailed
    )

def test_shared_utilities(detailed: bool = False) -> Dict[str, Any]:
    """Test shared utilities functionality (5 tests)."""
    coordinator = _get_debug_coordinator()
    return coordinator.execute_debug_operation(
        DebugOperation.TEST_SHARED_UTILITIES,
        detailed=detailed
    )

def test_legacy_elimination(detailed: bool = False) -> Dict[str, Any]:
    """Test legacy pattern elimination validation (3 tests)."""
    coordinator = _get_debug_coordinator()
    return coordinator.execute_debug_operation(
        DebugOperation.TEST_LEGACY_ELIMINATION,
        detailed=detailed
    )

# ===== SECTION 2: PERFORMANCE BENCHMARKING OPERATIONS =====

def run_performance_benchmark(benchmark_scope: str = "comprehensive",
                              iterations: int = 1000,
                              include_memory: bool = True) -> Dict[str, Any]:
    """Run comprehensive performance benchmark suite."""
    coordinator = _get_debug_coordinator()
    return coordinator.execute_debug_operation(
        DebugOperation.RUN_PERFORMANCE_BENCHMARK,
        benchmark_scope=benchmark_scope,
        iterations=iterations,
        include_memory=include_memory
    )

def benchmark_metrics_interface(iterations: int = 1000) -> Dict[str, Any]:
    """Benchmark metrics interface operations."""
    coordinator = _get_debug_coordinator()
    return coordinator.execute_debug_operation(
        DebugOperation.BENCHMARK_METRICS_INTERFACE,
        iterations=iterations
    )

def benchmark_singleton_interface(iterations: int = 1000) -> Dict[str, Any]:
    """Benchmark singleton interface operations."""
    coordinator = _get_debug_coordinator()
    return coordinator.execute_debug_operation(
        DebugOperation.BENCHMARK_SINGLETON_INTERFACE,
        iterations=iterations
    )

def benchmark_cache_interface(iterations: int = 1000) -> Dict[str, Any]:
    """Benchmark cache interface operations."""
    coordinator = _get_debug_coordinator()
    return coordinator.execute_debug_operation(
        DebugOperation.BENCHMARK_CACHE_INTERFACE,
        iterations=iterations
    )

def benchmark_security_interface(iterations: int = 1000) -> Dict[str, Any]:
    """Benchmark security interface operations."""
    coordinator = _get_debug_coordinator()
    return coordinator.execute_debug_operation(
        DebugOperation.BENCHMARK_SECURITY_INTERFACE,
        iterations=iterations
    )

def benchmark_memory_usage(operation_count: int = 100) -> Dict[str, Any]:
    """Benchmark memory usage and optimization effectiveness."""
    coordinator = _get_debug_coordinator()
    return coordinator.execute_debug_operation(
        DebugOperation.BENCHMARK_MEMORY_USAGE,
        operation_count=operation_count
    )

# ===== SECTION 3: GATEWAY UTILIZATION VALIDATION =====

def analyze_gateway_usage(file_path: str, file_content: str) -> Dict[str, Any]:
    """Analyze gateway usage patterns in a file."""
    coordinator = _get_debug_coordinator()
    return coordinator.execute_debug_operation(
        DebugOperation.ANALYZE_GATEWAY_USAGE,
        file_path=file_path,
        file_content=file_content
    )

def calculate_utilization_percentage(file_path: str, 
                                    gateway_usage: Dict[str, Any]) -> float:
    """Calculate gateway utilization percentage for a file."""
    coordinator = _get_debug_coordinator()
    return coordinator.execute_debug_operation(
        DebugOperation.CALCULATE_UTILIZATION_PERCENTAGE,
        file_path=file_path,
        gateway_usage=gateway_usage
    )

def identify_missing_integrations(file_path: str,
                                  gateway_usage: Dict[str, Any]) -> List[Dict[str, str]]:
    """Identify missing gateway integrations."""
    coordinator = _get_debug_coordinator()
    return coordinator.execute_debug_operation(
        DebugOperation.IDENTIFY_MISSING_INTEGRATIONS,
        file_path=file_path,
        gateway_usage=gateway_usage
    )

def generate_utilization_report(file_path: str, file_content: str) -> Dict[str, Any]:
    """Generate comprehensive gateway utilization report."""
    coordinator = _get_debug_coordinator()
    return coordinator.execute_debug_operation(
        DebugOperation.GENERATE_UTILIZATION_REPORT,
        file_path=file_path,
        file_content=file_content
    )

def analyze_project_wide_utilization(file_paths: List[str]) -> Dict[str, Any]:
    """Analyze gateway utilization across entire project."""
    coordinator = _get_debug_coordinator()
    return coordinator.execute_debug_operation(
        DebugOperation.ANALYZE_PROJECT_WIDE_UTILIZATION,
        file_paths=file_paths
    )

def generate_optimization_action_plan(report: Dict[str, Any]) -> List[Dict[str, str]]:
    """Generate actionable optimization plan from utilization report."""
    coordinator = _get_debug_coordinator()
    return coordinator.execute_debug_operation(
        DebugOperation.GENERATE_OPTIMIZATION_ACTION_PLAN,
        report=report
    )

# ===== SECTION 4: LEGACY PATTERN DETECTION & ELIMINATION =====

def scan_file_for_legacy_patterns(file_content: str) -> Dict[str, List[str]]:
    """Scan file for legacy patterns (7 pattern types)."""
    coordinator = _get_debug_coordinator()
    return coordinator.execute_debug_operation(
        DebugOperation.SCAN_FILE_FOR_LEGACY_PATTERNS,
        file_content=file_content
    )

def generate_replacement_suggestions(findings: Dict[str, Any]) -> List[Dict[str, str]]:
    """Generate replacement suggestions for legacy patterns."""
    coordinator = _get_debug_coordinator()
    return coordinator.execute_debug_operation(
        DebugOperation.GENERATE_REPLACEMENT_SUGGESTIONS,
        findings=findings
    )

def create_legacy_elimination_report(file_path: str, 
                                    file_content: str) -> Dict[str, Any]:
    """Create comprehensive legacy elimination report."""
    coordinator = _get_debug_coordinator()
    return coordinator.execute_debug_operation(
        DebugOperation.CREATE_LEGACY_ELIMINATION_REPORT,
        file_path=file_path,
        file_content=file_content
    )

def auto_replace_simple_patterns(file_content: str, 
                                 pattern_type: str) -> str:
    """Automatically replace simple legacy patterns."""
    coordinator = _get_debug_coordinator()
    return coordinator.execute_debug_operation(
        DebugOperation.AUTO_REPLACE_SIMPLE_PATTERNS,
        file_content=file_content,
        pattern_type=pattern_type
    )

def validate_gateway_usage(file_content: str) -> Dict[str, Any]:
    """Validate gateway pattern usage in file."""
    coordinator = _get_debug_coordinator()
    return coordinator.execute_debug_operation(
        DebugOperation.VALIDATE_GATEWAY_USAGE,
        file_content=file_content
    )

def generate_optimization_roadmap(files: List[str]) -> Dict[str, Any]:
    """Generate optimization roadmap for multiple files."""
    coordinator = _get_debug_coordinator()
    return coordinator.execute_debug_operation(
        DebugOperation.GENERATE_OPTIMIZATION_ROADMAP,
        files=files
    )

# ===== SECTION 5: ARCHITECTURE VALIDATION =====

def validate_system_architecture(project_path: str = ".") -> Dict[str, Any]:
    """Validate system architecture compliance."""
    coordinator = _get_debug_coordinator()
    return coordinator.execute_debug_operation(
        DebugOperation.VALIDATE_SYSTEM_ARCHITECTURE,
        project_path=project_path
    )

def validate_file_structure(project_path: str) -> Dict[str, Any]:
    """Validate project file structure."""
    coordinator = _get_debug_coordinator()
    return coordinator.execute_debug_operation(
        DebugOperation.VALIDATE_FILE_STRUCTURE,
        project_path=project_path
    )

def validate_naming_conventions(project_path: str) -> Dict[str, Any]:
    """Validate file naming conventions."""
    coordinator = _get_debug_coordinator()
    return coordinator.execute_debug_operation(
        DebugOperation.VALIDATE_NAMING_CONVENTIONS,
        project_path=project_path
    )

def validate_access_patterns(project_path: str) -> Dict[str, Any]:
    """Validate access pattern compliance."""
    coordinator = _get_debug_coordinator()
    return coordinator.execute_debug_operation(
        DebugOperation.VALIDATE_ACCESS_PATTERNS,
        project_path=project_path
    )

def validate_gateway_implementation(project_path: str) -> Dict[str, Any]:
    """Validate gateway pattern implementation."""
    coordinator = _get_debug_coordinator()
    return coordinator.execute_debug_operation(
        DebugOperation.VALIDATE_GATEWAY_IMPLEMENTATION,
        project_path=project_path
    )

# ===== SECTION 6: AWS CONSTRAINT VALIDATION =====

def validate_memory_constraints() -> Dict[str, Any]:
    """Validate memory usage against AWS Lambda constraints."""
    coordinator = _get_debug_coordinator()
    return coordinator.execute_debug_operation(
        DebugOperation.VALIDATE_MEMORY_CONSTRAINTS
    )

def validate_cost_protection() -> Dict[str, Any]:
    """Validate cost protection and free tier compliance."""
    coordinator = _get_debug_coordinator()
    return coordinator.execute_debug_operation(
        DebugOperation.VALIDATE_COST_PROTECTION
    )

def validate_aws_constraints() -> List[Dict[str, Any]]:
    """Validate all AWS constraint compliance."""
    coordinator = _get_debug_coordinator()
    return coordinator.execute_debug_operation(
        DebugOperation.VALIDATE_AWS_CONSTRAINTS
    )

# ===== SECTION 7: SECURITY VALIDATION =====

def validate_security_configuration() -> Dict[str, Any]:
    """Validate security configuration compliance."""
    coordinator = _get_debug_coordinator()
    return coordinator.execute_debug_operation(
        DebugOperation.VALIDATE_SECURITY_CONFIGURATION
    )

def validate_input_validation_implementation() -> Dict[str, Any]:
    """Validate input validation implementation."""
    coordinator = _get_debug_coordinator()
    return coordinator.execute_debug_operation(
        DebugOperation.VALIDATE_INPUT_VALIDATION
    )

def validate_data_sanitization() -> Dict[str, Any]:
    """Validate data sanitization implementation."""
    coordinator = _get_debug_coordinator()
    return coordinator.execute_debug_operation(
        DebugOperation.VALIDATE_DATA_SANITIZATION
    )

# ===== SECTION 8: CONFIGURATION TESTING =====

def run_configuration_tests() -> bool:
    """Run complete configuration system test suite."""
    coordinator = _get_debug_coordinator()
    return coordinator.execute_debug_operation(
        DebugOperation.RUN_CONFIGURATION_TESTS
    )

def test_configuration_presets() -> Dict[str, Any]:
    """Test configuration preset functionality."""
    coordinator = _get_debug_coordinator()
    return coordinator.execute_debug_operation(
        DebugOperation.TEST_CONFIGURATION_PRESETS
    )

def test_configuration_parameters() -> Dict[str, Any]:
    """Test configuration parameter management."""
    coordinator = _get_debug_coordinator()
    return coordinator.execute_debug_operation(
        DebugOperation.TEST_CONFIGURATION_PARAMETERS
    )

def test_configuration_tiers() -> Dict[str, Any]:
    """Test configuration tier management."""
    coordinator = _get_debug_coordinator()
    return coordinator.execute_debug_operation(
        DebugOperation.TEST_CONFIGURATION_TIERS
    )

def test_configuration_performance() -> Dict[str, Any]:
    """Test configuration system performance."""
    coordinator = _get_debug_coordinator()
    return coordinator.execute_debug_operation(
        DebugOperation.TEST_CONFIGURATION_PERFORMANCE
    )

# ===== SECTION 9: IMPORT VALIDATION =====

def validate_import_architecture(project_path: str = ".") -> Dict[str, Any]:
    """Validate import architecture and detect circular imports."""
    coordinator = _get_debug_coordinator()
    return coordinator.execute_debug_operation(
        DebugOperation.VALIDATE_IMPORT_ARCHITECTURE,
        project_path=project_path
    )

def detect_circular_imports(project_path: str) -> List[Dict[str, Any]]:
    """Detect circular import patterns."""
    coordinator = _get_debug_coordinator()
    return coordinator.execute_debug_operation(
        DebugOperation.DETECT_CIRCULAR_IMPORTS,
        project_path=project_path
    )

def analyze_import_dependencies(project_path: str) -> Dict[str, Any]:
    """Analyze import dependency graph."""
    coordinator = _get_debug_coordinator()
    return coordinator.execute_debug_operation(
        DebugOperation.ANALYZE_IMPORT_DEPENDENCIES,
        project_path=project_path
    )

def generate_import_fix_suggestions(violations: List[Dict]) -> List[Dict[str, str]]:
    """Generate fix suggestions for import violations."""
    coordinator = _get_debug_coordinator()
    return coordinator.execute_debug_operation(
        DebugOperation.GENERATE_IMPORT_FIX_SUGGESTIONS,
        violations=violations
    )

# ===== SECTION 10: INTEGRATION & MIGRATION =====

def migrate_utility_tests() -> Dict[str, Any]:
    """Migrate utility.py testing functions to debug interface."""
    coordinator = _get_debug_coordinator()
    return coordinator.execute_debug_operation(
        DebugOperation.MIGRATE_UTILITY_TESTS
    )

def integrate_config_testing() -> Dict[str, Any]:
    """Integrate config_testing.py patterns into debug framework."""
    coordinator = _get_debug_coordinator()
    return coordinator.execute_debug_operation(
        DebugOperation.INTEGRATE_CONFIG_TESTING
    )

def incorporate_import_validation() -> Dict[str, Any]:
    """Incorporate import validation into debug_validation.py."""
    coordinator = _get_debug_coordinator()
    return coordinator.execute_debug_operation(
        DebugOperation.INCORPORATE_IMPORT_VALIDATION
    )

def consolidate_validation_functions() -> Dict[str, Any]:
    """Consolidate scattered validation functions."""
    coordinator = _get_debug_coordinator()
    return coordinator.execute_debug_operation(
        DebugOperation.CONSOLIDATE_VALIDATION_FUNCTIONS
    )

def get_integration_status() -> Dict[str, Any]:
    """Get current integration/migration status."""
    coordinator = _get_debug_coordinator()
    return coordinator.execute_debug_operation(
        DebugOperation.GET_INTEGRATION_STATUS
    )

# ===== SECTION 11: UNIFIED TEST RUNNING =====

def run_unified_tests(interfaces: Optional[List[str]] = None) -> Dict[str, Any]:
    """Run unified tests across all or specific interfaces."""
    coordinator = _get_debug_coordinator()
    return coordinator.execute_debug_operation(
        DebugOperation.RUN_UNIFIED_TESTS,
        interfaces=interfaces
    )

def register_interface_tests(interface_name: str, 
                            test_functions: List[str]) -> bool:
    """Register test functions for an interface."""
    coordinator = _get_debug_coordinator()
    return coordinator.execute_debug_operation(
        DebugOperation.REGISTER_INTERFACE_TESTS,
        interface_name=interface_name,
        test_functions=test_functions
    )

def aggregate_test_results(test_results: List[Dict]) -> Dict[str, Any]:
    """Aggregate test results from multiple sources."""
    coordinator = _get_debug_coordinator()
    return coordinator.execute_debug_operation(
        DebugOperation.AGGREGATE_TEST_RESULTS,
        test_results=test_results
    )

# ===== SECTION 12: COMPREHENSIVE TESTING OPERATIONS =====

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
                       test_types: List[str] = None,
                       include_integration: bool = True) -> Dict[str, Any]:
    """Run tests for specific interface."""
    coordinator = _get_debug_coordinator()
    return coordinator.execute_debug_operation(
        DebugOperation.RUN_INTERFACE_TESTS,
        interface_name=interface_name,
        test_types=test_types,
        include_integration=include_integration
    )

def run_integration_tests(integration_scope: str = "cross_interface",
                         critical_paths_only: bool = False) -> Dict[str, Any]:
    """Run integration tests between interfaces."""
    coordinator = _get_debug_coordinator()
    return coordinator.execute_debug_operation(
        DebugOperation.RUN_INTEGRATION_TESTS,
        integration_scope=integration_scope,
        critical_paths_only=critical_paths_only
    )

def run_performance_tests(performance_targets: Dict[str, float] = None,
                         stress_test: bool = False) -> Dict[str, Any]:
    """Run performance tests with optional stress testing."""
    coordinator = _get_debug_coordinator()
    return coordinator.execute_debug_operation(
        DebugOperation.RUN_PERFORMANCE_TESTS,
        performance_targets=performance_targets,
        stress_test=stress_test
    )

def get_test_results(test_category: str = "all",
                    result_filter: str = "all",
                    include_details: bool = True) -> Dict[str, Any]:
    """Get test results with filtering options."""
    coordinator = _get_debug_coordinator()
    return coordinator.execute_debug_operation(
        DebugOperation.GET_TEST_RESULTS,
        test_category=test_category,
        result_filter=result_filter,
        include_details=include_details
    )

# ===== SECTION 13: VALIDATION OPERATIONS =====

def validate_gateway_compliance(interfaces: List[str] = None) -> List[Dict[str, Any]]:
    """Validate gateway pattern compliance for interfaces."""
    coordinator = _get_debug_coordinator()
    return coordinator.execute_debug_operation(
        DebugOperation.VALIDATE_GATEWAY_COMPLIANCE,
        interfaces=interfaces
    )

def validate_system_configuration(config_scope: str = "complete") -> Dict[str, Any]:
    """Validate system configuration."""
    coordinator = _get_debug_coordinator()
    return coordinator.execute_debug_operation(
        DebugOperation.VALIDATE_SYSTEM_CONFIGURATION,
        config_scope=config_scope
    )

def get_validation_status(validation_type: str = "all",
                         detailed_results: bool = False) -> Dict[str, Any]:
    """Get validation status with optional details."""
    coordinator = _get_debug_coordinator()
    return coordinator.execute_debug_operation(
        DebugOperation.GET_VALIDATION_STATUS,
        validation_type=validation_type,
        detailed_results=detailed_results
    )

# ===== SECTION 14: DIAGNOSTIC & TROUBLESHOOTING =====

def diagnose_system_health(diagnostic_depth: str = "comprehensive",
                          include_recommendations: bool = True) -> Dict[str, Any]:
    """Diagnose system health comprehensively."""
    coordinator = _get_debug_coordinator()
    return coordinator.execute_debug_operation(
        DebugOperation.DIAGNOSE_SYSTEM_HEALTH,
        diagnostic_depth=diagnostic_depth,
        include_recommendations=include_recommendations
    )

def analyze_performance_issues(performance_threshold: float = 100.0,
                              historical_comparison: bool = True) -> Dict[str, Any]:
    """Analyze performance issues and bottlenecks."""
    coordinator = _get_debug_coordinator()
    return coordinator.execute_debug_operation(
        DebugOperation.ANALYZE_PERFORMANCE_ISSUES,
        performance_threshold=performance_threshold,
        historical_comparison=historical_comparison
    )

def detect_resource_problems(resource_types: List[str] = None,
                            alert_thresholds: Dict[str, float] = None) -> Dict[str, Any]:
    """Detect resource usage problems."""
    coordinator = _get_debug_coordinator()
    return coordinator.execute_debug_operation(
        DebugOperation.DETECT_RESOURCE_PROBLEMS,
        resource_types=resource_types,
        alert_thresholds=alert_thresholds
    )

def generate_diagnostic_report(report_format: str = "comprehensive",
                              include_metrics: bool = True,
                              include_recommendations: bool = True) -> Dict[str, Any]:
    """Generate comprehensive diagnostic report."""
    coordinator = _get_debug_coordinator()
    return coordinator.execute_debug_operation(
        DebugOperation.GENERATE_DIAGNOSTIC_REPORT,
        report_format=report_format,
        include_metrics=include_metrics,
        include_recommendations=include_recommendations
    )

def get_troubleshooting_recommendations(issue_category: str = "all",
                                       priority_level: str = "all") -> List[Dict[str, str]]:
    """Get troubleshooting recommendations."""
    coordinator = _get_debug_coordinator()
    return coordinator.execute_debug_operation(
        DebugOperation.GET_TROUBLESHOOTING_RECOMMENDATIONS,
        issue_category=issue_category,
        priority_level=priority_level
    )

def get_system_diagnostic_info(diagnostic_level: str = "standard",
                              include_cache: bool = True,
                              include_performance: bool = True) -> Dict[str, Any]:
    """Get comprehensive system diagnostic information."""
    coordinator = _get_debug_coordinator()
    return coordinator.execute_debug_operation(
        DebugOperation.GET_SYSTEM_DIAGNOSTIC_INFO,
        diagnostic_level=diagnostic_level,
        include_cache=include_cache,
        include_performance=include_performance
    )

# ===== SECTION 15: DEBUG COORDINATION =====

def run_full_system_debug(debug_level: str = "comprehensive",
                         include_automation: bool = True,
                         generate_reports: bool = True) -> Dict[str, Any]:
    """Run full system debug with automation and reporting."""
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
    """Get current debug system status."""
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
    """Enable detailed debug mode."""
    coordinator = _get_debug_coordinator()
    return coordinator.execute_debug_operation(
        DebugOperation.ENABLE_DEBUG_MODE,
        debug_level=debug_level,
        enhanced_logging=enhanced_logging,
        performance_monitoring=performance_monitoring
    )

def disable_debug_mode(preserve_data: bool = True,
                      generate_summary: bool = True) -> Dict[str, Any]:
    """Disable debug mode."""
    coordinator = _get_debug_coordinator()
    return coordinator.execute_debug_operation(
        DebugOperation.DISABLE_DEBUG_MODE,
        preserve_data=preserve_data,
        generate_summary=generate_summary
    )

def get_debug_configuration(config_scope: str = "complete",
                           include_recommendations: bool = False) -> Dict[str, Any]:
    """Get current debug configuration."""
    coordinator = _get_debug_coordinator()
    return coordinator.execute_debug_operation(
        DebugOperation.GET_DEBUG_CONFIGURATION,
        config_scope=config_scope,
        include_recommendations=include_recommendations
    )

# EOF
