config.py - Pure SUGA Interface
Purpose: Thin wrapper - routes ALL calls to gateway

Pattern (ALL functions follow this):

def config_get_parameter(key: str, default: Any = None) -> Any:
    """Get configuration parameter."""
    from gateway import execute_operation, GatewayInterface
    return execute_operation(
        GatewayInterface.CONFIG,
        'get_parameter',
        key=key,
        default=default
    )
Function Categories:

Core Operations (7 functions)

config_initialize()
config_get_parameter()
config_set_parameter()
config_get_category()
config_reload()
config_switch_preset()
config_get_state()
Source Operations (5 functions)

config_load_from_environment()
config_load_from_file()
config_load_ha_config()
config_validate_ha_config()
config_validate_all()
Category Helpers (10 wrappers)

config_get_cache() → config_get_category('cache')
config_get_logging() → config_get_category('logging')
... all categories
Backward Compatibility (7 aliases)

get_parameter() → config_get_parameter()
set_parameter() → config_set_parameter()
... all legacy names
Legacy Helpers (11 from config_helpers.py)

get_cache_config(key, default)
get_logging_config(key, default)
... all specific helpers
Total: ~40 functions, ALL gateway-routed
