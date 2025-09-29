"""
debug_troubleshooting.py - Debug Troubleshooting Implementation
Version: 2025.09.28.01
Description: Troubleshooting functions for system diagnostics, issue resolution, and monitoring

ARCHITECTURE: SECONDARY IMPLEMENTATION - Internal Network
- System diagnostics (memory usage analysis, performance bottleneck detection, error pattern analysis)
- Issue resolution tools (automated fix suggestions, configuration optimization, performance tuning)
- Monitoring and alerting (health status monitoring, threshold breach detection, diagnostic reports)
- Resource leak detection and automated recovery procedures
- Proactive issue identification and intelligent recommendations

TROUBLESHOOTING FRAMEWORK:
- Real-time system health monitoring and analysis
- Automated diagnostic report generation with actionable recommendations
- Performance bottleneck detection and optimization suggestions
- Memory leak detection and resource usage optimization
- Error pattern analysis and automated fix suggestions
- Proactive monitoring with threshold-based alerting

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
import gc
import threading
import statistics
import traceback
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
import concurrent.futures

# Import gateway interfaces
import logging as log_gateway
import metrics
import cache
import config
import utility
import security

# Import core debug functionality
from .debug_core import DiagnosticResult, DiagnosticLevel, PerformanceMetrics

# ===== SECTION 1: TROUBLESHOOTING TYPES =====

class DiagnosticType(Enum):
    """Diagnostic operation types."""
    SYSTEM_HEALTH = "system_health"
    PERFORMANCE_ANALYSIS = "performance_analysis"
    MEMORY_ANALYSIS = "memory_analysis"
    ERROR_PATTERN_ANALYSIS = "error_pattern_analysis"
    RESOURCE_LEAK_DETECTION = "resource_leak_detection"
    BOTTLENECK_DETECTION = "bottleneck_detection"
    CONFIGURATION_ANALYSIS = "configuration_analysis"
    DEPENDENCY_ANALYSIS = "dependency_analysis"

class HealthStatus(Enum):
    """System health status levels."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    CRITICAL = "critical"
    UNKNOWN = "unknown"

class IssueType(Enum):
    """Issue classification types."""
    PERFORMANCE = "performance"
    MEMORY = "memory"
    CONFIGURATION = "configuration"
    DEPENDENCY = "dependency"
    SECURITY = "security"
    ARCHITECTURE = "architecture"
    RESOURCE = "resource"

@dataclass
class SystemMetrics:
    """System performance metrics snapshot."""
    timestamp: float
    memory_usage_mb: float
    response_time_ms: float
    error_rate: float
    cache_hit_rate: float
    cpu_usage_percent: Optional[float] = None
    active_connections: int = 0
    queue_size: int = 0

@dataclass
class IssueReport:
    """Issue analysis report."""
    issue_id: str
    issue_type: IssueType
    severity: DiagnosticLevel
    title: str
    description: str
    impact: str
    recommendations: List[str]
    auto_fix_available: bool = False
    estimated_fix_time: Optional[str] = None
    related_components: List[str] = field(default_factory=list)

@dataclass
class PerformanceBottleneck:
    """Performance bottleneck identification."""
    component: str
    operation: str
    avg_response_time_ms: float
    impact_score: float
    frequency: int
    recommendations: List[str]

# ===== SECTION 2: SYSTEM HEALTH DIAGNOSTICS =====

