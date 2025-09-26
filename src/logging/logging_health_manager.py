"""
logging_health_manager.py - CONSOLIDATED: Health Manager with Analysis and Core
Version: 2025.09.23.02
Description: Consolidated health manager with analysis and core functionality

CONSOLIDATED FROM:
- logging_health_manager_analysis.py
- logging_health_manager_core.py
- Original logging_health_manager.py

ARCHITECTURE: SECONDARY IMPLEMENTATION
- Internal health manager for logging.py gateway
- Memory-optimized for Lambda constraints
"""

import time
import threading
import logging
from typing import Dict, Any, Optional, List, Deque
from dataclasses import dataclass, field
from enum import Enum
from collections import deque, defaultdict, Counter
import statistics

logger = logging.getLogger(__name__)

class HealthStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

class HealthCategory(Enum):
    SYSTEM = "system"
    MEMORY = "memory"
    COST = "cost"
    SECURITY = "security"
    PERFORMANCE = "performance"
    INTEGRATION = "integration"

@dataclass
class OptimizedHealthRecord:
    timestamp: float
    category: HealthCategory
    status: HealthStatus
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    component: str = "unknown"
    response_time_ms: Optional[float] = None

@dataclass
class HealthThresholds:
    error_rate_threshold: float = 0.1
    response_time_threshold_ms: float = 5000.0
    memory_threshold_mb: float = 100.0
    error_rate_window: float = 300.0
    response_time_window: float = 300.0
    max_error_history: int = 100  # Reduced from 1000
    max_request_history: int = 50  # Reduced from 500

