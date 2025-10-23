# Lambda Environment Variables and SSM Parameters Reference
**Version:** 2025.10.22.01  
**Updated:** Added METRICS optimization variables from v2025.10.22 changelog

---

## Quick Reference

### Critical Variables

| Variable | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `LAMBDA_MODE` | String | No | `normal` | Operation mode: `normal`, `failsafe`, `diagnostic` |
| `HOME_ASSISTANT_ENABLED` | Boolean | No | `false` | Enable Home Assistant extension |
| `HOME_ASSISTANT_URL` | String | Yes* | - | Base URL of Home Assistant instance |
| `HOME_ASSISTANT_TOKEN` | String | No** | - | Long-lived access token (fallback) |
| `USE_PARAMETER_STORE` | Boolean | No | `false` | Enable SSM Parameter Store for token |
| `DEBUG_MODE` | Boolean | No | `false` | Enable debug output |
| `DEBUG_TIMINGS` | Boolean | No | `false` | Enable timing measurements |

\* Required when `HOME_ASSISTANT_ENABLED=true`  
\*\* Required if not using SSM Parameter Store

---

## LAMBDA_MODE (Operation Mode)

**Controls Lambda execution mode**

```bash
LAMBDA_MODE=normal      # Default - Full LEE operation (default if not set)
LAMBDA_MODE=failsafe    # Emergency - Direct HA passthrough
LAMBDA_MODE=diagnostic  # Testing - Diagnostic mode
```

### Mode Comparison

| Feature | Normal | Failsafe | Diagnostic |
|---------|--------|----------|------------|
| LEE/SUGA | ✅ Full | ❌ Bypassed | ⚠️ Limited |
| Memory | ~67MB | ~42MB | ~50MB |
| Latency | ~150ms | ~50ms | Varies |
| All Features | ✅ | ❌ | ⚠️ |
| Use Case | Production | Emergency | Testing |

**Default:** If `LAMBDA_MODE` is not set, defaults to `normal` mode. You do not need to explicitly set `LAMBDA_MODE=normal` for normal operation.

**Deprecated:** `LEE_FAILSAFE_ENABLED` has been removed. Use `LAMBDA_MODE=failsafe` instead.

---

## Core Lambda Configuration

### System Settings

| Variable | Type | Values | Description |
|----------|------|--------|-------------|
| `ENVIRONMENT` | String | `development`/`staging`/`production` | Deployment environment |
| `LOG_LEVEL` | String | `DEBUG`/`INFO`/`WARNING`/`ERROR`/`CRITICAL` | CloudWatch logging verbosity |
| `CONFIGURATION_TIER` | String | `minimum`/`standard`/`maximum`/`user` | Circuit breaker tier |

### Debug Settings

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `DEBUG_MODE` | Boolean | `false` | Enable debug statements |
| `DEBUG_TIMINGS` | Boolean | `false` | Enable timing measurements |

**Debug Output:**
- `DEBUG_MODE=true` → Shows execution flow, routing decisions, configuration loading
- `DEBUG_TIMINGS=true` → Shows performance measurements with millisecond precision
- Both can be enabled simultaneously for comprehensive diagnostics

**Cost Impact:**
- `DEBUG_MODE`: 3-5x log volume increase (~$0.50-$1.00 per million requests)
- `DEBUG_TIMINGS`: 2-3x log volume increase (~$0.30-$0.60 per million requests)
- **Recommendation:** Enable only for troubleshooting, disable immediately after

---

## METRICS Interface Configuration (NEW in v2025.10.22)

### METRICS Optimization Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `METRICS_FAST_PATH` | Boolean | `true` | Enable fast path optimization for hot metrics |
| `MAX_VALUES_PER_METRIC` | Integer | `1000` | Maximum values stored per metric (FIFO eviction) |
| `METRICS_ENABLE_STATS` | Boolean | `false` | Enable detailed rate limiting statistics |

### METRICS_FAST_PATH

**Purpose:** Bypasses validation for known hot metrics (30-50% performance improvement)

```bash
METRICS_FAST_PATH=true   # Default - enabled (recommended)
METRICS_FAST_PATH=false  # Disable if issues occur
```

**Benefits:**
- 30-50% faster on frequently accessed metrics
- Automatic hot path detection
- Zero configuration required

**When to Disable:**
- Debugging validation issues
- Testing new metric names
- Development environments only

**Performance:** +50ns per metric operation when disabled

