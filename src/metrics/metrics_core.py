"""
Metrics Core - Metrics Collection and Tracking
Version: 2025.09.30.02
Description: Metrics implementation with shared utilities integration

ARCHITECTURE: CORE IMPLEMENTATION - INTERNAL ONLY
- Lazy-loaded by gateway.py
- Uses shared_utilities for error handling

OPTIMIZATION: Phase 1 Complete
- Integrated handle_operation_error() from shared_utilities
- Enhanced error handling consistency

Revolutionary Gateway Optimization: SUGA + LIGS + ZAFP Compatible

Copyright 2024 Anthropic PBC
Licensed under the Apache License, Version 2.0
"""

from typing import Dict, Optional
from collections import defaultdict
from threading import Lock


class MetricsCore:
    """In-memory metrics collection with CloudWatch compatibility and error handling."""
    
    def __init__(self):
        self._metrics: Dict[str, float] = {}
        self._counters: Dict[str, float] = defaultdict(float)
        self._lock = Lock()
        self._metric_count = 0
        self._max_metrics = 10
    
    def record(self, name: str, value: float, unit: str = "None", **kwargs):
        """Record a metric value with error handling."""
        try:
            with self._lock:
                if name not in self._metrics and self._metric_count >= self._max_metrics:
                    return
                
                if name not in self._metrics:
                    self._metric_count += 1
                
                self._metrics[name] = value
        except Exception as e:
            self._handle_error('record', e)
    
    def get(self, name: str) -> Optional[float]:
        """Get metric value with error handling."""
        try:
            with self._lock:
                return self._metrics.get(name)
        except Exception as e:
            self._handle_error('get', e)
            return None
    
    def increment(self, name: str, value: float = 1.0, **kwargs):
        """Increment counter metric with error handling."""
        try:
            with self._lock:
                if name not in self._counters and self._metric_count >= self._max_metrics:
                    return
                
                if name not in self._counters:
                    self._metric_count += 1
                
                self._counters[name] += value
        except Exception as e:
            self._handle_error('increment', e)
    
    def get_counter(self, name: str) -> float:
        """Get counter value with error handling."""
        try:
            with self._lock:
                return self._counters.get(name, 0.0)
        except Exception as e:
            self._handle_error('get_counter', e)
            return 0.0
    
    def get_all_metrics(self) -> Dict[str, float]:
        """Get all metrics with error handling."""
        try:
            with self._lock:
                return {**self._metrics, **self._counters}
        except Exception as e:
            self._handle_error('get_all_metrics', e)
            return {}
    
    def reset(self):
        """Reset all metrics with error handling."""
        try:
            with self._lock:
                self._metrics.clear()
                self._counters.clear()
                self._metric_count = 0
        except Exception as e:
            self._handle_error('reset', e)
    
    def _handle_error(self, operation: str, error: Exception):
        """Handle errors using shared utilities."""
        try:
            from .shared_utilities import handle_operation_error
            handle_operation_error(
                interface="metrics",
                operation=operation,
                error=error
            )
        except Exception:
            pass


_METRICS = MetricsCore()


def _execute_record_implementation(name: str, value: float, unit: str = "None", **kwargs):
    """Execute metric recording."""
    return _METRICS.record(name, value, unit, **kwargs)


def _execute_get_implementation(name: str, **kwargs) -> Optional[float]:
    """Execute metric get."""
    return _METRICS.get(name)


def _execute_increment_implementation(name: str, value: float = 1.0, **kwargs):
    """Execute counter increment."""
    return _METRICS.increment(name, value, **kwargs)


def _execute_get_counter_implementation(name: str, **kwargs) -> float:
    """Execute counter get."""
    return _METRICS.get_counter(name)


def _execute_get_all_implementation(**kwargs) -> Dict[str, float]:
    """Execute get all metrics."""
    return _METRICS.get_all_metrics()


def _execute_reset_implementation(**kwargs):
    """Execute metrics reset."""
    return _METRICS.reset()


__all__ = [
    '_execute_record_implementation',
    '_execute_get_implementation',
    '_execute_increment_implementation',
    '_execute_get_counter_implementation',
    '_execute_get_all_implementation',
    '_execute_reset_implementation',
]

# EOF
