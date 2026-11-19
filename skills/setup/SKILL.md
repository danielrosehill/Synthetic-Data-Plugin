---
name: setup
description: Create or edit the user's private synthetic-data preferences (default models and routes, budget caps, diversity targets, output locations) and saved recipes. Use on "set up synthetic data", "synthetic data preferences", "change my default generation model", "save this as a recipe", "where are my synthetic-data settings".
---

# Set up the overlay

The plugin is generic. The user's own settings live in a private folder (the overlay), outside the plugin,
so plugin updates never touch them.

## Find it

```bash
"${CLAUDE_PLUGIN_ROOT}/scripts/overlay-paths.sh"
```

Resolution order: `$SYNTHETIC_DATA_DIR`, `$CLAUDE_USER_DATA/synthetic-data`, `~/.claude-user-data/synthetic-data`
(if `~/.claude-user-data` exists), `${XDG_DATA_HOME:-~/.local/share}/claude-plugins/synthetic-data`, else
`~/.claude-user-data/synthetic-data`. Never write inside the plugin directory. Caches go in `${CLAUDE_PLUGIN_DATA}`.

## Layout

```
<overlay>/
  preferences.md     defaults, read first by every generation skill
  recipes/<name>.md  saved recipes; same file name as a built-in in the plugin's recipes/ overrides it
  model-notes.md     optional: the user's own measurements (which models were varied, collapsed, refused options)
```

## preferences.md

Plain `key: value` lines under headings; unknown keys are ignored. Keys the skills read:

```
route: openrouter                # openrouter | openai | gemini | anthropic | ollama | openai-compat
base_url:                        # only for openai-compat / local servers
key_env: OPENROUTER_API_KEY      # NAME of the environment variable only, never a value
seed_model: <model id>           # cheap model that writes seed lists
writer_models: <id>, <id>, <id>  # 2-3 families, rotated by item index
use_batch_api: no                # yes only if the route has a cheaper async lane worth the wait
pilot_size: 30
budget_cap_usd: 5                # ask before any run estimated above this; pilots under 0.25 go ahead
diversity_max_trigram_jaccard: 0.07
diversity_max_top3_share: 0.4
dedupe_threshold: 0.5
default_language: en
output_dir: ./synthetic-data-workspace/outputs
publish_to:                      # e.g. a Hugging Face org/namespace, empty = never publish
```

## Procedure

1. Run `overlay-paths.sh`; create the folder if missing (`mkdir -p <dir>/recipes`).
2. If `preferences.md` exists, show it and edit only the keys the user names. Otherwise ask for route, models,
   budget cap and output location (offer to run the `generate-text-data` pilot to pick models), then write it.
3. "Save this as a recipe": copy the recipe just used from `recipes/` format (see `generate-text-data`) into
   `<overlay>/recipes/<name>.md`. Reusing a built-in name overrides it.
4. Report the path written. If the overlay folder is inside a git repo, stage only this plugin's folder.

Secrets: record only the environment variable name, never a value.
