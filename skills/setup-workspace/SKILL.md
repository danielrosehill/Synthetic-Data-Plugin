---
name: setup-workspace
description: Initialize a synthetic-data project folder (inputs, outputs, reports, configs) with a uv-managed Python project. Use on "start a synthetic data project", "set up a workspace for generated data".
---

# Set Up a Project Workspace

Per-project folder layout. User-wide preferences live in the overlay (`setup` skill), not here. Output location
defaults to the overlay's `output_dir` if set, else `./synthetic-data-workspace/`.

## Procedure

1. Create the layout and a uv project (Python 3.10+, uv only; no pip, no venv):
   ```bash
   mkdir -p synthetic-data-workspace/{inputs,outputs,reports,configs}
   cd synthetic-data-workspace && uv init --bare && uv add pandas numpy
   ```
2. Add only the packages the job needs, when it needs them: `uv add sdv sdmetrics` (tabular fit and evaluate),
   `uv add faker mimesis` (schema or PII swap), `uv add scikit-learn sentence-transformers` (text evaluation).
   One-off scripts can instead use `uv run --with <pkg> script.py`.
3. Write `README.md` describing the folders: `inputs/` real sources, `outputs/` generated data, `reports/`
   evaluation reports, `configs/` schemas and recipes.
4. Write `.gitignore` containing `inputs/`, `outputs/`, `.venv/` (real data and bulk output stay out of git).
5. Run generated scripts with `uv run script.py` from this folder.

If the folder exists, check for conflicts before writing. Never commit real source data.
