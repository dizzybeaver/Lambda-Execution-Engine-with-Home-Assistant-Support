"""
gateway_utilization_validator.py - Gateway Integration Validator
Version: 2025.09.29.01
Description: Validates and reports gateway utilization across all interfaces

VALIDATES:
- âœ… Gateway integration percentage per interface
- âœ… Available gateway functions not being used
- âœ… Legacy patterns that could use gateways
- âœ… Optimization opportunities

Licensed under the Apache License, Version 2.0
"""

import re
from typing import Dict, Any, List, Optional

AVAILABLE_GATEWAY_FUNCTIONS = {
    'cache': [
        'cache_get', 'cache_set', 'cache_delete', 'cache_clear',
        'cache_get_fast', 'cache_set_fast', 'cache_has',
        'cache_operation_result', 'get_cache_statistics',
        'optimize_cache_memory', 'get_cache_manager'
    ],
    'security': [
        'validate_input', 'validate_request', 'sanitize_data',
        'get_security_status', 'security_health_check',
        'get_security_validator', 'get_unified_validator'
    ],
    'utility': [
        'validate_string_input', 'create_success_response', 'create_error_response',
        'sanitize_response_data', 'get_current_timestamp', 'generate_correlation_id',
        'format_response', 'parse_request'
    ],
    'metrics': [
        'record_metric', 'get_metric', 'get_metrics_summary', 'get_performance_stats',
        'track_execution_time', 'track_memory_usage', 'track_http_request',
        'track_cache_hit', 'track_cache_miss', 'count_invocations'
    ],
    'logging': [
        'log_info', 'log_error', 'log_warning', 'log_debug',
        'get_log_statistics', 'create_log_context'
    ],
    'config': [
        'get_configuration', 'set_configuration', 'get_interface_configuration',
        'get_system_configuration', 'validate_configuration',
        'optimize_for_memory_constraint', 'get_configuration_health_status'
    ],
    'singleton': [
        'get_singleton', 'manage_singletons', 'validate_thread_safety',
        'execute_with_timeout', 'coordinate_operation', 'get_thread_coordinator',
        'get_memory_stats', 'optimize_memory', 'get_cache_manager'
    ]
}

EXPECTED_INTEGRATION_POINTS = {
    'metrics_core.py': {
        'cache': ['cache_operation_result', 'cache_get', 'cache_set'],
        'security': ['validate_input', 'sanitize_data'],
        'utility': ['generate_correlation_id', 'create_error_response'],
        'logging': ['log_info', 'log_error'],
        'config': ['get_interface_configuration']
    },
    'singleton_core.py': {
        'cache': ['cache_operation_result', 'cache_get', 'cache_set'],
        'security': ['validate_input', 'sanitize_data'],
        'utility': ['generate_correlation_id'],
        'logging': ['log_info', 'log_error'],
        'metrics': ['record_metric']
    },
    'http_client_core.py': {
        'cache': ['cache_operation_result', 'cache_get', 'cache_set'],
        'security': ['validate_input', 'validate_request'],
        'utility': ['generate_correlation_id', 'create_success_response'],
        'logging': ['log_info', 'log_error'],
        'metrics': ['track_http_request', 'track_execution_time'],
        'singleton': ['coordinate_operation']
    },
    'cache_core.py': {
        'security': ['validate_input', 'sanitize_data'],
        'utility': ['generate_correlation_id'],
        'logging': ['log_info', 'log_error'],
        'metrics': ['track_cache_hit', 'track_cache_miss'],
        'singleton': ['coordinate_operation', 'optimize_memory']
    },
    'security_core.py': {
        'cache': ['cache_operation_result'],
        'utility': ['generate_correlation_id', 'sanitize_response_data'],
        'logging': ['log_info', 'log_error'],
        'metrics': ['record_metric'],
        'config': ['get_interface_configuration']
    },
    'logging_core.py': {
        'cache': ['cache_set'],
        'security': ['sanitize_data'],
        'utility': ['generate_correlation_id', 'get_current_timestamp'],
        'metrics': ['record_metric']
    },
    'utility_core.py': {
        'cache': ['cache_get', 'cache_set'],
        'security': ['validate_input', 'sanitize_data'],
        'logging': ['log_info', 'log_error'],
        'metrics': ['record_metric']
    },
    'config_core.py': {
        'cache': ['cache_operation_result', 'cache_get', 'cache_set'],
        'security': ['validate_input'],
        'utility': ['generate_correlation_id'],
        'logging': ['log_info', 'log_error'],
        'metrics': ['record_metric']
    }
}

