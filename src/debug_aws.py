"""
debug_aws.py - AWS Lambda Debug Test Interface
Version: 2025.10.14.01
Description: AWS-specific test interface with CLI and Lambda handler

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
import argparse
from typing import Dict, Any, List

from gateway import (
    log_info, create_success_response, create_error_response, generate_correlation_id
)
from shared_utilities import handle_operation_error, create_operation_context, close_operation_context
from debug import execute_debug_operation, health_check, diagnostics, run_tests, analyze_system, DebugOperation


class AWSTestProgram:
    """AWS test program interface."""
    
    def __init__(self):
        self.correlation_id = generate_correlation_id()
        
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
        """Create argument parser."""
        parser = argparse.ArgumentParser(description='AWS Lambda Debug Test Interface')
        subparsers = parser.add_subparsers(dest='command')
        
        # Health command
        health_parser = subparsers.add_parser('health')
        health_parser.add_argument('--component', help='Component to check')
        
        # Test command
        test_parser = subparsers.add_parser('test')
        test_parser.add_argument('--type', default='comprehensive')
        test_parser.add_argument('--iterations', type=int, default=1000)
        test_parser.add_argument('--verbose', action='store_true')
        
        # Analyze command
        analyze_parser = subparsers.add_parser('analyze')
        analyze_parser.add_argument('--architecture', action='store_true')
        analyze_parser.add_argument('--imports', action='store_true')
        
        # Benchmark command
        benchmark_parser = subparsers.add_parser('benchmark')
        benchmark_parser.add_argument('--iterations', type=int, default=1000)
        
        # Diagnostics command
        diag_parser = subparsers.add_parser('diagnostics')
        diag_parser.add_argument('--full', action='store_true')
        
        return parser
    
    def _execute_command(self, args) -> Dict[str, Any]:
        """Execute command."""
        if args.command == 'health':
            result = health_check()
        elif args.command == 'test':
            result = run_tests(args.type)
        elif args.command == 'analyze':
            if args.architecture:
                result = execute_debug_operation(DebugOperation.VALIDATE_SYSTEM_ARCHITECTURE)
            elif args.imports:
                result = execute_debug_operation(DebugOperation.VALIDATE_IMPORTS)
            else:
                result = analyze_system()
        elif args.command == 'benchmark':
            result = execute_debug_operation(DebugOperation.RUN_PERFORMANCE_BENCHMARK, iterations=args.iterations)
        elif args.command == 'diagnostics':
            result = diagnostics() if not args.full else execute_debug_operation(DebugOperation.GENERATE_HEALTH_REPORT)
        else:
            return create_error_response(f"Unknown command: {args.command}")
        
        return create_success_response(f"{args.command} completed", result)


def main(args: List[str] = None) -> Dict[str, Any]:
    """Main CLI entry point."""
    if args is None:
        args = sys.argv[1:]
    
    program = AWSTestProgram()
    return program.run_program(args)


def lambda_handler(event: Dict[str, Any], context) -> Dict[str, Any]:
    """AWS Lambda handler."""
    command = event.get('command', 'health')
    args = event.get('args', [])
    
    if isinstance(command, str):
        args = [command] + (args if isinstance(args, list) else [])
    
    return main(args)


def run_quick_health() -> Dict[str, Any]:
    """Quick health check."""
    return health_check()


def run_quick_test() -> Dict[str, Any]:
    """Quick test."""
    return run_tests('performance')


def run_comprehensive_suite() -> Dict[str, Any]:
    """Comprehensive test suite."""
    results = {}
    operations = [
        ('health', ['health']),
        ('tests', ['test']),
        ('analysis', ['analyze', '--architecture']),
        ('benchmark', ['benchmark']),
        ('diagnostics', ['diagnostics', '--full'])
    ]
    
    for name, args in operations:
        try:
            results[name] = main(args)
        except Exception as e:
            results[name] = {'error': str(e)}
    
    return results


__all__ = [
    'main',
    'lambda_handler',
    'run_quick_health',
    'run_quick_test',
    'run_comprehensive_suite',
    'AWSTestProgram'
]

# EOF
