"""
metrics_response.py - UPDATED: Uses Unified Singleton System
Version: 2025.9.18.1-UNIFIED_SINGLETON_UPDATE
Description: Response metrics collection with unified singleton management

ELIMINATES:
- _response_metrics_manager global variable (REMOVED)
- _response_metrics_lock (REMOVED)
- get_response_metrics_manager() function (REMOVED)
- 35+ lines of duplicate singleton code (REMOVED)

USES:
- utility_singleton.get_response_metrics_manager()
"""

import time
import threading
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum
from collections import deque

logger = logging.getLogger(__name__)

# ===== SECTION 1: RESPONSE METRICS IMPLEMENTATION =====

class ResponseType(Enum):
    """Types of responses that can be tracked."""
    SUCCESS = "success"
    ERROR = "error"
    TIMEOUT = "timeout"
    CACHED = "cached"
    FALLBACK = "fallback"

@dataclass
class ResponseMetrics:
    """Response metrics data structure."""
    # Response counts
    total_responses: int = 0
    successful_responses: int = 0
    error_responses: int = 0
    timeout_responses: int = 0
    cached_responses: int = 0
    fallback_responses: int = 0
    
    # Timing metrics
    avg_response_time_ms: float = 0.0
    avg_processing_time_ms: float = 0.0
    fastest_response_ms: float = float('inf')
    slowest_response_ms: float = 0.0
    
    # Size metrics
    total_response_bytes: int = 0
    avg_response_size_bytes: float = 0.0
    largest_response_bytes: int = 0
    
    # Status code distribution
    status_2xx: int = 0
    status_3xx: int = 0
    status_4xx: int = 0
    status_5xx: int = 0
    
    # Cache metrics
    cache_hits: int = 0
    cache_misses: int = 0
    cache_invalidations: int = 0
    cache_hit_rate: float = 0.0
    
    # Error tracking
    last_error_time: float = 0.0
    last_error_message: str = ""
    error_types: Dict[str, int] = field(default_factory=dict)
    
    def success_rate(self) -> float:
        """Calculate success rate percentage."""
        return (self.successful_responses / self.total_responses * 100) if self.total_responses > 0 else 0.0
    
    def error_rate(self) -> float:
        """Calculate error rate percentage."""
        return (self.error_responses / self.total_responses * 100) if self.total_responses > 0 else 0.0
    
    def fallback_rate(self) -> float:
        """Calculate fallback rate percentage."""
        return (self.fallback_responses / self.total_responses * 100) if self.total_responses > 0 else 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary."""
        return {
            'response_counts': {
                'total': self.total_responses,
                'successful': self.successful_responses,
                'error': self.error_responses,
                'timeout': self.timeout_responses,
                'cached': self.cached_responses,
                'fallback': self.fallback_responses
            },
            'timing_metrics': {
                'avg_response_time_ms': self.avg_response_time_ms,
                'avg_processing_time_ms': self.avg_processing_time_ms,
                'fastest_response_ms': self.fastest_response_ms if self.fastest_response_ms != float('inf') else 0,
                'slowest_response_ms': self.slowest_response_ms
            },
            'size_metrics': {
                'total_response_bytes': self.total_response_bytes,
                'avg_response_size_bytes': self.avg_response_size_bytes,
                'largest_response_bytes': self.largest_response_bytes
            },
            'status_distribution': {
                '2xx': self.status_2xx,
                '3xx': self.status_3xx,
                '4xx': self.status_4xx,
                '5xx': self.status_5xx
            },
            'cache_metrics': {
                'hits': self.cache_hits,
                'misses': self.cache_misses,
                'invalidations': self.cache_invalidations,
                'hit_rate': self.cache_hit_rate
            },
            'rates': {
                'success_rate': self.success_rate(),
                'error_rate': self.error_rate(),
                'fallback_rate': self.fallback_rate()
            },
            'error_tracking': {
                'last_error_time': self.last_error_time,
                'last_error_message': self.last_error_message,
                'error_types': dict(self.error_types)
            }
        }

class ResponseMetricsManager:
    """
    Response metrics collection and analysis manager.
    No longer implements singleton pattern - uses utility_singleton.py instead.
    """
    
    def __init__(self, max_history: int = 100):
        self._metrics = ResponseMetrics()
        self._response_history: deque = deque(maxlen=max_history)
        self._lock = threading.Lock()
        self._max_history = max_history
        self._cost_protection_active = False
        
        logger.debug("Response metrics manager initialized (uses unified singleton)")
    
    def record_response(self, response_type: ResponseType, status_code: int = None,
                       response_time_ms: float = 0.0, processing_time_ms: float = 0.0,
                       response_size_bytes: int = 0, content_type: str = None,
                       endpoint: str = None, error_type: str = None) -> None:
        """Record a response with comprehensive metrics."""
        current_time = time.time()
        
        with self._lock:
            if self._cost_protection_active:
                return
            
            # Update response counts
            self._metrics.total_responses += 1
            
            if response_type == ResponseType.SUCCESS:
                self._metrics.successful_responses += 1
            elif response_type == ResponseType.ERROR:
                self._metrics.error_responses += 1
                self._metrics.last_error_time = current_time
                if error_type:
                    self._metrics.error_types[error_type] = self._metrics.error_types.get(error_type, 0) + 1
            elif response_type == ResponseType.TIMEOUT:
                self._metrics.timeout_responses += 1
            elif response_type == ResponseType.CACHED:
                self._metrics.cached_responses += 1
                self._metrics.cache_hits += 1
            elif response_type == ResponseType.FALLBACK:
                self._metrics.fallback_responses += 1
            
            # Update status code distribution
            if status_code:
                self._update_status_distribution(status_code)
            
            # Update timing metrics
            if response_time_ms > 0:
                self._update_response_timing(response_time_ms)
            
            if processing_time_ms > 0:
                self._update_processing_timing(processing_time_ms)
            
            # Update size metrics
            if response_size_bytes > 0:
                self._update_size_metrics(response_size_bytes)
            
            # Store response details
            response_details = {
                'type': response_type.value,
                'status_code': status_code,
                'response_time_ms': response_time_ms,
                'processing_time_ms': processing_time_ms,
                'response_size_bytes': response_size_bytes,
                'content_type': content_type,
                'endpoint': endpoint,
                'error_type': error_type,
                'timestamp': current_time
            }
            
            self._store_response(response_details)
    
    def record_cache_event(self, hit: bool, invalidation: bool = False) -> None:
        """Record cache-related events."""
        with self._lock:
            if self._cost_protection_active:
                return
            
            if invalidation:
                self._metrics.cache_invalidations += 1
            elif not hit:
                self._metrics.cache_misses += 1
            
            # Update cache hit rate
            total_cache_events = self._metrics.cached_responses + self._metrics.cache_misses
            if total_cache_events > 0:
                self._metrics.cache_hit_rate = (self._metrics.cached_responses / total_cache_events) * 100
    
    def _update_status_distribution(self, status_code: int) -> None:
        """Update status code distribution."""
        if 200 <= status_code < 300:
            self._metrics.status_2xx += 1
        elif 300 <= status_code < 400:
            self._metrics.status_3xx += 1
        elif 400 <= status_code < 500:
            self._metrics.status_4xx += 1
        elif 500 <= status_code < 600:
            self._metrics.status_5xx += 1
    
    def _update_response_timing(self, response_time_ms: float) -> None:
        """Update response timing metrics."""
        # Update average
        total_time = self._metrics.avg_response_time_ms * (self._metrics.total_responses - 1)
        self._metrics.avg_response_time_ms = (total_time + response_time_ms) / self._metrics.total_responses
        
        # Update extremes
        self._metrics.fastest_response_ms = min(self._metrics.fastest_response_ms, response_time_ms)
        self._metrics.slowest_response_ms = max(self._metrics.slowest_response_ms, response_time_ms)
    
    def _update_processing_timing(self, processing_time_ms: float) -> None:
        """Update processing timing metrics."""
        total_time = self._metrics.avg_processing_time_ms * (self._metrics.total_responses - 1)
        self._metrics.avg_processing_time_ms = (total_time + processing_time_ms) / self._metrics.total_responses
    
    def _update_size_metrics(self, response_size_bytes: int) -> None:
        """Update response size metrics."""
        self._metrics.total_response_bytes += response_size_bytes
        self._metrics.avg_response_size_bytes = self._metrics.total_response_bytes / self._metrics.total_responses
        self._metrics.largest_response_bytes = max(self._metrics.largest_response_bytes, response_size_bytes)
    
    def _store_response(self, response: Dict[str, Any]) -> None:
        """Store response in history."""
        self._response_history.append(response)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get comprehensive response metrics."""
        with self._lock:
            metrics_data = self._metrics.to_dict()
            metrics_data['recent_responses'] = list(self._response_history)[-10:]  # Last 10 responses
            metrics_data['cost_protection_active'] = self._cost_protection_active
            return metrics_data
    
    def get_performance_analysis(self) -> Dict[str, Any]:
        """Get response performance analysis."""
        with self._lock:
            return {
                'response_performance': {
                    'avg_response_time_ms': self._metrics.avg_response_time_ms,
                    'avg_processing_time_ms': self._metrics.avg_processing_time_ms,
                    'performance_ratio': self._metrics.avg_processing_time_ms / self._metrics.avg_response_time_ms if self._metrics.avg_response_time_ms > 0 else 0
                },
                'reliability': {
                    'success_rate': self._metrics.success_rate(),
                    'error_rate': self._metrics.error_rate(),
                    'timeout_rate': (self._metrics.timeout_responses / self._metrics.total_responses * 100) if self._metrics.total_responses > 0 else 0
                },
                'efficiency': {
                    'cache_hit_rate': self._metrics.cache_hit_rate,
                    'fallback_rate': self._metrics.fallback_rate(),
                    'avg_response_size_kb': self._metrics.avg_response_size_bytes / 1024
                }
            }
    
    def reset_metrics(self) -> None:
        """Reset response metrics."""
        with self._lock:
            self._metrics = ResponseMetrics()
            self._response_history.clear()
    
    def set_cost_protection(self, active: bool) -> None:
        """Set cost protection state."""
        with self._lock:
            self._cost_protection_active = active

