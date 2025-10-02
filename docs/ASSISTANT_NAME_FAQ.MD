# Assistant Name FAQ

## General Questions

**Q: What is the assistant name feature?**
A: Customize how you invoke your smart home through Alexa. Instead of "Alexa, ask Home Assistant...", use "Alexa, ask Jarvis..." or any name you choose.

**Q: Do I need this feature?**
A: No, it's optional. Default "Home Assistant" works fine. Use custom names for personalization or branding.

**Q: Does this cost extra?**
A: No additional AWS costs. Custom Skill setup is free.

**Q: Will this break my existing setup?**
A: No. Default behavior unchanged. Custom names are additive.

**Q: Can I change the name later?**
A: Yes. Update the environment variable and Alexa skill invocation name.

## Configuration Questions

**Q: How do I set a custom name?**
A: Set environment variable `HA_ASSISTANT_NAME=Your Name` in Lambda configuration.

**Q: Can I use Parameter Store instead?**
A: Yes. Create `/lambda-execution-engine/homeassistant/assistant_name` parameter. Environment variables take priority.

**Q: Which takes priority - environment variable or Parameter Store?**
A: Environment variable has higher priority than Parameter Store.

**Q: What if I don't set any custom name?**
A: Defaults to "Home Assistant".

**Q: How do I verify my configuration?**
A: Use diagnostic endpoint: `curl -X POST https://your-lambda-url/test -d '{"test_type":"configuration"}'`

## Name Validation Questions

**Q: What names are allowed?**
A: 2-25 characters, letters/numbers/spaces only. Examples: Jarvis, Computer, Smart Home.

**Q: What names are forbidden?**
A: Alexa, Amazon, Echo, wake words, numbers-only, special characters.

**Q: Can I use "Computer" like Star Trek?**
A: Yes, "Computer" is valid and popular.

**Q: Can I use two words?**
A: Yes. "Smart Home", "House Assistant", etc. are valid.

**Q: Is "Jarvis" allowed?**
A: Yes, very popular choice inspired by Iron Man.

**Q: What about "HAL" or "Friday"?**
A: Both valid - HAL (2001: A Space Odyssey), Friday (Marvel).

**Q: Case sensitivity?**
A: Automatically converted to proper case. "jarvis" becomes "Jarvis".

**Q: Can I use my own name?**
A: Yes, if it meets validation rules (2-25 chars, no forbidden words).

## Alexa Skill Questions

**Q: Do I need a Custom Skill for custom names?**
A: Yes. Smart Home Skills cannot use custom invocation names.

**Q: What's the difference between Smart Home and Custom Skills?**
A: Smart Home: Direct device control, no custom names. Custom: Conversational, custom names supported.

**Q: Can I have both skill types?**
A: Not recommended. Choose one based on your needs.

**Q: How do I create a Custom Skill?**
A: See ASSISTANT_NAME_QUICKSTART.md for step-by-step instructions.

**Q: Do I need to update my Alexa skill when I change names?**
A: Yes. Update the invocation name in Amazon Developer Console.

**Q: How long does it take for skill changes to work?**
A: 5-10 minutes for propagation. May need to disable/re-enable skill.

## Usage Questions

**Q: How do I invoke with custom names?**
A: "Alexa, ask [Your Name] to..." or "Alexa, tell [Your Name] to..."

**Q: Example phrases for "Jarvis"?**
A: 
- "Alexa, ask Jarvis to turn on the lights"
- "Alexa, tell Jarvis to lock the doors"
- "Alexa, ask Jarvis what's the temperature"

**Q: Can I still use the old way?**
A: If you switch to Custom Skill, use the new invocation. Smart Home direct commands won't work.

**Q: What commands work with custom names?**
A: All Home Assistant integrations: device control, scenes, automations, scripts.

**Q: Can multiple people use different names?**
A: No. One name per Lambda function. All users use the same invocation.

## Technical Questions

**Q: Where is the name validation performed?**
A: In the Lambda function using `validate_assistant_name()` function.

**Q: What happens if validation fails?**
A: Falls back to "Home Assistant" and logs warning.

