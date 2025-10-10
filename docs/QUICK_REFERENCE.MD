# Lambda Execution Engine - Quick Reference

**Version:** 2025.10.10  
**Purpose:** At-a-glance reference for common tasks and values

---

## Essential Configuration Values

### Required Environment Variables

```
HOME_ASSISTANT_ENABLED=true
USE_PARAMETER_STORE=true
PARAMETER_PREFIX=/lambda-execution-engine
HA_FEATURE_PRESET=standard
HA_TIMEOUT=30
HA_VERIFY_SSL=true
LUGS_ENABLED=true
```

### Required Parameter Store Paths

```
/lambda-execution-engine/homeassistant/url
/lambda-execution-engine/homeassistant/token
```

### Optional Parameter Store Paths

```
/lambda-execution-engine/homeassistant/assistant_name
/lambda-execution-engine/homeassistant/verify_ssl
/lambda-execution-engine/homeassistant/timeout
```

---

## Lambda Function Settings

### Basic Configuration

**Function Name:** lambda-execution-engine  
**Runtime:** Python 3.12  
**Architecture:** x86_64  
**Handler:** lambda_function.lambda_handler  
**Memory:** 128 MB  
**Timeout:** 30 seconds

### IAM Role Requirements

**Role Name:** LambdaExecutionEngineRole  
**Managed Policies:**
- AWSLambdaBasicExecutionRole
- AmazonSSMReadOnlyAccess

---

## Feature Presets

### Minimal Preset

**Memory Usage:** Approximately 15 MB  
**Cold Start:** Under 500 ms  
**Features:** Basic device control only  
**Use When:** Minimizing resource usage is priority

### Standard Preset

**Memory Usage:** Approximately 20 MB  
**Cold Start:** Under 700 ms  
**Features:** Device control, scenes, scripts  
**Use When:** Balanced features and performance needed

### Performance Preset

**Memory Usage:** Approximately 25 MB  
**Cold Start:** Under 900 ms  
**Features:** Standard features plus conversation and input helpers  
**Use When:** Advanced features required

### Maximum Preset

**Memory Usage:** Approximately 30 MB  
**Cold Start:** Under 1200 ms  
**Features:** All available features including area control and announcements  
**Use When:** Need every feature regardless of resource usage

---

## Common URLs and Endpoints

### AWS Console URLs

**Lambda Console:** https://console.aws.amazon.com/lambda  
**IAM Console:** https://console.aws.amazon.com/iam  
**Systems Manager:** https://console.aws.amazon.com/systems-manager  
**CloudWatch:** https://console.aws.amazon.com/cloudwatch

### Amazon Developer Console

**Skills Console:** https://developer.amazon.com/alexa/console/ask  
**Account Management:** https://developer.amazon.com/settings/console/mycredentials

---

## Testing Commands

### Discovery Test Event

Create a test event in Lambda to simulate Alexa device discovery. Name the event discovery-test and use a discovery directive payload following the Alexa Smart Home API format.

### Device Control Test Event

Create a test event that simulates turning a device on or off. Include the device entity ID from your Home Assistant instance.

### Health Check Test

Create a minimal test event that verifies the Lambda function executes successfully without requiring Home Assistant connection.

---

## CloudWatch Log Locations

**Log Group Path:** /aws/lambda/lambda-execution-engine  
**Log Retention:** Set based on your needs, typically 7 to 30 days  
**Search Tips:** Filter logs by ERROR or WARNING to find issues quickly

---

## Parameter Store Value Examples

### Cloudflare Tunnel URL

```
https://homeassistant.yourdomain.com
```

### Direct Connection URL

```
https://your-domain-or-ip:8123
```

### Local HTTP URL for Testing

```
http://192.168.1.100:8123
```

### Access Token Format

Long random string of letters and numbers, typically 100+ characters. Copy the entire value from your Home Assistant profile page without spaces or line breaks.

### Assistant Name Examples

Valid names: Jarvis, Computer, Smart Home, House Assistant  
Invalid names: Alexa, Amazon, Echo, @home, 123

---

## Common Error Messages

### Cannot connect to Home Assistant

**Check:** URL in Parameter Store is correct  
**Check:** Home Assistant is accessible from internet  
**Check:** Firewall allows incoming connections  
**Fix:** Verify URL by testing in browser from outside network

### Unauthorized or authentication error

