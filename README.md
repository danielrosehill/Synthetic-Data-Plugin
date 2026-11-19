# Synthetic Data Plugin

General-purpose synthetic data generation for AI work: training pairs, eval inputs, personas, scenarios,
read-aloud sentences for speech recording, support-style records, and tabular data. Vendor-agnostic: any
OpenAI-compatible API (OpenRouter and others), Anthropic, Gemini, or a local server. A batch API is one optional route.

Plugin name: `synthetic-data`. The core idea: variety comes from the **seed**, not the model or the temperature
(axes drawn in code, seeds written by a model in chunks, one item per seed, rotated writers, dedupe, diversity check).

## Skills

| Skill | Does |
| --- | --- |
| `setup` | Create or edit the private overlay: default routes and models, budget caps, diversity targets, saved recipes |
| `generate-text-data` | Main skill: seed-then-write generation of varied text on any route, with rotation, dedupe, pilot-first |
| `instruction-and-eval-data` | Instruction/response pairs, fine-tuning data, eval inputs and edge cases |
| `speech-recording-scripts` | Sentences and passages to read aloud for ASR/dictation data, term-anchored sets, mixed language |
| `check-diversity` | Trigram-Jaccard and top-word metrics, per-model breakdown, near-duplicate removal |
| `real-to-synth-llm` | Rewrite real text records into synthetic counterparts with an LLM, with a leakage check |
| `replace-pii` | Swap PII columns for realistic Faker values with deterministic mapping |
| `tabular-from-schema` | Tabular data from a JSON schema (Faker/Mimesis + distributions) |
| `tabular-from-real` | Fit SDV (GaussianCopula, CTGAN, TVAE) on a real CSV and sample |
| `evaluate-quality` | Fidelity, utility and privacy diagnostics; embedding leakage for text |
| `setup-workspace` | Per-project folder layout with a uv project |
| `tools-reference` | Reference card of OSS and hosted synthetic-data tools |

Built-in recipes (`recipes/`): `instruction-pairs`, `personas`, `asr-sentences`, `support-tickets`.

Scripts (`scripts/`, run with `uv run`, inline dependencies): `llm_generate.py` (any route, resumable, model rotation),
`axes.py` (seeded axis combinations), `diversity.py` (report and dedupe), `overlay-paths.sh`.

## Overlay (private user data)

The plugin holds no personal settings. They live in a data folder outside it, resolved in this order:

1. `$SYNTHETIC_DATA_DIR`
2. `$CLAUDE_USER_DATA/synthetic-data`
3. `~/.claude-user-data/synthetic-data` (if `~/.claude-user-data` exists)
4. `${XDG_DATA_HOME:-~/.local/share}/claude-plugins/synthetic-data`

```
<overlay>/
  preferences.md     default route/models, key env var NAME, budget cap, diversity targets, output dir, publish target
  recipes/<name>.md  saved recipes; same file name as a built-in overrides it
  model-notes.md     the user's own model measurements (optional)
```

`scripts/overlay-paths.sh` prints the resolved folder and the rule that chose it. Secrets are referenced by environment
variable name only. Caches go in `${CLAUDE_PLUGIN_DATA}`. Standard:
[Public-Plugin-Private-Overlay](https://github.com/danielrosehill/Public-Plugin-Private-Overlay).

## Install

```bash
claude plugins install synthetic-data@<marketplace>
```

## History

- 2026-11-19: renamed from `Claude-Synthetic-Data-Plugin`; absorbed the `synthetic-data-generation` skill from the
  Batch-Inference plugin (seed-then-write recipe, from an 11-model diversity probe on 2026-10-31); `text-records-llm`
  merged into `generate-text-data`; added the overlay, `setup`, `instruction-and-eval-data`,
  `speech-recording-scripts`, `check-diversity`; Python tooling moved to `uv`; Claude-CLI-only code made route-agnostic.
- Earlier: first release (v0.1.0) with tabular, PII, text-record and evaluation skills.

## License

MIT
