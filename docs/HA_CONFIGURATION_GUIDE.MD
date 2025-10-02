# Home Assistant Configuration Guide

Complete configuration reference for Lambda Execution Engine Home Assistant integration.

## Quick Reference

### Required Configuration
```bash
# Parameter Store (Required)
/lambda-execution-engine/homeassistant/url = https://home.yourdomain.com
/lambda-execution-engine/homeassistant/token = [SecureString]

# Environment Variables (Required)
HOME_ASSISTANT_ENABLED=true
```

### Optional Configuration
```bash
# Environment Variables (Optional)
HA_ASSISTANT_NAME=Home Assistant
HA_FEATURE_PRESET=standard
HA_TIMEOUT=30
HA_VERIFY_SSL=true
HA_CACHE_TTL=300

# Parameter Store (Optional)
/lambda-execution-engine/homeassistant/assistant_name = Home Assistant
/lambda-execution-engine/homeassistant/timeout = 30
/lambda-execution-engine/homeassistant/verify_ssl = true
```

## Environment Variables Reference

### Core Configuration

**HOME_ASSISTANT_ENABLED**
- Purpose: Master switch for HA integration
- Values: `true`, `false`, `1`, `0`
- Default: `false`
- Required: Yes (if using HA)

**HA_ASSISTANT_NAME**
- Purpose: Custom assistant invocation name for Alexa
- Values: 2-25 characters, alphanumeric + spaces
- Default: `Home Assistant`
- Example: `Jarvis`, `Computer`, `Smart Home`
- Invalid: `Alexa`, `Amazon`, `Echo`, numbers only

**HA_FEATURE_PRESET**
- Purpose: Controls performance tier and enabled features
- Values: `minimal`, `standard`, `performance`, `maximum`
- Default: `standard`
- Memory Usage:
  - minimal: ~15MB
  - standard: ~25MB  
  - performance: ~40MB
  - maximum: ~60MB

### Connection Settings

**HA_TIMEOUT**
- Purpose: Request timeout in seconds
- Values: 15-120 (integers)
- Default: `30`
- Recommendations:
  - Local network: 15-30
  - Cloud/Remote: 30-45
  - Slow connection: 45-60

**HA_VERIFY_SSL**
- Purpose: SSL certificate verification
- Values: `true`, `false`
- Default: `true`
- Use `false` for:
  - Self-signed certificates
  - Local HTTP connections
  - Development environments

**HA_CACHE_TTL**
- Purpose: Cache duration in seconds
- Values: 60-3600 (integers)
- Default: `300` (5 minutes)
- Recommendations:
  - Frequent changes: 60-300
  - Stable config: 600-1800
  - Development: 60

### Advanced Settings

**HA_MAX_RETRIES**
- Purpose: Maximum retry attempts for failed requests
- Values: 1-10 (integers)
- Default: `3`

**HA_CIRCUIT_BREAKER_THRESHOLD**
- Purpose: Failures before circuit breaker activates
- Values: 1-20 (integers)
- Default: `5`

**HA_BATCH_SIZE**
- Purpose: Entities processed in batch operations
- Values: 1-50 (integers)
- Default: `10`

## Parameter Store Configuration

### Required Parameters

**URL Parameter**
```
Parameter: /lambda-execution-engine/homeassistant/url
Type: String
Value: Your Home Assistant URL
Examples:
  - https://home.yourdomain.com (Custom domain)
  - http://192.168.1.100:8123 (Local IP)
  - https://your-ha-instance.duckdns.org (DuckDNS)
```

**Token Parameter**
```
Parameter: /lambda-execution-engine/homeassistant/token
Type: SecureString
Value: Long-lived access token from Home Assistant
KMS Key: alias/aws/ssm (default)
```

### Optional Parameters

**Assistant Name Parameter**
```
Parameter: /lambda-execution-engine/homeassistant/assistant_name
Type: String
Value: Custom assistant name
Priority: Overridden by HA_ASSISTANT_NAME environment variable
```

**Timeout Parameter**
```
Parameter: /lambda-execution-engine/homeassistant/timeout
Type: String
Value: Timeout in seconds (as string)
Priority: Overridden by HA_TIMEOUT environment variable
```

**SSL Verification Parameter**
```
Parameter: /lambda-execution-engine/homeassistant/verify_ssl
Type: String
Value: "true" or "false"
Priority: Overridden by HA_VERIFY_SSL environment variable
```

## Configuration Priority

Settings are applied in this order (highest to lowest priority):

1. **Environment Variables** (highest priority)
2. **Parameter Store**
3. **Default Values** (lowest priority)

Example: If both `HA_ASSISTANT_NAME=Jarvis` (env) and `/lambda-execution-engine/homeassistant/assistant_name=Computer` (parameter) are set, `Jarvis` is used.

## Entity Exposure Methods

Control which Home Assistant entities Alexa can access using one of three methods:

### Method 1: Expose All Entities (Default)
```yaml
# configuration.yaml
alexa:
  smart_home:
```
**Result**: All entities available to Alexa automatically

### Method 2: Manual Selection
```yaml
# configuration.yaml
alexa:
  smart_home:
    filter:
      include_entities:
        - light.living_room
        - switch.coffee_maker
        - climate.main_thermostat
      exclude_entities:
        - sensor.private_camera
```
**Result**: Only specified entities exposed

### Method 3: Domain/Pattern Filtering
```yaml
# configuration.yaml
alexa:
  smart_home:
    filter:
      include_domains:
        - light
        - switch
        - climate
      exclude_domains:
        - camera
        - person
      include_entity_globs:
        - "*.living_room"
        - "*.kitchen"
```
**Result**: Entities matching patterns exposed

## Configuration Examples

