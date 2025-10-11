# Lambda Execution Engine Documentation Index

**Version:** 2025.10.10.02  
**Last Updated:** October 10, 2025

---

## Welcome

This documentation helps you set up and configure the Lambda Execution Engine, a general-purpose Lambda optimization framework, and the Home Assistant Extension which connects Amazon Alexa to your Home Assistant smart home installation. The Lambda Execution Engine provides core services including gateway routing, lazy loading, caching, circuit breaker protection, logging, and metrics. The Home Assistant Extension consumes these services to translate Alexa voice commands into Home Assistant API calls, enabling you to control your smart home devices through voice.

---

## Quick Navigation

Choose the guide that matches your current needs.

### I am setting up the Lambda function for the first time

If you have never used AWS before and need step-by-step instructions, start with the **HOME_ASSISTANT_SETUP_GUIDE.md**. This guide walks through every step from creating your AWS account to testing your first voice command. It covers setting up the Lambda Execution Engine and configuring the Home Assistant Extension. Estimated time is 45 to 75 minutes.

If you are familiar with AWS services and want to complete setup quickly, use the **QUICK_START.md** guide. This condensed guide assumes you understand AWS concepts and focuses on essential configuration steps for the Engine and Extension. Estimated time is 10 to 15 minutes.

### I need to configure or change settings

For detailed information about all configuration options, consult the **CONFIGURATION_REFERENCE.md** guide. This technical reference explains every environment variable and Parameter Store setting, describes Engine-level and Extension-level configurations, documents the different feature presets, explains connection methods, and provides performance tuning guidance. It includes a dedicated section explaining the architecture relationship between the Engine and extensions.

### I want to use a custom assistant name

To configure a custom invocation name like Jarvis or Computer instead of the default Home Assistant, read the **ASSISTANT_NAME_GUIDE.md**. This guide explains custom names as a feature of the Home Assistant Extension, documents when custom names are useful, covers validation rules, provides step-by-step configuration instructions, and includes troubleshooting for name-related issues.

### I am experiencing problems or have questions

For answers to common questions and solutions to frequent problems, see the **FAQ_AND_TROUBLESHOOTING.md** guide. This comprehensive support document covers setup issues, connection problems, device control issues, performance problems, security questions, and advanced troubleshooting procedures. It includes specific FAQs explaining the difference between the Engine and the Extension.

### I need to test my installation

To systematically test your Lambda function deployment, follow the **TESTING_AND_VALIDATION_GUIDE.md**. This guide provides testing procedures for both Engine core functionality and Extension-specific features. It covers pre-deployment testing, post-deployment testing checklists, feature-specific testing scenarios, performance testing methods, and security validation steps. It includes guidance on determining testing scope based on whether you are testing the Engine alone or with extensions loaded.

---

## Documentation Structure

### Core Setup Guides

**HOME_ASSISTANT_SETUP_GUIDE.md** - Complete setup for first-time users  
This comprehensive guide covers everything from creating your AWS account through testing your first voice command. It assumes no prior AWS experience and explains each concept as it is introduced. The guide clearly distinguishes between Engine configuration and Extension configuration, helping you understand what each setting controls. Use this guide if you want detailed explanations and step-by-step instructions for every phase of setup.

**QUICK_START.md** - Fast-track setup for experienced users  
This condensed guide provides essential configuration steps without detailed explanations. It assumes you already understand AWS IAM, Lambda, and Parameter Store. The guide clarifies which settings are required for the Engine versus which are specific to the Home Assistant Extension. Use this guide if you want to complete setup quickly and only need configuration values and key steps.

### Reference Guides

**CONFIGURATION_REFERENCE.md** - Complete technical reference  
This reference document explains every configuration option available in the Lambda Execution Engine and the Home Assistant Extension. It includes a dedicated Architecture section explaining how the Engine provides services that extensions consume. The guide covers all environment variables with their valid values and defaults, all Parameter Store settings and their purposes, the different feature presets and what they include, connection methods for different network configurations, performance tuning techniques, and security configuration best practices.

**ASSISTANT_NAME_GUIDE.md** - Custom invocation names  
This feature-specific guide covers custom assistant name configuration for the Home Assistant Extension. It explains how custom names work as an Extension feature, when they are useful versus when the default name is better, the validation rules Amazon enforces for invocation names, how to configure the name in both Lambda and Alexa, and troubleshooting for common name-related issues.

### Support Guides

