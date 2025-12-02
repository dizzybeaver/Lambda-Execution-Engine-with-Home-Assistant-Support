# LEE Environment Variables Reference

**Version:** 1.0.0  
**Date:** 2025-12-02  
**Project:** LEE (Lambda Execution Engine)  
**Purpose:** Complete reference for all environment variables

---

## Overview

LEE uses environment variables for non-sensitive configuration. Sensitive data (HA token) stored in SSM Parameter Store.

**Configuration Priority:**
1. SSM Parameter Store (token only)
2. Environment variables
3. Code defaults

---

## Home Assistant Configuration

### HOME_ASSISTANT_ENABLED

**Purpose:** Enable/disable Home Assistant integration  
**Type:** Boolean (string)  
**Default:** `true`  
**Valid Values:** `true`, `false`, `1`, `0`, `yes`, `no`

```bash
HOME_ASSISTANT_ENABLED=true   # Enable HA integration
HOME_ASSISTANT_ENABLED=false  # Disable HA (failsafe only)
```

**Impact:** When `false`, HA extensions don't load (LEE runs in failsafe mode)

---

### HOME_ASSISTANT_URL

**Purpose:** Home Assistant base URL  
**Type:** String (URL)  
**Default:** None (required)  
**Format:** `http://host:port` or `https://host:port`

```bash
HOME_ASSISTANT_URL=http://homeassistant.local:8123
HOME_ASSISTANT_URL=https://ha.example.com:8123
```

**Notes:**
- Include protocol (http/https)
- Include port
- No trailing slash

---

### HOME_ASSISTANT_TOKEN

**Purpose:** HA long-lived access token (fallback)  
**Type:** String (secret)  
**Default:** None  
**Priority:** 2nd (after SSM)

```bash
HOME_ASSISTANT_TOKEN=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Security:**
- Use SSM Parameter Store instead (USE_PARAMETER_STORE=true)
- This is fallback only if SSM unavailable
- Token visible in Lambda console if used

**See Also:** LONG_LIVED_ACCESS_TOKEN (legacy name)

---

### LONG_LIVED_ACCESS_TOKEN

**Purpose:** HA token (legacy name)  
**Type:** String (secret)  
**Default:** None  
**Status:** Deprecated, use HOME_ASSISTANT_TOKEN

```bash
LONG_LIVED_ACCESS_TOKEN=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Migration:** Rename to HOME_ASSISTANT_TOKEN

---

### HOME_ASSISTANT_TIMEOUT

**Purpose:** API call timeout in seconds  
**Type:** Integer  
**Default:** `30`  
**Range:** 1-30

```bash
HOME_ASSISTANT_TIMEOUT=30   # Default
HOME_ASSISTANT_TIMEOUT=10   # Faster timeout
```

**Notes:**
- Lambda has 30s hard limit
- Lower values fail faster
- Higher values allow slow HA responses

---

### HOME_ASSISTANT_VERIFY_SSL

**Purpose:** Verify SSL certificates for HTTPS  
**Type:** Boolean (string)  
**Default:** `true`  
**Valid Values:** `true`, `false`, `1`, `0`, `yes`, `no`

```bash
HOME_ASSISTANT_VERIFY_SSL=true   # Verify certificates (recommended)
HOME_ASSISTANT_VERIFY_SSL=false  # Skip verification (self-signed certs)
```

**Security:** Only set to `false` for self-signed certificates in local network

---

### HA_ASSISTANT_NAME

**Purpose:** Assistant name for HA conversation integration  
**Type:** String  
**Default:** `Alexa`

```bash
HA_ASSISTANT_NAME=Alexa    # Default
HA_ASSISTANT_NAME=Claude   # Custom name
```

---

## Cache & Performance

### HA_CACHE_WARMING_ENABLED

**Purpose:** Pre-warm cache on cold start  
**Type:** Boolean (string)  
**Default:** `false`  
**Valid Values:** `true`, `false`

```bash
HA_CACHE_WARMING_ENABLED=false  # Default (disabled)
HA_CACHE_WARMING_ENABLED=true   # Enable cache warming
```

**Impact:**
- When `true`: Pre-loads HA config and states during cold start
- Reduces first request from 1498ms to 300ms (80% improvement)
- Adds 100-200ms to cold start time
- **Recommended:** Enable for production

**See:** Performance Optimization Guide for details

---

### HA_RATE_LIMIT_ENABLED

