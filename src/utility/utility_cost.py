"""
utility_cost.py
Version: 2025.9.17.01
Description: Single implementation for ALL cost protection operations to eliminate duplicates

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
import os
import json
import threading
import logging
from typing import Dict, Any, Optional, List, Set, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

# ===== SECTION 1: CONSOLIDATED COST PROTECTION ENUMS AND DATA STRUCTURES =====

class CostCategory(Enum):
    """Cost categories for request prioritization - CONSOLIDATED from http_client.py."""
    CRITICAL = "critical"     # Always allowed (Health checks, critical config)
    NORMAL = "normal"         # Standard operations
    OPTIONAL = "optional"     # Can be deferred (Metrics, analytics)
    LOW_PRIORITY = "low"      # First to be blocked

class CostProtectionLevel(Enum):
    """Cost protection levels based on usage thresholds."""
    DISABLED = "disabled"     # No cost protection
    MONITORING = "monitoring" # Track usage only
    WARNING = "warning"       # 50-75% of limits
    PROTECTION = "protection" # 75-90% of limits
    EMERGENCY = "emergency"   # >90% of limits

class ServiceType(Enum):
    """AWS services tracked for cost protection - CONSOLIDATED."""
    LAMBDA = "lambda"
    CLOUDWATCH = "cloudwatch"
    SSM = "ssm"
    CLOUDWATCH_LOGS = "cloudwatch_logs"

class EmergencyTrigger(Enum):
    """Triggers that can activate emergency mode."""
    MANUAL = "manual"
    LAMBDA_LIMIT = "lambda_limit"
    CLOUDWATCH_LIMIT = "cloudwatch_limit"
    SSM_LIMIT = "ssm_limit"
    COST_SPIKE = "cost_spike"
    MEMORY_CRITICAL = "memory_critical"

@dataclass
class CostLimits:
    """CONSOLIDATED: AWS Free Tier limits - replaces scattered limit definitions."""
    # Lambda limits (monthly)
    lambda_invocations_monthly: int = 1000000
    lambda_compute_seconds_monthly: int = 400000
    lambda_storage_gb_monthly: float = 0.5
    
    # CloudWatch limits (monthly)
    cloudwatch_api_calls_monthly: int = 1000000
    cloudwatch_logs_gb_monthly: float = 5.0
    cloudwatch_custom_metrics_monthly: int = 10
    
    # SSM limits (monthly)
    ssm_api_calls_monthly: int = 40000
    ssm_parameter_tier_advanced_monthly: int = 0  # Free tier doesn't include advanced
    
    # Warning thresholds (percentage of monthly limits)
    warning_threshold_percent: float = 75.0
    critical_threshold_percent: float = 90.0
    emergency_threshold_percent: float = 95.0

@dataclass
class UsageMetrics:
    """CONSOLIDATED: Current usage tracking - replaces scattered usage tracking."""
    # Lambda usage
    lambda_invocations: int = 0
    lambda_compute_seconds: float = 0.0
    lambda_storage_gb: float = 0.0
    
    # CloudWatch usage
    cloudwatch_api_calls: int = 0
    cloudwatch_logs_bytes: int = 0
    cloudwatch_custom_metrics: int = 0
    
    # SSM usage
    ssm_api_calls: int = 0
    ssm_advanced_parameters: int = 0
    
    # Timing
    last_reset: float = field(default_factory=time.time)
    last_updated: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'lambda_invocations': self.lambda_invocations,
            'lambda_compute_seconds': self.lambda_compute_seconds,
            'lambda_storage_gb': self.lambda_storage_gb,
            'cloudwatch_api_calls': self.cloudwatch_api_calls,
            'cloudwatch_logs_bytes': self.cloudwatch_logs_bytes,
            'cloudwatch_custom_metrics': self.cloudwatch_custom_metrics,
            'ssm_api_calls': self.ssm_api_calls,
            'ssm_advanced_parameters': self.ssm_advanced_parameters,
            'last_reset': self.last_reset,
            'last_updated': self.last_updated
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UsageMetrics':
        """Create from dictionary."""
        return cls(**data)

@dataclass
class CostProtectionState:
    """CONSOLIDATED: Complete cost protection state."""
    # Current state
    protection_level: CostProtectionLevel = CostProtectionLevel.MONITORING
    emergency_mode: bool = False
    emergency_trigger: Optional[EmergencyTrigger] = None
    emergency_timestamp: Optional[float] = None
    emergency_reason: str = ""
    
    # Usage data
    usage: UsageMetrics = field(default_factory=UsageMetrics)
    limits: CostLimits = field(default_factory=CostLimits)
    
    # Blocked operations tracking
    blocked_operations: Dict[str, int] = field(default_factory=dict)
    blocked_services: Set[ServiceType] = field(default_factory=set)
    
    # State persistence
    state_file: str = "/tmp/lambda_cost_protection_state.json"
    auto_save: bool = True

# ===== SECTION 2: CONSOLIDATED COST PROTECTION MANAGER =====

class ConsolidatedCostProtectionManager:
    """
    CONSOLIDATED: Single class for ALL cost protection operations.
    
    ELIMINATES:
    - Scattered try/except ImportError patterns (4+ locations)
    - Duplicate cost protection state management (3+ implementations)
    - Scattered emergency mode detection (multiple files)
    - Duplicate service usage tracking (scattered across modules)
    
    REPLACES:
    - http_client.py: Cost protection checking
    - security.py: set_cost_protection_state()
    - logging_cost_monitor.py: Usage tracking (will delegate to this)
    - All scattered is_cost_protection_active() imports
    """
    
    def __init__(self, state_file: str = None, auto_save: bool = True):
        self._state = CostProtectionState()
        self._state.state_file = state_file or "/tmp/lambda_cost_protection_state.json"
        self._state.auto_save = auto_save
        
        self._lock = threading.Lock()
        self._callbacks = {
            CostProtectionLevel.WARNING: [],
            CostProtectionLevel.PROTECTION: [],
            CostProtectionLevel.EMERGENCY: []
        }
        
        # Load persisted state
        self._load_state()
        
        # Check monthly reset
        self._check_monthly_reset()
        
        logger.debug(f"Cost protection manager initialized: {self._state.protection_level.value}")
    
    # ===== COST PROTECTION STATE MANAGEMENT =====
    
    def is_cost_protection_active(self) -> bool:
        """
        CONSOLIDATED: Check if cost protection is active.
        
        REPLACES ALL:
        - try/except ImportError patterns for is_cost_protection_active
        - Scattered cost protection checking
        - Multiple implementations across modules
        """
        return self._state.protection_level in [
            CostProtectionLevel.PROTECTION,
            CostProtectionLevel.EMERGENCY
        ]
    
    def is_emergency_mode_active(self) -> bool:
        """
        CONSOLIDATED: Check if emergency mode is active.
        
        REPLACES:
        - logging_cost_monitor.py: is_emergency_mode_active()
        - Scattered emergency mode checks
        """
        return self._state.emergency_mode
    
    def get_protection_level(self) -> CostProtectionLevel:
        """Get current cost protection level."""
        return self._state.protection_level
    
    def set_cost_protection_state(self, active: bool, emergency_mode: bool = False) -> None:
        """
        CONSOLIDATED: Set cost protection state.
        
        REPLACES:
        - security.py: set_cost_protection_state()
        - All manual cost protection state setting
        """
        with self._lock:
            if emergency_mode:
                self._activate_emergency_mode(EmergencyTrigger.MANUAL, "Manual activation")
            elif active:
                self._state.protection_level = CostProtectionLevel.PROTECTION
            else:
                self._state.protection_level = CostProtectionLevel.MONITORING
                self._state.emergency_mode = False
            
            self._save_state()
            logger.info(f"Cost protection state set: active={active}, emergency={emergency_mode}")
    
    def should_block_request(self, cost_category: CostCategory, 
                           service_type: ServiceType = None) -> bool:
        """
        CONSOLIDATED: Determine if request should be blocked.
        
        REPLACES:
        - http_client.py: _should_block_request()
        - All scattered cost protection checking
        """
        # Critical requests are never blocked
        if cost_category == CostCategory.CRITICAL:
            return False
        
        # Emergency mode blocks everything except critical
        if self._state.emergency_mode:
            self._record_blocked_operation(f"{service_type.value if service_type else 'unknown'}_request")
            return True
        
        # Protection mode blocks optional and low priority
        if self._state.protection_level == CostProtectionLevel.PROTECTION:
            if cost_category in [CostCategory.OPTIONAL, CostCategory.LOW_PRIORITY]:
                self._record_blocked_operation(f"{service_type.value if service_type else 'unknown'}_request")
                return True
        
        return False
    
    def _activate_emergency_mode(self, trigger: EmergencyTrigger, reason: str) -> None:
        """Activate emergency mode with specified trigger and reason."""
        self._state.emergency_mode = True
        self._state.emergency_trigger = trigger
        self._state.emergency_timestamp = time.time()
        self._state.emergency_reason = reason
        self._state.protection_level = CostProtectionLevel.EMERGENCY
        
        # Block all non-critical services
        self._state.blocked_services = {ServiceType.CLOUDWATCH, ServiceType.SSM}
        
        logger.critical(
            f"Emergency mode activated: {trigger.value} - {reason}",
            extra={
                'trigger': trigger.value,
                'reason': reason,
                'timestamp': self._state.emergency_timestamp
            }
        )
        
        # Execute emergency callbacks
        self._execute_callbacks(CostProtectionLevel.EMERGENCY)
        
        # Save state immediately
        self._save_state()
    
    def reset_emergency_mode(self) -> bool:
        """
        CONSOLIDATED: Reset emergency mode.
        
        REPLACES:
        - logging_cost_monitor.py: reset_emergency_mode()
        """
        with self._lock:
            if not self._state.emergency_mode:
                return False
            
            previous_trigger = self._state.emergency_trigger
            previous_reason = self._state.emergency_reason
            
            self._state.emergency_mode = False
            self._state.emergency_trigger = None
            self._state.emergency_timestamp = None
            self._state.emergency_reason = ""
            self._state.protection_level = CostProtectionLevel.MONITORING
            self._state.blocked_services.clear()
            
            logger.info(
                f"Emergency mode reset",
                extra={
                    'previous_trigger': previous_trigger.value if previous_trigger else None,
                    'previous_reason': previous_reason
                }
            )
            
            self._save_state()
            return True
    
    # ===== SERVICE USAGE TRACKING =====
    
    def record_lambda_invocation(self) -> bool:
        """
        CONSOLIDATED: Record Lambda invocation.
        
        REPLACES:
        - logging_cost_monitor.py: record_lambda_invocation()
        """
        with self._lock:
            if self.should_block_request(CostCategory.NORMAL, ServiceType.LAMBDA):
                return False
            
            self._state.usage.lambda_invocations += 1
            self._state.usage.last_updated = time.time()
            
            # Check limits
            self._check_service_limits(ServiceType.LAMBDA)
            
            if self._state.auto_save and self._state.usage.lambda_invocations % 100 == 0:
                self._save_state()
            
            return True
    
    def record_cloudwatch_api_call(self, count: int = 1) -> bool:
        """
        CONSOLIDATED: Record CloudWatch API call.
        
        REPLACES:
        - logging_cost_monitor.py: record_cloudwatch_api_call()
        """
        with self._lock:
            if self.should_block_request(CostCategory.OPTIONAL, ServiceType.CLOUDWATCH):
                return False
            
            self._state.usage.cloudwatch_api_calls += count
            self._state.usage.last_updated = time.time()
            
            # Check limits
            self._check_service_limits(ServiceType.CLOUDWATCH)
            
            if self._state.auto_save and self._state.usage.cloudwatch_api_calls % 50 == 0:
                self._save_state()
            
            return True
    
    def record_ssm_api_call(self, count: int = 1) -> bool:
        """
        CONSOLIDATED: Record SSM API call.
        
        REPLACES:
        - logging_cost_monitor.py: record_ssm_api_call()
        """
        with self._lock:
            if self.should_block_request(CostCategory.NORMAL, ServiceType.SSM):
                return False
            
            self._state.usage.ssm_api_calls += count
            self._state.usage.last_updated = time.time()
            
            # Check limits
            self._check_service_limits(ServiceType.SSM)
            
            if self._state.auto_save and self._state.usage.ssm_api_calls % 10 == 0:
                self._save_state()
            
            return True
    
    def record_cloudwatch_logs_bytes(self, bytes_written: int) -> bool:
        """
        CONSOLIDATED: Record CloudWatch Logs bytes.
        
        REPLACES:
        - logging_cost_monitor.py: record_cloudwatch_logs_bytes()
        """
        with self._lock:
            if self.should_block_request(CostCategory.OPTIONAL, ServiceType.CLOUDWATCH_LOGS):
                return False
            
            self._state.usage.cloudwatch_logs_bytes += bytes_written
            self._state.usage.last_updated = time.time()
            
            # Check limits
            logs_gb = self._state.usage.cloudwatch_logs_bytes / (1024**3)
            if logs_gb >= self._state.limits.cloudwatch_logs_gb_monthly:
                self._activate_emergency_mode(
                    EmergencyTrigger.CLOUDWATCH_LIMIT,
                    f"CloudWatch Logs limit exceeded: {logs_gb:.2f}GB"
                )
                return False
            
            return True
    
    def can_use_service(self, service_name: str) -> bool:
        """
        CONSOLIDATED: Check if service can be used.
        
        REPLACES:
        - logging_cost_monitor.py: can_use_service()
        """
        try:
            service_type = ServiceType(service_name.lower())
        except ValueError:
            # Unknown service, allow by default
            return True
        
        # Check if service is blocked
        if service_type in self._state.blocked_services:
            return False
        
        # Check emergency mode
        if self._state.emergency_mode:
            return False
        
        # Check protection level
        if self._state.protection_level == CostProtectionLevel.PROTECTION:
            # Allow critical services in protection mode
            if service_type == ServiceType.LAMBDA:
                return True
            # Block optional services
            return False
        
        return True
    
    def _check_service_limits(self, service_type: ServiceType) -> None:
        """Check if service limits are approaching and update protection level."""
        usage_percent = self._get_service_usage_percent(service_type)
        
        if usage_percent >= self._state.limits.emergency_threshold_percent:
            trigger_map = {
                ServiceType.LAMBDA: EmergencyTrigger.LAMBDA_LIMIT,
                ServiceType.CLOUDWATCH: EmergencyTrigger.CLOUDWATCH_LIMIT,
                ServiceType.SSM: EmergencyTrigger.SSM_LIMIT,
            }
            
            trigger = trigger_map.get(service_type, EmergencyTrigger.COST_SPIKE)
            self._activate_emergency_mode(
                trigger,
                f"{service_type.value} usage exceeded {usage_percent:.1f}% of monthly limit"
            )
        
        elif usage_percent >= self._state.limits.critical_threshold_percent:
            if self._state.protection_level != CostProtectionLevel.EMERGENCY:
                self._state.protection_level = CostProtectionLevel.PROTECTION
                self._execute_callbacks(CostProtectionLevel.PROTECTION)
        
        elif usage_percent >= self._state.limits.warning_threshold_percent:
            if self._state.protection_level == CostProtectionLevel.MONITORING:
                self._state.protection_level = CostProtectionLevel.WARNING
                self._execute_callbacks(CostProtectionLevel.WARNING)
    
    def _get_service_usage_percent(self, service_type: ServiceType) -> float:
        """Get current usage percentage for a service."""
        usage = self._state.usage
        limits = self._state.limits
        
        if service_type == ServiceType.LAMBDA:
            return (usage.lambda_invocations / limits.lambda_invocations_monthly) * 100
        elif service_type == ServiceType.CLOUDWATCH:
            return (usage.cloudwatch_api_calls / limits.cloudwatch_api_calls_monthly) * 100
        elif service_type == ServiceType.SSM:
            return (usage.ssm_api_calls / limits.ssm_api_calls_monthly) * 100
        elif service_type == ServiceType.CLOUDWATCH_LOGS:
            logs_gb = usage.cloudwatch_logs_bytes / (1024**3)
            return (logs_gb / limits.cloudwatch_logs_gb_monthly) * 100
        
        return 0.0
    
    def _record_blocked_operation(self, operation_name: str) -> None:
        """Record a blocked operation for monitoring."""
        self._state.blocked_operations[operation_name] = (
            self._state.blocked_operations.get(operation_name, 0) + 1
        )

# ===== SECTION 3: CALLBACK SYSTEM AND STATE PERSISTENCE =====

    # ===== CALLBACK SYSTEM =====
    
    def register_protection_callback(self, level: CostProtectionLevel, 
                                   callback: Callable[[CostProtectionState], None],
                                   name: str) -> None:
        """Register callback for cost protection level changes."""
        with self._lock:
            self._callbacks[level].append({
                'callback': callback,
                'name': name
            })
        logger.debug(f"Registered cost protection callback '{name}' for {level.value}")
    
    def _execute_callbacks(self, level: CostProtectionLevel) -> None:
        """Execute callbacks for protection level."""
        callbacks = self._callbacks.get(level, [])
        
        for callback_info in callbacks:
            try:
                callback_info['callback'](self._state)
                logger.debug(f"Executed callback '{callback_info['name']}' for {level.value}")
            except Exception as e:
                logger.error(f"Callback '{callback_info['name']}' failed: {e}")
    
    # ===== STATE PERSISTENCE =====
    
    def _save_state(self) -> None:
        """Save cost protection state to file."""
        if not self._state.auto_save:
            return
        
        try:
            state_data = {
                'protection_level': self._state.protection_level.value,
                'emergency_mode': self._state.emergency_mode,
                'emergency_trigger': self._state.emergency_trigger.value if self._state.emergency_trigger else None,
                'emergency_timestamp': self._state.emergency_timestamp,
                'emergency_reason': self._state.emergency_reason,
                'usage': self._state.usage.to_dict(),
                'limits': {
                    'lambda_invocations_monthly': self._state.limits.lambda_invocations_monthly,
                    'cloudwatch_api_calls_monthly': self._state.limits.cloudwatch_api_calls_monthly,
                    'ssm_api_calls_monthly': self._state.limits.ssm_api_calls_monthly,
                    'cloudwatch_logs_gb_monthly': self._state.limits.cloudwatch_logs_gb_monthly,
                    'warning_threshold_percent': self._state.limits.warning_threshold_percent,
                    'critical_threshold_percent': self._state.limits.critical_threshold_percent,
                    'emergency_threshold_percent': self._state.limits.emergency_threshold_percent
                },
                'blocked_operations': dict(self._state.blocked_operations),
                'blocked_services': [s.value for s in self._state.blocked_services],
                'saved_at': time.time()
            }
            
            with open(self._state.state_file, 'w') as f:
                json.dump(state_data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to save cost protection state: {e}")
    
    def _load_state(self) -> None:
        """Load cost protection state from file."""
        try:
            if not os.path.exists(self._state.state_file):
                return
            
            with open(self._state.state_file, 'r') as f:
                state_data = json.load(f)
            
            # Load protection level
            try:
                self._state.protection_level = CostProtectionLevel(
                    state_data.get('protection_level', 'monitoring')
                )
            except ValueError:
                self._state.protection_level = CostProtectionLevel.MONITORING
            
            # Load emergency state
            self._state.emergency_mode = state_data.get('emergency_mode', False)
            
            if state_data.get('emergency_trigger'):
                try:
                    self._state.emergency_trigger = EmergencyTrigger(state_data['emergency_trigger'])
                except ValueError:
                    self._state.emergency_trigger = None
            
            self._state.emergency_timestamp = state_data.get('emergency_timestamp')
            self._state.emergency_reason = state_data.get('emergency_reason', '')
            
            # Load usage data
            if 'usage' in state_data:
                self._state.usage = UsageMetrics.from_dict(state_data['usage'])
            
            # Load limits if customized
            if 'limits' in state_data:
                limits_data = state_data['limits']
                self._state.limits.lambda_invocations_monthly = limits_data.get(
                    'lambda_invocations_monthly', self._state.limits.lambda_invocations_monthly
                )
                self._state.limits.cloudwatch_api_calls_monthly = limits_data.get(
                    'cloudwatch_api_calls_monthly', self._state.limits.cloudwatch_api_calls_monthly
                )
                self._state.limits.ssm_api_calls_monthly = limits_data.get(
                    'ssm_api_calls_monthly', self._state.limits.ssm_api_calls_monthly
                )
                self._state.limits.cloudwatch_logs_gb_monthly = limits_data.get(
                    'cloudwatch_logs_gb_monthly', self._state.limits.cloudwatch_logs_gb_monthly
                )
            
            # Load blocked operations
            if 'blocked_operations' in state_data:
                self._state.blocked_operations = state_data['blocked_operations']
            
            # Load blocked services
            if 'blocked_services' in state_data:
                self._state.blocked_services = {
                    ServiceType(s) for s in state_data['blocked_services']
                    if s in [st.value for st in ServiceType]
                }
            
            logger.debug(f"Loaded cost protection state: {self._state.protection_level.value}")
            
        except Exception as e:
            logger.error(f"Failed to load cost protection state: {e}")
            # Reset to default state on load failure
            self._state = CostProtectionState()
    
    # ===== MONTHLY RESET LOGIC =====
    
    def _check_monthly_reset(self) -> None:
        """
        CONSOLIDATED: Check if monthly usage reset is needed.
        
        REPLACES:
        - logging_cost_monitor.py: _check_monthly_reset()
        """
        current_time = time.time()
        current_month = datetime.fromtimestamp(current_time, tz=timezone.utc).replace(
            day=1, hour=0, minute=0, second=0, microsecond=0
        )
        current_month_timestamp = current_month.timestamp()
        
        if self._state.usage.last_reset < current_month_timestamp:
            logger.info("Performing monthly cost protection reset")
            
            old_usage = self._state.usage.to_dict()
            
            # Reset usage metrics
            self._state.usage = UsageMetrics(last_reset=current_time)
            
            # Reset protection level but keep emergency mode if still valid
            if self._state.emergency_mode:
                # Check if emergency was from current month
                if (self._state.emergency_timestamp and 
                    self._state.emergency_timestamp < current_month_timestamp):
                    self.reset_emergency_mode()
            else:
                self._state.protection_level = CostProtectionLevel.MONITORING
            
            # Clear blocked operations history
            self._state.blocked_operations.clear()
            
            # Save new state
            self._save_state()
            
            logger.info(
                "Monthly cost protection reset completed",
                extra={
                    'previous_usage': old_usage,
                    'reset_timestamp': current_time,
                    'new_protection_level': self._state.protection_level.value
                }
            )
    
    # ===== MONITORING AND REPORTING =====
    
    def get_usage_summary(self) -> Dict[str, Any]:
        """
        CONSOLIDATED: Get comprehensive usage summary.
        
        REPLACES:
        - logging_cost_monitor.py: get_usage_summary()
        """
        with self._lock:
            current_time = time.time()
            
            # Calculate usage percentages
            services = {}
            for service_type in ServiceType:
                usage_percent = self._get_service_usage_percent(service_type)
                limit_info = self._get_service_limit_info(service_type)
                
                services[service_type.value] = {
                    'usage_percent': round(usage_percent, 2),
                    'current_usage': limit_info['current'],
                    'monthly_limit': limit_info['limit'],
                    'unit': limit_info['unit'],
                    'status': self._get_service_status(usage_percent)
                }
            
            return {
                'protection_level': self._state.protection_level.value,
                'emergency_mode': self._state.emergency_mode,
                'emergency_reason': self._state.emergency_reason,
                'services': services,
                'blocked_operations': dict(self._state.blocked_operations),
                'blocked_services': [s.value for s in self._state.blocked_services],
                'usage_period': {
                    'start_timestamp': self._state.usage.last_reset,
                    'current_timestamp': current_time,
                    'days_elapsed': (current_time - self._state.usage.last_reset) / 86400
                },
                'thresholds': {
                    'warning_percent': self._state.limits.warning_threshold_percent,
                    'critical_percent': self._state.limits.critical_threshold_percent,
                    'emergency_percent': self._state.limits.emergency_threshold_percent
                }
            }
    
    def _get_service_limit_info(self, service_type: ServiceType) -> Dict[str, Any]:
        """Get service limit information."""
        usage = self._state.usage
        limits = self._state.limits
        
        if service_type == ServiceType.LAMBDA:
            return {
                'current': usage.lambda_invocations,
                'limit': limits.lambda_invocations_monthly,
                'unit': 'invocations'
            }
        elif service_type == ServiceType.CLOUDWATCH:
            return {
                'current': usage.cloudwatch_api_calls,
                'limit': limits.cloudwatch_api_calls_monthly,
                'unit': 'api_calls'
            }
        elif service_type == ServiceType.SSM:
            return {
                'current': usage.ssm_api_calls,
                'limit': limits.ssm_api_calls_monthly,
                'unit': 'api_calls'
            }
        elif service_type == ServiceType.CLOUDWATCH_LOGS:
            return {
                'current': usage.cloudwatch_logs_bytes / (1024**3),
                'limit': limits.cloudwatch_logs_gb_monthly,
                'unit': 'GB'
            }
        
        return {'current': 0, 'limit': 0, 'unit': 'unknown'}
    
    def _get_service_status(self, usage_percent: float) -> str:
        """Get service status based on usage percentage."""
        if usage_percent >= self._state.limits.emergency_threshold_percent:
            return 'emergency'
        elif usage_percent >= self._state.limits.critical_threshold_percent:
            return 'critical'
        elif usage_percent >= self._state.limits.warning_threshold_percent:
            return 'warning'
        else:
            return 'normal'
    
    def generate_cost_report(self) -> str:
        """
        CONSOLIDATED: Generate detailed cost report.
        
        REPLACES:
        - Scattered cost reporting functionality
        """
        summary = self.get_usage_summary()
        
        report_lines = [
            "=" * 60,
            "AWS LAMBDA COST PROTECTION REPORT",
            f"Generated: {datetime.now().isoformat()}",
            f"Protection Level: {summary['protection_level'].upper()}",
            "=" * 60,
            ""
        ]
        
        # Emergency status
        if summary['emergency_mode']:
            report_lines.extend([
                "🚨 EMERGENCY MODE ACTIVE 🚨",
                f"Reason: {summary['emergency_reason']}",
                ""
            ])
        
        # Service usage
        report_lines.append("SERVICE USAGE:")
        for service_name, stats in summary['services'].items():
            status_emoji = {
                'normal': '✅',
                'warning': '⚠️',
                'critical': '🔶',
                'emergency': '🚨'
            }.get(stats['status'], '❓')
            
            report_lines.append(
                f"  {status_emoji} {service_name.upper()}: {stats['usage_percent']}% "
                f"({stats['current_usage']:.0f}/{stats['monthly_limit']:.0f} {stats['unit']})"
            )
        
        # Blocked operations
        if summary['blocked_operations']:
            report_lines.extend([
                "",
                "BLOCKED OPERATIONS:",
            ])
            for operation, count in summary['blocked_operations'].items():
                report_lines.append(f"  - {operation}: {count} times")
        
        # Recommendations
        recommendations = self._generate_recommendations(summary)
        if recommendations:
            report_lines.extend([
                "",
                "RECOMMENDATIONS:",
            ])
            for rec in recommendations:
                report_lines.append(f"  • {rec}")
        
        report_lines.append("=" * 60)
        
        return "\n".join(report_lines)
    
    def _generate_recommendations(self, summary: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on current usage."""
        recommendations = []
        
        for service_name, stats in summary['services'].items():
            usage_percent = stats['usage_percent']
            
            if usage_percent >= 80:
                recommendations.append(
                    f"Reduce {service_name} usage - currently at {usage_percent}%"
                )
            elif usage_percent >= 60:
                recommendations.append(
                    f"Monitor {service_name} usage - approaching warning threshold"
                )
        
        if summary['emergency_mode']:
            recommendations.append("Reset emergency mode if issue is resolved")
        
        if summary['blocked_operations']:
            recommendations.append("Review blocked operations and optimize request patterns")
        
        return recommendations
    
    def cleanup(self) -> Dict[str, Any]:
        """Cleanup cost protection manager."""
        cleanup_stats = {
            'final_usage_summary': self.get_usage_summary(),
            'state_saved': False
        }
        
        try:
            # Final state save
            self._save_state()
            cleanup_stats['state_saved'] = True
            
            # Clear callbacks
            with self._lock:
                self._callbacks.clear()
            
            logger.debug("Cost protection manager cleanup completed")
            
        except Exception as e:
            cleanup_stats['cleanup_error'] = str(e)
            logger.error(f"Cost protection manager cleanup error: {e}")
        
        return cleanup_stats

