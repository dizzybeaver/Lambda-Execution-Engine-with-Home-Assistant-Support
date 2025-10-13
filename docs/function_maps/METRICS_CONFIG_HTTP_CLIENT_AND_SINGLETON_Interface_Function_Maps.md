# METRICS, CONFIG, HTTP_CLIENT & SINGLETON Interface Function Maps

---

# 1. METRICS Interface Function Map
**Interface:** GatewayInterface.METRICS  
**Category:** Observability & Monitoring  
**Core File:** metrics_core.py

## Call Hierarchy

```
gateway.execute_operation(GatewayInterface.METRICS, operation)
    ├─→ gateway.record_metric(name, value, dimensions)
    └─→ gateway.increment_counter(name, value)
            ↓
    ├─→ _execute_record_metric_implementation()
    ├─→ _execute_increment_counter_implementation()
    └─→ _execute_get_stats_implementation()
            ↓
    _MANAGER.execute_metric_operation(MetricOperation, ...)
            ↓
    ├─→ MetricsCore.record_metric()
    ├─→ MetricsCore.increment_counter()
    ├─→ MetricsCore.get_metric()
    ├─→ MetricsCore.get_stats()
    └─→ MetricsCore.clear_metrics()
```

## Key Functions

### Gateway Functions
- **record_metric(name, value, dimensions)** - Record metric with dimensions
  - Map: `gateway → execute_operation → _execute_record_metric_implementation → _MANAGER.record_metric()`
  - Category: Observability - Metric Recording

- **increment_counter(name, value)** - Increment counter metric
  - Map: `gateway → execute_operation → _execute_increment_counter_implementation → _MANAGER.increment_counter()`
  - Category: Observability - Counter Tracking

### Core Class: MetricsCore

- **record_metric(name, value, dimensions)** - Store metric with metadata
  - Sub-functions: `_build_metric_key()`, update `_metrics` dict, update stats
  - Category: Metric Storage

- **increment_counter(name, value)** - Increment counter by value
  - Sub-functions: Get current count, add value, store in `_counters`
  - Category: Counter Management

- **get_metric(name)** - Retrieve specific metric
  - Returns: Dict with metric data or None
  - Category: Metric Retrieval

- **get_stats()** - Get metrics statistics
  - Returns: Total metrics, unique keys, counters, gauges, histograms counts
  - Category: Statistics

- **clear_metrics()** - Clear all metrics
  - Clears: `_metrics`, `_counters`, `_gauges`, `_histograms`, resets stats
  - Category: Maintenance

- **_build_metric_key(name, dimensions)** - Build unique key with dimensions
  - Format: `name[dim1=val1,dim2=val2]`
  - Category: Key Generation - Internal

### Enums
- **MetricOperation**: RECORD, INCREMENT, GET_STATS, CLEAR
- **MetricType**: COUNTER, GAUGE, HISTOGRAM

---

# 2. CONFIG Interface Function Map
**Interface:** GatewayInterface.CONFIG  
**Category:** Configuration Management  
**Core Files:** config_core.py, config.py, variables.py, variables_utils.py

## Call Hierarchy

```
gateway.execute_operation(GatewayInterface.CONFIG, operation)
    └─→ gateway.get_parameter(key, default) / set_parameter() / get_category_config()
            ↓
    ├─→ _initialize_implementation()
    ├─→ _get_parameter_implementation()
    ├─→ _set_parameter_implementation()
    ├─→ _get_category_implementation()
    ├─→ _reload_implementation()
    ├─→ _switch_preset_implementation()
    └─→ _get_state_implementation()
            ↓
    _config_core (ConfigurationCore singleton)
            ↓
    ├─→ ConfigurationCore.initialize()
    ├─→ ConfigurationCore.get_parameter()
    ├─→ ConfigurationCore.set_parameter()
    ├─→ ConfigurationCore.get_category_config()
    ├─→ ConfigurationCore.reload_config()
    ├─→ ConfigurationCore.switch_preset()
    ├─→ ConfigurationCore.load_from_environment()
    ├─→ ConfigurationCore.load_from_file()
    └─→ ConfigurationCore.validate_all_sections()
```

## Key Functions

### Gateway Functions (config.py wrapper)
- **config_get_parameter(key, default)** - Get config value
- **config_set_parameter(key, value)** - Set config value
- **config_get_category(category)** - Get category config
- **config_reload(validate)** - Reload configuration
- **config_switch_preset(preset_name)** - Switch config preset

### Core Class: ConfigurationCore

- **initialize()** - Initialize config system
  - Sub-functions: `load_from_environment()`, apply defaults, create state
  - Category: System Lifecycle

- **get_parameter(key, default)** - Get config parameter
  - Sub-functions: Check cache first (`cache_get`), fallback to `_config` dict
  - Category: Configuration Retrieval

- **set_parameter(key, value)** - Set config parameter
  - Sub-functions: Lock, update `_config`, cache invalidation
  - Category: Configuration Update

- **get_category_config(category)** - Get category configuration
  - Sub-functions: `cache_get()` → if miss → fetch from `_config` → `cache_set()`
  - Category: Category Access

- **reload_config(validate)** - Reload all configuration
  - Sub-functions: `load_from_environment()`, `apply_user_overrides()`, `validate_all_sections()`, `cache_delete()`
  - Updates: `_state.reload_count`, `_state.version_history`
  - Category: Configuration Management

- **switch_preset(preset_name)** - Switch to config preset
  - Sub-functions: Load preset from `CONFIGURATION_PRESETS`, apply, validate
  - Category: Preset Management

- **load_from_environment()** - Load from environment variables
  - Sub-functions: Read env vars, parse values, build config dict
  - Category: External Source Loading

