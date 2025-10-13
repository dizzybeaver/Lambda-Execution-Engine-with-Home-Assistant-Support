# DEBUG & TEST Files Function Maps
**Files:** debug_aws.py, ha_tests.py  
**Category:** Testing & Diagnostics

---

# 1. debug_aws.py - AWS Testing Program

## Call Hierarchy

```
CLI Entry / Lambda Handler
    ↓
AWSTestProgram.run_program(args)
    ↓
├─→ parse_arguments(args)
├─→ route_to_handler(parsed_args)
│       ↓
│   ├─→ run_health_check()
│   ├─→ run_tests(test_type)
│   ├─→ run_analysis(analysis_type)
│   ├─→ run_benchmark(iterations, memory_test)
│   ├─→ run_validation()
│   └─→ run_diagnostics(full)
└─→ print_results(result, full)
```

## Main Class: AWSTestProgram

### run_program(args: List[str]) -> Dict
- **Category:** CLI Program Entry
- **Description:** Main program execution with argument parsing and routing
- **Map:** `run_program → parse_arguments → route_to_handler → specific test → print_results`
- **Sub-functions:**
  - `parse_arguments()` - Parse CLI args
  - `route_to_handler()` - Route to appropriate test
  - `print_results()` - Display formatted results
- **Returns:** Test result dict

### parse_arguments(args: List[str]) -> Namespace
- **Category:** CLI Parsing
- **Commands:**
  - health - Health check
  - test [--type ultra/performance/config/comprehensive]
  - analyze [--architecture/--imports/--memory]
  - benchmark [--iterations N] [--memory]
  - validate [--deployment]
  - diagnostics [--full]
- **Returns:** argparse.Namespace

### route_to_handler(args: Namespace) -> Dict
- **Category:** Command Dispatcher
- **Routes:** Maps command to handler method
- **Handlers:**
  - 'health' → `run_health_check()`
  - 'test' → `run_tests(args.type)`
  - 'analyze' → `run_analysis(args.architecture, args.imports, args.memory)`
  - 'benchmark' → `run_benchmark(args.iterations, args.memory)`
  - 'validate' → `run_validation(args.deployment)`
  - 'diagnostics' → `run_diagnostics(args.full)`

## Test Execution Methods

### run_health_check() -> Dict
- **Category:** Health Check
- **Sub-functions:**
  - `execute_operation(LOGGING, 'get_stats')` - Get logging stats
  - `execute_operation(CACHE, 'get_stats')` - Get cache stats
  - `execute_operation(METRICS, 'get_stats')` - Get metrics stats
  - Gateway status check
- **Returns:** Health status dict

### run_tests(test_type: str) -> Dict
- **Category:** Test Execution
- **Test Types:**
  - 'ultra' - Ultra optimization tests
  - 'performance' - Performance benchmarks
  - 'configuration' - Config tests
  - 'comprehensive' - All tests
- **Sub-functions:** Delegates to debug_core test runners

### run_analysis(architecture: bool, imports: bool, memory: bool) -> Dict
- **Category:** System Analysis
- **Analysis Types:**
  - architecture - Validate SUGA architecture
  - imports - Detect circular imports
  - memory - Memory usage analysis
- **Sub-functions:** Calls utility analysis functions

### run_benchmark(iterations: int, memory_test: bool) -> Dict
- **Category:** Performance Benchmarking
- **Parameters:**
  - iterations (default: 1000)
  - memory_test (default: False)
- **Benchmarks:**
  - Gateway operation speed
  - Cache performance
  - Memory efficiency
- **Returns:** Benchmark results with timings

### run_validation() -> Dict
- **Category:** System Validation
- **Validations:**
  - AWS free tier compliance
  - Configuration validity
  - Deployment readiness
- **Returns:** Validation results

### run_diagnostics(full: bool) -> Dict
- **Category:** Diagnostics
- **Diagnostic Types:**
  - Quick - Basic health metrics
  - Full - Comprehensive system state
- **Sub-functions:**
  - Component health checks
  - Interface validation
  - Performance metrics
  - Error rate analysis

## Output Formatting Methods

### print_results(result: Dict, full: bool)
- **Category:** Output Formatting
- **Routes to specific printer:**
  - Health → `_print_health_results()`
  - Tests → `_print_test_results()`
  - Analysis → `_print_analysis_results()`
  - Benchmark → `_print_benchmark_results()`
  - Validation → `_print_validation_results()`
  - Diagnostics → `_print_diagnostics_results()`

