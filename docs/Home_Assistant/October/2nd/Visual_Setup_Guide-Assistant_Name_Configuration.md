# Visual Setup Guide: Assistant Name Configuration

## Configuration Flow Diagram

```
[Choose Name] → [Update Lambda] → [Create/Update Skill] → [Test] → [Done]
     ↓              ↓                   ↓             ↓        ↓
  2-25 chars    Environment Var     Custom Skill    Voice     Success
  No reserved   HA_ASSISTANT_NAME   Invocation      Test      
  words         Save & Deploy      Build Model     Commands   
```

## Step-by-Step Visual Checklist

### ✅ Step 1: Name Validation
```
Valid Names:          Invalid Names:
✅ Jarvis            ❌ Alexa
✅ Computer          ❌ Amazon  
✅ Smart Home        ❌ Echo
✅ House Assistant   ❌ 123
✅ Butler            ❌ @home
```

### ✅ Step 2: Lambda Configuration
```
AWS Lambda Console
└── Your Function
    └── Configuration Tab
        └── Environment variables
            └── Add/Edit Variable
                ├── Key: HA_ASSISTANT_NAME
                └── Value: [Your Name]
                    └── Save
```

### ✅ Step 3: Skill Type Decision
```
Current Setup:                Next Action:
┌─────────────────┐          ┌──────────────────┐
│ Smart Home Skill│    →     │ Create Custom    │
│ (Direct Control)│          │ Skill (Required) │
└─────────────────┘          └──────────────────┘

┌─────────────────┐          ┌──────────────────┐
│ Custom Skill    │    →     │ Update Invocation│
│ (Conversation)  │          │ Name (Simple)    │
└─────────────────┘          └──────────────────┘
```

### ✅ Step 4: Custom Skill Setup
```
Amazon Developer Console
└── Create Skill
    ├── Name: "[Your Name] Home Assistant"
    ├── Model: Custom
    ├── Method: Start from scratch
    └── Create skill
        └── Build Tab
            ├── Invocation: [your name] (lowercase)
            ├── JSON Editor: [Paste intent code]
            └── Endpoint: [Lambda ARN]
                └── Build Model
```

### ✅ Step 5: Lambda Integration
```
AWS Lambda Console
└── Your Function
    └── Add trigger
        ├── Source: Alexa Skills Kit
        ├── Skill ID: [From Developer Console]
        └── Add
            └── Trigger Active ✅
```

## Configuration Matrix

| Setting | Environment Variable | Parameter Store | Default |
|---------|---------------------|-----------------|---------|
| Assistant Name | `HA_ASSISTANT_NAME` | `/lambda-execution-engine/homeassistant/assistant_name` | "Home Assistant" |
| Timeout | `HA_TIMEOUT` | `/lambda-execution-engine/homeassistant/timeout` | 30 |
| SSL Verify | `HA_VERIFY_SSL` | `/lambda-execution-engine/homeassistant/verify_ssl` | true |

## Testing Command Examples

### With Default Name
```
❌ Old Way (Smart Home):
"Alexa, turn on the lights"

✅ New Way (Custom Skill):
"Alexa, ask Home Assistant to turn on the lights"
```

### With Custom Name "Jarvis"
```
✅ Custom Commands:
"Alexa, ask Jarvis to turn on the lights"
"Alexa, tell Jarvis to lock the doors"
"Alexa, ask Jarvis what's the temperature"
"Alexa, tell Jarvis to start movie mode"
```

## Troubleshooting Decision Tree

```
Issue: Alexa says "I don't know that"
├── Wait 5-10 minutes (skill propagation)
├── Check invocation name matches exactly
├── Disable/re-enable skill in Alexa app
└── Verify skill is enabled

Issue: Lambda function error
├── Check HA_ASSISTANT_NAME variable exists
├── Verify name passes validation
├── Check CloudWatch logs
└── Test diagnostic endpoint

Issue: Name validation fails
├── Remove forbidden words (Alexa, Amazon, Echo)
├── Check length (2-25 characters)
├── Use only letters, numbers, spaces
└── Avoid special characters
```

## Architecture Diagram

```
[Alexa Device]
      ↓
[Custom Skill] ← Invocation: "your name"
      ↓
[AWS Lambda] ← Environment: HA_ASSISTANT_NAME
      ↓
[Home Assistant] ← Standard API calls
```

## Quick Reference Card

**Essential Environment Variables:**
```bash
HOME_ASSISTANT_ENABLED=true
HA_ASSISTANT_NAME=Your Name
```

**Alexa Phrase Template:**
```
"Alexa, ask [Your Name] to [command]"
"Alexa, tell [Your Name] to [command]"
```

**Common Commands:**
- Turn on/off devices
- Set temperature
- Lock/unlock doors  
- Start scenes/automations
- Check status

**Validation Rules:**
- 2-25 characters
- Letters, numbers, spaces only
- No Alexa/Amazon/Echo
- Case automatically corrected
