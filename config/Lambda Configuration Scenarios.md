# Lambda Configuration Scenarios
**Version:** 2025.10.22.01  
**Updated:** Added METRICS optimization scenarios from v2025.10.22 changelog

---

## Scenario 1: SSM Parameter Store (Recommended for Production)

### Purpose
Secure token storage with SecureString encryption, all other config in environment.

### Lambda Environment Variables

| Variable | Value |
|----------|-------|
| `USE_PARAMETER_STORE` | `true` |
| `PARAMETER_PREFIX` | `/lambda-execution-engine` |
| `HOME_ASSISTANT_ENABLED` | `true` |
| `HOME_ASSISTANT_URL` | `http://192.168.1.100:8123` |
| `HOME_ASSISTANT_TIMEOUT` | `30` |
| `HOME_ASSISTANT_VERIFY_SSL` | `true` |
| `HA_ASSISTANT_NAME` | `Jarvis` |
| `HA_FEATURES` | `standard` |
| `HA_WEBSOCKET_ENABLED` | `false` |
| `LOG_LEVEL` | `INFO` |
| `ENVIRONMENT` | `production` |
| `CONFIGURATION_TIER` | `standard` |
| `DEBUG_MODE` | `false` |
| `DEBUG_TIMINGS` | `false` |

**NEW - METRICS Optimization (Optional):**

| Variable | Value | Notes |
|----------|-------|-------|
| `METRICS_FAST_PATH` | `true` | Default - no need to set |
| `MAX_VALUES_PER_METRIC` | `1000` | Default - no need to set |
| `METRICS_ENABLE_STATS` | `false` | Default - set `true` for monitoring |

### SSM Parameter to Create

**ONLY ONE parameter in SSM:**

| Parameter Path | Type | Value |
|----------------|------|-------|
| `/lambda-execution-engine/home_assistant/token` | **SecureString** | `eyJ0eXAiOiJKV1Qi...` |

**Create via AWS CLI:**
```bash
aws ssm put-parameter \
  --name "/lambda-execution-engine/home_assistant/token" \
  --value "eyJ0eXAiOiJKV1Qi..." \
  --type "SecureString" \
  --description "Home Assistant Long-Lived Access Token"
```

### IAM Policy Required

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["ssm:GetParameter"],
      "Resource": "arn:aws:ssm:REGION:ACCOUNT:parameter/lambda-execution-engine/home_assistant/token"
    }
  ]
}
```

### Benefits
- ✅ Token encrypted at rest (SecureString)
- ✅ Token encrypted in transit (TLS)
- ✅ Token cached (300s TTL, reduces API calls)
- ✅ All other config visible in Lambda console
- ✅ Fast configuration changes (no SSM updates)
- ✅ METRICS optimizations enabled by default (30-50% faster)

---

## Scenario 2: Environment Variables Only (Simple Deployment)

### Purpose
Simplest setup with all configuration in Lambda environment, no SSM required.

### Lambda Environment Variables

| Variable | Value |
|----------|-------|
| `HOME_ASSISTANT_ENABLED` | `true` |
| `HOME_ASSISTANT_URL` | `http://192.168.1.100:8123` |
| `HOME_ASSISTANT_TOKEN` | `eyJ0eXAiOiJKV1Qi...` |
| `HOME_ASSISTANT_TIMEOUT` | `30` |
| `HOME_ASSISTANT_VERIFY_SSL` | `true` |
| `HA_ASSISTANT_NAME` | `Jarvis` |
| `HA_FEATURES` | `standard` |
| `HA_WEBSOCKET_ENABLED` | `false` |
| `LOG_LEVEL` | `INFO` |
| `ENVIRONMENT` | `production` |
| `CONFIGURATION_TIER` | `standard` |
| `DEBUG_MODE` | `false` |
| `DEBUG_TIMINGS` | `false` |

