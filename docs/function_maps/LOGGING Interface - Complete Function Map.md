# LOGGING Interface - Complete Function Map
**Interface:** GatewayInterface.LOGGING  
**Category:** Observability & Monitoring  
**Core File:** logging_core.py

---

## Call Hierarchy Map

```
gateway.execute_operation(GatewayInterface.LOGGING, operation)
    ├─→ gateway.log_info(message, extra)          [Gateway Function]
    ├─→ gateway.log_error(message, error, extra)  [Gateway Function]
    ├─→ gateway.log_warning(message, error, extra)[Gateway Function]
    └─→ gateway.log_debug(message, error, extra)  [Gateway Function]
            ↓
    [Routes to logging_core Gateway Implementations]
            ↓
    ├─→ _execute_log_info_implementation(message, extra)
    ├─→ _execute_log_error_implementation(message, error, extra)
    ├─→ _execute_log_warning_implementation(message, extra)
    └─→ _execute_log_debug_implementation(message, extra)
            ↓
    [Delegates to Singleton Logging Manager]
            ↓
    _MANAGER.execute_log_operation(LogOperation, message, error, extra)
            ↓
    LoggingCore methods
            ↓
    ├─→ LoggingCore.log_info()
    ├─→ LoggingCore.log_error()
    ├─→ LoggingCore.log_warning()
    ├─→ LoggingCore.log_debug()
    ├─→ LoggingCore.log_operation_start()
    ├─→ LoggingCore.log_operation_success()
    ├─→ LoggingCore.log_template_fast()
    └─→ LoggingCore.get_stats()
```

---

## File: gateway.py
**Functions:** 4 gateway convenience wrappers

### log_info(message: str, extra: Optional[Dict], **kwargs)
- **Category:** Gateway Function - Observability
- **Map:** `User → gateway.log_info() → execute_operation(LOGGING, 'log_info') → _execute_log_info_implementation() → _MANAGER.execute_log_operation()`
- **Description:** Log informational message with metadata
- **Parameters:** Merges extra dict with kwargs for enriched logging

### log_error(message: str, error: Optional[Exception], extra: Optional[Dict], **kwargs)
- **Category:** Gateway Function - Observability
- **Map:** `User → gateway.log_error() → execute_operation(LOGGING, 'log_error') → _execute_log_error_implementation() → _MANAGER.execute_log_operation()`
- **Description:** Log error message with exception details
- **Parameters:** Includes exc_info for stack traces

### log_warning(message: str, error: Optional[Exception], extra: Optional[Dict], **kwargs)
- **Category:** Gateway Function - Observability
- **Map:** `User → gateway.log_warning() → execute_operation(LOGGING, 'log_warning') → _execute_log_warning_implementation() → _MANAGER.execute_log_operation()`
- **Description:** Log warning message

### log_debug(message: str, error: Optional[Exception], extra: Optional[Dict], **kwargs)
- **Category:** Gateway Function - Observability
- **Map:** `User → gateway.log_debug() → execute_operation(LOGGING, 'log_debug') → _execute_log_debug_implementation() → _MANAGER.execute_log_operation()`
- **Description:** Log debug message for development

---

## File: logging_core.py

### Gateway Implementation Functions (4)

#### _execute_log_info_implementation(message, extra)
- **Category:** Gateway Implementation - Observability
- **Map:** `execute_operation() → _execute_log_info_implementation() → _MANAGER.execute_log_operation(LogOperation.LOG_INFO)`
- **Description:** Gateway implementation for info logging
- **Private:** Yes

#### _execute_log_error_implementation(message, error, extra)
- **Category:** Gateway Implementation - Observability
- **Map:** `execute_operation() → _execute_log_error_implementation() → _MANAGER.execute_log_operation(LogOperation.LOG_ERROR)`
- **Description:** Gateway implementation for error logging with exception handling
- **Private:** Yes

#### _execute_log_warning_implementation(message, extra)
- **Category:** Gateway Implementation - Observability
- **Map:** `execute_operation() → _execute_log_warning_implementation() → _MANAGER.execute_log_operation(LogOperation.LOG_WARNING)`
- **Description:** Gateway implementation for warning logging
- **Private:** Yes

#### _execute_log_debug_implementation(message, extra)
- **Category:** Gateway Implementation - Observability
- **Map:** `execute_operation() → _execute_log_debug_implementation() → _MANAGER.execute_log_operation(LogOperation.LOG_DEBUG)`
- **Description:** Gateway implementation for debug logging
- **Private:** Yes

