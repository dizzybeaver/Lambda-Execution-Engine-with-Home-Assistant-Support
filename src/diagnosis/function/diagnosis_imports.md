# diagnosis_imports.py

**Version:** 2025-12-08_1  
**Module:** DIAGNOSIS Interface  
**Layer:** Core  
**Lines:** 135

---

## Purpose

Import testing and diagnostics for Lambda module loading. Tests module imports sequentially, measures timing, and diagnoses import failures.

---

## Functions

### test_module_import()

**Purpose:** Test importing a single module with timing

**Signature:**
```python
def test_module_import(module_name: str, import_func: Callable = None) -> Dict[str, Any]
```

**Parameters:**
- `module_name` - Module name to test (e.g., 'gateway_core', 'interface_cache')
- `import_func` - Optional callable that performs the import (default: None uses __import__)

**Returns:**
```python
{
    'test': str,              # Module name tested
    'success': bool,          # True if import succeeded
    'duration_ms': float,     # Import duration in milliseconds
    'error': str              # Error message (only if failed)
}
```

**Behavior:**
1. Records start time using time.time()
2. Attempts import via import_func or __import__(module_name)
3. Calculates duration in milliseconds
4. Returns success dict with timing
5. On failure, captures exception and returns error dict

**Timing:**
Uses time.time() for millisecond precision (not time.perf_counter())

**Error Scenarios:**
- ImportError → Returns `{'test': module_name, 'success': False, 'duration_ms': X, 'error': str(e)}`
- Any Exception → Same error structure

**Usage:**
```python
from diagnosis_imports import test_module_import

# Test basic import
result = test_module_import('gateway_core')
if result['success']:
    print(f"✓ Imported in {result['duration_ms']:.2f}ms")
else:
    print(f"✗ Failed: {result['error']}")

# Test with custom import function
def custom_import():
    from gateway import execute_operation
    
result = test_module_import('gateway.execute_operation', custom_import)
```

**Performance:** Variable (depends on module complexity, typically 5-500ms)

---

### test_import_sequence()

**Purpose:** Test importing modules sequentially and stop on first failure

**Signature:**
```python
def test_import_sequence(modules: List[str]) -> Dict[str, Any]
```

**Parameters:**
- `modules` - List of module names to test in order

**Returns:**
```python
{
    'statusCode': 200,
    'body': str  # JSON string containing:
    {
        'status': 'diagnostic_complete',
        'message': str,
        'results': List[Dict],
        'total_tests': int,
        'passed': int,
        'failed': int
    }
}
```

**Behavior:**
1. Iterates through modules list in order
2. Calls test_module_import() for each module
3. Appends result to results list
4. On first failure, stops testing and returns diagnostic response
5. If all pass, returns success diagnostic response

**Stop-on-Failure:**
Critical for debugging - identifies exactly which module breaks the import chain

**Usage:**
```python
from diagnosis_imports import test_import_sequence

modules = [
    'gateway_core',
    'gateway_wrappers',
    'gateway',
    'interface_cache',
    'cache_core'
]

response = test_import_sequence(modules)
body = json.loads(response['body'])

print(f"Status: {body['message']}")
print(f"Passed: {body['passed']}/{body['total_tests']}")

for result in body['results']:
    status = '✓' if result['success'] else '✗'
    print(f"{status} {result['test']}: {result['duration_ms']:.2f}ms")
```

**Example Output:**
```python
{
    'statusCode': 200,
    'body': '{
        "status": "diagnostic_complete",
        "message": "Failed at interface_cache",
        "results": [
            {"test": "gateway_core", "success": true, "duration_ms": 45.2},
            {"test": "gateway_wrappers", "success": true, "duration_ms": 123.7},
            {"test": "gateway", "success": true, "duration_ms": 5.1},
            {"test": "interface_cache", "success": false, "duration_ms": 12.3, "error": "No module named..."}
        ],
        "total_tests": 4,
        "passed": 3,
        "failed": 1
    }'
}
```

**Performance:** Sum of individual module import times (typically 100-2000ms for full sequence)

---

### format_diagnostic_response()

**Purpose:** Format test results into Lambda-compatible response structure

**Signature:**
```python
def format_diagnostic_response(results: List[Dict[str, Any]], message: str) -> Dict[str, Any]
```

**Parameters:**
- `results` - List of test result dictionaries from test_module_import()
- `message` - Summary message (e.g., "All imports successful", "Failed at module_x")

**Returns:**
```python
{
    'statusCode': 200,
    'body': str  # JSON string with indent=2
}
```

**Body Structure:**
```python
{
    'status': 'diagnostic_complete',
    'message': str,
    'results': List[Dict],
    'total_tests': int,
    'passed': int,
    'failed': int
}
```