**FAQ_AND_TROUBLESHOOTING.md** - Questions and problem resolution  
This support document provides answers to frequently asked questions about how the Engine and Extension work, cost, requirements, and capabilities. It includes a specific FAQ explaining the architectural difference between the Lambda Execution Engine and the Home Assistant Extension. The troubleshooting sections are organized by problem category such as setup issues, connection problems, device control issues, and performance problems. Each section provides diagnostic steps and solutions.

**TESTING_AND_VALIDATION_GUIDE.md** - Testing procedures  
This guide helps you verify that your Lambda function works correctly. It provides guidance on determining testing scope based on whether you are testing Engine core functionality or Extension-specific features. The guide includes pre-deployment testing to validate configuration before upload, post-deployment testing to confirm the function works after deployment, feature-specific testing for scenes, scripts, and other capabilities, performance testing to measure response times and resource usage, and security validation to ensure proper credential protection.

### Quick Reference

**QUICK_REFERENCE.md** - At-a-glance values and commands  
This quick reference provides common configuration values, testing commands, and troubleshooting steps in an easily scannable format. It clarifies which settings apply to the Engine core versus which are specific to the Home Assistant Extension, helping you quickly find the information you need.

### API Reference

**home_assistant_rest.md** - Home Assistant REST API reference  
This document describes the Home Assistant REST API endpoints that the Lambda function uses to communicate with Home Assistant. It covers authentication, available endpoints, request formats, and response structures.

**home_assistant_websocket.md** - Home Assistant WebSocket API reference  
This document describes the Home Assistant WebSocket API which provides real-time event streaming. While the Lambda function primarily uses REST API, understanding the WebSocket API helps with advanced troubleshooting.

**Home_assistant_auth_api.md** - Home Assistant authentication reference  
This document explains Home Assistant's authentication system including how to generate long-lived access tokens, how tokens are used in API requests, and token security considerations.

---

## Common Workflows

### First-Time Setup Workflow

Follow these steps when setting up the Lambda Execution Engine for the first time.

Read the prerequisites section in HOME_ASSISTANT_SETUP_GUIDE.md to ensure you have everything you need before starting. Note which prerequisites apply to the Engine versus which are specific to the Home Assistant Extension. Work through phases 1 through 9 of HOME_ASSISTANT_SETUP_GUIDE.md, completing each phase before moving to the next. After completing phase 9, proceed to TESTING_AND_VALIDATION_GUIDE.md and complete the post-deployment testing checklist. If you want to use a custom assistant name, read ASSISTANT_NAME_GUIDE.md and follow the configuration steps. When everything works, bookmark FAQ_AND_TROUBLESHOOTING.md for future reference when issues arise.

### Experienced User Workflow

If you are familiar with AWS, use this expedited workflow.

Review the prerequisites in QUICK_START.md to gather required information. Note that Home Assistant is only required if you are loading the Home Assistant Extension. Complete the AWS configuration section creating the IAM role, Parameter Store parameters, and Lambda function. Deploy your code package following the deployment section. Configure environment variables as documented, paying attention to HOME_ASSISTANT_ENABLED which controls extension loading. Set up your Alexa skill using either the Smart Home or Custom skill approach. Run the verification checklist in QUICK_START.md to confirm everything works. Reference CONFIGURATION_REFERENCE.md when you need details about specific settings.

### Troubleshooting Workflow

When you encounter problems, follow this systematic approach.

Check FAQ_AND_TROUBLESHOOTING.md to see if your issue is addressed in the frequently asked questions section. The FAQ includes specific guidance on distinguishing Engine issues from Extension issues. If your question is not covered, find the section that matches your problem type such as setup issues, connection problems, or device control issues. Follow the diagnostic steps provided for your specific problem. Check CloudWatch Logs as described in the advanced troubleshooting section if the problem persists. If your issue involves configuration settings, consult CONFIGURATION_REFERENCE.md to verify your settings are correct, paying attention to whether the setting is Engine-level or Extension-specific. For custom assistant name issues, check the troubleshooting section in ASSISTANT_NAME_GUIDE.md.

### Configuration Change Workflow

When you need to change configuration settings, use this workflow.

Identify what you want to change and look up the setting in CONFIGURATION_REFERENCE.md. The reference clearly indicates whether each setting controls Engine behavior or Extension behavior. Read the complete description of the setting including valid values, defaults, and consequences. Document your current configuration before making changes so you can revert if needed. Make the configuration change in either environment variables or Parameter Store as appropriate. If you changed Parameter Store, wait for cache expiration or restart the Lambda function. Test using procedures in TESTING_AND_VALIDATION_GUIDE.md appropriate for what you changed. Monitor CloudWatch metrics to verify the change had the intended effect. Document the change and the date you made it for future reference.