- **validate_all_sections()** - Validate entire configuration
  - Sub-functions: Delegate to `_validator.validate_all_sections()`
  - Category: Validation

### Supporting Files

**variables.py** - Configuration data structures
- `ConfigurationTier` enum: MINIMUM, STANDARD, MAXIMUM, USER
- `InterfaceType` enum: All interface types
- Config dicts: `CACHE_INTERFACE_CONFIG`, `LOGGING_INTERFACE_CONFIG`, etc.

**variables_utils.py** - Configuration utilities
- `estimate_cache_memory_usage(tier)` - Calculate memory
- `validate_override_combination(tier, overrides)` - Validate config
- `get_full_system_configuration(tier, overrides)` - Build complete config

---

# 3. HTTP_CLIENT Interface Function Map
**Interface:** GatewayInterface.HTTP_CLIENT  
**Category:** Network Communication  
**Core File:** http_client_core.py

## Call Hierarchy

```
gateway.execute_operation(GatewayInterface.HTTP_CLIENT, operation)
    ├─→ gateway.make_request(method, url, **kwargs)
    ├─→ gateway.make_get_request(url, **kwargs)
    └─→ gateway.make_post_request(url, data, **kwargs)
            ↓
    ├─→ _make_request_implementation()
    ├─→ _make_get_request_implementation()
    └─→ _make_post_request_implementation()
            ↓
    get_http_client() → HTTPClientCore singleton
            ↓
    ├─→ HTTPClientCore.make_request()
    ├─→ HTTPClientCore.get()
    ├─→ HTTPClientCore.post()
    ├─→ HTTPClientCore.put()
    ├─→ HTTPClientCore.delete()
    └─→ HTTPClientCore.get_stats()
```

## Key Functions

### Gateway Functions
- **make_request(method, url, **kwargs)** - Generic HTTP request
- **make_get_request(url, **kwargs)** - HTTP GET
- **make_post_request(url, data, **kwargs)** - HTTP POST

### Core Class: HTTPClientCore

- **make_request(method, url, **kwargs)** - Execute HTTP request
  - Parameters: method, url, data, headers, timeout
  - Sub-functions:
    - Build request with headers
    - Execute with `urlopen()`
    - Parse response
    - Update stats (requests, successful, failed)
  - Category: Network-HTTP

- **get(url, **kwargs)** - HTTP GET request
  - Map: `get() → make_request('GET', url, **kwargs)`
  - Category: Network-HTTP

- **post(url, data, **kwargs)** - HTTP POST request
  - Map: `post() → make_request('POST', url, data=data, **kwargs)`
  - Category: Network-HTTP

- **put(url, data, **kwargs)** - HTTP PUT request
  - Map: `put() → make_request('PUT', url, data=data, **kwargs)`
  - Category: Network-HTTP

- **delete(url, **kwargs)** - HTTP DELETE request
  - Map: `delete() → make_request('DELETE', url, **kwargs)`
  - Category: Network-HTTP

- **get_stats()** - Get HTTP client statistics
  - Returns: total_requests, successful, failed, retries, success_rate
  - Category: Observability

### Module Function
- **get_http_client()** - Get singleton HTTP client
  - Category: Singleton Access
  - Returns: Global `_http_client_instance`

---

# 4. SINGLETON Interface Function Map
**Interface:** GatewayInterface.SINGLETON  
**Category:** Memory Management  
**Core File:** singleton_core.py

## Call Hierarchy

```
gateway.execute_operation(GatewayInterface.SINGLETON, operation)
    ├─→ gateway.get_singleton(name)
    └─→ gateway.register_singleton(name, instance)
            ↓
    ├─→ _execute_get_implementation()
    ├─→ _execute_set_implementation()
    ├─→ _execute_reset_implementation()
    ├─→ _execute_reset_all_implementation()
    └─→ _execute_exists_implementation()
            ↓
    execute_singleton_operation(SingletonOperation, ...)
            ↓
    _SINGLETON_MANAGER (SingletonCore)
            ↓
    ├─→ SingletonCore.get()
    ├─→ SingletonCore.set()
    ├─→ SingletonCore.reset()
    ├─→ SingletonCore.reset_all()
    └─→ SingletonCore.exists()
```

## Key Functions

### Gateway Functions
- **get_singleton(name)** - Get singleton instance
- **register_singleton(name, instance)** - Register singleton

### Generic Operation Dispatcher
- **execute_singleton_operation(operation, *args, **kwargs)** - Universal dispatcher
  - Map: `execute_singleton_operation() → getattr(_SINGLETON_MANAGER, operation.value)()`
  - Uses dynamic method lookup via enum value
  - Category: Generic Dispatch Pattern

### Core Class: SingletonCore

- **get(name, factory_func, **kwargs)** - Get or create singleton
  - Sub-functions:
    - Check `_instances` dict
    - If not found and factory provided: `factory_func()` to create
    - Store in `_instances`
    - Thread-safe with `self._lock`
  - Category: Singleton Access

- **set(name, instance, **kwargs)** - Set singleton instance
  - Sub-functions: Lock, store in `_instances`
  - Category: Singleton Registration

- **reset(name, **kwargs)** - Delete specific singleton
  - Sub-functions: Lock, `del _instances[name]`
  - Returns: bool
  - Category: Singleton Lifecycle

- **reset_all(**kwargs)** - Clear all singletons
  - Sub-functions: Lock, `_instances.clear()`
  - Category: Singleton Lifecycle

- **exists(name)** - Check if singleton exists
  - Returns: bool
  - Category: Singleton Query

### Enums
- **SingletonOperation**: GET, SET, RESET, RESET_ALL, EXISTS

---

**End of METRICS, CONFIG, HTTP_CLIENT & SINGLETON Function Maps**
