# Lambda Environment Variables & SSM Parameters Reference
**Version:** 2025.10.14  
**Copyright:** 2025 Joseph Hersey  
**License:** Apache 2.0

---

## Lambda Core Environment Variables

### AWS-Managed Variables (Read-Only)

| Variable | Description |
|----------|-------------|
| `AWS_REGION` | AWS region for Lambda execution (cannot be overridden) |
| `AWS_LAMBDA_FUNCTION_NAME` | Lambda function name |
| `AWS_LAMBDA_FUNCTION_MEMORY_SIZE` | Allocated memory in MB |
| `AWS_EXECUTION_ENV` | Python runtime version |

### User-Configurable Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `LOG_LEVEL` | String | `INFO` | Logging verbosity: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` |
| `ENVIRONMENT` | String | `production` | Deployment environment: `development`, `staging`, `production` |
| `DEBUG_MODE` | Boolean | `false` | Enable detailed debugging output and stack traces |

---

## Configuration System Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `CONFIGURATION_TIER` | String | `standard` | Base tier: `minimum`, `standard`, `maximum`, `user` |
| `USE_PARAMETER_STORE` | Boolean | `false` | Enable AWS SSM Parameter Store for configuration |
| `PARAMETER_PREFIX` | String | `/lambda-execution-engine` | SSM parameter path prefix |

---

## HomeAssistant Extension Variables

### Required (if extension enabled)

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `HOME_ASSISTANT_ENABLED` | Boolean | `false` | Master switch to enable/disable HomeAssistant extension |
| `HOME_ASSISTANT_URL` | String | None | Base URL of Home Assistant instance (http://host:port) |
| `HOME_ASSISTANT_TOKEN` | String | None | Long-lived access token from Home Assistant |

### Optional

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `HOME_ASSISTANT_TIMEOUT` | Integer | `30` | HTTP request timeout in seconds |
| `HOME_ASSISTANT_VERIFY_SSL` | Boolean | `true` | Verify SSL certificates for HTTPS connections |
| `HA_ASSISTANT_NAME` | String | `Assistant` | Name used in conversation responses |
| `HA_FEATURES` | String | `basic` | Feature level: `basic`, `standard`, `full`, `development` |
| `HA_WEBSOCKET_ENABLED` | Boolean | `false` | Enable WebSocket for entity registry and filtering |
| `HA_WEBSOCKET_TIMEOUT` | Integer | `10` | WebSocket connection timeout in seconds |

---

## AWS Systems Manager (SSM) Parameter Store

### Enabling Parameter Store

Set these environment variables to enable SSM:
```bash
USE_PARAMETER_STORE=true
PARAMETER_PREFIX=/lambda-execution-engine
```

### SSM Parameter Hierarchy

All parameters use the prefix defined in `PARAMETER_PREFIX` (default: `/lambda-execution-engine/`)

#### Lambda Core Parameters

| Parameter Path | Type | Description |
|----------------|------|-------------|
| `/lambda-execution-engine/log_level` | String | Override LOG_LEVEL environment variable |
| `/lambda-execution-engine/environment` | String | Override ENVIRONMENT environment variable |
| `/lambda-execution-engine/debug_mode` | String | Override DEBUG_MODE environment variable |
| `/lambda-execution-engine/configuration_tier` | String | Override CONFIGURATION_TIER environment variable |

#### HomeAssistant Extension Parameters

| Parameter Path | Type | Description |
|----------------|------|-------------|
| `/lambda-execution-engine/home_assistant/enabled` | String | Override HOME_ASSISTANT_ENABLED |
| `/lambda-execution-engine/home_assistant/url` | String | Override HOME_ASSISTANT_URL |
| `/lambda-execution-engine/home_assistant/token` | SecureString | **Recommended for tokens** - Override HOME_ASSISTANT_TOKEN |
| `/lambda-execution-engine/home_assistant/timeout` | String | Override HOME_ASSISTANT_TIMEOUT |
| `/lambda-execution-engine/home_assistant/verify_ssl` | String | Override HOME_ASSISTANT_VERIFY_SSL |
| `/lambda-execution-engine/home_assistant/assistant_name` | String | Override HA_ASSISTANT_NAME |
| `/lambda-execution-engine/home_assistant/features` | String | Override HA_FEATURES |
| `/lambda-execution-engine/home_assistant/websocket_enabled` | String | Override HA_WEBSOCKET_ENABLED |
| `/lambda-execution-engine/home_assistant/websocket_timeout` | String | Override HA_WEBSOCKET_TIMEOUT |

#### Custom Configuration Parameters

| Parameter Path | Type | Description |
|----------------|------|-------------|
| `/lambda-execution-engine/custom/[key]` | Any | User-defined custom configuration values |

---

## Priority Order

Configuration values are resolved in this order (highest to lowest priority):

1. **Environment Variables** - Set in Lambda console
2. **SSM Parameter Store** - If `USE_PARAMETER_STORE=true`
3. **Default Values** - Hardcoded in application

---

## Quick Setup Examples

### Minimal Setup (Environment Variables Only)
```bash
HOME_ASSISTANT_ENABLED=true
HOME_ASSISTANT_URL=http://192.168.1.100:8123
HOME_ASSISTANT_TOKEN=eyJ0eXAiOiJKV1Qi...
```

### Secure Setup (Using SSM for Token)
```bash
# Environment Variables
HOME_ASSISTANT_ENABLED=true
HOME_ASSISTANT_URL=http://192.168.1.100:8123
USE_PARAMETER_STORE=true
PARAMETER_PREFIX=/lambda/ha

# SSM Parameter (create separately)
aws ssm put-parameter \
  --name "/lambda/ha/home_assistant/token" \
  --value "eyJ0eXAiOiJKV1Qi..." \
  --type "SecureString"
```

### Development Setup
```bash
ENVIRONMENT=development
DEBUG_MODE=true
LOG_LEVEL=DEBUG
CONFIGURATION_TIER=maximum
HOME_ASSISTANT_ENABLED=true
HOME_ASSISTANT_URL=http://192.168.1.100:8123
HOME_ASSISTANT_TOKEN=your_token
HA_FEATURES=development
HA_WEBSOCKET_ENABLED=true
```

### Production Setup
```bash
ENVIRONMENT=production
LOG_LEVEL=INFO
CONFIGURATION_TIER=standard
USE_PARAMETER_STORE=true
PARAMETER_PREFIX=/lambda-prod
# All sensitive values in SSM Parameter Store
```

---

## IAM Permissions for SSM

To use Parameter Store, add this policy to Lambda execution role:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ssm:GetParameter",
        "ssm:GetParameters"
      ],
      "Resource": [
        "arn:aws:ssm:REGION:ACCOUNT:parameter/lambda-execution-engine/*"
      ]
    }
  ]
}
```

Replace `REGION` and `ACCOUNT` with your AWS region and account ID.

---

## Notes

- Environment variables take precedence over SSM parameters
- SSM parameters are cached for 300 seconds to reduce API calls
- Boolean values in SSM must be strings: `"true"` or `"false"`
- Use `SecureString` type in SSM for all tokens and secrets
- Change `PARAMETER_PREFIX` to isolate configurations per environment