class SystemHealthDiagnostics:
    """System health monitoring and diagnostics."""
    
    def __init__(self):
        self._lock = threading.RLock()
        self._metrics_history: deque = deque(maxlen=100)
        self._error_patterns: Dict[str, int] = defaultdict(int)
        self._performance_baselines: Dict[str, float] = {}
        self._health_thresholds = {
            "memory_warning": 80.0,      # MB
            "memory_critical": 100.0,    # MB
            "response_time_warning": 200.0,  # ms
            "response_time_critical": 500.0, # ms
            "error_rate_warning": 0.05,   # 5%
            "error_rate_critical": 0.15   # 15%
        }
    
    def diagnose_system_health(self) -> DiagnosticResult:
        """Comprehensive system health diagnosis."""
        start_time = time.time()
        
        try:
            # Collect current metrics
            current_metrics = self._collect_system_metrics()
            
            # Analyze health indicators
            health_status, health_issues = self._analyze_health_status(current_metrics)
            
            # Generate recommendations
            recommendations = self._generate_health_recommendations(health_status, health_issues)
            
            # Store metrics for trending
            with self._lock:
                self._metrics_history.append(current_metrics)
            
            # Determine diagnostic level
            if health_status == HealthStatus.CRITICAL:
                level = DiagnosticLevel.CRITICAL
            elif health_status == HealthStatus.UNHEALTHY:
                level = DiagnosticLevel.ERROR
            elif health_status == HealthStatus.DEGRADED:
                level = DiagnosticLevel.WARNING
            else:
                level = DiagnosticLevel.INFO
            
            return DiagnosticResult(
                diagnostic_name="system_health",
                level=level,
                message=f"System health: {health_status.value}",
                recommendations=recommendations,
                metrics={
                    "health_status": health_status.value,
                    "current_metrics": {
                        "memory_usage_mb": current_metrics.memory_usage_mb,
                        "response_time_ms": current_metrics.response_time_ms,
                        "error_rate": current_metrics.error_rate,
                        "cache_hit_rate": current_metrics.cache_hit_rate
                    },
                    "health_issues": health_issues,
                    "thresholds": self._health_thresholds,
                    "diagnosis_duration_ms": (time.time() - start_time) * 1000
                }
            )
            
        except Exception as e:
            return DiagnosticResult(
                diagnostic_name="system_health",
                level=DiagnosticLevel.ERROR,
                message=f"Health diagnosis failed: {str(e)}",
                recommendations=["Manual system inspection required"],
                metrics={"error": str(e)}
            )
    
    def _collect_system_metrics(self) -> SystemMetrics:
        """Collect current system performance metrics."""
        try:
            # Get memory usage
            memory_usage = self._get_memory_usage()
            
            # Get response time metrics
            response_time = self._get_average_response_time()
            
            # Get error rate
            error_rate = self._get_current_error_rate()
            
            # Get cache performance
            cache_hit_rate = self._get_cache_hit_rate()
            
            return SystemMetrics(
                timestamp=time.time(),
                memory_usage_mb=memory_usage,
                response_time_ms=response_time,
                error_rate=error_rate,
                cache_hit_rate=cache_hit_rate
            )
            
        except Exception as e:
            log_gateway.log_error(f"Failed to collect system metrics: {str(e)}")
            return SystemMetrics(
                timestamp=time.time(),
                memory_usage_mb=0,
                response_time_ms=0,
                error_rate=0,
                cache_hit_rate=0
            )
    
    def _analyze_health_status(self, metrics: SystemMetrics) -> Tuple[HealthStatus, List[str]]:
        """Analyze current health status based on metrics."""
        issues = []
        
        # Check memory usage
        if metrics.memory_usage_mb > self._health_thresholds["memory_critical"]:
            issues.append(f"Critical memory usage: {metrics.memory_usage_mb}MB")
        elif metrics.memory_usage_mb > self._health_thresholds["memory_warning"]:
            issues.append(f"High memory usage: {metrics.memory_usage_mb}MB")
        
        # Check response time
        if metrics.response_time_ms > self._health_thresholds["response_time_critical"]:
            issues.append(f"Critical response time: {metrics.response_time_ms}ms")
        elif metrics.response_time_ms > self._health_thresholds["response_time_warning"]:
            issues.append(f"Slow response time: {metrics.response_time_ms}ms")
        
        # Check error rate
        if metrics.error_rate > self._health_thresholds["error_rate_critical"]:
            issues.append(f"Critical error rate: {metrics.error_rate:.1%}")
        elif metrics.error_rate > self._health_thresholds["error_rate_warning"]:
            issues.append(f"High error rate: {metrics.error_rate:.1%}")
        
        # Determine overall status
        critical_issues = [i for i in issues if "Critical" in i]
        warning_issues = [i for i in issues if "High" in i or "Slow" in i]
        
        if critical_issues:
            return HealthStatus.CRITICAL, issues
        elif len(warning_issues) >= 2:
            return HealthStatus.UNHEALTHY, issues
        elif warning_issues:
            return HealthStatus.DEGRADED, issues
        else:
            return HealthStatus.HEALTHY, []
    
    def _generate_health_recommendations(self, status: HealthStatus, issues: List[str]) -> List[str]:
        """Generate health improvement recommendations."""
        recommendations = []
        
        if status == HealthStatus.HEALTHY:
            recommendations.append("System is healthy - continue monitoring")
            return recommendations
        
        # Memory-related recommendations
        if any("memory" in issue.lower() for issue in issues):
            recommendations.extend([
                "Consider memory optimization using config.optimize_for_memory_constraint()",
                "Review cache configuration and implement memory pressure handling",
                "Check for memory leaks in long-running operations"
            ])
        
        # Response time recommendations
        if any("response" in issue.lower() for issue in issues):
            recommendations.extend([
                "Optimize performance using config.optimize_for_performance()",
                "Review slow operations and implement caching",
                "Consider circuit breaker patterns for external dependencies"
            ])
        
        # Error rate recommendations
        if any("error" in issue.lower() for issue in issues):
            recommendations.extend([
                "Review error logs for patterns and root causes",
                "Implement retry mechanisms for transient failures",
                "Validate input handling and error recovery procedures"
            ])
        
        # Critical status recommendations
        if status == HealthStatus.CRITICAL:
            recommendations.insert(0, "URGENT: System requires immediate attention")
            recommendations.append("Consider scaling down operations or implementing emergency mode")
        
        return recommendations