# EOS

# ===== SECTION 2: CONVENIENCE FUNCTIONS (UPDATED TO USE UNIFIED SINGLETON) =====

def get_response_metrics_manager():
    """
    UPDATED: Get response metrics manager using unified singleton system.
    REPLACES: Local singleton implementation with utility_singleton.get_response_metrics_manager()
    """
    from .utility_singleton import get_response_metrics_manager as unified_get_response_metrics_manager
    return unified_get_response_metrics_manager()

def record_successful_response(status_code: int, response_time_ms: float = 0.0, 
                             processing_time_ms: float = 0.0, response_size_bytes: int = 0,
                             content_type: str = None, endpoint: str = None) -> None:
    """Record successful response."""
    get_response_metrics_manager().record_response(
        ResponseType.SUCCESS, status_code, response_time_ms, processing_time_ms,
        response_size_bytes, content_type, endpoint
    )

def record_error_response(status_code: int, error_type: str, response_time_ms: float = 0.0,
                         endpoint: str = None) -> None:
    """Record error response."""
    get_response_metrics_manager().record_response(
        ResponseType.ERROR, status_code, response_time_ms, 0, 0, None, endpoint, error_type
    )

def record_timeout_response(endpoint: str = None, timeout_ms: float = 0.0) -> None:
    """Record timeout response."""
    get_response_metrics_manager().record_response(
        ResponseType.TIMEOUT, None, timeout_ms, 0, 0, None, endpoint, "timeout"
    )

