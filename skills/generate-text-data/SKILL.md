---
name: generate-text-data
description: Generate varied, non-repetitive synthetic text in bulk (support tickets, reviews, notes, personas, scenarios, fake messages, training pairs) with any LLM route, using the seed-then-write recipe with model rotation, dedupe and diversity checks. Use on "synthetic data", "generate examples", "make training data", "fake records", "it's too repetitive", or when a generated set looks samey.
---

# Generate varied synthetic text

Works with any chat-completions route: OpenRouter or any OpenAI-compatible API, Anthropic, Gemini, or a local
server (Ollama, vLLM, llama.cpp). A batch API is one optional route, not a requirement.

## Why a recipe

An 11-model probe (2026-10-31): the same prompt run 10 times on each model gave near-identical content
(over 80% of outputs shared the same two or three everyday topics). Every vendor converges on the same "typical"
item, and switching model does not fix it. Mixing models cuts wording overlap about 3x (mean trigram Jaccard 0.068
inside one model, 0.023 across models) but not topic overlap. Variety comes from the **seed**.

## 0. Read the overlay first

```bash
"${CLAUDE_PLUGIN_ROOT}/scripts/overlay-paths.sh"          # where the user's data lives
"${CLAUDE_PLUGIN_ROOT}/scripts/overlay-paths.sh" recipe instruction-pairs   # user copy wins over built-in
```

Read `<overlay>/preferences.md` (route, key_env, seed_model, writer_models, budget_cap_usd, pilot_size, diversity
targets, output_dir) and `model-notes.md` if present. If there is no overlay, run the `setup` skill or ask for
route and models. Built-in recipes: `instruction-pairs`, `personas`, `asr-sentences`, `support-tickets`.
Anything not covered: write a recipe in the same format and offer to save it to the overlay.

## Recipe format (`recipes/<name>.md`)

Sections: `## Axes` (a JSON block of name to list of values), `## Seed prompt` (placeholders `{k}`, `{n}`, axis
names), `## Item prompt` (placeholders for axes and `{seed}`, asks for JSON or plain text), `## Output fields`.

## Procedure

1. **Axes in code.** List what should vary (who, setting, length, tone, mess level, domain). Draw combinations
   with a seeded RNG, never ask a model for diversity you can enumerate:
   `uv run "${CLAUDE_PLUGIN_ROOT}/scripts/axes.py" axes.json --n 40 --seed 1 > combos.jsonl`
2. **Seeds from a model, in chunks.** For open-ended variety (situations, personas), ask for 20 to 25 per call.
   Each call gets one axis combination plus "set k of n, avoid the obvious ones". One long list repeats itself.
   Use the cheap `seed_model`. Dedupe the seed list too.
3. **One item per seed.** The writing prompt holds the seed and the axis values. Never "write 50 examples".
   Build `jobs.jsonl` (`{"id","prompt","system"?}`) with the recipe's item prompt filled per seed.
4. **Rotate 2 or 3 writer families** by item index (`i % 3`), from `writer_models`. Record the writer model on
   every row (the runner does). Don't use one model for both seeds and every item if the set will train a model:
   its habits become the dataset's habits.
5. **Run the pilot first** (`pilot_size`, default 30), read 10 items, run the diversity check
   (`check-diversity`), only then scale. Estimate cost before a bulk run and respect `budget_cap_usd`.
6. **Dedupe** (`check-diversity`: content-word Jaccard of 0.5 or more to an earlier item is dropped) and report how
   many were dropped. Parse and validate JSON outputs; drop and count failures.

## Running it

```bash
uv run "${CLAUDE_PLUGIN_ROOT}/scripts/llm_generate.py" jobs.jsonl --out out.jsonl \
  --route openrouter --models "<writer1>,<writer2>,<writer3>" --workers 8 --limit 30   # pilot
uv run "${CLAUDE_PLUGIN_ROOT}/scripts/llm_generate.py" jobs.jsonl --out out.jsonl --dry-run   # inspect request only
```

Routes: `openrouter`, `openai`, `gemini`, `anthropic`, `ollama`, `openai-compat` (`--base-url`). The key is read from
the environment variable named by `--key-env` (or the route default); never put a key in a file or a prompt. The
runner is resumable (finished ids are skipped) and retries on 429/5xx. For a batch API, write the same
`jobs.jsonl` into that API's request format, one batch per model, and join on `id`; seeds and items are two
batches because the second depends on the first. Models that reject a "no reasoning" option: turn reasoning off
only where the route supports it, otherwise raise `--max-tokens`.

## Don't

- Don't sample many items from one unseeded prompt: some models collapse hard (mean trigram Jaccard above 0.15).
- Don't turn temperature up to get variety: it adds noise, not new topics. Change the seed.
- Don't treat a model's measured diversity as permanent: re-probe when models change. The user's own measurements
  go in `<overlay>/model-notes.md`.
- Don't put real personal data in prompts. To convert real records, use `real-to-synth-llm`.

## Output

JSONL of items plus axes values, seed, writer model, id, in `output_dir`; a short report: counts, dropped
(failed, duplicate), diversity numbers, cost. Publish only if `publish_to` is set or the user asks.
