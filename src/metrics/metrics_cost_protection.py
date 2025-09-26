"""
metrics_cost_protection.py - FIXED: Circular Import Eliminated
Version: 2025.09.21.02
Description: Cost protection metrics with circular import ELIMINATED

CRITICAL FIX APPLIED:
- ❌ REMOVED: from logging import manage_logs (CIRCULAR IMPORT VIOLATION)
- ✅ ADDED: Proper internal logging using standard library only
- ✅ ELIMINATED: Circular dependency metrics_cost_protection → logging → metrics
- ✅ MAINTAINED: All cost protection functionality with safe logging

ELIMINATES VIOLATIONS:
- Direct logging primary gateway import (REMOVED - was causing circular import)
- Circular import chain through logging.py (ELIMINATED)
- Gateway hierarchy violations (CORRECTED)

USES PROPER SECONDARY ARCHITECTURE:
- utility.py:get_cost_protection() (DESIGNATED GATEWAY ONLY)
- Standard library logging for internal operations only
- No direct access to primary gateway files
- All external logging delegated to metrics.py primary gateway

INTERNAL MODULE - External files should access through metrics.py gateway
"""

import time
import threading
import logging
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, field
from enum import Enum

# CORRECTED: Use designated singleton gateway only (no circular import)
from utility import get_cost_protection

# SAFE: Use standard library logger for internal operations only
# This does NOT create circular imports because it's standard library
_internal_logger = logging.getLogger(__name__)

# ===== SECTION 1: COST PROTECTION METRICS ENUMS =====

class CostCategory(Enum):
    """Categories of AWS costs being tracked."""
    LAMBDA_INVOCATIONS = "lambda_invocations"
    LAMBDA_DURATION = "lambda_duration"
    LAMBDA_MEMORY = "lambda_memory"
    SSM_API_CALLS = "ssm_api_calls"
    CLOUDWATCH_API_CALLS = "cloudwatch_api_calls"
    CLOUDWATCH_LOGS = "cloudwatch_logs"
    CLOUDWATCH_METRICS = "cloudwatch_metrics"
    DATA_TRANSFER = "data_transfer"
    STORAGE = "storage"
    API_GATEWAY = "api_gateway"

class ProtectionLevel(Enum):
    """Cost protection levels."""
    DISABLED = "disabled"
    MONITORING = "monitoring"
    WARNING = "warning"
    BLOCKING = "blocking"
    EMERGENCY = "emergency"

class CostThresholdType(Enum):
    """Types of cost thresholds."""
    HOURLY = "hourly"
    DAILY = "daily"
    MONTHLY = "monthly"
    ABSOLUTE = "absolute"
    PERCENTAGE = "percentage"

class CostMetricType(Enum):
    """Types of cost metrics."""
    CURRENT_USAGE = "current_usage"
    PROJECTED_USAGE = "projected_usage"
    THRESHOLD_COMPARISON = "threshold_comparison"
    RATE_ANALYSIS = "rate_analysis"
    TREND_ANALYSIS = "trend_analysis"

# ===== SECTION 2: COST METRICS DATA CLASSES =====

@dataclass
class CostMetric:
    """Individual cost metric with enhanced tracking."""
    category: CostCategory
    amount: float
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
    threshold_type: CostThresholdType = CostThresholdType.ABSOLUTE
    protection_level: ProtectionLevel = ProtectionLevel.MONITORING
    metric_type: CostMetricType = CostMetricType.CURRENT_USAGE

@dataclass
class CostProtectionMetrics:
    """Comprehensive cost protection metrics."""
    total_cost_estimate: float = 0.0
    lambda_invocations: int = 0
    lambda_duration_ms: float = 0.0
    lambda_memory_usage_mb: float = 0.0
    api_calls_count: int = 0
    data_transfer_bytes: int = 0
    protection_level: ProtectionLevel = ProtectionLevel.MONITORING
    last_updated: float = field(default_factory=time.time)
    metrics_by_category: Dict[str, List[CostMetric]] = field(default_factory=dict)
    thresholds: Dict[str, float] = field(default_factory=dict)

# ===== SECTION 3: INTERNAL COST METRICS MANAGER =====

