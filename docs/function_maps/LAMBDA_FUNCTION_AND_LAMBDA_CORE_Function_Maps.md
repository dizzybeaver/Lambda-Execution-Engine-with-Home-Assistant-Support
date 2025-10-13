# LAMBDA_FUNCTION & LAMBDA_CORE Function Maps
**Files:** lambda_function.py (entry point), lambda_core.py (Lambda operations)  
**Category:** AWS Lambda Integration  

---

# 1. lambda_function.py - Main Entry Point

## Call Hierarchy

```
AWS Lambda Runtime
    ↓
lambda_handler(event, context)
    ↓
├─→ _determine_request_type(event)
├─→ validate_request(event) [from gateway]
├─→ validate_token(event['token']) [from gateway]
└─→ process_request(event, context, request_type)
        ↓
    ├─→ _handle_alexa_directive(event, context)
    │       └─→ homeassistant_extension.handle_alexa_smart_home_request()
    │
    ├─→ _handle_alexa_intent(event, context)
    │       ├─→ _handle_help_intent()
    │       ├─→ _handle_control_device_intent()
    │       ├─→ _handle_set_scene_intent()
    │       ├─→ _handle_run_script_intent()
    │       ├─→ _handle_stop_intent()
    │       └─→ _handle_session_ended_request()
    │
    ├─→ _handle_health_check(event, context)
    ├─→ _handle_analytics_request(event, context)
    ├─→ _handle_diagnostic_request(event, context)
    └─→ _handle_api_gateway_request(event, context)
```

## Main Handler

### lambda_handler(event: Dict, context: Any) -> Dict
- **Category:** Entry Point - AWS Lambda
- **Map:** `AWS → lambda_handler() → process_request() → specific handlers`
- **Description:** Main entry point for all Lambda invocations
- **Sub-functions:**
  - `log_info()` - Log invocation start
  - `increment_counter('lambda_invocations')` - Track invocation
  - `_determine_request_type(event)` - Identify request type
  - `validate_request(event)` - Validate structure (skip for Alexa directives)
  - `validate_token(event['token'])` - Validate auth token if present
  - `process_request()` - Route to specific handler
  - `get_gateway_stats()` - Collect performance stats
  - `record_request_usage()` - Track usage analytics
  - `format_response()` - Format final response
- **Error Handling:** Catches all exceptions, logs, increments error counter
- **Returns:** Lambda proxy integration response dict

## Request Routing

### _determine_request_type(event: Dict) -> str
- **Category:** Request Analysis
- **Description:** Identify request type from event structure
- **Detection Logic:**
  - `'directive' in event` → "alexa_directive"
  - `'request' in event and 'intent' in event['request']` → "alexa_intent"
  - `'httpMethod' in event` → "api_gateway"
  - `'test_type' in event` → "diagnostic"
  - `event.get('request_type') == 'health'` → "health_check"
  - `event.get('request_type') == 'analytics'` → "analytics"
  - Default → "unknown"

### process_request(event: Dict, context: Any, request_type: str) -> Dict
- **Category:** Request Dispatcher
- **Map:** Routes to specific handler based on request_type
- **Handlers:**
  - "alexa_directive" → `_handle_alexa_directive()`
  - "alexa_intent" → `_handle_alexa_intent()`
  - "health_check" → `_handle_health_check()`
  - "analytics" → `_handle_analytics_request()`
  - "diagnostic" → `_handle_diagnostic_request()`
  - "api_gateway" → `_handle_api_gateway_request()`

## Alexa Smart Home Handlers

### _handle_alexa_directive(event: Dict, context: Any) -> Dict
- **Category:** Alexa Smart Home Integration
- **Map:** `lambda_handler → process_request → _handle_alexa_directive → homeassistant_extension.handle_alexa_smart_home_request()`
- **Description:** Handle Alexa Smart Home skill directives (device control)
- **Sub-functions:**
  - `log_info()` - Log directive processing
  - `increment_counter('alexa_directives')` - Track directives
  - `homeassistant_extension.handle_alexa_smart_home_request()` - Delegate to HA
  - `increment_counter('successful_directives')` on success
- **Error Handling:** Returns Alexa error response on exception

## Alexa Custom Skill Handlers