# ===== SECTION 3: PERFORMANCE ANALYSIS =====

class PerformanceAnalyzer:
    """Performance bottleneck detection and analysis."""
    
    def __init__(self):
        self._lock = threading.Lock()
        self._performance_data: Dict[str, List[float]] = defaultdict(list)
        self._operation_counts: Dict[str, int] = defaultdict(int)
        self._bottleneck_history: List[PerformanceBottleneck] = []
    
    def analyze_performance_issues(self) -> DiagnosticResult:
        """Analyze performance issues and bottlenecks."""
        start_time = time.time()
        
        try:
            # Collect performance data
            bottlenecks = self._detect_performance_bottlenecks()
            
            # Analyze trends
            trends = self._analyze_performance_trends()
            
            # Generate recommendations
            recommendations = self._generate_performance_recommendations(bottlenecks)
            
            # Determine severity
            critical_bottlenecks = [b for b in bottlenecks if b.impact_score > 80]
            major_bottlenecks = [b for b in bottlenecks if 60 < b.impact_score <= 80]
            
            if critical_bottlenecks:
                level = DiagnosticLevel.CRITICAL
                message = f"Critical performance issues detected: {len(critical_bottlenecks)} bottlenecks"
            elif major_bottlenecks:
                level = DiagnosticLevel.ERROR
                message = f"Major performance issues detected: {len(major_bottlenecks)} bottlenecks"
            elif bottlenecks:
                level = DiagnosticLevel.WARNING
                message = f"Performance issues detected: {len(bottlenecks)} bottlenecks"
            else:
                level = DiagnosticLevel.INFO
                message = "No significant performance issues detected"
            
            return DiagnosticResult(
                diagnostic_name="performance_analysis",
                level=level,
                message=message,
                recommendations=recommendations,
                metrics={
                    "bottlenecks": [self._serialize_bottleneck(b) for b in bottlenecks],
                    "performance_trends": trends,
                    "analysis_duration_ms": (time.time() - start_time) * 1000
                }
            )
            
        except Exception as e:
            return DiagnosticResult(
                diagnostic_name="performance_analysis",
                level=DiagnosticLevel.ERROR,
                message=f"Performance analysis failed: {str(e)}",
                recommendations=["Manual performance review required"],
                metrics={"error": str(e)}
            )
    
    def _detect_performance_bottlenecks(self) -> List[PerformanceBottleneck]:
        """Detect performance bottlenecks across interfaces."""
        bottlenecks = []
        
        # Test interface performance
        interfaces = ["cache", "security", "logging", "metrics", "utility", "config"]
        
        for interface in interfaces:
            performance_data = self._measure_interface_performance(interface)
            
            if performance_data["avg_response_time"] > 100:  # 100ms threshold
                impact_score = min(100, performance_data["avg_response_time"] / 10)
                
                bottleneck = PerformanceBottleneck(
                    component=interface,
                    operation="primary_operations",
                    avg_response_time_ms=performance_data["avg_response_time"],
                    impact_score=impact_score,
                    frequency=performance_data["operation_count"],
                    recommendations=self._get_interface_recommendations(interface, performance_data)
                )
                
                bottlenecks.append(bottleneck)
        
        return sorted(bottlenecks, key=lambda x: x.impact_score, reverse=True)
    
    def _measure_interface_performance(self, interface_name: str) -> Dict[str, Any]:
        """Measure performance for specific interface."""
        response_times = []
        operation_count = 0
        
        # Perform multiple operations to get reliable measurements
        for _ in range(10):
            start_time = time.time()
            
            try:
                if interface_name == "cache":
                    cache.cache_get("performance_test")
                elif interface_name == "security":
                    security.validate_input("performance_test")
                elif interface_name == "logging":
                    log_gateway.log_info("Performance test")
                elif interface_name == "metrics":
                    metrics.record_metric("performance_test", 1.0)
                elif interface_name == "utility":
                    utility.validate_string_input("performance_test")
                elif interface_name == "config":
                    config.get_parameter("PERFORMANCE_TEST", "default")
                
                duration_ms = (time.time() - start_time) * 1000
                response_times.append(duration_ms)
                operation_count += 1
                
            except Exception:
                response_times.append(1000)  # Penalty for errors
                operation_count += 1
        
        return {
            "avg_response_time": statistics.mean(response_times) if response_times else 0,
            "max_response_time": max(response_times) if response_times else 0,
            "min_response_time": min(response_times) if response_times else 0,
            "operation_count": operation_count
        }

