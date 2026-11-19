---
name: evaluate-quality
description: Run fidelity, utility, and privacy diagnostics on a synthetic dataset against the real source, generating a markdown report.
---

# Evaluate Synthetic Data Quality

Run comprehensive diagnostics on a synthetic dataset against a real source dataset. Generates fidelity (how well statistics match), utility (usefulness for ML tasks), and privacy (leakage risk) reports. Outputs a markdown summary in `reports/<timestamp>/`.

## When to use

- User has generated synthetic data and wants to assess quality before use
- Need evidence of fidelity, utility, and privacy trade-offs
- Want to compare multiple synthesis approaches

## Inputs to gather

- **Real dataset path (CSV/Parquet):** Source data
- **Synthetic dataset path (CSV/Parquet):** Generated data
- **Dataset type:** `tabular` or `text`
- **Output path:** Where to save report (default: `./synthetic-data-workspace/reports/`)
- **Privacy mode:** Optional `text` evaluation (for unstructured records)

## Procedure

### For Tabular Data

1. **Dependencies:** `uv run --with sdmetrics --with pandas script.py`.

2. **Run fidelity and diagnostic reports:**
   ```python
   import pandas as pd
   from sdmetrics.reports.single_table import QualityReport, DiagnosticReport
   from datetime import datetime
   import os
   
   def evaluate_tabular(real_path, synth_path, output_dir):
       real_data = pd.read_csv(real_path)
       synth_data = pd.read_csv(synth_path)
       
       print(f"Real data shape: {real_data.shape}")
       print(f"Synthetic data shape: {synth_data.shape}")
       
       # Quality report (fidelity metrics)
       quality_report = QualityReport()
       quality_report.generate(real_data, synth_data)
       
       # Diagnostic report (column properties, relationships)
       diag_report = DiagnosticReport()
       diag_report.generate(real_data, synth_data)
       
       # Save reports as HTML
       os.makedirs(output_dir, exist_ok=True)
       timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
       quality_report.save_html(f'{output_dir}/quality_report_{timestamp}.html')
       diag_report.save_html(f'{output_dir}/diagnostic_report_{timestamp}.html')
       
       # Extract summary scores
       quality_score = quality_report.get_score()
       diag_score = diag_report.get_score()
       
       print(f"\nQuality score: {quality_score:.3f}")
       print(f"Diagnostic score: {diag_score:.3f}")
       
       return quality_report, diag_report
   
   if __name__ == '__main__':
       evaluate_tabular('real_data.csv', 'synthetic_data.csv', './reports')
   ```

3. **Generate a markdown summary:**
   ```python
   def generate_tabular_report(real_path, synth_path, output_dir, report_name="eval_report.md"):
       real_data = pd.read_csv(real_path)
       synth_data = pd.read_csv(synth_path)
       
       quality_report = QualityReport()
       quality_report.generate(real_data, synth_data)
       quality_score = quality_report.get_score()
       
       # Basic statistics comparison
       report_md = f"""# Synthetic Data Evaluation Report

## Dataset Summary
- Real data: {real_data.shape[0]} rows, {real_data.shape[1]} columns
- Synthetic data: {synth_data.shape[0]} rows, {synth_data.shape[1]} columns

## Fidelity (Quality Score: {quality_score:.3f}/1.0)
This measures how well synthetic data statistics match real data.

### Column Statistics
| Column | Real Mean | Synth Mean | Real Std | Synth Std |
|--------|-----------|-----------|----------|-----------|
"""
       
       for col in real_data.select_dtypes(include=['number']).columns:
           real_mean = real_data[col].mean()
           synth_mean = synth_data[col].mean()
           real_std = real_data[col].std()
           synth_std = synth_data[col].std()
           report_md += f"| {col} | {real_mean:.3f} | {synth_mean:.3f} | {real_std:.3f} | {synth_std:.3f} |\n"
       
       report_md += f"""
## Correlations
Compare Pearson correlations between real and synthetic data.

**Real data correlation matrix:**
```
{real_data.corr().to_string()}
```

**Synthetic data correlation matrix:**
```
{synth_data.corr().to_string()}
```

## Privacy Considerations
- Synthetic data should NOT be identical to real data (ensure diversity)
- Check for potential attribute disclosure (rare combinations of values)
- Consider differential privacy evaluation if privacy-critical

## Recommendations
- If score < 0.7: Consider refitting with different model/hyperparameters
- If score > 0.9: Good fidelity; verify utility on downstream tasks
- Always conduct domain-specific validation before production use
"""
       
       with open(f'{output_dir}/{report_name}', 'w') as f:
           f.write(report_md)
       
       print(f"Report saved to {output_dir}/{report_name}")
   ```