### _handle_alexa_intent(event: Dict, context: Any) -> Dict
- **Category:** Alexa Custom Skill Integration
- **Map:** `lambda_handler → process_request → _handle_alexa_intent → specific intent handler`
- **Description:** Route custom skill intents to handlers
- **Intent Routing:**
  - LaunchRequest → `_handle_help_intent()`
  - HelpIntent → `_handle_help_intent()`
  - ControlDeviceIntent → `_handle_control_device_intent()`
  - SetSceneIntent → `_handle_set_scene_intent()`
  - RunScriptIntent → `_handle_run_script_intent()`
  - SetInputHelperIntent → `_handle_set_input_helper_intent()`
  - MakeAnnouncementIntent → `_handle_make_announcement_intent()`
  - ControlAreaIntent → `_handle_control_area_intent()`
  - AMAZON.StopIntent/CancelIntent → `_handle_stop_intent()`
  - SessionEndedRequest → `_handle_session_ended_request()`

### _handle_help_intent(event: Dict, context: Any) -> Dict
- **Category:** Alexa Intent Handler
- **Sub-functions:**
  - `is_ha_extension_enabled()` - Check if HA enabled
  - `get_ha_assistant_name()` - Get assistant name from config
  - `_create_alexa_response()` - Build Alexa response
- **Returns:** Alexa response with help text and assistant name

### _handle_control_device_intent(event: Dict, context: Any) -> Dict
- **Category:** Alexa Intent Handler - Device Control
- **Description:** Handle custom device control commands
- **Slot Extraction:** DeviceName, Action slots
- **Status:** Placeholder - not yet implemented

### _handle_set_scene_intent(event: Dict, context: Any) -> Dict
- **Category:** Alexa Intent Handler - Scene Control
- **Slot Extraction:** SceneName slot
- **Status:** Placeholder - not yet implemented

### _handle_run_script_intent(event: Dict, context: Any) -> Dict
- **Category:** Alexa Intent Handler - Script Execution
- **Slot Extraction:** ScriptName slot
- **Status:** Placeholder - not yet implemented

### _handle_stop_intent(event: Dict, context: Any) -> Dict
- **Category:** Alexa Intent Handler
- **Returns:** "Goodbye!" response with session end

### _handle_session_ended_request(event: Dict, context: Any) -> Dict
- **Category:** Alexa Session Management
- **Description:** Handle session termination
- **Returns:** Empty dict

## Diagnostic & Analytics Handlers

### _handle_health_check(event: Dict, context: Any) -> Dict
- **Category:** Health Check - Observability
- **Description:** Comprehensive health status endpoint
- **Health Data:**
  - Status: "healthy"
  - Timestamp (request_id)
  - Version number
  - Gateway loaded status
  - HA extension status (if enabled)
  - HA connection status
- **Sub-functions:**
  - `is_ha_extension_enabled()` - Check HA status
  - `get_ha_status()` - Test HA connection
  - `format_response(200, health_status)` - HTTP response
- **Returns:** HTTP 200 with health JSON

### _handle_analytics_request(event: Dict, context: Any) -> Dict
- **Category:** Analytics - Observability
- **Description:** Usage statistics and metrics
- **Analytics Data:**
  - Usage summary from usage_analytics
  - Gateway statistics
  - Request timestamp
- **Sub-functions:**
  - `get_usage_summary()` - From usage_analytics module
  - `get_gateway_stats()` - Gateway metrics
  - `format_response(200, analytics)` - HTTP response

### _handle_diagnostic_request(event: Dict, context: Any) -> Dict
- **Category:** Diagnostics - Debugging
- **Description:** Comprehensive diagnostic information
- **Test Types:**
  - 'full' - All diagnostics
  - 'homeassistant' - HA specific
  - 'configuration' - Config only
- **Diagnostic Data:**
  - Lambda function info (name, version, memory, remaining time)
  - Gateway statistics
  - HA diagnostic info (if test_type includes 'homeassistant')
  - Environment variables (if show_config=true)
  - Assistant name status (if test_type includes 'configuration')
- **Sub-functions:**
  - `get_ha_diagnostic_info()` - HA diagnostics
  - `get_assistant_name_status()` - Name validation
  - `format_response(200, diagnostics)` - HTTP response

### _handle_api_gateway_request(event: Dict, context: Any) -> Dict
- **Category:** API Gateway Integration
- **Description:** Handle HTTP API requests
- **Routes:**
  - GET /health → `_handle_health_check()`
  - GET/POST /diagnostics → `_handle_diagnostic_request()`
  - GET /analytics → `_handle_analytics_request()`
  - All others → 404 Not Found