# ===== SECTION 4: GLOBAL INSTANCE MANAGEMENT =====

# Global unified cost protection manager instance
_cost_protection_manager: Optional[ConsolidatedCostProtectionManager] = None
_cost_protection_lock = threading.Lock()

def get_cost_protection_manager() -> ConsolidatedCostProtectionManager:
    """Get or create the global cost protection manager."""
    global _cost_protection_manager
    
    if _cost_protection_manager is None:
        with _cost_protection_lock:
            if _cost_protection_manager is None:
                _cost_protection_manager = ConsolidatedCostProtectionManager()
                logger.debug("Global cost protection manager created")
    
    return _cost_protection_manager

def reset_cost_protection_manager() -> None:
    """Reset the global cost protection manager."""
    global _cost_protection_manager
    with _cost_protection_lock:
        if _cost_protection_manager:
            _cost_protection_manager.cleanup()
        _cost_protection_manager = None

# ===== CONVENIENCE FUNCTIONS (REPLACE ALL SCATTERED PATTERNS) =====

def is_cost_protection_active() -> bool:
    """
    CONSOLIDATED: Check if cost protection is active.
    
    REPLACES ALL:
    - try/except ImportError patterns across all modules
    - from logging import is_cost_protection_active (4+ locations)
    - Scattered cost protection checking
    """
    return get_cost_protection_manager().is_cost_protection_active()

