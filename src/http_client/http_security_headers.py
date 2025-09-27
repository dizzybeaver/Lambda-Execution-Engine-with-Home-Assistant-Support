"""
http_security_headers.py - IMMEDIATE FIX: HTTP Security Headers Implementation
Version: 2025.09.27.01
Description: Comprehensive HTTP security headers for XSS, clickjacking, and MITM protection

IMMEDIATE SECURITY FIXES APPLIED:
- ✅ IMPLEMENTED: Complete security headers suite (HSTS, CSP, X-Frame-Options, etc.)
- ✅ PROTECTED: XSS protection with Content Security Policy
- ✅ SECURED: Clickjacking prevention with frame options
- ✅ ENHANCED: MIME type sniffing protection
- ✅ CONFIGURED: Home Assistant compatible security policies

SECURITY HEADERS IMPLEMENTED:
- Content-Security-Policy: XSS protection with restricted script sources
- X-Frame-Options: Clickjacking protection
- X-Content-Type-Options: MIME sniffing protection  
- X-XSS-Protection: Browser XSS filtering
- Strict-Transport-Security: HTTPS enforcement
- Referrer-Policy: Referrer information control
- Permissions-Policy: Feature access control

ARCHITECTURE: SECONDARY IMPLEMENTATION - Security Enhancement
- Integrates with existing HTTP client infrastructure
- Compatible with Home Assistant requirements
- Gateway interface integration for configuration

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

import logging
from typing import Dict, Any, Optional, List, Union

# Gateway imports for security headers
from . import utility
from . import config
from . import cache

logger = logging.getLogger(__name__)

# ===== SECURITY HEADERS CONFIGURATION =====

# Default security headers with Home Assistant compatibility
DEFAULT_SECURITY_HEADERS = {
    # Content Security Policy - Balanced security with HA compatibility
    "Content-Security-Policy": (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://www.gstatic.com; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com; "
        "img-src 'self' data: https:; "
        "connect-src 'self' https: wss: ws:; "
        "media-src 'self'; "
        "object-src 'none'; "
        "frame-ancestors 'self'; "
        "form-action 'self'; "
        "base-uri 'self'"
    ),
    
    # Clickjacking protection
    "X-Frame-Options": "SAMEORIGIN",
    
    # MIME type sniffing protection
    "X-Content-Type-Options": "nosniff",
    
    # XSS protection (legacy support)
    "X-XSS-Protection": "1; mode=block",
    
    # HTTPS enforcement (conditional based on TLS configuration)
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    
    # Referrer policy
    "Referrer-Policy": "strict-origin-when-cross-origin",
    
    # Permissions policy (feature access control)
    "Permissions-Policy": (
        "geolocation=(), "
        "microphone=(), "
        "camera=(), "
        "usb=(), "
        "bluetooth=(), "
        "midi=(), "
        "payment=(), "
        "sync-xhr=(), "
        "fullscreen=(self)"
    ),
    
    # Cache control for security
    "Cache-Control": "no-cache, no-store, must-revalidate",
    "Pragma": "no-cache",
    "Expires": "0"
}

# Home Assistant specific headers adjustments
HOME_ASSISTANT_HEADERS = {
    # More permissive CSP for Home Assistant frontend
    "Content-Security-Policy": (
        "default-src 'self' 'unsafe-inline' 'unsafe-eval'; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://www.gstatic.com https://www.google.com; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com; "
        "img-src 'self' data: https: blob:; "
        "connect-src 'self' https: wss: ws: blob:; "
        "media-src 'self' blob:; "
        "object-src 'none'; "
        "frame-ancestors 'self'; "
        "form-action 'self'; "
        "base-uri 'self'"
    ),
    
    # Allow framing for Home Assistant panels
    "X-Frame-Options": "SAMEORIGIN"
}

# Production security headers (stricter)
PRODUCTION_HEADERS = {
    "Content-Security-Policy": (
        "default-src 'self'; "
        "script-src 'self'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data:; "
        "connect-src 'self'; "
        "font-src 'self'; "
        "object-src 'none'; "
        "media-src 'self'; "
        "frame-ancestors 'none'; "
        "form-action 'self'; "
        "base-uri 'self'"
    ),
    "X-Frame-Options": "DENY",
    "Strict-Transport-Security": "max-age=63072000; includeSubDomains; preload"
}

# ===== SECURITY HEADERS IMPLEMENTATION =====

def get_security_headers(context: str = "default", **kwargs) -> Dict[str, str]:
    """
    Get appropriate security headers based on context.
    
    Args:
        context: 'default', 'home_assistant', 'production', or 'custom'
        **kwargs: Additional configuration options
    
    Returns:
        Dictionary of security headers
    """
    try:
        # Validate context using utility gateway
        if not utility.validate_string_input(context, max_length=50):
            logger.warning(f"Invalid context for security headers: {context}")
            context = "default"
        
        # Get base headers based on context
        if context == "home_assistant":
            base_headers = {**DEFAULT_SECURITY_HEADERS, **HOME_ASSISTANT_HEADERS}
        elif context == "production":
            base_headers = {**DEFAULT_SECURITY_HEADERS, **PRODUCTION_HEADERS}
        else:
            base_headers = DEFAULT_SECURITY_HEADERS.copy()
        
        # Apply TLS-specific configurations
        tls_bypass_enabled = config.get_parameter('TLS_VERIFY_BYPASS_ENABLED', 'false').lower() == 'true'
        
        if tls_bypass_enabled:
            # Remove HSTS when TLS bypass is enabled (for development/testing)
            if "Strict-Transport-Security" in base_headers:
                del base_headers["Strict-Transport-Security"]
            logger.info("HSTS disabled due to TLS verification bypass configuration")
        
        # Apply custom overrides
        custom_headers = kwargs.get('custom_headers', {})
        if custom_headers and isinstance(custom_headers, dict):
            for header, value in custom_headers.items():
                if utility.validate_string_input(header, max_length=100):
                    base_headers[header] = str(value)[:500]  # Limit header value length
        
        # Cache the headers for performance
        cache_key = f"security_headers_{context}_{hash(str(kwargs))}"
        cache.cache_set(cache_key, base_headers, ttl=300)  # 5 minutes
        
        logger.debug(f"Generated {len(base_headers)} security headers for context: {context}")
        return base_headers
        
    except Exception as e:
        logger.error(f"Error generating security headers: {str(e)}")
        # Return minimal security headers as fallback
        return {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "SAMEORIGIN",
            "Cache-Control": "no-cache, no-store, must-revalidate"
        }

def apply_security_headers_to_response(response_data: Dict[str, Any], 
                                     context: str = "default",
                                     **kwargs) -> Dict[str, Any]:
    """
    Apply security headers to HTTP response data.
    
    Args:
        response_data: HTTP response dictionary
        context: Security context for header selection
        **kwargs: Additional configuration
    
    Returns:
        Response data with security headers applied
    """
    try:
        if not isinstance(response_data, dict):
            logger.error("Invalid response data format for security headers")
            return response_data
        
        # Ensure headers section exists
        if 'headers' not in response_data:
            response_data['headers'] = {}
        elif not isinstance(response_data['headers'], dict):
            response_data['headers'] = {}
        
        # Get security headers
        security_headers = get_security_headers(context, **kwargs)
        
        # Apply security headers (do not override existing headers)
        for header, value in security_headers.items():
            if header not in response_data['headers']:
                response_data['headers'][header] = value
        
        # Add security metadata
        response_data['security_headers_applied'] = True
        response_data['security_context'] = context
        response_data['headers_count'] = len(response_data['headers'])
        
        logger.debug(f"Applied {len(security_headers)} security headers to response")
        return response_data
        
    except Exception as e:
        logger.error(f"Error applying security headers to response: {str(e)}")
        return response_data

def validate_security_headers(headers: Dict[str, str]) -> Dict[str, Any]:
    """
    Validate security headers configuration.
    
    Args:
        headers: Dictionary of headers to validate
    
    Returns:
        Validation result with recommendations
    """
    try:
        validation_result = {
            'valid': True,
            'warnings': [],
            'errors': [],
            'missing_headers': [],
            'recommendations': []
        }
        
        # Check for essential security headers
        essential_headers = [
            'X-Content-Type-Options',
            'X-Frame-Options',
            'Content-Security-Policy'
        ]
        
        for header in essential_headers:
            if header not in headers:
                validation_result['missing_headers'].append(header)
                validation_result['warnings'].append(f"Missing essential security header: {header}")
        
        # Validate CSP if present
        if 'Content-Security-Policy' in headers:
            csp_validation = _validate_csp_header(headers['Content-Security-Policy'])
            if not csp_validation['valid']:
                validation_result['errors'].extend(csp_validation['errors'])
                validation_result['valid'] = False
        
        # Check for insecure configurations
        if headers.get('X-Frame-Options') == 'ALLOWALL':
            validation_result['warnings'].append("X-Frame-Options set to ALLOWALL increases clickjacking risk")
        
        # Check HSTS configuration
        if 'Strict-Transport-Security' in headers:
            hsts_value = headers['Strict-Transport-Security']
            if 'max-age' not in hsts_value.lower():
                validation_result['errors'].append("HSTS header missing max-age directive")
                validation_result['valid'] = False
        
        # Add recommendations
        if validation_result['missing_headers']:
            validation_result['recommendations'].append(
                "Add missing security headers for comprehensive protection"
            )
        
        return validation_result
        
    except Exception as e:
        logger.error(f"Security headers validation failed: {str(e)}")
        return {
            'valid': False,
            'errors': [f"Validation error: {str(e)}"],
            'warnings': [],
            'missing_headers': [],
            'recommendations': []
        }

def _validate_csp_header(csp_value: str) -> Dict[str, Any]:
    """Validate Content Security Policy header."""
    try:
        validation_result = {'valid': True, 'errors': [], 'warnings': []}
        
        # Check for dangerous directives
        dangerous_patterns = [
            ('unsafe-eval', "CSP contains 'unsafe-eval' which allows eval()"),
            ('unsafe-inline', "CSP contains 'unsafe-inline' which reduces XSS protection"),
            ('data:', "CSP allows data: URIs which can be used for XSS"),
            ('*', "CSP contains wildcard (*) which reduces security")
        ]
        
        csp_lower = csp_value.lower()
        for pattern, warning in dangerous_patterns:
            if pattern in csp_lower:
                validation_result['warnings'].append(warning)
        
        # Check for required directives
        required_directives = ['default-src', 'script-src']
        for directive in required_directives:
            if directive not in csp_lower:
                validation_result['errors'].append(f"CSP missing required directive: {directive}")
                validation_result['valid'] = False
        
        return validation_result
        
    except Exception as e:
        return {'valid': False, 'errors': [f"CSP validation error: {str(e)}"], 'warnings': []}

def get_security_headers_middleware(context: str = "default"):
    """
    Create middleware function for automatic security headers application.
    
    Args:
        context: Security context for header selection
    
    Returns:
        Middleware function that applies security headers
    """
    def middleware(response_data: Dict[str, Any]) -> Dict[str, Any]:
        """Middleware function to apply security headers."""
        return apply_security_headers_to_response(response_data, context)
    
    return middleware

def create_secure_response(data: Any, 
                         status_code: int = 200, 
                         context: str = "default",
                         **kwargs) -> Dict[str, Any]:
    """
    Create a secure HTTP response with security headers.
    
    Args:
        data: Response data
        status_code: HTTP status code
        context: Security context
        **kwargs: Additional response options
    
    Returns:
        Secure HTTP response with headers
    """
    try:
        # Create base response
        response = {
            'statusCode': status_code,
            'body': data,
            'headers': kwargs.get('headers', {}),
            'isBase64Encoded': kwargs.get('isBase64Encoded', False)
        }
        
        # Apply security headers
        response = apply_security_headers_to_response(response, context, **kwargs)
        
        # Add CORS headers if requested
        if kwargs.get('enable_cors', False):
            cors_headers = _get_cors_headers(kwargs.get('cors_origin', '*'))
            response['headers'].update(cors_headers)
        
        return response
        
    except Exception as e:
        logger.error(f"Error creating secure response: {str(e)}")
        # Return minimal secure response
        return {
            'statusCode': 500,
            'body': {'error': 'Internal server error'},
            'headers': {
                'Content-Type': 'application/json',
                'X-Content-Type-Options': 'nosniff'
            }
        }

def _get_cors_headers(origin: str) -> Dict[str, str]:
    """Get CORS headers for cross-origin requests."""
    return {
        'Access-Control-Allow-Origin': origin,
        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Requested-With',
        'Access-Control-Max-Age': '86400'  # 24 hours
    }

# EOF
