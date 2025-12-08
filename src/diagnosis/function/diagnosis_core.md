# diagnosis_core.py

**Version:** 2025-12-08_1  
**Module:** DIAGNOSIS Interface  
**Layer:** Core  
**Lines:** 95

---

## Purpose

Core diagnosis operations and validation. Validates SUGA architecture compliance, import patterns, gateway routing, and provides comprehensive diagnostic suite.

---

## Functions

### validate_system_architecture()

**Purpose:** Validate SUGA architecture compliance

**Signature:**
```python
def validate_system_architecture(**kwargs) -> Dict[str, Any]
```

**Returns:**
```python
{
    'success': bool,
    'compliant': bool,
    'issues': List[str]
}
```

**Behavior:**
1. Checks gateway._OPERATION_REGISTRY exists and not empty
2. Calls validate_imports() to check import compliance
3. Collects violations from import check
4. Determines overall compliance (True if no issues)
5. Returns validation result

**Validation Checks:**
- **Operation Registry:** Must exist and not be empty
- **Import Compliance:** No direct cross-imports between modules

**Error Scenarios:**
- ImportError → Returns `{'success': False, 'error': str(e)}`
- Exception → Same error structure

**Usage:**
```python
from diagnosis_core import validate_system_architecture

result = validate_system_architecture()

if result['success']:
    if result['compliant']:
        print("✓ SUGA architecture compliant")
    else:
        print("✗ Architecture issues:")
        for issue in result['issues']:
            print(f"  - {issue}")
else:
    print(f"Error: {result['error']}")
```

**Performance:** ~20-50ms (includes import validation)

---

### validate_imports()

**Purpose:** Validate no direct imports between modules

**Signature:**
```python
def validate_imports(**kwargs) -> Dict[str, Any]
```

**Returns:**
```python
{
    'success': bool,
    'compliant': bool,
    'violations': List[str],     # If import_fixer available
    'note': str                   # If import_fixer not available
}
```

**Behavior:**
1. Attempts to import import_fixer
2. If available: Calls validate_imports('.') to check current directory
3. Returns validation results with violations list
4. If unavailable: Returns compliant=True with note

**SUGA Pattern Enforcement:**
Validates that:
- No direct imports between core modules
- All cross-interface calls go through gateway
- Import pattern follows Gateway → Interface → Core

**Error Scenarios:**
- ImportError (import_fixer) → Returns `{'success': True, 'compliant': True, 'note': 'import_fixer not available'}`
- This is non-critical (development tool)

**Usage:**
```python
from diagnosis_core import validate_imports

result = validate_imports()

if result.get('compliant'):
    print("✓ Import patterns compliant")
else:
    print("✗ Import violations:")
    for violation in result.get('violations', []):
        print(f"  - {violation}")
```

**Performance:** ~50-200ms (scans all Python files if import_fixer available)

---

### validate_gateway_routing()

**Purpose:** Validate all gateway routing works

**Signature:**
```python
def validate_gateway_routing(**kwargs) -> Dict[str, Any]
```

**Returns:**
```python
{
    'success': bool,
    'compliant': bool,
    'results': {
        'tested': int,
        'passed': int,
        'failed': List[str]
    }
}
```

**Behavior:**
1. Defines test operations list:
   - (GatewayInterface.CACHE, 'get_stats')
   - (GatewayInterface.LOGGING, 'get_stats')
   - (GatewayInterface.METRICS, 'get_stats')
2. For each operation:
   - Calls gateway.execute_operation(interface, operation)
   - Records pass/fail
3. Determines compliance (all tests passed)
4. Returns results dict

**Test Operations:**
Tests representative operations from different interfaces to validate routing works across all layers.

**Error Scenarios:**
- execute_operation() exception → Captured in failed list
- Overall failure → Returns `{'success': False, 'error': str(e)}`

**Usage:**
```python
from diagnosis_core import validate_gateway_routing

result = validate_gateway_routing()

print(f"Tested: {result['results']['tested']}")
print(f"Passed: {result['results']['passed']}")

if result['results']['failed']:
    print("Failed operations:")
    for failure in result['results']['failed']:
        print(f"  - {failure}")
```

**Performance:** ~10-30ms (executes 3 gateway operations)

---

### run_diagnostic_suite()

**Purpose:** Run comprehensive diagnostic suite

**Signature:**
```python
def run_diagnostic_suite(**kwargs) -> Dict[str, Any]
```

**Returns:**
```python
{
    'timestamp': str,
    'suite': 'comprehensive',
    'results': {
        'health': Dict,              # generate_health_report() result
        'system': Dict,              # diagnose_system_health() result
        'architecture': Dict,        # validate_system_architecture() result
        'imports': Dict,             # validate_imports() result
        'gateway_routing': Dict      # validate_gateway_routing() result
    }
}
```

