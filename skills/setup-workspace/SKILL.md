---
name: setup-workspace
description: Initialize a synthetic data workspace directory with standard folders, Python requirements, and venv setup.
---

# Set Up Workspace

Initialize a workspace for synthetic data generation tasks. This creates folder structure, a Python requirements file, and optionally a virtual environment.

## When to use

- Starting a new synthetic data project
- Want to organize outputs, inputs, configs, and reports in one place
- Need a repeatable, version-controlled setup

## Inputs to gather

- **Workspace path** (optional; default: `./synthetic-data-workspace/` in current directory)
- **Python version check** (requires 3.10+; script offers venv setup)
- **Tool selection** (SDV, Faker, Synthcity, etc. — user can customize requirements later)

## Procedure

1. **Create folder structure:**
   ```bash
   mkdir -p ./synthetic-data-workspace/{inputs,outputs,reports,configs}
   ```

2. **Create a `README.md` describing the workspace layout:**
   ```markdown
   # Synthetic Data Workspace

   - `inputs/` — Real source datasets (CSV, Parquet, JSON)
   - `outputs/` — Generated synthetic datasets
   - `reports/` — Quality evaluation reports
   - `configs/` — YAML/JSON configuration files (schemas, synthesis params)

   ## Quick start

   1. Activate venv: `source venv/bin/activate` (if created)
   2. Place real data in `inputs/`
   3. Define schema or config in `configs/`
   4. Run synthesis skill (e.g. `tabular-from-real`)
   5. Check outputs in `outputs/` and reports in `reports/`
   ```

3. **Create `requirements.txt` with common tools:**
   ```
   sdv>=1.10.0
   sdmetrics>=0.11.0
   faker>=20.0.0
   mimesis>=7.0.0
   synthcity>=0.2.0
   pandas>=2.0.0
   numpy>=1.24.0
   pyarrow>=12.0.0
   scikit-learn>=1.3.0
   umap-learn>=0.5.0
   ```
   (User can edit to remove unnecessary packages.)

4. **Check Python version:**
   ```bash
   python3 --version  # Must be 3.10 or higher
   ```

5. **Offer venv setup:**
   ```bash
   cd ./synthetic-data-workspace
   python3 -m venv venv
   source venv/bin/activate
   pip install --upgrade pip
   pip install -r ../requirements.txt
   ```

6. **Record workspace path** for other skills (e.g. in a `.workspace-config` file or environment variable):
   ```bash
   echo "SYNTHETIC_DATA_WORKSPACE=$(pwd)" > .workspace-config
   ```

## Output / side effects

- Folder structure in place: `./synthetic-data-workspace/{inputs,outputs,reports,configs}/`
- `requirements.txt` created and ready to customize
- `README.md` with usage guide
- Optional: virtual environment activated, dependencies installed
- Workspace path recorded for future skill invocations

## Safety / constraints

- If workspace folder already exists, check for conflicts before overwriting structure
- Recommend the user commit workspace config to version control (except large data files — add `inputs/` and `outputs/` to `.gitignore`)
