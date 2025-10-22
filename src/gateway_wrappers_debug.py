"""
gateway_wrappers_debug.py - DEBUG Interface Wrappers
Version: 2025.10.22.03
Description: Convenience wrappers for DEBUG interface operations

Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

from typing import Any, Dict
from gateway_core import GatewayInterface, execute_operation


# ===== GENERAL DEBUG OPERATIONS =====

def check_component_health(component: str) -> Dict[str, Any]:
    """Check component health."""
    return execute_operation(GatewayInterface.DEBUG, 'check_component_health', component=component)


def check_gateway_health() -> Dict[str, Any]:
    """Check gateway health."""
    return execute_operation(GatewayInterface.DEBUG, 'check_gateway_health')


def diagnose_system_health() -> Dict[str, Any]:
    """Diagnose system health."""
    return execute_operation(GatewayInterface.DEBUG, 'diagnose_system_health')


def run_debug_tests() -> Dict[str, Any]:
    """Run debug tests."""
    return execute_operation(GatewayInterface.DEBUG, 'run_debug_tests')


def validate_system_architecture() -> Dict[str, Any]:
    """Validate system architecture."""
    return execute_operation(GatewayInterface.DEBUG, 'validate_system_architecture')


# ===== CONFIG DEBUG OPERATIONS (2025.10.22.02) =====

def check_config_health() -> Dict[str, Any]:
    """
    Check CONFIG interface health.
    
    Verifies:
    - SINGLETON registration
    - Rate limiting effectiveness
    - No threading locks (AP-08 compliance)
    - Reset operation availability
    - Parameter operations working
    """
    return execute_operation(GatewayInterface.DEBUG, 'check_config_health')


def diagnose_config_performance() -> Dict[str, Any]:
    """
    Diagnose CONFIG interface performance.
    
    Analyzes:
    - Rate limiting effectiveness
    - Parameter operation performance
    - SSM vs environment variable usage
    - Configuration reload patterns
    - Cache hit rates
    """
    return execute_operation(GatewayInterface.DEBUG, 'diagnose_config_performance')


def validate_config_configuration() -> Dict[str, Any]:
    """
    Validate CONFIG interface configuration.
    
    Checks:
    - SINGLETON registration
    - No threading locks (AP-08 compliance)
    - Rate limiting configuration
    - Parameter Store setup
    - Reset operation availability
    - Configuration initialization
    """
    return execute_operation(GatewayInterface.DEBUG, 'validate_config_configuration')


def benchmark_config_operations() -> Dict[str, Any]:
    """
    Benchmark CONFIG interface operations.
    
    Measures:
    - Parameter get/set operations
    - Configuration validation
    - Reset operation
    - Rate limiting overhead
    """
    return execute_operation(GatewayInterface.DEBUG, 'benchmark_config_operations')


# ===== HTTP_CLIENT DEBUG OPERATIONS (2025.10.22.02) =====

def check_http_client_health() -> Dict[str, Any]:
    """
    Check HTTP_CLIENT interface health and compliance.
    
    Verifies:
    - SINGLETON registration
    - Rate limiting effectiveness
    - No threading locks (AP-08)
    - Reset operation availability
    - Connection pool status
    - Request statistics
    
    Returns:
        Dict with health status and detailed checks
        
    REF: AP-08, DEC-04, LESS-18, LESS-21
    """
    return execute_operation(GatewayInterface.DEBUG, 'check_http_client_health')


def diagnose_http_client_performance() -> Dict[str, Any]:
    """
    Diagnose HTTP_CLIENT interface performance characteristics.
    
    Analyzes:
    - Request patterns and statistics
    - Connection pool utilization
    - Retry behavior effectiveness
    - Rate limiting impact
    - Error rates and types
    
    Returns:
        Dict with performance diagnostics
        
    REF: LESS-21
    """
    return execute_operation(GatewayInterface.DEBUG, 'diagnose_http_client_performance')


def validate_http_client_configuration() -> Dict[str, Any]:
    """
    Validate HTTP_CLIENT interface configuration and compliance.
    
    Validates:
    - SINGLETON registration compliance
    - Threading lock compliance (CRITICAL)
    - Rate limiting configuration (500 ops/sec)
    - Connection pool settings
    - Retry configuration
    - Reset operation availability
    
    Returns:
        Dict with validation results and compliance status
        
    REF: AP-08, DEC-04, LESS-18, LESS-21
    """
    return execute_operation(GatewayInterface.DEBUG, 'validate_http_client_configuration')


def benchmark_http_client_operations() -> Dict[str, Any]:
    """
    Benchmark HTTP_CLIENT interface operations.
    
    Benchmarks:
    - GET request setup (100 ops)
    - POST request setup (100 ops)
    - Manager retrieval (50 ops)
    - get_stats (200 ops)
    - reset (10 ops)
    
    Total: 460 operations
    
    NOTE: Tests infrastructure only, not actual network performance.
    
    Returns:
        Dict with benchmark results for each operation
        
    REF: LESS-21
    """
    return execute_operation(GatewayInterface.DEBUG, 'benchmark_http_client_operations')


# ===== INITIALIZATION INTERFACE DEBUG OPERATIONS =====

def check_initialization_health(**kwargs) -> Dict[str, Any]:
    """Check INITIALIZATION interface health (AP-08, DEC-04, LESS-17, LESS-18, LESS-21)."""
    return execute_operation(GatewayInterface.DEBUG, 'check_initialization_health', **kwargs)


def diagnose_initialization_performance(**kwargs) -> Dict[str, Any]:
    """Diagnose INITIALIZATION interface performance patterns."""
    return execute_operation(GatewayInterface.DEBUG, 'diagnose_initialization_performance', **kwargs)


def validate_initialization_configuration(**kwargs) -> Dict[str, Any]:
    """Validate INITIALIZATION interface configuration and compliance."""
    return execute_operation(GatewayInterface.DEBUG, 'validate_initialization_configuration', **kwargs)


def benchmark_initialization_operations(**kwargs) -> Dict[str, Any]:
    """Benchmark INITIALIZATION interface operations."""
    return execute_operation(GatewayInterface.DEBUG, 'benchmark_initialization_operations', **kwargs)


# ===== UTILITY INTERFACE DEBUG OPERATIONS =====

def check_utility_health(**kwargs) -> Dict[str, Any]:
    """Check UTILITY interface health (AP-08, DEC-04, LESS-17, LESS-18, LESS-21)."""
    return execute_operation(GatewayInterface.DEBUG, 'check_utility_health', **kwargs)


def diagnose_utility_performance(**kwargs) -> Dict[str, Any]:
    """Diagnose UTILITY interface performance patterns."""
    return execute_operation(GatewayInterface.DEBUG, 'diagnose_utility_performance', **kwargs)


def validate_utility_configuration(**kwargs) -> Dict[str, Any]:
    """Validate UTILITY interface configuration and compliance."""
    return execute_operation(GatewayInterface.DEBUG, 'validate_utility_configuration', **kwargs)


def benchmark_utility_operations(**kwargs) -> Dict[str, Any]:
    """Benchmark UTILITY interface operations."""
    return execute_operation(GatewayInterface.DEBUG, 'benchmark_utility_operations', **kwargs)


# ===== SINGLETON INTERFACE DEBUG OPERATIONS =====

def check_singleton_health(**kwargs) -> Dict[str, Any]:
    """Check SINGLETON interface health (AP-08, DEC-04, LESS-17, LESS-18, LESS-21)."""
    return execute_operation(GatewayInterface.DEBUG, 'check_singleton_health', **kwargs)


def diagnose_singleton_performance(**kwargs) -> Dict[str, Any]:
    """Diagnose SINGLETON interface performance patterns."""
    return execute_operation(GatewayInterface.DEBUG, 'diagnose_singleton_performance', **kwargs)


def validate_singleton_configuration(**kwargs) -> Dict[str, Any]:
    """Validate SINGLETON interface configuration and compliance."""
    return execute_operation(GatewayInterface.DEBUG, 'validate_singleton_configuration', **kwargs)


def benchmark_singleton_operations(**kwargs) -> Dict[str, Any]:
    """Benchmark SINGLETON interface operations."""
    return execute_operation(GatewayInterface.DEBUG, 'benchmark_singleton_operations', **kwargs)


# ===== SYSTEM-WIDE DEBUG OPERATIONS =====

def check_system_health(**kwargs) -> Dict[str, Any]:
    """
    Comprehensive system-wide health check for all 12 interfaces.
    
    Validates:
    - All interfaces optimized (SINGLETON, rate limiting, no locks)
    - Full compliance with AP-08, DEC-04, LESS-17, LESS-18, LESS-21
    - System readiness for production
    """
    return execute_operation(GatewayInterface.DEBUG, 'check_system_health', **kwargs)


def validate_system_configuration(**kwargs) -> Dict[str, Any]:
    """
    Final system-wide configuration validation.
    
    Validates:
    - All 12 interfaces present and configured
    - SIMA pattern compliance across all interfaces
    - Anti-pattern compliance (no violations)
    - Complete optimization (Phase 1 + 3)
    """
    return execute_operation(GatewayInterface.DEBUG, 'validate_system_configuration', **kwargs)


__all__ = [
    # General debug operations
    'check_component_health',
    'check_gateway_health',
    'diagnose_system_health',
    'run_debug_tests',
    'validate_system_architecture',
    
    # CONFIG debug operations
    'check_config_health',
    'diagnose_config_performance',
    'validate_config_configuration',
    'benchmark_config_operations',
    
    # HTTP_CLIENT debug operations
    'check_http_client_health',
    'diagnose_http_client_performance',
    'validate_http_client_configuration',
    'benchmark_http_client_operations',
    
    # INITIALIZATION interface debug
    'check_initialization_health',
    'diagnose_initialization_performance',
    'validate_initialization_configuration',
    'benchmark_initialization_operations',
    
    # UTILITY interface debug
    'check_utility_health',
    'diagnose_utility_performance',
    'validate_utility_configuration',
    'benchmark_utility_operations',
    
    # SINGLETON interface debug
    'check_singleton_health',
    'diagnose_singleton_performance',
    'validate_singleton_configuration',
    'benchmark_singleton_operations',
    
    # System-wide debug
    'check_system_health',
    'validate_system_configuration',
]
