#!/usr/bin/env python3
"""Make a Google-Docs-friendly copy of a plan or feasibility markdown file.

  python3 plan-for-drive.py ~/.claude/fde-plans/FDE-842.md      → writes FDE-842.drive.md beside it

Google Docs cannot run the interactive layers / flow map, so each `layersmap` block is replaced
by plain tables: one row per ticket (status, parts it changes, parts it reads) and the arrows of
the flow. Everything else is copied unchanged. Upload the .drive.md copy with gsync; the original
stays the source of truth (`ws plan` still shows the interactive map).
"""
import json
import os
import re
import sys

ST = {"done": "Done", "prog": "In progress", "back": "Backlog"}


def tables(src):
    try:
        d = json.loads(src)
    except ValueError:
        return "_(The map data could not be read.)_"
    label = {p["id"]: p.get("label", p["id"]) for L in d.get("layers", []) for p in L.get("parts", [])}
    names = lambda ids: ", ".join(label.get(i, i) for i in ids) or "none"
    out = ["**Where each ticket lands** (interactive version: `ws plan`)", "",
           "| Ticket | Status | Changes | Reads or depends on |", "| --- | --- | --- | --- |"]
    for t in d.get("tickets", []):
        key = f"**{t.get('key')}**" if t.get("key") == d.get("focus") else t.get("key", "")
        out.append(f"| {key} {t.get('title', '')} | {ST.get(t.get('status'), '')} | "
                   f"{'no code change' if t.get('nocode') else names(t.get('hit', []))} | {names(t.get('near', []))} |")
    lit = set()
    for t in d.get("tickets", []):
        lit.update(t.get("hit", []) + t.get("near", []))
    flow = [e for e in d.get("edges", []) if isinstance(e, list) and len(e) > 1 and e[0] in lit and e[1] in lit]
    if flow:
        out += ["", "**How data flows between those parts**", ""]
        out += [f"- {label.get(e[0], e[0])} → {label.get(e[1], e[1])}" + (f" ({e[2]})" if len(e) > 2 and e[2] else "") for e in flow]
    return "\n".join(out)


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    src = sys.argv[1]
    text = open(src, encoding="utf-8").read()
    n = len(re.findall(r"```layersmap\n", text))
    text = re.sub(r"```layersmap\n(.*?)```", lambda m: tables(m.group(1)), text, flags=re.S)
    dest = re.sub(r"\.md$", "", src) + ".drive.md"
    open(dest, "w", encoding="utf-8").write(text)
    print(f"{dest} ({n} map block(s) converted to tables)")


if __name__ == "__main__":
    main()
