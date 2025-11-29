# Custom-Instructions-Part2.md

**Version:** 5.0.0  
**Date:** 2025-11-29  
**Purpose:** LEE project development instructions (Part 2/4)  
**Project:** LEE (Lambda Execution Engine)

---

## LMMS PATTERN

**Lazy Module Management System**

**Purpose:** Minimize cold start time

**Pattern:**
```python
# Hot path (always used) - module level
import json
import boto3

# Cold path (rarely used) - function level
def debug_function():
    import debug_module  # Lazy load
    return debug_module.diagnose()
```

**LEE Usage:**
```
Hot path: Device queries, Alexa responses (90%)
Warm path: Device control, scenes (8%)
Cold path: Debug, config updates (2%)
```

**Impact:**
```
Cold start: 680ms (vs 2,300ms eager)
Warm start: 45ms
Memory: 85MB (vs 120MB eager)
```

---

## ZAPH PATTERN

**Zero-Abstraction Path for Hot Operations**

**Tiers:**
```
Tier 1 (Hot): fast_path.py
- Zero abstraction
- Direct implementation
- 90% of traffic
- <50ms target

Tier 2 (Warm): Gateway wrappers
- Light abstraction
- Via interfaces
- 8% of traffic
- <100ms target

Tier 3 (Cold): Full stack
- Gateway → Interface → Core
- 2% of traffic
- <500ms acceptable
```

---

## DICTIONARY DISPATCH

**Pattern:**
```python
# interface_cache.py
DISPATCH = {
    "get": get_impl,
    "set": set_impl,
    "delete": delete_impl,
    "clear": clear_impl,
}

def execute_cache_operation(operation, **kwargs):
    handler = DISPATCH.get(operation)
    if not handler:
        raise ValueError(f"Unknown operation: {operation}")
    return handler(**kwargs)
```

**Benefits:**
- O(1) lookup
- Easy to extend
- Clear interface
- Type-safe routing

---

## HOME ASSISTANT INTEGRATION

**WebSocket Connection:**
```python
# Primary: WebSocket for real-time
ws_connection = await connect_websocket()
result = await ws_connection.call_service(domain, service, data)

# Fallback: REST API if WebSocket unavailable
result = await rest_client.post(f"/api/services/{domain}/{service}", data)
```

**Device Discovery:**
```python
# Cache devices on cold start
devices = await discover_devices()
cache.set("devices", devices, ttl=300)

# Use cached devices for queries
devices = cache.get("devices")
```

**State Updates:**
```python
# Subscribe to state changes via WebSocket
await subscribe_events("state_changed", callback)

# Invalidate cache on change
def callback(event):
    entity_id = event["data"]["entity_id"]
    cache.delete(f"state:{entity_id}")
```

---

## AWS LAMBDA CONSTRAINTS

**Memory:**
```
Total: 128MB
Runtime overhead: ~40MB
Available: ~85MB
Must stay under: 80MB to be safe
```

**Timeout:**
```
Hard limit: 30 seconds
Target: <500ms (Tier 3)
Target: <100ms (Tier 2)
Target: <50ms (Tier 1)
```

**Threading:**
```
❌ No threading primitives
❌ No locks/semaphores
❌ No thread pools
✅ Single-threaded execution
✅ Async/await for I/O
```

**Cold Start:**
```
Target: <3 seconds
Current: ~680ms (LMMS)
Critical for Alexa (5s timeout)
```

---

## ERROR HANDLING

**Pattern:**
```python
# Specific exceptions only
try:
    result = operation()
except ValidationError as e:
    logger.error(f"Validation failed: {e}")
    return {"error": "invalid_input"}
except ConnectionError as e:
    logger.error(f"Connection failed: {e}")
    return {"error": "connection_failed"}
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    raise  # Re-raise unexpected errors
```

**Circuit Breaker:**
```python
# Protect external calls
@circuit_breaker(max_failures=3, timeout=60)
async def call_ha_api():
    return await ha_client.request()
```

**Retry Logic:**
```python
# Exponential backoff
@retry(max_attempts=3, backoff=2.0)
async def fetch_device_state():
    return await ha_client.get_state(entity_id)
```

---

## LOGGING

**Pattern:**
```python
# Structured logging
logger.info(
    "Device state query",
    extra={
        "entity_id": entity_id,
        "duration_ms": duration,
        "cache_hit": cache_hit,
    }
)
```

**Levels:**
```
DEBUG: Development only
INFO: Normal operations
WARNING: Recoverable issues
ERROR: Operation failures
CRITICAL: System failures
```

**CloudWatch:**
```python
# Metrics
metrics.put_metric(
    "CacheHitRate",
    value=hit_rate,
    unit="Percent"
)

# Logs
logger.info("Operation complete", extra=context)
```

---

## CONFIGURATION

**Parameter Store:**
```python
# Load from SSM
ha_url = ssm.get_parameter("/lee/ha/url")
ha_token = ssm.get_parameter("/lee/ha/token", decrypt=True)

# Cache configuration
config = cache.get("config")
if not config:
    config = load_config_from_ssm()
    cache.set("config", config, ttl=3600)
```

**Environment Variables:**
```python
# Runtime config
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
HA_TIMEOUT = int(os.getenv("HA_TIMEOUT", "10"))
CACHE_TTL = int(os.getenv("CACHE_TTL", "300"))
```

---

## TESTING

**Unit Tests:**
```python
# Test interface operations
def test_cache_get():
    cache.set("key", "value")
    assert cache.get("key") == "value"

# Test gateway routing
def test_gateway_cache_get():
    result = gateway.cache_get("key")
    assert result == expected_value
```

**Integration Tests:**
```python
# Test HA integration
async def test_ha_device_query():
    device = await gateway.ha_device_get("light.living_room")
    assert device["state"] == "on"
```

**Performance Tests:**
```python
# Test cold start
def test_cold_start_time():
    start = time.time()
    import lambda_function
    duration = time.time() - start
    assert duration < 3.0  # 3s target
```

---

## DEPLOYMENT

**Package Structure:**
```
lambda_deployment.zip
├── lambda_function.py (handler)
├── gateway.py
├── interface_*.py (12 files)
├── *_core.py (implementations)
└── requirements.txt (none - built-in only)
```

**Environment:**
```
Runtime: Python 3.12
Memory: 128MB
Timeout: 30s
Handler: lambda_function.handler
```

**Configuration:**
```
SSM Parameters:
- /lee/ha/url
- /lee/ha/token (encrypted)

Environment Variables:
- LOG_LEVEL=INFO
- HA_TIMEOUT=10
- CACHE_TTL=300
```

---

**END PART 2**

**Lines:** 349 (AT LIMIT)