class ConsolidatedHealthManager:
    """Consolidated health manager with memory optimization."""
    
    def __init__(self, thresholds: Optional[HealthThresholds] = None):
        self.thresholds = thresholds or HealthThresholds()
        self._lock = threading.RLock()
        
        # Optimized collections
        self._health_records = deque(maxlen=200)  # Bounded
        self._error_times = deque(maxlen=self.thresholds.max_error_history)
        self._request_times = deque(maxlen=self.thresholds.max_request_history)
        self._success_count = 0
        self._error_count = 0
        self._last_cleanup = time.time()

    def record_ha_success(self, response_time_ms: Optional[float] = None) -> None:
        """Record Home Assistant success."""
        current_time = time.time()
        
        with self._lock:
            self._success_count += 1
            if response_time_ms:
                self._request_times.append((current_time, response_time_ms))
            
            self._health_records.append(OptimizedHealthRecord(
                timestamp=current_time,
                category=HealthCategory.INTEGRATION,
                status=HealthStatus.HEALTHY,
                message="HA operation successful",
                response_time_ms=response_time_ms
            ))
            
            self._cleanup_old_records()

    def record_ha_failure(self, error: Exception, response_status: Optional[int] = None) -> None:
        """Record Home Assistant failure."""
        current_time = time.time()
        
        with self._lock:
            self._error_count += 1
            self._error_times.append(current_time)
            
            self._health_records.append(OptimizedHealthRecord(
                timestamp=current_time,
                category=HealthCategory.INTEGRATION,
                status=HealthStatus.UNHEALTHY,
                message=f"HA operation failed: {str(error)[:100]}",
                details={
                    'error_type': type(error).__name__,
                    'response_status': response_status
                }
            ))
            
            self._cleanup_old_records()

    def is_ha_healthy(self) -> bool:
        """Check if Home Assistant integration is healthy."""
        try:
            error_rate = self.get_error_rate()
            avg_response_time = self.get_average_response_time()
            
            is_healthy = (
                error_rate < self.thresholds.error_rate_threshold and
                (avg_response_time is None or avg_response_time < self.thresholds.response_time_threshold_ms)
            )
            
            return is_healthy
        except Exception:
            return False

    def get_health_status(self) -> Dict[str, Any]:
        """Get comprehensive health status."""
        with self._lock:
            current_time = time.time()
            
            # Calculate metrics
            error_rate = self.get_error_rate()
            avg_response_time = self.get_average_response_time()
            total_requests = self._success_count + self._error_count
            
            # Determine overall status
            if error_rate > 0.5:
                status = HealthStatus.CRITICAL
            elif error_rate > self.thresholds.error_rate_threshold:
                status = HealthStatus.UNHEALTHY
            elif avg_response_time and avg_response_time > self.thresholds.response_time_threshold_ms:
                status = HealthStatus.DEGRADED
            else:
                status = HealthStatus.HEALTHY
            
            return {
                'overall_status': status.value,
                'is_healthy': self.is_ha_healthy(),
                'metrics': {
                    'error_rate': error_rate,
                    'average_response_time_ms': avg_response_time,
                    'total_requests': total_requests,
                    'success_count': self._success_count,
                    'error_count': self._error_count
                },
                'recent_records': len(self._health_records),
                'thresholds': {
                    'error_rate_threshold': self.thresholds.error_rate_threshold,
                    'response_time_threshold_ms': self.thresholds.response_time_threshold_ms
                }
            }

    def get_health_trend(self, window_minutes: int = 5) -> Dict[str, Any]:
        """Analyze health trend over time window."""
        current_time = time.time()
        window_start = current_time - (window_minutes * 60)
        
        with self._lock:
            recent_records = [
                r for r in self._health_records 
                if r.timestamp >= window_start
            ]
            
            if not recent_records:
                return {
                    'trend': 'stable',
                    'direction': 'neutral',
                    'confidence': 0.0,
                    'sample_size': 0
                }
            
            # Analyze status distribution
            status_counts = Counter(r.status.value for r in recent_records)
            healthy_ratio = status_counts.get('healthy', 0) / len(recent_records)
            
            # Determine trend
            if healthy_ratio > 0.8:
                trend = 'improving'
                direction = 'positive'
            elif healthy_ratio < 0.3:
                trend = 'degrading'
                direction = 'negative'
            else:
                trend = 'stable'
                direction = 'neutral'
            
            return {
                'trend': trend,
                'direction': direction,
                'confidence': min(len(recent_records) / 10, 1.0),
                'sample_size': len(recent_records),
                'healthy_ratio': healthy_ratio,
                'window_minutes': window_minutes
            }

    def get_error_rate(self) -> float:
        """Calculate current error rate."""
        current_time = time.time()
        window_start = current_time - self.thresholds.error_rate_window
        
        with self._lock:
            recent_errors = [t for t in self._error_times if t >= window_start]
            recent_requests = [
                t for t, _ in self._request_times if t >= window_start
            ]
            
            total_recent = len(recent_errors) + len(recent_requests)
            
            if total_recent == 0:
                return 0.0
            
            return len(recent_errors) / total_recent

    def get_average_response_time(self) -> Optional[float]:
        """Calculate average response time."""
        current_time = time.time()
        window_start = current_time - self.thresholds.response_time_window
        
        with self._lock:
            recent_times = [
                duration for timestamp, duration in self._request_times
                if timestamp >= window_start
            ]
            
            if not recent_times:
                return None
            
            return statistics.mean(recent_times)

    def get_recommendations(self) -> List[str]:
        """Get health improvement recommendations."""
        recommendations = []
        
        try:
            error_rate = self.get_error_rate()
            avg_response_time = self.get_average_response_time()
            
            if error_rate > self.thresholds.error_rate_threshold:
                recommendations.append(
                    f"High error rate ({error_rate:.2%}). Check Home Assistant connectivity."
                )
            
            if avg_response_time and avg_response_time > self.thresholds.response_time_threshold_ms:
                recommendations.append(
                    f"Slow response time ({avg_response_time:.0f}ms). Consider optimization."
                )
            
            if self._error_count > self._success_count:
                recommendations.append(
                    "More errors than successes. Check Home Assistant configuration."
                )
            
            if not recommendations:
                recommendations.append("System appears healthy. Continue monitoring.")
                
        except Exception:
            recommendations.append("Unable to analyze health metrics.")
        
        return recommendations

    def analyze_performance_patterns(self) -> Dict[str, Any]:
        """Analyze performance patterns and anomalies."""
        with self._lock:
            if len(self._request_times) < 5:
                return {
                    'analysis': 'insufficient_data',
                    'sample_size': len(self._request_times)
                }
            
            # Extract response times
            response_times = [duration for _, duration in self._request_times]
            
            # Statistical analysis
            mean_time = statistics.mean(response_times)
            median_time = statistics.median(response_times)
            
            try:
                std_dev = statistics.stdev(response_times) if len(response_times) > 1 else 0
            except statistics.StatisticsError:
                std_dev = 0
            
            # Detect outliers (beyond 2 std deviations)
            outliers = [
                t for t in response_times 
                if abs(t - mean_time) > 2 * std_dev
            ] if std_dev > 0 else []
            
            # Performance classification
            if mean_time < 1000:
                performance = 'excellent'
            elif mean_time < 3000:
                performance = 'good'
            elif mean_time < 5000:
                performance = 'acceptable'
            else:
                performance = 'poor'
            
            return {
                'analysis': 'complete',
                'performance': performance,
                'statistics': {
                    'mean_ms': round(mean_time, 2),
                    'median_ms': round(median_time, 2),
                    'std_dev_ms': round(std_dev, 2),
                    'min_ms': min(response_times),
                    'max_ms': max(response_times)
                },
                'outliers': {
                    'count': len(outliers),
                    'percentage': len(outliers) / len(response_times) * 100
                },
                'sample_size': len(response_times)
            }

    def _cleanup_old_records(self) -> None:
        """Cleanup old records periodically."""
        current_time = time.time()
        
        # Cleanup every 5 minutes
        if (current_time - self._last_cleanup) < 300:
            return
        
        # Collections are already bounded by deque maxlen
        self._last_cleanup = current_time

    def reset_health_data(self) -> Dict[str, Any]:
        """Reset all health data."""
        with self._lock:
            before_records = len(self._health_records)
            before_errors = len(self._error_times)
            before_requests = len(self._request_times)
            
            self._health_records.clear()
            self._error_times.clear()
            self._request_times.clear()
            self._success_count = 0
            self._error_count = 0
            
            return {
                'reset_completed': True,
                'cleared': {
                    'health_records': before_records,
                    'error_times': before_errors,
                    'request_times': before_requests
                }
            }

