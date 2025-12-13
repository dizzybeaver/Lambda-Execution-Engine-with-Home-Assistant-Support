# utility_cross_interface.md

**Version:** 2025-12-13_1  
**Purpose:** Function documentation for utility_cross_interface.py  
**Module:** Utility cross-interface utilities

---

## Overview

Shared utilities that integrate with other interfaces via gateway. Eliminates duplicate patterns across interfaces for caching, metrics, error handling, and operation tracking.

**File:** `utility/utility_cross_interface.py`  
**Lines:** ~350  
**Pattern:** Cross-interface utility functions

---

## Functions

### Operation Management

#### cache_operation_result()

**Purpose:** Generic caching wrapper for any interface operation  
**Returns:** Any (operation result)

**Parameters:**
- `operation_name` (str): Operation identifier
- `func` (Callable): Function to execute
- `ttl` (int, default=300): Cache TTL in seconds
- `cache_key_prefix` (str, optional): Custom cache key prefix
- `**kwargs`: Arguments for func

**Usage:**
```python
from utility_cross_interface import cache_operation_result

# Cache expensive operation
def expensive_query(user_id):
    # Complex database query
    return query_result

result = cache_operation_result(
    'user_query',
    expensive_query,
    ttl=600,
    user_id='123'
)
```

**Features:**
- Automatic cache key generation from kwargs
- Cache miss fallback
- Error tolerance (executes without cache on failure)
- Gateway CACHE interface integration

---

#### record_operation_metrics()

**Purpose:** Generic metrics recording for any interface operation  
**Returns:** None

**Parameters:**
- `interface` (str): Interface name
- `operation` (str): Operation name
- `duration` (float): Operation duration in milliseconds
- `success` (bool, default=True): Operation success
- `correlation_id` (str, optional): Correlation ID

**Usage:**
```python
from utility_cross_interface import record_operation_metrics
import time

start = time.time()
result = perform_operation()
duration = (time.time() - start) * 1000

record_operation_metrics(
    'cache',
    'get',
    duration,
    success=True,
    correlation_id='req-123'
)
```

**Metrics Recorded:**
- `{interface}_{operation}_duration` - Duration metric
- `{interface}_{operation}_error` - Error count (if failed)

**Tags:**
- interface
- operation
- success
- correlation_id (if provided)

---

#### handle_operation_error()

**Purpose:** Unified error handling with logging and metrics  
**Returns:** dict (error response)

**Parameters:**
- `interface` (str): Interface name
- `operation` (str): Operation name
- `error` (Exception): Exception that occurred
- `correlation_id` (str, optional): Correlation ID

**Usage:**
```python
from utility_cross_interface import handle_operation_error

try:
    result = risky_operation()
except Exception as e:
    return handle_operation_error('cache', 'get', e, correlation_id='req-123')
```

**Returns:**
```python
{
    'success': False,
    'error': 'Connection timeout',
    'error_type': 'TimeoutError',
    'interface': 'cache',
    'operation': 'get',
    'correlation_id': 'req-123',
    'timestamp': 1702480800
}
```

**Features:**
- Auto-generates correlation ID if missing
- Logs error via gateway LOGGING
- Records error metric
- Sanitizes error response via gateway SECURITY

---

### Context Management

#### create_operation_context()

**Purpose:** Create operation context with correlation tracking  
**Returns:** dict (operation context)

**Parameters:**
- `interface` (str): Interface name
- `operation` (str): Operation name
- `**kwargs`: Operation parameters

**Usage:**
```python
from utility_cross_interface import create_operation_context

context = create_operation_context(
    'cache',
    'get',
    key='user_123',
    default=None
)
# Result: {
#     'interface': 'cache',
#     'operation': 'get',
#     'correlation_id': '550e8400-e29b-41d4-a716-446655440000',
#     'start_time': 1702480800.123,
#     'parameters': {'key': 'user_123', 'default': None}
# }
```

**Features:**
- Auto-generates correlation ID
- Records start time
- Captures parameters
- Records operation start metric

---

#### close_operation_context()

**Purpose:** Close operation context and record final metrics  
**Returns:** dict (completion result)

**Parameters:**
- `context` (dict): Context from create_operation_context()
- `success` (bool, default=True): Operation success
- `result` (Any, optional): Operation result

**Usage:**
```python
from utility_cross_interface import create_operation_context, close_operation_context

# Start operation
context = create_operation_context('cache', 'get', key='user_123')

try:
    result = cache.get('user_123')
    return close_operation_context(context, success=True, result=result)
except Exception as e:
    return close_operation_context(context, success=False)
```

**Returns:**
```python
{
    'success': True,
    'duration': 12.34,  # milliseconds
    'correlation_id': '550e8400-...',
    'result': {'data': '...'}
}
```

**Features:**
- Calculates duration
- Records final metrics
- Logs completion

---

### Batch Operations

#### batch_cache_operations()

**Purpose:** Batch cache multiple operations for efficiency  
**Returns:** list[Any] (operation results)

**Parameters:**
- `operations` (list[dict]): List of operation definitions
- `ttl` (int, default=300): Cache TTL

**Operation Definition:**
```python
{
    'cache_key': 'unique_key',  # Optional
    'func': callable,           # Required
    'kwargs': {...}             # Optional
}
```

