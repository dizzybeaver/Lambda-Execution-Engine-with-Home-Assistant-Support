# Custom-Instructions-Part3.md

**Version:** 5.0.0  
**Date:** 2025-11-29  
**Purpose:** LEE project development instructions (Part 3/4)  
**Project:** LEE (Lambda Execution Engine)

---

## INTERFACE CATALOG

**LEE has 12 interfaces organized in 5 layers:**

### L0 - Foundational (3)

**Singleton (INT-00):**
```python
gateway.singleton_register(key, factory)
gateway.singleton_get(key)
```
Purpose: Single instances, memory management

**Utility (INT-01):**
```python
gateway.util_function()
```
Purpose: Helper functions, common utilities

**Config (INT-02):**
```python
gateway.config_get(key)
gateway.config_set(key, value)
```
Purpose: Configuration access, SSM integration

### L1 - Infrastructure (3)

**Logging (INT-03):**
```python
gateway.log_info(message, **context)
gateway.log_error(message, **context)
```
Purpose: Structured logging, CloudWatch

**Metrics (INT-04):**
```python
gateway.metrics_put(name, value, unit)
```
Purpose: CloudWatch metrics

**Security (INT-05):**
```python
gateway.security_validate(data)
gateway.security_encrypt(data)
```
Purpose: Validation, encryption

### L2 - Communication (2)

**HTTP (INT-06):**
```python
gateway.http_get(url, **kwargs)
gateway.http_post(url, data, **kwargs)
```
Purpose: REST client for HA

**WebSocket (INT-07):**
```python
gateway.ws_connect()
gateway.ws_call_service(domain, service, data)
```
Purpose: Real-time HA communication

### L3 - Operational (3)

**Cache (INT-08):**
```python
gateway.cache_get(key)
gateway.cache_set(key, value, ttl)
```
Purpose: Performance optimization

**Circuit Breaker (INT-09):**
```python
gateway.circuit_breaker_call(func, *args)
```
Purpose: Resilience, failure protection

**Debug (INT-10):**
```python
gateway.debug_diagnostics()
```
Purpose: Troubleshooting, diagnostics

### L4 - Initialization (1)

**Init (INT-11):**
```python
gateway.init_preload()
```
Purpose: Cold start optimization

---

## COMMON WORKFLOWS

### Add New Gateway Function

**Step 1: Add to appropriate interface**
```python
# interface_cache.py
def warm_cache_impl(**kwargs):
    """Warm cache with common data."""
    # Implementation
    pass

DISPATCH["warm"] = warm_cache_impl
```

**Step 2: Add gateway wrapper**
```python
# gateway.py
def cache_warm(**kwargs):
    """Warm cache with common data."""
    import interface_cache
    return interface_cache.execute_cache_operation("warm", **kwargs)
```

**Step 3: Export from gateway**
```python
# gateway.py
__all__ = [
    # ... existing exports
    "cache_warm",
]
```

**Step 4: Document in NMP**
```markdown
### cache_warm()

**Purpose:** Pre-load cache with common data
**Layer:** Interface
**Usage:** `gateway.cache_warm()`
```

### Add New Device Handler

**Step 1: Add to ha_devices_core.py**
```python
async def handle_new_device_type(device_id, **kwargs):
    """Handle new device type."""
    # Implementation
    return result
```

**Step 2: Register in dispatcher**
```python
DEVICE_HANDLERS = {
    "light": handle_light,
    "switch": handle_switch,
    "new_type": handle_new_device_type,  # Add here
}
```

**Step 3: Test integration**
```python
# Test discovery
devices = await gateway.ha_discover_devices()
assert any(d["type"] == "new_type" for d in devices)

# Test control
result = await gateway.ha_device_control(device_id, action="on")
assert result["success"]
```

### Debug Connection Issue

**Step 1: Check logs**
```python
# CloudWatch Logs Insights query
fields @timestamp, @message, entity_id, error
| filter @message like /WebSocket/
| sort @timestamp desc
| limit 100
```

