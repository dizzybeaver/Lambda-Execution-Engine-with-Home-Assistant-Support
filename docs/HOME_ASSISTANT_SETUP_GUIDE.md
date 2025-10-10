# Home Assistant Lambda Execution Engine - Complete Setup Guide

**Version:** 2025.10.10  
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

This guide will walk you through setting up the Lambda Execution Engine, which allows Amazon Alexa to control your Home Assistant installation. When you speak a command to Alexa, the request travels to your Lambda function in AWS, which then communicates with your Home Assistant instance to execute the command.

The Lambda Execution Engine uses a gateway architecture where all operations flow through a single entry point. This design keeps memory usage low, typically between 15 and 25 megabytes per request, with response times under 150 milliseconds.

---

## Before You Begin

You will need three accounts. The AWS account and Amazon Developer account are free to create. You should already have your Home Assistant instance running.

### AWS Account

You need an Amazon Web Services account. Create one at https://aws.amazon.com. AWS will ask for a credit card during registration for identity verification purposes. The free tier includes one million Lambda function invocations per month, which covers typical smart home usage without charges.

### Amazon Developer Account

You need an Amazon Developer account to create Alexa skills. Create one at https://developer.amazon.com. You can use your existing Amazon account credentials and add developer permissions.

### Home Assistant Requirements

Your Home Assistant instance must be accessible from the internet. This typically means using Cloudflare Tunnel, a VPN connection, or port forwarding with SSL certificates. You will need a long-lived access token from your Home Assistant profile page.

### Equipment Needed

You need a computer running Windows, Mac, or Linux with internet access. You will need an Alexa device to test voice commands after setup is complete.

---

## Phase 1: AWS Account Setup

This section covers creating your AWS account and selecting your region.

### Step 1: Create Your AWS Account

Navigate to https://aws.amazon.com and click the Create an AWS Account button. Enter your email address and choose an account name. Select Personal as the account type. Provide your contact information including phone number.

AWS requires a credit card for identity verification. Enter your payment information. AWS will place a small authorization hold that will be reversed, typically one dollar.

Select the Basic Support plan, which is free and provides access to documentation, forums, and service health dashboards.

### Step 2: Identity Verification

AWS will verify your identity through a phone call or text message. Choose your preferred verification method. If you select text message, AWS will send you a four-digit code. If you select voice call, an automated system will call you and read the code twice. Enter the verification code when prompted.

After verification completes, AWS needs a few minutes to activate your account. You will receive a welcome email when your account is ready. This usually takes five to ten minutes but can take up to one hour during high-traffic periods.

### Step 3: Enable Multi-Factor Authentication

After your account activates, log in to the AWS Console. Click on your account name in the top right corner and select Security Credentials. Under Multi-Factor Authentication, click Activate MFA. Choose Virtual MFA device and follow the prompts to set up an authenticator app on your phone.

Multi-factor authentication adds an extra security layer. Even if someone obtains your password, they cannot access your account without the second factor.

### Step 4: Select Your Region

AWS operates in multiple geographic regions. You should select the region closest to your physical location to minimize latency. Common regions include us-east-1 for US East Coast, us-west-2 for US West Coast, and eu-west-1 for Europe.

All services you create in this guide must be in the same region. Note your selected region and use it consistently throughout the setup process.

---

## Phase 2: IAM Role Creation

IAM stands for Identity and Access Management. You need to create a role that defines what permissions your Lambda function has. This role allows the Lambda function to write logs to CloudWatch and read configuration from Parameter Store, but prevents it from accessing other AWS services.

### Step 1: Access IAM Console

From the AWS Console, use the search bar at the top of the page. Type IAM and press Enter. Click on IAM in the search results to open the Identity and Access Management console.

### Step 2: Navigate to Roles

In the left sidebar, click on Roles. You will see a list of existing roles if any exist in your account. Click the Create Role button to begin creating a new role.

### Step 3: Select Trusted Entity

On the Select Trusted Entity page, choose AWS Service as the trusted entity type. From the list of use cases, select Lambda. This configuration allows Lambda functions to assume this role. Click Next to continue.

### Step 4: Attach Permissions Policies

You need to attach two managed policies to this role. In the search box, type AWSLambdaBasicExecutionRole. This is a managed policy provided by AWS that grants permission to create log groups, create log streams, and write log events to CloudWatch Logs. Check the box next to this policy.

Next, search for AmazonSSMReadOnlyAccess. This policy grants read-only access to Systems Manager Parameter Store where you will store your Home Assistant credentials. Check the box next to this policy.