**METRICS variables use defaults (no need to set):**
- `METRICS_FAST_PATH=true` (automatic)
- `MAX_VALUES_PER_METRIC=1000` (automatic)
- `METRICS_ENABLE_STATS=false` (automatic)

### Notes
- No SSM parameters needed
- No additional IAM permissions required
- Token stored as plaintext environment variable (less secure)
- Simpler setup for development/testing
- Configuration changes require Lambda update
- METRICS optimizations enabled automatically

### Benefits
- ✅ Simplest configuration
- ✅ No SSM dependencies
- ✅ No IAM complexity
- ✅ METRICS optimizations automatic
- ⚠️ Token visible in Lambda console
- ⚠️ Token in plaintext (base64 encoded by AWS)

---

## Scenario 3: Failsafe Mode (Emergency Recovery)

### Purpose
Emergency fallback when LEE fails. Bypasses all LEE/SUGA architecture and routes requests directly to Home Assistant's native Alexa Smart Home API.

### When to Use
- LEE crashes after deployment
- Critical bugs preventing normal operation
- Need immediate restoration while debugging
- Family needs smart home working NOW

### Lambda Environment Variables

| Variable | Value | Notes |
|----------|-------|-------|
| `LAMBDA_MODE` | `failsafe` | **Master switch** - activates failsafe mode |
| `HOME_ASSISTANT_URL` | `http://192.168.1.100:8123` | Base URL of HA instance |
| `HOME_ASSISTANT_TOKEN` | `eyJ0eXAiOiJKV1Qi...` | Long-lived access token |
| `HOME_ASSISTANT_VERIFY_SSL` | `false` | Optional - disable SSL verification |
| `DEBUG_MODE` | `true` | Optional - enable verbose logging |
| `DEBUG_TIMINGS` | `true` | Optional - enable timing measurements |

**Note:** METRICS optimization variables are ignored in failsafe mode (LEE bypassed entirely).

### Minimal Configuration (Copy-Paste Ready)
```bash
LAMBDA_MODE=failsafe
HOME_ASSISTANT_URL=http://192.168.1.100:8123
HOME_ASSISTANT_TOKEN=eyJ0eXAiOiJKV1Qi...
HOME_ASSISTANT_VERIFY_SSL=false
DEBUG_MODE=true
DEBUG_TIMINGS=true
```

### Features

| Feature | Normal Mode | Failsafe Mode |
|---------|-------------|---------------|
| LEE/SUGA Gateway | ✅ | ❌ Bypassed |
| Direct HA Calls | ❌ | ✅ |
| Circuit Breakers | ✅ | ❌ |
| Caching | ✅ | ❌ |
| Metrics | ✅ | ❌ |
| METRICS Optimization | ✅ | ❌ Not loaded |
| Memory Usage | ~67MB | ~42MB |
| Response Time | ~150ms | ~50ms |
| Reliability | 99.9% | 99.99% |

### Recovery Process

1. **Enable Failsafe (Instant)**
   ```bash
   aws lambda update-function-configuration \
     --function-name your-lambda \
     --environment Variables="{LAMBDA_MODE=failsafe,HOME_ASSISTANT_URL=http://...,HOME_ASSISTANT_TOKEN=...}"
   ```

2. **Verify Operation**
   - Test Alexa commands
   - Check CloudWatch logs: `[FAILSAFE] INFO: Failsafe mode activated`
   - Confirm family is happy

3. **Debug LEE (While Failsafe Active)**
   - Review CloudWatch logs
   - Identify root cause
   - Apply fixes
   - Test in separate environment

4. **Restore Normal Operation**
   ```bash
   aws lambda update-function-configuration \
     --function-name your-lambda \
     --environment Variables="{HOME_ASSISTANT_URL=http://...,HOME_ASSISTANT_TOKEN=...}"
   ```
   **Note:** Omit `LAMBDA_MODE` variable entirely - defaults to `normal`

5. **Monitor**
   - Watch CloudWatch logs
   - Test all Alexa commands
   - Verify full functionality

