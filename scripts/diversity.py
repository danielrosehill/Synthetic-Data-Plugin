# /// script
# requires-python = ">=3.10"
# ///
"""Diversity metrics and near-duplicate removal for generated text (stdlib only).

Usage:
  uv run diversity.py report items.jsonl --field text [--group-field model]
  uv run diversity.py dedupe items.jsonl --field text --out clean.jsonl [--threshold 0.5]

report: mean pairwise trigram Jaccard (target < 0.07 for free text; sampled to 400
        items), top-3 content-word share (target < 0.4), optionally per group.
dedupe: drops items whose content-word Jaccard to an earlier kept item >= threshold.
"""
import argparse, collections, itertools, json, random, re, sys

STOP = set("a an the and or but of to in on at for with from by is are was were be been it its this that these those i you he she we they my your his her our their as not no so if then than too very can will just do does did have has had me him us them what which who how when where why there here about into over out up down also".split())

def words(t): return re.findall(r"\w+", t.lower())
def content(t): return {w for w in words(t) if w not in STOP and len(w) > 2}
def trigrams(t):
    w = words(t); return {tuple(w[i:i+3]) for i in range(len(w) - 2)}
def jac(a, b): return len(a & b) / len(a | b) if a | b else 0.0

def load(path, field):
    rows = [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]
    for r in rows: r["_t"] = str(r.get(field, ""))
    return rows

def report_rows(rows):
    sample = rows if len(rows) <= 400 else random.Random(0).sample(rows, 400)
    tg = [trigrams(r["_t"]) for r in sample]
    pairs = list(itertools.combinations(range(len(tg)), 2))
    mj = sum(jac(tg[i], tg[j]) for i, j in pairs) / len(pairs) if pairs else 0.0
    cnt = collections.Counter(w for r in rows for w in content(r["_t"]))
    total = sum(cnt.values()) or 1
    top = cnt.most_common(3)
    return {"n": len(rows), "mean_trigram_jaccard": round(mj, 4),
            "top3_content_word_share": round(sum(c for _, c in top) / total, 4),
            "top3_words": [w for w, _ in top]}

ap = argparse.ArgumentParser()
ap.add_argument("cmd", choices=["report", "dedupe"]); ap.add_argument("path")
ap.add_argument("--field", default="text"); ap.add_argument("--group-field")
ap.add_argument("--out"); ap.add_argument("--threshold", type=float, default=0.5)
a = ap.parse_args()
rows = load(a.path, a.field)
if a.cmd == "report":
    out = {"all": report_rows(rows)}
    if a.group_field:
        g = collections.defaultdict(list)
        for r in rows: g[str(r.get(a.group_field))].append(r)
        out["groups"] = {k: report_rows(v) for k, v in g.items() if len(v) > 1}
    print(json.dumps(out, indent=2))
else:
    kept, sets = [], []
    for r in rows:
        s = content(r["_t"])
        if any(jac(s, k) >= a.threshold for k in sets): continue
        kept.append(r); sets.append(s)
    with open(a.out, "w", encoding="utf-8") as f:
        for r in kept:
            r.pop("_t", None); f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(json.dumps({"input": len(rows), "kept": len(kept), "dropped": len(rows) - len(kept)}))