**Q: How do I check if my name is valid programmatically?**
A: Call the diagnostic endpoint with test_type "configuration".

**Q: Can I bypass validation?**
A: No. Validation ensures Alexa compatibility.

**Q: Does the name affect performance?**
A: No performance impact. It's a simple string replacement.

**Q: Is the name stored securely?**
A: Environment variables: Lambda runtime only. Parameter Store: AWS encryption.

## Troubleshooting Questions

**Q: Alexa says "I don't know that" when I use my custom name?**
A: 
1. Verify Alexa skill invocation name matches
2. Wait 5-10 minutes for propagation
3. Disable/re-enable skill in Alexa app
4. Check skill is enabled

**Q: My Lambda function returns an error?**
A: 
1. Check `HA_ASSISTANT_NAME` environment variable
2. Verify name passes validation
3. Check CloudWatch logs
4. Test diagnostic endpoint

**Q: Name validation is failing?**
A: 
1. Avoid: Alexa, Amazon, Echo
2. Use 2-25 characters only
3. Letters, numbers, spaces only
4. No special characters

**Q: Custom Skill not responding?**
A: 
1. Verify Lambda trigger is configured
2. Check Skill ID matches in trigger
3. Test skill in Developer Console first
4. Check Lambda execution role permissions

**Q: Getting "Unauthorized" errors?**
A: Home Assistant token issue, not related to assistant name. Check HA configuration.

## Migration Questions

**Q: I currently use Smart Home Skill. How do I switch?**
A: 
1. Create new Custom Skill
2. Set up assistant name
3. Test thoroughly
4. Disable old Smart Home Skill

**Q: Can I migrate back to Smart Home Skill?**
A: Yes. Remove custom name configuration and recreate Smart Home Skill.

**Q: Will I lose my device names?**
A: Device names come from Home Assistant, not affected by assistant name changes.

**Q: Do I need to re-expose entities?**
A: No. Entity exposure is Home Assistant configuration, independent of assistant name.

## Advanced Questions

**Q: Can I use different names for different environments?**
A: Yes. Set different `HA_ASSISTANT_NAME` values in different Lambda functions.

**Q: Multiple Home Assistant instances with different names?**
A: Deploy separate Lambda functions with different configurations.

**Q: Can I change names dynamically?**
A: No. Requires Lambda environment variable update and Alexa skill rebuild.

**Q: Integration with other voice assistants?**
A: Feature is Alexa-specific. Other assistants need separate configuration.

**Q: Can I use this with Home Assistant Cloud?**
A: Yes, works with Nabu Casa, self-hosted, or any accessible HA instance.

## Best Practices

**Q: What's the most popular custom name?**
A: "Jarvis" (Iron Man reference) and "Computer" (Star Trek reference).

**Q: Should I tell family members about the name change?**
A: Yes. Include them in testing and provide phrase examples.

**Q: How do I choose a good name?**
A: 
- Easy to pronounce
- Not confusing with existing names
- Memorable for family
- Fits your smart home theme

**Q: Any naming conventions to follow?**
A: Keep it simple, avoid technical terms, consider family-friendly options.

**Q: Should I use my smart home brand name?**
A: If it meets validation rules and is easy to say, yes.

## Error Messages

**Q: "Invalid assistant name" error?**
A: Name failed validation. Check forbidden words and character limits.

**Q: "Assistant name not found" in logs?**
A: Environment variable not set or Parameter Store missing. Check configuration.

**Q: "Validation error" in diagnostic response?**
A: Name contains forbidden words or invalid characters.

**Q: "Home Assistant integration disabled" message?**
A: Set `HOME_ASSISTANT_ENABLED=true` environment variable.

## Performance Questions

**Q: Does custom name affect Lambda performance?**
A: No measurable impact. Simple string operations.

**Q: Does name length matter for performance?**
A: No. 2-character vs 25-character names have identical performance.

**Q: Any memory impact?**
A: Negligible. ~100 bytes maximum.

**Q: Does caching work with custom names?**
A: Yes. Caching is independent of assistant name.

**Q: Any AWS Lambda timeout impact?**
A: None. Name processing adds <1ms.