After selecting both policies, click Next to continue.

### Step 5: Name and Create Role

Enter LambdaExecutionEngineRole as the role name. Add an optional description such as Execution role for Lambda Execution Engine with Home Assistant integration. Review the permissions to confirm both policies are attached. Click Create Role to complete the process.

The role now appears in your roles list. Click on the role name to view its details and confirm that both AWSLambdaBasicExecutionRole and AmazonSSMReadOnlyAccess are listed under permissions policies.

---

## Phase 3: Parameter Store Configuration

Parameter Store is part of AWS Systems Manager. It provides secure storage for configuration data and secrets. You will store your Home Assistant URL and access token here as encrypted parameters that only your Lambda function can read.

### Step 1: Access Systems Manager

From the AWS Console search bar, type Systems Manager and select it from the results. In the left sidebar, find and click on Parameter Store under the Application Management section.

### Step 2: Create Home Assistant URL Parameter

Click the Create Parameter button. Enter the following details for your first parameter.

For the parameter name, enter /lambda-execution-engine/homeassistant/url. This path follows a hierarchical structure that groups related parameters together.

Set the tier to Standard. The Standard tier is free and supports parameters up to 4 kilobytes, which is sufficient for a URL.

Set the type to String. The URL does not need encryption since it is not secret information.

In the value field, enter your complete Home Assistant URL. Include the protocol and port number. For example, if you use Cloudflare Tunnel, enter something like https://homeassistant.yourdomain.com. If you use port forwarding, enter https://your-ip-or-domain:8123. Make sure the URL is exactly how you access your Home Assistant instance from outside your network.

Add a description such as Home Assistant base URL for API access. Click Create Parameter to save.

### Step 3: Create Home Assistant Token Parameter

Click Create Parameter again for your access token. Enter /lambda-execution-engine/homeassistant/token as the parameter name.

Set the tier to Standard. Set the type to SecureString. The SecureString type encrypts the value using AWS Key Management Service. This encryption protects your access token even if someone gains access to Parameter Store.

In the value field, paste your Home Assistant long-lived access token. You can generate this token from your Home Assistant profile page. Make sure you copy the entire token without any extra spaces or line breaks.

Add a description such as Home Assistant long-lived access token for API authentication. Click Create Parameter to save.

### Step 4: Create Optional Configuration Parameters

You can create additional parameters for advanced configuration. These are optional but useful for customization.

Create a parameter named /lambda-execution-engine/homeassistant/assistant_name with type String. Set the value to your preferred assistant name such as Jarvis or Computer. This controls how you invoke your assistant through Alexa. If you skip this parameter, the system defaults to Home Assistant.

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

The core module files include cache_core.py for caching functionality, logging_core.py for logging, security_core.py for security features, metrics_core.py for performance metrics, singleton_core.py for singleton pattern implementation, http_client_core.py for HTTP communications, utility_core.py for utility functions, initialization_core.py for system initialization, lambda_core.py for Lambda-specific functionality, circuit_breaker_core.py for circuit breaker pattern, and config_core.py for configuration management.

The supporting files include variables.py which defines configuration data structures and variables_utils.py which provides configuration utilities.

For Home Assistant integration, include homeassistant_extension.py.

### Step 2: Verify File Requirements

Before creating your deployment package, verify that all files use absolute imports instead of relative imports. Open gateway.py and confirm it includes a function named format_response. Open variables_utils.py and verify all import statements use absolute imports without dot notation.

If any files use relative imports like from .module_name import, change them to from module_name import using the absolute module name.

### Step 3: Create Deployment Package

On your computer, create a new folder and place all the Python files directly into this folder. The files must be at the root level of the folder, not in a subfolder.

To create the ZIP archive on Windows, select all the Python files in the folder. Right-click on the selected files and choose Send To, then Compressed Zipped Folder. Name the file lambda-execution-engine.zip. Make sure you select the files themselves, not the folder containing them.

To create the ZIP archive on Mac, select all the Python files. Right-click and choose Compress Items. Rename the resulting archive to lambda-execution-engine.zip.

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

Environment variables control your Lambda function behavior without modifying code. You will set variables that enable Home Assistant integration and configure performance settings.

### Step 1: Access Environment Variables

From your Lambda function page, click the Configuration tab. In the left menu, select Environment Variables. Click the Edit button to add or modify variables.

### Step 2: Add Required Variables

Click Add Environment Variable to add each variable. For the key field, enter the variable name exactly as shown. For the value field, enter the corresponding value.

