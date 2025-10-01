**Add to configuration validation:**

```python
def validate_deployment_config(self) -> bool:
    """Validate deployment configuration."""
    self.log_step("Validation", "START", "Validating configuration")
    
    try:
        # Validate assistant name
        assistant_name = os.getenv('HA_ASSISTANT_NAME', 'Home Assistant')
        
        self.log_step("Validation", "INFO", f"Assistant name: {assistant_name}")
        
        # Check for issues
        words = assistant_name.split()
        forbidden = ['alexa', 'amazon', 'echo', 'skill']
        
        for word in words:
            if word.lower() in forbidden:
                self.log_step(
                    "Validation", 
                    "WARN", 
                    f"Assistant name contains forbidden word '{word}'"
                )
        
        if len(words) == 1:
            self.log_step(
                "Validation",
                "INFO",
                f"Single-word name '{assistant_name}' - ensure it's a proper name"
            )
        
        self.log_step("Validation", "PASS", "Configuration validated")
        return True
        
    except Exception as e:
        self.log_step("Validation", "ERROR", str(e))
        return False
```

---

## Phase 5: Testing & Validation

### 5.1 Add Unit Tests

**Create test_ha_assistant_config.py:**

```python
"""
test_ha_assistant_config.py - Test Home Assistant Assistant Name Configuration
Version: 2025.10.01.01
"""

import os
import pytest
from unittest.mock import patch, MagicMock


def test_default_assistant_name():
    """Test default assistant name is 'Home Assistant'."""
    with patch.dict(os.environ, {}, clear=True):
        from homeassistant_extension import get_ha_assistant_name
        assert get_ha_assistant_name() == 'Home Assistant'


def test_custom_assistant_name_env():
    """Test custom assistant name from environment variable."""
    with patch.dict(os.environ, {'HA_ASSISTANT_NAME': 'Bob'}):
        from homeassistant_extension import get_ha_assistant_name
        assert get_ha_assistant_name() == 'Bob'


def test_assistant_name_validation_single_word():
    """Test validation warns about single-word names."""
    with patch.dict(os.environ, {'HA_ASSISTANT_NAME': 'Computer'}):
        from homeassistant_extension import validate_ha_assistant_configuration
        result = validate_ha_assistant_configuration()
        
        assert result['configured_name'] == 'Computer'
        assert len(result['warnings']) > 0
        assert any('Single-word' in w for w in result['warnings'])


def test_assistant_name_validation_forbidden_words():
    """Test validation catches forbidden words."""
    with patch.dict(os.environ, {'HA_ASSISTANT_NAME': 'Alexa Assistant'}):
        from homeassistant_extension import validate_ha_assistant_configuration
        result = validate_ha_assistant_configuration()
        
        assert len(result['warnings']) > 0
        assert any('forbidden' in w.lower() for w in result['warnings'])


def test_assistant_name_validation_valid_custom():
    """Test validation passes for valid custom names."""
    with patch.dict(os.environ, {'HA_ASSISTANT_NAME': 'My Assistant'}):
        from homeassistant_extension import validate_ha_assistant_configuration
        result = validate_ha_assistant_configuration()
        
        assert result['configured_name'] == 'My Assistant'
        assert result['is_default'] is False


def test_assistant_name_validation_default():
    """Test validation recognizes default name."""
    with patch.dict(os.environ, {'HA_ASSISTANT_NAME': 'Home Assistant'}):
        from homeassistant_extension import validate_ha_assistant_configuration
        result = validate_ha_assistant_configuration()
        
        assert result['is_default'] is True


def test_assistant_name_lowercase_conversion():
    """Test lowercase name generation for Alexa."""
    with patch.dict(os.environ, {'HA_ASSISTANT_NAME': 'My Assistant'}):
        from homeassistant_extension import validate_ha_assistant_configuration
        result = validate_ha_assistant_configuration()
        
        assert result['lowercase_name'] == 'my assistant'


def test_conversation_intent_uses_assistant_name():
    """Test conversation intent uses configured assistant name."""
    with patch.dict(os.environ, {'HA_ASSISTANT_NAME': 'Bob'}):
        from lambda_function import _handle_conversation_intent
        from homeassistant_extension import get_ha_assistant_name
        
        # Mock event
        event = {
            'request': {
                'type': 'IntentRequest',
                'intent': {
                    'name': 'TalkToHomeAssistant',
                    'slots': {
                        'query': {
                            'value': 'turn on lights'
                        }
                    }
                }
            }
        }
        
        # Verify assistant name is available
        assert get_ha_assistant_name() == 'Bob'


def test_diagnostic_endpoint_includes_assistant_config():
    """Test diagnostic endpoint includes assistant configuration."""
    with patch.dict(os.environ, {'HA_ASSISTANT_NAME': 'TestBot'}):
        from lambda_function import _handle_diagnostic_request
        
        event = {'diagnostic': True}
        result = _handle_diagnostic_request(event)
        
        assert result['statusCode'] == 200
        
        import json
        body = json.loads(result['body'])
        
        assert 'assistant_configuration' in body
        assert body['assistant_configuration']['configured_name'] == 'TestBot'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
```

---

### 5.2 Integration Test

**Create test_alexa_invocation.py:**

```python
"""
test_alexa_invocation.py - Test Alexa Custom Skill Invocation
Version: 2025.10.01.01
"""

import os
import json
from unittest.mock import patch, MagicMock


def test_custom_skill_invocation_default_name():
    """Test Custom Skill with default assistant name."""
    with patch.dict(os.environ, {'HA_ASSISTANT_NAME': 'Home Assistant'}):
        from lambda_function import lambda_handler
        
        # Simulate Alexa Custom Skill request
        event = {
            'version': '1.0',
            'session': {
                'new': True,
                'sessionId': 'test-session',
                'application': {
                    'applicationId': 'amzn1.ask.skill.test'
                }
            },
            'request': {
                'type': 'IntentRequest',
                'requestId': 'test-request',
                'intent': {
                    'name': 'TalkToHomeAssistant',
                    'slots': {
                        'query': {
                            'name': 'query',
                            'value': 'what is the temperature'
                        }
                    }
                }
            }
        }
        
        # Mock Home Assistant response
        with patch('homeassistant_extension.call_ha_api') as mock_call:
            mock_call.return_value = {
                'success': True,
                'data': {
                    'response': {
                        'speech': {
                            'plain': {
                                'speech': 'The temperature is 72 degrees'
                            }
                        }
                    }
                }
            }
            
            context = MagicMock()
            result = lambda_handler(event, context)
            
            assert result['response']['outputSpeech']['text']
            assert 'temperature' in result['response']['outputSpeech']['text'].lower()


def test_custom_skill_invocation_custom_name():
    """Test Custom Skill with custom assistant name."""
    with patch.dict(os.environ, {'HA_ASSISTANT_NAME': 'Bob'}):
        from lambda_function import lambda_handler
        from homeassistant_extension import get_ha_assistant_name
        
        # Verify custom name is set
        assert get_ha_assistant_name() == 'Bob'
        
        # Test would work the same as default, name is just logged
        # The actual Alexa invocation name is configured in Alexa Developer Console


def test_launch_request_mentions_assistant_name():
    """Test LaunchRequest response mentions assistant name."""
    with patch.dict(os.environ, {'HA_ASSISTANT_NAME': 'Bob'}):
        from lambda_function import _handle_launch_request
        
        event = {
            'request': {
                'type': 'LaunchRequest'
            }
        }
        
        result = _handle_launch_request(event)
        
        # Response should be personalized but this is optional
        assert result['response']['outputSpeech']['text']


if __name__ == '__main__':
    import pytest
    pytest.main([__file__, '-v'])
```