**Step 2: Verify configuration**
```python
# Check SSM parameters
ha_url = gateway.config_get("/lee/ha/url")
ha_token = gateway.config_get("/lee/ha/token")

logger.info("Config check", extra={
    "ha_url": ha_url,
    "token_length": len(ha_token) if ha_token else 0
})
```

**Step 3: Test connection**
```python
# Manual connection test
try:
    result = await gateway.ws_connect()
    logger.info("Connection successful", extra={"result": result})
except Exception as e:
    logger.error("Connection failed", extra={"error": str(e)})
```

**Step 4: Check circuit breaker**
```python
# Circuit breaker state
state = gateway.circuit_breaker_state("ha_api")
logger.info("Circuit breaker state", extra={"state": state})

# Reset if needed
if state == "open":
    gateway.circuit_breaker_reset("ha_api")
```

---

## PERFORMANCE OPTIMIZATION

### Identify Hot Path

**Step 1: Enable metrics**
```python
# Add timing to operations
import time

start = time.time()
result = operation()
duration = (time.time() - start) * 1000

gateway.metrics_put("OperationDuration", duration, "Milliseconds")
```

**Step 2: Analyze metrics**
```python
# CloudWatch query
SELECT AVG(OperationDuration), MAX(OperationDuration), COUNT(*)
FROM SCHEMA("AWS/Lambda", FunctionName)
WHERE FunctionName = 'lee-function'
GROUP BY operation
ORDER BY AVG(OperationDuration) DESC
```

**Step 3: Optimize hot path**
```python
# Move to fast_path.py if called frequently
# Use direct implementation, skip abstraction
def hot_operation():
    # Direct implementation
    return result
```

### Reduce Cold Start

**Step 1: Profile imports**
```python
# Add to lambda_function.py
import time

start = time.time()
import module_name
duration = (time.time() - start) * 1000
print(f"Import {module_name}: {duration}ms")
```

**Step 2: Lazy load cold path**
```python
# Move to function level
def rarely_used_operation():
    import expensive_module  # Lazy load
    return expensive_module.process()
```

**Step 3: Preload essentials**
```python
# In init interface
def preload_impl():
    """Preload essential data."""
    gateway.cache_set("devices", discover_devices())
    gateway.cache_set("config", load_config())
```

---

## ALEXA INTEGRATION

### Smart Home Skill

**Discovery:**
```python
def handle_discovery():
    """Discover HA devices for Alexa."""
    devices = gateway.ha_discover_devices()
    
    return {
        "event": {
            "header": {
                "namespace": "Alexa.Discovery",
                "name": "Discover.Response",
            },
            "payload": {
                "endpoints": [
                    format_device_for_alexa(d) 
                    for d in devices
                ]
            }
        }
    }
```

**State Report:**
```python
def handle_state_report(entity_id):
    """Report device state to Alexa."""
    state = gateway.ha_get_state(entity_id)
    
    return {
        "context": {
            "properties": [
                format_state_for_alexa(state)
            ]
        }
    }
```

**Control:**
```python
def handle_control(entity_id, action, value=None):
    """Control device via Alexa."""
    result = gateway.ha_device_control(
        entity_id,
        action=action,
        value=value
    )
    
    if result["success"]:
        return success_response()
    else:
        return error_response(result["error"])
```

---

## KNOWLEDGE REFERENCES

**Search project knowledge for:**

```
Architecture:
- "SUGA architecture pattern"
- "LMMS lazy loading"
- "ZAPH hot path optimization"

Interfaces:
- "interface catalog LEE"
- "gateway functions reference"
- "cache interface patterns"

Integration:
- "Home Assistant WebSocket"
- "Alexa Smart Home integration"
- "device discovery patterns"

Troubleshooting:
- "LEE debugging guide"
- "connection issues"
- "performance optimization"

Examples:
- "NMP LEE examples"
- "implementation patterns"
- "code templates"
```

---

**END PART 3**

**Lines:** 349 (AT LIMIT)
