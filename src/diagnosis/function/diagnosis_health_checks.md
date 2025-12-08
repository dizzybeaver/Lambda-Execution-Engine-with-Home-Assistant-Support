# diagnosis_health_checks.py

**Version:** 2025-12-08_1  
**Module:** DIAGNOSIS Interface  
**Layer:** Core  
**Lines:** 68

---

## Purpose

Basic component and gateway health checks for the DIAGNOSIS interface. Provides foundational health validation and comprehensive health reporting.

---

## Functions

### check_component_health()

**Purpose:** Check health of all system components

**Signature:**
```python
def check_component_health(**kwargs) -> Dict[str, Any]
```

**Returns:**
```python
{
    'success': bool,
    'components': {
        'component_name': {
            'status': 'healthy' | 'degraded' | 'critical',
            'details': {...}
        }
    }
}
```

**Behavior:**
1. Calls gateway.check_all_components()
2. Returns aggregated component health status
3. Returns error dict if gateway unavailable

**Error Scenarios:**
- ImportError → Returns `{'success': False, 'error': 'Gateway not available'}`

**Usage:**
```python
from diagnosis_health_checks import check_component_health

health = check_component_health()
if health['success']:
    print(f"Components: {health['components']}")
```

---

### check_gateway_health()

**Purpose:** Check gateway operation health

**Signature:**
```python
def check_gateway_health(**kwargs) -> Dict[str, Any]
```

**Returns:**
```python
{
    'success': bool,
    'stats': Dict,           # Gateway statistics
    'healthy': bool          # True if operations_count > 0
}
```

**Behavior:**
1. Calls gateway.get_gateway_stats()
2. Extracts operations_count
3. Determines healthy status (operations > 0)
4. Returns stats dict with health status

**Health Criteria:**
- **Healthy:** operations_count > 0
- **Unhealthy:** operations_count == 0

**Error Scenarios:**
- ImportError → Returns `{'success': False, 'error': 'Gateway not available'}`

**Usage:**
```python
from diagnosis_health_checks import check_gateway_health

health = check_gateway_health()
if health['success'] and health['healthy']:
    print(f"Gateway healthy: {health['stats']['operations_count']} ops")
```

---

### generate_health_report()

**Purpose:** Generate comprehensive system health report

**Signature:**
```python
def generate_health_report(**kwargs) -> Dict[str, Any]
```

**Returns:**
```python
{
    'timestamp': str,                    # ISO timestamp
    'system_health': Dict,               # diagnose_system_health() result
    'validation': {
        'architecture': Dict,            # SUGA compliance
        'imports': Dict,                 # Import validation
        'gateway_routing': Dict,         # Routing validation
        'registry_operations': Dict      # Registry verification
    },
    'stats': Dict,                       # System statistics
    'optimization': Dict,                # Optimization stats
    'dispatcher_performance': Dict       # Dispatcher metrics
}
```

**Behavior:**
1. Calls diagnose_system_health() for system health
2. Validates system architecture (SUGA compliance)
3. Validates imports (no direct cross-imports)
4. Validates gateway routing (all routes functional)
5. Verifies registry operations (all ops callable)
6. Collects system statistics
7. Collects optimization statistics
8. Collects dispatcher performance metrics
9. Aggregates all results into comprehensive report

**Dependencies:**
- diagnosis_performance.diagnose_system_health()
- diagnosis_core.validate_system_architecture()
- diagnosis_core.validate_imports()
- diagnosis_core.validate_gateway_routing()
- debug_verification.verify_registry_operations()
- debug_stats.get_system_stats()
- debug_stats.get_optimization_stats()
- debug_stats.get_dispatcher_stats()

**Error Handling:**
- Dispatcher stats failures → Returns `{'error': 'dispatcher stats not available'}`
- Other failures → Exception propagates

**Usage:**
```python
from diagnosis_health_checks import generate_health_report

report = generate_health_report()
print(f"System health: {report['system_health']}")
print(f"Architecture compliant: {report['validation']['architecture']['compliant']}")
print(f"Dispatcher performance: {report['dispatcher_performance']}")
```

**Performance:** ~100-200ms (aggregates multiple checks)

---

## Architecture Integration

**SUGA Layer:** Core  
**Interface:** DIAGNOSIS (INT-13)  
**Gateway Access:** Via `diagnosis_health_checks` functions

**Import Pattern:**
```python
# From gateway wrappers
from diagnosis_health_checks import check_component_health, check_gateway_health, generate_health_report

# Usage
health = check_component_health()
gateway_health = check_gateway_health()
full_report = generate_health_report()
```

---

## Dependencies

**Internal:**
- gateway (check_all_components, get_gateway_stats)
- diagnosis_performance (diagnose_system_health)
- diagnosis_core (validate_system_architecture, validate_imports, validate_gateway_routing)
- debug_verification (verify_registry_operations)
- debug_stats (get_system_stats, get_optimization_stats, get_dispatcher_stats)

**External:**
- typing (Dict, Any)

---

## Related Files

**Core Files:**
- diagnosis_health_interface.py - Interface-specific health checks
- diagnosis_health_system.py - System-wide health checks
- diagnosis_performance.py - Performance diagnostics
- diagnosis_core.py - Core validation logic

**Interface:**
- interface_diagnosis.py - DIAGNOSIS interface router

**Gateway:**
- gateway_wrappers_diagnosis.py - Gateway wrapper functions

---

## Changelog

### 2025-12-08_1
- Initial version split from diagnosis_health.py
- 3 functions: check_component_health, check_gateway_health, generate_health_report
- Minimal docstrings per SIMA standards
- Removed verbose comments
