# Home Assistant Extension Performance Optimization Plan

**Version:** 2025.09.30.01  
**Target:** Memory reduction + Deployment size optimization  
**Status:** Proposed

---

## Executive Summary

**Current State:**
- 6 feature modules: 12-15MB runtime memory
- Total extension memory: 18-22MB with gateway
- All features load on initialization
- Duplicate code across modules
- Full entity objects in responses

**Optimization Targets:**
- **Runtime Memory:** 12-20MB reduction potential
- **Deployment Size:** 40-60% smaller packages
- **Cold Start:** 30-50% faster initialization
- **Response Times:** Maintain sub-200ms performance

---

## Immediate Optimizations (Quick Wins)

### 1. Lazy Feature Loading (10-12MB Savings)

**Current Problem:**
All 6 feature modules load on extension initialization regardless of actual usage.

**Solution:**
Dynamic imports only when features are actually invoked:

```python
# In homeassistant_extension.py
def trigger_ha_automation(automation_name, **kwargs):
    """Lazy-load automation module only when needed."""
    from home_assistant_automation import trigger_automation
    return trigger_automation(automation_name, **kwargs)

def execute_ha_script(script_name, **kwargs):
    """Lazy-load script module only when needed."""
    from home_assistant_scripts import execute_script
    return execute_script(script_name, **kwargs)
```

**Benefits:**
- Only pay memory cost for features actually used
- Typical invocation uses 1-2 features = 2-4MB vs 12-15MB
- No breaking changes to external interface
- Compatible with current gateway architecture

**Implementation Priority:** HIGH

---

### 2. Shared HA Common Module (1-2MB Savings)

**Current Problem:**
Duplicate code across 6 feature modules:
- HA API request patterns
- Entity ID parsing/validation
- Error response formatting
- Configuration retrieval
- Cache key generation

**Solution:**
Create `ha_common.py` with shared utilities:

```python
# ha_common.py
def call_ha_api(endpoint, method="GET", data=None, ha_config=None):
    """Unified HA API call with standard error handling."""
    # Single implementation used by all features
    
def parse_entity_id(entity_id):
    """Standard entity ID validation."""
    
def format_ha_error(operation, error):
    """Consistent error response formatting."""
    
def get_ha_config():
    """Centralized configuration retrieval with caching."""
```

**Benefits:**
- Eliminates 200-400 lines of duplicate code
- Single point of maintenance
- Consistent behavior across features
- 1-2MB memory reduction

**Implementation Priority:** HIGH

---

### 3. Cache Structure Consolidation (500KB-1MB Savings)

**Current Problem:**
7+ separate cache keys with individual lookups:
- `ha_automation_list`
- `ha_script_list`
- `ha_input_helper_list_{type}` (4 types)
- `ha_area_list`
- `ha_area_devices_{area}_{domain}`
- `ha_timer_list`
- `ha_media_players`

**Solution:**
Single structured cache with nested data:

```python
# Single cache key: "ha_entity_cache"
cache_structure = {
    "automations": [...],
    "scripts": [...],
    "input_helpers": {
        "boolean": [...],
        "text": [...],
        "number": [...],
        "select": [...]
    },
    "areas": [...],
    "area_devices": {...},
    "timers": [...],
    "media_players": [...],
    "timestamp": 1234567890,
    "ttl": 300
}
```

**Benefits:**
- Single cache lookup vs 7+ lookups
- Reduced serialization overhead
- Easier cache invalidation
- More efficient memory usage

**Implementation Priority:** MEDIUM

---

### 4. Entity Data Minimization (30-40% Response Size Reduction)

**Current Problem:**
Full entity objects returned with all attributes, context, metadata.

**Solution:**
Strip to essential fields only:

```python
# Current (full entity)
{
    "entity_id": "light.living_room",
    "state": "on",
    "attributes": {
        "friendly_name": "Living Room",
        "brightness": 255,
        "color_mode": "xy",
        "color_temp": 370,
        "hs_color": [28.8, 68.4],
        "rgb_color": [255, 176, 80],
        "xy_color": [0.532, 0.386],
        "supported_features": 63,
        "effect_list": ["colorloop"],
        # ... 15+ more attributes
    },
    "context": {...},
    "last_changed": "2025-09-30T10:15:30.123Z",
    "last_updated": "2025-09-30T10:15:30.123Z"
}

# Optimized (essential only)
{
    "entity_id": "light.living_room",
    "friendly_name": "Living Room",
    "state": "on"
}
```

**Benefits:**
- 70-80% smaller response payloads
- Faster JSON parsing
- Reduced network transfer
- Same functionality for voice control

**Implementation Priority:** MEDIUM

---

### 5. Inline Micro-Modules (200-500KB Savings)

**Current Problem:**
Small feature modules have import overhead disproportionate to their code size.

**Solution:**
If module < 150 lines, inline into `homeassistant_extension.py`:

**Candidates:**
- `home_assistant_timers.py` (~120 lines)
- Timer logic is simple and self-contained

**Benefits:**
- Eliminates import overhead
- One less module to lazy-load
- Cleaner dependency tree

**Implementation Priority:** LOW

---

## Revolutionary Approach: Feature-Selective Compilation

### Concept

**Current:** One-size-fits-all deployment with all 6 features

**Proposed:** Build-time feature selection

### Implementation

**Environment Variable Configuration:**
```bash
# Enable only needed features
HA_FEATURES=automation,scripts,areas

# Or enable all (default)
HA_FEATURES=all
```