---

## Phase 6: Documentation Files to Create/Update

### 6.1 Files to Update

**README.md:**
- ✅ Add "Home Assistant Configuration" section
- ✅ Update "Alexa Skill Integration" section
- ✅ Add Nabu Casa vs. Assist clarification
- ✅ Add customization guide

**Install_Guide.MD:**
- ✅ Update Phase 3: Add assistant_name parameter
- ✅ Update Phase 3: Add optional SSL/timeout parameters
- ✅ Update Phase 5: Add HA environment variables
- ✅ Add Phase 6B: Custom Skill setup with assistant name
- ✅ Add testing instructions for custom names

**PROJECT_ARCHITECTURE_REFERENCE.md:**
- ✅ Document HA_ASSISTANT_NAME configuration
- ✅ Update environment variable reference
- ✅ Add assistant name validation functions

### 6.2 New Files to Create

**HA_CONFIGURATION_GUIDE.md:**

```markdown
# Home Assistant Configuration Guide

**Version:** 2025.10.01.01  
**Purpose:** Complete reference for Home Assistant integration configuration

---

## Overview

This guide covers all configuration options for the Home Assistant extension, including environment variables, Parameter Store values, entity exposure, and assistant name customization.

---

## Environment Variables

### Required Variables

**HOME_ASSISTANT_ENABLED**
- Type: Boolean
- Default: `false`
- Description: Master switch for Home Assistant integration
- Example: `HOME_ASSISTANT_ENABLED=true`

**HA_ASSISTANT_NAME**
- Type: String
- Default: `Home Assistant`
- Description: Name used for conversational commands
- Example: `HA_ASSISTANT_NAME=Bob`
- Usage: "Alexa, ask [HA_ASSISTANT_NAME] to turn on lights"
- **Important:** Must match Alexa Custom Skill invocation name

### Optional Variables

**HA_TIMEOUT**
- Type: Integer (seconds)
- Default: `30`
- Description: Maximum time to wait for HA responses
- Example: `HA_TIMEOUT=45`
- Adjust if: You see timeout errors or have slow network

**HA_VERIFY_SSL**
- Type: Boolean
- Default: `true`
- Description: Verify SSL certificates when connecting
- Example: `HA_VERIFY_SSL=false`
- **Warning:** Only set to `false` for local testing with self-signed certs

**HA_FEATURE_PRESET**
- Type: String
- Default: `full`
- Options: `minimal`, `voice_control`, `automation_basic`, `smart_home`, `full`
- Description: Controls which features are included in deployment
- Example: `HA_FEATURE_PRESET=smart_home`

**HA_CACHE_TTL**
- Type: Integer (seconds)
- Default: `300`
- Description: Cache duration for HA data
- Example: `HA_CACHE_TTL=600`
- Adjust to: Balance freshness vs. API call frequency

---

## Parameter Store Configuration

### Required Parameters

**/lambda-execution-engine/homeassistant/url**
- Type: String
- Description: Your Home Assistant instance URL
- Examples:
  - Local: `http://192.168.1.100:8123`
  - Nabu Casa: `https://xxxxx.ui.nabu.casa`
  - Custom domain: `https://home.yourdomain.com`

