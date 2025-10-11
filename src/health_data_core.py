"""
health_data_core.py
Version: 2025.10.03.01
Description: Health Data Management

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

import time
import json
import os
from typing import Dict, Any, List, Optional
from collections import deque
from dataclasses import dataclass, field
import threading

# ===== HEALTH DATA TEMPLATES (Template Optimization) =====

_HEALTH_DATA_TEMPLATE = {
    "total_requests": 0,
    "successful_requests": 0,
    "failed_requests": 0,
    "response_times": [],
    "recent_errors": [],
    "last_check": 0.0,
    "status": "unknown"
}

_COMPONENT_HEALTH_TEMPLATE = {
    "component_name": "",
    "status": "unknown",
    "last_check": 0.0,
    "response_time_ms": 0.0,
    "error_count": 0,
    "success_count": 0,
    "availability_percentage": 0.0,
    "details": {}
}

_SYSTEM_HEALTH_TEMPLATE = {
    "overall_status": "unknown",
    "overall_score": 0.0,
    "components": {},
    "checks_performed": 0,
    "last_full_check": 0.0,
    "health_trends": [],
    "critical_issues": [],
    "warnings": []
}

_HA_HEALTH_TEMPLATE = {
    "ha_connection_status": "unknown",
    "ha_response_time_ms": 0.0,
    "ha_entity_count": 0,
    "ha_last_update": 0.0,
    "ha_error_count": 0,
    "ha_success_rate": 0.0,
    "ha_available_domains": [],
    "ha_config_status": "unknown"
}

_LAMBDA_HEALTH_TEMPLATE = {
    "lambda_memory_used_mb": 0.0,
    "lambda_memory_limit_mb": 0.0,
    "lambda_remaining_time_ms": 0.0,
    "lambda_invocation_count": 0,
    "lambda_error_rate": 0.0,
    "lambda_avg_duration_ms": 0.0,
    "lambda_cold_starts": 0,
    "lambda_warm_starts": 0
}

_CACHE_HEALTH_TEMPLATE = {
    "cache_size": 0,
    "cache_max_size": 0,
    "cache_hit_rate": 0.0,
    "cache_memory_usage_mb": 0.0,
    "cache_evictions": 0,
    "cache_expired_items": 0,
    "cache_error_count": 0,
    "cache_last_cleanup": 0.0
}

_HTTP_HEALTH_TEMPLATE = {
    "http_total_requests": 0,
    "http_success_rate": 0.0,
    "http_avg_response_time_ms": 0.0,
    "http_timeout_count": 0,
    "http_connection_errors": 0,
    "http_active_connections": 0,
    "http_pool_size": 0,
    "http_last_request": 0.0
}

_USE_HEALTH_TEMPLATES = os.environ.get('USE_HEALTH_TEMPLATES', 'true').lower() == 'true'

@dataclass
class HealthMetrics:
    """Health metrics data structure."""
    component: str
    status: str
    timestamp: float = field(default_factory=time.time)
    response_time_ms: float = 0.0
    error_count: int = 0
    success_count: int = 0
    details: Dict[str, Any] = field(default_factory=dict)

def get_fresh_health_data() -> Dict[str, Any]:
    """Get fresh health data using template optimization."""
    try:
        if _USE_HEALTH_TEMPLATES:
            data = _HEALTH_DATA_TEMPLATE.copy()
            data["last_check"] = time.time()
            return data
        else:
            return {
                "total_requests": 0,
                "successful_requests": 0,
                "failed_requests": 0,
                "response_times": [],
                "recent_errors": [],
                "last_check": time.time(),
                "status": "unknown"
            }
    except Exception:
        return {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "last_check": time.time(),
            "status": "error"
        }

def get_fresh_component_health(component_name: str) -> Dict[str, Any]:
    """Get fresh component health using template optimization."""
    try:
        if _USE_HEALTH_TEMPLATES:
            data = _COMPONENT_HEALTH_TEMPLATE.copy()
            data["component_name"] = component_name
            data["last_check"] = time.time()
            return data
        else:
            return {
                "component_name": component_name,
                "status": "unknown",
                "last_check": time.time(),
                "response_time_ms": 0.0,
                "error_count": 0,
                "success_count": 0,
                "availability_percentage": 0.0,
                "details": {}
            }
    except Exception:
        return {
            "component_name": component_name,
            "status": "error",
            "last_check": time.time()
        }

def get_fresh_system_health() -> Dict[str, Any]:
    """Get fresh system health using template optimization."""
    try:
        if _USE_HEALTH_TEMPLATES:
            data = _SYSTEM_HEALTH_TEMPLATE.copy()
            data["last_full_check"] = time.time()
            return data
        else:
            return {
                "overall_status": "unknown",
                "overall_score": 0.0,
                "components": {},
                "checks_performed": 0,
                "last_full_check": time.time(),
                "health_trends": [],
                "critical_issues": [],
                "warnings": []
            }
    except Exception:
        return {
            "overall_status": "error",
            "overall_score": 0.0,
            "last_full_check": time.time()
        }

def get_fresh_ha_health() -> Dict[str, Any]:
    """Get fresh Home Assistant health using template optimization."""
    try:
        if _USE_HEALTH_TEMPLATES:
            data = _HA_HEALTH_TEMPLATE.copy()
            data["ha_last_update"] = time.time()
            return data
        else:
            return {
                "ha_connection_status": "unknown",
                "ha_response_time_ms": 0.0,
                "ha_entity_count": 0,
                "ha_last_update": time.time(),
                "ha_error_count": 0,
                "ha_success_rate": 0.0,
                "ha_available_domains": [],
                "ha_config_status": "unknown"
            }
    except Exception:
        return {
            "ha_connection_status": "error",
            "ha_last_update": time.time(),
            "ha_error_count": 1
        }

def get_fresh_lambda_health() -> Dict[str, Any]:
    """Get fresh Lambda health using template optimization."""
    try:
        if _USE_HEALTH_TEMPLATES:
            data = _LAMBDA_HEALTH_TEMPLATE.copy()
            return data
        else:
            return {
                "lambda_memory_used_mb": 0.0,
                "lambda_memory_limit_mb": 0.0,
                "lambda_remaining_time_ms": 0.0,
                "lambda_invocation_count": 0,
                "lambda_error_rate": 0.0,
                "lambda_avg_duration_ms": 0.0,
                "lambda_cold_starts": 0,
                "lambda_warm_starts": 0
            }
    except Exception:
        return {
            "lambda_memory_used_mb": 0.0,
            "lambda_error_rate": 1.0
        }

def get_fresh_cache_health() -> Dict[str, Any]:
    """Get fresh cache health using template optimization."""
    try:
        if _USE_HEALTH_TEMPLATES:
            data = _CACHE_HEALTH_TEMPLATE.copy()
            data["cache_last_cleanup"] = time.time()
            return data
        else:
            return {
                "cache_size": 0,
                "cache_max_size": 0,
                "cache_hit_rate": 0.0,
                "cache_memory_usage_mb": 0.0,
                "cache_evictions": 0,
                "cache_expired_items": 0,
                "cache_error_count": 0,
                "cache_last_cleanup": time.time()
            }
    except Exception:
        return {
            "cache_size": 0,
            "cache_error_count": 1,
            "cache_last_cleanup": time.time()
        }

def get_fresh_http_health() -> Dict[str, Any]:
    """Get fresh HTTP health using template optimization."""
    try:
        if _USE_HEALTH_TEMPLATES:
            data = _HTTP_HEALTH_TEMPLATE.copy()
            data["http_last_request"] = time.time()
            return data
        else:
            return {
                "http_total_requests": 0,
                "http_success_rate": 0.0,
                "http_avg_response_time_ms": 0.0,
                "http_timeout_count": 0,
                "http_connection_errors": 0,
                "http_active_connections": 0,
                "http_pool_size": 0,
                "http_last_request": time.time()
            }
    except Exception:
        return {
            "http_total_requests": 0,
            "http_success_rate": 0.0,
            "http_connection_errors": 1,
            "http_last_request": time.time()
        }

class HealthDataManager:
    """Health data manager with template optimization."""
    
    def __init__(self, max_history: int = 100):
        self.max_history = max_history
        self._health_cache = {}
        self._health_history = deque(maxlen=max_history)
        self._stats = {
            'health_checks': 0,
            'template_usage': 0,
            'legacy_usage': 0,
            'cache_hits': 0,
            'cache_misses': 0
        }
        self._lock = threading.RLock()
    
    def get_health_data(self, component: str, use_cache: bool = True) -> Dict[str, Any]:
        """Get health data for component with optional caching."""
        with self._lock:
            if use_cache and component in self._health_cache:
                self._stats['cache_hits'] += 1
                return self._health_cache[component].copy()
            
            self._stats['cache_misses'] += 1
            
            if component == "system":
                health_data = get_fresh_system_health()
            elif component == "homeassistant":
                health_data = get_fresh_ha_health()
            elif component == "lambda":
                health_data = get_fresh_lambda_health()
            elif component == "cache":
                health_data = get_fresh_cache_health()
            elif component == "http":
                health_data = get_fresh_http_health()
            else:
                health_data = get_fresh_component_health(component)
            
            if _USE_HEALTH_TEMPLATES:
                self._stats['template_usage'] += 1
            else:
                self._stats['legacy_usage'] += 1
            
            self._stats['health_checks'] += 1
            
            if use_cache:
                self._health_cache[component] = health_data.copy()
            
            return health_data
    
    def update_health_data(self, component: str, health_data: Dict[str, Any], 
                          store_in_history: bool = True):
        """Update health data for component."""
        with self._lock:
            self._health_cache[component] = health_data.copy()
            
            if store_in_history:
                history_entry = {
                    'timestamp': time.time(),
                    'component': component,
                    'health_data': health_data.copy()
                }
                self._health_history.append(history_entry)
    
    def get_combined_health(self, components: Optional[List[str]] = None) -> Dict[str, Any]:
        """Get combined health data for multiple components."""
        if components is None:
            components = ["system", "homeassistant", "lambda", "cache", "http"]
        
        combined_health = get_fresh_system_health()
        
        for component in components:
            component_health = self.get_health_data(component)
            combined_health["components"][component] = component_health
        
        combined_health["checks_performed"] = len(components)
        combined_health["last_full_check"] = time.time()
        
        overall_scores = []
        for comp_data in combined_health["components"].values():
            if isinstance(comp_data, dict):
                score = comp_data.get("availability_percentage", 0.0)
                if score > 0:
                    overall_scores.append(score)
        
        if overall_scores:
            combined_health["overall_score"] = sum(overall_scores) / len(overall_scores)
            if combined_health["overall_score"] >= 90:
                combined_health["overall_status"] = "healthy"
            elif combined_health["overall_score"] >= 70:
                combined_health["overall_status"] = "degraded"
            else:
                combined_health["overall_status"] = "unhealthy"
        else:
            combined_health["overall_status"] = "unknown"
        
        return combined_health
    
    def get_health_trends(self, component: Optional[str] = None, 
                         time_window_seconds: int = 3600) -> List[Dict[str, Any]]:
        """Get health trends for component within time window."""
        with self._lock:
            current_time = time.time()
            cutoff_time = current_time - time_window_seconds
            
            trends = []
            for entry in self._health_history:
                if entry['timestamp'] >= cutoff_time:
                    if component is None or entry['component'] == component:
                        trends.append(entry)
            
            return trends
    
    def clear_health_cache(self, component: Optional[str] = None):
        """Clear health cache for component or all components."""
        with self._lock:
            if component:
                self._health_cache.pop(component, None)
            else:
                self._health_cache.clear()
    
    def clear_health_history(self):
        """Clear health history."""
        with self._lock:
            self._health_history.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get health data manager statistics."""
        with self._lock:
            total_operations = self._stats['template_usage'] + self._stats['legacy_usage']
            template_usage_rate = self._stats['template_usage'] / max(total_operations, 1)
            cache_hit_rate = self._stats['cache_hits'] / max(self._stats['cache_hits'] + self._stats['cache_misses'], 1)
            
            return {
                'health_checks': self._stats['health_checks'],
                'template_usage_rate': template_usage_rate,
                'cache_hit_rate': cache_hit_rate,
                'template_optimization_enabled': _USE_HEALTH_TEMPLATES,
                'cache_size': len(self._health_cache),
                'history_size': len(self._health_history),
                'max_history': self.max_history,
                'stats': self._stats.copy()
            }
    
    def reset_stats(self):
        """Reset health data manager statistics."""
        with self._lock:
            self._stats = {
                'health_checks': 0,
                'template_usage': 0,
                'legacy_usage': 0,
                'cache_hits': 0,
                'cache_misses': 0
            }

# Global health data manager instance
_health_data_manager = HealthDataManager()

def get_health_data_manager() -> HealthDataManager:
    """Get global health data manager."""
    return _health_data_manager

# EOF
