# 🏠 Home Assistant Configuration

The Lambda Execution Engine provides comprehensive Home Assistant integration with sophisticated caching, circuit breaker protection, and customizable assistant invocation. This section covers configuration options, entity exposure methods, and integration patterns.

## Quick Configuration

### Essential Parameters

Your Home Assistant integration requires two mandatory parameters stored in AWS Systems Manager Parameter Store:

**Required Parameters:**
- `/lambda-execution-engine/homeassistant/url` - Your Home Assistant URL
- `/lambda-execution-engine/homeassistant/token` - Long-lived access token (SecureString)

**Optional Parameters:**
- `/lambda-execution-engine/homeassistant/assistant_name` - Custom assistant name (default: "Home Assistant")
- `/lambda-execution-engine/homeassistant/timeout` - Request timeout in seconds (default: 30)
- `/lambda-execution-engine/homeassistant/verify_ssl` - SSL certificate verification (default: true)

### Environment Variables

Control Home Assistant integration behavior through Lambda environment variables:

```bash
# Core Configuration
HOME_ASSISTANT_ENABLED=true          # Enable/disable HA integration
HA_ASSISTANT_NAME=Home Assistant     # How Alexa refers to your system
HA_FEATURE_PRESET=standard          # Feature tier (minimal/standard/performance/maximum)

# Connection Settings  
HA_TIMEOUT=30                       # Request timeout (seconds)
HA_VERIFY_SSL=true                  # SSL certificate verification
HA_CACHE_TTL=300                    # Cache duration (seconds)

# Advanced Options
HA_MAX_RETRIES=3                    # Maximum retry attempts
HA_CIRCUIT_BREAKER_THRESHOLD=5      # Circuit breaker failure threshold
HA_BATCH_SIZE=10                    # Batch operation size
```

## URL Configuration Patterns

### Nabu Casa Cloud

```bash
# Parameter Store
/lambda-execution-engine/homeassistant/url = https://xxxxx.ui.nabu.casa

# Environment Variables
HA_VERIFY_SSL=true
HA_TIMEOUT=30
```

Nabu Casa provides cloud connectivity with automatic SSL termination. Use your instance-specific URL found in Home Assistant Configuration → Home Assistant Cloud.

### Local Network (Direct IP)

```bash
# Parameter Store  
/lambda-execution-engine/homeassistant/url = http://192.168.1.100:8123

# Environment Variables
HA_VERIFY_SSL=false
HA_TIMEOUT=45
```

Direct IP access requires network connectivity between AWS Lambda and your local network via VPN or direct connection.

### Custom Domain (Self-Hosted)

```bash
# Parameter Store
/lambda-execution-engine/homeassistant/url = https://home.yourdomain.com

# Environment Variables
HA_VERIFY_SSL=true
HA_TIMEOUT=30
```

Self-hosted domains with valid SSL certificates provide secure access without cloud dependencies.

### Self-Signed Certificates

```bash
# Parameter Store
/lambda-execution-engine/homeassistant/url = https://192.168.1.100:8123

# Environment Variables  
HA_VERIFY_SSL=false
HA_TIMEOUT=45
```

Local HTTPS with self-signed certificates requires SSL verification bypass while maintaining encryption.

## Assistant Name Customization

### Default Configuration

```bash
# Uses "Home Assistant" as invocation name
HA_ASSISTANT_NAME=Home Assistant
```

**Alexa Phrases:**
- "Alexa, ask Home Assistant to turn on the lights"
- "Alexa, tell Home Assistant to start the morning routine"

### Custom Names

```bash
# Custom assistant names
HA_ASSISTANT_NAME=Jarvis
HA_ASSISTANT_NAME=Computer  
HA_ASSISTANT_NAME=Smart Home
HA_ASSISTANT_NAME=House
```

**Custom Invocation Examples:**
- "Alexa, ask Jarvis to turn on the lights"
- "Alexa, tell Computer to lock the doors"
- "Alexa, ask House to start movie mode"

### Name Validation Rules

**Valid Names:**
- Single words: Jarvis, Computer, House
- Two words: Smart Home, Home System
- Mixed case: automatically converted to lowercase
- Length: 2-25 characters

**Invalid Names:**
- Reserved words: Alexa, Amazon, Echo
- Numbers only: 123, 456
- Special characters: @jarvis, house!
- Empty or whitespace only

## Entity Exposure Methods

Home Assistant provides three methods to control which entities Alexa can access. Choose the method that matches your security and management preferences.

### Method 1: Expose All Entities (Default)

```yaml
# configuration.yaml
alexa:
  smart_home:
```

