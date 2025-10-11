"""
home_assistant_logging.py
Version: 2025.10.11.01
Description: Home Assistant Logging using single generic function with operation type enum

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

import logging
import time
from typing import Dict, Any, Optional, List, Union
from enum import Enum

# Ultra-pure gateway imports for maximum utilization
from . import logging as log_gateway
from . import metrics
from . import utility
from . import cache

logger = logging.getLogger(__name__)

# ===== SECTION 1: CONSOLIDATED ENUMS FOR ULTRA-GENERIC OPERATIONS =====

class HALoggingOperation(Enum):
    """Ultra-generic HA logging operations."""
    # Health Operations
    RECORD_SUCCESS = "record_success"
    RECORD_FAILURE = "record_failure"
    CHECK_HEALTH = "check_health"
    GET_STATUS = "get_status"
    GET_TREND = "get_trend"
    GET_ERROR_RATE = "get_error_rate"
    GET_RECOMMENDATIONS = "get_recommendations"
    
    # Event Operations
    LOG_OPERATION = "log_operation"
    LOG_CONNECTION = "log_connection"
    LOG_ERROR = "log_error"
    
    # Management Operations
    SETUP_LOGGING = "setup_logging"
    CLEANUP_LOGGING = "cleanup_logging"
    RESET_STATS = "reset_stats"
    GET_STATISTICS = "get_statistics"

# ===== SECTION 2: CACHE CONSTANTS =====

HA_HEALTH_CACHE_PREFIX = "ha_health_"
HA_STATS_CACHE_PREFIX = "ha_stats_"
HA_CACHE_TTL = 300  # 5 minutes

# ===== SECTION 3: ULTRA-GENERIC HA LOGGING FUNCTION =====

def generic_ha_logging_operation(operation: HALoggingOperation, **kwargs) -> Any:
    """
    ULTRA-GENERIC: Execute any HA logging operation using operation type.
    Consolidates 12+ HA logging functions into single ultra-optimized function.
    """
    try:
        operation_start = time.time()
        correlation_id = utility.generate_correlation_id()
        
        # Log operation start using logging gateway
        log_gateway.log_debug(
            f"HA logging operation started: {operation.value}",
            extra={"correlation_id": correlation_id, "operation": operation.value}
        )
        
        # Record metrics using metrics gateway
        metrics.record_metric("ha_logging_operation", 1.0, {
            "operation_type": operation.value,
            "correlation_id": correlation_id
        })
        
        # Execute operation based on type using gateway functions
        if operation == HALoggingOperation.RECORD_SUCCESS:
            result = _execute_record_success_operation(**kwargs)
        elif operation == HALoggingOperation.RECORD_FAILURE:
            result = _execute_record_failure_operation(**kwargs)
        elif operation == HALoggingOperation.CHECK_HEALTH:
            result = _execute_check_health_operation(**kwargs)
        elif operation == HALoggingOperation.GET_STATUS:
            result = _execute_get_status_operation(**kwargs)
        elif operation == HALoggingOperation.GET_TREND:
            result = _execute_get_trend_operation(**kwargs)
        elif operation == HALoggingOperation.GET_ERROR_RATE:
            result = _execute_get_error_rate_operation(**kwargs)
        elif operation == HALoggingOperation.GET_RECOMMENDATIONS:
            result = _execute_get_recommendations_operation(**kwargs)
        elif operation == HALoggingOperation.LOG_OPERATION:
            result = _execute_log_operation_operation(**kwargs)
        elif operation == HALoggingOperation.LOG_CONNECTION:
            result = _execute_log_connection_operation(**kwargs)
        elif operation == HALoggingOperation.LOG_ERROR:
            result = _execute_log_error_operation(**kwargs)
        elif operation == HALoggingOperation.SETUP_LOGGING:
            result = _execute_setup_logging_operation(**kwargs)
        elif operation == HALoggingOperation.CLEANUP_LOGGING:
            result = _execute_cleanup_logging_operation(**kwargs)
        elif operation == HALoggingOperation.RESET_STATS:
            result = _execute_reset_stats_operation(**kwargs)
        elif operation == HALoggingOperation.GET_STATISTICS:
            result = _execute_get_statistics_operation(**kwargs)
        else:
            return utility.create_error_response(
                f"Unknown HA logging operation: {operation.value}",
                {"operation": operation.value}
            )
        
        # Calculate duration and record completion metrics
        duration_ms = (time.time() - operation_start) * 1000
        
        metrics.record_metric("ha_logging_operation_duration", duration_ms, {
            "operation_type": operation.value,
            "success": result is not None
        })
        
        # Log completion using logging gateway
        log_gateway.log_debug(
            f"HA logging operation completed: {operation.value} ({duration_ms:.2f}ms)",
            extra={"correlation_id": correlation_id, "duration_ms": duration_ms}
        )
        
        return result
        
    except Exception as e:
        error_msg = f"HA logging operation failed: {operation.value} - {str(e)}"
        log_gateway.log_error(error_msg, error=e)
        
        # Return appropriate error response based on operation type
        if operation in [HALoggingOperation.CHECK_HEALTH]:
            return False
        elif operation in [HALoggingOperation.GET_STATUS, HALoggingOperation.GET_TREND, 
                          HALoggingOperation.GET_RECOMMENDATIONS, HALoggingOperation.GET_STATISTICS]:
            return utility.create_error_response(error_msg, {"operation": operation.value, "error": str(e)})
        elif operation in [HALoggingOperation.GET_ERROR_RATE]:
            return 100.0  # Return maximum error rate on failure
        else:
            return None

# ===== SECTION 4: HEALTH OPERATION IMPLEMENTATIONS =====

def _execute_record_success_operation(**kwargs) -> None:
    """Execute record success operation using cache and metrics gateways."""
    response_time_ms = kwargs.get('response_time_ms')
    
    try:
        # Record success using cache gateway for health tracking
        health_data = cache.cache_get(f"{HA_HEALTH_CACHE_PREFIX}data", default_value={
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "response_times": [],
            "last_success_time": None
        })
        
        health_data["total_requests"] += 1
        health_data["successful_requests"] += 1
        health_data["last_success_time"] = utility.get_current_timestamp()
        
        # Track response times using cache gateway (keep last 50 for analysis)
        if response_time_ms is not None:
            health_data["response_times"].append(response_time_ms)
            if len(health_data["response_times"]) > 50:
                health_data["response_times"] = health_data["response_times"][-50:]
        
        cache.cache_set(f"{HA_HEALTH_CACHE_PREFIX}data", health_data, 
                       ttl=HA_CACHE_TTL, cache_type=cache.CacheType.MEMORY)
        
        # Record metrics using metrics gateway
        metrics.record_metric("ha_request_success", 1.0, {
            "response_time_ms": response_time_ms or 0
        })
        
        # Log success using logging gateway
        if response_time_ms:
            log_gateway.log_info(f"HA operation successful - {response_time_ms}ms")
        else:
            log_gateway.log_info("HA operation successful")
            
    except Exception as e:
        log_gateway.log_error(f"Error recording HA success: {str(e)}", error=e)

def _execute_record_failure_operation(**kwargs) -> None:
    """Execute record failure operation using cache and metrics gateways."""
    error = kwargs.get('error')
    response_status = kwargs.get('response_status')
    
    try:
        # Record failure using cache gateway for health tracking
        health_data = cache.cache_get(f"{HA_HEALTH_CACHE_PREFIX}data", default_value={
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "response_times": [],
            "last_failure_time": None,
            "recent_errors": []
        })
        
        health_data["total_requests"] += 1
        health_data["failed_requests"] += 1
        health_data["last_failure_time"] = utility.get_current_timestamp()
        
        # Track recent errors using cache gateway (keep last 20 for analysis)
        error_entry = {
            "error": str(error) if error else "Unknown error",
            "status": response_status,
            "timestamp": utility.get_current_timestamp()
        }
        health_data.setdefault("recent_errors", []).append(error_entry)
        if len(health_data["recent_errors"]) > 20:
            health_data["recent_errors"] = health_data["recent_errors"][-20:]
        
        cache.cache_set(f"{HA_HEALTH_CACHE_PREFIX}data", health_data, 
                       ttl=HA_CACHE_TTL, cache_type=cache.CacheType.MEMORY)
        
        # Record metrics using metrics gateway
        metrics.record_metric("ha_request_failure", 1.0, {
            "error_type": str(error)[:50] if error else "unknown",
            "response_status": response_status or 0
        })
        
        # Log failure using logging gateway
        error_msg = f"HA operation failed: {error}"
        if response_status:
            error_msg += f" (status: {response_status})"
        log_gateway.log_error(error_msg, error=error)
            
    except Exception as e:
        log_gateway.log_error(f"Error recording HA failure: {str(e)}", error=e)

def _execute_check_health_operation(**kwargs) -> bool:
    """Execute check health operation using cache gateway."""
    try:
        health_data = cache.cache_get(f"{HA_HEALTH_CACHE_PREFIX}data", default_value={
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0
        })
        
        total_requests = health_data.get("total_requests", 0)
        if total_requests == 0:
            return True  # No data yet, assume healthy
        
        # Calculate success rate
        successful_requests = health_data.get("successful_requests", 0)
        success_rate = (successful_requests / total_requests) * 100
        
        # Health threshold: >75% success rate
        return success_rate > 75.0
        
    except Exception as e:
        log_gateway.log_error(f"Error checking HA health: {str(e)}", error=e)
        return False

def _execute_get_status_operation(**kwargs) -> Dict[str, Any]:
    """Execute get status operation using cache and utility gateways."""
    try:
        health_data = cache.cache_get(f"{HA_HEALTH_CACHE_PREFIX}data", default_value={
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "response_times": [],
            "last_success_time": None,
            "last_failure_time": None
        })
        
        total_requests = health_data.get("total_requests", 0)
        successful_requests = health_data.get("successful_requests", 0)
        failed_requests = health_data.get("failed_requests", 0)
        response_times = health_data.get("response_times", [])
        
        # Calculate statistics
        success_rate = (successful_requests / total_requests * 100) if total_requests > 0 else 0
        failure_rate = (failed_requests / total_requests * 100) if total_requests > 0 else 0
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        # Determine health status
        if success_rate > 90:
            status = "excellent"
        elif success_rate > 75:
            status = "good"
        elif success_rate > 50:
            status = "warning"
        else:
            status = "critical"
        
        status_data = {
            "status": status,
            "health_score": round(success_rate, 2),
            "total_requests": total_requests,
            "successful_requests": successful_requests,
            "failed_requests": failed_requests,
            "success_rate_percent": round(success_rate, 2),
            "failure_rate_percent": round(failure_rate, 2),
            "average_response_time_ms": round(avg_response_time, 2),
            "last_success_time": health_data.get("last_success_time"),
            "last_failure_time": health_data.get("last_failure_time"),
            "checked_at": utility.get_current_timestamp()
        }
        
        return utility.create_success_response("HA health status", status_data)
        
    except Exception as e:
        error_msg = f"Error getting HA health status: {str(e)}"
        log_gateway.log_error(error_msg, error=e)
        return utility.create_error_response(error_msg, {"error": str(e)})

def _execute_get_trend_operation(**kwargs) -> Dict[str, Any]:
    """Execute get trend operation using cache and utility gateways."""
    window_minutes = kwargs.get('window_minutes', 60)
    
    try:
        health_data = cache.cache_get(f"{HA_HEALTH_CACHE_PREFIX}data", default_value={
            "response_times": [],
            "recent_errors": []
        })
        
        response_times = health_data.get("response_times", [])
        recent_errors = health_data.get("recent_errors", [])
        
        # Analyze trends (simplified for ultra-optimization)
        trend_data = {
            "window_minutes": window_minutes,
            "sample_size": len(response_times),
            "recent_errors_count": len(recent_errors),
            "trend_direction": "stable"  # Simplified trend analysis
        }
        
        if len(response_times) >= 10:
            # Simple trend analysis based on recent vs older response times
            recent_times = response_times[-5:] if len(response_times) >= 5 else response_times
            older_times = response_times[:-5] if len(response_times) >= 10 else response_times[:-len(recent_times)]
            
            if older_times and recent_times:
                recent_avg = sum(recent_times) / len(recent_times)
                older_avg = sum(older_times) / len(older_times)
                
                if recent_avg > older_avg * 1.2:
                    trend_data["trend_direction"] = "degrading"
                elif recent_avg < older_avg * 0.8:
                    trend_data["trend_direction"] = "improving"
                    
                trend_data["recent_avg_ms"] = round(recent_avg, 2)
                trend_data["older_avg_ms"] = round(older_avg, 2)
        
        return utility.create_success_response("HA health trend analysis", trend_data)
        
    except Exception as e:
        error_msg = f"Error getting HA health trend: {str(e)}"
        log_gateway.log_error(error_msg, error=e)
        return utility.create_error_response(error_msg, {"error": str(e)})

def _execute_get_error_rate_operation(**kwargs) -> float:
    """Execute get error rate operation using cache gateway."""
    window_minutes = kwargs.get('window_minutes', 60)
    
    try:
        health_data = cache.cache_get(f"{HA_HEALTH_CACHE_PREFIX}data", default_value={
            "total_requests": 0,
            "failed_requests": 0
        })
        
        total_requests = health_data.get("total_requests", 0)
        failed_requests = health_data.get("failed_requests", 0)
        
        if total_requests == 0:
            return 0.0
        
        error_rate = (failed_requests / total_requests) * 100
        return round(error_rate, 2)
        
    except Exception as e:
        log_gateway.log_error(f"Error getting HA error rate: {str(e)}", error=e)
        return 100.0  # Return maximum error rate on failure

def _execute_get_recommendations_operation(**kwargs) -> List[str]:
    """Execute get recommendations operation using cache and utility gateways."""
    try:
        health_data = cache.cache_get(f"{HA_HEALTH_CACHE_PREFIX}data", default_value={
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "response_times": [],
            "recent_errors": []
        })
        
        recommendations = []
        
        total_requests = health_data.get("total_requests", 0)
        if total_requests == 0:
            recommendations.append("No HA interaction data available yet.")
            return recommendations
        
        # Analyze data and provide recommendations
        success_rate = (health_data.get("successful_requests", 0) / total_requests) * 100
        response_times = health_data.get("response_times", [])
        recent_errors = health_data.get("recent_errors", [])
        
        # Success rate recommendations
        if success_rate < 50:
            recommendations.append("CRITICAL: Success rate below 50%. Check HA connectivity and configuration.")
        elif success_rate < 75:
            recommendations.append("WARNING: Success rate below 75%. Monitor HA system stability.")
        
        # Response time recommendations
        if response_times:
            avg_response_time = sum(response_times) / len(response_times)
            if avg_response_time > 5000:
                recommendations.append("Response times are high. Consider optimizing HA queries or network.")
            elif avg_response_time > 3000:
                recommendations.append("Response times are elevated. Monitor HA performance.")
        
        # Error pattern recommendations
        if len(recent_errors) > 5:
            recommendations.append("Multiple recent errors detected. Check HA logs and system health.")
        
        # Default recommendation
        if not recommendations:
            recommendations.append("HA integration appears healthy. Continue monitoring.")
        
        return recommendations
        
    except Exception as e:
        log_gateway.log_error(f"Error getting HA recommendations: {str(e)}", error=e)
        return ["Unable to analyze HA health. Check system logs."]

# ===== SECTION 5: EVENT OPERATION IMPLEMENTATIONS =====

def _execute_log_operation_operation(**kwargs) -> None:
    """Execute log operation operation using logging gateway."""
    operation_type = kwargs.get('operation_type', 'unknown')
    entity_id = kwargs.get('entity_id')
    result = kwargs.get('result')
    error = kwargs.get('error')
    
    try:
        # Create structured log entry using utility gateway
        log_context = {
            "ha_operation": operation_type,
            "entity_id": entity_id,
            "correlation_id": utility.generate_correlation_id()
        }
        
        if result:
            log_context["result"] = str(result)[:200]  # Limit result size
        
        # Log using logging gateway with structured context
        if error:
            log_gateway.log_error(
                f"HA operation failed: {operation_type}",
                error=error,
                extra=log_context
            )
        else:
            log_gateway.log_info(
                f"HA operation executed: {operation_type}",
                extra=log_context
            )
        
        # Record metrics using metrics gateway
        metrics.record_metric("ha_operation_logged", 1.0, {
            "operation_type": operation_type,
            "has_error": bool(error),
            "has_entity_id": bool(entity_id)
        })
        
    except Exception as e:
        log_gateway.log_error(f"Error logging HA operation: {str(e)}", error=e)

def _execute_log_connection_operation(**kwargs) -> None:
    """Execute log connection operation using logging gateway."""
    event_type = kwargs.get('event_type', 'unknown')
    details = kwargs.get('details', {})
    
    try:
        # Create structured log entry using utility gateway
        log_context = {
            "ha_connection_event": event_type,
            "correlation_id": utility.generate_correlation_id()
        }
        
        if details:
            log_context["details"] = str(details)[:200]  # Limit details size
        
        # Log using logging gateway with structured context
        log_gateway.log_info(
            f"HA connection event: {event_type}",
            extra=log_context
        )
        
        # Record metrics using metrics gateway
        metrics.record_metric("ha_connection_event_logged", 1.0, {
            "event_type": event_type,
            "has_details": bool(details)
        })
        
    except Exception as e:
        log_gateway.log_error(f"Error logging HA connection event: {str(e)}", error=e)

def _execute_log_error_operation(**kwargs) -> None:
    """Execute log error operation using logging gateway."""
    error_message = kwargs.get('error_message', 'Unknown HA error')
    error_details = kwargs.get('error_details', {})
    error_exception = kwargs.get('error_exception')
    
    try:
        # Create structured log entry using utility gateway
        log_context = {
            "ha_error": True,
            "correlation_id": utility.generate_correlation_id()
        }
        
        if error_details:
            log_context["error_details"] = str(error_details)[:200]  # Limit details size
        
        # Log using logging gateway with structured context
        log_gateway.log_error(
            f"HA Error: {error_message}",
            error=error_exception,
            extra=log_context
        )
        
        # Record in health data for tracking
        _execute_record_failure_operation(error=error_message)
        
    except Exception as e:
        log_gateway.log_error(f"Error logging HA error: {str(e)}", error=e)

# ===== SECTION 6: MANAGEMENT OPERATION IMPLEMENTATIONS =====

def _execute_setup_logging_operation(**kwargs) -> Dict[str, Any]:
    """Execute setup logging operation using logging gateway."""
    log_level = kwargs.get('log_level', 'INFO')
    
    try:
        # Setup HA-specific logger using logging gateway
        ha_logger = log_gateway.get_logger("home_assistant")
        
        # Configure log level if provided
        if log_level:
            log_level_map = {
                'DEBUG': logging.DEBUG,
                'INFO': logging.INFO,
                'WARNING': logging.WARNING,
                'ERROR': logging.ERROR,
                'CRITICAL': logging.CRITICAL
            }
            
            if log_level.upper() in log_level_map:
                ha_logger.setLevel(log_level_map[log_level.upper()])
        
        # Initialize health data cache using cache gateway
        initial_health_data = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "response_times": [],
            "recent_errors": [],
            "setup_time": utility.get_current_timestamp()
        }
        
        cache.cache_set(f"{HA_HEALTH_CACHE_PREFIX}data", initial_health_data, 
                       ttl=HA_CACHE_TTL, cache_type=cache.CacheType.MEMORY)
        
        # Record metrics using metrics gateway
        metrics.record_metric("ha_logging_setup", 1.0, {
            "log_level": log_level
        })
        
        return utility.create_success_response("HA logging setup completed", {
            "log_level": log_level,
            "logger_name": "home_assistant",
            "setup_time": utility.get_current_timestamp()
        })
        
    except Exception as e:
        error_msg = f"Error setting up HA logging: {str(e)}"
        log_gateway.log_error(error_msg, error=e)
        return utility.create_error_response(error_msg, {"error": str(e)})

def _execute_cleanup_logging_operation(**kwargs) -> Dict[str, Any]:
    """Execute cleanup logging operation using cache gateway."""
    try:
        # Clear health data from cache using cache gateway
        health_keys_cleared = 0
        for key_suffix in ["data", "stats", "trends"]:
            cache_key = f"{HA_HEALTH_CACHE_PREFIX}{key_suffix}"
            if cache.cache_clear(cache_key):
                health_keys_cleared += 1
        
        # Clear stats data from cache using cache gateway
        stats_keys_cleared = 0
        for key_suffix in ["operations", "connections", "errors"]:
            cache_key = f"{HA_STATS_CACHE_PREFIX}{key_suffix}"
            if cache.cache_clear(cache_key):
                stats_keys_cleared += 1
        
        # Record metrics using metrics gateway
        metrics.record_metric("ha_logging_cleanup", 1.0, {
            "health_keys_cleared": health_keys_cleared,
            "stats_keys_cleared": stats_keys_cleared
        })
        
        return utility.create_success_response("HA logging cleanup completed", {
            "health_keys_cleared": health_keys_cleared,
            "stats_keys_cleared": stats_keys_cleared,
            "cleanup_time": utility.get_current_timestamp()
        })
        
    except Exception as e:
        error_msg = f"Error cleaning up HA logging: {str(e)}"
        log_gateway.log_error(error_msg, error=e)
        return utility.create_error_response(error_msg, {"error": str(e)})

def _execute_reset_stats_operation(**kwargs) -> Dict[str, Any]:
    """Execute reset stats operation using cache gateway."""
    try:
        # Reset health data using cache gateway
        reset_health_data = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "response_times": [],
            "recent_errors": [],
            "reset_time": utility.get_current_timestamp()
        }
        
        cache.cache_set(f"{HA_HEALTH_CACHE_PREFIX}data", reset_health_data, 
                       ttl=HA_CACHE_TTL, cache_type=cache.CacheType.MEMORY)
        
        # Record metrics using metrics gateway
        metrics.record_metric("ha_stats_reset", 1.0, {
            "reset_time": utility.get_current_timestamp()
        })
        
        return utility.create_success_response("HA statistics reset completed", {
            "reset_time": utility.get_current_timestamp()
        })
        
    except Exception as e:
        error_msg = f"Error resetting HA statistics: {str(e)}"
        log_gateway.log_error(error_msg, error=e)
        return utility.create_error_response(error_msg, {"error": str(e)})

def _execute_get_statistics_operation(**kwargs) -> Dict[str, Any]:
    """Execute get statistics operation using cache and utility gateways."""
    try:
        health_data = cache.cache_get(f"{HA_HEALTH_CACHE_PREFIX}data", default_value={
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "response_times": [],
            "recent_errors": []
        })
        
        # Calculate comprehensive statistics
        total_requests = health_data.get("total_requests", 0)
        successful_requests = health_data.get("successful_requests", 0)
        failed_requests = health_data.get("failed_requests", 0)
        response_times = health_data.get("response_times", [])
        recent_errors = health_data.get("recent_errors", [])
        
        statistics = {
            "requests": {
                "total": total_requests,
                "successful": successful_requests,
                "failed": failed_requests,
                "success_rate_percent": (successful_requests / total_requests * 100) if total_requests > 0 else 0,
                "failure_rate_percent": (failed_requests / total_requests * 100) if total_requests > 0 else 0
            },
            "performance": {
                "total_response_times": len(response_times),
                "avg_response_time_ms": sum(response_times) / len(response_times) if response_times else 0,
                "min_response_time_ms": min(response_times) if response_times else 0,
                "max_response_time_ms": max(response_times) if response_times else 0
            },
            "errors": {
                "recent_error_count": len(recent_errors),
                "recent_errors": recent_errors[-5:] if recent_errors else []  # Last 5 errors
            },
            "health": {
                "overall_healthy": (successful_requests / total_requests > 0.75) if total_requests > 0 else True,
                "status": "healthy" if (successful_requests / total_requests > 0.75) if total_requests > 0 else True else "unhealthy"
            },
            "retrieved_at": utility.get_current_timestamp()
        }
        
        return utility.create_success_response("HA statistics retrieved", statistics)
        
    except Exception as e:
        error_msg = f"Error getting HA statistics: {str(e)}"
        log_gateway.log_error(error_msg, error=e)
        return utility.create_error_response(error_msg, {"error": str(e)})

# ===== SECTION 7: COMPATIBILITY LAYER (THIN WRAPPERS FOR EXTERNAL API) =====

def record_ha_success(response_time_ms: Optional[float] = None) -> None:
    """COMPATIBILITY: Record successful HA interaction."""
    return generic_ha_logging_operation(HALoggingOperation.RECORD_SUCCESS, response_time_ms=response_time_ms)

def record_ha_failure(error: Optional[Exception] = None, response_status: Optional[int] = None) -> None:
    """COMPATIBILITY: Record failed HA interaction."""
    return generic_ha_logging_operation(HALoggingOperation.RECORD_FAILURE, error=error, response_status=response_status)

def is_ha_healthy() -> bool:
    """COMPATIBILITY: Check if HA connection is healthy."""
    return generic_ha_logging_operation(HALoggingOperation.CHECK_HEALTH)

def get_ha_health_status() -> Dict[str, Any]:
    """COMPATIBILITY: Get comprehensive HA health status."""
    return generic_ha_logging_operation(HALoggingOperation.GET_STATUS)

def get_ha_health_trend(window_minutes: int = 60) -> Dict[str, Any]:
    """COMPATIBILITY: Get HA health trend analysis."""
    return generic_ha_logging_operation(HALoggingOperation.GET_TREND, window_minutes=window_minutes)

def get_ha_error_rate(window_minutes: int = 60) -> float:
    """COMPATIBILITY: Get HA error rate percentage."""
    return generic_ha_logging_operation(HALoggingOperation.GET_ERROR_RATE, window_minutes=window_minutes)

def get_ha_recommendations() -> List[str]:
    """COMPATIBILITY: Get HA health recommendations."""
    return generic_ha_logging_operation(HALoggingOperation.GET_RECOMMENDATIONS)

def log_ha_operation(operation_type: str, entity_id: Optional[str] = None, 
                    result: Optional[Dict[str, Any]] = None, 
                    error: Optional[Exception] = None) -> None:
    """COMPATIBILITY: Log HA operations with structured data."""
    return generic_ha_logging_operation(HALoggingOperation.LOG_OPERATION, 
                                      operation_type=operation_type,
                                      entity_id=entity_id,
                                      result=result,
                                      error=error)

def log_ha_connection_event(event_type: str, details: Optional[Dict[str, Any]] = None) -> None:
    """COMPATIBILITY: Log HA connection events."""
    return generic_ha_logging_operation(HALoggingOperation.LOG_CONNECTION, 
                                      event_type=event_type,
                                      details=details)

def setup_ha_logging(log_level: str = "INFO") -> Dict[str, Any]:
    """COMPATIBILITY: Setup HA-specific logging configuration."""
    return generic_ha_logging_operation(HALoggingOperation.SETUP_LOGGING, log_level=log_level)

def cleanup_ha_logging() -> Dict[str, Any]:
    """COMPATIBILITY: Cleanup HA logging resources."""
    return generic_ha_logging_operation(HALoggingOperation.CLEANUP_LOGGING)

# Additional compatibility functions
def reset_ha_statistics() -> Dict[str, Any]:
    """COMPATIBILITY: Reset HA logging statistics."""
    return generic_ha_logging_operation(HALoggingOperation.RESET_STATS)

def get_ha_statistics() -> Dict[str, Any]:
    """COMPATIBILITY: Get comprehensive HA statistics."""
    return generic_ha_logging_operation(HALoggingOperation.GET_STATISTICS)

def log_ha_error(error_message: str, error_details: Dict[str, Any] = None, 
                error_exception: Exception = None) -> None:
    """COMPATIBILITY: Log HA errors with details."""
    return generic_ha_logging_operation(HALoggingOperation.LOG_ERROR,
                                      error_message=error_message,
                                      error_details=error_details,
                                      error_exception=error_exception)

# ===== SECTION 8: MODULE EXPORTS =====

__all__ = [
    # Ultra-generic function (for advanced users)
    'generic_ha_logging_operation',
    'HALoggingOperation',
    
    # Compatibility layer functions (for existing code)
    'record_ha_success',           # Record successful HA interaction
    'record_ha_failure',           # Record failed HA interaction
    'is_ha_healthy',              # Check HA connection health
    'get_ha_health_status',       # Get comprehensive HA health status
    'get_ha_health_trend',        # Get HA health trend analysis
    'get_ha_error_rate',          # Get HA error rate percentage
    'get_ha_recommendations',     # Get HA health recommendations
    'log_ha_operation',           # Log HA operations with structured data
    'log_ha_connection_event',    # Log HA connection events
    'log_ha_error',              # Log HA errors with details
    'setup_ha_logging',           # Setup HA-specific logging
    'cleanup_ha_logging',         # Cleanup HA logging resources
    'reset_ha_statistics',        # Reset HA logging statistics
    'get_ha_statistics'          # Get comprehensive HA statistics
]

# EOF
