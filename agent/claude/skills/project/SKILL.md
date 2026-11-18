---
name: project
description: Start or resume a project workstream on a branch — create or read PROJECT.md (goal, acceptance criteria, verifiers, decisions, status) so any agent session can pick up the work. Use when starting a new project or epic, when a session opens on a project branch, or when asked for project status or to "pick up where we left off".
---

# Project workstream

Each project lives on its own branch, usually in its own Ona environment. A file named
`PROJECT.md` at the repo root holds the project's **durable memory**. Sessions do not remember
anything between runs, so this file is how the next session knows what is going on.

Keep `PROJECT.md` out of commits that go to review. Add it to `.git/info/exclude` (local-only),
unless I say the team should see it.

## When you start a new project

1. Check the `[repo-sync]` lines: `main` should be current and `just post-pull` running or done.
   Create the branch from the fresh `main`: `git switch -c harman/<ticket>-<short-name> origin/main`.
   Then copy `~/.agent-setup/templates/PROJECT.md` to the repo root.
2. Interview me briefly to fill in: Goal, Links, Acceptance criteria, Verifiers, Constraints.
   Give a proposal for each one, so that "go with that" is a complete answer.
3. Propose a plan as a short ordered list of PR-sized steps. Each step names the verifier that
   proves it. Write the plan into the file when I approve it.
4. Add `PROJECT.md` to `.git/info/exclude`.

## When you resume (every new session on this branch)

1. Read the `[repo-sync]` lines at the start of the session. A hook has already fetched,
   updated `main`, and brought `main` into this branch (or told you why it could not).
   If it reports conflicts or a skipped sync, tell me before you do anything else.
   If it started `just post-pull`, wait for `EXIT=0` in its log before builds or tests.
2. Read `PROJECT.md`, then `git log --oneline -15` and `git status`.
3. Give me a 3-line status: what is done, what is next, and what is blocked.
4. Continue from "Next".

## While you work

- Update **Status** when you finish a step. Move it to Done, with the PR link and the verifiers run.
- Add each decision we make to **Decisions**, with a date and a one-line reason.
- Add anything you had to ask me to **Open questions**, until I answer it.
- Add surprises about the codebase (commands, gotchas) to **Notes for future sessions**.

## Rules

- `PROJECT.md` is short. Prune it when it passes about 150 lines.
- Never record secrets, tokens, or customer data in it.
