#!/usr/bin/env bash
# Ona EFS hook. It runs after your EFS network directory mounts (see go/efs).
#
# Purpose: keep Claude/gh auth and Claude conversation history across ALL your Ona boxes,
# so you do not have to run `claude auth login` on every new environment.
#
# Prerequisite: add EFS_MOUNT_POINT (for example /efs-home) to your personal Ona secrets:
#   https://app.gitpod.io/settings/members?user-settings=secrets
#
# VERIFY: go/efs says that obsidian ships a default hook that already shares the claude,
# codex, and gh auth folders. This script runs that default hook first, then re-links this
# repo's CLAUDE.md and skills. If go/efs changes, update this file to match.
set -uo pipefail

log() { printf '[agent-setup:efs] %s\n' "$*"; }

DEFAULT_HOOK=""
for candidate in \
  /workspaces/obsidian/.devcontainer/bin/default-post-install-efs-hook \
  "$HOME/obsidian/.devcontainer/bin/default-post-install-efs-hook"; do
  [ -x "$candidate" ] && { DEFAULT_HOOK="$candidate"; break; }
done

if [ -n "$DEFAULT_HOOK" ]; then
  log "running obsidian default EFS hook: $DEFAULT_HOOK"
  "$DEFAULT_HOOK" || log "default hook exited non-zero; continuing"
else
  log "obsidian default EFS hook not found; skipping (check go/efs)"
fi

# Re-link config after ~/.claude may have moved onto EFS.
"$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/install.sh"
