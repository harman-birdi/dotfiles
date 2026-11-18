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
# Before the Claude app connects, make sure the box has its per-box app folder on local disk.
# ~/.claude/remote links there (off the shared EFS home); if it's missing, the app fails with
# "Couldn't start Claude Code". Doing it from the Mac works no matter when dotfiles ran.
_ws_prep() {
  oo c "$1" -- 'mkdir -p ~/.claude-remote-local && chmod 700 ~/.claude-remote-local' >/dev/null 2>&1 \
    || echo "[ws] could not prepare $1; if Claude fails to start, run: oo c $1 -- mkdir -p ~/.claude-remote-local"
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
