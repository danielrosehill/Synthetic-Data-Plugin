# CLAUDE.md (for agents working on this repo)

Public plugin `synthetic-data`, repo `danielrosehill/Synthetic-Data-Plugin`. Release tier: small (`v1.0` style tags).

- Public text only: no personal names, addresses, hostnames, private infra, or a specific user's model picks.
  Say "the user". User-specific preferences belong in the overlay (see README), never in the code or skills.
- Overlay resolution: `$SYNTHETIC_DATA_DIR`, `$CLAUDE_USER_DATA/synthetic-data`, `~/.claude-user-data/synthetic-data`,
  XDG fallback. `scripts/overlay-paths.sh` is the single implementation. Skills read `<overlay>/preferences.md` first.
- Python: `uv` only (inline `# /// script` deps or `uv run --with`). Never pip, venv, or requirements.txt.
- Vendor-agnostic: no skill may assume the Claude CLI or one provider. Keys are env var names only.
- Skill names: no "claude" or "anthropic". Each SKILL.md under 500 lines, one-line description with trigger phrases.
- One generation skill (`generate-text-data`) holds the recipe; `instruction-and-eval-data` and
  `speech-recording-scripts` specialise it. Don't add near-duplicates; add a recipe in `recipes/` instead.
- Don't run paid generation beyond a sub-$0.05 smoke test. Use `llm_generate.py --dry-run` to test request shape.
- Bump `version` in `.claude-plugin/plugin.json` on every change; update README History.
- Marketplace manifests live elsewhere; don't edit them from here.
