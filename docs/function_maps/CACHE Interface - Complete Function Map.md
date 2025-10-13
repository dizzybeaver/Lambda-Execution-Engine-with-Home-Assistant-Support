# CACHE Interface - Complete Function Map
**Interface:** GatewayInterface.CACHE  
**Category:** Memory Management  
**Core File:** cache_core.py

---

## Call Hierarchy Map

```
gateway.execute_operation(GatewayInterface.CACHE, operation)
    ├─→ gateway.cache_get(key)                    [Gateway Convenience Function]
    ├─→ gateway.cache_set(key, value, ttl)        [Gateway Convenience Function]
    ├─→ gateway.cache_delete(key)                 [Gateway Convenience Function]
    └─→ gateway.cache_clear()                     [Gateway Convenience Function]
            ↓
    [Routes to cache_core Gateway Implementations]
            ↓
    ├─→ _execute_get_implementation(key, default)
    ├─→ _execute_set_implementation(key, value, ttl)
    ├─→ _execute_delete_implementation(key)
    └─→ _execute_clear_implementation()
            ↓
    [Delegates to Singleton Cache Instance]
            ↓
    _cache_instance (LUGSIntegratedCache)
            ↓
    ├─→ LUGSIntegratedCache.get(key)
    ├─→ LUGSIntegratedCache.set(key, value, ttl, source_module)
    ├─→ LUGSIntegratedCache.delete(key)
    ├─→ LUGSIntegratedCache.clear()
    ├─→ LUGSIntegratedCache.cleanup_expired()
    ├─→ LUGSIntegratedCache.get_stats()
    └─→ LUGSIntegratedCache.get_module_dependencies()
```

---

## File: gateway.py
**Functions:** 4 gateway convenience wrappers

### cache_get(key: str)
- **Category:** Gateway Function - Memory Management
- **Map:** `User → gateway.cache_get() → execute_operation(CACHE, 'get') → _execute_get_implementation() → _cache_instance.get()`
- **Description:** Get cached value by key
- **Returns:** Cached value or None

### cache_set(key: str, value: Any, ttl: Optional[int])
- **Category:** Gateway Function - Memory Management
- **Map:** `User → gateway.cache_set() → execute_operation(CACHE, 'set') → _execute_set_implementation() → _cache_instance.set()`
- **Description:** Store value in cache with optional TTL
- **Returns:** None

### cache_delete(key: str)
- **Category:** Gateway Function - Memory Management
- **Map:** `User → gateway.cache_delete() → execute_operation(CACHE, 'delete') → _execute_delete_implementation() → _cache_instance.delete()`
- **Description:** Remove cached entry by key
- **Returns:** bool (success/failure)

### cache_clear()
- **Category:** Gateway Function - Memory Management
- **Map:** `User → gateway.cache_clear() → execute_operation(CACHE, 'clear') → _execute_clear_implementation() → _cache_instance.clear()`
- **Description:** Clear all cached entries
- **Returns:** int (number of entries cleared)

---

## File: cache_core.py
**Primary Components:** Gateway implementations + Core cache class + Convenience functions

### Gateway Implementation Functions (4)

#### _execute_get_implementation(key: str, default: Any = None)
- **Category:** Gateway Implementation - Memory Management
- **Map:** `execute_operation() → _execute_get_implementation() → _cache_instance.get()`
- **Description:** Gateway implementation for cache retrieval with default fallback
- **Private:** Yes (called by gateway.py only)
- **Sub-functions:**
  - `_cache_instance.get(key)` - Retrieves value from LUGSIntegratedCache

#### _execute_set_implementation(key: str, value: Any, ttl: Optional[float])
- **Category:** Gateway Implementation - Memory Management
- **Map:** `execute_operation() → _execute_set_implementation() → _cache_instance.set()`
- **Description:** Gateway implementation for cache storage
- **Private:** Yes (called by gateway.py only)
- **Sub-functions:**
  - `_cache_instance.set(key, value, ttl or 300)` - Stores in cache with TTL

