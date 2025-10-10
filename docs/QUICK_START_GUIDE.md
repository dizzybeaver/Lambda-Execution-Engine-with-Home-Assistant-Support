# Lambda Execution Engine - Quick Start Guide

**Version:** 2025.10.10  
**Estimated Time:** 10-15 minutes  
**Target Audience:** Users familiar with AWS services

---

## Prerequisites

You need an AWS account with appropriate IAM permissions, a Home Assistant instance accessible from the internet, and a Home Assistant long-lived access token. You should be comfortable with AWS Lambda, IAM, and Parameter Store.

---

## AWS Configuration

### IAM Role

Create an IAM role named LambdaExecutionEngineRole with Lambda as the trusted entity. Attach the AWSLambdaBasicExecutionRole managed policy and the AmazonSSMReadOnlyAccess managed policy. This role allows your Lambda function to write CloudWatch logs and read from Parameter Store.

### Parameter Store

Create the following parameters in AWS Systems Manager Parameter Store.

Create /lambda-execution-engine/homeassistant/url as a String parameter containing your complete Home Assistant URL including protocol and port.

Create /lambda-execution-engine/homeassistant/token as a SecureString parameter containing your Home Assistant long-lived access token.

Optionally create /lambda-execution-engine/homeassistant/assistant_name as a String to set a custom invocation name for Alexa.

Optionally create /lambda-execution-engine/homeassistant/verify_ssl as a String set to true or false depending on your SSL certificate configuration.

Optionally create /lambda-execution-engine/homeassistant/timeout as a String with the timeout value in seconds, typically 30 or 45.

### Lambda Function

Create a Lambda function with the following configuration. Use Python 3.12 runtime on x86_64 architecture. Set the function name to lambda-execution-engine. Assign the LambdaExecutionEngineRole as the execution role. Configure 128 MB memory and 30 seconds timeout.

Set the handler to lambda_function.lambda_handler.

---

## Code Deployment

### Required Files

Your deployment package needs these core files: lambda_function.py, gateway.py, and fast_path.py.

Include these core modules: cache_core.py, logging_core.py, security_core.py, metrics_core.py, config_core.py, http_client_core.py, singleton_core.py, circuit_breaker_core.py, initialization_core.py, lambda_core.py, and utility_core.py.

Include these supporting files: variables.py and variables_utils.py.

Include the Home Assistant extension: homeassistant_extension.py.

### Package Creation

Place all Python files at the root level of a ZIP archive named lambda-execution-engine.zip. Verify that no files use relative imports. Confirm that gateway.py includes the format_response function.

Upload the ZIP file through the Lambda console Code tab using the Upload From ZIP File option.

---

## Environment Variables

Configure these environment variables in your Lambda function.

Set HOME_ASSISTANT_ENABLED to true to enable the integration.

Set USE_PARAMETER_STORE to true to read configuration from Parameter Store.

Set PARAMETER_PREFIX to /lambda-execution-engine to specify the Parameter Store path prefix.

Set HA_FEATURE_PRESET to standard for balanced functionality and performance.

Set HA_TIMEOUT to 30 for the Home Assistant API timeout in seconds.

Set HA_VERIFY_SSL to true unless you use self-signed certificates.

Set LUGS_ENABLED to true to enable lazy loading for memory optimization.

Optionally set HA_ASSISTANT_NAME to override the Parameter Store assistant name.

Optionally set HA_CACHE_TTL to set the cache duration in seconds, typically 300.

Optionally set DEBUG_MODE to true for verbose logging during testing, but keep it false in production.

---

## Alexa Skill Setup

### Smart Home Skill

Create a Smart Home skill in the Amazon Developer Console for direct device control without custom invocation names. Set the default endpoint to your Lambda function ARN. Add an Alexa Smart Home trigger to your Lambda function using the skill ID. Discover devices in the Alexa app.

### Custom Skill

Create a Custom skill for custom assistant names. Set the invocation name to your chosen name in lowercase. Define the interaction model with conversation, device control, and help intents. Set the endpoint to your Lambda function ARN. Add an Alexa Skills Kit trigger to your Lambda function using the skill ID. Enable the skill in the Alexa app.

---

## Home Assistant Configuration

Expose the entities you want Alexa to control. Use the Alexa integration in Home Assistant to select specific entities, or add expose: true to entity configurations in configuration.yaml. Verify entity exposure through the Home Assistant Alexa integration settings.

---

## Testing

Create a test event in Lambda using an Alexa discovery directive to verify Home Assistant connectivity. Check CloudWatch logs for successful execution and device discovery. Test voice commands through Alexa. Review Lambda metrics for invocation count, duration, and error rate.

---

## Verification Checklist

Confirm that your Lambda function executes without errors. Verify that the function connects to Home Assistant successfully. Check that Alexa discovers your exposed entities. Test device control commands through Alexa. Review CloudWatch logs for any warnings or errors. Monitor Lambda execution metrics for performance.

---

## Common Issues

If devices do not appear in Alexa discovery, verify Parameter Store values are correct and check entity exposure settings in Home Assistant. If commands fail, review CloudWatch logs for error messages and verify your access token permissions. If you encounter timeout errors, increase the Lambda timeout or HA_TIMEOUT environment variable. For SSL errors with self-signed certificates, set HA_VERIFY_SSL to false.

---

## Next Steps

Review the Configuration Reference guide for detailed environment variable documentation. See the Assistant Name Guide for custom invocation name setup. Consult the FAQ and Troubleshooting guide for advanced configuration and optimization techniques.
