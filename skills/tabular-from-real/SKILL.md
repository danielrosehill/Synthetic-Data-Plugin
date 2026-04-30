---
name: tabular-from-real
description: Fit a generative model on real tabular data and sample synthetic rows preserving correlations and distributions.
---

# Generate Tabular Data from Real Source

Learn a probabilistic model from a real dataset, then sample synthetic rows that preserve statistical properties (marginals, correlations, constraints).

## When to use

- User has a real tabular dataset and wants synthetic data with similar statistical structure
- Want to preserve correlations and data distributions, not just schema
- Faster iteration on synthetic data without fitting an LLM or GAN

## Inputs to gather

- **Real dataset path (CSV/Parquet):** Source data to fit
- **Output path:** Where to save synthetic data (default: `./synthetic-data-workspace/outputs/`)
- **Num samples:** How many synthetic rows to generate
- **Model choice:** `GaussianCopula` (fast, general), `CTGAN` (high-fidelity, slower), or `TVAE`
- **Multi-table:** If relational data, specify foreign keys

## Procedure

1. **Install SDV and SDMetrics:**
   ```bash
   pip install sdv sdmetrics
   ```

2. **Load real data and detect metadata:**
   ```python
   import pandas as pd
   from sdv.metadata import SingleTableMetadata
   from sdv.single_table import GaussianCopulaSynthesizer
   
   # Load real data
   real_data = pd.read_csv('real_data.csv')
   print(real_data.head())
   print(real_data.info())
   
   # Auto-detect metadata (column types, constraints)
   metadata = SingleTableMetadata.detect_from_dataframe(real_data)
   metadata.validate()
   print(metadata)
   ```

3. **Fit the synthesizer:**
   ```python
   # Option A: Fast general-purpose (GaussianCopula)
   synthesizer = GaussianCopulaSynthesizer(metadata)
   synthesizer.fit(real_data)
   
   # Option B: High-fidelity mixed-type (CTGAN, slower)
   # from sdv.single_table import CTGANSynthesizer
   # synthesizer = CTGANSynthesizer(metadata, epochs=100)
   # synthesizer.fit(real_data)
   ```

4. **Sample synthetic data:**
   ```python
   synthetic_data = synthesizer.sample(num_rows=1000)
   print(synthetic_data.head())
   
   # Save to CSV or Parquet
   synthetic_data.to_csv('synthetic_data.csv', index=False)
   # synthetic_data.to_parquet('synthetic_data.parquet', index=False)
   ```

5. **Optional: Multi-table synthesis (HMA):**
   ```python
   from sdv.metadata import MultiTableMetadata
   from sdv.multi_table import HMASynthesizer
   
   # If you have multiple related tables:
   metadata = MultiTableMetadata.detect_from_dataframes({
       'customers': customers_df,
       'orders': orders_df
   })
   metadata.set_relationships([
       {
           'parent_table_name': 'customers',
           'child_table_name': 'orders',
           'foreign_key_columns': {'order_customer_id': 'customer_id'}
       }
   ])
   
   synthesizer = HMASynthesizer(metadata)
   synthesizer.fit({'customers': customers_df, 'orders': orders_df})
   synthetic_tables = synthesizer.sample()
   ```

## Output / side effects

- Synthetic CSV/Parquet file with `num_rows` rows
- Column names, types, and distributions match the real data
- Correlations and constraints from real data are preserved
- Synthesizer model can be saved (e.g., `synthesizer.save('model.pkl')`) and reused

## Safety / constraints

- Ensure real data does not contain secrets or sensitive identifiers before fitting
- GaussianCopula assumes linear relationships; CTGAN better for nonlinear
- Synthetic data still may leak properties of the real data — run `evaluate-quality` to check
- For privacy-critical data, consider DP options (SDV's `synthesizer_kwargs={'epsilon': 1.0}`) or use Synthcity instead
