#!/usr/bin/env python3
"""Check a PLAN.md against the plan-ticket template. Exit 0 = pass, 1 = problems found.

  python3 check-plan.py ~/.claude/fde-plans/FDE-842.md            # structure only
  python3 check-plan.py ~/.claude/fde-plans/FDE-842.md --render   # also render every diagram with mmdc
  python3 check-plan.py <any file with a layersmap block> --map-only   # validate just the ticket ↔ diagram map

Checks: required sections in order, TL;DR present, no leftover <placeholders>, UI work answered
Yes/No, section 6 has a valid layers + flow map (`layersmap` block) in which tickets and diagram
agree (every ticket on the map, arrows valid, tickets named in section 8 present), criteria table has a verifier column, any mermaid block renders (--render).
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

REQUIRED = [
    "1. Problem", "2. Customer today", "3. Pain point", "4. Solution from the customer's side",
    "5. UI work", "6. Where this lands in Vanta", "7. How it works", "8. Steps (PR-sized)",
    "9. Acceptance criteria and verifiers", "10. Risks and open questions", "11. Sources",
    "12. Map updates", "13. Reviewer notes",
]


def sections(text):
    out, cur = {}, None
    for line in text.splitlines():
        m = re.match(r"^##\s+(.+?)\s*$", line)
        if m:
            cur = m.group(1)
            out[cur] = []
        elif cur:
            out[cur].append(line)
    return {k: "\n".join(v).strip() for k, v in out.items()}


def mermaid_blocks(text):
    return re.findall(r"```mermaid\n(.*?)```", text, re.S)


def check_layersmap(src):
    """The interactive layers + flow map. Tickets and the diagram must agree:
    valid JSON, known part ids, every ticket on the map, every new part owned by a ticket,
    arrows between known parts with no cycles, and the focus ticket changes something."""
    try:
        d = json.loads(src)
    except ValueError as e:
        return [f"layersmap block is not valid JSON: {e}"]
    out = []
    ids = [p.get("id") for L in d.get("layers", []) for p in L.get("parts", [])]
    if not ids:
        out.append("layersmap has no layers/parts")
    if len(ids) != len(set(ids)):
        out.append("layersmap has duplicate part ids")
    tickets = d.get("tickets") or []
    if not tickets:
        out.append("layersmap has no tickets")
    touched = set()
    for t in tickets:
        hit, near = t.get("hit", []), t.get("near", [])
        touched.update(hit + near)
        bad = [i for i in hit + near if i not in ids]
        if bad:
            out.append(f"layersmap ticket {t.get('key')} uses unknown part ids: {', '.join(bad)}")
        if t.get("status") not in ("done", "prog", "back"):
            out.append(f"layersmap ticket {t.get('key')}: status must be done, prog or back")
        if not hit and not t.get("nocode"):
            out.append(f"layersmap ticket {t.get('key')} changes no part: give it `hit` parts, or mark it \"nocode\": true (spike, sandbox check)")
    for L in d.get("layers", []):
        for p in L.get("parts", []):
            if p.get("new") and p.get("id") not in touched:
                out.append(f"layersmap new part `{p.get('id')}` is not used by any ticket")
    focus = next((t for t in tickets if t.get("key") == d.get("focus")), None)
    if not focus:
        out.append("layersmap `focus` must name one of its tickets")
    elif not focus.get("hit") and not focus.get("nocode"):
        out.append("layersmap focus ticket has no `hit` parts")
    # flow map: arrows
    edges = d.get("edges") or []
    if not edges:
        out.append("layersmap has no `edges`: the flow map needs arrows between parts")
    graph = {}
    for e in edges:
        if not isinstance(e, list) or len(e) < 2 or e[0] not in ids or e[1] not in ids:
            out.append(f"layersmap edge {e} must be [from, to] with known part ids")
            continue
        graph.setdefault(e[0], []).append(e[1])
    state = {}

    def cyclic(n):
        state[n] = 1
        for m in graph.get(n, []):
            if state.get(m) == 1 or (state.get(m) is None and cyclic(m)):
                return True
        state[n] = 2
        return False

    if any(state.get(n) is None and cyclic(n) for n in list(graph)):
        out.append("layersmap edges contain a cycle: the flow map needs arrows that only go forward")
    if focus and focus.get("hit") and edges and not any(e[0] in focus["hit"] or e[1] in focus["hit"] for e in edges if isinstance(e, list) and len(e) > 1):
        out.append("layersmap: no arrow touches the focus ticket's changed parts, so the flow map can't show it")
    return out


def map_data(text):
    m = re.search(r"```layersmap\n(.*?)```", text, re.S)
    try:
        return json.loads(m.group(1)) if m else None
    except ValueError:
        return None


def render(blocks):
    cmd = ["mmdc"] if shutil.which("mmdc") else (["npx", "-y", "@mermaid-js/mermaid-cli"] if shutil.which("npx") else None)
    if not cmd:
        return ["--render: mmdc/npx not found, diagrams not rendered"]
    errs = []
    with tempfile.TemporaryDirectory() as d:
        for i, b in enumerate(blocks, 1):
            src, out = os.path.join(d, f"{i}.mmd"), os.path.join(d, f"{i}.svg")
            open(src, "w").write(b)
            r = subprocess.run(cmd + ["-q", "-i", src, "-o", out], capture_output=True, text=True, timeout=120)
            if r.returncode != 0 or not os.path.exists(out):
                first = (r.stderr or r.stdout).strip().splitlines()
                errs.append(f"diagram {i} ({b.split()[0]}) does not render: {first[0] if first else 'unknown error'}")
    return errs


def check(path, do_render=False):
    text = open(path, encoding="utf-8").read()
    problems, notes = [], []
    secs = sections(text)
    names = list(secs)
    pos = -1
    for want in REQUIRED:
        if want not in secs:
            problems.append(f"missing section: ## {want}")
            continue
        i = names.index(want)
        if i < pos:
            problems.append(f"section out of order: ## {want}")
        pos = i
        if not secs[want] and want != "13. Reviewer notes":
            problems.append(f"empty section: ## {want}")
    if not re.search(r"\*\*TL;DR\*\*", text):
        problems.append("no **TL;DR** line under the title")
    leftovers = sorted(set(re.findall(r"<(?:KEY|EPIC|…|[a-z][^<>\n]{2,60})>", re.sub(r"`[^`\n]*`", "", re.sub(r"```.*?```", "", text, flags=re.S)))))
    leftovers = [l for l in leftovers if not re.match(r"<(br|/?b|/?i|https?:)", l)]
    if leftovers:
        problems.append("unfilled placeholders: " + ", ".join(leftovers[:6]))
    ui = secs.get("5. UI work", "")
    if not re.match(r"\*\*(Yes|No)\b", ui):
        problems.append("## 5. UI work must start with **Yes** or **No**")
    land = secs.get("6. Where this lands in Vanta", "")
    lm = re.search(r"```layersmap\n(.*?)```", land, re.S)
    if lm:
        problems += check_layersmap(lm.group(1))
        d = map_data(text) or {}
        keys = {t.get("key") for t in d.get("tickets", [])}
        prefix = (d.get("focus") or "").split("-")[0]
        steps = secs.get("8. Steps (PR-sized)", "")
        missing = sorted(set(re.findall(r"\b%s-\d+\b" % re.escape(prefix), steps)) - keys) if prefix else []
        if missing:
            problems.append("tickets named in ## 8 but not on the map: " + ", ".join(missing))
        focus = next((t for t in d.get("tickets", []) if t.get("key") == d.get("focus")), {})
        labels = {p["id"]: p.get("label", "") for L in d.get("layers", []) for p in L.get("parts", [])}
        table = land[lm.end():]
        untold = [i for i in focus.get("hit", []) if i not in table and labels.get(i, "\0") not in table]
        if untold:
            problems.append("## 6 table has no row for changed part(s): " + ", ".join(untold))
    elif "```mermaid" not in land or not re.search(r"^\s*class\s+[\w,]+\s+hit\s*$", land, re.M):
        problems.append("## 6 needs a `layersmap` block (see vanta-layers.md) with this ticket's `hit` parts")
    blocks = mermaid_blocks(text)
    crit = secs.get("9. Acceptance criteria and verifiers", "")
    if "|" not in crit or "verif" not in crit.lower():
        problems.append("## 9 needs a table with a Verifier column")
    if not re.search(r"\]\(https?://", secs.get("11. Sources", "")):
        problems.append("## 11. Sources has no links")
    if not secs.get("13. Reviewer notes"):
        notes.append("reviewer notes still empty (run the plan-reviewer subagent)")
    if do_render:
        problems += render(blocks)
    return problems, notes, len(blocks) + (1 if lm else 0)


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        sys.exit(__doc__)
    if "--map-only" in sys.argv:  # any file with a layersmap block, e.g. a feasibility's ticket map
        m = re.search(r"```layersmap\n(.*?)```", open(args[0], encoding="utf-8").read(), re.S)
        probs = check_layersmap(m.group(1)) if m else ["no `layersmap` block found"]
        for p in probs:
            print("FAIL", p)
        print(("PASS" if not probs else "FAIL") + f" map in {os.path.basename(args[0])}: {len(probs)} problem(s)")
        sys.exit(1 if probs else 0)
    problems, notes, n = check(args[0], "--render" in sys.argv)
    for p in problems:
        print("FAIL", p)
    for p in notes:
        print("NOTE", p)
    print(("PASS" if not problems else "FAIL") + f" {os.path.basename(args[0])}: {len(problems)} problem(s), {n} diagram(s)")
    sys.exit(1 if problems else 0)
