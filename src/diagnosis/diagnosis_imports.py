"""
diagnosis/diagnosis_imports.py
Version: 2025-12-08_1
Purpose: Import testing and diagnostics
License: Apache 2.0
"""

import time
from typing import Dict, Any, List, Callable


def test_module_import(module_name: str, import_func: Callable = None) -> Dict[str, Any]:
    """Test importing a single module."""
    start = time.time()
    
    try:
        if import_func:
            import_func()
        else:
            __import__(module_name)
        
        duration = (time.time() - start) * 1000
        return {
            'test': module_name,
            'success': True,
            'duration_ms': round(duration, 2)
        }
    
    except Exception as e:
        duration = (time.time() - start) * 1000
        return {
            'test': module_name,
            'success': False,
            'duration_ms': round(duration, 2),
            'error': str(e)
        }


def test_import_sequence(modules: List[str]) -> Dict[str, Any]:
    """Test importing modules sequentially."""
    results = []
    
    for module_name in modules:
        result = test_module_import(module_name)
        results.append(result)
        
        # Stop on first failure for diagnostic purposes
        if not result['success']:
            message = f"Failed at {module_name}"
            return format_diagnostic_response(results, message)
    
    return format_diagnostic_response(results, "All imports successful")


def format_diagnostic_response(results: List[Dict[str, Any]], message: str) -> Dict[str, Any]:
    """Format diagnostic test results into response structure."""
    import json
    
    passed = sum(1 for r in results if r.get('success'))
    failed = sum(1 for r in results if not r.get('success'))
    
    response_body = {
        'status': 'diagnostic_complete',
        'message': message,
        'results': results,
        'total_tests': len(results),
        'passed': passed,
        'failed': failed
    }
    
    return {
        'statusCode': 200,
        'body': json.dumps(response_body, indent=2)
    }


def diagnose_import_failure(module_name: str) -> Dict[str, Any]:
    """Diagnose why a module import failed."""
    import sys
    import os
    
    diagnostics = {
        'module': module_name,
        'checks': {}
    }
    
    # Check if module file exists
    module_path = module_name.replace('.', '/') + '.py'
    diagnostics['checks']['file_exists'] = os.path.exists(module_path)
    
    # Check sys.path
    diagnostics['checks']['sys_path'] = sys.path.copy()
    
    # Check if already imported
    diagnostics['checks']['already_imported'] = module_name in sys.modules
    
    # Try import with detailed error
    try:
        __import__(module_name)
        diagnostics['checks']['import_result'] = 'success'
    except ImportError as e:
        diagnostics['checks']['import_result'] = 'failed'
        diagnostics['checks']['import_error'] = str(e)
    except Exception as e:
        diagnostics['checks']['import_result'] = 'failed'
        diagnostics['checks']['unexpected_error'] = {
            'type': type(e).__name__,
            'message': str(e)
        }
    
    return diagnostics


__all__ = [
    'test_module_import',
    'test_import_sequence',
    'format_diagnostic_response',
    'diagnose_import_failure'
]
