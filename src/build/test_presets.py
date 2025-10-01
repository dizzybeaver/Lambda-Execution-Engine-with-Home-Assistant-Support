"""
test_presets.py - Automated Preset Testing Framework
Version: 2025.10.01.01
Daily Revision: Phase 4 Build System Enhancement

Automated testing for all feature presets with validation.
Ensures each preset builds correctly and contains expected features.

Licensed under the Apache License, Version 2.0
"""

import os
import sys
import subprocess
import tempfile
import shutil
import zipfile
from pathlib import Path
from typing import Dict, List, Any
from build_config import COMMON_PRESETS, HAFeature, FEATURE_MODULES


class PresetTester:
    """Automated testing framework for feature presets."""
    
    def __init__(self, build_script: str = "build_package.py"):
        self.build_script = build_script
        self.test_results = []
        self.temp_dir = None
        
    def setup_test_environment(self):
        """Create temporary test environment."""
        self.temp_dir = tempfile.mkdtemp(prefix="preset_test_")
        print(f"Test environment: {self.temp_dir}")
        
    def cleanup_test_environment(self):
        """Clean up test environment."""
        if self.temp_dir and Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
            
    def test_preset(self, preset_name: str) -> Dict[str, Any]:
        """Test a single preset build."""
        print(f"\nTesting preset: {preset_name}")
        
        result = {
            "preset": preset_name,
            "success": False,
            "build_time": 0,
            "package_size": 0,
            "features_expected": [],
            "features_found": [],
            "errors": []
        }
        
        try:
            os.environ["HA_FEATURE_PRESET"] = preset_name
            
            expected_features = COMMON_PRESETS.get(preset_name, [])
            result["features_expected"] = [f.value for f in expected_features]
            
            output_name = f"lambda_{preset_name}.zip"
            
            import time
            start_time = time.time()
            
            build_result = subprocess.run(
                [sys.executable, self.build_script, "--output", output_name],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            result["build_time"] = time.time() - start_time
            
            if build_result.returncode != 0:
                result["errors"].append(f"Build failed: {build_result.stderr}")
                return result
                
            package_path = Path("dist") / output_name
            if not package_path.exists():
                result["errors"].append(f"Package not found: {package_path}")
                return result
                
            result["package_size"] = package_path.stat().st_size
            
            with zipfile.ZipFile(package_path, 'r') as zf:
                files_in_zip = zf.namelist()
                
            for feature, module in FEATURE_MODULES.items():
                if feature in expected_features:
                    if module in files_in_zip:
                        result["features_found"].append(feature.value)
                    else:
                        result["errors"].append(f"Expected module missing: {module}")
                else:
                    if module in files_in_zip:
                        result["errors"].append(f"Unexpected module included: {module}")
                        
            result["success"] = len(result["errors"]) == 0
            
            if package_path.exists():
                package_path.unlink()
                
        except subprocess.TimeoutExpired:
            result["errors"].append("Build timeout (30s)")
        except Exception as e:
            result["errors"].append(f"Test exception: {str(e)}")
            
        return result
        
    def test_all_presets(self) -> Dict[str, Any]:
        """Test all available presets."""
        print("="*60)
        print("PRESET BUILD TESTING")
        print("="*60)
        
        self.setup_test_environment()
        
        try:
            for preset_name in COMMON_PRESETS.keys():
                result = self.test_preset(preset_name)
                self.test_results.append(result)
                
            summary = self.generate_summary()
            return summary
            
        finally:
            self.cleanup_test_environment()
            
    def generate_summary(self) -> Dict[str, Any]:
        """Generate test summary."""
        total = len(self.test_results)
        passed = sum(1 for r in self.test_results if r["success"])
        failed = total - passed
        
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        print(f"Total Presets: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Success Rate: {(passed/total*100):.1f}%")
        
        if failed > 0:
            print("\nFailed Presets:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  {result['preset']}:")
                    for error in result["errors"]:
                        print(f"    - {error}")
                        
        return {
            "total_presets": total,
            "passed": passed,
            "failed": failed,
            "success_rate": passed/total*100,
            "results": self.test_results
        }
        
    def validate_feature_coverage(self) -> Dict[str, Any]:
        """Validate all features are covered in presets."""
        all_features = set(HAFeature)
        covered_features = set()
        
        for preset_features in COMMON_PRESETS.values():
            covered_features.update(preset_features)
            
        uncovered = all_features - covered_features
        
        result = {
            "total_features": len(all_features),
            "covered_features": len(covered_features),
            "uncovered_features": [f.value for f in uncovered],
            "coverage_percentage": len(covered_features) / len(all_features) * 100
        }
        
        print("\n" + "="*60)
        print("FEATURE COVERAGE ANALYSIS")
        print("="*60)
        print(f"Total Features: {result['total_features']}")
        print(f"Covered in Presets: {result['covered_features']}")
        print(f"Coverage: {result['coverage_percentage']:.1f}%")
        
        if uncovered:
            print(f"\nUncovered Features ({len(uncovered)}):")
            for feature in uncovered:
                print(f"  - {feature.value}")
                
        return result
        

def main():
    """Main entry point for preset testing."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test feature presets")
    parser.add_argument("--preset", help="Test specific preset")
    parser.add_argument("--coverage", action="store_true", help="Check feature coverage")
    args = parser.parse_args()
    
    tester = PresetTester()
    
    if args.coverage:
        tester.validate_feature_coverage()
        return 0
        
    if args.preset:
        result = tester.test_preset(args.preset)
        print(f"\nResult: {'PASS' if result['success'] else 'FAIL'}")
        if result['errors']:
            for error in result['errors']:
                print(f"  {error}")
        return 0 if result['success'] else 1
    else:
        summary = tester.test_all_presets()
        return 0 if summary['failed'] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
