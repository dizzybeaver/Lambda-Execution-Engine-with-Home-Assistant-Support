"""
metrics_http_client.py - CONSOLIDATED: Pure HTTP Metrics (Singleton Access Removed)
Version: 2025.09.25.02
Description: HTTP client metrics using consolidated singleton.py gateway

CONSOLIDATION APPLIED:
- ❌ REMOVED: Direct singleton.get_singleton() calls
- ❌ REMOVED: Import singleton module
- ✅ IMPORTS: Manager access from singleton.py gateway
- ✅ MAINTAINED: All metrics functionality through delegation

PURE FUNCTIONAL INTERFACE - No singleton management code

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
import time
import threading
from typing import Dict, Any, Optional
from collections import defaultdict, deque

# CONSOLIDATION: Import manager access from singleton.py gateway
from singleton import get_http_client_metrics_manager

logger = logging.getLogger(__name__)

# ===== SECTION 1: HTTP CLIENT METRICS OPERATIONS (PURE DELEGATION) =====

def increment_counter(counter_name: str, increment: int = 1) -> bool:
    """Increment HTTP client counter using consolidated singleton access."""
    try:
        # Use singleton.py gateway for manager access
        metrics_manager = get_http_client_metrics_manager()
        
        if not metrics_manager:
            logger.error("HTTP client metrics manager not available")
            return False
        
        # Pure delegation to manager
        return metrics_manager.increment_counter(counter_name, increment)
        
    except Exception as e:
        logger.error(f"Counter increment failed: {e}")
        return False

def get_counter_value(counter_name: str) -> int:
    """Get HTTP client counter value using consolidated singleton access."""
    try:
        # Use singleton.py gateway for manager access
        metrics_manager = get_http_client_metrics_manager()
        
        if not metrics_manager:
            logger.error("HTTP client metrics manager not available")
            return 0
        
        # Pure delegation to manager
        return metrics_manager.get_counter_value(counter_name)
        
    except Exception as e:
        logger.error(f"Counter retrieval failed: {e}")
        return 0

def record_value(metric_name: str, value: float) -> bool:
    """Record HTTP client metric value using consolidated singleton access."""
    try:
        # Use singleton.py gateway for manager access
        metrics_manager = get_http_client_metrics_manager()
        
        if not metrics_manager:
            logger.error("HTTP client metrics manager not available")
            return False
        
        # Pure delegation to manager
        return metrics_manager.record_value(metric_name, value)
        
    except Exception as e:
        logger.error(f"Value recording failed: {e}")
        return False

def get_average_value(metric_name: str) -> float:
    """Get HTTP client average value using consolidated singleton access."""
    try:
        # Use singleton.py gateway for manager access
        metrics_manager = get_http_client_metrics_manager()
        
        if not metrics_manager:
            logger.error("HTTP client metrics manager not available")
            return 0.0
        
        # Pure delegation to manager
        return metrics_manager.get_average_value(metric_name)
        
    except Exception as e:
        logger.error(f"Average retrieval failed: {e}")
        return 0.0

# ===== SECTION 2: HTTP CLIENT METRICS COLLECTION (PURE DELEGATION) =====

def get_http_client_metrics() -> Dict[str, Any]:
    """Get comprehensive HTTP client metrics using consolidated singleton access."""
    try:
        # Use singleton.py gateway for manager access
        metrics_manager = get_http_client_metrics_manager()
        
        if not metrics_manager:
            logger.error("HTTP client metrics manager not available")
            return {
                'error': 'Metrics manager not available',
                'counters': {},
                'values': {},
                'averages': {},
                'timestamp': time.time()
            }
        
        # Pure delegation to manager
        metrics = metrics_manager.get_metrics()
        
        # Add timestamp if not present
        if 'timestamp' not in metrics:
            metrics['timestamp'] = time.time()
        
        return metrics
        
    except Exception as e:
        logger.error(f"HTTP client metrics retrieval failed: {e}")
        return {
            'error': str(e),
            'counters': {},
            'values': {},
            'averages': {},
            'timestamp': time.time()
        }

def reset_http_client_metrics() -> bool:
    """Reset HTTP client metrics using consolidated singleton access."""
    try:
        # Use singleton.py gateway for manager access
        metrics_manager = get_http_client_metrics_manager()
        
        if not metrics_manager:
            logger.error("HTTP client metrics manager not available")
            return False
        
        # Pure delegation to manager
        return metrics_manager.reset_metrics()
        
    except Exception as e:
        logger.error(f"HTTP client metrics reset failed: {e}")
        return False

def get_http_client_performance_summary() -> Dict[str, Any]:
    """Get HTTP client performance summary using consolidated singleton access."""
    try:
        metrics = get_http_client_metrics()
        
        if 'error' in metrics:
            return {
                'performance_summary': 'unavailable',
                'error': metrics['error']
            }
        
        # Calculate performance summary from metrics
        counters = metrics.get('counters', {})
        averages = metrics.get('averages', {})
        
        total_requests = counters.get('total_requests', 0)
        successful_requests = counters.get('successful_requests', 0)
        failed_requests = counters.get('failed_requests', 0)
        
        success_rate = (successful_requests / max(1, total_requests)) * 100
        
        return {
            'performance_summary': 'available',
            'total_requests': total_requests,
            'successful_requests': successful_requests,
            'failed_requests': failed_requests,
            'success_rate_percent': round(success_rate, 2),
            'average_response_time_ms': averages.get('response_time_ms', 0.0),
            'average_request_size_bytes': averages.get('request_size_bytes', 0.0),
            'timestamp': metrics.get('timestamp', time.time())
        }
        
    except Exception as e:
        logger.error(f"Performance summary generation failed: {e}")
        return {
            'performance_summary': 'error',
            'error': str(e)
        }

# ===== SECTION 3: CONVENIENCE FUNCTIONS (PURE FUNCTIONAL) =====

def record_request_metrics(response_time_ms: float, request_size_bytes: int, 
                          response_size_bytes: int, success: bool) -> bool:
    """Record comprehensive request metrics - convenience function."""
    try:
        success_count = 0
        
        # Record response time
        if record_value('response_time_ms', response_time_ms):
            success_count += 1
        
        # Record request size
        if record_value('request_size_bytes', request_size_bytes):
            success_count += 1
        
        # Record response size
        if record_value('response_size_bytes', response_size_bytes):
            success_count += 1
        
        # Increment counters
        if increment_counter('total_requests'):
            success_count += 1
        
        if success:
            if increment_counter('successful_requests'):
                success_count += 1
        else:
            if increment_counter('failed_requests'):
                success_count += 1
        
        # Consider successful if most operations succeeded
        return success_count >= 4
        
    except Exception as e:
        logger.error(f"Request metrics recording failed: {e}")
        return False

def get_http_client_health() -> Dict[str, Any]:
    """Get HTTP client health status - pure functional."""
    try:
        # Use singleton.py gateway for manager access
        metrics_manager = get_http_client_metrics_manager()
        
        if not metrics_manager:
            return {
                'healthy': False,
                'reason': 'Metrics manager not available',
                'timestamp': time.time()
            }
        
        # Get current metrics for health assessment
        metrics = get_http_client_metrics()
        
        if 'error' in metrics:
            return {
                'healthy': False,
                'reason': f"Metrics error: {metrics['error']}",
                'timestamp': time.time()
            }
        
        # Assess health based on metrics
        counters = metrics.get('counters', {})
        total_requests = counters.get('total_requests', 0)
        failed_requests = counters.get('failed_requests', 0)
        
        # Calculate failure rate
        failure_rate = (failed_requests / max(1, total_requests)) * 100
        
        # Health thresholds
        healthy = failure_rate < 20.0  # Less than 20% failure rate
        
        return {
            'healthy': healthy,
            'failure_rate_percent': round(failure_rate, 2),
            'total_requests': total_requests,
            'failed_requests': failed_requests,
            'timestamp': time.time()
        }
        
    except Exception as e:
        logger.error(f"HTTP client health check failed: {e}")
        return {
            'healthy': False,
            'reason': f"Health check error: {str(e)}",
            'timestamp': time.time()
        }

# ===== SECTION 4: METRIC CATEGORIES (PURE FUNCTIONAL) =====

def get_request_metrics() -> Dict[str, Any]:
    """Get request-specific metrics - pure functional."""
    try:
        metrics = get_http_client_metrics()
        
        return {
            'total_requests': metrics.get('counters', {}).get('total_requests', 0),
            'successful_requests': metrics.get('counters', {}).get('successful_requests', 0),
            'failed_requests': metrics.get('counters', {}).get('failed_requests', 0),
            'average_response_time_ms': metrics.get('averages', {}).get('response_time_ms', 0.0),
            'timestamp': metrics.get('timestamp', time.time())
        }
        
    except Exception as e:
        logger.error(f"Request metrics retrieval failed: {e}")
        return {}

def get_performance_metrics() -> Dict[str, Any]:
    """Get performance-specific metrics - pure functional."""
    try:
        metrics = get_http_client_metrics()
        
        return {
            'response_time_stats': {
                'average_ms': metrics.get('averages', {}).get('response_time_ms', 0.0),
                'total_recorded': metrics.get('counters', {}).get('response_time_recordings', 0)
            },
            'data_transfer_stats': {
                'average_request_bytes': metrics.get('averages', {}).get('request_size_bytes', 0.0),
                'average_response_bytes': metrics.get('averages', {}).get('response_size_bytes', 0.0)
            },
            'timestamp': metrics.get('timestamp', time.time())
        }
        
    except Exception as e:
        logger.error(f"Performance metrics retrieval failed: {e}")
        return {}

# ===== EXPORTED FUNCTIONS =====

__all__ = [
    # Core metrics operations
    'increment_counter', 'get_counter_value', 'record_value', 'get_average_value',
    
    # Metrics collection
    'get_http_client_metrics', 'reset_http_client_metrics', 
    'get_http_client_performance_summary',
    
    # Convenience functions
    'record_request_metrics', 'get_http_client_health',
    
    # Metric categories
    'get_request_metrics', 'get_performance_metrics'
]

# EOF - metrics_http_client.py is now purely functional with consolidated singleton access!