---

### Public Interface Functions (2)

#### log_template_fast(template: LogTemplate, *args, level: int)
- **Category:** Public Function - Performance Optimization
- **Map:** `Direct call → _MANAGER.log_template_fast()`
- **Description:** Ultra-fast template-based logging using pre-compiled format strings
- **Public:** Yes

#### get_logging_stats()
- **Category:** Public Function - Observability
- **Map:** `Direct call → _MANAGER.get_stats()`
- **Description:** Get logging performance statistics
- **Public:** Yes

---

### Core Class: LoggingCore

#### Constructor: __init__()
- **Category:** Initialization - Observability
- **Description:** Initialize logger and statistics
- **Initializes:**
  - `self.logger` - Standard Python logger
  - `self._stats` - Dict tracking log counts by level

#### execute_log_operation(operation: LogOperation, message, error, extra)
- **Category:** Generic Operation Dispatch - Observability
- **Map:** `execute_log_operation() → getattr(operation.value) → log_info/error/warning/debug()`
- **Description:** Universal log operation dispatcher using LogOperation enum
- **Sub-functions:**
  - Dynamically calls appropriate log method based on operation enum
  - Handles exceptions by falling back to basic logger

#### log_info(message, extra)
- **Category:** Core Operation - Observability
- **Map:** `log_info() → self.logger.info() → update _stats`
- **Description:** Log info message to Python logger
- **Sub-functions:**
  - `self.logger.info(message, extra=extra or {})`
  - Increments `self._stats['info_count']`

#### log_error(message, error, extra)
- **Category:** Core Operation - Observability
- **Map:** `log_error() → self.logger.error() → update _stats`
- **Description:** Log error with optional exception and stack trace
- **Sub-functions:**
  - If error provided: `self.logger.error(f"{message}: {str(error)}", exc_info=True)`
  - Else: `self.logger.error(message, extra=extra or {})`
  - Increments `self._stats['error_count']`

#### log_warning(message, extra)
- **Category:** Core Operation - Observability
- **Map:** `log_warning() → self.logger.warning() → update _stats`
- **Description:** Log warning message
- **Sub-functions:**
  - `self.logger.warning(message, extra=extra or {})`
  - Increments `self._stats['warning_count']`

#### log_debug(message, extra)
- **Category:** Core Operation - Observability
- **Map:** `log_debug() → self.logger.debug() → update _stats`
- **Description:** Log debug message
- **Sub-functions:**
  - `self.logger.debug(message, extra=extra or {})`
  - Increments `self._stats['debug_count']`

#### log_operation_start(operation, correlation_id)
- **Category:** Structured Logging - Observability
- **Map:** `log_operation_start() → [check USE_LOG_TEMPLATES] → logger.info() → update _stats`
- **Description:** Log operation start with correlation ID
- **Sub-functions:**
  - If templates enabled: Uses `_OPERATION_START_LOG % (operation, correlation_id)`
  - Else: Standard format string
  - Increments `self._stats['info_count']`
  - Increments `self._stats['template_usage']` if template used

#### log_operation_success(operation, duration_ms)
- **Category:** Structured Logging - Performance Tracking
- **Map:** `log_operation_success() → [check USE_LOG_TEMPLATES] → logger.info() → update _stats`
- **Description:** Log operation completion with duration
- **Sub-functions:**
  - If templates enabled: Uses `_OPERATION_SUCCESS_LOG % (operation, duration_ms)`
  - Else: Standard format string
  - Increments `self._stats['info_count']`
  - Increments `self._stats['template_usage']` if template used

#### log_template_fast(template: LogTemplate, *args, level)
- **Category:** Performance Optimization - Template Logging
- **Map:** `log_template_fast() → [lookup template] → logger.log(level, formatted) → update _stats`
- **Description:** Ultra-fast logging using pre-compiled format strings
- **Template Mapping:**
  - `CACHE_HIT` → `_CACHE_HIT_LOG`
  - `CACHE_MISS` → `_CACHE_MISS_LOG`
  - `HA_SUCCESS` → `_HA_SUCCESS_LOG`
  - `HA_ERROR` → `_HA_ERROR_LOG`
  - `HTTP_REQUEST` → `_HTTP_REQUEST_LOG`
  - `HTTP_SUCCESS` → `_HTTP_SUCCESS_LOG`
  - `OPERATION_START` → `_OPERATION_START_LOG`
  - `OPERATION_SUCCESS` → `_OPERATION_SUCCESS_LOG`
  - `LAMBDA_START` → `_LAMBDA_START_LOG`
  - `METRIC_RECORD` → `_METRIC_RECORD_LOG`
  - `MODULE_LOAD` → `_MODULE_LOAD_LOG`
  - `MODULE_UNLOAD` → `_MODULE_UNLOAD_LOG`
  - `CIRCUIT_OPEN` → `_CIRCUIT_OPEN_LOG`
  - `CIRCUIT_CLOSE` → `_CIRCUIT_CLOSE_LOG`
