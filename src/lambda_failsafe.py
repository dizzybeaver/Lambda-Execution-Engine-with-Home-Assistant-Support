"""
lambda_failsafe.py - Emergency Failsafe Handler
Version: 2025.10.15.02
Description: Standalone failsafe for Home Assistant Alexa integration.
             COMPLETELY INDEPENDENT - No SUGA imports, no extensions.
             Now includes basic in-memory caching.

Copyright 2025 Joseph Hersey
Licensed under Apache 2.0 (see LICENSE).

USAGE:
  Set these Lambda environment variables to activate:
    LEE_FAILSAFE_ENABLED=true
    HOME_ASSISTANT_URL=http://192.168.1.100:8123
    HOME_ASSISTANT_TOKEN=your_long_lived_token
    HOME_ASSISTANT_VERIFY_SSL=false  (optional, default: true)
    DEBUG_MODE=false  (optional, default: false)
    FAILSAFE_CACHE_ENABLED=true  (optional, default: true)
"""

import os
import json
import logging
import time
from typing import Any, Dict, Optional
import urllib3

# Initialize logger
_debug = os.getenv('DEBUG_MODE', 'false').lower() == 'true'
_logger = logging.getLogger('LEE-Failsafe')
_logger.setLevel(logging.DEBUG if _debug else logging.INFO)


# ===== SIMPLE CACHE IMPLEMENTATION =====