### Important Notes
- Failsafe activates **before** any LEE imports
- No code changes required (environment variable only)
- Can use SSM for token even in failsafe mode
- Original HA configuration unaffected
- No changes to Alexa skill required
- Toggle on/off without redeployment
- METRICS optimizations not available in failsafe mode

---

## Scenario 4: Configuration Tier Optimization

### Purpose
Tune memory allocation and circuit breaker behavior based on deployment requirements.

### Tier Comparison

| Tier | Memory | Protected Services | Failure Threshold | Recovery Time | METRICS History |
|------|--------|-------------------|------------------|---------------|-----------------|
| `minimum` | ~15MB | None | N/A | N/A | 500 values |
| `standard` | ~20MB | Critical only | 5 failures | 60s | 1000 values |
| `maximum` | ~30MB | All services | 3 failures | 30s | 2000 values |

### Minimal Tier (Resource Constrained)
```bash
CONFIGURATION_TIER=minimum
HOME_ASSISTANT_ENABLED=true
HA_WEBSOCKET_ENABLED=false

# METRICS optimization for low memory
MAX_VALUES_PER_METRIC=500      # Reduce history
METRICS_FAST_PATH=true         # Keep fast path (minimal overhead)
```
- Lowest memory footprint
- No circuit breaker protection
- Reduced metric history
- Best for: Testing, development, tight memory constraints (128MB Lambda)

### Standard Tier (Production Recommended)
```bash
CONFIGURATION_TIER=standard
HOME_ASSISTANT_ENABLED=true
HA_WEBSOCKET_ENABLED=false

# METRICS uses defaults (no need to set)
# METRICS_FAST_PATH=true (automatic)
# MAX_VALUES_PER_METRIC=1000 (automatic)
```
- Balanced memory and protection
- Circuit breakers on critical services
- Standard metric history
- Best for: Most production deployments (256MB Lambda)

### Maximum Tier (High Reliability)
```bash
CONFIGURATION_TIER=maximum
HOME_ASSISTANT_ENABLED=true
HA_WEBSOCKET_ENABLED=true

# METRICS optimization for high reliability
MAX_VALUES_PER_METRIC=2000     # More history
METRICS_ENABLE_STATS=true      # Monitor performance
```
- Maximum circuit breaker protection
- All services protected
- Fastest recovery
- Extended metric history
- Best for: Mission-critical deployments (512MB+ Lambda)

---

## Scenario 5: Debug Mode with Diagnostics

### Purpose
Enable enhanced logging and diagnostic tools for troubleshooting.

### Lambda Environment Variables

```bash
# Debug settings
DEBUG_MODE=true
DEBUG_TIMINGS=true

# Core settings
LOG_LEVEL=DEBUG
ENVIRONMENT=development
CONFIGURATION_TIER=standard

# Home Assistant
HOME_ASSISTANT_ENABLED=true
HOME_ASSISTANT_URL=http://192.168.1.100:8123
HOME_ASSISTANT_TOKEN=eyJ0eXAiOiJKV1Qi...

# METRICS debugging
METRICS_FAST_PATH=false        # Disable to see all validation
MAX_VALUES_PER_METRIC=500      # Smaller for testing
METRICS_ENABLE_STATS=true      # Track performance
```

### What Debug Modes Enable

**DEBUG_MODE=true:**
- Function entry/exit points
- Operation routing decisions
- Gateway operation dispatch
- Cache hit/miss events
- Configuration loading steps
- Error conditions with context
- Extension initialization
- API call parameters
- **NEW:** METRICS fast path hits/misses
- **NEW:** METRICS validation details
- **NEW:** METRICS eviction events

**DEBUG_TIMINGS=true:**
- Cold start timing breakdown
- Module import durations
- SSM API call latency
- Cache operation performance
- HTTP request/response times
- Gateway dispatch overhead
- Total operation duration
- Step-by-step timing within operations
- **NEW:** METRICS operation latency (fast vs validation path)
- **NEW:** METRICS eviction timing