def is_emergency_mode_active() -> bool:
    """
    CONSOLIDATED: Check if emergency mode is active.
    
    REPLACES:
    - logging_cost_monitor.py: is_emergency_mode_active()
    - Scattered emergency mode checks
    """
    return get_cost_protection_manager().is_emergency_mode_active()

def should_block_request(cost_category: CostCategory, service_type: ServiceType = None) -> bool:
    """
    CONSOLIDATED: Check if request should be blocked by cost protection.
    
    REPLACES:
    - http_client.py: _should_block_request()
    - All scattered cost protection request checking
    """
    return get_cost_protection_manager().should_block_request(cost_category, service_type)

def set_cost_protection_state(active: bool, emergency_mode: bool = False) -> None:
    """
    CONSOLIDATED: Set cost protection state.
    
    REPLACES:
    - security.py: set_cost_protection_state()
    - All manual cost protection state setting
    """
    get_cost_protection_manager().set_cost_protection_state(active, emergency_mode)

def record_lambda_invocation() -> bool:
    """
    CONSOLIDATED: Record Lambda invocation for cost tracking.
    
    REPLACES:
    - logging_cost_monitor.py: record_lambda_invocation()
    """
    return get_cost_protection_manager().record_lambda_invocation()

def record_cloudwatch_api_call(count: int = 1) -> bool:
    """
    CONSOLIDATED: Record CloudWatch API call for cost tracking.
    
    REPLACES:
    - logging_cost_monitor.py: record_cloudwatch_api_call()
    """
    return get_cost_protection_manager().record_cloudwatch_api_call(count)

