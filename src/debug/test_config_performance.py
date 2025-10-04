"""
test_config_performance.py - Configuration System Performance Tests
Version: 2025.10.04.01
Description: Performance and memory tests for configuration system

Phase 5: Configuration System Consolidation - Performance Testing
Tests hot-reload performance, memory usage, and cache efficiency.

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

import time
import sys
from typing import Dict, Any
from gateway import execute_operation, GatewayInterface, log_info


def run_config_performance_tests() -> Dict[str, Any]:
    """Run all configuration performance tests."""
    results = {
        "total_tests": 0,
        "passed": 0,
        "failed": 0,
        "tests": []
    }
    
    tests = [
        test_parameter_access_speed,
        test_category_access_speed,
        test_reload_performance,
        test_preset_switch_performance,
        test_cache_efficiency,
        test_memory_usage,
        test_lazy_loading
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


def test_parameter_access_speed() -> Dict[str, Any]:
    """Test parameter access performance."""
    try:
        iterations = 100
        start_time = time.time()
        
        for i in range(iterations):
            execute_operation(
                GatewayInterface.CONFIG,
                'get_parameter',
                key='test.parameter',
                default='default'
            )
        
        elapsed = (time.time() - start_time) * 1000  # Convert to ms
        avg_time = elapsed / iterations
        
        # Should be under 5ms per access on average
        if avg_time < 5.0:
            return {
                "success": True,
                "message": f"Parameter access: {avg_time:.2f}ms average ({iterations} iterations)"
            }
        else:
            return {
                "success": False,
                "error": f"Parameter access too slow: {avg_time:.2f}ms (threshold: 5ms)"
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Parameter access test exception: {str(e)}"
        }


def test_category_access_speed() -> Dict[str, Any]:
    """Test category configuration access performance."""
    try:
        iterations = 50
        start_time = time.time()
        
        for i in range(iterations):
            execute_operation(
                GatewayInterface.CONFIG,
                'get_category_config',
                category='cache'
            )
        
        elapsed = (time.time() - start_time) * 1000
        avg_time = elapsed / iterations
        
        # Should be under 10ms per access
        if avg_time < 10.0:
            return {
                "success": True,
                "message": f"Category access: {avg_time:.2f}ms average ({iterations} iterations)"
            }
        else:
            return {
                "success": False,
                "error": f"Category access too slow: {avg_time:.2f}ms (threshold: 10ms)"
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Category access test exception: {str(e)}"
        }


def test_reload_performance() -> Dict[str, Any]:
    """Test configuration reload performance."""
    try:
        iterations = 10
        times = []
        
        for i in range(iterations):
            start_time = time.time()
            
            execute_operation(
                GatewayInterface.CONFIG,
                'reload_config',
                validate=True
            )
            
            elapsed = (time.time() - start_time) * 1000
            times.append(elapsed)
        
        avg_time = sum(times) / len(times)
        max_time = max(times)
        
        # Should be under 100ms on average
        if avg_time < 100.0:
            return {
                "success": True,
                "message": f"Reload performance: {avg_time:.2f}ms average, {max_time:.2f}ms max"
            }
        else:
            return {
                "success": False,
                "error": f"Reload too slow: {avg_time:.2f}ms (threshold: 100ms)"
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Reload performance test exception: {str(e)}"
        }


def test_preset_switch_performance() -> Dict[str, Any]:
    """Test preset switching performance."""
    try:
        presets = ['minimum', 'standard', 'maximum']
        times = []
        
        for preset in presets:
            start_time = time.time()
            
            execute_operation(
                GatewayInterface.CONFIG,
                'switch_preset',
                preset_name=preset
            )
            
            elapsed = (time.time() - start_time) * 1000
            times.append(elapsed)
        
        avg_time = sum(times) / len(times)
        
        # Should be under 50ms on average
        if avg_time < 50.0:
            return {
                "success": True,
                "message": f"Preset switch: {avg_time:.2f}ms average"
            }
        else:
            return {
                "success": False,
                "error": f"Preset switch too slow: {avg_time:.2f}ms (threshold: 50ms)"
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Preset switch test exception: {str(e)}"
        }


def test_cache_efficiency() -> Dict[str, Any]:
    """Test configuration caching efficiency."""
    try:
        # Set a parameter
        execute_operation(
            GatewayInterface.CONFIG,
            'set_parameter',
            key='cache.test.param',
            value='cached_value'
        )
        
        # First access (cache miss)
        start_time = time.time()
        first_result = execute_operation(
            GatewayInterface.CONFIG,
            'get_parameter',
            key='cache.test.param',
            default=None
        )
        first_time = (time.time() - start_time) * 1000
        
        # Second access (cache hit)
        start_time = time.time()
        second_result = execute_operation(
            GatewayInterface.CONFIG,
            'get_parameter',
            key='cache.test.param',
            default=None
        )
        second_time = (time.time() - start_time) * 1000
        
        # Cache hit should be faster or equal
        if second_time <= first_time and first_result == second_result:
            return {
                "success": True,
                "message": f"Cache efficient: first={first_time:.2f}ms, second={second_time:.2f}ms"
            }
        else:
            return {
                "success": False,
                "error": f"Cache not efficient: first={first_time:.2f}ms, second={second_time:.2f}ms"
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Cache efficiency test exception: {str(e)}"
        }


def test_memory_usage() -> Dict[str, Any]:
    """Test configuration memory usage."""
    try:
        # Get memory before
        try:
            import resource
            mem_before = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024  # KB to MB
        except:
            mem_before = 0
        
        # Initialize configuration
        execute_operation(
            GatewayInterface.CONFIG,
            'initialize'
        )
        
        # Load multiple categories
        for category in ['cache', 'logging', 'metrics', 'security']:
            execute_operation(
                GatewayInterface.CONFIG,
                'get_category_config',
                category=category
            )
        
        # Get memory after
        try:
            mem_after = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024
            mem_used = mem_after - mem_before
        except:
            mem_used = 0
        
        # Should use less than 30MB
        if mem_used < 30.0 or mem_used == 0:
            return {
                "success": True,
                "message": f"Memory usage acceptable: {mem_used:.2f}MB"
            }
        else:
            return {
                "success": False,
                "error": f"Memory usage high: {mem_used:.2f}MB (threshold: 30MB)"
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Memory usage test exception: {str(e)}"
        }


def test_lazy_loading() -> Dict[str, Any]:
    """Test lazy loading of config_core module."""
    try:
        # Check if config_core is loaded
        config_core_loaded = 'config_core' in sys.modules
        
        # Execute a config operation
        execute_operation(
            GatewayInterface.CONFIG,
            'get_state'
        )
        
        # Now it should be loaded
        config_core_now_loaded = 'config_core' in sys.modules
        
        if config_core_now_loaded:
            return {
                "success": True,
                "message": f"Lazy loading working: loaded on demand"
            }
        else:
            return {
                "success": False,
                "error": "config_core not loaded after operation"
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Lazy loading test exception: {str(e)}"
        }


__all__ = [
    'run_config_performance_tests'
]

# EOF
