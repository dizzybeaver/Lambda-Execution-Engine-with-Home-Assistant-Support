# diagnosis_performance.py

**Version:** 2025-12-08_1  
**Module:** DIAGNOSIS Interface  
**Layer:** Core  
**Lines:** 310

---

## Purpose

Performance diagnostics for system and components. Analyzes system health, component performance, memory usage, and interface-specific performance patterns.

---

## Functions

### diagnose_system_health()

**Purpose:** Comprehensive system health diagnosis

**Signature:**
```python
def diagnose_system_health(**kwargs) -> Dict[str, Any]
```

**Returns:**
```python
{
    'success': bool,
    'component_health': Dict,    # From check_component_health()
    'gateway_health': Dict,      # From check_gateway_health()
    'memory': Dict               # From diagnose_memory_usage()
}
```

**Behavior:**
1. Lazy imports diagnosis_health to avoid circular dependencies
2. Calls check_component_health() for component status
3. Calls check_gateway_health() for gateway status
4. Calls diagnose_memory_usage() for memory metrics
5. Aggregates all results into single dict

**Dependencies:**
- diagnosis_health.check_component_health()
- diagnosis_health.check_gateway_health()
- diagnose_memory_usage() (local)

**Usage:**
```python
from diagnosis_performance import diagnose_system_health

health = diagnose_system_health()
print(f"System health: {health['success']}")
print(f"Components: {health['component_health']}")
print(f"Memory: {health['memory']['objects']} objects")
```

**Performance:** ~50-100ms (aggregates multiple checks)

---

### diagnose_component_performance()

**Purpose:** Performance diagnosis for gateway or specific component

**Signature:**
```python
def diagnose_component_performance(component: str = None, **kwargs) -> Dict[str, Any]
```

**Parameters:**
- `component` - Optional component name (default: 'gateway')

**Returns:**
```python
{
    'success': bool,
    'component': str,
    'gateway_operations': int,
    'fast_path_enabled': bool,
    'call_counts': Dict[str, int]
}
```

**Behavior:**
1. Calls gateway.get_gateway_stats()
2. Extracts operations_count
3. Checks fast_path_enabled flag
4. Returns call_counts per operation
5. On error, returns error dict

**Metrics Provided:**
- **gateway_operations:** Total operations executed
- **fast_path_enabled:** Whether ZAPH fast path is active
- **call_counts:** Dictionary of operation → count

**Error Scenarios:**
- ImportError → Returns `{'success': False, 'component': component, 'error': str(e)}`
- Exception → Same error structure

**Usage:**
```python
from diagnosis_performance import diagnose_component_performance

# Default (gateway)
perf = diagnose_component_performance()
print(f"Operations: {perf['gateway_operations']}")
print(f"Fast path: {perf['fast_path_enabled']}")

# Specific component
perf = diagnose_component_performance(component='cache')
```

**Performance:** <10ms (reads gateway stats)

---

### diagnose_memory_usage()

**Purpose:** Memory usage diagnosis using Python garbage collector

**Signature:**
```python
def diagnose_memory_usage(**kwargs) -> Dict[str, Any]
```

**Returns:**
```python
{
    'success': bool,
    'objects': int,           # Total objects tracked by GC
    'garbage': int,           # Objects in gc.garbage (uncollectable)
    'collections': tuple      # GC generation counts (gen0, gen1, gen2)
}
```

**Behavior:**
1. Gets GC stats via gc.get_stats() if available
2. Counts total objects via len(gc.get_objects())
3. Counts garbage objects via len(gc.garbage)
4. Gets collection counts via gc.get_count()
5. Returns memory metrics dict

**GC Metrics:**
- **objects:** Total Python objects being tracked
- **garbage:** Uncollectable objects (memory leaks)
- **collections:** Tuple of (gen0, gen1, gen2) collection counts

**Usage:**
```python
from diagnosis_performance import diagnose_memory_usage

memory = diagnose_memory_usage()
print(f"Objects: {memory['objects']:,}")
print(f"Garbage: {memory['garbage']}")
print(f"Collections: {memory['collections']}")

# Monitor for leaks
if memory['garbage'] > 0:
    print(f"WARNING: {memory['garbage']} uncollectable objects!")
```

**Performance:** ~5-20ms (depends on object count)

---

### diagnose_initialization_performance()

**Purpose:** Diagnose INITIALIZATION interface performance patterns

**Signature:**
```python
def diagnose_initialization_performance(**kwargs) -> Dict[str, Any]
```

**Returns:**
```python
{
    'interface': 'INITIALIZATION',
    'timestamp': float,
    'metrics': {
        'initialized': bool,
        'flag_count': int,
        'config_keys_count': int,
        'rate_limited_count': int,
        'init_duration_ms': float,
        'uptime_seconds': float
    },
    'patterns': {
        'initialized_at': str,
        'flag_types': Dict[str, str],
        'flag_count': int,
        'config_keys': List[str],
        'config_count': int
    },
    'recommendations': List[str]
}
```

**Behavior:**
1. Calls gateway.initialization_get_status()
2. Extracts basic metrics (initialized, flag_count, etc.)
3. Analyzes timing (init_duration_ms, uptime_seconds)
4. Analyzes flag patterns (types, count)
5. Analyzes config patterns (keys, count)
6. Generates recommendations based on thresholds

