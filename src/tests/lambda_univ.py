"""
lambda_function.py - UNIVERSAL IMPORT DIAGNOSTIC

Version: DIAGNOSTIC-UNIVERSAL
Date: 2025-11-30
Purpose: Systematic testing of Python import paths in AWS Lambda

⚠️ THIS IS A TEMPORARY DIAGNOSTIC FILE ⚠️

USAGE:
1. Backup: mv lambda_function.py lambda_function.py.backup
2. Deploy this file as lambda_function.py
3. Set environment variables to configure what to test:
   - TEST_PACKAGE: Package name to test (default: "home_assistant")
   - TEST_MODULE: Main module name (default: "ha_interconnect")
   - TEST_SUBMODULES: Comma-separated list of submodules (optional)
4. Trigger Lambda with any event
5. Check CloudWatch logs for results
6. Restore: mv lambda_function.py.backup lambda_function.py

EXAMPLES:
- Test home_assistant: TEST_PACKAGE=home_assistant TEST_MODULE=ha_interconnect
- Test custom_module: TEST_PACKAGE=custom_module TEST_MODULE=main
- Test with submodules: TEST_SUBMODULES=utils,helpers,validators

Copyright 2025 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).
"""

import sys
import os

# Setup sys.path
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import time
from typing import Dict, Any, List, Optional


# ===== CONFIGURATION FROM ENVIRONMENT =====
TEST_PACKAGE = os.getenv('TEST_PACKAGE', 'home_assistant')
TEST_MODULE = os.getenv('TEST_MODULE', 'ha_interconnect')
TEST_SUBMODULES_ENV = os.getenv('TEST_SUBMODULES', '')

# Parse submodules from comma-separated string
if TEST_SUBMODULES_ENV:
    TEST_SUBMODULES = [s.strip() for s in TEST_SUBMODULES_ENV.split(',') if s.strip()]
else:
    # Default submodules for home_assistant (used if not specified)
    if TEST_PACKAGE == 'home_assistant':
        TEST_SUBMODULES = ['ha_interconnect_validation', 'ha_interconnect_alexa', 
                          'ha_interconnect_devices', 'ha_interconnect_assist']
    else:
        TEST_SUBMODULES = []


def print_test_header(test_name: str):
    """Print formatted test header."""
    print(f"\n{'=' * 80}")
    print(f"{test_name}")
    print(f"{'=' * 80}\n")


def print_result(test_name: str, passed: bool, reason: Optional[str] = None):
    """Print test result in standard format."""
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{test_name}: {status}")
    if reason:
        print(f"Reason: {reason}")


