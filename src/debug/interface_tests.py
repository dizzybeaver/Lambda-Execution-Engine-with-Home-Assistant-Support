"""
Interface Tests - Comprehensive Testing for All Core Interfaces
Version: 2025.09.29.01
Daily Revision: 001
"""

from gateway import (
    cache_get, cache_set, cache_delete, cache_clear,
    log_debug, log_info, log_warning, log_error,
    validate_request, validate_token, encrypt_data, decrypt_data,
    record_metric, get_metric, increment_counter,
    get_singleton, reset_singleton,
    http_get, http_post,
    format_response, parse_json,
    initialize_lambda,
    get_circuit_breaker, call_with_circuit_breaker,
    get_config, set_config,
    debug_info,
    get_gateway_stats
)

def test_cache_interface():
    """Test cache interface operations."""
    cache_clear()
    
    result = cache_set('test_key', 'test_value', ttl=60)
    assert result == True, "Cache set failed"
    
    value = cache_get('test_key')
    assert value == 'test_value', f"Cache get failed: {value}"
    
    result = cache_delete('test_key')
    assert result == True, "Cache delete failed"
    
    value = cache_get('test_key', default='default')
    assert value == 'default', f"Cache get default failed: {value}"
    
    cache_set('ttl_key', 'ttl_value', ttl=1)
    import time
    time.sleep(2)
    value = cache_get('ttl_key', default='expired')
    assert value == 'expired', "TTL expiration failed"
    
    return True

def test_logging_interface():
    """Test logging interface operations."""
    log_debug("Debug message")
    log_info("Info message")
    log_warning("Warning message")
    
    try:
        raise ValueError("Test error")
    except ValueError as e:
        log_error("Error occurred", error=e)
    
    return True

def test_security_interface():
    """Test security interface operations."""
    request = {'requestType': 'test', 'data': 'value'}
    result = validate_request(request)
    assert result == True, "Request validation failed"
    
    invalid_request = {'data': 'value'}
    result = validate_request(invalid_request)
    assert result == False, "Invalid request not rejected"
    
    token = "dGVzdF90b2tlbl92YWx1ZQ=="
    result = validate_token(token)
    assert result == True, "Token validation failed"
    
    data = {'secret': 'data'}
    encrypted = encrypt_data(data)
    assert isinstance(encrypted, str), "Encryption failed"
    
    decrypted = decrypt_data(encrypted)
    assert decrypted == data, "Decryption failed"
    
    return True

def test_metrics_interface():
    """Test metrics interface operations."""
    record_metric('test_metric', 100.0, unit='Count')
    
    value = get_metric('test_metric')
    assert value == 100.0, f"Metric get failed: {value}"
    
    increment_counter('test_counter', 1.0)
    increment_counter('test_counter', 2.0)
    
    return True

def test_singleton_interface():
    """Test singleton interface operations."""
    class TestSingleton:
        def __init__(self):
            self.value = 'singleton'
    
    instance1 = get_singleton('test_singleton', factory_func=TestSingleton)
    instance2 = get_singleton('test_singleton')
    
    assert instance1 is instance2, "Singleton instances don't match"
    assert instance1.value == 'singleton', "Singleton value incorrect"
    
    result = reset_singleton('test_singleton')
    assert result == True, "Singleton reset failed"
    
    return True

def test_utility_interface():
    """Test utility interface operations."""
    response = format_response(200, {'message': 'success'})
    assert response['statusCode'] == 200, "Response format failed"
    assert 'body' in response, "Response missing body"
    
    json_str = '{"key": "value"}'
    parsed = parse_json(json_str)
    assert parsed == {'key': 'value'}, "JSON parse failed"
    
    return True

def test_initialization_interface():
    """Test initialization interface operations."""
    result = initialize_lambda()
    assert 'status' in result, "Initialization failed"
    
    return True

def test_circuit_breaker_interface():
    """Test circuit breaker interface operations."""
    breaker = get_circuit_breaker('test_breaker', failure_threshold=3, timeout=5)
    assert breaker is not None, "Circuit breaker get failed"
    
    def success_func():
        return 'success'
    
    result = call_with_circuit_breaker('test_breaker', success_func)
    assert result == 'success', "Circuit breaker call failed"
    
    return True

def test_config_interface():
    """Test config interface operations."""
    set_config('test_key', 'test_value')
    value = get_config('test_key')
    assert value == 'test_value', "Config get/set failed"
    
    default_value = get_config('nonexistent', default='default')
    assert default_value == 'default', "Config default failed"
    
    return True

def test_debug_interface():
    """Test debug interface operations."""
    info = debug_info()
    assert 'python_version' in info, "Debug info missing python_version"
    assert 'platform' in info, "Debug info missing platform"
    
    return True

def test_gateway_stats():
    """Test gateway statistics."""
    stats = get_gateway_stats()
    assert 'loaded_modules' in stats, "Stats missing loaded_modules"
    assert 'usage_stats' in stats, "Stats missing usage_stats"
    
    return True

def run_all_tests():
    """Run all interface tests."""
    tests = [
        ('Cache', test_cache_interface),
        ('Logging', test_logging_interface),
        ('Security', test_security_interface),
        ('Metrics', test_metrics_interface),
        ('Singleton', test_singleton_interface),
        ('Utility', test_utility_interface),
        ('Initialization', test_initialization_interface),
        ('Circuit Breaker', test_circuit_breaker_interface),
        ('Config', test_config_interface),
        ('Debug', test_debug_interface),
        ('Gateway Stats', test_gateway_stats)
    ]
    
    results = {}
    for name, test_func in tests:
        try:
            test_func()
            results[name] = 'PASS'
        except Exception as e:
            results[name] = f'FAIL: {str(e)}'
    
    return results

#EOF