**Check:** Access token in Parameter Store is correct  
**Check:** Token has not been revoked in Home Assistant  
**Fix:** Generate new token and update Parameter Store

### SSL certificate verification failed

**Check:** HA_VERIFY_SSL setting matches your SSL configuration  
**Fix:** Set HA_VERIFY_SSL to false for self-signed certificates

### Lambda function timeout

**Check:** HA_TIMEOUT is high enough for your network  
**Check:** Lambda timeout setting is adequate  
**Fix:** Increase timeout values to 45 or 60 seconds

### Device not found

**Check:** Device is exposed in Home Assistant Alexa integration  
**Check:** Entity ID is correct  
**Fix:** Re-run device discovery in Alexa app

---

## Performance Optimization

### Reduce Memory Usage

Set HA_FEATURE_PRESET to minimal or standard  
Enable LUGS_ENABLED for lazy loading  
Reduce HA_CACHE_TTL to decrease cache size

### Improve Response Time

Increase HA_CACHE_TTL to reduce API calls  
Lower HA_TIMEOUT if you have fast network  
Enable LUGS_ENABLED to reduce cold start time

### Increase Reliability

Increase HA_MAX_RETRIES to tolerate network issues  
Set HA_CIRCUIT_BREAKER_THRESHOLD higher  
Increase HA_TIMEOUT for slower connections

---

## Alexa Skill Configuration

### Smart Home Skill

**Model Type:** Smart Home  
**Hosting:** Provision Your Own  
**Endpoint:** Your Lambda function ARN  
**Commands:** Direct device control without invocation name  
**Example:** Alexa, turn on the lights

### Custom Skill

**Model Type:** Custom  
**Template:** Start From Scratch  
**Invocation Name:** Your chosen name in lowercase  
**Endpoint:** Your Lambda function ARN  
**Commands:** Require invocation name  
**Example:** Alexa, ask Jarvis to turn on the lights

---

## Security Checklist

**Token Storage:** Use SecureString type in Parameter Store  
**IAM Permissions:** Role has only required permissions  
**SSL Configuration:** Use HA_VERIFY_SSL=true with valid certificates  
**Multi-Factor Authentication:** Enabled on AWS account  
**Log Review:** Verify no sensitive data in CloudWatch Logs  
**Token Rotation:** Rotate access tokens every 6 to 12 months

---

## Deployment Package Requirements

### Core Files

lambda_function.py  
gateway.py  
fast_path.py

### Core Modules

cache_core.py  
logging_core.py  
security_core.py  
metrics_core.py  
config_core.py  
http_client_core.py  
singleton_core.py  
circuit_breaker_core.py  
initialization_core.py  
lambda_core.py  
utility_core.py

### Supporting Files

variables.py  
variables_utils.py

### Extensions

homeassistant_extension.py

### Package Requirements

All files at root level of ZIP archive  
No relative imports, only absolute imports  
gateway.py must include format_response function  
Total files: Minimum 17

---

## Troubleshooting Quick Steps

### Function will not create

Verify IAM permissions allow Lambda function creation  
Check that execution role exists and has correct trust policy  
Confirm you are within service quota limits

### Code upload fails

Verify ZIP file size is under 50 MB  
Check that Python files are at ZIP root level  
Ensure all required files are included

### Tests fail after deployment

Check environment variables are set correctly  
Verify Parameter Store values are accessible  
Review CloudWatch Logs for specific error messages

### Alexa cannot discover devices

Verify Lambda function executed successfully  
Check that devices are exposed in Home Assistant  
Confirm Alexa trigger is configured with correct Skill ID

### Commands fail but discovery works

Test devices directly in Home Assistant  
Verify entity IDs match between Alexa and Home Assistant  
Check Home Assistant logs for incoming API requests

---

## AWS Region Codes

**US East (N. Virginia):** us-east-1  
**US East (Ohio):** us-east-2  
**US West (N. California):** us-west-1  
**US West (Oregon):** us-west-2  
**EU (Ireland):** eu-west-1  
**EU (London):** eu-west-2  
**EU (Frankfurt):** eu-central-1  
**Asia Pacific (Tokyo):** ap-northeast-1  
**Asia Pacific (Singapore):** ap-southeast-1  
**Asia Pacific (Sydney):** ap-southeast-2

---

## File Import Verification

### Correct Absolute Imports

```python
from gateway import execute_operation
from variables import Config
from utility_core import log_info
```

