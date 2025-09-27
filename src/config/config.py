"""
config.py - ULTRA-OPTIMIZED: Enhanced JWT Configuration Support
Version: 2025.09.27.01
Description: Configuration enhancements to support proper JWT signature verification

SECURITY ENHANCEMENTS FOR ISSUE #9:
- ✅ JWT SECRET KEY MANAGEMENT: Secure secret key configuration with validation
- ✅ JWT ALGORITHM CONFIGURATION: Algorithm whitelist and security settings
- ✅ JWT CLAIMS VALIDATION: Required claims configuration for enhanced security
- ✅ JWT TIMING CONFIGURATION: Clock skew tolerance and expiration settings
- ✅ ALEXA INTEGRATION CONFIG: Enhanced Alexa skill configuration for JWT
- ✅ FALLBACK SECURITY: Secure fallback mechanisms for missing configurations

ARCHITECTURE: SPECIAL STATUS - CENTRAL CONFIGURATION REPOSITORY
- Enhanced JWT security configuration parameters
- Maintains gateway patterns with special configuration status
- Backward compatible with existing configuration system
- Memory-optimized for AWS Lambda 128MB compliance

FOLLOWS PROJECT_ARCHITECTURE_REFERENCE.md - ULTRA-PURE IMPLEMENTATION
"""

import os
import logging
from typing import Dict, Any, Optional, Union, List

logger = logging.getLogger(__name__)

# Import existing configuration system
from .config_core import get_configuration_parameter, set_configuration_parameter, validate_configuration

# ===== SECTION 1: JWT SECURITY CONFIGURATION PARAMETERS =====

# JWT Security Configuration Defaults
JWT_DEFAULT_CONFIG = {
    # JWT Algorithm and Security Settings
    'jwt_algorithm': 'HS256',
    'jwt_algorithm_whitelist': ['HS256', 'HS384', 'HS512'],
    'jwt_clock_skew_seconds': 300,  # 5 minutes
    'jwt_maximum_token_age_seconds': 86400,  # 24 hours
    'jwt_minimum_secret_length': 32,  # Minimum 32 characters for security
    
    # JWT Required Claims Configuration
    'jwt_required_claims': {
        'iss': None,  # Issuer - set to required issuer or None to skip
        'aud': None,  # Audience - set to required audience or None to skip
        'exp': True,  # Expiration - always required
        'iat': True,  # Issued at - always required
        'nbf': False, # Not before - optional
        'sub': False, # Subject - optional
        'jti': False  # JWT ID - optional
    },
    
    # JWT Validation Settings
    'jwt_strict_validation': True,  # Enable strict validation
    'jwt_require_issued_at': True,  # Require iat claim
    'jwt_require_expiration': True, # Require exp claim
    'jwt_allow_none_algorithm': False,  # Never allow 'none' algorithm
    
    # JWT Caching Configuration
    'jwt_cache_enabled': True,
    'jwt_cache_ttl_seconds': 300,  # 5 minutes
    'jwt_failed_cache_ttl_seconds': 30,  # 30 seconds for failed attempts
    
    # Security Headers Configuration (for HTTP responses)
    'security_headers_enabled': True,
    'security_headers': {
        'X-Frame-Options': 'DENY',
        'X-Content-Type-Options': 'nosniff',
        'X-XSS-Protection': '1; mode=block',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'Content-Security-Policy': "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'",
        'Referrer-Policy': 'strict-origin-when-cross-origin'
    },
    
    # Enhanced Alexa Configuration
    'alexa_application_id': '',  # Must be set for Alexa skill validation
    'alexa_require_access_token': False,  # Whether to require access token
    'alexa_jwt_validation': True,  # Enable JWT validation for Alexa tokens
    
    # Rate Limiting Configuration (enhanced for JWT)
    'jwt_rate_limit_enabled': True,
    'jwt_rate_limit_requests_per_minute': 60,
    'jwt_rate_limit_burst_requests': 10,
    
    # Error Handling Configuration
    'jwt_detailed_errors': False,  # Set to False in production
    'jwt_log_failed_attempts': True,
    'jwt_sanitize_error_responses': True,
    
    # Fallback Configuration
    'fallback_jwt_secret': 'INSECURE_FALLBACK_KEY_CHANGE_IN_PRODUCTION',
    'emergency_jwt_bypass': False,  # Emergency bypass - NEVER enable in production
}

# ===== SECTION 2: JWT CONFIGURATION ACCESS FUNCTIONS =====