def analyze_gateway_usage(file_path: str, file_content: str) -> Dict[str, Any]:
    """
    Analyze gateway usage in a file.
    """
    gateway_usage = {}
    
    for gateway, functions in AVAILABLE_GATEWAY_FUNCTIONS.items():
        import_found = re.search(f'from \\. import {gateway}', file_content)
        
        if import_found:
            usage_count = {}
            total_usage = 0
            
            for func in functions:
                pattern = f'{gateway}\\.{func}\\('
                matches = len(re.findall(pattern, file_content))
                if matches > 0:
                    usage_count[func] = matches
                    total_usage += matches
            
            gateway_usage[gateway] = {
                'imported': True,
                'functions_used': list(usage_count.keys()),
                'total_calls': total_usage,
                'usage_details': usage_count,
                'functions_available_but_unused': [f for f in functions if f not in usage_count]
            }
        else:
            gateway_usage[gateway] = {
                'imported': False,
                'functions_used': [],
                'total_calls': 0,
                'usage_details': {},
                'functions_available_but_unused': functions
            }
    
    return gateway_usage

def calculate_utilization_percentage(file_path: str, gateway_usage: Dict[str, Any]) -> float:
    """
    Calculate gateway utilization percentage for a file.
    """
    file_name = file_path.split('/')[-1]
    
    if file_name not in EXPECTED_INTEGRATION_POINTS:
        return 0.0
    
    expected = EXPECTED_INTEGRATION_POINTS[file_name]
    
    total_expected = sum(len(funcs) for funcs in expected.values())
    total_used = 0
    
    for gateway, expected_funcs in expected.items():
        if gateway in gateway_usage:
            used_funcs = gateway_usage[gateway]['functions_used']
            total_used += len([f for f in expected_funcs if f in used_funcs])
    
    if total_expected == 0:
        return 100.0
    
    return (total_used / total_expected) * 100

def identify_missing_integrations(file_path: str, gateway_usage: Dict[str, Any]) -> List[Dict[str, str]]:
    """
    Identify missing gateway integrations that should be added.
    """
    file_name = file_path.split('/')[-1]
    
    if file_name not in EXPECTED_INTEGRATION_POINTS:
        return []
    
    expected = EXPECTED_INTEGRATION_POINTS[file_name]
    missing = []
    
    for gateway, expected_funcs in expected.items():
        if gateway in gateway_usage:
            used_funcs = gateway_usage[gateway]['functions_used']
            for func in expected_funcs:
                if func not in used_funcs:
                    missing.append({
                        'gateway': gateway,
                        'function': func,
                        'reason': f'Expected in {file_name} for optimization',
                        'priority': 'HIGH' if gateway in ['cache', 'security'] else 'MEDIUM'
                    })
    
    return missing

def generate_utilization_report(file_path: str, file_content: str) -> Dict[str, Any]:
    """
    Generate comprehensive gateway utilization report for a file.
    """
    gateway_usage = analyze_gateway_usage(file_path, file_content)
    utilization = calculate_utilization_percentage(file_path, gateway_usage)
    missing = identify_missing_integrations(file_path, gateway_usage)
    
    total_gateway_calls = sum(g['total_calls'] for g in gateway_usage.values())
    gateways_imported = sum(1 for g in gateway_usage.values() if g['imported'])
    
    optimization_status = 'ULTRA-OPTIMIZED' if utilization >= 95 else 'OPTIMIZED' if utilization >= 70 else 'NEEDS_OPTIMIZATION'
    
    report = {
        'file_path': file_path,
        'optimization_status': optimization_status,
        'utilization_percentage': round(utilization, 2),
        'total_gateway_calls': total_gateway_calls,
        'gateways_imported': gateways_imported,
        'gateway_usage_details': gateway_usage,
        'missing_integrations': missing,
        'recommendations': _generate_recommendations(utilization, missing, gateway_usage)
    }
    
    return report

