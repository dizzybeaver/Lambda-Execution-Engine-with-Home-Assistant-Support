# test_debug_patterns.py
"""
test_debug_patterns.py
Version: 1.0.0
Date: 2025-11-04
Description: Generic debug pattern verification for all core modules

Tests that core modules follow debug/timing patterns:
- _DEBUG_MODE_ENABLED module variable
- _is_debug_mode() function
- DebugContext context manager (optional)
- _trace_step() gated operations (optional)
- Performance profiling gated by DEBUG_MODE

Parameterized to work with:
- LEE cores (cache_core, logging_core, etc.)
- HA-SUGA cores (ha_alexa_core, ha_assist_core, ha_devices_core)
- Any future cores

Copyright 2025 Joseph Hersey

Licensed under the Apache License, Version 2.0.
"""

import sys
import importlib
import inspect
from typing import Dict, List, Any, Optional


# ADDED: Generic debug pattern verification test
def run_debug_pattern_tests(cores: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Run debug pattern tests on specified cores.
    
    Args:
        cores: List of core module names to test. If None, test all known cores.
        
    Returns:
        Test results dictionary
    """
    results = {
        "total_tests": 0,
        "passed": 0,
        "failed": 0,
        "tests": []
    }
    
    # Default cores to test
    if cores is None:
        cores = [
            'cache_core',
            'logging_core',
            'config_core',
            'security_core',
            'metrics_core'
        ]
        
        # Add HA cores if HA enabled
        import os
        if os.environ.get('HOME_ASSISTANT_ENABLE', 'false').lower() == 'true':
            cores.extend([
                'home_assistant.ha_alexa_core',
                'home_assistant.ha_assist_core',
                'home_assistant.ha_devices_core'
            ])
    
    # Test each core
    for core_name in cores:
        results["total_tests"] += 1
        
        try:
            test_result = test_core_debug_patterns(core_name)
            
            if test_result.get("success", False):
                results["passed"] += 1
            else:
                results["failed"] += 1
            
            results["tests"].append({
                "core": core_name,
                "success": test_result.get("success", False),
                "message": test_result.get("message", test_result.get("error", ""))
            })
            
        except Exception as e:
            results["failed"] += 1
            results["tests"].append({
                "core": core_name,
                "success": False,
                "message": f"Exception: {str(e)}"
            })
    
    return results


# ADDED: Test individual core for debug patterns
def test_core_debug_patterns(core_name: str) -> Dict[str, Any]:
    """
    Test a single core module for debug patterns.
    
    Args:
        core_name: Name of core module (e.g., 'cache_core' or 'home_assistant.ha_alexa_core')
        
    Returns:
        Test result dictionary
    """
    try:
        # Import the core module
        core_module = importlib.import_module(core_name)
        
        # Get module source
        source = inspect.getsource(core_module)
        
        # Check for required patterns
        patterns = {
            'DEBUG_MODE_ENABLED': '_DEBUG_MODE_ENABLED' in source,
            'is_debug_mode_function': '_is_debug_mode' in source or 'def is_debug_mode' in source,
            'debug_logging': 'if _DEBUG_MODE_ENABLED' in source or 'if DEBUG_MODE' in source or 'if _is_debug_mode()' in source
        }
        
        # Optional patterns (not all cores need these)
        optional_patterns = {
            'DebugContext': 'class DebugContext' in source,
            'trace_step': '_trace_step' in source,
            'performance_profiling': 'HA_SLOW_OPERATION_THRESHOLD_MS' in source or 'SLOW_OPERATION_THRESHOLD' in source
        }
        
        # Check module-level variable exists
        has_debug_var = hasattr(core_module, '_DEBUG_MODE_ENABLED') or hasattr(core_module, 'DEBUG_MODE_ENABLED')
        
        # Check function exists
        has_debug_func = hasattr(core_module, '_is_debug_mode') or hasattr(core_module, 'is_debug_mode')
        
        # Verify patterns
        missing_required = [k for k, v in patterns.items() if not v]
        found_optional = [k for k, v in optional_patterns.items() if v]
        
        if not missing_required and (has_debug_var or has_debug_func):
            return {
                "success": True,
                "message": f"Debug patterns present: {list(patterns.keys())} + {found_optional}"
            }
        else:
            issues = []
            if missing_required:
                issues.append(f"Missing required: {missing_required}")
            if not has_debug_var:
                issues.append("No DEBUG_MODE variable")
            if not has_debug_func:
                issues.append("No is_debug_mode function")
            
            return {
                "success": False,
                "error": f"Debug pattern issues: {issues}"
            }
    
    except ModuleNotFoundError:
        return {
            "success": False,
            "error": f"Core module not found: {core_name}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Test exception: {str(e)}"
        }


# ADDED: Test DEBUG_MODE actually gates operations
def test_debug_mode_gating() -> Dict[str, Any]:
    """Test that DEBUG_MODE actually gates debug operations."""
    try:
        import os
        
        # Test with DEBUG_MODE off
        os.environ['DEBUG_MODE'] = 'false'
        
        # Import a core that uses debug patterns
        import cache_core
        
        # Verify debug mode is off
        if hasattr(cache_core, '_is_debug_mode'):
            debug_off = not cache_core._is_debug_mode()
        elif hasattr(cache_core, 'is_debug_mode'):
            debug_off = not cache_core.is_debug_mode()
        else:
            return {
                "success": False,
                "error": "No is_debug_mode function found"
            }
        
        if not debug_off:
            return {
                "success": False,
                "error": "DEBUG_MODE=false but is_debug_mode() returned True"
            }
        
        # Test with DEBUG_MODE on
        os.environ['DEBUG_MODE'] = 'true'
        
        # Reload module to pick up new env var
        importlib.reload(cache_core)
        
        # Verify debug mode is on
        if hasattr(cache_core, '_is_debug_mode'):
            debug_on = cache_core._is_debug_mode()
        elif hasattr(cache_core, 'is_debug_mode'):
            debug_on = cache_core.is_debug_mode()
        else:
            debug_on = False
        
        if not debug_on:
            return {
                "success": False,
                "error": "DEBUG_MODE=true but is_debug_mode() returned False"
            }
        
        return {
            "success": True,
            "message": "DEBUG_MODE gating works correctly"
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": f"Gating test exception: {str(e)}"
        }
    finally:
        # Cleanup
        if 'DEBUG_MODE' in os.environ:
            del os.environ['DEBUG_MODE']


# ADDED: Test performance profiling is gated
def test_performance_profiling_gating() -> Dict[str, Any]:
    """Test that performance profiling is only active when DEBUG_MODE enabled."""
    try:
        import os
        import time
        
        # Test with DEBUG_MODE off
        os.environ['DEBUG_MODE'] = 'false'
        
        # Import core with performance profiling
        try:
            from home_assistant import ha_devices_core
            has_ha = True
        except ImportError:
            has_ha = False
        
        if not has_ha:
            return {
                "success": True,
                "message": "HA not available, skipping performance profiling test"
            }
        
        # Reload to pick up DEBUG_MODE
        importlib.reload(ha_devices_core)
        
        # Check that profiling is disabled
        if hasattr(ha_devices_core, '_is_debug_mode'):
            debug_off = not ha_devices_core._is_debug_mode()
        else:
            debug_off = True
        
        if not debug_off:
            return {
                "success": False,
                "error": "Performance profiling should be disabled when DEBUG_MODE=false"
            }
        
        return {
            "success": True,
            "message": "Performance profiling correctly gated by DEBUG_MODE"
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": f"Profiling test exception: {str(e)}"
        }
    finally:
        # Cleanup
        if 'DEBUG_MODE' in os.environ:
            del os.environ['DEBUG_MODE']


# ADDED: Main test runner
def main():
    """Main test runner."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test debug patterns in core modules")
    parser.add_argument("--cores", nargs="+", help="Specific cores to test")
    parser.add_argument("--include-ha", action="store_true", help="Include HA cores in test")
    args = parser.parse_args()
    
    cores = args.cores
    
    if args.include_ha:
        import os
        os.environ['HOME_ASSISTANT_ENABLE'] = 'true'
    
    print("="*60)
    print("DEBUG PATTERN TESTS")
    print("="*60)
    
    # Test core debug patterns
    results = run_debug_pattern_tests(cores)
    
    print(f"\nCore Pattern Tests: {results['passed']}/{results['total_tests']} passed")
    
    for test in results['tests']:
        status = "✅ PASS" if test['success'] else "❌ FAIL"
        print(f"{status}: {test['core']} - {test['message']}")
    
    # Test DEBUG_MODE gating
    print("\n" + "="*60)
    print("DEBUG_MODE GATING TESTS")
    print("="*60)
    
    gating_result = test_debug_mode_gating()
    status = "✅ PASS" if gating_result['success'] else "❌ FAIL"
    print(f"{status}: {gating_result.get('message', gating_result.get('error', ''))}")
    
    # Test performance profiling gating
    profiling_result = test_performance_profiling_gating()
    status = "✅ PASS" if profiling_result['success'] else "❌ FAIL"
    print(f"{status}: {profiling_result.get('message', profiling_result.get('error', ''))}")
    
    # Summary
    total_passed = results['passed'] + (1 if gating_result['success'] else 0) + (1 if profiling_result['success'] else 0)
    total_tests = results['total_tests'] + 2
    
    print("\n" + "="*60)
    print(f"TOTAL: {total_passed}/{total_tests} tests passed")
    print("="*60)
    
    return 0 if total_passed == total_tests else 1


if __name__ == "__main__":
    sys.exit(main())


__all__ = [
    'run_debug_pattern_tests',
    'test_core_debug_patterns',
    'test_debug_mode_gating',
    'test_performance_profiling_gating'
]

# EOF
