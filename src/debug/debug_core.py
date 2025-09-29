"""
debug_core.py - Debug Primary Gateway Interface Core Implementation
Version: 2025.09.28.01
Description: Core implementation for generic debug, testing, validation, and troubleshooting operations

ARCHITECTURE: SECONDARY IMPLEMENTATION - Internal Network
- Generic testing infrastructure and framework
- Test runner coordination and result aggregation  
- Performance measurement and analysis utilities
- Generic validation framework and system health checking
- Error analysis and diagnostic utilities
- Memory optimization and AWS constraint compliance

CORE FUNCTIONALITY:
- Test execution coordination across all interfaces
- Performance measurement and benchmarking
- System health monitoring and analysis
- Error pattern detection and analysis
- Resource usage tracking and optimization
- Test environment setup and cleanup
- Result aggregation and reporting

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

import time
import sys
import gc
import traceback
import statistics
from typing import Dict, Any, List, Optional, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
import threading
import concurrent.futures

# Import gateway interfaces
import cache
import security  
import logging as log_gateway
import metrics
import utility
import config

# ===== SECTION 1: DEBUG OPERATION TYPES =====

class DebugOperation(Enum):
    """Debug operation types for coordination."""
    
    # Test operations
    RUN_COMPREHENSIVE_TESTS = "run_comprehensive_tests"
    RUN_INTERFACE_TESTS = "run_interface_tests"
    RUN_INTEGRATION_TESTS = "run_integration_tests"
    RUN_PERFORMANCE_TESTS = "run_performance_tests"
    GET_TEST_RESULTS = "get_test_results"
    
    # Validation operations
    VALIDATE_SYSTEM_ARCHITECTURE = "validate_system_architecture"
    VALIDATE_AWS_CONSTRAINTS = "validate_aws_constraints"
    VALIDATE_GATEWAY_COMPLIANCE = "validate_gateway_compliance"
    VALIDATE_CONFIGURATION = "validate_configuration"
    GET_VALIDATION_STATUS = "get_validation_status"
    
    # Troubleshooting operations
    DIAGNOSE_SYSTEM_HEALTH = "diagnose_system_health"
    ANALYZE_PERFORMANCE_ISSUES = "analyze_performance_issues"
    DETECT_RESOURCE_PROBLEMS = "detect_resource_problems"
    GENERATE_DIAGNOSTIC_REPORT = "generate_diagnostic_report"
    GET_TROUBLESHOOTING_RECOMMENDATIONS = "get_troubleshooting_recommendations"
    
    # Debug coordination
    RUN_FULL_SYSTEM_DEBUG = "run_full_system_debug"
    GET_DEBUG_STATUS = "get_debug_status"
    ENABLE_DEBUG_MODE = "enable_debug_mode"
    DISABLE_DEBUG_MODE = "disable_debug_mode"
    GET_DEBUG_CONFIGURATION = "get_debug_configuration"

class TestStatus(Enum):
    """Test execution status."""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"

class ValidationStatus(Enum):
    """Validation status levels."""
    VALID = "valid"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class DiagnosticLevel(Enum):
    """Diagnostic severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

# ===== SECTION 2: DATA STRUCTURES =====

@dataclass
class TestResult:
    """Test execution result."""
    test_name: str
    status: TestStatus
    duration_ms: float
    message: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    memory_usage_mb: Optional[float] = None
    error_trace: Optional[str] = None

@dataclass
class ValidationResult:
    """Validation result."""
    validation_name: str
    status: ValidationStatus
    message: str
    recommendations: List[str] = field(default_factory=list)
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

@dataclass
class DiagnosticResult:
    """Diagnostic analysis result."""
    diagnostic_name: str
    level: DiagnosticLevel
    message: str
    recommendations: List[str] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

@dataclass
class PerformanceMetrics:
    """Performance measurement data."""
    execution_time_ms: float
    memory_usage_mb: float
    cpu_time_ms: Optional[float] = None
    cache_hits: int = 0
    cache_misses: int = 0
    errors: int = 0
    warnings: int = 0

# ===== SECTION 3: CORE DEBUG MANAGER =====

