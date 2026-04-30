---
name: replace-pii
description: Anonymise a real dataset by replacing PII columns with realistic Faker values, preserving structure and referential integrity.
---

# Replace PII in Dataset

Anonymise a real dataset in place by replacing specified PII columns (name, email, phone, address, SSN, IP, DoB) with realistic fake values, while preserving non-PII columns and row count. Uses deterministic mapping to ensure repeated values (e.g., the same customer name appearing 5 times) map to the same fake name.

## When to use

- User has real data with PII (names, emails, phone numbers, addresses, SSNs, dates of birth, IP addresses)
- Want to replace PII with realistic fakes while keeping the dataset structure
- Need to preserve referential integrity (same real value → same fake value across rows)
- Quick anonymisation without fitting a generative model

## Inputs to gather

- **Real data path (CSV/Parquet):** Dataset to anonymise
- **PII columns:** List of column names and their types (e.g., `{"name": "name", "email": "email", "phone": "phone_number"}`)
- **Locale:** Faker locale for generated values (default: `en_US`; e.g., `de_DE`, `fr_FR`, `ja_JP`)
- **Output path:** Where to save anonymised data (default: `./synthetic-data-workspace/outputs/`)

## Procedure

1. **Install Faker:**
   ```bash
   pip install faker
   ```

2. **Write a PII replacement script:**
   ```python
   import pandas as pd
   import hashlib
   from faker import Faker
   
   def anonymise_pii(input_path, output_path, pii_columns, locale='en_US'):
       """
       Replace PII columns with faker-generated values.
       pii_columns: dict of {col_name: faker_provider}
       E.g. {'name': 'name', 'email': 'email', 'phone': 'phone_number',
             'address': 'address', 'ssn': 'ssn', 'dob': 'date_of_birth'}
       """
       fake = Faker(locale)
       df = pd.read_csv(input_path)
       
       # Deterministic mapping: hash(real_value) → seed → fake_value
       # Ensures same real PII → same fake PII across rows
       mapping = {}
       
       for col_name, provider in pii_columns.items():
           if col_name not in df.columns:
               print(f"Warning: column {col_name} not found, skipping")
               continue
           
           # Build mapping for this column
           col_mapping = {}
           for real_value in df[col_name].dropna().unique():
               real_value_str = str(real_value)
               
               # Deterministic seed from hash
               hash_int = int(hashlib.md5(real_value_str.encode()).hexdigest(), 16)
               seed = hash_int % (2**31)
               
               # Generate fake value with that seed
               Faker.seed(seed)
               fake_temp = Faker(locale)
               fake_temp.seed_instance(seed)
               
               # Get the fake value
               fake_value = getattr(fake_temp, provider)()
               col_mapping[real_value] = fake_value
           
           # Apply mapping to column
           df[col_name] = df[col_name].map(col_mapping)
           mapping[col_name] = col_mapping
           print(f"Replaced {col_name}: {len(col_mapping)} unique values")
       
       # Save anonymised data
       df.to_csv(output_path, index=False)
       print(f"Anonymised data saved to {output_path}")
       print(df.head())
       
       return df, mapping
   
   if __name__ == '__main__':
       pii_cols = {
           'customer_name': 'name',
           'email': 'email',
           'phone': 'phone_number',
           'address': 'address'
       }
       anonymise_pii('real_data.csv', 'anonymised_data.csv', pii_cols, locale='de_DE')
   ```

3. **Run the script:**
   ```bash
   python replace_pii.py
   ```

4. **Verify output:**
   ```bash
   head -5 anonymised_data.csv
   # Check that PII columns are replaced and non-PII columns unchanged
   ```

5. **Optional: Check referential integrity:**
   ```python
   # Verify that the same original PII value always maps to the same fake
   original_df = pd.read_csv('real_data.csv')
   anon_df = pd.read_csv('anonymised_data.csv')
   
   for col in pii_cols.keys():
       print(f"{col}: All rows with same real value mapped to same fake?")
       # This is guaranteed by deterministic seed, but can spot-check
   ```

## Output / side effects

- Anonymised CSV/Parquet file with same row count and structure
- PII columns replaced with realistic Faker values
- Non-PII columns unchanged
- Deterministic mapping ensures same real PII → same fake PII (referential integrity preserved)
- Original file untouched

## Safety / constraints

- This is **pseudonymisation**, not formal anonymisation — sophisticated re-identification may still be possible
- For formal privacy guarantees, use differential privacy (Synthcity or DataSynthesizer)
- Ensure output file is not shared without understanding residual re-identification risk
- Locales must match Faker's supported locales
- If mapping file needed for audit trail, save it separately (not recommended for sensitive environments)
