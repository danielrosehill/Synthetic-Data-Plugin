---
name: real-to-synth-llm
description: Transform real text records into synthetic counterparts that preserve semantics while changing specifics, using Claude.
---

# Transform Real Text to Synthetic with LLM

Convert real unstructured or semi-structured text records into synthetic counterparts that preserve semantic intent and structure while replacing all personally identifiable, datable, and location-specific details. Uses Claude to intelligently rewrite records with explicit "preserve / change" rules.

## When to use

- Have real text records (customer reviews, medical notes, support tickets, emails) that must be anonymised
- Want to preserve intent, sentiment, and structure but change all specifics
- Prefer LLM-driven paraphrasing over simple PII replacement
- Can afford API costs for batch transformation

## Inputs to gather

- **Real data path (JSONL or CSV with text column):** Source records
- **Record type:** Description of what the records represent (e.g., "customer support tickets", "medical notes")
- **Fields to preserve:** Which fields to keep unchanged (e.g., "category", "priority")
- **Fields to transform:** Which fields to rewrite (e.g., "body", "customer_name")
- **Preservation rules:** Explicit constraints (e.g., "preserve length distribution", "preserve tone", "remove all dates")
- **Output path:** Where to save transformed JSONL (default: `./synthetic-data-workspace/outputs/`)
- **QA threshold:** Semantic similarity cap (default: 0.75) — flag records that stay too close to source

## Procedure

1. **Install Anthropic and dependencies:**
   ```bash
   pip install anthropic pandas tqdm numpy scikit-learn
   ```

2. **Draft a transformation prompt with explicit rules:**
   ```
   You are anonymising {record_type} for research/testing purposes.
   
   Read this real record:
   {real_record_json}
   
   Rewrite it as a synthetic record following these rules:
   - PRESERVE: semantic intent, tone, structure, technical content, logical flow
   - PRESERVE: {preservation_rules}
   - CHANGE: all names, places, dates, email addresses, phone numbers, URLs, IDs
   - CHANGE: specific quoted text, proper nouns, organizational names
   - MAINTAIN: field schema, word count approximately
   
   Return only valid JSON, no markdown.
   ```

3. **Write a batch transformation script with progress and resume:**
   ```python
   import json
   import anthropic
   import pandas as pd
   from pathlib import Path
   import time
   
   def transform_records(input_path, output_path, record_type,
                         preserve_rules, transform_fields, locale="en"):
       client = anthropic.Anthropic()
       
       # Load real records
       if input_path.endswith('.jsonl'):
           with open(input_path) as f:
               real_records = [json.loads(line) for line in f]
       else:  # CSV
           df = pd.read_csv(input_path)
           real_records = df.to_dict(orient='records')
       
       # Track progress and resume if interrupted
       completed = set()
       if Path(output_path).exists():
           with open(output_path) as f:
               completed = {i for i, _ in enumerate(f)}
       
       synthetic_records = []
       
       for idx, real_record in enumerate(real_records):
           if idx in completed:
               continue
           
           record_json = json.dumps(real_record, indent=2)
           
           prompt = f"""Transform this {record_type} into a synthetic version:

   {record_json}
   
   Rules:
   - PRESERVE semantic intent, tone, structure, technical details
   - PRESERVE: {preserve_rules}
   - CHANGE ALL: names, locations, dates, emails, phone numbers, IDs, URLs
   - CHANGE: specific quoted text and proper nouns
   - MAINTAIN: approximate length and field schema
   
   Return ONLY valid JSON, no markdown or explanation."""
           
           try:
               message = client.messages.create(
                   model="claude-3-5-haiku-20241022",
                   max_tokens=1000,
                   messages=[{"role": "user", "content": prompt}]
               )
               
               response_text = message.content[0].text.strip()
               
               # Strip markdown if present
               if response_text.startswith('```'):
                   response_text = response_text.split('```')[1].lstrip('json').strip()
               
               synthetic_record = json.loads(response_text)
               
               # Append to output (streaming write for resume capability)
               with open(output_path, 'a') as f:
                   f.write(json.dumps(synthetic_record) + '\n')
               
               synthetic_records.append(synthetic_record)
               
               if (idx + 1) % 10 == 0:
                   print(f"Transformed {idx + 1}/{len(real_records)} records...")
               
               # Politeness: small delay between API calls
               time.sleep(0.5)
           
           except json.JSONDecodeError as e:
               print(f"Warning: JSON parse error on record {idx}: {e}")
               continue
           except anthropic.APIError as e:
               print(f"API error on record {idx}: {e}")
               time.sleep(2)
               continue
       
       print(f"Transformed {len(synthetic_records)} records to {output_path}")
       return synthetic_records
   
   if __name__ == '__main__':
       transform_records(
           input_path="real_tickets.jsonl",
           output_path="synthetic_tickets.jsonl",
           record_type="customer support ticket",
           preserve_rules="priority level, issue category, technical complexity",
           transform_fields=["customer_name", "body", "email"]
       )
   ```

4. **Optional: QA check for leakage (flag records too similar to source):**
   ```python
   import numpy as np
   from sklearn.feature_extraction.text import TfidfVectorizer
   from sklearn.metrics.pairwise import cosine_similarity
   
   def check_leakage(real_path, synth_path, threshold=0.75):
       with open(real_path) as f:
           real_records = [json.loads(line) for line in f]
       with open(synth_path) as f:
           synth_records = [json.loads(line) for line in f]
       
       # Concatenate all text fields
       real_texts = [' '.join(str(v) for v in r.values()) for r in real_records]
       synth_texts = [' '.join(str(v) for v in r.values()) for r in synth_records]
       
       vectorizer = TfidfVectorizer()
       all_texts = real_texts + synth_texts
       tfidf = vectorizer.fit_transform(all_texts)
       
       flagged = []
       for i, synth_idx in enumerate(range(len(real_texts), len(all_texts))):
           similarity = cosine_similarity(tfidf[synth_idx], tfidf[:len(real_texts)])
           max_sim = np.max(similarity)
           
           if max_sim > threshold:
               flagged.append({
                   'synthetic_record_idx': i,
                   'max_similarity': float(max_sim),
                   'closest_real_idx': int(np.argmax(similarity))
               })
       
       if flagged:
           print(f"Flagged {len(flagged)} records with similarity > {threshold}")
           for f in flagged[:5]:
               print(f"  Record {f['synthetic_record_idx']}: similarity={f['max_similarity']:.3f}")
       else:
           print(f"All {len(synth_records)} records passed leakage check (similarity < {threshold})")
       
       return flagged
   ```

5. **Run transformation and QA:**
   ```bash
   python transform_real_to_synth.py
   python check_leakage.py  # Optional QA
   ```

## Output / side effects

- JSONL file with transformed synthetic records
- Records match schema of real data but with anonymised content
- Optional: QA report flagging records with residual similarity to source
- API costs (~$0.01–0.05 per record with Haiku, depending on length)

## Safety / constraints

- **Leakage risk:** LLM may inadvertently preserve identifying details — always run QA check
- **Semantic fidelity:** Transformation may alter nuance; validate against domain requirements
- **API costs and rate limits:** Monitor usage; implement backoff for rate-limit errors
- **Resume capability:** Script writes records incrementally; safe to interrupt and resume
- **Data handling:** Do not commit real data to version control; process locally
