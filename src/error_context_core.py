"""
Error Context Core - Error Context Management with Template Optimization
Version: 2025.10.02.01
Description: Error context creation and management with pre-compiled templates

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

import json
import time
import uuid
import os
from typing import Dict, Any, Optional, Union
from enum import Enum
import threading

# ===== ERROR CONTEXT TEMPLATES (Phase 3 Optimization) =====

_ERROR_CONTEXT_TEMPLATE = '{"interface":"%s","operation":"%s","correlation_id":"%s","timestamp":%f}'
_ERROR_CONTEXT_WITH_CODE = '{"interface":"%s","operation":"%s","correlation_id":"%s","timestamp":%f,"error_code":"%s"}'
_ERROR_CONTEXT_WITH_DETAILS = '{"interface":"%s","operation":"%s","correlation_id":"%s","timestamp":%f,"error_code":"%s","details":%s}'

_VALIDATION_ERROR_CONTEXT = '{"interface":"validation","operation":"validate_%s","correlation_id":"%s","timestamp":%f,"field":"%s"}'
_HTTP_ERROR_CONTEXT = '{"interface":"http","operation":"%s","correlation_id":"%s","timestamp":%f,"url":"%s","status_code":%d}'
_CACHE_ERROR_CONTEXT = '{"interface":"cache","operation":"%s","correlation_id":"%s","timestamp":%f,"key":"%s"}'
_HA_ERROR_CONTEXT = '{"interface":"homeassistant","operation":"%s","correlation_id":"%s","timestamp":%f,"entity_id":"%s"}'
_LAMBDA_ERROR_CONTEXT = '{"interface":"lambda","operation":"handler","correlation_id":"%s","timestamp":%f,"request_id":"%s"}'

_CORRELATION_PREFIX = None
_CORRELATION_COUNTER = 0
_CORRELATION_LOCK = threading.Lock()

_USE_ERROR_TEMPLATES = os.environ.get('USE_ERROR_TEMPLATES', 'true').lower() == 'true'

class ErrorSeverity(Enum):
    """Error severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ErrorCategory(Enum):
    """Error categories."""
    VALIDATION = "validation"
    HTTP = "http"
    CACHE = "cache"
    HOMEASSISTANT = "homeassistant"
    LAMBDA = "lambda"
    SECURITY = "security"
    CONFIGURATION = "configuration"
    GENERIC = "generic"

def generate_correlation_id_fast() -> str:
    """Fast correlation ID generation with template-based counter."""
    global _CORRELATION_PREFIX, _CORRELATION_COUNTER
    
    try:
        with _CORRELATION_LOCK:
            if _CORRELATION_PREFIX is None:
                _CORRELATION_PREFIX = str(uuid.uuid4())[:6]
            
            _CORRELATION_COUNTER += 1
            
            if _CORRELATION_COUNTER > 9999:
                _CORRELATION_COUNTER = 1
                _CORRELATION_PREFIX = str(uuid.uuid4())[:6]
            
            return f"{_CORRELATION_PREFIX}-{_CORRELATION_COUNTER:04d}"
            
    except Exception:
        return str(uuid.uuid4())[:12]

