"""
legacy_elimination_patterns.py - Legacy Code Elimination Utilities
Version: 2025.09.29.01
Description: Utilities for identifying and replacing legacy patterns with gateway equivalents

ELIMINATES:
- âŒ Manual threading patterns -> singleton.coordinate_operation
- âŒ Manual memory management -> singleton.optimize_memory
- âŒ Direct cache management -> cache.cache_operation_result
- âŒ Manual validation -> security.validate_input

Licensed under the Apache License, Version 2.0
"""

from typing import Dict, Any, Callable, Optional, List
import re

LEGACY_PATTERNS = {
    'manual_threading': {
        'patterns': [
            r'import threading',
            r'threading\.RLock\(\)',
            r'threading\.Lock\(\)',
            r'with self\._lock:',
            r'self\._lock = threading\.',
        ],
        'replacement': 'singleton.coordinate_operation',
        'example': '''
# OLD (LEGACY):
import threading
self._lock = threading.RLock()
with self._lock:
    result = function()

# NEW (GATEWAY):
from . import singleton
result = singleton.coordinate_operation(function)
'''
    },
    'manual_memory_management': {
        'patterns': [
            r'import gc',
            r'gc\.collect\(\)',
            r'sys\.getsizeof\(',
            r'weakref\.WeakValueDictionary',
        ],
        'replacement': 'singleton.optimize_memory',
        'example': '''
# OLD (LEGACY):
import gc
gc.collect()
memory_size = sys.getsizeof(obj)

# NEW (GATEWAY):
from . import singleton
memory_stats = singleton.get_memory_stats()
singleton.optimize_memory()
'''
    },
    'direct_cache_management': {
        'patterns': [
            r'from functools import lru_cache',
            r'@lru_cache\(maxsize=\d+\)',
            r'cache\.clear\(\)',
        ],
        'replacement': 'cache.cache_operation_result',
        'example': '''
# OLD (LEGACY):
from functools import lru_cache
@lru_cache(maxsize=128)
def function():
    pass

# NEW (GATEWAY):
from . import cache
from .shared_utilities import cache_operation_result
result = cache_operation_result("operation_name", function)
'''
    },
    'manual_validation': {
        'patterns': [
            r'if not isinstance\(value, str\)',
            r'if len\(value\) < \d+ or len\(value\) > \d+',
            r'if not re\.match\(',
        ],
        'replacement': 'security.validate_input',
        'example': '''
# OLD (LEGACY):
if not isinstance(value, str):
    raise ValueError("Invalid type")
if len(value) < 1 or len(value) > 100:
    raise ValueError("Invalid length")

# NEW (GATEWAY):
from . import security
validation = security.validate_input({'value': value})
if not validation.get('valid', False):
    raise ValueError("Validation failed")
'''
    },
    'manual_metrics': {
        'patterns': [
            r'def track_.*?\(.*?\):',
            r'metrics_dict\[.*?\] = ',
            r'self\.metrics\[.*?\] \+= ',
        ],
        'replacement': 'metrics.record_metric',
        'example': '''
# OLD (LEGACY):
self.metrics['operation_count'] += 1
self.metrics['execution_time'] = duration

# NEW (GATEWAY):
from . import metrics
metrics.record_metric('operation_count', 1.0)
metrics.record_metric('execution_time', duration)
'''
    },
    'manual_logging': {
        'patterns': [
            r'logging\.getLogger\(__name__\)',
            r'logger\.info\(f"',
            r'logger\.error\(f"',
        ],
        'replacement': 'logging.log_info / logging.log_error',
        'example': '''
# OLD (LEGACY):
import logging
logger = logging.getLogger(__name__)
logger.info(f"Operation completed: {op}")

# NEW (GATEWAY):
from . import logging
logging.log_info("Operation completed", {'operation': op})
'''
    },
    'direct_config_access': {
        'patterns': [
            r'self\.config\[.*?\]',
            r'config_dict\.get\(',
            r'DEFAULT_CONFIG = \{',
        ],
        'replacement': 'config.get_interface_configuration',
        'example': '''
# OLD (LEGACY):
DEFAULT_CONFIG = {'max_size': 1000}
max_size = self.config.get('max_size', 1000)

# NEW (GATEWAY):
from . import config
cfg = config.get_interface_configuration("interface_name", "production")
max_size = cfg.get('max_size', 1000)
'''
    }
}

def scan_file_for_legacy_patterns(file_content: str) -> Dict[str, List[str]]:
    """
    Scan file content for legacy patterns.
    Returns dict of pattern_type -> list of matches.
    """
    findings = {}
    
    for pattern_type, pattern_info in LEGACY_PATTERNS.items():
        matches = []
        for pattern in pattern_info['patterns']:
            found = re.findall(pattern, file_content)
            if found:
                matches.extend(found)
        
        if matches:
            findings[pattern_type] = {
                'matches': matches,
                'count': len(matches),
                'replacement': pattern_info['replacement'],
                'example': pattern_info['example']
            }
    
    return findings

