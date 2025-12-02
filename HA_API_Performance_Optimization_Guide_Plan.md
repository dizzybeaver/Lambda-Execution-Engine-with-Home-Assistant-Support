# Home Assistant API Performance Optimization Guide

**Version:** 1.0.0  
**Date:** 2025-12-02  
**Project:** LEE (Lambda Execution Engine)  
**Purpose:** Comprehensive guide to improving HA API performance

---

## Executive Summary

Current performance: **1498ms (first request) → 300ms (warm requests)**  
Target performance: **<500ms (all requests)**  
Achievable with: **Cache warming + configuration tuning**

---

## Quick Wins (High Impact, Low Effort)

### 1. Enable Cache Warming ⭐ **Best ROI**

**Implementation:**
```bash
# Set Lambda environment variable:
HA_CACHE_WARMING_ENABLED=true
```

**What it does:**
- Pre-loads device states during cold start
- Eliminates first-request penalty
- Reduces HA API calls by 60-80%

**Expected improvement:** 1498ms → 300ms (80% reduction)

**Configuration in code:**
```python
# Already in ha_devices_helpers.py:
HA_CACHE_WARMING_ENABLED = os.getenv('HA_CACHE_WARMING_ENABLED', 'false').lower() == 'true'
```

---

### 2. Use WebSocket (Already Implemented) ✅

Your code already uses WebSocket which is faster than REST:

**Performance comparison:**
- WebSocket: ~100ms per call
- REST API: ~500ms per call

**Status:** Already implemented and working correctly.

---

### 3. Aggressive Response Caching

**Implementation:**
```python
# In ha_devices_helpers.py, modify cache TTLs:

# Current values:
HA_CACHE_TTL_STATE = 60        # 1 minute
HA_CACHE_TTL_ENTITIES = 300    # 5 minutes

# Recommended values:
HA_CACHE_TTL_STATE = 300       # 5 minutes (5x increase)
HA_CACHE_TTL_ENTITIES = 600    # 10 minutes (2x increase)
```

**Trade-off:** Slightly stale data vs faster responses

**Expected improvement:** 30-50% reduction in API calls

---

## Medium Impact Changes

### 4. Connection Keep-Alive

Maintain persistent WebSocket connection to avoid reconnection overhead.

**Implementation:**
```python
# Add to ha_config.py or Lambda environment variables:
HA_WEBSOCKET_KEEPALIVE = true
HA_WEBSOCKET_PING_INTERVAL = 30  # seconds
```

**Expected improvement:** Saves 100-200ms per request (reconnection overhead)

---

### 5. Batch Device Queries

Query multiple devices in single API call instead of individual calls.

**Before (inefficient):**
```python
device1 = get_device("light.living_room")   # API call 1: 150ms
device2 = get_device("light.bedroom")       # API call 2: 150ms
# Total: 300ms
```

**After (efficient):**
```python
devices = get_devices([
    "light.living_room",
    "light.bedroom"
])
# Total: 150ms (50% reduction)
```

**Implementation location:** `ha_devices_core.py` - `get_states_impl()` already supports this

---

### 6. Parallel Requests (Use Carefully)

For independent operations that don't depend on each other.

**Implementation:**
```python
import asyncio

# For multiple independent HA endpoints:
results = await asyncio.gather(
    call_ha_api("/api/states"),
    call_ha_api("/api/services"),
    call_ha_api("/api/config")
)
```

**⚠️ Warning:** Limit to 3-5 parallel requests to avoid overloading Home Assistant.

---

## Home Assistant Side Optimizations

### 7. Reduce HA Database Size

Smaller database = faster queries.

**Implementation:**
```yaml
# In Home Assistant configuration.yaml:
recorder:
  purge_keep_days: 7           # Reduce from default 10+
  commit_interval: 1
  db_url: sqlite:////config/home-assistant_v2.db
  
  # Exclude unnecessary domains:
  exclude:
    domains:
      - automation
      - script
    entities:
      - sensor.date_time
```

**Expected improvement:** 20-30% faster database queries

---

### 8. Disable Unused Integrations

Each integration adds overhead during API calls.

**How to audit:**
```bash
# List all integrations:
ha core config

# Check integrations in UI:
Settings → Devices & Services → Integrations
```

**Disable unused integrations:**
- Remove from UI
- Comment out in `configuration.yaml`

**Expected improvement:** 10-20% reduction in API response time

---

### 9. Upgrade HA Hardware/Resources

If running on constrained hardware:

**Current hardware assessment:**
- Raspberry Pi 3/4: Adequate for small setups
- Raspberry Pi Zero: Too slow
- Dedicated server: Best performance

