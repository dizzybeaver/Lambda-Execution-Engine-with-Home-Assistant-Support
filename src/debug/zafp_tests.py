"""
zafp_tests.py - ZAFP Testing
Version: 2025.09.29.07
Daily Revision: Phase 5 Zero-Abstraction Fast Path Tests

Tests for Zero-Abstraction Fast Path system
Validates hot path detection and performance improvements
"""

import time
from typing import Dict, Any

def run_zafp_tests() -> Dict[str, Any]:
    """Run all ZAFP tests."""
    print("\n" + "="*80)
    print("PHASE 5: ZERO-ABSTRACTION FAST PATH TESTS")
    print("Testing ZAFP System with Hot Path Detection")
    print("="*80 + "\n")
    
    results = {
        "total_tests": 0,
        "passed": 0,
        "failed": 0,
        "tests": []
    }
    
    tests = [
        test_fast_path_system_creation,
        test_operation_tracking,
        test_hot_operation_detection,
        test_fast_path_registration,
        test_fast_path_execution,
        test_cache_fast_path,
        test_logging_fast_path,
        test_metrics_fast_path,
        test_gateway_fast_path_integration,
        test_fast_path_statistics,
        test_fast_path_performance,
        test_normal_path_fallback,
        test_fast_path_config,
        test_hot_threshold_detection
    ]
    
    for test_func in tests:
        results["total_tests"] += 1
        test_name = test_func.__name__
        
        try:
            print(f"Running: {test_name}...")
            test_result = test_func()
            
            if test_result.get("success", False):
                results["passed"] += 1
                print(f"  ✅ PASSED: {test_result.get('message', 'Test passed')}")
            else:
                results["failed"] += 1
                print(f"  ❌ FAILED: {test_result.get('error', 'Test failed')}")
            
            results["tests"].append({
                "name": test_name,
                "success": test_result.get("success", False),
                "message": test_result.get("message", test_result.get("error", ""))
            })
            
        except Exception as e:
            results["failed"] += 1
            print(f"  ❌ EXCEPTION: {str(e)}")
            results["tests"].append({
                "name": test_name,
                "success": False,
                "message": f"Exception: {str(e)}"
            })
    
    print("\n" + "="*80)
    print(f"ZAFP TEST RESULTS")
    print(f"Total Tests: {results['total_tests']}")
    print(f"Passed: {results['passed']}")
    print(f"Failed: {results['failed']}")
    print(f"Success Rate: {(results['passed']/results['total_tests']*100):.1f}%")
    print("="*80 + "\n")
    
    return results

def test_fast_path_system_creation() -> Dict[str, Any]:
    """Test FastPathSystem creation."""
    try:
        from fast_path import FastPathSystem, FastPathConfig
        
        config = FastPathConfig()
        system = FastPathSystem(config)
        
        if system and system.config:
            return {
                "success": True,
                "message": "FastPathSystem created successfully"
            }
        else:
            return {
                "success": False,
                "error": "FastPathSystem creation failed"
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"FastPathSystem test failed: {str(e)}"
        }

def test_operation_tracking() -> Dict[str, Any]:
    """Test operation tracking."""
    try:
        from fast_path import FastPathSystem
        
        system = FastPathSystem()
        system.track_operation("test.operation", 10.5)
        
        stats = system.get_operation_stats("test.operation")
        
        if stats and stats.call_count == 1:
            return {
                "success": True,
                "message": f"Operation tracked: {stats.call_count} calls"
            }
        else:
            return {
                "success": False,
                "error": "Operation tracking failed"
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Operation tracking test failed: {str(e)}"
        }