### Incorrect Relative Imports

```python
from .gateway import execute_operation  # Wrong
from .variables import Config  # Wrong
from .utility_core import log_info  # Wrong
```

---

## Environment Variable Types

### Boolean Values

Valid: true, false, 1, 0  
Invalid: yes, no, maybe, True, False

### String Values

Enter as plain text  
No quotes needed in Lambda console  
Case sensitive

### Numeric Values

Enter as string representation  
Example: 30 for timeout in seconds  
Lambda converts to appropriate type

---

## Custom Assistant Name Validation

### Valid Names

Length: 2 to 25 characters  
Characters: Letters, numbers, spaces  
Examples: Jarvis, Computer, Smart Home

### Invalid Names

Reserved words: Alexa, Amazon, Echo  
Special characters: @home, house!  
Numbers only: 123, 456  
Too short: Single letters like A or H

---

## Monitoring Metrics

### Key Metrics to Watch

**Invocation Count:** Number of times function was called  
**Error Count:** Number of failed executions  
**Duration:** How long function takes to execute  
**Memory Usage:** Amount of memory consumed  
**Throttles:** Requests rejected due to concurrency limits

### Acceptable Ranges

**Duration:** 200 to 1500 ms depending on cold start  
**Memory:** 15 to 30 MB depending on preset  
**Error Rate:** Below 5 percent  
**Throttles:** Should be zero for typical usage

---

## Support Resources

### Documentation References

Setup Guide: HOME_ASSISTANT_SETUP_GUIDE.md  
Quick Start: QUICK_START.md  
Configuration: CONFIGURATION_REFERENCE.md  
Custom Names: ASSISTANT_NAME_GUIDE.md  
Troubleshooting: FAQ_AND_TROUBLESHOOTING.md  
Testing: TESTING_AND_VALIDATION_GUIDE.md

### Diagnostic Information to Gather

CloudWatch Logs showing the error  
Environment variable configuration  
Parameter Store parameter names  
Feature preset in use  
Home Assistant version  
Lambda function version

---

## Cost Estimates

### Typical Monthly Usage

Voice commands: 1500 to 2000 per month  
Memory per request: 25 MB  
Duration per request: 300 ms  
Compute usage: 50 to 75 GB-seconds per month

### AWS Free Tier

Lambda requests: 1,000,000 per month  
Compute time: 400,000 GB-seconds per month  
Parameter Store: Standard tier is free  
CloudWatch Logs: First 5 GB per month free

### Expected Costs

Typical smart home usage: Zero dollars per month  
Heavy usage over free tier: A few cents to a few dollars  
Costs only apply if you exceed free tier limits

---

## Update Procedures

### Update Environment Variable

Navigate to Lambda function Configuration tab  
Click Environment Variables, then Edit  
Modify the value  
Click Save  
Changes take effect immediately on next invocation

### Update Parameter Store Value

Navigate to Systems Manager Parameter Store  
Find the parameter to update  
Click the parameter name  
Click Edit  
Update the value  
Click Save Changes  
Wait for cache expiration or restart function

### Update Lambda Code

Create new deployment package with updated files  
Navigate to Lambda function Code tab  
Click Upload From, select ZIP File  
Choose your new package  
Click Save  
Test immediately after upload

---

## Connection Method Selection

### Use Cloudflare Tunnel When

You have a domain name  
You want the easiest setup  
You want automatic SSL certificates  
You do not want to configure port forwarding

### Use Direct Connection When

You have a static IP or dynamic DNS  
You can obtain valid SSL certificates  
You can configure router port forwarding  
You want to avoid third-party services

### Use VPN When

You need maximum security  
You have specific compliance requirements  
You already have VPN infrastructure  
Cost is not a primary concern

---

## Quick Decision Guide

### Choose Minimal Preset If

You only need basic on/off device control  
Memory usage is critical  
You want fastest cold start times  
You do not use scenes or scripts

### Choose Standard Preset If

You use scenes for groups of devices  
You run scripts through voice commands  
You want balanced features and performance  
You follow recommended best practices

### Choose Performance Preset If

You use Home Assistant conversation  
You control input helpers through voice  
You need advanced error messages  
Memory usage is not a concern

### Choose Maximum Preset If

You use area-based device control  
You send announcements through Home Assistant  
You need comprehensive diagnostics  
You want every available feature
