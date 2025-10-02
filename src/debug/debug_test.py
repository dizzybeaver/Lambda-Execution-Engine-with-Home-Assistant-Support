# Add this to debug_test.py - HA Extension Integration

def test_ha_extension_suite() -> Dict[str, Any]:
    """Test Home Assistant extension if available."""
    return execute_test_with_caching("ha_extension_suite", _test_ha_extension_suite_impl, ttl=120)

def _test_ha_extension_suite_impl() -> bool:
    """HA extension suite test implementation."""
    try:
        import ha_tests
        
        if not ha_tests.is_ha_extension_available():
            log_gateway.log_info("HA extension not available, skipping tests")
            return True
        
        suite_result = ha_tests.run_all_ha_tests()
        
        if suite_result.get('status') == 'skip':
            return True
        
        pass_rate = suite_result.get('pass_rate', 0)
        return pass_rate >= 80
        
    except ImportError:
        log_gateway.log_debug("ha_tests.py not available")
        return True
    except Exception as e:
        log_gateway.log_error(f"HA extension test suite failed: {e}")
        return False

def run_comprehensive_test_suite() -> Dict[str, Any]:
    """Run comprehensive test suite including HA extension."""
    correlation_id = utility.generate_correlation_id()
    start_time = time.time()
    
    log_gateway.log_info("Starting comprehensive test suite", correlation_id=correlation_id)
    
    test_categories = {
        'core_interfaces': run_all_interface_tests,
        'revolutionary_gateway': run_revolutionary_gateway_validation_suite,
        'system_integration': test_system_validation_integration,
        'production_readiness': test_production_readiness_integration,
        'ha_extension': test_ha_extension_suite
    }
    
    results = {}
    total_passed = 0
    total_failed = 0
    total_tests = 0
    
    for category, test_func in test_categories.items():
        try:
            result = test_func()
            results[category] = result
            
            if isinstance(result, dict):
                passed = result.get('passed', 0)
                failed = result.get('failed', 0)
                category_total = result.get('total_tests', 1)
                
                if result.get('status') == 'pass':
                    passed = 1
                    category_total = 1
                elif result.get('status') in ['fail', 'error']:
                    failed = 1
                    category_total = 1
                
                total_passed += passed
                total_failed += failed
                total_tests += category_total
            
        except Exception as e:
            results[category] = {
                'status': 'error',
                'error': str(e)
            }
            total_failed += 1
            total_tests += 1
    
    duration = time.time() - start_time
    
    summary = {
        'total_tests': total_tests,
        'passed': total_passed,
        'failed': total_failed,
        'pass_rate': (total_passed / total_tests) * 100 if total_tests > 0 else 0,
        'duration_seconds': duration,
        'correlation_id': correlation_id,
        'categories': results,
        'test_type': 'comprehensive_suite'
    }
    
    metrics.record_metric("comprehensive_test_suite", duration, dimensions={
        "total": total_tests,
        "passed": total_passed,
        "failed": total_failed,
        "correlation_id": correlation_id
    })
    
    log_gateway.log_info("Comprehensive test suite completed", **summary)
    
    return summary

def get_available_test_suites() -> Dict[str, Any]:
    """Get information about available test suites."""
    suites = {
        'core_interfaces': {
            'description': 'Core gateway interface tests',
            'test_count': 8,
            'available': True
        },
        'revolutionary_gateway': {
            'description': 'Revolutionary Gateway architecture validation',
            'test_count': 5,
            'available': True
        },
        'system_integration': {
            'description': 'System validation integration tests',
            'test_count': 1,
            'available': True
        },
        'production_readiness': {
            'description': 'Production readiness checklist',
            'test_count': 1,
            'available': True
        }
    }
    
    try:
        import ha_tests
        ha_info = ha_tests.get_ha_test_info()
        suites['ha_extension'] = ha_info
    except ImportError:
        suites['ha_extension'] = {
            'description': 'Home Assistant extension tests',
            'test_count': 0,
            'available': False,
            'reason': 'ha_tests.py not available'
        }
    
    return {
        'available_suites': suites,
        'total_suites': len(suites),
        'timestamp': time.time()
    }

def run_targeted_ha_tests(test_names: Optional[List[str]] = None) -> Dict[str, Any]:
    """Run specific HA tests by name."""
    try:
        import ha_tests
        
        if not ha_tests.is_ha_extension_available():
            return {
                'status': 'skip',
                'reason': 'HA extension not available',
                'timestamp': time.time()
            }
        
        available_tests = {
            'initialization': ha_tests.test_ha_extension_initialization,
            'assistant_name_validation': ha_tests.test_ha_assistant_name_validation,
            'configuration_retrieval': ha_tests.test_ha_configuration_retrieval,
            'assistant_name_retrieval': ha_tests.test_ha_assistant_name_retrieval,
            'status_check': ha_tests.test_ha_status_check,
            'diagnostic_info': ha_tests.test_ha_diagnostic_info,
            'cleanup': ha_tests.test_ha_cleanup,
            'environment_variables': ha_tests.test_ha_environment_variables,
            'cache_operations': ha_tests.test_ha_cache_operations,
            'response_formatting': ha_tests.test_ha_response_formatting
        }
        
        if test_names is None:
            test_names = list(available_tests.keys())
        
        results = {}
        passed = 0
        failed = 0
        
        for test_name in test_names:
            if test_name in available_tests:
                result = available_tests[test_name]()
                results[test_name] = result
                
                if result.get('status') == 'pass':
                    passed += 1
                else:
                    failed += 1
            else:
                results[test_name] = {
                    'status': 'error',
                    'error': f'Test {test_name} not found'
                }
                failed += 1
        
        return {
            'requested_tests': test_names,
            'executed_tests': len(results),
            'passed': passed,
            'failed': failed,
            'results': results,
            'timestamp': time.time()
        }
        
    except ImportError:
        return {
            'status': 'error',
            'error': 'ha_tests.py not available',
            'timestamp': time.time()
        }

# Update the existing run_all_interface_tests function to include HA
def run_all_interface_tests_with_extensions() -> Dict[str, Any]:
    """Run all interface tests including extension tests."""
    correlation_id = utility.generate_correlation_id()
    start_time = time.time()
    
    log_gateway.log_info("Starting interface tests with extensions", correlation_id=correlation_id)
    
    # Core interface tests
    core_result = run_all_interface_tests()
    
    # HA extension tests (if available)
    ha_result = test_ha_extension_suite()
    
    combined_results = {
        'core_interfaces': core_result,
        'ha_extension': ha_result
    }
    
    # Calculate combined statistics
    total_passed = core_result.get('passed', 0)
    total_failed = core_result.get('failed', 0)
    total_tests = core_result.get('total_tests', 0)
    
    if ha_result.get('status') == 'pass':
        total_passed += 1
        total_tests += 1
    elif ha_result.get('status') in ['fail', 'error']:
        total_failed += 1
        total_tests += 1
    
    duration = time.time() - start_time
    
    summary = {
        'total_tests': total_tests,
        'passed': total_passed,
        'failed': total_failed,
        'pass_rate': (total_passed / total_tests) * 100 if total_tests > 0 else 0,
        'duration_seconds': duration,
        'correlation_id': correlation_id,
        'results': combined_results,
        'test_type': 'interface_with_extensions'
    }
    
    log_gateway.log_info("Interface tests with extensions completed", **summary)
    
    return summary
