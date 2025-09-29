"""
debug_core.py - Core Debug Implementation for SUGA
Version: 2025.09.29.03
Daily Revision: 01

REVOLUTIONARY ARCHITECTURE - Optimized for Single Universal Gateway
FREE TIER COMPLIANCE: 100% - Debug and testing utilities
"""

import sys
import time
import traceback
from typing import Any, Dict, Optional, List

def debug_inspect(obj: Any, max_depth: int = 3, current_depth: int = 0) -> Dict[str, Any]:
    """Inspect object for debugging."""
    if current_depth >= max_depth:
        return {"type": type(obj).__name__, "value": str(obj)[:100]}
    
    result = {
        "type": type(obj).__name__,
        "repr": repr(obj)[:200]
    }
    
    if isinstance(obj, dict):
        result["length"] = len(obj)
        result["keys"] = list(obj.keys())[:10]
        if current_depth < max_depth - 1:
            result["sample"] = {
                k: debug_inspect(v, max_depth, current_depth + 1)
                for k, v in list(obj.items())[:3]
            }
    elif isinstance(obj, (list, tuple)):
        result["length"] = len(obj)
        if current_depth < max_depth - 1:
            result["sample"] = [
                debug_inspect(item, max_depth, current_depth + 1)
                for item in obj[:3]
            ]
    elif hasattr(obj, '__dict__'):
        result["attributes"] = list(obj.__dict__.keys())[:10]
    
    return result

def get_memory_usage() -> Dict[str, Any]:
    """Get memory usage information."""
    import resource
    usage = resource.getrusage(resource.RUSAGE_SELF)
    
    return {
        "max_rss_mb": usage.ru_maxrss / 1024 / 1024,
        "user_time": usage.ru_utime,
        "system_time": usage.ru_stime
    }

def get_system_info() -> Dict[str, Any]:
    """Get system information."""
    return {
        "python_version": sys.version,
        "platform": sys.platform,
        "modules_loaded": len(sys.modules),
        "recursion_limit": sys.getrecursionlimit()
    }

def trace_execution(func: callable, *args, **kwargs) -> Dict[str, Any]:
    """Trace function execution."""
    start_time = time.time()
    error = None
    result = None
    
    try:
        result = func(*args, **kwargs)
    except Exception as e:
        error = e
        traceback_str = ''.join(traceback.format_tb(e.__traceback__))
    
    duration = time.time() - start_time
    
    return {
        "duration": duration,
        "success": error is None,
        "error": str(error) if error else None,
        "error_type": type(error).__name__ if error else None,
        "traceback": traceback_str if error else None,
        "result_type": type(result).__name__ if result is not None else None
    }

def validate_imports() -> Dict[str, Any]:
    """Validate no forbidden imports."""
    forbidden = [
        'psutil', 'PIL', 'numpy', 'pandas', 'scipy',
        'tensorflow', 'torch', 'sklearn', 'matplotlib',
        'seaborn', 'lxml', 'beautifulsoup4'
    ]
    
    found_forbidden = []
    for module in sys.modules.keys():
        module_base = module.split('.')[0]
        if module_base in forbidden:
            found_forbidden.append(module_base)
    
    return {
        "valid": len(found_forbidden) == 0,
        "forbidden_found": list(set(found_forbidden)),
        "total_modules": len(sys.modules)
    }

def get_module_info(module_name: str) -> Dict[str, Any]:
    """Get information about a loaded module."""
    if module_name not in sys.modules:
        return {"exists": False}
    
    module = sys.modules[module_name]
    
    return {
        "exists": True,
        "name": module.__name__,
        "file": getattr(module, '__file__', None),
        "package": getattr(module, '__package__', None),
        "version": getattr(module, '__version__', None)
    }

def list_loaded_modules(filter_prefix: Optional[str] = None) -> List[str]:
    """List all loaded modules."""
    modules = list(sys.modules.keys())
    
    if filter_prefix:
        modules = [m for m in modules if m.startswith(filter_prefix)]
    
    return sorted(modules)

def benchmark_operation(operation: callable, iterations: int = 100) -> Dict[str, Any]:
    """Benchmark an operation."""
    times = []
    
    for _ in range(iterations):
        start = time.time()
        try:
            operation()
            duration = time.time() - start
            times.append(duration)
        except Exception:
            pass
    
    if not times:
        return {"success": False, "error": "All iterations failed"}
    
    times.sort()
    return {
        "success": True,
        "iterations": len(times),
        "min": min(times),
        "max": max(times),
        "avg": sum(times) / len(times),
        "median": times[len(times) // 2],
        "p95": times[int(len(times) * 0.95)],
        "p99": times[int(len(times) * 0.99)]
    }

def check_free_tier_compliance() -> Dict[str, Any]:
    """Check AWS free tier compliance."""
    memory_usage = get_memory_usage()
    imports = validate_imports()
    
    issues = []
    if memory_usage["max_rss_mb"] > 128:
        issues.append(f"Memory usage {memory_usage['max_rss_mb']:.2f}MB exceeds 128MB limit")
    
    if not imports["valid"]:
        issues.append(f"Forbidden imports found: {imports['forbidden_found']}")
    
    return {
        "compliant": len(issues) == 0,
        "issues": issues,
        "memory_mb": memory_usage["max_rss_mb"],
        "forbidden_imports": imports["forbidden_found"]
    }

def get_debug_stats() -> Dict[str, Any]:
    """Get debug statistics."""
    return {
        "memory": get_memory_usage(),
        "system": get_system_info(),
        "imports": validate_imports(),
        "free_tier": check_free_tier_compliance()
    }

def profile_memory(func: callable, *args, **kwargs) -> Dict[str, Any]:
    """Profile memory usage of a function."""
    import gc
    gc.collect()
    
    before = get_memory_usage()
    start_time = time.time()
    
    result = None
    error = None
    try:
        result = func(*args, **kwargs)
    except Exception as e:
        error = e
    
    duration = time.time() - start_time
    after = get_memory_usage()
    
    return {
        "duration": duration,
        "memory_before_mb": before["max_rss_mb"],
        "memory_after_mb": after["max_rss_mb"],
        "memory_delta_mb": after["max_rss_mb"] - before["max_rss_mb"],
        "success": error is None,
        "error": str(error) if error else None
    }

def create_test_data(data_type: str, size: int = 100) -> Any:
    """Create test data for debugging."""
    if data_type == "dict":
        return {f"key_{i}": f"value_{i}" for i in range(size)}
    elif data_type == "list":
        return [f"item_{i}" for i in range(size)]
    elif data_type == "nested_dict":
        return {
            f"level1_{i}": {
                f"level2_{j}": f"value_{i}_{j}"
                for j in range(min(size // 10, 10))
            }
            for i in range(min(size, 10))
        }
    else:
        raise ValueError(f"Unsupported data type: {data_type}")

def validate_response(response: Dict[str, Any]) -> Dict[str, Any]:
    """Validate Lambda response structure."""
    required_keys = ["statusCode"]
    missing_keys = [k for k in required_keys if k not in response]
    
    warnings = []
    if "body" not in response:
        warnings.append("Missing 'body' key")
    if "headers" not in response:
        warnings.append("Missing 'headers' key")
    
    return {
        "valid": len(missing_keys) == 0,
        "missing_keys": missing_keys,
        "warnings": warnings,
        "has_body": "body" in response,
        "has_headers": "headers" in response,
        "status_code": response.get("statusCode")
    }
