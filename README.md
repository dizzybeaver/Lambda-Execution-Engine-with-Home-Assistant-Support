# Lambda Execution Engine with Home Assistant Support

[![Status](https://img.shields.io/badge/status-beta-yellow.svg)](https://github.com/dizzybeaver/Lambda-Execution-Engine-with-Home-Assistant-Support)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![AWS Lambda](https://img.shields.io/badge/AWS-Lambda-orange.svg)](https://aws.amazon.com/lambda/)
[![Python](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/)
[![Free Tier](https://img.shields.io/badge/AWS-Free%20Tier-green.svg)](https://aws.amazon.com/free/)

**A revolutionary AWS Lambda-based execution engine with native Home Assistant integration and Alexa voice control support.**

---

## Overview

The Lambda Execution Engine (LEE) is a serverless smart home automation platform built on AWS Lambda. It combines innovative architectural patterns with real-world functionality to deliver a highly optimized, maintainable, and extensible execution environment.

The Home Assistant extension enables voice control through Alexa, automation management, and seamless integration with your existing Home Assistant setup - all running within AWS Free Tier constraints.

### Current Status: BETA

**What's Working:**
- Core Lambda Execution Engine - Production Ready
- Home Assistant Extension - Successfully deployed **October 18, 2025**
- Alexa Voice Control - Working in production
- Smart Home Device Discovery & Control
- Automation & Script Execution
- Real-time Status Updates

**What to Expect:**
- Active feature testing and refinement
- Occasional bugs (we're in beta!)
- Ongoing performance optimizations
- Documentation improvements
- Community feedback integration

---

## Key Features

### Lambda Execution Engine
- **Zero Technical Debt Architecture** - Built on proven SUGA-ISP patterns
- **128MB Memory Constraint** - Optimized for AWS Free Tier
- **Sub-200ms Response Times** - Performance-first design
- **Intelligent Circuit Breakers** - Automatic fault protection
- **Multi-tier Configuration** - From minimal to maximum capability
- **Failsafe Mode** - Emergency fallback system (toggle without redeployment)

### Home Assistant Integration
- **Alexa Smart Home Skill** - Full voice control integration
- **Device Management** - Lights, switches, climate, locks, and more
- **Automation Control** - Trigger and manage automations via voice
- **Script Execution** - Run Home Assistant scripts
- **Real-time Updates** - WebSocket support for live status
- **Secure Token Management** - AWS SSM Parameter Store integration

---

## The Three Revolutionary Architectures

### 1. SUGA - Single Universal Gateway Architecture

**The Problem:** Traditional Lambda applications duplicate infrastructure across every module - HTTP clients, logging, caching, error handling - resulting in 400KB+ of redundant code and maintenance nightmares.

**The Solution:** SUGA consolidates ALL infrastructure operations through ONE intelligent routing hub.

```python
# Every module imports ONLY from gateway
from gateway import log_info, cache_get, http_post, execute_operation
```

**Benefits:**
- Eliminates circular import dependencies
- Reduces memory overhead by 400KB+
- Enables lazy loading of modules
- Centralizes optimization
- Makes features truly removable

**Quantified Impact:**
- **Memory Reduction:** 400KB+ saved
- **Import Complexity:** 11 gateways → 1 gateway
- **Maintenance:** Single point of optimization
- **Code Duplication:** 0% (vs 60%+ traditional)

### 2. ISP Network Topology

**The Enhancement:** Inspired by Internet Service Provider architecture, the ISP layer adds interface-level isolation to prevent circular dependencies at scale.

```
Gateway (ISP Layer)
    ↓
Interface Routers (Firewalls)
    ↓
Internal Implementations
```

**Key Principles:**
- Interface routers act as firewalls
- Internal files can communicate within their interface
- Cross-interface communication MUST use the gateway
- Uni-directional flow prevents circular imports

**Benefits:**
- Impossible to create cross-interface circular dependencies
- Clear architectural boundaries
- Self-documenting structure
- Easy to test and maintain

### 3. Extension Pure Delegation Facade

**The Pattern:** Extensions (like Home Assistant) follow a pure delegation pattern where the extension file acts as a mini-gateway.

```
lambda_function.py
    ↓
homeassistant_extension.py (Extension ISP)
    ↓
home_assistant/ (Internal Implementation)
```

**Facade Characteristics:**
- Pure delegation - no business logic in facade
- Access control - extension enabled checks
- Lazy loading - imports internals only when called
- Error boundary - top-level exception handling
- Gateway powered - uses SUGA for all infrastructure

**Complete Removability:**
```bash
# To remove Home Assistant extension:
export HOME_ASSISTANT_ENABLED=false
rm homeassistant_extension.py
rm -rf home_assistant/

# Lambda continues working perfectly!
```

---

## Performance Optimizations

### Intelligent Caching
- Multi-tier cache system (minimum to maximum)
- Configurable TTL and memory allocation
- Cache hit rate monitoring
- Automatic cache invalidation

### Circuit Breaker Protection
- Automatic failure detection
- Half-open recovery testing
- Configurable thresholds per tier
- Prevents cascade failures

### Lazy Loading
- Modules loaded only when needed
- Faster cold starts
- Reduced memory pressure
- Dynamic feature activation

### Memory Management
```
Minimum Tier:  ~45MB total usage
Standard Tier: ~64MB total usage
Maximum Tier:  ~85MB total usage
```

All tiers operate comfortably within the 128MB Lambda limit.

---

## Security Features

### Multi-Layer Protection
- **Input Validation** - Sanitization at gateway level
- **Token Encryption** - AWS SSM SecureString storage
- **SSL Verification** - Configurable per environment
- **Rate Limiting** - Protection against abuse
- **Audit Logging** - Security event tracking

### Secure Credential Management
```bash
# Tokens stored in AWS Systems Manager Parameter Store
/lambda-execution-engine/homeassistant/token
/lambda-execution-engine/homeassistant/url

# Type: SecureString (encrypted at rest)
# Cached: 300 seconds (reduces API calls)
```

### Threat Detection
- Anomaly detection (standard/maximum tiers)
- Behavioral analysis (maximum tier)
- Circuit breaker integration
- Automatic security metrics

---

## Failsafe Mode

**The Insurance Policy:** When things go wrong, failsafe mode provides a minimal, guaranteed-to-work execution path.

### How It Works
```bash
# Enable failsafe mode (no code changes needed!)
export LEE_FAILSAFE_ENABLED=true

# Lambda automatically switches to lambda_failsafe.py
# - Minimal dependencies
# - Basic request/response
# - Maximum reliability
# - Zero extra features
```

### When to Use
- Critical bugs in main engine
- Memory pressure issues
- Testing deployment
- Emergency fallback
- Troubleshooting

### Activation
Toggle the environment variable without redeployment. The Lambda will automatically route to failsafe mode on next invocation.

---

## Home Assistant Extension

### Alexa Smart Home Integration

**Milestone:** First successful deployment with working voice control - **October 18, 2025**

#### Supported Capabilities
- **PowerController** - "Alexa, turn on kitchen light"
- **BrightnessController** - "Alexa, set bedroom to 50%"
- **ColorController** - "Alexa, make the lamp blue"
- **ColorTemperatureController** - "Alexa, set warm white"
- **ThermostatController** - "Alexa, set temperature to 72"
- **LockController** - "Alexa, lock the front door"

#### Discovery
- Automatic device discovery from Home Assistant
- Supports all Home Assistant entity types
- Proper capability mapping
- Real-time availability updates

#### Control Flow
```
Alexa Voice Command
    ↓
AWS Lambda (Alexa Skill)
    ↓
Lambda Execution Engine
    ↓
Home Assistant Extension (Facade)
    ↓
Home Assistant API
    ↓
Smart Device
```

### Feature Configuration

The Home Assistant extension supports modular feature sets via presets:

```bash
# Minimal (Core + Alexa only)
export HA_FEATURES=minimal

# Basic (Add device management)
export HA_FEATURES=basic

# Standard (Add automations & scripts) - Default
export HA_FEATURES=standard

# Full (Add notifications & conversation)
export HA_FEATURES=full

# Development (Everything including WebSocket)
export HA_FEATURES=development
```

### Setup Requirements

1. **Home Assistant Instance** (accessible from internet)
2. **Long-Lived Access Token**
3. **AWS Account** (Free Tier eligible)
4. **Alexa Developer Account** (for skill setup)

---

## Quick Start

### Prerequisites
- AWS Account
- Python 3.12
- Home Assistant instance (for HA extension)
- AWS CLI configured

### Installation

```bash
# Clone repository
git clone https://github.com/dizzybeaver/Lambda-Execution-Engine-with-Home-Assistant-Support.git
cd Lambda-Execution-Engine-with-Home-Assistant-Support/src

# Configure environment
export HOME_ASSISTANT_ENABLED=true
export HOME_ASSISTANT_URL=https://your-ha-instance.com
export USE_PARAMETER_STORE=true
export PARAMETER_PREFIX=/lambda-execution-engine

# Store Home Assistant token in SSM
aws ssm put-parameter \
    --name "/lambda-execution-engine/homeassistant/token" \
    --value "your-long-lived-access-token" \
    --type SecureString

aws ssm put-parameter \
    --name "/lambda-execution-engine/homeassistant/url" \
    --value "https://your-ha-instance.com" \
    --type String

# Deploy to Lambda
# (Package all .py files in flat structure)
zip -r lambda-package.zip *.py

aws lambda create-function \
    --function-name HomeAssistantExecutionEngine \
    --runtime python3.12 \
    --role your-lambda-execution-role \
    --handler lambda_function.lambda_handler \
    --zip-file fileb://lambda-package.zip \
    --memory-size 128 \
    --timeout 30 \
    --environment Variables="{HOME_ASSISTANT_ENABLED=true,USE_PARAMETER_STORE=true,PARAMETER_PREFIX=/lambda-execution-engine}"
```

### Testing

```bash
# Test basic Lambda
aws lambda invoke \
    --function-name HomeAssistantExecutionEngine \
    --payload '{"test": "basic"}' \
    response.json

# Test Home Assistant connection
aws lambda invoke \
    --function-name HomeAssistantExecutionEngine \
    --payload '{"operation": "ha_status"}' \
    response.json
```

---

## Configuration Tiers

Choose your performance vs resource balance:

| Tier | Memory | Metrics | Features | Best For |
|------|--------|---------|----------|----------|
| **Minimum** | ~45MB | 3 | Basic | Cost optimization |
| **Standard** | ~64MB | 6 | Balanced | Production (default) |
| **Maximum** | ~85MB | 10 | Full | Feature-rich |

```bash
# Set configuration tier
export CONFIGURATION_TIER=standard  # minimum, standard, or maximum
```

---

## Architecture Diagrams

### Overall System Flow
```
â"Œâ"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"
â"‚   Alexa Echo    â"‚
â""â"€â"€â"€â"€â"€â"€â"€â"¬â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"˜
        â"‚
        â–¼
â"Œâ"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"
â"‚  Alexa Service  â"‚
â""â"€â"€â"€â"€â"€â"€â"€â"¬â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"˜
        â"‚
        â–¼
â"Œâ"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"
â"‚      AWS Lambda (LEE)        â"‚
â"‚  â"Œâ"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"  â"‚
â"‚  â"‚  lambda_function.py  â"‚  â"‚
â"‚  â""â"€â"€â"€â"€â"€â"€â"€â"€â"€â"¬â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"˜  â"‚
â"‚           â"‚                â"‚
â"‚  â"Œâ"€â"€â"€â"€â"€â"€â"€â"€â"¼â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"  â"‚
â"‚  â"‚   gateway.py (SUGA) â"‚  â"‚
â"‚  â""â"€â"€â"€â"€â"€â"€â"€â"€â"¬â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"˜  â"‚
â"‚           â"‚                â"‚
â"‚  â"Œâ"€â"€â"€â"€â"€â"€â"€â"€â"¼â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"  â"‚
â"‚  â"‚ homeassistant_extension.py â"‚  â"‚
â"‚  â""â"€â"€â"€â"€â"€â"€â"€â"€â"¬â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"˜  â"‚
â"‚           â"‚                â"‚
â"‚  â"Œâ"€â"€â"€â"€â"€â"€â"€â"€â"¼â"€â"€â"€â"€â"€â"€â"€â"€â"€â"  â"‚
â"‚  â"‚ home_assistant/  â"‚  â"‚
â"‚  â"‚  - ha_core.py    â"‚  â"‚
â"‚  â"‚  - ha_alexa.py   â"‚  â"‚
â"‚  â"‚  - ha_features.py â"‚  â"‚
â"‚  â""â"€â"€â"€â"€â"€â"€â"€â"€â"¬â"€â"€â"€â"€â"€â"€â"€â"€â"€â"˜  â"‚
â""â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"¼â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"˜
           â"‚
           â–¼
â"Œâ"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"
â"‚   Home Assistant    â"‚
â"‚   (Your Instance)   â"‚
â""â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"€â"˜
```

### SUGA Gateway Pattern
```
Traditional (BEFORE):
module_a.py â†' http_client + logging + cache + errors
module_b.py â†' http_client + logging + cache + errors
module_c.py â†' http_client + logging + cache + errors
Result: 400KB+ duplication

SUGA (AFTER):
module_a.py â"
module_b.py â"¼â"€â†' gateway.py â†' infrastructure
module_c.py â"˜
Result: Zero duplication
```

---

## Environment Variables Reference

### Core Configuration
- `HOME_ASSISTANT_ENABLED` - Enable/disable HA extension (true/false)
- `CONFIGURATION_TIER` - Performance tier (minimum/standard/maximum)
- `DEBUG_MODE` - Enable debug logging (true/false)
- `LEE_FAILSAFE_ENABLED` - Activate failsafe mode (true/false)

### Home Assistant Specific
- `HOME_ASSISTANT_URL` - Your HA instance URL
- `HOME_ASSISTANT_TOKEN` - Long-lived access token (or use SSM)
- `HOME_ASSISTANT_VERIFY_SSL` - SSL verification (true/false)
- `HA_FEATURES` - Feature preset (minimal/basic/standard/full/development)
- `HA_WEBSOCKET_ENABLED` - Enable WebSocket connection (true/false)

### AWS Integration
- `USE_PARAMETER_STORE` - Use AWS SSM for configuration (true/false)
- `PARAMETER_PREFIX` - SSM parameter prefix (default: /lambda-execution-engine)

---

## Cost Analysis

### AWS Free Tier Coverage
- **Lambda Invocations:** 1M requests/month free
- **Lambda Compute:** 400,000 GB-seconds free
- **Systems Manager:** Parameter Store standard tier free
- **CloudWatch:** Basic monitoring included

### Estimated Monthly Costs (Beyond Free Tier)
With typical smart home usage (100 voice commands/day):
- Lambda costs: **$0.00** (well within free tier)
- SSM parameter reads: **$0.00** (300s cache reduces calls)
- CloudWatch logs: **$0.20** (minimum tier)

**Total: ~$0.20/month** or less

---

## Troubleshooting

### Home Assistant Connection Issues
```bash
# Verify token in SSM
aws ssm get-parameter --name /lambda-execution-engine/homeassistant/token --with-decryption

# Check Lambda logs
aws logs tail /aws/lambda/HomeAssistantExecutionEngine --follow

# Test HA connectivity
curl -H "Authorization: Bearer YOUR_TOKEN" https://your-ha-instance.com/api/
```

### Alexa Discovery Not Working
1. Check `HOME_ASSISTANT_ENABLED=true`
2. Verify token has proper permissions
3. Ensure devices are in supported domains (light, switch, climate, etc.)
4. Check CloudWatch logs for errors
5. Try "Alexa, discover devices" again

### Performance Issues
```bash
# Switch to minimum tier
export CONFIGURATION_TIER=minimum

# Disable WebSocket if not needed
export HA_WEBSOCKET_ENABLED=false

# Enable failsafe mode as temporary measure
export LEE_FAILSAFE_ENABLED=true
```

---

## Contributing

This project is in active beta. While we're not accepting pull requests yet, we welcome:
- Bug reports
- Feature suggestions
- Performance feedback
- Documentation improvements

Please open an issue on GitHub for any feedback.

---

## Roadmap

### Current Focus (Beta Phase)
- [ ] Stabilize Alexa integration
- [ ] Expand device capability support
- [ ] Improve error handling
- [ ] Performance optimization
- [ ] Documentation completion

### Future Enhancements
- [ ] Google Assistant support
- [ ] Enhanced automation features
- [ ] Advanced scene management
- [ ] Energy monitoring integration
- [ ] Custom dashboard support

---

## Known Limitations

### Beta Status Considerations
- Active development means occasional breaking changes
- Some edge cases may not be handled
- Documentation is evolving
- Performance tuning ongoing

### Technical Constraints
- 128MB Lambda memory limit (by design for Free Tier)
- Single-threaded execution (Lambda constraint)
- No local state persistence (serverless architecture)
- Cold start latency (~800-1200ms first invocation)

### Home Assistant Specific
- Requires internet-accessible HA instance
- WebSocket support is outbound only
- Some entity types may not map perfectly to Alexa capabilities
- Long-running operations may timeout

---

## FAQ

**Q: Why AWS Lambda instead of running on Home Assistant directly?**
A: Separation of concerns - Alexa skill backend must be hosted on AWS. This architecture provides professional-grade reliability, scalability, and integrates seamlessly with AWS services.

**Q: What about cold starts?**
A: First invocation: 800-1200ms. Subsequent: <200ms. For voice control, users don't notice cold starts. Consider provisioned concurrency if needed.

**Q: Can I use this without Home Assistant?**
A: The Lambda Execution Engine works standalone. Simply set `HOME_ASSISTANT_ENABLED=false` and the HA extension is completely removed from execution.

**Q: Is this production-ready?**
A: The core Lambda engine is production-ready. The Home Assistant extension is in beta - working and functional, but expect refinements.

**Q: How do I update to newer versions?**
A: Currently manual deployment. Watch the repository for updates. Future: automated deployment scripts.

**Q: What happens if Home Assistant is down?**
A: Circuit breaker detects failures and stops attempting connection. Alexa receives error responses. No Lambda crashes or cascading failures.

---

## License

Copyright 2025 Joseph Hersey

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

---

## Acknowledgments

Built with innovative architectural patterns:
- **SUGA** - Single Universal Gateway Architecture
- **ISP** - Network-inspired interface isolation
- **Pure Delegation Facade** - Extension architecture pattern

Powered by:
- AWS Lambda (Python 3.12)
- Home Assistant
- Amazon Alexa Smart Home API
- AWS Systems Manager Parameter Store

---

## Support

- **GitHub Issues:** [Report bugs or request features](https://github.com/dizzybeaver/Lambda-Execution-Engine-with-Home-Assistant-Support/issues)
- **Documentation:** See `/docs` folder (coming soon)
- **Discussions:** GitHub Discussions (coming soon)

---

**Made with** ❤️ **for the smart home community**

**Status:** Beta - Working and improving daily!

**Latest Milestone:** Home Assistant + Alexa voice control successfully deployed October 18, 2025