**Purpose:** Enable rate limiting for HA API calls  
**Type:** Boolean (string)  
**Default:** `true`  
**Valid Values:** `true`, `false`

```bash
HA_RATE_LIMIT_ENABLED=true   # Default (enabled)
HA_RATE_LIMIT_ENABLED=false  # Disable rate limiting
```

**Impact:** Protects Home Assistant from overload

---

### HA_RATE_LIMIT_PER_SECOND

**Purpose:** Maximum HA API calls per second  
**Type:** Integer  
**Default:** `10`  
**Range:** 1-100

```bash
HA_RATE_LIMIT_PER_SECOND=10   # Default
HA_RATE_LIMIT_PER_SECOND=20   # Allow more concurrent calls
```

**Notes:**
- Higher values = more HA load
- Monitor HA CPU/memory when increasing
- Token bucket algorithm

---

### HA_RATE_LIMIT_BURST

**Purpose:** Maximum burst size for HA API calls  
**Type:** Integer  
**Default:** `20`  
**Range:** 1-200

```bash
HA_RATE_LIMIT_BURST=20   # Default
HA_RATE_LIMIT_BURST=50   # Allow larger bursts
```

**Notes:**
- Allows temporary spikes above per-second limit
- Useful for bulk operations

---

## SSM Parameter Store

### USE_PARAMETER_STORE

**Purpose:** Enable SSM Parameter Store for HA token  
**Type:** Boolean (string)  
**Default:** `false`  
**Valid Values:** `true`, `false`

```bash
USE_PARAMETER_STORE=false  # Use environment variable for token
USE_PARAMETER_STORE=true   # Use SSM for token (recommended)
```

**Impact:**
- When `true`: Token loaded from SSM (encrypted, secure)
- When `false`: Token loaded from HOME_ASSISTANT_TOKEN env var
- **Recommended:** Set to `true` for production

**Performance:**
- First call: ~250ms (SSM API call)
- Cached calls: 0ms (5-minute TTL)

**See:** DEC-21 for rationale

---

### PARAMETER_PREFIX

**Purpose:** SSM parameter path prefix  
**Type:** String  
**Default:** `/lambda-execution-engine`

```bash
PARAMETER_PREFIX=/lambda-execution-engine           # Default
PARAMETER_PREFIX=/prod/lee                          # Custom prefix
PARAMETER_PREFIX=/my-org/smart-home/lambda-engine   # Hierarchical
```

**Token Path:** `{PARAMETER_PREFIX}/home_assistant/token`

**Example:**
```bash
PARAMETER_PREFIX=/prod/lee
# Token at: /prod/lee/home_assistant/token
```

---

### SSM_CACHE_TTL

**Purpose:** SSM token cache duration in seconds  
**Type:** Integer  
**Default:** `300` (5 minutes)  
**Range:** 60-3600

```bash
SSM_CACHE_TTL=300    # Default (5 minutes)
SSM_CACHE_TTL=600    # 10 minutes
SSM_CACHE_TTL=3600   # 1 hour
```

**Notes:**
- Longer TTL = fewer SSM API calls
- Shorter TTL = faster token rotation
- Balance performance vs security

---

## Debug & Logging

### DEBUG_MODE

**Purpose:** Enable operation flow visibility  
**Type:** Boolean (string)  
**Default:** `false`  
**Valid Values:** `true`, `false`

```bash
DEBUG_MODE=false  # Default (production)
DEBUG_MODE=true   # Enable debug logging
```

**Output When Enabled:**
```
[DEBUG] Executing: cache.get, kwargs_keys=['key']
[INFO] Cache get: user_123
[DEBUG] Completed: cache.get, result_type=dict
```

**Impact:**
- Shows which operations called
- Shows operation parameters
- Shows operation results
- Increases log volume
- **Cost:** Higher CloudWatch Logs costs when enabled

**Use Cases:**
- Troubleshooting production issues
- Understanding request flow
- Debugging integration problems

**See:** DEC-22 for details

---

### DEBUG_TIMINGS

**Purpose:** Enable performance timing for operations  
**Type:** Boolean (string)  
**Default:** `false`  
**Valid Values:** `true`, `false`

```bash
DEBUG_TIMINGS=false  # Default (production)
DEBUG_TIMINGS=true   # Enable timing measurements
```

**Output When Enabled:**
```
[INFO] Cache get: user_123
[TIMING] cache.get: 0.85ms

[INFO] HTTP POST: /api/services/light/turn_on
[TIMING] http.post: 125.43ms
```

