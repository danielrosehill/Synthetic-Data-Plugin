# /// script
# requires-python = ">=3.10"
# dependencies = ["httpx>=0.27"]
# ///
"""Run many independent prompts against any chat-completions route, resumably.

Input JSONL, one job per line: {"id": "...", "prompt": "...", "system": "...optional", "model": "...optional", ...extra fields copied to output}
Output JSONL: the job fields plus "output", "model", "route", and "error" on failure.

Routes (--route): openai-compat (needs --base-url, --key-env optional), openrouter, openai,
gemini, anthropic, ollama (http://localhost:11434/v1), vllm/llamacpp via openai-compat.
Keys are read from the environment variable named by --key-env (defaults per route);
this script never stores or prints a key.

Model rotation: --models a,b,c assigns models[i % len] by job index unless the job has "model".
Resume: ids already present in --out are skipped. Dry run: --dry-run prints the first
job's request body and exits without any call.

Usage:
  uv run llm_generate.py jobs.jsonl --out out.jsonl --route openrouter --models m1,m2 --workers 8 [--limit 5]
"""
import argparse, concurrent.futures as cf, json, os, sys, threading, time
import httpx

ROUTES = {
    "openrouter": ("https://openrouter.ai/api/v1", "OPENROUTER_API_KEY"),
    "openai": ("https://api.openai.com/v1", "OPENAI_API_KEY"),
    "gemini": ("https://generativelanguage.googleapis.com/v1beta/openai", "GEMINI_API_KEY"),
    "ollama": ("http://localhost:11434/v1", None),
    "openai-compat": (None, None),
    "anthropic": ("https://api.anthropic.com/v1", "ANTHROPIC_API_KEY"),
}

ap = argparse.ArgumentParser()
ap.add_argument("jobs"); ap.add_argument("--out", required=True)
ap.add_argument("--route", default="openrouter", choices=list(ROUTES))
ap.add_argument("--base-url"); ap.add_argument("--key-env")
ap.add_argument("--models", required=True, help="comma-separated; rotated by job index")
ap.add_argument("--workers", type=int, default=4); ap.add_argument("--limit", type=int)
ap.add_argument("--max-tokens", type=int, default=1024); ap.add_argument("--temperature", type=float)
ap.add_argument("--retries", type=int, default=3); ap.add_argument("--dry-run", action="store_true")
a = ap.parse_args()

base, key_env = ROUTES[a.route]
base = a.base_url or base
key_env = a.key_env or key_env
if not base: sys.exit("--base-url required for this route")
key = os.environ.get(key_env, "") if key_env else ""
if key_env and not key and not a.dry_run: sys.exit(f"set ${key_env} (the key's value is never read from files by this script)")
models = a.models.split(",")

def request(job, i):
    model = job.get("model") or models[i % len(models)]
    msgs = ([{"role": "system", "content": job["system"]}] if job.get("system") else []) + [{"role": "user", "content": job["prompt"]}]
    if a.route == "anthropic":
        body = {"model": model, "max_tokens": a.max_tokens, "messages": [m for m in msgs if m["role"] != "system"]}
        if job.get("system"): body["system"] = job["system"]
        if a.temperature is not None: body["temperature"] = a.temperature
        return model, f"{base}/messages", {"x-api-key": key, "anthropic-version": "2023-06-01"}, body
    body = {"model": model, "messages": msgs, "max_tokens": a.max_tokens}
    if a.temperature is not None: body["temperature"] = a.temperature
    return model, f"{base}/chat/completions", ({"Authorization": f"Bearer {key}"} if key else {}), body

def text_of(data):
    if a.route == "anthropic": return "".join(b.get("text", "") for b in data["content"])
    return data["choices"][0]["message"]["content"] or ""

jobs = [json.loads(l) for l in open(a.jobs, encoding="utf-8") if l.strip()]
if a.limit: jobs = jobs[: a.limit]
if a.dry_run:
    m, url, _, body = request(jobs[0], 0)
    print(json.dumps({"url": url, "body": body, "jobs": len(jobs), "models": models}, indent=2)); sys.exit(0)
done = set()
if os.path.exists(a.out):
    done = {json.loads(l).get("id") for l in open(a.out, encoding="utf-8") if l.strip()}
lock = threading.Lock()

def run(ij):
    i, job = ij
    if job.get("id") in done: return
    model, url, headers, body = request(job, i)
    rec = {k: v for k, v in job.items() if k not in ("prompt", "system")}
    rec.update(model=model, route=a.route)
    for attempt in range(a.retries):
        try:
            r = httpx.post(url, headers=headers, json=body, timeout=120)
            if r.status_code in (429, 500, 502, 503, 529): raise RuntimeError(f"http {r.status_code}")
            r.raise_for_status(); rec["output"] = text_of(r.json()); break
        except Exception as e:
            rec["error"] = f"{type(e).__name__}: {e}"[:300]; time.sleep(2 ** attempt)
    else:
        pass
    if "output" in rec: rec.pop("error", None)
    with lock, open(a.out, "a", encoding="utf-8") as f: f.write(json.dumps(rec, ensure_ascii=False) + "\n")

with cf.ThreadPoolExecutor(a.workers) as ex: list(ex.map(run, enumerate(jobs)))
print(f"done: {len(jobs)} jobs -> {a.out}", file=sys.stderr)