### MAX_VALUES_PER_METRIC

**Purpose:** Controls memory usage by limiting metric history with FIFO eviction

```bash
MAX_VALUES_PER_METRIC=1000  # Default - balanced
MAX_VALUES_PER_METRIC=500   # Low memory (128MB Lambda)
MAX_VALUES_PER_METRIC=2000  # High memory (512MB+ Lambda)
```

**Memory Impact:**
- 1 metric, 1000 values: ~16KB
- 10,000 metrics @ 1000 values each: ~160MB

**Security:**
- Prevents unbounded memory growth
- Mitigates memory exhaustion DoS attacks
- FIFO eviction (oldest data removed first)

**Tuning Guidelines:**

| Lambda Memory | Recommended Value | Max Metrics |
|---------------|-------------------|-------------|
| 128MB | 500 | ~5,000 |
| 256MB | 1000 (default) | ~10,000 |
| 512MB+ | 2000 | ~20,000 |

### METRICS_ENABLE_STATS

**Purpose:** Tracks detailed statistics for rate limiting and performance monitoring

```bash
METRICS_ENABLE_STATS=false  # Default - disabled
METRICS_ENABLE_STATS=true   # Enable for monitoring
```

**Statistics Tracked:**
- Rate limiting hits/blocks
- Operation frequency
- Memory usage patterns
- Performance bottlenecks

**Use Cases:**
- Production monitoring
- Capacity planning
- Performance tuning
- Security auditing

**Overhead:** <1ms per 1000 operations, minimal impact

**CloudWatch Integration:** Exports statistics as custom CloudWatch metrics when enabled

---

## Home Assistant Extension Configuration

### Core Settings

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `HOME_ASSISTANT_ENABLED` | Boolean | `false` | Master switch for HA extension |
| `HOME_ASSISTANT_URL` | String | - | Base URL (e.g., `http://192.168.1.100:8123`) |
| `HOME_ASSISTANT_TOKEN` | String | - | Long-lived token (if not using SSM) |
| `HOME_ASSISTANT_TIMEOUT` | Integer | `30` | API timeout in seconds |
| `HOME_ASSISTANT_VERIFY_SSL` | Boolean | `true` | Verify SSL certificates |

### Extension Features

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `HA_ASSISTANT_NAME` | String | `Jarvis` | Assistant name for responses |
| `HA_FEATURES` | String | `standard` | Feature preset: `minimal`/`standard`/`full`/`development` |
| `HA_WEBSOCKET_ENABLED` | Boolean | `false` | Enable WebSocket support |
| `HA_WEBSOCKET_TIMEOUT` | Integer | `10` | WebSocket timeout in seconds |

---

## SSM Parameter Store Configuration (TOKEN-ONLY)

### Enabling SSM

```bash
USE_PARAMETER_STORE=true
PARAMETER_PREFIX=/lambda-execution-engine
```

### CRITICAL: Token Only in SSM

**SSM now stores ONLY the Home Assistant token.**

**SSM Parameter:**
```
/lambda-execution-engine/home_assistant/token (SecureString)
```

**All other configuration MUST be in Lambda environment variables:**
- URL, timeout, verify_ssl, assistant_name, features, websocket settings
- Log level, environment, debug mode, configuration tier
- METRICS optimization variables (METRICS_FAST_PATH, MAX_VALUES_PER_METRIC, etc.)
- Everything except the token

### SSM Priority

**Token loading priority:**
1. SSM Parameter Store (if `USE_PARAMETER_STORE=true`)
2. `HOME_ASSISTANT_TOKEN` environment variable
3. `LONG_LIVED_ACCESS_TOKEN` environment variable (legacy)

**Performance:**
- First call: ~250ms (SSM API call)
- Subsequent calls: <2ms (cached for 300 seconds)
- Cache TTL: 300 seconds (5 minutes)

### IAM Permissions

**Minimal permissions required:**
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

**Note:** Only `ssm:GetParameter` needed for single token parameter.

---

## Configuration Priority

### Normal Mode
1. Lambda environment variables (primary)
2. SSM Parameter Store token (if `USE_PARAMETER_STORE=true`)
3. Default values

### Failsafe Mode (`LAMBDA_MODE=failsafe`)
1. Lambda environment variables ONLY
2. No SSM calls (faster, simpler)
3. Token from `HOME_ASSISTANT_TOKEN` environment variable

---

## Configuration Examples

