"""
metrics_singleton.py - Singleton Metrics Collection
Version: 2025.09.23.02
Description: Singleton lifecycle and access metrics (LEGACY CLEANED)

ARCHITECTURE: SECONDARY IMPLEMENTATION
- Lightweight metrics collection for Lambda
- Direct integration with core singleton system
- Memory-efficient data structures
- ALL LEGACY BYPASS FUNCTIONS REMOVED

FOLLOWS PROJECT_ARCHITECTURE_REFERENCE.md
"""

import logging
import time
import threading
from typing import Dict, Any, Optional, List, Set
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict

logger = logging.getLogger(__name__)

# ===== METRICS TYPES =====

class SingletonEvent(Enum):
    """Singleton lifecycle events."""
    CREATED = "created"
    ACCESSED = "accessed"
    RESET = "reset"
    ERROR = "error"
    CLEANUP = "cleanup"

class SingletonState(Enum):
    """Singleton states."""
    NOT_CREATED = "not_created"
    INITIALIZING = "initializing"
    READY = "ready"
    RESETTING = "resetting"
    ERROR = "error"

@dataclass
class SingletonMetrics:
    """Consolidated singleton metrics for Lambda optimization."""
    # Core counters
    total_created: int = 0
    total_accessed: int = 0
    total_resets: int = 0
    total_errors: int = 0
    
    # Performance tracking
    avg_creation_time_ms: float = 0.0
    total_creation_time_ms: float = 0.0
    
    # State tracking
    active_singletons: int = 0
    state_distribution: Dict[str, int] = field(default_factory=dict)
    
    # Memory tracking
    estimated_memory_bytes: int = 0
    
    # Timeline
    first_creation: Optional[float] = None
    last_activity: Optional[float] = None
    
    def success_rate(self) -> float:
        """Calculate success rate percentage."""
        total_ops = self.total_created + self.total_accessed
        if total_ops == 0:
            return 100.0
        return ((total_ops - self.total_errors) / total_ops) * 100.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'totals': {
                'created': self.total_created,
                'accessed': self.total_accessed,
                'resets': self.total_resets,
                'errors': self.total_errors
            },
            'performance': {
                'avg_creation_time_ms': self.avg_creation_time_ms,
                'total_creation_time_ms': self.total_creation_time_ms,
                'success_rate_percent': self.success_rate()
            },
            'status': {
                'active_singletons': self.active_singletons,
                'states': self.state_distribution,
                'memory_bytes': self.estimated_memory_bytes
            },
            'timeline': {
                'first_creation': self.first_creation,
                'last_activity': self.last_activity,
                'duration_seconds': (self.last_activity - self.first_creation) if self.first_creation and self.last_activity else 0
            }
        }

# ===== METRICS COLLECTOR =====

