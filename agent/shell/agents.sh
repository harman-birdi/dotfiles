# Shell helpers for running agents on Ona with `oo`. Sourced from ~/.bashrc / ~/.zshrc.
# Edit the values below to match your setup.

# Your git branch prefix, so `oo c login-fix` finds harman/login-fix.  VERIFY this matches your branches.
export OO_BRANCH_PREFIX="${OO_BRANCH_PREFIX:-harman/}"

# Defaults for `oo new` (otherwise oo copies whatever your newest environment used).
# export OO_PROJECT="obsidian"        # from: ona project list
# export OO_CLASS="oregon"            # from: ona environment list-classes

# One Ona environment per workstream, opened as a Claude Code session in the desktop app.
#   ws new integ-okta     → create env named integ-okta and open it in Claude desktop (Code tab)
#   ws open integ-okta    → reopen a Claude session on an existing env (starts it if stopped)
#   ws                    → list environments with status / PR / unpushed work
# Before the Claude app connects, wait for the box to finish its startup.
# On a new box, dotfiles run first and ~1 minute later ~/.claude is swapped over to the shared
# EFS home. If the app connects inside that minute, its files vanish mid-connect and it fails
# with "Couldn't start Claude Code ... ~/.claude/remote". So: wait (up to ~3 min) until ~/.claude
# is the EFS link, then make sure the per-box app folder exists on local disk.
_ws_prep() {
  echo "[ws] waiting for $1 to finish setup (shared home + Claude app folder)…"
  oo c "$1" -- 'for i in $(seq 1 60); do [ -L ~/.claude ] && break; sleep 3; done
mkdir -p ~/.claude-remote-local && chmod 700 ~/.claude-remote-local
if [ -L ~/.claude ]; then echo READY; else echo NO_EFS_LINK; fi' 2>/dev/null | grep -qx READY \
    && echo "[ws] $1 is ready." \
    || echo "[ws] $1 did not finish setup in time. If Claude fails to start, wait a minute and run: ws open $1"
}

ws() {
  case "${1:-}" in
    new)  shift; oo new -n "$1" -t none && _ws_prep "$1" && oo claude "$1" --label "$1" ;;
    open) shift; _ws_prep "$1"; oo claude "$1" --label "$1" ;;
    stop) shift; oo stop "$@" ;;
    "")   oo ;;
    *)    oo "$@" ;;
  esac
}

# Pull the latest version of this setup repo (on your Mac or an Ona box).
agent-setup-update() { git -C "$HOME/.agent-setup" pull --ff-only && "$HOME/.agent-setup/install.sh"; }
