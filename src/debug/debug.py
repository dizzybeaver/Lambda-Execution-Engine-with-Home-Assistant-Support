"""
debug.py - Debug, Testing, and Validation Primary Gateway Interface
Version: 2025.09.29.02
Description: Comprehensive testing, validation, troubleshooting, and deployment gateway

INTEGRATIONS COMPLETED (2025.09.29.02):
- ✅ INTEGRATED: ultra_optimization_tester.py (29 tests)
- ✅ INTEGRATED: performance_benchmark.py (comprehensive benchmarking)
- ✅ INTEGRATED: gateway_utilization_validator.py (57 functions tracked)
- ✅ INTEGRATED: legacy_elimination_patterns.py (7 pattern types)
- ✅ INTEGRATED: debug_validation.py (architecture/config/security)
- ✅ INTEGRATED: config_testing.py (configuration system tests)
- ✅ INTEGRATED: debug_integration.py (test migration)
- ✅ INTEGRATED: utility_import_validation.py (circular import detection)
- ✅ INTEGRATED: deployment_automation.py (deployment operations)

ARCHITECTURE: PRIMARY GATEWAY INTERFACE - SPECIAL STATUS
- Pure delegation to debug_core.py
- External access point for all debug operations
- Ultra-optimized for 128MB Lambda constraint

Licensed under the Apache License, Version 2.0
"""

from typing import Dict, Any, List, Optional, Callable, Tuple
from .debug_core import get_debug_coordinator, DebugOperation

def _get_debug_coordinator():
    """Get debug coordinator singleton instance."""
    return get_debug_coordinator()

# ===== SECTION 1: ULTRA-OPTIMIZATION TESTING =====

def run_ultra_optimization_tests(test_filter: Optional[str] = None,
                                 verbose: bool = True,
                                 parallel: bool = False) -> Dict[str, Any]:
    """Run comprehensive ultra-optimization test suite."""
    coordinator = _get_debug_coordinator()
    return coordinator.execute_debug_operation(
        DebugOperation.RUN_ULTRA_OPTIMIZATION_TESTS,
        test_filter=test_filter,
        verbose=verbose,
        parallel=parallel
    )

def test_metrics_gateway_optimization(detailed: bool = False) -> Dict[str, Any]:
    """Test metrics interface ultra-optimization."""
    coordinator = _get_debug_coordinator()
    return coordinator.execute_debug_operation(
        DebugOperation.TEST_METRICS_GATEWAY_OPTIMIZATION,
        detailed=detailed
    )

def test_singleton_gateway_optimization(detailed: bool = False) -> Dict[str, Any]:
    """Test singleton interface ultra-optimization."""
    coordinator = _get_debug_coordinator()
    return coordinator.execute_debug_operation(
        DebugOperation.TEST_SINGLETON_GATEWAY_OPTIMIZATION,
        detailed=detailed
    )

def test_cache_gateway_integration(detailed: bool = False) -> Dict[str, Any]:
    """Test cache interface gateway integration."""
    coordinator = _get_debug_coordinator()
    return coordinator.execute_debug_operation(
        DebugOperation.TEST_CACHE_GATEWAY_INTEGRATION,
        detailed=detailed
    )

def test_security_gateway_integration(detailed: bool = False) -> Dict[str, Any]:
    """Test security interface gateway integration."""
    coordinator = _get_debug_coordinator()
    return coordinator.execute_debug_operation(
        DebugOperation.TEST_SECURITY_GATEWAY_INTEGRATION,
        detailed=detailed
    )

def test_shared_utilities(detailed: bool = False) -> Dict[str, Any]:
    """Test shared utilities functionality."""
    coordinator = _get_debug_coordinator()
    return coordinator.execute_debug_operation(
        DebugOperation.TEST_SHARED_UTILITIES,
        detailed=detailed
    )

def test_legacy_elimination(detailed: bool = False) -> Dict[str, Any]:
    """Test legacy pattern elimination validation."""
    coordinator = _get_debug_coordinator()
    return coordinator.execute_debug_operation(
        DebugOperation.TEST_LEGACY_ELIMINATION,
        detailed=detailed
    )

# ===== SECTION 2: PERFORMANCE BENCHMARKING =====

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
                                    gateway_usage: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate gateway utilization percentage for a file."""
    coordinator = _get_debug_coordinator()
    return coordinator.execute_debug_operation(
        DebugOperation.CALCULATE_UTILIZATION_PERCENTAGE,
        file_path=file_path,
        gateway_usage=gateway_usage
    )

def identify_missing_integrations(file_path: str,
                                 gateway_usage: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Identify missing gateway integrations in a file."""
    coordinator = _get_debug_coordinator()
    return coordinator.execute_debug_operation(
        DebugOperation.IDENTIFY_MISSING_INTEGRATIONS,
        file_path=file_path,
        gateway_usage=gateway_usage
    )

