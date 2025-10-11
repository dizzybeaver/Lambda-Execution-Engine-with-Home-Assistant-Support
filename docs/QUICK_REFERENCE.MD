# Lambda Execution Engine - Quick Reference

**Version:** 2025.10.10.02  
**Purpose:** At-a-glance reference for common tasks and values

---

## Essential Configuration Values

These values configure the Lambda Execution Engine with the Home Assistant Extension loaded. If you are running the Engine without any extensions, only AWS_REGION is required. All other variables configure the Home Assistant Extension.

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

These presets only apply when HOME_ASSISTANT_ENABLED is set to true. They control which features of the Home Assistant Extension are loaded. When running the Engine without the Home Assistant Extension, these presets have no effect.

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

## Common Troubleshooting Steps

### Function Does Not Execute

Verify Lambda trigger is configured correctly. Check that environment variables are set. Confirm IAM role has required permissions. Review CloudWatch Logs for specific error messages.

### Cannot Connect to Home Assistant

Test Home Assistant URL from external network. Verify access token is valid and not expired. Check SSL verification setting matches certificate type. Confirm Parameter Store values are accessible.

### Alexa Cannot Discover Devices

Verify Lambda function executed successfully. Check that devices are exposed in Home Assistant. Confirm Alexa trigger is configured with correct Skill ID.

### Commands Fail but Discovery Works

Test devices directly in Home Assistant. Verify entity IDs match between Alexa and Home Assistant. Check Home Assistant logs for incoming API requests.

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
Too short: A, H  
Too long: Names exceeding 25 characters