class SingletonMetricsCollector:
    """Lightweight metrics collector for singleton operations."""
    
    def __init__(self):
        self._metrics = SingletonMetrics()
        self._lock = threading.Lock()
        self._event_history: List[Dict[str, Any]] = []
        self._max_history = 50  # Limit for Lambda memory constraints
        
        logger.debug("Singleton metrics collector initialized")
    
    def record_creation(self, singleton_name: str, creation_time_ms: float = 0.0, success: bool = True) -> None:
        """Record singleton creation event."""
        with self._lock:
            current_time = time.time()
            
            if success:
                self._metrics.total_created += 1
                self._metrics.active_singletons += 1
                
                # Update creation time metrics
                if creation_time_ms > 0:
                    self._metrics.total_creation_time_ms += creation_time_ms
                    self._metrics.avg_creation_time_ms = (
                        self._metrics.total_creation_time_ms / self._metrics.total_created
                    )
                
                # Update timeline
                if self._metrics.first_creation is None:
                    self._metrics.first_creation = current_time
                self._metrics.last_activity = current_time
                
                # Update state distribution
                self._metrics.state_distribution[SingletonState.READY.value] = (
                    self._metrics.state_distribution.get(SingletonState.READY.value, 0) + 1
                )
            else:
                self._metrics.total_errors += 1
                self._metrics.state_distribution[SingletonState.ERROR.value] = (
                    self._metrics.state_distribution.get(SingletonState.ERROR.value, 0) + 1
                )
            
            # Record event
            self._record_event(SingletonEvent.CREATED, singleton_name, success, creation_time_ms)
    
    def record_access(self, singleton_name: str, success: bool = True) -> None:
        """Record singleton access event."""
        with self._lock:
            current_time = time.time()
            
            if success:
                self._metrics.total_accessed += 1
                self._metrics.last_activity = current_time
            else:
                self._metrics.total_errors += 1
            
            self._record_event(SingletonEvent.ACCESSED, singleton_name, success)
    
    def record_reset(self, singleton_name: str, success: bool = True) -> None:
        """Record singleton reset event."""
        with self._lock:
            current_time = time.time()
            
            if success:
                self._metrics.total_resets += 1
                if self._metrics.active_singletons > 0:
                    self._metrics.active_singletons -= 1
                self._metrics.last_activity = current_time
                
                # Update state distribution
                self._metrics.state_distribution[SingletonState.READY.value] = max(0,
                    self._metrics.state_distribution.get(SingletonState.READY.value, 0) - 1
                )
            else:
                self._metrics.total_errors += 1
            
            self._record_event(SingletonEvent.RESET, singleton_name, success)
    
    def _record_event(self, event_type: SingletonEvent, singleton_name: str, success: bool, duration_ms: float = 0.0) -> None:
        """Record event in history with memory limits."""
        event = {
            'event': event_type.value,
            'singleton': singleton_name,
            'success': success,
            'timestamp': time.time(),
            'duration_ms': duration_ms
        }
        
        self._event_history.append(event)
        
        # Maintain memory limits
        if len(self._event_history) > self._max_history:
            self._event_history = self._event_history[-self._max_history:]
    
    def get_metrics(self) -> SingletonMetrics:
        """Get current metrics snapshot."""
        with self._lock:
            # Update estimated memory usage
            self._metrics.estimated_memory_bytes = (
                len(self._event_history) * 200 +  # Rough estimate per event
                len(str(self._metrics.state_distribution)) * 4
            )
            return self._metrics
    
    def get_summary(self) -> Dict[str, Any]:
        """Get metrics summary optimized for Lambda."""
        metrics = self.get_metrics()
        return {
            'active_singletons': metrics.active_singletons,
            'total_operations': metrics.total_created + metrics.total_accessed,
            'success_rate': metrics.success_rate(),
            'avg_creation_ms': metrics.avg_creation_time_ms,
            'memory_bytes': metrics.estimated_memory_bytes,
            'last_activity': metrics.last_activity,
            'healthy': metrics.total_errors < 5 and metrics.success_rate() > 95
        }
    
    def reset_metrics(self) -> None:
        """Reset all metrics - for testing or cleanup."""
        with self._lock:
            self._metrics = SingletonMetrics()
            self._event_history.clear()

# ===== GLOBAL COLLECTOR =====

_metrics_collector: Optional[SingletonMetricsCollector] = None
_collector_lock = threading.Lock()

def get_metrics_collector() -> SingletonMetricsCollector:
    """Get global metrics collector."""
    global _metrics_collector
    if _metrics_collector is None:
        with _collector_lock:
            if _metrics_collector is None:
                _metrics_collector = SingletonMetricsCollector()
    return _metrics_collector

# ===== GATEWAY FUNCTIONS =====

def record_singleton_creation(singleton_name: str, creation_time_ms: float = 0.0, success: bool = True) -> None:
    """Record singleton creation for metrics."""
    collector = get_metrics_collector()
    collector.record_creation(singleton_name, creation_time_ms, success)

def record_singleton_access(singleton_name: str, success: bool = True) -> None:
    """Record singleton access for metrics."""
    collector = get_metrics_collector()
    collector.record_access(singleton_name, success)

def record_singleton_reset(singleton_name: str, success: bool = True) -> None:
    """Record singleton reset for metrics."""
    collector = get_metrics_collector()
    collector.record_reset(singleton_name, success)

def get_singleton_metrics() -> Dict[str, Any]:
    """Get current singleton metrics."""
    collector = get_metrics_collector()
    return collector.get_summary()

def reset_singleton_metrics() -> None:
    """Reset singleton metrics."""
    collector = get_metrics_collector()
    collector.reset_metrics()

# EOF