**Recommended upgrades:**
- **RAM:** 4GB minimum (8GB optimal)
- **Storage:** SSD instead of SD card (3-5x faster)
- **CPU:** Pi 4 or x86 server (2-3x faster)

**Expected improvement:** 2-3x API response improvement

---

### 10. Network Optimization

Ensure LEE → HA connection is optimized.

**Best configuration:**
- ✅ **Local network** (not through cloud/VPN)
- ✅ **Wired Ethernet** (not WiFi if possible)
- ✅ **Low latency** (<10ms ping)

**Test connection:**
```bash
# From Lambda or same network:
ping your-ha-instance.local

# Expected:
# < 10ms: Excellent
# 10-50ms: Good
# > 50ms: Needs optimization
```

**Expected improvement:** 50-100ms reduction in API calls

---

## Advanced Optimizations

### 11. Predictive Pre-fetching

Pre-load commonly accessed devices during cache warming.

**Implementation:**
```python
# In ha_devices_cache.py - warm_cache_impl():

COMMON_DEVICES = [
    "light.living_room",
    "light.bedroom",
    "light.kitchen",
    "switch.fan",
    "climate.thermostat"
]

def warm_cache_impl(**kwargs):
    # Existing cache warming...
    
    # Add predictive pre-fetching:
    for device_id in COMMON_DEVICES:
        try:
            get_by_id_impl(device_id)  # Warms cache
        except Exception:
            pass  # Don't fail if device doesn't exist
```

**Expected improvement:** 90% cache hit rate on common devices

---

### 12. Fast Path for Common Operations

Skip validation for simple, safe operations.

**Implementation:**
```python
# In ha_devices_core.py:

FAST_OPERATIONS = {"turn_on", "turn_off", "toggle"}

def call_service_impl(domain, service, entity_id, service_data, **kwargs):
    if service in FAST_OPERATIONS and not service_data:
        # Use cached state, skip heavy validation
        return execute_fast_path(domain, service, entity_id)
    
    # Normal path for complex operations
    return execute_normal_path(domain, service, entity_id, service_data, **kwargs)
```

**Expected improvement:** 30-50ms faster for simple operations

---

### 13. HA API Rate Limit Tuning

Increase rate limits to allow more concurrent requests.

**Implementation:**
```python
# In ha_devices_helpers.py, modify:

# Current values:
HA_RATE_LIMIT_PER_SECOND = 10
HA_RATE_LIMIT_BURST = 20

# Recommended values:
HA_RATE_LIMIT_PER_SECOND = 20   # 2x increase
HA_RATE_LIMIT_BURST = 50        # 2.5x increase
```

**⚠️ Warning:** Monitor Home Assistant CPU/memory usage after increasing.

---

## Measurement & Monitoring

### 14. Add Performance Metrics

Track and monitor slow operations.

**Implementation:**
```python
# Already exists in ha_devices_helpers.py:

if duration_ms > HA_SLOW_OPERATION_THRESHOLD_MS:
    _SLOW_OPERATIONS[f'call_ha_api_{endpoint}'] += 1
    log_warning(f"Slow API call: {endpoint} took {duration_ms:.2f}ms")
    record_metric("SlowAPICall", 1.0)
```

**Create CloudWatch dashboard:**
- Average API response time
- P95/P99 latency
- Slow operation count
- Cache hit rate

---

### 15. A/B Testing Framework

Test changes systematically before deploying.

**Implementation:**
```python
# Use environment variables for gradual rollout:
USE_CACHE_WARMING = os.getenv("TEST_CACHE_WARMING", "false") == "true"
USE_PARALLEL_REQUESTS = os.getenv("TEST_PARALLEL", "false") == "true"

if USE_CACHE_WARMING:
    warm_cache_impl()
```

**Process:**
1. Enable feature for 10% of traffic
2. Monitor performance metrics
3. Gradually increase to 100% if successful

---

## Performance Impact Matrix

| Optimization | Impact | Effort | Expected Improvement | Complexity |
|--------------|--------|--------|---------------------|------------|
| Cache warming | ⭐⭐⭐⭐⭐ | Low | 1500ms → 300ms (80%) | Low |
| Increase cache TTL | ⭐⭐⭐ | Low | 300ms → 200ms (33%) | Low |
| WebSocket keepalive | ⭐⭐⭐ | Medium | 300ms → 250ms (17%) | Medium |
| Batch requests | ⭐⭐⭐ | Medium | 600ms → 300ms (50%) | Medium |
| HA hardware upgrade | ⭐⭐⭐⭐ | High | 300ms → 150ms (50%) | High |
| Network optimization | ⭐⭐⭐ | Medium | 300ms → 200ms (33%) | Medium |
| Predictive pre-fetch | ⭐⭐⭐⭐ | Medium | 80%+ cache hit rate | Medium |
| Fast path operations | ⭐⭐ | High | 50ms per operation | High |
| Parallel requests | ⭐⭐⭐ | Medium | 40-60% faster | Medium |

