# Lambda Configuration Scenarios
**Version:** 2025.10.20.01  
**Updated:** SSM token-only, LAMBDA_MODE, DEBUG_MODE/DEBUG_TIMINGS

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

**Note:** Only `ssm:GetParameter` needed for single token parameter.

### Benefits
- ✅ Token encrypted at rest (SecureString)
- ✅ Token encrypted in transit (TLS)
- ✅ Token cached (300s TTL, reduces API calls)
- ✅ All other config visible in Lambda console
- ✅ Fast configuration changes (no SSM updates)

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

### Notes
- No SSM parameters needed
- No additional IAM permissions required
- Token stored as plaintext environment variable (less secure)
- Simpler setup for development/testing
- Configuration changes require Lambda update

### Benefits
- ✅ Simplest configuration
- ✅ No SSM dependencies
- ✅ No IAM complexity
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
     --environment Variables="{LAMBDA_MODE=normal,...}"
   ```

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

---

## Scenario 4: Configuration Tier Optimization

### Purpose
Tune memory allocation and circuit breaker behavior based on deployment requirements.

### Tier Comparison

| Tier | Memory | Protected Services | Failure Threshold | Recovery Time |
|------|--------|-------------------|------------------|---------------|
| `minimum` | ~15MB | None | N/A | N/A |
| `standard` | ~20MB | Critical only | 5 failures | 60s |
| `maximum` | ~30MB | All services | 3 failures | 30s |
| `user` | Variable | Custom | Custom | Custom |

### Minimal Tier (Resource Constrained)
```bash
CONFIGURATION_TIER=minimum
HOME_ASSISTANT_ENABLED=true
HA_WEBSOCKET_ENABLED=false
```
- Lowest memory footprint
- No circuit breaker protection
- Best for: Testing, development, tight memory constraints

### Standard Tier (Production Recommended)
```bash
CONFIGURATION_TIER=standard
HOME_ASSISTANT_ENABLED=true
HA_WEBSOCKET_ENABLED=false
```
- Balanced memory and protection
- Circuit breakers on critical services
- Best for: Most production deployments

### Maximum Tier (High Reliability)
```bash
CONFIGURATION_TIER=maximum
HOME_ASSISTANT_ENABLED=true
HA_WEBSOCKET_ENABLED=true
```
- Maximum circuit breaker protection
- All services protected
- Fastest recovery
- Best for: Mission-critical deployments

---

## Scenario 5: Debug Mode with Diagnostics

### Purpose
Enable enhanced logging and diagnostic tools for troubleshooting.

### Lambda Environment Variables

```bash
# Debug settings (NEW)
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

**DEBUG_TIMINGS=true:**
- Cold start timing breakdown
- Module import durations
- SSM API call latency
- Cache operation performance
- HTTP request/response times
- Gateway dispatch overhead
- Total operation duration
- Step-by-step timing within operations

**CloudWatch Output Examples:**
```
[SSM_DEBUG] Retrieving Home Assistant token from SSM
[SSM_TIMING] SSM token retrieval: 250ms, success=true
[HA_CONFIG_DEBUG] Loading HA config (force_refresh=false)
[HA_CONFIG_TIMING] Config built: 300ms
[CACHE_DEBUG] cache_get: key=ha_config, hit=True
[GATEWAY_DEBUG] execute_operation: interface=CACHE, operation=get
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
Maximum resilience for critical production deployments.

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

**Reliability:**
- Circuit breakers trip at 3 failures
- 30-second recovery windows
- Automatic healing
- Failsafe fallback available

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
```

---

## Scenario 7: Multi-Environment Setup

### Purpose
Separate configurations for development, staging, and production.

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

---

## Quick Reference Table

| Scenario | Memory | Latency | SSM | Debug | Use Case |
|----------|--------|---------|-----|-------|----------|
| SSM Token Only | ~67MB | ~150ms | Token only | Off | Recommended production |
| Environment Only | ~67MB | ~150ms | None | Off | Simple deployment |
| Failsafe | ~42MB | ~50ms | Optional | Optional | Emergency recovery |
| Minimum Tier | ~50MB | ~120ms | Optional | Off | Resource constrained |
| Standard Tier | ~67MB | ~150ms | Recommended | Off | Normal production |
| Maximum Tier | ~85MB | ~180ms | Recommended | Off | High reliability |
| Debug Mode | ~70MB | ~160ms | Optional | On | Troubleshooting |
| High Reliability | ~85MB | ~180ms | Required | Off | Mission critical |

---

## Migration from Old Configuration

### If You Have LEE_FAILSAFE_ENABLED

**OLD (No longer works):**
```bash
LEE_FAILSAFE_ENABLED=true  # ❌ Deprecated
```

**NEW (Use this):**
```bash
LAMBDA_MODE=failsafe  # ✅ Current
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

**See:** `MIGRATION GUIDE - SSM Simplification (Token Only).md`

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

| Configuration | Response Time |
|---------------|---------------|
| Failsafe | ~50ms |
| All Tiers (Token cached) | ~100-150ms |
| With Debug | ~160ms |

---

## Related Documentation

- **Debug System:** `REMINDER - Debug Trapping and Performance Analysis.md`
- **SSM Migration:** `MIGRATION GUIDE - SSM Simplification (Token Only).md`
- **Variable Reference:** `Lambda Environment Variables and SSM Parameters Reference.md`
- **LAMBDA_MODE Change:** `BREAKING CHANGE - LEE_FAILSAFE_ENABLED to LAMBDA_MODE.md`

---

# EOF
