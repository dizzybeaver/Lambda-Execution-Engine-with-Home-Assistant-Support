"""
debug_tools.py - Debug, Test, Benchmark, and Validation Test Scripts
Version: 2025.09.30.01
Description: ULTRA-OPTIMIZED callable test scripts using generic operation pattern

ULTRA-OPTIMIZATIONS COMPLETED (2025.09.30.01):
- ✅ UPDATED: All scripts use execute_debug_operation() generic function
- ✅ STREAMLINED: Reduced function call overhead
- ✅ MAINTAINED: All test execution functionality
- ✅ ENHANCED: Better correlation ID tracking

ARCHITECTURE: EXTERNAL FILE - Test Scripts
- Calls debug.py gateway interface functions
- Provides standalone test/validation/benchmarking scripts
- Contains ACTUAL test execution scripts (not test implementation)
- Test implementation is in debug_core.py, debug_test.py, debug_validation.py

TEST SCRIPTS PROVIDED:
- Ultra-optimization testing (29 tests across 6 interfaces)
- Performance benchmarking (4 interface benchmarks)
- Gateway utilization validation (57 functions tracked)
- Legacy pattern detection (7 pattern types)
- Architecture validation (system compliance)
- Configuration testing (preset validation)
- Import validation (circular import detection)
- Integration testing (cross-interface testing)

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

import sys
import json
from typing import Dict, Any, List, Optional

from . import debug
from .debug_core import DebugOperation

def run_all_ultra_optimization_tests(verbose: bool = True, 
                                     parallel: bool = False) -> Dict[str, Any]:
    """Execute complete ultra-optimization test suite."""
    print("\n" + "="*80)
    print("ULTRA-OPTIMIZATION TEST SUITE")
    print("="*80)
    
    result = debug.execute_debug_operation(
        DebugOperation.RUN_ULTRA_OPTIMIZATION_TESTS,
        test_filter=None,
        verbose=verbose,
        parallel=parallel
    )
    
    if verbose:
        print(f"\nTests Passed: {result.get('tests_passed', 0)}/{result.get('tests_total', 0)}")
        print(f"Pass Rate: {result.get('pass_rate', 0):.1f}%")
        print(f"Optimization Status: {result.get('optimization_status', 'UNKNOWN')}")
        print(f"Gateway Utilization: {result.get('gateway_utilization', 0):.1f}%")
        
        if result.get('success'):
            print("\n✅ ALL TESTS PASSED")
        else:
            print("\n❌ SOME TESTS FAILED")
    
    return result

def run_performance_benchmarks(iterations: int = 1000, 
                               include_memory: bool = True) -> Dict[str, Any]:
    """Execute comprehensive performance benchmark suite."""
    print("\n" + "="*80)
    print("PERFORMANCE BENCHMARK SUITE")
    print("="*80)
    
    result = debug.execute_debug_operation(
        DebugOperation.RUN_PERFORMANCE_BENCHMARK,
        benchmark_scope="comprehensive",
        iterations=iterations,
        include_memory=include_memory
    )
    
    print(f"\nBenchmark Completed:")
    print(f"Total Iterations: {iterations}")
    print(f"Average Duration: {result.get('average_duration_ms', 0):.2f}ms")
    print(f"P95 Latency: {result.get('p95_latency_ms', 0):.2f}ms")
    print(f"P99 Latency: {result.get('p99_latency_ms', 0):.2f}ms")
    
    if include_memory:
        print(f"Memory Usage: {result.get('memory_usage_mb', 0):.2f}MB")
    
    return result

def analyze_file_gateway_usage(file_path: str) -> Dict[str, Any]:
    """Analyze gateway usage patterns in a specific file."""
    print("\n" + "="*80)
    print(f"GATEWAY USAGE ANALYSIS: {file_path}")
    print("="*80)
    
    try:
        with open(file_path, 'r') as f:
            file_content = f.read()
    except Exception as e:
        print(f"\n❌ Error reading file: {e}")
        return {"error": str(e)}
    
    result = debug.execute_debug_operation(
        DebugOperation.ANALYZE_GATEWAY_USAGE,
        file_path=file_path,
        file_content=file_content
    )
    
    print(f"\nGateway Functions Used: {result.get('functions_used', 0)}")
    print(f"Total Available: {result.get('functions_available', 0)}")
    print(f"Utilization: {result.get('utilization_percentage', 0):.1f}%")
    
    missing = result.get('missing_integrations', [])
    if missing:
        print(f"\nMissing Integrations ({len(missing)}):")
        for m in missing[:5]:
            print(f"  - {m.get('function', 'Unknown')}")
    
    return result

def run_architecture_validation(project_path: str = ".") -> Dict[str, Any]:
    """Run complete architecture validation."""
    print("\n" + "="*80)
    print("ARCHITECTURE VALIDATION")
    print("="*80)
    
    result = debug.execute_debug_operation(
        DebugOperation.VALIDATE_SYSTEM_ARCHITECTURE,
        project_path=project_path
    )
    
    print(f"\nValidation Status: {result.get('status', 'UNKNOWN')}")
    print(f"Compliance Score: {result.get('compliance_score', 0):.1f}%")
    
    violations = result.get('violations', [])
    if violations:
        print(f"\nViolations Found ({len(violations)}):")
        for v in violations[:10]:
            print(f"  - {v.get('type', 'Unknown')}: {v.get('description', 'N/A')}")
    else:
        print("\n✅ No violations found")
    
    return result

def run_import_validation(project_path: str = ".") -> Dict[str, Any]:
    """Run import architecture validation and circular import detection."""
    print("\n" + "="*80)
    print("IMPORT VALIDATION")
    print("="*80)
    
    arch_result = debug.execute_debug_operation(
        DebugOperation.VALIDATE_IMPORT_ARCHITECTURE,
        project_path=project_path
    )
    
    print(f"\nArchitecture Validation: {arch_result.get('status', 'UNKNOWN')}")
    
    circular_result = debug.execute_debug_operation(
        DebugOperation.DETECT_CIRCULAR_IMPORTS,
        project_path=project_path
    )
    
    circular_imports = circular_result.get('circular_imports', [])
    if circular_imports:
        print(f"\n❌ Circular Imports Detected ({len(circular_imports)}):")
        for ci in circular_imports[:5]:
            print(f"  - {ci.get('cycle', 'Unknown')}")
    else:
        print("\n✅ No circular imports detected")
    
    return {
        'architecture': arch_result,
        'circular_imports': circular_result
    }

def run_configuration_tests() -> Dict[str, Any]:
    """Run complete configuration system tests."""
    print("\n" + "="*80)
    print("CONFIGURATION SYSTEM TESTS")
    print("="*80)
    
    result = debug.execute_debug_operation(
        DebugOperation.RUN_CONFIGURATION_TESTS
    )
    
    if result:
        print("\n✅ Configuration tests passed")
    else:
        print("\n❌ Configuration tests failed")
    
    return {"success": result}

def run_comprehensive_tests(test_scope: str = "all") -> Dict[str, Any]:
    """Run comprehensive system tests."""
    print("\n" + "="*80)
    print("COMPREHENSIVE SYSTEM TESTS")
    print("="*80)
    print(f"Scope: {test_scope}")
    
    result = debug.execute_debug_operation(
        DebugOperation.RUN_COMPREHENSIVE_TESTS,
        test_scope=test_scope,
        test_depth="standard",
        parallel_execution=False
    )
    
    print(f"\nTests Passed: {result.get('tests_passed', 0)}/{result.get('tests_total', 0)}")
    print(f"Success Rate: {result.get('success_rate', 0):.1f}%")
    print(f"Duration: {result.get('duration_seconds', 0):.2f}s")
    
    return result

def diagnose_system_health() -> Dict[str, Any]:
    """Diagnose system health and identify issues."""
    print("\n" + "="*80)
    print("SYSTEM HEALTH DIAGNOSIS")
    print("="*80)
    
    result = debug.execute_debug_operation(
        DebugOperation.DIAGNOSE_SYSTEM_HEALTH,
        health_check_depth="standard",
        include_recommendations=True
    )
    
    print(f"\nHealth Status: {result.get('health_status', 'UNKNOWN')}")
    print(f"Overall Score: {result.get('health_score', 0):.1f}%")
    
    issues = result.get('issues', [])
    if issues:
        print(f"\nIssues Detected ({len(issues)}):")
        for issue in issues[:5]:
            print(f"  - {issue.get('severity', 'Unknown')}: {issue.get('description', 'N/A')}")
    else:
        print("\n✅ No issues detected")
    
    recommendations = result.get('recommendations', [])
    if recommendations:
        print(f"\nRecommendations ({len(recommendations)}):")
        for rec in recommendations[:5]:
            print(f"  - {rec}")
    
    return result

def create_deployment_backup(files: List[str], 
                             backup_name: Optional[str] = None) -> Dict[str, Any]:
    """Create backup of specified files before deployment."""
    print("\n" + "="*80)
    print("DEPLOYMENT BACKUP")
    print("="*80)
    
    result = debug.execute_debug_operation(
        DebugOperation.CREATE_BACKUP,
        files=files,
        backup_name=backup_name,
        project_root="."
    )
    
    print(f"\nBackup Status: {result.get('status', 'UNKNOWN')}")
    print(f"Backup Location: {result.get('backup_path', 'N/A')}")
    print(f"Files Backed Up: {result.get('files_count', 0)}")
    
    return result

def validate_deployment_ready(files: List[str]) -> Dict[str, Any]:
    """Validate files are ready for deployment."""
    print("\n" + "="*80)
    print("DEPLOYMENT READINESS VALIDATION")
    print("="*80)
    
    result = debug.execute_debug_operation(
        DebugOperation.VALIDATE_DEPLOYMENT_READY,
        files=files,
        required_version=None,
        project_root="."
    )
    
    print(f"\nValidation Status: {result.get('status', 'UNKNOWN')}")
    
    if result.get('ready', False):
        print("✅ All files ready for deployment")
    else:
        print("❌ Files not ready for deployment")
        issues = result.get('issues', [])
        if issues:
            print(f"\nIssues ({len(issues)}):")
            for issue in issues:
                print(f"  - {issue}")
    
    return result

def main():
    """Main entry point for debug tools."""
    if len(sys.argv) < 2:
        print("\nUsage: python -m debug_tools <command> [args]")
        print("\nCommands:")
        print("  tests              - Run ultra-optimization tests")
        print("  benchmark          - Run performance benchmarks")
        print("  analyze <file>     - Analyze gateway usage in file")
        print("  validate           - Run architecture validation")
        print("  imports            - Run import validation")
        print("  config             - Run configuration tests")
        print("  comprehensive      - Run comprehensive tests")
        print("  health             - Diagnose system health")
        print("  backup <files...>  - Create deployment backup")
        return
    
    command = sys.argv[1]
    
    if command == "tests":
        run_all_ultra_optimization_tests()
    elif command == "benchmark":
        run_performance_benchmarks()
    elif command == "analyze" and len(sys.argv) > 2:
        analyze_file_gateway_usage(sys.argv[2])
    elif command == "validate":
        run_architecture_validation()
    elif command == "imports":
        run_import_validation()
    elif command == "config":
        run_configuration_tests()
    elif command == "comprehensive":
        run_comprehensive_tests()
    elif command == "health":
        diagnose_system_health()
    elif command == "backup" and len(sys.argv) > 2:
        create_deployment_backup(sys.argv[2:])
    else:
        print(f"\n❌ Unknown command: {command}")

if __name__ == "__main__":
    main()

# EOF