### Production Cloud Setup
```bash
# Environment Variables
HOME_ASSISTANT_ENABLED=true
HA_ASSISTANT_NAME=Smart Home
HA_FEATURE_PRESET=standard
HA_VERIFY_SSL=true
HA_TIMEOUT=30
HA_CACHE_TTL=300

# Parameter Store
/lambda-execution-engine/homeassistant/url = https://home.yourdomain.com
/lambda-execution-engine/homeassistant/token = [SecureString]
```

### Local Development
```bash
# Environment Variables
HOME_ASSISTANT_ENABLED=true
HA_ASSISTANT_NAME=Test Assistant
HA_FEATURE_PRESET=minimal
HA_VERIFY_SSL=false
HA_TIMEOUT=45
HA_CACHE_TTL=60
DEBUG_MODE=true

# Parameter Store
/lambda-execution-engine/homeassistant/url = http://192.168.1.100:8123
/lambda-execution-engine/homeassistant/token = [SecureString]
```

### High Performance
```bash
# Environment Variables
HOME_ASSISTANT_ENABLED=true
HA_ASSISTANT_NAME=Jarvis
HA_FEATURE_PRESET=performance
HA_VERIFY_SSL=true
HA_TIMEOUT=45
HA_CACHE_TTL=600
HA_MAX_RETRIES=5

# Parameter Store
/lambda-execution-engine/homeassistant/url = https://home.domain.com
/lambda-execution-engine/homeassistant/token = [SecureString]
```

### Multi-Instance (Advanced)
```bash
# Environment Variables
HOME_ASSISTANT_ENABLED=true
HA_MULTI_INSTANCE=true
HA_FEATURE_PRESET=performance

# Parameter Store (Primary)
/lambda-execution-engine/homeassistant/primary/url = https://home.domain.com
/lambda-execution-engine/homeassistant/primary/token = [SecureString]

# Parameter Store (Vacation)
/lambda-execution-engine/homeassistant/vacation/url = https://cabin.domain.com
/lambda-execution-engine/homeassistant/vacation/token = [SecureString]
```

## Security Configuration

### Network Security

**Cloud Services (Recommended)**
- End-to-end encryption
- Automatic certificate management
- No firewall configuration needed

**Custom Domain**
- Valid SSL certificates required
- DNS configuration needed
- Firewall rules for HTTPS (443)

**Local Network**
- VPN or AWS Direct Connect recommended
- Firewall rules for Lambda IP ranges
- Consider IP restrictions

### Token Security

**Best Practices**
- Use Parameter Store SecureString encryption
- Rotate tokens every 90 days
- Limit token scope to required operations
- Monitor token usage in HA logs

**Token Permissions**
Required permissions for full functionality:
- Read entities and states
- Call services
- Access configuration
- Read areas and devices

## Troubleshooting

### Connection Issues

**"Cannot reach Home Assistant"**
1. Verify URL accessibility from AWS region
2. Check firewall/port configurations  
3. Test with `curl` from Lambda region
4. Validate SSL certificate

**"Unauthorized" errors**
1. Regenerate HA long-lived access token
2. Update Parameter Store with new token
3. Verify token permissions in HA
4. Check token hasn't expired

### Configuration Issues

**"Entity not found"**
1. Verify entity exists in HA
2. Check entity exposure configuration
3. Clear Lambda cache via diagnostic endpoint
4. Confirm entity_id spelling

**Assistant name not working**
1. Verify `HA_ASSISTANT_NAME` environment variable
2. Update Alexa skill invocation name
3. Check Parameter Store assistant_name
4. Restart Lambda function

### Performance Issues

**Slow responses**
1. Increase `HA_TIMEOUT` value
2. Switch to higher performance preset
3. Check HA system resources
4. Monitor CloudWatch metrics

**High memory usage**
1. Switch to lower feature preset
2. Reduce `HA_CACHE_TTL`
3. Enable LUGS (set `LUGS_ENABLED=true`)
4. Monitor Lambda memory metrics

## Validation

### Configuration Test
```bash
# Test via diagnostic endpoint
curl -X POST https://your-lambda-url/test \
  -H "Content-Type: application/json" \
  -d '{"test_type": "configuration"}'
```

### Expected Response
```json
{
  "configuration_valid": true,
  "ha_connection": "success", 
  "entities_accessible": 47,
  "assistant_name": "Your Assistant Name",
  "preset": "standard"
}
```

### Environment Variable Validation

**Valid Values**
```bash
HOME_ASSISTANT_ENABLED=true     ✅
HOME_ASSISTANT_ENABLED=false    ✅
HOME_ASSISTANT_ENABLED=1        ✅ (true)
HOME_ASSISTANT_ENABLED=0        ✅ (false)
HA_VERIFY_SSL=true             ✅
HA_VERIFY_SSL=false            ✅
HA_TIMEOUT=30                  ✅
HA_ASSISTANT_NAME=Jarvis       ✅
```

**Invalid Values**
```bash
HOME_ASSISTANT_ENABLED=maybe   ❌ (defaults to false)
HA_TIMEOUT=abc                 ❌ (defaults to 30)
HA_ASSISTANT_NAME=Alexa        ❌ (validation error)
HA_ASSISTANT_NAME=""           ❌ (validation error)
```

## Migration Guide

### From Legacy Configuration
1. Move URL/token to Parameter Store
2. Add environment variables
3. Update entity exposure method
4. Test configuration
5. Monitor performance

### Version Compatibility
- Home Assistant 2021.3+ (recommended)
- Home Assistant 2020.12+ (basic features)
- Conversation API requires 2023.1+
- Assistant name feature requires this version

This guide covers all configuration aspects for the Lambda Execution Engine Home Assistant integration. For additional support, use the diagnostic endpoint or check CloudWatch logs.
