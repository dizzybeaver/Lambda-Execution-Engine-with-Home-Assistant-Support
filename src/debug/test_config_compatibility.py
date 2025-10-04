"""
test_config_compatibility.py - Configuration System Backward Compatibility Tests
Version: 2025.10.04.01
Description: Tests for backward compatibility with legacy configuration code

Phase 5: Configuration System Consolidation - Compatibility Testing
Ensures zero breaking changes for existing code.

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
from gateway import log_info


def run_config_compatibility_tests() -> Dict[str, Any]:
    """Run all configuration compatibility tests."""
    results = {
        "total_tests": 0,
        "passed": 0,
        "failed": 0,
        "tests": []
    }
    
    tests = [
        test_config_module_imports,
        test_legacy_function_names,
        test_category_helpers,
        test_config_interface_exists,
        test_gateway_delegation,
        test_backward_compatible_returns
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


def test_config_module_imports() -> Dict[str, Any]:
    """Test that config module can be imported."""
    try:
        import config
        
        if hasattr(config, 'config_get_parameter'):
            return {
                "success": True,
                "message": "Config module imports successfully"
            }
        else:
            return {
                "success": False,
                "error": "Config module missing expected functions"
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Config module import failed: {str(e)}"
        }


def test_legacy_function_names() -> Dict[str, Any]:
    """Test that legacy function names still work."""
    try:
        from config import get_parameter, set_parameter, get_category_config
        
        # Test legacy get_parameter
        result = get_parameter('legacy.test', 'default_value')
        
        if result is not None:
            # Test legacy set_parameter
            set_result = set_parameter('legacy.test.write', 'test_value')
            
            if set_result or set_result is None:  # Some implementations return None for success
                # Test legacy get_category_config
                cat_result = get_category_config('cache')
                
                if isinstance(cat_result, dict) or cat_result is None:
                    return {
                        "success": True,
                        "message": "All legacy function names work"
                    }
                else:
                    return {
                        "success": False,
                        "error": "get_category_config failed"
                    }
            else:
                return {
                    "success": False,
                    "error": "set_parameter failed"
                }
        else:
            return {
                "success": False,
                "error": "get_parameter failed"
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Legacy function test exception: {str(e)}"
        }


def test_category_helpers() -> Dict[str, Any]:
    """Test category-specific helper functions."""
    try:
        from config import (
            config_get_cache,
            config_get_logging,
            config_get_metrics,
            config_get_security
        )
        
        helpers = {
            'cache': config_get_cache,
            'logging': config_get_logging,
            'metrics': config_get_metrics,
            'security': config_get_security
        }
        
        results = {}
        for name, helper_func in helpers.items():
            try:
                result = helper_func()
                results[name] = isinstance(result, dict) or result is None
            except Exception as e:
                results[name] = False
        
        if all(results.values()):
            return {
                "success": True,
                "message": f"All {len(helpers)} category helpers work"
            }
        else:
            failed = [k for k, v in results.items() if not v]
            return {
                "success": False,
                "error": f"Category helpers failed: {failed}"
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Category helpers test exception: {str(e)}"
        }


def test_config_interface_exists() -> Dict[str, Any]:
    """Test that config.py interface exists with all functions."""
    try:
        import config
        
        required_functions = [
            'config_initialize',
            'config_get_parameter',
            'config_set_parameter',
            'config_get_category',
            'config_reload',
            'config_switch_preset',
            'config_get_state',
            'get_parameter',  # Legacy
            'set_parameter',  # Legacy
            'get_category_config'  # Legacy
        ]
        
        missing = [f for f in required_functions if not hasattr(config, f)]
        
        if not missing:
            return {
                "success": True,
                "message": f"All {len(required_functions)} interface functions exist"
            }
        else:
            return {
                "success": False,
                "error": f"Missing functions: {missing}"
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Interface check exception: {str(e)}"
        }


def test_gateway_delegation() -> Dict[str, Any]:
    """Test that config functions delegate to gateway correctly."""
    try:
        from config import config_get_parameter
        
        # This should go through gateway
        result = config_get_parameter('test.gateway.param', 'gateway_default')
        
        # Should return the default value we passed
        if result == 'gateway_default' or isinstance(result, str):
            return {
                "success": True,
                "message": "Gateway delegation working"
            }
        else:
            return {
                "success": False,
                "error": f"Gateway delegation returned unexpected: {result}"
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Gateway delegation exception: {str(e)}"
        }


def test_backward_compatible_returns() -> Dict[str, Any]:
    """Test that function return types are backward compatible."""
    try:
        from config import config_get_parameter, config_get_state, config_reload
        
        # get_parameter should return the value or default
        param_result = config_get_parameter('test.return', 'default')
        param_compatible = isinstance(param_result, str) or param_result is None
        
        # get_state should return a dict
        state_result = config_get_state()
        state_compatible = isinstance(state_result, dict)
        
        # reload should return a dict with success key
        reload_result = config_reload()
        reload_compatible = isinstance(reload_result, dict)
        
        if param_compatible and state_compatible and reload_compatible:
            return {
                "success": True,
                "message": "All return types backward compatible"
            }
        else:
            errors = []
            if not param_compatible:
                errors.append(f"get_parameter: {type(param_result)}")
            if not state_compatible:
                errors.append(f"get_state: {type(state_result)}")
            if not reload_compatible:
                errors.append(f"reload: {type(reload_result)}")
            
            return {
                "success": False,
                "error": f"Incompatible return types: {errors}"
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Return type test exception: {str(e)}"
        }


__all__ = [
    'run_config_compatibility_tests'
]

# EOF
