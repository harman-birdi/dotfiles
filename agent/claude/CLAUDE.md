# Harman's user-level agent rules

These rules load into every Claude Code session I start, on my Mac or on any Ona box.
Repo-level `CLAUDE.md` / `AGENTS.md` files add to these. When the two conflict, the repo file wins.

## Who I am and what I work on

- I am a Senior Forward Deployed Engineer (FDE) at Vanta. FDE builds customer-driven extensions
  to the product, usually behind a feature flag, and owns that work for 90 days after release.
- My work falls into three kinds. Each has a skill:
  - **Feasibility evaluations** for customer requests from `#fde-intake` → use the `feasibility` skill.
  - **Integration (connector) work** in the `obsidian` repo → use the `integrations` skill.
  - **Project work** on a branch with a spec → use the `project` skill.
- When an agent session gets something wrong more than once, use the `tune-agent` skill to fix
  the cause instead of patching the output.

## How I want you to work (Vanta's agent-first loop)

1. **Define the hill first.** Before you write code, agree on 3–5 acceptance criteria, a failing
   test, or a reproduction. If none exist, propose them and wait for my OK.
2. **Plan before big changes.** For anything larger than a bounded fix, write a short plan I can
   check against the criteria.
3. **Run the cheapest check that fits**: typecheck, targeted tests, lint, a repro script.
   Iterate until it passes or stops improving, then tell me which one happened.
4. **Never weaken a verifier to get to green.** Do not delete, skip, or loosen tests, lint rules,
   or type checks. If one looks wrong, stop and tell me why.
5. **Attach evidence.** When you finish, say what you ran, what passed, and what you did *not*
   verify. Every PR description includes: verification run, how AI was used, open questions.
6. **Keep each PR to a single intent.** Split unrelated changes.
7. **Ask before you change contracts.** That includes changes to system contracts, public APIs,
   auth/permissions, customer data, migrations, or billing. Flag them and name the owning team.
8. **Repo sync.** A SessionStart hook syncs the repo when a session opens and prints
   `[repo-sync]` lines. Read them first. Report conflicts or a skipped sync to me before
   other work. If `just post-pull` is running, wait for `EXIT=0` in its log before builds
   or tests. Ask before you push a sync merge.

## Tool etiquette

- Check auth before you use a CLI: `gh auth status`, `acli jira auth status`, `ona whoami`.
  If auth is missing inside Ona, tell me. Do not try to work around it.
- **Ona:** reuse a running environment before you create one. Ask before you create, start,
  stop, or delete an environment, or open a port.
- **Jira / Slack / Google Docs:** read freely. Ask before you create, edit, comment, transition,
  or post, unless I asked for that exact action.
- **Git:** work on a branch. Never force-push to `main`. Ask before you push.
- Prefer `--format json` when you parse CLI output.

## Where to find Vanta context

- Glean MCP (`glean_default`) for docs, Slack, Guru, and Drive. Use it before you guess about
  product behavior or ownership.
- Code is the ground truth. When docs and code disagree, cite the code path and flag the gap.
- Cite sources (doc links, file paths with line numbers) for any claim about how Vanta works.

## Style

- **Times:** give every time in Pacific Time (America/Los_Angeles), labelled PT, e.g. "3:15 PM PT". Tools, logs, CI, Jira and Ona usually report UTC: convert before telling me. Add the date when it is not today.
- Be concise. Lead with the answer, then the evidence.
- When you are unsure, say so and say what would resolve it.