- **Sub-functions:**
  - Extract httpMethod and path from event
  - Route to appropriate handler
  - `format_response()` with status code

## Response Builders

### _create_alexa_response(speech_text: str, should_end_session: bool) -> Dict
- **Category:** Response Formatting - Alexa
- **Description:** Create standard Alexa Custom Skill response
- **Format:**
```json
{
  "version": "1.0",
  "response": {
    "outputSpeech": {
      "type": "PlainText",
      "text": "..."
    },
    "shouldEndSession": true/false
  }
}
```

---

# 2. lambda_core.py - Lambda Operations

## Call Hierarchy

```
Lambda Operations (not through gateway)
    ↓
_LAMBDA (LambdaCore singleton)
    ↓
├─→ LambdaCore.start_invocation()
├─→ LambdaCore.end_invocation()
├─→ LambdaCore.get_stats()
└─→ LambdaCore.estimate_cost()
```

## Core Class: LambdaCore

### Constructor: __init__()
- **Initializes:**
  - `_invocation_count` = 0
  - `_total_duration` = 0.0
  - `_start_time` = None

### start_invocation() -> float
- **Category:** Invocation Tracking
- **Description:** Start tracking Lambda invocation
- **Sub-functions:**
  - Increment `_invocation_count`
  - Set `_start_time = time.time()`
- **Returns:** Start timestamp

### end_invocation() -> float
- **Category:** Invocation Tracking
- **Description:** End tracking and calculate duration
- **Sub-functions:**
  - Calculate `duration = time.time() - _start_time`
  - Add to `_total_duration`
  - Reset `_start_time = None`
- **Returns:** Duration in seconds

### get_stats() -> Dict
- **Category:** Observability - Statistics
- **Description:** Get Lambda execution statistics
- **Calculations:**
  - `avg_duration = total_duration / invocation_count`
- **Returns:**
  - invocation_count
  - total_duration
  - average_duration

### estimate_cost(memory_mb: int = 128) -> Dict
- **Category:** AWS Cost Estimation
- **Description:** Estimate Lambda costs for free tier tracking
- **Calculations:**
  - `gb_seconds = (memory_mb / 1024) * total_duration`
  - `requests_pct = (invocations / 1_000_000) * 100`
  - `compute_pct = (gb_seconds / 400_000) * 100`
- **Free Tier Limits:**
  - Requests: 1,000,000 per month
  - Compute: 400,000 GB-seconds per month
- **Returns:**
  - invocations count
  - gb_seconds_used
  - free_tier_requests_pct
  - free_tier_compute_pct
  - within_free_tier (bool)

## Gateway Implementation Functions

### _execute_start_invocation_implementation() -> float
- **Map:** `execute_operation → _LAMBDA.start_invocation()`

### _execute_end_invocation_implementation() -> float
- **Map:** `execute_operation → _LAMBDA.end_invocation()`

### _execute_get_stats_implementation() -> Dict
- **Map:** `execute_operation → _LAMBDA.get_stats()`

### _execute_estimate_cost_implementation(memory_mb: int) -> Dict
- **Map:** `execute_operation → _LAMBDA.estimate_cost(memory_mb)`

---

## Function Categories Summary

### lambda_function.py Categories

**Entry Point & Routing**
- lambda_handler() - Main entry point
- _determine_request_type() - Request analysis
- process_request() - Request dispatcher

**Alexa Integration**
- _handle_alexa_directive() - Smart Home skill
- _handle_alexa_intent() - Custom skill
- Intent handlers (help, control, scene, script, stop, etc.)

**Diagnostics & Monitoring**
- _handle_health_check() - Health endpoint
- _handle_analytics_request() - Usage analytics
- _handle_diagnostic_request() - Comprehensive diagnostics
- _handle_api_gateway_request() - HTTP API

**Response Formatting**
- _create_alexa_response() - Alexa response builder

### lambda_core.py Categories

**Invocation Tracking**
- start_invocation() - Track start
- end_invocation() - Track end, calculate duration

**Observability**
- get_stats() - Execution statistics

**Cost Management**
- estimate_cost() - AWS free tier tracking

---

**End of LAMBDA_FUNCTION & LAMBDA_CORE Function Maps**