def get_jwt_configuration(parameter_name: str, default_value: Any = None) -> Any:
    """
    Get JWT-specific configuration parameter with enhanced security validation.
    
    Args:
        parameter_name: Name of the JWT configuration parameter
        default_value: Default value if parameter not found
        
    Returns:
        Configuration parameter value
    """
    try:
        # First try environment variables for sensitive settings
        if parameter_name == 'jwt_secret_key':
            # Try multiple environment variable names for secret key
            env_secret = (
                os.environ.get('JWT_SECRET_KEY') or
                os.environ.get('JWT_SECRET') or
                os.environ.get('APP_SECRET_KEY') or
                os.environ.get('SECRET_KEY')
            )
            if env_secret:
                if len(env_secret) < JWT_DEFAULT_CONFIG['jwt_minimum_secret_length']:
                    logger.warning(f"JWT secret key from environment is too short: {len(env_secret)} characters")
                return env_secret
        
        # Try configuration system
        config_value = get_configuration_parameter(parameter_name, default_value)
        if config_value is not None:
            return config_value
        
        # Try JWT defaults
        if parameter_name in JWT_DEFAULT_CONFIG:
            return JWT_DEFAULT_CONFIG[parameter_name]
        
        # Return provided default
        return default_value
        
    except Exception as e:
        logger.error(f"Failed to get JWT configuration {parameter_name}: {str(e)}")
        return default_value

def validate_jwt_configuration() -> Dict[str, Any]:
    """
    Validate JWT configuration for security compliance.
    
    Returns:
        Dictionary with validation results and recommendations
    """
    try:
        validation_result = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'security_score': 100,
            'recommendations': []
        }
        
        # Validate JWT secret key
        secret_key = get_jwt_configuration('jwt_secret_key')
        if not secret_key:
            validation_result['errors'].append('JWT secret key not configured')
            validation_result['valid'] = False
            validation_result['security_score'] -= 50
        elif secret_key == JWT_DEFAULT_CONFIG['fallback_jwt_secret']:
            validation_result['errors'].append('Using insecure fallback JWT secret key')
            validation_result['valid'] = False
            validation_result['security_score'] -= 40
        elif len(secret_key) < JWT_DEFAULT_CONFIG['jwt_minimum_secret_length']:
            validation_result['warnings'].append(f'JWT secret key is short: {len(secret_key)} characters')
            validation_result['security_score'] -= 20
        
        # Validate algorithm configuration
        algorithm = get_jwt_configuration('jwt_algorithm', 'HS256')
        whitelist = get_jwt_configuration('jwt_algorithm_whitelist', ['HS256'])
        
        if algorithm not in whitelist:
            validation_result['errors'].append(f'JWT algorithm {algorithm} not in whitelist')
            validation_result['valid'] = False
            validation_result['security_score'] -= 30
        
        if 'none' in whitelist or algorithm == 'none':
            validation_result['errors'].append('Insecure "none" algorithm allowed')
            validation_result['valid'] = False
            validation_result['security_score'] -= 50
        
        # Validate timing configuration
        clock_skew = get_jwt_configuration('jwt_clock_skew_seconds', 300)
        if clock_skew > 600:  # More than 10 minutes
            validation_result['warnings'].append('JWT clock skew tolerance is very high')
            validation_result['security_score'] -= 10
        
        # Validate claims configuration
        required_claims = get_jwt_configuration('jwt_required_claims', {})
        if not required_claims.get('exp', False):
            validation_result['errors'].append('JWT expiration claim not required')
            validation_result['valid'] = False
            validation_result['security_score'] -= 25
        
        # Validate Alexa configuration
        alexa_app_id = get_jwt_configuration('alexa_application_id', '')
        if not alexa_app_id:
            validation_result['warnings'].append('Alexa application ID not configured')
            validation_result['security_score'] -= 5
        
        # Security recommendations based on score
        if validation_result['security_score'] < 70:
            validation_result['recommendations'].append('Critical security issues detected - immediate action required')
        elif validation_result['security_score'] < 90:
            validation_result['recommendations'].append('Security improvements recommended')
        else:
            validation_result['recommendations'].append('JWT configuration meets security standards')
        
        return validation_result
        
    except Exception as e:
        logger.error(f"JWT configuration validation failed: {str(e)}")
        return {
            'valid': False,
            'errors': [f'Validation error: {str(e)}'],
            'security_score': 0,
            'recommendations': ['Manual configuration review required']
        }

