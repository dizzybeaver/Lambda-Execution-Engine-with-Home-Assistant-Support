# Lambda Environment Variables & SSM Parameters Reference
**Version:** 2025.10.18  
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

## Emergency Failsafe Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `LEE_FAILSAFE_ENABLED` | Boolean | `false` | **Master switch** - Bypasses entire LEE/SUGA and routes directly to Home Assistant |

### Failsafe Behavior

When `LEE_FAILSAFE_ENABLED=true`:
- **Activates before any LEE imports** - checked first in `lambda_handler()`
- Routes all requests to standalone `lambda_failsafe.py`
- Uses only these variables:
  - `HOME_ASSISTANT_URL` (required)
  - `HOME_ASSISTANT_TOKEN` (required)
  - `HOME_ASSISTANT_VERIFY_SSL` (optional)
  - `DEBUG_MODE` (optional)
- Ignores all other LEE/extension configuration
- Falls back to normal LEE if failsafe file missing

### Use Cases
- Emergency recovery after failed deployment
- Critical bugs preventing LEE operation
- Immediate restoration while debugging
- Temporary bypass for troubleshooting

### Recovery
```bash
# Enable failsafe
LEE_FAILSAFE_ENABLED=true

# After fixing LEE
LEE_FAILSAFE_ENABLED=false
```

---

## Configuration System Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `CONFIGURATION_TIER` | String | `standard` | Base tier: `minimum`, `standard`, `maximum`, `user` |
| `USE_PARAMETER_STORE` | Boolean | `false` | Enable AWS SSM Parameter Store for configuration |
| `PARAMETER_PREFIX` | String | `/lambda-execution-engine` | SSM parameter path prefix |

### Configuration Tier Details

Each tier controls memory allocation and circuit breaker behavior:

#### `minimum` Tier
- **Memory:** 0.5MB circuit breaker overhead
- **Services:** CloudWatch API, Home Assistant only
- **Thresholds:** Conservative (3 failures, 30-60s timeouts)
- **Use Case:** Development, testing, tight memory constraints

#### `standard` Tier (Recommended)
- **Memory:** 2MB circuit breaker overhead
- **Services:** CloudWatch API, Home Assistant, External HTTP
- **Thresholds:** Balanced (2-3 failures, 20-45s timeouts)
- **Use Case:** Production deployments, balanced performance

#### `maximum` Tier
- **Memory:** 6MB circuit breaker overhead
- **Services:** All services including Database, Custom Services
- **Thresholds:** Aggressive (2-3 failures, 20-60s timeouts)
- **Use Case:** High-reliability requirements, maximum protection

#### `user` Tier
- **Memory:** Custom defined in `user_config.py`
- **Services:** Custom defined
- **Thresholds:** Custom defined
- **Use Case:** Advanced users with specific requirements

---

## Circuit Breaker Configuration

Circuit breaker settings are controlled by `CONFIGURATION_TIER`, not individual environment variables. Each tier defines service-specific thresholds.

### Configuration Tier Circuit Breaker Settings

#### MINIMUM Tier

| Service | Failure Threshold | Recovery Timeout | Max Test Calls |
|---------|------------------|------------------|----------------|
| CloudWatch API | 3 | 60s | 1 |
| Home Assistant | 2 | 30s | 1 |

#### STANDARD Tier

| Service | Failure Threshold | Recovery Timeout | Max Test Calls |
|---------|------------------|------------------|----------------|
| CloudWatch API | 3 | 45s | 2 |
| Home Assistant | 2 | 20s | 1 |
| External HTTP | 3 | 30s | 2 |

#### MAXIMUM Tier

| Service | Failure Threshold | Recovery Timeout | Max Test Calls |
|---------|------------------|------------------|----------------|
| CloudWatch API | 3 | 45s | 2 |
| Home Assistant | 2 | 20s | 1 |
| External HTTP | 3 | 30s | 2 |
| Database | 2 | 60s | 1 |
| Custom Services | 3 | 30s | 2 |

### Circuit Breaker States

