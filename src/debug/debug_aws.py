"""
debug_aws.py
Version: 2025.10.11.01
Description: Debug AWS-specific test interface with program-like execution capabilities

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

import sys
import json
import time
import argparse
from typing import Dict, Any, List, Optional

from gateway import (
    log_info, log_error, log_warning,
    create_success_response, create_error_response,
    generate_correlation_id
)

from shared_utilities import (
    handle_operation_error,
    create_operation_context, close_operation_context
)

from gateway import (
    execute_debug_operation, debug_health_check, debug_diagnostics, 
    debug_run_tests, debug_analyze_system
)

# ===== SECTION 1: AWS TEST PROGRAM INTERFACE =====

class AWSTestProgram:
    """AWS test program interface for running tests like a standalone program."""
    
    def __init__(self):
        self.correlation_id = generate_correlation_id()
        self.start_time = time.time()
        
    def run_program(self, args: List[str]) -> Dict[str, Any]:
        """Main program entry point."""
        context = create_operation_context('debug_aws', 'run_program')
        
        try:
            parser = self._create_argument_parser()
            parsed_args = parser.parse_args(args)
            
            result = self._execute_command(parsed_args)
            
            close_operation_context(context, success=True, result=result)
            return result
            
        except Exception as e:
            return handle_operation_error('debug_aws', 'run_program', e, context['correlation_id'])
    
    def _create_argument_parser(self) -> argparse.ArgumentParser:
        """Create command line argument parser."""
        parser = argparse.ArgumentParser(
            description='AWS Lambda Debug Test Interface',
            prog='Debug_aws'
        )
        
        subparsers = parser.add_subparsers(dest='command', help='Available commands')
        
        # Health command
        health_parser = subparsers.add_parser('health', help='Run health checks')
        health_parser.add_argument('--component', help='Specific component to check')
        
        # Test command
        test_parser = subparsers.add_parser('test', help='Run test suites')
        test_parser.add_argument('--type', choices=['ultra', 'performance', 'configuration', 'comprehensive'],
                                default='comprehensive', help='Test type to run')
        test_parser.add_argument('--iterations', type=int, default=1000, help='Performance test iterations')
        test_parser.add_argument('--verbose', action='store_true', help='Verbose output')
        
        # Analysis command
        analysis_parser = subparsers.add_parser('analyze', help='System analysis')
        analysis_parser.add_argument('--file', help='File to analyze')
        analysis_parser.add_argument('--architecture', action='store_true', help='Architecture analysis')
        analysis_parser.add_argument('--imports', action='store_true', help='Import analysis')
        
        # Monitor command
        monitor_parser = subparsers.add_parser('monitor', help='Monitor system performance')
        monitor_parser.add_argument('--duration', type=int, default=60, help='Monitoring duration in seconds')
        monitor_parser.add_argument('--interval', type=int, default=5, help='Monitoring interval in seconds')
        
        # Benchmark command
        benchmark_parser = subparsers.add_parser('benchmark', help='Performance benchmarking')
        benchmark_parser.add_argument('--iterations', type=int, default=1000, help='Benchmark iterations')
        benchmark_parser.add_argument('--memory', action='store_true', help='Include memory profiling')
        
        # Validation command
        validation_parser = subparsers.add_parser('validate', help='System validation')
        validation_parser.add_argument('--deployment', action='store_true', help='Deployment readiness')
        validation_parser.add_argument('--files', nargs='+', help='Files to validate')
        
        # Diagnostics command
        diag_parser = subparsers.add_parser('diagnostics', help='System diagnostics')
        diag_parser.add_argument('--full', action='store_true', help='Full diagnostic report')
        
        return parser
    
    def _execute_command(self, args) -> Dict[str, Any]:
        """Execute the specified command."""
        command_map = {
            'health': self._run_health_command,
            'test': self._run_test_command,
            'analyze': self._run_analyze_command,
            'monitor': self._run_monitor_command,
            'benchmark': self._run_benchmark_command,
            'validate': self._run_validate_command,
            'diagnostics': self._run_diagnostics_command
        }
        
        if not args.command:
            return self._show_help()
        
        handler = command_map.get(args.command)
        if not handler:
            return create_error_response(f"Unknown command: {args.command}")
        
        return handler(args)
    
    def _run_health_command(self, args) -> Dict[str, Any]:
        """Run health check command."""
        log_info("Running health check", correlation_id=self.correlation_id)
        
        if args.component:
            result = debug_health_check(component=args.component)
        else:
            result = debug_health_check()
        
        self._print_health_results(result)
        return create_success_response("Health check completed", result)
    
    def _run_test_command(self, args) -> Dict[str, Any]:
        """Run test command."""
        log_info(f"Running {args.type} tests", correlation_id=self.correlation_id)
        
        if args.type == 'performance':
            result = execute_debug_operation(
                'RUN_PERFORMANCE_BENCHMARK',
                iterations=args.iterations,
                include_memory=True
            )
        else:
            result = debug_run_tests(args.type)
        
        self._print_test_results(result, args.verbose)
        return create_success_response("Tests completed", result)
    
    def _run_analyze_command(self, args) -> Dict[str, Any]:
        """Run analysis command."""
        log_info("Running system analysis", correlation_id=self.correlation_id)
        
        if args.file:
            result = execute_debug_operation(
                'ANALYZE_GATEWAY_USAGE',
                file_path=args.file
            )
            self._print_file_analysis(result)
        elif args.architecture:
            result = execute_debug_operation('VALIDATE_SYSTEM_ARCHITECTURE')
            self._print_architecture_analysis(result)
        elif args.imports:
            result = execute_debug_operation('VALIDATE_IMPORT_ARCHITECTURE')
            self._print_import_analysis(result)
        else:
            result = debug_analyze_system()
            self._print_system_analysis(result)
        
        return create_success_response("Analysis completed", result)
    
    def _run_monitor_command(self, args) -> Dict[str, Any]:
        """Run monitoring command."""
        log_info(f"Monitoring system for {args.duration} seconds", correlation_id=self.correlation_id)
        
        result = execute_debug_operation(
            'MONITOR_PERFORMANCE',
            duration=args.duration
        )
        
        self._print_monitoring_results(result)
        return create_success_response("Monitoring completed", result)
    
    def _run_benchmark_command(self, args) -> Dict[str, Any]:
        """Run benchmark command."""
        log_info(f"Running benchmark with {args.iterations} iterations", correlation_id=self.correlation_id)
        
        result = execute_debug_operation(
            'RUN_PERFORMANCE_BENCHMARK',
            iterations=args.iterations,
            include_memory=args.memory
        )
        
        self._print_benchmark_results(result)
        return create_success_response("Benchmark completed", result)
    
    def _run_validate_command(self, args) -> Dict[str, Any]:
        """Run validation command."""
        log_info("Running validation", correlation_id=self.correlation_id)
        
        if args.deployment:
            result = execute_debug_operation(
                'VALIDATE_DEPLOYMENT_READY',
                files=args.files or []
            )
            self._print_deployment_validation(result)
        else:
            result = execute_debug_operation('VALIDATE_SYSTEM_ARCHITECTURE')
            self._print_system_validation(result)
        
        return create_success_response("Validation completed", result)
    
    def _run_diagnostics_command(self, args) -> Dict[str, Any]:
        """Run diagnostics command."""
        log_info("Running diagnostics", correlation_id=self.correlation_id)
        
        result = debug_diagnostics()
        
        self._print_diagnostics_results(result, args.full)
        return create_success_response("Diagnostics completed", result)
    
    def _show_help(self) -> Dict[str, Any]:
        """Show help message."""
        help_text = """