### For Text Records (LLM-generated)

1. **Dependencies:** `uv run --with sentence-transformers --with umap-learn --with scikit-learn --with matplotlib script.py` (embedding models run on CPU or a GPU box; for large sets use a hosted embedding API rather than a laptop). For quick wording-overlap and near-duplicate numbers on text, `check-diversity` is enough.

2. **Run embedding distribution and leakage checks:**
   ```python
   import json
   import numpy as np
   from sentence_transformers import SentenceTransformer
   from sklearn.metrics.pairwise import cosine_similarity
   import matplotlib.pyplot as plt
   
   def evaluate_text(real_path, synth_path, output_dir):
       model = SentenceTransformer('all-MiniLM-L6-v2')
       
       # Load records
       with open(real_path) as f:
           real_records = [json.loads(line) for line in f]
       with open(synth_path) as f:
           synth_records = [json.loads(line) for line in f]
       
       # Concatenate all fields for embedding
       real_texts = [' '.join(str(v) for v in r.values()) for r in real_records]
       synth_texts = [' '.join(str(v) for v in r.values()) for r in synth_records]
       
       # Embed
       real_embeddings = model.encode(real_texts, convert_to_numpy=True)
       synth_embeddings = model.encode(synth_texts, convert_to_numpy=True)
       
       # Nearest-neighbour leakage check
       similarities = cosine_similarity(synth_embeddings, real_embeddings)
       max_sims = np.max(similarities, axis=1)
       mean_sim = np.mean(max_sims)
       
       report_md = f"""# Synthetic Text Evaluation Report

## Dataset Summary
- Real records: {len(real_records)}
- Synthetic records: {len(synth_records)}

## Embedding-based Leakage Check
Measures how closely synthetic records match nearest real records by embedding similarity.

- Mean nearest-neighbour similarity: {mean_sim:.3f}
- Median: {np.median(max_sims):.3f}
- Max: {np.max(max_sims):.3f}
- Min: {np.min(max_sims):.3f}

**Interpretation:**
- If mean < 0.5: Good — synthetic records are distinct from real
- If mean > 0.7: Risk — potential attribute disclosure/memorization
- If any > 0.95: Alarm — record may be too similar to source

Flagged records (similarity > 0.8):
"""
       
       for i, sim in enumerate(max_sims):
           if sim > 0.8:
               real_idx = np.argmax(similarities[i])
               report_md += f"- Synth[{i}] ↔ Real[{real_idx}]: {sim:.3f}\n"
       
       # N-gram diversity
       from collections import Counter
       import re
       
       def extract_ngrams(texts, n=3):
           all_ngrams = Counter()
           for text in texts:
               tokens = re.findall(r'\w+', text.lower())
               for i in range(len(tokens) - n + 1):
                   ngram = tuple(tokens[i:i+n])
                   all_ngrams[ngram] += 1
           return all_ngrams
       
       real_ngrams = extract_ngrams(real_texts, n=3)
       synth_ngrams = extract_ngrams(synth_texts, n=3)
       
       report_md += f"""

## N-gram Diversity
- Real unique 3-grams: {len(real_ngrams)}
- Synth unique 3-grams: {len(synth_ngrams)}
- Overlap: {len(set(real_ngrams.keys()) & set(synth_ngrams.keys()))} ({100*len(set(real_ngrams.keys()) & set(synth_ngrams.keys()))/len(set(real_ngrams.keys()) | set(synth_ngrams.keys())):.1f}%)

## Recommendations
- If leakage scores > 0.7: Consider re-running synthesis with stricter transformation rules
- If diversity low: May need more varied personas or longer generation
- Validate semantic quality by manual spot-check of a few records
"""
       
       with open(f'{output_dir}/text_eval_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md', 'w') as f:
           f.write(report_md)
       
       print(f"Report saved")
       return {"mean_similarity": mean_sim, "n_gram_diversity": len(synth_ngrams)}
   ```

## Output / side effects

- Markdown evaluation report in `reports/<timestamp>/`
- For tabular: quality score (0–1), correlation comparisons, statistical checks
- For text: embedding-based leakage assessment, n-gram diversity, flagged records
- Optional: HTML reports and visualization plots

## Safety / constraints

- Quality score is relative; always validate against domain requirements
- Embedding-based leakage check is heuristic, not a formal privacy proof
- Reports are informational; high scores don't guarantee safety
- For privacy-critical applications, engage privacy experts before deployment