**Behavior:**
1. Counts passed tests (success == True)
2. Counts failed tests (success == False)
3. Creates response body dict
4. JSON encodes with indent=2 for readability
5. Wraps in Lambda response structure (statusCode=200)

**Usage:**
```python
from diagnosis_imports import format_diagnostic_response

results = [
    {'test': 'gateway', 'success': True, 'duration_ms': 45.2},
    {'test': 'cache', 'success': True, 'duration_ms': 23.1}
]

response = format_diagnostic_response(results, "All imports successful")
print(response)
# {
#     'statusCode': 200,
#     'body': '{\n  "status": "diagnostic_complete",\n  "message": "All imports successful",\n  ...\n}'
# }
```

**Performance:** <1ms (JSON encoding only)

---

### diagnose_import_failure()

**Purpose:** Diagnose why a module import failed

**Signature:**
```python
def diagnose_import_failure(module_name: str) -> Dict[str, Any]
```

**Parameters:**
- `module_name` - Module that failed to import

**Returns:**
```python
{
    'module': str,
    'checks': {
        'file_exists': bool,
        'sys_path': List[str],
        'already_imported': bool,
        'import_result': 'success' | 'failed',
        'import_error': str,           # If ImportError
        'unexpected_error': {          # If other Exception
            'type': str,
            'message': str
        }
    }
}
```

**Checks Performed:**
1. **File Exists:** Checks if module_name.py exists on filesystem
2. **sys.path:** Returns current Python path for debugging
3. **Already Imported:** Checks if module in sys.modules
4. **Import Attempt:** Tries import and captures detailed error

**Behavior:**
1. Converts module name to file path (replace '.' with '/')
2. Checks if .py file exists
3. Gets sys.path snapshot
4. Checks sys.modules for existing import
5. Attempts fresh import
6. Captures ImportError or unexpected Exception
7. Returns diagnostic dict

**Usage:**
```python
from diagnosis_imports import diagnose_import_failure

# After an import fails
diagnosis = diagnose_import_failure('interface_cache')

print(f"File exists: {diagnosis['checks']['file_exists']}")
print(f"Already imported: {diagnosis['checks']['already_imported']}")
print(f"Import result: {diagnosis['checks']['import_result']}")

if diagnosis['checks']['import_result'] == 'failed':
    error = diagnosis['checks'].get('import_error') or diagnosis['checks'].get('unexpected_error')
    print(f"Error: {error}")
```

**Performance:** ~5-20ms (includes file I/O and import attempt)

---

## Architecture Integration

**SUGA Layer:** Core  
**Interface:** DIAGNOSIS (INT-13)  
**Gateway Access:** Via gateway wrappers

**Import Pattern:**
```python
# From gateway
from gateway import test_module_import, test_import_sequence

# Direct (for testing)
from diagnosis_imports import test_module_import, test_import_sequence

result = test_module_import('gateway_core')
```

---

## Dependencies

**Internal:** None (standalone module)

**External:**
- time (timing measurements)
- typing (Dict, Any, List, Callable)

---

## Use Cases

### Lambda Cold Start Diagnosis
Test which modules are slow to import during Lambda initialization

```python
critical_modules = [
    'lambda_preload',
    'gateway_core',
    'gateway_wrappers',
    'gateway'
]

response = test_import_sequence(critical_modules)
# Identify slow imports in cold start
```

### Import Chain Debugging
Find exactly where import chain breaks

```python
all_modules = [
    'gateway_core',
    'interface_cache',
    'cache_core',
    'interface_logging',
    'logging_core'
]

response = test_import_sequence(all_modules)
# Stops at first failure, pinpoints issue
```

### Module Load Time Profiling
Measure individual module import times

```python
modules = ['heavy_module', 'light_module']
for module in modules:
    result = test_module_import(module)
    print(f"{module}: {result['duration_ms']:.2f}ms")
```

---

## Related Files

**Core Files:**
- diagnosis_performance.py - Performance diagnostics
- diagnosis_core.py - Core validation logic

**Lambda Files:**
- lambda_diagnostic.py - Uses these functions for Lambda mode testing

**Interface:**
- interface_diagnosis.py - DIAGNOSIS interface router

---

## Changelog

### 2025-12-08_1
- Initial version migrated from lambda_diagnostic.py
- 4 functions: test_module_import, test_import_sequence, format_diagnostic_response, diagnose_import_failure
- Preserved exact timing logic (time.time() for consistency)
- Preserved stop-on-failure behavior for test_import_sequence
- Minimal docstrings per SIMA standards