**Legend:**
- ⭐⭐⭐⭐⭐ = Critical impact
- ⭐⭐⭐⭐ = High impact
- ⭐⭐⭐ = Medium impact
- ⭐⭐ = Low impact

---

## Recommended Action Plan

### Week 1: Quick Wins (2-3 hours)

**Day 1:**
```bash
# 1. Enable cache warming
export HA_CACHE_WARMING_ENABLED=true

# 2. Measure baseline
# Record current P50/P95/P99 latency
```

**Day 2:**
```python
# 3. Increase cache TTLs in ha_devices_helpers.py
HA_CACHE_TTL_STATE = 300       # From 60
HA_CACHE_TTL_ENTITIES = 600    # From 300
```

**Day 3:**
```bash
# 4. Deploy and measure
# Compare before/after metrics
# Expected: 70-80% improvement
```

---

### Week 2: Medium Impact Changes (4-6 hours)

**Tasks:**
1. Implement WebSocket keepalive
2. Audit and batch common device queries
3. Test parallel requests (3-5 concurrent max)
4. Measure improvement

**Expected cumulative improvement:** 80-85% reduction in latency

---

### Week 3: Home Assistant Optimization (3-4 hours)

**Tasks:**
1. Audit HA integrations (disable unused)
2. Optimize HA database (purge old data)
3. Review network configuration
4. Test HA hardware performance

**Expected cumulative improvement:** 85-90% reduction in latency

---

### Month 2+: Advanced Optimizations (8-12 hours)

**Tasks:**
1. Consider HA hardware upgrade if still slow
2. Implement predictive pre-fetching
3. Add comprehensive performance monitoring
4. Build CloudWatch dashboards
5. Implement A/B testing framework

**Expected cumulative improvement:** 90-95% reduction in latency

---

## Success Metrics

### Target Performance

| Metric | Current | Target | Stretch Goal |
|--------|---------|--------|--------------|
| Cold start | 187ms | <200ms | <150ms |
| First HA call | 1498ms | <500ms | <300ms |
| Warm HA call | 300ms | <200ms | <100ms |
| Cache hit rate | ~40% | >80% | >90% |
| Memory usage | 57MB | <80MB | <60MB |

### Monitoring Dashboard

**Key metrics to track:**
1. Average API response time (per hour)
2. P95/P99 latency
3. Cache hit rate
4. Slow operation count (>1s)
5. Error rate
6. Lambda concurrent executions

**CloudWatch queries:**
```
fields @timestamp, @message
| filter @message like /Slow API call/
| stats count() by bin(5m)
```

---

## Troubleshooting

### Issue: Cache warming doesn't improve performance

**Diagnosis:**
```python
# Check if cache warming is actually running:
# Look for log: "Cache warming complete"
```

**Fix:** Verify `HA_CACHE_WARMING_ENABLED=true` in Lambda environment

---

### Issue: HA still slow after all optimizations

**Diagnosis:**
```bash
# Test HA directly (bypass LEE):
curl -X GET \
  -H "Authorization: Bearer YOUR_TOKEN" \
  http://your-ha-instance:8123/api/states
```

**If slow:** Problem is Home Assistant, not LEE
**If fast:** Problem is LEE → HA connection

---

### Issue: High cache miss rate

**Diagnosis:**
```python
# Add logging to track cache hits/misses:
log_info(f"Cache hit rate: {hits}/{total}")
```

**Fixes:**
1. Increase cache TTL
2. Pre-warm more devices
3. Review cache invalidation logic

---

## Conclusion

**Best ROI strategy:**
1. ✅ Enable cache warming (5 min work, 80% improvement)
2. ✅ Increase cache TTLs (5 min work, 15% improvement)
3. ✅ Measure and iterate

**Total time investment:** 10 minutes  
**Total expected improvement:** 1498ms → 300ms (80% reduction)

**For 95% improvement:** Follow full 4-week action plan

---

## References

- **LEE Documentation:** `/sima/projects/lee/`
- **Performance Metrics:** CloudWatch Logs Insights
- **Cache Implementation:** `ha_devices_cache.py`
- **HA API Calls:** `ha_devices_helpers.py`
- **Configuration:** `ha_config.py`

---

**Version:** 1.0.0  
**Last Updated:** 2025-12-02  
**Maintainer:** LEE Development Team