def test_hot_operation_detection() -> Dict[str, Any]:
    """Test hot operation detection."""
    try:
        from fast_path import FastPathSystem, FastPathConfig
        
        config = FastPathConfig(hot_threshold_calls=5, hot_threshold_frequency=0.5)
        system = FastPathSystem(config)
        
        for i in range(10):
            system.track_operation("hot.operation", 5.0)
        
        is_hot = system.is_hot_operation("hot.operation")
        
        if is_hot:
            return {
                "success": True,
                "message": "Hot operation detected after 10 calls"
            }
        else:
            return {
                "success": False,
                "error": "Hot operation detection failed"
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Hot detection test failed: {str(e)}"
        }

def test_fast_path_registration() -> Dict[str, Any]:
    """Test fast path registration."""
    try:
        from fast_path import FastPathSystem
        
        system = FastPathSystem()
        
        def test_fast_func(*args, **kwargs):
            return "fast_result"
        
        system.register_fast_path("test.fast", test_fast_func)
        
        fast_func = system.get_fast_path("test.fast")
        
        if fast_func and fast_func() == "fast_result":
            return {
                "success": True,
                "message": "Fast path registered and retrieved"
            }
        else:
            return {
                "success": False,
                "error": "Fast path registration failed"
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Fast path registration test failed: {str(e)}"
        }

def test_fast_path_execution() -> Dict[str, Any]:
    """Test fast path execution."""
    try:
        from fast_path import FastPathSystem, FastPathConfig
        
        config = FastPathConfig(hot_threshold_calls=2, hot_threshold_frequency=0.5)
        system = FastPathSystem(config)
        
        def normal_func(*args, **kwargs):
            return "normal"
        
        def fast_func(*args, **kwargs):
            return "fast"
        
        system.register_fast_path("test.exec", fast_func)
        
        for i in range(5):
            system.track_operation("test.exec", 5.0)
        
        result = system.execute_with_fast_path("test.exec", normal_func, fast_func)
        
        if result == "fast":
            return {
                "success": True,
                "message": "Fast path executed successfully"
            }
        else:
            return {
                "success": False,
                "error": f"Expected 'fast', got '{result}'"
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Fast path execution test failed: {str(e)}"
        }

def test_cache_fast_path() -> Dict[str, Any]:
    """Test cache fast path functions."""
    try:
        from fast_path import cache_get_fast_path, cache_set_fast_path
        
        cache_set_fast_path("test_key", "test_value", ttl=60)
        result = cache_get_fast_path("test_key")
        
        if result == "test_value":
            return {
                "success": True,
                "message": "Cache fast path working"
            }
        else:
            return {
                "success": False,
                "error": f"Expected 'test_value', got '{result}'"
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Cache fast path test failed: {str(e)}"
        }

def test_logging_fast_path() -> Dict[str, Any]:
    """Test logging fast path functions."""
    try:
        from fast_path import log_info_fast_path, log_error_fast_path
        
        log_info_fast_path("Test info message")
        log_error_fast_path("Test error message")
        
        return {
            "success": True,
            "message": "Logging fast path working"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Logging fast path test failed: {str(e)}"
        }

def test_metrics_fast_path() -> Dict[str, Any]:
    """Test metrics fast path function."""
    try:
        from fast_path import record_metric_fast_path
        
        result = record_metric_fast_path("test_metric", 42.0, {"test": "dimension"})
        
        if result:
            return {
                "success": True,
                "message": "Metrics fast path working"
            }
        else:
            return {
                "success": False,
                "error": "Metrics fast path failed"
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Metrics fast path test failed: {str(e)}"
        }

def test_gateway_fast_path_integration() -> Dict[str, Any]:
    """Test gateway integration with fast path."""
    try:
        from gateway import get_gateway_stats, enable_fast_path, get_fast_path_stats
        
        enable_fast_path()
        
        stats = get_gateway_stats()
        
        if "fast_path_enabled" in stats and stats["fast_path_enabled"]:
            return {
                "success": True,
                "message": "Gateway fast path integration working"
            }
        else:
            return {
                "success": False,
                "error": "Gateway fast path not enabled"
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Gateway integration test failed: {str(e)}"
        }

