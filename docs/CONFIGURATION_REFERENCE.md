# Lambda Execution Engine - Configuration Reference

**Version:** 2025.10.10  
**Purpose:** Complete reference for all configuration options

---

## Table of Contents

1. [Configuration Overview](#configuration-overview)
2. [Environment Variables](#environment-variables)
3. [Parameter Store Settings](#parameter-store-settings)
4. [Feature Presets](#feature-presets)
5. [Connection Methods](#connection-methods)
6. [Performance Tuning](#performance-tuning)
7. [Security Configuration](#security-configuration)

---

## Configuration Overview

The Lambda Execution Engine uses a layered configuration system. Environment variables in your Lambda function control runtime behavior and feature selection. Parameter Store holds sensitive credentials and instance-specific settings. Environment variables take precedence over Parameter Store values when both define the same setting.

Configuration changes in environment variables take effect immediately on the next function invocation. Parameter Store changes require the function to restart or cache to expire before taking effect. The cache duration is controlled by the HA_CACHE_TTL setting.

---

## Environment Variables

Environment variables are set in the Lambda function configuration under the Environment Variables section. These variables control core functionality, feature loading, performance characteristics, and integration behavior.

### Core System Variables

HOME_ASSISTANT_ENABLED controls whether the Home Assistant integration loads. Valid values are true and false. Set this to true to enable Home Assistant functionality or false to disable it completely. When disabled, the Lambda function will not attempt to connect to Home Assistant or load any Home Assistant modules. The default value is false.

USE_PARAMETER_STORE controls whether the function reads configuration from AWS Systems Manager Parameter Store. Valid values are true and false. Set this to true to enable Parameter Store integration or false to use only environment variables. When enabled, the function reads Home Assistant URL, token, and other settings from Parameter Store on startup. The default value is false.

PARAMETER_PREFIX defines the base path for Parameter Store parameters. The value should be a string starting with a forward slash. The default value is /lambda-execution-engine. The function appends additional path segments to this prefix to locate specific parameters. For example, with the default prefix, the Home Assistant URL parameter would be located at /lambda-execution-engine/homeassistant/url.

AWS_REGION specifies which AWS region to use for Parameter Store and other AWS services. Valid values include us-east-1, us-west-2, eu-west-1, and other AWS region codes. The default value is the region where your Lambda function runs. You only need to set this variable if you store parameters in a different region than your Lambda function.

DEBUG_MODE enables verbose logging for troubleshooting. Valid values are true and false. Set this to true during initial setup or when diagnosing problems. Set this to false in production to reduce log volume and memory usage. When enabled, the function logs detailed information about each operation, including parameter values, HTTP requests, and internal state. The default value is false.

### Home Assistant Integration Variables

HA_FEATURE_PRESET determines which Home Assistant features are loaded into memory. Valid values are minimal, standard, performance, and maximum. The minimal preset loads only basic device control functionality. The standard preset adds scene and script support. The performance preset includes advanced features like conversation and input helper support. The maximum preset loads all available features. The default value is standard. Higher presets consume more memory but provide more functionality.

HA_TIMEOUT sets the maximum time in seconds to wait for Home Assistant API responses. Valid values are integers from 5 to 120. Set lower values for faster local network connections or higher values for slower internet connections or complex automations. If Home Assistant does not respond within this timeout, the request fails and Alexa receives an error message. The default value is 30 seconds.

HA_VERIFY_SSL controls SSL certificate verification when connecting to Home Assistant. Valid values are true and false. Set this to true when using valid SSL certificates from a certificate authority or Cloudflare Tunnel. Set this to false when using self-signed certificates or local HTTP connections. Disabling verification reduces security but allows connections to Home Assistant instances without proper certificates. The default value is true.

HA_CACHE_TTL sets the duration in seconds to cache Home Assistant entity states and configuration. Valid values are integers from 0 to 3600. Higher values reduce API calls to Home Assistant but may return stale data. Lower values provide fresher data but increase network traffic. A value of 0 disables caching entirely. The default value is 300 seconds, which is five minutes.

HA_MAX_RETRIES specifies how many times to retry failed Home Assistant API calls. Valid values are integers from 0 to 5. Higher values increase reliability when Home Assistant experiences temporary issues but may delay error responses to Alexa. The default value is 3 retries.

HA_CIRCUIT_BREAKER_THRESHOLD sets the number of consecutive failures before the circuit breaker opens and stops sending requests to Home Assistant. Valid values are integers from 1 to 20. When the circuit breaker opens, the function immediately returns errors without attempting to contact Home Assistant. This protects Home Assistant from being overwhelmed during outages. The circuit breaker automatically closes after a recovery period. The default value is 5 failures.

HA_BATCH_SIZE controls how many operations to batch together when processing multiple device commands. Valid values are integers from 1 to 50. Higher values improve efficiency when controlling multiple devices simultaneously but may increase memory usage. The default value is 10 operations.

HA_ASSISTANT_NAME sets the invocation name for custom Alexa skills. Valid values are strings between 2 and 25 characters containing only letters, numbers, and spaces. Invalid values include reserved words like Alexa, Amazon, Echo, or strings containing special characters. This setting overrides the Parameter Store assistant_name value if both are set. The default value when not set is Home Assistant.

### Performance and Resource Variables

LUGS_ENABLED controls the Lazy loading Universal Gateway System. Valid values are true and false. Set this to true to enable lazy loading of modules, which reduces memory usage and improves cold start times. Set this to false to load all modules at startup. The default value is true. You should keep this enabled unless you need to debug module loading issues.

CONFIGURATION_TIER specifies the overall system resource usage tier. Valid values are minimum, standard, and maximum. The minimum tier disables non-essential features to reduce memory usage. The standard tier balances features and resources. The maximum tier enables all features and allocates more resources for performance. The default value is standard. This setting works in conjunction with HA_FEATURE_PRESET but controls system-wide resources rather than just Home Assistant features.

### Integration Control Variables

ALEXA_SKILL_ENABLED controls whether Alexa skill functionality is available. Valid values are true and false. Set this to true when using Alexa to control Home Assistant. Set this to false if you use the Lambda function for other purposes without Alexa integration. The default value is true.

---

## Parameter Store Settings

Parameter Store settings are created in AWS Systems Manager Parameter Store. Each parameter has a name following a hierarchical path structure, a type indicating how the value is stored, and a value containing the actual configuration data.

### Home Assistant Connection Parameters

The /lambda-execution-engine/homeassistant/url parameter stores your Home Assistant base URL. Create this as a String type parameter. The value should be your complete Home Assistant URL including the protocol and port number. For Cloudflare Tunnel connections, use the format https://homeassistant.yourdomain.com. For direct connections with port forwarding, use the format https://your-ip-or-domain:8123. For local HTTP connections during testing, use the format http://192.168.1.100:8123. The URL must be exactly how you access Home Assistant from outside your local network.

The /lambda-execution-engine/homeassistant/token parameter stores your Home Assistant long-lived access token. Create this as a SecureString type parameter for encryption. Generate the token from your Home Assistant profile page. Copy the entire token value without any spaces or line breaks. The token typically starts with a long random string of letters and numbers. SecureString encryption protects this sensitive credential even if someone gains access to Parameter Store.

### Home Assistant Behavior Parameters

The /lambda-execution-engine/homeassistant/assistant_name parameter sets the custom invocation name for Alexa. Create this as a String type parameter. Valid values are strings between 2 and 25 characters containing only letters, numbers, and spaces. Avoid reserved words like Alexa, Amazon, or Echo. Common choices include Jarvis, Computer, Smart Home, or House Assistant. This parameter is optional. When not set, the system uses Home Assistant as the default invocation name. The HA_ASSISTANT_NAME environment variable overrides this parameter if both are set.

The /lambda-execution-engine/homeassistant/verify_ssl parameter controls SSL certificate verification. Create this as a String type parameter. Valid values are true and false. Set this to true for connections using valid SSL certificates. Set this to false for self-signed certificates or local HTTP connections. This parameter is optional. When not set, the system defaults to true. The HA_VERIFY_SSL environment variable overrides this parameter if both are set.

The /lambda-execution-engine/homeassistant/timeout parameter sets the API timeout in seconds. Create this as a String type parameter. Valid values are integers from 5 to 120 represented as strings. Higher values work better for slower network connections or complex automations that take longer to execute. This parameter is optional. When not set, the system defaults to 30 seconds. The HA_TIMEOUT environment variable overrides this parameter if both are set.

---

## Feature Presets

Feature presets control which Home Assistant capabilities are loaded into memory. Each preset includes a specific set of modules optimized for different use cases. Higher presets provide more functionality but consume more memory and increase cold start times.

### Minimal Preset

The minimal preset loads only essential modules for basic device control. This preset includes entity state management, device control operations, and basic error handling. It supports turning devices on and off, setting brightness and temperature, and checking device status. The minimal preset uses approximately 15 megabytes of memory and completes cold starts in under 500 milliseconds.

The minimal preset does not include scene activation, script execution, automation control, conversation interface, input helper management, or area-based control. Use this preset when you only need simple device control and want to minimize resource usage.

### Standard Preset

The standard preset adds scene and script support to the minimal feature set. This preset includes all minimal features plus scene activation and script execution capabilities. It supports activating predefined scenes like movie mode or good morning, running automation scripts, and combining multiple device actions into single commands.

The standard preset uses approximately 20 megabytes of memory and completes cold starts in under 700 milliseconds. This is the recommended preset for most users as it provides commonly used features while maintaining good performance.

### Performance Preset

The performance preset includes advanced features for power users. This preset adds conversation interface support, input helper management, and enhanced error handling to the standard feature set. It supports natural language commands through Home Assistant conversation, setting input booleans and input numbers, and more detailed error messages.

The performance preset uses approximately 25 megabytes of memory and completes cold starts in under 900 milliseconds. Use this preset when you need advanced features and your Home Assistant instance includes conversation integration or extensive input helper configurations.

### Maximum Preset

The maximum preset loads all available modules for complete functionality. This preset includes all features from lower presets plus area-based control, announcement capabilities, and comprehensive diagnostics. It supports controlling all devices in a specific area with one command, sending text-to-speech announcements through Home Assistant, and accessing detailed system diagnostics through Alexa.

The maximum preset uses approximately 30 megabytes of memory and completes cold starts in under 1200 milliseconds. Use this preset when you need every available feature and memory usage is not a concern.

---

## Connection Methods

The Lambda Execution Engine supports multiple methods for connecting to your Home Assistant instance. Each method has different security, cost, and configuration requirements.

### Cloudflare Tunnel

Cloudflare Tunnel provides secure access to your Home Assistant instance without exposing ports to the internet. This method requires a domain name and Cloudflare account. Configuration involves installing the Cloudflare Tunnel client on your Home Assistant host and creating a tunnel that routes traffic to your local instance.

Set your Parameter Store URL to the format https://homeassistant.yourdomain.com where yourdomain.com is your registered domain. Set HA_VERIFY_SSL to true since Cloudflare provides valid SSL certificates automatically. This is the recommended method for most users due to its security and ease of use.

### Direct Connection with Valid SSL

Direct connection with valid SSL certificates requires port forwarding on your router and properly configured SSL certificates. This method uses a static IP address or dynamic DNS service. Configuration involves forwarding port 443 on your router to your Home Assistant instance and obtaining SSL certificates from a certificate authority.

Set your Parameter Store URL to the format https://your-domain.com:443 or https://your-static-ip:443. Set HA_VERIFY_SSL to true since you have valid SSL certificates. Ensure your certificates are current and automatically renewing to prevent connection failures.

### Direct Connection with Self-Signed Certificates

Self-signed certificates provide encryption without using a certificate authority. This method requires port forwarding and manual certificate creation. Configuration involves generating self-signed certificates on your Home Assistant host and configuring Home Assistant to use them.

Set your Parameter Store URL to the format https://your-ip:8123. Set HA_VERIFY_SSL to false since self-signed certificates cannot be verified against a trusted certificate authority. This method provides encryption but does not protect against man-in-the-middle attacks.

### VPN Connection

VPN connection provides the highest security by creating an encrypted tunnel between AWS and your home network. This method requires configuring AWS VPC, setting up a VPN gateway, and establishing a VPN connection to your home router. Configuration is complex and involves AWS networking services beyond the scope of this document.

Set your Parameter Store URL to your Home Assistant local IP address in the format http://192.168.1.100:8123. Set HA_VERIFY_SSL based on your internal certificate configuration. VPN connections incur additional AWS charges for VPN gateway operation.

---

## Performance Tuning

You can optimize Lambda Execution Engine performance by adjusting various configuration parameters based on your specific requirements and constraints.

### Memory Optimization

Reduce memory usage by setting HA_FEATURE_PRESET to minimal or standard. Enable LUGS_ENABLED to activate lazy loading. Set CONFIGURATION_TIER to minimum for the smallest memory footprint. Reduce HA_CACHE_TTL to decrease cache memory usage. These changes trade some functionality for lower memory consumption.

Monitor memory usage through CloudWatch metrics. If your function consistently uses less than 80 megabytes, you can leave the memory allocation at 128 megabytes. If usage approaches 128 megabytes, either increase the allocated memory or reduce the feature preset.

### Response Time Optimization

Improve response times by increasing HA_CACHE_TTL to reduce API calls to Home Assistant. Set HA_TIMEOUT to a lower value if you have a fast local network connection. Enable LUGS_ENABLED to reduce cold start times through lazy loading. Consider increasing Lambda allocated memory to 256 megabytes, which provides more CPU power and can improve execution speed.

Monitor execution duration through CloudWatch metrics. Target response times under 1000 milliseconds for good user experience with voice commands. Response times over 3000 milliseconds may cause Alexa to timeout.

### Reliability Optimization

Improve reliability by increasing HA_MAX_RETRIES to handle temporary network issues. Set HA_CIRCUIT_BREAKER_THRESHOLD higher to tolerate more failures before stopping requests. Increase HA_TIMEOUT for slower network connections. Enable comprehensive logging with DEBUG_MODE during troubleshooting but disable it in production.

Monitor error rates through CloudWatch metrics. Error rates above 5 percent indicate configuration or connectivity problems that need attention.

---

## Security Configuration

Proper security configuration protects your Home Assistant credentials and prevents unauthorized access to your smart home.

### Credential Protection

Always store your Home Assistant access token in Parameter Store using SecureString encryption. Never include tokens directly in environment variables or code. Use IAM roles to control access to Parameter Store parameters. Regularly rotate your Home Assistant access tokens by generating new tokens and updating Parameter Store.

Enable AWS CloudTrail to log all access to Parameter Store parameters. Review these logs periodically to detect any unauthorized access attempts. Configure Parameter Store parameter policies to restrict which IAM roles can read token values.

### Network Security

Use SSL connections to Home Assistant whenever possible by setting HA_VERIFY_SSL to true. Obtain proper SSL certificates from a certificate authority rather than using self-signed certificates. Consider using Cloudflare Tunnel which provides SSL termination and DDoS protection automatically.

If you must use self-signed certificates, ensure the private key remains secure on your Home Assistant host. Replace self-signed certificates with proper certificates as soon as possible for production deployments.

### Lambda Security

Restrict Lambda function IAM role permissions to the minimum required. The role should only have permission to write CloudWatch logs and read Parameter Store parameters. Do not grant additional permissions unless absolutely necessary.

Enable Lambda function encryption for environment variables if you store any sensitive values there. Review Lambda function configuration periodically to ensure no unnecessary permissions have been added. Monitor Lambda invocation logs through CloudWatch for any suspicious activity patterns.

### Access Token Security

Generate long-lived access tokens with the minimum permissions required for Lambda function operation. Create a dedicated Home Assistant user account for Lambda with restricted permissions if possible. Set token expiration dates and calendar reminders to rotate tokens before expiration.

Never share access tokens between multiple integrations or services. Create separate tokens for each integration to enable individual revocation if a token is compromised. Store backup tokens securely in case you need to restore access quickly.
