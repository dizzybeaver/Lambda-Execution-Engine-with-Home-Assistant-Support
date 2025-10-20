# Lambda Environment Variables and SSM Parameters Reference
**Version:** 2025.10.20.01  
**Updated:** SSM now token-only, LAMBDA_MODE replaces LEE_FAILSAFE_ENABLED

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

**NEW:** Replaces deprecated `LEE_FAILSAFE_ENABLED`

```bash
LAMBDA_MODE=normal      # Default - Full LEE operation
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

**Default:** If not set, defaults to `normal`

---

## Core Lambda Configuration

### System Settings

| Variable | Type | Values | Description |
|----------|------|--------|-------------|
| `ENVIRONMENT` | String | `development`/`staging`/`production` | Deployment environment |
| `LOG_LEVEL` | String | `DEBUG`/`INFO`/`WARNING`/`ERROR`/`CRITICAL` | CloudWatch logging verbosity |
| `CONFIGURATION_TIER` | String | `minimum`/`standard`/`maximum`/`user` | Circuit breaker tier |

### Debug Settings (NEW)

| Variable | Type | Values | Description |
|----------|------|--------|-------------|
| `DEBUG_MODE` | Boolean | `true`/`false` | Enable debug statements |
| `DEBUG_TIMINGS` | Boolean | `true`/`false` | Enable timing measurements |

**Debug Output:**
- `DEBUG_MODE=true` → Shows execution flow, routing decisions, configuration loading
- `DEBUG_TIMINGS=true` → Shows performance measurements with millisecond precision
- Both can be enabled simultaneously for comprehensive diagnostics

**Cost Impact:**
- `DEBUG_MODE`: 3-5x log volume increase (~$0.50-$1.00 per million requests)
- `DEBUG_TIMINGS`: 2-3x log volume increase (~$0.30-$0.60 per million requests)
- **Recommendation:** Enable only for troubleshooting, disable immediately after

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

## SSM Parameter Store Configuration (SIMPLIFIED)

### Enabling SSM

```bash
USE_PARAMETER_STORE=true
PARAMETER_PREFIX=/lambda-execution-engine
```

### CRITICAL CHANGE: Token Only

**SSM now stores ONLY the Home Assistant token.**

**SSM Parameter:**
```
/lambda-execution-engine/home_assistant/token (SecureString)
```

**All other configuration MUST be in Lambda environment variables:**
- URL, timeout, verify_ssl, assistant_name, features, websocket settings
- Log level, environment, debug mode, configuration tier
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

### Secure (Token in SSM)
```bash
# Lambda environment
HOME_ASSISTANT_ENABLED=true
HOME_ASSISTANT_URL=http://192.168.1.100:8123
HOME_ASSISTANT_TIMEOUT=30
HOME_ASSISTANT_VERIFY_SSL=true
USE_PARAMETER_STORE=true
PARAMETER_PREFIX=/lambda-execution-engine

# SSM parameter (create separately)
/lambda-execution-engine/home_assistant/token (SecureString)
```

### Emergency Failsafe
```bash
LAMBDA_MODE=failsafe
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
```
**Overhead:** ~15-20MB  
**Available:** ~108-113MB

### Standard Configuration
```bash
CONFIGURATION_TIER=standard
HOME_ASSISTANT_ENABLED=true
HA_WEBSOCKET_ENABLED=false
```
**Overhead:** ~20-25MB  
**Available:** ~103-108MB

### Maximum Configuration
```bash
CONFIGURATION_TIER=maximum
HOME_ASSISTANT_ENABLED=true
HA_WEBSOCKET_ENABLED=true
```
**Overhead:** ~30-35MB  
**Available:** ~93-98MB

### Failsafe Mode
```bash
LAMBDA_MODE=failsafe
```
**Overhead:** ~5-8MB  
**Available:** ~120-123MB

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
2. Not `LEE_FAILSAFE_ENABLED` (deprecated, no longer works)
3. `lambda_failsafe.py` exists in deployment package
4. Check CloudWatch logs for activation message

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
- ✅ Disable unused features (websocket if not needed)
- ❌ Avoid `DEBUG_MODE=true` in production (log volume)
- ✅ Token caching automatic (300s TTL)
- ✅ Monitor cold start times with `DEBUG_TIMINGS`

### Reliability
- ✅ Configure failsafe mode for emergencies (`LAMBDA_MODE=failsafe`)
- ✅ Enable circuit breaker protection (tier >= standard)
- ✅ Set appropriate timeouts for your network
- ✅ Monitor CloudWatch logs regularly
- ✅ Test failsafe activation periodically

### Cost Optimization
- ✅ Minimize log volume (disable debug in production)
- ✅ SSM token caching reduces API calls (automatic)
- ✅ Use short CloudWatch log retention (7 days for debug)
- ✅ Monitor Lambda invocation count
- ✅ Consider reserved concurrency for predictable costs

---

## Migration Notes

### From Old Configuration

**If you have:**
```bash
LEE_FAILSAFE_ENABLED=true  # ❌ No longer works
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

**See:** `MIGRATION GUIDE - SSM Simplification (Token Only).md`

---

## Notes

- `LAMBDA_MODE` replaces deprecated `LEE_FAILSAFE_ENABLED`
- SSM now stores ONLY the token (all other config in environment)
- Debug modes add <1ms overhead but increase log volume significantly
- Boolean values: use lowercase `true`/`false` not `True`/`False`
- SSM token cached for 300 seconds (5 minutes)
- Failsafe mode bypasses ALL LEE infrastructure
- Toggle failsafe without code changes or redeployment
- Circuit breaker configuration is tier-based, not per-variable

---

# EOF