def set_jwt_configuration(parameter_name: str, value: Any) -> bool:
    """
    Set JWT configuration parameter with validation.
    
    Args:
        parameter_name: Name of the configuration parameter
        value: Value to set
        
    Returns:
        True if successfully set, False otherwise
    """
    try:
        # Validate sensitive parameters
        if parameter_name == 'jwt_secret_key':
            if not isinstance(value, str):
                logger.error("JWT secret key must be a string")
                return False
            
            if len(value) < JWT_DEFAULT_CONFIG['jwt_minimum_secret_length']:
                logger.error(f"JWT secret key too short: {len(value)} characters")
                return False
        
        elif parameter_name == 'jwt_algorithm':
            whitelist = get_jwt_configuration('jwt_algorithm_whitelist', ['HS256'])
            if value not in whitelist:
                logger.error(f"JWT algorithm {value} not in whitelist")
                return False
        
        elif parameter_name == 'jwt_algorithm_whitelist':
            if 'none' in value:
                logger.error("Cannot add insecure 'none' algorithm to whitelist")
                return False
        
        # Set the configuration
        return set_configuration_parameter(parameter_name, value)
        
    except Exception as e:
        logger.error(f"Failed to set JWT configuration {parameter_name}: {str(e)}")
        return False

def get_jwt_security_status() -> Dict[str, Any]:
    """
    Get comprehensive JWT security status and configuration summary.
    
    Returns:
        Dictionary with JWT security status information
    """
    try:
        validation = validate_jwt_configuration()
        
        status = {
            'jwt_enabled': True,
            'security_score': validation['security_score'],
            'configuration_valid': validation['valid'],
            'algorithm': get_jwt_configuration('jwt_algorithm', 'HS256'),
            'clock_skew_seconds': get_jwt_configuration('jwt_clock_skew_seconds', 300),
            'required_claims': get_jwt_configuration('jwt_required_claims', {}),
            'strict_validation': get_jwt_configuration('jwt_strict_validation', True),
            'cache_enabled': get_jwt_configuration('jwt_cache_enabled', True),
            'rate_limiting_enabled': get_jwt_configuration('jwt_rate_limit_enabled', True),
            'alexa_integration': {
                'application_id_configured': bool(get_jwt_configuration('alexa_application_id', '')),
                'jwt_validation_enabled': get_jwt_configuration('alexa_jwt_validation', True),
                'require_access_token': get_jwt_configuration('alexa_require_access_token', False)
            },
            'security_headers_enabled': get_jwt_configuration('security_headers_enabled', True),
            'errors': validation['errors'],
            'warnings': validation['warnings'],
            'recommendations': validation['recommendations']
        }
        
        return status
        
    except Exception as e:
        logger.error(f"Failed to get JWT security status: {str(e)}")
        return {
            'jwt_enabled': False,
            'error': str(e),
            'security_score': 0
        }

# ===== SECTION 3: BACKWARD COMPATIBILITY AND GATEWAY INTEGRATION =====

def get_parameter(parameter_name: str, default_value: Any = None) -> Any:
    """
    Enhanced parameter access with JWT configuration support.
    Maintains backward compatibility with existing get_parameter function.
    """
    try:
        # Check if this is a JWT-specific parameter
        if parameter_name.startswith('jwt_') or parameter_name in JWT_DEFAULT_CONFIG:
            return get_jwt_configuration(parameter_name, default_value)
        
        # Fall back to existing configuration system
        return get_configuration_parameter(parameter_name, default_value)
        
    except Exception as e:
        logger.error(f"Failed to get parameter {parameter_name}: {str(e)}")
        return default_value

# ===== SECTION 4: INITIALIZATION AND VALIDATION =====

def initialize_jwt_configuration() -> bool:
    """
    Initialize JWT configuration with security validation.
    
    Returns:
        True if initialization successful, False otherwise
    """
    try:
        logger.info("Initializing JWT configuration...")
        
        # Validate current configuration
        validation = validate_jwt_configuration()
        
        if not validation['valid']:
            logger.error("JWT configuration validation failed:")
            for error in validation['errors']:
                logger.error(f"  - {error}")
            return False
        
        if validation['warnings']:
            logger.warning("JWT configuration warnings:")
            for warning in validation['warnings']:
                logger.warning(f"  - {warning}")
        
        logger.info(f"JWT configuration initialized - Security score: {validation['security_score']}/100")
        return True
        
    except Exception as e:
        logger.error(f"JWT configuration initialization failed: {str(e)}")
        return False

# EOF
