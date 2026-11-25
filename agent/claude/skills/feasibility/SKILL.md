---
name: feasibility
description: Draft an FDE Feasibility Evaluation for a customer request from #fde-intake, in the official template format. Use when asked to write, draft, or update a feasibility, feasibility eval, or FDE eval for a request, Slack intake link, Jira ticket, or context brief.
---

# FDE Feasibility Evaluation

You draft the feasibility evaluation. A human FDE owns the verdict, the estimate, and the urgency.

## Inputs (ask for any that are missing)

1. The intake: a `#fde-intake` Slack message URL, the Jira ticket, or both.
2. The **context brief** from `/fde:intake`, if it exists. If it does not exist, suggest that I run
   `/fde:intake <slack url>` first. The brief saves a lot of research. If I say skip, do the research yourself (step 2).
3. Any notes I have on the customer, the deal, or a preferred approach.

## Procedure

1. **Read the request.** Restate the customer ask in two sentences. Confirm it with me before you go
   further if it is ambiguous.
2. **Research the product side** with Glean. Find:
   - the owning product area, its PM, and its eng lead
   - existing RFCs, PRDs, eng specs, and roadmap items that overlap the ask
   - earlier FDE work or Slack threads about the same request
3. **Research the code side** in `obsidian`. Find the relevant domains, data models, services,
   integrations, and feature-flag patterns. Record file paths. Note Dominion domain boundaries
   that the change would cross.
4. **Generate options.** Option A must meet the requirements with the *smallest blast radius*.
   Give 1–2 alternatives and say why each one is rejected.
5. **Break Option A into tickets and map them** (tickets and the diagram go hand in hand).
   Propose the tickets for Option A, one per numbered "How" component, with keys `T1`, `T2`… (or
   real Jira keys if they exist). Write a `layersmap` block (format and base data:
   `~/.claude/skills/plan-ticket/references/vanta-layers.md`): each ticket with the parts it
   changes (`hit`) and reads (`near`), plus the `edges` showing how data flows. Save it as
   `~/.claude/fde-plans/<short-slug>-feasibility.md` with a one-line title and the ticket list
   above the block. Validate it:
   `python3 ~/.claude/skills/plan-ticket/scripts/check-plan.py <that file> --map-only`.
   Fix every FAIL. If a "How" component has no ticket, or a ticket changes no part, the solution
   is not yet worked out: go back to step 4.
6. **Draft the document** in the template structure below. The "How" list in the Executive Summary
   and the Technical details must match the mapped tickets one to one. The map file is working
   material for me and reviewers; the template's Project breakdown stays `<TODO!>` unless asked.
7. **Self-check** against the checklist at the end. Fix the problems before you show me the draft.

## Template structure (from the FDE Feasibility Evaluation Template)

Template: https://docs.google.com/document/d/13iBgwxYloebqd6eqGSpMhwkwDxRFvgNFD9QUctdE4SA

Header: Title · Last updated · Status: WIP · Author(s) · Intake Request Link · Feature Ticket Link ·
Reviewer table (FDE EM, Product Team PM, Product Team Eng Lead, FDE Eng Reviewer; all "To Do").

Sections, in order:

1. **Executive Summary** (write last): Summary · Feasibility · Estimate · What · How (numbered
   components) · Output · Feature flag · Risk flagged. Each in its own short paragraph.
2. **Background & Urgency**: context, history, and links to SA docs, specs, and Slack threads.
3. **Request Details & Requirements**: the specific ask and the minimum hard requirements.
4. **Feasibility & Sizing**
5. **Possible Architectures / Options / Alternatives**: Option A (recommended, smallest blast radius) with a
   summary and blockers; Option B/C with the reason each one is rejected.
6. **UI/UX Implications**: what differs for this customer, and parity against other integrations of
   the same type. Write "N/a" if there are none.
7. **Out of Scope**
8. **Recommended Solution Applicability**: can it go GA? Which customers benefit?
9. **Solution Uncertainties**
10. **Eng Spec**: Vocabulary · Technical details (Model changes, API changes, UI changes) ·
    Testing plan · Metrics · Rollout plan (default: behind a feature flag, PM owns the GA decision) ·
    Security Implications table. Leave Deployment and Project breakdown as `<TODO!>` unless asked.

## Hard rules from the template

- **Write `<TODO!>`, not content, for:** the Estimate line, the Urgency part of Background,
  the whole Feasibility & Sizing section, and the "external reasons" bullet under Solution
  Uncertainties. You MAY put *evidence* for the human under a `<TODO!>` in a clearly labelled
  "Notes for FDE" sub-bullet. Do not give a verdict or a number of weeks.
- **Product-level above, engineering-level below.** Keep property names, packages, and
  architecture details out of every section before "Technical details".
- **Prose, not bullets,** unless the template already uses a structure there.
- **Use ASD-STE100 Simplified Technical English:** active voice, simple tenses, no "-ing" forms
  except in technical names, one word per meaning, ≤25 words per descriptive sentence,
  ≤20 words per procedural sentence, ≤6 sentences per paragraph, and keep all articles.
- Express all time in **weeks**. Never use story points or T-shirt sizes.
- Remove the Style Guidance section from the output.

## Output

- Default: a Markdown file `feasibility-<short-slug>.md` in the current directory, ready to paste
  into a copy of the template.
- The ticket map: `~/.claude/fde-plans/<short-slug>-feasibility.md`. Tell me the command to view it
  as the layers map and flow map: `ws plan <box> <short-slug>-feasibility`.
- Finish with a short list: the sources you used (links/paths), the `<TODO!>` items for me, and
  the open questions for the PM or eng lead.

## Self-check before you hand over

- [ ] Every claim about product behavior has a doc link or a code path.
- [ ] Option A has the smallest blast radius of all the options.
- [ ] The ticket map passes `check-plan.py --map-only`, and its tickets match the "How" components.
- [ ] Estimate, Urgency, Feasibility & Sizing, and the external-reasons bullet are `<TODO!>`.
- [ ] No technical identifiers appear above "Technical details".
- [ ] Spot-check five sentences against the STE rules (length, voice, no "-ing").
- [ ] Rollout is behind a feature flag unless the request says otherwise.
