"""
Usage Analytics - Track Module Loading and Usage Patterns
Version: 2025.09.29.01
Daily Revision: 001

Provides analytics for LIGS optimization and intelligent lazy loading decisions.
"""

import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from collections import defaultdict

class UsageAnalytics:
    """
    Track and analyze module usage patterns for optimization.
    """
    
    def __init__(self):
        self._request_patterns = []
        self._module_frequency = defaultdict(int)
        self._module_combinations = defaultdict(int)
        self._cold_start_modules = []
        self._request_count = 0
    
    def record_request(self, loaded_modules: List[str], request_type: Optional[str] = None):
        """
        Record which modules were loaded for a request.
        
        Args:
            loaded_modules: List of module names loaded during request
            request_type: Optional request type identifier
        """
        self._request_count += 1
        
        pattern = {
            'timestamp': datetime.utcnow().isoformat(),
            'request_type': request_type,
            'modules': sorted(loaded_modules),
            'module_count': len(loaded_modules)
        }
        self._request_patterns.append(pattern)
        
        for module in loaded_modules:
            self._module_frequency[module] += 1
        
        module_combo = tuple(sorted(loaded_modules))
        self._module_combinations[module_combo] += 1
    
    def get_hot_modules(self, threshold: float = 0.5) -> List[str]:
        """
        Get modules loaded in > threshold% of requests.
        
        Args:
            threshold: Percentage threshold (0.0 to 1.0)
            
        Returns:
            List of frequently used module names
        """
        if self._request_count == 0:
            return []
        
        hot_modules = []
        for module, count in self._module_frequency.items():
            if count / self._request_count > threshold:
                hot_modules.append(module)
        
        return sorted(hot_modules, key=lambda m: self._module_frequency[m], reverse=True)
    
    def get_cold_modules(self, threshold: float = 0.1) -> List[str]:
        """
        Get modules loaded in < threshold% of requests.
        
        Args:
            threshold: Percentage threshold (0.0 to 1.0)
            
        Returns:
            List of rarely used module names
        """
        if self._request_count == 0:
            return []
        
        cold_modules = []
        for module, count in self._module_frequency.items():
            if count / self._request_count < threshold:
                cold_modules.append(module)
        
        return sorted(cold_modules, key=lambda m: self._module_frequency[m])
    
    def get_common_patterns(self, top_n: int = 5) -> List[Dict[str, Any]]:
        """
        Get most common module loading patterns.
        
        Args:
            top_n: Number of top patterns to return
            
        Returns:
            List of pattern dictionaries with modules and frequency
        """
        sorted_patterns = sorted(
            self._module_combinations.items(),
            key=lambda x: x[1],
            reverse=True
        )[:top_n]
        
        patterns = []
        for modules, count in sorted_patterns:
            patterns.append({
                'modules': list(modules),
                'frequency': count,
                'percentage': (count / self._request_count * 100) if self._request_count > 0 else 0
            })
        
        return patterns
    
    def get_optimization_recommendations(self) -> Dict[str, Any]:
        """
        Generate optimization recommendations based on usage patterns.
        
        Returns:
            Dictionary with optimization suggestions
        """
        hot_modules = self.get_hot_modules(threshold=0.7)
        cold_modules = self.get_cold_modules(threshold=0.1)
        common_patterns = self.get_common_patterns(top_n=3)
        
        recommendations = {
            'eager_load_candidates': hot_modules,
            'eager_load_reason': 'Loaded in >70% of requests - consider eager loading',
            'keep_lazy_candidates': cold_modules,
            'keep_lazy_reason': 'Loaded in <10% of requests - keep lazy loading',
            'common_patterns': common_patterns,
            'pattern_optimization': 'Consider creating fast paths for common patterns'
        }
        
        return recommendations
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive usage summary.
        
        Returns:
            Dictionary with usage statistics
        """
        return {
            'total_requests': self._request_count,
            'unique_modules_used': len(self._module_frequency),
            'module_frequency': dict(self._module_frequency),
            'hot_modules': self.get_hot_modules(threshold=0.5),
            'cold_modules': self.get_cold_modules(threshold=0.2),
            'common_patterns': self.get_common_patterns(top_n=5),
            'optimization_recommendations': self.get_optimization_recommendations()
        }
    
    def export_data(self) -> str:
        """
        Export analytics data as JSON.
        
        Returns:
            JSON string with all analytics data
        """
        data = {
            'request_patterns': self._request_patterns,
            'module_frequency': dict(self._module_frequency),
            'module_combinations': {
                str(k): v for k, v in self._module_combinations.items()
            },
            'summary': self.get_summary()
        }
        return json.dumps(data, indent=2)
    
    def reset(self):
        """Reset all analytics data."""
        self._request_patterns.clear()
        self._module_frequency.clear()
        self._module_combinations.clear()
        self._cold_start_modules.clear()
        self._request_count = 0


_ANALYTICS = UsageAnalytics()


def record_request_usage(loaded_modules: List[str], request_type: Optional[str] = None):
    """Record module usage for current request."""
    _ANALYTICS.record_request(loaded_modules, request_type)


def get_usage_summary() -> Dict[str, Any]:
    """Get usage analytics summary."""
    return _ANALYTICS.get_summary()


def get_optimization_recommendations() -> Dict[str, Any]:
    """Get optimization recommendations."""
    return _ANALYTICS.get_optimization_recommendations()


def export_analytics() -> str:
    """Export analytics data as JSON."""
    return _ANALYTICS.export_data()


def reset_analytics():
    """Reset analytics data."""
    _ANALYTICS.reset()