class _CostMetricsManager:
    """Internal cost metrics management - accessed only through utility gateway."""
    
    def __init__(self):
        self._lock = threading.Lock()
        self._metrics = CostProtectionMetrics()
        self._initialized = False
        
    def initialize(self) -> bool:
        """Initialize cost metrics tracking."""
        with self._lock:
            if self._initialized:
                return True
                
            try:
                # Set default thresholds for free tier
                self._metrics.thresholds = {
                    'lambda_invocations_monthly': 1000000,  # 1M free tier
                    'lambda_duration_monthly_ms': 400000000,  # 400k GB-seconds
                    'lambda_memory_limit_mb': 128,  # Our constraint
                    'api_calls_hourly': 100,  # Conservative limit
                    'data_transfer_monthly_gb': 1.0  # 1GB free tier
                }
                
                self._initialized = True
                return True
                
            except Exception as e:
                # SAFE: Internal logging only - no circular import
                _internal_logger.error(f"Failed to initialize cost metrics: {e}")
                return False
    
    def record_metric(self, category: CostCategory, amount: float, 
                     metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Record a cost metric."""
        if not self._initialized:
            self.initialize()
            
        try:
            with self._lock:
                metric = CostMetric(
                    category=category,
                    amount=amount,
                    metadata=metadata or {}
                )
                
                # Add to category collection
                category_key = category.value
                if category_key not in self._metrics.metrics_by_category:
                    self._metrics.metrics_by_category[category_key] = []
                
                self._metrics.metrics_by_category[category_key].append(metric)
                
                # Update aggregate counters
                if category == CostCategory.LAMBDA_INVOCATIONS:
                    self._metrics.lambda_invocations += int(amount)
                elif category == CostCategory.LAMBDA_DURATION:
                    self._metrics.lambda_duration_ms += amount
                elif category == CostCategory.LAMBDA_MEMORY:
                    self._metrics.lambda_memory_usage_mb = max(self._metrics.lambda_memory_usage_mb, amount)
                elif category in [CostCategory.SSM_API_CALLS, CostCategory.CLOUDWATCH_API_CALLS]:
                    self._metrics.api_calls_count += int(amount)
                elif category == CostCategory.DATA_TRANSFER:
                    self._metrics.data_transfer_bytes += int(amount)
                
                # Update cost estimate
                self._update_cost_estimate()
                self._metrics.last_updated = time.time()
                
                return True
                
        except Exception as e:
            # SAFE: Internal logging only - no circular import
            _internal_logger.error(f"Failed to record cost metric: {e}")
            return False
    
    def _update_cost_estimate(self) -> None:
        """Update total cost estimate based on current metrics."""
        try:
            # AWS Lambda pricing (approximate, US East)
            cost = 0.0
            
            # Lambda invocation cost: $0.0000002 per request
            cost += self._metrics.lambda_invocations * 0.0000002
            
            # Lambda duration cost: $0.0000166667 per GB-second
            # Convert MB-ms to GB-seconds: (MB * ms) / (1024 * 1000)
            gb_seconds = (self._metrics.lambda_memory_usage_mb * self._metrics.lambda_duration_ms) / (1024 * 1000)
            cost += gb_seconds * 0.0000166667
            
            # API calls (conservative estimate): $0.0001 per call
            cost += self._metrics.api_calls_count * 0.0001
            
            # Data transfer (approximate): $0.09 per GB
            gb_transfer = self._metrics.data_transfer_bytes / (1024 * 1024 * 1024)
            cost += gb_transfer * 0.09
            
            self._metrics.total_cost_estimate = cost
            
        except Exception as e:
            # SAFE: Internal logging only - no circular import
            _internal_logger.warning(f"Failed to update cost estimate: {e}")
            self._metrics.total_cost_estimate = 0.0
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current cost protection metrics."""
        if not self._initialized:
            self.initialize()
            
        with self._lock:
            return {
                'total_cost_estimate': self._metrics.total_cost_estimate,
                'lambda_invocations': self._metrics.lambda_invocations,
                'lambda_duration_ms': self._metrics.lambda_duration_ms,
                'lambda_memory_usage_mb': self._metrics.lambda_memory_usage_mb,
                'api_calls_count': self._metrics.api_calls_count,
                'data_transfer_bytes': self._metrics.data_transfer_bytes,
                'protection_level': self._metrics.protection_level.value,
                'last_updated': self._metrics.last_updated,
                'metrics_count_by_category': {
                    category: len(metrics) 
                    for category, metrics in self._metrics.metrics_by_category.items()
                },
                'thresholds': self._metrics.thresholds.copy()
            }
    
    def reset_metrics(self) -> bool:
        """Reset all cost metrics."""
        try:
            with self._lock:
                self._metrics = CostProtectionMetrics()
                self._initialized = False
                return True
        except Exception as e:
            # SAFE: Internal logging only - no circular import
            _internal_logger.error(f"Failed to reset cost metrics: {e}")
            return False

# Global instance - internal to this module only
_cost_metrics_manager = None
_manager_lock = threading.Lock()

def _get_cost_metrics_manager() -> _CostMetricsManager:
    """Get the internal cost metrics manager."""
    global _cost_metrics_manager
    
    with _manager_lock:
        if _cost_metrics_manager is None:
            _cost_metrics_manager = _CostMetricsManager()
        return _cost_metrics_manager

# ===== SECTION 4: PUBLIC INTERFACE FUNCTIONS =====
# These functions are called by metrics.py primary gateway

def get_cost_protection_metrics(max_retries: int = 3) -> Dict[str, Any]:
    """
    FIXED: Get cost protection metrics without circular import.
    Uses utility.py designated singleton gateway and internal metrics manager.
    """
    for attempt in range(max_retries + 1):
        try:
            # Get cost protection instance through designated gateway
            cost_protection = get_cost_protection()
            
            if cost_protection is not None:
                # Try to get metrics from cost protection instance
                if hasattr(cost_protection, 'get_metrics'):
                    try:
                        cost_metrics = cost_protection.get_metrics()
                        
                        # Enhance with internal metrics
                        internal_metrics = _get_cost_metrics_manager().get_metrics()
                        
                        return {
                            'status': 'success',
                            'cost_protection_metrics': cost_metrics,
                            'internal_metrics': internal_metrics,
                            'combined_estimate': cost_metrics.get('total_cost', 0.0) + internal_metrics.get('total_cost_estimate', 0.0),
                            'timestamp': time.time(),
                            'retrieval_attempt': attempt + 1
                        }
                        
                    except Exception as e:
                        # SAFE: Internal logging only - no circular import
                        _internal_logger.warning(f"Cost protection metrics method failed: {e}")
                        # Fall through to use internal metrics only
                else:
                    # SAFE: Internal logging only - no circular import
                    _internal_logger.info("Cost protection instance doesn't have metrics method")
                    # Fall through to use internal metrics only
                
                # Return internal metrics with available methods
                internal_metrics = _get_cost_metrics_manager().get_metrics()
                return {
                    'status': 'limited_functionality',
                    'internal_metrics': internal_metrics,
                    'protection_active': hasattr(cost_protection, 'is_cost_protection_active'),
                    'methods_available': [method for method in dir(cost_protection) if not method.startswith('_')],
                    'timestamp': time.time(),
                    'retrieval_attempt': attempt + 1
                }
                
        except ImportError as e:
            # SAFE: Internal logging only - no circular import
            _internal_logger.error(f"Import error getting cost protection: {e}")
            if attempt < max_retries:
                time.sleep(0.1 * (attempt + 1))  # Exponential backoff
                continue
            
            # Return fallback metrics
            internal_metrics = _get_cost_metrics_manager().get_metrics()
            return {
                'status': 'import_error',
                'error': str(e),
                'internal_metrics': internal_metrics,
                'fallback_metrics': {
                    'lambda_invocations': internal_metrics.get('lambda_invocations', 0),
                    'estimated_cost': internal_metrics.get('total_cost_estimate', 0.0),
                    'protection_active': False
                },
                'timestamp': time.time(),
                'total_attempts': attempt + 1
            }
            
        except Exception as e:
            # SAFE: Internal logging only - no circular import
            _internal_logger.error(f"Error getting cost protection metrics: {e}")
            if attempt < max_retries:
                time.sleep(0.1 * (attempt + 1))  # Exponential backoff
                continue
            
            # Return fallback metrics
            internal_metrics = _get_cost_metrics_manager().get_metrics()
            return {
                'status': 'error',
                'error': str(e),
                'internal_metrics': internal_metrics,
                'fallback_metrics': {
                    'lambda_invocations': internal_metrics.get('lambda_invocations', 0),
                    'estimated_cost': internal_metrics.get('total_cost_estimate', 0.0),
                    'protection_active': False
                },
                'timestamp': time.time(),
                'total_attempts': attempt + 1
            }
    
    # This should never be reached, but just in case
    internal_metrics = _get_cost_metrics_manager().get_metrics()
    return {
        'status': 'max_retries_exceeded',
        'internal_metrics': internal_metrics,
        'timestamp': time.time(),
        'total_attempts': max_retries + 1
    }

def record_cost_metric(category: CostCategory, amount: float, metadata: Optional[Dict[str, Any]] = None) -> bool:
    """
    FIXED: Record cost metric without circular import.
    Uses utility.py designated singleton gateway and internal metrics manager.
    """
    try:
        # Record in internal metrics manager
        internal_success = _get_cost_metrics_manager().record_metric(category, amount, metadata)
        
        # Try to record through cost protection instance
        try:
            cost_protection = get_cost_protection()
            if cost_protection and hasattr(cost_protection, 'record_usage'):
                cost_protection.record_usage(category.value, amount, metadata)
        except Exception as e:
            # SAFE: Internal logging only - no circular import
            _internal_logger.warning(f"Failed to record through cost protection: {e}")
        
        return internal_success
        
    except Exception as e:
        # SAFE: Internal logging only - no circular import
        _internal_logger.error(f"Failed to record cost metric: {e}")
        return False

def is_cost_protection_active() -> bool:
    """
    FIXED: Check if cost protection is active without circular import.
    Uses utility.py designated singleton gateway.
    """
    try:
        cost_protection = get_cost_protection()
        if cost_protection and hasattr(cost_protection, 'is_active'):
            return cost_protection.is_active()
        elif cost_protection and hasattr(cost_protection, 'is_cost_protection_active'):
            return cost_protection.is_cost_protection_active()
        else:
            # Default to monitoring level
            return True
    except Exception as e:
        # SAFE: Internal logging only - no circular import
        _internal_logger.warning(f"Failed to check cost protection status: {e}")
        return False

def get_protection_level() -> ProtectionLevel:
    """Get current cost protection level."""
    try:
        cost_protection = get_cost_protection()
        if cost_protection and hasattr(cost_protection, 'get_protection_level'):
            level_str = cost_protection.get_protection_level()
            return ProtectionLevel(level_str)
        else:
            return ProtectionLevel.MONITORING
    except Exception as e:
        # SAFE: Internal logging only - no circular import
        _internal_logger.warning(f"Failed to get protection level: {e}")
        return ProtectionLevel.MONITORING

def reset_cost_metrics() -> bool:
    """Reset all cost metrics."""
    try:
        # Reset internal metrics
        internal_success = _get_cost_metrics_manager().reset_metrics()
        
        # Try to reset through cost protection instance
        try:
            cost_protection = get_cost_protection()
            if cost_protection and hasattr(cost_protection, 'reset'):
                cost_protection.reset()
        except Exception as e:
            # SAFE: Internal logging only - no circular import
            _internal_logger.warning(f"Failed to reset through cost protection: {e}")
        
        return internal_success
        
    except Exception as e:
        # SAFE: Internal logging only - no circular import
        _internal_logger.error(f"Failed to reset cost metrics: {e}")
        return False

# EOS

# ===== SECTION 5: MODULE EXPORTS =====

__all__ = [
    # Enums
    'CostCategory',
    'ProtectionLevel', 
    'CostThresholdType',
    'CostMetricType',
    
    # Data classes
    'CostMetric',
    'CostProtectionMetrics',
    
    # Public interface functions (called by metrics.py gateway)
    'get_cost_protection_metrics',
    'record_cost_metric',
    'is_cost_protection_active',
    'get_protection_level',
    'reset_cost_metrics'
]

# EOF
