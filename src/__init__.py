"""
__init__.py - UPDATED: Primary Interface Exports with New Logging System
Version: 2025.09.25.01
Description: Updated module exports for ultra-pure logging interface integration

LOGGING SYSTEM UPDATES:
- âœ… UPDATED: New ultra-pure logging interface exports
- âœ… COMPATIBLE: Maintains backwards compatibility with convenience functions
- âœ… OPTIMIZED: Includes cross-gateway utilization benefits
- âœ… COMPLETE: All essential logging functions available

ARCHITECTURE: PRIMARY MODULE EXPORTS
- All gateway interfaces exported for external use
- Updated logging exports to match new ultra-pure interface
- Maintains full compatibility with existing code

Licensed under the Apache License, Version 2.0
"""

# ===== CORE GATEWAY SYSTEMS =====

# Singleton system
from .singleton import (
    get_singleton,
    manage_singletons, 
    singleton_health_check,
    get_memory_status,
    validate_thread_safety,
    get_thread_safety_status,
    execute_with_timeout,
    coordinate_operation,
    get_thread_coordinator,
    get_cost_protection,
    get_cache_manager,
    get_security_validator,
    get_unified_validator,
    get_config_manager,
    get_memory_manager,
    get_lambda_cache,
    get_response_cache,
    get_circuit_breaker_manager,
    get_response_processor,
    get_lambda_optimizer,
    get_response_metrics_manager,
    SingletonType,
    SystemOperation
)

# Cache system  
from .cache import (
    cache_get,
    cache_set, 
    cache_clear,
    get_cache_statistics,
    optimize_cache_memory,
    get_lambda_cache,
    get_response_cache,
    CacheType
)

# ===== UPDATED LOGGING SYSTEM =====

from .logging import (
    # Core logging functions (ultra-pure interface)
    log,                    # Universal logging function
    get_logger,            # Logger access via singleton
    setup_logging,         # Configuration
    get_status,            # Status (renamed from get_log_statistics)
    
    # Convenience wrapper functions (maintained for compatibility)
    log_info,              # Info logging
    log_error,             # Error logging  
    log_debug,             # Debug logging
    log_warning,           # Warning logging
    log_critical,          # Critical logging
    
    # Enums (re-exported from logging_core for compatibility)
    LogLevel,              # Log level enumeration
    LoggingOperation       # Logging operation enumeration
)

# Security system
from .security import (
    # Enhanced security validation through gateway
    validate_input,
    validate_request,
    sanitize_data,
    sanitize_logging_context,  # NEW: Enhanced for logging integration
    get_security_status,
    security_health_check,
    authenticate_alexa_request,
    authenticate_token,
    validate_token_expiration,
    get_authentication_status,
    authorize_directive_access,
    authorize_resource_access, 
    get_authorization_status,
    sanitize_error_response,
    sanitize_debug_information,
    get_safe_error_message,
    filter_sensitive_information,  # NEW: For logging context filtering
    validate_certificate_chain,
    validate_certificate_expiration,
    get_certificate_security_level,
    enforce_rate_limiting,
    check_rate_limit_status,
    reset_rate_limit,
    encrypt_cache_data,
    decrypt_cache_data,
    validate_cache_security,
    detect_injection_patterns,
    validate_input_structure,
    check_malicious_patterns,
    assess_threat_level,
    get_security_validator,
    get_unified_validator,
    get_rate_limiter
)

