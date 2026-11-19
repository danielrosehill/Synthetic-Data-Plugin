---
name: real-to-synth-llm
description: Transform real text records into synthetic counterparts that preserve semantics while changing specifics, with any LLM route.
---

# Transform Real Text to Synthetic with LLM

Convert real unstructured or semi-structured text records into synthetic counterparts that preserve semantic intent and structure while replacing all personally identifiable, datable, and location-specific details. Uses an LLM to intelligently rewrite records with explicit "preserve / change" rules.

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

1. **Dependencies** are inline in each script (`uv run --with scikit-learn --with numpy check_leakage.py`); no install step.

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

3. **Build jobs and run them on any route** (read the overlay `preferences.md` first for route, models, budget; see `generate-text-data`). One job per real record; the runner is resumable and vendor-agnostic:
   ```python
   # make_jobs.py  (run: uv run make_jobs.py real.jsonl > jobs.jsonl)
   # /// script
   # dependencies = ["pandas"]
   # ///
   import json, sys
   import pandas as pd
   path = sys.argv[1]
   rows = ([json.loads(l) for l in open(path)] if path.endswith(".jsonl")
           else pd.read_csv(path).to_dict(orient="records"))
   TEMPLATE = open("prompt.txt").read()   # the prompt from step 2 with {real_record_json}
   for i, r in enumerate(rows):
       print(json.dumps({"id": str(i), "prompt": TEMPLATE.replace("{real_record_json}", json.dumps(r, ensure_ascii=False))}))
   ```
   ```bash
   uv run "${CLAUDE_PLUGIN_ROOT}/scripts/llm_generate.py" jobs.jsonl --out synth_raw.jsonl \
     --route <route> --models <model> --workers 4 --limit 10     # pilot, then drop --limit
   ```
   Parse each `output` as JSON (strip markdown fences), drop and count failures. Real data goes only to a route the user approves for it; for sensitive records prefer a local route (`--route ollama`).

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
   uv run --with scikit-learn --with numpy check_leakage.py  # Optional QA
   ```

## Output / side effects

- JSONL file with transformed synthetic records
- Records match schema of real data but with anonymised content
- Optional: QA report flagging records with residual similarity to source
- API costs (small per record on a cheap model; estimate before a bulk run)

## Safety / constraints

- **Leakage risk:** LLM may inadvertently preserve identifying details — always run QA check
- **Semantic fidelity:** Transformation may alter nuance; validate against domain requirements
- **API costs and rate limits:** Monitor usage; implement backoff for rate-limit errors
- **Resume capability:** Script writes records incrementally; safe to interrupt and resume
- **Data handling:** Do not commit real data to version control; process locally
