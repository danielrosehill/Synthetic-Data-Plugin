---
name: tools-reference
description: Reference card of open-source synthetic data tools, when to use each, install commands, and design patterns.
---

# Tools Reference

A curated reference of open-source and cloud synthetic data tools. Use this skill when the user asks which tool to pick for their use case, or wants to understand the landscape.

## Tabular data

### SDV (Synthetic Data Vault)
**What it does:** Learns probability distribution from real data, then samples synthetic rows that preserve marginals, correlations, and constraints.

**When to use:**  
- Real tabular data → synthetic tabular data (preserving statistical properties)
- Fast iteration on schema-less synthesis
- Single-table or multi-table (relational) datasets

**Pros:** Mature, multi-table support, handles mixed types, row/column constraints, reversible transformations.  
**Cons:** Slower for very high-dimensional data; assumes stationarity.

**Key models:**
- `GaussianCopulaSynthesizer` — fast, general, works well for continuous/categorical mix
- `CTGANSynthesizer` — neural-network-based, high fidelity on mixed types, slower to fit
- `TVAESynthesizer` — variational autoencoder, good balance of speed/fidelity
- `HMASynthesizer` — multi-table, learns foreign-key relationships

**Install:** `uv run --with sdv script.py` (or `uv add sdv` in a project)  
**Quality eval:** `uv run --with sdmetrics script.py` (or `uv add sdmetrics` in a project)

### Synthcity
**What it does:** Plugin-based generative synthesis with support for differential privacy, fairness constraints, and time-series.

**When to use:**  
- Privacy-sensitive tabular synthesis with formal privacy budgets
- Time-series generation
- Fairness/bias constraints on synthetic output

**Pros:** DP guarantees, plugin architecture, time-series module.  
**Cons:** Steeper learning curve; fewer pre-packaged models than SDV.

**Install:** `uv run --with synthcity script.py` (or `uv add synthcity` in a project)

### DataSynthesizer
**What it does:** Differentially-private tabular synthesis using Gaussian copula or uniform sampling.

**When to use:**  
- Data that must satisfy formal differential-privacy (DP) constraints
- Compliance-heavy industries (HIPAA, GDPR)
- Schema is known or easily inferred

**Pros:** Formal privacy guarantees, simple API, fast.  
**Cons:** Limited to DP copula approach; less flexible than SDV.

**Install:** `uv run --with DataSynthesizer script.py` (or `uv add DataSynthesizer` in a project)

### ydata-synthetic
**What it does:** GAN-based tabular and time-series synthesis.

**When to use:**  
- High-fidelity tabular synthesis where neural approaches needed
- Time-series with adversarial training

**Pros:** Strong empirical fidelity; time-series support.  
**Cons:** Training can be unstable; hyperparameter-sensitive.

**Install:** `uv run --with ydata-synthetic script.py` (or `uv add ydata-synthetic` in a project)

## Field-level (record-wise) generation

### Faker
**What it does:** Generates realistic fake values for common fields (names, emails, phone numbers, addresses, dates, credit cards, SSNs, IP addresses, etc.) with locale support.

**When to use:**  
- Schema-based generation (you define columns, Faker fills values)
- PII replacement (swap real names/emails with fake ones)
- Creating realistic test data quickly
- Localized personas (de_DE, fr_FR, ja_JP, etc.)

**Pros:** Simple, fast, extremely customizable, 50+ locales.  
**Cons:** No correlation learning; purely random per-field.

**Install:** `uv run --with faker script.py` (or `uv add faker` in a project)

**Example:**
```python
from faker import Faker
fake = Faker('de_DE')
print(fake.name(), fake.email(), fake.phone_number())
```

### Mimesis
**What it does:** Similar to Faker — generates localized fake data with additional structure (e.g. geography, person relationships).

**When to use:**  
- Alternative to Faker with slightly different provider library
- Data generation with geographic/organizational context

**Pros:** Compact, fast, good geographic support.  
**Cons:** Smaller ecosystem than Faker.

**Install:** `uv run --with mimesis script.py` (or `uv add mimesis` in a project)

## Time-series

### Chronos (Amazon)
**What it does:** LLM-based probabilistic time-series forecasting and generation.

**When to use:**  
- Synthetic time-series that extrapolate real historical patterns
- Pre-trained foundation model approach (zero-shot)

**Pros:** Pre-trained, handles multiple series lengths.  
**Cons:** Requires external service or local inference.

**Install:** Via Hugging Face, `huggingface_hub`

### TimeGAN
**What it does:** Generative adversarial network for time-series synthesis.

**When to use:**  
- Synthetic sequences that preserve temporal dependencies
- Long sequences with complex dynamics

**Pros:** Good temporal fidelity.  
**Cons:** Training instability; requires careful hypertuning.

**Install:** Via research implementations (e.g. GitHub repos)

## Unstructured/Text

### LLM APIs (vendor-agnostic)
**What it does:** Any chat model (OpenRouter or another OpenAI-compatible API, Anthropic, Gemini, or a local Ollama, vLLM or llama.cpp server) generates or transforms text from prompts describing persona, tone, intent and schema.

**When to use:**  
- Synthetic text (tickets, reviews, notes, chat logs, instruction pairs, read-aloud sentences, personas)
- Real-to-synthetic transformation (change specifics, preserve semantics)
- Semantic coherence preferred over speed

**Pros:** Flexible, human-readable output, custom logic via prompts.  
**Cons:** API cost; needs a key (or a local model); collapses to "typical" content unless seeded.

**Use:** this plugin's `scripts/llm_generate.py` (httpx only, any route, resumable) via `generate-text-data`. Batch APIs are a cheaper async option on some routes.

## Cloud / Fully-managed

### Gretel CLI
**What it does:** Client for Gretel's cloud-based synthetic data platform. Uploads data, trains models in the cloud, downloads synthetic data.

**When to use:**  
- User prefers cloud-hosted synthesis (no local infra)
- Need advanced options (differential privacy, data transforms) without local setup
- Data governance / audit trail required

**Pros:** Managed service, no local compute, audit trail.  
**Cons:** Costs; data leaves local network.

**Install:** `uv run --with gretel-client script.py` (or `uv add gretel-client` in a project)

## Choosing a tool

| Use case | Recommended | Alternatives |
|----------|-------------|--------------|
| Real tabular → synthetic | SDV (GaussianCopula) | Synthcity, ydata-synthetic |
| Mixed-type tabular, high fidelity | SDV (CTGAN) | ydata-synthetic (GAN), Gretel |
| Privacy-sensitive tabular | Synthcity, DataSynthesizer | SDV + manual DP |
| Multi-table relational | SDV (HMA) | Synthcity with custom |
| Schema-based tabular (fake) | Faker + Mimesis | custom generation |
| PII replacement on real data | Faker + deterministic mapping | ydata-synthetic (PII aware) |
| Synthetic text records | LLM API (`generate-text-data`) | ydata-synthetic (text models) |
| Real text → synthetic (paraphrase) | LLM API with prompts | fine-tuned LLMs |
| Time-series forecasting | Chronos | SDV (multivariate time) |
| Time-series GAN-based | TimeGAN, ydata-synthetic | SDV (univariate) |

---

**Next:** Choose your use case, then refer to the appropriate skill (`tabular-from-schema`, `tabular-from-real`, `generate-text-data`, etc.) for step-by-step execution.