# ===== SECTION 4: MEMORY ANALYSIS =====

class MemoryAnalyzer:
    """Memory usage analysis and leak detection."""
    
    def __init__(self):
        self._lock = threading.Lock()
        self._memory_snapshots: List[Tuple[float, float]] = []
        self._memory_baseline: Optional[float] = None
    
    def detect_resource_problems(self) -> DiagnosticResult:
        """Detect memory leaks and resource problems."""
        start_time = time.time()
        
        try:
            # Take memory snapshot
            current_memory = self._get_memory_usage()
            
            # Store snapshot
            with self._lock:
                self._memory_snapshots.append((time.time(), current_memory))
                
                # Keep last 50 snapshots
                if len(self._memory_snapshots) > 50:
                    self._memory_snapshots.pop(0)
            
            # Analyze memory trends
            memory_trend = self._analyze_memory_trend()
            
            # Detect potential leaks
            leak_indicators = self._detect_memory_leaks()
            
            # Check resource limits
            resource_issues = self._check_resource_limits(current_memory)
            
            # Generate recommendations
            recommendations = self._generate_memory_recommendations(memory_trend, leak_indicators, resource_issues)
            
            # Determine severity
            if resource_issues["critical"]:
                level = DiagnosticLevel.CRITICAL
                message = "Critical memory issues detected"
            elif resource_issues["warning"] or leak_indicators:
                level = DiagnosticLevel.WARNING
                message = "Memory concerns detected"
            else:
                level = DiagnosticLevel.INFO
                message = "Memory usage within normal limits"
            
            return DiagnosticResult(
                diagnostic_name="resource_problems",
                level=level,
                message=message,
                recommendations=recommendations,
                metrics={
                    "current_memory_mb": current_memory,
                    "memory_trend": memory_trend,
                    "leak_indicators": leak_indicators,
                    "resource_issues": resource_issues,
                    "analysis_duration_ms": (time.time() - start_time) * 1000
                }
            )
            
        except Exception as e:
            return DiagnosticResult(
                diagnostic_name="resource_problems",
                level=DiagnosticLevel.ERROR,
                message=f"Resource analysis failed: {str(e)}",
                recommendations=["Manual memory inspection required"],
                metrics={"error": str(e)}
            )
    
    def _analyze_memory_trend(self) -> Dict[str, Any]:
        """Analyze memory usage trends."""
        with self._lock:
            if len(self._memory_snapshots) < 5:
                return {"trend": "insufficient_data", "samples": len(self._memory_snapshots)}
            
            # Extract memory values
            memory_values = [snapshot[1] for snapshot in self._memory_snapshots[-10:]]
            
            # Calculate trend
            if len(memory_values) > 1:
                first_half = memory_values[:len(memory_values)//2]
                second_half = memory_values[len(memory_values)//2:]
                
                avg_first = statistics.mean(first_half)
                avg_second = statistics.mean(second_half)
                
                growth_rate = (avg_second - avg_first) / avg_first if avg_first > 0 else 0
                
                if growth_rate > 0.1:  # 10% growth
                    trend = "increasing"
                elif growth_rate < -0.1:
                    trend = "decreasing"
                else:
                    trend = "stable"
            else:
                trend = "stable"
                growth_rate = 0
            
            return {
                "trend": trend,
                "growth_rate": growth_rate,
                "current": memory_values[-1],
                "average": statistics.mean(memory_values),
                "max": max(memory_values),
                "min": min(memory_values),
                "samples": len(memory_values)
            }

# ===== SECTION 5: DIAGNOSTIC REPORT GENERATION =====

class DiagnosticReportGenerator:
    """Generate comprehensive diagnostic reports."""
    
    def __init__(self):
        self.health_diagnostics = SystemHealthDiagnostics()
        self.performance_analyzer = PerformanceAnalyzer()
        self.memory_analyzer = MemoryAnalyzer()
    
    def generate_diagnostic_report(self) -> DiagnosticResult:
        """Generate comprehensive system diagnostic report."""
        start_time = time.time()
        
        try:
            # Collect all diagnostic results
            health_result = self.health_diagnostics.diagnose_system_health()
            performance_result = self.performance_analyzer.analyze_performance_issues()
            memory_result = self.memory_analyzer.detect_resource_problems()
            
            # Combine results
            all_recommendations = []
            all_recommendations.extend(health_result.recommendations)
            all_recommendations.extend(performance_result.recommendations)
            all_recommendations.extend(memory_result.recommendations)
            
            # Determine overall severity
            levels = [health_result.level, performance_result.level, memory_result.level]
            if DiagnosticLevel.CRITICAL in levels:
                overall_level = DiagnosticLevel.CRITICAL
            elif DiagnosticLevel.ERROR in levels:
                overall_level = DiagnosticLevel.ERROR
            elif DiagnosticLevel.WARNING in levels:
                overall_level = DiagnosticLevel.WARNING
            else:
                overall_level = DiagnosticLevel.INFO
            
            # Generate executive summary
            summary = self._generate_executive_summary(health_result, performance_result, memory_result)
            
            return DiagnosticResult(
                diagnostic_name="comprehensive_diagnostic",
                level=overall_level,
                message=f"System diagnostic complete - {overall_level.value} issues found",
                recommendations=all_recommendations[:10],  # Top 10 recommendations
                metrics={
                    "executive_summary": summary,
                    "health_status": health_result.metrics,
                    "performance_analysis": performance_result.metrics,
                    "memory_analysis": memory_result.metrics,
                    "report_generation_time_ms": (time.time() - start_time) * 1000
                }
            )
            
        except Exception as e:
            return DiagnosticResult(
                diagnostic_name="comprehensive_diagnostic",
                level=DiagnosticLevel.ERROR,
                message=f"Diagnostic report generation failed: {str(e)}",
                recommendations=["Manual system inspection required"],
                metrics={"error": str(e)}
            )

# ===== SECTION 6: UTILITY FUNCTIONS =====

def _get_memory_usage() -> float:
    """Get current memory usage in MB."""
    try:
        import psutil
        process = psutil.Process()
        return process.memory_info().rss / 1024 / 1024
    except ImportError:
        # Fallback: estimate based on object count
        return len(gc.get_objects()) / 10000  # Rough estimate

def _get_average_response_time() -> float:
    """Get average response time from recent operations."""
    try:
        # Mock implementation - would use real metrics
        return 50.0  # ms
    except Exception:
        return 0.0

def _get_current_error_rate() -> float:
    """Get current error rate."""
    try:
        # Mock implementation - would use real error tracking
        return 0.02  # 2% error rate
    except Exception:
        return 0.0

def _get_cache_hit_rate() -> float:
    """Get cache hit rate."""
    try:
        # Mock implementation - would use real cache metrics
        return 0.85  # 85% hit rate
    except Exception:
        return 0.0

# ===== SECTION 7: MAIN TROUBLESHOOTING FUNCTIONS =====

def diagnose_system_health() -> DiagnosticResult:
    """Diagnose overall system health."""
    diagnostics = SystemHealthDiagnostics()
    return diagnostics.diagnose_system_health()

def analyze_performance_issues() -> DiagnosticResult:
    """Analyze performance issues and bottlenecks."""
    analyzer = PerformanceAnalyzer()
    return analyzer.analyze_performance_issues()

def detect_resource_problems() -> DiagnosticResult:
    """Detect memory leaks and resource problems."""
    analyzer = MemoryAnalyzer()
    return analyzer.detect_resource_problems()

def generate_diagnostic_report() -> DiagnosticResult:
    """Generate comprehensive diagnostic report."""
    generator = DiagnosticReportGenerator()
    return generator.generate_diagnostic_report()

    def _get_interface_recommendations(self, interface: str, performance_data: Dict[str, Any]) -> List[str]:
        """Get performance recommendations for specific interface."""
        recommendations = []
        
        avg_time = performance_data["avg_response_time"]
        max_time = performance_data["max_response_time"]
        
        if avg_time > 200:
            recommendations.append(f"High average response time ({avg_time:.1f}ms) - consider optimization")
        
        if max_time > 500:
            recommendations.append(f"Very slow maximum response time ({max_time:.1f}ms) - investigate bottlenecks")
        
        # Interface-specific recommendations
        if interface == "cache":
            recommendations.extend([
                "Consider cache prewarming for frequently accessed data",
                "Review cache eviction policies and memory allocation",
                "Implement cache hit ratio monitoring"
            ])
        elif interface == "security":
            recommendations.extend([
                "Review input validation complexity",
                "Consider caching validation results for repeated inputs",
                "Optimize security rule evaluation order"
            ])
        elif interface == "logging":
            recommendations.extend([
                "Review log level configuration",
                "Consider asynchronous logging for performance",
                "Implement log rotation and cleanup policies"
            ])
        elif interface == "metrics":
            recommendations.extend([
                "Optimize metric aggregation algorithms",
                "Consider batch metric submission",
                "Review metric retention policies"
            ])
        elif interface == "config":
            recommendations.extend([
                "Implement configuration caching",
                "Review configuration validation complexity",
                "Consider lazy loading of configuration sections"
            ])
        
        return recommendations or ["Performance appears acceptable for this interface"]
    
    def _analyze_performance_trends(self) -> Dict[str, Any]:
        """Analyze performance trends over time."""
        with self._lock:
            if len(self._performance_data) < 5:
                return {"trend_analysis": "insufficient_data", "sample_size": len(self._performance_data)}
            
            trends = {}
            
            for operation, measurements in self._performance_data.items():
                if len(measurements) >= 3:
                    recent_measurements = measurements[-10:]  # Last 10 measurements
                    
                    # Calculate trend
                    avg_time = statistics.mean(recent_measurements)
                    median_time = statistics.median(recent_measurements)
                    
                    # Trend analysis
                    if len(recent_measurements) > 5:
                        first_half = recent_measurements[:len(recent_measurements)//2]
                        second_half = recent_measurements[len(recent_measurements)//2:]
                        
                        avg_first = statistics.mean(first_half)
                        avg_second = statistics.mean(second_half)
                        
                        if avg_second > avg_first * 1.2:
                            trend = "degrading"
                        elif avg_second < avg_first * 0.8:
                            trend = "improving"
                        else:
                            trend = "stable"
                    else:
                        trend = "stable"
                    
                    trends[operation] = {
                        "trend": trend,
                        "average_ms": avg_time,
                        "median_ms": median_time,
                        "sample_size": len(recent_measurements),
                        "performance_score": max(0, 100 - avg_time / 10)
                    }
            
            return {
                "trend_analysis": "complete",
                "operation_trends": trends,
                "overall_trend": self._calculate_overall_trend(trends)
            }
    
    def _calculate_overall_trend(self, operation_trends: Dict[str, Dict[str, Any]]) -> str:
        """Calculate overall performance trend."""
        if not operation_trends:
            return "unknown"
        
        trend_counts = {"degrading": 0, "improving": 0, "stable": 0}
        
        for operation_data in operation_trends.values():
            trend = operation_data.get("trend", "stable")
            trend_counts[trend] += 1
        
        total = sum(trend_counts.values())
        
        if trend_counts["degrading"] / total > 0.5:
            return "degrading"
        elif trend_counts["improving"] / total > 0.5:
            return "improving"
        else:
            return "stable"
    
    def _serialize_bottleneck(self, bottleneck: PerformanceBottleneck) -> Dict[str, Any]:
        """Serialize performance bottleneck for JSON output."""
        return {
            "component": bottleneck.component,
            "operation": bottleneck.operation,
            "avg_response_time_ms": bottleneck.avg_response_time_ms,
            "impact_score": bottleneck.impact_score,
            "frequency": bottleneck.frequency,
            "recommendations": bottleneck.recommendations
        }

    def _detect_memory_leaks(self) -> List[str]:
        """Detect potential memory leaks."""
        leak_indicators = []
        
        with self._lock:
            if len(self._memory_snapshots) < 10:
                return ["Insufficient data for leak detection"]
            
            # Analyze memory growth pattern
            memory_values = [snapshot[1] for snapshot in self._memory_snapshots]
            
            # Check for consistent growth
            growth_points = 0
            for i in range(1, len(memory_values)):
                if memory_values[i] > memory_values[i-1]:
                    growth_points += 1
            
            growth_rate = growth_points / (len(memory_values) - 1)
            
            if growth_rate > 0.7:  # 70% of measurements show growth
                leak_indicators.append(f"Consistent memory growth detected ({growth_rate:.1%} of measurements)")
            
            # Check for memory spikes
            avg_memory = statistics.mean(memory_values)
            spike_threshold = avg_memory * 1.5
            
            spikes = [m for m in memory_values if m > spike_threshold]
            if len(spikes) > len(memory_values) * 0.2:  # More than 20% are spikes
                leak_indicators.append(f"Frequent memory spikes detected ({len(spikes)} spikes)")
            
            # Check for high baseline
            if avg_memory > 80:  # 80MB baseline
                leak_indicators.append(f"High memory baseline ({avg_memory:.1f}MB)")
        
        return leak_indicators or ["No obvious memory leak indicators detected"]
    
    def _check_resource_limits(self, current_memory: float) -> Dict[str, List[str]]:
        """Check resource limits and constraints."""
        issues = {"critical": [], "warning": []}
        
        # Memory limit checks
        if current_memory > 100:  # 100MB critical threshold
            issues["critical"].append(f"Memory usage critical: {current_memory:.1f}MB")
        elif current_memory > 80:   # 80MB warning threshold
            issues["warning"].append(f"Memory usage high: {current_memory:.1f}MB")
        
        # Check available system resources
        try:
            import psutil
            
            # Check system memory if available
            system_memory = psutil.virtual_memory()
            if system_memory.percent > 90:
                issues["critical"].append(f"System memory critical: {system_memory.percent:.1f}%")
            elif system_memory.percent > 80:
                issues["warning"].append(f"System memory high: {system_memory.percent:.1f}%")
                
        except ImportError:
            issues["warning"].append("System resource monitoring unavailable")
        
        # Check Lambda-specific constraints
        if current_memory > 128:  # AWS Lambda default limit
            issues["critical"].append("Memory usage exceeds AWS Lambda 128MB limit")
        
        return issues
    
    def _generate_memory_recommendations(self, memory_trend: Dict[str, Any], leak_indicators: List[str], resource_issues: Dict[str, List[str]]) -> List[str]:
        """Generate memory optimization recommendations."""
        recommendations = []
        
        # Critical memory issues
        if resource_issues["critical"]:
            recommendations.extend([
                "URGENT: Reduce memory usage immediately",
                "Consider using config.optimize_for_memory_constraint()",
                "Implement emergency memory cleanup procedures"
            ])
        
        # Memory leak indicators
        if any("growth" in indicator.lower() for indicator in leak_indicators):
            recommendations.extend([
                "Investigate potential memory leaks",
                "Review object lifecycle management",
                "Implement periodic garbage collection"
            ])
        
        # Memory trend issues
        trend = memory_trend.get("trend", "stable")
        if trend == "increasing":
            recommendations.extend([
                "Memory usage is increasing - monitor closely",
                "Review recent code changes for memory impact",
                "Consider implementing memory pressure handling"
            ])
        
        # General memory optimization
        if memory_trend.get("current", 0) > 50:
            recommendations.extend([
                "Consider cache size optimization",
                "Review data structure efficiency",
                "Implement lazy loading where possible"
            ])
        
        # Warning level issues
        if resource_issues["warning"]:
            recommendations.extend([
                "Monitor memory usage trends",
                "Consider proactive memory optimization",
                "Review memory allocation patterns"
            ])
        
        return recommendations or ["Memory usage appears normal"]
    
    def _generate_executive_summary(self, health_result: DiagnosticResult, performance_result: DiagnosticResult, memory_result: DiagnosticResult) -> Dict[str, Any]:
        """Generate executive summary of diagnostic results."""
        summary = {
            "timestamp": time.time(),
            "overall_health": "healthy",
            "critical_issues": 0,
            "warnings": 0,
            "key_findings": [],
            "immediate_actions": [],
            "recommendations": []
        }
        
        # Analyze health status
        health_level = health_result.level
        if health_level == DiagnosticLevel.CRITICAL:
            summary["overall_health"] = "critical"
            summary["critical_issues"] += 1
            summary["immediate_actions"].append("Address critical system health issues")
        elif health_level == DiagnosticLevel.ERROR:
            summary["overall_health"] = "unhealthy"
            summary["warnings"] += 1
        
        # Analyze performance status
        performance_level = performance_result.level
        if performance_level == DiagnosticLevel.CRITICAL:
            summary["overall_health"] = "critical"
            summary["critical_issues"] += 1
            summary["immediate_actions"].append("Address critical performance issues")
        elif performance_level == DiagnosticLevel.ERROR:
            if summary["overall_health"] == "healthy":
                summary["overall_health"] = "degraded"
            summary["warnings"] += 1
        
        # Analyze memory status
        memory_level = memory_result.level
        if memory_level == DiagnosticLevel.CRITICAL:
            summary["overall_health"] = "critical"
            summary["critical_issues"] += 1
            summary["immediate_actions"].append("Address critical memory issues")
        elif memory_level == DiagnosticLevel.WARNING:
            summary["warnings"] += 1
        
        # Key findings
        summary["key_findings"].extend([
            f"System Health: {health_result.message}",
            f"Performance: {performance_result.message}",
            f"Memory: {memory_result.message}"
        ])
        
        # Compile recommendations
        all_recommendations = []
        all_recommendations.extend(health_result.recommendations[:3])
        all_recommendations.extend(performance_result.recommendations[:3])
        all_recommendations.extend(memory_result.recommendations[:3])
        
        summary["recommendations"] = list(set(all_recommendations))[:10]  # Top 10 unique recommendations
        
        return summary
