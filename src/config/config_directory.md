# config/ Directory

**Version:** 2025-12-09_1  
**Purpose:** Configuration module directory structure  
**Module:** config

---

## Directory Structure

```
config/
├── __init__.py                  # Public API exports
├── config_core.py               # Core configuration class & singleton
├── config_parameters.py         # Parameter get/set operations
├── config_loader.py             # Load from environment/file
├── config_presets.py            # Configuration presets
├── config_state.py              # State management dataclasses
├── config_validator.py          # Validation logic
└── DIRECTORY.md                 # This file
```

---

## File Descriptions

### __init__.py (56 lines)
**Purpose:** Public API exports  
**Exports:** All public functions from config module  
**Pattern:** Import and re-export pattern

### config_core.py (140 lines)
**Purpose:** Core configuration management  
**Key Components:**
- `ConfigurationCore` class
- `get_config_manager()` singleton
- Rate limiting (1000 ops/sec)
- Statistics tracking

**Debug Integration:**
- `gateway.debug_log()` for operations
- `gateway.debug_timing()` for timing
- CONFIG scope flags

### config_parameters.py (180 lines)
**Purpose:** Parameter operations with SSM-first priority  
**Key Functions:**
- `initialize_config()` - Initialize system
- `get_parameter()` - Get with SSM-first
- `set_parameter()` - Set parameter
- `get_category_config()` - Get category
- `get_state()` - Get current state

**Priority Order:**
1. SSM Parameter Store (if enabled)
2. Environment variable
3. Default value

### config_loader.py (130 lines)
**Purpose:** Load configuration from sources  
**Key Functions:**
- `load_from_environment()` - Load env vars
- `load_from_file()` - Load from file (JSON or key=value)
- `reload_config()` - Reload with validation
- `merge_configs()` - Merge two configs

### config_presets.py (150 lines)
**Purpose:** Configuration preset management  
**Key Functions:**
- `switch_preset()` - Switch to preset
- `get_preset_list()` - List available presets
- `get_preset_config()` - Get preset config

**Presets:**
- minimal - Minimal resource usage
- standard - Standard production
- debug - Debug mode verbose
- performance - Performance optimized

### config_state.py (35 lines)
**Purpose:** State management dataclasses  
**Key Components:**
- `ConfigurationVersion` - Version history
- `ConfigurationState` - Current state tracking

### config_validator.py (140 lines)
**Purpose:** Configuration validation  
**Key Components:**
- `ConfigurationValidator` class
- `validate_parameter()` - Single param
- `validate_section()` - Section validation
- `validate_all_sections()` - Full validation

---

## Import Patterns

### Public API (from other modules)
```python
import config

# Initialize
config.initialize_config()

# Get/set parameters
value = config.get_parameter('key', 'default')
config.set_parameter('key', value)

# State and presets
state = config.get_state()
config.switch_preset('standard')
```

### Internal (within config module)
```python
from config.config_core import get_config_manager
from config.config_parameters import get_parameter
```

---

## Debug Integration

All config operations support hierarchical debug control:

### Environment Variables
```bash
DEBUG_MODE=true                  # Master switch
CONFIG_DEBUG_MODE=true           # Config debug logging
CONFIG_DEBUG_TIMING=true         # Config timing measurements
```

### Debug Output
```python
# Debug logging
gateway.debug_log("CONFIG", "CONFIG", "Getting parameter", key=key)

# Timing context
with gateway.debug_timing("CONFIG", "CONFIG", "operation"):
    # operation code
```

---

## Interface Integration

### Interface Router
**Location:** `interfaces/interface_config.py`  
**Pattern:** Dispatch dictionary with validation  
**Operations:** 12 operations supported

### Gateway Wrappers
**Location:** `gateway/wrappers/gateway_wrappers_config.py`  
**Pattern:** Thin wrappers calling execute_operation()  
**Functions:** Standardized + legacy aliases

---

## Architecture Compliance

### SUGA Pattern
- ✅ Gateway → Interface → Core flow
- ✅ Lazy imports in gateway wrappers
- ✅ No direct core imports from outside module
- ✅ Singleton pattern via gateway

### File Standards
- ✅ All files ≤350 lines
- ✅ 5-line headers
- ✅ No threading primitives
- ✅ Debug integration throughout

### Performance
- Rate limiting: 1000 ops/sec
- SSM-first priority for parameters
- Cache validation
- Statistics tracking

---

## Testing

### Unit Tests
Test each module component:
- config_core: Singleton, rate limiting
- config_parameters: Get/set, SSM priority
- config_loader: Load sources, reload
- config_presets: Switch, list presets
- config_validator: Validation logic

### Integration Tests
Test via gateway:
```python
import gateway

# Initialize
result = gateway.config_initialize()

# Parameter operations
value = gateway.config_get_parameter('key', 'default')
gateway.config_set_parameter('key', value)

# State
state = gateway.config_get_state()
```

---

## Migration Notes

### From Old Structure
Old files consolidated into new structure:
- `config_core.py` → Split into multiple files
- `interface_config.py` → Moved to interfaces/
- `gateway_wrappers_config.py` → Moved to gateway/wrappers/

### Import Updates
```python
# Old
from config_core import get_config_manager

# New (public API)
import config
manager = config.get_config_manager()

# New (internal only)
from config.config_core import get_config_manager
```

---

## Related Documentation

**SIMA Knowledge:**
- SUGA Architecture: `/sima/shared/SUGA-Architecture.md`
- File Standards: `/sima/shared/File-Standards.md`
- Debug System: `/sima/entries/interfaces/INT-14-Debug-Interface.md`

**Project Knowledge:**
- Config Interface: `/sima/projects/LEE/nmp01/NMP01-LEE-06-Config-Interface.md`
- Gateway Pattern: `/sima/entries/gateways/GATE-01_Gateway-Layer-Structure.md`

---

**END OF DIRECTORY LISTING**
