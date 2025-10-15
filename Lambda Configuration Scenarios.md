# Lambda Configuration Scenarios
**Version:** 2025.10.14  
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