| State | Description | Behavior |
|-------|-------------|----------|
| `CLOSED` | Normal operation | All requests pass through |
| `OPEN` | Failing, reject calls | Requests immediately fail |
| `HALF_OPEN` | Testing recovery | Limited test calls allowed |

### Monitoring Circuit Breakers

Circuit breaker metrics are automatically recorded:
- State transitions (CLOSED -> OPEN -> HALF_OPEN -> CLOSED)
- Failure counts per service
- Recovery attempts
- Success/failure rates

**CloudWatch Insights Query:**
```
fields @timestamp, message
| filter message like /circuit_breaker/
| stats count() by service_name, state
```

---

## HomeAssistant Extension Variables

### Required (if extension enabled)

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `HOME_ASSISTANT_ENABLED` | Boolean | `false` | Master switch to enable/disable HomeAssistant extension |
| `HOME_ASSISTANT_URL` | String | None | Base URL of Home Assistant instance (http://host:port) |
| `HOME_ASSISTANT_TOKEN` | String | None | Long-lived access token from Home Assistant |

**Note:** When failsafe mode is enabled (`LEE_FAILSAFE_ENABLED=true`), `HOME_ASSISTANT_ENABLED` is ignored. Only `HOME_ASSISTANT_URL` and `HOME_ASSISTANT_TOKEN` are required.

### Optional

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `HOME_ASSISTANT_TIMEOUT` | Integer | `30` | HTTP request timeout in seconds (not used by failsafe) |
| `HOME_ASSISTANT_VERIFY_SSL` | Boolean | `true` | Verify SSL certificates for HTTPS connections (used by failsafe) |
| `HA_ASSISTANT_NAME` | String | `Assistant` | Name used in conversation responses (not used by failsafe) |
| `HA_FEATURES` | String | `basic` | Feature level: `basic`, `standard`, `full`, `development` (not used by failsafe) |
| `HA_WEBSOCKET_ENABLED` | Boolean | `false` | Enable WebSocket for entity registry and filtering (not used by failsafe) |
| `HA_WEBSOCKET_TIMEOUT` | Integer | `10` | WebSocket connection timeout in seconds (not used by failsafe) |

---

## WebSocket Configuration

WebSocket functionality is controlled via Home Assistant extension variables.

| Variable | Type | Default | Description | Free Tier |
|----------|------|---------|-------------|-----------|
| `HA_WEBSOCKET_ENABLED` | Boolean | `false` | Enable WebSocket client connections | YES |
| `HA_WEBSOCKET_TIMEOUT` | Integer | `10` | Connection and receive timeout (seconds) | YES |

### WebSocket Capabilities

When `HA_WEBSOCKET_ENABLED=true`, Lambda can:
- **Connect:** Establish outbound WebSocket connections to external servers
- **Send:** Transmit JSON messages over WebSocket
- **Receive:** Receive responses with timeout
- **Close:** Gracefully close connections

### WebSocket Limitations

- [YES] Outbound connections FROM Lambda TO external WebSocket servers
- [NO] Inbound connections (requires API Gateway WebSocket API)
- [YES] Standard Lambda execution costs only
- [YES] No additional AWS services required

### Use Cases
- Home Assistant WebSocket API access
- Real-time entity state subscriptions
- Bidirectional communication with HA
- Event streaming from HA

### Performance Considerations
- WebSocket adds connection overhead (~100-300ms)
- Consider disabling if not needed to reduce latency
- Connection reuse not supported (Lambda stateless)
- Each request creates new connection

---

## Debug Interface Variables

Debug interface is controlled by `DEBUG_MODE` and `LOG_LEVEL` variables.

| Variable | Type | Values | Description |
|----------|------|--------|-------------|
| `DEBUG_MODE` | Boolean | `true`/`false` | Enable enhanced debugging features |
| `LOG_LEVEL` | String | `DEBUG`/`INFO`/`WARNING`/`ERROR`/`CRITICAL` | CloudWatch logging verbosity |

### Debug Mode Features

When `DEBUG_MODE=true`:
- Full request/response logging
- Gateway operation routing details
- Circuit breaker state transitions
- WebSocket connection lifecycle
- Detailed timing metrics
- Stack traces for all errors

### Log Level Behavior

| Level | What Gets Logged |
|-------|------------------|
| `DEBUG` | Everything including verbose internal operations |
| `INFO` | Normal operations, success/failure, timing |
| `WARNING` | Potential issues, degraded performance |
| `ERROR` | Errors that didn't crash Lambda |
| `CRITICAL` | Severe errors requiring immediate attention |

### Debug Helpers

Additional debug tools bypass normal execution:
- `Lambda_diagnostics.py` - Isolated testing, bypasses Lambda_function.py
- `Lambda_emergency.py` - Emergency scenario testing

**Usage:**
```python
# Normal: lambda_function.py handles all requests
# Diagnostic: Lambda_diagnostics.py bypasses LEE
# Emergency: Lambda_emergency.py tests failure scenarios
```

---

## AWS Systems Manager (SSM) Parameter Store

### Enabling Parameter Store

Set these environment variables to enable SSM:
```bash
USE_PARAMETER_STORE=true
PARAMETER_PREFIX=/lambda-execution-engine
```

**Note:** SSM parameters are **not used** when failsafe mode is active. Failsafe reads only from Lambda environment variables.

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

#### Circuit Breaker Parameters (Advanced)

Circuit breaker configuration is tier-based and not exposed as individual SSM parameters. To customize circuit breaker settings:

1. Use `CONFIGURATION_TIER=user`
2. Modify `user_config.py` with custom thresholds
3. Redeploy Lambda package

**Not supported via SSM:**
- Individual service failure thresholds
- Per-service recovery timeouts
- Custom service definitions

#### Custom Configuration Parameters

| Parameter Path | Type | Description |
|----------------|------|-------------|
| `/lambda-execution-engine/custom/[key]` | Any | User-defined custom configuration values |

---

## Priority Order

Configuration values are resolved in this order (highest to lowest priority):

1. **Failsafe Mode** - If `LEE_FAILSAFE_ENABLED=true`, only environment variables are used
2. **Environment Variables** - Set in Lambda console
3. **SSM Parameter Store** - If `USE_PARAMETER_STORE=true` (ignored in failsafe mode)
4. **Default Values** - Hardcoded in application

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

### Emergency Failsafe Setup
```bash
# Minimal configuration for immediate recovery
LEE_FAILSAFE_ENABLED=true
HOME_ASSISTANT_URL=http://192.168.1.100:8123
HOME_ASSISTANT_TOKEN=eyJ0eXAiOiJKV1Qi...
HOME_ASSISTANT_VERIFY_SSL=false
DEBUG_MODE=true
```

### Development Setup
```bash
ENVIRONMENT=development
DEBUG_MODE=true
LOG_LEVEL=DEBUG
CONFIGURATION_TIER=standard
HOME_ASSISTANT_ENABLED=true
HOME_ASSISTANT_URL=http://192.168.1.100:8123
HOME_ASSISTANT_TOKEN=your_token
HA_FEATURES=development
HA_WEBSOCKET_ENABLED=true
```

### Production Setup (High Reliability)
```bash
ENVIRONMENT=production
LOG_LEVEL=INFO
CONFIGURATION_TIER=maximum
USE_PARAMETER_STORE=true
PARAMETER_PREFIX=/lambda-prod
HOME_ASSISTANT_ENABLED=true
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

**Note:** IAM permissions are not required for failsafe mode, as it only reads Lambda environment variables.

---

## Variable Usage by Mode

### Normal LEE Mode
- Uses all variables listed above
- Respects `HOME_ASSISTANT_ENABLED`
- Can use SSM Parameter Store
- Full feature set available
- Circuit breaker protection active

### Failsafe Mode (`LEE_FAILSAFE_ENABLED=true`)
**Only uses these variables:**
- `HOME_ASSISTANT_URL` [REQUIRED]
- `HOME_ASSISTANT_TOKEN` [REQUIRED]
- `HOME_ASSISTANT_VERIFY_SSL` [OPTIONAL] (default: true)
- `DEBUG_MODE` [OPTIONAL] (default: false)

**Ignores all other variables:**
- Configuration tier, logging, metrics
- Extension features, caching, circuit breaker
- SSM Parameter Store (reads only env vars)
- All HA extension optional features

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
**Available:** ~108-113MB for code

### Standard Configuration
```bash
CONFIGURATION_TIER=standard
HOME_ASSISTANT_ENABLED=true
HA_WEBSOCKET_ENABLED=false
```
**Overhead:** ~20-25MB  
**Available:** ~103-108MB for code

### Maximum Configuration
```bash
CONFIGURATION_TIER=maximum
HOME_ASSISTANT_ENABLED=true
HA_WEBSOCKET_ENABLED=true
```
**Overhead:** ~30-35MB  
**Available:** ~93-98MB for code

### Failsafe Mode
```bash
LEE_FAILSAFE_ENABLED=true
```
**Overhead:** ~5-8MB  
**Available:** ~120-123MB for code

**Notes:**
- Overhead includes: LEE core, SUGA-ISP, interfaces, circuit breakers, metrics
- Actual usage varies based on request complexity
- WebSocket adds ~2-3MB when enabled
- Cache usage grows during execution
- Consider increasing Lambda memory if approaching limits

---

## Troubleshooting Variable Issues

### Issue: Configuration Not Loading
**Check:**
1. Variable names are EXACT (case-sensitive)
2. Boolean values are lowercase: `true`/`false`
3. SSM parameter paths match PARAMETER_PREFIX
4. IAM policy grants ssm:GetParameter
5. SSM parameters exist in correct region

### Issue: Failsafe Not Activating
**Check:**
1. Variable is exactly: `LEE_FAILSAFE_ENABLED=true`
2. Value is lowercase: `true` not `True` or `TRUE`
3. lambda_failsafe.py exists in deployment package
4. Check CloudWatch logs for activation message

### Issue: Circuit Breaker Too Aggressive
**Solutions:**
1. Change tier: `CONFIGURATION_TIER=minimum`
2. Modify user_config.py for custom thresholds
3. Review service availability
4. Check network latency

### Issue: Out of Memory Errors
**Solutions:**
1. Decrease tier: `CONFIGURATION_TIER=minimum`
2. Disable WebSocket: `HA_WEBSOCKET_ENABLED=false`
3. Review cache settings
4. Increase Lambda memory allocation

---

## Best Practices

### Security
- [YES] Use SSM SecureString for tokens
- [YES] Enable HOME_ASSISTANT_VERIFY_SSL=true in production
- [YES] Use PARAMETER_PREFIX to isolate environments
- [NO] Never commit tokens to version control
- [YES] Rotate tokens regularly

### Performance
- [YES] Use CONFIGURATION_TIER=standard for most cases
- [YES] Disable unused features (websocket if not needed)
- [NO] Avoid DEBUG_MODE in production (log volume)
- [YES] Monitor circuit breaker states
- [YES] Cache SSM parameters (automatic, 300s TTL)

### Reliability
- [YES] Enable circuit breaker protection (tier >= standard)
- [YES] Set appropriate timeouts for your network
- [YES] Configure LEE_FAILSAFE_ENABLED for emergencies
- [YES] Monitor CloudWatch logs regularly
- [YES] Test failover scenarios periodically

### Cost Optimization
- [YES] Minimize log volume (avoid DEBUG in prod)
- [YES] Use SSM parameter caching (reduces API calls)
- [YES] Monitor Lambda invocation count
- [YES] Review CloudWatch log retention
- [YES] Consider Lambda reserved concurrency

---

## Notes

- Environment variables take precedence over SSM parameters (except in failsafe mode)
- SSM parameters are cached for 300 seconds to reduce API calls
- Boolean values in SSM must be strings: `"true"` or `"false"`
- Use `SecureString` type in SSM for all tokens and secrets
- Change `PARAMETER_PREFIX` to isolate configurations per environment
- Failsafe mode provides insurance against LEE failures
- Toggle failsafe without code changes or redeployment
- Circuit breaker configuration is tier-based, not per-variable
- WebSocket is outbound only (Lambda client to external server)
