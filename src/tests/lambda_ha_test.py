"""
lambda_function.py - Complete Import Chain Tester

Tests the complete import chain:
1. home_assistant package
2. ha_interconnect module (gateway)
3. ha_interface_* modules
4. ha_*_core modules

Shows exactly where the import chain breaks.
"""

import sys
import os

# Setup sys.path
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from typing import Dict, Any, List, Tuple


def test_import(module_path: str, description: str) -> Tuple[bool, str]:
    """
    Test a single import.
    
    Args:
        module_path: Import path (e.g., "home_assistant.ha_interconnect")
        description: Human-readable description
        
    Returns:
        (success, error_message)
    """
    try:
        if " import " in module_path:
            # It's a "from X import Y" style
            exec(module_path)
        else:
            # It's a "import X" style
            exec(f"import {module_path}")
        return (True, "")
    except Exception as e:
        return (False, str(e))


def run_comprehensive_test():
    """Run comprehensive import tests."""
    
    print("=" * 80)
    print("COMPREHENSIVE IMPORT CHAIN TEST")
    print("=" * 80)
    print("\nTesting complete import chain from package → gateway → interfaces → cores")
    print("=" * 80)
    
    tests = [
        # Layer 1: Package
        ("import home_assistant", "Package: home_assistant"),
        
        # Layer 2: Gateway files (ha_interconnect_*)
        ("from home_assistant import ha_interconnect_validation", "Gateway: ha_interconnect_validation"),
        ("from home_assistant import ha_interconnect_alexa", "Gateway: ha_interconnect_alexa"),
        ("from home_assistant import ha_interconnect_devices", "Gateway: ha_interconnect_devices"),
        ("from home_assistant import ha_interconnect_assist", "Gateway: ha_interconnect_assist"),
        
        # Layer 3: Main gateway (imports all the above)
        ("from home_assistant import ha_interconnect", "Main Gateway: ha_interconnect"),
        
        # Layer 4: Interface routing files
        ("from home_assistant import ha_interface_alexa", "Interface: ha_interface_alexa"),
        ("from home_assistant import ha_interface_devices", "Interface: ha_interface_devices"),
        ("from home_assistant import ha_interface_assist", "Interface: ha_interface_assist"),
        
        # Layer 5: Core implementation files
        ("from home_assistant import ha_alexa_core", "Core: ha_alexa_core"),
        ("from home_assistant import ha_devices_core", "Core: ha_devices_core"),
        ("from home_assistant import ha_assist_core", "Core: ha_assist_core"),
        
        # Layer 6: Helper files
        ("from home_assistant import ha_devices_helpers", "Helper: ha_devices_helpers"),
        ("from home_assistant import ha_devices_cache", "Helper: ha_devices_cache"),
        ("from home_assistant import ha_websocket", "Helper: ha_websocket"),
    ]
    
    results = []
    first_failure = None
    
    for test_import, description in tests:
        print(f"\n[TEST] {description}")
        print(f"       Import: {test_import}")
        
        success, error = test_import(test_import, description)
        
        if success:
            print(f"       ✅ SUCCESS")
            results.append((description, True, ""))
        else:
            print(f"       ❌ FAILED")
            print(f"       Reason: {error}")
            results.append((description, False, error))
            
            if first_failure is None:
                first_failure = (description, error)
                print(f"\n⚠️  STOPPING AT FIRST FAILURE")
                break
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    passed = sum(1 for _, success, _ in results if success)
    failed = sum(1 for _, success, _ in results if not success)
    total = len(results)
    
    print(f"\nTests run: {total}/{len(tests)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    
    if first_failure:
        print(f"\n❌ FIRST FAILURE:")
        print(f"   Module: {first_failure[0]}")
        print(f"   Reason: {first_failure[1]}")
        print(f"\n💡 FIX: Check this module's import statements")
        print(f"   All imports should use: from home_assistant.module_name import ...")
    else:
        print("\n✅ ALL IMPORTS SUCCESSFUL!")
        print("\n🎉 The import chain is working correctly!")
        
        # Show what's loaded
        print("\n" + "=" * 80)
        print("LOADED MODULES")
        print("=" * 80)
        loaded = sorted([k for k in sys.modules.keys() if 'home_assistant' in k])
        print(f"\nTotal home_assistant modules loaded: {len(loaded)}")
        for mod in loaded:
            print(f"  ✓ {mod}")
    
    print("=" * 80)


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Lambda handler."""
    print("[LAMBDA HANDLER] Starting comprehensive import chain test...\n")
    
    run_comprehensive_test()
    
    print("\n[LAMBDA HANDLER] Tests complete - exiting")
    sys.exit(0)


# EOF
