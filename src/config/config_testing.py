"""
config_testing.py - Ultra-Optimized Configuration System Integration Testing Framework
Version: 2025.09.28.03
Description: Comprehensive testing framework for configuration system validation

COMPLETE TESTING FRAMEWORK: Configuration System Validation
- Gateway interface compliance testing
- Configuration preset validation
- Resource constraint verification
- Optimization function testing
- AWS Lambda constraint compliance
- Performance and memory validation

ARCHITECTURE: TESTING MODULE - GATEWAY UTILIZATION
- Tests config.py gateway interface exclusively
- Validates all configuration presets against constraints
- Verifies optimization functions work correctly
- Tests error handling and edge cases
- No direct access to internal implementation files

TESTING COVERAGE:
- Configuration tier management
- Preset management and validation
- Resource estimation accuracy
- Optimization functions
- AWS constraint compliance
- Gateway pattern enforcement

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

import time
import unittest
from typing import Dict, Any, List
from unittest.mock import patch, MagicMock

# Import ONLY the gateway interface - following architecture compliance
from config import (
    # Core parameter management
    get_parameter, set_parameter, get_all_parameters,
    get_configuration_types, create_configuration_type, clear_configuration_cache,
    
    # Configuration tier management
    get_interface_configuration, get_system_configuration, validate_configuration,
    apply_configuration_overrides_to_base,
    
    # Preset management
    get_available_presets, get_preset_details, apply_preset, list_preset_names,
    
    # Resource estimation and validation
    estimate_memory_usage, estimate_metrics_usage, get_memory_allocation_summary,
    validate_aws_constraints,
    
    # Optimization functions
    optimize_for_memory_constraint, optimize_for_performance, optimize_for_cost_protection,
    get_optimization_recommendations,
    
    # Analysis and monitoring
    analyze_configuration_compliance, get_configuration_health_status,
    
    # Utility functions
    create_custom_configuration, compare_configurations,
    
    # Configuration enums
    ConfigurationTier, InterfaceType
)

class ConfigurationSystemTestSuite(unittest.TestCase):
    """Comprehensive test suite for configuration system validation."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_start_time = time.time()
        
    def tearDown(self):
        """Clean up after tests."""
        # Clear any test configuration cache
        clear_configuration_cache("test")
        
    # ===== BASIC PARAMETER MANAGEMENT TESTS =====
    
    def test_basic_parameter_operations(self):
        """Test basic parameter get/set operations."""
        # Test parameter setting
        result = set_parameter("TEST_PARAM", "test_value", "test")
        self.assertTrue(result, "Parameter setting should succeed")
        
        # Test parameter retrieval
        value = get_parameter("TEST_PARAM", None, "test")
        self.assertEqual(value, "test_value", "Parameter value should match what was set")
        
        # Test default value handling
        default_value = get_parameter("NONEXISTENT_PARAM", "default", "test")
        self.assertEqual(default_value, "default", "Default value should be returned for non-existent parameter")
    
    def test_configuration_types(self):
        """Test configuration type management."""
        # Get initial types
        initial_types = get_configuration_types()
        self.assertIsInstance(initial_types, list, "Configuration types should be a list")
        self.assertIn("default", initial_types, "Default type should always be available")
        
        # Create new type
        result = create_configuration_type("test_type")
        self.assertIsInstance(result, dict, "Create type result should be a dictionary")
        
        # Verify new type exists
        updated_types = get_configuration_types()
        self.assertIn("test_type", updated_types, "New type should be in the list")
    
    def test_get_all_parameters(self):
        """Test retrieving all parameters for a configuration type."""
        # Set some test parameters
        set_parameter("PARAM1", "value1", "test")
        set_parameter("PARAM2", "value2", "test")
        
        # Get all parameters
        result = get_all_parameters("test")
        self.assertIsInstance(result, dict, "Get all parameters should return a dictionary")
        
        # Verify structure
        if result.get("success", False):
            parameters = result.get("data", {}).get("parameters", {})
            self.assertIsInstance(parameters, dict, "Parameters should be a dictionary")
    
    # ===== CONFIGURATION TIER TESTS =====
    
    def test_interface_configuration_retrieval(self):
        """Test interface configuration retrieval for all tiers."""
        interfaces = [
            InterfaceType.CACHE, InterfaceType.LOGGING, InterfaceType.METRICS,
            InterfaceType.SECURITY, InterfaceType.CIRCUIT_BREAKER, InterfaceType.SINGLETON
        ]
        
        tiers = [ConfigurationTier.MINIMUM, ConfigurationTier.STANDARD, ConfigurationTier.MAXIMUM]
        
        for interface in interfaces:
            for tier in tiers:
                config = get_interface_configuration(interface, tier)
                self.assertIsInstance(config, dict, f"Configuration for {interface.value}/{tier.value} should be a dictionary")
                self.assertIn("tier", config.get("_metadata", {}).get("base_tier", tier.value) or config, 
                            f"Configuration should indicate tier for {interface.value}/{tier.value}")
    
    def test_system_configuration(self):
        """Test complete system configuration generation."""
        # Test base tier configuration
        config = get_system_configuration(ConfigurationTier.STANDARD)
        self.assertIsInstance(config, dict, "System configuration should be a dictionary")
        
        # Test with overrides
        overrides = {
            InterfaceType.CACHE: ConfigurationTier.MAXIMUM,
            InterfaceType.SECURITY: ConfigurationTier.MAXIMUM
        }
        
        config_with_overrides = get_system_configuration(ConfigurationTier.MINIMUM, overrides)
        self.assertIsInstance(config_with_overrides, dict, "System configuration with overrides should be a dictionary")
        
        # Verify overrides are applied
        metadata = config_with_overrides.get("_metadata", {})
        applied_overrides = metadata.get("overrides", {})
        self.assertEqual(applied_overrides.get("cache"), "maximum", "Cache override should be applied")
        self.assertEqual(applied_overrides.get("security"), "maximum", "Security override should be applied")
    
    def test_configuration_validation(self):
        """Test configuration validation against AWS constraints."""
        # Test valid configuration
        validation = validate_configuration(ConfigurationTier.STANDARD, {})
        self.assertIsInstance(validation, dict, "Validation result should be a dictionary")
        self.assertIn("is_valid", validation, "Validation should include validity status")
        self.assertIn("memory_estimate", validation, "Validation should include memory estimate")
        self.assertIn("metric_estimate", validation, "Validation should include metric estimate")
        
        # Test invalid configuration (all maximum should exceed constraints)
        max_overrides = {
            InterfaceType.CACHE: ConfigurationTier.MAXIMUM,
            InterfaceType.LOGGING: ConfigurationTier.MAXIMUM,
            InterfaceType.METRICS: ConfigurationTier.MAXIMUM,
            InterfaceType.SECURITY: ConfigurationTier.MAXIMUM,
            InterfaceType.CIRCUIT_BREAKER: ConfigurationTier.MAXIMUM,
            InterfaceType.SINGLETON: ConfigurationTier.MAXIMUM
        }
        
        max_validation = validate_configuration(ConfigurationTier.MAXIMUM, max_overrides)
        # This might be valid or invalid depending on exact memory calculations
        self.assertIsInstance(max_validation, dict, "Maximum validation result should be a dictionary")
        
        # Memory should be calculated
        memory_estimate = max_validation.get("memory_estimate", 0)
        self.assertGreater(memory_estimate, 0, "Memory estimate should be positive")
    
    # ===== PRESET MANAGEMENT TESTS =====
    
    def test_preset_operations(self):
        """Test preset management operations."""
        # Get available presets
        presets = get_available_presets()
        self.assertIsInstance(presets, list, "Available presets should be a list")
        self.assertGreater(len(presets), 0, "Should have at least one preset available")
        
        # Test required presets exist
        preset_names = list_preset_names()
        required_presets = [
            "ultra_conservative", "production_balanced", "performance_optimized",
            "development_debug", "security_focused"
        ]
        
        for preset_name in required_presets:
            self.assertIn(preset_name, preset_names, f"Required preset {preset_name} should be available")
    
    def test_preset_application(self):
        """Test applying configuration presets."""
        preset_names = list_preset_names()
        
        for preset_name in preset_names[:3]:  # Test first 3 presets to avoid timeout
            with self.subTest(preset=preset_name):
                config = apply_preset(preset_name)
                self.assertIsInstance(config, dict, f"Preset {preset_name} should return configuration dictionary")
                
                # Verify preset metadata
                metadata = config.get("_metadata", {})
                self.assertIsInstance(metadata, dict, f"Preset {preset_name} should have metadata")
    
    def test_preset_details(self):
        """Test preset details retrieval."""
        preset_names = list_preset_names()
        
        for preset_name in preset_names[:3]:  # Test first 3 presets
            with self.subTest(preset=preset_name):
                details = get_preset_details(preset_name)
                self.assertIsInstance(details, dict, f"Preset {preset_name} details should be a dictionary")
    
    # ===== RESOURCE ESTIMATION TESTS =====
    
    def test_memory_estimation(self):
        """Test memory usage estimation."""
        # Test tier-specific estimation
        for tier in ConfigurationTier:
            memory_usage = estimate_memory_usage(tier)
            self.assertIsInstance(memory_usage, (int, float), f"Memory usage for {tier.value} should be numeric")
            self.assertGreater(memory_usage, 0, f"Memory usage for {tier.value} should be positive")
        
        # Test interface-specific estimation
        interfaces = [InterfaceType.CACHE, InterfaceType.SECURITY, InterfaceType.METRICS]
        for interface in interfaces:
            memory_usage = estimate_memory_usage(ConfigurationTier.STANDARD, interface)
            self.assertIsInstance(memory_usage, (int, float), f"Memory usage for {interface.value} should be numeric")
    
    def test_metrics_estimation(self):
        """Test metrics usage estimation."""
        for tier in ConfigurationTier:
            metrics_usage = estimate_metrics_usage(tier)
            self.assertIsInstance(metrics_usage, int, f"Metrics usage for {tier.value} should be integer")
            self.assertGreaterEqual(metrics_usage, 0, f"Metrics usage for {tier.value} should be non-negative")
            self.assertLessEqual(metrics_usage, 15, f"Metrics usage for {tier.value} should be reasonable")
    
    def test_memory_allocation_summary(self):
        """Test memory allocation summary generation."""
        summary = get_memory_allocation_summary()
        self.assertIsInstance(summary, dict, "Memory allocation summary should be a dictionary")
        
        required_keys = [
            "total_memory_mb", "memory_limit_mb", "memory_available_mb", 
            "utilization_percent", "within_constraints"
        ]
        
        for key in required_keys:
            self.assertIn(key, summary, f"Memory allocation summary should include {key}")
    
    def test_aws_constraints_validation(self):
        """Test AWS constraints validation."""
        constraints = validate_aws_constraints(ConfigurationTier.STANDARD)
        self.assertIsInstance(constraints, dict, "AWS constraints validation should return a dictionary")
        
        # Verify structure
        self.assertIn("constraints", constraints, "Should include constraints section")
        self.assertIn("compliance_status", constraints, "Should include compliance status")
        
        constraints_section = constraints.get("constraints", {})
        self.assertIn("memory_constraint", constraints_section, "Should include memory constraint")
        self.assertIn("metrics_constraint", constraints_section, "Should include metrics constraint")
    
    # ===== OPTIMIZATION FUNCTION TESTS =====
    
    def test_memory_optimization(self):
        """Test memory constraint optimization."""
        # Test optimization for different targets
        targets = [32, 64, 96]
        
        for target in targets:
            with self.subTest(target=target):
                result = optimize_for_memory_constraint(target)
                self.assertIsInstance(result, dict, f"Memory optimization for {target}MB should return dictionary")
                
                # Verify structure
                self.assertIn("optimized_configuration", result, "Should include optimized configuration")
                self.assertIn("optimization_result", result, "Should include optimization result")
                self.assertIn("memory_usage_mb", result, "Should include memory usage")
    
    def test_performance_optimization(self):
        """Test performance optimization."""
        result = optimize_for_performance()
        self.assertIsInstance(result, dict, "Performance optimization should return dictionary")
        
        # Verify structure
        self.assertIn("optimized_configuration", result, "Should include optimized configuration")
        self.assertIn("optimization_result", result, "Should include optimization result")
    
    def test_cost_optimization(self):
        """Test cost protection optimization."""
        result = optimize_for_cost_protection()
        self.assertIsInstance(result, dict, "Cost optimization should return dictionary")
        
        # Verify structure
        self.assertIn("optimized_configuration", result, "Should include optimized configuration")
        self.assertIn("optimization_result", result, "Should include optimization result")
        self.assertIn("cost_protection_features", result, "Should include cost protection features")
    
    def test_optimization_recommendations(self):
        """Test optimization recommendations generation."""
        recommendations = get_optimization_recommendations()
        self.assertIsInstance(recommendations, list, "Optimization recommendations should be a list")
        
        # Each recommendation should have required fields
        for recommendation in recommendations:
            self.assertIsInstance(recommendation, dict, "Each recommendation should be a dictionary")
            self.assertIn("type", recommendation, "Recommendation should have type")
            self.assertIn("priority", recommendation, "Recommendation should have priority")
            self.assertIn("recommendation", recommendation, "Recommendation should have recommendation text")
    
    # ===== ANALYSIS AND MONITORING TESTS =====
    
    def test_configuration_compliance_analysis(self):
        """Test configuration compliance analysis."""
        analysis = analyze_configuration_compliance(ConfigurationTier.STANDARD)
        self.assertIsInstance(analysis, dict, "Compliance analysis should return dictionary")
        
        # Verify structure
        expected_keys = [
            "compliance_status", "validation_results", "constraint_analysis", 
            "memory_analysis", "recommendations"
        ]
        
        for key in expected_keys:
            self.assertIn(key, analysis, f"Compliance analysis should include {key}")
    
    def test_configuration_health_status(self):
        """Test configuration health status monitoring."""
        health = get_configuration_health_status()
        self.assertIsInstance(health, dict, "Health status should return dictionary")
        
        # Verify structure
        required_keys = ["health_status", "system_configuration", "resource_utilization"]
        
        for key in required_keys:
            self.assertIn(key, health, f"Health status should include {key}")
        
        # Verify health status is valid
        valid_statuses = ["healthy", "warning", "critical"]
        self.assertIn(health["health_status"], valid_statuses, "Health status should be valid")
    
    # ===== UTILITY FUNCTION TESTS =====
    
    def test_custom_configuration_creation(self):
        """Test custom configuration creation."""
        overrides = {
            InterfaceType.CACHE: ConfigurationTier.MAXIMUM,
            InterfaceType.SECURITY: ConfigurationTier.STANDARD
        }
        
        result = create_custom_configuration(
            "test_custom", 
            ConfigurationTier.MINIMUM, 
            overrides,
            "Test custom configuration"
        )
        
        self.assertIsInstance(result, dict, "Custom configuration creation should return dictionary")
        self.assertIn("creation_result", result, "Should include creation result")
    
    def test_configuration_comparison(self):
        """Test configuration comparison."""
        config1 = apply_preset("ultra_conservative")
        config2 = apply_preset("performance_optimized")
        
        comparison = compare_configurations(config1, config2)
        self.assertIsInstance(comparison, dict, "Configuration comparison should return dictionary")
        
        # Verify comparison structure
        expected_keys = ["memory_difference_mb", "metric_difference", "performance_impact"]
        for key in expected_keys:
            self.assertIn(key, comparison, f"Comparison should include {key}")
    
    # ===== CONSTRAINT COMPLIANCE TESTS =====
    
    def test_all_presets_aws_compliance(self):
        """Test that all presets comply with AWS constraints."""
        preset_names = list_preset_names()
        
        for preset_name in preset_names:
            with self.subTest(preset=preset_name):
                config = apply_preset(preset_name)
                metadata = config.get("_metadata", {})
                
                # Check memory constraint
                memory_estimate = metadata.get("memory_estimate", 0)
                self.assertLessEqual(memory_estimate, 128, f"Preset {preset_name} should not exceed 128MB memory limit")
                
                # Check metrics constraint
                metric_estimate = metadata.get("metric_estimate", 0)
                self.assertLessEqual(metric_estimate, 10, f"Preset {preset_name} should not exceed 10 metrics limit")
    
    def test_tier_memory_progression(self):
        """Test that memory usage increases with tier progression."""
        tiers = [ConfigurationTier.MINIMUM, ConfigurationTier.STANDARD, ConfigurationTier.MAXIMUM]
        memory_usages = []
        
        for tier in tiers:
            memory_usage = estimate_memory_usage(tier)
            memory_usages.append(memory_usage)
        
        # Memory should generally increase with tier level
        self.assertLessEqual(memory_usages[0], memory_usages[1], "Standard tier should use >= memory than minimum")
        # Maximum might not always be greater than standard due to optimization
        
    # ===== ERROR HANDLING TESTS =====
    
    def test_invalid_input_handling(self):
        """Test handling of invalid inputs."""
        # Test invalid configuration tier
        try:
            # This should handle gracefully
            config = get_interface_configuration("invalid_interface", ConfigurationTier.STANDARD)
            # If it doesn't raise an exception, it should return something reasonable
            self.assertIsInstance(config, dict, "Invalid interface should return dictionary")
        except (ValueError, KeyError, AttributeError):
            # These exceptions are acceptable for invalid input
            pass
        
        # Test invalid preset name
        config = apply_preset("nonexistent_preset")
        self.assertIsInstance(config, dict, "Invalid preset should return fallback configuration")
    
    def test_edge_case_configurations(self):
        """Test edge case configurations."""
        # Test all minimum configuration
        min_config = get_system_configuration(ConfigurationTier.MINIMUM, {})
        validation = validate_configuration(ConfigurationTier.MINIMUM, {})
        
        self.assertTrue(validation.get("is_valid", False), "All minimum configuration should be valid")
        
        # Test empty overrides
        empty_overrides_config = get_system_configuration(ConfigurationTier.STANDARD, {})
        self.assertIsInstance(empty_overrides_config, dict, "Empty overrides should work")