#### _execute_delete_implementation(key: str)
- **Category:** Gateway Implementation - Memory Management
- **Map:** `execute_operation() → _execute_delete_implementation() → _cache_instance.delete()`
- **Description:** Gateway implementation for cache deletion
- **Private:** Yes (called by gateway.py only)
- **Returns:** bool

#### _execute_clear_implementation()
- **Category:** Gateway Implementation - Memory Management
- **Map:** `execute_operation() → _execute_clear_implementation() → _cache_instance.clear()`
- **Description:** Gateway implementation for clearing all cache
- **Private:** Yes (called by gateway.py only)
- **Returns:** int (count cleared)

---

### Convenience Functions (7)

#### cache_set(key, value, ttl, source_module)
- **Category:** Convenience Function - Memory Management
- **Map:** `Direct call → _cache_instance.set()`
- **Description:** Direct cache set with LUGS module tracking
- **Public:** Yes

#### cache_get(key)
- **Category:** Convenience Function - Memory Management
- **Map:** `Direct call → _cache_instance.get()`
- **Description:** Direct cache retrieval
- **Public:** Yes

#### cache_delete(key)
- **Category:** Convenience Function - Memory Management
- **Map:** `Direct call → _cache_instance.delete()`
- **Description:** Direct cache deletion
- **Public:** Yes

#### cache_clear()
- **Category:** Convenience Function - Memory Management
- **Map:** `Direct call → _cache_instance.clear()`
- **Description:** Direct cache clear
- **Public:** Yes

#### cache_cleanup()
- **Category:** Convenience Function - Memory Management
- **Map:** `Direct call → _cache_instance.cleanup_expired()`
- **Description:** Remove expired entries
- **Public:** Yes

#### cache_get_stats()
- **Category:** Convenience Function - Observability
- **Map:** `Direct call → _cache_instance.get_stats()`
- **Description:** Get cache statistics
- **Public:** Yes

#### cache_operation_result(operation_name, func, ttl, cache_key_prefix, source_module)
- **Category:** Higher-Order Function - Performance Optimization
- **Map:** `Call → cache_get() → [cache miss] → func() → cache_set()`
- **Description:** Cache function result with LUGS tracking
- **Public:** Yes
- **Sub-functions:**
  - `cache_get(cache_key)` - Check cache first
  - `func()` - Execute function if cache miss
  - `cache_set(cache_key, result, ttl, source_module)` - Store result
  - `get_lugs_manager()` - Track cache hit in LUGS (optional)

---

### Core Class: LUGSIntegratedCache

#### Constructor: __init__()
- **Category:** Initialization - Memory Management
- **Description:** Initialize cache with lock, storage dict, and statistics
- **Initializes:**
  - `self._lock` - Thread lock for synchronization
  - `self._cache` - Dict[str, CacheEntry] main storage
  - `self._stats` - Statistics dict

---

#### set(key, value, ttl, source_module)
- **Category:** Core Operation - Memory Management
- **Map:** `set() → [lock] → create CacheEntry → store in _cache → add_cache_module_dependency()`
- **Description:** Store value in cache with LUGS module dependency tracking
- **Thread-Safe:** Yes (uses self._lock)
- **Sub-functions:**
  - `time.time()` - Get current timestamp
  - `CacheEntry()` - Create entry with metadata
  - `gateway.add_cache_module_dependency()` - Register LUGS dependency (optional)
- **Private Functions:**
  - Updates `self._stats['total_sets']`

#### get(key)
- **Category:** Core Operation - Memory Management
- **Map:** `get() → [lock] → check _cache → validate TTL → return value or None`
- **Description:** Retrieve cached value with TTL validation and access tracking
- **Thread-Safe:** Yes (uses self._lock)
- **Sub-functions:**
  - `time.time()` - Get current timestamp
  - TTL validation: `current_time - entry.timestamp > entry.ttl`
  - Updates entry: `access_count++`, `last_access`
- **Private Functions:**
  - Updates `self._stats['total_gets']`
  - Updates `self._stats['cache_hits']` or `self._stats['cache_misses']`
  - Updates `self._stats['entries_expired']` if expired

