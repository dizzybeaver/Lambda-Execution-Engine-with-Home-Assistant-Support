"""
config.py - ENHANCED: Configuration Gateway with Advanced Security Settings
Version: 2025.09.25.01
Description: Enhanced configuration gateway with comprehensive security variables and TLS configurability

ARCHITECTURE: PRIMARY GATEWAY - ULTRA-PURE DELEGATION
- config.py (this file) = Gateway/Firewall - function declarations ONLY
- config_core.py = Core configuration logic using all gateway interfaces
- config_http.py = HTTP-specific configuration implementation

ENHANCED SECURITY CONFIGURATION VARIABLES:
- SECURITY_STRICT_CERT_VALIDATION: Force certificate chain validation (true/false)
- SECURITY_SANITIZE_ERRORS: Remove sensitive details from error responses (true/false)
- RATE_LIMITING_ENABLED: Enable authentication rate limiting (true/false)
- CACHE_ENCRYPTION_ENABLED: Encrypt sensitive cached data (true/false)
- TLS_VERIFY_BYPASS_ENABLED: Allow TLS verification bypass for certificates (true/false)
- SECURITY_THREAT_DETECTION_ENABLED: Enable enhanced threat pattern detection (true/false)
- AUTH_TOKEN_EXPIRATION_CHECK: Enable token expiration validation (true/false)
- SECURITY_AUDIT_COMPREHENSIVE: Enable comprehensive security audit logging (true/false)

RATE LIMITING CONFIGURATION:
- RATE_LIMIT_PER_MINUTE: Request rate limit per minute (10-1000)
- RATE_LIMIT_PER_HOUR: Hourly rate limit (100-10000)
- RATE_LIMIT_AUTHENTICATION_PER_MINUTE: Auth-specific per-minute limit (5-100)
- RATE_LIMIT_EMERGENCY_THRESHOLD: Threshold for emergency rate limiting (1000-10000)

CACHE SECURITY CONFIGURATION:
- CACHE_ENCRYPTION_KEY_ROTATION_DAYS: Encryption key rotation interval (7-365)
- CACHE_SECURE_TTL_OVERRIDE: Override TTL for secure cache types (60-7200)
- CACHE_AUTHENTICATION_TTL: TTL for authentication cache (60-3600)
- CACHE_RATE_LIMITING_TTL: TTL for rate limiting counters (60-7200)

TLS/SSL SECURITY CONFIGURATION:
- SSL_CERT_VALIDATION_LEVEL: Certificate validation level (none/basic/standard/strict)
- SSL_CERT_EXPIRATION_WARNING_DAYS: Days before expiration warning (1-90)
- SSL_CIPHER_SUITE_ENFORCEMENT: Enforce secure cipher suites (true/false)
- SSL_PROTOCOL_MIN_VERSION: Minimum TLS protocol version (1.0/1.1/1.2/1.3)

ERROR HANDLING SECURITY:
- ERROR_SANITIZATION_LEVEL: Level of error sanitization (basic/standard/strict)
- DEBUG_INFO_SECURITY_FILTER: Filter debug info based on security level (true/false)
- STACK_TRACE_EXPOSURE_LIMIT: Limit stack trace exposure (0-10 levels)
- ERROR_CORRELATION_ID_ENABLED: Enable correlation IDs in errors (true/false)

Licensed under the Apache License, Version 2.0
"""

from typing import Dict, Any, Optional, Union, List
from .config_core import (
    # Core configuration implementations
    _get_parameter_implementation,
    _set_parameter_implementation,
    _validate_parameter_implementation,
    _get_configuration_section_implementation,
    
    # Environment implementations
    _get_environment_implementation,
    _set_environment_implementation,
    _get_debug_mode_implementation,
    _set_debug_mode_implementation,
    
    # Enhanced security implementations
    _get_security_level_implementation,
    _set_security_level_implementation,
    _get_rate_limit_per_minute_implementation,
    _get_rate_limit_per_hour_implementation,
    _is_strict_cert_validation_enabled_implementation,
    _is_error_sanitization_enabled_implementation,
    _is_cache_encryption_enabled_implementation,
    _is_tls_verify_bypass_enabled_implementation,
    
    # SSL/TLS configuration implementations
    _get_ssl_cert_validation_level_implementation,
    _set_ssl_cert_validation_level_implementation,
    _get_ssl_cert_expiration_warning_days_implementation,
    _get_ssl_protocol_min_version_implementation,
    
    # Authentication configuration implementations
    _get_auth_token_ttl_implementation,
    _is_auth_token_expiration_check_enabled_implementation,
    _get_authentication_rate_limit_implementation,
    
    # Cache security implementations
    _get_cache_encryption_key_rotation_days_implementation,
    _get_cache_secure_ttl_override_implementation,
    _get_cache_authentication_ttl_implementation,
    _get_cache_rate_limiting_ttl_implementation,
    
    # Error handling security implementations
    _get_error_sanitization_level_implementation,
    _is_debug_info_security_filter_enabled_implementation,
    _get_stack_trace_exposure_limit_implementation,
    
    # Legacy configuration implementations
    _is_validation_enabled_implementation,
    _get_validation_strictness_implementation,
    _get_credential_rotation_days_implementation,
    _is_security_audit_enabled_implementation,
    _is_encryption_enabled_implementation,
    _get_cache_ttl_implementation,
    _get_cache_max_size_implementation,
    _is_cache_enabled_implementation
)

