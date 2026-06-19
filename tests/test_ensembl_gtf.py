"""
Tests for ensembl_gtf recipe.

Verifies that the TSS extraction correctly preserves genes that share
the same transcription start site position (GitHub issue #282).
"""

from pathlib import Path

import pytest
import yaml


@pytest.fixture
def ensembl_gtf_recipe() -> dict:
    """Load the ensembl_gtf recipe YAML."""
    recipe_path = Path(__file__).parent.parent / "recipes" / "ensembl_gtf_asset_recipe.yaml"
    with open(recipe_path) as f:
        return yaml.safe_load(f)


def extract_tss_command(recipe: dict) -> str:
    """Extract the TSS generation command from the recipe."""
    for cmd in recipe["command_templates"]:
        if "_ensembl_TSS.bed" in cmd:
            return cmd
    raise ValueError("TSS command not found in recipe")


class TestEnsemblTSSExtraction:
    """Tests for ensembl TSS extraction."""

    def test_recipe_uses_fixed_command(self, ensembl_gtf_recipe: dict):
        """Verify the recipe YAML contains the fixed sort command."""
        tss_cmd = extract_tss_command(ensembl_gtf_recipe)

        assert "-k4,4" in tss_cmd or "-k4" in tss_cmd, (
            f"Recipe TSS command missing gene name sort key (-k4,4):\n{tss_cmd}"
        )