class DebugCoreManager:
    """Core debug operations manager with thread-safe execution."""
    
    def __init__(self):
        self._lock = threading.RLock()
        self._test_results: Dict[str, List[TestResult]] = defaultdict(list)
        self._validation_results: Dict[str, List[ValidationResult]] = defaultdict(list)
        self._diagnostic_results: Dict[str, List[DiagnosticResult]] = defaultdict(list)
        self._performance_history: deque = deque(maxlen=100)
        self._debug_mode_enabled = False
        self._correlation_id = None
        
    def execute_debug_operation(self, operation: DebugOperation, **kwargs) -> Dict[str, Any]:
        """Execute debug operation with comprehensive tracking."""
        start_time = time.time()
        correlation_id = self._generate_correlation_id()
        
        try:
            log_gateway.log_debug(f"Debug operation started: {operation.value}", {
                "correlation_id": correlation_id,
                "operation": operation.value,
                "kwargs": str(kwargs)[:200]
            })
            
            # Route to appropriate handler
            if operation.value.startswith('run_') or operation == DebugOperation.GET_TEST_RESULTS:
                result = self._handle_test_operation(operation, **kwargs)
            elif operation.value.startswith('validate_') or operation == DebugOperation.GET_VALIDATION_STATUS:
                result = self._handle_validation_operation(operation, **kwargs)
            elif operation.value.startswith('diagnose_') or operation.value.startswith('analyze_') or operation.value.startswith('detect_') or operation.value.startswith('generate_') or operation.value.startswith('get_troubleshooting_'):
                result = self._handle_diagnostic_operation(operation, **kwargs)
            else:
                result = self._handle_coordination_operation(operation, **kwargs)
            
            # Add metadata
            duration_ms = (time.time() - start_time) * 1000
            result.update({
                "correlation_id": correlation_id,
                "operation": operation.value,
                "duration_ms": duration_ms,
                "timestamp": time.time(),
                "memory_usage_mb": self._get_current_memory_usage()
            })
            
            # Record performance metrics
            self._record_performance_metrics(operation, duration_ms)
            
            log_gateway.log_debug(f"Debug operation completed: {operation.value}", {
                "correlation_id": correlation_id,
                "duration_ms": duration_ms,
                "success": result.get("success", True)
            })
            
            return result
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            error_result = {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__,
                "correlation_id": correlation_id,
                "operation": operation.value,
                "duration_ms": duration_ms,
                "timestamp": time.time(),
                "trace": traceback.format_exc() if self._debug_mode_enabled else None
            }
            
            log_gateway.log_error(f"Debug operation failed: {operation.value}", {
                "correlation_id": correlation_id,
                "error": str(e),
                "duration_ms": duration_ms
            })
            
            return error_result
    
    def _handle_test_operation(self, operation: DebugOperation, **kwargs) -> Dict[str, Any]:
        """Handle test-related operations."""
        if operation == DebugOperation.RUN_COMPREHENSIVE_TESTS:
            return self._run_comprehensive_tests(**kwargs)
        elif operation == DebugOperation.RUN_INTERFACE_TESTS:
            return self._run_interface_tests(**kwargs)
        elif operation == DebugOperation.RUN_INTEGRATION_TESTS:
            return self._run_integration_tests(**kwargs)
        elif operation == DebugOperation.RUN_PERFORMANCE_TESTS:
            return self._run_performance_tests(**kwargs)
        elif operation == DebugOperation.GET_TEST_RESULTS:
            return self._get_test_results(**kwargs)
        else:
            return {"success": False, "error": f"Unknown test operation: {operation}"}
    
    def _handle_validation_operation(self, operation: DebugOperation, **kwargs) -> Dict[str, Any]:
        """Handle validation-related operations."""
        if operation == DebugOperation.VALIDATE_SYSTEM_ARCHITECTURE:
            return self._validate_system_architecture(**kwargs)
        elif operation == DebugOperation.VALIDATE_AWS_CONSTRAINTS:
            return self._validate_aws_constraints(**kwargs)
        elif operation == DebugOperation.VALIDATE_GATEWAY_COMPLIANCE:
            return self._validate_gateway_compliance(**kwargs)
        elif operation == DebugOperation.VALIDATE_CONFIGURATION:
            return self._validate_configuration(**kwargs)
        elif operation == DebugOperation.GET_VALIDATION_STATUS:
            return self._get_validation_status(**kwargs)
        else:
            return {"success": False, "error": f"Unknown validation operation: {operation}"}
    
    def _handle_diagnostic_operation(self, operation: DebugOperation, **kwargs) -> Dict[str, Any]:
        """Handle diagnostic and troubleshooting operations."""
        if operation == DebugOperation.DIAGNOSE_SYSTEM_HEALTH:
            return self._diagnose_system_health(**kwargs)
        elif operation == DebugOperation.ANALYZE_PERFORMANCE_ISSUES:
            return self._analyze_performance_issues(**kwargs)
        elif operation == DebugOperation.DETECT_RESOURCE_PROBLEMS:
            return self._detect_resource_problems(**kwargs)
        elif operation == DebugOperation.GENERATE_DIAGNOSTIC_REPORT:
            return self._generate_diagnostic_report(**kwargs)
        elif operation == DebugOperation.GET_TROUBLESHOOTING_RECOMMENDATIONS:
            return self._get_troubleshooting_recommendations(**kwargs)
        else:
            return {"success": False, "error": f"Unknown diagnostic operation: {operation}"}
    
    def _handle_coordination_operation(self, operation: DebugOperation, **kwargs) -> Dict[str, Any]:
        """Handle debug coordination operations."""
        if operation == DebugOperation.RUN_FULL_SYSTEM_DEBUG:
            return self._run_full_system_debug(**kwargs)
        elif operation == DebugOperation.GET_DEBUG_STATUS:
            return self._get_debug_status(**kwargs)
        elif operation == DebugOperation.ENABLE_DEBUG_MODE:
            return self._enable_debug_mode(**kwargs)
        elif operation == DebugOperation.DISABLE_DEBUG_MODE:
            return self._disable_debug_mode(**kwargs)
        elif operation == DebugOperation.GET_DEBUG_CONFIGURATION:
            return self._get_debug_configuration(**kwargs)
        else:
            return {"success": False, "error": f"Unknown coordination operation: {operation}"}

    # ===== SECTION 4: TEST OPERATION IMPLEMENTATIONS =====
    
    def _run_comprehensive_tests(self, **kwargs) -> Dict[str, Any]:
        """Run comprehensive system-wide tests."""
        test_suite = kwargs.get("test_suite", "all")
        parallel = kwargs.get("parallel", True)
        max_workers = kwargs.get("max_workers", 4)
        
        test_results = []
        start_time = time.time()
        
        try:
            # Define test categories
            test_categories = [
                "gateway_interfaces",
                "configuration_system", 
                "security_validation",
                "cache_operations",
                "import_architecture",
                "memory_constraints",
                "performance_benchmarks"
            ]
            
            if test_suite != "all":
                test_categories = [cat for cat in test_categories if test_suite in cat]
            
            if parallel and len(test_categories) > 1:
                # Run tests in parallel
                with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                    future_to_category = {
                        executor.submit(self._run_test_category, category): category 
                        for category in test_categories
                    }
                    
                    for future in concurrent.futures.as_completed(future_to_category):
                        category = future_to_category[future]
                        try:
                            category_results = future.result()
                            test_results.extend(category_results)
                        except Exception as e:
                            test_results.append(TestResult(
                                test_name=f"{category}_execution",
                                status=TestStatus.ERROR,
                                duration_ms=0,
                                message=f"Test category execution failed: {str(e)}",
                                error_trace=traceback.format_exc()
                            ))
            else:
                # Run tests sequentially
                for category in test_categories:
                    category_results = self._run_test_category(category)
                    test_results.extend(category_results)
            
            # Store results
            with self._lock:
                self._test_results["comprehensive"].extend(test_results)
            
            # Generate summary
            total_tests = len(test_results)
            passed = len([r for r in test_results if r.status == TestStatus.PASSED])
            failed = len([r for r in test_results if r.status == TestStatus.FAILED])
            errors = len([r for r in test_results if r.status == TestStatus.ERROR])
            
            return {
                "success": True,
                "test_summary": {
                    "total_tests": total_tests,
                    "passed": passed,
                    "failed": failed,
                    "errors": errors,
                    "pass_rate": passed / total_tests if total_tests > 0 else 0
                },
                "execution_time_ms": (time.time() - start_time) * 1000,
                "test_results": [self._serialize_test_result(r) for r in test_results],
                "recommendations": self._generate_test_recommendations(test_results)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Comprehensive test execution failed: {str(e)}",
                "execution_time_ms": (time.time() - start_time) * 1000
            }
    
    def _run_interface_tests(self, **kwargs) -> Dict[str, Any]:
        """Run tests for specific interface."""
        interface_name = kwargs.get("interface_name", "all")
        test_types = kwargs.get("test_types", ["functionality", "performance", "memory"])
        
        if interface_name == "all":
            interfaces = ["cache", "security", "logging", "metrics", "utility", "config"]
        else:
            interfaces = [interface_name]
        
        all_results = []
        
        for interface in interfaces:
            interface_results = self._test_interface(interface, test_types)
            all_results.extend(interface_results)
        
        with self._lock:
            self._test_results[f"interface_{interface_name}"].extend(all_results)
        
        return {
            "success": True,
            "interface": interface_name,
            "test_results": [self._serialize_test_result(r) for r in all_results],
            "summary": self._summarize_test_results(all_results)
        }
    
    def _run_integration_tests(self, **kwargs) -> Dict[str, Any]:
        """Run integration tests across interfaces."""
        workflows = kwargs.get("workflows", ["end_to_end", "gateway_compliance", "memory_constraints"])
        
        integration_results = []
        
        for workflow in workflows:
            workflow_results = self._test_integration_workflow(workflow)
            integration_results.extend(workflow_results)
        
        with self._lock:
            self._test_results["integration"].extend(integration_results)
        
        return {
            "success": True,
            "integration_results": [self._serialize_test_result(r) for r in integration_results],
            "summary": self._summarize_test_results(integration_results)
        }
    
    def _run_performance_tests(self, **kwargs) -> Dict[str, Any]:
        """Run performance benchmarking tests."""
        benchmark_types = kwargs.get("benchmark_types", ["response_time", "memory_usage", "throughput"])
        iterations = kwargs.get("iterations", 10)
        
        performance_results = []
        
        for benchmark in benchmark_types:
            benchmark_results = self._run_performance_benchmark(benchmark, iterations)
            performance_results.extend(benchmark_results)
        
        return {
            "success": True,
            "performance_results": [self._serialize_test_result(r) for r in performance_results],
            "benchmark_summary": self._analyze_performance_results(performance_results)
        }
    
    def _get_test_results(self, **kwargs) -> Dict[str, Any]:
        """Get stored test results."""
        test_category = kwargs.get("test_category", "all")
        limit = kwargs.get("limit", 100)
        
        with self._lock:
            if test_category == "all":
                all_results = []
                for category_results in self._test_results.values():
                    all_results.extend(category_results)
                results = sorted(all_results, key=lambda x: x.timestamp, reverse=True)[:limit]
            else:
                results = list(self._test_results.get(test_category, []))[-limit:]
        
        return {
            "success": True,
            "test_category": test_category,
            "results_count": len(results),
            "test_results": [self._serialize_test_result(r) for r in results]
        }

    # ===== SECTION 5: VALIDATION OPERATION IMPLEMENTATIONS =====
    
    def _validate_system_architecture(self, **kwargs) -> Dict[str, Any]:
        """Validate overall system architecture compliance."""
        checks = kwargs.get("checks", ["gateway_pattern", "import_dependencies", "file_structure"])
        
        validation_results = []
        
        for check in checks:
            if check == "gateway_pattern":
                result = self._validate_gateway_pattern()
            elif check == "import_dependencies":
                result = self._validate_import_dependencies()
            elif check == "file_structure":
                result = self._validate_file_structure()
            else:
                result = ValidationResult(
                    validation_name=check,
                    status=ValidationStatus.ERROR,
                    message=f"Unknown validation check: {check}"
                )
            
            validation_results.append(result)
        
        with self._lock:
            self._validation_results["architecture"].extend(validation_results)
        
        return {
            "success": True,
            "validation_results": [self._serialize_validation_result(r) for r in validation_results],
            "overall_status": self._get_overall_validation_status(validation_results)
        }
    
    def _validate_aws_constraints(self, **kwargs) -> Dict[str, Any]:
        """Validate AWS Lambda constraints compliance."""
        constraints = kwargs.get("constraints", ["memory_limits", "execution_time", "cost_protection"])
        
        validation_results = []
        
        for constraint in constraints:
            if constraint == "memory_limits":
                result = self._validate_memory_constraints()
            elif constraint == "execution_time":
                result = self._validate_execution_time_constraints()
            elif constraint == "cost_protection":
                result = self._validate_cost_protection()
            else:
                result = ValidationResult(
                    validation_name=constraint,
                    status=ValidationStatus.ERROR,
                    message=f"Unknown constraint check: {constraint}"
                )
            
            validation_results.append(result)
        
        return {
            "success": True,
            "constraint_validation": [self._serialize_validation_result(r) for r in validation_results],
            "compliance_status": self._assess_aws_compliance(validation_results)
        }
    
    def _validate_gateway_compliance(self, **kwargs) -> Dict[str, Any]:
        """Validate gateway pattern compliance."""
        interfaces = kwargs.get("interfaces", ["all"])
        
        if "all" in interfaces:
            interfaces = ["cache", "security", "logging", "metrics", "utility", "config", "debug"]
        
        compliance_results = []
        
        for interface in interfaces:
            result = self._check_gateway_compliance(interface)
            compliance_results.append(result)
        
        return {
            "success": True,
            "compliance_results": [self._serialize_validation_result(r) for r in compliance_results],
            "compliance_score": self._calculate_compliance_score(compliance_results)
        }

    # ===== SECTION 6: UTILITY METHODS =====
    
    def _generate_correlation_id(self) -> str:
        """Generate unique correlation ID for tracking."""
        import uuid
        return str(uuid.uuid4())[:8]
    
    def _get_current_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        try:
            import psutil
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024
        except ImportError:
            return 0.0
    
    def _record_performance_metrics(self, operation: DebugOperation, duration_ms: float) -> None:
        """Record performance metrics for analysis."""
        metrics_data = PerformanceMetrics(
            execution_time_ms=duration_ms,
            memory_usage_mb=self._get_current_memory_usage()
        )
        
        with self._lock:
            self._performance_history.append({
                "operation": operation.value,
                "timestamp": time.time(),
                "metrics": metrics_data
            })
    
    def _serialize_test_result(self, result: TestResult) -> Dict[str, Any]:
        """Serialize test result for JSON output."""
        return {
            "test_name": result.test_name,
            "status": result.status.value,
            "duration_ms": result.duration_ms,
            "message": result.message,
            "details": result.details,
            "timestamp": result.timestamp,
            "memory_usage_mb": result.memory_usage_mb,
            "error_trace": result.error_trace if self._debug_mode_enabled else None
        }
    
    def _serialize_validation_result(self, result: ValidationResult) -> Dict[str, Any]:
        """Serialize validation result for JSON output."""
        return {
            "validation_name": result.validation_name,
            "status": result.status.value,
            "message": result.message,
            "recommendations": result.recommendations,
            "details": result.details,
            "timestamp": result.timestamp
        }

# ===== SECTION 7: SINGLETON MANAGER INSTANCE =====

_debug_core_manager = None
_manager_lock = threading.Lock()

def get_debug_core_manager() -> DebugCoreManager:
    """Get singleton debug core manager instance."""
    global _debug_core_manager
    
    if _debug_core_manager is None:
        with _manager_lock:
            if _debug_core_manager is None:
                _debug_core_manager = DebugCoreManager()
    
    return _debug_core_manager

# ===== SECTION 8: GENERIC DEBUG OPERATION FUNCTION =====

def generic_debug_operation(operation: DebugOperation, **kwargs) -> Dict[str, Any]:
    """
    ULTRA-GENERIC: Execute any debug operation using operation type.
    Consolidates all debug functions into single ultra-optimized function.
    """
    manager = get_debug_core_manager()
    return manager.execute_debug_operation(operation, **kwargs)
