# Lambda Configuration Scenarios
**Version:** 2025.10.18  
**Copyright:** 2025 Joseph Hersey  
**License:** Apache 2.0

---

## Scenario 1: Using SSM Parameter Store (Recommended for Production)

### Lambda Environment Variables

| Variable | Value |
|----------|-------|
| `USE_PARAMETER_STORE` | `true` |
| `PARAMETER_PREFIX` | `/lambda-execution-engine` |
| `HOME_ASSISTANT_ENABLED` | `true` |

### SSM Parameters to Create

| Parameter Path | Type | Example Value |
|----------------|------|---------------|
| `/lambda-execution-engine/log_level` | String | `INFO` |
| `/lambda-execution-engine/environment` | String | `production` |
| `/lambda-execution-engine/configuration_tier` | String | `standard` |
| `/lambda-execution-engine/home_assistant/url` | String | `http://192.168.1.100:8123` |
| `/lambda-execution-engine/home_assistant/token` | **SecureString** | `eyJ0eXAiOiJKV1Qi...` |
| `/lambda-execution-engine/home_assistant/timeout` | String | `30` |
| `/lambda-execution-engine/home_assistant/verify_ssl` | String | `true` |
| `/lambda-execution-engine/home_assistant/assistant_name` | String | `Jarvis` |
| `/lambda-execution-engine/home_assistant/features` | String | `full` |
| `/lambda-execution-engine/home_assistant/websocket_enabled` | String | `false` |
| `/lambda-execution-engine/home_assistant/websocket_timeout` | String | `10` |

### IAM Policy Required

```json
{
  "Effect": "Allow",
  "Action": ["ssm:GetParameter"],
  "Resource": "arn:aws:ssm:REGION:ACCOUNT:parameter/lambda-execution-engine/*"
}
```

---

## Scenario 2: Using Environment Variables Only (Simple Deployment)

### Lambda Environment Variables

| Variable | Value |
|----------|-------|
| `LOG_LEVEL` | `INFO` |
| `ENVIRONMENT` | `production` |
| `DEBUG_MODE` | `false` |
| `CONFIGURATION_TIER` | `standard` |
| `HOME_ASSISTANT_ENABLED` | `true` |
| `HOME_ASSISTANT_URL` | `http://192.168.1.100:8123` |
| `HOME_ASSISTANT_TOKEN` | `eyJ0eXAiOiJKV1Qi...` |
| `HOME_ASSISTANT_TIMEOUT` | `30` |
| `HOME_ASSISTANT_VERIFY_SSL` | `true` |
| `HA_ASSISTANT_NAME` | `Jarvis` |
| `HA_FEATURES` | `full` |
| `HA_WEBSOCKET_ENABLED` | `false` |
| `HA_WEBSOCKET_TIMEOUT` | `10` |

### Notes

- No SSM parameters needed
- No additional IAM permissions required
- Tokens stored as plaintext environment variables (less secure)
- Simpler setup for development/testing
- AWS_REGION is auto-set by AWS Lambda (cannot be overridden)

---

## Scenario 3: Fail-Safe Mode (Emergency Recovery)

### Purpose
Emergency fallback when Lambda Execution Engine fails. Bypasses all LEE/SUGA architecture and routes requests directly to Home Assistant's native Alexa Smart Home API.

### When to Use
- LEE crashes after deployment
- Critical bugs preventing normal operation
- Need immediate restoration while debugging
- Family needs smart home working NOW

### Lambda Environment Variables

| Variable | Value | Notes |
|----------|-------|-------|
| `LEE_FAILSAFE_ENABLED` | `true` | **Master switch** - enables failsafe mode |
| `HOME_ASSISTANT_URL` | `http://192.168.1.100:8123` | Base URL of HA instance |
| `HOME_ASSISTANT_TOKEN` | `eyJ0eXAiOiJKV1Qi...` | Long-lived access token |
| `HOME_ASSISTANT_VERIFY_SSL` | `false` | Optional - disable SSL verification |
| `DEBUG_MODE` | `true` | Optional - enable verbose logging |