def record_ssm_api_call(count: int = 1) -> bool:
    """
    CONSOLIDATED: Record SSM API call for cost tracking.
    
    REPLACES:
    - logging_cost_monitor.py: record_ssm_api_call()
    """
    return get_cost_protection_manager().record_ssm_api_call(count)

def record_cloudwatch_logs_bytes(bytes_written: int) -> bool:
    """
    CONSOLIDATED: Record CloudWatch Logs bytes for cost tracking.
    
    REPLACES:
    - logging_cost_monitor.py: record_cloudwatch_logs_bytes()
    """
    return get_cost_protection_manager().record_cloudwatch_logs_bytes(bytes_written)

def can_use_service(service_name: str) -> bool:
    """
    CONSOLIDATED: Check if service can be used under current cost constraints.
    
    REPLACES:
    - logging_cost_monitor.py: can_use_service()
    """
    return get_cost_protection_manager().can_use_service(service_name)

def get_usage_summary() -> Dict[str, Any]:
    """
    CONSOLIDATED: Get current usage summary.
    
    REPLACES:
    - logging_cost_monitor.py: get_usage_summary()
    """
    return get_cost_protection_manager().get_usage_summary()

def generate_cost_report() -> str:
    """
    CONSOLIDATED: Generate detailed cost report.
    
    REPLACES:
    - Scattered cost reporting functionality
    """
    return get_cost_protection_manager().generate_cost_report()

