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

The Lambda Execution Engine acts as a translator between Amazon Alexa and your Home Assistant installation. When you speak a command to Alexa, your voice travels to Amazon's servers. Amazon processes your speech and determines you are asking a skill to do something. Amazon then sends a structured request to your Lambda function. Your Lambda function interprets this request, translates it into the appropriate Home Assistant API calls, sends those calls to your Home Assistant instance, receives the response, and sends a formatted reply back to Amazon. Amazon then tells Alexa what to say to you.

This process happens in milliseconds. The Lambda function handles the complexity of understanding different types of Alexa requests, managing authentication with Home Assistant, retrying failed requests, caching information for performance, and formatting responses that Alexa can understand. You benefit from this without needing to write any code yourself.

### How much does this cost to run?

AWS provides a generous free tier for Lambda functions. The free tier includes one million requests per month and 400,000 gigabyte-seconds of compute time per month. A typical smart home uses between 1,000 and 2,000 requests per month, depending on how often you use voice commands. Each request uses approximately 25 megabytes of memory and executes in under one second, which translates to about 0.025 gigabyte-seconds per request.

At 2,000 requests per month using 0.025 gigabyte-seconds each, you consume 50 gigabyte-seconds, which is well within the 400,000 gigabyte-second free tier allowance. Unless your usage is extremely high, you will not incur any Lambda charges. Parameter Store and CloudWatch Logs also have free tiers that cover typical smart home usage. Most users pay nothing for this integration.

### Do I need to keep my computer running?

No, you do not need to keep any computer running for the Lambda function to work. Lambda is a serverless compute service, which means AWS manages all the servers and infrastructure. Your code runs in Amazon's data centers on servers that AWS maintains. When Alexa needs to invoke your function, AWS automatically allocates resources, runs your code, and then deallocates those resources.

You do need to keep your Home Assistant instance running since the Lambda function needs to communicate with it to control your devices. Home Assistant typically runs on a Raspberry Pi, a dedicated computer, or a server that stays on continuously. The Lambda function in AWS communicates with your Home Assistant instance over the internet.

### Can I use this without Alexa?

The Lambda Execution Engine is specifically designed to work with Amazon Alexa. The code expects to receive requests in the Alexa Smart Home API format and returns responses in that format. Without Alexa, the function would not receive properly formatted requests and could not operate correctly.

If you want to control Home Assistant through other voice assistants like Google Assistant or Apple HomeKit, you would need different integrations specifically designed for those platforms. Home Assistant provides native integrations for these services that do not require Lambda functions.

### Will this work with Cloudflare Tunnel?

Yes, Cloudflare Tunnel works excellently with the Lambda Execution Engine. Cloudflare Tunnel creates a secure connection from your Home Assistant instance to Cloudflare's network without requiring you to open ports on your firewall. When you configure Cloudflare Tunnel, you receive a public URL that routes to your local Home Assistant instance. You enter this URL in your Parameter Store configuration, and the Lambda function uses it to communicate with Home Assistant.

Cloudflare Tunnel provides valid SSL certificates automatically, so you can set HA_VERIFY_SSL to true for secure connections. This is the recommended method for exposing Home Assistant to the internet because it combines security, ease of setup, and reliability.

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

### Can I use this for both Alexa and Google Home?

This Lambda function is designed specifically for Alexa and uses the Alexa Smart Home API format. Google Home uses a different API format called Google Smart Home API. You would need a separate integration for Google Home.

However, your Home Assistant instance itself can support multiple voice assistants simultaneously. You can have the Lambda Execution Engine handling Alexa while using the native Google Assistant integration in Home Assistant for Google Home. Both can control the same devices through Home Assistant. You would just use Alexa commands for Alexa devices and Google commands for Google Home devices.

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

### Deployment package upload fails

If uploading your ZIP file fails, first check the file size. Lambda has a 50 megabyte limit for direct ZIP file uploads. The Lambda Execution Engine code is much smaller than this limit, but if you accidentally included unnecessary files in your ZIP, it might exceed the limit. Verify your ZIP contains only Python files and no additional directories, images, or documentation.

If upload succeeds but the function shows an error about missing handler, verify that your Python files are at the root level of the ZIP archive. If you unzip your deployment package, you should see Python files immediately, not a folder containing Python files. Repackage your ZIP ensuring files are at the root.

If upload succeeds but imports fail during execution, check that all required files are included in your ZIP package. Missing core files like gateway.py or configuration files like variables.py will cause import errors. Review the required files list in the deployment documentation and verify each file is present.

---

## Connection Problems

### Cannot connect to Home Assistant

