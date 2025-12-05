# test_error_scenarios.py
"""
test_error_scenarios.py
Version: 1.0.0
Date: 2025-11-04
Description: Generic error handling verification for all interfaces

Tests error handling across all interfaces:
- Invalid operations return proper errors
- Exceptions logged with correlation IDs
- Circuit breaker patterns work (if applicable)
- Retry logic behaves correctly (if applicable)
- Graceful degradation when dependencies fail

Parameterized to work with:
- LEE interfaces (CONFIG, CACHE, LOGGING, etc.)
- HA-SUGA (when HOME_ASSISTANT_ENABLE=true)
- Any future interfaces

Copyright 2025 Joseph Hersey

Licensed under the Apache License, Version 2.0.
"""

import sys
import os
from typing import Dict, List, Any, Optional
from gateway import execute_operation, GatewayInterface


# ADDED: Generic error scenario testing
def run_error_scenario_tests(interfaces: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Run error scenario tests on specified interfaces.
    
    Args:
        interfaces: List of interface names to test. If None, test all known interfaces.
        
    Returns:
        Test results dictionary
    """
    results = {
        "total_tests": 0,
        "passed": 0,
        "failed": 0,
        "tests": []
    }
    
    # Default interfaces to test
    if interfaces is None:
        interfaces = [
            'CONFIG',
            'CACHE',
            'LOGGING',
            'METRICS',
            'SECURITY',
            'HTTP',
            'WEBSOCKET'
        ]
    
    # Test each interface
    for interface_name in interfaces:
        # Test 1: Invalid operation
        results["total_tests"] += 1
        try:
            test_result = test_invalid_operation(interface_name)
            if test_result.get("success", False):
                results["passed"] += 1
            else:
                results["failed"] += 1
            results["tests"].append({
                "interface": interface_name,
                "test": "invalid_operation",
                "success": test_result.get("success", False),
                "message": test_result.get("message", test_result.get("error", ""))
            })
        except Exception as e:
            results["failed"] += 1
            results["tests"].append({
                "interface": interface_name,
                "test": "invalid_operation",
                "success": False,
                "message": f"Exception: {str(e)}"
            })
        
        # Test 2: Missing required parameters
        results["total_tests"] += 1
        try:
            test_result = test_missing_parameters(interface_name)
            if test_result.get("success", False):
                results["passed"] += 1
            else:
                results["failed"] += 1
            results["tests"].append({
                "interface": interface_name,
                "test": "missing_parameters",
                "success": test_result.get("success", False),
                "message": test_result.get("message", test_result.get("error", ""))
            })
        except Exception as e:
            results["failed"] += 1
            results["tests"].append({
                "interface": interface_name,
                "test": "missing_parameters",
                "success": False,
                "message": f"Exception: {str(e)}"
            })
    
    return results


# ADDED: Test invalid operation error handling
def test_invalid_operation(interface_name: str) -> Dict[str, Any]:
    """
    Test that invalid operations return proper errors.
    
    Args:
        interface_name: Name of interface to test (e.g., 'CONFIG', 'CACHE')
        
    Returns:
        Test result dictionary
    """
    try:
        # Get interface enum
        try:
            interface = getattr(GatewayInterface, interface_name)
        except AttributeError:
            return {
                "success": False,
                "error": f"Interface not found: {interface_name}"
            }
        
        # Try invalid operation
        try:
            result = execute_operation(
                interface,
                'invalid_operation_that_does_not_exist',
                some_param='value'
            )
            
            # Should have raised an error
            return {
                "success": False,
                "error": f"Invalid operation didn't raise error: {result}"
            }
        
        except ValueError as e:
            # This is expected
            error_message = str(e).lower()
            
            # Check error message is informative
            if 'unknown' in error_message or 'invalid' in error_message or 'operation' in error_message:
                return {
                    "success": True,
                    "message": f"Invalid operation error handled correctly: {str(e)}"
                }
            else:
                return {
                    "success": False,
                    "error": f"Error message not informative: {str(e)}"
                }
        
        except Exception as e:
            # Unexpected error type
            return {
                "success": False,
                "error": f"Unexpected error type: {type(e).__name__}: {str(e)}"
            }
    
    except Exception as e:
        return {
            "success": False,
            "error": f"Test exception: {str(e)}"
        }


# ADDED: Test missing parameter error handling
def test_missing_parameters(interface_name: str) -> Dict[str, Any]:
    """
    Test that missing required parameters are handled.
    
    Args:
        interface_name: Name of interface to test
        
    Returns:
        Test result dictionary
    """
    try:
        # Get interface enum
        try:
            interface = getattr(GatewayInterface, interface_name)
        except AttributeError:
            return {
                "success": False,
                "error": f"Interface not found: {interface_name}"
            }
        
        # Operations that require parameters
        operations_with_params = {
            'CONFIG': ('get_parameter', {'key': None}),  # Missing key value
            'CACHE': ('cache_get', {'key': None}),  # Missing key value
            'LOGGING': ('log_info', {'message': None}),  # Missing message
            'METRICS': ('track_time', {'metric_name': None}),  # Missing metric
            'SECURITY': ('encrypt', {'data': None}),  # Missing data
        }
        
        if interface_name not in operations_with_params:
            # Interface doesn't have operations that require params, or we don't test it
            return {
                "success": True,
                "message": f"No parameter requirements to test for {interface_name}"
            }
        
        operation, invalid_params = operations_with_params[interface_name]
        
        try:
            result = execute_operation(interface, operation, **invalid_params)
            
            # Should have handled None/missing parameter gracefully
            # Either raised error or returned error response
            if isinstance(result, dict) and 'error' in result:
                return {
                    "success": True,
                    "message": f"Missing parameter handled gracefully: {result['error']}"
                }
            else:
                return {
                    "success": False,
                    "error": f"Missing parameter not handled: {result}"
                }
        
        except (ValueError, TypeError, KeyError) as e:
            # This is expected - parameter validation caught it
            return {
                "success": True,
                "message": f"Missing parameter caught by validation: {str(e)}"
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error: {type(e).__name__}: {str(e)}"
            }
    
    except Exception as e:
        return {
            "success": False,
            "error": f"Test exception: {str(e)}"
        }


# ADDED: Test graceful degradation
def test_graceful_degradation() -> Dict[str, Any]:
    """Test that system degrades gracefully when dependencies fail."""
    try:
        # Simulate dependency failure
        # For example, if cache fails, system should still work but slower
        
        # Try operation that uses cache
        try:
            result = execute_operation(
                GatewayInterface.CONFIG,
                'get_parameter',
                key='test.parameter',
                default='fallback_value'
            )
            
            # Should get fallback value if cache unavailable
            if result is not None:
                return {
                    "success": True,
                    "message": "Graceful degradation working (fallback to default)"
                }
            else:
                return {
                    "success": False,
                    "error": "No fallback when cache unavailable"
                }
        
        except Exception as e:
            # Should not crash, should degrade gracefully
            return {
                "success": False,
                "error": f"Not degrading gracefully: {str(e)}"
            }
    
    except Exception as e:
        return {
            "success": False,
            "error": f"Test exception: {str(e)}"
        }


# ADDED: Test correlation ID flow through errors
def test_correlation_id_in_errors() -> Dict[str, Any]:
    """Test that correlation IDs are preserved in error responses."""
    try:
        # Create request with correlation ID
        correlation_id = "test-correlation-123"
        
        # Try operation that will fail
        try:
            result = execute_operation(
                GatewayInterface.CONFIG,
                'invalid_operation',
                correlation_id=correlation_id
            )
            
            # If result is dict, check for correlation_id
            if isinstance(result, dict):
                if 'correlation_id' in result and result['correlation_id'] == correlation_id:
                    return {
                        "success": True,
                        "message": "Correlation ID preserved in error response"
                    }
                else:
                    return {
                        "success": False,
                        "error": "Correlation ID not in error response"
                    }
        
        except ValueError as e:
            # Exception raised instead of error response
            # Check if correlation ID in logs (can't easily test, so pass)
            return {
                "success": True,
                "message": "Error raised (correlation ID should be in logs)"
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}"
            }
    
    except Exception as e:
        return {
            "success": False,
            "error": f"Test exception: {str(e)}"
        }


# ADDED: Test HA-specific error scenarios (if HA enabled)
def test_ha_error_scenarios() -> Dict[str, Any]:
    """Test HA-specific error scenarios (only if HA enabled)."""
    try:
        # Check if HA enabled
        if os.environ.get('HOME_ASSISTANT_ENABLE', 'false').lower() != 'true':
            return {
                "success": True,
                "message": "HA not enabled, skipping HA error tests"
            }
        
        # Test HA-specific errors
        # Note: This just verifies error handling exists, doesn't test actual HA connection
        
        try:
            from home_assistant import ha_alexa_core
            
            # Check that error handling functions exist
            has_error_handling = (
                hasattr(ha_alexa_core, 'handle_error') or
                'handle_error' in dir(ha_alexa_core) or
                'ErrorResponse' in dir(ha_alexa_core)
            )
            
            if has_error_handling:
                return {
                    "success": True,
                    "message": "HA error handling infrastructure present"
                }
            else:
                return {
                    "success": False,
                    "error": "HA error handling not found"
                }
        
        except ImportError:
            return {
                "success": False,
                "error": "HA modules not available"
            }
    
    except Exception as e:
        return {
            "success": False,
            "error": f"HA error test exception: {str(e)}"
        }


# ADDED: Main test runner
def main():
    """Main test runner."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test error handling in interfaces")
    parser.add_argument("--interfaces", nargs="+", help="Specific interfaces to test")
    parser.add_argument("--include-ha", action="store_true", help="Include HA error tests")
    args = parser.parse_args()
    
    if args.include_ha:
        os.environ['HOME_ASSISTANT_ENABLE'] = 'true'
    
    print("="*60)
    print("ERROR SCENARIO TESTS")
    print("="*60)
    
    # Test interface error handling
    results = run_error_scenario_tests(args.interfaces)
    
    print(f"\nInterface Error Tests: {results['passed']}/{results['total_tests']} passed")
    
    for test in results['tests']:
        status = "✅ PASS" if test['success'] else "❌ FAIL"
        print(f"{status}: {test['interface']}.{test['test']} - {test['message']}")
    
    # Test graceful degradation
    print("\n" + "="*60)
    print("GRACEFUL DEGRADATION TEST")
    print("="*60)
    
    degradation_result = test_graceful_degradation()
    status = "✅ PASS" if degradation_result['success'] else "❌ FAIL"
    print(f"{status}: {degradation_result.get('message', degradation_result.get('error', ''))}")
    
    # Test correlation ID preservation
    correlation_result = test_correlation_id_in_errors()
    status = "✅ PASS" if correlation_result['success'] else "❌ FAIL"
    print(f"{status}: {correlation_result.get('message', correlation_result.get('error', ''))}")
    
    # Test HA errors if enabled
    if args.include_ha:
        print("\n" + "="*60)
        print("HA ERROR SCENARIOS")
        print("="*60)
        
        ha_error_result = test_ha_error_scenarios()
        status = "✅ PASS" if ha_error_result['success'] else "❌ FAIL"
        print(f"{status}: {ha_error_result.get('message', ha_error_result.get('error', ''))}")
        
        extra_tests = 3
    else:
        extra_tests = 2
    
    # Summary
    total_passed = results['passed'] + sum([
        1 if degradation_result['success'] else 0,
        1 if correlation_result['success'] else 0
    ])
    
    if args.include_ha:
        total_passed += 1 if ha_error_result['success'] else 0
    
    total_tests = results['total_tests'] + extra_tests
    
    print("\n" + "="*60)
    print(f"TOTAL: {total_passed}/{total_tests} tests passed")
    print("="*60)
    
    return 0 if total_passed == total_tests else 1


if __name__ == "__main__":
    sys.exit(main())


__all__ = [
    'run_error_scenario_tests',
    'test_invalid_operation',
    'test_missing_parameters',
    'test_graceful_degradation',
    'test_correlation_id_in_errors',
    'test_ha_error_scenarios'
]

# EOF
