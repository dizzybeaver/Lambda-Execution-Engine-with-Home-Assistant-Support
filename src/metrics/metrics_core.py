"""
metrics_core.py - Core Metrics Implementation for SUGA
Version: 2025.09.29.03
Daily Revision: 01

REVOLUTIONARY ARCHITECTURE - Optimized for Single Universal Gateway
FREE TIER COMPLIANCE: 100% - CloudWatch 10 metric limit enforced
"""

import time
from typing import Any, Dict, Optional, List
from dataclasses import dataclass, field
from collections import defaultdict

@dataclass
class MetricData:
    """Metric data point."""
    name: str
    value: float
    unit: str
    timestamp: float
    dimensions: Dict[str, str] = field(default_factory=dict)

@dataclass
class MetricStats:
    """Metric statistics."""
    count: int = 0
    sum: float = 0.0
    min: float = float('inf')
    max: float = float('-inf')
    avg: float = 0.0
    
    def update(self, value: float) -> None:
        """Update statistics with new value."""
        self.count += 1
        self.sum += value
        self.min = min(self.min, value)
        self.max = max(self.max, value)
        self.avg = self.sum / self.count

_METRICS: Dict[str, List[MetricData]] = defaultdict(list)
_METRIC_STATS: Dict[str, MetricStats] = defaultdict(MetricStats)
_MAX_METRICS = 10
_ACTIVE_METRICS: List[str] = []
_METRIC_BUFFER_SIZE = 100

def set_max_metrics(limit: int) -> None:
    """Set maximum number of active metrics."""
    global _MAX_METRICS
    _MAX_METRICS = limit

def get_active_metrics() -> List[str]:
    """Get list of active metrics."""
    return _ACTIVE_METRICS.copy()

def _ensure_metric_limit(metric_name: str) -> bool:
    """Ensure metric count stays within limit."""
    if metric_name in _ACTIVE_METRICS:
        return True
    
    if len(_ACTIVE_METRICS) >= _MAX_METRICS:
        return False
    
    _ACTIVE_METRICS.append(metric_name)
    return True

def record_metric(
    name: str,
    value: float,
    unit: str = "None",
    **dimensions
) -> bool:
    """Record a metric value."""
    if not _ensure_metric_limit(name):
        return False
    
    metric = MetricData(
        name=name,
        value=value,
        unit=unit,
        timestamp=time.time(),
        dimensions=dimensions
    )
    
    _METRICS[name].append(metric)
    
    if len(_METRICS[name]) > _METRIC_BUFFER_SIZE:
        _METRICS[name] = _METRICS[name][-_METRIC_BUFFER_SIZE:]
    
    _METRIC_STATS[name].update(value)
    
    return True

def get_metric(name: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
    """Get metric values."""
    metrics = _METRICS.get(name, [])
    
    if limit:
        metrics = metrics[-limit:]
    
    return [
        {
            "name": m.name,
            "value": m.value,
            "unit": m.unit,
            "timestamp": m.timestamp,
            "dimensions": m.dimensions
        }
        for m in metrics
    ]

def get_metric_stats(name: str) -> Dict[str, Any]:
    """Get metric statistics."""
    if name not in _METRIC_STATS:
        return {
            "name": name,
            "count": 0,
            "exists": False
        }
    
    stats = _METRIC_STATS[name]
    return {
        "name": name,
        "count": stats.count,
        "sum": stats.sum,
        "min": stats.min if stats.min != float('inf') else None,
        "max": stats.max if stats.max != float('-inf') else None,
        "avg": stats.avg,
        "exists": True
    }

def get_all_metrics_stats() -> Dict[str, Any]:
    """Get statistics for all metrics."""
    return {
        name: get_metric_stats(name)
        for name in _ACTIVE_METRICS
    }

def track_execution_time(operation_name: str, duration: float) -> bool:
    """Track execution time."""
    return record_metric(
        f"execution_time_{operation_name}",
        duration * 1000,
        "Milliseconds"
    )

def track_memory_usage(memory_mb: float) -> bool:
    """Track memory usage."""
    return record_metric(
        "memory_usage",
        memory_mb,
        "Megabytes"
    )

def track_error(error_type: str) -> bool:
    """Track error occurrence."""
    return record_metric(
        f"error_{error_type}",
        1,
        "Count"
    )

def track_invocation() -> bool:
    """Track Lambda invocation."""
    return record_metric(
        "invocation_count",
        1,
        "Count"
    )

def clear_metric(name: str) -> int:
    """Clear metric data."""
    if name in _METRICS:
        count = len(_METRICS[name])
        del _METRICS[name]
        if name in _METRIC_STATS:
            del _METRIC_STATS[name]
        if name in _ACTIVE_METRICS:
            _ACTIVE_METRICS.remove(name)
        return count
    return 0

def clear_all_metrics() -> int:
    """Clear all metrics."""
    count = sum(len(metrics) for metrics in _METRICS.values())
    _METRICS.clear()
    _METRIC_STATS.clear()
    _ACTIVE_METRICS.clear()
    return count

def export_metrics(format: str = "json") -> str:
    """Export metrics in specified format."""
    import json
    
    data = {}
    for name in _ACTIVE_METRICS:
        data[name] = {
            "values": get_metric(name),
            "stats": get_metric_stats(name)
        }
    
    if format.lower() == "json":
        return json.dumps(data, indent=2)
    else:
        raise ValueError(f"Unsupported format: {format}")

def get_metrics_summary() -> Dict[str, Any]:
    """Get summary of all metrics."""
    return {
        "active_metrics": len(_ACTIVE_METRICS),
        "max_metrics": _MAX_METRICS,
        "metrics_available": _MAX_METRICS - len(_ACTIVE_METRICS),
        "total_data_points": sum(len(metrics) for metrics in _METRICS.values()),
        "metric_names": _ACTIVE_METRICS.copy()
    }

def rotate_metric(old_name: str, new_name: str) -> bool:
    """Rotate a metric (remove old, add new)."""
    if old_name in _ACTIVE_METRICS:
        clear_metric(old_name)
    return True

def get_top_metrics(limit: int = 5) -> List[Dict[str, Any]]:
    """Get top metrics by value."""
    all_stats = []
    for name in _ACTIVE_METRICS:
        stats = get_metric_stats(name)
        if stats["exists"]:
            all_stats.append(stats)
    
    all_stats.sort(key=lambda x: x["avg"], reverse=True)
    return all_stats[:limit]

def record_batch_metrics(metrics: List[Dict[str, Any]]) -> int:
    """Record multiple metrics at once."""
    count = 0
    for metric in metrics:
        if record_metric(
            metric["name"],
            metric["value"],
            metric.get("unit", "None"),
            **metric.get("dimensions", {})
        ):
            count += 1
    return count

def get_metric_health() -> Dict[str, Any]:
    """Get metrics health status."""
    return {
        "healthy": len(_ACTIVE_METRICS) < _MAX_METRICS,
        "at_limit": len(_ACTIVE_METRICS) >= _MAX_METRICS,
        "usage_percentage": (len(_ACTIVE_METRICS) / _MAX_METRICS) * 100,
        "available_slots": _MAX_METRICS - len(_ACTIVE_METRICS)
    }
