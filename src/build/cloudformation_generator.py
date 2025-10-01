"""
cloudformation_generator.py - CloudFormation Template Generator
Version: 2025.10.01.01
Daily Revision: Phase 4 Build System Enhancement

Generates CloudFormation templates for automated AWS deployment.
Creates complete infrastructure with Lambda, IAM roles, and parameters.

Licensed under the Apache License, Version 2.0
"""

import json
import yaml
from typing import Dict, Any, List
from build_config import COMMON_PRESETS


class CloudFormationGenerator:
    """Generate CloudFormation templates for Lambda deployment."""
    
    def __init__(self, preset: str = "smart_home"):
        self.preset = preset
        self.template = {
            "AWSTemplateFormatVersion": "2010-09-09",
            "Description": f"Lambda Execution Engine - {preset} preset",
            "Parameters": {},
            "Resources": {},
            "Outputs": {}
        }
        
    def add_parameters(self):
        """Add CloudFormation parameters."""
        self.template["Parameters"] = {
            "HomeAssistantURL": {
                "Type": "String",
                "Description": "Home Assistant URL",
                "Default": ""
            },
            "HomeAssistantToken": {
                "Type": "String",
                "Description": "Home Assistant Long-Lived Access Token",
                "NoEcho": True,
                "Default": ""
            },
            "ConfigurationTier": {
                "Type": "String",
                "Description": "Configuration tier (MINIMUM, STANDARD, PERFORMANCE, MAXIMUM)",
                "Default": "STANDARD",
                "AllowedValues": ["MINIMUM", "STANDARD", "PERFORMANCE", "MAXIMUM"]
            },
            "FeaturePreset": {
                "Type": "String",
                "Description": "Feature preset selection",
                "Default": self.preset,
                "AllowedValues": list(COMMON_PRESETS.keys())
            }
        }
        
    def add_iam_role(self):
        """Add IAM execution role."""
        self.template["Resources"]["LambdaExecutionRole"] = {
            "Type": "AWS::IAM::Role",
            "Properties": {
                "RoleName": "LambdaExecutionEngineRole",
                "AssumeRolePolicyDocument": {
                    "Version": "2012-10-17",
                    "Statement": [{
                        "Effect": "Allow",
                        "Principal": {"Service": "lambda.amazonaws.com"},
                        "Action": "sts:AssumeRole"
                    }]
                },
                "ManagedPolicyArns": [
                    "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
                ],
                "Policies": [{
                    "PolicyName": "LambdaExecutionEnginePolicy",
                    "PolicyDocument": {
                        "Version": "2012-10-17",
                        "Statement": [{
                            "Effect": "Allow",
                            "Action": [
                                "logs:CreateLogGroup",
                                "logs:CreateLogStream",
                                "logs:PutLogEvents"
                            ],
                            "Resource": "arn:aws:logs:*:*:*"
                        }]
                    }
                }]
            }
        }
        
    def add_lambda_function(self):
        """Add Lambda function resource."""
        self.template["Resources"]["LambdaFunction"] = {
            "Type": "AWS::Lambda::Function",
            "Properties": {
                "FunctionName": "LambdaExecutionEngine",
                "Runtime": "python3.12",
                "Handler": "lambda_function.lambda_handler",
                "Role": {"Fn::GetAtt": ["LambdaExecutionRole", "Arn"]},
                "Code": {
                    "ZipFile": "# Placeholder - deploy with actual code"
                },
                "MemorySize": 128,
                "Timeout": 30,
                "Environment": {
                    "Variables": {
                        "HOME_ASSISTANT_ENABLED": "true",
                        "HOME_ASSISTANT_URL": {"Ref": "HomeAssistantURL"},
                        "HOME_ASSISTANT_TOKEN": {"Ref": "HomeAssistantToken"},
                        "CONFIGURATION_TIER": {"Ref": "ConfigurationTier"},
                        "HA_FEATURE_PRESET": {"Ref": "FeaturePreset"}
                    }
                }
            },
            "DependsOn": "LambdaExecutionRole"
        }
        
    def add_cloudwatch_log_group(self):
        """Add CloudWatch log group."""
        self.template["Resources"]["LogGroup"] = {
            "Type": "AWS::Logs::LogGroup",
            "Properties": {
                "LogGroupName": "/aws/lambda/LambdaExecutionEngine",
                "RetentionInDays": 7
            }
        }
        
    def add_alexa_skill_permission(self):
        """Add Alexa Skill permission."""
        self.template["Resources"]["AlexaSkillPermission"] = {
            "Type": "AWS::Lambda::Permission",
            "Properties": {
                "FunctionName": {"Ref": "LambdaFunction"},
                "Action": "lambda:InvokeFunction",
                "Principal": "alexa-appkit.amazon.com"
            }
        }
        
    def add_outputs(self):
        """Add CloudFormation outputs."""
        self.template["Outputs"] = {
            "LambdaFunctionArn": {
                "Description": "Lambda function ARN",
                "Value": {"Fn::GetAtt": ["LambdaFunction", "Arn"]},
                "Export": {"Name": "LambdaExecutionEngine-FunctionArn"}
            },
            "LambdaFunctionName": {
                "Description": "Lambda function name",
                "Value": {"Ref": "LambdaFunction"}
            },
            "LambdaExecutionRoleArn": {
                "Description": "Lambda execution role ARN",
                "Value": {"Fn::GetAtt": ["LambdaExecutionRole", "Arn"]}
            }
        }
        
    def generate(self, output_format: str = "yaml") -> str:
        """Generate complete CloudFormation template."""
        self.add_parameters()
        self.add_iam_role()
        self.add_lambda_function()
        self.add_cloudwatch_log_group()
        self.add_alexa_skill_permission()
        self.add_outputs()
        
        if output_format == "json":
            return json.dumps(self.template, indent=2)
        else:
            return yaml.dump(self.template, default_flow_style=False, sort_keys=False)
            
    def save(self, filename: str = None, output_format: str = "yaml"):
        """Save template to file."""
        if filename is None:
            ext = "json" if output_format == "json" else "yaml"
            filename = f"cloudformation_{self.preset}.{ext}"
            
        content = self.generate(output_format)
        
        with open(filename, 'w') as f:
            f.write(content)
            
        print(f"CloudFormation template saved: {filename}")
        return filename


def generate_all_presets(output_format: str = "yaml"):
    """Generate CloudFormation templates for all presets."""
    templates = []
    
    for preset in COMMON_PRESETS.keys():
        generator = CloudFormationGenerator(preset)
        filename = generator.save(output_format=output_format)
        templates.append(filename)
        
    print(f"\nGenerated {len(templates)} CloudFormation templates")
    return templates


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate CloudFormation templates")
    parser.add_argument("--preset", help="Feature preset", default="smart_home")
    parser.add_argument("--format", choices=["yaml", "json"], default="yaml")
    parser.add_argument("--all", action="store_true", help="Generate all presets")
    parser.add_argument("--output", help="Output filename")
    args = parser.parse_args()
    
    if args.all:
        generate_all_presets(output_format=args.format)
    else:
        generator = CloudFormationGenerator(args.preset)
        generator.save(filename=args.output, output_format=args.format)


if __name__ == "__main__":
    main()