def generate_replacement_suggestions(findings: Dict[str, Any]) -> List[Dict[str, str]]:
    """
    Generate replacement suggestions for legacy patterns found.
    """
    suggestions = []
    
    for pattern_type, info in findings.items():
        suggestion = {
            'pattern_type': pattern_type,
            'occurrences': info['count'],
            'legacy_pattern': ', '.join(set(info['matches'])),
            'recommended_replacement': info['replacement'],
            'example': info['example']
        }
        suggestions.append(suggestion)
    
    return suggestions

def create_legacy_elimination_report(file_path: str, file_content: str) -> Dict[str, Any]:
    """
    Create comprehensive legacy elimination report for a file.
    """
    findings = scan_file_for_legacy_patterns(file_content)
    suggestions = generate_replacement_suggestions(findings)
    
    total_legacy_patterns = sum(f['count'] for f in findings.values())
    
    report = {
        'file_path': file_path,
        'total_legacy_patterns_found': total_legacy_patterns,
        'patterns_by_type': findings,
        'replacement_suggestions': suggestions,
        'priority': 'HIGH' if total_legacy_patterns > 10 else 'MEDIUM' if total_legacy_patterns > 5 else 'LOW',
        'estimated_memory_reduction': f"{total_legacy_patterns * 2}KB"
    }
    
    return report

def auto_replace_simple_patterns(file_content: str, pattern_type: str) -> str:
    """
    Automatically replace simple legacy patterns with gateway equivalents.
    Only handles straightforward replacements.
    """
    if pattern_type not in LEGACY_PATTERNS:
        return file_content
    
    pattern_info = LEGACY_PATTERNS[pattern_type]
    
    replacements = {
        'manual_threading': [
            (r'import threading\n', ''),
            (r'self\._lock = threading\.RLock\(\)\n', ''),
            (r'with self\._lock:\n\s+(.*)', r'from . import singleton\n\1 = singleton.coordinate_operation(lambda: \1)'),
        ],
        'manual_memory_management': [
            (r'import gc\n', ''),
            (r'gc\.collect\(\)', 'from . import singleton\nsingleton.optimize_memory()'),
        ],
        'direct_cache_management': [
            (r'from functools import lru_cache\n', ''),
            (r'@lru_cache\(maxsize=\d+\)\n', ''),
        ],
    }
    
    if pattern_type in replacements:
        for old_pattern, new_pattern in replacements[pattern_type]:
            file_content = re.sub(old_pattern, new_pattern, file_content)
    
    return file_content

def validate_gateway_usage(file_content: str) -> Dict[str, Any]:
    """
    Validate that file is using gateway patterns correctly.
    """
    gateway_imports = {
        'cache': r'from \. import cache',
        'singleton': r'from \. import singleton',
        'security': r'from \. import security',
        'metrics': r'from \. import metrics',
        'logging': r'from \. import logging',
        'config': r'from \. import config',
        'utility': r'from \. import utility',
    }
    
    usage = {}
    for gateway, pattern in gateway_imports.items():
        found = re.search(pattern, file_content)
        usage[gateway] = {
            'imported': found is not None,
            'usage_count': len(re.findall(f'{gateway}\\.', file_content))
        }
    
    total_gateway_usage = sum(u['usage_count'] for u in usage.values())
    legacy_patterns = scan_file_for_legacy_patterns(file_content)
    total_legacy = sum(f['count'] for f in legacy_patterns.values())
    
    gateway_utilization = (total_gateway_usage / (total_gateway_usage + total_legacy)) * 100 if (total_gateway_usage + total_legacy) > 0 else 0
    
    return {
        'gateway_usage': usage,
        'total_gateway_calls': total_gateway_usage,
        'total_legacy_patterns': total_legacy,
        'gateway_utilization_percentage': gateway_utilization,
        'optimization_status': 'ULTRA-OPTIMIZED' if gateway_utilization > 90 else 'OPTIMIZED' if gateway_utilization > 70 else 'NEEDS_OPTIMIZATION'
    }

def generate_optimization_roadmap(files: List[str]) -> Dict[str, Any]:
    """
    Generate optimization roadmap for multiple files.
    """
    roadmap = {
        'total_files': len(files),
        'files_by_priority': {'HIGH': [], 'MEDIUM': [], 'LOW': []},
        'total_legacy_patterns': 0,
        'estimated_total_memory_reduction': 0
    }
    
    for file_path in files:
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            report = create_legacy_elimination_report(file_path, content)
            roadmap['files_by_priority'][report['priority']].append({
                'file': file_path,
                'legacy_patterns': report['total_legacy_patterns_found']
            })
            roadmap['total_legacy_patterns'] += report['total_legacy_patterns_found']
        except Exception:
            pass
    
    roadmap['estimated_total_memory_reduction'] = f"{roadmap['total_legacy_patterns'] * 2}KB"
    
    return roadmap

__all__ = [
    'LEGACY_PATTERNS',
    'scan_file_for_legacy_patterns',
    'generate_replacement_suggestions',
    'create_legacy_elimination_report',
    'auto_replace_simple_patterns',
    'validate_gateway_usage',
    'generate_optimization_roadmap'
]

# EOF