**Behavior:**
1. Runs generate_health_report() → results['health']
2. Runs diagnose_system_health() → results['system']
3. Runs validate_system_architecture() → results['architecture']
4. Runs validate_imports() → results['imports']
5. Runs validate_gateway_routing() → results['gateway_routing']
6. Captures exceptions for each test (stores error dict)
7. Aggregates all results into comprehensive report

**Suite Components:**
- **Health:** Comprehensive health report with dispatcher metrics
- **System:** System health diagnosis (components, gateway, memory)
- **Architecture:** SUGA compliance validation
- **Imports:** Import pattern validation
- **Gateway Routing:** Routing functionality validation

**Error Handling:**
Each test wrapped in try/except - failures don't stop suite execution

**Usage:**
```python
from diagnosis_core import run_diagnostic_suite

report = run_diagnostic_suite()

print(f"Suite: {report['suite']}")
print(f"Timestamp: {report['timestamp']}")

# Check health
if 'error' not in report['results']['health']:
    print(f"✓ Health report generated")
else:
    print(f"✗ Health report error: {report['results']['health']['error']}")

# Check architecture
if report['results']['architecture'].get('compliant'):
    print("✓ Architecture compliant")
else:
    print(f"✗ Architecture issues: {report['results']['architecture'].get('issues', [])}")

# Check imports
if report['results']['imports'].get('compliant'):
    print("✓ Imports compliant")
    
# Check routing
if report['results']['gateway_routing'].get('compliant'):
    print("✓ Gateway routing functional")
```

**Performance:** ~200-500ms (runs 5 diagnostic operations)

**Example Output:**
```python
{
    'timestamp': '2025-12-08',
    'suite': 'comprehensive',
    'results': {
        'health': {
            'timestamp': '2025-12-08',
            'system_health': {...},
            'validation': {...},
            ...
        },
        'system': {
            'success': True,
            'component_health': {...},
            ...
        },
        'architecture': {
            'success': True,
            'compliant': True,
            'issues': []
        },
        'imports': {
            'success': True,
            'compliant': True,
            'note': 'import_fixer not available'
        },
        'gateway_routing': {
            'success': True,
            'compliant': True,
            'results': {
                'tested': 3,
                'passed': 3,
                'failed': []
            }
        }
    }
}
```

---

## Architecture Integration

**SUGA Layer:** Core  
**Interface:** DIAGNOSIS (INT-13)  
**Gateway Access:** Via gateway wrappers

**Import Pattern:**
```python
# From gateway
from gateway import validate_system_architecture, run_diagnostic_suite

# Direct (for testing)
from diagnosis_core import validate_system_architecture, run_diagnostic_suite

result = validate_system_architecture()
report = run_diagnostic_suite()
```

---

## Dependencies

**Internal:**
- gateway (_OPERATION_REGISTRY, execute_operation, GatewayInterface)
- import_fixer (optional, for validate_imports)
- diagnosis_health (generate_health_report)
- diagnosis_performance (diagnose_system_health)

**External:**
- typing (Dict, Any)

---

## Use Cases

### Pre-Deployment Validation
Run full diagnostic suite before deploying to production

```python
report = run_diagnostic_suite()

# Check all critical areas
if (report['results']['architecture'].get('compliant') and
    report['results']['gateway_routing'].get('compliant')):
    print("✓ Ready for deployment")
else:
    print("✗ Fix issues before deploying")
```

### Continuous Monitoring
Validate architecture compliance in CI/CD pipeline

```python
result = validate_system_architecture()
if not result.get('compliant'):
    sys.exit(1)  # Fail CI/CD build
```

### Import Compliance Check
Ensure SUGA pattern maintained during development

```python
result = validate_imports()
if result.get('violations'):
    for violation in result['violations']:
        print(f"VIOLATION: {violation}")
```

---

## Related Files

**Core Files:**
- diagnosis_health_checks.py - Health checks
- diagnosis_performance.py - Performance diagnostics
- diagnosis_imports.py - Import testing

**Interface:**
- interface_diagnosis.py - DIAGNOSIS interface router

**Gateway:**
- gateway_wrappers_diagnosis.py - Gateway wrappers

**Tools:**
- import_fixer.py - Import validation tool (optional)

---

## Changelog

### 2025-12-08_1
- Initial version migrated from debug_validation.py
- 4 functions: validate_system_architecture, validate_imports, validate_gateway_routing, run_diagnostic_suite
- Preserved exact validation logic
- Added comprehensive diagnostic suite aggregator
- Minimal docstrings per SIMA standards