**Impact:**
- Shows operation execution time
- Identifies performance bottlenecks
- Uses high-precision timer (perf_counter)
- Minimal overhead (~0.01ms per operation)

**Use Cases:**
- Performance optimization
- Identifying slow operations
- Validating improvements
- Data-driven optimization (LESS-02)

**Combine With DEBUG_MODE:**
```bash
DEBUG_MODE=true
DEBUG_TIMINGS=true
# Shows what runs + how long it takes
```

**See:** DEC-23 for details

---

### LOG_LEVEL

**Purpose:** Python logging level  
**Type:** String  
**Default:** `INFO`  
**Valid Values:** `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`

```bash
LOG_LEVEL=INFO      # Default (standard logging)
LOG_LEVEL=DEBUG     # Verbose logging
LOG_LEVEL=WARNING   # Warnings and errors only
LOG_LEVEL=ERROR     # Errors only
LOG_LEVEL=CRITICAL  # Critical errors only
```

**Impact:**
- `DEBUG`: Very verbose (all messages)
- `INFO`: Normal operations
- `WARNING`: Issues that don't stop execution
- `ERROR`: Failures
- `CRITICAL`: System-level failures

**Notes:**
- Lower levels include higher levels (DEBUG includes INFO, WARNING, etc.)
- Production typically uses `INFO` or `WARNING`
- Development uses `DEBUG`

---

### USE_LOG_TEMPLATES

**Purpose:** Enable structured log templates  
**Type:** Boolean (string)  
**Default:** `false`  
**Valid Values:** `true`, `false`

```bash
USE_LOG_TEMPLATES=false  # Default (simple logging)
USE_LOG_TEMPLATES=true   # Enable structured templates
```

**Impact:** Enables pre-defined log message templates for consistency

---

### MAX_LOGS_PER_INVOCATION

**Purpose:** Maximum log messages per Lambda invocation  
**Type:** Integer  
**Default:** `500`  
**Range:** 100-10000

```bash
MAX_LOGS_PER_INVOCATION=500    # Default
MAX_LOGS_PER_INVOCATION=1000   # Allow more logs
```

**Impact:**
- Prevents log flooding attacks
- Protects CloudWatch Logs quota
- Logs after limit are dropped

---

### LOG_RATE_LIMIT_ENABLED

**Purpose:** Enable log rate limiting  
**Type:** Boolean (string)  
**Default:** `true`  
**Valid Values:** `true`, `false`

```bash
LOG_RATE_LIMIT_ENABLED=true   # Default (enabled)
LOG_RATE_LIMIT_ENABLED=false  # Disable rate limiting
```

**Impact:** Works with MAX_LOGS_PER_INVOCATION to prevent log spam

---

## System Configuration

### AWS_REGION

**Purpose:** AWS region for SDK operations  
**Type:** String  
**Default:** `us-east-1`  
**Valid Values:** Any AWS region code

```bash
AWS_REGION=us-east-1  # Default
AWS_REGION=us-west-2  # Oregon
AWS_REGION=eu-west-1  # Ireland
```

**Notes:**
- Typically set automatically by Lambda runtime
- Override only if needed for multi-region

---

### CONFIGURATION_TIER

**Purpose:** System configuration tier  
**Type:** String  
**Default:** `standard`  
**Valid Values:** `minimum`, `standard`, `maximum`, `user`

```bash
CONFIGURATION_TIER=standard  # Default (balanced)
CONFIGURATION_TIER=minimum   # Resource-constrained
CONFIGURATION_TIER=maximum   # Performance-optimized
```

**Impact:**
- `minimum`: Lowest resource usage
- `standard`: Balanced (recommended)
- `maximum`: Highest performance
- `user`: Custom configuration

---

### LAMBDA_MODE

**Purpose:** Lambda execution mode  
**Type:** String  
**Default:** `normal`  
**Valid Values:** `normal`, `failsafe`, `diagnostic`, `test`

```bash
LAMBDA_MODE=normal    # Default (full functionality)
LAMBDA_MODE=failsafe  # Emergency bypass mode
```

**Modes:**
- `normal`: Full LEE + HA integration
- `failsafe`: Alexa → HA direct (LEE bypass)
- `diagnostic`: Debug/testing mode
- `test`: Automated testing

**See:** DEC-20 for details

---

## Quick Reference

### Production Recommended Settings

