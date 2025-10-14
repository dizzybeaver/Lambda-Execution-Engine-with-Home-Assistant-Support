"""
security_jwt_validation.py
Version: 2025.10.13.01
Description: JWT validation with AWS Lambda compatible absolute imports

Copyright 2025 Joseph Hersey

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

import base64
import json
import hmac
import hashlib
import time
from typing import Dict, Any, Optional, Union, List

# ✅ CORRECT: Absolute imports from gateway
from gateway import (
    cache_get, cache_set,
    get_singleton, register_singleton,
    create_success_response, create_error_response, generate_correlation_id,
    log_info, log_error, log_warning,
    get_parameter, set_parameter
)

# JWT-specific constants
JWT_ALGORITHM_WHITELIST = ['HS256', 'HS384', 'HS512']
JWT_CLOCK_SKEW_SECONDS = 300  # 5 minutes clock skew tolerance
JWT_CACHE_PREFIX = "jwt_"

def validate_jwt_signature(token: str, secret_key: str, algorithm: str = 'HS256') -> Dict[str, Any]:
    """
    Validate JWT signature with proper cryptographic verification.
    
    Args:
        token: JWT token string
        secret_key: Secret key for signature verification
        algorithm: JWT algorithm (must be in whitelist)
        
    Returns:
        Dictionary with validation results and decoded payload
    """
    try:
        # Check token cache first
        token_hash = hashlib.sha256(token.encode()).hexdigest()[:16]
        cache_key = f"{JWT_CACHE_PREFIX}validated_{token_hash}"
        cached_result = cache_get(cache_key)
        if cached_result is not None:
            return cached_result
        
        validation_result = {
            'valid': False,
            'payload': None,
            'header': None,
            'signature_valid': False,
            'expired': True,
            'errors': [],
            'exp': None,
            'iat': None,
            'nbf': None
        }
        
        # Basic token format validation
        if not token or not isinstance(token, str):
            validation_result['errors'].append('Token is empty or invalid type')
            return validation_result
        
        # Split JWT into parts
        parts = token.split('.')
        if len(parts) != 3:
            validation_result['errors'].append('Invalid JWT format - must have 3 parts')
            return validation_result
        
        header_b64, payload_b64, signature_b64 = parts
        
        # Decode header with proper error handling
        try:
            header = _decode_jwt_part(header_b64)
            validation_result['header'] = header
        except Exception as e:
            validation_result['errors'].append(f'Invalid JWT header: {str(e)}')
            return validation_result
        
        # Validate algorithm
        header_alg = header.get('alg', '')
        if header_alg not in JWT_ALGORITHM_WHITELIST:
            validation_result['errors'].append(f'Unsupported algorithm: {header_alg}')
            return validation_result
        
        if algorithm != header_alg:
            validation_result['errors'].append(f'Algorithm mismatch: expected {algorithm}, got {header_alg}')
            return validation_result
        
        # Decode payload with proper error handling
        try:
            payload = _decode_jwt_part(payload_b64)
            validation_result['payload'] = payload
        except Exception as e:
            validation_result['errors'].append(f'Invalid JWT payload: {str(e)}')
            return validation_result
        
        # Verify signature
        expected_signature = _create_jwt_signature(header_b64, payload_b64, secret_key, algorithm)
        
        try:
            provided_signature = base64.urlsafe_b64decode(_add_padding(signature_b64))
            signature_valid = hmac.compare_digest(expected_signature, provided_signature)
            validation_result['signature_valid'] = signature_valid
            
            if not signature_valid:
                validation_result['errors'].append('Invalid signature')
                return validation_result
        except Exception as e:
            validation_result['errors'].append(f'Signature verification failed: {str(e)}')
            return validation_result
        
        # Extract time claims
        exp = payload.get('exp')
        iat = payload.get('iat')
        nbf = payload.get('nbf')
        
        validation_result['exp'] = exp
        validation_result['iat'] = iat
        validation_result['nbf'] = nbf
        
        current_time = int(time.time())
        
        # Validate expiration
        if exp is not None:
            if not isinstance(exp, (int, float)):
                validation_result['errors'].append('Invalid exp claim type')
                return validation_result
            
            if current_time > (exp + JWT_CLOCK_SKEW_SECONDS):
                validation_result['expired'] = True
                validation_result['errors'].append('Token expired (exp)')
                return validation_result
            else:
                validation_result['expired'] = False
        else:
            validation_result['expired'] = False
        
        # Validate not before
        if nbf is not None:
            if not isinstance(nbf, (int, float)):
                validation_result['errors'].append('Invalid nbf claim type')
                return validation_result
            
            if current_time < (nbf - JWT_CLOCK_SKEW_SECONDS):
                validation_result['errors'].append('Token not yet valid (nbf)')
                return validation_result
        
        # Validate issued at
        if iat is not None:
            if not isinstance(iat, (int, float)):
                validation_result['errors'].append('Invalid iat claim type')
                return validation_result
            
            if iat > (current_time + JWT_CLOCK_SKEW_SECONDS):
                validation_result['errors'].append('Token issued in future (iat)')
                return validation_result
        
        # All validations passed
        validation_result['valid'] = True
        
        # Cache successful validation (shorter TTL for security)
        cache_ttl = min(300, max(60, exp - current_time)) if exp else 300
        cache_set(cache_key, validation_result, ttl=cache_ttl)
        
        return validation_result
        
    except Exception as e:
        log_error(f"JWT validation failed: {str(e)}", error=e)
        return {
            'valid': False,
            'errors': [f'JWT validation error: {str(e)}'],
            'signature_valid': False,
            'expired': True
        }

def validate_jwt_claims(payload: Dict[str, Any], required_claims: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Validate JWT claims against required values.
    
    Args:
        payload: Decoded JWT payload
        required_claims: Dictionary of required claim values
        
    Returns:
        Dictionary with claim validation results
    """
    try:
        validation_result = {
            'valid': True,
            'errors': [],
            'missing_claims': [],
            'invalid_claims': []
        }
        
        if not payload or not isinstance(payload, dict):
            validation_result['valid'] = False
            validation_result['errors'].append('Invalid payload')
            return validation_result
        
        # Get required claims from config
        if required_claims is None:
            required_claims = get_parameter('jwt_required_claims', {})
        
        # Validate required claims
        for claim_name, expected_value in required_claims.items():
            if claim_name not in payload:
                validation_result['missing_claims'].append(claim_name)
                validation_result['valid'] = False
                continue
            
            actual_value = payload[claim_name]
            
            # Handle different validation types
            if isinstance(expected_value, list):
                # Audience can be string or list
                if claim_name == 'aud':
                    if isinstance(actual_value, str):
                        actual_value = [actual_value]
                    if not isinstance(actual_value, list):
                        validation_result['invalid_claims'].append(f'{claim_name}: must be string or array')
                        validation_result['valid'] = False
                        continue
                    
                    if not any(aud in expected_value for aud in actual_value):
                        validation_result['invalid_claims'].append(f'{claim_name}: no matching audience')
                        validation_result['valid'] = False
                else:
                    if actual_value not in expected_value:
                        validation_result['invalid_claims'].append(f'{claim_name}: value not in allowed list')
                        validation_result['valid'] = False
            else:
                if actual_value != expected_value:
                    validation_result['invalid_claims'].append(f'{claim_name}: value mismatch')
                    validation_result['valid'] = False
        
        return validation_result
        
    except Exception as e:
        log_error(f"JWT claims validation failed: {str(e)}", error=e)
        return {
            'valid': False,
            'errors': [f'Claims validation error: {str(e)}']
        }

