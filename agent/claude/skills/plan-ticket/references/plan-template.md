# PLAN.md template

Copy this into `~/.claude/fde-plans/<KEY>.md` (shared by every box) and fill it in. Keep the
headings exactly as written: `check-plan.py` and `ws plan` look for them. Replace every
`<…>` placeholder. If a section does not apply, write one line saying why. Do not delete it.

Writing rules: short sentences, plain words, one idea per bullet. Customer sections use the
customer's words, not code names. Every claim about code ends with a `path:line`.

---

~~~~markdown
# <KEY>: <ticket title>

> **TL;DR** <One or two sentences: what changes for the customer, how big it is, and the one
> thing that could block it.>

| Ticket | Epic | Customer | Size | UI work? | Status |
| --- | --- | --- | --- | --- | --- |
| [<KEY>](<jira url>) | [<EPIC>](<url>) | <customer> | <S / M / L, ~N PRs> | <Yes / No> | Draft for review |

## 1. Problem
<2–4 sentences. What is broken or missing, for whom, and why it matters now.>

## 2. Customer today
<What the customer does today, step by step, in their words. Include the workaround.>

## 3. Pain point
- <The specific pain, with a number when there is one: hours per week, records missed, deals blocked.>

## 4. Solution from the customer's side
<What the customer sees and does after this ships. No code names.>

## 5. UI work
**<Yes / No>.** <If yes: which screens change and whether a designer is needed (Alpaca components?).
If no: say where the result shows up anyway, e.g. "existing Inventory page, no change".>

## 6. Where this lands in Vanta
<One sentence: which layers this touches.>

```layersmap
<base JSON from references/vanta-layers.md, plus "focus" and "tickets" (this ticket and its epic)>
```

| Part | Change | Where (path) |
| --- | --- | --- |
| <node id> | <what changes> | <path:line> |

## 7. How it works
<The flow after the change, as a numbered list: one line per step, who does what. Add a Mermaid
diagram only if Harman asked for one.>

## 8. Steps (PR-sized)
1. **<PR title>** · <files> · verified by <test or check>
2. …


## 9. Acceptance criteria and verifiers
| # | Criterion | Verifier (command or check) |
| --- | --- | --- |
| 1 | <…> | <`pnpm test …` / manual step> |

## 10. Risks and open questions
| Risk or question | Impact | Proposed answer | Owner |
| --- | --- | --- | --- |
| <…> | <High/Med/Low> | <…> | <Harman / PM / customer> |

## 11. Sources
- <[title](url)> — <what it told you>

## 12. Map updates
<Parts of the Vanta layers map that were missing or wrong, or "None".>

## 13. Reviewer notes
<Filled by the plan-reviewer subagent: verdict, and what was fixed.>
~~~~
