# Lambda Execution Engine - Configuration Reference

**Version:** 2025.10.10  
**Purpose:** Complete reference for all configuration options

---

## Table of Contents

1. [Configuration Overview](#configuration-overview)
2. [Architecture: Engine and Extensions](#architecture-engine-and-extensions)
3. [Environment Variables](#environment-variables)
4. [Parameter Store Settings](#parameter-store-settings)
5. [Feature Presets](#feature-presets)
6. [Connection Methods](#connection-methods)
7. [Performance Tuning](#performance-tuning)
8. [Security Configuration](#security-configuration)

---

## Configuration Overview

The Lambda Execution Engine is a general-purpose Lambda optimization framework that provides core services for building extensions. The Home Assistant Extension is one extension that uses these services. Configuration settings fall into two categories: Engine-level settings that control core framework behavior, and extension-specific settings that control the Home Assistant Extension when loaded.

The Lambda Execution Engine uses a layered configuration system. Environment variables in your Lambda function control runtime behavior and feature selection. Parameter Store holds sensitive credentials and instance-specific settings. Environment variables take precedence over Parameter Store values when both define the same setting.

Configuration changes in environment variables take effect immediately on the next function invocation. Parameter Store changes require the function to restart or cache to expire before taking effect. The cache duration is controlled by the HA_CACHE_TTL setting.

---

## Architecture: Engine and Extensions

The Lambda Execution Engine follows a layered architecture that separates core framework services from extension-specific functionality. Understanding this architecture helps you configure the system correctly and explains why certain settings exist.

### Engine Core Services

The Engine core provides services that any extension can consume. These services include the gateway pattern where all operations route through a single entry point, lazy loading that imports modules only when needed, caching that stores frequently accessed data in memory, circuit breaker protection that prevents cascading failures when external services are unavailable, comprehensive logging that tracks all operations, and performance metrics that measure execution characteristics.

These services are always available when the Lambda function runs, regardless of which extensions are loaded. The Engine core does not implement any integration-specific logic. It provides the infrastructure that extensions use to implement their specific functionality.

### Home Assistant Extension

The Home Assistant Extension is self-contained code that implements Home Assistant integration by consuming Engine services. The extension uses the gateway for routing operations, the HTTP client for communicating with the Home Assistant API, the caching system for storing entity states, the circuit breaker for handling Home Assistant outages, and the logging system for recording operations.

The extension implements Home Assistant-specific logic including device discovery that queries Home Assistant for available entities, state queries that retrieve current entity states, device control that sends commands to change entity states, scene activation that triggers Home Assistant scenes, and script execution that runs Home Assistant scripts.

When HOME_ASSISTANT_ENABLED is false, the extension does not load. The Engine core still provides all its services, but no Home Assistant-specific functionality is available. When HOME_ASSISTANT_ENABLED is true, the extension loads and uses Engine services to provide full Home Assistant integration.

### Extension Development

The Engine's architecture allows you to develop additional extensions. Each extension must be self-contained, meaning it includes all its own logic without modifying the Engine core. Extensions use Engine services through well-defined interfaces. Extensions can access the gateway for routing, the HTTP client for external communication, the caching system for performance optimization, the circuit breaker for reliability, and the logging and metrics systems for observability.

An extension for Google Assistant would follow the same pattern as the Home Assistant Extension. It would implement Google-specific device discovery, state queries, and command execution while using Engine services for HTTP communication, caching, and error handling. An extension for SmartThings would similarly implement SmartThings-specific logic while leveraging Engine services.

The Engine does not limit what extensions can do. As long as an extension is self-contained and uses Engine services through their interfaces, it can implement any functionality. Extensions could integrate with different smart home platforms, provide webhook endpoints for other services, or implement entirely different Lambda function purposes.

---

## Environment Variables

Environment variables are set in the Lambda function configuration under the Environment Variables section. These variables control core functionality, feature loading, performance characteristics, and integration behavior.

### Core System Variables

**HOME_ASSISTANT_ENABLED**

This variable controls whether the Home Assistant Extension loads into the Lambda Execution Engine. The Engine itself is a standalone framework that provides services like gateway routing, lazy loading, caching, circuit breaker protection, and logging. These services remain available whether this variable is true or false. When set to true, the Home Assistant Extension loads and consumes these services to provide Home Assistant integration. When set to false, the Engine runs without the Home Assistant Extension, and the core services remain available for other extensions or purposes. The default value is false.

Valid values are true and false. Set this to true to enable Home Assistant functionality or false to disable it completely. When disabled, the Lambda function will not attempt to connect to Home Assistant or load any Home Assistant modules.

**USE_PARAMETER_STORE**

This variable controls whether the function reads configuration from AWS Systems Manager Parameter Store. Valid values are true and false. Set this to true to enable Parameter Store integration or false to use only environment variables. When enabled, the function reads Home Assistant URL, token, and other settings from Parameter Store on startup. The default value is false.

**PARAMETER_PREFIX**

This setting defines the base path for Parameter Store parameters. The value should be a string starting with a forward slash. The default value is /lambda-execution-engine. The function appends additional path segments to this prefix to locate specific parameters. For example, with the default prefix, the Home Assistant URL parameter would be located at /lambda-execution-engine/homeassistant/url.

**AWS_REGION**

This variable specifies which AWS region to use for Parameter Store and other AWS services. Valid values include us-east-1, us-west-2, eu-west-1, and other AWS region codes. The default value is the region where your Lambda function runs. You only need to set this variable if you store parameters in a different region than your Lambda function.

**DEBUG_MODE**

This setting enables verbose logging for troubleshooting. Valid values are true and false. When enabled, the function generates detailed log output including request payloads, response structures, internal state changes, and timing information. Debug mode significantly increases CloudWatch log volume and should only be enabled temporarily during troubleshooting. The default value is false.

### Extension Architecture

The Lambda Execution Engine follows an extension-based architecture. The Engine core provides optimized services that extensions consume. Each extension is self-contained and uses the services the Engine provides without modifying the Engine itself.

The Home Assistant Extension is currently the primary extension available. It uses Engine services for gateway routing, HTTP communication, caching, circuit breaker protection, logging, and metrics. The extension implements Home Assistant-specific logic for device discovery, state queries, and command execution.

You can build additional extensions following the same pattern. An extension for Google Assistant integration could use the same Engine services. An extension for SmartThings could use the same caching and circuit breaker services. The Engine's services are purpose-agnostic and support any extension that follows the extension interface.

### Home Assistant Extension Variables

These variables control the Home Assistant Extension when HOME_ASSISTANT_ENABLED is set to true. If the extension is not loaded, these variables have no effect, though they can remain configured without causing errors.

**HA_ASSISTANT_NAME**

This setting defines how Alexa refers to your Home Assistant system in custom skills. Valid values are strings between 2 and 25 characters containing only letters, numbers, and spaces. You cannot use reserved words like Alexa, Amazon, or Echo. The default value is Home Assistant. Examples of valid custom names include Jarvis, Computer, Smart Home, or House Control. The name you set here must match the invocation name in your Alexa Custom Skill configuration.

**HA_FEATURE_PRESET**

This variable controls which Home Assistant features load into memory and how much resources they consume. Valid values are minimal, standard, performance, and maximum. The minimal preset loads only essential functionality and uses approximately 15MB of memory. The standard preset provides all core features with balanced resource allocation and uses approximately 25MB of memory. The performance preset adds optimization features and enhanced caching using approximately 40MB of memory. The maximum preset enables all available features and uses approximately 60MB of memory. The default value is standard.

**HA_TIMEOUT**

This setting specifies how long in seconds the function waits for Home Assistant to respond before timing out. Valid values are integers from 15 to 120. Lower values fail faster when Home Assistant is unreachable but may cause timeouts on slow networks. Higher values provide more tolerance for network delays but can cause user-visible lag when Home Assistant is down. For local network connections, values between 15 and 30 work well. For internet connections, values between 30 and 45 provide good balance. For slow or unreliable connections, consider values up to 60 seconds. The default value is 30.

**HA_VERIFY_SSL**

This variable controls whether the function verifies SSL certificates when connecting to Home Assistant. Valid values are true and false. Set this to true for production deployments with valid SSL certificates. Set to false for development environments, local installations with self-signed certificates, or HTTP connections. When set to false, the connection is still encrypted but certificate validity is not checked. The default value is true.

**HA_CACHE_TTL**

This setting defines how long in seconds the function caches Home Assistant entity states before refreshing them. Valid values are integers from 60 to 3600. Lower values keep state information more current but generate more Home Assistant API calls. Higher values reduce API traffic but may show stale information. For frequently changing devices like sensors, values between 60 and 300 work well. For stable configurations like device lists, values between 600 and 1800 are appropriate. During development when you are making frequent changes, use 60 to see updates quickly. The default value is 300 (5 minutes).

**HA_MAX_RETRIES**

This variable specifies how many times the function retries failed Home Assistant requests before giving up. Valid values are integers from 1 to 10. Higher values provide more resilience to temporary network issues but can increase response time when Home Assistant is truly unavailable. Lower values fail faster but may not recover from transient problems. The default value is 3.

**HA_CIRCUIT_BREAKER_THRESHOLD**

This setting determines how many consecutive failures trigger the circuit breaker to open and temporarily stop requests to Home Assistant. Valid values are integers from 1 to 20. Lower values protect Home Assistant from excessive traffic during outages but may open too quickly from isolated failures. Higher values tolerate more errors before opening but may allow more failed requests through. The default value is 5.

**HA_BATCH_SIZE**

This variable controls how many entities the function processes in batch operations like device discovery. Valid values are integers from 1 to 50. Lower values reduce memory usage but increase processing time. Higher values process faster but use more memory. The default value is 10.

### Performance and Resource Variables

**CONFIGURATION_TIER**

This setting controls the overall resource allocation and feature set for the Engine core services. Valid values are minimum, standard, maximum, and user. The minimum tier uses approximately 8MB of memory and provides essential functionality only. The standard tier uses approximately 32MB and provides complete production capability with balanced features. The maximum tier uses approximately 103MB and activates all available features. The user tier allows custom per-interface configuration. The default value is standard.

**LUGS_ENABLED**

This variable enables the Lazy Universal Gateway System that delays loading modules until they are actually needed. Valid values are true and false. When enabled, the function starts faster and uses less memory because it only loads modules required for each specific request. When disabled, all modules load at startup which increases cold start time but may reduce individual request latency. This setting should almost always be true. The default value is true.

### Integration Control Variables

**ALEXA_SKILL_ENABLED**

This setting controls whether the function processes Alexa skill requests. Valid values are true and false. Set this to true when using the function with Alexa or false to disable Alexa integration. The default value is true.

---

## Parameter Store Settings

AWS Systems Manager Parameter Store provides secure storage for sensitive configuration values like Home Assistant URLs and access tokens. Parameters are organized under a prefix path defined by the PARAMETER_PREFIX environment variable.

### Connection Parameters

**/lambda-execution-engine/homeassistant/url**

This parameter stores the complete URL to your Home Assistant instance. The value should include the protocol (http or https), hostname or IP address, and port if non-standard. For example, https://your-home.example.com or http://192.168.1.100:8123. The function uses this URL for all Home Assistant API requests.

Create this parameter as type String (not SecureString because URLs are not sensitive). If you change this value, the function will use the new URL on the next invocation after the cache expires.

**/lambda-execution-engine/homeassistant/token**

This parameter stores your Home Assistant long-lived access token. Create this parameter as type SecureString to ensure the token is encrypted at rest. The token value should be the complete access token string generated in Home Assistant under your user profile. The function uses this token to authenticate all Home Assistant API requests.

If you regenerate your Home Assistant token, update this parameter with the new value and the function will use it on the next invocation.

### Behavior Parameters

**/lambda-execution-engine/homeassistant/assistant_name**

This optional parameter stores the custom assistant name for Alexa invocations. The value should match the invocation name configured in your Alexa Custom Skill. If this parameter exists, its value is used unless the HA_ASSISTANT_NAME environment variable is set (environment variables take precedence). Create this as type String.

**/lambda-execution-engine/homeassistant/timeout**

This optional parameter sets the Home Assistant request timeout in seconds. If this parameter exists, its value is used unless the HA_TIMEOUT environment variable is set. Valid values are integers from 15 to 120. Create this as type String.

**/lambda-execution-engine/homeassistant/verify_ssl**

This optional parameter controls SSL certificate verification. Valid values are true and false as strings. If this parameter exists, its value is used unless the HA_VERIFY_SSL environment variable is set. Create this as type String.

---

## Feature Presets

Feature presets control which Home Assistant Extension features load into memory. These presets only apply when HOME_ASSISTANT_ENABLED is set to true. When the extension is not loaded, preset settings have no effect.

### Minimal Preset

The minimal preset loads only essential Home Assistant functionality and uses approximately 15MB of memory. This preset includes basic device control and state queries. It provides cache TTL of 60 seconds, supports 2 retry attempts, has a timeout of 15 seconds, and enables basic features only. Use this preset for testing, development, or resource-constrained environments where you need to minimize memory usage.

### Standard Preset (Recommended)

The standard preset provides all core Home Assistant functionality with balanced resource allocation. This preset uses approximately 25MB of memory and includes all typical smart home features. It provides cache TTL of 300 seconds (5 minutes), supports 3 retry attempts, has a timeout of 30 seconds, and enables all standard features. This preset works well for most production deployments and provides the right balance between functionality and resource efficiency.

### Performance Preset

The performance preset adds optimization features and enhanced caching to improve response times. This preset uses approximately 40MB of memory. It provides cache TTL of 600 seconds (10 minutes), supports 5 retry attempts, has a timeout of 45 seconds, and enables all features plus optimizations. Use this preset for large installations with many devices or when you want maximum responsiveness and can afford the extra memory usage.

### Maximum Preset

The maximum preset enables all available Home Assistant Extension features and uses approximately 60MB of memory. It provides cache TTL of 1800 seconds (30 minutes), supports 7 retry attempts, has a timeout of 60 seconds, and enables everything with maximum caching. This preset suits enterprise deployments or situations requiring maximum reliability. The increased cache duration and retry attempts provide excellent resilience but consume more memory and may show less current state information.

---

## Connection Methods

Your Home Assistant installation must be accessible from AWS for the Lambda function to communicate with it. Several connection methods are available depending on your network setup and security requirements.

### Direct Connection with Valid SSL

If your Home Assistant has a public domain name with a valid SSL certificate, this is the simplest and most secure connection method. Set HA_VERIFY_SSL to true and provide your complete HTTPS URL. The function will verify the SSL certificate on every connection ensuring secure communication. This method works with Let's Encrypt certificates, certificates from commercial certificate authorities, or any other valid SSL certificate.

### Direct Connection with Self-Signed Certificates

If your Home Assistant uses a self-signed SSL certificate, you need to disable SSL verification to allow the connection. Set HA_VERIFY_SSL to false and provide your HTTPS URL. The traffic is still encrypted, but the function does not verify the certificate validity. This method is acceptable for home use but should not be used for production environments with sensitive data.

### VPN Connection

For maximum security, you can set up a VPN connection between your AWS VPC and your home network. This method requires creating an AWS VPC, setting up a VPN gateway, configuring your Lambda function to run inside the VPC, and establishing the VPN connection to your home network. VPN connections provide the highest security level but add complexity and may incur additional AWS costs outside the free tier.

### HTTP Connection (Local Networks Only)

If your Home Assistant is not accessible via HTTPS, you can use an HTTP connection. Set HA_VERIFY_SSL to false and provide your HTTP URL. This method transmits all traffic including your access token in the clear and should only be used on trusted local networks. Never use HTTP connections over the public internet as your credentials could be intercepted.

---

## Performance Tuning

The Lambda Execution Engine provides multiple ways to optimize performance for your specific use case. Understanding these tuning options helps you find the right balance between response time, resource usage, and cost.

### Memory Optimization

Lower memory usage reduces AWS Lambda costs and allows more concurrent invocations within free tier limits. To optimize memory, use a lower feature preset like minimal or standard. Enable LUGS to ensure lazy loading. Set HA_BATCH_SIZE to smaller values to process entities in smaller chunks. Choose the minimum CONFIGURATION_TIER that meets your functional needs. Monitor actual memory usage in CloudWatch and adjust configuration accordingly.

Memory usage varies by operation type. Device discovery uses the most memory because it processes all entities at once. Simple device commands use minimal memory because they only load required modules. State queries fall in between depending on how many entities you query.

### Response Time Optimization

Faster response times improve user experience but may require more memory or generate more API calls. To optimize response times, use a higher feature preset like performance or maximum. Increase HA_CACHE_TTL to cache entity states longer and reduce API calls. Set HA_BATCH_SIZE to larger values to process entities faster. Choose a higher CONFIGURATION_TIER to enable performance features. Ensure your Home Assistant responds quickly by optimizing its performance.

The most impactful optimization is cache tuning. Longer cache TTL means the function returns cached entity states instead of querying Home Assistant, dramatically improving response time. However, cached states may be stale if devices change state between queries.

### Reliability Optimization

Higher reliability ensures the function handles temporary issues gracefully but may increase response time when problems occur. To optimize reliability, increase HA_MAX_RETRIES to retry more times on failures. Raise HA_CIRCUIT_BREAKER_THRESHOLD to tolerate more errors before opening. Extend HA_TIMEOUT to allow more time for slow responses. Use performance or maximum preset for enhanced error recovery features. Monitor circuit breaker activations in CloudWatch logs.

The circuit breaker is the most important reliability feature. When Home Assistant becomes unreachable, the circuit breaker opens after the threshold number of failures. While open, the function immediately rejects requests without trying to connect, preventing timeout delays. The circuit closes automatically after a recovery period, allowing requests to try again.

---

## Security Configuration

Security configuration protects your Home Assistant credentials and ensures only authorized requests reach your smart home.

### Credential Protection

Your Home Assistant access token grants complete control over your smart home installation. Proper credential protection is essential. Always store tokens in Parameter Store as SecureString type which encrypts the token at rest. Never put tokens in environment variables because those are visible in the Lambda console. Rotate tokens periodically by generating a new token in Home Assistant and updating Parameter Store. Limit token scope to required operations when Home Assistant supports scoped tokens. Monitor token usage in Home Assistant logs to detect unauthorized access.

The Lambda function retrieves tokens from Parameter Store on each invocation. The token exists in memory only during request processing and disappears when the function completes. The function never logs tokens or includes them in error messages.

### Network Security

Network security ensures communication between the Lambda function and Home Assistant cannot be intercepted or modified. Use SSL/TLS connections with valid certificates whenever possible by setting HA_VERIFY_SSL to true. Only disable SSL verification for local networks you control. Never transmit credentials over unencrypted HTTP connections. Consider VPN connections for maximum security. Keep Home Assistant updated with security patches.

The Lambda function runs in AWS's secure environment. AWS manages all security for the Lambda runtime, operating system, and network infrastructure. You are responsible for securing your Home Assistant installation and network connection.

### Lambda Security

Lambda function security controls what the function can access in AWS. Use the principle of least privilege by granting only required IAM permissions. Never grant Administrator access or overly broad permissions. Enable MFA on your AWS account to prevent unauthorized changes. Review permissions regularly and remove any that are no longer needed. Monitor CloudWatch logs for unusual activity. Use CloudWatch alarms to detect suspicious invocation patterns.

The Lambda execution role should grant access to Parameter Store for reading configuration, CloudWatch Logs for writing log entries, and no other AWS services unless specifically required for additional functionality.

### Access Token Security

Home Assistant access tokens provide complete control over your installation. Generate tokens with appropriate scope when Home Assistant supports scoped tokens. Set token expiration when Home Assistant supports expiring tokens. Revoke tokens immediately if compromised. Use different tokens for different integrations. Monitor token usage in Home Assistant audit logs.

When you rotate tokens, update Parameter Store with the new value. The function will use the new token on its next invocation. There is no need to restart or redeploy the Lambda function.
