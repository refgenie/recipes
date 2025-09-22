#!/usr/bin/env python3
"""
Script to automatically build the index.yaml file from the recipes folder structure.
This replaces the need to hard-code the yaml file manually.
"""

import yaml
from pathlib import Path


def build_index(recipes_dir="recipes", asset_classes_dir="asset_classes", output_path="index.yaml"):
    """
    Build index.yaml file from the directory structure of asset_classes and recipes.

    Args:
        recipes_dir: Path to the recipes directory containing asset_classes and recipes subdirs
    """
    recipes_path = Path(recipes_dir)
    asset_classes_path = Path(asset_classes_dir)

    # Check if directory exists
    if not recipes_path.exists():
        print(f"Error: Directory '{recipes_dir}' not found")
        return

    index_data = {}

    # Process asset_classes directory
    if asset_classes_path.exists() and asset_classes_path.is_dir():
        asset_files = sorted([f.name for f in asset_classes_path.iterdir()
                            if f.is_file() and f.suffix == '.yaml'])
        if asset_files:
            index_data['asset_class'] = {
                'dir': 'asset_classes',
                'files': asset_files
            }

    # Process recipes directory

    if recipes_path.exists() and recipes_path.is_dir():
        recipe_files = sorted([f.name for f in recipes_path.iterdir()
                             if f.is_file() and f.suffix == '.yaml'])
        if recipe_files:
            index_data['recipe'] = {
                'dir': 'recipes',
                'files': recipe_files
            }

    # Write the index.yaml file

    with open(output_path, 'w') as f:
        yaml.dump(index_data, f, default_flow_style=False, sort_keys=False)

    print(f"Successfully built index.yaml with:")
    if 'asset_class' in index_data:
        print(f"  - {len(index_data['asset_class']['files'])} asset class files")
    if 'recipe' in index_data:
        print(f"  - {len(index_data['recipe']['files'])} recipe files")
    print(f"Index file written to: {output_path}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Build index.yaml file from recipes directory structure"
    )
    parser.add_argument(
        "-r", "--recipes-dir",
        default="recipes",
        help="Path to the recipes directory (default: recipes)"
    )

    parser.add_argument(
        "-a", "--asset-classes-dir",
        default="asset_classes",
        help="Path to the asset_classes directory (default: asset_classes)"
    )

    parser.add_argument(
        "-o", "--output-path",
        default="index.yaml",
        help="Path to output index.yaml file (default: index.yaml)"
    )

    args = parser.parse_args()
    build_index(args.recipes_dir, args.asset_classes_dir, args.output_path)