def test_fast_path_statistics() -> Dict[str, Any]:
    """Test fast path statistics."""
    try:
        from fast_path import get_fast_path_stats, FastPathSystem
        
        system = FastPathSystem()
        system.track_operation("test.stats", 5.0)
        
        stats = system.get_stats()
        
        if "total_operations" in stats and stats["total_operations"] > 0:
            return {
                "success": True,
                "message": f"Stats collected: {stats['total_operations']} operations"
            }
        else:
            return {
                "success": False,
                "error": "Statistics not collected"
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Statistics test failed: {str(e)}"
        }

def test_fast_path_performance() -> Dict[str, Any]:
    """Test fast path performance improvement."""
    try:
        from fast_path import FastPathSystem, FastPathConfig
        
        config = FastPathConfig(hot_threshold_calls=5)
        system = FastPathSystem(config)
        
        def normal_func():
            time.sleep(0.001)
            return "normal"
        
        def fast_func():
            return "fast"
        
        system.register_fast_path("perf.test", fast_func)
        
        for i in range(10):
            system.track_operation("perf.test", 5.0)
        
        start = time.time()
        result = system.execute_with_fast_path("perf.test", normal_func, fast_func)
        fast_time = time.time() - start
        
        if result == "fast" and fast_time < 0.001:
            return {
                "success": True,
                "message": f"Fast path executed in {fast_time*1000:.2f}ms"
            }
        else:
            return {
                "success": False,
                "error": "Performance improvement not detected"
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Performance test failed: {str(e)}"
        }

def test_normal_path_fallback() -> Dict[str, Any]:
    """Test fallback to normal path when not hot."""
    try:
        from fast_path import FastPathSystem
        
        system = FastPathSystem()
        
        def normal_func():
            return "normal"
        
        def fast_func():
            return "fast"
        
        result = system.execute_with_fast_path("cold.operation", normal_func, fast_func)
        
        if result == "normal":
            return {
                "success": True,
                "message": "Normal path fallback working"
            }
        else:
            return {
                "success": False,
                "error": f"Expected 'normal', got '{result}'"
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Fallback test failed: {str(e)}"
        }

def test_fast_path_config() -> Dict[str, Any]:
    """Test fast path configuration."""
    try:
        from fast_path import FastPathConfig
        
        config = FastPathConfig(
            hot_threshold_calls=20,
            hot_threshold_frequency=0.75,
            enable_profiling=True,
            enable_fast_path=True
        )
        
        if (config.hot_threshold_calls == 20 and 
            config.hot_threshold_frequency == 0.75 and
            config.enable_profiling and config.enable_fast_path):
            return {
                "success": True,
                "message": "Fast path configuration working"
            }
        else:
            return {
                "success": False,
                "error": "Configuration values incorrect"
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Config test failed: {str(e)}"
        }

def test_hot_threshold_detection() -> Dict[str, Any]:
    """Test hot threshold detection with different frequencies."""
    try:
        from fast_path import FastPathSystem, FastPathConfig
        
        config = FastPathConfig(hot_threshold_calls=10, hot_threshold_frequency=0.6)
        system = FastPathSystem(config)
        
        for i in range(20):
            if i < 15:
                system.track_operation("frequent.op", 5.0)
            else:
                system.track_operation("infrequent.op", 5.0)
        
        frequent_hot = system.is_hot_operation("frequent.op")
        infrequent_hot = system.is_hot_operation("infrequent.op")
        
        if frequent_hot and not infrequent_hot:
            return {
                "success": True,
                "message": "Hot threshold detection accurate"
            }
        else:
            return {
                "success": False,
                "error": f"Frequent: {frequent_hot}, Infrequent: {infrequent_hot}"
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Threshold test failed: {str(e)}"
        }

if __name__ == "__main__":
    results = run_zafp_tests()
    
    if results["failed"] > 0:
        print(f"\n⚠️ {results['failed']} test(s) failed")
        exit(1)
    else:
        print("\n✅ All ZAFP tests passed!")
        exit(0)

# EOF
