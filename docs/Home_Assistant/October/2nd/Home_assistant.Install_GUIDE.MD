### **Step 5: Create Additional Home Assistant Parameters**

Now we'll create the optional parameters that control advanced Home Assistant behavior and customization.

**Assistant Name Parameter (Optional):**

Click **"Create parameter"**

**Parameter name:** `/lambda-execution-engine/homeassistant/assistant_name`

**Description:** "Custom assistant name for Alexa invocation"

**Tier:** Standard

**Type:** String

**Value:** Enter your preferred assistant name (examples: `Jarvis`, `Computer`, `Smart Home`, `House`)

This parameter controls how you invoke your assistant through Alexa. If not set, defaults to "Home Assistant".

**SSL Verification Parameter (Optional):**

Click **"Create parameter"**

**Parameter name:** `/lambda-execution-engine/homeassistant/verify_ssl`

**Description:** "SSL certificate verification for Home Assistant connection"

**Tier:** Standard

**Type:** String

**Value:** `true` (for production) or `false` (for self-signed certificates)

Set to `false` if using self-signed certificates or local HTTP connections.

**Timeout Parameter (Optional):**

Click **"Create parameter"**

**Parameter name:** `/lambda-execution-engine/homeassistant/timeout`

**Description:** "Request timeout for Home Assistant API calls in seconds"

**Tier:** Standard

**Type:** String

**Value:** `30` (default) or `45` (for slower networks)

Increase for slow networks or complex automations that take longer to execute.

### **Step 6: Updated Environment Variables Configuration**

Navigate back to your Lambda function's **Configuration** tab, then **Environment variables**.

Click **"Edit"** and add/update these variables:

**Core Home Assistant Variables:**

- Key: `HOME_ASSISTANT_ENABLED`, Value: `true`
- Key: `HA_ASSISTANT_NAME`, Value: `Home Assistant` (or your custom name)
- Key: `HA_FEATURE_PRESET`, Value: `standard`

**Connection Control Variables:**

- Key: `HA_TIMEOUT`, Value: `30`
- Key: `HA_VERIFY_SSL`, Value: `true`
- Key: `HA_CACHE_TTL`, Value: `300`

**Advanced Control Variables:**

- Key: `HA_MAX_RETRIES`, Value: `3`
- Key: `HA_CIRCUIT_BREAKER_THRESHOLD`, Value: `5`
- Key: `HA_BATCH_SIZE`, Value: `10`

**Feature Flags:**

- Key: `LUGS_ENABLED`, Value: `true`
- Key: `DEBUG_MODE`, Value: `false`

Click **"Save"**

### **Environment Variable Explanations**

**HOME_ASSISTANT_ENABLED**: Master switch for Home Assistant integration
- `true`: Enable all Home Assistant features
- `false`: Disable Home Assistant integration completely

**HA_ASSISTANT_NAME**: How Alexa refers to your system
- `Home Assistant`: Default invocation ("Alexa, ask Home Assistant...")
- `Jarvis`: Custom name ("Alexa, ask Jarvis...")
- Must match your Alexa skill invocation name

**HA_FEATURE_PRESET**: Controls performance and resource usage
- `minimal`: ~15MB memory, basic features only
- `standard`: ~25MB memory, all core features (recommended)
- `performance`: ~40MB memory, enhanced caching
- `maximum`: ~60MB memory, all features enabled

**HA_TIMEOUT**: Request timeout in seconds
- `30`: Standard timeout for most setups
- `45`: For slower networks or complex automations
- `60`: For very slow networks (not recommended)

**HA_VERIFY_SSL**: SSL certificate verification
- `true`: Verify SSL certificates (production, Nabu Casa)
- `false`: Skip verification (self-signed certs, local HTTP)

**HA_CACHE_TTL**: Cache duration in seconds
- `300`: 5 minutes (standard)
- `600`: 10 minutes (performance mode)
- `60`: 1 minute (development/testing)

**HA_MAX_RETRIES**: Maximum retry attempts for failed requests
- `3`: Standard retry count
- `5`: Higher reliability (performance mode)
- `1`: Faster failure (minimal mode)

**HA_CIRCUIT_BREAKER_THRESHOLD**: Failures before circuit breaker activates
- `5`: Standard threshold
- `3`: More sensitive (faster protection)
- `10`: Less sensitive (more tolerance)

**HA_BATCH_SIZE**: Number of entities processed in batch operations
- `10`: Standard batch size
- `20`: Larger batches (performance mode)
- `5`: Smaller batches (minimal mode)

## 🎭 **Phase 6B: Alexa Custom Skill Setup (Assistant Name Customization)**

If you want to use a custom assistant name (like "Jarvis" instead of "Home Assistant"), you need to create a Custom Skill instead of a Smart Home Skill.

### **When to Use Custom Skills**

**Use Smart Home Skill when:**
- You want to say "Alexa, turn on the lights" (direct commands)
- You're happy with device names as invocation
- You want the simplest setup

**Use Custom Skill when:**
- You want custom assistant names: "Alexa, ask Jarvis..."
- You want conversation-style interactions
- You want branded experience

### **Step 1: Create Custom Skill**