**CloudWatch Output Examples:**
```
[SSM_DEBUG] Retrieving Home Assistant token from SSM
[SSM_TIMING] SSM token retrieval: 250ms, success=true
[HA_CONFIG_DEBUG] Loading HA config (force_refresh=false)
[HA_CONFIG_TIMING] Config built: 300ms
[CACHE_DEBUG] cache_get: key=ha_config, hit=True
[GATEWAY_DEBUG] execute_operation: interface=CACHE, operation=get
[METRICS_DEBUG] Fast path hit: request_count (5μs)
[METRICS_DEBUG] Validation path: new_metric_name (15μs)
[METRICS_DEBUG] FIFO eviction: old_metric (1000 → 999 values)
[METRICS_TIMING] Metric operation: 7μs (fast_path=true)
[METRICS_STATS] Rate limiting: 0 blocked, 1547 allowed
```

### METRICS Debugging Tips

**Disable fast path to see validation:**
```bash
METRICS_FAST_PATH=false  # All operations use validation path
DEBUG_MODE=true          # Show validation details
```

**Monitor eviction patterns:**
```bash
MAX_VALUES_PER_METRIC=100   # Low limit to trigger frequent evictions
METRICS_ENABLE_STATS=true   # Track eviction count
DEBUG_MODE=true             # Show eviction events
```

**Test memory limits:**
```bash
METRICS_ENABLE_STATS=true   # Monitor total values stored
DEBUG_TIMINGS=true          # Track eviction performance
```

### CloudWatch Insights Queries

**Find slow operations:**
```
fields @timestamp, @message
| filter @message like /\[.*_TIMING\]/
| filter @message like /elapsed:/
| parse @message '*elapsed: *ms*' as component, elapsed
| filter elapsed > 1000
| sort elapsed desc
```

**METRICS fast path effectiveness (NEW):**
```
fields @timestamp, @message
| filter @message like /\[METRICS_DEBUG\]/
| filter @message like /(Fast path|Validation path)/
| stats count() by fast_path
```

**METRICS eviction rate (NEW):**
```
fields @timestamp, @message
| filter @message like /\[METRICS_DEBUG\]/
| filter @message like /FIFO eviction/
| stats count() as evictions by bin(5m)
```

**Track SSM performance:**
```
fields @timestamp, @message
| filter @message like /\[SSM_TIMING\]/
| filter @message like /SSM API:/
| parse @message '*SSM API: *ms*' as label, duration
| stats avg(duration), max(duration), count() as calls
```

**Cache hit rate:**
```
fields @timestamp, @message
| filter @message like /\[CACHE_DEBUG\]/
| filter @message like /cache_get/
| parse @message '*hit=*' as prefix, result
| stats count() by result
```

### When to Use
- Investigating performance issues
- Debugging configuration loading
- Analyzing SSM token retrieval
- Troubleshooting API failures
- Optimizing cold start times
- Understanding execution flow
- **NEW:** Tuning METRICS performance (fast path effectiveness)
- **NEW:** Analyzing memory usage patterns (eviction rates)
- **NEW:** Validating rate limiting behavior

### Warning
Debug modes generate significant CloudWatch logs.

**Cost Impact:**
- `DEBUG_MODE`: 3-5x log volume (~$0.50-$1.00 per million requests)
- `DEBUG_TIMINGS`: 2-3x log volume (~$0.30-$0.60 per million requests)
- Combined: 5-8x log volume (~$0.80-$1.60 per million requests)

**Recommendations:**
1. Enable only temporarily for troubleshooting
2. Use `DEBUG_TIMINGS` alone for performance analysis
3. Set CloudWatch retention to 7 days for debug logs
4. Disable immediately after diagnosis complete
5. Never enable in production long-term

---

## Scenario 6: High-Reliability Production

### Purpose
Maximum resilience for critical production deployments with optimized METRICS.