### Minimal Configuration (Copy-Paste)
```bash
LEE_FAILSAFE_ENABLED=true
HOME_ASSISTANT_URL=http://192.168.1.100:8123
HOME_ASSISTANT_TOKEN=eyJ0eXAiOiJKV1Qi...
HOME_ASSISTANT_VERIFY_SSL=false
```

### Features
- [YES] Zero LEE dependencies - completely standalone
- [YES] Direct passthrough to Home Assistant
- [YES] All Alexa directive types supported
- [YES] Minimal latency (no SUGA overhead)
- [YES] Works with existing HA Alexa integration

### Limitations
- [NO] No LEE features (caching, metrics, circuit breaker)
- [NO] No custom intents/automations
- [NO] No enhanced logging/diagnostics
- [NO] Basic error handling only

### Recovery Process

1. **Enable Failsafe**
   ```bash
   # Set in Lambda console
   LEE_FAILSAFE_ENABLED=true
   HOME_ASSISTANT_URL=http://your-ha-ip:8123
   HOME_ASSISTANT_TOKEN=your_token
   ```

2. **Verify Operation**
   - Test Alexa commands
   - Check CloudWatch logs
   - Confirm family is happy

3. **Debug LEE**
   - Review CloudWatch logs
   - Identify root cause
   - Apply fixes

4. **Restore Normal Operation**
   ```bash
   # After fixing LEE
   LEE_FAILSAFE_ENABLED=false
   ```

5. **Redeploy**
   - Upload fixed Lambda package
   - Test thoroughly
   - Monitor for issues

### Notes
- Failsafe activates **before** any LEE imports
- If failsafe file missing, falls back to LEE
- Original HA configuration unaffected
- No changes to Alexa skill required
- Can toggle on/off without code changes

---

## Scenario 4: Configuration Tier Optimization

### Purpose
Tune memory allocation and circuit breaker behavior based on deployment requirements.

### Configuration Tier Levels

#### MINIMUM (128MB Lambda, Conservative)
**Best for:** Development, testing, tight memory constraints

```bash
CONFIGURATION_TIER=minimum
```

**Circuit Breaker Settings:**
- CloudWatch API: 3 failures, 60s timeout
- Home Assistant: 2 failures, 30s timeout
- External HTTP: Not configured (tier too low)
- Memory: 0.5MB circuit breaker overhead

**Characteristics:**
- Minimal memory footprint
- Conservative failure thresholds
- Longer recovery times
- Basic service coverage only

#### STANDARD (128MB Lambda, Balanced) **[RECOMMENDED]**
**Best for:** Production deployments, balanced performance

```bash
CONFIGURATION_TIER=standard
```

**Circuit Breaker Settings:**
- CloudWatch API: 3 failures, 45s timeout, 2 test calls
- Home Assistant: 2 failures, 20s timeout, 1 test call
- External HTTP: 3 failures, 30s timeout, 2 test calls
- Memory: 2MB circuit breaker overhead

**Characteristics:**
- Balanced memory vs reliability
- Moderate failure thresholds
- Faster recovery
- All common services protected

#### MAXIMUM (128MB Lambda, Aggressive)
**Best for:** High-reliability requirements, can spare memory

```bash
CONFIGURATION_TIER=maximum
```

**Circuit Breaker Settings:**
- CloudWatch API: 3 failures, 45s timeout, 2 test calls
- Home Assistant: 2 failures, 20s timeout, 1 test call
- External HTTP: 3 failures, 30s timeout, 2 test calls
- Database: 2 failures, 60s timeout, 1 test call
- Custom Services: 3 failures, 30s timeout, 2 test calls
- Memory: 6MB circuit breaker overhead

**Characteristics:**
- Maximum protection coverage
- Shortest recovery windows
- All services protected
- Highest memory usage

#### USER (Custom Configuration)
**Best for:** Custom tuning via user_config.py

```bash
CONFIGURATION_TIER=user
```

**Characteristics:**
- Full control over all parameters
- Define custom service thresholds
- Adjust memory allocations
- Requires modifying user_config.py

