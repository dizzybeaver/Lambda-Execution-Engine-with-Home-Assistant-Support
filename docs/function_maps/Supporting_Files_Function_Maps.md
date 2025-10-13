# Supporting Files Function Maps
**Files:** usage_analytics.py, cloudformation_generator.py, deploy_automation.py  
**Category:** Utilities & Automation

---

# 1. usage_analytics.py - Usage Tracking

## Purpose
Track Lambda function usage patterns, module loading, and request types for optimization insights.

## Key Functions

### record_request_usage(loaded_modules: List[str], request_type: str)
- **Category:** Usage Tracking
- **Description:** Record which modules were loaded for a request type
- **Storage:** In-memory dict tracking patterns
- **Data Tracked:**
  - Request type
  - Loaded modules list
  - Timestamp
  - Request count

### get_usage_summary() -> Dict
- **Category:** Analytics Retrieval
- **Description:** Get summary of usage patterns
- **Returns:**
  - Most common request types
  - Most loaded modules
  - Average modules per request
  - Request type distribution

### analyze_module_patterns() -> Dict
- **Category:** Pattern Analysis
- **Description:** Analyze which modules are frequently loaded together
- **Returns:** Module co-occurrence patterns

### get_optimization_recommendations() -> List[str]
- **Category:** Optimization Insights
- **Description:** Suggest optimizations based on usage patterns
- **Recommendations:**
  - Modules to pre-load
  - Modules to lazy-load
  - Request routing optimizations

---

# 2. cloudformation_generator.py - Infrastructure as Code

## Purpose
Generate AWS CloudFormation templates for Lambda deployment.

## Class: CloudFormationGenerator

### __init__(preset: str)
- **Category:** Template Generator
- **Parameters:**
  - preset: Feature preset name (smart_home, api_gateway, etc.)
- **Initializes:** Template structure with preset configuration

### generate_template() -> Dict
- **Category:** Template Generation
- **Description:** Generate complete CloudFormation template
- **Template Sections:**
  - AWSTemplateFormatVersion
  - Description
  - Parameters (runtime, memory, timeout)
  - Resources (IAM role, Lambda function, triggers)
  - Outputs (function ARN, role ARN)
- **Returns:** CloudFormation template dict

### add_lambda_function(config: Dict)
- **Category:** Resource Builder
- **Description:** Add Lambda function resource to template
- **Configuration:**
  - FunctionName
  - Runtime (Python 3.12)
  - Handler (lambda_function.lambda_handler)
  - Role (IAM execution role)
  - MemorySize, Timeout
  - Environment variables

### add_iam_role(policies: List[str])
- **Category:** Security Configuration
- **Description:** Add IAM execution role with policies
- **Default Policies:**
  - AWSLambdaBasicExecutionRole (CloudWatch logs)
  - AmazonSSMReadOnlyAccess (Parameter Store)
- **Custom Policies:** Based on preset requirements

### add_triggers(triggers: List[Dict])
- **Category:** Event Source Configuration
- **Description:** Add event source mappings (Alexa Skills Kit, API Gateway, etc.)

### save(filename: str, output_format: str) -> str
- **Category:** Template Export
- **Description:** Save template to file
- **Formats:** YAML (default) or JSON
- **Returns:** Output filename

## Module Functions

### generate_all_presets(output_format: str) -> List[str]
- **Category:** Batch Generation
- **Description:** Generate CloudFormation templates for all presets
- **Presets:**
  - smart_home - Alexa Smart Home skill
  - custom_skill - Alexa Custom skill
  - api_gateway - HTTP API
  - scheduled - CloudWatch Events
  - minimal - Basic Lambda
- **Returns:** List of generated filenames

### main()
- **Category:** CLI Entry Point
- **Arguments:**
  - --preset: Preset name
  - --format: yaml or json
  - --all: Generate all presets
  - --output: Output filename

---

# 3. deploy_automation.py - Deployment Automation

## Purpose
Automate Lambda function deployment with testing, packaging, and verification.

## Class: DeploymentAutomation

