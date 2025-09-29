"""
deployment_automation.py - Ultra-Optimization Deployment Automation
Version: 2025.09.29.01
Description: Automated deployment utilities for ultra-optimization implementation

PROVIDES:
- ✅ Automated backup creation
- ✅ File version verification
- ✅ Deployment validation
- ✅ Rollback automation
- ✅ Post-deployment testing

Licensed under the Apache License, Version 2.0
"""

import os
import shutil
import time
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import hashlib

class DeploymentManager:
    def __init__(self, project_root: str = "."):
        self.project_root = project_root
        self.backup_dir = os.path.join(project_root, "backups")
        self.deployment_log = []
        
        os.makedirs(self.backup_dir, exist_ok=True)
    
    def create_backup(self, files: List[str], backup_name: Optional[str] = None) -> Dict[str, Any]:
        """Create backup of specified files."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = backup_name or f"backup_{timestamp}"
        backup_path = os.path.join(self.backup_dir, backup_name)
        
        os.makedirs(backup_path, exist_ok=True)
        
        backed_up = []
        failed = []
        
        for file_path in files:
            try:
                full_path = os.path.join(self.project_root, file_path)
                if os.path.exists(full_path):
                    dest_path = os.path.join(backup_path, os.path.basename(file_path))
                    shutil.copy2(full_path, dest_path)
                    backed_up.append(file_path)
                else:
                    failed.append(f"{file_path} (not found)")
            except Exception as e:
                failed.append(f"{file_path} ({str(e)})")
        
        result = {
            'backup_name': backup_name,
            'backup_path': backup_path,
            'files_backed_up': len(backed_up),
            'backed_up_files': backed_up,
            'failed': failed,
            'timestamp': timestamp,
            'success': len(failed) == 0
        }
        
        self.deployment_log.append({
            'action': 'backup_created',
            'timestamp': time.time(),
            'details': result
        })
        
        return result
    
    def verify_file_version(self, file_path: str, expected_version: str) -> Dict[str, Any]:
        """Verify file has expected version."""
        full_path = os.path.join(self.project_root, file_path)
        
        if not os.path.exists(full_path):
            return {
                'file': file_path,
                'exists': False,
                'version_match': False,
                'expected_version': expected_version
            }
        
        try:
            with open(full_path, 'r') as f:
                content = f.read()
            
            version_match = f"Version: {expected_version}" in content
            
            return {
                'file': file_path,
                'exists': True,
                'version_match': version_match,
                'expected_version': expected_version,
                'file_size': len(content)
            }
        except Exception as e:
            return {
                'file': file_path,
                'exists': True,
                'version_match': False,
                'error': str(e)
            }
    
    def deploy_files(self, file_mappings: Dict[str, str]) -> Dict[str, Any]:
        """
        Deploy files from source to destination.
        file_mappings: {source_path: dest_path}
        """
        deployed = []
        failed = []
        
        for source, dest in file_mappings.items():
            try:
                full_dest = os.path.join(self.project_root, dest)
                
                os.makedirs(os.path.dirname(full_dest), exist_ok=True)
                
                shutil.copy2(source, full_dest)
                
                deployed.append({'source': source, 'destination': dest})
            except Exception as e:
                failed.append({'source': source, 'destination': dest, 'error': str(e)})
        
        result = {
            'files_deployed': len(deployed),
            'deployed_files': deployed,
            'failed': failed,
            'timestamp': time.time(),
            'success': len(failed) == 0
        }
        
        self.deployment_log.append({
            'action': 'files_deployed',
            'timestamp': time.time(),
            'details': result
        })
        
        return result
    
    def rollback_from_backup(self, backup_name: str, files: Optional[List[str]] = None) -> Dict[str, Any]:
        """Rollback files from backup."""
        backup_path = os.path.join(self.backup_dir, backup_name)
        
        if not os.path.exists(backup_path):
            return {
                'success': False,
                'error': f"Backup {backup_name} not found"
            }
        
        restored = []
        failed = []
        
        backup_files = os.listdir(backup_path) if files is None else files
        
        for filename in backup_files:
            try:
                source = os.path.join(backup_path, filename)
                dest = os.path.join(self.project_root, filename)
                
                if os.path.exists(source):
                    shutil.copy2(source, dest)
                    restored.append(filename)
                else:
                    failed.append(f"{filename} (not in backup)")
            except Exception as e:
                failed.append(f"{filename} ({str(e)})")
        
        result = {
            'backup_name': backup_name,
            'files_restored': len(restored),
            'restored_files': restored,
            'failed': failed,
            'timestamp': time.time(),
            'success': len(failed) == 0
        }
        
        self.deployment_log.append({
            'action': 'rollback_completed',
            'timestamp': time.time(),
            'details': result
        })
        
        return result
    
    def validate_deployment(self, expected_files: List[Tuple[str, str]]) -> Dict[str, Any]:
        """
        Validate deployment by checking file versions.
        expected_files: [(file_path, expected_version), ...]
        """
        validations = []
        all_valid = True
        
        for file_path, expected_version in expected_files:
            validation = self.verify_file_version(file_path, expected_version)
            validations.append(validation)
            
            if not validation.get('version_match', False):
                all_valid = False
        
        result = {
            'all_files_valid': all_valid,
            'files_checked': len(validations),
            'validations': validations,
            'timestamp': time.time()
        }
        
        return result
    
    def run_post_deployment_tests(self) -> Dict[str, Any]:
        """Run post-deployment tests using ultra_optimization_tester."""
        try:
            from .ultra_optimization_tester import run_ultra_optimization_tests
            
            print("\n🔬 Running post-deployment tests...")
            test_results = run_ultra_optimization_tests()
            
            self.deployment_log.append({
                'action': 'post_deployment_tests',
                'timestamp': time.time(),
                'details': test_results
            })
            
            return test_results
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Failed to run tests: {str(e)}"
            }
    
    def get_deployment_log(self) -> List[Dict[str, Any]]:
        """Get deployment activity log."""
        return self.deployment_log
    
    def generate_deployment_report(self) -> str:
        """Generate comprehensive deployment report."""
        report = []
        report.append("=" * 70)
        report.append("ULTRA-OPTIMIZATION DEPLOYMENT REPORT")
        report.append("=" * 70)
        report.append(f"\nDeployment Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Total Actions: {len(self.deployment_log)}\n")
        
        for i, log_entry in enumerate(self.deployment_log, 1):
            action = log_entry.get('action', 'unknown')
            timestamp = datetime.fromtimestamp(log_entry.get('timestamp', 0))
            details = log_entry.get('details', {})
            
            report.append(f"\n{i}. {action.upper().replace('_', ' ')}")
            report.append(f"   Time: {timestamp.strftime('%H:%M:%S')}")
            
            if action == 'backup_created':
                report.append(f"   Backup: {details.get('backup_name', 'N/A')}")
                report.append(f"   Files: {details.get('files_backed_up', 0)}")
                report.append(f"   Status: {'✅ Success' if details.get('success') else '❌ Failed'}")
            
            elif action == 'files_deployed':
                report.append(f"   Deployed: {details.get('files_deployed', 0)}")
                report.append(f"   Status: {'✅ Success' if details.get('success') else '❌ Failed'}")
            
            elif action == 'rollback_completed':
                report.append(f"   Restored: {details.get('files_restored', 0)}")
                report.append(f"   Status: {'✅ Success' if details.get('success') else '❌ Failed'}")
            
            elif action == 'post_deployment_tests':
                report.append(f"   Tests Passed: {details.get('tests_passed', 0)}/{details.get('total_tests_run', 0)}")
                report.append(f"   Pass Rate: {details.get('pass_rate_percentage', 0):.1f}%")
                report.append(f"   Status: {'✅ All Passed' if details.get('all_tests_passed') else '⚠️ Some Failed'}")
        
        report.append("\n" + "=" * 70)
        report.append("END OF DEPLOYMENT REPORT")
        report.append("=" * 70)
        
        return "\n".join(report)

def automated_ultra_optimization_deployment(project_root: str = ".") -> Dict[str, Any]:
    """
    Fully automated ultra-optimization deployment process.
    """
    manager = DeploymentManager(project_root)
    
    print("🚀 Starting Ultra-Optimization Deployment...")
    print("=" * 70)
    
    files_to_backup = [
        "metrics.py",
        "metrics_core.py",
        "singleton.py",
        "singleton_core.py",
        "cache_core.py",
        "security_core.py"
    ]
    
    print("\n📦 Phase 1: Creating Backup...")
    backup_result = manager.create_backup(files_to_backup)
    print(f"   Backup created: {backup_result['backup_name']}")
    print(f"   Files backed up: {backup_result['files_backed_up']}")
    
    if not backup_result['success']:
        print(f"   ⚠️ Warning: Some files failed to backup: {backup_result['failed']}")
    
    file_mappings = {}
    
    print("\n📥 Phase 2: Deploying Ultra-Optimized Files...")
    deploy_result = manager.deploy_files(file_mappings)
    print(f"   Files deployed: {deploy_result['files_deployed']}")
    
    if not deploy_result['success']:
        print(f"   ❌ Deployment failed: {deploy_result['failed']}")
        print("\n🔄 Rolling back...")
        rollback_result = manager.rollback_from_backup(backup_result['backup_name'])
        print(f"   Rollback completed: {rollback_result['files_restored']} files restored")
        return {
            'success': False,
            'stage': 'deployment',
            'backup': backup_result,
            'deploy': deploy_result,
            'rollback': rollback_result
        }
    
    expected_files = [
        ("metrics.py", "2025.09.29.01"),
        ("metrics_core.py", "2025.09.29.01"),
        ("singleton.py", "2025.09.29.01"),
        ("singleton_core.py", "2025.09.29.01"),
        ("cache_core.py", "2025.09.29.01"),
        ("security_core.py", "2025.09.29.01")
    ]
    
    print("\n✅ Phase 3: Validating Deployment...")
    validation_result = manager.validate_deployment(expected_files)
    print(f"   Files validated: {validation_result['files_checked']}")
    print(f"   All valid: {'✅ Yes' if validation_result['all_files_valid'] else '❌ No'}")
    
    if not validation_result['all_files_valid']:
        print("   ⚠️ Warning: Some files have incorrect versions")
    
    print("\n🧪 Phase 4: Running Post-Deployment Tests...")
    test_results = manager.run_post_deployment_tests()
    
    if test_results.get('all_tests_passed', False):
        print(f"   ✅ All tests passed! ({test_results.get('tests_passed', 0)}/{test_results.get('total_tests_run', 0)})")
    else:
        print(f"   ⚠️ Some tests failed ({test_results.get('tests_passed', 0)}/{test_results.get('total_tests_run', 0)})")
    
    print("\n📄 Generating Deployment Report...")
    report = manager.generate_deployment_report()
    
    report_path = os.path.join(project_root, f"deployment_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
    with open(report_path, 'w') as f:
        f.write(report)
    print(f"   Report saved: {report_path}")
    
    print("\n" + "=" * 70)
    print("🎉 DEPLOYMENT COMPLETE")
    print("=" * 70)
    
    return {
        'success': test_results.get('all_tests_passed', False),
        'backup': backup_result,
        'deploy': deploy_result,
        'validation': validation_result,
        'tests': test_results,
        'report_path': report_path
    }

__all__ = [
    'DeploymentManager',
    'automated_ultra_optimization_deployment'
]
