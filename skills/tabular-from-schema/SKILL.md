---
name: tabular-from-schema
description: Generate a synthetic tabular dataset from a JSON schema describing columns, types, and Faker providers.
---

# Generate Tabular Data from Schema

Build a synthetic dataset from scratch using a user-supplied schema. Each column is defined by type (string, int, float, date, etc.), a Faker provider (e.g., "name", "email", "address"), or a distribution.

## When to use

- User has a schema but no real data yet
- Want to generate quick test/demo datasets with realistic values
- Schema-driven, fully controlled generation (no fitting to real data)

## Inputs to gather

- **Schema (JSON):** Columns with `name`, `type`, `faker_provider`, optional `locale` and `constraints`
- **Row count:** How many synthetic rows to generate
- **Output format:** CSV or Parquet
- **Output path:** Where to save the file (default: `./synthetic-data-workspace/outputs/`)

## Procedure

1. **Prepare a schema file (e.g., `schema.json`):**
   ```json
   {
     "columns": [
       {
         "name": "customer_id",
         "type": "int",
         "distribution": {"type": "sequential"}
       },
       {
         "name": "name",
         "type": "string",
         "faker_provider": "name"
       },
       {
         "name": "email",
         "type": "string",
         "faker_provider": "email"
       },
       {
         "name": "phone",
         "type": "string",
         "faker_provider": "phone_number"
       },
       {
         "name": "address",
         "type": "string",
         "faker_provider": "address"
       },
       {
         "name": "signup_date",
         "type": "date",
         "faker_provider": "date_between",
         "faker_kwargs": {"start_date": "-5y"}
       },
       {
         "name": "purchase_amount",
         "type": "float",
         "distribution": {"type": "normal", "mean": 100, "std": 25}
       }
     ]
   }
   ```

2. **Write a generation script:**
   ```python
   import json
   import pandas as pd
   import numpy as np
   from faker import Faker
   
   def generate_from_schema(schema_path, num_rows, output_path, locale='en_US'):
       with open(schema_path) as f:
           schema = json.load(f)
       
       fake = Faker(locale)
       data = {}
       
       for col in schema['columns']:
           name = col['name']
           col_type = col['type']
           provider = col.get('faker_provider')
           
           if provider:
               if col.get('faker_kwargs'):
                   data[name] = [getattr(fake, provider)(**col['faker_kwargs']) 
                                  for _ in range(num_rows)]
               else:
                   data[name] = [getattr(fake, provider)() for _ in range(num_rows)]
           elif 'distribution' in col:
               dist = col['distribution']
               if dist['type'] == 'sequential':
                   data[name] = list(range(1, num_rows + 1))
               elif dist['type'] == 'normal':
                   data[name] = np.random.normal(dist['mean'], dist['std'], num_rows)
               elif dist['type'] == 'uniform':
                   data[name] = np.random.uniform(dist['min'], dist['max'], num_rows)
           else:
               data[name] = [None] * num_rows
       
       df = pd.DataFrame(data)
       
       if output_path.endswith('.parquet'):
           df.to_parquet(output_path, index=False)
       else:
           df.to_csv(output_path, index=False)
       
       print(f"Generated {num_rows} rows to {output_path}")
       print(df.head())
   
   if __name__ == '__main__':
       generate_from_schema('schema.json', 1000, 'synthetic_data.csv')
   ```

3. **Run the script:**
   ```bash
   python generate_from_schema.py
   ```

4. **Verify output:**
   ```bash
   head -5 synthetic_data.csv
   wc -l synthetic_data.csv  # Check row count
   ```

## Output / side effects

- Synthetic CSV or Parquet file in the specified output directory
- File contains `num_rows` rows with realistic faker-generated values
- No fitting to real data; fully schema-driven

## Safety / constraints

- Locales must be valid Faker locales (e.g., `en_US`, `de_DE`, `ja_JP`)
- Distributions assume numeric columns; validate before use
- If using sequential IDs, ensure no duplicates needed elsewhere