# ===== SECTION 1: CORE CONFIGURATION =====

def get_parameter(key: str, default_value: Any = None, section: str = None, tier_aware: bool = False) -> Any:
    """
    PURE DELEGATION: Get configuration parameter with tier-aware scaling.
    Supports free-tier optimizations and memory-efficient caching.
    """
    return _get_parameter_implementation(key, default_value, section, tier_aware)

def set_parameter(key: str, value: Any, section: str = None) -> bool:
    """
    PURE DELEGATION: Set configuration parameter with validation.
    Uses security.py for input validation and logging.py for audit trails.
    """
    return _set_parameter_implementation(key, value, section)

def validate_parameter(key: str, value: Any, section: str = None) -> Dict[str, Any]:
    """
    PURE DELEGATION: Validate configuration parameter.
    Uses utility.py for validation patterns and security.py for threat detection.
    """
    return _validate_parameter_implementation(key, value, section)

def get_configuration_section(section: str) -> Dict[str, Any]:
    """
    PURE DELEGATION: Get entire configuration section.
    Uses cache.py for section-level caching optimization.
    """
    return _get_configuration_section_implementation(section)

# ===== SECTION 2: ENVIRONMENT CONFIGURATION =====

def get_environment() -> str:
    """
    PURE DELEGATION: Get current environment setting.
    Returns: development, staging, production
    """
    return _get_environment_implementation()

def set_environment(environment: str) -> bool:
    """
    PURE DELEGATION: Set environment with validation.
    Validates environment values and updates dependent configurations.
    """
    return _set_environment_implementation(environment)

def get_debug_mode() -> bool:
    """
    PURE DELEGATION: Get debug mode status.
    Integrates with security settings for safe debug information exposure.
    """
    return _get_debug_mode_implementation()

def set_debug_mode(enabled: bool) -> bool:
    """
    PURE DELEGATION: Set debug mode with security considerations.
    Automatically adjusts security filtering based on debug status.
    """
    return _set_debug_mode_implementation(enabled)

# ===== SECTION 3: ENHANCED SECURITY CONFIGURATION =====

def get_security_level() -> str:
    """
    PURE DELEGATION: Get security validation level.
    Returns: basic, standard, enhanced, strict
    """
    return _get_security_level_implementation()

def set_security_level(level: str) -> bool:
    """
    PURE DELEGATION: Set security level with cascading configuration updates.
    Automatically adjusts related security settings based on level.
    """
    return _set_security_level_implementation(level)

def get_rate_limit_per_minute() -> int:
    """
    PURE DELEGATION: Get per-minute rate limit.
    Used by security.py for rate limiting enforcement.
    """
    return _get_rate_limit_per_minute_implementation()

def get_rate_limit_per_hour() -> int:
    """
    PURE DELEGATION: Get per-hour rate limit.
    Used by security.py for hourly rate limiting windows.
    """
    return _get_rate_limit_per_hour_implementation()

def is_strict_cert_validation_enabled() -> bool:
    """
    PURE DELEGATION: Check if strict certificate validation is enabled.
    Controls certificate chain validation and expiration checks.
    """
    return _is_strict_cert_validation_enabled_implementation()

def is_error_sanitization_enabled() -> bool:
    """
    PURE DELEGATION: Check if error response sanitization is enabled.
    Controls removal of sensitive information from error responses.
    """
    return _is_error_sanitization_enabled_implementation()

def is_cache_encryption_enabled() -> bool:
    """
    PURE DELEGATION: Check if cache encryption is enabled.
    Controls encryption of sensitive data in cache storage.
    """
    return _is_cache_encryption_enabled_implementation()

def is_tls_verify_bypass_enabled() -> bool:
    """
    PURE DELEGATION: Check if TLS verification bypass is allowed.
    Enables users to bypass certificate verification when needed.
    """
    return _is_tls_verify_bypass_enabled_implementation()

# ===== SECTION 4: SSL/TLS SECURITY CONFIGURATION =====

def get_ssl_cert_validation_level() -> str:
    """
    PURE DELEGATION: Get SSL certificate validation level.
    Returns: none, basic, standard, strict
    Controls depth of certificate validation performed.
    """
    return _get_ssl_cert_validation_level_implementation()

def set_ssl_cert_validation_level(level: str) -> bool:
    """
    PURE DELEGATION: Set SSL certificate validation level.
    Validates level and updates certificate validation behavior.
    """
    return _set_ssl_cert_validation_level_implementation(level)

