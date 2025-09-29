"""
utility_core.py - Core Utility Implementation for SUGA
Version: 2025.09.29.03
Daily Revision: 01

REVOLUTIONARY ARCHITECTURE - Optimized for Single Universal Gateway
FREE TIER COMPLIANCE: 100% - Lightweight utility functions
"""

import json
import uuid
from typing import Any, Dict, Optional, List
from copy import deepcopy

def validate_type(value: Any, expected_type: type) -> bool:
    """Validate value type."""
    return isinstance(value, expected_type)

def deep_merge(dict1: Dict, dict2: Dict) -> Dict:
    """Deep merge two dictionaries."""
    result = deepcopy(dict1)
    
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = deepcopy(value)
    
    return result

def generate_id(prefix: str = "") -> str:
    """Generate unique ID."""
    unique_id = str(uuid.uuid4())
    return f"{prefix}{unique_id}" if prefix else unique_id

def generate_correlation_id() -> str:
    """Generate correlation ID."""
    return generate_id("corr-")

def safe_json_dumps(data: Any, default: Any = None) -> str:
    """Safely dump JSON."""
    try:
        return json.dumps(data)
    except (TypeError, ValueError):
        if default is not None:
            return json.dumps(default)
        return json.dumps({"error": "Failed to serialize"})

def safe_json_loads(data: str, default: Any = None) -> Any:
    """Safely load JSON."""
    try:
        return json.loads(data)
    except (TypeError, ValueError, json.JSONDecodeError):
        return default

def flatten_dict(d: Dict, parent_key: str = '', sep: str = '.') -> Dict:
    """Flatten nested dictionary."""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)

def unflatten_dict(d: Dict, sep: str = '.') -> Dict:
    """Unflatten dictionary."""
    result = {}
    for key, value in d.items():
        parts = key.split(sep)
        current = result
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]
        current[parts[-1]] = value
    return result

def get_nested_value(d: Dict, path: str, default: Any = None, sep: str = '.') -> Any:
    """Get nested dictionary value by path."""
    keys = path.split(sep)
    current = d
    
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default
    
    return current

def set_nested_value(d: Dict, path: str, value: Any, sep: str = '.') -> Dict:
    """Set nested dictionary value by path."""
    keys = path.split(sep)
    current = d
    
    for key in keys[:-1]:
        if key not in current:
            current[key] = {}
        current = current[key]
    
    current[keys[-1]] = value
    return d

def chunk_list(lst: List, chunk_size: int) -> List[List]:
    """Split list into chunks."""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]

def deduplicate_list(lst: List) -> List:
    """Remove duplicates while preserving order."""
    seen = set()
    result = []
    for item in lst:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result

def filter_dict(d: Dict, keys: List[str], include: bool = True) -> Dict:
    """Filter dictionary by keys."""
    if include:
        return {k: v for k, v in d.items() if k in keys}
    else:
        return {k: v for k, v in d.items() if k not in keys}

def map_dict_values(d: Dict, func: callable) -> Dict:
    """Apply function to all dictionary values."""
    return {k: func(v) for k, v in d.items()}

def merge_dicts(*dicts: Dict) -> Dict:
    """Merge multiple dictionaries."""
    result = {}
    for d in dicts:
        result.update(d)
    return result

def invert_dict(d: Dict) -> Dict:
    """Invert dictionary (swap keys and values)."""
    return {v: k for k, v in d.items()}

def sort_dict(d: Dict, by_key: bool = True, reverse: bool = False) -> Dict:
    """Sort dictionary by keys or values."""
    if by_key:
        return dict(sorted(d.items(), key=lambda x: x[0], reverse=reverse))
    else:
        return dict(sorted(d.items(), key=lambda x: x[1], reverse=reverse))

def safe_divide(a: float, b: float, default: float = 0.0) -> float:
    """Safely divide numbers."""
    try:
        return a / b if b != 0 else default
    except (TypeError, ZeroDivisionError):
        return default

def clamp(value: float, min_value: float, max_value: float) -> float:
    """Clamp value between min and max."""
    return max(min_value, min(max_value, value))

def percentage(part: float, total: float, decimals: int = 2) -> float:
    """Calculate percentage."""
    if total == 0:
        return 0.0
    return round((part / total) * 100, decimals)

def format_bytes(bytes_value: int) -> str:
    """Format bytes as human readable string."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.2f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.2f} PB"

def parse_bool(value: Any) -> bool:
    """Parse boolean from various types."""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in ('true', 'yes', '1', 'on')
    if isinstance(value, (int, float)):
        return value != 0
    return False

def truncate_string(s: str, max_length: int, suffix: str = "...") -> str:
    """Truncate string to max length."""
    if len(s) <= max_length:
        return s
    return s[:max_length - len(suffix)] + suffix

def retry_operation(
    func: callable,
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0
) -> Any:
    """Retry operation with exponential backoff."""
    import time
    
    attempt = 0
    current_delay = delay
    
    while attempt < max_attempts:
        try:
            return func()
        except Exception as e:
            attempt += 1
            if attempt >= max_attempts:
                raise e
            time.sleep(current_delay)
            current_delay *= backoff

def batch_items(items: List, batch_size: int) -> List[List]:
    """Batch items into groups."""
    return chunk_list(items, batch_size)

def get_first_non_none(*values: Any) -> Any:
    """Get first non-None value."""
    for value in values:
        if value is not None:
            return value
    return None

def create_lookup(items: List[Dict], key: str) -> Dict:
    """Create lookup dictionary from list of dicts."""
    return {item[key]: item for item in items if key in item}

def group_by(items: List[Dict], key: str) -> Dict[Any, List[Dict]]:
    """Group items by key value."""
    from collections import defaultdict
    result = defaultdict(list)
    for item in items:
        if key in item:
            result[item[key]].append(item)
    return dict(result)