#### delete(key)
- **Category:** Core Operation - Memory Management
- **Map:** `delete() → [lock] → del _cache[key]`
- **Description:** Remove specific cache entry
- **Thread-Safe:** Yes (uses self._lock)
- **Returns:** bool (True if existed, False otherwise)

#### clear()
- **Category:** Core Operation - Memory Management
- **Map:** `clear() → [lock] → _cache.clear()`
- **Description:** Remove all cache entries
- **Thread-Safe:** Yes (uses self._lock)
- **Returns:** int (number of entries cleared)

#### cleanup_expired()
- **Category:** Maintenance - Memory Management
- **Map:** `cleanup_expired() → [lock] → iterate _cache → delete expired → update stats`
- **Description:** Remove all expired cache entries
- **Thread-Safe:** Yes (uses self._lock)
- **Sub-functions:**
  - `time.time()` - Get current timestamp
  - Iterate `self._cache.items()` to find expired
  - TTL check: `current_time - entry.timestamp > entry.ttl`
  - `del self._cache[key]` for each expired
- **Private Functions:**
  - Updates `self._stats['entries_expired']`
- **Returns:** int (count of expired entries removed)

#### get_stats()
- **Category:** Observability - Statistics
- **Map:** `get_stats() → [lock] → copy _stats → calculate rates → return`
- **Description:** Get comprehensive cache statistics
- **Thread-Safe:** Yes (uses self._lock)
- **Calculations:**
  - `cache_hit_rate = (cache_hits / total_gets) * 100`
  - `entries_count = len(self._cache)`
- **Returns:** Dict with stats including hit rate

#### get_module_dependencies()
- **Category:** LUGS Integration - Dependency Tracking
- **Map:** `get_module_dependencies() → [lock] → iterate _cache → group by source_module`
- **Description:** Get all cache entries grouped by source module for LUGS
- **Thread-Safe:** Yes (uses self._lock)
- **Returns:** Dict[str, Set[str]] mapping module names to cache keys

---

### Data Class: CacheEntry

#### Fields
- **value: Any** - Cached value
- **timestamp: float** - Creation time
- **ttl: float** - Time to live in seconds
- **source_module: Optional[str]** - Module that created entry (LUGS tracking)
- **access_count: int** - Number of times accessed (default: 0)
- **last_access: float** - Last access timestamp (default: 0.0)

---

## Module Variables

### _cache_instance
- **Type:** LUGSIntegratedCache
- **Category:** Singleton Instance
- **Description:** Global singleton cache instance
- **Initialization:** `_cache_instance = LUGSIntegratedCache()`

---

## Function Categories Summary

### Memory Management (Primary)
- All set/get/delete/clear operations
- Cache entry lifecycle management
- TTL-based expiration

### Performance Optimization
- `cache_operation_result()` - Higher-order caching
- Fast lookup with O(1) dict access
- Lazy cleanup of expired entries

### LUGS Integration
- `source_module` tracking in CacheEntry
- `get_module_dependencies()` for LUGS manager
- `add_cache_module_dependency()` integration

### Observability
- `get_stats()` - Cache performance metrics
- Access count tracking per entry
- Hit/miss rate calculation

### Thread Safety
- All core operations use `self._lock`
- Thread-safe dict operations
- Atomic stat updates

---

## Usage Examples

### Basic Cache Operations
```python
from gateway import cache_set, cache_get, cache_delete

# Set value with 5 minute TTL
cache_set('user:123', {'name': 'John'}, ttl=300)

# Get value
user = cache_get('user:123')

# Delete
cache_delete('user:123')
```

### Function Result Caching
```python
from cache_core import cache_operation_result

def expensive_operation():
    # Complex computation
    return result

# Cache result for 10 minutes
result = cache_operation_result(
    'my_operation',
    expensive_operation,
    ttl=600,
    source_module='my_module'
)
```

### Statistics
```python
from cache_core import cache_get_stats

stats = cache_get_stats()
# Returns: {
#   'total_sets': 100,
#   'total_gets': 500,
#   'cache_hits': 450,
#   'cache_misses': 50,
#   'cache_hit_rate': 90.0,
#   'entries_count': 75,
#   'entries_expired': 25
# }
```

---

**End of CACHE Interface Function Map**
