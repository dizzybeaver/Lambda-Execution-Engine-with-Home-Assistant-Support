"""
import_fixer.py
Version: 2025.10.13.01
Description: Utility to fix AWS Lambda incompatible imports across codebase

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

import os
import re
from typing import Dict, List, Set, Tuple


# ===== IMPORT PATTERNS =====

# Patterns that violate AWS Lambda compatibility
VIOLATION_PATTERNS = [
    r'from\s+\.\s+import\s+',  # from . import X
    r'from\s+\.\w+\s+import\s+',  # from .module import X
    r'import\s+\w+\s+#.*local',  # import module # local module comment
]

# Correct patterns for AWS Lambda
CORRECT_PATTERNS = {
    'gateway': 'from gateway import execute_operation, GatewayInterface',
    'metrics_core': 'from metrics_core import _execute_',
    'logging_core': 'from logging_core import _execute_',
    'cache_core': 'from cache_core import _execute_',
    'security_core': 'from security_core import _execute_',
}


# ===== FILE SCANNING =====

def scan_file_for_violations(filepath: str) -> List[Dict[str, any]]:
    """
    Scan a Python file for AWS Lambda import violations.
    
    Args:
        filepath: Path to Python file
    
    Returns:
        List of violation dictionaries
    """
    violations = []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        for line_num, line in enumerate(lines, 1):
            for pattern in VIOLATION_PATTERNS:
                if re.search(pattern, line):
                    violations.append({
                        'file': filepath,
                        'line': line_num,
                        'content': line.strip(),
                        'pattern': pattern
                    })
    
    except Exception as e:
        pass
    
    return violations


def scan_directory_for_violations(directory: str, extensions: Tuple[str, ...] = ('.py',)) -> Dict[str, List]:
    """
    Scan directory recursively for import violations.
    
    Args:
        directory: Root directory to scan
        extensions: File extensions to check
    
    Returns:
        Dictionary mapping filepaths to violations
    """
    all_violations = {}
    
    for root, dirs, files in os.walk(directory):
        # Skip test and __pycache__ directories
        dirs[:] = [d for d in dirs if d not in ('__pycache__', 'tests', '.git')]
        
        for file in files:
            if file.endswith(extensions):
                filepath = os.path.join(root, file)
                violations = scan_file_for_violations(filepath)
                
                if violations:
                    all_violations[filepath] = violations
    
    return all_violations


# ===== IMPORT FIXING =====

def fix_relative_import(line: str) -> str:
    """
    Fix a single relative import line.
    
    Args:
        line: Import line to fix
    
    Returns:
        Fixed import line
    """
    # from . import module
    if re.search(r'from\s+\.\s+import\s+(\w+)', line):
        module = re.search(r'from\s+\.\s+import\s+(\w+)', line).group(1)
        return f"from {module} import"
    
    # from .module import X
    match = re.search(r'from\s+\.(\w+)\s+import\s+(.+)', line)
    if match:
        module = match.group(1)
        imports = match.group(2)
        return f"from {module} import {imports}"
    
    # import module (local) - standardize to from module import
    if 'import' in line and '#' in line and 'local' in line.lower():
        module = re.search(r'import\s+(\w+)', line).group(1)
        return f"from {module} import"
    
    return line


def fix_file_imports(filepath: str, dry_run: bool = True) -> Dict[str, any]:
    """
    Fix import violations in a file.
    
    Args:
        filepath: Path to file to fix
        dry_run: If True, don't write changes
    
    Returns:
        Dictionary with fix results
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        fixed_lines = []
        changes = []
        
        for line_num, line in enumerate(lines, 1):
            fixed_line = line
            
            for pattern in VIOLATION_PATTERNS:
                if re.search(pattern, line):
                    fixed_line = fix_relative_import(line)
                    changes.append({
                        'line': line_num,
                        'original': line.strip(),
                        'fixed': fixed_line.strip()
                    })
            
            fixed_lines.append(fixed_line)
        
        if not dry_run and changes:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.writelines(fixed_lines)
        
        return {
            'file': filepath,
            'changes': len(changes),
            'details': changes,
            'success': True
        }
    
    except Exception as e:
        return {
            'file': filepath,
            'changes': 0,
            'error': str(e),
            'success': False
        }


# ===== REPORTING =====

