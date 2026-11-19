#!/usr/bin/env bash
# Resolve the synthetic-data overlay (the user's private data folder).
#   overlay-paths.sh            data dir, rule that picked it, files present
#   overlay-paths.sh dir        data dir only
#   overlay-paths.sh recipes    every recipe, overlay first: <name>\t<user|builtin>\t<path>
#   overlay-paths.sh recipe N   path of recipe N (user copy wins), exit 1 if none
# Order: $SYNTHETIC_DATA_DIR > $CLAUDE_USER_DATA/synthetic-data >
#        ~/.claude-user-data/synthetic-data (if ~/.claude-user-data exists) >
#        ${XDG_DATA_HOME:-~/.local/share}/claude-plugins/synthetic-data > ~/.claude-user-data/synthetic-data
set -euo pipefail
NAME=synthetic-data
ROOT="${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
XDG="${XDG_DATA_HOME:-$HOME/.local/share}/claude-plugins"
if [[ -n "${SYNTHETIC_DATA_DIR:-}" ]]; then DIR="$SYNTHETIC_DATA_DIR"; RULE=SYNTHETIC_DATA_DIR
elif [[ -n "${CLAUDE_USER_DATA:-}" ]]; then DIR="$CLAUDE_USER_DATA/$NAME"; RULE=CLAUDE_USER_DATA
elif [[ -d "$HOME/.claude-user-data" ]]; then DIR="$HOME/.claude-user-data/$NAME"; RULE="existing ~/.claude-user-data"
elif [[ -d "$XDG" ]]; then DIR="$XDG/$NAME"; RULE="existing $XDG"
else DIR="$HOME/.claude-user-data/$NAME"; RULE=default; fi
list() {
  declare -A seen=()
  for f in "$DIR"/recipes/*.md; do [[ -e $f ]] || continue; b=$(basename "$f"); seen[$b]=1; printf '%s\tuser\t%s\n' "$b" "$f"; done
  for f in "$ROOT"/recipes/*.md; do [[ -e $f ]] || continue; b=$(basename "$f"); [[ -n ${seen[$b]:-} ]] && continue; printf '%s\tbuiltin\t%s\n' "$b" "$f"; done
}
case "${1:-}" in
  dir) echo "$DIR" ;;
  recipes) list ;;
  recipe) n="${2:?recipe name}"; n="${n%.md}.md"
    if [[ -e $DIR/recipes/$n ]]; then echo "$DIR/recipes/$n"
    elif [[ -e $ROOT/recipes/$n ]]; then echo "$ROOT/recipes/$n"
    else echo "no recipe named '$n'" >&2; exit 1; fi ;;
  "") echo "data_dir: $DIR"; echo "rule: $RULE"; echo "plugin_root: $ROOT"
      echo "preferences: $([[ -f $DIR/preferences.md ]] && echo present || echo missing)"
      [[ -d $DIR ]] && ls -1 "$DIR" | sed 's/^/  /' || true ;;
  *) echo "usage: $0 [dir|recipes|recipe NAME]" >&2; exit 2 ;;
esac