class FailsafeCache:
    """
    Simple in-memory cache for failsafe mode.
    Completely self-contained - no external dependencies.
    """
    
    def __init__(self):
        self._cache = {}
        self._enabled = os.getenv('FAILSAFE_CACHE_ENABLED', 'true').lower() == 'true'
        self._stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'expired': 0
        }
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache if not expired."""
        if not self._enabled:
            return None
        
        if key not in self._cache:
            self._stats['misses'] += 1
            return None
        
        entry = self._cache[key]
        current_time = time.time()
        
        # Check if expired
        if current_time - entry['timestamp'] > entry['ttl']:
            del self._cache[key]
            self._stats['expired'] += 1
            self._stats['misses'] += 1
            return None
        
        self._stats['hits'] += 1
        _logger.debug(f"Cache HIT: {key}")
        return entry['value']
    
    def set(self, key: str, value: Any, ttl: int = 300):
        """Set value in cache with TTL."""
        if not self._enabled:
            return
        
        self._cache[key] = {
            'value': value,
            'timestamp': time.time(),
            'ttl': ttl
        }
        self._stats['sets'] += 1
        _logger.debug(f"Cache SET: {key} (TTL: {ttl}s)")
    
    def clear(self):
        """Clear all cache entries."""
        count = len(self._cache)
        self._cache.clear()
        _logger.info(f"Cache cleared: {count} entries removed")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_requests = self._stats['hits'] + self._stats['misses']
        hit_rate = (self._stats['hits'] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'enabled': self._enabled,
            'entries': len(self._cache),
            'hits': self._stats['hits'],
            'misses': self._stats['misses'],
            'sets': self._stats['sets'],
            'expired': self._stats['expired'],
            'hit_rate_percent': round(hit_rate, 2)
        }


# Global cache instance
_cache = FailsafeCache()


def _generate_cache_key(directive: Dict[str, Any], token: str) -> str:
    """Generate cache key from directive and token."""
    header = directive.get('header', {})
    namespace = header.get('namespace', 'Unknown')
    name = header.get('name', 'Unknown')
    
    # Use first 8 chars of token for key uniqueness per user
    token_prefix = token[:8] if token else 'notoken'
    
    # For Discovery, key is just namespace+name+token
    if namespace == 'Alexa.Discovery' and name == 'Discover':
        return f"discovery:{token_prefix}"
    
    # For ReportState, include endpoint ID
    endpoint = directive.get('endpoint', {})
    endpoint_id = endpoint.get('endpointId', 'unknown')
    
    return f"{namespace}:{name}:{endpoint_id}:{token_prefix}"


def _get_cache_ttl(directive: Dict[str, Any]) -> int:
    """Determine appropriate TTL for directive type."""
    header = directive.get('header', {})
    namespace = header.get('namespace', '')
    name = header.get('name', '')
    
    # Discovery responses rarely change - cache longer
    if namespace == 'Alexa.Discovery' and name == 'Discover':
        return 300  # 5 minutes
    
    # State reports change frequently - cache briefly
    if 'ReportState' in name:
        return 30  # 30 seconds
    
    # Default for other commands - don't cache
    return 0


# ===== MAIN HANDLER =====

def lambda_handler(event, context):
    """
    Emergency failsafe handler for Home Assistant Alexa integration.
    Routes all requests directly to Home Assistant's /api/alexa/smart_home endpoint.
    Now includes basic caching for improved performance.
    """
    _logger.info("FAILSAFE MODE ACTIVE - Routing to Home Assistant directly")
    _logger.debug(f"Event: {json.dumps(event, default=str)}")

    # Load configuration from environment
    base_url = os.getenv('HOME_ASSISTANT_URL')
    if not base_url:
        _logger.error("HOME_ASSISTANT_URL not configured")
        return _create_error_response(
            'INVALID_CONFIGURATION',
            'HOME_ASSISTANT_URL environment variable not set'
        )
    
    base_url = base_url.strip("/")
    _logger.info(f"Using Home Assistant URL: {base_url}")

    # Validate Alexa directive structure
    directive = event.get('directive')
    if not directive:
        _logger.error("Missing directive in request")
        return _create_error_response(
            'INVALID_DIRECTIVE',
            'Malformatted request - missing directive'
        )
    
    # Validate payload version
    payload_version = directive.get('header', {}).get('payloadVersion')
    if payload_version != '3':
        _logger.error(f"Unsupported payload version: {payload_version}")
        return _create_error_response(
            'INVALID_DIRECTIVE',
            'Only payloadVersion 3 is supported'
        )
    
    # Extract access token
    token = _extract_token(directive)
    if not token:
        _logger.error("No access token found in request")
        return _create_error_response(
            'INVALID_AUTHORIZATION_CREDENTIAL',
            'Access token not found in request'
        )
    
    _logger.debug("Access token extracted successfully")
    
    # Check cache first
    cache_key = _generate_cache_key(directive, token)
    cached_response = _cache.get(cache_key)
    if cached_response:
        _logger.info(f"Returning cached response for {cache_key}")
        return cached_response
    
    # Forward to Home Assistant
    api_endpoint = f"{base_url}/api/alexa/smart_home"
    _logger.info(f"Forwarding request to: {api_endpoint}")
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # Configure SSL verification
    verify_ssl = os.getenv('HOME_ASSISTANT_VERIFY_SSL', 'true').lower() == 'true'
    
    try:
        http = urllib3.PoolManager(
            cert_reqs='CERT_REQUIRED' if verify_ssl else 'CERT_NONE',
            timeout=urllib3.Timeout(connect=5.0, read=10.0)
        )
        
        if not verify_ssl:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        response = http.request(
            'POST',
            api_endpoint,
            body=json.dumps(event).encode('utf-8'),
            headers=headers
        )
        
        if response.status == 200:
            response_data = json.loads(response.data.decode('utf-8'))
            _logger.info("Successfully received response from Home Assistant")
            _logger.debug(f"Response: {json.dumps(response_data, default=str)}")
            
            # Cache the response if appropriate
            ttl = _get_cache_ttl(directive)
            if ttl > 0:
                _cache.set(cache_key, response_data, ttl)
                _logger.info(f"Cached response with TTL: {ttl}s")
            
            # Log cache stats periodically
            if _debug:
                stats = _cache.get_stats()
                _logger.debug(f"Cache stats: {stats}")
            
            return response_data
        else:
            _logger.error(f"Home Assistant returned error: {response.status}")
            _logger.error(f"Response: {response.data.decode('utf-8')}")
            return _create_error_response(
                'INTERNAL_ERROR',
                f'Home Assistant returned status {response.status}'
            )
    
    except urllib3.exceptions.TimeoutError:
        _logger.error("Request to Home Assistant timed out")
        return _create_error_response(
            'INTERNAL_ERROR',
            'Connection to Home Assistant timed out'
        )
    except urllib3.exceptions.HTTPError as e:
        _logger.error(f"HTTP error communicating with Home Assistant: {str(e)}")
        return _create_error_response(
            'INTERNAL_ERROR',
            f'HTTP error: {str(e)}'
        )
    except Exception as e:
        _logger.error(f"Unexpected error: {str(e)}")
        return _create_error_response(
            'INTERNAL_ERROR',
            f'Unexpected error: {str(e)}'
        )


def _extract_token(directive: Dict[str, Any]) -> Optional[str]:
    scope = directive.get('endpoint', {}).get('scope')
    if scope and scope.get('type') == 'BearerToken':
        token = scope.get('token')
        if token:
            return token
    
    # Try payload.grantee (Linking directive)
    grantee = directive.get('payload', {}).get('grantee')
    if grantee and grantee.get('type') == 'BearerToken':
        token = grantee.get('token')
        if token:
            return token
    
    # Try payload.scope (Discovery directive)
    payload_scope = directive.get('payload', {}).get('scope')
    if payload_scope and payload_scope.get('type') == 'BearerToken':
        token = payload_scope.get('token')
        if token:
            return token
    
    # Fall back to environment variable in debug mode
    if _debug:
        env_token = os.getenv('HOME_ASSISTANT_TOKEN')
        if env_token:
            _logger.warning("Using token from HOME_ASSISTANT_TOKEN environment variable (debug mode)")
            return env_token
    
    return None


def _create_error_response(error_type: str, message: str) -> dict:
    """Create Alexa error response."""
    return {
        'event': {
            'header': {
                'namespace': 'Alexa',
                'name': 'ErrorResponse',
                'messageId': 'failsafe-error',
                'payloadVersion': '3'
            },
            'payload': {
                'type': error_type,
                'message': message
            }
        }
    }


# EOF
