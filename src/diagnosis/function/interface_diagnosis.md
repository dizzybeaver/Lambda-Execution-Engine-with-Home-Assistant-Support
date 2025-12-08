# interface_diagnosis.py

**Version:** 2025-12-08_1  
**Module:** DIAGNOSIS Interface  
**Layer:** Interface  
**Lines:** 87

---

## Purpose

Interface router for DIAGNOSIS operations (INT-13). Routes 21 diagnostic operations to core implementations using dictionary dispatch pattern.

---

## Architecture

**SUGA Pattern:**
```
Gateway → interface_diagnosis.py → Core Modules
```

**Dispatch Dictionary:**
Maps operation names to core functions with O(1) lookup.

---

## Operations Routed (21 Total)

### Import Testing (4 operations)
- `test_module_import` → diagnosis_imports.py
- `test_import_sequence` → diagnosis_imports.py
- `format_diagnostic_response` → diagnosis_imports.py
- `diagnose_import_failure` → diagnosis_imports.py

### Performance Diagnostics (6 operations)
- `diagnose_system_health` → diagnosis_performance.py
- `diagnose_component_performance` → diagnosis_performance.py
- `diagnose_memory_usage` → diagnosis_performance.py
- `diagnose_initialization_performance` → diagnosis_performance.py
- `diagnose_utility_performance` → diagnosis_performance.py
- `diagnose_singleton_performance` → diagnosis_performance.py

### Validation (4 operations)
- `validate_system_architecture` → diagnosis_core.py
- `validate_imports` → diagnosis_core.py
- `validate_gateway_routing` → diagnosis_core.py
- `run_diagnostic_suite` → diagnosis_core.py

### Health Checks (7 operations)
- `check_component_health` → diagnosis_health_checks.py
- `check_gateway_health` → diagnosis_health_checks.py
- `generate_health_report` → diagnosis_health_checks.py
- `check_initialization_health` → diagnosis_health_interface.py
- `check_utility_health` → diagnosis_health_interface.py
- `check_singleton_health` → diagnosis_health_interface.py
- `check_system_health` → diagnosis_health_system.py

---

## Functions

### execute_diagnosis_operation()

**Purpose:** Route diagnosis operations to core implementations

**Signature:**
```python
def execute_diagnosis_operation(operation: str, **kwargs) -> Any
```

**Parameters:**
- `operation` - Operation name (e.g., 'test_module_import')
- `**kwargs` - Operation-specific parameters

**Returns:**
Operation result (varies by operation)

**Behavior:**
1. Checks if DIAGNOSIS available (imports succeeded)
2. Looks up operation in _DISPATCH dictionary
3. Calls handler function with kwargs
4. Returns result

**Error Scenarios:**
- DIAGNOSIS unavailable → RuntimeError with import error details
- Unknown operation → ValueError with operation name

**Usage:**
```python
from interface_diagnosis import execute_diagnosis_operation

# Via interface
result = execute_diagnosis_operation('test_module_import', module_name='gateway_core')

# Via gateway (preferred)
from gateway import test_module_import
result = test_module_import('gateway_core')
```

**Performance:** <1ms (dictionary lookup overhead only)

---

## Error Handling

### Import Failure
If core modules fail to import:
- `_DIAGNOSIS_AVAILABLE` = False
- `_DIAGNOSIS_IMPORT_ERROR` = Error message
- All operations raise RuntimeError with details

### Unknown Operation
If operation not in dispatch dictionary:
- Raises ValueError with operation name
- Lists valid operations implicitly via dispatch keys

---

## Core Module Dependencies

**Import Groups:**
```python
# Group 1: Import Testing
from diagnosis_imports import (4 functions)

# Group 2: Performance
from diagnosis_performance import (6 functions)

# Group 3: Validation
from diagnosis_core import (4 functions)

# Group 4: Health Checks
from diagnosis_health_checks import (3 functions)
from diagnosis_health_interface import (3 functions)
from diagnosis_health_system import (1 function)
```

**Total:** 21 functions from 6 modules

---

## Dispatch Dictionary Pattern

**Structure:**
```python
_DISPATCH = {
    'operation_name': function_reference,
    ...
} if _DIAGNOSIS_AVAILABLE else {}
```

**Benefits:**
- O(1) operation lookup
- Easy to add new operations (1 line)
- Clear operation → function mapping
- Supports operation aliases (same function, different keys)

**vs elif Chain:**
- Dictionary: O(1) lookup
- elif chain: O(n) lookup (n = number of operations)

---

## Integration with Gateway

**Gateway Integration:**
```python
# In gateway.py
from gateway_wrappers_diagnosis import *

# Or explicit imports
from gateway_wrappers_diagnosis import (
    test_module_import,
    diagnose_system_health,
    check_system_health,
    # ... all 21 functions
)

# Export
__all__ = [
    # ... existing exports
    'test_module_import',
    'diagnose_system_health',
    'check_system_health',
    # ... all 21 functions
]
```

**Usage via Gateway:**
```python
import gateway

# Import testing
result = gateway.test_module_import('gateway_core')

# Performance
health = gateway.diagnose_system_health()

# Validation
valid = gateway.validate_system_architecture()

# Health checks
report = gateway.check_system_health()
```

---

## Related Files

**Core Modules:**
- diagnosis_imports.py (4 functions)
- diagnosis_performance.py (6 functions)
- diagnosis_core.py (4 functions)
- diagnosis_health_checks.py (3 functions)
- diagnosis_health_interface.py (3 functions)
- diagnosis_health_system.py (1 function)

**Gateway Integration:**
- gateway_wrappers_diagnosis.py (21 wrapper functions)
- gateway.py (imports and exports wrappers)

---

## Changelog

### 2025-12-08_1
- Initial version for DIAGNOSIS interface (INT-13)
- 21 operations routed to 6 core modules
- Dictionary dispatch pattern (O(1) lookup)
- Minimal docstrings per SIMA standards
- Import error handling
