"""
lambda_diagnostic.py - DIAGNOSTIC VERSION
Version: 2025.10.15.DIAGNOSTIC
Description: Test imports one at a time to find the hang
"""

import json
import time
from typing import Dict, Any


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Diagnostic handler - test imports step by step.
    """
    
    results = []
    
    def test_import(name: str, import_func):
        """Test a single import."""
        print(f"[DIAG] Testing: {name}")
        start = time.time()
        try:
            import_func()
            duration = (time.time() - start) * 1000
            print(f"[DIAG] ✓ {name}: {duration:.2f}ms")
            results.append({"test": name, "success": True, "duration_ms": duration})
            return True
        except Exception as e:
            duration = (time.time() - start) * 1000
            print(f"[DIAG] ✗ {name}: {duration:.2f}ms - {str(e)}")
            results.append({"test": name, "success": False, "duration_ms": duration, "error": str(e)})
            return False
    
    print(f"[DIAG] Starting import diagnostics")
    
    # Test 1: gateway_core
    if not test_import("gateway_core", lambda: __import__('gateway_core')):
        return _create_response(results, "Failed at gateway_core")
    
    # Test 2: gateway_wrappers
    if not test_import("gateway_wrappers", lambda: __import__('gateway_wrappers')):
        return _create_response(results, "Failed at gateway_wrappers")
    
    # Test 3: gateway (combined)
    if not test_import("gateway", lambda: __import__('gateway')):
        return _create_response(results, "Failed at gateway")
    
    # Test 4: Try to import specific functions
    def import_gateway_functions():
        from gateway import log_info, format_response
    
    if not test_import("gateway functions", import_gateway_functions):
        return _create_response(results, "Failed importing gateway functions")
    
    # Test 5: Try to call log_info
    def call_log_info():
        from gateway import log_info
        log_info("Test log")
    
    if not test_import("log_info call", call_log_info):
        return _create_response(results, "Failed calling log_info")
    
    # Test 6: Try format_response
    def call_format_response():
        from gateway import format_response
        return format_response(200, {"test": "ok"})
    
    if not test_import("format_response call", call_format_response):
        return _create_response(results, "Failed calling format_response")
    
    print(f"[DIAG] All tests passed!")
    return _create_response(results, "All imports successful")


def _create_response(results, message):
    """Create diagnostic response."""
    return {
        "statusCode": 200,
        "body": json.dumps({
            "status": "diagnostic_complete",
            "message": message,
            "results": results,
            "total_tests": len(results),
            "passed": sum(1 for r in results if r.get('success')),
            "failed": sum(1 for r in results if not r.get('success'))
        }, indent=2)
    }

# EOF