### __init__(preset: str, function_name: str)
- **Category:** Deployment Manager
- **Parameters:**
  - preset: Feature preset
  - function_name: Lambda function name
- **Initializes:**
  - AWS clients (Lambda, S3)
  - Deployment configuration
  - Logging

### execute_deployment() -> Dict
- **Category:** Deployment Orchestration
- **Description:** Execute complete deployment pipeline
- **Pipeline Steps:**
  1. Run tests
  2. Build package
  3. Deploy to AWS
  4. Update environment
  5. Verify deployment
- **Returns:** Deployment report

### run_tests() -> bool
- **Category:** Pre-Deployment Testing
- **Description:** Run test suite before deployment
- **Tests:**
  - Health checks
  - Unit tests
  - Integration tests (if available)
- **Sub-functions:**
  - Uses debug_aws test framework
- **Returns:** bool (pass/fail)

### build_package() -> str
- **Category:** Packaging
- **Description:** Create deployment package ZIP
- **Steps:**
  1. Gather all Python files
  2. Verify no relative imports
  3. Create ZIP at root level
  4. Validate package structure
- **Returns:** Path to ZIP file

### deploy_to_aws(package_path: str) -> bool
- **Category:** AWS Deployment
- **Description:** Upload and deploy to Lambda
- **Sub-functions:**
  - `lambda_client.update_function_code()` - Upload ZIP
  - `lambda_client.get_function()` - Verify upload
- **Returns:** bool (success/failure)

### update_environment() -> bool
- **Category:** Configuration
- **Description:** Update Lambda environment variables
- **Variables Set:**
  - HOME_ASSISTANT_ENABLED
  - USE_PARAMETER_STORE
  - HA_FEATURE_PRESET
  - LUGS_ENABLED
  - DEBUG_MODE
- **Sub-functions:**
  - `lambda_client.update_function_configuration()`

### verify_deployment() -> bool
- **Category:** Post-Deployment Verification
- **Description:** Verify deployment success
- **Verification:**
  - Test invocation
  - Health check
  - Metrics validation
- **Sub-functions:**
  - `lambda_client.invoke()` - Test invocation
  - Parse response and validate

### log_step(step: str, status: str, details: str)
- **Category:** Logging
- **Description:** Log deployment step with status
- **Statuses:** START, SUCCESS, FAIL, SKIP

### generate_report(success: bool, duration: float) -> Dict
- **Category:** Reporting
- **Description:** Generate deployment report
- **Report Contents:**
  - Success/failure status
  - Preset and function name
  - Duration
  - Step-by-step log
  - Deployment statistics

## Module Functions

### main()
- **Category:** CLI Entry Point
- **Arguments:**
  - --preset: Feature preset
  - --function: Lambda function name
  - --skip-tests: Skip testing phase

---

# 4. homeassistant_extension.py - Home Assistant Integration

## Purpose
Extension module providing Home Assistant integration for Alexa Smart Home and Custom Skills.

## Core Functions

### initialize_ha_extension() -> Dict
- **Category:** Extension Lifecycle
- **Description:** Initialize HA extension
- **Sub-functions:**
  - Load configuration from Parameter Store
  - Validate HA connection
  - Initialize HA manager
- **Returns:** Success/error dict

### is_ha_extension_enabled() -> bool
- **Category:** Configuration
- **Description:** Check if extension is enabled
- **Source:** HOME_ASSISTANT_ENABLED environment variable

### get_ha_assistant_name() -> str
- **Category:** Configuration
- **Description:** Get configured assistant name
- **Sources (priority order):**
  1. HA_ASSISTANT_NAME env var
  2. Parameter Store
  3. Default: "Home Assistant"

### validate_assistant_name(name: str) -> Dict
- **Category:** Validation
- **Description:** Validate assistant name meets requirements
- **Rules:**
  - Length: 2-20 characters
  - No reserved words (Alexa, Amazon, Echo)
  - Alphanumeric with spaces only
- **Returns:** Dict with is_valid and error

## Alexa Integration