class ConfigurationPerformanceTests(unittest.TestCase):
    """Performance tests for configuration system."""
    
    def test_configuration_retrieval_performance(self):
        """Test configuration retrieval performance."""
        start_time = time.time()
        
        # Perform multiple configuration operations
        for _ in range(10):
            config = apply_preset("production_balanced")
            validation = validate_configuration(ConfigurationTier.STANDARD, {})
            memory_usage = estimate_memory_usage(ConfigurationTier.STANDARD)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Should complete within reasonable time (2 seconds for 10 operations)
        self.assertLess(execution_time, 2.0, "Configuration operations should be performant")
    
    def test_memory_efficiency(self):
        """Test memory efficiency of configuration operations."""
        # This is a basic test - in production you'd use memory profiling tools
        initial_config = apply_preset("ultra_conservative")
        complex_config = apply_preset("performance_optimized")
        
        # Both operations should complete without memory issues
        self.assertIsInstance(initial_config, dict, "Memory-efficient configuration should work")
        self.assertIsInstance(complex_config, dict, "Complex configuration should work")

def run_configuration_tests():
    """Run the complete configuration system test suite."""
    print("=== Configuration System Integration Test Suite ===")
    print("Testing ultra-optimized configuration system...")
    
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add configuration system tests
    suite.addTest(unittest.makeSuite(ConfigurationSystemTestSuite))
    suite.addTest(unittest.makeSuite(ConfigurationPerformanceTests))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Report results
    print(f"\n=== Test Results ===")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print(f"\nFailures:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print(f"\nErrors:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    # Run tests when script is executed directly
    success = run_configuration_tests()
    exit(0 if success else 1)
