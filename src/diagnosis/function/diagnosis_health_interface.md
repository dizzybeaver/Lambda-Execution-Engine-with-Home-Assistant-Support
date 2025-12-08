# diagnosis_health_interface.py

**Version:** 2025-12-08_1  
**Module:** DIAGNOSIS Interface  
**Layer:** Core  
**Lines:** 249

---

## Purpose

Interface-specific health checks for INITIALIZATION, UTILITY, and SINGLETON interfaces. Validates compliance with AP-08, DEC-04, LESS-17, LESS-18, and LESS-21 standards.

---

## Compliance Standards

**AP-08:** No threading locks (Lambda single-threaded)  
**DEC-04:** Lambda single-threaded execution model  
**LESS-17:** Threading locks unnecessary in Lambda  
**LESS-18:** SINGLETON pattern required for managers  
**LESS-21:** Rate limiting required for DoS protection

---

## Functions

### check_initialization_health()

**Purpose:** Check INITIALIZATION interface health and compliance

**Signature:**
```python
def check_initialization_health(**kwargs) -> Dict[str, Any]
```

**Returns:**
```python
{
    'interface': 'INITIALIZATION',
    'timestamp': float,
    'checks': {
        'singleton_registered': {
            'status': 'pass' | 'fail',
            'value': bool,
            'requirement': str
        },
        'rate_limiting': {
            'status': 'pass' | 'fail',
            'value': bool,
            'rate': str,
            'requirement': str
        },
        'no_threading_locks': {
            'status': 'pass' | 'fail',
            'value': bool,
            'lock_import': bool,
            'lock_usage': bool,
            'requirement': str
        },
        'reset_available': {
            'status': 'pass' | 'fail',
            'value': bool,
            'requirement': str
        }
    },
    'compliance': {
        'ap_08': bool,
        'dec_04': bool,
        'less_17': bool,
        'less_18': bool,
        'less_21': bool
    },
    'status': 'healthy' | 'degraded' | 'critical'
}
```

**Checks Performed:**
1. **SINGLETON Registration:** Verifies initialization_manager registered
2. **Rate Limiting:** Checks for _rate_limiter attribute (1000 ops/sec)
3. **No Threading Locks:** Scans source code for Lock() or threading imports
4. **Reset Available:** Verifies reset() method exists

**Status Determination:**
- **critical:** Threading locks found (AP-08 violation)
- **degraded:** Any check fails (non-critical)
- **healthy:** All checks pass

**Source Code Scanning:**
Checks for these patterns in initialization_core.py:
- `from threading import Lock`
- `import threading`
- `Lock()`
- `self._lock`

**Error Scenarios:**
- ImportError → Returns error dict with timestamp
- File read error → Propagates exception

**Usage:**
```python
from diagnosis_health_interface import check_initialization_health

health = check_initialization_health()
if health['status'] == 'critical':
    print(f"CRITICAL: {health['checks']['no_threading_locks']}")
elif health['status'] == 'degraded':
    print(f"DEGRADED: Review checks {health['checks']}")
```

**Performance:** ~20-50ms (includes file I/O for source scanning)

---

### check_utility_health()

**Purpose:** Check UTILITY interface health and compliance

**Signature:**
```python
def check_utility_health(**kwargs) -> Dict[str, Any]
```

**Returns:** Same structure as check_initialization_health() with interface='UTILITY'

**Checks Performed:**
1. **SINGLETON Registration:** Verifies utility_manager registered
2. **Rate Limiting:** Checks SharedUtilityCore for _rate_limiter
3. **No Threading Locks:** Scans utility_core.py source
4. **Reset Available:** Verifies SharedUtilityCore.reset() exists

**Source Code Scanning:**
Checks for these patterns in utility_core.py:
- `import threading`
- `Lock()`
- `self._lock`

**Status Determination:**
- **critical:** Threading locks found
- **degraded:** Any check fails (non-critical)
- **healthy:** All checks pass