def create_error_context_fast(interface: str, operation: str, 
                             correlation_id: Optional[str] = None,
                             error_code: Optional[str] = None,
                             details: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Fast error context creation using templates."""
    try:
        if _USE_ERROR_TEMPLATES:
            corr_id = correlation_id or generate_correlation_id_fast()
            timestamp = time.time()
            
            if details and error_code:
                details_json = json.dumps(details)
                json_str = _ERROR_CONTEXT_WITH_DETAILS % (
                    interface, operation, corr_id, timestamp, error_code, details_json
                )
            elif error_code:
                json_str = _ERROR_CONTEXT_WITH_CODE % (
                    interface, operation, corr_id, timestamp, error_code
                )
            else:
                json_str = _ERROR_CONTEXT_TEMPLATE % (
                    interface, operation, corr_id, timestamp
                )
            
            return json.loads(json_str)
        else:
            return _create_error_context_legacy(interface, operation, correlation_id, error_code, details)
            
    except Exception:
        return _create_error_context_legacy(interface, operation, correlation_id, error_code, details)

def _create_error_context_legacy(interface: str, operation: str,
                                correlation_id: Optional[str],
                                error_code: Optional[str],
                                details: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Legacy dict-based error context creation."""
    context = {
        'interface': interface,
        'operation': operation,
        'correlation_id': correlation_id or generate_correlation_id_fast(),
        'timestamp': time.time()
    }
    
    if error_code:
        context['error_code'] = error_code
    
    if details:
        context['details'] = details
    
    return context

def create_validation_error_context(field: str, correlation_id: Optional[str] = None) -> Dict[str, Any]:
    """Create validation error context using specialized template."""
    try:
        if _USE_ERROR_TEMPLATES:
            corr_id = correlation_id or generate_correlation_id_fast()
            timestamp = time.time()
            
            json_str = _VALIDATION_ERROR_CONTEXT % (
                field, corr_id, timestamp, field
            )
            
            return json.loads(json_str)
        else:
            return create_error_context_fast("validation", f"validate_{field}", correlation_id)
            
    except Exception:
        return create_error_context_fast("validation", f"validate_{field}", correlation_id)

def create_http_error_context(operation: str, url: str, status_code: int, 
                             correlation_id: Optional[str] = None) -> Dict[str, Any]:
    """Create HTTP error context using specialized template."""
    try:
        if _USE_ERROR_TEMPLATES:
            corr_id = correlation_id or generate_correlation_id_fast()
            timestamp = time.time()
            
            json_str = _HTTP_ERROR_CONTEXT % (
                operation, corr_id, timestamp, url, status_code
            )
            
            return json.loads(json_str)
        else:
            return create_error_context_fast("http", operation, correlation_id, 
                                           details={"url": url, "status_code": status_code})
            
    except Exception:
        return create_error_context_fast("http", operation, correlation_id)

def create_cache_error_context(operation: str, key: str, 
                              correlation_id: Optional[str] = None) -> Dict[str, Any]:
    """Create cache error context using specialized template."""
    try:
        if _USE_ERROR_TEMPLATES:
            corr_id = correlation_id or generate_correlation_id_fast()
            timestamp = time.time()
            
            json_str = _CACHE_ERROR_CONTEXT % (
                operation, corr_id, timestamp, key
            )
            
            return json.loads(json_str)
        else:
            return create_error_context_fast("cache", operation, correlation_id, 
                                           details={"key": key})
            
    except Exception:
        return create_error_context_fast("cache", operation, correlation_id)

def create_ha_error_context(operation: str, entity_id: str, 
                           correlation_id: Optional[str] = None) -> Dict[str, Any]:
    """Create Home Assistant error context using specialized template."""
    try:
        if _USE_ERROR_TEMPLATES:
            corr_id = correlation_id or generate_correlation_id_fast()
            timestamp = time.time()
            
            json_str = _HA_ERROR_CONTEXT % (
                operation, corr_id, timestamp, entity_id
            )
            
            return json.loads(json_str)
        else:
            return create_error_context_fast("homeassistant", operation, correlation_id,
                                           details={"entity_id": entity_id})
            
    except Exception:
        return create_error_context_fast("homeassistant", operation, correlation_id)

def create_lambda_error_context(request_id: str, correlation_id: Optional[str] = None) -> Dict[str, Any]:
    """Create Lambda error context using specialized template."""
    try:
        if _USE_ERROR_TEMPLATES:
            corr_id = correlation_id or generate_correlation_id_fast()
            timestamp = time.time()
            
            json_str = _LAMBDA_ERROR_CONTEXT % (
                corr_id, timestamp, request_id
            )
            
            return json.loads(json_str)
        else:
            return create_error_context_fast("lambda", "handler", correlation_id,
                                           details={"request_id": request_id})
            
    except Exception:
        return create_error_context_fast("lambda", "handler", correlation_id)

class ErrorContextManager:
    """Error context manager with template optimization."""
    
    def __init__(self):
        self._context_cache = {}
        self._stats = {
            'contexts_created': 0,
            'template_usage': 0,
            'legacy_usage': 0,
            'correlation_ids_generated': 0,
            'cache_hits': 0,
            'cache_misses': 0
        }
        self._lock = threading.RLock()
    
    def create_context(self, interface: str, operation: str, 
                      correlation_id: Optional[str] = None,
                      error_code: Optional[str] = None,
                      details: Optional[Dict[str, Any]] = None,
                      use_cache: bool = True) -> Dict[str, Any]:
        """Create error context with optional caching."""
        with self._lock:
            cache_key = f"{interface}_{operation}_{error_code}"
            
            if use_cache and cache_key in self._context_cache:
                cached_context = self._context_cache[cache_key].copy()
                cached_context['correlation_id'] = correlation_id or generate_correlation_id_fast()
                cached_context['timestamp'] = time.time()
                if details:
                    cached_context['details'] = details
                
                self._stats['cache_hits'] += 1
                return cached_context
            
            self._stats['cache_misses'] += 1
            
            if _USE_ERROR_TEMPLATES:
                context = create_error_context_fast(interface, operation, correlation_id, error_code, details)
                self._stats['template_usage'] += 1
            else:
                context = _create_error_context_legacy(interface, operation, correlation_id, error_code, details)
                self._stats['legacy_usage'] += 1
            
            self._stats['contexts_created'] += 1
            
            if use_cache and len(self._context_cache) < 100:
                template_context = context.copy()
                template_context.pop('correlation_id', None)
                template_context.pop('timestamp', None)
                template_context.pop('details', None)
                self._context_cache[cache_key] = template_context
            
            return context
    
    def create_validation_context(self, field: str, correlation_id: Optional[str] = None) -> Dict[str, Any]:
        """Create validation error context."""
        context = create_validation_error_context(field, correlation_id)
        with self._lock:
            self._stats['contexts_created'] += 1
            if _USE_ERROR_TEMPLATES:
                self._stats['template_usage'] += 1
            else:
                self._stats['legacy_usage'] += 1
        return context
    
    def create_http_context(self, operation: str, url: str, status_code: int,
                           correlation_id: Optional[str] = None) -> Dict[str, Any]:
        """Create HTTP error context."""
        context = create_http_error_context(operation, url, status_code, correlation_id)
        with self._lock:
            self._stats['contexts_created'] += 1
            if _USE_ERROR_TEMPLATES:
                self._stats['template_usage'] += 1
            else:
                self._stats['legacy_usage'] += 1
        return context
    
    def create_cache_context(self, operation: str, key: str,
                            correlation_id: Optional[str] = None) -> Dict[str, Any]:
        """Create cache error context."""
        context = create_cache_error_context(operation, key, correlation_id)
        with self._lock:
            self._stats['contexts_created'] += 1
            if _USE_ERROR_TEMPLATES:
                self._stats['template_usage'] += 1
            else:
                self._stats['legacy_usage'] += 1
        return context
    
    def create_ha_context(self, operation: str, entity_id: str,
                         correlation_id: Optional[str] = None) -> Dict[str, Any]:
        """Create Home Assistant error context."""
        context = create_ha_error_context(operation, entity_id, correlation_id)
        with self._lock:
            self._stats['contexts_created'] += 1
            if _USE_ERROR_TEMPLATES:
                self._stats['template_usage'] += 1
            else:
                self._stats['legacy_usage'] += 1
        return context
    
    def create_lambda_context(self, request_id: str, correlation_id: Optional[str] = None) -> Dict[str, Any]:
        """Create Lambda error context."""
        context = create_lambda_error_context(request_id, correlation_id)
        with self._lock:
            self._stats['contexts_created'] += 1
            if _USE_ERROR_TEMPLATES:
                self._stats['template_usage'] += 1
            else:
                self._stats['legacy_usage'] += 1
        return context
    
    def get_stats(self) -> Dict[str, Any]:
        """Get error context statistics."""
        with self._lock:
            total_operations = self._stats['template_usage'] + self._stats['legacy_usage']
            template_usage_rate = self._stats['template_usage'] / max(total_operations, 1)
            cache_hit_rate = self._stats['cache_hits'] / max(self._stats['cache_hits'] + self._stats['cache_misses'], 1)
            
            return {
                'contexts_created': self._stats['contexts_created'],
                'template_usage_rate': template_usage_rate,
                'cache_hit_rate': cache_hit_rate,
                'template_optimization_enabled': _USE_ERROR_TEMPLATES,
                'correlation_ids_generated': self._stats['correlation_ids_generated'],
                'cache_size': len(self._context_cache),
                'stats': self._stats.copy()
            }
    
    def clear_cache(self):
        """Clear error context cache."""
        with self._lock:
            self._context_cache.clear()
    
    def reset_stats(self):
        """Reset error context statistics."""
        with self._lock:
            self._stats = {
                'contexts_created': 0,
                'template_usage': 0,
                'legacy_usage': 0,
                'correlation_ids_generated': 0,
                'cache_hits': 0,
                'cache_misses': 0
            }

# Global error context manager instance
_error_context_manager = ErrorContextManager()

def get_error_context_manager() -> ErrorContextManager:
    """Get global error context manager."""
    return _error_context_manager
