"""
build/__init__.py - Build Package Exports
Version: 2025.10.14.01
Description: Exports for build package (CloudFormation, deployment, test presets)

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

# CloudFormation Generator
from cloudformation_generator import (
    generate_cloudformation_template,
    validate_template,
    get_template_parameters,
)

# Deploy Automation
from deploy_automation import (
    deploy_lambda,
    update_lambda,
    rollback_deployment,
    get_deployment_status,
)

# Test Presets
from test_presets import (
    get_test_preset,
    list_test_presets,
    apply_test_preset,
    validate_test_preset,
)

__all__ = [
    # CloudFormation Generator
    'generate_cloudformation_template',
    'validate_template',
    'get_template_parameters',
    
    # Deploy Automation
    'deploy_lambda',
    'update_lambda',
    'rollback_deployment',
    'get_deployment_status',
    
    # Test Presets
    'get_test_preset',
    'list_test_presets',
    'apply_test_preset',
    'validate_test_preset',
]

# EOF