### Lambda Environment Variables

```bash
# Core Configuration
LOG_LEVEL=INFO
ENVIRONMENT=production
DEBUG_MODE=false
DEBUG_TIMINGS=false
CONFIGURATION_TIER=maximum

# SSM Parameter Store (Token Only)
USE_PARAMETER_STORE=true
PARAMETER_PREFIX=/lambda-prod

# Home Assistant
HOME_ASSISTANT_ENABLED=true
HOME_ASSISTANT_URL=https://ha.example.com
HOME_ASSISTANT_TIMEOUT=30
HOME_ASSISTANT_VERIFY_SSL=true
HA_ASSISTANT_NAME=Jarvis
HA_FEATURES=full
HA_WEBSOCKET_ENABLED=false

# METRICS Optimization (NEW)
METRICS_FAST_PATH=true         # Default - enable fast path
MAX_VALUES_PER_METRIC=2000     # Extended history for high-memory Lambda
METRICS_ENABLE_STATS=true      # Monitor production performance
```

### SSM Parameter (Token Only)

```bash
/lambda-prod/home_assistant/token (SecureString)
```

**Create via CLI:**
```bash
aws ssm put-parameter \
  --name "/lambda-prod/home_assistant/token" \
  --value "eyJ0eXAiOiJKV1Qi..." \
  --type "SecureString"
```

### Architecture Benefits

**Circuit Breaker Protection:**
- Prevents cascade failures
- Automatic service isolation
- Self-healing recovery (30s)
- All services protected (maximum tier)

**Security:**
- Token in SSM SecureString (encrypted at rest)
- SSL verification enabled
- Encrypted transit (TLS)
- Minimal IAM permissions

**Performance:**
- Token cached (300s TTL)
- Single SSM call per 5 minutes
- Optimized cold starts
- Sub-200ms response times
- **NEW:** 30-50% faster METRICS operations (fast path)
- **NEW:** Extended metric history (2000 values)

**Reliability:**
- Circuit breakers trip at 3 failures
- 30-second recovery windows
- Automatic healing
- Failsafe fallback available
- **NEW:** Bounded METRICS memory (prevents exhaustion)
- **NEW:** Production monitoring enabled (stats)

### Monitoring Setup

**CloudWatch Alarms:**
```bash
# Alert on errors
aws cloudwatch put-metric-alarm \
  --alarm-name lambda-error-rate \
  --metric-name Errors \
  --threshold 10 \
  --evaluation-periods 2

# Alert on duration
aws cloudwatch put-metric-alarm \
  --alarm-name lambda-duration \
  --metric-name Duration \
  --threshold 3000 \
  --evaluation-periods 2

# NEW - Alert on METRICS memory (requires METRICS_ENABLE_STATS=true)
aws cloudwatch put-metric-alarm \
  --alarm-name metrics-memory-high \
  --metric-name MetricValuesCount \
  --namespace Lambda/SUGA-ISP \
  --threshold 15000000 \
  --evaluation-periods 2
```

**Log Insights Queries:**
```
# Error tracking
fields @timestamp, @message
| filter @message like /ERROR/
| stats count() by bin(5m)

# Performance monitoring
fields @timestamp, @message
| filter @message like /duration_ms/
| stats avg(duration_ms), max(duration_ms), min(duration_ms)

# NEW - METRICS performance
fields @timestamp, @message
| filter @message like /\[METRICS_STATS\]/
| parse @message '*Total metrics: *' as prefix, metric_count
| stats latest(metric_count) by bin(5m)
```

---

## Scenario 7: Multi-Environment Setup

### Purpose
Separate configurations for development, staging, and production with appropriate METRICS tuning.

