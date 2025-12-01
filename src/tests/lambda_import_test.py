"""
lambda_import_test.py - Import Diagnostics for Lambda
Drop-in Import testing for lambda_function.py

Version: DIAGNOSTIC
Date: 2025-11-30
Purpose: Systematic testing of Python import paths in AWS Lambda

⚠️ THIS IS A TEMPORARY DIAGNOSTIC FILE ⚠️
USAGE:
1. Rename your current lambda_function.py to lambda_function.py.backup
2. Rename this file to lambda_function.py
3. Deploy to Lambda (handler is already lambda_function.lambda_handler)
4. Trigger Lambda with any event (Alexa request will work)
5. Check CloudWatch logs for test results
6. Restore lambda_function.py.backup when done

CUSTOMIZATION:
- Modify TEST_PACKAGE to test different packages
- Add/remove tests as needed
- Change file inspection in TEST 5

Copyright 2025 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

# ===== CRITICAL: sys.path fix for subdirectory imports =====
# This MUST be first, before any imports
import sys
import os

# Ensure lambda_function.py's directory is in sys.path
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import time
from typing import Dict, Any


# ===== CONFIGURATION =====
TEST_PACKAGE = "home_assistant"  # Change this to test other packages
TEST_MODULE = "ha_interconnect"  # Change this to test other modules
TEST_SUBMODULE = "ha_interconnect_validation"  # Change this to test other submodules


def _print_timing(msg: str):
    """Print timing message."""
    print(f"[TIMING] {msg}")


def run_import_tests():
    """
    Run systematic import tests to diagnose Python package issues.
    
    Tests are numbered and independent - if one fails, others still run.
    All results print to CloudWatch logs.
    """
    
    print("=" * 70)
    print("LAMBDA IMPORT DIAGNOSTIC TEST")
    print("=" * 70)
    
    # Get ROOT_DIR (Lambda's /var/task directory)
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
    print(f"\n[SETUP] ROOT_DIR: {ROOT_DIR}")
    print(f"[SETUP] sys.path (first 3): {sys.path[:3]}")
    
    # Show COMPLETE list of files in Lambda root directory
    print(f"\n[SETUP] === COMPLETE FILE LIST IN LAMBDA ROOT ===")
    try:
        root_files = sorted(os.listdir(ROOT_DIR))
        print(f"[SETUP] Total files/directories: {len(root_files)}")
        
        # Separate files from directories
        files = []
        dirs = []
        for item in root_files:
            item_path = os.path.join(ROOT_DIR, item)
            if os.path.isdir(item_path):
                dirs.append(item)
            else:
                files.append(item)
        
        print(f"\n[SETUP] Directories ({len(dirs)}):")
        for d in dirs:
            print(f"         📁 {d}/")
        
        print(f"\n[SETUP] Python files ({len([f for f in files if f.endswith('.py')])}):")
        for f in files:
            if f.endswith('.py'):
                print(f"         📄 {f}")
        
        print(f"\n[SETUP] Other files ({len([f for f in files if not f.endswith('.py')])}):")
        for f in files:
            if not f.endswith('.py'):
                print(f"         📄 {f}")
    except Exception as e:
        print(f"[SETUP] ❌ Error listing root directory: {e}")
    
    # Check if test package directory exists and is accessible
    print(f"\n[SETUP] === CHECKING {TEST_PACKAGE}/ DIRECTORY ===")
    try:
        package_dir = os.path.join(ROOT_DIR, TEST_PACKAGE)
        
        if not os.path.exists(package_dir):
            print(f"[SETUP] ❌ {TEST_PACKAGE}/ directory NOT FOUND")
        elif not os.path.isdir(package_dir):
            print(f"[SETUP] ❌ {TEST_PACKAGE} exists but is NOT a directory")
        else:
            print(f"[SETUP] ✅ {TEST_PACKAGE}/ directory exists")
            
            # Check read permissions
            if os.access(package_dir, os.R_OK):
                print(f"[SETUP] ✅ {TEST_PACKAGE}/ is readable")
            else:
                print(f"[SETUP] ❌ {TEST_PACKAGE}/ is NOT readable (permission issue)")
            
            # List contents
            package_files = sorted(os.listdir(package_dir))
            print(f"[SETUP] {TEST_PACKAGE}/ contains {len(package_files)} files:")
            for pf in package_files:
                pf_path = os.path.join(package_dir, pf)
                if os.path.isdir(pf_path):
                    print(f"         📁 {pf}/")
                elif pf.endswith('.py'):
                    print(f"         🐍 {pf}")
                else:
                    print(f"         📄 {pf}")
            
            # Check if __init__.py exists
            init_file = os.path.join(package_dir, "__init__.py")
            if os.path.exists(init_file):
                print(f"[SETUP] ✅ {TEST_PACKAGE}/__init__.py exists (valid package)")
            else:
                print(f"[SETUP] ⚠️  {TEST_PACKAGE}/__init__.py NOT FOUND (not a valid package!)")
            
            # Check if test module exists
            module_file = os.path.join(package_dir, f"{TEST_MODULE}.py")
            if os.path.exists(module_file):
                print(f"[SETUP] ✅ {TEST_PACKAGE}/{TEST_MODULE}.py exists")
            else:
                print(f"[SETUP] ⚠️  {TEST_PACKAGE}/{TEST_MODULE}.py NOT FOUND")
    except Exception as e:
        print(f"[SETUP] ❌ Error checking {TEST_PACKAGE}/ directory: {e}")
    
    print("\n" + "=" * 70)
    print("RUNNING TESTS")
    print("=" * 70)
    
    # ===== TEST 1: Import package =====
    print("\n[TEST 1] Import package")
    print(f"         Trying: import {TEST_PACKAGE}")
    print(f"         Purpose: Verify package is importable")
    print(f"         Customize: Change TEST_PACKAGE variable")
    try:
        exec(f"import {TEST_PACKAGE}")
        print(f"         ✅ SUCCESS - {TEST_PACKAGE} imported")
    except Exception as e:
        print(f"         ❌ FAILED - {e}")
    
    # ===== TEST 2: Import module from package =====
    print("\n[TEST 2] Import module from package")
    print(f"         Trying: from {TEST_PACKAGE} import {TEST_MODULE}")
    print(f"         Purpose: Verify module inside package is importable")
    print(f"         Customize: Change TEST_MODULE variable")
    try:
        exec(f"from {TEST_PACKAGE} import {TEST_MODULE}")
        print(f"         ✅ SUCCESS - {TEST_MODULE} imported from {TEST_PACKAGE}")
    except Exception as e:
        print(f"         ❌ FAILED - {e}")
    
    # ===== TEST 3: Import submodule directly =====
    print("\n[TEST 3] Import submodule directly from package")
    print(f"         Trying: from {TEST_PACKAGE} import {TEST_SUBMODULE}")
    print(f"         Purpose: Verify submodules are directly importable")
    print(f"         Customize: Change TEST_SUBMODULE variable")
    try:
        exec(f"from {TEST_PACKAGE} import {TEST_SUBMODULE}")
        print(f"         ✅ SUCCESS - {TEST_SUBMODULE} imported")
    except Exception as e:
        print(f"         ❌ FAILED - {e}")
    
    # ===== TEST 4: Check sys.modules =====
    print("\n[TEST 4] Check what's loaded in sys.modules")
    print(f"         Purpose: See which modules Python has loaded")
    print(f"         Customize: Change filter string in list comprehension")
    try:
        loaded_modules = [k for k in sys.modules.keys() if TEST_PACKAGE in k]
        print(f"         Loaded modules containing '{TEST_PACKAGE}':")
        if loaded_modules:
            for mod in loaded_modules:
                print(f"           - {mod}")
        else:
            print(f"         ⚠️  No modules containing '{TEST_PACKAGE}' found")
        print(f"         ✅ SUCCESS - sys.modules checked")
    except Exception as e:
        print(f"         ❌ FAILED - {e}")
    
    # ===== TEST 5: Inspect module file content =====
    print("\n[TEST 5] Inspect module file for import statements")
    print(f"         Purpose: See actual import statements in deployed file")
    print(f"         Customize: Change file path and line filters")
    try:
        module_path = os.path.join(ROOT_DIR, TEST_PACKAGE, f"{TEST_MODULE}.py")
        
        if not os.path.exists(module_path):
            print(f"         ⚠️  File not found: {module_path}")
        else:
            with open(module_path, 'r') as f:
                lines = f.readlines()
            
            print(f"         File: {module_path}")
            print(f"         Total lines: {len(lines)}")
            print(f"         Import statements found:")
            
            import_count = 0
            for i, line in enumerate(lines[:100], 1):  # Check first 100 lines
                stripped = line.strip()
                # Find import lines (not comments)
                if ('import' in stripped and 
                    not stripped.startswith('#') and 
                    stripped):
                    print(f"           Line {i:3d}: {line.rstrip()}")
                    import_count += 1
            
            if import_count == 0:
                print(f"         ⚠️  No import statements found in first 100 lines")
            
            print(f"         ✅ SUCCESS - File inspected ({import_count} imports found)")
    except Exception as e:
        print(f"         ❌ FAILED - {e}")
    
    # ===== TEST 6: Check __init__.py content =====
    print("\n[TEST 6] Check package __init__.py content")
    print(f"         Purpose: Verify __init__.py is not causing import issues")
    print(f"         Customize: Change package path")
    try:
        init_path = os.path.join(ROOT_DIR, TEST_PACKAGE, "__init__.py")
        
        if not os.path.exists(init_path):
            print(f"         ⚠️  __init__.py not found (package might not be valid)")
        else:
            with open(init_path, 'r') as f:
                content = f.read()
            
            print(f"         File: {init_path}")
            print(f"         Size: {len(content)} characters")
            print(f"         Lines: {len(content.splitlines())} lines")
            
            if len(content.strip()) == 0:
                print(f"         ℹ️  __init__.py is EMPTY (blank)")
            else:
                print(f"         Content preview (first 500 chars):")
                print(f"         {'-' * 60}")
                print(content[:500])
                if len(content) > 500:
                    print(f"         ... (truncated)")
                print(f"         {'-' * 60}")
            
            print(f"         ✅ SUCCESS - __init__.py checked")
    except Exception as e:
        print(f"         ❌ FAILED - {e}")
    
    # ===== TEST 7: Try alternative import style =====
    print("\n[TEST 7] Try alternative import: import package.module")
    print(f"         Trying: import {TEST_PACKAGE}.{TEST_MODULE}")
    print(f"         Purpose: Test if dot-notation import works")
    print(f"         Customize: Change package.module path")
    try:
        exec(f"import {TEST_PACKAGE}.{TEST_MODULE}")
        print(f"         ✅ SUCCESS - {TEST_PACKAGE}.{TEST_MODULE} imported")
    except Exception as e:
        print(f"         ❌ FAILED - {e}")
    
    # ===== SUMMARY =====
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"All tests completed. Check results above.")
    print(f"Package tested: {TEST_PACKAGE}")
    print(f"Module tested: {TEST_MODULE}")
    print(f"Submodule tested: {TEST_SUBMODULE}")
    print("=" * 70)


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler - runs tests and exits.
    
    Args:
        event: Lambda event (ignored)
        context: Lambda context (ignored)
        
    Returns:
        Never returns - exits after tests
    """
    print("[LAMBDA HANDLER] Starting import diagnostic tests...")
    
    # Run all tests
    run_import_tests()
    
    # Exit cleanly
    print("\n[LAMBDA HANDLER] Tests complete - exiting")
    sys.exit(0)


# EOF - lambda_import_test.py