### Tier Selection Guide

| Scenario | Recommended Tier | Rationale |
|----------|------------------|-----------|
| Development/Testing | `minimum` | Low memory, basic features |
| Production (normal) | `standard` | Best balance, proven reliable |
| High-traffic production | `maximum` | Maximum protection, faster recovery |
| Custom requirements | `user` | Full control, requires coding |

### Memory Impact (128MB Lambda)

| Tier | Circuit Breaker | Available for Code | % Overhead |
|------|----------------|-------------------|------------|
| `minimum` | 0.5MB | 127.5MB | 0.4% |
| `standard` | 2.0MB | 126.0MB | 1.6% |
| `maximum` | 6.0MB | 122.0MB | 4.7% |

**Note:** These are circuit breaker allocations only. Total LEE overhead includes caching, metrics, logging, etc.

---

## Scenario 5: Debug Mode with Diagnostics

### Purpose
Enable enhanced logging and diagnostic tools for troubleshooting.

### Lambda Environment Variables

```bash
DEBUG_MODE=true
LOG_LEVEL=DEBUG
ENVIRONMENT=development
CONFIGURATION_TIER=standard
HOME_ASSISTANT_ENABLED=true
HOME_ASSISTANT_URL=http://192.168.1.100:8123
HOME_ASSISTANT_TOKEN=eyJ0eXAiOiJKV1Qi...
```

### What Debug Mode Enables

**Enhanced Logging:**
- Full request/response bodies logged
- Gateway operation routing details
- Circuit breaker state transitions
- WebSocket connection lifecycle
- Timing metrics for all operations

**CloudWatch Insights:**
```
# Find slow operations
fields @timestamp, message
| filter message like /duration_ms/
| filter duration_ms > 1000
| sort duration_ms desc

# Track circuit breaker trips
fields @timestamp, message
| filter message like /OPEN/
| stats count() by service_name
```

**Diagnostic Helpers:**
- `Lambda_diagnostics.py` - Bypass Lambda_function.py for isolated testing
- `Lambda_emergency.py` - Test emergency scenarios

### When to Use
- Investigating performance issues
- Debugging integration failures
- Analyzing circuit breaker behavior
- Troubleshooting WebSocket connections

### Warning
Debug mode generates significant CloudWatch logs. Disable after troubleshooting to avoid:
- Excessive CloudWatch costs
- Log storage quota issues
- Performance degradation from I/O

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
CONFIGURATION_TIER=maximum

# SSM Parameter Store
USE_PARAMETER_STORE=true
PARAMETER_PREFIX=/lambda-prod

# Home Assistant
HOME_ASSISTANT_ENABLED=true
```

### SSM Parameters (All SecureString where applicable)

```bash
# Core
/lambda-prod/log_level=INFO
/lambda-prod/environment=production
/lambda-prod/configuration_tier=maximum

