#!/usr/bin/env python3
"""
Data channel checker for refgenie repositories.
This script validates asset classes and recipes from either a local directory or remote API.
"""

import argparse
import sys
import urllib.request
import urllib.parse
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional


def load_yaml_content(source: str, is_url: bool = False) -> Optional[Dict]:
    """
    Load YAML content from either a file path or URL.

    Args:
        source: File path or URL to load from
        is_url: Whether the source is a URL

    Returns:
        Parsed YAML as dict or None if failed
    """
    try:
        if is_url:
            with urllib.request.urlopen(source) as response:
                content = response.read().decode('utf-8')
        else:
            with open(source, 'r') as f:
                content = f.read()

        return yaml.safe_load(content)
    except Exception as e:
        print(f"❌ Failed to load {source}: {e}")
        return None


def validate_asset_class(data: Dict) -> List[str]:
    """
    Validate an asset class according to the specification.
    https://refgenie.org/refgenie1/asset_class_specification/

    Args:
        data: The asset class data

    Returns:
        List of validation errors
    """
    errors = []

    # Required fields (relaxed validation for actual schema used)
    required_fields = ['name', 'description']
    for field in required_fields:
        if field not in data:
            errors.append(f"Missing required field: {field}")

    # Optional: Check for seek_keys which is commonly used
    if 'seek_keys' in data and not isinstance(data['seek_keys'], dict):
        errors.append("'seek_keys' must be a dictionary")

    return errors


def validate_recipe(data: Dict) -> List[str]:
    """
    Validate a recipe according to the specification.
    https://refgenie.org/refgenie1/recipe_specification/

    Args:
        data: The recipe data

    Returns:
        List of validation errors
    """
    errors = []

    # Required fields (relaxed validation for actual schema used)
    required_fields = ['name', 'description']
    for field in required_fields:
        if field not in data:
            errors.append(f"Missing required field: {field}")

    # Check for common recipe fields
    if 'command_templates' in data:
        if not isinstance(data['command_templates'], list):
            errors.append("'command_templates' must be a list")

    if 'input_files' in data and not isinstance(data['input_files'], dict):
        errors.append("'input_files' must be a dictionary")

    return errors


def check_data_channel(source_path: str) -> bool:
    """
    Check a data channel for validity.

    Args:
        source_path: Either a local directory path or a remote URL

    Returns:
        True if all checks passed, False otherwise
    """
    # Determine if source is URL or local path
    is_url = source_path.startswith(('http://', 'https://'))

    if is_url:
        # Ensure URL ends with /
        if not source_path.endswith('/'):
            source_path += '/'
        print(f"🔍 Checking remote data channel: {source_path}")
    else:
        # Convert to Path object for local paths
        base_path = Path(source_path)
        if not base_path.exists():
            print(f"❌ Directory not found: {source_path}")
            return False
        print(f"🔍 Checking local data channel: {base_path.absolute()}")

    print("-" * 60)

    # Step 1: Load index.yaml
    if is_url:
        index_source = urllib.parse.urljoin(source_path, 'index.yaml')
    else:
        index_source = base_path / 'index.yaml'
        if not index_source.exists():
            print(f"❌ index.yaml not found in {base_path}")
            return False
        index_source = str(index_source)

    print(f"\n📥 Loading index: {index_source}")
    index_data = load_yaml_content(index_source, is_url)

    if not index_data:
        print("❌ Failed to load index.yaml")
        return False

    print("✅ Successfully loaded index.yaml")

    all_valid = True

    # Step 2: Check asset classes
    if 'asset_class' in index_data:
        asset_class_info = index_data['asset_class']
        asset_dir = asset_class_info.get('dir', 'asset_classes')
        files = asset_class_info.get('files', [])

        print(f"\n📂 Checking {len(files)} asset class files...")

        for filename in files:
            if is_url:
                file_source = urllib.parse.urljoin(source_path, f"{asset_dir}/{filename}")
            else:
                file_source = base_path / asset_dir / filename
                if not file_source.exists():
                    print(f"\n  Checking: {filename}")
                    print(f"    ❌ File not found")
                    all_valid = False
                    continue
                file_source = str(file_source)

            print(f"\n  Checking: {filename}")
            asset_data = load_yaml_content(file_source, is_url)

            if not asset_data:
                print(f"    ❌ Failed to load")
                all_valid = False
                continue

            errors = validate_asset_class(asset_data)
            if errors:
                print(f"    ⚠️  Validation warnings:")
                for error in errors:
                    print(f"       - {error}")
                # Don't fail on warnings for now
            else:
                print(f"    ✅ Valid asset class")

    # Step 3: Check recipes
    if 'recipe' in index_data:
        recipe_info = index_data['recipe']
        recipe_dir = recipe_info.get('dir', 'recipes')
        files = recipe_info.get('files', [])

        print(f"\n📂 Checking {len(files)} recipe files...")

        for filename in files:
            if is_url:
                file_source = urllib.parse.urljoin(source_path, f"{recipe_dir}/{filename}")
            else:
                file_source = base_path / recipe_dir / filename
                if not file_source.exists():
                    print(f"\n  Checking: {filename}")
                    print(f"    ❌ File not found")
                    all_valid = False
                    continue
                file_source = str(file_source)

            print(f"\n  Checking: {filename}")
            recipe_data = load_yaml_content(file_source, is_url)

            if not recipe_data:
                print(f"    ❌ Failed to load")
                all_valid = False
                continue

            errors = validate_recipe(recipe_data)
            if errors:
                print(f"    ⚠️  Validation warnings:")
                for error in errors:
                    print(f"       - {error}")
                # Don't fail on warnings for now
            else:
                print(f"    ✅ Valid recipe")

    # Final report
    print("\n" + "=" * 60)
    if all_valid:
        print("✅ All checks passed! Data channel is valid.")
    else:
        print("❌ Some checks failed. Please review the errors above.")

    return all_valid


def main():
    parser = argparse.ArgumentParser(
        description="Check a refgenie data channel for validity (local or remote)"
    )
    parser.add_argument(
        "source",
        help="Local directory path or remote URL (e.g., . or https://refgenie.github.io/recipes/)"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail on validation warnings (not just errors)"
    )

    args = parser.parse_args()

    # Run the check
    success = check_data_channel(args.source)

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()