def generate_utilization_report(file_path: str,
                               file_content: str) -> Dict[str, Any]:
    """Generate comprehensive gateway utilization report for a file."""
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
    """Generate actionable optimization plan for a file."""
    coordinator = _get_debug_coordinator()
    return coordinator.execute_debug_operation(
        DebugOperation.GENERATE_OPTIMIZATION_ACTION_PLAN,
        report=report
    )

# ===== SECTION 4: LEGACY PATTERN DETECTION =====

def scan_file_for_legacy_patterns(file_content: str) -> Dict[str, Any]:
    """Scan a file for legacy code patterns."""
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
    """Test configuration preset validation."""
    coordinator = _get_debug_coordinator()
    return coordinator.execute_debug_operation(
        DebugOperation.TEST_CONFIGURATION_PRESETS
    )

def test_configuration_parameters() -> Dict[str, Any]:
    """Test configuration parameter operations."""
    coordinator = _get_debug_coordinator()
    return coordinator.execute_debug_operation(
        DebugOperation.TEST_CONFIGURATION_PARAMETERS
    )

def test_configuration_tiers() -> Dict[str, Any]:
    """Test configuration tier validation."""
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
    """Validate import architecture compliance."""
    coordinator = _get_debug_coordinator()
    return coordinator.execute_debug_operation(
        DebugOperation.VALIDATE_IMPORT_ARCHITECTURE,
        project_path=project_path
    )

def detect_circular_imports(project_path: str = ".") -> Dict[str, Any]:
    """Detect circular import patterns."""
    coordinator = _get_debug_coordinator()
    return coordinator.execute_debug_operation(
        DebugOperation.DETECT_CIRCULAR_IMPORTS,
        project_path=project_path
    )

def analyze_import_dependencies(project_path: str = ".") -> Dict[str, Any]:
    """Analyze import dependency chains."""
    coordinator = _get_debug_coordinator()
    return coordinator.execute_debug_operation(
        DebugOperation.ANALYZE_IMPORT_DEPENDENCIES,
        project_path=project_path
    )

def generate_import_fix_suggestions(violations: List[Dict]) -> List[Dict[str, str]]:
    """Generate suggestions for fixing import issues."""
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

# ===== SECTION 12: COMPREHENSIVE TESTING =====

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

def validate_gateway_compliance(project_path: str = ".") -> Dict[str, Any]:
    """Validate gateway/firewall architecture compliance."""
    coordinator = _get_debug_coordinator()
    return coordinator.execute_debug_operation(
        DebugOperation.VALIDATE_GATEWAY_COMPLIANCE,
        project_path=project_path
    )

def validate_system_configuration(config_scope: str = "all") -> Dict[str, Any]:
    """Validate system configuration."""
    coordinator = _get_debug_coordinator()
    return coordinator.execute_debug_operation(
        DebugOperation.VALIDATE_SYSTEM_CONFIGURATION,
        config_scope=config_scope
    )

def get_validation_status(validation_type: str = "all",
                         include_history: bool = False) -> Dict[str, Any]:
    """Get validation status summary."""
    coordinator = _get_debug_coordinator()
    return coordinator.execute_debug_operation(
        DebugOperation.GET_VALIDATION_STATUS,
        validation_type=validation_type,
        include_history=include_history
    )

# ===== SECTION 14: DIAGNOSTIC OPERATIONS =====

def diagnose_system_health(health_check_depth: str = "standard",
                          include_recommendations: bool = True) -> Dict[str, Any]:
    """Diagnose system health and identify issues."""
    coordinator = _get_debug_coordinator()
    return coordinator.execute_debug_operation(
        DebugOperation.DIAGNOSE_SYSTEM_HEALTH,
        health_check_depth=health_check_depth,
        include_recommendations=include_recommendations
    )

def analyze_performance_issues(analysis_scope: str = "system_wide",
                              time_range_seconds: int = 3600) -> Dict[str, Any]:
    """Analyze performance issues and bottlenecks."""
    coordinator = _get_debug_coordinator()
    return coordinator.execute_debug_operation(
        DebugOperation.ANALYZE_PERFORMANCE_ISSUES,
        analysis_scope=analysis_scope,
        time_range_seconds=time_range_seconds
    )

def detect_resource_problems(resource_types: List[str] = None,
                            threshold_percentages: Dict[str, float] = None) -> Dict[str, Any]:
    """Detect resource constraint problems."""
    coordinator = _get_debug_coordinator()
    return coordinator.execute_debug_operation(
        DebugOperation.DETECT_RESOURCE_PROBLEMS,
        resource_types=resource_types,
        threshold_percentages=threshold_percentages
    )

