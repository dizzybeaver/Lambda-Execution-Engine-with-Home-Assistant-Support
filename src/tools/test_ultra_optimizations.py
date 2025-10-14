"""
test_ultra_optimizations.py
Version: 2025.10.13.01
Description: Comprehensive tests for Phase 2 ultra-optimizations

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

from typing import Dict, Any


# ===== GATEWAY WRAPPER TESTS =====

def test_gateway_wrapper_basic() -> Dict[str, Any]:
    """Test basic gateway wrapper functionality."""
    try:
        from gateway_wrapper import execute_generic_operation, get_wrapper_stats
        from gateway import GatewayInterface
        
        # Execute test operation
        result = execute_generic_operation(
            GatewayInterface.CACHE,
            'get',
            key='test_key'
        )
        
        # Check stats
        stats = get_wrapper_stats()
        
        return {
            'success': True,
            'stats': stats,
            'message': 'Gateway wrapper basic test passed'
        }
    
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def test_gateway_wrapper_caching() -> Dict[str, Any]:
    """Test gateway wrapper implementation caching."""
    try:
        from gateway_wrapper import (
            execute_generic_operation,
            get_wrapper_stats,
            reset_stats,
            clear_implementation_cache
        )
        from gateway import GatewayInterface
        
        # Reset for clean test
        reset_stats()
        clear_implementation_cache()
        
        # First call - cache miss
        execute_generic_operation(GatewayInterface.CACHE, 'get', key='test1')
        stats1 = get_wrapper_stats()
        
        # Second call - cache hit
        execute_generic_operation(GatewayInterface.CACHE, 'get', key='test2')
        stats2 = get_wrapper_stats()
        
        cache_working = stats2['cache_hits'] > stats1['cache_hits']
        
        return {
            'success': cache_working,
            'cache_hits': stats2['cache_hits'],
            'hit_rate': stats2['hit_rate_percent'],
            'message': 'Gateway wrapper caching validated'
        }
    
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


# ===== IMPORT FIXER TESTS =====

def test_import_fixer_scan() -> Dict[str, Any]:
    """Test import fixer scanning capabilities."""
    try:
        from import_fixer import check_imports
        
        results = check_imports('.', report=False)
        
        return {
            'success': True,
            'compliant': results['compliant'],
            'violations': len(results['violations']),
            'statistics': results['statistics'],
            'message': 'Import fixer scan completed'
        }
    
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def test_import_compliance() -> Dict[str, Any]:
    """Test that all files are AWS Lambda compatible."""
    try:
        from import_fixer import get_import_statistics
        
        stats = get_import_statistics('.')
        
        compliant = stats['compliance_rate_percent'] == 100.0
        
        return {
            'success': compliant,
            'compliance_rate': stats['compliance_rate_percent'],
            'clean_files': stats['clean_files'],
            'total_files': stats['total_python_files'],
            'message': 'Import compliance validated' if compliant else 'Import violations detected'
        }
    
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


# ===== DEBUG UNIFIED TESTS =====

def test_debug_health_checks() -> Dict[str, Any]:
    """Test debug unified health checking."""
    try:
        from debug_unified import check_all_components, check_gateway_health
        
        # Check all components
        components = check_all_components()
        
        # Check gateway specifically
        gateway = check_gateway_health()
        
        return {
            'success': True,
            'components': components.get('status', 'unknown'),
            'gateway': gateway.get('overall_status', 'unknown'),
            'message': 'Debug health checks completed'
        }
    
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def test_debug_diagnostics() -> Dict[str, Any]:
    """Test debug diagnostics functionality."""
    try:
        from debug_unified import run_full_diagnostics, diagnose_performance
        
        # Run diagnostics
        diagnostics = run_full_diagnostics()
        performance = diagnose_performance()
        
        return {
            'success': True,
            'diagnostics_status': diagnostics.get('status', 'unknown'),
            'performance_status': performance.get('status', 'unknown'),
            'message': 'Debug diagnostics completed'
        }
    
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


# ===== VALIDATION WRAPPER TESTS =====

def test_validation_basic() -> Dict[str, Any]:
    """Test basic validation functions."""
    try:
        from validation_wrapper import (
            validate_required,
            validate_type,
            validate_range,
            ValidationError
        )
        
        tests_passed = 0
        
        # Test required validation
        try:
            validate_required("value", "test_field")
            tests_passed += 1
        except ValidationError:
            pass
        
        # Test type validation
        try:
            validate_type("string", str, "test_field")
            tests_passed += 1
        except ValidationError:
            pass
        
        # Test range validation
        try:
            validate_range(50, 0, 100, "test_field")
            tests_passed += 1
        except ValidationError:
            pass
        
        return {
            'success': tests_passed == 3,
            'tests_passed': tests_passed,
            'message': f'{tests_passed}/3 validation tests passed'
        }
    
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def test_validation_decorators() -> Dict[str, Any]:
    """Test validation decorators."""
    try:
        from validation_wrapper import validate_params, validate_required
        
        @validate_params(
            key=lambda v: validate_required(v, 'key')
        )
        def test_function(key, value=None):
            return True
        
        # Test with valid params
        result1 = test_function(key='valid_key')
        
        # Test invalid params should raise
        try:
            test_function(key=None)
            decorator_working = False
        except:
            decorator_working = True
        
        return {
            'success': result1 and decorator_working,
            'message': 'Validation decorators working'
        }
    
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


# ===== FAST PATH OPTIMIZER TESTS =====

def test_fast_path_basic() -> Dict[str, Any]:
    """Test fast-path optimizer basic functionality."""
    try:
        from fast_path_optimizer import (
            execute_fast_path,
            get_fast_path_stats,
            reset_stats
        )
        
        reset_stats()
        
        # Execute test operations
        def test_op():
            return "result"
        
        for i in range(15):
            execute_fast_path('test_operation', test_op)
        
        stats = get_fast_path_stats()
        
        return {
            'success': True,
            'total_calls': stats['total_calls'],
            'fast_path_hits': stats['fast_path_hits'],
            'hit_rate': stats['hit_rate_percent'],
            'message': 'Fast-path optimizer working'
        }
    
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def test_fast_path_prewarming() -> Dict[str, Any]:
    """Test fast-path cache prewarming."""
    try:
        from fast_path_optimizer import (
            prewarm_common_operations,
            get_cached_operations,
            clear_fast_path_cache
        )
        
        # Clear and prewarm
        clear_fast_path_cache()
        prewarm_common_operations()
        
        cached = get_cached_operations()
        
        return {
            'success': len(cached) > 0,
            'prewarmed_operations': len(cached),
            'operations': cached,
            'message': 'Fast-path prewarming working'
        }
    
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


# ===== BATCH OPERATIONS TESTS =====

def test_batch_execution() -> Dict[str, Any]:
    """Test basic batch execution."""
    try:
        from batch_operations import execute_batch
        from gateway import GatewayInterface
        
        operations = [
            {
                'interface': GatewayInterface.CACHE,
                'operation': 'get',
                'params': {'key': 'test1'}
            },
            {
                'interface': GatewayInterface.METRICS,
                'operation': 'get_metrics',
                'params': {}
            }
        ]
        
        results = execute_batch(operations)
        
        return {
            'success': len(results) == 2,
            'operations_executed': len(results),
            'message': 'Batch execution working'
        }
    
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def test_batch_builder() -> Dict[str, Any]:
    """Test batch builder pattern."""
    try:
        from batch_operations import BatchBuilder
        
        results = (BatchBuilder()
            .add_cache_get('key1')
            .add_log_info('test message')
            .add_record_metric('test_metric', 1.0)
            .execute())
        
        return {
            'success': len(results) == 3,
            'operations_executed': len(results),
            'message': 'Batch builder working'
        }
    
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


# ===== INTEGRATION TESTS =====

def test_full_optimization_stack() -> Dict[str, Any]:
    """Test full optimization stack integration."""
    try:
        from gateway_wrapper import execute_generic_operation
        from fast_path_optimizer import execute_fast_path
        from batch_operations import BatchBuilder
        from validation_wrapper import validate_required
        from gateway import GatewayInterface
        
        # Test generic dispatch
        result1 = execute_generic_operation(
            GatewayInterface.CACHE,
            'get',
            key='test'
        )
        
        # Test fast-path
        def test_func():
            return True
        result2 = execute_fast_path('test_op', test_func)
        
        # Test batch
        result3 = (BatchBuilder()
            .add_cache_get('key')
            .execute())
        
        # Test validation
        validate_required('value', 'field')
        
        return {
            'success': True,
            'message': 'Full optimization stack integrated successfully'
        }
    
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


# ===== TEST RUNNER =====

def run_all_optimization_tests() -> Dict[str, Any]:
    """Run all Phase 2 optimization tests."""
    
    test_suite = [
        ('Gateway Wrapper Basic', test_gateway_wrapper_basic),
        ('Gateway Wrapper Caching', test_gateway_wrapper_caching),
        ('Import Fixer Scan', test_import_fixer_scan),
        ('Import Compliance', test_import_compliance),
        ('Debug Health Checks', test_debug_health_checks),
        ('Debug Diagnostics', test_debug_diagnostics),
        ('Validation Basic', test_validation_basic),
        ('Validation Decorators', test_validation_decorators),
        ('Fast Path Basic', test_fast_path_basic),
        ('Fast Path Prewarming', test_fast_path_prewarming),
        ('Batch Execution', test_batch_execution),
        ('Batch Builder', test_batch_builder),
        ('Full Stack Integration', test_full_optimization_stack)
    ]
    
    results = {}
    passed = 0
    failed = 0
    
    for test_name, test_func in test_suite:
        try:
            result = test_func()
            results[test_name] = result
            
            if result.get('success'):
                passed += 1
            else:
                failed += 1
        
        except Exception as e:
            results[test_name] = {
                'success': False,
                'error': str(e)
            }
            failed += 1
    
    return {
        'total_tests': len(test_suite),
        'passed': passed,
        'failed': failed,
        'success_rate': round((passed / len(test_suite)) * 100, 2),
        'results': results,
        'overall_success': failed == 0
    }


# ===== EXPORTED FUNCTIONS =====

__all__ = [
    'test_gateway_wrapper_basic',
    'test_gateway_wrapper_caching',
    'test_import_fixer_scan',
    'test_import_compliance',
    'test_debug_health_checks',
    'test_debug_diagnostics',
    'test_validation_basic',
    'test_validation_decorators',
    'test_fast_path_basic',
    'test_fast_path_prewarming',
    'test_batch_execution',
    'test_batch_builder',
    'test_full_optimization_stack',
    'run_all_optimization_tests'
]

# EOF
