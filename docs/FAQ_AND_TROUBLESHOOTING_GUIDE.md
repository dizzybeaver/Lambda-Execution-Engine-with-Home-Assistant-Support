# Lambda Execution Engine - FAQ and Troubleshooting Guide

**Version:** 2025.10.10  
**Purpose:** Answers to common questions and solutions to frequent problems

---

## Table of Contents

1. [Frequently Asked Questions](#frequently-asked-questions)
2. [Setup and Configuration Issues](#setup-and-configuration-issues)
3. [Connection Problems](#connection-problems)
4. [Device Control Issues](#device-control-issues)
5. [Performance Problems](#performance-problems)
6. [Security Questions](#security-questions)
7. [Advanced Troubleshooting](#advanced-troubleshooting)

---

## Frequently Asked Questions

### What does this Lambda function actually do?

The Lambda Execution Engine is a general-purpose Lambda optimization framework providing services like gateway routing, lazy loading, caching, circuit breaker protection, logging, and metrics. The Home Assistant Extension is one extension built on this framework. When loaded, it acts as a translator between Amazon Alexa and your Home Assistant installation, using the Engine's services to implement this functionality efficiently.

When you speak a command to Alexa, your voice travels to Amazon's servers. Amazon processes your speech and determines you are asking a skill to do something. Amazon then sends a structured request to your Lambda function. Your Lambda function interprets this request through the Home Assistant Extension, which translates it into the appropriate Home Assistant API calls, sends those calls to your Home Assistant instance, receives the response, and sends a formatted reply back to Amazon. Amazon then tells Alexa what to say to you.

This process happens in milliseconds. The Lambda function handles the complexity of understanding different types of Alexa requests, managing authentication with Home Assistant, retrying failed requests, caching information for performance, and formatting responses that Alexa can understand. You benefit from this without needing to write any code yourself.

### What is the difference between the Engine and the Home Assistant Extension?

The Lambda Execution Engine is a complete, standalone framework that provides optimized services for building Lambda functions. It implements the Single Universal Gateway Architecture where all operations flow through one entry point. It provides lazy loading to minimize memory usage, caching to reduce external API calls, circuit breaker protection to handle service failures gracefully, comprehensive logging, and performance metrics collection. The Engine can run entirely by itself without any extensions.

The Home Assistant Extension is self-contained code that uses the Engine's services to provide Home Assistant integration. The extension implements device discovery, state queries, and device control by calling the Engine's gateway, using the Engine's HTTP client for API communication, leveraging the Engine's caching for performance, and relying on the Engine's circuit breaker for reliability. The extension depends on the Engine, but the Engine does not depend on the extension.

This architecture allows you to build other extensions using the same Engine services. You could create a Google Assistant extension, a SmartThings extension, or extensions for entirely different purposes, all benefiting from the Engine's optimizations.

### How much does this cost to run?

AWS provides a generous free tier for Lambda functions. The free tier includes one million requests per month and 400,000 gigabyte-seconds of compute time per month. A typical smart home uses between 1,000 and 2,000 requests per month, depending on how often you use voice commands. Each request uses approximately 25 megabytes of memory and executes in under one second, which translates to about 0.025 gigabyte-seconds per request.

At 2,000 requests per month using 0.025 gigabyte-seconds each, you consume 50 gigabyte-seconds, which is well within the 400,000 gigabyte-second free tier allowance. Unless your usage is extremely high, you will not incur any Lambda charges. Parameter Store and CloudWatch Logs also have free tiers that cover typical smart home usage. Most users pay nothing for this integration.

### Do I need to keep my computer running?

No, you do not need to keep any computer running for the Lambda function to work. Lambda is a serverless compute service, which means AWS manages all the servers and infrastructure. Your code runs in Amazon's data centers on servers that AWS maintains. When Alexa needs to invoke your function, AWS automatically allocates resources, runs your code, and then deallocates those resources.

You do need to keep your Home Assistant instance running since the Lambda function needs to communicate with it to control your devices. Home Assistant typically runs on a Raspberry Pi, a dedicated computer, or a server that stays on continuously. The Lambda function in AWS communicates with your Home Assistant instance over the internet.

### Can I use this without Alexa?

The Lambda Execution Engine with the Home Assistant Extension is specifically designed to work with Amazon Alexa. The code expects to receive requests in the Alexa Smart Home API format and returns responses in that format. Without Alexa, the function would not receive properly formatted requests and could not operate correctly.

If you want to control Home Assistant through other voice assistants like Google Assistant or Apple HomeKit, you would need different integrations specifically designed for those platforms. Home Assistant provides native integrations for these services that do not require Lambda functions. However, you could build additional extensions for the Lambda Execution Engine to support other platforms using the same Engine services.

### Will this work with different connection methods?

Yes, the Lambda Execution Engine works with several connection methods for reaching your Home Assistant instance. You can use a direct HTTPS connection with a valid SSL certificate if your Home Assistant has a public domain name. You can use a direct HTTPS connection with SSL verification disabled if you have a self-signed certificate. You can connect over HTTP for local network testing though this is not recommended for production use. You can also establish a VPN connection between AWS and your home network for maximum security.

Each connection method has its own configuration requirements. Direct connections require your Home Assistant to be accessible from the internet. VPN connections require setting up AWS VPC and VPN gateway infrastructure. The choice of connection method depends on your security requirements, network setup, and technical comfort level.

### What happens if my internet goes down?

If your internet connection fails, Alexa will not be able to reach your Lambda function or your Home Assistant instance. Voice commands through Alexa will fail with an error message indicating the service is unavailable. Your local devices that do not depend on cloud services will continue working with their physical controls, but voice control and remote control will not function until internet connectivity restores.

When internet connectivity returns, the Lambda function and Home Assistant will begin working again automatically. No configuration changes or manual intervention are required. The circuit breaker protection in the Lambda function prevents it from repeatedly trying to contact Home Assistant during extended outages, which helps it recover quickly once connectivity returns.

### Can multiple people use this at the same time?

Yes, multiple people can issue voice commands to Alexa simultaneously from different rooms or devices. Each command creates a separate invocation of your Lambda function. AWS automatically scales Lambda functions to handle concurrent requests. If three people ask Alexa to do different things at the same moment, AWS runs three simultaneous copies of your function to process all three requests.

However, Home Assistant itself may have limitations on concurrent API requests depending on your hardware and configuration. If many concurrent requests arrive at Home Assistant simultaneously, it might slow down or queue requests. For typical household usage with a small number of people, this is rarely a problem.

### How do I update the Lambda function code?

When new versions of the Lambda Execution Engine become available, you can update your function by creating a new deployment package with the updated code files and uploading it through the Lambda console. Navigate to your Lambda function, click on the Code tab, click Upload From, and select ZIP File. Choose your new deployment package and click Save.

The update takes effect immediately on the next function invocation. AWS keeps previous versions of your code, so you can roll back if the new version has problems. Before updating production deployments, test new versions thoroughly to ensure they work correctly with your configuration.

### What is the gateway architecture?

The gateway architecture is a design pattern where all operations flow through a single entry point called the gateway. Instead of having separate modules that communicate directly with each other, everything goes through the gateway. When Alexa sends a request, it arrives at the gateway. The gateway determines what needs to happen, delegates work to the appropriate modules, collects their responses, and sends the final response back to Alexa.

This architecture provides several benefits. It enables lazy loading, where modules are only imported when they are needed rather than all at startup. It centralizes error handling so errors are caught and managed consistently. It simplifies monitoring because all operations pass through one point where you can log and measure them. It reduces memory usage because modules that are not needed for a particular request are never loaded.

### Can I use this for both Alexa and other platforms?

The Lambda Execution Engine is designed as a general-purpose framework that can support multiple extensions. Currently, the Home Assistant Extension provides Alexa integration. However, the Engine's architecture allows you to build additional extensions for other voice assistants or platforms.

You could create a Google Assistant extension that uses the same Engine services for gateway routing, HTTP communication, caching, and circuit breaker protection while implementing Google-specific device discovery and control. Similarly, you could build extensions for SmartThings, Apple HomeKit, or entirely different purposes. Each extension would be self-contained and use the Engine's services without modifying the Engine core itself.

---

## Setup and Configuration Issues

### Parameter Store values are not being used

If your Lambda function does not seem to use values from Parameter Store, first verify that USE_PARAMETER_STORE is set to true in your environment variables. Without this variable set to true, the function will not attempt to read from Parameter Store.

Check that your PARAMETER_PREFIX environment variable matches the path structure you used when creating parameters. If you created parameters starting with /lambda-execution-engine but set PARAMETER_PREFIX to a different value, the function will look in the wrong location and not find your parameters.

Verify that your Lambda IAM role has the AmazonSSMReadOnlyAccess policy attached. Without this permission, the function cannot read Parameter Store values even if everything else is configured correctly. Navigate to IAM in the AWS Console, find your Lambda execution role, and confirm the policy is listed under permissions.

Check that you created parameters in the same AWS region where your Lambda function runs. Parameter Store values are region-specific. If you created parameters in us-east-1 but your Lambda function runs in us-west-2, the function will not find the parameters. Create parameters in the same region or set the AWS_REGION environment variable to the region where your parameters exist.

### Environment variables are not taking effect

If you change environment variables but do not see the changes reflected in function behavior, first confirm you clicked Save after editing the variables. Unsaved changes do not apply to your function. AWS displays a banner indicating unsaved changes before you click Save.

After saving environment variables, the changes take effect on the next function invocation. If your function is warm from recent invocations, it may still be using cached configuration. Wait a few minutes for the function to cool down, or manually deploy a new version to force reinitialization.

Verify the variable names are spelled exactly as expected. Environment variable names are case-sensitive. HA_TIMEOUT works correctly while ha_timeout or HA_Timeout would not be recognized. Compare your variable names against the documentation to ensure correct spelling.

### Lambda function fails to create

If Lambda function creation fails with a permission error, verify that your IAM user account has permission to create Lambda functions. You need IAM permissions for lambda:CreateFunction at minimum. If you are using an IAM user rather than the root account, ensure your user has the necessary Lambda permissions.

If function creation fails with a role error, confirm that the IAM role you selected exists and grants Lambda service permission to assume it. Navigate to IAM, find the role, and verify that the trust relationship allows lambda.amazonaws.com to assume the role. If the trust relationship is incorrect, edit the role and fix the trust policy.

If creation fails with a quota error, you may have reached the limit for Lambda functions in your region. AWS imposes service quotas to prevent runaway resource creation. Check your service quotas in the AWS Console under Service Quotas. You can request quota increases if needed, though the default quotas are usually sufficient for personal projects.

Note that Lambda function creation succeeds whether or not you plan to use the Home Assistant Extension. The Engine creates successfully with HOME_ASSISTANT_ENABLED set to false.

### Deployment package upload fails

If uploading your ZIP file fails, first check the file size. Lambda has a 50 megabyte limit for direct ZIP file uploads. The Lambda Execution Engine code is much smaller than this limit, but if you accidentally included unnecessary files in your ZIP, it might exceed the limit. Verify your ZIP contains only Python files and no additional directories, images, or documentation.

If upload succeeds but the function shows an error about missing handler, verify that your Python files are at the root level of the ZIP archive. The files should not be inside a folder within the ZIP. When you open the ZIP file, you should see lambda_function.py and other Python files immediately, not a folder containing those files.

If the upload is very slow, your internet connection may be the bottleneck. Lambda deployment packages upload from your computer to AWS over your internet connection. Slow upload speeds can make large packages take several minutes to upload. Be patient and wait for the upload to complete rather than canceling and retrying, which will start the process over.

---

## Connection Problems

### Cannot connect to Home Assistant

If the Lambda function cannot connect to your Home Assistant instance, first verify that Home Assistant is running and accessible. Try accessing your Home Assistant URL from a web browser. If you cannot reach Home Assistant from your browser, the Lambda function will not be able to reach it either.

Check that the URL in your Parameter Store or environment variable is correct and complete. The URL should include the protocol (http or https), the full hostname or IP address, and the port if you use a non-standard port. For example, https://home.example.com or http://192.168.1.100:8123. Test the exact URL you configured by pasting it into a web browser.

Verify that your Home Assistant is accessible from the internet if you are using a direct connection method. Some Home Assistant installations run only on local networks and cannot be reached from AWS. You need either port forwarding, a VPN, or a tunneling service to make local Home Assistant instances accessible from AWS.

Check your firewall settings both on your router and on the computer running Home Assistant. Firewalls may block incoming connections even if port forwarding is configured correctly. Temporarily disable firewalls for testing to determine if they are causing the connection problem.

### SSL certificate verification fails

If you see SSL certificate verification errors in your logs, your Home Assistant instance is using an SSL certificate that AWS does not trust. This commonly happens with self-signed certificates that you generated yourself rather than obtaining from a certificate authority.

The simplest solution is to set HA_VERIFY_SSL to false in your environment variables. This tells the Lambda function to accept the certificate without verification. The connection is still encrypted, but the function does not validate the certificate's authenticity. This solution works fine for home use where you control both ends of the connection.

For a more secure solution, obtain a valid SSL certificate from a certificate authority. Let's Encrypt provides free SSL certificates that are trusted by all major clients including AWS. Many DNS providers and domain registrars offer integrated Let's Encrypt support that automates certificate issuance and renewal.

### Connection timeout errors

Connection timeout errors mean the Lambda function waited for Home Assistant to respond but did not receive a response within the timeout period. This suggests Home Assistant is reachable but responding too slowly.

Check Home Assistant's performance. If Home Assistant is running on underpowered hardware or processing many automations, it may respond slowly to API requests. Monitor Home Assistant's resource usage including CPU, memory, and disk I/O to identify bottlenecks.

Increase the HA_TIMEOUT value to give Home Assistant more time to respond. The default is 30 seconds, but you can increase this to 45 or 60 seconds if your Home Assistant instance consistently requires more time. However, higher timeouts mean users wait longer when genuine problems occur.

Verify your network connection between AWS and Home Assistant. Network latency and packet loss can cause slow responses even when Home Assistant performs well. Use network diagnostic tools to measure round-trip time and packet loss from AWS to your home network.

### Authentication failures

Authentication failures indicate that Home Assistant is rejecting the access token your Lambda function provides. This usually means the token is invalid, expired, or configured incorrectly.

Generate a new long-lived access token in Home Assistant. Open your user profile in Home Assistant, scroll to Long-Lived Access Tokens, and create a new token. Copy this token immediately because Home Assistant will not display it again.

Update your Parameter Store with the new token. Navigate to Parameter Store in AWS Systems Manager, find the homeassistant/token parameter, and update its value with the new token. Ensure you update the correct parameter and do not create a duplicate parameter with a slightly different name.

Verify that the token grants the necessary permissions in Home Assistant. Tokens are associated with a user account, and that user account must have permission to view and control the entities you want the Lambda function to access. Check that your Home Assistant user account has appropriate permissions.

---

## Device Control Issues

### Alexa cannot find devices

If Alexa fails to find any devices during discovery, verify that Home Assistant is accessible and your access token works correctly. Test your connection by manually invoking your Lambda function with a test discovery request to see if it successfully retrieves devices from Home Assistant.

Check that you have entities exposed for Alexa in Home Assistant. By default, Home Assistant does not expose all entities to Alexa. You must explicitly mark entities as exposed. In Home Assistant, navigate to each entity's settings and enable Alexa exposure.

Verify that the device discovery process completes successfully in the Lambda function logs. CloudWatch logs will show whether the function successfully contacted Home Assistant, retrieved the entity list, and returned a properly formatted discovery response to Alexa.

Give Alexa time to process discovery results. The discovery process can take up to 45 seconds for large numbers of devices. If you cancel discovery too quickly, Alexa may not complete importing your devices. Let the discovery process finish completely before concluding it failed.

### Commands work but devices do not respond

If Alexa acknowledges commands but your devices do not actually change state, the problem likely lies in the communication between the Lambda function and Home Assistant. Check CloudWatch logs to verify that the Lambda function is sending commands to Home Assistant.

Verify that the entity IDs the Lambda function sends to Home Assistant match your actual entities. The function uses the entity ID Alexa provides, which is based on information from the discovery response. If entity IDs changed in Home Assistant after discovery, commands will fail.

Test device control directly in Home Assistant to ensure your devices work correctly. If a device does not respond to commands in Home Assistant's interface, the Lambda function cannot control it either. Troubleshoot the device in Home Assistant first.

Check for automation or script errors in Home Assistant that might interfere with device control. Complex automations or scripts that trigger on state changes could potentially prevent or override commands sent through the Lambda function.

### Some devices work while others do not

When some devices work correctly while others fail, the problem usually involves device-specific configuration or capabilities. Compare the working and non-working devices to identify differences.

Verify that all devices are properly exposed to Alexa in Home Assistant. It is easy to accidentally expose some entities while forgetting others. Check each device's exposure settings in Home Assistant.

Check CloudWatch logs for errors specific to the failing devices. The logs will show which entity IDs fail and may provide error messages explaining why. Common issues include unsupported entity types, missing required attributes, or devices that are unavailable in Home Assistant.

Test the failing devices directly in Home Assistant to ensure they work correctly there. If a device does not work in Home Assistant, the Lambda function cannot control it.

### Scene or script activation fails

Scene and script activation failures often result from incorrect entity IDs or missing exposures. Verify that you exposed the scene or script entity to Alexa in Home Assistant. Scenes and scripts must be explicitly exposed just like device entities.

Check that the scene or script executes correctly when triggered manually in Home Assistant. If it does not work in Home Assistant, it will not work through the Lambda function.

Review CloudWatch logs for detailed error messages about scene or script activation. The logs will indicate whether the Lambda function successfully sent the activation command to Home Assistant and what response Home Assistant returned.

---

## Performance Problems

### Lambda function is slow

If your Lambda function responds slowly, first determine whether the slowness occurs during cold starts or warm invocations. Cold starts happen when AWS allocates resources for a new function instance, while warm invocations use an already-running instance. Cold starts naturally take longer.

Cold start performance improves by minimizing your deployment package size and enabling LUGS for lazy loading. Remove any unnecessary files from your deployment package. Ensure LUGS_ENABLED is set to true so the function only loads modules it actually needs for each request.

Warm invocation slowness usually indicates performance issues in Home Assistant or network problems. Check Home Assistant's response time by reviewing its logs. Slow database queries, heavy automations, or resource exhaustion can all slow Home Assistant responses.

Monitor CloudWatch metrics for your Lambda function to identify specifically where time is spent. The metrics show how long each invocation takes and can help isolate whether delays occur in Lambda processing, network communication, or Home Assistant responses.

### High memory usage

High memory usage can indicate that too many modules are loading or caching is using excessive memory. Check your CONFIGURATION_TIER setting and consider lowering it to a tier that uses less memory. The minimum tier uses only 8 megabytes while the maximum tier uses over 100 megabytes.

Verify that LUGS is enabled and functioning correctly. Without lazy loading, all modules load at startup which significantly increases memory usage. CloudWatch logs will show which modules load during function initialization.

Review your feature preset setting if using the Home Assistant Extension. Higher feature presets like performance and maximum load more features into memory. The minimal or standard preset uses much less memory.

Monitor actual memory usage in CloudWatch rather than relying on Lambda's allocated memory. Lambda allocates memory in fixed increments, but your function may use much less than allocated. CloudWatch metrics show actual memory consumption during invocations.

### Frequent timeout errors

Frequent timeout errors suggest that Home Assistant cannot respond within the configured timeout period. This may result from Home Assistant performance problems, network issues, or an unrealistically short timeout setting.

Increase the HA_TIMEOUT environment variable to give Home Assistant more time to respond. Try 45 or 60 seconds instead of the default 30 seconds. This prevents timeouts when Home Assistant legitimately needs extra time but increases user wait time when genuine problems occur.

Investigate Home Assistant performance if increasing timeout does not help. Check Home Assistant's CPU, memory, and database performance. Consider optimizing automations, cleaning up the database, or upgrading hardware if Home Assistant consistently responds slowly.

Check network connectivity between AWS and your Home Assistant instance. High latency or packet loss can cause responses to arrive too slowly even when Home Assistant processes requests quickly. Use network monitoring tools to measure connection quality.

---

## Security Questions

### Is my access token secure?

When stored properly in Parameter Store as a SecureString, your access token is encrypted at rest using AWS encryption. Only your Lambda function can decrypt it because only your Lambda IAM role has permission to read that specific parameter. The token never appears in logs or error messages.

The Lambda function retrieves your token from Parameter Store when it initializes and holds it in memory only during request processing. When the function completes, all memory is cleared and the token disappears. AWS automatically secures the Lambda runtime environment, so other AWS customers cannot access your function's memory.

Transmission of the token between Lambda and Home Assistant occurs over HTTPS when you set HA_VERIFY_SSL to true. The encrypted connection prevents the token from being intercepted during transmission. Never use HTTP connections over the public internet as they would expose your token.

### Can someone else invoke my Lambda function?

By default, your Lambda function requires AWS credentials to invoke. Only accounts and IAM users with appropriate permissions in your AWS account can invoke the function. Alexa invokes your function using a special trigger that you must explicitly configure, which authorizes Alexa to invoke it without AWS credentials.

The Alexa trigger is specific to your Alexa skill. Only your Alexa skill can invoke your function, and only users who have enabled your skill in their Alexa app can trigger invocations. This limits function invocations to authorized Alexa users.

Monitor CloudWatch metrics for unusual invocation patterns. High invocation counts or invocations at unexpected times might indicate unauthorized access. CloudWatch alarms can notify you of abnormal activity.

### Should I use VPN for maximum security?

VPN provides the highest security level for Lambda-to-Home Assistant communication. With VPN, all traffic flows through an encrypted tunnel between AWS and your home network. No traffic traverses the public internet, eliminating exposure to potential interception.

However, VPN adds significant complexity to your setup. You must create an AWS VPC, configure a VPN gateway, set up your Lambda function to run inside the VPC, establish the VPN connection to your home network, and maintain the VPN infrastructure. This complexity may not be justified for typical home automation use.

For most home users, HTTPS with a valid SSL certificate provides adequate security. The connection is encrypted end-to-end, and only your Lambda function can access your token. This provides strong protection for the majority of use cases without VPN complexity.

### How often should I rotate access tokens?

Rotating access tokens periodically limits the damage if a token is compromised. A compromised token only remains valid until you rotate it. Best practice suggests rotating tokens every 90 to 180 days even if you have no reason to believe they have been compromised.

When you rotate tokens, generate a new long-lived access token in Home Assistant and update Parameter Store with the new value. The Lambda function will use the new token on its next invocation after reading the updated parameter. No code changes or function redeployment are required.

After updating Parameter Store, revoke the old token in Home Assistant. This ensures the old token cannot be used even if someone obtained it. Only the new token will work after revocation.

If you suspect a token has been compromised, rotate it immediately rather than waiting for a scheduled rotation. Generate a new token, update Parameter Store, test that the new token works, and revoke the old token as quickly as possible.

---

## Advanced Troubleshooting

### Reading CloudWatch Logs

CloudWatch Logs contain detailed information about every Lambda function invocation. These logs are essential for troubleshooting because they show exactly what your function did, what errors occurred, and how long operations took.

Navigate to CloudWatch in the AWS Console, then select Log Groups. Find the log group for your Lambda function, which will be named /aws/lambda/lambda-execution-engine or similar. Click on the log group to see log streams.

Each log stream represents a separate instance of your Lambda function. When AWS scales your function to handle concurrent requests, it creates multiple instances, each with its own log stream. Click on a log stream to see the actual log messages.

Log messages appear in chronological order and include timestamps. Look for error messages, warnings, and informational messages that describe what the function did during each invocation. ERROR level messages indicate problems that need attention.

Use the search feature to find specific text in logs. You can search for entity IDs, error types, or any other text that appears in log messages. This helps locate relevant messages in large volumes of logs.

### Using Lambda Test Events

Lambda provides a test feature that allows you to invoke your function manually with custom request data. This feature is invaluable for troubleshooting because it lets you test specific scenarios without needing to trigger them through Alexa.

Create test events that simulate different types of Alexa requests. A discovery test event simulates Alexa discovering your devices. A device control test event simulates turning a device on or off. A scene activation test event simulates activating a scene.

Run your test events and examine the results. The test feature shows both the response your function returned and execution logs. This allows you to see exactly what your function does when it receives specific requests.

Save multiple test events for different scenarios so you can quickly test various functions. Name your test events descriptively like discovery-test or light-on-test so you can identify them easily.

### Enabling Debug Logging

Setting DEBUG_MODE to true in environment variables enables verbose logging that provides much more detail about what your function does during execution. Debug mode logs include configuration values, intermediate calculations, detailed HTTP request and response information, and internal state information.

Debug logging helps diagnose complex problems where standard logs do not provide enough information. However, debug mode increases memory usage and log volume, which can increase costs if you generate massive amounts of log data.

Enable debug mode when troubleshooting specific problems, then disable it once you resolve the issue. Do not leave debug mode enabled in production unless you specifically need the extra logging for monitoring purposes.

### Circuit Breaker Diagnosis

The circuit breaker protects your system when Home Assistant becomes unavailable or unresponsive. When too many consecutive requests fail, the circuit breaker opens and immediately rejects requests without attempting to contact Home Assistant.

If you see circuit breaker errors in logs, it indicates your Home Assistant instance failed to respond to multiple consecutive requests. Check Home Assistant's availability and responsiveness. Verify that it is running and accessible. Check Home Assistant logs for errors or resource exhaustion.

The circuit breaker automatically closes after a recovery period. During this period, it occasionally allows a test request through to check if Home Assistant has recovered. If the test succeeds, the circuit closes and normal operation resumes.

Adjust HA_CIRCUIT_BREAKER_THRESHOLD to change how many failures trigger the circuit breaker. Higher values tolerate more failures before opening but may cause longer periods of failed requests during outages. Lower values protect Home Assistant more aggressively but may open the circuit breaker unnecessarily due to transient issues.
