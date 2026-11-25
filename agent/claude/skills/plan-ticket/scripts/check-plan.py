#!/usr/bin/env python3
"""Check a PLAN.md against the plan-ticket template. Exit 0 = pass, 1 = problems found.

  python3 check-plan.py ~/.claude/fde-plans/FDE-842.md            # structure only
  python3 check-plan.py ~/.claude/fde-plans/FDE-842.md --render   # also render every diagram with mmdc

Checks: required sections in order, TL;DR present, no leftover <placeholders>, UI work answered
Yes/No, the layers map has at least one `hit`, at least 3 diagrams, criteria table has a verifier
column, every mermaid block renders (with --render, when mmdc or npx is available).
"""
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
    if "```mermaid" not in land or not re.search(r"^\s*class\s+[\w,]+\s+hit\s*$", land, re.M):
        problems.append("## 6 needs the layers map with at least one `class <id> hit` line")
    blocks = mermaid_blocks(text)
    if len(blocks) < 3:
        problems.append(f"only {len(blocks)} diagram(s); a plan needs at least 3 (layers map, flow, journey or dependencies)")
    crit = secs.get("9. Acceptance criteria and verifiers", "")
    if "|" not in crit or "verif" not in crit.lower():
        problems.append("## 9 needs a table with a Verifier column")
    if not re.search(r"\]\(https?://", secs.get("11. Sources", "")):
        problems.append("## 11. Sources has no links")
    if not secs.get("13. Reviewer notes"):
        notes.append("reviewer notes still empty (run the plan-reviewer subagent)")
    if do_render:
        problems += render(blocks)
    return problems, notes, len(blocks)


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        sys.exit(__doc__)
    problems, notes, n = check(args[0], "--render" in sys.argv)
    for p in problems:
        print("FAIL", p)
    for p in notes:
        print("NOTE", p)
    print(("PASS" if not problems else "FAIL") + f" {os.path.basename(args[0])}: {len(problems)} problem(s), {n} diagram(s)")
    sys.exit(1 if problems else 0)
