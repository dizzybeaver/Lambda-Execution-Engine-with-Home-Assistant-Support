# Custom Assistant Name Configuration Guide

**Version:** 2025.10.10.02  
**Purpose:** Complete guide to configuring custom invocation names for Alexa

---

## Table of Contents

1. [Understanding Custom Names](#understanding-custom-names)
2. [When to Use Custom Names](#when-to-use-custom-names)
3. [Validation Rules](#validation-rules)
4. [Configuration Methods](#configuration-methods)
5. [Alexa Skill Setup](#alexa-skill-setup)
6. [Testing Your Configuration](#testing-your-configuration)
7. [Troubleshooting](#troubleshooting)

---

## Understanding Custom Names

By default, when you use the Home Assistant Extension with Alexa, you invoke commands using phrases like Alexa, ask Home Assistant to turn on the lights. The custom assistant name feature allows you to change Home Assistant to any name you prefer, enabling phrases like Alexa, ask Jarvis to turn on the lights or Alexa, tell Computer to lock the doors.

Custom names are a feature of the Home Assistant Extension, not the Lambda Execution Engine core. When you configure a custom name, you are customizing how the Extension presents itself to Alexa and your users. The Engine itself does not require or use custom names.

This feature works by configuring both your Lambda function and your Alexa skill to recognize your chosen name. The Lambda function needs to know the name so it can reference it in responses to Alexa. The Alexa skill needs to know the name so it understands what you say when you invoke the skill.

Custom names only work with Custom Skills, not Smart Home Skills. Smart Home Skills provide direct device control without requiring an invocation name, which means you say Alexa, turn on the lights directly. Custom Skills require you to use an invocation phrase that includes your assistant name, but they allow you to use any name you choose within the validation rules.

---

## When to Use Custom Names

Custom assistant names provide personalization and can make your smart home feel more unique. If you want to use a name from science fiction like Jarvis from Iron Man or Computer from Star Trek, custom names enable this. If you want a descriptive name like Smart Home or House Assistant that clearly indicates what the skill controls, custom names work well.

Custom names work best when everyone in your household agrees on the name and finds it natural to use. If different family members prefer different names, the default Home Assistant name might create less friction. Custom names also require everyone to remember to include the invocation phrase before commands, which some users find more cumbersome than the direct control provided by Smart Home Skills.

Consider using custom names if you find the Home Assistant name confusing or too generic, if you want your smart home to feel more personalized, if you enjoy references to science fiction or other media, or if you want a name that clearly indicates the purpose of the skill to guests or family members who might use it.

Consider keeping the default name if multiple people in your household cannot agree on a custom name, if you find invocation phrases like ask Name to be awkward, if you prefer the directness of Smart Home Skills, or if you frequently add new devices and want them to work immediately without skill updates.

---

## Validation Rules

Amazon enforces specific rules for skill invocation names to prevent confusion and ensure the Alexa voice recognition system can understand them reliably. Your chosen name must comply with all these rules or Alexa will reject it during skill configuration.

### Length Requirements

Your assistant name must contain at least two characters and no more than twenty-five characters. Single-letter names like A or H do not meet the minimum length requirement. Names longer than twenty-five characters exceed the maximum length and will be rejected.

### Character Requirements

Your name can contain only letters from the English alphabet, numbers, and spaces. Letters can be uppercase or lowercase, though Amazon normalizes all invocation names to lowercase internally. You can use numbers within the name, but numbers by themselves without any letters are not allowed.

Special characters including punctuation marks, symbols, and accented letters are not permitted. This means you cannot use names like Hal-9000 with hyphens, @Home with symbols, or Jarv!s with exclamation points.

### Reserved Words

Amazon prohibits several reserved words that could create confusion with Alexa's core functionality or Amazon's product names. You cannot use Alexa as your assistant name. You cannot use Amazon or any variation of the Amazon company name. You cannot use Echo or any Amazon device names like Echo Dot, Echo Show, or Echo Plus.

You also cannot use wake words that activate Alexa devices. These include the default wake word Alexa and alternate wake words like Computer, Amazon, and Echo. Note that while Computer is a prohibited wake word, you can use it as an invocation name in some regions where it is not enabled as a wake word option.

### Phrase Structure

Your name should be something natural to say as part of a voice command. Names that sound like questions or commands themselves can confuse the voice recognition system. Avoid names that start with words like who, what, when, where, why, how, could, should, or would.

Names should not include verb phrases that might be confused with commands. For example, Turn On is not a good name because Alexa might interpret it as the start of a command rather than an invocation name.

### Testing Your Name

Before committing to a name, test it by saying it out loud in the context of commands you will use. Say Alexa, ask [your name] to turn on the lights. Does it feel natural? Is it easy to pronounce clearly? Will other people in your household find it comfortable to use? These practical considerations matter as much as the technical validation rules.

---

## Configuration Methods

You can configure your custom assistant name using either environment variables in Lambda, Parameter Store in AWS Systems Manager, or both. Environment variables take precedence over Parameter Store when both are set, which allows you to override Parameter Store settings temporarily without changing the stored value.

### Using Environment Variables

To configure your assistant name with environment variables, navigate to your Lambda function in the AWS Console. Click on the Configuration tab, then select Environment Variables from the left menu. Click Edit to modify variables.

Add a new environment variable if one does not exist already, or edit the existing variable if you previously configured an assistant name. Set the key to HA_ASSISTANT_NAME. Set the value to your chosen assistant name, such as Jarvis or Computer. The value should match the validation rules described earlier. Click Save to apply your changes.

Environment variable configuration takes effect immediately on the next function invocation. You do not need to redeploy your code or restart your function. This method works well for testing different names quickly or making temporary changes.

### Using Parameter Store

To configure your assistant name with Parameter Store, navigate to AWS Systems Manager in the AWS Console. Click on Parameter Store in the left sidebar. Click Create Parameter to add a new parameter.

Set the parameter name to /lambda-execution-engine/homeassistant/assistant_name. If you used a different parameter prefix in your PARAMETER_PREFIX environment variable, adjust the path accordingly. Set the tier to Standard, which is free and provides enough storage for a name. Set the type to String since assistant names are not sensitive information that needs encryption.

Set the value to your chosen assistant name following the validation rules. Add a description such as Custom invocation name for Alexa skill to help you remember the parameter's purpose. Click Create Parameter to save.

Parameter Store configuration requires your Lambda function to read the parameter, which happens during function initialization. If you change a Parameter Store value while your function is warm from recent invocations, the change may not take effect until the function cold starts again or the cache expires based on your HA_CACHE_TTL setting.

### Using Both Methods

You can configure both environment variables and Parameter Store with assistant names. This approach allows you to set a stable default name in Parameter Store while using environment variables for temporary overrides during testing or troubleshooting.

The environment variable always takes precedence when both are set. If you set HA_ASSISTANT_NAME to Jarvis in environment variables and set the Parameter Store value to Computer, the function will use Jarvis. If you later remove the environment variable, the function will fall back to using Computer from Parameter Store.

---

## Alexa Skill Setup

Custom assistant names require creating a Custom Skill rather than a Smart Home Skill. Custom Skills support invocation names while Smart Home Skills do not. This section walks through creating and configuring the Custom Skill.

### Creating the Skill

Navigate to the Amazon Developer Console at https://developer.amazon.com/alexa/console/ask. Sign in with your Amazon Developer account. Click Create Skill to begin the skill creation process.

On the Create Skill page, enter a skill name that includes your custom assistant name. For example, if your assistant name is Jarvis, you might name the skill Jarvis Home Assistant Control. This name appears in the Alexa app and helps users identify the skill, but it does not need to match your invocation name exactly.

Under Choose a Model, select Custom. This enables you to define a custom invocation name rather than using direct device control like Smart Home Skills provide. Under Choose a Method to Host Your Skill's Backend Resources, select Provision Your Own. This indicates you will use your own Lambda function rather than Alexa-hosted resources. Click Create Skill to proceed.

Alexa displays a template selection page. Choose Start From Scratch to create a minimal skill that you will configure manually. Click Continue to finish the initial creation.

### Configuring the Invocation Name

After skill creation completes, Alexa displays the skill builder interface. In the left sidebar, click on Invocation under the Skill Builder Checklist section. This opens the invocation configuration page.

In the Skill Invocation Name field, enter your chosen assistant name in lowercase. For example, if you configured HA_ASSISTANT_NAME as Jarvis, enter jarvis here. If you configured it as Computer, enter computer. The invocation name must exactly match your Lambda configuration in lowercase form.

Alexa automatically converts multi-word names to lowercase with spaces preserved. For example, Smart Home becomes smart home as the invocation name. Users will say Alexa, ask smart home to turn on lights.

Click Save Model at the top of the page to save your invocation configuration. This saves the change but does not build the skill yet.

### Defining Intents

Intents define what types of requests your skill can handle. You need to create intents that process commands and route them to your Lambda function. Click on JSON Editor in the left sidebar to access the raw interaction model.

Replace the existing JSON with an interaction model that includes intents for conversation, help, and stop. The conversation intent should include sample utterances that users might say to control their smart home. The help intent responds when users ask for help. The stop intent allows users to exit the skill.

Your JSON should define the invocation name to match your assistant name, list the intents your skill supports, and provide sample utterances for each intent. After pasting your interaction model, click Save Model at the top.

Click Build Model to compile your interaction model. This process takes thirty to sixty seconds. Alexa validates your interaction model and reports any errors. If errors occur, review the error messages and correct the issues before building again.

### Configuring the Endpoint

After building your interaction model successfully, click on Endpoint in the left sidebar. Select AWS Lambda ARN as your endpoint type since you are using an existing Lambda function.

You need to enter your Lambda function ARN in the Default Region field. To find your ARN, open your Lambda function in the AWS Console. The ARN appears near the top of the page in the format arn:aws:lambda:region:account:function:name. Copy this complete ARN.

Paste the ARN into the Default Region field in the Alexa Developer Console. If your Lambda function is in a region other than the default, you may need to use the region-specific endpoint field instead. Click Save Endpoints to apply the configuration.

### Adding Lambda Trigger

Return to your Lambda function in the AWS Console. Click Add Trigger on the function overview page. Select Alexa Skills Kit from the trigger type dropdown.

In the Skill ID field, paste your Alexa Skill ID. Find this ID in the Alexa Developer Console on your skill's main page under Skill ID. The ID looks like amzn1.ask.skill.xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx.

Click Add to create the trigger. This allows your Alexa skill to invoke your Lambda function.

### Enabling Testing

In the Alexa Developer Console, locate the dropdown menu at the top of the page that says Skill Testing is Disabled. Click on it and select Development. This enables you to test your skill through the Alexa Developer Console simulator and on your registered Alexa devices.

---

## Testing Your Configuration

After configuring your custom assistant name in both Lambda and your Alexa skill, test that everything works correctly.

### Testing in Developer Console

In the Alexa Developer Console, click on the Test tab. The testing interface shows a text input and a microphone button. Type or speak a test command using your custom assistant name.

For example, if your custom name is Jarvis, type ask jarvis to turn on the lights. The simulator processes your request and shows both the request sent to Lambda and the response received. Review the response to verify it uses your custom name appropriately.

Test several different commands to ensure the skill recognizes your invocation name consistently. Try commands with different phrasing to verify the intents handle variations correctly.

### Testing with Alexa Devices

On a registered Alexa device linked to the same Amazon account as your developer account, speak a command using your custom name. Say Alexa, ask [your name] to turn on the lights. Alexa should process the command and control your device.

Test that Alexa responses include your custom name where appropriate. The responses should feel natural and refer to your assistant by the custom name rather than using generic phrases.

### Verifying Lambda Logs

Navigate to CloudWatch Logs and open the log group for your Lambda function. Find the most recent log stream corresponding to your test invocation. Review the logs to verify the function received and processed your custom assistant name correctly.

Check that configuration loading shows your custom name. Look for log entries indicating which assistant name the function is using. This helps confirm that environment variables or Parameter Store values loaded correctly.

---

## Troubleshooting

### Alexa Does Not Recognize Your Name

If Alexa responds that it cannot find a skill when you use your custom name, verify that the skill is enabled on your account. Open the Alexa app, navigate to Skills & Games, then Your Skills, and confirm your skill appears and shows as enabled.

Check that the invocation name in your Alexa skill configuration exactly matches what you say. The names must match character for character, ignoring case differences. If you configured jarvis as the invocation name, you must say ask jarvis not ask Jarvis or ask JARVIS.

Verify that skill testing is enabled in Development mode. If testing is disabled, Alexa devices will not recognize the skill even if it is properly configured.

Wait five to ten minutes after enabling testing or making changes. Skills sometimes take time to propagate to devices. Try disabling and re-enabling the skill in the Alexa app. Sometimes this forces a refresh of skill information.

### Lambda Function Errors

If Alexa responds with an error message when you use your custom name, check CloudWatch logs for detailed error information. The logs show exactly what went wrong during function execution.

Verify your HA_ASSISTANT_NAME environment variable is set correctly in Lambda. Typos in the variable name or value prevent proper configuration. Confirm your Lambda function has the correct IAM permissions to read Parameter Store if you use Parameter Store for configuration.

Test your Lambda function directly using the test feature in the Lambda console. Create a test event that simulates an Alexa request with your custom name. This isolates whether the problem is with Alexa skill configuration or Lambda function execution.

### Name Validation Failures

If Amazon rejects your chosen name during skill configuration, review the validation rules to identify which rule your name violates. Common violations include using reserved words like Alexa or Amazon, using special characters or punctuation, making the name too short or too long, or using only numbers without letters.

Choose a different name that complies with all validation rules. Test the new name using the same process. Keep in mind that Amazon may update validation rules occasionally, so a name that worked previously might not work for new skills.

### Invocation Phrase Awkwardness

If your custom name works technically but feels awkward to say in practice, consider whether the name flows naturally in spoken commands. Some names sound good in writing but are difficult to pronounce clearly or feel unnatural in conversation.

Test your name with other household members to gather feedback. Different people may have different comfort levels with certain names. Consider choosing a shorter name if longer names feel cumbersome. Single-word names like Jarvis or Computer often work better than multi-word names like Smart Home System.

### Family Members Forget Custom Name

If household members frequently forget to use your custom name and try to use direct commands instead, consider whether the custom name adds enough value to justify the learning curve. Smart Home Skills with direct commands may be more practical for households where not everyone wants to use custom invocations.

Create reminder cards or notes near Alexa devices listing example commands with your custom name. Practice using the commands together as a family to build the habit. Consider whether a more memorable or meaningful name might be easier for everyone to remember.

---

## Example Commands

This section provides example commands showing how to use custom assistant names in practice.

### With Custom Name Jarvis

Alexa, ask Jarvis to turn on the living room lights.  
Alexa, tell Jarvis to set the thermostat to 72 degrees.  
Alexa, ask Jarvis what the temperature is in the bedroom.  
Alexa, tell Jarvis to lock the front door.  
Alexa, ask Jarvis to activate the movie scene.

### With Custom Name Computer

Alexa, ask Computer to turn off all the lights.  
Alexa, tell Computer to start the morning routine.  
Alexa, ask Computer what devices are on.  
Alexa, tell Computer to close the garage door.  
Alexa, ask Computer to turn on the fan.

### With Custom Name Smart Home

Alexa, ask Smart Home to dim the bedroom lights to 50 percent.  
Alexa, tell Smart Home to turn on the coffee maker.  
Alexa, ask Smart Home if the front door is locked.  
Alexa, tell Smart Home to turn off the TV.  
Alexa, ask Smart Home to run the bedtime script.
