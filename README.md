# recipes

This repository contains a community-organized set of recipes and asset class definition files for use with the refgenie system.

## How to submit

Submissions via Pull Request are welcome. Subbmissions of new recipes will be reviewed and approved by the refgenie team. Just clone the repository, add your recipe or asset class files, and submit a PR.


## Indexing

The `build_index.py` script automatically generates the `index.yaml` file from the contents of the `asset_classes/` and `recipes/` directories. This eliminates the need to manually maintain the index file.

```sh
# From within the recipes directory:
python build_index.py --recipes recipes --asset-classes asset_classes -o index.yaml
```

This will scan both directories for YAML files and regenerate the `index.yaml` file.

## Validation

The `data_channel_check.py` script validates that all asset classes and recipes are properly formatted and accessible. It works with both local directories and remote URLs.

```sh
# Check local files (during development)
python data_channel_check.py .

# Check published data channel
python data_channel_check.py https://refgenie.github.io/recipes/
```

This will verify:
- All files listed in `index.yaml` exist
- YAML files are properly formatted
- Required fields are present in asset classes and recipes

