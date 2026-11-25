# Learnings log

One line per tuning change, appended by the `tune-agent` skill (or by hand).
Format: `YYYY-MM-DD · <what went wrong> → <what changed> · <file>`

Review this monthly. Promote anything that would help the team into the `fde` plugin or `/marketplace-vanta`.

---

- 2026-11-16 · initial setup → CLAUDE.md, feasibility / integrations / project / tune-agent skills · (all)
- 2026-11-18 · new boxes ran a stale main without post-pull → SessionStart repo-sync hook · hooks/sync-repo.sh, install.sh
- 2026-11-18 · Claude app failed on boxes: ~/.claude/remote shared over EFS → link it to per-box local disk · install.sh step 6
- 2026-11-18 · first open after `ws new` failed: app connected before EFS swap → ws waits for setup first · shell/agents.sh
- 2026-11-25 fde plugin enabled from plugins.txt at user scope (was project scope per checkout); plan-ticket skill, plan-reviewer subagent, fde output style, ws skills / ws plan.
- 2026-11-25 plan-reviewer caught unverified spec paths in the example plan → plan-ticket now requires opening every cited file or marking it "(from spec, unverified)".
- 2026-11-25 Diagram preference: the interactive layers map (click a ticket, its parts light up) is the default; other diagram types only on request. Plans carry it as a `layersmap` block; `ws plan` draws it.
- 2026-11-25 Diagram preference is now two views of one `layersmap` block: layers map + flow map. Tickets and the diagram must agree: check-plan.py fails a plan (or a feasibility ticket map, --map-only) where they do not. Feasibility skill now maps Option A tickets before drafting.
- 2026-11-25 Saved the Vanta system map in maps/ (`ws map`).
- 2026-11-25 Added gsync: share-to-drive skill (ask first, Drive copy turns the interactive map into tables), gsync plugin in plugins.txt (name unconfirmed).