### Minimal (Environment Only)
```bash
HOME_ASSISTANT_ENABLED=true
HOME_ASSISTANT_URL=http://192.168.1.100:8123
HOME_ASSISTANT_TOKEN=eyJ0eXAiOiJKV1Qi...
```

### Optimized METRICS (NEW)
```bash
# Standard configuration with METRICS optimization
HOME_ASSISTANT_ENABLED=true
HOME_ASSISTANT_URL=http://192.168.1.100:8123
HOME_ASSISTANT_TOKEN=eyJ0eXAiOiJKV1Qi...

# METRICS optimization (all optional)
METRICS_FAST_PATH=true          # Default - enable fast path
MAX_VALUES_PER_METRIC=1000      # Default - 1000 values per metric
METRICS_ENABLE_STATS=false      # Default - disable stats
```

### High-Performance METRICS
```bash
# For high-traffic deployments with 512MB+ Lambda
HOME_ASSISTANT_ENABLED=true
HOME_ASSISTANT_URL=http://192.168.1.100:8123
USE_PARAMETER_STORE=true
PARAMETER_PREFIX=/lambda-execution-engine

# Maximize METRICS performance
METRICS_FAST_PATH=true          # Enable hot path optimization
MAX_VALUES_PER_METRIC=2000      # More history (requires more memory)
METRICS_ENABLE_STATS=true       # Enable monitoring
```

### Memory-Constrained (128MB Lambda)
```bash
# Minimal memory footprint
HOME_ASSISTANT_ENABLED=true
HOME_ASSISTANT_URL=http://192.168.1.100:8123
HOME_ASSISTANT_TOKEN=eyJ0eXAiOiJKV1Qi...

# Reduce METRICS memory usage
CONFIGURATION_TIER=minimum
MAX_VALUES_PER_METRIC=500       # Reduce metric history
METRICS_FAST_PATH=true          # Keep fast path (minimal overhead)
```

### Secure (Token in SSM)
```bash
# Lambda environment
HOME_ASSISTANT_ENABLED=true
HOME_ASSISTANT_URL=http://192.168.1.100:8123
HOME_ASSISTANT_TIMEOUT=30
HOME_ASSISTANT_VERIFY_SSL=true
USE_PARAMETER_STORE=true
PARAMETER_PREFIX=/lambda-execution-engine

# METRICS optimization (optional)
METRICS_FAST_PATH=true
MAX_VALUES_PER_METRIC=1000
METRICS_ENABLE_STATS=false

# SSM parameter (create separately)
# /lambda-execution-engine/home_assistant/token (SecureString)
```

### Emergency Failsafe
```bash
LAMBDA_MODE=failsafe           # Bypass LEE, direct HA passthrough
HOME_ASSISTANT_URL=http://192.168.1.100:8123
HOME_ASSISTANT_TOKEN=eyJ0eXAiOiJKV1Qi...
HOME_ASSISTANT_VERIFY_SSL=false
DEBUG_MODE=true
```

### Development with Debug
```bash
ENVIRONMENT=development
DEBUG_MODE=true
DEBUG_TIMINGS=true
LOG_LEVEL=DEBUG
CONFIGURATION_TIER=standard
HOME_ASSISTANT_ENABLED=true
HOME_ASSISTANT_URL=http://192.168.1.100:8123
HOME_ASSISTANT_TOKEN=your_token
HA_FEATURES=development

# METRICS development settings
METRICS_FAST_PATH=false        # Disable fast path for testing
MAX_VALUES_PER_METRIC=500      # Smaller history for dev
METRICS_ENABLE_STATS=true      # Enable monitoring
```

### Production (High Reliability)
```bash
ENVIRONMENT=production
LOG_LEVEL=INFO
DEBUG_MODE=false
DEBUG_TIMINGS=false
CONFIGURATION_TIER=maximum
USE_PARAMETER_STORE=true
PARAMETER_PREFIX=/lambda-prod
HOME_ASSISTANT_ENABLED=true
HOME_ASSISTANT_URL=https://ha.example.com
HOME_ASSISTANT_VERIFY_SSL=true

# METRICS production optimization
METRICS_FAST_PATH=true         # Enable fast path
MAX_VALUES_PER_METRIC=1000     # Standard history
METRICS_ENABLE_STATS=true      # Monitor in production

# Token in SSM: /lambda-prod/home_assistant/token
```

---

## Memory Budget by Configuration