### handle_alexa_smart_home_request(event: Dict, context: Any) -> Dict
- **Category:** Alexa Smart Home
- **Description:** Handle Alexa Smart Home skill directives
- **Supported Directives:**
  - Discovery (DiscoverAppliancesRequest)
  - TurnOn/TurnOff
  - SetBrightness
  - SetColor
  - SetThermostat
  - Lock/Unlock
- **Sub-functions:**
  - Parse directive
  - Call HA API
  - Format Alexa response
- **Returns:** Alexa directive response

## Home Assistant API

### _get_ha_config_gateway() -> Dict
- **Category:** Configuration - Internal
- **Description:** Get HA configuration from all sources
- **Config Keys:**
  - enabled, base_url, access_token, timeout, verify_ssl, assistant_name
- **Sources:** Env vars + Parameter Store

### _make_ha_api_request(endpoint: str, method: str, data: Dict) -> Dict
- **Category:** HTTP Client - Internal
- **Description:** Make authenticated request to HA API
- **Sub-functions:**
  - Build headers with bearer token
  - `make_request()` from gateway
  - Error handling with circuit breaker
- **Returns:** API response dict

### get_ha_status() -> Dict
- **Category:** Health Check
- **Description:** Check HA connection and API status
- **Test:** GET /api/ endpoint
- **Returns:** Success/error with connection details

## Diagnostics

### get_ha_diagnostic_info() -> Dict
- **Category:** Diagnostics
- **Description:** Get comprehensive HA extension diagnostics
- **Diagnostic Data:**
  - Extension enabled status
  - Connection status
  - Assistant name
  - Configuration summary
  - Recent errors
- **Returns:** Diagnostic info dict

### cleanup_ha_extension() -> Dict
- **Category:** Lifecycle
- **Description:** Cleanup HA extension resources
- **Cleanup:**
  - Clear cache
  - Reset connection pool
  - Clear error state

---

# 5. fast_path.py - Performance Optimization

## Purpose
Ultra-fast execution paths for common operations, bypassing gateway routing when safe.

## Fast Path Functions

### fast_cache_get(key: str) -> Any
- **Category:** Performance - Cache
- **Description:** Direct cache access bypassing gateway
- **Use Case:** Hot path operations
- **Returns:** Cached value or None

### fast_log_info(message: str)
- **Category:** Performance - Logging
- **Description:** Template-based logging for common patterns
- **Uses:** Pre-compiled log templates
- **Performance:** 2-3x faster than standard logging

### fast_metric_record(name: str, value: float)
- **Category:** Performance - Metrics
- **Description:** Direct metric recording
- **Bypasses:** Gateway routing overhead

## Monitoring

### get_fast_path_stats() -> Dict
- **Category:** Observability
- **Description:** Get fast path usage statistics
- **Stats:**
  - Total fast path calls
  - Time saved
  - Hit rate
- **Returns:** Performance metrics

---

## Function Categories Summary

### usage_analytics.py
- **Usage Tracking:** record_request_usage()
- **Analytics:** get_usage_summary(), analyze_module_patterns()
- **Optimization:** get_optimization_recommendations()

### cloudformation_generator.py
- **Template Generation:** CloudFormationGenerator class
- **Resource Builders:** add_lambda_function(), add_iam_role(), add_triggers()
- **Export:** save(), generate_all_presets()

### deploy_automation.py
- **Deployment Pipeline:** DeploymentAutomation class
- **Testing:** run_tests()
- **Packaging:** build_package()
- **AWS Deployment:** deploy_to_aws(), update_environment()
- **Verification:** verify_deployment(), generate_report()

### homeassistant_extension.py
- **Lifecycle:** initialize_ha_extension(), cleanup_ha_extension()
- **Configuration:** get_ha_assistant_name(), validate_assistant_name()
- **Alexa Integration:** handle_alexa_smart_home_request()
- **HA API:** _make_ha_api_request(), get_ha_status()
- **Diagnostics:** get_ha_diagnostic_info()

### fast_path.py
- **Fast Operations:** fast_cache_get(), fast_log_info(), fast_metric_record()
- **Monitoring:** get_fast_path_stats()

---

**End of Supporting Files Function Maps**
