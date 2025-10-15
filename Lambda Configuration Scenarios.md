# Lambda Configuration Scenarios
**Version:** 2025.10.15  
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
- ✅ Zero LEE dependencies - completely standalone
- ✅ Direct passthrough to Home Assistant
- ✅ All Alexa directive types supported
- ✅ Minimal latency (no SUGA overhead)
- ✅ Works with existing HA Alexa integration

### Limitations
- ❌ No LEE features (caching, metrics, circuit breaker)
- ❌ No custom intents/automations
- ❌ No enhanced logging/diagnostics
- ❌ Basic error handling only

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