Set HOME_ASSISTANT_ENABLED to true. This enables the Home Assistant integration in your Lambda function.

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

Home Assistant provides three methods to control which entities Alexa can access. The cloud method uses the cloud integration if you have configured it. The customize method adds expose: true to each entity in your configuration.yaml file. The manual selection method uses the Alexa integration settings in Home Assistant.

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

Click JSON Editor in the left menu. You need to paste a JSON interaction model that defines the intents your skill handles. The model should include intents for conversation, device control, and help requests.

After pasting the interaction model, click Save Model at the top, then click Build Model. Wait for the build to complete.

In the Endpoint section, select AWS Lambda ARN. Paste your Lambda function ARN in the Default Region field.

Copy your Skill ID from the top of the page. Return to your Lambda function and add an Alexa Skills Kit trigger. Paste the Skill ID when prompted.

In the Alexa app, enable your custom skill under Skills and Games. You can now test commands using your custom name.

---

## Phase 9: Testing

After completing the setup, you should test that all components work together correctly.

### Voice Command Testing

Start with simple commands to verify basic functionality. Try saying Alexa, turn on the living room lights if using a Smart Home skill, or Alexa, ask Jarvis to turn on the living room lights if using a custom skill.

If Alexa responds that she cannot find the device, verify that the device is exposed in your Home Assistant Alexa integration settings. If Alexa responds but the device does not change state, check your Home Assistant logs for incoming API requests.

Test multiple device types to ensure the integration works broadly. Try lights, switches, locks, and climate controls if you have them configured.

### CloudWatch Logs Review

Open the AWS Console and navigate to CloudWatch. Click Logs in the left menu, then click Log Groups. Find the log group named /aws/lambda/lambda-execution-engine.

Click on the log group to see log streams. Each stream represents an execution of your function. Click on the most recent stream to view the logs.

Look for log entries that show successful connection to Home Assistant, device discovery, and command execution. Error messages in the logs will indicate problems that need attention.

### Lambda Metrics Review

From your Lambda function page, click the Monitor tab. View the invocation count to see how many times your function has been called. Check the error count and success rate. Review the duration metric to confirm execution times remain under your timeout setting.

---

## Troubleshooting

This section covers common issues and their solutions.

### Alexa Cannot Find Devices

If Alexa says she cannot find any devices after discovery, first verify that your Lambda function executed successfully by checking CloudWatch logs. Confirm that devices are exposed to Alexa in your Home Assistant configuration. Verify that your Home Assistant URL and token in Parameter Store are correct. Test that your Home Assistant instance is accessible from outside your network.

### Device Commands Do Not Work

If Alexa acknowledges commands but devices do not respond, check that the device works when controlled directly through Home Assistant. Review CloudWatch logs to confirm the Lambda function received and processed the command. Verify that your Home Assistant access token has the necessary permissions to control devices. Check for entity ID mismatches between Alexa and Home Assistant.

### Lambda Function Timeout

If your function times out before completing, increase the timeout setting in Lambda General Configuration to 45 or 60 seconds. Check your Home Assistant response time by testing API calls directly. Verify your network connection between Lambda and Home Assistant is not experiencing high latency. Consider switching to a lower HA_FEATURE_PRESET to reduce processing time.

### High Memory Usage

If your function approaches the 128 MB memory limit, verify that LUGS_ENABLED is set to true in environment variables. Switch to a lower HA_FEATURE_PRESET value such as minimal. Reduce HA_CACHE_TTL to decrease cache memory usage. Review CloudWatch metrics to identify which invocations use the most memory.

### Invalid Token Errors

If you see unauthorized or invalid token errors, regenerate your Home Assistant long-lived access token from your profile page. Update the token value in Parameter Store. Verify the token has not expired. Confirm you copied the entire token without extra spaces or line breaks.

### SSL Certificate Errors

If you see SSL verification errors, verify that your Home Assistant instance uses valid SSL certificates. For self-signed certificates, set HA_VERIFY_SSL to false in environment variables. Consider obtaining proper SSL certificates through Let's Encrypt for production use.

---

## Next Steps

After completing this setup, you have a working integration between Alexa and Home Assistant. You can now explore additional features and customization options.

Review the Configuration Reference guide for detailed information about all available environment variables and Parameter Store settings. Read the Assistant Name Guide if you want to implement custom invocation names. Consult the FAQ and Troubleshooting guide for solutions to common issues and advanced configuration techniques.