**/lambda-execution-engine/homeassistant/token**
- Type: SecureString
- Description: Long-lived access token
- Creation:
  1. HA → Profile → Long-Lived Access Tokens
  2. Create token with name "AWS Lambda Integration"
  3. Copy token immediately (won't be shown again)

### Optional Parameters

**/lambda-execution-engine/homeassistant/assistant_name**
- Type: String
- Default: `Home Assistant`
- Description: Assistant name for conversational commands
- Example: `Bob`, `Jarvis`, `Computer`

**/lambda-execution-engine/homeassistant/verify_ssl**
- Type: String
- Default: `true`
- Description: Override SSL verification setting
- Use case: Testing with self-signed certificates

**/lambda-execution-engine/homeassistant/timeout**
- Type: String (integer as string)
- Default: `30`
- Description: Override timeout setting
- Use case: Slow network or distant HA instance

---

## Entity Exposure Configuration

### Method 1: Nabu Casa Cloud (Recommended)

**Prerequisites:**
- Nabu Casa subscription ($6.50/month)
- Home Assistant Cloud integration enabled

**Steps:**
1. Go to Configuration → Cloud
2. Click "Alexa" tab
3. Select entities to expose
4. Click "Sync Entities"

**Advantages:**
- Simple configuration
- Automatic HTTPS setup
- No port forwarding required
- Entity filtering built-in

### Method 2: Manual Entity Exposure (Free)

**Prerequisites:**
- Home Assistant 2021.3+
- Direct HTTPS access to HA instance

**Steps:**
1. Go to Configuration → Entities
2. Select entity
3. Click entity settings (gear icon)
4. Enable "Expose to voice assistants"
5. Save changes

**Per-entity control:**
```yaml
# configuration.yaml (advanced)
homeassistant:
  customize:
    light.kitchen:
      cloud:
        alexa:
          should_expose: true
    light.bedroom:
      conversation:
        should_expose: true
```

### Method 3: Expose All (Not Recommended)

If entity registry is unavailable (HA < 2021.3), all entities are exposed by default. This is not recommended for security and privacy.

**To limit exposure:**
Use entity filtering in Home Assistant automations or scripts to hide sensitive entities.

---

## Conversation Agent Configuration

### Built-in Assist (Default)

Home Assistant's built-in conversation agent.

**Setup:**
- Enabled by default in HA 2023.3+
- No additional configuration required
- Free and privacy-focused

**Capabilities:**
- Device control
- State queries
- Basic automation
- Limited context understanding

### OpenAI Conversation

Enhanced natural language understanding via OpenAI API.

**Setup:**
1. Get OpenAI API key from platform.openai.com
2. Go to Configuration → Integrations
3. Add "OpenAI Conversation" integration
4. Enter API key
5. Set as default conversation agent

**Capabilities:**
- Advanced NLU
- Context awareness
- Complex queries
- Creative responses

**Cost:** OpenAI API charges apply (~$0.002 per conversation)

### Custom Conversation Agents

Any conversation integration can be used:
- Google Generative AI
- Local LLM (llama.cpp, Ollama)
- Custom Python integration

**Setup:**
1. Install conversation integration
2. Configure in Home Assistant
3. Set as default conversation agent
4. Lambda automatically uses it

**No code changes required** - Lambda uses HA's configured agent automatically.

---

## Assistant Name Customization

### Overview

By default, you invoke conversational commands with:
```
"Alexa, ask Home Assistant to turn on lights"
```

You can customize this to any name you prefer.

### Step-by-Step Customization

**Step 1: Choose Your Name**

Pick a name that follows Alexa's rules:
- ✅ Valid: "Bob", "My Assistant", "House Computer", "Jarvis"
- ❌ Invalid: "Alexa", "Echo", "The Assistant", "Skill"

**Rules:**
- Cannot contain: alexa, amazon, echo, skill, the
- Single words must be proper names (Bob, Jarvis)
- Must be 2+ words otherwise

**Step 2: Set Environment Variable**

```bash
# Lambda Environment Variable
HA_ASSISTANT_NAME=Bob
```

**OR** set in Parameter Store:
```
/lambda-execution-engine/homeassistant/assistant_name = Bob
```

**Step 3: Update Alexa Skill**

1. Open Alexa Developer Console
2. Select your Custom Skill
3. Go to "Invocation" section
4. Change "Skill Invocation Name" to your chosen name (lowercase)
5. Example: `bob` or `my assistant`
6. Click "Save Model"
7. Click "Build Model"
8. Wait for build to complete

**Step 4: Test**

```
"Alexa, ask Bob to turn on the lights"
"Alexa, tell Bob dinner is ready"
```

**Step 5: Verify Configuration**

Test the diagnostic endpoint:
```json
{
  "diagnostic": true
}
```

Check that `assistant_configuration.configured_name` matches your choice.

### Troubleshooting Custom Names

**"Alexa doesn't understand my invocation name"**
- Ensure name follows Alexa's rules (see above)
- Verify name matches in BOTH Lambda and Alexa Console
- Wait 5 minutes after Alexa skill changes
- Use lowercase in Alexa Console

**"Single word name doesn't work"**
- Alexa requires 2+ words unless it's a proper name
- Try: "My [Name]" or "[Name] Assistant"
- Examples: "My Bob" or "Bob Assistant"

**"Alexa says skill isn't responding"**
- Check Lambda logs in CloudWatch
- Verify HA_ASSISTANT_NAME is set correctly
- Test diagnostic endpoint
- Check Lambda function has Alexa trigger configured

---

## Nabu Casa vs. Direct Access

### Decision Matrix

| Feature | Nabu Casa Cloud | Direct HTTPS Access |
|---------|----------------|-------------------|
| **Cost** | $6.50/month | Free |
| **Setup Complexity** | Easy | Moderate-Hard |
| **Security** | Managed | Self-managed |
| **Remote Access** | Built-in | Configure yourself |
| **Port Forwarding** | Not needed | Required |
| **SSL Certificates** | Included | Must obtain (Let's Encrypt) |
| **Entity Exposure** | UI-based | Manual configuration |
| **Recommended For** | Beginners | Advanced users |

### Nabu Casa Cloud Setup

**Prerequisites:**
- Home Assistant Cloud subscription
- Home Assistant 2021.3+

**Steps:**
1. Subscribe at nabucasa.com
2. Enable Cloud integration in HA
3. Configure entity exposure
4. Use Nabu Casa URL in Lambda: `https://xxxxx.ui.nabu.casa`

**Advantages:**
- Zero networking knowledge required
- Automatic HTTPS
- Secure by default
- Supports HA development

### Direct HTTPS Access Setup

**Prerequisites:**
- Domain name
- Router access
- SSL certificate (Let's Encrypt)
- Networking knowledge

**Steps:**
1. Configure dynamic DNS
2. Set up port forwarding (443)
3. Install Let's Encrypt add-on in HA
4. Configure SSL in HA
5. Test external access
6. Use public URL in Lambda

**Advantages:**
- No recurring cost
- Full control
- No third-party dependency
- Learn networking concepts

**Security Requirements:**
- Strong passwords
- Fail2ban or similar
- Regular updates
- Firewall rules
- VPN recommended

---

## Feature Presets

### Minimal Preset

**Includes:**
- Device control via Smart Home API
- Entity exposure filtering
- Basic Alexa integration

**Excludes:**
- Conversation API
- Automations
- Scripts
- All advanced features

**Use Case:** Simple device control only

**Deployment Size:** ~60% smaller than full

### Voice Control Preset

**Includes:**
- Minimal preset features
- Conversation API support
- Natural language processing

**Use Case:** Device control + conversational AI

**Deployment Size:** ~50% smaller than full

### Automation Basic Preset

**Includes:**
- Voice Control preset features
- Automation triggering
- Script execution

**Use Case:** Voice control + automation management

**Deployment Size:** ~40% smaller than full

### Smart Home Preset

**Includes:**
- Automation Basic preset features
- Input helper management
- TTS announcements
- Area control

**Use Case:** Comprehensive smart home control

**Deployment Size:** ~20% smaller than full

### Full Preset (Default)

**Includes:**
- All Smart Home preset features
- Timer management
- All current and future features

**Use Case:** Complete feature set

**Deployment Size:** Full size (still under 50MB)

### Changing Presets

**Method 1: Environment Variable**
```bash
HA_FEATURE_PRESET=smart_home
```

**Method 2: Build Time**
```bash
python build_package.py --preset smart_home --output lambda_smart_home.zip
```

**Method 3: Parameter Store**
```
/lambda-execution-engine/homeassistant/feature_preset = smart_home
```

---

## Advanced Configuration

### SSL Certificate Verification

**When to Disable:**
- Local testing with self-signed certificates
- Development environment only
- Temporary troubleshooting

**How to Disable:**
```bash
HA_VERIFY_SSL=false
```

**Security Warning:** Never disable for production internet-accessible instances.

**Better Alternative:** Use valid Let's Encrypt certificates (free).

### Timeout Tuning

**Default:** 30 seconds

**Increase When:**
- Home Assistant on slow hardware
- High network latency
- Complex automations take time
- Frequent timeout errors

**Decrease When:**
- Want faster failure detection
- HA is fast and reliable
- Optimizing for speed

**Example:**
```bash
HA_TIMEOUT=45  # Slow HA instance
HA_TIMEOUT=15  # Fast local HA
```

### Cache TTL Optimization

**Default:** 300 seconds (5 minutes)

**Increase To:**
- Reduce API calls to HA
- Improve Lambda performance
- Lower HA load
- Static entity lists

**Decrease To:**
- More real-time updates
- Frequently changing entities
- Testing changes
- Dynamic environments

**Example:**
```bash
HA_CACHE_TTL=600   # Less frequent updates OK
HA_CACHE_TTL=60    # Need fresh data often
```

**What Gets Cached:**
- Entity lists
- Automation lists
- Script lists
- Area data
- Media player lists
- Timer lists

**Not Cached:**
- Entity states (always fresh)
- Service call results
- Real-time data

---

## Troubleshooting

### Configuration Issues

**Problem:** "HA extension disabled"
**Solution:** Set `HOME_ASSISTANT_ENABLED=true`

**Problem:** "Cannot connect to Home Assistant"
**Solutions:**
- Verify URL is correct and accessible
- Check token is valid
- Test URL from AWS (try EC2 instance in same region)
- Verify SSL certificate (or disable verification for testing)

**Problem:** "Assistant name doesn't work"
**Solutions:**
- Check HA_ASSISTANT_NAME matches Alexa invocation name
- Verify no forbidden words (alexa, amazon, echo, skill, the)
- Wait 5 minutes after Alexa skill changes
- Review diagnostic endpoint output

**Problem:** "Entities not discovered"
**Solutions:**
- Verify entities are exposed (Method 1 or 2)
- Check HA version supports entity exposure (2021.3+)
- Run Alexa device discovery again
- Check CloudWatch logs for errors

### Performance Issues

**Problem:** "Slow responses"
**Solutions:**
- Check HA response times
- Review cache hit rates in metrics
- Increase cache TTL
- Check network latency to HA
- Review Lambda cold start times

**Problem:** "Frequent timeouts"
**Solutions:**
- Increase HA_TIMEOUT
- Check HA server performance
- Verify network stability
- Review HA logs for slow operations

### Conversation Issues

**Problem:** "Conversation doesn't work"
**Solutions:**
- Verify Conversation integration enabled in HA
- Test conversation directly in HA UI
- Check conversation agent is configured
- Review Lambda logs for API errors

**Problem:** "Responses not making sense"
**Solutions:**
- Check which conversation agent is active
- Try OpenAI Conversation for better NLU
- Review conversation agent configuration
- Test queries directly in HA

---

## Best Practices

### Security

1. **Always use HTTPS** for internet-accessible HA
2. **Use SecureString** for tokens in Parameter Store
3. **Enable SSL verification** except for local testing
4. **Rotate tokens** annually
5. **Limit entity exposure** to only needed devices
6. **Use strong passwords** on HA
7. **Keep HA updated** for security patches

### Performance

1. **Use appropriate cache TTL** for your use case
2. **Expose only needed entities** to reduce discovery payload
3. **Monitor cache hit rates** and adjust as needed
4. **Use feature presets** if not all features needed
5. **Keep HA responsive** for best Lambda performance

### Reliability

1. **Use Nabu Casa** for easiest setup
2. **Monitor CloudWatch logs** for errors
3. **Set up billing alerts** for AWS costs
4. **Test regularly** to catch issues early
5. **Keep backups** of configuration

### Maintenance

1. **Review logs monthly** for issues
2. **Update Lambda runtime** when notified
3. **Rotate tokens annually**
4. **Check AWS Free Tier usage**
5. **Test after HA updates**

---

## Configuration Examples

### Minimal Setup (Local Testing)

```bash
# Environment Variables
HOME_ASSISTANT_ENABLED=true
HA_ASSISTANT_NAME=Home Assistant
HA_TIMEOUT=30
HA_VERIFY_SSL=false
HA_FEATURE_PRESET=minimal
```

```
# Parameter Store
/lambda-execution-engine/homeassistant/url = http://192.168.1.100:8123
/lambda-execution-engine/homeassistant/token = [SecureString] eyJ0eXAi...
```

### Production Setup (Nabu Casa)

```bash
# Environment Variables
HOME_ASSISTANT_ENABLED=true
HA_ASSISTANT_NAME=Home Assistant
HA_TIMEOUT=30
HA_VERIFY_SSL=true
HA_FEATURE_PRESET=full
HA_CACHE_TTL=300
```

```
# Parameter Store
/lambda-execution-engine/homeassistant/url = https://xxxxx.ui.nabu.casa
/lambda-execution-engine/homeassistant/token = [SecureString] eyJ0eXAi...
```

### Custom Name Setup

```bash
# Environment Variables
HOME_ASSISTANT_ENABLED=true
HA_ASSISTANT_NAME=Jarvis
HA_TIMEOUT=30
HA_VERIFY_SSL=true
HA_FEATURE_PRESET=full
```

```
# Parameter Store
/lambda-execution-engine/homeassistant/url = https://home.mydomain.com
/lambda-execution-engine/homeassistant/token = [SecureString] eyJ0eXAi...
/lambda-execution-engine/homeassistant/assistant_name = Jarvis
```

```
# Alexa Custom Skill
Invocation Name: jarvis
```

### High-Performance Setup

```bash
# Environment Variables
HOME_ASSISTANT_ENABLED=true
HA_ASSISTANT_NAME=Home Assistant
HA_TIMEOUT=15
HA_VERIFY_SSL=true
HA_FEATURE_PRESET=full
HA_CACHE_TTL=600
```

---

## Summary

This configuration guide covers all aspects of Home Assistant integration setup. Start with the minimal setup for testing, then progress to production configuration with appropriate security and performance settings.

For most users, the default values with Nabu Casa Cloud provide the best balance of ease-of-use and functionality.

#EOF
```

---

## Phase 7: Implementation Checklist

### 7.1 Code Changes

- [ ] Update `homeassistant_extension.py`
  - [ ] Add `get_ha_assistant_name()` function
  - [ ] Add `validate_ha_assistant_configuration()` function
  - [ ] Update `initialize_ha_extension()` to validate assistant config
  - [ ] Add assistant name to initialization response

- [ ] Update `lambda_function.py`
  - [ ] Import `get_ha_assistant_name` in conversation handler
  - [ ] Log assistant name in conversation intent
  - [ ] Add `_handle_diagnostic_request()` function
  - [ ] Update `lambda_handler()` to support diagnostic requests
  - [ ] Use assistant name in error messages

- [ ] Create `test_ha_assistant_config.py`
  - [ ] Add default name test
  - [ ] Add custom name test
  - [ ] Add validation tests
  - [ ] Add diagnostic endpoint test

- [ ] Update `build_config.py`
  - [ ] Add `validate_assistant_configuration()` function
  - [ ] Add validation to build process

- [ ] Update `deploy_automation.py`
  - [ ] Add assistant name validation
  - [ ] Log assistant configuration

### 7.2 Documentation Changes

- [ ] Update `README.md`
  - [ ] Add "Home Assistant Configuration" section
  - [ ] Update "Alexa Skill Integration" section
  - [ ] Add Nabu Casa vs. Assist clarification
  - [ ] Add assistant name customization guide

- [ ] Update `Install_Guide.MD`
  - [ ] Update Phase 3: Parameter Store
  - [ ] Update Phase 5: Environment Variables  
  - [ ] Add Phase 6B: Custom Skill Setup
  - [ ] Add assistant name customization steps

- [ ] Update `PROJECT_ARCHITECTURE_REFERENCE.md`
  - [ ] Document `HA_ASSISTANT_NAME` variable
  - [ ] Document `get_ha_assistant_name()` function
  - [ ] Document `validate_ha_assistant_configuration()` function
  - [ ] Update environment variable reference

- [ ] Create `HA_CONFIGURATION_GUIDE.md`
  - [ ] Complete configuration reference
  - [ ] All environment variables documented
  - [ ] All Parameter Store values documented
  - [ ] Entity exposure methods
  - [ ] Conversation agent setup
  - [ ] Assistant name customization
  - [ ] Troubleshooting guide

### 7.3 Testing

- [ ] Unit Tests
  - [ ] Test default assistant name
  - [ ] Test custom assistant name from env
  - [ ] Test validation with single-word names
  - [ ] Test validation with forbidden words
  - [ ] Test validation with valid names
  - [ ] Test lowercase conversion

- [ ] Integration Tests
  - [ ] Test conversation intent with default name
  - [ ] Test conversation intent with custom name
  - [ ] Test diagnostic endpoint
  - [ ] Test LaunchRequest response

- [ ] Manual Testing
  - [ ] Deploy with default name
  - [ ] Test "Alexa, ask Home Assistant..."
  - [ ] Change to custom name
  - [ ] Update Alexa skill invocation name
  - [ ] Test "Alexa, ask [CustomName]..."
  - [ ] Verify diagnostic endpoint works
  - [ ] Check CloudWatch logs show correct name

### 7.4 Validation

- [ ] Documentation Review
  - [ ] All new sections accurate
  - [ ] No broken links
  - [ ] Examples are correct
  - [ ] Troubleshooting is complete

- [ ] Code Review
  - [ ] Follows gateway pattern
  - [ ] Proper error handling
  - [ ] Logging is appropriate
  - [ ] No breaking changes

- [ ] User Experience
  - [ ] Clear instructions
  - [ ] Easy to customize
  - [ ] Good error messages
  - [ ] Helpful diagnostics

---

## Phase 8: Deployment Strategy

### 8.1 Rollout Plan

**Stage 1: Code Implementation (Week 1)**
- Implement all code changes
- Add validation functions
- Create diagnostic endpoint
- Write unit tests

**Stage 2: Documentation (Week 1-2)**
- Update README.m# Documentation & Configuration Enhancement Plan
## Home Assistant Integration Clarifications

**Version:** 2025.10.01.01  
**Purpose:** Address missing documentation and add configurable assistant name support  
**Priority:** HIGH - User confusion about Nabu Casa, Assist, and invocation names

---

## Executive Summary

### Issues Identified

1. **README.md** lacks Home Assistant configuration reference
2. **Nabu Casa vs. Assist confusion** - Documentation doesn't clarify the difference
3. **Hardcoded invocation name** - "Home Assistant" is assumed, not configurable
4. **Missing environment variables** - Several HA-specific variables not documented

### Proposed Solutions

1. Add comprehensive HA Configuration Reference to README.md
2. Create clear Nabu Casa vs. Assist explanation
3. Implement `HA_ASSISTANT_NAME` environment variable
4. Update Install_Guide.MD with complete configuration options
5. Add validation and helpful logging for assistant name configuration

---

## Phase 1: README.md Enhancements

### 1.1 Add Home Assistant Configuration Section

**Location:** After "Configuration" section, before "Alexa Skill Integration"

**New Section Content:**

```markdown
### Home Assistant Configuration

The Home Assistant extension provides comprehensive smart home control through both Alexa Smart Home API (device control) and Custom Skill (conversational AI). Understanding the configuration options ensures optimal integration.

#### Required Configuration

**Environment Variables:**
- `HOME_ASSISTANT_ENABLED` - Set to `true` to enable HA integration
- `HA_ASSISTANT_NAME` - Invocation name for conversational commands (default: "Home Assistant")

**AWS Parameter Store:**
- `/lambda-execution-engine/homeassistant/url` - Your HA instance URL
- `/lambda-execution-engine/homeassistant/token` - Long-lived access token (SecureString)

#### Optional Configuration

**Environment Variables:**
- `HA_TIMEOUT` - Request timeout in seconds (default: 30)
- `HA_VERIFY_SSL` - SSL certificate verification (default: true)
- `HA_FEATURE_PRESET` - Feature subset selection (default: full)
  - Options: `minimal`, `voice_control`, `automation_basic`, `smart_home`, `full`
- `HA_CACHE_TTL` - Cache duration in seconds (default: 300)

**Parameter Store (Optional):**
- `/lambda-execution-engine/homeassistant/verify_ssl` - Override SSL verification
- `/lambda-execution-engine/homeassistant/timeout` - Override timeout setting

#### Home Assistant Instance Requirements

**Minimum Version:** Home Assistant 2021.3+ (for entity registry support)

**Required Integrations:**
- **Conversation** - For natural language processing via Custom Skill
- **Cloud (Nabu Casa)** - Optional, for entity exposure configuration
  - OR manual entity exposure via `should_expose` attributes

**Recommended Setup:**
- Long-lived access token with appropriate permissions
- HTTPS with valid SSL certificate (or `HA_VERIFY_SSL=false` for local testing)
- Exposed entities for voice control (see Entity Exposure below)

#### Entity Exposure Methods

**Method 1: Nabu Casa Cloud (Easiest)**
If you have a Nabu Casa subscription:
1. Go to Configuration → Cloud → Alexa
2. Select which entities to expose
3. Entities automatically filtered by Lambda function

**Method 2: Manual Exposure (No Nabu Casa Required)**
Without Nabu Casa, expose entities manually:
1. Go to Configuration → Entities
2. Select entity → Settings
3. Enable "Expose to voice assistants"

**Method 3: Expose All Entities (Not Recommended)**
The system will expose all entities if entity registry unavailable (HA < 2021.3).

#### Understanding Nabu Casa vs. Assist

**Common Confusion Clarified:**

**Nabu Casa Cloud:**
- Paid subscription service ($6.50/month)
- Provides secure remote access to Home Assistant
- Enables Alexa Smart Home integration without port forwarding
- Handles entity exposure configuration
- **NOT required** for this Lambda integration if you have direct HTTPS access

**Home Assistant Assist:**
- Built-in conversation agent (FREE)
- Local natural language processing
- Can use various AI backends (OpenAI, local models, etc.)
- This is what powers the "Alexa, ask [AssistantName]..." commands
- Works with any conversation agent you configure

**What This Integration Uses:**
- **Smart Home API** (device control) → Uses entity exposure settings
- **Conversation API** (natural language) → Uses your configured conversation agent (Assist or other)

**Bottom Line:** You can use this integration with or without Nabu Casa. You need either:
- Nabu Casa Cloud (easiest setup)
- OR direct HTTPS access to your HA instance (requires network configuration)

#### Conversation Agent Configuration

The Custom Skill integration works with any Home Assistant conversation agent:

**Built-in Assist (Default):**
- No additional configuration needed
- Uses Home Assistant's local conversation processing
- Free and privacy-focused

**OpenAI Conversation:**
- More advanced natural language understanding
- Requires OpenAI API key
- Configure in Configuration → Integrations → OpenAI Conversation

**Custom Agent ("Bob" Example):**
- Install and configure any conversation integration
- Set as default conversation agent in HA
- Update `HA_ASSISTANT_NAME` environment variable to match
- Update Alexa Skill invocation name to match (see Customization below)

**Agent Selection:** The system automatically uses whichever conversation agent is set as default in Home Assistant. No code changes required.

#### Customizing the Assistant Name

By default, you invoke conversational commands with:
```
"Alexa, ask Home Assistant to turn on the lights"
```

**To customize the name (e.g., "Bob"):**

**Step 1: Set Environment Variable**
```bash
HA_ASSISTANT_NAME=Bob
```

**Step 2: Update Alexa Skill Invocation Name**
1. Open Alexa Developer Console
2. Select your skill
3. Go to "Invocation" settings
4. Change "Skill Invocation Name" to "bob"
5. Save and rebuild skill

**Step 3: Use New Name**
```
"Alexa, ask Bob to turn on the lights"
```

**Important Notes:**
- Alexa invocation names must be lowercase
- Multi-word names require specific formatting (check Alexa guidelines)
- Invocation name must be changed in BOTH environment variable AND Alexa console
- Changes take ~5 minutes to propagate

#### Feature Presets

Control which Home Assistant features are included in your deployment:

**Preset Options:**
- `minimal` - Basic device control only (smallest deployment)
- `voice_control` - Device control + conversation
- `automation_basic` - Adds automation and script execution
- `smart_home` - Adds input helpers, notifications, area control
- `full` - All features including timers (default, recommended)

**To Change Preset:**
```bash
# Environment Variable
HA_FEATURE_PRESET=smart_home

# Rebuild and deploy
python build_package.py --preset smart_home --output lambda_smart_home.zip
```

See `build_config.py` for detailed feature breakdown.

#### Troubleshooting Configuration

**"Alexa can't find my devices"**
- Verify entities are exposed (Method 1 or 2 above)
- Run device discovery in Alexa app
- Check CloudWatch logs for discovery errors
- Verify HA token has sufficient permissions

**"Alexa doesn't understand conversational commands"**
- Verify Conversation integration enabled in HA
- Check HA_ASSISTANT_NAME matches Alexa skill invocation name
- Test conversation directly in HA first
- Review Lambda logs for conversation errors

**"Connection to Home Assistant failed"**
- Verify HA URL is accessible from AWS (test with curl from EC2 instance)
- Check SSL certificate validity (or set HA_VERIFY_SSL=false for testing)
- Verify long-lived access token is valid
- Check timeout settings if HA is slow to respond

**"Assistant name doesn't work"**
- Environment variable: `HA_ASSISTANT_NAME=YourName`
- Alexa Developer Console: Skill invocation name must match
- Wait 5 minutes after Alexa skill changes
- Say "Alexa, ask [YourName]..." not just "[YourName]"
```

---

### 1.2 Update "Alexa Skill Integration" Section

**Replace existing text with enhanced version:**

```markdown
### Alexa Skill Integration

After deploying the Lambda function, you create **two types of Alexa skills** that work together:

#### Smart Home Skill (Device Control)

**Purpose:** Control individual devices by name
**Example Commands:**
- "Alexa, turn on the kitchen lights"
- "Alexa, set bedroom temperature to 72"
- "Alexa, lock the front door"

**Setup:**
1. Create Smart Home skill in Amazon Developer Console
2. Link to Lambda function ARN
3. Configure account linking (if using authentication)
4. Run device discovery in Alexa app

**How It Works:**
- Uses Alexa Smart Home API
- Exposes Home Assistant entities as Alexa devices
- Direct device control (no invocation name needed)
- Works with exposed entities only (see Configuration above)

#### Custom Skill (Conversational AI)

**Purpose:** Natural language commands and queries
**Default Commands:**
- "Alexa, ask Home Assistant to turn on all the lights"
- "Alexa, tell Home Assistant dinner is ready"
- "Alexa, ask Home Assistant what's the temperature"

**Customized Commands (if you set `HA_ASSISTANT_NAME=Bob`):**
- "Alexa, ask Bob to turn on all the lights"
- "Alexa, tell Bob dinner is ready"
- "Alexa, ask Bob what's the temperature"

**Setup:**
1. Create Custom Skill in Amazon Developer Console
2. Set invocation name (default: "home assistant", or your custom name)
3. Configure intents (TalkToHomeAssistant, TriggerAutomation, etc.)
4. Link to Lambda function ARN
5. Enable for testing

**How It Works:**
- Uses Alexa Custom Skill API
- Processes natural language through Home Assistant Conversation API
- Works with any conversation agent (Assist, OpenAI, custom)
- Requires invocation name: "Alexa, ask [Name]..."

#### Why Both Skills?

**Smart Home Skill:**
- ✅ Simple device control
- ✅ No invocation name needed
- ✅ Works with Alexa routines
- ❌ Limited to exposed devices
- ❌ No complex commands

**Custom Skill:**
- ✅ Natural language understanding
- ✅ Complex multi-device commands
- ✅ Triggers automations and scripts
- ✅ Conversational AI capabilities
- ❌ Requires invocation name
- ❌ Cannot be used in routines

**Recommendation:** Enable both for maximum flexibility. Use Smart Home for simple device control, Custom Skill for complex commands and conversations.
```

---

## Phase 2: Install_Guide.MD Updates

### 2.1 Update Phase 3: AWS Systems Manager Setup

**Add to "Step 5: Create Configuration Parameters" section:**

```markdown
**Home Assistant Assistant Name Parameter:**

Click **"Create parameter"**

**Parameter name:** `/lambda-execution-engine/homeassistant/assistant_name`
**Type:** String
**Value:** `Home Assistant` (or your preferred name like `Bob`, `Assistant`, `Jarvis`)
**Description:** The name you'll use to invoke conversational commands

**What this controls:**
This is the name you'll say when using conversational commands:
- "Alexa, ask **[AssistantName]** to turn on the lights"
- "Alexa, tell **[AssistantName]** dinner is ready"

**Important:** You must also set this same name as the "Skill Invocation Name" when creating your Alexa Custom Skill in Phase 6. The names must match exactly (though Alexa converts to lowercase).

**Examples:**
- `Home Assistant` → "Alexa, ask Home Assistant..."
- `Bob` → "Alexa, ask Bob..."
- `House` → "Alexa, ask House..."
- `Computer` → "Alexa, ask Computer..."

**Alexa Invocation Name Rules:**
- Must be 2+ words (exception: proper names like "Bob")
- Cannot be a single word unless it's a proper name
- Cannot include: "the", "alexa", "amazon", "echo", "skill"
- Must be lowercase when configured in Alexa
- Cannot sound like existing Alexa commands

**Recommended Approach:**
For simplicity, use the default "Home Assistant" when first setting up. You can change it later once everything works.

Click **"Create parameter"**

---

**Optional SSL Verification Parameter:**

If your Home Assistant instance uses a self-signed certificate or you're testing locally:

Click **"Create parameter"**

**Parameter name:** `/lambda-execution-engine/homeassistant/verify_ssl`
**Type:** String
**Value:** `false` (only for testing/development)
**Description:** Disable SSL certificate verification (NOT recommended for production)

**Security Warning:** Only set this to `false` if you're testing locally and understand the security implications. For production use with internet-accessible Home Assistant, always use valid SSL certificates and keep this `true`.

Click **"Create parameter"**

---

**Optional Timeout Parameter:**

If your Home Assistant instance is slow to respond:

Click **"Create parameter"**

**Parameter name:** `/lambda-execution-engine/homeassistant/timeout`
**Type:** String
**Value:** `30` (seconds)
**Description:** Maximum time to wait for Home Assistant responses

**When to adjust:**
- Increase if you see timeout errors in CloudWatch logs
- Decrease if you want faster failure detection
- Default of 30 seconds works for most setups

Click **"Create parameter"**
```

---

### 2.2 Update Phase 5: Step 6: Configure Environment Variables

**Replace the "Feature Flags" section with:**

```markdown
**Feature Flags:**
- Key: `HOME_ASSISTANT_ENABLED`, Value: `true`
- Key: `ALEXA_SKILL_ENABLED`, Value: `true`
- Key: `DEBUG_MODE`, Value: `false`

**Home Assistant Configuration:**
- Key: `HA_ASSISTANT_NAME`, Value: `Home Assistant`
- Key: `HA_TIMEOUT`, Value: `30`
- Key: `HA_VERIFY_SSL`, Value: `true`
- Key: `HA_FEATURE_PRESET`, Value: `full`
- Key: `HA_CACHE_TTL`, Value: `300`

Click **"Save"**

**What these Home Assistant variables do:**

**HA_ASSISTANT_NAME:**
- The name you'll use for conversational commands
- Example: "Alexa, ask [AssistantName] to..."
- Must match your Alexa Custom Skill invocation name
- Can be customized to any name you prefer

**HA_TIMEOUT:**
- Maximum seconds to wait for Home Assistant responses
- Default: 30 seconds
- Increase if your HA instance is slow or on a slow network
- Decrease for faster failure detection

**HA_VERIFY_SSL:**
- Whether to verify SSL certificates when connecting to HA
- Set to `false` only for local testing with self-signed certs
- Always `true` for production with valid certificates
- Security risk if disabled on internet-accessible instances

**HA_FEATURE_PRESET:**
- Controls which HA features are included
- Options: minimal, voice_control, automation_basic, smart_home, full
- Use `minimal` for smallest deployment
- Use `full` for all features (recommended)

**HA_CACHE_TTL:**
- How long to cache Home Assistant data (in seconds)
- Default: 300 (5 minutes)
- Increase to reduce API calls to HA
- Decrease for more real-time updates
- Affects: entity lists, automation lists, script lists, area data
```

---

### 2.3 Update Phase 6: Alexa Skill Setup

**Add new subsection after "Step 2: Create New Skill":**

```markdown
### **Step 2.5: Important - Skill Type Clarification**

You will create **TWO separate skills**:

**Skill 1: Smart Home Skill** (for device control)
- Type: "Smart Home"
- Controls individual devices by name
- No invocation name needed
- Example: "Alexa, turn on kitchen lights"

**Skill 2: Custom Skill** (for conversations)
- Type: "Custom"
- Handles natural language and complex commands
- Requires invocation name
- Example: "Alexa, ask [AssistantName] to turn on all lights"

**We're setting up the Smart Home skill first.** Continue below for Smart Home setup, then we'll add the Custom Skill setup steps.
```

---

**Add new section after current Phase 6:**

```markdown
## Ã°Å¸Â—£ï¸ **Phase 6B: Alexa Custom Skill Setup (Conversational AI)**

Now we'll create the Custom Skill that enables conversational commands with your Home Assistant.

### **Step 1: Create Custom Skill**

Back in the Alexa Developer Console (developer.amazon.com/alexa/console/ask):

Click **"Create Skill"** button (to create a second skill)

**Skill name:** Enter the name from your `HA_ASSISTANT_NAME` parameter
- If you used "Home Assistant": Enter "Home Assistant Voice Control"
- If you used "Bob": Enter "Bob Assistant"
- This is just the display name, not what you say

**Default language:** Select your language (typically **English (US)**)

**Choose a model:** Select **"Custom"** (NOT Smart Home this time)

**Choose a method:** Select **"Provision your own"**

Click **"Create skill"**

**Choose a template:** Select **"Start from scratch"**

Click **"Continue with template"**

### **Step 2: Configure Invocation Name**

This is critical - the invocation name is what you say to Alexa.

In the left sidebar, click **"Invocation"** under "Skill builder"

**Skill Invocation Name:** Enter your assistant name in lowercase
- If using "Home Assistant": Enter `home assistant`
- If using "Bob": Enter `bob`
- If using "House": Enter `house`

**Must match your `HA_ASSISTANT_NAME` exactly** (but lowercase)

Click **"Save Model"** at the top

### **Step 3: Create Intents**

We need to add the intents that handle different types of commands.

Click **"Interaction Model"** → **"JSON Editor"** in the left sidebar

Replace the entire JSON with this:

```json
{
  "interactionModel": {
    "languageModel": {
      "invocationName": "home assistant",
      "intents": [
        {
          "name": "TalkToHomeAssistant",
          "slots": [
            {
              "name": "query",
              "type": "AMAZON.SearchQuery"
            }
          ],
          "samples": [
            "{query}",
            "to {query}",
            "ask {query}",
            "tell {query}"
          ]
        },
        {
          "name": "TriggerAutomation",
          "slots": [
            {
              "name": "AutomationName",
              "type": "AMAZON.SearchQuery"
            }
          ],
          "samples": [
            "trigger {AutomationName}",
            "run {AutomationName} automation",
            "trigger automation {AutomationName}",
            "activate {AutomationName}"
          ]
        },
        {
          "name": "RunScript",
          "slots": [
            {
              "name": "ScriptName",
              "type": "AMAZON.SearchQuery"
            }
          ],
          "samples": [
            "run {ScriptName}",
            "execute {ScriptName} script",
            "run script {ScriptName}",
            "start {ScriptName}"
          ]
        },
        {
          "name": "SetInputHelper",
          "slots": [
            {
              "name": "HelperName",
              "type": "AMAZON.SearchQuery"
            },
            {
              "name": "HelperValue",
              "type": "AMAZON.SearchQuery"
            }
          ],
          "samples": [
            "set {HelperName} to {HelperValue}",
            "turn {HelperValue} {HelperName}",
            "change {HelperName} to {HelperValue}"
          ]
        },
        {
          "name": "MakeAnnouncement",
          "slots": [
            {
              "name": "Message",
              "type": "AMAZON.SearchQuery"
            }
          ],
          "samples": [
            "announce {Message}",
            "say {Message} to everyone",
            "broadcast {Message}"
          ]
        },
        {
          "name": "ControlArea",
          "slots": [
            {
              "name": "AreaName",
              "type": "AMAZON.SearchQuery"
            },
            {
              "name": "Action",
              "type": "AMAZON.SearchQuery"
            }
          ],
          "samples": [
            "turn {Action} everything in {AreaName}",
            "turn {Action} all {AreaName} devices",
            "{Action} everything in the {AreaName}"
          ]
        },
        {
          "name": "ManageTimer",
          "slots": [
            {
              "name": "TimerAction",
              "type": "AMAZON.SearchQuery"
            },
            {
              "name": "TimerName",
              "type": "AMAZON.SearchQuery"
            },
            {
              "name": "Duration",
              "type": "AMAZON.SearchQuery"
            }
          ],
          "samples": [
            "{TimerAction} {Duration} timer for {TimerName}",
            "{TimerAction} {TimerName} timer",
            "{Duration} timer for {TimerName}"
          ]
        },
        {
          "name": "AMAZON.CancelIntent",
          "samples": []
        },
        {
          "name": "AMAZON.HelpIntent",
          "samples": []
        },
        {
          "name": "AMAZON.StopIntent",
          "samples": []
        }
      ]
    }
  }
}
```

**IMPORTANT:** Change the `"invocationName"` value to match your assistant name (lowercase).

Click **"Save Model"** at the top

Click **"Build Model"** button

Wait for the build to complete (~30 seconds)

### **Step 4: Configure Endpoint**

Click **"Endpoint"** in the left sidebar

**Service Endpoint Type:** Select **"AWS Lambda ARN"**

**Default Region:** Paste your Lambda function ARN
- (Same ARN you used for Smart Home skill)

**Paste your Lambda ARN here:** (Copy from Lambda function page)

Click **"Save Endpoints"**

### **Step 5: Enable Testing**

Click **"Test"** tab at the top

**Skill testing is enabled in:** Change from "Off" to **"Development"**

Your Custom Skill is now enabled for testing!

### **Step 6: Test the Custom Skill**

In the test page, try typing or speaking:

**Test Conversational Command:**
```
ask [your assistant name] to turn on the lights
```

For example:
- "ask home assistant to turn on the lights" (if using default)
- "ask bob to turn on the lights" (if using Bob)

You should see a response from your Home Assistant conversation agent.

### **Step 7: Test on Your Alexa Device**

Now try on your actual Echo device:

```
"Alexa, ask [AssistantName] to turn on the lights"
"Alexa, tell [AssistantName] dinner is ready"
"Alexa, ask [AssistantName] what's the temperature"
```

**First time may be slower** as Lambda cold-starts. Subsequent requests will be faster.

### **Understanding What You've Built**

You now have **TWO ways** to control Home Assistant through Alexa:

**Direct Device Control (Smart Home Skill):**
```
"Alexa, turn on kitchen lights"
"Alexa, set bedroom temperature to 72"
```
- No invocation name needed
- Direct device control
- Fast and simple
- Limited to exposed devices

**Conversational AI (Custom Skill):**
```
"Alexa, ask [AssistantName] to turn on all the lights"
"Alexa, tell [AssistantName] dinner is ready"
```
- Requires invocation name
- Natural language understanding
- Complex commands possible
- Powered by Home Assistant Conversation API

**Use Both:** They complement each other perfectly. Use direct control for simple commands, conversational AI for complex scenarios.
```

---

## Phase 3: Code Enhancements

### 3.1 Add HA_ASSISTANT_NAME Support to homeassistant_extension.py

**Add to initialization section:**

```python
def get_ha_assistant_name() -> str:
    """Get configured Home Assistant assistant name."""
    import os
    
    # Try environment variable first
    name = os.getenv('HA_ASSISTANT_NAME')
    if name:
        return name
    
    # Try Parameter Store
    try:
        from gateway import execute_operation, GatewayInterface
        result = execute_operation(
            GatewayInterface.CONFIG,
            "get_parameter",
            parameter_name="/lambda-execution-engine/homeassistant/assistant_name"
        )
        if result and result.get('success'):
            return result.get('value', 'Home Assistant')
    except:
        pass
    
    # Default
    return 'Home Assistant'
```

**Add validation function:**

```python
def validate_ha_assistant_configuration() -> Dict[str, Any]:
    """Validate Home Assistant assistant name configuration."""
    from gateway import log_info, log_warning
    
    assistant_name = get_ha_assistant_name()
    
    # Log the configured name
    log_info(f"Home Assistant assistant name configured as: {assistant_name}")
    
    validation = {
        "configured_name": assistant_name,
        "lowercase_name": assistant_name.lower(),
        "warnings": []
    }
    
    # Check for common issues
    if assistant_name == "Home Assistant":
        validation["is_default"] = True
    else:
        validation["is_default"] = False
        validation["warnings"].append(
            f"Custom assistant name '{assistant_name}' configured. "
            f"Ensure Alexa Custom Skill invocation name is set to '{assistant_name.lower()}'"
        )
    
    # Check for Alexa invocation name rules
    words = assistant_name.split()
    if len(words) == 1 and assistant_name.lower() not in ['bob', 'hal', 'jarvis']:
        validation["warnings"].append(
            f"Single-word invocation name '{assistant_name}' may not work. "
            "Alexa requires 2+ words unless it's a recognized proper name."
        )
    
    forbidden_words = ['alexa', 'amazon', 'echo', 'skill', 'the']
    for word in words:
        if word.lower() in forbidden_words:
            validation["warnings"].append(
                f"Invocation name contains forbidden word '{word}'. "
                "Alexa doesn't allow: alexa, amazon, echo, skill, the"
            )
    
    # Log warnings
    for warning in validation["warnings"]:
        log_warning(f"Assistant name validation: {warning}")
    
    return validation
```

**Add to initialize_ha_extension():**

```python
def initialize_ha_extension() -> Dict[str, Any]:
    """Initialize Home Assistant extension."""
    try:
        correlation_id = generate_correlation_id()
        log_info(f"Initializing HA extension [{correlation_id}]")
        
        if not is_ha_extension_enabled():
            return create_error_response("HA extension disabled", {
                "correlation_id": correlation_id
            })
        
        # Validate assistant configuration
        validation = validate_ha_assistant_configuration()
        
        # ... rest of existing initialization code ...
        
        return create_success_response("HA extension initialized", {
            "correlation_id": correlation_id,
            "assistant_name": validation["configured_name"],
            "assistant_warnings": validation["warnings"]
        })
        
    except Exception as e:
        log_error(f"HA extension initialization failed: {str(e)}")
        return create_error_response("Initialization failed", {"error": str(e)})
```

---

### 3.2 Update lambda_function.py Logging

**Add to _handle_conversation_intent():**

```python
def _handle_conversation_intent(event: Dict[str, Any]) -> Dict[str, Any]:
    """Handle conversation with Home Assistant."""
    try:
        from homeassistant_extension import (
            process_alexa_conversation,
            get_ha_assistant_name
        )
        
        # Get configured assistant name
        assistant_name = get_ha_assistant_name()
        
        # Log for debugging
        log_info(f"Processing conversation intent for assistant: {assistant_name}")
        
        # ... rest of existing code ...
        
    except Exception as e:
        log_error(f"Conversation intent failed: {str(e)}")
        return _create_custom_skill_response(
            f"Sorry, {get_ha_assistant_name()} encountered an error."
        )
```

---

### 3.3 Add Diagnostic Endpoint

**Add to lambda_function.py:**

```python
def _handle_diagnostic_request(event: Dict[str, Any]) -> Dict[str, Any]:
    """Handle diagnostic information request."""
    try:
        from homeassistant_extension import (
            get_ha_assistant_name,
            validate_ha_assistant_configuration,
            is_ha_extension_enabled
        )
        
        diagnostics = {
            "ha_enabled": is_ha_extension_enabled(),
            "assistant_configuration": validate_ha_assistant_configuration(),
            "timestamp": time.time()
        }
        
        return {
            "statusCode": 200,
            "body": json.dumps(diagnostics, indent=2),
            "headers": {
                "Content-Type": "application/json"
            }
        }
        
    except Exception as e:
        log_error(f"Diagnostic request failed: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)}),
            "headers": {
                "Content-Type": "application/json"
            }
        }
```

**Update lambda_handler to support diagnostics:**

```python
def lambda_handler(event, context):
    """Main Lambda handler."""
    try:
        # ... existing code ...
        
        # Check for diagnostic request
        if event.get('diagnostic') or event.get('requestType') == 'diagnostic':
            return _handle_diagnostic_request(event)
        
        # ... rest of existing handler code ...
        
    except Exception as e:
        log_error(f"Lambda handler exception: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Internal server error"})
        }
```

---

## Phase 4: Build System Updates

### 4.1 Update build_config.py

**Add validation for assistant name configuration:**

```python
def validate_assistant_configuration() -> Dict[str, Any]:
    """Validate assistant name configuration for build."""
    import os
    
    assistant_name = os.getenv('HA_ASSISTANT_NAME', 'Home Assistant')
    
    validation = {
        "assistant_name": assistant_name,
        "valid": True,
        "warnings": []
    }
    
    # Check for common issues
    words = assistant_name.split()
    if len(words) == 1:
        validation["warnings"].append(
            f"Single-word name '{assistant_name}' may require it to be a proper name in Alexa"
        )
    
    forbidden = ['alexa', 'amazon', 'echo', 'skill', 'the']
    for word in words:
        if word.lower() in forbidden:
            validation["valid"] = False
            validation["warnings"].append(
                f"Name contains forbidden word '{word}' - Alexa won't accept this"
            )
    
    return validation
```

---

### 4.2 Update deploy_automation.py

**Add to configuration validation:**

```python
def validate_deployment_config(self)