Estimated memory overhead for different configurations (128MB Lambda):

### Minimal Configuration
```bash
CONFIGURATION_TIER=minimum
HOME_ASSISTANT_ENABLED=true
HA_WEBSOCKET_ENABLED=false
MAX_VALUES_PER_METRIC=500      # Reduced for low memory
```
**Overhead:** ~15-20MB  
**Available:** ~108-113MB

### Standard Configuration
```bash
CONFIGURATION_TIER=standard
HOME_ASSISTANT_ENABLED=true
HA_WEBSOCKET_ENABLED=false
MAX_VALUES_PER_METRIC=1000     # Default
METRICS_FAST_PATH=true         # Minimal overhead
```
**Overhead:** ~20-25MB  
**Available:** ~103-108MB

### Maximum Configuration
```bash
CONFIGURATION_TIER=maximum
HOME_ASSISTANT_ENABLED=true
HA_WEBSOCKET_ENABLED=true
MAX_VALUES_PER_METRIC=2000     # Increased history
METRICS_ENABLE_STATS=true      # Stats tracking
```
**Overhead:** ~30-35MB  
**Available:** ~93-98MB

### Failsafe Mode
```bash
LAMBDA_MODE=failsafe
```
**Overhead:** ~5-8MB  
**Available:** ~120-123MB  
**Note:** METRICS optimization variables ignored in failsafe mode

---

## Troubleshooting

### Issue: Configuration Not Loading

**Check:**
1. Variable names are EXACT (case-sensitive)
2. Boolean values are lowercase: `true`/`false`
3. If using SSM: parameter path matches `PARAMETER_PREFIX`
4. If using SSM: IAM policy grants `ssm:GetParameter`
5. If using SSM: parameter exists in correct region

### Issue: Failsafe Not Activating

**Check:**
1. Variable is exactly: `LAMBDA_MODE=failsafe` (lowercase)
2. Not `LEE_FAILSAFE_ENABLED` (deprecated, removed)
3. `lambda_failsafe.py` exists in deployment package
4. Check CloudWatch logs for activation message

### Issue: METRICS Performance Issues

**Check METRICS_FAST_PATH:**
```bash
DEBUG_MODE=true
DEBUG_TIMINGS=true
```

**Look for in CloudWatch:**
```
[METRICS_DEBUG] Fast path hit: metric_name
[METRICS_DEBUG] Validation path: metric_name (first access)
[METRICS_TIMING] Fast path operation: 5μs
[METRICS_TIMING] Validation path operation: 15μs
```

**Solutions:**
1. Verify `METRICS_FAST_PATH=true` (should be default)
2. Check hot metric promotion (50 calls threshold)
3. Increase `MAX_VALUES_PER_METRIC` if evicting too frequently
4. Enable `METRICS_ENABLE_STATS=true` to diagnose

### Issue: Memory Exhaustion

**Check MAX_VALUES_PER_METRIC:**
```bash
# Enable stats to see memory usage
METRICS_ENABLE_STATS=true
DEBUG_MODE=true
```

**CloudWatch Output:**
```
[METRICS_STATS] Total metrics: 15,000
[METRICS_STATS] Total values: 15,000,000 (15M)
[METRICS_STATS] Estimated memory: 240MB
[METRICS_STATS] Evictions triggered: 12,500
```

**Solutions:**
1. Reduce `MAX_VALUES_PER_METRIC` (e.g., 1000 → 500)
2. Increase Lambda memory allocation
3. Review metric usage patterns
4. Consider metric aggregation

### Issue: Token Not Loading

**Enable debug to diagnose:**
```bash
DEBUG_MODE=true
DEBUG_TIMINGS=true
```

**Check CloudWatch logs for:**
```
[SSM_DEBUG] Attempting SSM token retrieval
[SSM_TIMING] SSM token retrieval: XXms, success=true/false
[HA_CONFIG_DEBUG] Token retrieved from SSM/environment
```

**Solutions:**
1. Verify SSM parameter exists: `aws ssm get-parameter --name /path/to/token`
2. Check IAM permissions for Lambda execution role
3. Verify `USE_PARAMETER_STORE=true` set correctly
4. Fallback to environment: Set `HOME_ASSISTANT_TOKEN` temporarily

### Issue: Debug Output Not Appearing