**Analysis Thresholds:**
- **Rate limiting:** > 0 blocked requests → Recommend optimization
- **Init duration:** > 100ms → Recommend review complexity
- **Flag count:** > 50 flags → Recommend consolidation

**Usage:**
```python
from diagnosis_performance import diagnose_initialization_performance

diag = diagnose_initialization_performance()
print(f"Initialized: {diag['metrics']['initialized']}")
print(f"Init duration: {diag['metrics']['init_duration_ms']:.2f}ms")
print(f"Flags: {diag['metrics']['flag_count']}")

if diag['recommendations']:
    print("Recommendations:")
    for rec in diag['recommendations']:
        print(f"  - {rec}")
```

**Performance:** ~10-30ms

---

### diagnose_utility_performance()

**Purpose:** Diagnose UTILITY interface performance patterns

**Signature:**
```python
def diagnose_utility_performance(**kwargs) -> Dict[str, Any]
```

**Returns:**
```python
{
    'interface': 'UTILITY',
    'timestamp': float,
    'metrics': {
        'id_pool_size': int,
        'json_cache_size': int,
        'cache_enabled': bool,
        'rate_limited_count': int
    },
    'patterns': {
        'slowest_operation': str,
        'fastest_operation': str,
        'total_operations': int
    },
    'recommendations': List[str]
}
```

**Behavior:**
1. Calls gateway.utility_get_performance_stats()
2. Extracts basic metrics
3. Analyzes operation patterns (slowest/fastest operations)
4. Checks cache near limit
5. Analyzes rate limiting
6. Checks ID pool size
7. Generates recommendations

**Analysis Thresholds:**
- **JSON cache:** > 80% of limit → Recommend cleanup
- **Rate limiting:** > 0 blocked → Notify
- **ID pool:** < 10 → Recommend replenishment

**Usage:**
```python
from diagnosis_performance import diagnose_utility_performance

diag = diagnose_utility_performance()
print(f"ID pool: {diag['metrics']['id_pool_size']}")
print(f"JSON cache: {diag['metrics']['json_cache_size']}")
print(f"Slowest op: {diag['patterns']['slowest_operation']}")
```

**Performance:** ~10-30ms

---

### diagnose_singleton_performance()

**Purpose:** Diagnose SINGLETON interface performance patterns

**Signature:**
```python
def diagnose_singleton_performance(**kwargs) -> Dict[str, Any]
```

**Returns:**
```python
{
    'interface': 'SINGLETON',
    'timestamp': float,
    'metrics': {
        'total_singletons': int,
        'rate_limited_count': int,
        'estimated_memory_mb': float,
        'singleton_types': Dict[str, int]
    },
    'patterns': {
        'total_accesses': int,
        'average_accesses': float,
        'max_accesses': int,
        'min_accesses': int,
        'most_accessed': str,
        'oldest_singleton': str,
        'newest_singleton': str,
        'average_age_seconds': float
    },
    'recommendations': List[str]
}
```

**Behavior:**
1. Calls gateway.singleton_get_stats()
2. Extracts basic metrics
3. Analyzes singleton types breakdown
4. Analyzes access patterns (total, avg, max, min)
5. Analyzes creation times (oldest, newest, avg age)
6. Checks rate limiting
7. Checks memory usage
8. Checks singleton count
9. Generates recommendations

**Analysis Thresholds:**
- **Rate limiting:** > 0 blocked → Recommend optimization
- **Memory:** > 10 MB → Recommend lifecycle review
- **Count:** > 50 singletons → Recommend consolidation

**Usage:**
```python
from diagnosis_performance import diagnose_singleton_performance

diag = diagnose_singleton_performance()
print(f"Total singletons: {diag['metrics']['total_singletons']}")
print(f"Memory: {diag['metrics']['estimated_memory_mb']:.2f} MB")
print(f"Most accessed: {diag['patterns']['most_accessed']}")
print(f"Total accesses: {diag['patterns']['total_accesses']}")
```

**Performance:** ~10-30ms

---

## Architecture Integration

**SUGA Layer:** Core  
**Interface:** DIAGNOSIS (INT-13)  
**Gateway Access:** Via gateway wrappers

**Import Pattern:**
```python
# From gateway
from gateway import diagnose_system_health, diagnose_component_performance

# Direct (for testing)
from diagnosis_performance import diagnose_system_health

health = diagnose_system_health()
```

---

## Dependencies

**Internal:**
- gateway (get_gateway_stats, initialization_get_status, utility_get_performance_stats, singleton_get_stats)
- diagnosis_health (check_component_health, check_gateway_health) - lazy import

**External:**
- gc (garbage collector metrics)
- time (timestamp generation)
- typing (Dict, Any)

---

## Related Files

**Core Files:**
- diagnosis_health_checks.py - Basic health checks
- diagnosis_health_interface.py - Interface health checks
- diagnosis_imports.py - Import testing

**Interface:**
- interface_diagnosis.py - DIAGNOSIS interface router

**Gateway:**
- gateway_wrappers_diagnosis.py - Gateway wrappers

---

## Changelog

### 2025-12-08_1
- Initial version migrated from debug_diagnostics.py
- 6 functions: diagnose_system_health, diagnose_component_performance, diagnose_memory_usage, diagnose_initialization_performance, diagnose_utility_performance, diagnose_singleton_performance
- Preserved exact analysis logic and thresholds
- Added lazy imports to avoid circular dependencies
- Minimal docstrings per SIMA standards