**Usage:**
```python
from utility_cross_interface import batch_cache_operations

operations = [
    {
        'cache_key': 'user_123',
        'func': get_user,
        'kwargs': {'user_id': '123'}
    },
    {
        'cache_key': 'user_456',
        'func': get_user,
        'kwargs': {'user_id': '456'}
    }
]

results = batch_cache_operations(operations, ttl=600)
# Result: [user_123_data, user_456_data]
```

**Features:**
- Checks cache before execution
- Caches results after execution
- Error tolerance per operation
- Efficient for bulk operations

---

#### parallel_operation_execution()

**Purpose:** Execute multiple operations in parallel with timeout protection  
**Returns:** dict (execution results)

**Parameters:**
- `operations` (list[Callable]): List of operations to execute
- `max_workers` (int, default=5): Maximum parallel workers
- `timeout` (float, default=30.0): Total timeout in seconds

**Usage:**
```python
from utility_cross_interface import parallel_operation_execution

operations = [
    lambda: expensive_query_1(),
    lambda: expensive_query_2(),
    lambda: expensive_query_3()
]

result = parallel_operation_execution(operations, max_workers=3, timeout=10.0)
# Result: {
#     'results': [result1, result2, result3],
#     'total_count': 3,
#     'success_count': 3,
#     'error_count': 0,
#     'all_succeeded': True
# }
```

**Features:**
- Validates max_workers against CPU count
- Timeout protection
- Error tracking per operation
- Success/failure counts

**IMPORTANT:** Uses ThreadPoolExecutor (only safe in specific contexts)

---

### Interface Utilities

#### aggregate_interface_metrics()

**Purpose:** Aggregate metrics for an interface over time range  
**Returns:** dict (aggregated metrics)

**Parameters:**
- `interface` (str): Interface name
- `time_range_minutes` (int, default=60): Time range

**Usage:**
```python
from utility_cross_interface import aggregate_interface_metrics

metrics = aggregate_interface_metrics('cache', time_range_minutes=30)
# Result: {
#     'cache_get_count': 1500,
#     'cache_get_avg_duration': 2.5,
#     'cache_set_count': 300,
#     ...
# }
```

---

#### optimize_interface_memory()

**Purpose:** Optimize memory usage for an interface  
**Returns:** dict (optimization result)

**Parameters:**
- `interface` (str): Interface name

**Usage:**
```python
from utility_cross_interface import optimize_interface_memory

result = optimize_interface_memory('cache')
# Result: {
#     'interface': 'cache',
#     'optimizations': ['cache_cleared'],
#     'timestamp': 1702480800
# }
```

**Optimizations:**
- Clears cache via gateway CACHE.clear()
- Reports timestamp

---

#### validate_aws_free_tier_compliance()

**Purpose:** Validate AWS free tier compliance for an interface  
**Returns:** dict (compliance status)

**Parameters:**
- `interface` (str): Interface name

**Usage:**
```python
from utility_cross_interface import validate_aws_free_tier_compliance

compliance = validate_aws_free_tier_compliance('cache')
# Result: {
#     'interface': 'cache',
#     'invocations': 50000,
#     'free_tier_limit': 1000000,
#     'compliant': True,
#     'utilization_percentage': 5.0,
#     'headroom': 950000
# }
```

**Free Tier Limit:** 1,000,000 invocations/month

---

## Usage Patterns

### Operation Tracking Pattern
```python
from utility_cross_interface import create_operation_context, close_operation_context

# Start operation
context = create_operation_context('my_interface', 'my_operation', param1='value1')

try:
    # Perform operation
    result = perform_operation(context['parameters']['param1'])
    
    # Close successfully
    return close_operation_context(context, success=True, result=result)
except Exception as e:
    # Close with error
    return close_operation_context(context, success=False)
```

### Cached Operation Pattern
```python
from utility_cross_interface import cache_operation_result

def expensive_operation(param1, param2):
    # Expensive computation
    return result

# Cached execution
result = cache_operation_result(
    'expensive_op',
    expensive_operation,
    ttl=600,
    cache_key_prefix='exp_op',
    param1='value1',
    param2='value2'
)
```

### Error Handling Pattern
```python
from utility_cross_interface import handle_operation_error

try:
    result = risky_operation()
except Exception as e:
    error_response = handle_operation_error(
        'my_interface',
        'my_operation',
        e,
        correlation_id=correlation_id
    )
    return error_response
```

---

## Gateway Dependencies

**Required Gateway Interfaces:**
- CACHE - For caching operations
- LOGGING - For logging
- METRICS - For metrics recording
- SECURITY - For sanitization
- SINGLETON - For timeout execution
- CONFIG - For configuration retrieval

**Import Protection:**
- All functions have try/except around gateway imports
- Graceful degradation if gateway unavailable
- Logs warnings on import failure

---

## Threading Warning

⚠️ **CRITICAL:** `parallel_operation_execution()` uses `ThreadPoolExecutor`

**Safe Use:**
- Only in specific contexts where threading is allowed
- NOT safe in Lambda (single-threaded model)
- Validates max_workers against CPU count

**Alternative:** Use sequential execution or async patterns for Lambda

---

## Related Files

- **Gateway:** All gateway interfaces (CACHE, LOGGING, METRICS, etc.)
- **Core:** `utility/utility_core.py`
- **Manager:** `utility/utility_manager.py`

---

**END OF DOCUMENTATION**