### Upgrade Workflow

When updating Lambda function code to a new version, follow these steps.

Review the release notes or changelog to understand what changed in the new version. Note whether changes affect the Engine core, the Home Assistant Extension, or both. Test the new code in a development environment if possible before updating production. Create a backup of your current deployment package in case you need to roll back. Follow the code update checklist in TESTING_AND_VALIDATION_GUIDE.md. Update your Lambda function with the new deployment package. Run smoke tests immediately after deployment to verify core functionality. Monitor error rates and performance metrics through CloudWatch. If critical issues occur, roll back to your backup deployment package. Document the upgrade and any issues you encountered.

---

## Additional Resources

### Home Assistant API Documentation

The API reference documents provide detailed technical information about Home Assistant APIs. While you do not need to understand these APIs in depth to use the Lambda Execution Engine with the Home Assistant Extension, they are helpful for troubleshooting connection issues or understanding what happens behind the scenes when the Extension communicates with Home Assistant.

The REST API reference explains the HTTP endpoints the Lambda function calls to control devices and query state. The WebSocket API reference describes the real-time event system Home Assistant uses. The authentication reference explains how access tokens work and how they are validated.

### AWS Documentation

AWS provides extensive documentation for Lambda, IAM, Parameter Store, and CloudWatch. These resources are helpful when you need to understand AWS concepts more deeply or troubleshoot AWS-specific issues.

The Lambda documentation explains concepts like execution roles, environment variables, and resource allocation. The IAM documentation covers permissions, policies, and security best practices. The Systems Manager documentation details Parameter Store encryption and access control. The CloudWatch documentation explains metrics, logs, and alarms.

---

## Getting Help

### Before Asking for Help

Before requesting assistance, complete these steps to gather information.

Check FAQ_AND_TROUBLESHOOTING.md for your specific issue. Review CloudWatch Logs for your Lambda function to see error messages. Determine whether the issue involves Engine core functionality or Extension-specific features. Test your Home Assistant instance directly using the REST API to isolate whether the problem is with Lambda or with Home Assistant. Verify your configuration against CONFIGURATION_REFERENCE.md. Try the troubleshooting steps for your issue type in the appropriate guide.

### Information to Include

When requesting help, provide these details to enable accurate assistance.

Describe what you are trying to do and what happens instead. Specify whether you are using the Home Assistant Extension or running the Engine without extensions. Include the exact error message if one appears. Provide relevant CloudWatch Log entries showing the error. Describe your configuration including HOME_ASSISTANT_ENABLED setting, feature preset, timeout settings, and connection method. Explain what troubleshooting steps you have already tried. Specify which guide you followed and at what step you encountered the problem.

---

## Documentation Conventions

### Placeholders

Documentation uses placeholders that you should replace with your actual values. Placeholders appear in italics or between brackets. For example, your-domain.com should be replaced with your actual domain name. The region code us-east-1 is an example that you should replace with your chosen AWS region.

### Command Examples

Command examples show the exact syntax you should use. Text you should type appears in monospace font. Comments explain what each part of the command does. Optional parameters are marked as optional in comments.

### File Paths

File paths in documentation use forward slashes consistent with Linux and macOS systems. Windows users should convert forward slashes to backslashes when appropriate. Parameter Store paths always use forward slashes even on Windows systems.

---

## Version History

**Version 2025.10.10.02** - Architecture corrections applied  
Updated all documentation to clarify architectural relationship between Lambda Execution Engine (standalone framework) and Home Assistant Extension (extension consuming Engine services). Emphasized extensibility and removed all implications that Engine requires Home Assistant. Removed all Nabu Casa references. Applied consistent terminology across all documents.

**Version 2025.10.10** - Initial consolidated documentation release  
Consolidated eight overlapping documentation files into five focused guides. Removed redundant information and external references. Added comprehensive testing guide and this navigation index. Improved organization for different user types and use cases.

---

## Contributing

If you find errors in documentation or have suggestions for improvement, note the specific document and section where the issue occurs. Describe the error or what information is missing or unclear. If suggesting new content, explain what use case it would address. Documentation improvements help all users of the Lambda Execution Engine.

---

## License

This documentation is provided as part of the Lambda Execution Engine project and is licensed under the Apache 2.0 license. You may use, modify, and distribute this documentation following the terms of that license.