# ===== GLOBAL HEALTH MANAGER =====

_consolidated_health_manager: Optional[ConsolidatedHealthManager] = None
_health_manager_lock = threading.Lock()

def get_consolidated_health_manager() -> ConsolidatedHealthManager:
    """Get global consolidated health manager."""
    global _consolidated_health_manager
    if _consolidated_health_manager is None:
        with _health_manager_lock:
            if _consolidated_health_manager is None:
                _consolidated_health_manager = ConsolidatedHealthManager()
    return _consolidated_health_manager

# ===== PUBLIC INTERFACE FUNCTIONS =====

def record_ha_success(response_time_ms: Optional[float] = None) -> None:
    """Record successful Home Assistant interaction."""
    manager = get_consolidated_health_manager()
    manager.record_ha_success(response_time_ms)

def record_ha_failure(error: Exception, response_status: Optional[int] = None) -> None:
    """Record failed Home Assistant interaction."""
    manager = get_consolidated_health_manager()
    manager.record_ha_failure(error, response_status)

def is_ha_healthy() -> bool:
    """Check if Home Assistant integration is healthy."""
    manager = get_consolidated_health_manager()
    return manager.is_ha_healthy()

def get_health_status() -> Dict[str, Any]:
    """Get comprehensive health status."""
    manager = get_consolidated_health_manager()
    return manager.get_health_status()

def get_health_trend(window_minutes: int = 5) -> Dict[str, Any]:
    """Get health trend analysis."""
    manager = get_consolidated_health_manager()
    return manager.get_health_trend(window_minutes)

def get_error_rate() -> float:
    """Get current error rate."""
    manager = get_consolidated_health_manager()
    return manager.get_error_rate()

def get_recommendations() -> List[str]:
    """Get health improvement recommendations."""
    manager = get_consolidated_health_manager()
    return manager.get_recommendations()

def analyze_performance_patterns() -> Dict[str, Any]:
    """Analyze performance patterns."""
    manager = get_consolidated_health_manager()
    return manager.analyze_performance_patterns()

def reset_health_data() -> Dict[str, Any]:
    """Reset all health data."""
    manager = get_consolidated_health_manager()
    return manager.reset_health_data()

# EOF
