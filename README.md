# This project is in developement Flux, Please expect it to be broke.

# When trying out for yourself, move all .py files to the root directory of the zip file you make before deployment.
## I only keep them seperated here for ease of finding them.

### 1. Consider this project in Alpha Stage, I will update with changes as I go. 
### 2. The instruction are broke and 90% right and not complete but will worked on and simplified as I go.
### 3. I will do my best to address any breaking issues after it becomes fully functional.

'''
# Brief Informational Synopse:
## The Lambda Execution Engine
1. The Lambda Execution Engine is fully functional upon itself. It does not require any extension to work. But would have little to do if nothing used its services
2. The LEE is designed to keep resource usage at minimum while decreasing latency of services.
3. The LEE can be used to provide its functions and services to any extension added to it.
4. The LEE is upgraded to add in additional services or functions that an extension requires as generic functions and services. This in turn adds to more functions and services available to extensions in general.

## Extensions
1. Any Extension must wholely contained within itself. All code, if something needs to be changed in the LEE as requirement for the extension see #4 above.
2. It can use any services and functions provided by LEE. Think The Lambda Execution Engine is like the engine in the car, not the car. The extension is everything else but the engine.
3. The LEE must not be modified to make a extension work except to add the extension interface into LEE to be able to use it. See #4 above.
4. Extensions that are disabled must use almost zero memory and cpu. They should not be required for the LEE to work.

# Work Log
## Date: 10-13-2025 
1.  Import errors throughout project have been hunted and removed as much as I could find.
2.  http_client gateway interface has been optimized and websocket support added in along with normal http requests
3.  Home Assistant Extension has been optimized to reduce size and integrate in new websocket support thru the http_client gateway interface
4.  Cache and Singleton gateway interfaces optimized and checked for any import errors or breaking changes by other modifications.
5.  Metrics and Logging gateway interfaces optimized and checked for any import errors or breaking changes by other modifications.


# Below is an easy to access MD of available AWS Lambda Test Tab JSONs to be used to get information about any problems.

# Lambda Test Events Reference

Quick reference for AWS Lambda test events. Copy-paste these JSON payloads directly into the Lambda Test tab.

---

## Health & Diagnostics

### Basic Health Check
```json
{
  "health_check": true
}
```
*Returns Lambda status, version, gateway state, and HA connection*

### Full Diagnostic Scan
```json
{
  "test_type": "full"
}
```
*Complete system diagnostics: Lambda info, gateway stats, HA connection, assistant name*

### Full Diagnostic with Environment Display
```json
{
  "test_type": "full",
  "show_config": true
}
```
*Full diagnostics plus environment variables (HA_BASE_URL, tokens, etc.)*

### Home Assistant Diagnostic
```json
{
  "test_type": "homeassistant"
}
```
*Tests HA-specific functionality: connection status, entities, configuration*

### Configuration Diagnostic
```json
{
  "test_type": "configuration"
}
```
*Validates configuration settings and assistant name status only*

### Gateway-Only Diagnostic
```json
{
  "test_type": "gateway"
}
```
*Tests gateway stats, loaded modules, and core Lambda metrics without HA*

### Analytics Request
```json
{
  "analytics": true
}
```
*Returns usage statistics, gateway metrics, and request history*

---

## Debug Operations

### Debug Health Check
```json
{
  "command_args": ["health"]
}
```
*Runs debug_aws.py health check on all components*

### Debug Health Check - Specific Component
```json
{
  "command_args": ["health", "--component", "gateway"]
}
```
*Health check for specific component (gateway, cache, config, logging)*

### Debug Comprehensive Tests
```json
{
  "command_args": ["test", "--type", "comprehensive"]
}
```
*Runs full test suite across all components*

### Debug Ultra Optimization Tests
```json
{
  "command_args": ["test", "--type", "ultra"]
}
```
*Runs ultra-optimized test suite for speed*

### Debug Performance Tests
```json
{
  "command_args": ["test", "--type", "performance", "--iterations", "5000"]
}
```
*Performance benchmark with specified iterations*

### Debug Configuration Tests
```json
{
  "command_args": ["test", "--type", "configuration"]
}
```
*Tests configuration loading and validation*

### Debug System Analysis
```json
{
  "command_args": ["analyze"]
}
```
*Analyzes system architecture and module usage*

### Debug Architecture Analysis
```json
{
  "command_args": ["analyze", "--architecture"]
}
```
*Validates architectural compliance and patterns*

### Debug Import Analysis
```json
{
  "command_args": ["analyze", "--imports"]
}
```
*Validates import architecture and dependencies*

### Debug File Analysis
```json
{
  "command_args": ["analyze", "--file", "gateway.py"]
}
```
*Analyzes specific file usage patterns*

### Debug Performance Monitoring
```json
{
  "command_args": ["monitor", "--duration", "120"]
}
```
*Monitors performance for specified seconds*

### Debug Performance Benchmark
```json
{
  "command_args": ["benchmark", "--iterations", "1000"]
}
```
*Runs performance benchmark with iteration count*

### Debug Memory Benchmark
```json
{
  "command_args": ["benchmark", "--iterations", "500", "--memory"]
}
```
*Benchmark including memory analysis*

### Debug System Validation
```json
{
  "command_args": ["validate"]
}
```
*Validates system architecture and compliance*

### Debug Deployment Validation
```json
{
  "command_args": ["validate", "--deployment"]
}
```
*Validates deployment readiness*

### Debug Deployment Validation - Specific Files
```json
{
  "command_args": ["validate", "--deployment", "--files", "gateway.py", "lambda_function.py"]
}
```
*Validates specific files for deployment*

### Debug Full Diagnostics
```json
{
  "command_args": ["diagnostics", "--full"]
}
```
*Complete diagnostic report with all issues*

### Debug Quick Diagnostics
```json
{
  "command_args": ["diagnostics"]
}
```
*Quick diagnostic overview*

---

## API Gateway Simulation

### Health Endpoint (GET)
```json
{
  "httpMethod": "GET",
  "path": "/health"
}
```
*Simulates API Gateway health check request*

### Diagnostics Endpoint - Full (GET)
```json
{
  "httpMethod": "GET",
  "path": "/diagnostics",
  "queryStringParameters": {
    "type": "full"
  }
}
```
*Full diagnostics via API Gateway with query parameter*

### Diagnostics Endpoint - Home Assistant (GET)
```json
{
  "httpMethod": "GET",
  "path": "/diagnostics",
  "queryStringParameters": {
    "type": "homeassistant"
  }
}
```
*HA diagnostics via API Gateway*

### Diagnostics Endpoint - Configuration (GET)
```json
{
  "httpMethod": "GET",
  "path": "/diagnostics",
  "queryStringParameters": {
    "type": "configuration"
  }
}
```
*Configuration diagnostics via API Gateway*

### Diagnostics Endpoint (POST)
```json
{
  "httpMethod": "POST",
  "path": "/diagnostics"
}
```
*POST request triggers full diagnostics*

### Analytics Endpoint (GET)
```json
{
  "httpMethod": "GET",
  "path": "/analytics"
}
```
*Returns usage statistics and gateway metrics*

### Invalid Endpoint (404 Test)
```json
{
  "httpMethod": "GET",
  "path": "/invalid"
}
```
*Tests 404 error handling*

---

## Alexa Smart Home Directives

### Discovery Request
```json
{
  "directive": {
    "header": {
      "namespace": "Alexa.Discovery",
      "name": "Discover",
      "messageId": "test-message-001",
      "payloadVersion": "3"
    },
    "payload": {
      "scope": {
        "type": "BearerToken",
        "token": "test-token"
      }
    }
  }
}
```
*Discovers all available Home Assistant devices*

### Turn Device On
```json
{
  "directive": {
    "header": {
      "namespace": "Alexa.PowerController",
      "name": "TurnOn",
      "messageId": "test-message-002",
      "correlationToken": "test-correlation",
      "payloadVersion": "3"
    },
    "endpoint": {
      "endpointId": "light.living_room",
      "scope": {
        "type": "BearerToken",
        "token": "test-token"
      }
    },
    "payload": {}
  }
}
```
*Turns on specified device (replace endpointId with your entity)*

### Turn Device Off
```json
{
  "directive": {
    "header": {
      "namespace": "Alexa.PowerController",
      "name": "TurnOff",
      "messageId": "test-message-003",
      "correlationToken": "test-correlation",
      "payloadVersion": "3"
    },
    "endpoint": {
      "endpointId": "light.living_room",
      "scope": {
        "type": "BearerToken",
        "token": "test-token"
      }
    },
    "payload": {}
  }
}
```
*Turns off specified device*

### Set Brightness
```json
{
  "directive": {
    "header": {
      "namespace": "Alexa.BrightnessController",
      "name": "SetBrightness",
      "messageId": "test-message-004",
      "correlationToken": "test-correlation",
      "payloadVersion": "3"
    },
    "endpoint": {
      "endpointId": "light.bedroom",
      "scope": {
        "type": "BearerToken",
        "token": "test-token"
      }
    },
    "payload": {
      "brightness": 75
    }
  }
}
```
*Sets device brightness (0-100)*

### Adjust Brightness
```json
{
  "directive": {
    "header": {
      "namespace": "Alexa.BrightnessController",
      "name": "AdjustBrightness",
      "messageId": "test-message-005",
      "correlationToken": "test-correlation",
      "payloadVersion": "3"
    },
    "endpoint": {
      "endpointId": "light.bedroom",
      "scope": {
        "type": "BearerToken",
        "token": "test-token"
      }
    },
    "payload": {
      "brightnessDelta": -20
    }
  }
}
```
*Adjusts brightness relatively (positive or negative)*

### Set Thermostat Temperature
```json
{
  "directive": {
    "header": {
      "namespace": "Alexa.ThermostatController",
      "name": "SetTargetTemperature",
      "messageId": "test-message-006",
      "correlationToken": "test-correlation",
      "payloadVersion": "3"
    },
    "endpoint": {
      "endpointId": "climate.home",
      "scope": {
        "type": "BearerToken",
        "token": "test-token"
      }
    },
    "payload": {
      "targetSetpoint": {
        "value": 72.0,
        "scale": "FAHRENHEIT"
      }
    }
  }
}
```
*Sets thermostat target temperature*

### Adjust Thermostat Temperature
```json
{
  "directive": {
    "header": {
      "namespace": "Alexa.ThermostatController",
      "name": "AdjustTargetTemperature",
      "messageId": "test-message-007",
      "correlationToken": "test-correlation",
      "payloadVersion": "3"
    },
    "endpoint": {
      "endpointId": "climate.home",
      "scope": {
        "type": "BearerToken",
        "token": "test-token"
      }
    },
    "payload": {
      "targetSetpointDelta": {
        "value": 2.0,
        "scale": "FAHRENHEIT"
      }
    }
  }
}
```
*Adjusts thermostat temperature relatively*

### Set Thermostat Mode
```json
{
  "directive": {
    "header": {
      "namespace": "Alexa.ThermostatController",
      "name": "SetThermostatMode",
      "messageId": "test-message-008",
      "correlationToken": "test-correlation",
      "payloadVersion": "3"
    },
    "endpoint": {
      "endpointId": "climate.home",
      "scope": {
        "type": "BearerToken",
        "token": "test-token"
      }
    },
    "payload": {
      "thermostatMode": {
        "value": "HEAT"
      }
    }
  }
}
```
*Sets thermostat mode (HEAT, COOL, AUTO, OFF)*

### Accept Grant (Authorization)
```json
{
  "directive": {
    "header": {
      "namespace": "Alexa.Authorization",
      "name": "AcceptGrant",
      "messageId": "test-message-009",
      "payloadVersion": "3"
    },
    "payload": {
      "grant": {
        "type": "OAuth2.AuthorizationCode",
        "code": "test-auth-code"
      },
      "grantee": {
        "type": "BearerToken",
        "token": "test-token"
      }
    }
  }
}
```
*Handles OAuth authorization grant*

---

## Alexa Custom Skill Intents

### Launch Request
```json
{
  "version": "1.0",
  "session": {
    "new": true,
    "sessionId": "test-session-001",
    "application": {
      "applicationId": "amzn1.ask.skill.test"
    },
    "user": {
      "userId": "test-user-001"
    }
  },
  "request": {
    "type": "LaunchRequest",
    "requestId": "test-request-001",
    "timestamp": "2025-10-13T00:00:00Z",
    "locale": "en-US"
  }
}
```
*Launches custom skill with personalized assistant name*

### Help Intent
```json
{
  "version": "1.0",
  "session": {
    "new": false,
    "sessionId": "test-session-002",
    "application": {
      "applicationId": "amzn1.ask.skill.test"
    },
    "user": {
      "userId": "test-user-001"
    }
  },
  "request": {
    "type": "IntentRequest",
    "requestId": "test-request-002",
    "timestamp": "2025-10-13T00:00:00Z",
    "locale": "en-US",
    "intent": {
      "name": "AMAZON.HelpIntent"
    }
  }
}
```
*Triggers help response with assistant capabilities*

### Stop/Cancel Intent
```json
{
  "version": "1.0",
  "session": {
    "new": false,
    "sessionId": "test-session-003",
    "application": {
      "applicationId": "amzn1.ask.skill.test"
    },
    "user": {
      "userId": "test-user-001"
    }
  },
  "request": {
    "type": "IntentRequest",
    "requestId": "test-request-003",
    "timestamp": "2025-10-13T00:00:00Z",
    "locale": "en-US",
    "intent": {
      "name": "AMAZON.StopIntent"
    }
  }
}
```
*Stops skill session*

### Activate Scene Intent
```json
{
  "version": "1.0",
  "session": {
    "new": false,
    "sessionId": "test-session-004",
    "application": {
      "applicationId": "amzn1.ask.skill.test"
    },
    "user": {
      "userId": "test-user-001"
    }
  },
  "request": {
    "type": "IntentRequest",
    "requestId": "test-request-004",
    "timestamp": "2025-10-13T00:00:00Z",
    "locale": "en-US",
    "intent": {
      "name": "ActivateSceneIntent",
      "slots": {
        "SceneName": {
          "name": "SceneName",
          "value": "movie time"
        }
      }
    }
  }
}
```
*Activates Home Assistant scene*

### Trigger Automation Intent
```json
{
  "version": "1.0",
  "session": {
    "new": false,
    "sessionId": "test-session-005",
    "application": {
      "applicationId": "amzn1.ask.skill.test"
    },
    "user": {
      "userId": "test-user-001"
    }
  },
  "request": {
    "type": "IntentRequest",
    "requestId": "test-request-005",
    "timestamp": "2025-10-13T00:00:00Z",
    "locale": "en-US",
    "intent": {
      "name": "TriggerAutomationIntent",
      "slots": {
        "AutomationName": {
          "name": "AutomationName",
          "value": "bedtime routine"
        }
      }
    }
  }
}
```
*Triggers Home Assistant automation*

### Run Script Intent
```json
{
  "version": "1.0",
  "session": {
    "new": false,
    "sessionId": "test-session-006",
    "application": {
      "applicationId": "amzn1.ask.skill.test"
    },
    "user": {
      "userId": "test-user-001"
    }
  },
  "request": {
    "type": "IntentRequest",
    "requestId": "test-request-006",
    "timestamp": "2025-10-13T00:00:00Z",
    "locale": "en-US",
    "intent": {
      "name": "RunScriptIntent",
      "slots": {
        "ScriptName": {
          "name": "ScriptName",
          "value": "party mode"
        }
      }
    }
  }
}
```
*Runs Home Assistant script*

### Set Input Helper Intent
```json
{
  "version": "1.0",
  "session": {
    "new": false,
    "sessionId": "test-session-007",
    "application": {
      "applicationId": "amzn1.ask.skill.test"
    },
    "user": {
      "userId": "test-user-001"
    }
  },
  "request": {
    "type": "IntentRequest",
    "requestId": "test-request-007",
    "timestamp": "2025-10-13T00:00:00Z",
    "locale": "en-US",
    "intent": {
      "name": "SetInputHelperIntent",
      "slots": {
        "HelperName": {
          "name": "HelperName",
          "value": "house mode"
        },
        "HelperValue": {
          "name": "HelperValue",
          "value": "away"
        }
      }
    }
  }
}
```
*Sets Home Assistant input helper value*

### Session Ended Request
```json
{
  "version": "1.0",
  "session": {
    "new": false,
    "sessionId": "test-session-008",
    "application": {
      "applicationId": "amzn1.ask.skill.test"
    },
    "user": {
      "userId": "test-user-001"
    }
  },
  "request": {
    "type": "SessionEndedRequest",
    "requestId": "test-request-008",
    "timestamp": "2025-10-13T00:00:00Z",
    "locale": "en-US",
    "reason": "USER_INITIATED"
  }
}
```
*Handles session end notification*

---

## Test Combinations

### Quick System Check
```json
{
  "health_check": true
}
```
*Fastest way to verify Lambda is operational*

### Deep System Audit
```json
{
  "test_type": "full",
  "show_config": true
}
```
*Complete diagnostic with environment display*

### Debug Performance Suite
```json
{
  "command_args": ["benchmark", "--iterations", "1000", "--memory"]
}
```
*Comprehensive performance analysis*

### Debug Deployment Check
```json
{
  "command_args": ["validate", "--deployment"]
}
```
*Pre-deployment validation*

### Full Test Suite
```json
{
  "command_args": ["test", "--type", "comprehensive", "--verbose"]
}
```
*Run all tests with verbose output*

---

## Notes

**Entity IDs:** Replace placeholder entity IDs (like `light.living_room`) with actual entity IDs from your Home Assistant instance.

**Message IDs:** All message IDs are examples. Lambda doesn't validate these during testing.

**Tokens:** Test tokens are placeholders. Real Alexa requests include valid OAuth tokens.

**Debug Commands:** debug_aws.py commands return structured JSON responses suitable for CI/CD pipelines.

**Test Types:** 
- `full` - Complete diagnostics including HA and configuration
- `homeassistant` - HA connection and entity discovery
- `configuration` - Assistant name and config validation
- `gateway` - Gateway stats without HA testing

**Command Args:** debug_aws.py accepts command-line style arguments as array or space-separated string.

**Performance:** Debug operations may take longer than normal requests due to comprehensive analysis.

# EOF