def run_import_tests():
    """Run systematic import diagnostics."""
    
    print("=" * 80)
    print("LAMBDA IMPORT DIAGNOSTIC TEST - UNIVERSAL")
    print("=" * 80)
    print(f"\nConfiguration:")
    print(f"  TEST_PACKAGE: {TEST_PACKAGE}")
    print(f"  TEST_MODULE: {TEST_MODULE}")
    print(f"  TEST_SUBMODULES: {TEST_SUBMODULES if TEST_SUBMODULES else '(none)'}")
    
    # ===== FILE SYSTEM CHECK =====
    print_test_header("FILE SYSTEM CHECK")
    
    # Show sys.path
    print(f"sys.path: {sys.path}")
    
    # Show root directory
    print(f"\nRoot Directory: {ROOT_DIR}")
    
    # Check if module directory is accessible
    package_dir = os.path.join(ROOT_DIR, TEST_PACKAGE)
    print(f"\nChecking module directory access: {TEST_PACKAGE}/")
    
    if not os.path.exists(package_dir):
        print(f"❌ FATAL: {TEST_PACKAGE}/ directory does NOT exist")
        print(f"Cannot proceed with tests.")
        sys.exit(1)
    
    if not os.path.isdir(package_dir):
        print(f"❌ FATAL: {TEST_PACKAGE} exists but is NOT a directory")
        sys.exit(1)
    
    if not os.access(package_dir, os.R_OK):
        print(f"❌ FATAL: {TEST_PACKAGE}/ exists but is NOT readable (permission denied)")
        sys.exit(1)
    
    print(f"✅ Module directory accessible: {TEST_PACKAGE}/")
    
    # List package contents
    try:
        package_files = sorted(os.listdir(package_dir))
        print(f"\nPackage contents ({len(package_files)} files):")
        for pf in package_files:
            if pf.endswith('.py'):
                print(f"  🐍 {pf}")
    except Exception as e:
        print(f"❌ ERROR: Cannot list {TEST_PACKAGE}/ contents: {e}")
    
    # ===== CHECK __init__.py =====
    print_test_header("CHECKING __init__.py")
    
    init_path = os.path.join(package_dir, "__init__.py")
    
    if not os.path.exists(init_path):
        print(f"⚠️  __init__.py does NOT exist")
        print(f"Note: {TEST_PACKAGE} may not be a valid Python package")
        has_init_imports = False
    else:
        try:
            with open(init_path, 'r') as f:
                init_content = f.read()
            
            # Check if blank
            if len(init_content.strip()) == 0:
                print(f"✅ __init__.py is BLANK")
                has_init_imports = False
            else:
                # Check if has imports
                has_init_imports = any(
                    line.strip().startswith(('import ', 'from ')) 
                    and not line.strip().startswith('#')
                    for line in init_content.splitlines()
                )
                
                if not has_init_imports:
                    print(f"✅ __init__.py has content but NO imports")
                else:
                    print(f"⚠️  __init__.py has IMPORTS - testing...")
                    
                    # Test if __init__.py imports work
                    try:
                        exec(f"import {TEST_PACKAGE}")
                        print_result("__init__.py imports test", True)
                    except Exception as e:
                        print_result("__init__.py imports test", False, str(e))
        except Exception as e:
            print(f"❌ ERROR reading __init__.py: {e}")
            has_init_imports = False
    
    # ===== BASIC IMPORT TESTS =====
    print_test_header("BASIC IMPORT TESTS")
    
    # TEST 1: Import package
    print("\n[TEST 1] Import package")
    try:
        exec(f"import {TEST_PACKAGE}")
        print_result(f"import {TEST_PACKAGE}", True)
    except Exception as e:
        print_result(f"import {TEST_PACKAGE}", False, str(e))
    
    # TEST 2: Import module from package
    print("\n[TEST 2] Import module from package")
    try:
        exec(f"from {TEST_PACKAGE} import {TEST_MODULE}")
        print_result(f"from {TEST_PACKAGE} import {TEST_MODULE}", True)
    except Exception as e:
        print_result(f"from {TEST_PACKAGE} import {TEST_MODULE}", False, str(e))
    
    # TEST 3: Import using dot notation
    print("\n[TEST 3] Import using dot notation")
    try:
        exec(f"import {TEST_PACKAGE}.{TEST_MODULE}")
        print_result(f"import {TEST_PACKAGE}.{TEST_MODULE}", True)
    except Exception as e:
        print_result(f"import {TEST_PACKAGE}.{TEST_MODULE}", False, str(e))
    
    # ===== FOCUS: Load main module only =====
    # We don't test submodules individually - ha_interconnect.py imports them all
    
    # ===== MODULE FILE INSPECTION =====
    print_test_header("MAIN MODULE FILE INSPECTION")
    
    module_path = os.path.join(package_dir, f"{TEST_MODULE}.py")
    
    if not os.path.exists(module_path):
        print(f"⚠️  {TEST_MODULE}.py not found in {TEST_PACKAGE}/")
    else:
        try:
            with open(module_path, 'r') as f:
                lines = f.readlines()
            
            print(f"File: {TEST_MODULE}.py")
            print(f"Total lines: {len(lines)}")
            print(f"\nImport statements (all lines):")
            
            import_lines = []
            for i, line in enumerate(lines, 1):
                stripped = line.strip()
                if (stripped.startswith(('import ', 'from ')) and 
                    not stripped.startswith('#')):
                    import_lines.append((i, line.rstrip()))
            
            if import_lines:
                for line_num, import_stmt in import_lines:
                    print(f"  Line {line_num:3d}: {import_stmt}")
                print(f"\nTotal imports found: {len(import_lines)}")
            else:
                print(f"  No import statements found")
        except Exception as e:
            print(f"❌ ERROR reading {TEST_MODULE}.py: {e}")
    
    # ===== IMPORT STYLE ANALYSIS =====
    print_test_header("IMPORT STYLE ANALYSIS FOR MAIN MODULE")
    
    if os.path.exists(module_path):
        print(f"Analyzing import styles in {TEST_MODULE}.py:\n")
        
        try:
            with open(module_path, 'r') as f:
                content = f.read()
            
            # Count different import types
            relative_imports = [l.strip() for l in content.splitlines() 
                              if l.strip().startswith('from .') and not l.strip().startswith('#')]
            absolute_package_imports = [l.strip() for l in content.splitlines() 
                                       if l.strip().startswith(f'from {TEST_PACKAGE}.') 
                                       and not l.strip().startswith('#')]
            absolute_imports = [l.strip() for l in content.splitlines() 
                              if l.strip().startswith('from ') 
                              and not l.strip().startswith(('from .', f'from {TEST_PACKAGE}.', '#'))]
            
            print(f"Relative imports (from .module): {len(relative_imports)}")
            if relative_imports:
                for ri in relative_imports[:5]:
                    print(f"  {ri}")
                if len(relative_imports) > 5:
                    print(f"  ... and {len(relative_imports) - 5} more")
            
            print(f"\nAbsolute package imports (from {TEST_PACKAGE}.module): {len(absolute_package_imports)}")
            if absolute_package_imports:
                for ai in absolute_package_imports[:5]:
                    print(f"  {ai}")
                if len(absolute_package_imports) > 5:
                    print(f"  ... and {len(absolute_package_imports) - 5} more")
            
            print(f"\nOther imports: {len(absolute_imports)}")
            if absolute_imports:
                for oi in absolute_imports[:5]:
                    print(f"  {oi}")
                if len(absolute_imports) > 5:
                    print(f"  ... and {len(absolute_imports) - 5} more")
            
            # Recommendation
            print(f"\n{'=' * 60}")
            print("RECOMMENDATION:")
            if relative_imports and not absolute_package_imports:
                print(f"✗ Using relative imports (from .module)")
                print(f"  These may not work when importing via: from {TEST_PACKAGE} import {TEST_MODULE}")
                print(f"\n  Try changing to: from {TEST_PACKAGE}.module_name import ...")
            elif absolute_package_imports and not relative_imports:
                print(f"✓ Using absolute package imports (from {TEST_PACKAGE}.module)")
                print(f"  This should work correctly")
            elif relative_imports and absolute_package_imports:
                print(f"⚠ MIXED import styles detected!")
                print(f"  {len(relative_imports)} relative, {len(absolute_package_imports)} absolute")
                print(f"  Consider using only one style for consistency")
            print(f"{'=' * 60}")
            
        except Exception as e:
            print(f"❌ ERROR analyzing imports: {e}")
    
    # ===== sys.modules CHECK =====
    print_test_header("sys.modules CHECK")
    
    loaded_modules = [k for k in sys.modules.keys() if TEST_PACKAGE in k]
    print(f"Modules loaded containing '{TEST_PACKAGE}': {len(loaded_modules)}")
    if loaded_modules:
        for mod in sorted(loaded_modules):
            print(f"  ✓ {mod}")
    else:
        print(f"  (none)")
    
    # ===== SUMMARY =====
    print_test_header("TEST COMPLETE")
    print(f"Package tested: {TEST_PACKAGE}")
    print(f"Module tested: {TEST_MODULE}")
    print(f"Submodules tested: {len(TEST_SUBMODULES)}")
    print(f"\nAll tests completed. Review results above.")
    print("=" * 80)


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler - runs tests and exits.
    
    Args:
        event: Lambda event (ignored)
        context: Lambda context (ignored)
        
    Returns:
        Never returns - exits after tests
    """
    print("[LAMBDA HANDLER] Starting universal import diagnostic tests...")
    
    # Run all tests
    run_import_tests()
    
    # Exit cleanly
    print("\n[LAMBDA HANDLER] Tests complete - exiting")
    sys.exit(0)


# EOF