AWS Lambda Debug Test Interface

Commands:
  health                    - Run health checks
  test [--type TYPE]        - Run test suites
  analyze [--file FILE]     - System analysis  
  monitor [--duration SEC]  - Monitor performance
  benchmark [--iterations N] - Performance benchmarking
  validate [--deployment]   - System validation
  diagnostics [--full]      - System diagnostics

Examples:
  Debug_aws health
  Debug_aws test --type performance --iterations 5000
  Debug_aws analyze --file gateway.py
  Debug_aws monitor --duration 120
  Debug_aws benchmark --memory
  Debug_aws validate --deployment --files *.py
  Debug_aws diagnostics --full
        """
        
        print(help_text)
        return create_success_response("Help displayed", {"help": help_text})

    # ===== SECTION 2: OUTPUT FORMATTERS =====
    
    def _print_health_results(self, result: Dict[str, Any]):
        """Print health check results."""
        print("\n" + "="*60)
        print("HEALTH CHECK RESULTS")
        print("="*60)
        
        if isinstance(result, dict) and 'gateway' in result:
            for component, health in result.items():
                status = health.get('status', 'unknown')
                print(f"{component.upper()}: {status.upper()}")
        else:
            print(f"Overall Status: {result.get('health_status', 'unknown').upper()}")
            if 'health_score' in result:
                print(f"Health Score: {result['health_score']:.1f}%")
    
    def _print_test_results(self, result: Dict[str, Any], verbose: bool):
        """Print test results."""
        print("\n" + "="*60)
        print("TEST RESULTS")
        print("="*60)
        
        print(f"Tests Passed: {result.get('tests_passed', 0)}/{result.get('tests_total', 0)}")
        print(f"Success Rate: {result.get('pass_rate', result.get('success_rate', 0)):.1f}%")
        
        if verbose and 'results' in result:
            print("\nDetailed Results:")
            for test in result['results']:
                status = test.get('status', 'unknown')
                print(f"  {test.get('test', 'Unknown')}: {status.upper()}")
    
    def _print_file_analysis(self, result: Dict[str, Any]):
        """Print file analysis results."""
        print("\n" + "="*60)
        print("FILE ANALYSIS")
        print("="*60)
        
        print(f"Gateway Functions Used: {result.get('functions_used', 0)}")
        print(f"Gateway Functions Available: {result.get('functions_available', 0)}")
        print(f"Utilization: {result.get('utilization_percentage', 0):.1f}%")
    
    def _print_architecture_analysis(self, result: Dict[str, Any]):
        """Print architecture analysis results."""
        print("\n" + "="*60)
        print("ARCHITECTURE ANALYSIS")
        print("="*60)
        
        print(f"Status: {result.get('status', 'unknown').upper()}")
        print(f"Compliance Score: {result.get('compliance_score', 0):.1f}%")
        
        violations = result.get('violations', [])
        if violations:
            print(f"\nViolations ({len(violations)}):")
            for v in violations[:5]:
                print(f"  - {v.get('type', 'Unknown')}: {v.get('description', 'N/A')}")
    
    def _print_import_analysis(self, result: Dict[str, Any]):
        """Print import analysis results."""
        print("\n" + "="*60)
        print("IMPORT ANALYSIS")
        print("="*60)
        
        print(f"Status: {result.get('status', 'unknown').upper()}")
        print(f"Import Depth: {result.get('import_depth', 0)}")
        print(f"Circular Imports: {result.get('circular_imports', 0)}")
    
    def _print_system_analysis(self, result: Dict[str, Any]):
        """Print system analysis results."""
        print("\n" + "="*60)
        print("SYSTEM ANALYSIS")
        print("="*60)
        
        print(f"Status: {result.get('status', 'unknown').upper()}")
        print(f"Compliance Score: {result.get('compliance_score', 0):.1f}%")
    
    def _print_monitoring_results(self, result: Dict[str, Any]):
        """Print monitoring results."""
        print("\n" + "="*60)
        print("MONITORING RESULTS")
        print("="*60)
        
        print(f"Duration: {result.get('duration_seconds', 0)} seconds")
        print(f"Measurements: {result.get('measurements', 0)}")
        print(f"Avg Memory: {result.get('avg_memory_mb', 0):.1f}MB")
        print(f"Avg Response Time: {result.get('avg_response_time_ms', 0):.1f}ms")
    
    def _print_benchmark_results(self, result: Dict[str, Any]):
        """Print benchmark results."""
        print("\n" + "="*60)
        print("BENCHMARK RESULTS")
        print("="*60)
        
        print(f"Iterations: {result.get('iterations', 0)}")
        print(f"Average Duration: {result.get('average_duration_ms', 0):.2f}ms")
        print(f"P95 Latency: {result.get('p95_latency_ms', 0):.2f}ms")
        print(f"P99 Latency: {result.get('p99_latency_ms', 0):.2f}ms")
        
        if 'memory_usage_mb' in result:
            print(f"Memory Usage: {result['memory_usage_mb']:.1f}MB")
    
    def _print_deployment_validation(self, result: Dict[str, Any]):
        """Print deployment validation results."""
        print("\n" + "="*60)
        print("DEPLOYMENT VALIDATION")
        print("="*60)
        
        print(f"Status: {'READY' if result.get('ready', False) else 'NOT READY'}")
        print(f"Files Checked: {result.get('files_count', 0)}")
        
        issues = result.get('issues', [])
        if issues:
            print(f"\nIssues ({len(issues)}):")
            for issue in issues:
                print(f"  - {issue}")
    
    def _print_system_validation(self, result: Dict[str, Any]):
        """Print system validation results."""
        print("\n" + "="*60)
        print("SYSTEM VALIDATION")
        print("="*60)
        
        print(f"Status: {result.get('status', 'unknown').upper()}")
        print(f"Compliance Score: {result.get('compliance_score', 0):.1f}%")
    
    def _print_diagnostics_results(self, result: Dict[str, Any], full: bool):
        """Print diagnostics results."""
        print("\n" + "="*60)
        print("DIAGNOSTICS RESULTS")
        print("="*60)
        
        print(f"Health Status: {result.get('health_status', 'unknown').upper()}")
        print(f"Health Score: {result.get('health_score', 0):.1f}%")
        
        if 'memory_usage_mb' in result:
            print(f"Memory Usage: {result['memory_usage_mb']:.1f}MB")
        
        if 'error_rate' in result:
            print(f"Error Rate: {result['error_rate']:.1%}")
        
        if full:
            issues = result.get('issues', [])
            if issues:
                print(f"\nIssues ({len(issues)}):")
                for issue in issues:
                    severity = issue.get('severity', 'unknown')
                    description = issue.get('description', 'N/A')
                    print(f"  [{severity.upper()}] {description}")

# ===== SECTION 3: PROGRAM ENTRY POINTS =====

def main(args: Optional[List[str]] = None) -> Dict[str, Any]:
    """Main program entry point."""
    if args is None:
        args = sys.argv[1:]
    
    program = AWSTestProgram()
    return program.run_program(args)

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """AWS Lambda handler for serverless execution."""
    try:
        # Extract command from event
        command_args = event.get('command_args', [])
        if isinstance(command_args, str):
            command_args = command_args.split()
        
        log_info("Lambda debug execution started", args=command_args)
        
        program = AWSTestProgram()
        result = program.run_program(command_args)
        
        log_info("Lambda debug execution completed", result=result)
        
        return {
            'statusCode': 200,
            'body': json.dumps(result),
            'headers': {
                'Content-Type': 'application/json'
            }
        }
        
    except Exception as e:
        log_error("Lambda debug execution failed", error=str(e))
        
        return {
            'statusCode': 500,
            'body': json.dumps({
                'success': False,
                'error': str(e),
                'message': 'Debug execution failed'
            }),
            'headers': {
                'Content-Type': 'application/json'
            }
        }

# ===== SECTION 4: CONVENIENCE FUNCTIONS =====

def run_quick_health() -> Dict[str, Any]:
    """Quick health check."""
    return main(['health'])

def run_quick_test() -> Dict[str, Any]:
    """Quick test execution."""
    return main(['test', '--type', 'ultra'])

def run_quick_benchmark() -> Dict[str, Any]:
    """Quick performance benchmark."""
    return main(['benchmark', '--iterations', '100'])

def run_full_diagnostics() -> Dict[str, Any]:
    """Full diagnostic report."""
    return main(['diagnostics', '--full'])

# ===== SECTION 5: BATCH OPERATIONS =====

def run_comprehensive_suite() -> Dict[str, Any]:
    """Run comprehensive test and analysis suite."""
    results = {}
    
    operations = [
        ('health', ['health']),
        ('tests', ['test', '--type', 'comprehensive']),
        ('analysis', ['analyze', '--architecture']),
        ('benchmark', ['benchmark', '--iterations', '1000', '--memory']),
        ('validation', ['validate']),
        ('diagnostics', ['diagnostics', '--full'])
    ]
    
    for name, args in operations:
        try:
            result = main(args)
            results[name] = result
        except Exception as e:
            results[name] = {'error': str(e)}
    
    return results

def run_ci_cd_suite() -> Dict[str, Any]:
    """Run CI/CD validation suite."""
    results = {}
    
    # Critical checks for CI/CD pipeline
    checks = [
        ('health_check', ['health']),
        ('architecture_validation', ['analyze', '--architecture']),
        ('import_validation', ['analyze', '--imports']),
        ('performance_baseline', ['benchmark', '--iterations', '500']),
        ('deployment_readiness', ['validate', '--deployment'])
    ]
    
    for name, args in checks:
        try:
            result = main(args)
            results[name] = result
            
            # Fail fast on critical issues
            if not result.get('success', False):
                results['ci_status'] = 'FAILED'
                results['failure_point'] = name
                break
        except Exception as e:
            results[name] = {'error': str(e)}
            results['ci_status'] = 'FAILED'
            results['failure_point'] = name
            break
    else:
        results['ci_status'] = 'PASSED'
    
    return results

# ===== MODULE EXPORTS =====

__all__ = [
    'main',
    'lambda_handler',
    'run_quick_health',
    'run_quick_test', 
    'run_quick_benchmark',
    'run_full_diagnostics',
    'run_comprehensive_suite',
    'run_ci_cd_suite',
    'AWSTestProgram'
]

# ===== CLI ENTRY POINT =====

if __name__ == "__main__":
    result = main()
    
    # Exit with appropriate code
    if result.get('success', False):
        sys.exit(0)
    else:
        sys.exit(1)