- **Sub-functions:**
  - String formatting using `%` operator for performance
  - Direct logger call: `self.logger.log(level, formatted_message)`
  - Increments `self._stats['template_usage']`

#### get_stats()
- **Category:** Observability - Statistics
- **Map:** `get_stats() → return _stats dict`
- **Description:** Get logging statistics
- **Returns:** Dict with counts for info, error, warning, debug, template usage

---

## Enums

### LogOperation
- **LOG_INFO** = "log_info"
- **LOG_ERROR** = "log_error"
- **LOG_WARNING** = "log_warning"
- **LOG_DEBUG** = "log_debug"
- **LOG_START** = "log_operation_start"
- **LOG_SUCCESS** = "log_operation_success"
- **LOG_TEMPLATE** = "log_template"

### LogTemplate
Pre-defined log message templates for performance:
- **CACHE_HIT** - "Cache hit: %s (access_count=%d)"
- **CACHE_MISS** - "Cache miss: %s"
- **HA_SUCCESS** - "HA operation success: %s (%.2fms)"
- **HA_ERROR** - "HA operation failed: %s - %s"
- **HTTP_REQUEST** - "HTTP %s %s"
- **HTTP_SUCCESS** - "HTTP success: %d (%.2fms)"
- **OPERATION_START** - "Operation started: %s [%s]"
- **OPERATION_SUCCESS** - "Operation completed: %s (%.2fms)"
- **LAMBDA_START** - "Lambda invocation started [%s]"
- **METRIC_RECORD** - "Metric recorded: %s = %.2f"
- **MODULE_LOAD** - "Module loaded: %s (%.2fms)"
- **MODULE_UNLOAD** - "Module unloaded: %s"
- **CIRCUIT_OPEN** - "Circuit breaker opened: %s"
- **CIRCUIT_CLOSE** - "Circuit breaker closed: %s"

---

## Module Variables

### _MANAGER
- **Type:** LoggingCore
- **Category:** Singleton Instance
- **Description:** Global logging manager
- **Initialization:** `_MANAGER = LoggingCore()`

### _USE_LOG_TEMPLATES
- **Type:** bool
- **Category:** Configuration
- **Description:** Enable/disable template-based logging
- **Source:** `os.environ.get('USE_LOG_TEMPLATES', 'true').lower() == 'true'`

### Template Constants
All template strings stored as module-level constants (14 total) for ultra-fast string formatting using `%` operator instead of f-strings.

---

## Function Categories Summary

### Observability (Primary)
- All log_info/error/warning/debug operations
- Structured logging with correlation IDs
- Exception tracking with stack traces

### Performance Optimization
- Template-based logging (`log_template_fast()`)
- Pre-compiled format strings
- `%` operator formatting (faster than f-strings)

### Statistics Tracking
- Count by log level
- Template usage tracking
- Performance metrics

### Structured Logging
- Operation lifecycle logging (start/success)
- Correlation ID integration
- Metadata enrichment via extra dict

---

## Usage Examples

### Basic Logging
```python
from gateway import log_info, log_error

log_info("User logged in", extra={'user_id': 123})
log_error("Database error", error=exc, extra={'query': 'SELECT'})
```

### Template Logging (High Performance)
```python
from logging_core import log_template_fast, LogTemplate
import logging

# Ultra-fast cache hit logging
log_template_fast(LogTemplate.CACHE_HIT, "user:123", 5, level=logging.INFO)
# Result: "Cache hit: user:123 (access_count=5)"
```

### Operation Tracking
```python
from logging_core import _MANAGER

correlation_id = "abc-123"
_MANAGER.log_operation_start("process_request", correlation_id)
# ... do work ...
_MANAGER.log_operation_success("process_request", 45.2)
```

---

**End of LOGGING Interface Function Map**
