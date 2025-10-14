"""
aws/metrics_types.py - Metrics type definitions and data structures
Version: 2025.10.14.04
Description: Enumerations and data classes for metrics subsystem

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

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Optional
from collections import defaultdict


# ===== ENUMERATIONS =====

class MetricOperation(Enum):
    """Generic metric operations."""
    RECORD = "record"
    INCREMENT = "increment"
    DECREMENT = "decrement"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    GET_METRIC = "get_metric"
    GET_STATS = "get_stats"
    CLEAR = "clear"
    # Phase 4 Task #7: Dispatcher timing operations
    RECORD_DISPATCHER_TIMING = "record_dispatcher_timing"
    GET_DISPATCHER_STATS = "get_dispatcher_stats"
    GET_OPERATION_METRICS = "get_operation_metrics"


class MetricType(Enum):
    """Metric types."""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"


class ResponseType(Enum):
    """Response types for tracking."""
    SUCCESS = "success"
    ERROR = "error"
    TIMEOUT = "timeout"
    CACHED = "cached"
    FALLBACK = "fallback"


# ===== DATA STRUCTURES =====

@dataclass
class ResponseMetrics:
    """Response metrics data structure."""
    total_responses: int = 0
    successful_responses: int = 0
    error_responses: int = 0
    timeout_responses: int = 0
    cached_responses: int = 0
    fallback_responses: int = 0
    avg_response_time_ms: float = 0.0
    fastest_response_ms: float = float('inf')
    slowest_response_ms: float = 0.0
    cache_hit_rate: float = 0.0
    
    def success_rate(self) -> float:
        """Calculate success rate percentage."""
        return (self.successful_responses / self.total_responses * 100) if self.total_responses > 0 else 0.0


@dataclass
class HTTPClientMetrics:
    """HTTP client metrics data structure."""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    avg_response_time_ms: float = 0.0
    total_response_time_ms: float = 0.0
    requests_by_method: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    requests_by_status: Dict[int, int] = field(default_factory=lambda: defaultdict(int))


@dataclass
class CircuitBreakerMetrics:
    """Circuit breaker metrics data structure."""
    state: str = "closed"
    failure_count: int = 0
    success_count: int = 0
    last_failure_time: Optional[float] = None
    total_requests: int = 0


__all__ = [
    'MetricOperation',
    'MetricType',
    'ResponseType',
    'ResponseMetrics',
    'HTTPClientMetrics',
    'CircuitBreakerMetrics',
]

# EOF