### Development Lambda
```bash
ENVIRONMENT=development
DEBUG_MODE=true
DEBUG_TIMINGS=true
LOG_LEVEL=DEBUG
CONFIGURATION_TIER=minimum
HOME_ASSISTANT_ENABLED=true
HOME_ASSISTANT_URL=http://dev-ha.local:8123
HOME_ASSISTANT_TOKEN=dev_token_xyz...
HOME_ASSISTANT_VERIFY_SSL=false
HA_FEATURES=development

# METRICS for development/testing
METRICS_FAST_PATH=false        # Disable to test validation
MAX_VALUES_PER_METRIC=100      # Small for frequent evictions
METRICS_ENABLE_STATS=true      # Monitor behavior
```

### Staging Lambda
```bash
ENVIRONMENT=staging
DEBUG_MODE=false
DEBUG_TIMINGS=false
LOG_LEVEL=INFO
CONFIGURATION_TIER=standard
HOME_ASSISTANT_ENABLED=true
HOME_ASSISTANT_URL=http://staging-ha.local:8123
USE_PARAMETER_STORE=true
PARAMETER_PREFIX=/lambda-staging
HOME_ASSISTANT_VERIFY_SSL=true
HA_FEATURES=standard

# METRICS for staging (production-like)
METRICS_FAST_PATH=true         # Test fast path behavior
MAX_VALUES_PER_METRIC=1000     # Standard history
METRICS_ENABLE_STATS=true      # Monitor before prod deployment
```

### Production Lambda
```bash
ENVIRONMENT=production
DEBUG_MODE=false
DEBUG_TIMINGS=false
LOG_LEVEL=WARNING
CONFIGURATION_TIER=maximum
HOME_ASSISTANT_ENABLED=true
HOME_ASSISTANT_URL=https://ha.example.com
USE_PARAMETER_STORE=true
PARAMETER_PREFIX=/lambda-prod
HOME_ASSISTANT_VERIFY_SSL=true
HA_FEATURES=full

# METRICS for production (optimized)
METRICS_FAST_PATH=true         # Maximum performance
MAX_VALUES_PER_METRIC=2000     # Extended history
METRICS_ENABLE_STATS=true      # Production monitoring
```

### SSM Parameters by Environment
```
Development: No SSM (token in environment)
Staging:     /lambda-staging/home_assistant/token
Production:  /lambda-prod/home_assistant/token
```

### Benefits
- ✅ Isolated configurations
- ✅ Environment-specific tokens
- ✅ Different debug levels
- ✅ Tiered reliability
- ✅ Easy promotion path
- ✅ Progressive METRICS testing (dev → staging → prod)

---

## Scenario 8: METRICS Optimization Scenarios (NEW)

### Scenario 8A: High-Traffic Production (Memory Optimized)

**Use Case:** High-volume deployments with 512MB+ Lambda

```bash
# Base configuration
CONFIGURATION_TIER=standard
HOME_ASSISTANT_ENABLED=true
HOME_ASSISTANT_URL=https://ha.example.com
USE_PARAMETER_STORE=true

# METRICS optimization for high traffic
METRICS_FAST_PATH=true         # 30-50% faster operations
MAX_VALUES_PER_METRIC=2000     # Extended history (requires more memory)
METRICS_ENABLE_STATS=true      # Monitor performance and capacity
```

**Benefits:**
- Handles 10,000+ metrics efficiently
- Extended history without memory issues
- Production monitoring enabled
- Optimal performance with fast path

**Memory Budget:** ~35-40MB for METRICS (2000 values × 10,000 metrics)

### Scenario 8B: Memory-Constrained (128MB Lambda)

**Use Case:** Tight memory constraints, need to minimize overhead

```bash
# Base configuration
CONFIGURATION_TIER=minimum
HOME_ASSISTANT_ENABLED=true
HOME_ASSISTANT_URL=http://192.168.1.100:8123
HOME_ASSISTANT_TOKEN=eyJ0eXAiOiJKV1Qi...

# METRICS optimization for low memory
METRICS_FAST_PATH=true         # Keep fast path (minimal overhead)
MAX_VALUES_PER_METRIC=500      # Reduced history to save memory
METRICS_ENABLE_STATS=false     # Disable to save processing/memory
```

