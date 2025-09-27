"""
__init__.py - UPDATED: Main Module Initialization with Gateway Interface Exports
Version: 2025.09.27.01
Description: Updated module initialization with corrected gateway interface imports

UPDATES APPLIED:
- ✅ CORRECTED: lambda_handlers → lambda import fix
- ✅ VERIFIED: All gateway interface exports current
- ✅ MAINTAINED: Complete function export compatibility

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

# Cache system
from .cache import (
    # Cache Manager Interface
    get_cache_manager,
    reset_cache_manager,
    
    # Cache Operations
    cache_get,
    cache_set,
    cache_delete,
    cache_clear,
    cache_exists,
    cache_get_stats,
    
    # BoundedCollection for memory management
    BoundedCollection
)

# Singleton management system  
from .singleton import (
    # Core singleton operations
    get_singleton,
    manage_singletons,
    
    # Thread safety functions (consolidated in singleton gateway)
    validate_thread_safety,
    execute_with_timeout,
    coordinate_operation,
    get_thread_coordinator,
    
    # Singleton types and modes
    SingletonType,
    SingletonMode,
    SystemOperation
)

# Security system
from .security import (
    # Request validation
    validate_request,
    get_security_status,
    
    # Input validation and sanitization  
    validate_string_input,
    validate_input_length,
    validate_alphanumeric,
    sanitize_input,
    validate_uuid_format,
    validate_email_format,
    validate_url_format,
    validate_json_structure,
    validate_parameter_name,
    validate_aws_region,
    is_valid_environment,
    check_regex_complexity,
    validate_pattern_safety,
    
    # Secure key generation
    generate_secure_random_key,
    validate_key_entropy,
    create_cryptographic_hash,
    generate_secure_token,
    
    # Enhanced data sanitization
    sanitize_sensitive_data,
    filter_security_sensitive_keys,
    sanitize_error_data,
    clean_response_for_external_use,
    
    # Security-aware response formatting
    create_safe_error_response,
    format_security_response,
    sanitize_debug_information,
    create_security_audit_response,
    
    # Timeout-protected operations
    execute_with_timeout,
    timeout_protected_validation,
    safe_regex_match,
    bounded_string_processing,
    
    # Generic security utilities
    calculate_data_hash,
    validate_data_integrity,
    create_security_context,
    
    # Cost protection
    validate_cost_constraints,
    check_memory_usage,        # Used by logging.py for memory pressure monitoring
    optimize_data_structure
)

# Metrics system
from .metrics import (
    # Universal metrics interface
    collect_metrics,
    format_metric, 
    calculate_health,
    analyze_performance,
    record_metric,
    
    # Metrics management
    get_metrics_manager,
    reset_metrics_manager,
    get_metrics_summary,
    clear_metrics,
    
    # Specialized metrics
    get_security_metrics,
    get_performance_metrics,
    get_cost_metrics,
    get_health_metrics,
    
    # Memory status (used by logging.py)
    get_memory_status,
    
    # Data structures
    MetricType,
    MetricCategory,
    HealthStatus
)

# HTTP Client system
from .http_client import (
    # HTTP client operations
    make_request,
    get_http_status,
    get_aws_client,
    
    # HTTP client management
    get_http_client_manager,
    reset_http_client_manager
)

# Initialization system
from .initialization import (
    # Lambda initialization
    unified_lambda_initialization,
    unified_lambda_cleanup,
    get_initialization_status,
    get_free_tier_memory_status,
    get_dependency_container
)

# Lambda system
from .lambda import (
    alexa_lambda_handler,
    create_alexa_response,
    lambda_handler_with_gateway,
    get_lambda_status
)

# Circuit Breaker system
from .circuit_breaker import (
    get_circuit_breaker,
    circuit_breaker_call,
    get_circuit_breaker_status,
    reset_circuit_breaker
)

# Configuration system (if available)
try:
    from .config import (
        # Configuration Manager
        get_configuration_manager,
        reset_configuration_manager,
        reload_configuration,
        
        # Parameter Management
        get_parameter,
        set_parameter,
        delete_parameter,
        get_all_parameters,
        validate_parameter,
        
        # Environment Configuration
        get_environment,
        set_environment,
        is_production,
        is_debug_mode,
        set_debug_mode,
        get_debug_level,
        set_debug_level,
        
        # AWS Configuration
        get_aws_region,
        set_aws_region,
        get_aws_profile,
        set_aws_profile,
        get_aws_config,
        validate_aws_region,
        get_supported_regions,
        
        # HTTP Client Configuration
        get_http_timeout,
        set_http_timeout,
        get_http_retry_policy,
        set_http_retry_policy,
        get_http_connection_pool_size,
        set_http_connection_pool_size,
        should_verify_ssl,
        set_ssl_verification,
        get_http_headers,
        set_http_header,
        
        # Cache Configuration
        get_cache_ttl,
        set_cache_ttl,
        get_cache_max_size,
        set_cache_max_size,
        get_cache_eviction_policy,
        set_cache_eviction_policy,
        is_cache_enabled,
        set_cache_enabled,
        
        # Logging Configuration
        get_log_level,
        set_log_level,
        get_log_format,
        set_log_format,
        is_structured_logging_enabled,
        set_structured_logging,
        
        # Performance Configuration  
        get_memory_threshold_percent,
        set_memory_threshold_percent,
        get_cleanup_interval,
        set_cleanup_interval,
        is_performance_monitoring_enabled,
        set_performance_monitoring,
        
        # Cost Protection Configuration
        is_cost_protection_active,
        set_cost_protection_active,
        get_rate_limit_per_minute,
        set_rate_limit_per_minute,
        get_cost_threshold,
        set_cost_threshold,
        
        # Utility Configuration
        get_validation_rules,
        set_validation_rule,
        get_timeout_settings,
        set_timeout_setting,
        get_retry_settings,
        set_retry_setting
    )
except ImportError:
    # Config module not available
    pass

# Utility system
from .utility import (
    # Core utility operations
    validate_string_input,
    create_success_response,
    create_error_response,
    sanitize_response_data,
    get_current_timestamp,
    
    # Utility management
    get_utility_manager,
    reset_utility_manager
)

# Logging system
from .logging import (
    # Universal logging interface
    log_info,
    log_error,
    log_warning,
    log_debug,
    
    # Logging management
    get_logging_manager,
    reset_logging_manager,
    
    # Specialized logging
    log_security_event,
    log_performance_metric,
    log_cost_event,
    log_health_check
)

# Cost protection system
from .cost_protection import (
    # Cost monitoring
    should_block_request,
    record_lambda_invocation,
    get_usage_summary,
    is_cost_protection_enabled,
    
    # Cost management
    cost_protection_active
)

# Module-level exports
__all__ = [
    # ===== CACHE SYSTEM =====
    'get_cache_manager',
    'reset_cache_manager',
    'cache_get',
    'cache_set',
    'cache_delete',
    'cache_clear',
    'cache_exists',
    'cache_get_stats',
    'BoundedCollection',
    
    # ===== SINGLETON SYSTEM =====
    'get_singleton',
    'manage_singletons',
    'validate_thread_safety',
    'execute_with_timeout',
    'coordinate_operation',
    'get_thread_coordinator',
    'SingletonType',
    'SingletonMode',
    'SystemOperation',
    
    # ===== SECURITY SYSTEM =====
    'validate_request',
    'get_security_status',
    'validate_string_input',
    'validate_input_length',
    'validate_alphanumeric',
    'sanitize_input',
    'validate_uuid_format',
    'validate_email_format',
    'validate_url_format',
    'validate_json_structure',
    'validate_parameter_name',
    'validate_aws_region',
    'is_valid_environment',
    'check_regex_complexity',
    'validate_pattern_safety',
    'generate_secure_random_key',
    'validate_key_entropy',
    'create_cryptographic_hash',
    'generate_secure_token',
    'sanitize_sensitive_data',
    'filter_security_sensitive_keys',
    'sanitize_error_data',
    'clean_response_for_external_use',
    'create_safe_error_response',
    'format_security_response',
    'create_security_audit_response',
    'timeout_protected_validation',
    'safe_regex_match',
    'bounded_string_processing',
    'calculate_data_hash',
    'validate_data_integrity',
    'create_security_context',
    'validate_cost_constraints',
    'check_memory_usage',          # Used by logging.py
    'optimize_data_structure',
    
    # ===== METRICS SYSTEM =====
    'collect_metrics',
    'format_metric',
    'calculate_health',
    'analyze_performance',
    'record_metric',
    'get_metrics_manager',
    'reset_metrics_manager',
    'get_metrics_summary',
    'clear_metrics',
    'get_security_metrics',
    'get_performance_metrics',
    'get_cost_metrics',
    'get_health_metrics',
    'MetricType',
    'MetricCategory',
    'HealthStatus',
    
    # ===== HTTP CLIENT SYSTEM =====
    'make_request',
    'get_http_status',
    'get_aws_client',
    'get_http_client_manager',
    'reset_http_client_manager',
    
    # ===== INITIALIZATION SYSTEM =====
    'unified_lambda_initialization',
    'unified_lambda_cleanup',
    'get_initialization_status',
    'get_free_tier_memory_status',
    'get_dependency_container',
    
    # ===== LAMBDA SYSTEM =====
    'alexa_lambda_handler',
    'create_alexa_response',
    'lambda_handler_with_gateway',
    'get_lambda_status',
    
    # ===== CIRCUIT BREAKER SYSTEM =====
    'get_circuit_breaker',
    'circuit_breaker_call',
    'get_circuit_breaker_status',
    'reset_circuit_breaker',
    
    # ===== CONFIGURATION SYSTEM =====
    'get_configuration_manager',
    'is_debug_mode',
    'get_debug_level',
    'get_log_level',
    'is_cost_protection_active',
    
    # ===== COST PROTECTION SYSTEM =====
    'should_block_request',
    'record_lambda_invocation',
    'get_usage_summary',
    'is_cost_protection_enabled',
    'cost_protection_active'
]

# EOF
