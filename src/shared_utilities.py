"""
shared_utilities.py
Version: 2025.10.11.01
Description: Enhanced Utilities with Template Optimization


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
import threading
import os
from typing import Dict, Any, Optional, Union, List
from dataclasses import dataclass
from enum import Enum

from gateway import (
    log_info, log_error, log_debug,
    record_metric,
    cache_get, cache_set
)

# ===== JSON RESPONSE TEMPLATES (Phase 1 Optimization) =====

_SUCCESS_TEMPLATE = '{"success":true,"message":"%s","timestamp":%d,"data":%s}'
_SUCCESS_WITH_CORRELATION = '{"success":true,"message":"%s","timestamp":%d,"data":%s,"correlation_id":"%s"}'
_ERROR_TEMPLATE = '{"success":false,"error":"%s","timestamp":%d}'
_ERROR_WITH_CODE = '{"success":false,"error":"%s","error_code":"%s","timestamp":%d,"details":%s}'
_ERROR_WITH_CORRELATION = '{"success":false,"error":"%s","error_code":"%s","timestamp":%d,"details":%s,"correlation_id":"%s"}'
_EMPTY_DATA = '{}'

# Template usage flag (for rollback capability)
_USE_TEMPLATES = os.environ.get('USE_JSON_TEMPLATES', 'true').lower() == 'true'


class UtilityOperationType(str, Enum):
    CREATE_RESPONSE = "create_response"
    PARSE_JSON = "parse_json"
    GENERATE_ID = "generate_id"
    VALIDATE_DATA = "validate_data"
    FORMAT_DATA = "format_data"


@dataclass
class UtilityMetrics:
    """Metrics for utility operations."""
    operation_type: str
    call_count: int = 0
    total_duration_ms: float = 0.0
    avg_duration_ms: float = 0.0
    cache_hits: int = 0
    cache_misses: int = 0
    error_count: int = 0
    template_usage: int = 0


class LUGSUtilityManager:
    """LUGS-integrated utility manager with template optimization."""
    
    def __init__(self):
        self._metrics: Dict[str, UtilityMetrics] = {}
        self._lock = threading.RLock()
        self._cache_enabled = True
        self._cache_ttl = 300
        
        self._id_pool: List[str] = []
        self._id_pool_size = 100
        self._id_pool_refill_threshold = 20
        
        self._stats = {
            'total_operations': 0,
            'cache_optimized_operations': 0,
            'lugs_integrations': 0,
            'performance_optimizations': 0,
            'template_optimizations': 0
        }
        
        self._refill_id_pool()
    
    def create_success_response(
        self,
        message: str,
        data: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create success response with template optimization."""
        start_time = time.time()
        operation_type = UtilityOperationType.CREATE_RESPONSE
        
        try:
            self._start_operation_tracking(operation_type)
            
            if _USE_TEMPLATES:
                timestamp = int(time.time())
                data_json = _EMPTY_DATA if not data else json.dumps(data)
                
                if correlation_id:
                    json_str = _SUCCESS_WITH_CORRELATION % (
                        message, timestamp, data_json, correlation_id
                    )
                else:
                    json_str = _SUCCESS_TEMPLATE % (message, timestamp, data_json)
                
                response = json.loads(json_str)
                self._stats['template_optimizations'] += 1
                
                duration_ms = (time.time() - start_time) * 1000
                self._complete_operation_tracking(operation_type, duration_ms, success=True, template_used=True)
                
                return response
            else:
                return self._create_success_response_legacy(message, data, correlation_id)
                
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self._complete_operation_tracking(operation_type, duration_ms, success=False)
            
            return {
                "success": True,
                "message": message,
                "timestamp": int(time.time()),
                "data": data or {},
                "error": f"Response creation error: {str(e)}"
            }
    
    def _create_success_response_legacy(
        self,
        message: str,
        data: Optional[Dict[str, Any]],
        correlation_id: Optional[str]
    ) -> Dict[str, Any]:
        """Legacy dict-based response creation."""
        response = {
            "success": True,
            "message": message,
            "timestamp": int(time.time()),
            "data": data or {}
        }
        
        if correlation_id:
            response["correlation_id"] = correlation_id
        
        return response
    
    def create_error_response(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create error response with template optimization."""
        start_time = time.time()
        operation_type = UtilityOperationType.CREATE_RESPONSE
        
        try:
            self._start_operation_tracking(operation_type)
            
            if _USE_TEMPLATES:
                timestamp = int(time.time())
                
                if error_code or details or correlation_id:
                    error_code = error_code or "GENERIC_ERROR"
                    details_json = _EMPTY_DATA if not details else json.dumps(details)
                    
                    if correlation_id:
                        json_str = _ERROR_WITH_CORRELATION % (
                            message, error_code, timestamp, details_json, correlation_id
                        )
                    else:
                        json_str = _ERROR_WITH_CODE % (
                            message, error_code, timestamp, details_json
                        )
                else:
                    json_str = _ERROR_TEMPLATE % (message, timestamp)
                
                response = json.loads(json_str)
                self._stats['template_optimizations'] += 1
                
                duration_ms = (time.time() - start_time) * 1000
                self._complete_operation_tracking(operation_type, duration_ms, success=True, template_used=True)
                
                return response
            else:
                return self._create_error_response_legacy(message, error_code, details, correlation_id)
                
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self._complete_operation_tracking(operation_type, duration_ms, success=False)
            
            return {
                "success": False,
                "error": message,
                "error_code": error_code or "GENERIC_ERROR",
                "timestamp": int(time.time()),
                "details": details or {},
                "fallback": f"Template error: {str(e)}"
            }
    
    def _create_error_response_legacy(
        self,
        message: str,
        error_code: Optional[str],
        details: Optional[Dict[str, Any]],
        correlation_id: Optional[str]
    ) -> Dict[str, Any]:
        """Legacy dict-based error response creation."""
        response = {
            "success": False,
            "error": message,
            "timestamp": int(time.time())
        }
        
        if error_code:
            response["error_code"] = error_code
        if details:
            response["details"] = details
        if correlation_id:
            response["correlation_id"] = correlation_id
        
        return response
    
    def generate_correlation_id(self, prefix: Optional[str] = None) -> str:
        """Generate correlation ID with pool optimization."""
        start_time = time.time()
        operation_type = UtilityOperationType.GENERATE_ID
        
        try:
            self._start_operation_tracking(operation_type)
            
            if self._id_pool:
                base_id = self._id_pool.pop()
                
                if len(self._id_pool) <= self._id_pool_refill_threshold:
                    self._refill_id_pool()
                
                correlation_id = f"{prefix}_{base_id}" if prefix else base_id
            else:
                correlation_id = f"{prefix}_{str(uuid.uuid4())[:8]}" if prefix else str(uuid.uuid4())[:8]
            
            duration_ms = (time.time() - start_time) * 1000
            self._complete_operation_tracking(operation_type, duration_ms, success=True)
            
            return correlation_id
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self._complete_operation_tracking(operation_type, duration_ms, success=False)
            
            return f"err_{int(time.time())}"
    
    def parse_json_safely(
        self,
        json_str: str,
        use_cache: bool = True
    ) -> Optional[Dict[str, Any]]:
        """Parse JSON safely with caching."""
        start_time = time.time()
        operation_type = UtilityOperationType.PARSE_JSON
        
        try:
            self._start_operation_tracking(operation_type)
            
            cache_key = None
            if use_cache and self._cache_enabled and len(json_str) > 1000:
                cache_key = f"json_parse_{hash(json_str)}"
                cached_result = cache_get(cache_key)
                
                if cached_result is not None:
                    duration_ms = (time.time() - start_time) * 1000
                    self._complete_operation_tracking(operation_type, duration_ms, success=True, cache_hit=True)
                    return cached_result
            
            parsed_data = json.loads(json_str)
            
            if cache_key and parsed_data:
                cache_set(cache_key, parsed_data, self._cache_ttl)
            
            duration_ms = (time.time() - start_time) * 1000
            self._complete_operation_tracking(operation_type, duration_ms, success=True, cache_hit=False)
            
            return parsed_data
            
        except json.JSONDecodeError:
            duration_ms = (time.time() - start_time) * 1000
            self._complete_operation_tracking(operation_type, duration_ms, success=False)
            return None
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self._complete_operation_tracking(operation_type, duration_ms, success=False)
            
            log_error(f"JSON parsing error: {str(e)}", extra={
                "json_length": len(json_str),
                "error_type": type(e).__name__
            })
            return None
    
    def validate_data_structure(
        self,
        data: Any,
        expected_type: type,
        required_fields: Optional[List[str]] = None
    ) -> bool:
        """Validate data structure."""
        start_time = time.time()
        operation_type = UtilityOperationType.VALIDATE_DATA
        
        try:
            self._start_operation_tracking(operation_type)
            
            if not isinstance(data, expected_type):
                duration_ms = (time.time() - start_time) * 1000
                self._complete_operation_tracking(operation_type, duration_ms, success=False)
                return False
            
            if required_fields and isinstance(data, dict):
                for field in required_fields:
                    if field not in data:
                        duration_ms = (time.time() - start_time) * 1000
                        self._complete_operation_tracking(operation_type, duration_ms, success=False)
                        return False
            
            duration_ms = (time.time() - start_time) * 1000
            self._complete_operation_tracking(operation_type, duration_ms, success=True)
            
            return True
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self._complete_operation_tracking(operation_type, duration_ms, success=False)
            
            log_error(f"Data validation error: {str(e)}", extra={
                "expected_type": expected_type.__name__,
                "required_fields": required_fields
            })
            return False
    
    def format_data_for_response(
        self,
        data: Any,
        format_type: str = "json",
        include_metadata: bool = True
    ) -> Dict[str, Any]:
        """Format data for response."""
        start_time = time.time()
        operation_type = UtilityOperationType.FORMAT_DATA
        
        try:
            self._start_operation_tracking(operation_type)
            
            formatted_data = {
                "formatted_data": data,
                "format_type": format_type
            }
            
            if include_metadata:
                formatted_data["metadata"] = {
                    "timestamp": int(time.time()),
                    "data_type": type(data).__name__
                }
            
            duration_ms = (time.time() - start_time) * 1000
            self._complete_operation_tracking(operation_type, duration_ms, success=True)
            
            return formatted_data
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self._complete_operation_tracking(operation_type, duration_ms, success=False)
            
            log_error(f"Data formatting error: {str(e)}")
            return {"error": str(e)}
    
    def _start_operation_tracking(self, operation_type: UtilityOperationType) -> None:
        """Start tracking utility operation."""
        with self._lock:
            self._stats['total_operations'] += 1
            
            if operation_type not in self._metrics:
                self._metrics[operation_type] = UtilityMetrics(operation_type=operation_type)
    
    def _complete_operation_tracking(
        self,
        operation_type: UtilityOperationType,
        duration_ms: float,
        success: bool,
        cache_hit: bool = False,
        template_used: bool = False
    ) -> None:
        """Complete tracking utility operation."""
        with self._lock:
            if operation_type not in self._metrics:
                self._metrics[operation_type] = UtilityMetrics(operation_type=operation_type)
            
            metrics = self._metrics[operation_type]
            metrics.call_count += 1
            metrics.total_duration_ms += duration_ms
            metrics.avg_duration_ms = metrics.total_duration_ms / metrics.call_count
            
            if cache_hit:
                metrics.cache_hits += 1
                self._stats['cache_optimized_operations'] += 1
            else:
                metrics.cache_misses += 1
            
            if template_used:
                metrics.template_usage += 1
            
            if not success:
                metrics.error_count += 1
            
            record_metric("utility_operation", 1.0, {
                "operation_type": operation_type,
                "success": str(success).lower(),
                "cache_hit": str(cache_hit).lower(),
                "template_used": str(template_used).lower()
            })
            
            if duration_ms < 10.0:
                self._stats['performance_optimizations'] += 1
    
    def _refill_id_pool(self) -> None:
        """Refill the correlation ID pool."""
        try:
            while len(self._id_pool) < self._id_pool_size:
                self._id_pool.append(str(uuid.uuid4())[:8])
        except Exception as e:
            log_error(f"Failed to refill ID pool: {str(e)}")
    
    def cleanup_cache(self, max_age_seconds: int = 3600) -> int:
        """Clean up old cached data."""
        try:
            self._stats['lugs_integrations'] += 1
            return 0
        except Exception as e:
            log_error(f"Cache cleanup error: {str(e)}")
            return 0
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get utility performance statistics."""
        with self._lock:
            operation_stats = {}
            
            for op_type, metrics in self._metrics.items():
                cache_hit_rate = 0.0
                if metrics.cache_hits + metrics.cache_misses > 0:
                    cache_hit_rate = metrics.cache_hits / (metrics.cache_hits + metrics.cache_misses) * 100
                
                error_rate = 0.0
                if metrics.call_count > 0:
                    error_rate = metrics.error_count / metrics.call_count * 100
                
                template_usage_rate = 0.0
                if metrics.call_count > 0:
                    template_usage_rate = metrics.template_usage / metrics.call_count * 100
                
                operation_stats[op_type] = {
                    "call_count": metrics.call_count,
                    "avg_duration_ms": round(metrics.avg_duration_ms, 2),
                    "cache_hit_rate_percent": round(cache_hit_rate, 2),
                    "error_rate_percent": round(error_rate, 2),
                    "template_usage_percent": round(template_usage_rate, 2),
                    "cache_hits": metrics.cache_hits,
                    "cache_misses": metrics.cache_misses,
                    "error_count": metrics.error_count,
                    "template_usage": metrics.template_usage
                }
            
            return {
                "overall_stats": self._stats,
                "operation_stats": operation_stats,
                "id_pool_size": len(self._id_pool),
                "cache_enabled": self._cache_enabled,
                "templates_enabled": _USE_TEMPLATES
            }
    
    def optimize_performance(self) -> Dict[str, Any]:
        """Optimize utility performance based on usage patterns."""
        with self._lock:
            optimizations = []
            
            for op_type, metrics in self._metrics.items():
                if metrics.call_count > 100:
                    
                    if metrics.avg_duration_ms > 50 and metrics.cache_hits == 0:
                        optimizations.append({
                            "operation": op_type,
                            "suggestion": "enable_caching",
                            "reason": f"Slow operation ({metrics.avg_duration_ms:.1f}ms avg) with no caching"
                        })
                    
                    if metrics.call_count > 1000 and metrics.avg_duration_ms > 10:
                        optimizations.append({
                            "operation": op_type,
                            "suggestion": "enable_fast_path",
                            "reason": f"High frequency operation ({metrics.call_count} calls)"
                        })
            
            id_generation_metrics = self._metrics.get(UtilityOperationType.GENERATE_ID)
            if id_generation_metrics and id_generation_metrics.call_count > 500:
                new_pool_size = min(500, id_generation_metrics.call_count // 10)
                if new_pool_size > self._id_pool_size:
                    self._id_pool_size = new_pool_size
                    optimizations.append({
                        "operation": "id_pool",
                        "suggestion": "increase_pool_size",
                        "reason": f"High ID generation frequency, increased pool to {new_pool_size}"
                    })
            
            return {
                "optimizations_applied": len(optimizations),
                "optimizations": optimizations,
                "performance_impact": "improved" if optimizations else "no_changes"
            }


_utility_manager = LUGSUtilityManager()


def create_success_response(
    message: str,
    data: Optional[Dict[str, Any]] = None,
    correlation_id: Optional[str] = None
) -> Dict[str, Any]:
    """Create success response."""
    return _utility_manager.create_success_response(message, data, correlation_id)


def create_error_response(
    message: str,
    error_code: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    correlation_id: Optional[str] = None
) -> Dict[str, Any]:
    """Create error response."""
    return _utility_manager.create_error_response(message, error_code, details, correlation_id)


def generate_correlation_id(prefix: Optional[str] = None) -> str:
    """Generate correlation ID."""
    return _utility_manager.generate_correlation_id(prefix)


def parse_json_safely(json_str: str, use_cache: bool = True) -> Optional[Dict[str, Any]]:
    """Parse JSON safely with optional caching."""
    return _utility_manager.parse_json_safely(json_str, use_cache)


def validate_data_structure(
    data: Any,
    expected_type: type,
    required_fields: Optional[List[str]] = None
) -> bool:
    """Validate data structure."""
    return _utility_manager.validate_data_structure(data, expected_type, required_fields)


def format_data_for_response(
    data: Any,
    format_type: str = "json",
    include_metadata: bool = True
) -> Dict[str, Any]:
    """Format data for response."""
    return _utility_manager.format_data_for_response(data, format_type, include_metadata)


def cleanup_utility_cache(max_age_seconds: int = 3600) -> int:
    """Clean up old cached utility data."""
    return _utility_manager.cleanup_cache(max_age_seconds)


def get_utility_performance_stats() -> Dict[str, Any]:
    """Get utility performance statistics."""
    return _utility_manager.get_performance_stats()


def optimize_utility_performance() -> Dict[str, Any]:
    """Optimize utility performance based on usage patterns."""
    return _utility_manager.optimize_performance()


def configure_utility_caching(enabled: bool, ttl: int = 300) -> bool:
    """Configure utility caching settings."""
    try:
        _utility_manager._cache_enabled = enabled
        _utility_manager._cache_ttl = ttl
        return True
    except Exception as e:
        log_error(f"Failed to configure utility caching: {str(e)}")
        return False


def safe_string_conversion(data: Any, max_length: int = 10000) -> str:
    """Safely convert data to string with length limits."""
    try:
        result = str(data)
        if len(result) > max_length:
            return result[:max_length] + "... [truncated]"
        return result
    except Exception:
        return "[conversion_error]"


def merge_dictionaries(*dicts: Dict[str, Any]) -> Dict[str, Any]:
    """Merge multiple dictionaries safely."""
    try:
        result = {}
        for d in dicts:
            if isinstance(d, dict):
                result.update(d)
        return result
    except Exception as e:
        log_error(f"Dictionary merge error: {str(e)}")
        return {}


def extract_error_details(error: Exception) -> Dict[str, Any]:
    """Extract detailed error information."""
    try:
        return {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "error_args": list(error.args) if error.args else [],
            "timestamp": int(time.time())
        }
    except Exception:
        return {
            "error_type": "UNKNOWN",
            "error_message": "Error details extraction failed",
            "timestamp": int(time.time())
        }

def create_operation_context(interface: str, operation: str, **kwargs) -> Dict[str, Any]:
    """
    Create operation context with correlation tracking and metrics recording.
    Compatible with LUGSUtilityManager-based utilities.
    """
    try:
        correlation_id = generate_correlation_id()
        start_time = time.time()
        
        context = {
            "interface": interface,
            "operation": operation,
            "correlation_id": correlation_id,
            "start_time": start_time,
            "parameters": kwargs,
        }

        # Record start metric
        record_metric(
            f"{interface}_operation_started",
            1.0,
            {
                "operation": operation,
                "correlation_id": correlation_id,
                "timestamp": int(start_time),
            },
        )

        log_info(f"{interface}.{operation} context created", {
            "correlation_id": correlation_id,
            "parameters": list(kwargs.keys())
        })

        return context

    except Exception as e:
        log_error(f"Failed to create operation context for {interface}.{operation}: {str(e)}")
        return {
            "interface": interface,
            "operation": operation,
            "correlation_id": f"err_{int(time.time())}",
            "error": str(e),
            "timestamp": int(time.time()),
        }

def close_operation_context(context: Dict[str, Any], success: bool = True, result: Any = None) -> Dict[str, Any]:
    """
    Close operation context and record final metrics.
    Mirrors the older shared_utilities version but adapted to LUGSUtilityManager.
    """
    try:
        end_time = time.time()
        duration = end_time - context.get("start_time", end_time)
        interface = context.get("interface", "unknown")
        operation = context.get("operation", "unknown")
        correlation_id = context.get("correlation_id", "unknown")

        record_metric(
            f"{interface}_operation_completed",
            1.0,
            {
                "operation": operation,
                "correlation_id": correlation_id,
                "duration_ms": round(duration * 1000, 2),
                "success": str(success).lower(),
            },
        )

        log_info(f"{interface}.{operation} completed", {
            "correlation_id": correlation_id,
            "duration_ms": round(duration * 1000, 2),
            "success": success
        })

        return {
            "success": success,
            "duration_ms": round(duration * 1000, 2),
            "correlation_id": correlation_id,
            "result": result,
        }

    except Exception as e:
        log_error(f"Failed to close operation context: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "timestamp": int(time.time()),
        }


#EOF
