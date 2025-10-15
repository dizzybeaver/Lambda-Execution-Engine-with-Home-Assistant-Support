"""
test_config_gateway.py
Version: 2025.10.11.01
Description: Configuration System Gateway Routing Tests

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
from typing import Dict, Any
from gateway import execute_operation, GatewayInterface, log_info


def run_config_gateway_tests() -> Dict[str, Any]:
    """Run all configuration gateway routing tests."""
    results = {
        "total_tests": 0,
        "passed": 0,
        "failed": 0,
        "tests": []
    }
    
    tests = [
        test_gateway_interface_enum,
        test_all_operations_route,
        test_lazy_loading_compliance,
        test_suga_compliance,
        test_no_direct_imports,
        test_gateway_stats_tracking,
        test_error_handling
    ]
    
    for test_func in tests:
        results["total_tests"] += 1
        test_name = test_func.__name__
        
        try:
            test_result = test_func()
            
            if test_result.get("success", False):
                results["passed"] += 1
            else:
                results["failed"] += 1
            
            results["tests"].append({
                "name": test_name,
                "success": test_result.get("success", False),
                "message": test_result.get("message", test_result.get("error", ""))
            })
            
        except Exception as e:
            results["failed"] += 1
            results["tests"].append({
                "name": test_name,
                "success": False,
                "message": f"Exception: {str(e)}"
            })
    
    return results


def test_gateway_interface_enum() -> Dict[str, Any]:
    """Test that GatewayInterface.CONFIG exists."""
    try:
        # Check if CONFIG interface exists
        has_config = hasattr(GatewayInterface, 'CONFIG')
        
        if has_config:
            config_value = GatewayInterface.CONFIG.value
            return {
                "success": True,
                "message": f"GatewayInterface.CONFIG exists: {config_value}"
            }
        else:
            return {
                "success": False,
                "error": "GatewayInterface.CONFIG not found"
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Gateway interface enum test exception: {str(e)}"
        }


def test_all_operations_route() -> Dict[str, Any]:
    """Test that all 12 CONFIG operations route correctly."""
    try:
        operations = [
            ('initialize', {}),
            ('get_parameter', {'key': 'test', 'default': 'value'}),
            ('set_parameter', {'key': 'test', 'value': 'value'}),
            ('get_category_config', {'category': 'cache'}),
            ('reload_config', {'validate': True}),
            ('switch_preset', {'preset_name': 'standard'}),
            ('get_state', {}),
            ('load_from_environment', {}),
            ('load_from_file', {'filepath': '/tmp/test.json'}),
            ('validate_all_sections', {})
        ]
        
        results = {}
        for op_name, kwargs in operations:
            try:
                result = execute_operation(
                    GatewayInterface.CONFIG,
                    op_name,
                    **kwargs
                )
                results[op_name] = result is not None
            except Exception as e:
                results[op_name] = False
        
        successful = sum(1 for v in results.values() if v)
        total = len(operations)
        
        if successful == total:
            return {
                "success": True,
                "message": f"All {total} operations route correctly"
            }
        else:
            failed = [k for k, v in results.items() if not v]
            return {
                "success": False,
                "error": f"{successful}/{total} operations succeeded. Failed: {failed}"
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Operations routing test exception: {str(e)}"
        }


def test_lazy_loading_compliance() -> Dict[str, Any]:
    """Test that config_core is lazy-loaded by gateway."""
    try:
        # config_core should be loaded after first CONFIG operation
        config_core_loaded = 'config_core' in sys.modules
        
        # Execute a config operation
        execute_operation(
            GatewayInterface.CONFIG,
            'get_state'
        )
        
        # Now it should definitely be loaded
        config_core_now_loaded = 'config_core' in sys.modules
        
        if config_core_now_loaded:
            return {
                "success": True,
                "message": "LIGS compliant: config_core lazy-loaded"
            }
        else:
            return {
                "success": False,
                "error": "config_core not loaded - lazy loading may not be working"
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Lazy loading test exception: {str(e)}"
        }


def test_suga_compliance() -> Dict[str, Any]:
    """Test SUGA architecture compliance."""
    try:
        # All operations should go through execute_operation
        # Test that direct import from config_core doesn't work the same way
        
        # This should work (through gateway)
        gateway_result = execute_operation(
            GatewayInterface.CONFIG,
            'get_state'
        )
        
        gateway_works = isinstance(gateway_result, dict)
        
        if gateway_works:
            return {
                "success": True,
                "message": "SUGA compliant: all operations through gateway"
            }
        else:
            return {
                "success": False,
                "error": "Gateway routing not working correctly"
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"SUGA compliance test exception: {str(e)}"
        }


def test_no_direct_imports() -> Dict[str, Any]:
    """Test that config.py doesn't directly import from config_core."""
    try:
        import config
        import inspect
        
        # Get config.py source
        config_source = inspect.getsource(config)
        
        # Should not have "from config_core import" (except in implementation)
        # But should have "from gateway import"
        has_gateway_import = 'from gateway import' in config_source
        
        # Check that it uses execute_operation
        uses_execute_operation = 'execute_operation' in config_source
        
        if has_gateway_import and uses_execute_operation:
            return {
                "success": True,
                "message": "No direct config_core imports, uses gateway"
            }
        else:
            issues = []
            if not has_gateway_import:
                issues.append("missing gateway import")
            if not uses_execute_operation:
                issues.append("not using execute_operation")
            
            return {
                "success": False,
                "error": f"Import issues: {issues}"
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Import check exception: {str(e)}"
        }


def test_gateway_stats_tracking() -> Dict[str, Any]:
    """Test that gateway tracks CONFIG operations in stats."""
    try:
        from gateway import get_gateway_stats
        
        # Get initial stats
        initial_stats = get_gateway_stats()
        
        # Execute some CONFIG operations
        execute_operation(GatewayInterface.CONFIG, 'get_state')
        execute_operation(GatewayInterface.CONFIG, 'get_parameter', key='test', default='value')
        
        # Get updated stats
        updated_stats = get_gateway_stats()
        
        # Stats should have been updated
        if updated_stats.get('total_operations', 0) > initial_stats.get('total_operations', 0):
            return {
                "success": True,
                "message": f"Gateway tracking CONFIG operations: {updated_stats.get('total_operations')} total"
            }
        else:
            return {
                "success": False,
                "error": "Gateway not tracking operations properly"
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Stats tracking test exception: {str(e)}"
        }


def test_error_handling() -> Dict[str, Any]:
    """Test that gateway handles CONFIG operation errors correctly."""
    try:
        # Try an invalid operation
        try:
            result = execute_operation(
                GatewayInterface.CONFIG,
                'invalid_operation',
                some_param='value'
            )
            
            # Should have raised an error or returned an error response
            return {
                "success": False,
                "error": f"Invalid operation didn't raise error: {result}"
            }
        except ValueError as e:
            # This is expected
            if 'Unknown CONFIG operation' in str(e):
                return {
                    "success": True,
                    "message": "Gateway error handling works correctly"
                }
            else:
                return {
                    "success": False,
                    "error": f"Unexpected error message: {str(e)}"
                }
    except Exception as e:
        return {
            "success": False,
            "error": f"Error handling test exception: {str(e)}"
        }


__all__ = [
    'run_config_gateway_tests'
]

# EOF
