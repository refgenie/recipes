# Recipe Tests

Tests verify that the shell commands in recipe YAML files produce correct output, focusing on edge cases like shared genomic positions.

## What's tested

- **refgene_anno**: TSS extraction preserves genes sharing a transcription start site (GitHub issue [#282](https://github.com/refgenie/refgenie/issues/282)). Verifies both `_TSS.bed` (all genes) and `_TSS_unique.bed` (position-unique) outputs.
- **ensembl_gtf**: Ensures the Ensembl TSS recipe includes the gene-name sort key (`-k4,4`).

## Running

```bash
pip install -e ".[test]"
pytest
```
