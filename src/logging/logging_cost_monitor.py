"""
logging_cost_monitor.py
Version: 2025.9.18.1-METRICS_GATEWAY_COMPLIANCE
Description: Updated to use metrics.py gateway for all metrics access

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
import logging
import threading
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime

# FIXED: Import metrics through gateway
from metrics import record_error_response_metric, get_all_metrics

# Import from consolidated cost protection
from utility_cost import (
    get_cost_protection_manager,
    CostCategory,
    CostProtectionLevel,
    ServiceType,
    EmergencyTrigger,
    register_protection_callback
)

logger = logging.getLogger(__name__)

# ===== SECTION 1: LOGGING-FOCUSED COST MONITOR =====

@dataclass
class CostMonitoringMetrics:
    """Metrics specific to cost monitoring and logging."""
    log_entries_written: int = 0
    alert_notifications_sent: int = 0
    reports_generated: int = 0
    last_alert_timestamp: float = 0.0
    monitoring_start_time: float = 0.0

class LoggingCostMonitor:
    """
    Cost monitor focused on logging and reporting.
    FIXED: Uses metrics gateway for all metrics operations.
    """
    
    def __init__(self):
        self._metrics = CostMonitoringMetrics()
        self._metrics.monitoring_start_time = time.time()
        self._lock = threading.Lock()
        
        # Alert configuration
        self._alert_interval = 300.0  # 5 minutes between alerts
        self._last_alert_levels = {}  # Track last alert for each level
        
        # Register for cost protection callbacks
        self._register_cost_protection_callbacks()
        
        logger.debug("Logging cost monitor initialized")
    
    def _register_cost_protection_callbacks(self) -> None:
        """Register callbacks to receive cost protection events."""
        try:
            cost_manager = get_cost_protection_manager()
            
            # Register callback for cost events
            register_protection_callback('cost_threshold_reached', self._handle_cost_threshold)
            register_protection_callback('emergency_mode_activated', self._handle_emergency_mode)
            register_protection_callback('cost_limit_exceeded', self._handle_cost_limit)
            
            logger.debug("Cost protection callbacks registered")
            
        except Exception as e:
            logger.warning(f"Failed to register cost protection callbacks: {e}")
    
    def _handle_cost_threshold(self, event_data: Dict[str, Any]) -> None:
        """Handle cost threshold reached event."""
        with self._lock:
            self._metrics.log_entries_written += 1
            
            # FIXED: Record through metrics gateway
            record_error_response_metric(
                error_type='cost_threshold_reached',
                severity='medium',
                category='cost_protection',
                context=event_data
            )
            
            # Check if alert should be sent
            threshold = event_data.get('threshold', 'unknown')
            if self._should_send_alert(threshold):
                self._send_cost_alert(event_data)
    
    def _handle_emergency_mode(self, event_data: Dict[str, Any]) -> None:
        """Handle emergency mode activation."""
        with self._lock:
            self._metrics.log_entries_written += 1
            
            # FIXED: Record through metrics gateway
            record_error_response_metric(
                error_type='emergency_mode_activated',
                severity='critical',
                category='cost_protection',
                context=event_data
            )
            
            # Always send alert for emergency mode
            self._send_emergency_alert(event_data)
    
    def _handle_cost_limit(self, event_data: Dict[str, Any]) -> None:
        """Handle cost limit exceeded event."""
        with self._lock:
            self._metrics.log_entries_written += 1
            
            # FIXED: Record through metrics gateway
            record_error_response_metric(
                error_type='cost_limit_exceeded',
                severity='high',
                category='cost_protection',
                context=event_data
            )
            
            # Send limit exceeded alert
            self._send_limit_alert(event_data)
    
    def _should_send_alert(self, alert_level: str) -> bool:
        """Check if alert should be sent based on interval."""
        current_time = time.time()
        last_alert = self._last_alert_levels.get(alert_level, 0)
        
        return (current_time - last_alert) >= self._alert_interval
    
    def _send_cost_alert(self, event_data: Dict[str, Any]) -> None:
        """Send cost threshold alert."""
        alert_data = {
            'alert_type': 'cost_threshold',
            'timestamp': time.time(),
            'event_data': event_data,
            'monitoring_duration': time.time() - self._metrics.monitoring_start_time
        }
        
        logger.warning(f"Cost threshold alert: {alert_data}")
        
        with self._lock:
            self._metrics.alert_notifications_sent += 1
            self._metrics.last_alert_timestamp = time.time()
            self._last_alert_levels[event_data.get('threshold', 'unknown')] = time.time()
    
    def _send_emergency_alert(self, event_data: Dict[str, Any]) -> None:
        """Send emergency mode alert."""
        alert_data = {
            'alert_type': 'emergency_mode',
            'timestamp': time.time(),
            'event_data': event_data,
            'trigger': event_data.get('trigger', 'unknown')
        }
        
        logger.critical(f"EMERGENCY MODE ACTIVATED: {alert_data}")
        
        with self._lock:
            self._metrics.alert_notifications_sent += 1
            self._metrics.last_alert_timestamp = time.time()
    
    def _send_limit_alert(self, event_data: Dict[str, Any]) -> None:
        """Send cost limit exceeded alert."""
        alert_data = {
            'alert_type': 'cost_limit_exceeded',
            'timestamp': time.time(),
            'event_data': event_data,
            'limit': event_data.get('limit', 'unknown')
        }
        
        logger.error(f"Cost limit exceeded: {alert_data}")
        
        with self._lock:
            self._metrics.alert_notifications_sent += 1
            self._metrics.last_alert_timestamp = time.time()
    
    def generate_cost_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive cost monitoring report.
        FIXED: Uses metrics gateway for system metrics.
        """
        try:
            # FIXED: Get system metrics through gateway
            system_metrics = get_all_metrics()
            
            # Get cost protection status
            cost_manager = get_cost_protection_manager()
            cost_status = cost_manager.get_protection_status() if cost_manager else {}
            
            # Generate report
            report = {
                'report_type': 'cost_monitoring',
                'generated_at': time.time(),
                'monitoring_duration': time.time() - self._metrics.monitoring_start_time,
                'monitoring_metrics': {
                    'log_entries_written': self._metrics.log_entries_written,
                    'alert_notifications_sent': self._metrics.alert_notifications_sent,
                    'reports_generated': self._metrics.reports_generated,
                    'last_alert_timestamp': self._metrics.last_alert_timestamp
                },
                'cost_protection_status': cost_status,
                'system_metrics': system_metrics,
                'recommendations': self._generate_recommendations(cost_status, system_metrics)
            }
            
            with self._lock:
                self._metrics.reports_generated += 1
            
            # FIXED: Record report generation through gateway
            record_error_response_metric(
                error_type='cost_report_generated',
                severity='low',
                category='reporting',
                context={'report_size': len(str(report))}
            )
            
            logger.info(f"Cost monitoring report generated (report #{self._metrics.reports_generated})")
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate cost report: {e}")
            
            # FIXED: Record failure through gateway
            record_error_response_metric(
                error_type='cost_report_failed',
                severity='medium',
                category='reporting',
                context={'error': str(e)}
            )
            
            return {
                'report_type': 'cost_monitoring',
                'generated_at': time.time(),
                'error': str(e),
                'status': 'failed'
            }
    
    def _generate_recommendations(self, cost_status: Dict[str, Any], 
                                system_metrics: Dict[str, Any]) -> List[str]:
        """Generate cost optimization recommendations."""
        recommendations = []
        
        # Check if emergency mode is active
        if cost_status.get('emergency_mode_active', False):
            recommendations.append("Emergency mode active - review cost patterns immediately")
        
        # Check alert frequency
        if self._metrics.alert_notifications_sent > 10:
            recommendations.append("High alert frequency - consider adjusting thresholds")
        
        # Check monitoring duration
        monitoring_hours = (time.time() - self._metrics.monitoring_start_time) / 3600
        if monitoring_hours > 24 and self._metrics.log_entries_written > 100:
            recommendations.append("High cost event frequency - investigate cost drivers")
        
        # Default recommendation
        if not recommendations:
            recommendations.append("Cost monitoring operating normally")
        
        return recommendations
    
    def get_monitoring_metrics(self) -> Dict[str, Any]:
        """Get current monitoring metrics."""
        with self._lock:
            return {
                'log_entries_written': self._metrics.log_entries_written,
                'alert_notifications_sent': self._metrics.alert_notifications_sent,
                'reports_generated': self._metrics.reports_generated,
                'last_alert_timestamp': self._metrics.last_alert_timestamp,
                'monitoring_start_time': self._metrics.monitoring_start_time,
                'monitoring_duration': time.time() - self._metrics.monitoring_start_time,
                'alert_levels_tracked': len(self._last_alert_levels)
            }

# EOS

# ===== SECTION 2: GLOBAL INSTANCE =====

_cost_monitor = None
_monitor_lock = threading.Lock()

def get_cost_monitor() -> LoggingCostMonitor:
    """Get or create the global cost monitor."""
    global _cost_monitor
    
    if _cost_monitor is None:
        with _monitor_lock:
            if _cost_monitor is None:
                _cost_monitor = LoggingCostMonitor()
    
    return _cost_monitor

def reset_cost_monitor() -> None:
    """Reset the global cost monitor."""
    global _cost_monitor
    with _monitor_lock:
        _cost_monitor = None

# EOS

# ===== MODULE EXPORTS =====

__all__ = [
    'LoggingCostMonitor',
    'CostMonitoringMetrics',
    'get_cost_monitor',
    'reset_cost_monitor'
]

# EOF