def generate_violation_report(violations: Dict[str, List]) -> str:
    """
    Generate human-readable violation report.
    
    Args:
        violations: Dictionary of violations per file
    
    Returns:
        Formatted report string
    """
    if not violations:
        return "✅ No import violations found!"
    
    report_lines = [
        "=" * 80,
        "AWS LAMBDA IMPORT VIOLATIONS REPORT",
        "=" * 80,
        "",
        f"Total Files with Violations: {len(violations)}",
        f"Total Violations: {sum(len(v) for v in violations.values())}",
        "",
    ]
    
    for filepath, file_violations in sorted(violations.items()):
        report_lines.append(f"\n📄 {filepath}")
        report_lines.append("-" * 80)
        
        for violation in file_violations:
            report_lines.append(f"  Line {violation['line']}: {violation['content']}")
        
        report_lines.append("")
    
    report_lines.extend([
        "=" * 80,
        "RECOMMENDED FIXES:",
        "=" * 80,
        "",
        "1. Run: python import_fixer.py --fix <directory>",
        "2. Or manually replace:",
        "   - 'from . import X' → 'from X import'",
        "   - 'from .module import X' → 'from module import X'",
        "   - 'import gateway' → 'from gateway import execute_operation'",
        ""
    ])
    
    return "\n".join(report_lines)


# ===== VALIDATION =====

def validate_fixed_imports(filepath: str) -> bool:
    """
    Validate that file has no import violations.
    
    Args:
        filepath: Path to file to validate
    
    Returns:
        True if no violations found
    """
    violations = scan_file_for_violations(filepath)
    return len(violations) == 0


def validate_directory_imports(directory: str) -> Dict[str, bool]:
    """
    Validate all files in directory.
    
    Args:
        directory: Directory to validate
    
    Returns:
        Dictionary mapping filepaths to validation status
    """
    violations = scan_directory_for_violations(directory)
    
    results = {}
    
    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if d not in ('__pycache__', 'tests', '.git')]
        
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                results[filepath] = filepath not in violations
    
    return results


# ===== STATISTICS =====

def get_import_statistics(directory: str) -> Dict[str, any]:
    """
    Get statistics about imports in codebase.
    
    Args:
        directory: Directory to analyze
    
    Returns:
        Dictionary with import statistics
    """
    violations = scan_directory_for_violations(directory)
    validation = validate_directory_imports(directory)
    
    total_files = len(validation)
    clean_files = sum(1 for v in validation.values() if v)
    violation_files = len(violations)
    total_violations = sum(len(v) for v in violations.values())
    
    return {
        'total_python_files': total_files,
        'clean_files': clean_files,
        'files_with_violations': violation_files,
        'total_violations': total_violations,
        'compliance_rate_percent': round((clean_files / total_files * 100) if total_files > 0 else 0, 2)
    }


# ===== MAIN INTERFACE =====

def check_imports(directory: str = '.', report: bool = True) -> Dict[str, any]:
    """
    Check directory for import violations.
    
    Args:
        directory: Directory to check
        report: Generate and print report
    
    Returns:
        Results dictionary
    """
    violations = scan_directory_for_violations(directory)
    stats = get_import_statistics(directory)
    
    results = {
        'violations': violations,
        'statistics': stats,
        'compliant': len(violations) == 0
    }
    
    if report:
        print(generate_violation_report(violations))
        print("\nSTATISTICS:")
        print(f"  Total Files: {stats['total_python_files']}")
        print(f"  Clean Files: {stats['clean_files']}")
        print(f"  Violations: {stats['files_with_violations']} files, {stats['total_violations']} issues")
        print(f"  Compliance Rate: {stats['compliance_rate_percent']}%")
    
    return results


def fix_imports(directory: str = '.', dry_run: bool = False) -> Dict[str, any]:
    """
    Fix import violations in directory.
    
    Args:
        directory: Directory to fix
        dry_run: If True, don't write changes
    
    Returns:
        Results dictionary
    """
    violations = scan_directory_for_violations(directory)
    
    if not violations:
        return {
            'success': True,
            'message': 'No violations found',
            'files_fixed': 0
        }
    
    fix_results = []
    
    for filepath in violations.keys():
        result = fix_file_imports(filepath, dry_run=dry_run)
        fix_results.append(result)
    
    total_changes = sum(r['changes'] for r in fix_results if r['success'])
    
    return {
        'success': True,
        'files_fixed': len([r for r in fix_results if r['success']]),
        'total_changes': total_changes,
        'results': fix_results,
        'dry_run': dry_run
    }


# ===== EXPORTED FUNCTIONS =====

__all__ = [
    'scan_file_for_violations',
    'scan_directory_for_violations',
    'fix_file_imports',
    'validate_fixed_imports',
    'validate_directory_imports',
    'get_import_statistics',
    'generate_violation_report',
    'check_imports',
    'fix_imports'
]

# EOF
