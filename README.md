# recipes (legacy — superseded by refgenie-registry)

> **Deprecated.** This repository is the recipe / asset-class data channel for
> the **legacy** refgenie (`refgenie` / `refgenconf` / `refgenieserver`), which
> is end-of-life. It is **not used by refgenie1**.
>
> **New recipes, asset classes, and build requests go to
> [refgenie-registry](https://github.com/refgenie/refgenie-registry)** — the
> single source of truth for refgenie1. refgenie1 builds directly from the
> registry, and that is also where users submit new recipes and request builds.
> Please do **not** open recipe PRs here.
>
> This repository is retained only to keep the legacy
> `https://refgenie.github.io/recipes/` data channel serving existing
> legacy-refgenie users during the transition.

This repository contains a community-organized set of recipes and asset class definition files for use with the **legacy** refgenie system.

## How to submit

New submissions are **no longer accepted here**. Contribute recipes and asset
classes to [refgenie-registry](https://github.com/refgenie/refgenie-registry)
instead (see its *Add a recipe* section). The indexing and validation steps
below apply only to maintaining the legacy data channel.


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

