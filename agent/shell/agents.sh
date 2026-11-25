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
#   ws skills integ-okta  → page listing every skill, plugin and subagent on that box
#   ws plan integ-okta FDE-842 → open that plan (from the plan-ticket skill) as a page
#   ws map                → open the Vanta system map (maps/vanta-system-map.html in this repo)
# Before the Claude app connects, get the box ready:
#  1. Wait for its startup. On a new box, ~/.claude is swapped over to the shared EFS home about a
#     minute after boot; if the app connects inside that minute it fails with "Couldn't start
#     Claude Code ... ~/.claude/remote". So wait (up to ~3 min) for the EFS link.
#  2. Make sure the per-box Claude app folder exists on local disk.
#  3. Pull your latest dotfiles and re-link rules and skills, so the session starts with them.
#     A failed pull (no network, local changes) never blocks opening the box.
_ws_prep() {
  echo "[ws] getting $1 ready (shared home, app folder, latest rules and skills)…"
  local out
  out=$(oo c "$1" -- 'for i in $(seq 1 60); do [ -L ~/.claude ] && break; sleep 3; done
mkdir -p ~/.claude-remote-local && chmod 700 ~/.claude-remote-local
if [ -L ~/.claude ]; then echo READY; else echo NO_EFS_LINK; fi
if [ -f "$HOME/.agent-setup/install.sh" ]; then
  if GIT_TERMINAL_PROMPT=0 timeout 40 git -C "$HOME/.agent-setup" pull --ff-only -q >/dev/null 2>&1; then echo SETUP_PULLED; else echo SETUP_PULL_FAILED; fi
  if timeout 150 bash "$HOME/.agent-setup/install.sh" > /tmp/agent-setup.log 2>&1; then echo SETUP_LINKED; else echo SETUP_LINK_FAILED; fi
  grep -o "plugin on: .*\|plugin .* is not in .*\|could not enable plugin .*" /tmp/agent-setup.log | sed "s/^/PLUGINLINE /"
else
  echo SETUP_MISSING
fi' 2>/dev/null)
  if printf '%s\n' "$out" | grep -qx READY; then
    echo "[ws] $1 is ready."
  else
    echo "[ws] $1 did not finish setup in time. If Claude fails to start, wait a minute and run: ws open $1"
  fi
  case "$out" in
    *SETUP_PULLED*SETUP_LINKED*) echo "[ws] rules and skills are up to date." ;;
    *SETUP_PULL_FAILED*) echo "[ws] could not pull your dotfiles on $1 (using the copy already there). Check: oo c $1 -- 'git -C ~/.agent-setup status -sb'" ;;
    *SETUP_LINK_FAILED*) echo "[ws] pulled your dotfiles but install.sh failed on $1. Check: oo c $1 -- 'bash ~/.agent-setup/install.sh'" ;;
    *SETUP_MISSING*) echo "[ws] your dotfiles are not on $1 yet (Ona may still be running them)." ;;
  esac
  printf '%s\n' "$out" | sed -n 's/^PLUGINLINE /[ws] /p'
}

# ws skills <box>: every skill, plugin and subagent on that box, as a page on your Mac.
_ws_skills() {
  [ -n "${1:-}" ] || { echo "usage: ws skills <box>"; return 1; }
  local dir="$HOME/.agent-pages"; mkdir -p "$dir"
  local out="$dir/skills-$1.html"
  if oo c "$1" -- 'python3 ~/.agent-setup/bin/skills-catalog.py' > "$out" 2>/dev/null && [ -s "$out" ]; then
    echo "[ws] skills on $1 → $out"; open "$out" 2>/dev/null || true
  else
    rm -f "$out"; echo "[ws] could not list skills on $1. Is it running? Try: ws open $1"; return 1
  fi
}

# ws plan <box> [KEY]: open a plan written by the plan-ticket skill (newest if no KEY).
# Plans live in ~/.claude/fde-plans, shared by every box, so any running box works.
#   ws plan <box> --list   → list plans
_ws_plan() {
  [ -n "${1:-}" ] || { echo "usage: ws plan <box> [KEY|--list]"; return 1; }
  local box="$1" key="${2:-}"
  if [ "$key" = "--list" ]; then oo c "$box" -- 'python3 ~/.agent-setup/bin/plan-html.py --list'; return; fi
  local dir="$HOME/.agent-pages"; mkdir -p "$dir"
  local out="$dir/plan-${key:-latest}.html"
  if oo c "$box" -- "python3 ~/.agent-setup/bin/plan-html.py $key" > "$out" 2>/dev/null && [ -s "$out" ]; then
    echo "[ws] plan → $out"; open "$out" 2>/dev/null || true
  else
    rm -f "$out"; echo "[ws] no plan found on $box${key:+ for $key}. List them: ws plan $box --list"; return 1
  fi
}

# End of day: stop every box and confirm they really stopped.
# The Claude desktop app reconnects to its sessions when it is open, and connecting to a
# stopped box starts it again, so the app must be quit first. `ws down --force` skips that check.
_ws_down() {
  if [ "${1:-}" != "--force" ] && pgrep -x Claude >/dev/null 2>&1; then
    echo "[ws] The Claude desktop app is open. Quit it first (Cmd+Q) so it can't wake the boxes,"
    echo "     then run: ws down     (or: ws down --force to stop anyway)"
    return 1
  fi
  oo stop --all || return 1
  echo "[ws] waiting for the boxes to stop…"
  local i
  for i in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16; do
    sleep 15
    if ! oo 2>/dev/null | grep -qE 'running|starting|stopping'; then
      echo "[ws] all boxes are stopped. Good night."
      return 0
    fi
  done
  echo "[ws] some boxes are still not stopped after 4 minutes:"
  oo
  return 1
}

ws() {
  case "${1:-}" in
    new)  shift; oo new -n "$1" -t none && _ws_prep "$1" && oo claude "$1" --label "$1" ;;
    open) shift; _ws_prep "$1"; oo claude "$1" --label "$1" ;;
    stop) shift; oo stop "$@" ;;
    down) shift; _ws_down "$@" ;;
    skills) shift; _ws_skills "$@" ;;
    plan) shift; _ws_plan "$@" ;;
    map) open "$HOME/.agent-setup/maps/vanta-system-map.html" 2>/dev/null || echo "[ws] map not found; run agent-setup-update" ;;
    "")   oo ;;
    *)    oo "$@" ;;
  esac
}

# Pull the latest version of this setup repo (on your Mac or an Ona box).
agent-setup-update() { git -C "$HOME/.agent-setup" pull --ff-only && "$HOME/.agent-setup/install.sh"; }
