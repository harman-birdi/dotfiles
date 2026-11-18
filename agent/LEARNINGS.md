# Learnings log

One line per tuning change, appended by the `tune-agent` skill (or by hand).
Format: `YYYY-MM-DD · <what went wrong> → <what changed> · <file>`

Review this monthly. Promote anything that would help the team into the `fde` plugin or `/marketplace-vanta`.

---

- 2026-11-16 · initial setup → CLAUDE.md, feasibility / integrations / project / tune-agent skills · (all)
- 2026-11-18 · new boxes ran a stale main without post-pull → SessionStart repo-sync hook · hooks/sync-repo.sh, install.sh
- 2026-11-18 · Claude app failed on boxes: ~/.claude/remote shared over EFS → link it to per-box local disk · install.sh step 6
- 2026-11-18 · first open after `ws new` failed: app connected before EFS swap → ws waits for setup first · shell/agents.sh
