# agent-setup

My personal Claude Code configuration for agent-first FDE work at Vanta. One git repo holds the
rules, skills, and shell helpers. Every Claude session loads them: on my Mac, and on every Ona box
through Ona dotfiles.

```
claude/CLAUDE.md                 standing rules for every session (→ ~/.claude/CLAUDE.md)
claude/skills/feasibility/       draft an FDE Feasibility Evaluation in the template format
claude/skills/integrations/      connector work in obsidian: platform, precedent, verifiers
claude/skills/project/           PROJECT.md = durable memory for a branch/workstream
claude/skills/tune-agent/        "fix the input, not the output": route a fix to the right layer
templates/PROJECT.md             template the project skill copies
shell/agents.sh                  oo defaults + `ws` helper
install.sh                       links everything into ~/.claude (safe to re-run)
post-start-install.sh            Ona EFS hook: keeps auth across boxes, then re-runs install.sh
LEARNINGS.md                     one line per tuning change
```

## The mental model

| Layer | What it is | Here |
|---|---|---|
| **Specialists** | Reusable config that any session can load | the skills in `claude/skills/` |
| **Workstreams** | One Ona env + one Claude session per active branch | `ws new <name>` |
| **Memory** | Sessions remember nothing, so state lives in files | `PROJECT.md`, skill "Repo notes" |
| **Tuning** | Fix the cause in config, not the output | `tune-agent` skill + `LEARNINGS.md` |

---

## One-time setup

### 1. Put this repo on GitHub
Create a **private** repo (for example `harman-birdi/agent-setup`) and push these files to it.

### 2. Ona: dotfiles and secrets
1. Ona → user settings → **Dotfiles** → paste the repo URL. New environments run `install.sh`.
2. Run **go/ona-env-wizard** if you have not already. It sets up your personal Ona secrets.
3. Add these to your **personal Ona secrets** (https://app.gitpod.io/settings/members?user-settings=secrets):
   - `EFS_MOUNT_POINT` = `/efs-home`. This keeps Claude/gh auth across boxes; see go/efs.
   - `JIRA_API_TOKEN` and `JIRA_USERNAME`. The `fde:intake` skill needs them for `acli`.
4. Restart, or create, an environment to pick up the changes.

### 3. Your Mac
```sh
git clone git@github.com:<you>/agent-setup.git ~/code/agent-setup
~/code/agent-setup/install.sh
```
Check that `OO_BRANCH_PREFIX` in `shell/agents.sh` matches your branch names.

### 4. First Ona box (once; EFS keeps it after that)
```sh
ws new setup-check          # creates an env and opens Claude desktop on it
```
In that session, run once:
1. `claude auth login` (if prompted)
2. Say "do the Glean MCP auth" and follow the link.
3. `npx gsync auth login` (run it from an editor terminal)
4. `just enable-claude-plugin fde` (gives you `/fde:intake`)
5. `acli jira auth status`

Then open a **second** env and confirm that you are still logged in. If you are, EFS works.

---

## Daily workflows

### Feasibility (research-heavy; Cowork or Claude Code)
1. A request arrives in `#fde-intake`.
2. In a Claude Code session on an obsidian box, run `/fde:intake <slack url>`. It creates the Jira
   ticket and a context brief.
3. Say "draft the feasibility from the brief". The `feasibility` skill writes the template sections
   and leaves `<TODO!>` for the estimate, the urgency, and the verdict.
4. You fill in the `<TODO!>`s, paste the draft into a copy of the template, and send it for review.

### Integration work
```sh
ws new integ-<vendor>       # fresh env + Claude session
```
Say "use the integrations skill: <task>". The agent classifies the task, finds the platform and a
precedent connector, and proposes acceptance criteria. After you agree on them, it implements to
green and attaches the evidence.

### A project
```sh
ws new <project>            # first time
ws open <project>           # every time after
```
First session: "start a project". The skill interviews you and writes `PROJECT.md`.
Later sessions: "resume". The agent reads `PROJECT.md` and gives a 3-line status.

### Seeing everything
```sh
ws                          # all envs: running/stopped, PR state, unpushed work
ws stop --all               # end of day
```

### When an agent gets something wrong
Say **"tune: <what went wrong>"**. The `tune-agent` skill picks the layer (rule, skill, hook, test,
tool), proposes a diff to this repo, and logs it in `LEARNINGS.md`. Then push, and run
`agent-setup-update` on other boxes, or just create new ones.

---

## Pace (from the Automation AI-first doc)
Get **one** session through the full loop (spec → PR → review → rollout) before you run several
in parallel. Go back to one stream if reviews pile up. Next step after that: an orchestrator that
sends briefs out to N envs. See Jeremiah Pratt's `/dispatch` skill (access-mgmt-knowledge-base)
and Sam Storino's Stratus CLI, which also passes Claude auth to each box.

## Sources
- Automation: Becoming AI-First (Engineer Edition): https://docs.google.com/document/d/1pML0Ug7MN4YG3QpM5ZWuAHjiWffGlc2AHIkIcX7SLis
- FDE Feasibility Evaluation Template: https://docs.google.com/document/d/13iBgwxYloebqd6eqGSpMhwkwDxRFvgNFD9QUctdE4SA
- How to Use the FDE Intake Claude Code Skill: https://app.getguru.com/card/iq9rEyoT
- EFS network directory (go/efs): https://docs.google.com/document/d/1sypPRmiGrbh4g2UmbkNNLo8ELKG7mSK_Avs7vyx2KPk
- oo: https://github.com/adamtrain/oo
