# Assistant Name Quick Start Guide

Get your custom assistant name working in 10 minutes.

## Overview

Change how you invoke your smart home from "Alexa, ask Home Assistant..." to "Alexa, ask Jarvis..." (or any name you choose).

## Step 1: Choose Your Name (2 minutes)

### Valid Names
- **Single words**: Jarvis, Computer, House, Butler
- **Two words**: Smart Home, Home Control, House Assistant
- **Mixed case**: Automatically converted to proper case

### Invalid Names (Avoid These)
- Reserved words: Alexa, Amazon, Echo
- Numbers only: 123, 456
- Special characters: @jarvis, house!
- Too short/long: Must be 2-25 characters

### Popular Examples
- Jarvis (Iron Man inspired)
- Computer (Star Trek style)
- Smart Home (descriptive)
- House (simple and short)

## Step 2: Update Lambda Configuration (3 minutes)

### Method A: Environment Variable (Recommended)
1. Open AWS Lambda Console
2. Go to your Lambda function
3. Click **Configuration** → **Environment variables**
4. Add/edit: `HA_ASSISTANT_NAME` = `Your Name`
5. Click **Save**

### Method B: Parameter Store
1. Open AWS Systems Manager Console
2. Go to **Parameter Store**
3. Create parameter: `/lambda-execution-engine/homeassistant/assistant_name`
4. Type: String
5. Value: `Your Name`

## Step 3: Update Alexa Skill (3 minutes)

### For Smart Home Skill Users
**You cannot use custom names with Smart Home skills.** Skip to Step 4 to create a Custom Skill.

### For Custom Skill Users
1. Open [Amazon Developer Console](https://developer.amazon.com/alexa/console/ask)
2. Find your skill → **Build** tab
3. Click **Invocation** in left sidebar
4. Change **Skill Invocation Name** to your name (lowercase)
5. Click **Save Model** → **Build Model**

## Step 4: Create Custom Skill (If Needed) (5 minutes)

### When You Need This
- You want custom assistant names
- You currently use Smart Home skill
- You want conversational commands

### Quick Setup
1. Go to [Amazon Developer Console](https://developer.amazon.com/alexa/console/ask)
2. Click **Create Skill**
3. **Skill name**: `Your Name Home Assistant`
4. **Model**: Custom
5. **Method**: Start from scratch
6. Click **Create skill**

### Configure Invocation
1. **Build** tab → **Invocation**
2. **Skill Invocation Name**: `your name` (lowercase)
3. **Save Model**

### Add Intent
1. **Build** tab → **JSON Editor**
2. Replace content with:

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
                        "please {command}",
                        "can you {command}"
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
            ]
        }
    }
}
```

3. Replace `"jarvis"` with your chosen name (lowercase)
4. **Save Model** → **Build Model**

### Connect to Lambda
1. **Endpoint** tab
2. **AWS Lambda ARN**: Paste your Lambda function ARN
3. **Save Endpoints**

### Add Lambda Trigger
1. Go to AWS Lambda Console
2. Your function → **Add trigger**
3. **Source**: Alexa Skills Kit
4. **Skill ID**: Copy from Alexa Developer Console (Build → Custom → Skill ID)
5. **Add**

## Step 5: Test Your Configuration (2 minutes)

### Test Phrases
Try these with your new name:

**Basic Commands**:
- "Alexa, ask [Your Name] to turn on the living room lights"
- "Alexa, tell [Your Name] to lock the doors"
- "Alexa, ask [Your Name] what's the temperature"

**Examples**:
- "Alexa, ask Jarvis to turn on the lights"
- "Alexa, tell Computer to start movie mode"
- "Alexa, ask Smart Home to set temperature to 72"

### Troubleshooting Quick Fixes

**Alexa says "I don't know that"**
- Wait 5-10 minutes for skill propagation
- Disable and re-enable skill in Alexa app
- Check invocation name matches exactly

**Function returns error**
- Verify `HA_ASSISTANT_NAME` environment variable
- Check Lambda logs in CloudWatch
- Test with diagnostic endpoint

**Name validation fails**
- Avoid reserved words (Alexa, Amazon, Echo)
- Keep between 2-25 characters
- Use only letters, numbers, spaces

## Diagnostic Check

### Test Configuration
```bash
# Replace with your Lambda function URL
curl -X POST https://your-lambda-url/test \
  -H "Content-Type: application/json" \
  -d '{"test_type": "configuration"}'
```

### Expected Response
```json
{
  "configuration_valid": true,
  "assistant_name": "Your Name",
  "assistant_name_source": "environment_variable",
  "ha_connection": "success"
}
```

## Common Examples

### Family-Friendly Names
- Smart Home
- House Assistant
- Home Control
- Family Assistant

### Tech/Sci-Fi Names
- Jarvis (Iron Man)
- Computer (Star Trek)
- Friday (Marvel)
- HAL (2001: A Space Odyssey)

### Simple Names
- House
- Home
- Butler
- Assistant

## Next Steps

1. **Test thoroughly** with various commands
2. **Update family members** on new invocation name  
3. **Customize further** with additional intents
4. **Monitor performance** via CloudWatch

## Need Help?

### Quick Diagnostics
- Check environment variable: `HA_ASSISTANT_NAME`
- Verify Alexa skill invocation name matches
- Test Lambda function directly first

### Common Issues
- **Name not recognized**: Check skill configuration
- **Lambda errors**: Verify environment variables
- **Timeout issues**: Check Home Assistant connection

Total setup time: **10 minutes**  
Difficulty: **Beginner-friendly**
