---
name: tune-agent
description: Fix the cause when an agent session makes a mistake, misses context, or works in a way I don't like — decide whether the fix belongs in CLAUDE.md, a skill, a hook, a test, or a tool, and propose the edit to my agent-setup repo. Use when I say "remember this", "don't do that again", "update the skill", "tune", "retro", or when the same correction happens twice.
---

# Tune the agent ("fix the input, not the output")

My agent configuration lives in the git repo at `~/.agent-setup` (symlinked into `~/.claude`).
Changes there apply to every future session, on every machine.

## Procedure

1. **Name the miss** in one sentence. What happened, and what should have happened?
2. **Ask the two questions** from the Vanta AI-first doc:
   - What input would have changed the outcome?
   - What verification would prevent this next time?
3. **Pick the layer.** Use the first row that fits:

   | If the fix is… | Put it in… |
   |---|---|
   | Must *always* hold, and can be checked by a machine | A **hook** or CI check (a gate, not advice) |
   | A behavior check on code | A **test** or verifier in the repo |
   | Steps for one kind of task | That task's **skill** (`claude/skills/<name>/SKILL.md`) |
   | Knowledge specific to one repo | The repo's `AGENTS.md`, or the skill's "Repo notes" |
   | A standing preference across all my work | `claude/CLAUDE.md` |
   | The agent could not see something | A **tool**: an MCP server, a CLI, or a secret in Ona |
   | Only for this project | `PROJECT.md` → "Notes for future sessions" |

4. **Propose the smallest edit.** Show it as a diff. Keep the wording short and direct. A
   good rule explains *why*. Prefer one precise sentence over a paragraph.
5. **After I approve:** apply the edit in `~/.agent-setup`, then add one line to `LEARNINGS.md`
   (`YYYY-MM-DD · <miss> → <fix> · <file>`). Commit with a clear message. Ask before you push.
6. **Consider sharing.** If the fix would help other FDEs or engineers, say so. Then it can go
   to the team `fde` plugin or `/marketplace-vanta`.

## Rules

- Do not put the same rule in two layers.
- If `CLAUDE.md` passes about 120 lines, propose moving task-specific rules into skills.
- Never weaken a verifier as a "fix".