**Benefits:**
- Minimal memory footprint (~15-20MB total)
- Still benefits from fast path optimization
- Handles 5,000+ metrics safely
- No stats overhead

**Memory Budget:** ~10-12MB for METRICS (500 values × 5,000 metrics)

### Scenario 8C: Development/Testing (Eviction Testing)

**Use Case:** Testing memory limits and eviction behavior

```bash
# Base configuration
ENVIRONMENT=development
DEBUG_MODE=true
DEBUG_TIMINGS=true
CONFIGURATION_TIER=standard

# METRICS for testing eviction
METRICS_FAST_PATH=false        # Disable to see all validation
MAX_VALUES_PER_METRIC=100      # Very low to trigger frequent evictions
METRICS_ENABLE_STATS=true      # Monitor eviction patterns
```

**Benefits:**
- Triggers evictions quickly for testing
- Shows validation details (fast path disabled)
- Comprehensive logging of eviction events
- Stats track eviction frequency

**Expected CloudWatch Output:**
```
[METRICS_DEBUG] FIFO eviction: test_metric (100 → 99 values)
[METRICS_TIMING] Eviction operation: 1μs
[METRICS_STATS] Total evictions: 347
```

### Scenario 8D: Production Monitoring (Stats-Heavy)

**Use Case:** Need detailed production metrics and capacity planning

```bash
# Base configuration
ENVIRONMENT=production
CONFIGURATION_TIER=maximum
USE_PARAMETER_STORE=true

# METRICS for comprehensive monitoring
METRICS_FAST_PATH=true         # Maintain performance
MAX_VALUES_PER_METRIC=1500     # Balanced history
METRICS_ENABLE_STATS=true      # Detailed statistics

# Enable additional CloudWatch metrics export
```

**Benefits:**
- Detailed performance statistics
- Capacity planning data
- Rate limiting effectiveness
- Memory usage tracking
- Operation frequency analysis

**CloudWatch Custom Metrics (when stats enabled):**
- `MetricCount` - Total unique metrics
- `MetricValuesCount` - Total values stored
- `EvictionCount` - FIFO evictions triggered
- `FastPathHitRate` - Fast path effectiveness
- `RateLimitBlocked` - Rate limit rejections

---

## Quick Reference Table

| Scenario | Memory | Latency | SSM | Debug | METRICS Fast Path | METRICS History | Use Case |
|----------|--------|---------|-----|-------|------------------|----------------|----------|
| SSM Token Only | ~67MB | ~150ms | Token only | Off | ✅ Enabled | 1000 (default) | Recommended production |
| Environment Only | ~67MB | ~150ms | None | Off | ✅ Enabled | 1000 (default) | Simple deployment |
| Failsafe | ~42MB | ~50ms | Optional | Optional | ❌ Not loaded | N/A | Emergency recovery |
| Minimum Tier | ~50MB | ~120ms | Optional | Off | ✅ Enabled | 500 | Resource constrained |
| Standard Tier | ~67MB | ~150ms | Recommended | Off | ✅ Enabled | 1000 | Normal production |
| Maximum Tier | ~85MB | ~180ms | Recommended | Off | ✅ Enabled | 2000 | High reliability |
| Debug Mode | ~70MB | ~160ms | Optional | On | ❌ Disabled | 500 | Troubleshooting |
| High Reliability | ~85MB | ~180ms | Required | Off | ✅ Enabled | 2000 | Mission critical |
| High-Traffic | ~90MB | ~145ms | Required | Off | ✅ Enabled | 2000 | High volume |
| Memory-Constrained | ~50MB | ~140ms | Optional | Off | ✅ Enabled | 500 | 128MB Lambda |

---

## Migration from Old Configuration

### If You Have LEE_FAILSAFE_ENABLED (Deprecated)