### _print_health_results(result: Dict, full: bool)
- **Displays:**
  - Overall status
  - Component statuses (gateway, cache, logging, metrics)
  - Issue count
  - Health score

### _print_test_results(result: Dict, full: bool)
- **Displays:**
  - Test type
  - Total/passed/failed/skipped counts
  - Pass rate percentage
  - Individual test results (if full)

### _print_benchmark_results(result: Dict, full: bool)
- **Displays:**
  - Operations per second
  - Average latency
  - Memory usage
  - Detailed metrics (if full)

## Convenience Functions

### main(args: Optional[List[str]]) -> Dict
- **Category:** CLI Entry Point
- **Map:** `main() → AWSTestProgram.run_program()`
- **Returns:** Program result

### lambda_handler(event: Dict, context: Any) -> Dict
- **Category:** Lambda Entry Point
- **Map:** `lambda_handler → extract command_args → AWSTestProgram.run_program()`
- **Returns:** Lambda HTTP response

### run_quick_health() -> Dict
- **Map:** `main(['health'])`

### run_quick_test() -> Dict
- **Map:** `main(['test', '--type', 'ultra'])`

### run_quick_benchmark() -> Dict
- **Map:** `main(['benchmark', '--iterations', '100'])`

### run_full_diagnostics() -> Dict
- **Map:** `main(['diagnostics', '--full'])`

## Batch Operations

### run_comprehensive_suite() -> Dict
- **Category:** Batch Testing
- **Executes:**
  1. Health check
  2. Comprehensive tests
  3. Architecture analysis
  4. Benchmark (1000 iterations)
  5. Validation
  6. Full diagnostics
- **Returns:** Dict of all results

### run_ci_cd_suite() -> Dict
- **Category:** CI/CD Pipeline
- **Critical Checks:**
  1. Health check
  2. Architecture validation
  3. Import validation
  4. Performance baseline (500 iterations)
  5. Deployment readiness
- **Fail Fast:** Stops on first failure
- **Returns:** Results with CI status (PASSED/FAILED)

---

# 2. ha_tests.py - Home Assistant Test Suite

## Call Hierarchy

```
run_all_ha_tests()
    ↓
├─→ is_ha_extension_available()
└─→ For each test:
        ↓
    execute_ha_test_with_caching(test_name, test_func, ttl)
        ↓
    ├─→ Check cache for previous result
    ├─→ If miss: Execute test_func()
    ├─→ Record metrics
    ├─→ Cache result
    └─→ Return test result dict
```

## Core Testing Functions

### is_ha_extension_available() -> bool
- **Category:** Availability Check
- **Description:** Check if HA extension is loaded and enabled
- **Sub-functions:**
  - Import homeassistant_extension
  - `is_ha_extension_enabled()` - Check enabled status
- **Returns:** bool

### execute_ha_test_with_caching(test_name, test_func, ttl) -> Dict
- **Category:** Test Execution Framework
- **Description:** Standard test execution with caching and metrics
- **Map:** `execute_ha_test_with_caching → cache_get → [miss] → test_func() → record_metric → cache_set`
- **Sub-functions:**
  - `is_ha_extension_available()` - Check availability
  - `cache_get(f"ha_test_result_{test_name}")` - Check cache
  - `generate_correlation_id()` - Track test
  - `test_func()` - Execute test implementation
  - `record_metric()` - Record execution metrics
  - `cache_set()` - Cache result
  - `log_info/log_error()` - Log test execution
- **Returns:** Test result dict with status, duration, correlation_id

## Individual Tests

### test_ha_extension_initialization() -> Dict
- **Category:** HA Extension - Initialization
- **Tests:** Extension initialization succeeds
- **Implementation:** `_test_ha_extension_initialization_impl()`
- **Sub-functions:**
  - `initialize_ha_extension()` - Initialize
  - `is_ha_extension_enabled()` - Check enabled
- **Pass Criteria:** Result is dict with success=True

### test_ha_assistant_name_validation() -> Dict
- **Category:** HA Extension - Validation
- **Tests:** Assistant name validation logic
- **Valid Names:** "Jarvis", "Computer", "Smart Home", etc.
- **Invalid Names:** "", "Alexa", "Amazon", "a", "a"*30, etc.
- **Sub-functions:**
  - `validate_assistant_name(name)` - Validate each name
- **Pass Criteria:** All valid pass, all invalid fail

