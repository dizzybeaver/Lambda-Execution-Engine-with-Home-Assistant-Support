"""
debug_core.py - LUGS Diagnostics & Monitoring System
Version: 2025.10.01.05
Daily Revision: LUGS Diagnostics Implementation

ARCHITECTURE: DEBUGGING AND MONITORING LAYER
- Comprehensive LUGS performance monitoring
- Module lifecycle diagnostics
- Memory usage tracking and analysis
- Performance bottleneck identification
- Real-time system health monitoring

OPTIMIZATION: Phase 6 + LUGS Complete
- ADDED: LUGS module lifecycle monitoring
- ADDED: Memory savings calculation and tracking
- ADDED: Performance impact analysis
- ADDED: System health diagnostics
- 100% architecture compliance + LUGS diagnostics

Revolutionary Gateway Optimization: SUGA + LIGS + ZAFP + LUGS

Copyright 2024 Anthropic PBC
Licensed under the Apache License, Version 2.0
"""

import sys
import time
import psutil
import threading
import traceback
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta

from gateway import (
    log_info, log_error, log_debug,
    record_metric,
    generate_correlation_id,
    get_lugs_stats, get_module_lifecycle_info,
    create_success_response, create_error_response
)


class DiagnosticLevel(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class HealthStatus(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    CRITICAL = "critical"


@dataclass
class MemorySnapshot:
    """Memory usage snapshot for analysis."""
    timestamp: float
    total_memory_mb: float
    available_memory_mb: float
    process_memory_mb: float
    loaded_modules_count: int
    protected_modules_count: int
    cache_size_mb: float
    estimated_lugs_savings_mb: float = 0.0


@dataclass
class PerformanceMetric:
    """Performance metric tracking."""
    metric_name: str
    value: float
    timestamp: float
    dimensions: Dict[str, str] = field(default_factory=dict)
    trend: Optional[str] = None  # "improving", "degrading", "stable"


@dataclass
class SystemHealth:
    """Overall system health assessment."""
    status: HealthStatus
    score: float  # 0-100
    issues: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    timestamp: float = field(default_factory=time.time)


class LUGSDiagnosticsManager:
    """Comprehensive LUGS diagnostics and monitoring system."""
    
    def __init__(self):
        self._lock = threading.RLock()
        self._memory_snapshots: List[MemorySnapshot] = []
        self._performance_metrics: Dict[str, List[PerformanceMetric]] = {}
        self._diagnostic_events: List[Dict[str, Any]] = []
        
        # Configuration
        self._max_snapshots = 100
        self._max_metrics_per_type = 200
        self._max_events = 500
        self._snapshot_interval = 60  # 1 minute
        self._last_snapshot_time = 0
        
        # Health thresholds
        self._health_thresholds = {
            "memory_usage_percent": 80,
            "cache_hit_rate_percent": 70,
            "module_churn_rate": 0.1,  # 10% modules loading/unloading per minute
            "error_rate_percent": 5,
            "avg_response_time_ms": 200
        }
        
        # Performance tracking
        self._baseline_metrics: Dict[str, float] = {}
        self._performance_trends: Dict[str, str] = {}
        
        self._stats = {
            'diagnostics_run': 0,
            'health_checks': 0,
            'performance_analyses': 0,
            'memory_optimizations_detected': 0,
            'bottlenecks_identified': 0,
            'recommendations_generated': 0
        }
    
    def capture_memory_snapshot(self) -> MemorySnapshot:
        """Capture current memory usage snapshot."""
        try:
            # Get system memory info
            memory_info = psutil.virtual_memory()
            process = psutil.Process()
            process_memory = process.memory_info()
            
            # Get LUGS statistics
            lugs_stats = get_lugs_stats()
            module_info = get_module_lifecycle_info()
            
            # Estimate cache size (rough approximation)
            cache_size_mb = 0.0
            try:
                from cache_core import get_stats as get_cache_stats
                cache_stats = get_cache_stats()
                # Rough estimate: 1KB per cache entry
                cache_size_mb = cache_stats.get('total_entries', 0) * 0.001
            except:
                pass
            
            snapshot = MemorySnapshot(
                timestamp=time.time(),
                total_memory_mb=memory_info.total / 1024 / 1024,
                available_memory_mb=memory_info.available / 1024 / 1024,
                process_memory_mb=process_memory.rss / 1024 / 1024,
                loaded_modules_count=lugs_stats.get('active_modules', 0),
                protected_modules_count=lugs_stats.get('hot_path_modules', 0),
                cache_size_mb=cache_size_mb,
                estimated_lugs_savings_mb=lugs_stats.get('memory_saved_bytes', 0) / 1024 / 1024
            )
            
            with self._lock:
                self._memory_snapshots.append(snapshot)
                
                # Keep only recent snapshots
                if len(self._memory_snapshots) > self._max_snapshots:
                    self._memory_snapshots = self._memory_snapshots[-self._max_snapshots:]
            
            return snapshot
            
        except Exception as e:
            log_error(f"Failed to capture memory snapshot: {str(e)}")
            return MemorySnapshot(
                timestamp=time.time(),
                total_memory_mb=0,
                available_memory_mb=0,
                process_memory_mb=0,
                loaded_modules_count=0,
                protected_modules_count=0,
                cache_size_mb=0
            )
    
    def analyze_performance_trends(self) -> Dict[str, Any]:
        """Analyze performance trends over time."""
        with self._lock:
            analysis = {
                "trends": {},
                "improvements": [],
                "degradations": [],
                "stable_metrics": [],
                "recommendations": []
            }
            
            for metric_name, metrics_list in self._performance_metrics.items():
                if len(metrics_list) < 5:  # Need at least 5 data points
                    continue
                
                # Get recent metrics (last 20 data points)
                recent_metrics = metrics_list[-20:]
                values = [m.value for m in recent_metrics]
                
                # Calculate trend
                if len(values) >= 10:
                    # Simple linear regression for trend
                    x_values = list(range(len(values)))
                    n = len(values)
                    sum_x = sum(x_values)
                    sum_y = sum(values)
                    sum_xy = sum(x * y for x, y in zip(x_values, values))
                    sum_x2 = sum(x * x for x in x_values)
                    
                    slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
                    
                    # Determine trend
                    if abs(slope) < 0.01:  # Threshold for stability
                        trend = "stable"
                        analysis["stable_metrics"].append(metric_name)
                    elif slope > 0:
                        trend = "improving" if "error" not in metric_name.lower() else "degrading"
                        if trend == "improving":
                            analysis["improvements"].append({
                                "metric": metric_name,
                                "slope": slope,
                                "current_value": values[-1]
                            })
                        else:
                            analysis["degradations"].append({
                                "metric": metric_name,
                                "slope": slope,
                                "current_value": values[-1]
                            })
                    else:
                        trend = "degrading" if "error" not in metric_name.lower() else "improving"
                        if trend == "degrading":
                            analysis["degradations"].append({
                                "metric": metric_name,
                                "slope": slope,
                                "current_value": values[-1]
                            })
                        else:
                            analysis["improvements"].append({
                                "metric": metric_name,
                                "slope": slope,
                                "current_value": values[-1]
                            })
                    
                    analysis["trends"][metric_name] = {
                        "trend": trend,
                        "slope": slope,
                        "current_value": values[-1],
                        "avg_value": sum(values) / len(values),
                        "data_points": len(values)
                    }
            
            # Generate recommendations based on trends
            analysis["recommendations"] = self._generate_performance_recommendations(analysis)
            
            self._stats['performance_analyses'] += 1
            return analysis
    
    def assess_system_health(self) -> SystemHealth:
        """Assess overall system health based on multiple factors."""
        try:
            health = SystemHealth(status=HealthStatus.HEALTHY, score=100.0)
            
            # Get latest metrics
            latest_snapshot = self.capture_memory_snapshot()
            lugs_stats = get_lugs_stats()
            
            # Memory health check
            memory_usage_percent = (latest_snapshot.process_memory_mb / latest_snapshot.total_memory_mb) * 100
            if memory_usage_percent > self._health_thresholds["memory_usage_percent"]:
                health.issues.append(f"High memory usage: {memory_usage_percent:.1f}%")
                health.score -= 20
                if memory_usage_percent > 90:
                    health.status = HealthStatus.CRITICAL
                elif memory_usage_percent > 85:
                    health.status = HealthStatus.UNHEALTHY
                else:
                    health.status = HealthStatus.DEGRADED
            
            # LUGS effectiveness check
            modules_loaded = lugs_stats.get('modules_loaded', 0)
            modules_unloaded = lugs_stats.get('modules_unloaded', 0)
            
            if modules_loaded > 0:
                unload_rate = modules_unloaded / modules_loaded
                if unload_rate < 0.1:  # Less than 10% unload rate
                    health.issues.append(f"Low LUGS unload rate: {unload_rate:.1%}")
                    health.score -= 10
                    health.recommendations.append("Consider lowering module unload thresholds")
            
            # Cache performance check
            try:
                from cache_core import get_stats as get_cache_stats
                cache_stats = get_cache_stats()
                cache_hit_rate = cache_stats.get('hit_rate_percent', 0)
                
                if cache_hit_rate < self._health_thresholds["cache_hit_rate_percent"]:
                    health.issues.append(f"Low cache hit rate: {cache_hit_rate:.1f}%")
                    health.score -= 15
                    health.recommendations.append("Review cache TTL settings and key strategies")
            except:
                pass
            
            # Hot path protection check
            hot_path_modules = lugs_stats.get('hot_path_modules', 0)
            total_modules = lugs_stats.get('total_tracked_modules', 1)
            hot_path_ratio = hot_path_modules / total_modules
            
            if hot_path_ratio < 0.1:  # Less than 10% of modules are protected
                health.recommendations.append("Consider more aggressive hot path detection")
            elif hot_path_ratio > 0.5:  # More than 50% are protected
                health.recommendations.append("Review hot path thresholds - too many modules protected")
            
            # Performance trend check
            performance_analysis = self.analyze_performance_trends()
            if len(performance_analysis["degradations"]) > len(performance_analysis["improvements"]):
                health.issues.append("More performance degradations than improvements detected")
                health.score -= 10
                health.status = HealthStatus.DEGRADED if health.status == HealthStatus.HEALTHY else health.status
            
            # Determine final health status based on score
            if health.score >= 90:
                health.status = HealthStatus.HEALTHY
            elif health.score >= 70:
                health.status = HealthStatus.DEGRADED
            elif health.score >= 50:
                health.status = HealthStatus.UNHEALTHY
            else:
                health.status = HealthStatus.CRITICAL
            
            # Add general recommendations if healthy
            if health.status == HealthStatus.HEALTHY:
                health.recommendations.extend([
                    "System operating optimally",
                    "Continue monitoring LUGS performance",
                    "Consider periodic optimization reviews"
                ])
            
            self._stats['health_checks'] += 1
            return health
            
        except Exception as e:
            log_error(f"Health assessment failed: {str(e)}")
            return SystemHealth(
                status=HealthStatus.CRITICAL,
                score=0.0,
                issues=[f"Health assessment failed: {str(e)}"],
                recommendations=["Check system logs for errors"]
            )
    
    def identify_performance_bottlenecks(self) -> List[Dict[str, Any]]:
        """Identify performance bottlenecks in the system."""
        bottlenecks = []
        
        try:
            # Memory bottlenecks
            if len(self._memory_snapshots) >= 2:
                latest = self._memory_snapshots[-1]
                previous = self._memory_snapshots[-2]
                
                memory_growth = latest.process_memory_mb - previous.process_memory_mb
                if memory_growth > 10:  # More than 10MB growth
                    bottlenecks.append({
                        "type": "memory_growth",
                        "severity": "high" if memory_growth > 50 else "medium",
                        "description": f"Memory growth of {memory_growth:.1f}MB detected",
                        "recommendation": "Check for memory leaks or excessive module loading",
                        "metrics": {
                            "growth_mb": memory_growth,
                            "current_usage_mb": latest.process_memory_mb
                        }
                    })
            
            # Module churn bottlenecks
            lugs_stats = get_lugs_stats()
            modules_loaded = lugs_stats.get('modules_loaded', 0)
            modules_unloaded = lugs_stats.get('modules_unloaded', 0)
            
            if modules_loaded > 100 and modules_unloaded < modules_loaded * 0.5:
                bottlenecks.append({
                    "type": "module_churn",
                    "severity": "medium",
                    "description": f"High module loading with low unloading: {modules_loaded} loaded, {modules_unloaded} unloaded",
                    "recommendation": "Review module unload thresholds and cache dependencies",
                    "metrics": {
                        "modules_loaded": modules_loaded,
                        "modules_unloaded": modules_unloaded,
                        "unload_ratio": modules_unloaded / modules_loaded if modules_loaded > 0 else 0
                    }
                })
            
            # Cache bottlenecks
            try:
                from cache_core import get_stats as get_cache_stats
                cache_stats = get_cache_stats()
                
                if cache_stats.get('misses', 0) > cache_stats.get('hits', 1) * 2:  # More than 2:1 miss ratio
                    bottlenecks.append({
                        "type": "cache_inefficiency",
                        "severity": "high",
                        "description": "Poor cache hit ratio detected",
                        "recommendation": "Review cache key strategies and TTL settings",
                        "metrics": cache_stats
                    })
            except:
                pass
            
            # Hot path bottlenecks
            try:
                from fast_path import get_fast_path_stats
                fast_path_stats = get_fast_path_stats()
                
                if fast_path_stats.get('fast_path_executions', 0) < fast_path_stats.get('total_operation_calls', 1) * 0.1:
                    bottlenecks.append({
                        "type": "underutilized_fast_path",
                        "severity": "low",
                        "description": "Fast path underutilized",
                        "recommendation": "Review hot path thresholds for more aggressive optimization",
                        "metrics": fast_path_stats
                    })
            except:
                pass
            
            if bottlenecks:
                self._stats['bottlenecks_identified'] += len(bottlenecks)
            
            return bottlenecks
            
        except Exception as e:
            log_error(f"Bottleneck identification failed: {str(e)}")
            return [{
                "type": "analysis_error",
                "severity": "critical",
                "description": f"Failed to identify bottlenecks: {str(e)}",
                "recommendation": "Check system logs and restart diagnostics"
            }]
    
    def generate_optimization_report(self) -> Dict[str, Any]:
        """Generate comprehensive optimization report."""
        correlation_id = generate_correlation_id("opt_report")
        
        try:
            # Capture current state
            memory_snapshot = self.capture_memory_snapshot()
            system_health = self.assess_system_health()
            performance_trends = self.analyze_performance_trends()
            bottlenecks = self.identify_performance_bottlenecks()
            
            # Calculate LUGS impact
            lugs_stats = get_lugs_stats()
            lugs_impact = self._calculate_lugs_impact(lugs_stats)
            
            # Generate recommendations
            recommendations = self._generate_comprehensive_recommendations(
                system_health, performance_trends, bottlenecks, lugs_impact
            )
            
            report = {
                "report_id": correlation_id,
                "timestamp": time.time(),
                "executive_summary": {
                    "system_health": {
                        "status": system_health.status,
                        "score": system_health.score,
                        "issues_count": len(system_health.issues)
                    },
                    "lugs_performance": {
                        "memory_saved_mb": lugs_impact.get("memory_saved_mb", 0),
                        "modules_unloaded": lugs_stats.get('modules_unloaded', 0),
                        "cache_hit_effectiveness": lugs_impact.get("cache_effectiveness_percent", 0)
                    },
                    "optimization_opportunities": len(recommendations)
                },
                "detailed_analysis": {
                    "memory_usage": {
                        "current_mb": memory_snapshot.process_memory_mb,
                        "total_available_mb": memory_snapshot.available_memory_mb,
                        "usage_percent": (memory_snapshot.process_memory_mb / memory_snapshot.total_memory_mb) * 100,
                        "lugs_savings_mb": memory_snapshot.estimated_lugs_savings_mb
                    },
                    "performance_trends": performance_trends,
                    "bottlenecks": bottlenecks,
                    "lugs_statistics": lugs_stats
                },
                "recommendations": recommendations,
                "next_steps": [
                    "Review and implement high-priority recommendations",
                    "Monitor system performance for 24-48 hours",
                    "Re-run optimization analysis to measure improvements",
                    "Consider additional LUGS tuning if needed"
                ]
            }
            
            self._stats['diagnostics_run'] += 1
            self._stats['recommendations_generated'] += len(recommendations)
            
            log_info(f"Optimization report generated", extra={
                "correlation_id": correlation_id,
                "health_score": system_health.score,
                "recommendations_count": len(recommendations),
                "lugs_memory_saved_mb": lugs_impact.get("memory_saved_mb", 0)
            })
            
            return report
            
        except Exception as e:
            log_error(f"Optimization report generation failed: {str(e)}", extra={
                "correlation_id": correlation_id
            })
            
            return {
                "report_id": correlation_id,
                "timestamp": time.time(),
                "error": f"Report generation failed: {str(e)}",
                "recommendations": ["Check system logs and retry report generation"]
            }
    
    def _calculate_lugs_impact(self, lugs_stats: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate LUGS performance impact."""
        impact = {
            "memory_saved_mb": lugs_stats.get('memory_saved_bytes', 0) / 1024 / 1024,
            "modules_loaded": lugs_stats.get('modules_loaded', 0),
            "modules_unloaded": lugs_stats.get('modules_unloaded', 0),
            "cache_hits_avoided_load": lugs_stats.get('cache_hits_avoided_load', 0),
            "hot_path_protections": lugs_stats.get('hot_path_protections', 0)
        }
        
        # Calculate effectiveness percentages
        if impact["modules_loaded"] > 0:
            impact["unload_effectiveness_percent"] = (impact["modules_unloaded"] / impact["modules_loaded"]) * 100
        else:
            impact["unload_effectiveness_percent"] = 0
        
        # Estimate cache effectiveness
        total_operations = impact["modules_loaded"] + impact["cache_hits_avoided_load"]
        if total_operations > 0:
            impact["cache_effectiveness_percent"] = (impact["cache_hits_avoided_load"] / total_operations) * 100
        else:
            impact["cache_effectiveness_percent"] = 0
        
        return impact
    
    def _generate_performance_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate performance recommendations based on trend analysis."""
        recommendations = []
        
        # Based on degradations
        for degradation in analysis.get("degradations", []):
            metric_name = degradation["metric"]
            if "memory" in metric_name.lower():
                recommendations.append(f"Address memory usage increase in {metric_name}")
            elif "error" in metric_name.lower():
                recommendations.append(f"Investigate error rate increase in {metric_name}")
            elif "duration" in metric_name.lower() or "time" in metric_name.lower():
                recommendations.append(f"Optimize performance for {metric_name}")
        
        # Based on stable but suboptimal metrics
        for metric_name, trend_data in analysis.get("trends", {}).items():
            if trend_data["trend"] == "stable":
                current_value = trend_data["current_value"]
                if "hit_rate" in metric_name.lower() and current_value < 80:
                    recommendations.append(f"Improve cache hit rate for {metric_name}")
                elif "duration" in metric_name.lower() and current_value > 100:
                    recommendations.append(f"Consider fast path optimization for {metric_name}")
        
        return recommendations
    
    def _generate_comprehensive_recommendations(
        self,
        system_health: SystemHealth,
        performance_trends: Dict[str, Any],
        bottlenecks: List[Dict[str, Any]],
        lugs_impact: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate comprehensive optimization recommendations."""
        recommendations = []
        
        # Health-based recommendations
        for issue in system_health.issues:
            if "memory" in issue.lower():
                recommendations.append({
                    "priority": "high",
                    "category": "memory",
                    "title": "Address Memory Usage",
                    "description": issue,
                    "action": "Review memory allocation and enable more aggressive LUGS unloading",
                    "estimated_impact": "10-30% memory reduction"
                })
            elif "cache" in issue.lower():
                recommendations.append({
                    "priority": "medium",
                    "category": "performance",
                    "title": "Improve Cache Performance",
                    "description": issue,
                    "action": "Optimize cache key strategies and TTL settings",
                    "estimated_impact": "15-25% performance improvement"
                })
        
        # Bottleneck-based recommendations
        for bottleneck in bottlenecks:
            priority = "high" if bottleneck["severity"] == "high" else "medium"
            recommendations.append({
                "priority": priority,
                "category": bottleneck["type"],
                "title": f"Resolve {bottleneck['type'].title()} Bottleneck",
                "description": bottleneck["description"],
                "action": bottleneck["recommendation"],
                "estimated_impact": "5-15% performance improvement"
            })
        
        # LUGS-specific recommendations
        if lugs_impact["unload_effectiveness_percent"] < 30:
            recommendations.append({
                "priority": "medium",
                "category": "lugs",
                "title": "Improve LUGS Unload Rate",
                "description": f"Only {lugs_impact['unload_effectiveness_percent']:.1f}% of loaded modules are being unloaded",
                "action": "Lower unload delay thresholds and review cache dependencies",
                "estimated_impact": "20-40% memory reduction"
            })
        
        if lugs_impact["cache_effectiveness_percent"] < 50:
            recommendations.append({
                "priority": "medium",
                "category": "cache",
                "title": "Enhance Cache-LUGS Integration",
                "description": f"Cache avoiding only {lugs_impact['cache_effectiveness_percent']:.1f}% of module loads",
                "action": "Extend cache TTLs for stable data and improve cache warming",
                "estimated_impact": "30-50% reduction in module loading"
            })
        
        # Sort by priority
        priority_order = {"high": 3, "medium": 2, "low": 1}
        recommendations.sort(key=lambda x: priority_order.get(x["priority"], 0), reverse=True)
        
        return recommendations
    
    def get_diagnostic_stats(self) -> Dict[str, Any]:
        """Get diagnostic system statistics."""
        with self._lock:
            return {
                **self._stats,
                'memory_snapshots_count': len(self._memory_snapshots),
                'performance_metrics_types': len(self._performance_metrics),
                'diagnostic_events_count': len(self._diagnostic_events),
                'last_snapshot_time': self._last_snapshot_time,
                'health_thresholds': self._health_thresholds
            }


# Global diagnostics manager instance
_diagnostics_manager = LUGSDiagnosticsManager()

# === PUBLIC INTERFACE ===

def capture_memory_snapshot() -> Dict[str, Any]:
    """Capture memory usage snapshot."""
    snapshot = _diagnostics_manager.capture_memory_snapshot()
    return {
        "timestamp": snapshot.timestamp,
        "process_memory_mb": snapshot.process_memory_mb,
        "available_memory_mb": snapshot.available_memory_mb,
        "loaded_modules_count": snapshot.loaded_modules_count,
        "cache_size_mb": snapshot.cache_size_mb,
        "lugs_savings_mb": snapshot.estimated_lugs_savings_mb
    }

def assess_system_health() -> Dict[str, Any]:
    """Assess system health."""
    health = _diagnostics_manager.assess_system_health()
    return {
        "status": health.status,
        "score": health.score,
        "issues": health.issues,
        "recommendations": health.recommendations,
        "timestamp": health.timestamp
    }

def analyze_performance_trends() -> Dict[str, Any]:
    """Analyze performance trends."""
    return _diagnostics_manager.analyze_performance_trends()

def identify_performance_bottlenecks() -> List[Dict[str, Any]]:
    """Identify performance bottlenecks."""
    return _diagnostics_manager.identify_performance_bottlenecks()

def generate_optimization_report() -> Dict[str, Any]:
    """Generate comprehensive optimization report."""
    return _diagnostics_manager.generate_optimization_report()

def get_diagnostic_stats() -> Dict[str, Any]:
    """Get diagnostic statistics."""
    return _diagnostics_manager.get_diagnostic_stats()

# === LUGS INTEGRATION HELPERS ===

def track_performance_metric(metric_name: str, value: float, dimensions: Optional[Dict[str, str]] = None) -> None:
    """Track performance metric for trend analysis."""
    try:
        with _diagnostics_manager._lock:
            if metric_name not in _diagnostics_manager._performance_metrics:
                _diagnostics_manager._performance_metrics[metric_name] = []
            
            metric = PerformanceMetric(
                metric_name=metric_name,
                value=value,
                timestamp=time.time(),
                dimensions=dimensions or {}
            )
            
            _diagnostics_manager._performance_metrics[metric_name].append(metric)
            
            # Keep only recent metrics
            if len(_diagnostics_manager._performance_metrics[metric_name]) > _diagnostics_manager._max_metrics_per_type:
                _diagnostics_manager._performance_metrics[metric_name] = \
                    _diagnostics_manager._performance_metrics[metric_name][-_diagnostics_manager._max_metrics_per_type:]
    
    except Exception as e:
        log_error(f"Failed to track performance metric {metric_name}: {str(e)}")

def log_diagnostic_event(event_type: str, description: str, level: DiagnosticLevel = DiagnosticLevel.INFO, data: Optional[Dict[str, Any]] = None) -> None:
    """Log diagnostic event."""
    try:
        event = {
            "timestamp": time.time(),
            "event_type": event_type,
            "description": description,
            "level": level,
            "data": data or {},
            "correlation_id": generate_correlation_id("diag")
        }
        
        with _diagnostics_manager._lock:
            _diagnostics_manager._diagnostic_events.append(event)
            
            # Keep only recent events
            if len(_diagnostics_manager._diagnostic_events) > _diagnostics_manager._max_events:
                _diagnostics_manager._diagnostic_events = _diagnostics_manager._diagnostic_events[-_diagnostics_manager._max_events:]
        
        # Log to system logger based on level
        if level == DiagnosticLevel.ERROR or level == DiagnosticLevel.CRITICAL:
            log_error(f"Diagnostic {event_type}: {description}", extra={"diagnostic_data": data})
        elif level == DiagnosticLevel.WARNING:
            log_debug(f"Diagnostic {event_type}: {description}", extra={"diagnostic_data": data})
        else:
            log_debug(f"Diagnostic {event_type}: {description}", extra={"diagnostic_data": data})
    
    except Exception as e:
        log_error(f"Failed to log diagnostic event: {str(e)}")

def run_health_check() -> Dict[str, Any]:
    """Run immediate health check and return results."""
    try:
        health = assess_system_health()
        bottlenecks = identify_performance_bottlenecks()
        memory_snapshot = capture_memory_snapshot()
        
        return {
            "health_check_id": generate_correlation_id("health"),
            "timestamp": time.time(),
            "system_health": health,
            "bottlenecks": bottlenecks,
            "memory_snapshot": memory_snapshot,
            "summary": {
                "status": health["status"],
                "issues_count": len(health["issues"]),
                "bottlenecks_count": len(bottlenecks),
                "memory_usage_mb": memory_snapshot["process_memory_mb"]
            }
        }
    
    except Exception as e:
        log_error(f"Health check failed: {str(e)}")
        return {
            "health_check_id": generate_correlation_id("health_err"),
            "timestamp": time.time(),
            "error": str(e),
            "status": "FAILED"
        }

def configure_diagnostics(
    snapshot_interval: int = 60,
    max_snapshots: int = 100,
    health_thresholds: Optional[Dict[str, float]] = None
) -> bool:
    """Configure diagnostic system settings."""
    try:
        _diagnostics_manager._snapshot_interval = snapshot_interval
        _diagnostics_manager._max_snapshots = max_snapshots
        
        if health_thresholds:
            _diagnostics_manager._health_thresholds.update(health_thresholds)
        
        log_info("Diagnostics configuration updated", extra={
            "snapshot_interval": snapshot_interval,
            "max_snapshots": max_snapshots,
            "health_thresholds": _diagnostics_manager._health_thresholds
        })
        
        return True
    
    except Exception as e:
        log_error(f"Failed to configure diagnostics: {str(e)}")
        return False
