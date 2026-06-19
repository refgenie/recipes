"""Pytest configuration for recipe tests."""

from pathlib import Path

import pytest


@pytest.fixture
def fixtures_path() -> Path:
    """Path to test data directory."""
    return Path(__file__).parent / "data"


@pytest.fixture
def shared_tss_refgene(fixtures_path) -> Path:
    """Path to test refGene file with genes sharing TSS positions."""
    return fixtures_path / "shared_tss_refgene.txt"