**Check:**
```bash
# Verify variables set
aws lambda get-function-configuration --function-name <name> \
  | jq '.Environment.Variables | {DEBUG_MODE, DEBUG_TIMINGS}'

# Check CloudWatch log group exists
aws logs describe-log-groups --log-group-name-prefix /aws/lambda/

# Verify IAM permissions for CloudWatch Logs
```

---

## Best Practices

### Security
- ✅ Use SSM SecureString for token (encrypted at rest)
- ✅ Enable `HOME_ASSISTANT_VERIFY_SSL=true` in production
- ✅ Use different `PARAMETER_PREFIX` per environment
- ❌ Never commit tokens to version control
- ✅ Rotate tokens regularly
- ✅ Restrict IAM permissions to token path only

### Performance
- ✅ Use `CONFIGURATION_TIER=standard` for most cases
- ✅ Keep `METRICS_FAST_PATH=true` (default) for performance
- ✅ Use `MAX_VALUES_PER_METRIC=1000` (default) for balanced memory/history
- ✅ Disable unused features (websocket if not needed)
- ❌ Avoid `DEBUG_MODE=true` in production (log volume)
- ✅ Token caching automatic (300s TTL)
- ✅ Monitor cold start times with `DEBUG_TIMINGS`

### METRICS Optimization (NEW)
- ✅ Leave `METRICS_FAST_PATH=true` (30-50% faster, minimal risk)
- ✅ Adjust `MAX_VALUES_PER_METRIC` based on Lambda memory
- ✅ Enable `METRICS_ENABLE_STATS=true` for production monitoring
- ❌ Don't set `MAX_VALUES_PER_METRIC` too high (memory exhaustion risk)
- ✅ Monitor eviction rates with stats enabled
- ✅ Test metric memory usage in staging first

### Reliability
- ✅ Configure failsafe mode for emergencies (`LAMBDA_MODE=failsafe`)
- ✅ Enable circuit breaker protection (tier >= standard)
- ✅ Set appropriate timeouts for your network
- ✅ Monitor CloudWatch logs regularly
- ✅ Test failsafe activation periodically
- ✅ Monitor METRICS memory usage with stats

### Cost Optimization
- ✅ Minimize log volume (disable debug in production)
- ✅ SSM token caching reduces API calls (automatic)
- ✅ Use short CloudWatch log retention (7 days for debug)
- ✅ Monitor Lambda invocation count
- ✅ Consider reserved concurrency for predictable costs
- ✅ METRICS optimization reduces memory costs (bounded growth)

---

## Migration Notes

### From Old Configuration

**If you have:**
```bash
LEE_FAILSAFE_ENABLED=true  # ❌ No longer works (removed)
USE_PARAMETER_STORE=true
# Multiple SSM parameters for URL, timeout, etc.
```

**Update to:**
```bash
LAMBDA_MODE=failsafe  # ✅ New variable
USE_PARAMETER_STORE=true  # ✅ Token only now
HOME_ASSISTANT_URL=http://...  # ✅ Now in environment
HOME_ASSISTANT_TIMEOUT=30  # ✅ Now in environment
# ... all other config in environment ...

# SSM: Only /path/to/token remains
```

### New in v2025.10.22

**METRICS optimization variables are all optional:**
```bash
# These all have sensible defaults, only set if customization needed:
METRICS_FAST_PATH=true          # Default - no need to set
MAX_VALUES_PER_METRIC=1000      # Default - no need to set
METRICS_ENABLE_STATS=false      # Default - set true for monitoring
```

**Benefits of v2025.10.22:**
- 30-50% faster metrics operations (fast path)
- Protection against memory exhaustion (bounded storage)
- Better observability (stats tracking)
- Zero breaking changes

---

## Notes

- `LAMBDA_MODE` replaces deprecated `LEE_FAILSAFE_ENABLED` (removed)
- Default `LAMBDA_MODE` is `normal` - no need to set explicitly
- SSM now stores ONLY the token (all other config in environment)
- Debug modes add <1ms overhead but increase log volume significantly
- Boolean values: use lowercase `true`/`false` not `True`/`False`
- SSM token cached for 300 seconds (5 minutes)
- Failsafe mode bypasses ALL LEE infrastructure
- Toggle failsafe without code changes or redeployment
- Circuit breaker configuration is tier-based, not per-variable
- **NEW:** METRICS optimization variables provide 30-50% performance improvement
- **NEW:** Bounded metric storage prevents memory exhaustion attacks
- **NEW:** METRICS stats enable production monitoring and capacity planning

---

# EOF