**Usage:**
```python
from diagnosis_health_interface import check_utility_health

health = check_utility_health()
print(f"UTILITY status: {health['status']}")
print(f"Compliance: {health['compliance']}")
```

**Performance:** ~20-50ms

---

### check_singleton_health()

**Purpose:** Check SINGLETON interface health and compliance

**Signature:**
```python
def check_singleton_health(**kwargs) -> Dict[str, Any]
```

**Returns:** Same structure as check_initialization_health() with interface='SINGLETON'

**Checks Performed:**
1. **SINGLETON Registration:** Verifies singleton_manager registered
2. **Rate Limiting:** Checks SingletonCore for _rate_limiter
3. **No Threading Locks:** Scans singleton_core.py source
4. **Reset Available:** Verifies SingletonCore.reset() exists

**Source Code Scanning:**
Checks for these patterns in singleton_core.py:
- `from threading import Lock`
- `import threading`
- `Lock()`
- `self._lock`

**Status Determination:**
- **critical:** Threading locks found (most severe for SINGLETON)
- **degraded:** Any check fails (non-critical)
- **healthy:** All checks pass

**Usage:**
```python
from diagnosis_health_interface import check_singleton_health

health = check_singleton_health()
if not health['compliance']['ap_08']:
    print("WARNING: AP-08 violation - threading locks found!")
```

**Performance:** ~20-50ms

---

## Common Patterns

### Health Check Pattern

All three functions follow identical pattern:

```python
def check_X_health(**kwargs) -> Dict[str, Any]:
    try:
        import X_core
        from gateway import singleton_get
        
        health = {
            'interface': 'X',
            'timestamp': time.time(),
            'checks': {},
            'compliance': {},
            'status': 'healthy'
        }
        
        # Check 1: SINGLETON registration
        manager = singleton_get('X_manager')
        health['checks']['singleton_registered'] = {...}
        
        # Check 2: Rate limiting
        core_instance = X_core.XCore()
        has_rate_limiter = hasattr(core_instance, '_rate_limiter')
        health['checks']['rate_limiting'] = {...}
        
        # Check 3: No threading locks
        source_file = X_core.__file__
        with open(source_file, 'r') as f:
            source_code = f.read()
        has_locks = check_for_locks(source_code)
        health['checks']['no_threading_locks'] = {...}
        
        # Check 4: Reset available
        has_reset = hasattr(X_core.XCore, 'reset')
        health['checks']['reset_available'] = {...}
        
        # Compliance summary
        health['compliance'] = compute_compliance(health['checks'])
        
        # Overall status
        health['status'] = determine_status(health['checks'], has_locks)
        
        return health
        
    except Exception as e:
        return error_dict(e)
```

---

## Architecture Integration

**SUGA Layer:** Core  
**Interface:** DIAGNOSIS (INT-13)  
**Gateway Access:** Via gateway wrappers

**Import Pattern:**
```python
# From gateway
from gateway import check_initialization_health, check_utility_health, check_singleton_health

# Direct (for testing)
from diagnosis_health_interface import check_initialization_health

health = check_initialization_health()
```

---

## Dependencies

**Internal:**
- gateway (singleton_get)
- initialization_core (InitializationCore)
- utility_core (SharedUtilityCore)
- singleton_core (SingletonCore)

**External:**
- time (timestamp generation)
- typing (Dict, Any)

---

## Related Files

**Core Files:**
- diagnosis_health_checks.py - Basic health checks
- diagnosis_health_system.py - System-wide health checks
- initialization_core.py - INITIALIZATION interface implementation
- utility_core.py - UTILITY interface implementation
- singleton_core.py - SINGLETON interface implementation

**Interface:**
- interface_diagnosis.py - DIAGNOSIS interface router

---

## Changelog

### 2025-12-08_1
- Initial version split from diagnosis_health.py
- 3 functions: check_initialization_health, check_utility_health, check_singleton_health
- Compliance checks: AP-08, DEC-04, LESS-17, LESS-18, LESS-21
- Source code scanning for threading locks
- Minimal docstrings per SIMA standards
