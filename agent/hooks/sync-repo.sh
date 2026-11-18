#!/usr/bin/env bash
# Claude Code SessionStart hook: keep the repo current whenever a Claude session opens
# on an Ona box (a new box, or `ws open` on an existing one).
#
# What it does, in order:
#   1. git fetch origin
#   2. Fast-forward your local main to origin/main (never rewrites main).
#   3. On a feature branch with a clean working tree:
#        - pick up commits pushed to this branch from elsewhere (fast-forward only)
#        - never pushed yet  → rebase onto origin/main
#        - already pushed     → merge origin/main in (so no force-push is needed)
#      On conflicts it aborts and leaves the branch exactly as it was.
#   4. If the code changed since the last `just post-pull`, start it in the background.
#
# Everything it prints is shown to the agent at the start of the session.
# Only runs on Ona (IS_ON_ONA=true). Turn it off for a session with AGENT_SYNC_DISABLE=1.
set -uo pipefail

[ -n "${AGENT_SYNC_DISABLE:-}" ] && exit 0
[ "${IS_ON_ONA:-}" = "true" ] || [ -d /workspaces ] || [ -f /etc/profile.d/ona-secrets.sh ] \
  || [ -n "${AGENT_SYNC_FORCE:-}" ] || exit 0
repo="$(git rev-parse --show-toplevel 2>/dev/null)" || exit 0
cd "$repo" || exit 0

say() { printf '[repo-sync] %s\n' "$*"; }
to() { if command -v timeout >/dev/null 2>&1; then timeout "$@"; else shift; "$@"; fi; }

gitdir="$(cd "$(git rev-parse --git-dir)" && pwd)"
main="$(git symbolic-ref --short refs/remotes/origin/HEAD 2>/dev/null | sed 's#^origin/##')"
main="${main:-main}"

if ! to 45 git fetch --quiet --prune origin 2>/dev/null; then
  say "git fetch failed (auth or network). Nothing was updated. Tell the user before relying on main being current."
  exit 0
fi

branch="$(git symbolic-ref --short HEAD 2>/dev/null || echo DETACHED)"
dirty=""
[ -n "$(git status --porcelain --untracked-files=no)" ] && dirty=1

# 1. Local main → origin/main (fast-forward only)
if [ "$branch" = "$main" ]; then
  if [ -n "$dirty" ]; then
    say "on $main with uncommitted changes: skipped update."
  elif git merge --ff-only --quiet "origin/$main" 2>/dev/null; then
    say "$main is at origin/$main ($(git rev-parse --short HEAD))."
  else
    say "$main has diverged from origin/$main: NOT updated. Ask the user how to proceed."
  fi
elif git show-ref --verify --quiet "refs/heads/$main"; then
  if git fetch --quiet . "origin/$main:$main" 2>/dev/null; then
    say "local $main updated to origin/$main ($(git rev-parse --short "$main"))."
  else
    say "local $main could not fast-forward to origin/$main (diverged): left as is."
  fi
fi

# 2. Feature branch
if [ "$branch" != "$main" ] && [ "$branch" != "DETACHED" ]; then
  upstream="$(git rev-parse --abbrev-ref --symbolic-full-name '@{u}' 2>/dev/null || true)"
  if [ -n "$dirty" ]; then
    say "$branch has uncommitted changes: did not bring in origin/$main. Commit or stash, then ask to sync."
  else
    if [ -n "$upstream" ] && [ "$(git rev-parse HEAD)" != "$(git rev-parse "$upstream")" ] \
       && git merge-base --is-ancestor HEAD "$upstream"; then
      git merge --ff-only --quiet "$upstream" && say "$branch fast-forwarded to $upstream (commits pushed from elsewhere)."
    fi
    behind="$(git rev-list --count "HEAD..origin/$main")"
    if [ "$behind" -eq 0 ]; then
      say "$branch already contains everything on origin/$main."
    elif [ -z "$upstream" ]; then
      if git rebase --quiet "origin/$main" >/dev/null 2>&1; then
        say "$branch (not pushed yet) rebased onto origin/$main: $behind new commits from $main."
      else
        git rebase --abort >/dev/null 2>&1
        say "rebasing $branch onto origin/$main hit conflicts: aborted, branch unchanged. Resolve together with the user."
      fi
    else
      if git merge --no-edit --quiet "origin/$main" >/dev/null 2>&1; then
        say "merged origin/$main into $branch: $behind new commits. This merge is NOT pushed yet."
      else
        git merge --abort >/dev/null 2>&1
        say "merging origin/$main into $branch hit conflicts: aborted, branch unchanged. Resolve together with the user."
      fi
    fi
  fi
fi

# 3. Dependencies: rerun `just post-pull` in the background when the code changed
if command -v just >/dev/null 2>&1 && just --summary 2>/dev/null | tr ' ' '\n' | grep -qx post-pull; then
  head="$(git rev-parse HEAD)"
  marker="$gitdir/agent-post-pull-sha"
  log="$gitdir/agent-post-pull.log"
  if [ "$(cat "$marker" 2>/dev/null)" = "$head" ]; then
    say "dependencies already set up for this commit."
  elif pgrep -f "just post-pull" >/dev/null 2>&1; then
    say "'just post-pull' is already running. Log: $log"
  else
    ( nohup bash -c "just post-pull; rc=\$?; [ \$rc -eq 0 ] && echo $head > '$marker'; echo EXIT=\$rc" \
        >"$log" 2>&1 </dev/null & )
    say "code changed since the last setup: started 'just post-pull' in the background. Log: $log"
    say "Before builds or tests, wait until the log ends with EXIT=0 (check with: tail -1 $log)."
  fi
fi

exit 0