If your Lambda function cannot connect to Home Assistant, first verify that your Home Assistant instance is accessible from the internet. Open a web browser on a device that is not connected to your home network, such as your phone using cellular data rather than WiFi. Navigate to the URL you configured in Parameter Store. If you cannot load the Home Assistant login page, your instance is not accessible from outside your network.

Check your router's port forwarding configuration if you use direct connection. Verify that traffic on port 443 or 8123 forwards to your Home Assistant device. Test the port forwarding using an online port checking tool. Confirm your firewall allows incoming connections on the forwarded port.

If you use Cloudflare Tunnel, verify the tunnel is running and connected. Check the Cloudflare Tunnel daemon logs on your Home Assistant host. Ensure the tunnel configuration points to the correct local address and port. Test the tunnel by accessing your Cloudflare URL directly in a browser.

Verify your Parameter Store URL is correct. Common mistakes include missing the protocol (https://), incorrect port numbers, or typographical errors in the domain name. The URL should match exactly how you access Home Assistant from outside your network.

### SSL certificate verification fails

If you see SSL verification errors in CloudWatch logs, your Home Assistant instance either does not have SSL certificates or uses self-signed certificates that cannot be verified. First, determine which SSL configuration you have.

For self-signed certificates, set HA_VERIFY_SSL to false in your Lambda environment variables. This tells the function to accept the SSL connection without verifying the certificate against a trusted authority. Note that this reduces security because it makes your connection vulnerable to man-in-the-middle attacks, but it allows the connection to work with self-signed certificates.

For Cloudflare Tunnel, SSL verification should work automatically because Cloudflare provides valid certificates. If you see verification errors with Cloudflare Tunnel, check that you are using the HTTPS URL Cloudflare provided, not an HTTP URL. Verify the tunnel is running and connected.

For direct connections with Let's Encrypt or other valid certificates, verification should work with HA_VERIFY_SSL set to true. If verification fails despite having valid certificates, check that your certificates are not expired. Verify that your Home Assistant SSL configuration includes the full certificate chain, not just the end certificate.

### Connection timeout errors

If requests to Home Assistant time out before completing, first check your network connection speed and latency. Use a speed test tool to measure your upload speed from your home network and download speed to your home network. Slow internet connections may not complete requests within the default 30-second timeout.

Increase the HA_TIMEOUT environment variable to give requests more time to complete. Try 45 or 60 seconds for slower connections or complex automations. Remember that Alexa itself has timeouts, so extremely long timeouts may cause Alexa to give up before your Lambda function returns a response.

Check your Home Assistant performance and resource usage. If Home Assistant is using all available CPU or memory, it may respond slowly to API requests. Review Home Assistant logs for performance warnings. Consider upgrading your Home Assistant hardware or reducing the number of integrations and automations if performance is consistently poor.

Verify that your Home Assistant instance is not blocking or rate-limiting requests from your Lambda function. Some firewall configurations or reverse proxy setups implement rate limiting that blocks rapid requests. Check your reverse proxy logs if you use one. Review Home Assistant configuration for any rate limiting settings.

### Authentication failures

If you see unauthorized or authentication errors, your Home Assistant access token may be invalid or expired. First, verify that you copied the complete token from Home Assistant when creating it. Tokens are long strings that must be copied exactly without any spaces or line breaks at the beginning or end.

Try generating a new long-lived access token from your Home Assistant profile page. Copy the new token carefully and update your Parameter Store value with the new token. Wait a few minutes for the change to propagate, then test again.

Check that the Home Assistant user account associated with your token has permission to control devices. Some Home Assistant configurations restrict which users can control which devices. Ensure your token's user account has administrative access or appropriate permissions for the devices you want to control.

Verify that you stored the token in Parameter Store as a SecureString type. While String type tokens can work, SecureString provides encryption and is the recommended type. If you used String type, the token might display differently than expected. Try recreating the parameter with SecureString type.

---

## Device Control Issues

### Alexa cannot find devices

If Alexa cannot find any devices during discovery, first verify that your Lambda function executed successfully. Check CloudWatch logs for the discovery request. The logs should show your Lambda function receiving a discovery directive from Alexa and sending back a list of devices.

If the Lambda function never executed, verify that you added the Alexa trigger to your Lambda function with the correct Skill ID. The trigger must use the exact Skill ID from your Alexa skill in the developer console. Check that the trigger is enabled and not accidentally disabled.

If the Lambda function executed but returned an empty device list, check that you exposed entities in your Home Assistant configuration. Navigate to Home Assistant's Alexa integration settings and verify that entities are toggled on for exposure. Alternatively, if you use the customize method, check that entities have expose: true in configuration.yaml.

Verify that the entities you want to expose are actually supported entity types. The Lambda function can discover lights, switches, climate devices, locks, covers, and scenes. Other entity types like sensors or binary sensors may not appear in device discovery depending on their configuration.

### Commands work but devices do not respond

If Alexa acknowledges your commands but the physical devices do not change state, the problem likely exists between Home Assistant and your devices rather than between Alexa and Home Assistant. Test controlling the devices directly through the Home Assistant web interface. If the devices respond through Home Assistant, the issue is with Lambda or Alexa. If they do not respond through Home Assistant, the issue is with your Home Assistant device configuration.

Check Home Assistant logs for messages when you issue voice commands. You should see incoming API requests from your Lambda function. If these requests appear in the logs, Home Assistant received the command from Lambda. If the device still does not respond, check the device's integration logs for errors or warnings.

Verify that entity IDs match between Alexa and Home Assistant. Sometimes entity IDs get out of sync if you rename devices. When this happens, Alexa tries to control an entity that no longer exists under that ID. Re-run device discovery in the Alexa app to refresh entity IDs.

Check for temporary device connectivity issues. Some smart devices occasionally disconnect from Home Assistant and reconnect after a few minutes. If commands usually work but occasionally fail, this suggests intermittent device connectivity rather than a configuration problem.

### Some devices work while others do not

If some devices respond to Alexa commands while others do not, focus on the differences between working and non-working devices. Check whether non-working devices are exposed in your Home Assistant Alexa integration. Devices that are not exposed will not be discovered by Alexa.

Verify that non-working devices are in a responsive state in Home Assistant. Devices that are unavailable or in an error state in Home Assistant will not respond to commands even if Alexa sends them. Check the device's status in Home Assistant and troubleshoot the device's connection to Home Assistant first.

Check for entity naming conflicts. If two devices have very similar names, Alexa might confuse them or send commands to the wrong device. Review your device names in both Home Assistant and the Alexa app. Rename devices with similar names to make them more distinct.

Test non-working devices directly through the Home Assistant API using a tool like curl or Postman. If they respond to direct API calls but not to Alexa commands, the issue involves how Alexa formats the requests or how the Lambda function translates them. Check CloudWatch logs to see the exact API calls being made for non-working devices.

### Scene or script activation fails

If activating scenes or scripts through Alexa fails, first verify that scenes and scripts are exposed in your Home Assistant Alexa integration. Scenes and scripts must be explicitly exposed like other entities.

Check that your HA_FEATURE_PRESET includes scene and script support. The minimal preset does not include these features. You need at least the standard preset for scene activation and script execution.

Verify that scenes and scripts work when activated directly through Home Assistant. If they fail when activated manually, they will also fail when activated through Alexa. Review scene and script configurations for errors. Check Home Assistant logs when activating them manually to diagnose configuration issues.

Some scenes or scripts take longer to execute than others, especially if they control many devices or include delays. If a scene times out, try increasing HA_TIMEOUT to give it more time to complete.

---

## Performance Problems

### Lambda function is slow

If your Lambda function responds slowly, first check whether the slowness occurs on cold starts or all invocations. Cold starts happen when Lambda needs to initialize a new container to run your function. This initialization includes loading Python, importing modules, and establishing connections. Cold starts typically take longer than subsequent invocations.

To improve cold start performance, verify that LUGS_ENABLED is set to true. This enables lazy loading which reduces the number of modules that load during initialization. Consider switching to a lower HA_FEATURE_PRESET like minimal or standard to load fewer modules.

If all invocations are slow, not just cold starts, the problem likely involves network latency between Lambda and Home Assistant. Measure the time Home Assistant takes to respond to API calls. You can do this by checking CloudWatch logs which include timestamps for request start and response receipt.

Reduce network latency by ensuring your Home Assistant instance has good internet connectivity. If you use port forwarding over residential internet, upload speeds may be slow. Consider switching to Cloudflare Tunnel which often provides better performance for incoming connections.

### High memory usage

If your Lambda function approaches the 128 megabyte memory limit, reduce memory consumption by switching to a lower HA_FEATURE_PRESET. The minimal preset uses approximately 15 megabytes while the maximum preset can use 30 megabytes or more.

Reduce HA_CACHE_TTL to decrease cache memory usage. Caching saves memory by storing frequently accessed data, but large caches can use significant memory. Experiment with lower cache TTL values to find a balance between performance and memory usage.

Verify that LUGS_ENABLED is set to true. Without lazy loading, all modules load into memory even if they are not used for a particular request. Lazy loading significantly reduces memory consumption.

Monitor memory usage through CloudWatch metrics over time. Occasional spikes in memory usage during complex operations are normal. If memory usage consistently remains high across many invocations, you may need to increase allocated memory to 256 megabytes or reduce your feature preset.

### Frequent timeout errors

If your Lambda function times out frequently before completing requests, first determine whether the timeout occurs in Lambda itself or in communication with Home Assistant. Check CloudWatch logs for the last log entry before the timeout. If logs show the function trying to contact Home Assistant, the timeout likely occurs waiting for Home Assistant's response.

Increase HA_TIMEOUT to give Home Assistant more time to respond. Some automations or scenes take several seconds to execute fully. Make sure HA_TIMEOUT is high enough to accommodate your slowest operations.

Increase the Lambda function timeout in Lambda's general configuration. The default 30-second timeout should be sufficient for most operations, but if you have complex automations, you might need 45 or 60 seconds.

If timeouts occur during discovery requests specifically, you might have many devices exposed which take time to enumerate. Consider exposing only devices you actually control through voice commands. Reducing the number of exposed devices speeds up discovery.

---

## Security Questions

### Is my access token secure?

Your Home Assistant access token is stored in AWS Systems Manager Parameter Store as a SecureString type. AWS encrypts SecureString parameters using AWS Key Management Service. This encryption protects your token from unauthorized access. Even if someone gained access to your AWS account without proper IAM permissions, they would not be able to read the decrypted token value.

Your Lambda function decrypts the token when it runs, loads it into memory, uses it to authenticate with Home Assistant, and then the memory is cleared when the function finishes. The token is never written to logs or stored in any permanent location outside Parameter Store.

To further secure your token, use IAM policies to restrict which users and roles can read Parameter Store parameters. Only your Lambda execution role should need permission to read the token. Regular users should not have Parameter Store read access unless they specifically need it for other purposes.

### Can someone else invoke my Lambda function?

Your Lambda function is protected by AWS IAM permissions. Only your Alexa skill can invoke the function because you configured an Alexa Skills Kit trigger with a specific Skill ID. Lambda validates that incoming requests come from Alexa and specifically from your Skill ID before allowing execution.

Other AWS users cannot invoke your function unless you explicitly grant them permission. Your Lambda function is private to your AWS account by default. No one outside your account can even see that the function exists without proper IAM credentials.

Within your AWS account, users with Lambda invocation permissions could potentially invoke your function. Use IAM policies to restrict which users have Lambda invocation permissions if you share your AWS account with others.

### Should I use VPN for maximum security?

VPN provides the highest level of security by creating an encrypted tunnel between AWS and your home network that does not expose any ports to the public internet. However, VPN requires complex AWS networking configuration, costs money for the VPN gateway, and provides minimal security benefit over properly configured SSL connections for most users.

Cloudflare Tunnel with SSL verification enabled provides excellent security for most users without the complexity and cost of VPN. The connection is encrypted end-to-end, Cloudflare provides DDoS protection, and no ports are exposed on your home network.

Consider VPN only if you have specific security requirements that demand it, such as compliance with particular security standards, extreme privacy requirements, or integration with existing VPN infrastructure. For typical smart home use, Cloudflare Tunnel or direct connection with valid SSL certificates provides adequate security.

### How often should I rotate access tokens?

Home Assistant long-lived access tokens do not expire automatically unless you explicitly set an expiration date or revoke them. However, security best practices recommend rotating credentials periodically even if they have not been compromised.

Consider rotating your access token every six to twelve months as a preventive measure. To rotate the token, generate a new long-lived access token in Home Assistant, update your Parameter Store value with the new token, test that everything still works, and then revoke the old token in Home Assistant.

If you suspect your token may have been compromised, rotate it immediately. Signs of compromise include unexpected device state changes, unusual entries in Home Assistant logs, or API requests from IP addresses you do not recognize.

---

## Advanced Troubleshooting

### Reading CloudWatch Logs

CloudWatch Logs contain detailed information about every Lambda function execution. To access logs, navigate to CloudWatch in the AWS Console, click Logs, then Log Groups, then find your Lambda function's log group.

Each log group contains multiple log streams. Each stream represents a single container that ran your function. Click on the most recent stream to see logs from recent executions.

Logs include several types of entries. START entries mark the beginning of a function invocation and include the request ID. Log entries from your code show information the function logged during execution. END entries mark successful completion. REPORT entries provide statistics about memory usage, duration, and billed duration.

Look for ERROR or WARNING entries which indicate problems. Error entries usually include stack traces showing exactly where the code failed and what error occurred. Use these stack traces to diagnose problems.

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