def _generate_recommendations(utilization: float, missing: List[Dict], gateway_usage: Dict) -> List[str]:
    """
    Generate recommendations for improving gateway utilization.
    """
    recommendations = []
    
    if utilization < 70:
        recommendations.append(f"LOW UTILIZATION: Only {utilization:.1f}% gateway integration. Target 95%+")
    
    if len(missing) > 0:
        high_priority = [m for m in missing if m['priority'] == 'HIGH']
        if high_priority:
            recommendations.append(f"Add {len(high_priority)} HIGH priority gateway integrations")
    
    for gateway, info in gateway_usage.items():
        if info['imported'] and info['total_calls'] == 0:
            recommendations.append(f"Remove unused import: {gateway}")
        
        if len(info['functions_available_but_unused']) > 5 and info['total_calls'] > 0:
            recommendations.append(f"Consider using more {gateway} functions: {len(info['functions_available_but_unused'])} available")
    
    if not recommendations:
        recommendations.append("Gateway utilization is excellent - no improvements needed")
    
    return recommendations

def analyze_project_wide_utilization(file_paths: List[str]) -> Dict[str, Any]:
    """
    Analyze gateway utilization across entire project.
    """
    project_report = {
        'total_files_analyzed': 0,
        'files_by_status': {'ULTRA-OPTIMIZED': [], 'OPTIMIZED': [], 'NEEDS_OPTIMIZATION': []},
        'average_utilization': 0.0,
        'total_missing_integrations': 0,
        'project_wide_recommendations': []
    }
    
    utilization_scores = []
    
    for file_path in file_paths:
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            report = generate_utilization_report(file_path, content)
            project_report['files_by_status'][report['optimization_status']].append(file_path)
            utilization_scores.append(report['utilization_percentage'])
            project_report['total_missing_integrations'] += len(report['missing_integrations'])
            project_report['total_files_analyzed'] += 1
        except Exception:
            pass
    
    if utilization_scores:
        project_report['average_utilization'] = sum(utilization_scores) / len(utilization_scores)
    
    needs_optimization = len(project_report['files_by_status']['NEEDS_OPTIMIZATION'])
    if needs_optimization > 0:
        project_report['project_wide_recommendations'].append(
            f"Focus on optimizing {needs_optimization} files with low gateway utilization"
        )
    
    if project_report['average_utilization'] < 80:
        project_report['project_wide_recommendations'].append(
            f"Project-wide utilization ({project_report['average_utilization']:.1f}%) below target (95%+)"
        )
    else:
        project_report['project_wide_recommendations'].append(
            f"Excellent project-wide utilization: {project_report['average_utilization']:.1f}%"
        )
    
    return project_report

def generate_optimization_action_plan(report: Dict[str, Any]) -> List[Dict[str, str]]:
    """
    Generate actionable optimization plan from utilization report.
    """
    action_plan = []
    
    for missing in report['missing_integrations']:
        action = {
            'action': f"Add {missing['gateway']}.{missing['function']}() integration",
            'file': report['file_path'],
            'priority': missing['priority'],
            'benefit': 'Improves gateway utilization and reduces memory footprint',
            'estimated_time': '5-10 minutes'
        }
        action_plan.append(action)
    
    return action_plan

__all__ = [
    'AVAILABLE_GATEWAY_FUNCTIONS',
    'EXPECTED_INTEGRATION_POINTS',
    'analyze_gateway_usage',
    'calculate_utilization_percentage',
    'identify_missing_integrations',
    'generate_utilization_report',
    'analyze_project_wide_utilization',
    'generate_optimization_action_plan'
]
