---
name: check-diversity
description: Measure how repetitive a generated text set is (trigram Jaccard, top-word share, per-model breakdown) and remove near-duplicates. Use on "is this too samey", "dedupe the generated data", "diversity check", "check the pilot before scaling".
---

# Diversity and dedupe

Stdlib-only scripts, run with `uv run` (no install).

```bash
uv run "${CLAUDE_PLUGIN_ROOT}/scripts/diversity.py" report items.jsonl --field text --group-field model
uv run "${CLAUDE_PLUGIN_ROOT}/scripts/diversity.py" dedupe items.jsonl --field text --out clean.jsonl --threshold 0.5
```

Targets for free text come from the overlay `preferences.md` (`diversity_max_trigram_jaccard`, default 0.07;
`diversity_max_top3_share`, default 0.4; `dedupe_threshold`, default 0.5). `--field` is the JSON key holding the
text; for records with several fields, concatenate them into one field first.

## Reading the numbers

- **Mean pairwise trigram Jaccard** (sampled to 400 items): wording overlap. Above target: change the seeds or
  rotate more model families.
- **Top-3 content-word share**: topic concentration (the "dentist and dry cleaning" effect). Above target: the
  seed axes are too narrow; add values or axes. Changing temperature or model will not fix it.
- **Per-group**: with `--group-field model`, find the collapsing model and drop it from the rotation.
- **Dedupe**: drops items whose content-word Jaccard to an earlier kept item is at or above the threshold; report
  the dropped count. For embedding-based checks (cosine 0.9 or more) see `evaluate-quality`.

Always read about 10 items by eye after the numbers: metrics miss shared structure (every item opening the same
way, same length, same ending).