def record_cached_response(response_size_bytes: int = 0, processing_time_ms: float = 0.0) -> None:
    """Record cached response."""
    get_response_metrics_manager().record_response(
        ResponseType.CACHED, 200, 0, processing_time_ms, response_size_bytes
    )

def record_fallback_response(processing_time_ms: float = 0.0, reason: str = None) -> None:
    """Record fallback response."""
    get_response_metrics_manager().record_response(
        ResponseType.FALLBACK, 200, 0, processing_time_ms, 0, None, None, reason
    )

def record_cache_hit() -> None:
    """Record cache hit."""
    get_response_metrics_manager().record_cache_event(True)

def record_cache_miss() -> None:
    """Record cache miss."""
    get_response_metrics_manager().record_cache_event(False)

def record_cache_invalidation() -> None:
    """Record cache invalidation."""
    get_response_metrics_manager().record_cache_event(False, True)

def get_response_metrics() -> Dict[str, Any]:
    """Get comprehensive response metrics."""
    return get_response_metrics_manager().get_metrics()

def get_response_performance_analysis() -> Dict[str, Any]:
    """Get response performance analysis."""
    return get_response_metrics_manager().get_performance_analysis()

def reset_response_metrics() -> None:
    """Reset all response metrics."""
    get_response_metrics_manager().reset_metrics()

# EOS

# ===== SECTION 3: MODULE EXPORTS =====

__all__ = [
    # Main classes
    'ResponseMetricsManager',
    'ResponseMetrics',
    'ResponseType',
    
    # UPDATED global access (uses unified singleton)
    'get_response_metrics_manager',    # UPDATED: Uses utility_singleton.get_response_metrics_manager()
    
    # Convenience functions
    'record_successful_response',
    'record_error_response',
    'record_timeout_response',
    'record_cached_response',
    'record_fallback_response',
    'record_cache_hit',
    'record_cache_miss',
    'record_cache_invalidation',
    'get_response_metrics',
    'get_response_performance_analysis',
    'reset_response_metrics'
]

# EOF