**Behavior:** All entities become available to Alexa automatically
**Pros:** Zero configuration, new devices work immediately
**Cons:** Less security, Alexa sees everything
**Best For:** Small installations, trusted environments

### Method 2: Manual Entity Selection

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

**Behavior:** Only specified entities are exposed
**Pros:** Complete control, enhanced security
**Cons:** Manual maintenance required
**Best For:** Large installations, privacy-focused setups

### Method 3: Domain and Area Filtering

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

**Behavior:** Expose entities by type and location patterns
**Pros:** Balanced control and automation
**Cons:** Requires understanding of domains
**Best For:** Medium installations, organized device naming

## Feature Presets

Control system behavior and resource usage through feature presets that automatically configure cache sizes, timeouts, and enabled features.

### Minimal Preset

```bash
HA_FEATURE_PRESET=minimal
```

**Configuration:**
- Memory usage: ~15MB
- Cache TTL: 60 seconds
- Features: Basic device control only
- Retries: 2 attempts
- Timeout: 15 seconds

**Use Cases:** Testing, development, resource-constrained environments

### Standard Preset (Recommended)

```bash
HA_FEATURE_PRESET=standard
```

**Configuration:**
- Memory usage: ~25MB
- Cache TTL: 300 seconds (5 minutes)
- Features: All core functionality
- Retries: 3 attempts
- Timeout: 30 seconds

**Use Cases:** Production deployments, typical smart homes

### Performance Preset

```bash
HA_FEATURE_PRESET=performance
```

**Configuration:**
- Memory usage: ~40MB
- Cache TTL: 600 seconds (10 minutes)
- Features: All functionality plus optimizations
- Retries: 5 attempts
- Timeout: 45 seconds

**Use Cases:** Large installations, performance-critical applications

### Maximum Preset

```bash
HA_FEATURE_PRESET=maximum
```

**Configuration:**
- Memory usage: ~60MB
- Cache TTL: 1800 seconds (30 minutes)
- Features: Everything enabled
- Retries: 7 attempts  
- Timeout: 60 seconds

**Use Cases:** Enterprise deployments, maximum reliability requirements

## Configuration Validation

The system provides comprehensive configuration validation with clear error messages and diagnostic capabilities.

### Environment Variable Validation

```bash
# Valid configurations
HOME_ASSISTANT_ENABLED=true          ✅
HOME_ASSISTANT_ENABLED=false         ✅  
HOME_ASSISTANT_ENABLED=1             ✅ (interpreted as true)
HOME_ASSISTANT_ENABLED=0             ✅ (interpreted as false)

# Invalid configurations  
HOME_ASSISTANT_ENABLED=maybe         ❌ (defaults to false)
HOME_ASSISTANT_ENABLED=""            ❌ (defaults to false)
```

### Parameter Store Validation

The system validates Parameter Store configuration at startup:

**URL Validation:**
- Must start with http:// or https://
- Must include port for non-standard ports
- Must be reachable from Lambda execution environment

**Token Validation:**
- Must be SecureString type in Parameter Store
- Must be valid Home Assistant long-lived access token
- Must have sufficient permissions for intended operations

### Configuration Testing

Access the diagnostic endpoint to validate your configuration:

```bash
# Test configuration
curl -X POST https://your-lambda-url/test \
  -H "Content-Type: application/json" \
  -d '{"test_type": "configuration"}'

# Response includes:
{
  "configuration_valid": true,
  "ha_connection": "success",
  "entities_accessible": 47,
  "assistant_name": "Jarvis",
  "preset": "standard"
}
```

## Conversation Agent Setup

Enable natural language control through Home Assistant's Conversation integration.

### Basic Conversation Configuration

```yaml
# configuration.yaml
conversation:

# Optional: Custom intents
intent_script:
  MovieMode:
    speech:
      text: "Starting movie mode"
    action:
      - service: script.movie_mode
      
  GoodMorning:
    speech:
      text: "Good morning! Starting your morning routine"
    action:
      - service: script.morning_routine
```

### Conversation Examples

With conversation agent configured, you can use natural language:

**Device Control:**
- "Alexa, ask Jarvis to turn on the living room lights"
- "Alexa, tell Computer to set the temperature to 72 degrees"

**Scene Activation:**
- "Alexa, ask Home Assistant to activate movie mode"
- "Alexa, tell Jarvis to start the morning routine"

**Status Queries:**
- "Alexa, ask Home Assistant what's the temperature"
- "Alexa, ask Jarvis if the doors are locked"

## Advanced Integration Patterns

### Multi-Instance Support

Manage multiple Home Assistant installations from a single Lambda function:

