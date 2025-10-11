# Lambda Test Events Collection

Quick reference guide for testing your Lambda Execution Engine.

## Diagnostic & Health Tests

**01-health-check-test.json**
- Tests basic Lambda execution
- No Home Assistant connection required
- Validates gateway is working

**02-diagnostic-full-test.json**
- Full system diagnostic
- Tests all modules and connections
- Returns comprehensive status

**03-diagnostic-homeassistant-test.json**
- Home Assistant connectivity test
- Validates HA URL and token
- Returns HA system info

**04-diagnostic-configuration-test.json**
- Configuration validation test
- Checks environment variables
- Validates Parameter Store access

**05-analytics-test.json**
- Usage analytics report
- Module loading statistics
- Request type metrics

## API Gateway Tests

**06-api-gateway-health-test.json**
- Simulates HTTP GET to /health
- Tests API Gateway integration
- Returns service status

**07-api-gateway-diagnostics-test.json**
- Simulates HTTP GET to /diagnostics
- Tests with query parameter
- Returns full diagnostic info

**08-api-gateway-analytics-test.json**
- Simulates HTTP GET to /analytics
- Tests analytics endpoint
- Returns usage statistics

## Alexa Custom Skill Tests

**09-alexa-launch-request-test.json**
- Tests skill launch
- Returns welcome message with assistant name
- Validates custom name configuration

**10-alexa-help-intent-test.json**
- Tests AMAZON.HelpIntent
- Returns help information
- Validates intent routing

**11-alexa-stop-intent-test.json**
- Tests AMAZON.StopIntent
- Returns goodbye message
- Validates session ending

**12-alexa-session-ended-test.json**
- Tests SessionEndedRequest
- Validates cleanup logic
- No response expected

**13-alexa-conversation-intent-test.json**
- Tests TalkToHomeAssistant intent
- Sends message to HA conversation
- Validates slot value extraction

**14-alexa-diagnostics-intent-test.json**
- Tests GetDiagnostics intent
- Returns system info via voice
- Validates intent handling

## Smart Home Directive Tests

**NOTE:** Smart Home tests in separate collection due to different use case (see SMART-HOME-TESTS.md)

## Debugging Tests

**15-minimal-unknown-test.json**
- Tests unknown request type handling
- Validates error responses
- Checks logging for unknown requests

**16-alexa-accept-grant-test.json**
- Tests OAuth grant acceptance
- **Currently returns "Unsupported directive" error** (see logs)
- Use this to debug authorization flow

**17-empty-event-test.json**
- Tests empty event handling
- Validates request validation
- Checks error handling for malformed requests

## How to Use These Tests

### In AWS Lambda Console

1. Navigate to your Lambda function
2. Click the **Test** tab
3. Click **Create new test event**
4. Give it a descriptive name (e.g., "Health-Check")
5. Copy/paste the JSON from the test file
6. Click **Save**
7. Click **Test** to execute

### Common Testing Workflow

**Initial Setup Verification:**
```
1. Run: 01-health-check-test.json
2. Run: 02-diagnostic-full-test.json
3. Run: 03-diagnostic-homeassistant-test.json
```

**Debugging Connection Issues:**
```
1. Run: 01-health-check-test.json (should succeed)
2. Run: 03-diagnostic-homeassistant-test.json (check error details)
3. Review CloudWatch logs for specific errors
```

**Testing Custom Skill:**
```
1. Run: 09-alexa-launch-request-test.json
2. Run: 13-alexa-conversation-intent-test.json
3. Run: 10-alexa-help-intent-test.json
```

**Performance Testing:**
```
1. Run: 01-health-check-test.json (note cold start time)
2. Run again immediately (note warm start time)
3. Run: 05-analytics-test.json (view performance data)
```

## Interpreting Results

### Successful Response
```json
{
  "statusCode": 200,
  "body": "{...}"
}
```

### Error Response
```json
{
  "statusCode": 400/401/500,
  "body": "{\"error\": \"...\"}"
}
```

### Check CloudWatch Logs
Always review logs at: **CloudWatch > Log groups > /aws/lambda/your-function-name**

## Quick Troubleshooting

**Test fails with validation error:**
- Check environment variables are set
- Verify HOME_ASSISTANT_ENABLED setting
- Check IAM role permissions

**Home Assistant tests fail:**
- Verify HA_URL in Parameter Store
- Check HA_TOKEN is valid
- Test HA_URL accessibility from internet

**Unknown directive errors:**
- Check if directive is implemented
- Review homeassistant_extension.py handlers
- See test #16 for AcceptGrant example

**Empty/minimal tests fail:**
- This is expected for validation
- Use to verify error handling works
- Check logs show proper error messages

## Next Steps

After basic tests pass:
1. Enable your Alexa skill for testing
2. Link your Amazon account
3. Test with actual voice commands
4. Monitor CloudWatch logs during live testing
5. Use analytics endpoint to track usage patterns
