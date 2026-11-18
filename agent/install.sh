#!/usr/bin/env bash
# Links this repo's Claude config into ~/.claude. Safe to re-run.
#
# - On Ona: set this repo as your dotfiles repo (Ona user settings → Dotfiles).
#   Ona clones it and runs install.sh on every new environment.
# - On your Mac: clone it anywhere and run ./install.sh once.
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
STABLE="$HOME/.agent-setup"          # stable path that skills and docs refer to
CLAUDE_DIR="$HOME/.claude"

log() { printf '[agent-setup] %s\n' "$*"; }

# link SRC DEST: symlink, backing up a real file/dir that is in the way.
link() {
  local src="$1" dest="$2"
  if [ -L "$dest" ]; then
    [ "$(readlink "$dest")" = "$src" ] && return 0
    rm "$dest"
  elif [ -e "$dest" ]; then
    local backup="$dest.bak.$(date +%Y%m%d%H%M%S)"
    log "backing up existing $dest → $backup"
    mv "$dest" "$backup"
  fi
  ln -s "$src" "$dest"
  log "linked $dest → $src"
}

# 1. Stable path to this repo
if [ "$REPO" != "$STABLE" ]; then
  link "$REPO" "$STABLE"
fi

# 2. User-level CLAUDE.md and skills
mkdir -p "$CLAUDE_DIR/skills"
link "$STABLE/claude/CLAUDE.md" "$CLAUDE_DIR/CLAUDE.md"
for skill in "$STABLE"/claude/skills/*/; do
  name="$(basename "$skill")"
  link "$STABLE/claude/skills/$name" "$CLAUDE_DIR/skills/$name"
done

# 3. Shell helpers (oo defaults, aliases)
for rc in "$HOME/.bashrc" "$HOME/.zshrc"; do
  [ -f "$rc" ] || continue
  line="[ -f \"$STABLE/shell/agents.sh\" ] && . \"$STABLE/shell/agents.sh\""
  grep -qF ".agent-setup/shell/agents.sh" "$rc" || { printf '\n%s\n' "$line" >> "$rc"; log "added shell helpers to $rc"; }
done

# 4. Glean MCP for Claude Code (user scope). Auth still happens once in a session:
#    open claude and say "do the Glean MCP auth".
t() { if command -v timeout >/dev/null 2>&1; then timeout 20 "$@"; else "$@"; fi; }  # macOS lacks timeout
if command -v claude >/dev/null 2>&1; then
  if ! t claude mcp get glean_default >/dev/null 2>&1; then
    t claude mcp add glean_default https://vanta-be.glean.com/mcp/default \
      --transport http --scope user >/dev/null 2>&1 \
      && log "added Glean MCP (glean_default)" \
      || log "could not add Glean MCP automatically; see README"
  fi
else
  log "claude CLI not found; skipped Glean MCP setup"
fi

# 5. SessionStart hook: sync the repo with main whenever a Claude session opens (Ona only;
#    the hook exits immediately on the Mac). Merged into settings.json without touching
#    any other settings.
SETTINGS="$CLAUDE_DIR/settings.json"
HOOK_CMD='bash "$HOME/.agent-setup/hooks/sync-repo.sh"'
if command -v python3 >/dev/null 2>&1; then
  python3 - "$SETTINGS" "$HOOK_CMD" <<'PY' || log "could not update $SETTINGS; add the hook by hand (see README)"
import json, os, sys
path, cmd = sys.argv[1], sys.argv[2]
data = {}
if os.path.exists(path):
    txt = open(path).read().strip()
    data = json.loads(txt) if txt else {}
groups = data.setdefault("hooks", {}).setdefault("SessionStart", [])
if not any(h.get("command") == cmd for g in groups for h in g.get("hooks", [])):
    groups.append({"matcher": "startup|resume",
                   "hooks": [{"type": "command", "command": cmd, "timeout": 120}]})
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(data, f, indent=2); f.write("\n")
    os.replace(tmp, path)
    print("[agent-setup] added SessionStart repo-sync hook to " + path)
PY
else
  log "python3 not found; skipped SessionStart hook setup"
fi

log "done. Start a new Claude session to pick up changes."