### test_ha_configuration_retrieval() -> Dict
- **Category:** HA Extension - Configuration
- **Tests:** Configuration retrieval returns valid structure
- **Required Keys:** enabled, base_url, access_token, timeout, verify_ssl
- **Sub-functions:**
  - `_get_ha_config_gateway()` - Get config
- **Pass Criteria:** All required keys present, valid values

### test_ha_assistant_name_retrieval() -> Dict
- **Category:** HA Extension - Configuration
- **Tests:** Assistant name retrieval
- **Sub-functions:**
  - `get_ha_assistant_name()` - Get name
- **Pass Criteria:** String, length ≥ 2, non-empty

### test_ha_status_check() -> Dict
- **Category:** HA Extension - Health
- **Tests:** HA status check returns valid structure
- **Sub-functions:**
  - `get_ha_status()` - Check status
- **Pass Criteria:** Dict with 'success', 'data', or 'error' key

### test_ha_diagnostic_info() -> Dict
- **Category:** HA Extension - Diagnostics
- **Tests:** Diagnostic info retrieval
- **Expected Fields:** timestamp, ha_enabled, connection_status, assistant_name, configuration
- **Sub-functions:**
  - `get_ha_diagnostic_info()` - Get diagnostics
- **Pass Criteria:** All expected fields present

### test_ha_cleanup() -> Dict
- **Category:** HA Extension - Lifecycle
- **Tests:** Extension cleanup succeeds
- **Sub-functions:**
  - `cleanup_ha_extension()` - Cleanup
- **Pass Criteria:** Result is dict with success=True

### test_ha_environment_variables() -> Dict
- **Category:** HA Extension - Configuration
- **Tests:** Environment variable handling
- **Checks:**
  - HOME_ASSISTANT_ENABLED valid values
  - HA_ASSISTANT_NAME validation if set
- **Pass Criteria:** Valid env var values

### test_ha_cache_operations() -> Dict
- **Category:** HA Extension - Caching
- **Tests:** Cache operations work correctly
- **Operations:**
  - cache_set() for HA keys
  - cache_get() retrieval
  - cache_delete() removal
- **Pass Criteria:** All cache operations succeed

### test_ha_response_formatting() -> Dict
- **Category:** HA Extension - Response Format
- **Tests:** Response formatting consistency
- **Checks:**
  - Success response structure
  - Error response structure
- **Pass Criteria:** Correct dict structure for both

## Test Suite Runner

### run_all_ha_tests() -> Dict
- **Category:** Test Suite Execution
- **Description:** Execute all HA extension tests
- **Tests Executed (10):**
  1. initialization
  2. assistant_name_validation
  3. configuration_retrieval
  4. assistant_name_retrieval
  5. status_check
  6. diagnostic_info
  7. cleanup
  8. environment_variables
  9. cache_operations
  10. response_formatting
- **Sub-functions:**
  - `is_ha_extension_available()` - Check availability
  - `generate_correlation_id()` - Track suite
  - Execute each test function
  - `record_metric()` - Record suite metrics
- **Returns:** Summary dict with:
  - total_tests, passed, failed, skipped
  - pass_rate percentage
  - duration_seconds
  - correlation_id
  - Individual test results

### get_ha_test_info() -> Dict
- **Category:** Test Metadata
- **Returns:** Test suite information without execution
- **Info:**
  - available (bool)
  - test_count
  - test names list
  - description
  - category

---

## Function Categories Summary

### debug_aws.py Categories

**CLI & Entry Points**
- main() - CLI entry
- lambda_handler() - Lambda entry
- AWSTestProgram.run_program() - Main execution

**Test Execution**
- run_health_check() - Health tests
- run_tests() - Test suites
- run_analysis() - System analysis
- run_benchmark() - Performance tests
- run_validation() - Validation checks
- run_diagnostics() - Diagnostics

**Batch Operations**
- run_comprehensive_suite() - All tests
- run_ci_cd_suite() - CI/CD pipeline

**Output Formatting**
- print_results() - Main formatter
- Specific printers for each result type

### ha_tests.py Categories

**Test Framework**
- is_ha_extension_available() - Availability check
- execute_ha_test_with_caching() - Test executor

**Test Implementations**
- 10 individual test functions
- Each with implementation function (_impl suffix)

**Test Suite**
- run_all_ha_tests() - Execute all tests
- get_ha_test_info() - Test metadata

---

**End of DEBUG & TEST Files Function Maps**
