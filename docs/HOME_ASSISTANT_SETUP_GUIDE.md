# Home Assistant Lambda Execution Engine - Complete Setup Guide

**Version:** 2025.10.10.02  
**Estimated Time:** 45-75 minutes  
**Target Audience:** First-time AWS users setting up Home Assistant integration

---

## Table of Contents

1. [What This Guide Covers](#what-this-guide-covers)
2. [Before You Begin](#before-you-begin)
3. [Phase 1: AWS Account Setup](#phase-1-aws-account-setup)
4. [Phase 2: IAM Role Creation](#phase-2-iam-role-creation)
5. [Phase 3: Parameter Store Configuration](#phase-3-parameter-store-configuration)
6. [Phase 4: Lambda Function Creation](#phase-4-lambda-function-creation)
7. [Phase 5: Code Deployment](#phase-5-code-deployment)
8. [Phase 6: Environment Variables](#phase-6-environment-variables)
9. [Phase 7: Home Assistant Connection](#phase-7-home-assistant-connection)
10. [Phase 8: Alexa Skill Setup](#phase-8-alexa-skill-setup)
11. [Phase 9: Testing](#phase-9-testing)
12. [Troubleshooting](#troubleshooting)

---

## What This Guide Covers

This guide will walk you through setting up the Lambda Execution Engine with the Home Assistant Extension. The Lambda Execution Engine is a general-purpose Lambda optimization framework. The Home Assistant Extension is one extension built on top of this framework, providing integration between Amazon Alexa and your Home Assistant installation. When you speak a command to Alexa, the request travels to your Lambda function in AWS, which then communicates with your Home Assistant instance to execute the command.

The Lambda Execution Engine provides core services including the gateway architecture, lazy loading, caching, circuit breaker protection, logging, and metrics collection. The Home Assistant Extension uses these services to implement Home Assistant-specific functionality. You could build other extensions using the same Engine services for different smart home platforms or entirely different purposes.

The Lambda Execution Engine uses a gateway architecture where all operations flow through a single entry point. This design keeps memory usage low, typically between 15 and 25 megabytes per request, with response times under 150 milliseconds.

---

## Before You Begin

You will need three accounts. The AWS account and Amazon Developer account are free to create. You should already have your Home Assistant instance running.

### AWS Account

You need an Amazon Web Services account. Create one at https://aws.amazon.com. AWS will ask for a credit card during registration for identity verification purposes. The free tier includes one million Lambda function invocations per month, which covers typical smart home usage without charges.

### Amazon Developer Account

You need an Amazon Developer account to create Alexa skills. Create one at https://developer.amazon.com. You can use your existing Amazon account credentials and add developer permissions.

### Home Assistant Extension Requirements

These requirements apply only if you are using the Home Assistant Extension. The Lambda Execution Engine itself does not require Home Assistant.

Your Home Assistant instance must be accessible from the internet. This typically means using Cloudflare Tunnel, a VPN connection, or port forwarding with SSL certificates. You will need a long-lived access token from your Home Assistant profile page.

### Equipment Needed

You need a computer running Windows, Mac, or Linux with internet access. You will need an Alexa device to test voice commands after setup is complete.

---

## Phase 1: AWS Account Setup

This section covers creating your AWS account and selecting your region.

### Step 1: Create Your AWS Account

Navigate to https://aws.amazon.com and click the Create an AWS Account button. Enter your email address and choose an account name. AWS sends a verification code to your email address. Enter the code to verify your email.

Choose a password for your AWS account. AWS requires strong passwords with uppercase letters, lowercase letters, numbers, and special characters. Enter your password and confirm it by entering it again.

### Step 2: Provide Contact Information

AWS asks for your contact information including name, phone number, and address. This information is required for account verification and billing purposes. Enter accurate information as AWS may use it to verify your identity.

Choose Personal or Business account type. Personal accounts work fine for home automation purposes. Business accounts provide features needed for commercial use but are not necessary for smart home control.

### Step 3: Payment Information

AWS asks for payment information during registration. Enter your credit or debit card details. AWS uses this information for identity verification and will charge your card only if you exceed free tier limits. Most home automation usage stays well within free tier limits.

AWS may place a temporary hold on your card for verification purposes. This hold typically releases within a few days.

### Step 4: Identity Verification

AWS requires phone verification to confirm your identity. Choose whether you want to receive verification by voice call or SMS text message. AWS sends a verification code to your phone. Enter the code on the verification page.

### Step 5: Support Plan Selection

AWS asks you to select a support plan. Choose the Basic Support plan which is free. This plan provides access to documentation, whitepapers, support forums, and AWS Trusted Advisor. You do not need paid support plans for home automation purposes.

### Step 6: Region Selection

After account creation completes, sign in to the AWS Console. In the top right corner, you will see your selected region. Click on the region to open a dropdown menu showing all available regions.

Choose a region geographically close to your location for best performance. For users in the eastern United States, us-east-1 (Virginia) works well. For western United States users, us-west-2 (Oregon) provides good performance. European users should choose eu-west-1 (Ireland) or eu-central-1 (Frankfurt).

Remember which region you selected. You must create all related AWS resources in the same region for them to work together. If you create your Lambda function in us-east-1, your Parameter Store parameters must also be in us-east-1.

---

## Phase 2: IAM Role Creation

IAM (Identity and Access Management) controls permissions for AWS services. Your Lambda function needs an IAM role that grants permission to write logs and read Parameter Store values.

### Step 1: Access IAM Console

From the AWS Console search bar at the top of the page, type IAM and select IAM from the search results. This opens the IAM console where you manage users, roles, and permissions.

### Step 2: Create Role

Click on Roles in the left sidebar navigation. This displays all roles in your account. Click the Create Role button to begin creating a new role.

Under Select Type of Trusted Entity, choose AWS Service. This indicates that an AWS service rather than a user will use this role. Under Choose a Use Case, select Lambda from the list. This tells AWS that your Lambda function will use this role. Click Next: Permissions to continue.

### Step 3: Attach Policies

The permissions page lets you select which policies to attach to your role. Policies define what actions the role can perform. You need to attach two policies for the Lambda Execution Engine to function correctly.

In the search box, type AWSLambdaBasicExecutionRole. Select the checkbox next to this policy. This policy grants permission to write logs to CloudWatch Logs, which allows you to see what your Lambda function is doing and diagnose any problems.

Clear the search box and type AmazonSSMReadOnlyAccess. Select the checkbox next to this policy. This policy grants permission to read values from Parameter Store, which is where you will store your Home Assistant URL and access token.

After selecting both policies, click Next: Tags to continue.

### Step 4: Add Tags

Tags help you organize and track AWS resources. Tags are optional but can be useful if you manage multiple AWS resources. You can add a tag with Key set to Purpose and Value set to Home Assistant Integration.

Click Next: Review to continue to the review page.

### Step 5: Name and Create Role

On the review page, enter LambdaExecutionEngineRole as the role name. Role names must be unique within your AWS account. This name clearly indicates the role's purpose.

Enter a description such as Execution role for Lambda Execution Engine with Home Assistant Extension. Descriptions help you remember what each role does if you create multiple roles.

Verify that both AWSLambdaBasicExecutionRole and AmazonSSMReadOnlyAccess appear in the policies list. If either is missing, click Previous to go back and add it.

Click Create Role to create the role. AWS creates the role and returns you to the roles list where you can see your new role.

---

## Phase 3: Parameter Store Configuration

AWS Systems Manager Parameter Store provides secure storage for configuration values. You will store your Home Assistant URL and access token here so they do not appear directly in your Lambda function code or environment variables.

### Step 1: Access Parameter Store

From the AWS Console search bar, type Systems Manager and select AWS Systems Manager from the results. In the left sidebar, scroll down to the Application Management section and click Parameter Store.

### Step 2: Create URL Parameter

Click Create Parameter to begin creating your first parameter. Set the name to /lambda-execution-engine/homeassistant/url. The forward slashes create a hierarchy that organizes your parameters. The Lambda function reads parameters starting with /lambda-execution-engine/ by default.

Under Description, enter Home Assistant base URL for API access. Descriptions help you remember what each parameter contains.

Set Tier to Standard. Standard tier is free and provides adequate storage for URLs. Advanced tier costs money and is unnecessary for these parameters.

Set Type to String. The URL does not need encryption since it is not sensitive information.

In the Value field, enter your complete Home Assistant URL including the protocol and port. For Cloudflare Tunnel access, use https://homeassistant.yourdomain.com. For direct access with SSL, use https://your-domain-or-ip:8123. For local access without SSL, use http://your-ip:8123 but this is not recommended for security reasons.

Do not include a trailing slash at the end of the URL. The URL should end with the domain or port number.

Click Create Parameter to save this parameter.

### Step 3: Create Token Parameter

Click Create Parameter again to create the access token parameter. Set the name to /lambda-execution-engine/homeassistant/token.

Set Type to SecureString. This encrypts your access token so it cannot be viewed in plain text through the AWS Console. AWS automatically encrypts the value using your account's default encryption key.

In the Value field, enter your Home Assistant long-lived access token. To create a long-lived access token, open your Home Assistant web interface, click on your user profile in the bottom left corner, scroll down to the Long-Lived Access Tokens section, and click Create Token. Give the token a name like Lambda Function Access and copy the generated token.

Paste the token into the Parameter Store value field. Click Create Parameter to save this parameter.

### Step 4: Create Optional Parameters

You can create additional optional parameters that override default behavior. These parameters are not required but provide additional control if needed.

Create a parameter named /lambda-execution-engine/homeassistant/assistant_name with type String if you want to use a custom invocation name for Alexa. Set the value to your desired name such as Jarvis or Computer. If you skip this parameter, the system defaults to Home Assistant.

Create a parameter named /lambda-execution-engine/homeassistant/verify_ssl with type String. Set the value to true if you use valid SSL certificates or false if you use self-signed certificates. If you skip this parameter, the system defaults to true.

Create a parameter named /lambda-execution-engine/homeassistant/timeout with type String. Set the value to the number of seconds to wait for Home Assistant responses, typically 30 or 45. Higher values work better for slower network connections.

---

## Phase 4: Lambda Function Creation

Lambda is a serverless compute service that runs your code in response to events. You will create a Lambda function that acts as the bridge between Alexa and Home Assistant.

### Step 1: Access Lambda Console

From the AWS Console search bar, type Lambda and select it. Click the Create Function button to begin.

### Step 2: Configure Basic Settings

Leave the default option Author from Scratch selected. Enter lambda-execution-engine as the function name. Function names must be unique within your AWS account and region.

Under Runtime, select Python 3.12 or the most recent Python 3.x version available in the dropdown. The Lambda Execution Engine is written in Python and requires version 3.12 or newer.

Under Architecture, leave x86_64 selected. This is the standard architecture for Lambda functions.

### Step 3: Configure Permissions

Expand the section labeled Change Default Execution Role. Select Use an Existing Role from the options. In the dropdown menu that appears, find and select LambdaExecutionEngineRole, which is the role you created in Phase 2.

Leave all other settings at their default values. Click Create Function at the bottom of the page.

### Step 4: Configure Function Settings

AWS creates your function and displays the function configuration page. Click on the Configuration tab, then select General Configuration from the left menu. Click the Edit button.

Set Memory to 128 MB. The Lambda Execution Engine uses minimal memory due to its optimized architecture. Set Timeout to 30 seconds. This gives enough time for the function to communicate with Home Assistant and return a response. Leave Ephemeral Storage at the default 512 MB.

Click Save to apply these settings.

---

## Phase 5: Code Deployment

You need to upload the Lambda Execution Engine code to your function. The code consists of multiple Python files that must be packaged correctly into a ZIP archive.

### Step 1: Gather Required Files

You need these Python files for a complete deployment. The core files include lambda_function.py which serves as the main entry point, gateway.py which implements the universal gateway pattern, and fast_path.py for performance optimization.

The core modules include cache_core.py for caching functionality, logging_core.py for logging, security_core.py for security features, metrics_core.py for performance tracking, config_core.py for configuration management, http_client_core.py for HTTP communication, singleton_core.py for singleton pattern implementation, circuit_breaker_core.py for resilience, initialization_core.py for startup management, lambda_core.py for Lambda-specific functionality, and utility_core.py for utility functions.

Supporting files include variables.py which contains configuration presets and variables_utils.py for configuration utilities. The Home Assistant extension file is homeassistant_extension.py.

### Step 2: Verify File Structure

Ensure all Python files are in a single folder with no subdirectories. The Lambda function expects to find all modules at the root level. Check that no files use relative imports like from .gateway import function. All imports should be absolute, like from gateway import function.

Verify that gateway.py includes the format_response function which Lambda uses to format responses for Alexa. This function must be present at the gateway module level.

### Step 3: Create ZIP Archive

You need to create a ZIP archive containing all Python files at the root level. The method for creating the archive depends on your operating system.

On Windows, select all Python files in File Explorer. Right-click on the selected files and choose Send To then Compressed Zip Folder. Name the archive lambda-execution-engine.zip. Verify that the files are at the root of the ZIP archive by opening it. You should see the Python files immediately, not a folder containing the files.

On Mac, select all Python files in Finder. Right-click on the selected files and choose Compress Items. macOS creates Archive.zip. Rename it to lambda-execution-engine.zip. Open the archive to verify the files are at the root level.

To create the ZIP archive on Linux, open a terminal in the folder containing your Python files. Run the command zip -r lambda-execution-engine.zip *.py to create the archive.

The critical requirement is that the Python files must be at the root level of the ZIP file. If you unzip the file, you should see the Python files immediately, not a folder that then contains the files.

### Step 4: Upload to Lambda

Return to your Lambda function page in the AWS Console. Click on the Code tab. Click the Upload From button and select ZIP File from the dropdown menu.

Click the Upload button and select your lambda-execution-engine.zip file. Click Save to begin the upload. AWS displays a progress indicator while uploading. Wait for the upload to complete before proceeding.

### Step 5: Configure Handler

After the upload completes, click on the Configuration tab. In the left menu, click Runtime Settings. Click the Edit button.

In the Handler field, enter lambda_function.lambda_handler. This tells Lambda which function to call when your function executes. The format is filename.function_name. Click Save to apply the change.

---

## Phase 6: Environment Variables

Environment variables control your Lambda function behavior without modifying code. You will set variables that enable the Home Assistant Extension and configure performance settings.

### Step 1: Access Environment Variables

From your Lambda function page, click the Configuration tab. In the left menu, select Environment Variables. Click the Edit button to add or modify variables.

### Step 2: Add Required Variables

Click Add Environment Variable to add each variable. For the key field, enter the variable name exactly as shown. For the value field, enter the corresponding value.

Set HOME_ASSISTANT_ENABLED to true. This enables loading the Home Assistant Extension. When set to false, the Lambda Execution Engine runs without loading the Home Assistant Extension, and the Engine's core services remain available for other extensions or purposes.

Set USE_PARAMETER_STORE to true. This instructs the Lambda function to read configuration from Parameter Store.

Set PARAMETER_PREFIX to /lambda-execution-engine. This tells the function where to find your parameters in Parameter Store.

Set HA_FEATURE_PRESET to standard. This determines which Home Assistant features are loaded. The standard preset includes core device control, scenes, and scripts without advanced features that use more memory.

Set HA_TIMEOUT to 30. This sets the timeout in seconds for Home Assistant API calls.

Set HA_VERIFY_SSL to true. Set this to false only if you use self-signed certificates and cannot verify SSL.

Set LUGS_ENABLED to true. LUGS stands for Lazy loading Universal Gateway System and improves memory efficiency.

### Step 3: Add Optional Variables

For custom assistant names, set HA_ASSISTANT_NAME to your preferred name such as Jarvis or Computer. This overrides the Parameter Store value if both are set.

For debugging purposes, you can set DEBUG_MODE to true, but this should remain false in production since it increases log verbosity and memory usage.

For performance tuning, you can set HA_CACHE_TTL to the number of seconds to cache Home Assistant state information, typically 300 for five minutes.

### Step 4: Save Configuration

After adding all environment variables, click Save at the bottom of the page. Lambda applies the new configuration immediately. Your function will use these variables on the next invocation.

---

## Phase 7: Home Assistant Connection

You need to verify that your Lambda function can communicate with your Home Assistant instance and configure which entities Alexa can control.

### Step 1: Verify Network Accessibility

Your Home Assistant instance must be accessible from the internet for Lambda to connect. Test this by opening a web browser on a device not connected to your home network, such as your phone using cellular data. Navigate to the URL you entered in Parameter Store. You should see your Home Assistant login page. If you cannot access it, you need to configure port forwarding, VPN access, or Cloudflare Tunnel before proceeding.

### Step 2: Configure Entity Exposure

Home Assistant provides several methods to control which entities Alexa can access. The manual selection method uses the Alexa integration settings in Home Assistant. The customize method adds expose: true to each entity in your configuration.yaml file.

For manual selection, open your Home Assistant interface. Navigate to Configuration, then Integrations. If you do not see an Alexa integration, click Add Integration and search for Alexa Smart Home. Follow the prompts to add it.

Once the integration exists, click on it to open settings. You will see a list of entities. Enable the entities you want Alexa to control by toggling them on. Click Save when finished.

### Step 3: Test Lambda Connection

You can test whether Lambda can reach your Home Assistant instance by creating a test event. From your Lambda function page, click the Test tab. Click Create New Test Event.

Give the event a name such as discovery-test. In the event JSON editor, paste a discovery request that simulates Alexa asking for available devices. The exact JSON format matches the Alexa Smart Home API discovery directive structure.

Click Save, then click Test. Watch the execution results. If the test succeeds, the response will contain a list of discovered devices from your Home Assistant instance. If the test fails, check the error message to diagnose the connection problem. Common issues include incorrect URLs in Parameter Store, invalid access tokens, or network accessibility problems.

---

## Phase 8: Alexa Skill Setup

You need to create an Alexa skill and connect it to your Lambda function. There are two types of skills you can create depending on whether you want to use a custom assistant name.

### Option A: Smart Home Skill for Direct Device Control

Smart Home Skills provide direct device control without requiring an invocation name. You say Alexa, turn on the lights instead of Alexa, ask Home Assistant to turn on the lights. This option does not support custom assistant names.

Navigate to the Amazon Developer Console at https://developer.amazon.com/alexa/console/ask. Click Create Skill. Enter a skill name such as Home Assistant Control. Select Smart Home as the model type. Select Provision Your Own as the hosting method. Click Create Skill.

On the skill configuration page, find the Default Endpoint field. Enter your Lambda function ARN here. You can find your Lambda ARN on your function page in the AWS Console, displayed near the function name at the top of the page. It looks like arn:aws:lambda:region:account-id:function:function-name.

Save the endpoint configuration. Copy your Skill ID from the skill details page.

Return to your Lambda function in the AWS Console. Click Add Trigger. Select Alexa Smart Home from the trigger list. Paste your Skill ID in the Application ID field. Click Add to create the trigger.

In the Alexa app on your phone, navigate to Devices. Tap Discover Devices and wait 30 to 45 seconds. Your Home Assistant entities should appear in the Alexa app. If they do not appear, check CloudWatch logs for errors.

### Option B: Custom Skill for Custom Assistant Names

Custom Skills allow you to use custom invocation names but require you to say Alexa, ask Name to command instead of direct commands. Follow this path if you want to use a name like Jarvis or Computer.

Navigate to the Amazon Developer Console and click Create Skill. Enter a skill name that includes your chosen assistant name, such as Jarvis Home Assistant. Select Custom as the model type. Select Start From Scratch as the template. Click Create Skill.

In the Build tab, click Invocation in the left menu. Change the Skill Invocation Name to your chosen name in lowercase, such as jarvis. Click Save Model.

Click JSON Editor in the left menu. Replace the existing JSON with an interaction model that defines intents for conversation, help, and stop. After pasting your interaction model, click Save Model, then click Build Model.

Click Endpoint in the left sidebar. Select AWS Lambda ARN as your endpoint type. Enter your Lambda function ARN in the Default Region field. Click Save Endpoints.

Return to your Lambda function in the AWS Console. Click Add Trigger. Select Alexa Skills Kit from the trigger list. Paste your Skill ID in the Skill ID field. Click Add to create the trigger.

In the Build tab of the Alexa Developer Console, click on the dropdown menu next to Skill Testing is Disabled at the top of the page. Select Development to enable testing. Test your skill by saying Alexa, ask [your name] to turn on the lights.

---

## Phase 9: Testing

After completing setup, test your installation to verify everything works correctly.

### Step 1: Test in Alexa App

Open the Alexa app on your phone. Navigate to Devices. If you created a Smart Home Skill, you should see your Home Assistant devices listed. If you created a Custom Skill, enable the skill in the Skills section before testing.

### Step 2: Test Voice Commands

Try simple commands first. For Smart Home Skills, say Alexa, turn on [device name]. For Custom Skills, say Alexa, ask [your assistant name] to turn on [device name]. Verify that your devices respond to commands.

Test different types of devices including lights, switches, and scenes. Verify that Alexa responds with confirmation messages and that your devices actually change state.

### Step 3: Check CloudWatch Logs

Navigate to CloudWatch in the AWS Console. Click Logs, then Log Groups. Find the log group for your Lambda function, which will be named /aws/lambda/lambda-execution-engine.

Click on the log group to see recent log streams. Each Lambda invocation creates a new log stream. Click on the most recent stream to see detailed execution logs. Look for any errors or warnings that might indicate problems.

### Step 4: Monitor Performance

In the Lambda console, click on the Monitor tab for your function. Review the invocation metrics to see how many times your function has run. Check the duration and memory usage to verify they fall within expected ranges. The Engine typically uses 15-25 MB of memory and completes requests in 100-200 milliseconds.

---

## Troubleshooting

### Lambda Function Does Not Invoke

If your Lambda function does not invoke when you speak commands to Alexa, verify that you added the correct trigger to your Lambda function. The Skill ID in the trigger must match your Alexa skill exactly.

Check that your skill is enabled in the Alexa app. Navigate to Skills & Games, then Your Skills, and verify your skill appears and shows as enabled.

### Cannot Connect to Home Assistant

If CloudWatch logs show connection errors, verify that your Home Assistant URL in Parameter Store is correct and accessible from the internet. Test the URL from a device outside your local network.

Check that your access token is valid. Try using the token to make a direct API request to Home Assistant using a tool like curl or Postman. If the token does not work, generate a new long-lived access token and update the Parameter Store parameter.

Verify that HA_VERIFY_SSL is set appropriately. If you use self-signed certificates, set it to false. If you use valid certificates, set it to true.

### Devices Do Not Appear

If device discovery completes but no devices appear in Alexa, verify that you exposed entities in Home Assistant. Check the Alexa integration settings in Home Assistant to confirm that entities are enabled for Alexa access.

Run a discovery test event in Lambda to see which devices the function discovers. Compare this list to the entities you expect. If devices are missing from the Lambda response, they are not properly exposed in Home Assistant.

### Commands Fail

If commands invoke your Lambda function but devices do not respond, check CloudWatch logs for specific error messages. Common issues include incorrect entity IDs, unsupported device types, or Home Assistant errors.

Verify that devices work when controlled directly through the Home Assistant web interface. If devices do not work in Home Assistant, they will not work through Alexa.

### Performance Issues

If your Lambda function is slow or times out, check the execution duration in CloudWatch metrics. If duration exceeds several seconds, you may need to optimize your Home Assistant configuration or network connection.

Verify that HA_CACHE_TTL is set to cache frequently accessed data. Caching reduces the number of API calls to Home Assistant and improves response times.

Check your HA_TIMEOUT setting. If your Home Assistant instance is slow to respond, increase the timeout to 45 or 60 seconds to prevent premature timeout errors.
