"""
test_config_integration.py - Configuration System Integration Tests
Version: 2025.10.04.01
Description: Integration tests for multi-source configuration loading

Phase 5: Configuration System Consolidation - Integration Testing
Tests configuration loading from multiple sources and integration.

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

import os
from typing import Dict, Any
from gateway import execute_operation, GatewayInterface, log_info


def run_config_integration_tests() -> Dict[str, Any]:
    """Run all configuration integration tests."""
    results = {
        "total_tests": 0,
        "passed": 0,
        "failed": 0,
        "tests": []
    }
    
    tests = [
        test_environment_to_config,
        test_file_to_config,
        test_parameter_persistence,
        test_category_config_access,
        test_preset_switching_integration,
        test_reload_with_validation,
        test_state_tracking,
        test_multi_source_loading
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


def test_environment_to_config() -> Dict[str, Any]:
    """Test loading configuration from environment variables."""
    try:
        # Set test environment variable
        os.environ['TEST_CONFIG_VALUE'] = 'test123'
        
        # Load from environment
        env_config = execute_operation(
            GatewayInterface.CONFIG,
            'load_from_environment'
        )
        
        # Clean up
        if 'TEST_CONFIG_VALUE' in os.environ:
            del os.environ['TEST_CONFIG_VALUE']
        
        if isinstance(env_config, dict):
            return {
                "success": True,
                "message": f"Environment loading successful: {len(env_config)} variables"
            }
        else:
            return {
                "success": False,
                "error": "Environment loading failed"
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Environment test exception: {str(e)}"
        }


def test_file_to_config() -> Dict[str, Any]:
    """Test loading configuration from file."""
    try:
        # Test with non-existent file
        file_config = execute_operation(
            GatewayInterface.CONFIG,
            'load_from_file',
            filepath='/tmp/test_config.json'
        )
        
        if isinstance(file_config, dict):
            return {
                "success": True,
                "message": "File loading handled gracefully"
            }
        else:
            return {
                "success": False,
                "error": "File loading failed"
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"File test exception: {str(e)}"
        }


def test_parameter_persistence() -> Dict[str, Any]:
    """Test parameter set/get persistence."""
    try:
        # Set a parameter
        set_result = execute_operation(
            GatewayInterface.CONFIG,
            'set_parameter',
            key='integration.test.param',
            value='integration_value'
        )
        
        if not set_result:
            return {
                "success": False,
                "error": "Parameter set failed"
            }
        
        # Get the parameter back
        get_result = execute_operation(
            GatewayInterface.CONFIG,
            'get_parameter',
            key='integration.test.param',
            default=None
        )
        
        if get_result == 'integration_value':
            return {
                "success": True,
                "message": "Parameter persistence verified"
            }
        else:
            return {
                "success": False,
                "error": f"Parameter not persisted: got {get_result}"
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Persistence test exception: {str(e)}"
        }


def test_category_config_access() -> Dict[str, Any]:
    """Test accessing configuration by category."""
    try:
        categories = ['cache', 'logging', 'metrics', 'security']
        results = {}
        
        for category in categories:
            cat_config = execute_operation(
                GatewayInterface.CONFIG,
                'get_category_config',
                category=category
            )
            results[category] = isinstance(cat_config, dict)
        
        if all(results.values()):
            return {
                "success": True,
                "message": f"All {len(categories)} categories accessible"
            }
        else:
            failed = [k for k, v in results.items() if not v]
            return {
                "success": False,
                "error": f"Categories failed: {failed}"
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Category access exception: {str(e)}"
        }


def test_preset_switching_integration() -> Dict[str, Any]:
    """Test switching between presets."""
    try:
        presets = ['minimum', 'standard', 'maximum']
        results = {}
        
        for preset in presets:
            switch_result = execute_operation(
                GatewayInterface.CONFIG,
                'switch_preset',
                preset_name=preset
            )
            results[preset] = isinstance(switch_result, dict) and switch_result.get('success')
        
        if all(results.values()):
            return {
                "success": True,
                "message": f"All {len(presets)} presets switchable"
            }
        else:
            failed = [k for k, v in results.items() if not v]
            return {
                "success": False,
                "error": f"Presets failed: {failed}"
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Preset switching exception: {str(e)}"
        }


def test_reload_with_validation() -> Dict[str, Any]:
    """Test configuration reload with validation."""
    try:
        # Reload with validation enabled
        reload_result = execute_operation(
            GatewayInterface.CONFIG,
            'reload_config',
            validate=True
        )
        
        if isinstance(reload_result, dict) and reload_result.get('success'):
            # Verify state was updated
            state = execute_operation(
                GatewayInterface.CONFIG,
                'get_state'
            )
            
            if state.get('reload_count', 0) > 0:
                return {
                    "success": True,
                    "message": f"Reload with validation successful: {state.get('reload_count')} reloads"
                }
            else:
                return {
                    "success": False,
                    "error": "Reload count not updated"
                }
        else:
            return {
                "success": False,
                "error": f"Reload failed: {reload_result}"
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Reload test exception: {str(e)}"
        }


def test_state_tracking() -> Dict[str, Any]:
    """Test configuration state tracking."""
    try:
        state = execute_operation(
            GatewayInterface.CONFIG,
            'get_state'
        )
        
        required_fields = ['version', 'tier', 'preset', 'reload_count', 'initialized']
        missing_fields = [f for f in required_fields if f not in state]
        
        if not missing_fields:
            return {
                "success": True,
                "message": f"State tracking complete: {len(state)} fields"
            }
        else:
            return {
                "success": False,
                "error": f"Missing state fields: {missing_fields}"
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"State tracking exception: {str(e)}"
        }


def test_multi_source_loading() -> Dict[str, Any]:
    """Test loading configuration from multiple sources."""
    try:
        # Initialize config (loads all sources)
        init_result = execute_operation(
            GatewayInterface.CONFIG,
            'initialize'
        )
        
        if not (isinstance(init_result, dict) and init_result.get('success')):
            return {
                "success": False,
                "error": "Initialization failed"
            }
        
        # Load from environment
        env_result = execute_operation(
            GatewayInterface.CONFIG,
            'load_from_environment'
        )
        
        # Verify state shows initialization
        state = execute_operation(
            GatewayInterface.CONFIG,
            'get_state'
        )
        
        if state.get('initialized') and isinstance(env_result, dict):
            return {
                "success": True,
                "message": "Multi-source loading successful"
            }
        else:
            return {
                "success": False,
                "error": "Multi-source loading incomplete"
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Multi-source test exception: {str(e)}"
        }


__all__ = [
    'run_config_integration_tests'
]

# EOF