def _decode_jwt_part(encoded_part: str) -> Dict[str, Any]:
    """Decode JWT part with proper padding and error handling."""
    try:
        # Add padding if needed
        padded = _add_padding(encoded_part)
        
        # Decode base64
        decoded_bytes = base64.urlsafe_b64decode(padded)
        
        # Parse JSON
        decoded_json = json.loads(decoded_bytes.decode('utf-8'))
        
        return decoded_json
        
    except Exception as e:
        raise ValueError(f"Failed to decode JWT part: {str(e)}")

def _add_padding(encoded_string: str) -> str:
    """Add proper base64 padding."""
    missing_padding = len(encoded_string) % 4
    if missing_padding:
        encoded_string += '=' * (4 - missing_padding)
    return encoded_string

def _create_jwt_signature(header_b64: str, payload_b64: str, secret_key: str, algorithm: str) -> bytes:
    """Create JWT signature using specified algorithm."""
    try:
        # Create signing input
        signing_input = f"{header_b64}.{payload_b64}".encode('utf-8')
        
        # Select hash algorithm
        if algorithm == 'HS256':
            hash_func = hashlib.sha256
        elif algorithm == 'HS384':
            hash_func = hashlib.sha384
        elif algorithm == 'HS512':
            hash_func = hashlib.sha512
        else:
            raise ValueError(f"Unsupported algorithm: {algorithm}")
        
        # Create HMAC signature
        signature = hmac.new(
            secret_key.encode('utf-8'),
            signing_input,
            hash_func
        ).digest()
        
        return signature
        
    except Exception as e:
        raise ValueError(f"Failed to create JWT signature: {str(e)}")

def get_jwt_secret_key() -> str:
    """Get JWT secret key from configuration with proper error handling."""
    try:
        # Try to get from config
        secret_key = get_parameter('jwt_secret_key')
        
        if not secret_key:
            # Fallback to environment or generate warning
            log_error("JWT secret key not configured - using fallback")
            secret_key = get_parameter('fallback_jwt_secret', 'INSECURE_FALLBACK_KEY_CHANGE_IN_PRODUCTION')
        
        if len(secret_key) < 32:
            log_error("JWT secret key is too short - minimum 32 characters recommended")
        
        return secret_key
        
    except Exception as e:
        log_error(f"Failed to get JWT secret key: {str(e)}", error=e)
        return 'EMERGENCY_FALLBACK_KEY_CHANGE_IMMEDIATELY'

# EOF