```bash
# Home Assistant
HOME_ASSISTANT_ENABLED=true
HOME_ASSISTANT_URL=https://homeassistant.local:8123
HOME_ASSISTANT_TIMEOUT=30
HOME_ASSISTANT_VERIFY_SSL=true

# Performance
HA_CACHE_WARMING_ENABLED=true
HA_RATE_LIMIT_ENABLED=true
HA_RATE_LIMIT_PER_SECOND=10
HA_RATE_LIMIT_BURST=20

# SSM
USE_PARAMETER_STORE=true
PARAMETER_PREFIX=/lambda-execution-engine
SSM_CACHE_TTL=300

# Logging
LOG_LEVEL=INFO
DEBUG_MODE=false
DEBUG_TIMINGS=false

# System
LAMBDA_MODE=normal
CONFIGURATION_TIER=standard
```

---

### Development Settings

```bash
# Same as production, plus:
DEBUG_MODE=true
DEBUG_TIMINGS=true
LOG_LEVEL=DEBUG
HA_CACHE_WARMING_ENABLED=false  # See cold start behavior
```

---

### Troubleshooting Settings

```bash
# Enable all debugging:
DEBUG_MODE=true
DEBUG_TIMINGS=true
LOG_LEVEL=DEBUG

# Disable after troubleshooting to save costs
```

---

## Environment Variable Groups

### Required for Basic Operation
- HOME_ASSISTANT_URL
- HOME_ASSISTANT_TOKEN (or USE_PARAMETER_STORE=true)

### Recommended for Production
- HOME_ASSISTANT_ENABLED=true
- HA_CACHE_WARMING_ENABLED=true
- USE_PARAMETER_STORE=true
- LOG_LEVEL=INFO

### Optional Performance Tuning
- HA_RATE_LIMIT_PER_SECOND
- HA_RATE_LIMIT_BURST
- SSM_CACHE_TTL
- CONFIGURATION_TIER

### Optional Debugging
- DEBUG_MODE
- DEBUG_TIMINGS
- LOG_LEVEL=DEBUG

---

## Migration Guide

### From Legacy Configuration

**Old:**
```bash
HA_URL=http://homeassistant.local:8123
LONG_LIVED_ACCESS_TOKEN=eyJ...
```

**New:**
```bash
HOME_ASSISTANT_URL=http://homeassistant.local:8123
HOME_ASSISTANT_TOKEN=eyJ...
# Or better:
USE_PARAMETER_STORE=true
# (Token in SSM: /lambda-execution-engine/home_assistant/token)
```

---

### Enabling Cache Warming

**Before:**
```bash
# No cache warming
# First request: 1498ms
```

**After:**
```bash
HA_CACHE_WARMING_ENABLED=true
# First request: 300ms (80% improvement)
```

---

### Enabling SSM for Token

**Before:**
```bash
HOME_ASSISTANT_TOKEN=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
# Token visible in Lambda console
```

**After:**
```bash
USE_PARAMETER_STORE=true
PARAMETER_PREFIX=/lambda-execution-engine

# Create SSM parameter:
aws ssm put-parameter \
  --name /lambda-execution-engine/home_assistant/token \
  --type SecureString \
  --value "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# Remove HOME_ASSISTANT_TOKEN from environment
```

---

## Validation

### Check Configuration

```bash
# List all environment variables:
aws lambda get-function-configuration \
  --function-name my-function \
  --query 'Environment.Variables'

# Check specific variable:
aws lambda get-function-configuration \
  --function-name my-function \
  --query 'Environment.Variables.DEBUG_MODE'
```

---

### Update Configuration

```bash
# Update single variable:
aws lambda update-function-configuration \
  --function-name my-function \
  --environment Variables={DEBUG_MODE=true}

# Update multiple variables:
aws lambda update-function-configuration \
  --function-name my-function \
  --environment Variables="{
    DEBUG_MODE=true,
    DEBUG_TIMINGS=true,
    LOG_LEVEL=DEBUG
  }"
```

---

## References

- **DEC-20:** LAMBDA_MODE design
- **DEC-21:** SSM token-only configuration
- **DEC-22:** DEBUG_MODE implementation
- **DEC-23:** DEBUG_TIMINGS implementation
- **Performance Guide:** HA_API_Performance_Optimization_Guide_Plan.md

---

**Total Environment Variables:** 23  
**Required:** 2 (HOME_ASSISTANT_URL, token)  
**Recommended:** 6 (+ performance/SSM settings)  
**Optional:** 15 (debug/tuning)

---

**END OF REFERENCE**
