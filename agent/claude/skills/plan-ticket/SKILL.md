---
name: plan-ticket
description: Turn a Jira ticket into a short, readable plan with diagrams. Researches the ticket, its epic, linked docs, Slack, Glean and the code, asks Harman 3-5 questions, then writes PLAN.md (problem, customer today, pain point, solution from the customer's side, UI yes/no, interactive Vanta layers map and flow map showing which parts each ticket touches, how it works, PR-sized steps, verifiers) and has a Sonnet reviewer check it. Use when asked to plan, scope, break down or "look into" a ticket or FDE-123 style key.
---

# Plan a ticket

You turn one Jira ticket into a plan Harman can read in two minutes and act on. You research
deeply, ask before you assume, and show the shape of the work in diagrams. You do not write code
in this skill.

Output: `~/.claude/fde-plans/<KEY>.md` (shared by every box through the EFS home). Harman opens it
on his Mac with `ws plan <box> <KEY>`.

## Step 1 · Research (no questions yet)

Do these in parallel where you can. Note every source URL as you go.

1. **The ticket.** Summary, description, acceptance criteria, status, assignee, links, comments.
   Use `acli jira workitem view <KEY> --json` (or the Atlassian MCP if it is connected).
2. **Its neighbours.** The parent epic and its other tickets: which block this one, which it blocks,
   which are done. These feed the dependency diagram.
3. **The docs.** Every linked spec, RFC, PRD or Engagement Request: read the sections the ticket
   names ("Covers: …"). Use Glean `read_document` for Google Docs.
4. **The customer.** Who asked and why: the `#fde-intake` thread, the feasibility doc, Gong or
   Salesforce notes if Glean finds them. You need their words for sections 2–4.
5. **The code.** Find where the change lands. Start from the paths in
   `references/vanta-layers.md`, then Glob/Grep. Find the closest existing example (a similar
   integration, handler, converter) and note its `path:line`. Open every file you cite: a path you
   only saw in a doc is marked `(from spec, unverified)`. Code beats docs when they disagree.
6. **Prior art.** Glean search for the same vendor or feature: someone may have built half of it.

Stop researching when you can fill every template section or name exactly what is unknown.

## Step 2 · Ask (3 to 5 questions, one round)

Ask with the AskUserQuestion tool when it exists, otherwise a numbered list. Each question:
- is about a decision or a fact you could not find, never something the sources answer,
- carries your proposal as the first option ("Go with REST pagination (Recommended)"),
- says in one line why it matters to the plan.

Good topics: scope edges, which option a spike chose, customer priorities, whether UI is wanted,
deadlines, who reviews. Wait for the answers. "Your call" means use your proposal.

## Step 3 · Write the plan

1. Copy `references/plan-template.md` into `~/.claude/fde-plans/<KEY>.md` and fill every section.
   Keep the headings exactly. Customer sections (2–4) use plain words, no code names.
2. Diagrams: Harman's two preferred diagrams are the **layers map** (what each ticket touches)
   and the **flow map** (how data moves, what is downstream). Section 6 carries both as one
   `layersmap` block: the base JSON from `references/vanta-layers.md` (parts and `edges`), plus
   this ticket and the other tickets in its epic, each with the parts it changes (`hit`) and
   reads (`near`). `ws plan` draws it with a Layers / Flow switch. Do not add other diagrams
   (sequence, journey, state…) unless Harman asks; `references/diagram-cookbook.md` has them.
   **Tickets and the diagram go hand in hand.** Build the map while you break the work down, not
   after: each PR step in section 8 changes parts that are lit for its ticket; a part nobody
   changes is not lit; if the breakdown changes, the map changes in the same edit.
3. Every code claim ends with `path:line`. Every fact from a doc links to it in section 11.
4. Sizes: S = 1 PR, M = 2–3 PRs, L = 4+ PRs or needs a design/RFC. Each step in section 8 is one PR
   with its verifier.

## Step 4 · Check, review, hand over

1. **Validated.** Run `python3 ~/.claude/skills/plan-ticket/scripts/check-plan.py ~/.claude/fde-plans/<KEY>.md --render`
   and fix every FAIL. It checks that tickets and diagram agree: every ticket is on the map and
   changes a part (or is marked `nocode`), every new part has a ticket, arrows are valid, tickets
   named in section 8 are on the map. A plan is not ready until this passes.
2. Hand the plan to the **plan-reviewer** subagent (Agent tool, `subagent_type: plan-reviewer`):
   "Review ~/.claude/fde-plans/<KEY>.md for ticket <KEY>." It has no context on purpose. Apply the
   fixes you agree with and write its verdict plus what you changed in section 13.
3. If you found a part of Vanta missing from the layers map, list it in section 12 and offer to
   update `references/vanta-layers.md` (it lives in Harman's dotfiles repo: `~/.agent-setup`).
4. If Harman wants the plan in Google Drive for review, use the `share-to-drive` skill (gsync).
   Ask first; never upload on your own.
5. Reply in the fde style (see output style): the TL;DR, the size, the open questions that still
   need Harman, and the command to view it: `ws plan <box> <KEY>`.

## Rules

- Never post to Jira or Slack from this skill. Suggest the comment text if useful.
- Unknown is fine; say "unknown, need X" rather than guess. No invented numbers.
- If the ticket is blocked (a blocker not Done), say so in the TL;DR and plan the parts that are not.