def get_ssl_cert_expiration_warning_days() -> int:
    """
    PURE DELEGATION: Get days before certificate expiration warning.
    Used by security.py for proactive certificate management.
    """
    return _get_ssl_cert_expiration_warning_days_implementation()

def get_ssl_protocol_min_version() -> str:
    """
    PURE DELEGATION: Get minimum TLS protocol version.
    Returns: 1.0, 1.1, 1.2, 1.3
    Controls minimum allowed TLS version for connections.
    """
    return _get_ssl_protocol_min_version_implementation()

# ===== SECTION 5: AUTHENTICATION CONFIGURATION =====

def get_auth_token_ttl() -> int:
    """
    PURE DELEGATION: Get authentication token TTL in seconds.
    Used by security.py for token expiration validation.
    """
    return _get_auth_token_ttl_implementation()

def is_auth_token_expiration_check_enabled() -> bool:
    """
    PURE DELEGATION: Check if token expiration checking is enabled.
    Controls automatic validation of token expiration times.
    """
    return _is_auth_token_expiration_check_enabled_implementation()

def get_authentication_rate_limit() -> int:
    """
    PURE DELEGATION: Get authentication-specific rate limit per minute.
    Separate from general rate limiting for authentication operations.
    """
    return _get_authentication_rate_limit_implementation()

# ===== SECTION 6: CACHE SECURITY CONFIGURATION =====

def get_cache_encryption_key_rotation_days() -> int:
    """
    PURE DELEGATION: Get encryption key rotation interval in days.
    Controls automatic rotation of cache encryption keys.
    """
    return _get_cache_encryption_key_rotation_days_implementation()

def get_cache_secure_ttl_override() -> int:
    """
    PURE DELEGATION: Get TTL override for secure cache types.
    Provides different TTL for authentication and sensitive data caches.
    """
    return _get_cache_secure_ttl_override_implementation()

def get_cache_authentication_ttl() -> int:
    """
    PURE DELEGATION: Get TTL specifically for authentication cache.
    Controls how long authentication tokens are cached.
    """
    return _get_cache_authentication_ttl_implementation()

def get_cache_rate_limiting_ttl() -> int:
    """
    PURE DELEGATION: Get TTL for rate limiting counters.
    Controls persistence duration of rate limiting data.
    """
    return _get_cache_rate_limiting_ttl_implementation()

# ===== SECTION 7: ERROR HANDLING SECURITY CONFIGURATION =====

def get_error_sanitization_level() -> str:
    """
    PURE DELEGATION: Get error sanitization level.
    Returns: basic, standard, strict
    Controls amount of information removed from error responses.
    """
    return _get_error_sanitization_level_implementation()

def is_debug_info_security_filter_enabled() -> bool:
    """
    PURE DELEGATION: Check if debug info security filtering is enabled.
    Controls filtering of debug information based on security level.
    """
    return _is_debug_info_security_filter_enabled_implementation()

def get_stack_trace_exposure_limit() -> int:
    """
    PURE DELEGATION: Get maximum stack trace levels to expose.
    Controls depth of stack traces included in error responses.
    """
    return _get_stack_trace_exposure_limit_implementation()

# ===== SECTION 8: LEGACY SECURITY CONFIGURATION (MAINTAINED FOR COMPATIBILITY) =====

def is_validation_enabled() -> bool:
    """
    PURE DELEGATION: Check if input validation is enabled (legacy).
    Maintained for backward compatibility with existing code.
    """
    return _is_validation_enabled_implementation()

def get_validation_strictness() -> int:
    """
    PURE DELEGATION: Get validation strictness level (legacy).
    Returns: 0-3, maintained for backward compatibility.
    """
    return _get_validation_strictness_implementation()

def get_credential_rotation_days() -> int:
    """
    PURE DELEGATION: Get credential rotation interval (legacy).
    Maintained for backward compatibility.
    """
    return _get_credential_rotation_days_implementation()

def is_security_audit_enabled() -> bool:
    """
    PURE DELEGATION: Check if security audit logging is enabled (legacy).
    Maintained for backward compatibility.
    """
    return _is_security_audit_enabled_implementation()

def is_encryption_enabled() -> bool:
    """
    PURE DELEGATION: Check if encryption is enabled (legacy).
    Maintained for backward compatibility - use is_cache_encryption_enabled() for new code.
    """
    return _is_encryption_enabled_implementation()

# ===== SECTION 9: CACHE CONFIGURATION (ENHANCED) =====

def get_cache_ttl(ttl_type: str = "default") -> int:
    """
    PURE DELEGATION: Get cache TTL by type with security considerations.
    Supports different TTLs for secure cache types.
    """
    return _get_cache_ttl_implementation(ttl_type)

def get_cache_max_size() -> int:
    """
    PURE DELEGATION: Get cache max size with memory optimization.
    Automatically scales based on environment and security requirements.
    """
    return _get_cache_max_size_implementation()

def is_cache_enabled() -> bool:
    """
    PURE DELEGATION: Check if caching system is enabled.
    Controls overall cache system availability.
    """
    return _is_cache_enabled_implementation()

# EOF
