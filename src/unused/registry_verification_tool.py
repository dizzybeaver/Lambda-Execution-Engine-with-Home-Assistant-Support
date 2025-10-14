"""
registry_verification_tool.py - Complete registry verification utility
Version: 2025.10.14.01
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

from typing import Dict, Any, List, Tuple
import importlib


def verify_all_registry_operations() -> Dict[str, Any]:
    """
    Verify all 63 operations in _OPERATION_REGISTRY are callable.
    Tests each registry entry by attempting to import module and get function.
    """
    from gateway import _OPERATION_REGISTRY, GatewayInterface
    
    results = {
        'total_operations': len(_OPERATION_REGISTRY),
        'tested': 0,
        'passed': 0,
        'failed': 0,
        'failures': [],
        'naming_inconsistencies': [],
        'by_interface': {}
    }
    
    # Test each registry entry
    for (interface, operation), (module_name, func_name) in _OPERATION_REGISTRY.items():
        results['tested'] += 1
        
        # Track by interface
        iface_name = interface.value
        if iface_name not in results['by_interface']:
            results['by_interface'][iface_name] = {
                'total': 0,
                'passed': 0,
                'failed': 0,
                'operations': []
            }
        
        results['by_interface'][iface_name]['total'] += 1
        
        try:
            # Try to import module
            mod = importlib.import_module(module_name)
            
            # Try to get function
            if not hasattr(mod, func_name):
                raise AttributeError(f"Function '{func_name}' not found in module '{module_name}'")
            
            func = getattr(mod, func_name)
            
            # Check if callable
            if not callable(func):
                raise TypeError(f"'{func_name}' in '{module_name}' is not callable")
            
            results['passed'] += 1
            results['by_interface'][iface_name]['passed'] += 1
            results['by_interface'][iface_name]['operations'].append({
                'operation': operation,
                'status': 'PASS',
                'function': func_name
            })
            
            # Check naming consistency
            if not (func_name.startswith('_execute_') or func_name.startswith('_') or 
                    func_name.endswith('_implementation')):
                results['naming_inconsistencies'].append({
                    'interface': iface_name,
                    'operation': operation,
                    'module': module_name,
                    'function': func_name,
                    'issue': 'Non-standard naming pattern'
                })
            
        except (ImportError, AttributeError, TypeError) as e:
            results['failed'] += 1
            results['by_interface'][iface_name]['failed'] += 1
            
            failure_info = {
                'interface': iface_name,
                'operation': operation,
                'module': module_name,
                'function': func_name,
                'error_type': type(e).__name__,
                'error_message': str(e)
            }
            
            results['failures'].append(failure_info)
            results['by_interface'][iface_name]['operations'].append({
                'operation': operation,
                'status': 'FAIL',
                'function': func_name,
                'error': str(e)
            })
    
    # Calculate success rate
    results['success_rate'] = (results['passed'] / results['total_operations'] * 100) if results['total_operations'] > 0 else 0
    results['naming_consistency_rate'] = ((results['total_operations'] - len(results['naming_inconsistencies'])) / results['total_operations'] * 100) if results['total_operations'] > 0 else 0
    
    return results


def analyze_naming_patterns() -> Dict[str, Any]:
    """
    Analyze naming patterns across all registry entries.
    Categorizes functions by naming convention.
    """
    from gateway import _OPERATION_REGISTRY
    
    patterns = {
        '_execute_*_implementation': [],
        '_*_implementation': [],
        '*_implementation': [],
        'direct_names': [],
        'other': []
    }
    
    for (interface, operation), (module_name, func_name) in _OPERATION_REGISTRY.items():
        entry = {
            'interface': interface.value,
            'operation': operation,
            'module': module_name,
            'function': func_name
        }
        
        if func_name.startswith('_execute_') and func_name.endswith('_implementation'):
            patterns['_execute_*_implementation'].append(entry)
        elif func_name.startswith('_') and func_name.endswith('_implementation'):
            patterns['_*_implementation'].append(entry)
        elif func_name.endswith('_implementation'):
            patterns['*_implementation'].append(entry)
        elif not func_name.startswith('_'):
            patterns['direct_names'].append(entry)
        else:
            patterns['other'].append(entry)
    
    summary = {
        'total_operations': len(_OPERATION_REGISTRY),
        'pattern_counts': {k: len(v) for k, v in patterns.items()},
        'patterns': patterns,
        'most_common': max(patterns.items(), key=lambda x: len(x[1]))[0] if patterns else None,
        'consistency_issues': len(patterns['direct_names']) + len(patterns['other'])
    }
    
    return summary


def generate_verification_report() -> str:
    """
    Generate comprehensive verification report in markdown format.
    Includes verification results and naming analysis.
    """
    verification_results = verify_all_registry_operations()
    naming_analysis = analyze_naming_patterns()
    
    report = []
    report.append("# Gateway Registry Verification Report")
    report.append(f"**Generated:** 2025.10.14")
    report.append(f"**Status:** Phase 2 Completion\n")
    
    report.append("## Executive Summary\n")
    report.append(f"- **Total Operations:** {verification_results['total_operations']}")
    report.append(f"- **Tested:** {verification_results['tested']}")
    report.append(f"- **Passed:** {verification_results['passed']}")
    report.append(f"- **Failed:** {verification_results['failed']}")
    report.append(f"- **Success Rate:** {verification_results['success_rate']:.1f}%")
    report.append(f"- **Naming Consistency:** {verification_results['naming_consistency_rate']:.1f}%\n")
    
    if verification_results['failed'] > 0:
        report.append("## ❌ FAILURES\n")
        for failure in verification_results['failures']:
            report.append(f"### {failure['interface']}.{failure['operation']}")
            report.append(f"- **Module:** `{failure['module']}`")
            report.append(f"- **Function:** `{failure['function']}`")
            report.append(f"- **Error:** {failure['error_type']}: {failure['error_message']}\n")
    
    if verification_results['naming_inconsistencies']:
        report.append("## ⚠️ NAMING INCONSISTENCIES\n")
        report.append(f"Found {len(verification_results['naming_inconsistencies'])} naming inconsistencies:\n")
        
        for inconsistency in verification_results['naming_inconsistencies']:
            report.append(f"- **{inconsistency['interface']}.{inconsistency['operation']}**")
            report.append(f"  - Module: `{inconsistency['module']}`")
            report.append(f"  - Function: `{inconsistency['function']}`")
            report.append(f"  - Issue: {inconsistency['issue']}\n")
    
    report.append("## 📊 Naming Pattern Analysis\n")
    report.append(f"**Most Common Pattern:** `{naming_analysis['most_common']}`\n")
    
    for pattern_name, count in naming_analysis['pattern_counts'].items():
        if count > 0:
            report.append(f"### {pattern_name} ({count} operations)")
            for entry in naming_analysis['patterns'][pattern_name][:5]:  # Show first 5
                report.append(f"- {entry['interface']}.{entry['operation']} → `{entry['function']}`")
            if count > 5:
                report.append(f"  ... and {count - 5} more\n")
            else:
                report.append("")
    
    report.append("## ✅ Verification by Interface\n")
    for interface_name, stats in verification_results['by_interface'].items():
        status = "✅" if stats['failed'] == 0 else "⚠️"
        report.append(f"### {status} {interface_name.upper()}")
        report.append(f"- Total: {stats['total']}")
        report.append(f"- Passed: {stats['passed']}")
        report.append(f"- Failed: {stats['failed']}")
        
        if stats['failed'] > 0:
            report.append("- **Failed Operations:**")
            for op in stats['operations']:
                if op['status'] == 'FAIL':
                    report.append(f"  - {op['operation']}: {op.get('error', 'Unknown error')}")
        report.append("")
    
    report.append("## 📋 Recommendations\n")
    if verification_results['failed'] > 0:
        report.append("**CRITICAL:** Fix failed operations before proceeding to Phase 3.\n")
    
    if len(verification_results['naming_inconsistencies']) > 5:
        report.append("**HIGH PRIORITY:** Standardize naming conventions:")
        report.append(f"- Current inconsistencies: {len(verification_results['naming_inconsistencies'])}")
        report.append(f"- Recommended pattern: `_execute_*_implementation`")
        report.append(f"- Benefits: Consistent, clear, maintainable\n")
    
    report.append("**Phase 3 Readiness:**")
    if verification_results['failed'] == 0:
        report.append("- ✅ All operations callable")
        report.append("- ✅ Ready for generic dispatcher expansion")
    else:
        report.append("- ❌ Fix failures before Phase 3")
        report.append("- ⚠️ Address naming inconsistencies")
    
    return "\n".join(report)


def quick_verify() -> bool:
    """
    Quick verification - returns True if all operations pass.
    Use for fast health checks.
    """
    results = verify_all_registry_operations()
    return results['failed'] == 0


def get_failed_operations() -> List[Dict[str, str]]:
    """Get list of failed operations for debugging."""
    results = verify_all_registry_operations()
    return results['failures']


def get_naming_issues() -> List[Dict[str, str]]:
    """Get list of naming inconsistencies."""
    results = verify_all_registry_operations()
    return results['naming_inconsistencies']


# ===== EXPORTS =====

__all__ = [
    'verify_all_registry_operations',
    'analyze_naming_patterns',
    'generate_verification_report',
    'quick_verify',
    'get_failed_operations',
    'get_naming_issues'
]

# EOF