```bash
# Environment Variables
HOME_ASSISTANT_ENABLED=true
HA_MULTI_INSTANCE=true

# Parameter Store (per instance)
/lambda-execution-engine/homeassistant/primary/url = https://home.nabu.casa
/lambda-execution-engine/homeassistant/primary/token = [SecureString]
/lambda-execution-engine/homeassistant/vacation/url = https://cabin.domain.com  
/lambda-execution-engine/homeassistant/vacation/token = [SecureString]
```

### Custom Service Integration

Extend functionality beyond basic device control:

```bash
# Environment Variables
HA_CUSTOM_SERVICES=true
HA_SERVICE_WHITELIST=script.movie_mode,automation.security_check
```

**Custom Service Examples:**
- Complex automation sequences
- Security system integration  
- Media center control
- HVAC scheduling

### Performance Monitoring

Enable detailed performance metrics:

```bash
# Environment Variables
HA_METRICS_ENABLED=true
HA_PERFORMANCE_LOGGING=true
```

**Available Metrics:**
- Request latency per operation type
- Cache hit rates by entity type
- Circuit breaker activation frequency
- Memory usage patterns

## Troubleshooting Common Issues

### Connection Failures

**Symptoms:** "Cannot reach Home Assistant" errors

**Solutions:**
1. Verify URL accessibility from AWS region
2. Check firewall/port configurations
3. Validate SSL certificate if using HTTPS
4. Test with `HA_VERIFY_SSL=false` for diagnosis

### Authentication Errors

**Symptoms:** "Unauthorized" or "Invalid token" messages

**Solutions:**
1. Regenerate Home Assistant long-lived access token
2. Update Parameter Store with new token
3. Verify token permissions in Home Assistant
4. Check token hasn't expired

### Entity Not Found

**Symptoms:** "Entity not available" for known devices

**Solutions:**
1. Verify entity exists in Home Assistant
2. Check entity exposure configuration
3. Clear Lambda cache via diagnostic endpoint
4. Confirm entity_id spelling and format

### Performance Issues

**Symptoms:** Slow responses or timeouts

**Solutions:**
1. Increase `HA_TIMEOUT` value
2. Switch to higher performance preset
3. Check Home Assistant system resources
4. Monitor CloudWatch metrics for bottlenecks

### Assistant Name Not Working

**Symptoms:** Alexa doesn't recognize custom name

**Solutions:**
1. Update Alexa skill invocation name in developer console
2. Verify `HA_ASSISTANT_NAME` environment variable
3. Restart Lambda function to reload configuration
4. Test with Alexa app device discovery

## Security Considerations

### Network Security

**Cloud Deployments (Nabu Casa):**
- End-to-end encryption
- Automatic certificate management
- AWS security group protection

**Local Deployments:**
- VPN or direct connect recommended
- Firewall rules for Lambda IP ranges
- Consider port restrictions

### Authentication Security

**Token Management:**
- Use Parameter Store SecureString encryption
- Rotate tokens periodically
- Limit token scope to required operations
- Monitor token usage in Home Assistant logs

### Data Privacy

**Information Handling:**
- No persistent data storage
- Memory-only caching
- Logs contain no sensitive information
- Request data cleared after processing

## Configuration Examples

### Production Nabu Casa Setup

```bash
# Environment Variables
HOME_ASSISTANT_ENABLED=true
HA_ASSISTANT_NAME=Smart Home
HA_FEATURE_PRESET=standard
HA_VERIFY_SSL=true
HA_TIMEOUT=30
HA_CACHE_TTL=300

# Parameter Store
/lambda-execution-engine/homeassistant/url = https://xxxxx.ui.nabu.casa
/lambda-execution-engine/homeassistant/token = [SecureString]
/lambda-execution-engine/homeassistant/assistant_name = Smart Home
```

### Development Local Setup

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

### High-Performance Setup

```bash
# Environment Variables
HOME_ASSISTANT_ENABLED=true
HA_ASSISTANT_NAME=Jarvis
HA_FEATURE_PRESET=performance
HA_VERIFY_SSL=true
HA_TIMEOUT=45
HA_CACHE_TTL=600
HA_MAX_RETRIES=5
HA_CIRCUIT_BREAKER_THRESHOLD=3

# Parameter Store
/lambda-execution-engine/homeassistant/url = https://home.domain.com
/lambda-execution-engine/homeassistant/token = [SecureString]
/lambda-execution-engine/homeassistant/assistant_name = Jarvis
```

This comprehensive configuration system provides the flexibility to adapt the Lambda Execution Engine to any Home Assistant deployment while maintaining optimal performance and security.