# Utility system  
from .utility import (
    # Core validation functions
    validate_string_input,
    validate_numeric_input,
    validate_dict_structure,
    validate_list_structure,
    
    # Response formatting functions
    create_success_response,
    create_error_response,
    format_response_data,
    sanitize_response_data,
    
    # NEW: Logging integration functions
    generate_correlation_id,    # Used by logging.py for request correlation
    get_current_timestamp,     # Used by logging.py for consistent timestamping
    sanitize_logging_data,     # Logging-specific sanitization
    format_logging_response,   # Logging-specific response formatting
    
    # Data processing functions
    process_json_data,
    convert_data_types,
    filter_dict_keys,
    merge_dictionaries,
    
    # ReDoS-resistant validation
    validate_input_with_timeout,
    compile_regex_patterns_safe,
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
from .lambda_handlers import (
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
        
        # Service Configuration
        is_service_enabled,
        set_service_enabled,
        get_service_endpoint,
        set_service_endpoint,
        get_service_timeout,
        set_service_timeout,
        
        # Health Check Configuration
        get_health_check_timeout,
        set_health_check_timeout,
        get_health_check_interval,
        set_health_check_interval
    )
except ImportError:
    # Configuration system not available - provide basic stubs
    def get_configuration_manager(): return None
    def is_debug_mode(): return False
    def get_debug_level(): return 0
    def get_log_level(): return "INFO"
    def is_cost_protection_active(): return True

# Cost Protection system (if available)
try:
    from .cost_protection import (
        # Cost protection interface
        should_block_request,
        record_lambda_invocation,
        get_usage_summary,
        is_cost_protection_enabled,
        cost_protection_active,
        reset_cost_protection,
        
        # Cost categories and service types
        CostCategory,
        ServiceType,
        
        # API call recording
        record_api_call,
        record_ssm_api_call,
        can_use_service
    )
except ImportError:
    # Cost protection not available - provide basic stubs
    def should_block_request(): return False
    def record_lambda_invocation(): pass
    def get_usage_summary(): return {}
    def is_cost_protection_enabled(): return False
    def cost_protection_active(): return False

# ===== COMPREHENSIVE EXPORTS =====

__all__ = [
    # ===== SINGLETON SYSTEM =====
    'get_singleton',
    'manage_singletons', 
    'singleton_health_check',
    'get_memory_status',
    'validate_thread_safety',
    'get_thread_safety_status',
    'execute_with_timeout',
    'coordinate_operation',
    'get_thread_coordinator',
    'get_cost_protection',
    'get_cache_manager',
    'get_security_validator',
    'get_unified_validator',
    'get_config_manager',
    'get_memory_manager',
    'get_lambda_cache',
    'get_response_cache',
    'get_circuit_breaker_manager',
    'get_response_processor',
    'get_lambda_optimizer',
    'get_response_metrics_manager',
    'SingletonType',
    'SystemOperation',
    
    # ===== CACHE SYSTEM =====
    'cache_get',
    'cache_set', 
    'cache_clear',
    'get_cache_statistics',
    'optimize_cache_memory',
    'CacheType',
    
    # ===== UPDATED LOGGING SYSTEM =====
    # Core functions
    'log',                        # NEW: Universal logging function
    'get_logger',
    'setup_logging',
    'get_status',                 # RENAMED: was get_log_statistics
    
    # Convenience functions (maintained)
    'log_info',
    'log_error', 
    'log_debug',
    'log_warning',
    'log_critical',
    
    # Enums (re-exported)
    'LogLevel',
    'LoggingOperation',
    
    # ===== SECURITY SYSTEM =====
    'validate_input',
    'validate_request',
    'sanitize_data',
    'sanitize_logging_context',    # NEW
    'get_security_status',
    'security_health_check',
    'authenticate_alexa_request',
    'authenticate_token',
    'validate_token_expiration',
    'get_authentication_status',
    'authorize_directive_access',
    'authorize_resource_access',
    'get_authorization_status',
    'sanitize_error_response',
    'sanitize_debug_information',
    'get_safe_error_message',
    'filter_sensitive_information', # NEW
    'validate_certificate_chain',
    'validate_certificate_expiration',
    'get_certificate_security_level',
    'enforce_rate_limiting',
    'check_rate_limit_status',
    'reset_rate_limit',
    'encrypt_cache_data',
    'decrypt_cache_data',
    'validate_cache_security',
    'detect_injection_patterns',
    'validate_input_structure',
    'check_malicious_patterns',
    'assess_threat_level',
    'get_rate_limiter',
    
    # ===== UTILITY SYSTEM =====
    'validate_string_input',
    'validate_numeric_input',
    'validate_dict_structure',
    'validate_list_structure',
    'create_success_response',
    'create_error_response',
    'format_response_data',
    'sanitize_response_data',
    
    # NEW: Logging integration functions
    'generate_correlation_id',
    'get_current_timestamp', 
    'sanitize_logging_data',
    'format_logging_response',
    
    'process_json_data',
    'convert_data_types',
    'filter_dict_keys',
    'merge_dictionaries',
    'validate_input_with_timeout',
    'compile_regex_patterns_safe',
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
