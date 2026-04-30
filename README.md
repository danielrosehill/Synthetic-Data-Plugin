# Synthetic Data

Generate synthetic datasets — from a schema, from a real source, or via LLM-driven persona generation. Includes utilities for PII replacement, real-to-synth transformation, and quality/privacy evaluation.

## Skills

- `tools-reference` — Reference card of recommended OSS tooling (SDV, Synthcity, Faker, Mimesis, DataSynthesizer, ydata-synthetic, Gretel, time-series and LLM options).
- `setup-workspace` — Initialize a workspace folder (`inputs/`, `outputs/`, `reports/`, `configs/`) and a `requirements.txt`.
- `tabular-from-schema` — Generate tabular data from a JSON schema (Faker/Mimesis + numpy distributions).
- `tabular-from-real` — Fit SDV (`GaussianCopula`, `CTGAN`, `TVAE`) on a real CSV and sample synthetic rows preserving marginals + correlations.
- `replace-pii` — Swap PII columns in a real dataset for realistic Faker values, with deterministic mapping for referential integrity.
- `text-records-llm` — Generate synthetic text records (tickets, reviews, notes) via the Claude CLI with persona/style controls and dedup.
- `real-to-synth-llm` — LLM-driven transformation of real records into synthetic counterparts that preserve semantic structure but change all specifics.
- `evaluate-quality` — Fidelity, utility, and privacy diagnostics (SDMetrics for tabular; embedding-based leakage and n-gram diversity for text).

## Installation

```bash
claude plugins install synthetic-data@danielrosehill
```

Or, scoped to a single project:

```bash
claude plugins install synthetic-data@danielrosehill --scope project
```

## License

MIT
