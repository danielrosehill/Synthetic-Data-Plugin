---
name: text-records-llm
description: Generate synthetic text records (support tickets, reviews, medical notes, etc.) using Claude based on a persona pool and schema.
---

# Generate Synthetic Text Records with LLM

Create synthetic text records (customer support tickets, product reviews, medical notes, chat logs, etc.) using Claude. User specifies the record type, field schema, persona pool, count, and tone. The skill batch-generates records with optional deduplication by semantic similarity.

## When to use

- Need synthetic unstructured or semi-structured text (not tabular)
- Want semantically coherent, high-quality generated records
- Can afford API costs (Claude Haiku is economical for batch generation)
- Have a clear description of persona and tone

## Inputs to gather

- **Record type:** What kind of record (e.g., "customer support ticket", "product review", "medical note", "chat message")
- **Schema fields:** List of fields to generate (e.g., `["subject", "body", "priority"]` for a ticket)
- **Persona pool:** List of personas/contexts (e.g., `["angry customer", "confused user", "power user", "first-time buyer"]`)
- **Count:** Number of records to generate
- **Tone/style:** Descriptive instruction (e.g., "professional but frustrated", "casual and enthusiastic", "technical and concise")
- **Language:** Language to generate in (default: English)
- **Output path:** Where to save JSONL output (default: `./synthetic-data-workspace/outputs/`)

## Procedure

1. **Install Anthropic CLI and dependencies:**
   ```bash
   pip install anthropic pandas
   ```

2. **Draft a generation prompt template:**
   ```
   You are generating synthetic {record_type} records for testing/training purposes.
   
   Each record must be realistic, following this schema:
   {schema_json}
   
   Generate one record as valid JSON (no markdown, just raw JSON).
   Assume the persona: {persona}
   Tone/style: {tone}
   Language: {language}
   
   Ensure each field is filled with realistic, natural text.
   ```

3. **Write a batch generation script:**
   ```python
   import json
   import anthropic
   from itertools import cycle
   
   def generate_synthetic_records(record_type, schema_fields, personas, count,
                                   tone, language, output_path):
       client = anthropic.Anthropic()  # Uses ANTHROPIC_API_KEY env var
       
       schema_json = json.dumps({f: f"<{f} value>" for f in schema_fields})
       
       records = []
       persona_cycle = cycle(personas)
       
       for i in range(count):
           persona = next(persona_cycle)
           
           prompt = f"""You are generating synthetic {record_type} records for testing.
   
   Schema (as JSON):
   {schema_json}
   
   Generate ONE record. Return only valid JSON, no markdown.
   
   Persona: {persona}
   Tone: {tone}
   Language: {language}"""
           
           try:
               message = client.messages.create(
                   model="claude-3-5-haiku-20241022",  # Fast, economical
                   max_tokens=500,
                   messages=[
                       {"role": "user", "content": prompt}
                   ]
               )
               
               response_text = message.content[0].text.strip()
               
               # Try to parse as JSON; if markdown-wrapped, extract
               if response_text.startswith('```'):
                   response_text = response_text.split('```')[1].lstrip('json').strip()
               
               record = json.loads(response_text)
               records.append(record)
               
               if (i + 1) % 10 == 0:
                   print(f"Generated {i + 1}/{count} records...")
           
           except json.JSONDecodeError as e:
               print(f"Warning: failed to parse record {i+1}: {e}")
               continue
           except anthropic.APIError as e:
               print(f"API error on record {i+1}: {e}")
               continue
       
       # Save to JSONL
       with open(output_path, 'w') as f:
           for record in records:
               f.write(json.dumps(record) + '\n')
       
       print(f"Generated {len(records)} records to {output_path}")
       return records
   
   if __name__ == '__main__':
       schema = ["subject", "body", "priority", "category"]
       personas = [
           "An angry customer whose order arrived late",
           "A confused user having technical issues",
           "A power user reporting a feature request",
           "A first-time buyer with basic questions"
       ]
       
       generate_synthetic_records(
           record_type="customer support ticket",
           schema_fields=schema,
           personas=personas,
           count=50,
           tone="realistic and varied",
           language="English",
           output_path="synthetic_tickets.jsonl"
       )
   ```

4. **Optional: Deduplication by semantic similarity:**
   ```python
   import json
   from sklearn.metrics.pairwise import cosine_similarity
   from sklearn.feature_extraction.text import TfidfVectorizer
   
   def deduplicate_by_similarity(jsonl_path, threshold=0.85):
       """Remove records with cosine similarity > threshold to earlier records."""
       with open(jsonl_path) as f:
           records = [json.loads(line) for line in f]
       
       # Concatenate fields for similarity check
       texts = [' '.join(str(v) for v in r.values()) for r in records]
       
       vectorizer = TfidfVectorizer()
       tfidf = vectorizer.fit_transform(texts)
       similarities = cosine_similarity(tfidf)
       
       unique_records = [records[0]]
       for i in range(1, len(records)):
           # Check if this record is too similar to any earlier record
           max_sim = max(similarities[i, :i])
           if max_sim < threshold:
               unique_records.append(records[i])
       
       print(f"Kept {len(unique_records)} unique records (removed {len(records) - len(unique_records)})")
       return unique_records
   ```

5. **Run the script and verify:**
   ```bash
   python generate_text_records.py
   head synthetic_tickets.jsonl | python -m json.tool
   ```

## Output / side effects

- JSONL file (one JSON record per line) with generated synthetic text records
- Optional: deduplication report (near-duplicates removed)
- API calls to Claude (costs ~$0.01 per 100 records with Haiku)

## Safety / constraints

- **API costs:** Monitor usage; Haiku is economical but scale accordingly
- **Semantic quality:** LLM-generated text is semantically coherent; validate against domain requirements
- **Diversity:** Use persona pool to vary output; consider diversity checks before use
- **Language:** Ensure locale/language in prompt matches user intent