**OLD (No longer works):**
```bash
LEE_FAILSAFE_ENABLED=true  # ❌ Removed in v2025.10.22
```

**NEW (Use this):**
```bash
LAMBDA_MODE=failsafe  # ✅ Current
```

**Or for normal operation (default):**
```bash
# Option 1: Omit LAMBDA_MODE entirely (defaults to normal)
# No variable needed

# Option 2: Explicitly set (not necessary)
LAMBDA_MODE=normal
```

### If You Have Multiple SSM Parameters

**OLD (No longer supported):**
```bash
# Multiple SSM parameters
/lambda-execution-engine/home_assistant/url
/lambda-execution-engine/home_assistant/token
/lambda-execution-engine/home_assistant/timeout
# ... etc
```

**NEW (Token only):**
```bash
# Lambda environment variables
HOME_ASSISTANT_URL=http://...
HOME_ASSISTANT_TIMEOUT=30
# ... all config except token

# Single SSM parameter
/lambda-execution-engine/home_assistant/token  # Only this
```

### Adopting v2025.10.22 METRICS Optimizations

**No migration required!** METRICS optimizations are:
- ✅ Enabled by default (fast path automatic)
- ✅ Backward compatible (no breaking changes)
- ✅ Optional customization (all have sensible defaults)

**To customize (optional):**
```bash
# Only set these if you need non-default values
METRICS_FAST_PATH=true          # Default anyway
MAX_VALUES_PER_METRIC=1000      # Default anyway
METRICS_ENABLE_STATS=true       # Set for production monitoring
```

**Benefits You Get Automatically:**
- 30-50% faster METRICS operations
- Protection against memory exhaustion
- Bounded storage (prevents DoS attacks)
- Zero code changes required

---

## Performance Benchmarks

### Cold Start Times

| Configuration | INIT Phase | First Request | Total | Notes |
|---------------|-----------|---------------|-------|-------|
| Failsafe | 150ms | 50ms | 200ms | Minimal imports |
| Minimum Tier | 300ms | 100ms | 400ms | No circuit breakers |
| Standard Tier (No SSM) | 400ms | 150ms | 550ms | Token from env |
| Standard Tier (SSM cached) | 400ms | 152ms | 552ms | Token cached |
| Standard Tier (SSM uncached) | 400ms | 400ms | 800ms | Token from API |
| Maximum Tier | 450ms | 200ms | 650ms | All features |

### Warm Start Times

| Configuration | Response Time | METRICS Overhead |
|---------------|---------------|------------------|
| Failsafe | ~50ms | N/A (not loaded) |
| All Tiers (Fast path) | ~100-150ms | +5μs per operation |
| All Tiers (Validation) | ~100-150ms | +15μs per operation |
| With Debug | ~160ms | +2ms (logging) |

### METRICS Performance (NEW)

| Operation Type | Fast Path | Validation Path | Improvement |
|---------------|-----------|-----------------|-------------|
| Hot metrics (>50 calls) | ~5μs | ~15μs | 67% faster |
| Cold metrics (<50 calls) | ~15μs | ~15μs | Same |
| Memory eviction | ~1μs | ~1μs | N/A |
| Rate limit check | <1μs | <1μs | N/A |

**Key Insight:** Fast path provides 30-50% improvement on frequently accessed metrics (80% of traffic in typical deployments).

---

## Related Documentation

- **Debug System:** `REMINDER - Debug Trapping and Performance Analysis.md`
- **SSM Migration:** `MIGRATION GUIDE - SSM Simplification (Token Only).md`
- **Variable Reference:** `Lambda Environment Variables and SSM Parameters Reference.md`
- **LAMBDA_MODE Change:** `BREAKING CHANGE - LEE_FAILSAFE_ENABLED to LAMBDA_MODE.md`
- **METRICS Optimization:** `changelog-v2025.10.22-Beta.md`
- **Security Fixes:** `NM06-LESSONS-2025.10.21-METRICS-Phase1.md`

---

# EOF