**Build Script:**
```python
# build_ha_extension.py
enabled_features = os.getenv('HA_FEATURES', 'all').split(',')

if enabled_features != ['all']:
    # Include only specified feature modules
    # Exclude unused modules from deployment
    # Update router to handle only enabled features
    pass

# Pre-compile to bytecode
# Deploy .pyc files only (no .py sources)
```

**Benefits:**
- **Typical User (3 features):** 60% smaller deployment
- **Power User (all features):** 20% smaller (bytecode only)
- **Runtime Memory:** Only enabled features loaded
- **Cold Start:** 30-50% faster with fewer modules

**Example Configurations:**

| Profile | Features | Deployment Size | Runtime Memory |
|---------|----------|-----------------|----------------|
| Basic | automation, scripts | ~40KB | 4-6MB |
| Standard | +areas, notifications | ~65KB | 6-9MB |
| Advanced | +input_helpers, timers | ~95KB | 10-14MB |
| Full | all 6 features | ~120KB | 12-15MB |

**Implementation Priority:** MEDIUM (requires build tooling)

---

## Pre-compilation Strategy

### Current Deployment
```
deployment/
  ├── homeassistant_extension.py
  ├── home_assistant_automation.py
  ├── home_assistant_scripts.py
  └── ... (6 total .py files)
```

### Optimized Deployment
```
deployment/
  ├── homeassistant_extension.pyc
  ├── home_assistant_automation.pyc
  └── ... (only .pyc bytecode)
```

**Benefits:**
- 15-25% smaller package
- Slightly faster cold start (no parse step)
- Source protection bonus

**Implementation:**
```python
import py_compile
import os

for py_file in feature_modules:
    py_compile.compile(py_file, cfile=py_file + 'c', optimize=2)
    os.remove(py_file)  # Remove source
```

---

## Impact Analysis

### Memory Savings Summary

| Optimization | Memory Saved | Difficulty | Priority |
|--------------|--------------|------------|----------|
| Lazy Loading | 10-12MB | Low | HIGH |
| Shared Common | 1-2MB | Low | HIGH |
| Cache Consolidation | 500KB-1MB | Medium | MEDIUM |
| Entity Minimization | Minimal runtime | Low | MEDIUM |
| Inline Micro-Modules | 200-500KB | Low | LOW |
| Feature Selection | 8-15MB | Medium | MEDIUM |

**Total Potential:** 12-20MB reduction (50-65% memory savings)

### Deployment Size Savings

| Optimization | Size Reduction | Impact |
|--------------|----------------|--------|
| Pre-compilation | 15-25% | Cold start |
| Feature Selection | 40-80% | Deployment |
| Combined | 45-85% | Both |

---

## Implementation Roadmap

### Phase 1: Quick Wins (1-2 hours)
1. ✅ Create `ha_common.py` with shared utilities
2. ✅ Implement lazy loading in router functions
3. ✅ Update feature modules to use `ha_common`
4. ✅ Test memory usage and performance

**Expected Gains:** 11-14MB memory reduction

### Phase 2: Structural Optimization (2-3 hours)
1. ✅ Consolidate cache structure
2. ✅ Implement entity data minimization
3. ✅ Inline timer module if beneficial
4. ✅ Test cache performance

**Expected Gains:** Additional 1-2MB + faster responses

### Phase 3: Build Optimization (4-6 hours)
1. ✅ Create feature selection build script
2. ✅ Implement pre-compilation pipeline
3. ✅ Generate profile-specific packages
4. ✅ Update deployment documentation

**Expected Gains:** 40-60% smaller deployments

---

## Testing Requirements

### Memory Profiling
- Measure baseline per feature module
- Verify lazy loading memory savings
- Confirm cache consolidation efficiency
- Test feature-selective builds

### Performance Benchmarks
- Cold start times (all scenarios)
- Warm invocation response times
- Cache hit/miss ratios
- End-to-end latency

### Functional Testing
- All 6 features work with lazy loading
- Shared utilities maintain behavior
- Cache consolidation preserves TTLs
- Feature selection doesn't break dependencies

---

## Risk Assessment

### Low Risk
- Lazy loading (no external interface changes)
- Shared common module (internal refactor)
- Entity minimization (only impacts internal processing)

### Medium Risk
- Cache consolidation (migration path needed)
- Pre-compilation (reversible)

### Higher Risk
- Feature selection (requires careful dependency management)

### Mitigation
- Feature flags for gradual rollout
- Comprehensive test suite
- Rollback plan for each phase
- Memory monitoring in production

---

## Success Metrics

### Primary Goals
- ✅ Runtime memory < 10MB typical usage
- ✅ Cold start < 1.5 seconds
- ✅ Response times maintain sub-200ms
- ✅ Zero breaking changes to API

### Secondary Goals
- ✅ Deployment package < 60KB (typical)
- ✅ 50%+ reduction in duplicate code
- ✅ Feature-selective builds available

---

## Conclusion

The proposed optimizations deliver substantial improvements while maintaining full functionality and AWS Free Tier compliance. The phased approach enables incremental adoption with measurable results at each stage.

**Recommended:** Implement Phase 1 immediately, evaluate results, proceed to Phases 2-3 based on actual needs.

---

## Appendix: Current Architecture Compliance

All proposed changes maintain:
- ✅ Gateway architecture compliance (SUGA)
- ✅ Lazy loading compatibility (LIGS)
- ✅ Free Tier compliance (100%)
- ✅ Self-contained extension pattern
- ✅ Zero breaking changes to external interfaces

---

**Document Status:** Ready for Review  
**Next Action:** Approval for Phase 1 implementation
