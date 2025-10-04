"""
test_config_unit.py - Configuration System Unit Tests
Version: 2025.10.04.01
Description: Unit tests for config_core.py operations

Phase 5: Configuration System Consolidation - Unit Testing
Tests all 13 configuration operations through gateway interface.

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
from gateway import execute_operation, GatewayInterface, log_info, log_error


def run_config_unit_tests() -> Dict[str, Any]:
    """Run all configuration unit tests."""
    results = {
        "total_tests": 0,
        "passed": 0,
        "failed": 0,
        "tests": []
    }
    
    tests = [
        test_config_initialize,
        test_config_get_parameter,
        test_config_set_parameter,
        test_config_get_category_config,
        test_config_reload,
        test_config_switch_preset,
        test_config_get_state,
        test_config_load_from_environment,
        test_config_load_from_file,
        test_config_validate_all_sections
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


def test_config_initialize() -> Dict[str, Any]:
    """Test configuration initialization."""
    try:
        result = execute_operation(
            GatewayInterface.CONFIG,
            'initialize'
        )
        
        if isinstance(result, dict) and result.get('success'):
            return {
                "success": True,
                "message": "Configuration initialized successfully"
            }
        else:
            return {
                "success": False,
                "error": f"Initialization failed: {result}"
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Initialization exception: {str(e)}"
        }


def test_config_get_parameter() -> Dict[str, Any]:
    """Test getting configuration parameter."""
    try:
        # Test with default value
        result = execute_operation(
            GatewayInterface.CONFIG,
            'get_parameter',
            key='test.parameter',
            default='default_value'
        )
        
        if result is not None:
            return {
                "success": True,
                "message": f"Get parameter successful: {result}"
            }
        else:
            return {
                "success": False,
                "error": "Get parameter returned None"
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Get parameter exception: {str(e)}"
        }


def test_config_set_parameter() -> Dict[str, Any]:
    """Test setting configuration parameter."""
    try:
        result = execute_operation(
            GatewayInterface.CONFIG,
            'set_parameter',
            key='test.parameter',
            value='test_value'
        )
        
        if result:
            # Verify we can get it back
            get_result = execute_operation(
                GatewayInterface.CONFIG,
                'get_parameter',
                key='test.parameter',
                default=None
            )
            
            if get_result == 'test_value':
                return {
                    "success": True,
                    "message": "Set parameter successful and verified"
                }
            else:
                return {
                    "success": False,
                    "error": f"Set parameter not persisted: got {get_result}"
                }
        else:
            return {
                "success": False,
                "error": "Set parameter returned False"
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Set parameter exception: {str(e)}"
        }


def test_config_get_category_config() -> Dict[str, Any]:
    """Test getting category configuration."""
    try:
        result = execute_operation(
            GatewayInterface.CONFIG,
            'get_category_config',
            category='cache'
        )
        
        if isinstance(result, dict):
            return {
                "success": True,
                "message": f"Get category config successful: {len(result)} keys"
            }
        else:
            return {
                "success": False,
                "error": f"Get category config invalid type: {type(result)}"
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Get category config exception: {str(e)}"
        }


def test_config_reload() -> Dict[str, Any]:
    """Test configuration reload."""
    try:
        result = execute_operation(
            GatewayInterface.CONFIG,
            'reload_config',
            validate=True
        )
        
        if isinstance(result, dict) and result.get('success'):
            return {
                "success": True,
                "message": "Configuration reload successful"
            }
        else:
            return {
                "success": False,
                "error": f"Reload failed: {result}"
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Reload exception: {str(e)}"
        }


def test_config_switch_preset() -> Dict[str, Any]:
    """Test preset switching."""
    try:
        result = execute_operation(
            GatewayInterface.CONFIG,
            'switch_preset',
            preset_name='minimum'
        )
        
        if isinstance(result, dict) and result.get('success'):
            return {
                "success": True,
                "message": "Preset switch successful"
            }
        else:
            return {
                "success": False,
                "error": f"Preset switch failed: {result}"
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Preset switch exception: {str(e)}"
        }


def test_config_get_state() -> Dict[str, Any]:
    """Test getting configuration state."""
    try:
        result = execute_operation(
            GatewayInterface.CONFIG,
            'get_state'
        )
        
        if isinstance(result, dict) and 'version' in result:
            return {
                "success": True,
                "message": f"Get state successful: version {result.get('version')}"
            }
        else:
            return {
                "success": False,
                "error": f"Get state invalid: {result}"
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Get state exception: {str(e)}"
        }


def test_config_load_from_environment() -> Dict[str, Any]:
    """Test loading from environment variables."""
    try:
        result = execute_operation(
            GatewayInterface.CONFIG,
            'load_from_environment'
        )
        
        if isinstance(result, dict):
            return {
                "success": True,
                "message": f"Load from environment successful: {len(result)} keys"
            }
        else:
            return {
                "success": False,
                "error": f"Load from environment invalid: {type(result)}"
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Load from environment exception: {str(e)}"
        }


def test_config_load_from_file() -> Dict[str, Any]:
    """Test loading from file."""
    try:
        # Test with non-existent file (should handle gracefully)
        result = execute_operation(
            GatewayInterface.CONFIG,
            'load_from_file',
            filepath='/tmp/nonexistent_config.json'
        )
        
        # Should return dict even if file doesn't exist
        if isinstance(result, dict):
            return {
                "success": True,
                "message": "Load from file handled gracefully"
            }
        else:
            return {
                "success": False,
                "error": f"Load from file invalid: {type(result)}"
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Load from file exception: {str(e)}"
        }


def test_config_validate_all_sections() -> Dict[str, Any]:
    """Test validating all configuration sections."""
    try:
        result = execute_operation(
            GatewayInterface.CONFIG,
            'validate_all_sections'
        )
        
        if isinstance(result, dict) and 'valid' in result:
            return {
                "success": True,
                "message": f"Validation complete: valid={result.get('valid')}"
            }
        else:
            return {
                "success": False,
                "error": f"Validation invalid result: {result}"
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Validation exception: {str(e)}"
        }


__all__ = [
    'run_config_unit_tests'
]

# EOF
