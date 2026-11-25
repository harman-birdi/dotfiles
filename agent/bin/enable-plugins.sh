#!/usr/bin/env bash
# Enable the plugins listed in plugins.txt from the obsidian repo's local marketplace.
# Ona only, safe to re-run. Prints one PLUGIN_<status> line per plugin for `ws` to report.
#
# Why: `just enable-claude-plugin fde` writes the PROJECT settings file by default, which lives
# in one box's checkout, so new boxes never had it. User scope lives in ~/.claude (shared EFS
# home), but the marketplace must also be registered, and the repo can be stale on a new box.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LIST="${PLUGINS_LIST:-$HERE/plugins.txt}"
t() { if command -v timeout >/dev/null 2>&1; then timeout "$@"; else shift; "$@"; fi; }

command -v claude >/dev/null 2>&1 || { echo "PLUGIN_SKIPPED no-claude-cli"; exit 0; }
REPO=""
for d in /workspaces/*/; do
  [ -f "$d/.claude-plugin/marketplace.json" ] && { REPO="${d%/}"; break; }
done
[ -n "$REPO" ] || { echo "PLUGIN_SKIPPED no-marketplace-repo"; exit 0; }

MKT="$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["name"])' "$REPO/.claude-plugin/marketplace.json" 2>/dev/null || echo obsidian-local)"
AVAILABLE="$(python3 -c 'import json,sys;print("\n".join(p["name"] for p in json.load(open(sys.argv[1]))["plugins"]))' "$REPO/.claude-plugin/marketplace.json" 2>/dev/null)"

# Register the repo as a marketplace once (user scope). Re-adding an existing one is harmless.
if ! t 30 claude plugin marketplace list 2>/dev/null | grep -q "$MKT"; then
  t 60 claude plugin marketplace add "$REPO" >/dev/null 2>&1 || true
fi
t 60 claude plugin marketplace update "$MKT" >/dev/null 2>&1 || true

grep -vE '^\s*(#|$)' "$LIST" 2>/dev/null | while read -r name; do
  if ! printf '%s\n' "$AVAILABLE" | grep -qx "$name"; then
    echo "PLUGIN_MISSING $name"; continue
  fi
  if t 90 claude plugin install "$name@$MKT" --scope user >/dev/null 2>&1; then
    echo "PLUGIN_OK $name"
  elif (cd "$REPO" && t 90 just enable-claude-plugin "$name" --user >/dev/null 2>&1); then
    echo "PLUGIN_OK $name"
  else
    echo "PLUGIN_FAILED $name"
  fi
done
