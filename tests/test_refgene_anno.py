"""
Tests for refgene_anno recipe.

Verifies that the TSS extraction correctly preserves genes that share
the same transcription start site position (GitHub issue #282).
"""

import subprocess
from pathlib import Path

import pytest
import yaml


@pytest.fixture
def refgene_anno_recipe() -> dict:
    """Load the refgene_anno recipe YAML."""
    recipe_path = Path(__file__).parent.parent / "recipes" / "refgene_anno_asset_recipe.yaml"
    with open(recipe_path) as f:
        return yaml.safe_load(f)


def extract_tss_command(recipe: dict) -> str:
    """Extract the TSS generation command (all genes) from the recipe."""
    for cmd in recipe["command_templates"]:
        if "_TSS.bed" in cmd and "_TSS_unique" not in cmd:
            return cmd
    raise ValueError("TSS command not found in recipe")


def extract_tss_unique_command(recipe: dict) -> str:
    """Extract the TSS unique generation command from the recipe."""
    for cmd in recipe["command_templates"]:
        if "_TSS_unique.bed" in cmd:
            return cmd
    raise ValueError("TSS unique command not found in recipe")


class TestTSSExtraction:
    """Tests for TSS extraction from refGene annotation."""

    def test_shared_tss_genes_preserved(self, shared_tss_refgene: Path):
        """
        Test that genes sharing the same TSS position are all preserved.

        This is the regression test for GitHub issue #282:
        https://github.com/refgenie/refgenie/issues/282

        The bug was that `sort -k1,1 -k2,2n -u` would deduplicate based
        only on chromosome and position, losing genes like HYDIN and CMTR2
        that share a TSS. The fix adds `-k4,4` to include gene name.
        """
        # The fixed TSS extraction command (what the recipe should use)
        # Simplified version without the gzip and file paths
        tss_cmd = (
            f"cat {shared_tss_refgene} | grep -v '^#' | "
            "awk '{if($4==\"+\"){print $3\"\\t\"$5\"\\t\"$5\"\\t\"$13\"\\t.\\t\"$4}"
            "else{print $3\"\\t\"$6\"\\t\"$6\"\\t\"$13\"\\t.\\t\"$4}}' | "
            "LC_COLLATE=C sort -k1,1 -k2,2n -k4,4 -u"
        )

        result = subprocess.run(
            tss_cmd,
            shell=True,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0, f"Command failed: {result.stderr}"

        output_lines = result.stdout.strip().split("\n")
        gene_names = [line.split("\t")[3] for line in output_lines if line]

        # Both HYDIN and CMTR2 share chr16:1000 TSS - both must be present
        assert "HYDIN" in gene_names, "HYDIN missing - shared TSS gene was deduplicated"
        assert "CMTR2" in gene_names, "CMTR2 missing - shared TSS gene was deduplicated"

        # Both MINUSGENE1 and MINUSGENE2 share chr2:8000/9000 positions
        # (minus strand uses txEnd for TSS, which differ, so both should be present anyway)
        assert "MINUSGENE1" in gene_names
        assert "MINUSGENE2" in gene_names

        # Sanity check - GENE3 should also be present
        assert "GENE3" in gene_names

    def test_unique_tss_deduplicates_by_position(self, shared_tss_refgene: Path):
        """
        Test that TSS_unique deduplicates by position, keeping one entry per locus.

        This is the position-unique variant: genes sharing the same TSS
        position are collapsed to a single entry.
        """
        unique_cmd = (
            f"cat {shared_tss_refgene} | grep -v '^#' | "
            "awk '{if($4==\"+\"){print $3\"\\t\"$5\"\\t\"$5\"\\t\"$13\"\\t.\\t\"$4}"
            "else{print $3\"\\t\"$6\"\\t\"$6\"\\t\"$13\"\\t.\\t\"$4}}' | "
            "LC_COLLATE=C sort -k1,1 -k2,2n -u"
        )

        result = subprocess.run(
            unique_cmd,
            shell=True,
            capture_output=True,
            text=True,
        )

        output_lines = result.stdout.strip().split("\n")
        gene_names = [line.split("\t")[3] for line in output_lines if line]

        # With position-unique dedup, only ONE of HYDIN/CMTR2 should survive
        shared_tss_genes = [g for g in gene_names if g in ("HYDIN", "CMTR2")]
        assert len(shared_tss_genes) == 1, (
            f"Expected only 1 of HYDIN/CMTR2 in position-unique output, "
            f"got {len(shared_tss_genes)}: {shared_tss_genes}"
        )

    def test_recipe_has_both_tss_commands(self, refgene_anno_recipe: dict):
        """Verify the recipe YAML contains both TSS and TSS_unique commands."""
        tss_cmd = extract_tss_command(refgene_anno_recipe)
        tss_unique_cmd = extract_tss_unique_command(refgene_anno_recipe)

        assert "-k4,4" in tss_cmd or "-k4" in tss_cmd, (
            f"Recipe TSS command missing gene name sort key (-k4,4):\n{tss_cmd}"
        )
        assert "_TSS_unique.bed" in tss_unique_cmd, (
            f"Recipe TSS unique command missing output file:\n{tss_unique_cmd}"
        )
        # The unique command should NOT have -k4,4 (dedup by position only)
        assert "-k4,4" not in tss_unique_cmd, (
            f"Recipe TSS unique command should not include -k4,4:\n{tss_unique_cmd}"
        )
