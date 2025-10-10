# Lambda Execution Engine - Testing and Validation Guide

**Version:** 2025.10.10  
**Purpose:** Comprehensive testing procedures and validation checklists

---

## Table of Contents

1. [Testing Overview](#testing-overview)
2. [Pre-Deployment Testing](#pre-deployment-testing)
3. [Post-Deployment Testing](#post-deployment-testing)
4. [Feature-Specific Testing](#feature-specific-testing)
5. [Performance Testing](#performance-testing)
6. [Security Validation](#security-validation)
7. [Regression Testing](#regression-testing)
8. [Automated Testing](#automated-testing)

---

## Testing Overview

Testing the Lambda Execution Engine involves verifying that all components work correctly together and that voice commands through Alexa successfully control your Home Assistant devices. This guide provides systematic testing procedures to ensure your installation is complete and functioning properly.

### Testing Phases

Testing occurs in three main phases. Pre-deployment testing verifies your configuration before uploading code to Lambda. Post-deployment testing confirms the Lambda function works correctly after deployment. Ongoing testing validates that the system continues working as you add devices or change configurations.

### Testing Tools

You will use several tools during testing. The AWS Lambda console provides a test interface for invoking your function with custom events. The Alexa Developer Console offers a simulator for testing voice commands without an Alexa device. CloudWatch Logs show detailed execution information. Your physical Alexa devices provide real-world testing. The Home Assistant web interface allows you to verify device state changes.

---

## Pre-Deployment Testing

Before deploying your Lambda function, validate that your configuration is correct and your Home Assistant instance is accessible.

### Validate Parameter Store Values

Navigate to AWS Systems Manager Parameter Store and verify that all required parameters exist. Check that the Home Assistant URL parameter contains your complete URL including protocol and port. Verify the format matches how you access Home Assistant from outside your network. For Cloudflare Tunnel, the format should be https://homeassistant.yourdomain.com. For direct connections, use https://your-domain-or-ip:port.

Check that the Home Assistant token parameter exists as a SecureString type. You cannot view the encrypted value, but you can verify the parameter exists and was created recently. If you are uncertain whether the token is correct, regenerate it in Home Assistant and update the parameter.

Verify optional parameters if you created them. Check that the assistant name parameter contains a valid name between 2 and 25 characters. Verify the SSL verification parameter is set to true or false as appropriate for your SSL configuration. Confirm the timeout parameter contains a number representing seconds.

### Test Home Assistant Accessibility

From a device that is not connected to your home network, such as your phone using cellular data, attempt to access your Home Assistant URL. You should see the Home Assistant login page. If you cannot load the page, your Home Assistant instance is not accessible from the internet and Lambda will not be able to connect to it.

If you use Cloudflare Tunnel, verify the tunnel is running by checking the tunnel daemon logs on your Home Assistant host. The logs should show the tunnel connected and ready to receive traffic. Test that the Cloudflare URL loads the Home Assistant login page.

If you use port forwarding, verify your router forwards traffic correctly. Use an online port checking tool to test whether your port is open and accessible. Confirm your firewall allows incoming connections on the forwarded port.

### Verify Home Assistant API Access

Using a tool like curl or Postman, test direct API access to Home Assistant. Construct an API request to get all states using your access token for authentication. The command should return a JSON array containing all entity states in your Home Assistant instance.

If the API request succeeds, your token is valid and Home Assistant is accessible. If the request fails with an authorization error, your token is invalid or expired. If the request fails with a connection error, Home Assistant is not accessible from the internet. If the request fails with an SSL error, your SSL configuration needs adjustment.

### Check Environment Variable Configuration

Before uploading your Lambda code, prepare a checklist of environment variables you will set. Verify you have values for HOME_ASSISTANT_ENABLED set to true, USE_PARAMETER_STORE set to true, PARAMETER_PREFIX matching your Parameter Store path, HA_FEATURE_PRESET set to your desired preset, and HA_TIMEOUT set appropriately for your network.

Write down these values so you can enter them quickly after creating your Lambda function. Having them prepared prevents errors from mistyping values during configuration.

### Validate Code Package

Before uploading your deployment package, extract it to a temporary folder and verify the contents. Check that all required Python files are present at the root level of the ZIP archive. Verify no extra folders or files were accidentally included. Confirm that Python files use absolute imports rather than relative imports.

Check that gateway.py includes the format_response function. Verify that variables_utils.py uses absolute imports. These are common issues that cause deployment failures if not corrected before upload.

---

## Post-Deployment Testing

After deploying your Lambda function, systematically test each component to ensure everything works correctly.

### Lambda Function Execution Test

From your Lambda function page in the AWS Console, click the Test tab. Create a new test event named health-check. Configure the test event with minimal JSON that the function can process successfully. Click Test to invoke the function.

Watch the execution results. The function should complete successfully with a green success indicator. Check the execution duration to ensure it completes well under your timeout setting. Review the memory usage to confirm it stays within your allocated memory.

If the test fails, examine the error message and stack trace. Common issues include missing environment variables, incorrect IAM permissions, or Python syntax errors. Fix any errors before proceeding with additional testing.

### Home Assistant Connection Test

Create a test event that simulates an Alexa discovery request. This event instructs your function to query Home Assistant for available devices. The test event should follow the Alexa Smart Home discovery directive format.

Run the test and examine the response. A successful test returns a discovery response containing a list of devices from your Home Assistant instance. The response should include device IDs, friendly names, and capabilities for each device you have exposed to Alexa.

If the discovery test fails, check CloudWatch Logs for detailed error information. Look for connection errors indicating the function cannot reach Home Assistant, authentication errors suggesting an invalid token, or SSL errors pointing to certificate problems.

### CloudWatch Logs Verification

Navigate to CloudWatch Logs and find your Lambda function's log group. Click on the most recent log stream to view logs from your test invocations. Verify that logs appear for each test you ran.

Examine the log contents. You should see initialization messages when the function starts, connection messages when it contacts Home Assistant, and response messages when it returns results. Look for any warning or error messages that indicate problems even if the test appeared to succeed.

Check that no sensitive information appears in logs. Access tokens and other secrets should never be logged. If you see tokens in logs, you have a security issue that needs immediate attention.

### Environment Variable Validation

Create a test that verifies your environment variables are correctly loaded. Some functions include a diagnostic endpoint that returns current configuration. Invoke this endpoint and verify that your environment variables show the expected values.

Check that HA_FEATURE_PRESET matches what you configured. Verify HA_TIMEOUT shows the correct number. Confirm HOME_ASSISTANT_ENABLED shows true. If any values are incorrect, update your environment variables and test again.

---

## Feature-Specific Testing

Test specific features based on your feature preset and requirements.

### Device Control Testing

Test basic device control for each device type you have exposed. For lights, test turning them on and off. Test setting brightness levels if your lights support dimming. Test color changes if you have color-capable lights.

For switches, test on and off commands. For climate devices, test setting temperature and changing modes between heat, cool, and auto. For locks, test locking and unlocking. For covers like garage doors or blinds, test opening, closing, and stopping.

Create a test event for each command type. Run the test and verify the response indicates success. Check your Home Assistant instance to confirm the device actually changed state. If the Lambda function reports success but the device did not change, the problem is between Home Assistant and the device rather than between Lambda and Home Assistant.

### Scene Activation Testing

If your feature preset includes scene support, test activating scenes through Lambda. Create a test event that requests scene activation. Include the scene entity ID in the request.

Run the test and verify the response indicates successful scene activation. Check your Home Assistant instance to confirm the scene ran and devices changed to the expected states. If the scene did not activate, verify that scenes are exposed in your Home Assistant Alexa integration and that the HA_FEATURE_PRESET includes scene support.

### Script Execution Testing

For feature presets that include script support, test running scripts through Lambda. Create a test event requesting script execution with a specific script entity ID.

Verify the script runs successfully and completes all its actions. Check Home Assistant logs to see the script execution. If the script fails, ensure it works when executed directly through Home Assistant before troubleshooting the Lambda integration.

### Custom Assistant Name Testing

If you configured a custom assistant name, test that the function recognizes and uses this name in responses. Create test events that reference your custom name in the request. Verify that responses from the function also use your custom name when addressing the user.

Check that the name validation works correctly by trying to configure an invalid name. The function should reject names that violate the validation rules and fall back to the default name.

### Conversation Interface Testing

For advanced feature presets that include conversation support, test sending natural language commands. Create test events with conversational requests like what is the temperature in the bedroom or turn on all the lights in the kitchen.

Verify that the function processes these requests correctly and returns appropriate responses. Check that the conversation interface integrates properly with Home Assistant's conversation component.

---

## Performance Testing

Performance testing ensures your function responds quickly enough for good user experience with voice commands.

### Cold Start Testing

Lambda functions experience cold starts when AWS must initialize a new container to run your code. Test cold start performance by waiting several minutes between test invocations to ensure the function container has been terminated.

Invoke the function after this wait period and measure the duration. Cold starts should complete within 1000 to 1500 milliseconds for minimal and standard presets. Higher presets may take up to 2000 milliseconds for cold starts.

If cold starts take longer than 2000 milliseconds, verify that LUGS_ENABLED is set to true for lazy loading. Consider switching to a lower feature preset to reduce initialization time. Review your code package to ensure no unnecessary files are included that increase initialization overhead.

### Warm Execution Testing

Warm executions occur when Lambda reuses an existing container from a previous invocation. Test warm execution performance by running multiple test invocations in quick succession without waiting between them.

Measure the duration of the second and subsequent invocations. Warm executions should complete within 200 to 500 milliseconds depending on the complexity of the request and your network latency to Home Assistant.

If warm executions are slow, measure the time spent communicating with Home Assistant versus time spent in Lambda processing. Slow Home Assistant responses indicate a Home Assistant performance issue rather than a Lambda issue.

### Memory Usage Testing

Run tests while monitoring memory usage through CloudWatch metrics. Verify that memory usage stays well below your allocated limit. Usage should typically be between 15 and 30 megabytes depending on your feature preset.

If memory usage approaches your 128 megabyte limit, switch to a lower feature preset or increase allocated memory to 256 megabytes. Monitor memory usage over many invocations to identify any memory leaks where usage gradually increases without being released.

### Concurrent Request Testing

Test how the function handles multiple simultaneous requests. From different Alexa devices or using multiple test invocations started rapidly, generate concurrent requests to your function.

Verify that all requests complete successfully and that performance does not degrade significantly under concurrent load. Lambda automatically scales to handle concurrent requests by running multiple container instances simultaneously.

### Timeout Testing

Test scenarios that might approach your timeout limit. Execute complex scenes or scripts that take several seconds to complete. Monitor the duration to ensure operations complete well before your timeout setting.

If operations frequently approach the timeout limit, increase either the Lambda timeout or the HA_TIMEOUT environment variable to provide more time for completion.

---

## Security Validation

Validate that your deployment follows security best practices and does not expose sensitive information.

### Access Token Protection

Verify that your access token is stored as a SecureString in Parameter Store. Attempt to read the parameter through the AWS Console. You should not be able to see the decrypted value unless you use an AWS CLI command with proper permissions.

Check CloudWatch Logs to confirm that access tokens never appear in log output. Search logs for your token string. If you find it, you have a logging vulnerability that must be fixed immediately.

Test that only your Lambda execution role can read the token parameter. Try to read the parameter using an IAM user without the necessary permissions. The attempt should fail with an access denied error.

### IAM Permission Validation

Review your Lambda execution role permissions. Verify that the role has only the permissions it needs and no excess privileges. The role should include AWSLambdaBasicExecutionRole for logging and AmazonSSMReadOnlyAccess for Parameter Store but nothing more.

Attempt to invoke your Lambda function using IAM credentials that do not have Lambda invocation permission. The attempt should fail, confirming that only authorized principals can invoke your function.

Verify that your Alexa Skills Kit trigger properly validates the Skill ID. Try to invoke the function with a request that does not include the correct Skill ID. Lambda should reject the invocation.

### Network Security Testing

Test your SSL configuration by examining the SSL handshake during Home Assistant connection. If you use valid SSL certificates, the connection should verify successfully with HA_VERIFY_SSL set to true.

If you use self-signed certificates, verify that connections fail when HA_VERIFY_SSL is true and succeed when it is false. This confirms that SSL verification is actually occurring.

Test that your Home Assistant instance is not accessible through unencrypted HTTP if you configured HTTPS. Attempting to connect via HTTP should fail or redirect to HTTPS.

### Parameter Store Encryption

Verify that your SecureString parameters are actually encrypted. Use the AWS CLI to describe the parameter and check its type. Confirm it shows SecureString rather than String.

Test that changing the encryption key for Parameter Store parameters works correctly. This ensures you can rotate encryption keys if needed for security compliance.

---

## Regression Testing

Regression testing ensures that changes to your configuration or code do not break existing functionality.

### Configuration Change Testing

Before making configuration changes in production, test them in a development environment if possible. If you must test in production, document your current configuration so you can revert changes if problems occur.

After changing environment variables, run your complete test suite to verify that all previously working features still function. Pay special attention to features that might be affected by the specific variable you changed.

When updating Parameter Store values, test immediately after the change. Remember that cached values may delay when the change takes effect. Wait for the cache to expire or restart the function to force the new values to load.

### Code Update Testing

Before deploying new code versions, test them thoroughly in a separate Lambda function or development environment. Run the complete test suite against the new code. Compare performance metrics to the previous version to ensure the update does not degrade performance.

After deploying a code update to production, run abbreviated smoke tests to quickly verify core functionality. If critical features fail, immediately roll back to the previous code version while you diagnose the issue.

### Device Addition Testing

When you add new devices to Home Assistant and expose them to Alexa, run device discovery through the Alexa app. Verify that new devices appear correctly. Test controlling each new device to ensure it responds properly.

Check that adding new devices did not cause existing devices to stop working. Sometimes entity ID changes or configuration conflicts can affect other devices when you add new ones.

### Integration Update Testing

When Home Assistant or the Alexa integration updates, retest your Lambda function integration. Major Home Assistant updates sometimes change API behavior or entity structures that might affect Lambda function compatibility.

After updating the Alexa integration in Home Assistant, re-run device discovery and test device control to ensure the update did not break the integration.

---

## Automated Testing

While manual testing is important, automated testing provides consistent validation and catches regressions quickly.

### Lambda Test Events Library

Build a library of Lambda test events covering common scenarios. Create events for device discovery, turning devices on and off, scene activation, script execution, and error conditions.

Name your test events descriptively so you can identify them easily. Organize them into categories like device-control, scenes, scripts, and errors. Save all test events so you can run them repeatedly as you make changes.

### Test Event Documentation

Document what each test event does and what response it should produce. Include expected duration ranges and memory usage. This documentation helps you identify when test results deviate from normal behavior.

Create a checklist that lists all your test events. After making changes, work through the checklist running each test and verifying it passes. This systematic approach ensures you do not skip critical tests.

### CloudWatch Alarms

Set up CloudWatch alarms to alert you when your function experiences errors or performance degradation. Create an alarm that triggers when error count exceeds a threshold. Set up an alarm for high execution duration or memory usage.

Configure alarms to send notifications through email or SMS so you know immediately when problems occur. This allows you to respond quickly before users experience widespread issues.

### Monitoring Dashboard

Create a CloudWatch dashboard that displays key metrics for your Lambda function. Include graphs for invocation count, duration, memory usage, error count, and throttles.

Review the dashboard regularly to identify trends. Gradual increases in duration or memory usage may indicate developing problems that need attention before they cause failures.

---

## Test Checklists

These checklists provide quick reference for common testing scenarios.

### Initial Deployment Checklist

Verify all Parameter Store parameters exist and contain correct values. Confirm environment variables are set correctly in Lambda configuration. Test Lambda function execution with a simple test event. Run Home Assistant connection test to verify API access. Test device discovery to confirm entity exposure. Test basic device control for at least one device of each type. Check CloudWatch Logs for errors or warnings. Verify no sensitive information appears in logs. Test one complete voice command through Alexa. Document test results and any issues encountered.

### Configuration Change Checklist

Document current configuration before making changes. Apply configuration changes in environment variables or Parameter Store. Wait for cache expiration or force function restart. Run abbreviated smoke tests for core functionality. Test features specifically affected by the configuration change. Monitor CloudWatch metrics for any performance changes. If problems occur, revert configuration and retest. Document the change and test results.

### Code Update Checklist

Test new code in development environment before production deployment. Run complete test suite against new code. Compare performance metrics to previous version. Create new deployment package with updated code. Upload deployment package to Lambda function. Verify upload completed successfully and handler is correct. Run smoke tests immediately after deployment. Monitor error rates through CloudWatch. If critical issues occur, roll back to previous code version. Document the update and any issues encountered.

### Periodic Validation Checklist

Run complete test event library. Verify all tests pass with expected results. Check CloudWatch metrics for any unusual patterns. Review recent logs for any errors or warnings. Test voice commands through Alexa devices. Verify all exposed devices appear in Alexa app. Test device control for each device type. Check that scenes and scripts activate correctly. Verify response times remain acceptable. Document test date and results.

---

## Conclusion

Systematic testing ensures your Lambda Execution Engine deployment works correctly and continues working as you make changes. Use the checklists and procedures in this guide to validate your installation thoroughly. Regular testing catches problems early before they affect users and helps maintain a reliable smart home voice control system.