def generate_diagnostic_report(report_scope: str = "comprehensive",
                              report_format: str = "detailed") -> Dict[str, Any]:
    """Generate comprehensive diagnostic report."""
    coordinator = _get_debug_coordinator()
    return coordinator.execute_debug_operation(
        DebugOperation.GENERATE_DIAGNOSTIC_REPORT,
        report_scope=report_scope,
        report_format=report_format
    )

def get_troubleshooting_recommendations(issue_category: str = "all",
                                       priority_filter: str = "all") -> List[Dict[str, Any]]:
    """Get troubleshooting recommendations for identified issues."""
    coordinator = _get_debug_coordinator()
    return coordinator.execute_debug_operation(
        DebugOperation.GET_TROUBLESHOOTING_RECOMMENDATIONS,
        issue_category=issue_category,
        priority_filter=priority_filter
    )

def get_system_diagnostic_info(info_categories: List[str] = None,
                               include_sensitive: bool = False) -> Dict[str, Any]:
    """Get system diagnostic information."""
    coordinator = _get_debug_coordinator()
    return coordinator.execute_debug_operation(
        DebugOperation.GET_SYSTEM_DIAGNOSTIC_INFO,
        info_categories=info_categories,
        include_sensitive=include_sensitive
    )

# ===== SECTION 15: DEBUG COORDINATION =====

def run_full_system_debug(debug_level: str = "comprehensive",
                         include_automation: bool = True,
                         generate_reports: bool = True) -> Dict[str, Any]:
    """Run complete system-wide debug operation."""
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

# ===== SECTION 16: DEPLOYMENT OPERATIONS =====

def create_backup(files: List[str], 
                 backup_name: Optional[str] = None,
                 project_root: str = ".") -> Dict[str, Any]:
    """Create backup of specified files before deployment."""
    coordinator = _get_debug_coordinator()
    return coordinator.execute_debug_operation(
        DebugOperation.CREATE_BACKUP,
        files=files,
        backup_name=backup_name,
        project_root=project_root
    )

def verify_file_version(file_path: str, 
                       expected_version: str,
                       project_root: str = ".") -> Dict[str, Any]:
    """Verify file has expected version string."""
    coordinator = _get_debug_coordinator()
    return coordinator.execute_debug_operation(
        DebugOperation.VERIFY_FILE_VERSION,
        file_path=file_path,
        expected_version=expected_version,
        project_root=project_root
    )

def deploy_files(file_mappings: Dict[str, str],
                project_root: str = ".") -> Dict[str, Any]:
    """Deploy files from source to destination."""
    coordinator = _get_debug_coordinator()
    return coordinator.execute_debug_operation(
        DebugOperation.DEPLOY_FILES,
        file_mappings=file_mappings,
        project_root=project_root
    )

def rollback_from_backup(backup_name: str,
                        files: Optional[List[str]] = None,
                        project_root: str = ".") -> Dict[str, Any]:
    """Rollback files from specified backup."""
    coordinator = _get_debug_coordinator()
    return coordinator.execute_debug_operation(
        DebugOperation.ROLLBACK_FROM_BACKUP,
        backup_name=backup_name,
        files=files,
        project_root=project_root
    )

def validate_deployment(expected_files: List[Tuple[str, str]],
                       project_root: str = ".") -> Dict[str, Any]:
    """Validate deployment by checking file versions."""
    coordinator = _get_debug_coordinator()
    return coordinator.execute_debug_operation(
        DebugOperation.VALIDATE_DEPLOYMENT,
        expected_files=expected_files,
        project_root=project_root
    )

def run_post_deployment_tests(test_scope: str = "comprehensive") -> Dict[str, Any]:
    """Run post-deployment validation tests."""
    coordinator = _get_debug_coordinator()
    return coordinator.execute_debug_operation(
        DebugOperation.RUN_POST_DEPLOYMENT_TESTS,
        test_scope=test_scope
    )

def generate_deployment_report(include_logs: bool = True,
                              report_format: str = "detailed") -> str:
    """Generate comprehensive deployment report."""
    coordinator = _get_debug_coordinator()
    return coordinator.execute_debug_operation(
        DebugOperation.GENERATE_DEPLOYMENT_REPORT,
        include_logs=include_logs,
        report_format=report_format
    )

def automated_deployment(files_to_backup: List[str],
                        file_mappings: Dict[str, str],
                        expected_files: List[Tuple[str, str]],
                        project_root: str = ".") -> Dict[str, Any]:
    """Fully automated deployment with backup, deploy, validate, and test."""
    coordinator = _get_debug_coordinator()
    return coordinator.execute_debug_operation(
        DebugOperation.AUTOMATED_DEPLOYMENT,
        files_to_backup=files_to_backup,
        file_mappings=file_mappings,
        expected_files=expected_files,
        project_root=project_root
    )

# EOF