def reset_emergency_mode() -> bool:
    """
    CONSOLIDATED: Reset emergency mode.
    
    REPLACES:
    - logging_cost_monitor.py: reset_emergency_mode()
    """
    return get_cost_protection_manager().reset_emergency_mode()

def register_protection_callback(level: CostProtectionLevel,
                               callback: Callable[[CostProtectionState], None],
                               name: str) -> None:
    """
    NEW: Register callback for cost protection level changes.
    """
    get_cost_protection_manager().register_protection_callback(level, callback, name)

def get_protection_level() -> CostProtectionLevel:
    """
    NEW: Get current cost protection level.
    """
    return get_cost_protection_manager().get_protection_level()

# ===== BACKWARD COMPATIBILITY FUNCTIONS =====

# These maintain exact compatibility with existing scattered patterns

def check_cost_protection() -> bool:
    """
    BACKWARD COMPATIBILITY: For modules that check cost protection differently.
    """
    return is_cost_protection_active()

def is_cost_protection_enabled() -> bool:
    """
    BACKWARD COMPATIBILITY: Alternative naming pattern.
    """
    return is_cost_protection_active()

def cost_protection_active() -> bool:
    """
    BACKWARD COMPATIBILITY: Short form used in some modules.
    """
    return is_cost_protection_active()