# Home Assistant
/lambda-prod/home_assistant/enabled=true
/lambda-prod/home_assistant/url=https://ha.example.com
/lambda-prod/home_assistant/token=<SecureString>
/lambda-prod/home_assistant/timeout=30
/lambda-prod/home_assistant/verify_ssl=true
/lambda-prod/home_assistant/assistant_name=Jarvis
/lambda-prod/home_assistant/features=full
/lambda-prod/home_assistant/websocket_enabled=false
/lambda-prod/home_assistant/websocket_timeout=10
```

### Architecture Benefits

**Circuit Breaker Protection:**
- Prevents cascade failures
- Automatic service isolation
- Self-healing recovery
- All services protected (max tier)

**Security:**
- Tokens in SSM SecureString
- SSL verification enabled
- Audit trail via CloudWatch
- No plaintext credentials

**Monitoring:**
- Structured CloudWatch logs
- Circuit breaker metrics
- Operation timing data
- Error rate tracking

### Production Checklist

```
[ ] SSM parameters created with SecureString
[ ] IAM policy grants ssm:GetParameter
[ ] CONFIGURATION_TIER=maximum
[ ] HOME_ASSISTANT_VERIFY_SSL=true
[ ] DEBUG_MODE=false
[ ] CloudWatch alarms configured
[ ] Tested failover scenarios
[ ] LEE_FAILSAFE_ENABLED=false (confirm)
[ ] Lambda reserved concurrency set
[ ] CloudWatch log retention configured
```

---

## Quick Copy-Paste Configurations

### SSM Enabled (Environment Variables)
```bash
USE_PARAMETER_STORE=true
PARAMETER_PREFIX=/lambda-execution-engine
HOME_ASSISTANT_ENABLED=true
```

### SSM Disabled (All Environment Variables)
```bash
LOG_LEVEL=INFO
ENVIRONMENT=production
DEBUG_MODE=false
CONFIGURATION_TIER=standard
HOME_ASSISTANT_ENABLED=true
HOME_ASSISTANT_URL=http://192.168.1.100:8123
HOME_ASSISTANT_TOKEN=eyJ0eXAiOiJKV1Qi...
HOME_ASSISTANT_TIMEOUT=30
HOME_ASSISTANT_VERIFY_SSL=true
HA_ASSISTANT_NAME=Jarvis
HA_FEATURES=full
HA_WEBSOCKET_ENABLED=false
HA_WEBSOCKET_TIMEOUT=10
```

### Emergency Failsafe (Minimal)
```bash
LEE_FAILSAFE_ENABLED=true
HOME_ASSISTANT_URL=http://192.168.1.100:8123
HOME_ASSISTANT_TOKEN=eyJ0eXAiOiJKV1Qi...
HOME_ASSISTANT_VERIFY_SSL=false
DEBUG_MODE=true
```

### Debug/Development
```bash
LOG_LEVEL=DEBUG
ENVIRONMENT=development
DEBUG_MODE=true
CONFIGURATION_TIER=standard
HOME_ASSISTANT_ENABLED=true
HOME_ASSISTANT_URL=http://192.168.1.100:8123
HOME_ASSISTANT_TOKEN=eyJ0eXAiOiJKV1Qi...
HA_FEATURES=development
HA_WEBSOCKET_ENABLED=true
```

---

## Configuration Tier Comparison Matrix

| Feature | MINIMUM | STANDARD | MAXIMUM | USER |
|---------|---------|----------|---------|------|
| Circuit Breaker Memory | 0.5MB | 2.0MB | 6.0MB | Custom |
| Services Protected | 2 | 3 | 5 | Custom |
| Failure Threshold | 3 | 2-3 | 2-3 | Custom |
| Recovery Timeout | 30-60s | 20-45s | 20-60s | Custom |
| Best For | Dev/Test | Production | High-Reliability | Advanced |

---

## Troubleshooting Common Issues

### Issue: Circuit Breaker Tripping Frequently
**Symptoms:** Logs show repeated OPEN state

**Solutions:**
1. Increase CONFIGURATION_TIER (minimum -> standard -> maximum)
2. Check Home Assistant availability
3. Review network connectivity
4. Verify timeout values aren't too aggressive

### Issue: High Memory Usage
**Symptoms:** Lambda approaching 128MB limit

**Solutions:**
1. Decrease CONFIGURATION_TIER (maximum -> standard -> minimum)
2. Disable unnecessary features (websocket_enabled=false)
3. Review cache settings
4. Consider increasing Lambda memory allocation

### Issue: Slow Response Times
**Symptoms:** Alexa delays, timeout errors

**Solutions:**
1. Enable DEBUG_MODE to find bottlenecks
2. Check circuit breaker states
3. Review Home Assistant response times
4. Consider increasing timeout values

### Issue: Failsafe Not Activating
**Symptoms:** LEE_FAILSAFE_ENABLED=true but LEE still running

**Solutions:**
1. Verify lambda_failsafe.py exists in deployment package
2. Check Lambda environment variable is exact: LEE_FAILSAFE_ENABLED
3. Value must be exact string: true (lowercase)
4. Redeploy Lambda function
