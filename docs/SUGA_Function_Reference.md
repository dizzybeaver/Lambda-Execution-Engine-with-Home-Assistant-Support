# SUGA Function Reference

## Config Gateway Interface Architecture

```
┌─────────────────────────────────────────────┐
│  APPLICATION CODE                           │
│  (imports from config.py)                   │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│  config.py (THIN SUGA INTERFACE)            │
│  - All functions call gateway only          │
│  - NO business logic                        │
│  - 100% gateway.execute_operation() calls   │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│  gateway.py (CENTRAL ROUTER)                │
│  GatewayInterface.CONFIG routing            │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│  config_core.py (SINGLE IMPLEMENTATION)     │
│  ConfigurationCore class with:              │
│  - Environment loading                      │
│  - File loading                             │
│  - Parameter Store                          │
│  - HA configuration                         │
│  - Validation                               │
│  - Hot-reload                               │
│  - Preset management                        │
│  - User overrides                           │
└─────────────────────────────────────────────┘
```

---

## config.py - Config Gateway Interface File

**Purpose:** Thin wrapper - routes ALL calls to gateway

**Pattern (ALL functions follow this):**
```python
def config_get_parameter(key: str, default: Any = None) -> Any:
    """Get configuration parameter."""
    from gateway import execute_operation, GatewayInterface
    return execute_operation(
        GatewayInterface.CONFIG,
        'get_parameter',
        key=key,
        default=default
    )
```

**Function Categories:**
1. **Core Operations** (7 functions)
   - config_initialize()
   - config_get_parameter()
   - config_set_parameter()
   - config_get_category()
   - config_reload()
   - config_switch_preset()
   - config_get_state()

2. **Source Operations** (5 functions)
   - config_load_from_environment()
   - config_load_from_file()
   - config_load_ha_config()
   - config_validate_ha_config()
   - config_validate_all()

3. **Category Helpers** (10 wrappers)
   - config_get_cache() → config_get_category('cache')
   - config_get_logging() → config_get_category('logging')
   - ... all categories

4. **Backward Compatibility** (7 aliases)
   - get_parameter() → config_get_parameter()
   - set_parameter() → config_set_parameter()
   - ... all legacy names

5. **Legacy Helpers** (11 from config_helpers.py)
   - get_cache_config(key, default)
   - get_logging_config(key, default)
   - ... all specific helpers

**Total:** ~40 functions, ALL gateway-routed

---

## config_core.py - Config Consolidated Function Implementation - Private functions of Config Gateway Interface - Not for External use

**Purpose:** Single source of truth for ALL configuration logic

**Structure:**
```python
class ConfigurationState:
    """Track configuration state"""
    current_version: str = "1.0.0"
    last_reload_time: float = 0.0
    active_tier: ConfigurationTier = ConfigurationTier.STANDARD
    active_preset: Optional[str] = None
    reload_count: int = 0

class ConfigurationValidator:
    """Validate configuration sections"""
    def validate_ha_config() -> Dict
    def validate_all_sections() -> Dict

class ConfigurationCore:
    """Complete configuration system"""
    
    # INITIALIZATION (from config_manager)
    def initialize() -> Dict[str, Any]
    
    # LOADING (from config_loader)
    def load_from_environment() -> Dict[str, Any]
    def load_from_file(filepath: str) -> Dict[str, Any]
    def get_parameter(key: str, default: Any) -> Any
    def set_parameter(key: str, value: Any) -> bool
    
    # HA CONFIG (from ha_config)
    def load_ha_config() -> Dict[str, Any]
    def validate_ha_config(config: Dict) -> Dict[str, Any]
    
    # USER OVERRIDES (from user_config integration)
    def apply_user_overrides(base_config: Dict) -> Dict
    
    # PRESETS (from config_extensions)
    def switch_preset(preset_name: str) -> Dict[str, Any]
    
    # HOT-RELOAD (from config_extensions)
    def reload_config(validate: bool) -> Dict[str, Any]
    
    # VALIDATION (from config_manager)
    def validate_all_sections() -> Dict[str, Any]
    
    # ACCESS
    def get_category_config(category: str) -> Dict[str, Any]
    def get_state() -> Dict[str, Any]

# Gateway Implementation Functions
def _initialize_implementation() -> Dict[str, Any]
def _get_parameter_implementation(key, default) -> Any
def _set_parameter_implementation(key, value) -> bool
def _get_category_implementation(category) -> Dict[str, Any]
def _reload_implementation(validate) -> Dict[str, Any]
def _switch_preset_implementation(preset) -> Dict[str, Any]
def _get_state_implementation() -> Dict[str, Any]
def _load_environment_implementation() -> Dict[str, Any]
def _load_file_implementation(filepath) -> Dict[str, Any]
def _load_ha_config_implementation() -> Dict[str, Any]
def _validate_ha_config_implementation(config) -> Dict[str, Any]
def _validate_all_implementation() -> Dict[str, Any]
```

---