# ===== MODULE EXPORTS =====

__all__ = [
    # Main classes
    'ConsolidatedCostProtectionManager',
    'CostProtectionState',
    'UsageMetrics',
    'CostLimits',
    
    # Enums
    'CostCategory',
    'CostProtectionLevel',
    'ServiceType', 
    'EmergencyTrigger',
    
    # Global access
    'get_cost_protection_manager',
    'reset_cost_protection_manager',
    
    # CONSOLIDATED FUNCTIONS (replace all scattered patterns)
    'is_cost_protection_active',      # Replaces try/except import patterns
    'is_emergency_mode_active',       # Replaces scattered emergency checks
    'should_block_request',           # Replaces _should_block_request()
    'set_cost_protection_state',      # Replaces security.py function
    
    # Usage tracking (replaces logging_cost_monitor.py functions)
    'record_lambda_invocation',
    'record_cloudwatch_api_call',
    'record_ssm_api_call',
    'record_cloudwatch_logs_bytes',
    'can_use_service',
    'get_usage_summary',
    'reset_emergency_mode',
    
    # Monitoring and reporting
    'generate_cost_report',
    'get_protection_level',
    'register_protection_callback',
    
    # Backward compatibility
    'check_cost_protection',
    'is_cost_protection_enabled',
    'cost_protection_active'
]

# EOF
