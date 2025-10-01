"""
build_package.py - Automated Feature-Selective Packaging
Version: 2025.10.01.01
Daily Revision: Phase 3 Build Optimization

Automated packaging script for Lambda Execution Engine.
Builds deployment packages with only enabled features.

Licensed under the Apache License, Version 2.0
"""

import os
import sys
import shutil
import zipfile
import py_compile
import argparse
from pathlib import Path
from typing import List, Set
from build_config import (
    get_enabled_modules,
    get_excluded_modules,
    validate_feature_configuration,
    get_build_config,
    COMMON_PRESETS
)


BUILD_DIR = Path("build")
DIST_DIR = Path("dist")
SOURCE_DIR = Path(".")


CORE_FILES = [
    "lambda_function.py",
    "gateway.py",
    "config.py",
    "config_core.py",
    "variables.py",
    "variables_utils.py",
]


EXTENSION_FILES = [
    "homeassistant_extension.py",
    "ha_common.py",
]


def clean_build_dirs():
    """Clean build and dist directories."""
    for dir_path in [BUILD_DIR, DIST_DIR]:
        if dir_path.exists():
            shutil.rmtree(dir_path)
        dir_path.mkdir(parents=True, exist_ok=True)
    
    print(f"✓ Cleaned build directories")


def copy_core_files():
    """Copy core system files to build directory."""
    copied = 0
    for filename in CORE_FILES:
        src = SOURCE_DIR / filename
        if src.exists():
            shutil.copy2(src, BUILD_DIR / filename)
            copied += 1
    
    print(f"✓ Copied {copied} core files")
    return copied


def copy_feature_modules(enabled_modules: List[str]) -> int:
    """Copy enabled feature modules to build directory."""
    copied = 0
    for module in enabled_modules:
        src = SOURCE_DIR / module
        if src.exists():
            shutil.copy2(src, BUILD_DIR / module)
            copied += 1
    
    print(f"✓ Copied {copied} feature modules")
    return copied


def compile_python_files(compile_bytecode: bool = False) -> int:
    """Optionally compile Python files to bytecode."""
    if not compile_bytecode:
        return 0
    
    compiled = 0
    for py_file in BUILD_DIR.glob("*.py"):
        try:
            py_compile.compile(py_file, cfile=str(py_file) + "c", doraise=True)
            compiled += 1
        except py_compile.PyCompileError as e:
            print(f"⚠ Warning: Failed to compile {py_file.name}: {e}")
    
    if compiled > 0:
        print(f"✓ Compiled {compiled} Python files to bytecode")
    
    return compiled


def create_deployment_package(package_name: str) -> Path:
    """Create deployment ZIP package."""
    zip_path = DIST_DIR / package_name
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in BUILD_DIR.rglob("*"):
            if file_path.is_file():
                arcname = file_path.relative_to(BUILD_DIR)
                zipf.write(file_path, arcname)
    
    size_mb = zip_path.stat().st_size / (1024 * 1024)
    print(f"✓ Created package: {package_name} ({size_mb:.2f} MB)")
    
    return zip_path


def generate_feature_manifest(enabled_modules: List[str], excluded_modules: List[str]):
    """Generate feature manifest file."""
    manifest_path = BUILD_DIR / "FEATURES.txt"
    
    config = get_build_config()
    
    with open(manifest_path, 'w') as f:
        f.write("Lambda Execution Engine - Feature Manifest\n")
        f.write("=" * 50 + "\n\n")
        
        f.write(f"Enabled Features ({len(config['enabled_features'])}):\n")
        for feature in sorted(config['enabled_features']):
            f.write(f"  ✓ {feature}\n")
        
        f.write(f"\nIncluded Modules ({len(enabled_modules)}):\n")
        for module in sorted(enabled_modules):
            f.write(f"  • {module}\n")
        
        if excluded_modules:
            f.write(f"\nExcluded Modules ({len(excluded_modules)}):\n")
            for module in sorted(excluded_modules):
                f.write(f"  ✗ {module}\n")
        
        f.write(f"\nEstimated Size Reduction: {config['estimated_size_reduction']}\n")
    
    print(f"✓ Generated feature manifest")


def build_package(
    compile_bytecode: bool = False,
    package_name: str = "lambda_function.zip"
) -> dict:
    """Build deployment package with selected features."""
    
    print("\n" + "=" * 60)
    print("Lambda Execution Engine - Feature-Selective Build")
    print("=" * 60 + "\n")
    
    config = validate_feature_configuration()
    
    print(f"Build Configuration:")
    print(f"  Features: {config['feature_count']}")
    print(f"  Modules: {len(config['enabled_modules'])}")
    print(f"  Excluded: {len(config['excluded_modules'])}")
    print(f"  Size Reduction: {config['estimated_size_reduction']}")
    print()
    
    clean_build_dirs()
    
    core_count = copy_core_files()
    module_count = copy_feature_modules(config['enabled_modules'])
    
    generate_feature_manifest(
        config['enabled_modules'],
        config['excluded_modules']
    )
    
    bytecode_count = 0
    if compile_bytecode:
        bytecode_count = compile_python_files(compile_bytecode)
    
    zip_path = create_deployment_package(package_name)
    
    print("\n" + "=" * 60)
    print("Build Complete")
    print("=" * 60)
    print(f"Package: {zip_path}")
    print(f"Size: {zip_path.stat().st_size / (1024 * 1024):.2f} MB")
    print(f"Files: {core_count + module_count}")
    if bytecode_count:
        print(f"Bytecode: {bytecode_count} files")
    print()
    
    return {
        "success": True,
        "package_path": str(zip_path),
        "package_size_mb": zip_path.stat().st_size / (1024 * 1024),
        "file_count": core_count + module_count,
        "bytecode_compiled": bytecode_count,
        "config": config
    }


def main():
    """Main entry point for build script."""
    parser = argparse.ArgumentParser(
        description="Build Lambda Execution Engine deployment package"
    )
    
    parser.add_argument(
        "--compile",
        action="store_true",
        help="Compile Python files to bytecode"
    )
    
    parser.add_argument(
        "--preset",
        choices=list(COMMON_PRESETS.keys()),
        help="Use feature preset"
    )
    
    parser.add_argument(
        "--features",
        help="Comma-separated list of features to include"
    )
    
    parser.add_argument(
        "--output",
        default="lambda_function.zip",
        help="Output package filename"
    )
    
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate configuration and exit"
    )
    
    args = parser.parse_args()
    
    if args.preset:
        os.environ["HA_FEATURE_PRESET"] = args.preset
    
    if args.features:
        os.environ["HA_FEATURES"] = args.features
    
    config = validate_feature_configuration()
    
    if args.validate:
        print("\nFeature Configuration:")
        print(f"  Enabled: {', '.join(config['enabled_features'])}")
        print(f"  Modules: {len(config['enabled_modules'])}")
        print(f"  Excluded: {len(config['excluded_modules'])}")
        print(f"  Size Reduction: {config['estimated_size_reduction']}")
        return 0
    
    result = build_package(
        compile_bytecode=args.compile,
        package_name=args.output
    )
    
    return 0 if result["success"] else 1


if __name__ == "__main__":
    sys.exit(main())