1. Go to [Amazon Developer Console](https://developer.amazon.com/alexa/console/ask)
2. Click **"Create Skill"**
3. **Skill name:** `[Your Name] Home Assistant` (e.g., "Jarvis Home Assistant")
4. **Default language:** English (US)
5. **Choose a model:** Custom
6. **Choose a method:** Start from scratch
7. Click **"Create skill"**

### **Step 2: Configure Invocation Name**

1. In the Build tab, click **"Invocation"** in left sidebar
2. **Skill Invocation Name:** Enter your custom name (e.g., `jarvis`, `computer`, `smart home`)
3. Click **"Save Model"**

**Invocation Name Rules:**
- Must be lowercase
- Cannot include wake words (alexa, amazon, echo)
- 2-25 characters
- Two or more words recommended for uniqueness

### **Step 3: Create Intent Schema**

Click **"JSON Editor"** in left sidebar and replace the content with:

```json
{
    "interactionModel": {
        "languageModel": {
            "invocationName": "jarvis",
            "intents": [
                {
                    "name": "ConversationIntent",
                    "slots": [
                        {
                            "name": "command",
                            "type": "AMAZON.SearchQuery"
                        }
                    ],
                    "samples": [
                        "to {command}",
                        "{command}",
                        "tell me {command}",
                        "I want to {command}",
                        "please {command}",
                        "can you {command}",
                        "would you {command}"
                    ]
                },
                {
                    "name": "AMAZON.HelpIntent",
                    "samples": []
                },
                {
                    "name": "AMAZON.StopIntent",
                    "samples": []
                },
                {
                    "name": "AMAZON.CancelIntent",
                    "samples": []
                }
            ],
            "types": []
        }
    }
}
```

Replace `"jarvis"` with your chosen invocation name.

Click **"Save Model"** then **"Build Model"**

### **Step 4: Configure Endpoint**

1. Click **"Endpoint"** in left sidebar
2. **Service Endpoint Type:** AWS Lambda ARN
3. **Default Region:** Paste your Lambda function ARN
4. Click **"Save Endpoints"**

### **Step 5: Lambda Trigger Configuration**

Back in AWS Lambda Console:

1. Go to your Lambda function
2. Click **"Add trigger"**
3. **Source:** Alexa Skills Kit
4. **Skill ID:** Copy from your Custom Skill (found in Build → Custom → Skill ID)
5. Click **"Add"**

### **Step 6: Test Custom Skill**

1. In Alexa Developer Console, click **"Test"** tab
2. Enable testing: **"Development"**
3. Type or say: `ask [your invocation name] to turn on the lights`

**Example Testing Phrases:**
- "ask jarvis to turn on the living room lights"
- "tell computer to set temperature to 72 degrees"
- "ask smart home to start movie mode"
- "tell house to lock all doors"

### **Step 7: Account Linking (If Using Smart Home Features)**

If you want both conversation AND smart home features:

1. Click **"Account Linking"** in left sidebar
2. **Authorization URL:** `https://your-lambda-url/auth`
3. **Access Token URI:** `https://your-lambda-url/token`
4. **Client ID:** Generate a random string
5. Add client ID to your Lambda environment variables as `ALEXA_CLIENT_ID`

### **Custom Skill Testing Examples**

**Device Control:**
- "Alexa, ask Jarvis to turn on the bedroom lights"
- "Alexa, tell Computer to unlock the front door"
- "Alexa, ask Smart Home to set temperature to 70"

**Scene Activation:**
- "Alexa, tell Jarvis to activate movie mode"
- "Alexa, ask Computer to start morning routine"
- "Alexa, tell House to enable security mode"

**Status Queries:**
- "Alexa, ask Jarvis what's the temperature"
- "Alexa, tell Computer to check if doors are locked"
- "Alexa, ask Smart Home for system status"

### **Troubleshooting Custom Skills**

**Skill Not Responding:**
1. Verify invocation name matches JSON configuration
2. Check Lambda trigger is configured for Alexa Skills Kit
3. Ensure Skill ID matches in Lambda trigger
4. Test with Alexa Developer Console simulator first

**Commands Not Working:**
1. Check intent matching in developer console logs
2. Verify Lambda function logs in CloudWatch
3. Test with simple commands first
4. Ensure Home Assistant is reachable

**Assistant Name Not Recognized:**
1. Rebuild skill model after changes
2. Wait 5-10 minutes for propagation
3. Try disabling and re-enabling skill
4. Check for invocation name conflicts

### **Configuration Validation**

After setup, test your configuration:

```bash
# Test basic functionality
"Alexa, ask [your assistant name] to turn on test light"

# Test conversation
"Alexa, tell [your assistant name] to check system status"

# Test complex commands
"Alexa, ask [your assistant name] to start the evening routine"
```

Your Lambda function logs will show whether the custom assistant name is being used correctly.

### **Parameter Store Summary**

After completing all steps, your Parameter Store should contain:

**Required Parameters:**
- `/lambda-execution-engine/homeassistant/url`
- `/lambda-execution-engine/homeassistant/token` (SecureString)

**Optional Parameters:**
- `/lambda-execution-engine/homeassistant/assistant_name`
- `/lambda-execution-engine/homeassistant/verify_ssl`
- `/lambda-execution-engine/homeassistant/timeout`

**Configuration Parameters:**
- `/lambda-execution-engine/config/tier`

### **Environment Variables Summary**

Your Lambda function environment variables should include:

**Core Configuration:**
- `USE_PARAMETER_STORE=true`
- `PARAMETER_PREFIX=/lambda-execution-engine`
- `AWS_REGION=us-east-1`

**Home Assistant Integration:**
- `HOME_ASSISTANT_ENABLED=true`
- `HA_ASSISTANT_NAME=Your Assistant Name`
- `HA_FEATURE_PRESET=standard`
- `HA_TIMEOUT=30`
- `HA_VERIFY_SSL=true`
- `HA_CACHE_TTL=300`

**Performance Control:**
- `LUGS_ENABLED=true`
- `HA_MAX_RETRIES=3`
- `HA_CIRCUIT_BREAKER_THRESHOLD=5`
- `HA_BATCH_SIZE=10`

**Feature Flags:**
- `ALEXA_SKILL_ENABLED=true`
- `DEBUG_MODE=false`
