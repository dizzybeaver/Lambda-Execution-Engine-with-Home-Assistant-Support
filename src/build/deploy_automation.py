"""
deploy_automation.py - Automated Deployment Workflow
Version: 2025.10.01.01
Daily Revision: Phase 4 Build System Enhancement

Automated end-to-end deployment workflow for Lambda Execution Engine.
Handles build, test, deploy, and verification.

Licensed under the Apache License, Version 2.0
"""

import os
import sys
import time
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional
from build_config import COMMON_PRESETS
from test_presets import PresetTester


class DeploymentAutomation:
    """Automated deployment workflow orchestrator."""
    
    def __init__(self, preset: str = "smart_home", function_name: str = "LambdaExecutionEngine"):
        self.preset = preset
        self.function_name = function_name
        self.aws_region = os.getenv("AWS_REGION", "us-east-1")
        self.deployment_log = []
        
    def log_step(self, step: str, status: str, message: str = ""):
        """Log deployment step."""
        entry = {
            "step": step,
            "status": status,
            "message": message,
            "timestamp": time.time()
        }
        self.deployment_log.append(entry)
        print(f"[{status}] {step}: {message}")
        
    def run_tests(self) -> bool:
        """Run automated tests."""
        self.log_step("Testing", "START", f"Testing {self.preset} preset")
        
        try:
            tester = PresetTester()
            result = tester.test_preset(self.preset)
            
            if result["success"]:
                self.log_step("Testing", "PASS", "All tests passed")
                return True
            else:
                self.log_step("Testing", "FAIL", "; ".join(result["errors"]))
                return False
                
        except Exception as e:
            self.log_step("Testing", "ERROR", str(e))
            return False
            
    def build_package(self) -> Optional[Path]:
        """Build deployment package."""
        self.log_step("Building", "START", f"Building {self.preset} preset")
        
        try:
            output_name = f"lambda_{self.preset}.zip"
            
            result = subprocess.run(
                [sys.executable, "build_package.py", 
                 "--preset", self.preset,
                 "--output", output_name],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode != 0:
                self.log_step("Building", "FAIL", result.stderr)
                return None
                
            package_path = Path("dist") / output_name
            if not package_path.exists():
                self.log_step("Building", "FAIL", "Package not found")
                return None
                
            size_mb = package_path.stat().st_size / (1024 * 1024)
            self.log_step("Building", "PASS", f"Package: {size_mb:.2f}MB")
            return package_path
            
        except Exception as e:
            self.log_step("Building", "ERROR", str(e))
            return None
            
    def deploy_to_aws(self, package_path: Path) -> bool:
        """Deploy package to AWS Lambda."""
        self.log_step("Deploying", "START", f"Deploying to {self.function_name}")
        
        try:
            result = subprocess.run(
                ["aws", "lambda", "update-function-code",
                 "--function-name", self.function_name,
                 "--zip-file", f"fileb://{package_path}",
                 "--region", self.aws_region],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode != 0:
                self.log_step("Deploying", "FAIL", result.stderr)
                return False
                
            self.log_step("Deploying", "PASS", "Code deployed")
            
            subprocess.run(
                ["aws", "lambda", "wait", "function-updated",
                 "--function-name", self.function_name,
                 "--region", self.aws_region],
                timeout=120
            )
            
            self.log_step("Deploying", "PASS", "Function updated")
            return True
            
        except Exception as e:
            self.log_step("Deploying", "ERROR", str(e))
            return False
            
    def update_environment(self) -> bool:
        """Update Lambda environment variables."""
        self.log_step("Configuration", "START", "Updating environment")
        
        try:
            env_vars = {
                "HOME_ASSISTANT_ENABLED": "true",
                "HA_FEATURE_PRESET": self.preset,
                "CONFIGURATION_TIER": "STANDARD"
            }
            
            env_string = ",".join([f"{k}={v}" for k, v in env_vars.items()])
            
            result = subprocess.run(
                ["aws", "lambda", "update-function-configuration",
                 "--function-name", self.function_name,
                 "--environment", f"Variables={{{env_string}}}",
                 "--region", self.aws_region],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode != 0:
                self.log_step("Configuration", "FAIL", result.stderr)
                return False
                
            self.log_step("Configuration", "PASS", "Environment updated")
            return True
            
        except Exception as e:
            self.log_step("Configuration", "ERROR", str(e))
            return False
            
    def verify_deployment(self) -> bool:
        """Verify deployment is functional."""
        self.log_step("Verification", "START", "Testing deployment")
        
        try:
            result = subprocess.run(
                ["aws", "lambda", "invoke",
                 "--function-name", self.function_name,
                 "--payload", '{"test": true}',
                 "--region", self.aws_region,
                 "response.json"],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode != 0:
                self.log_step("Verification", "FAIL", result.stderr)
                return False
                
            response_path = Path("response.json")
            if response_path.exists():
                response_path.unlink()
                
            self.log_step("Verification", "PASS", "Deployment verified")
            return True
            
        except Exception as e:
            self.log_step("Verification", "ERROR", str(e))
            return False
            
    def execute_deployment(self) -> Dict[str, Any]:
        """Execute complete deployment workflow."""
        print("="*60)
        print(f"AUTOMATED DEPLOYMENT: {self.preset}")
        print("="*60)
        
        start_time = time.time()
        
        if not self.run_tests():
            return self.generate_report(False, time.time() - start_time)
            
        package_path = self.build_package()
        if not package_path:
            return self.generate_report(False, time.time() - start_time)
            
        if not self.deploy_to_aws(package_path):
            return self.generate_report(False, time.time() - start_time)
            
        if not self.update_environment():
            return self.generate_report(False, time.time() - start_time)
            
        if not self.verify_deployment():
            return self.generate_report(False, time.time() - start_time)
            
        return self.generate_report(True, time.time() - start_time)
        
    def generate_report(self, success: bool, duration: float) -> Dict[str, Any]:
        """Generate deployment report."""
        print("\n" + "="*60)
        print("DEPLOYMENT REPORT")
        print("="*60)
        print(f"Preset: {self.preset}")
        print(f"Status: {'SUCCESS' if success else 'FAILED'}")
        print(f"Duration: {duration:.1f}s")
        
        print("\nSteps:")
        for entry in self.deployment_log:
            print(f"  [{entry['status']}] {entry['step']}")
            
        return {
            "success": success,
            "preset": self.preset,
            "function_name": self.function_name,
            "duration": duration,
            "steps": self.deployment_log
        }


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Automated Lambda deployment")
    parser.add_argument("--preset", default="smart_home", 
                       choices=list(COMMON_PRESETS.keys()))
    parser.add_argument("--function", default="LambdaExecutionEngine",
                       help="Lambda function name")
    parser.add_argument("--skip-tests", action="store_true",
                       help="Skip testing phase")
    args = parser.parse_args()
    
    automation = DeploymentAutomation(args.preset, args.function)
    
    if args.skip_tests:
        automation.log_step("Testing", "SKIP", "Tests skipped")
        package_path = automation.build_package()
        if package_path:
            automation.deploy_to_aws(package_path)
            automation.update_environment()
            automation.verify_deployment()
    else:
        result = automation.execute_deployment()
        
    return 0 if result["success"] else 1


if __name__ == "__main__":
    sys.exit(main())
