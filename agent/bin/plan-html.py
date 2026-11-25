#!/usr/bin/env python3
"""Render a plan (markdown with Mermaid) as one HTML page. No dependencies.

  python3 plan-html.py              → newest plan in ~/.claude/fde-plans
  python3 plan-html.py FDE-842      → that plan
  python3 plan-html.py path/to.md   → any markdown file
  python3 plan-html.py --list       → list plans, newest first

The page loads marked and mermaid from jsDelivr in your browser, so the box needs nothing
installed. `ws plan <box> [KEY]` runs this on the box and opens the page on your Mac.
"""
import glob
import html
import json
import os
import sys
import time

PLANS = os.path.expanduser("~/.claude/fde-plans")


def pick(arg):
    if arg and os.path.isfile(arg):
        return arg
    files = sorted(glob.glob(os.path.join(PLANS, "*.md")), key=os.path.getmtime, reverse=True)
    if not arg:
        return files[0] if files else None
    for f in files:
        if os.path.basename(f).lower().startswith(arg.lower()):
            return f
    return None


def main():
    arg = sys.argv[1] if len(sys.argv) > 1 else ""
    if arg == "--list":
        for f in sorted(glob.glob(os.path.join(PLANS, "*.md")), key=os.path.getmtime, reverse=True):
            print(time.strftime("%Y-%m-%d %H:%M", time.localtime(os.path.getmtime(f))), os.path.basename(f)[:-3])
        return
    path = pick(arg)
    if not path:
        sys.stderr.write(f"no plan found for '{arg or 'newest'}' in {PLANS}\n")
        sys.exit(1)
    md = open(path, encoding="utf-8").read()
    title = next((l[2:].strip() for l in md.splitlines() if l.startswith("# ")), os.path.basename(path))
    updated = time.strftime("%b %d, %Y %H:%M", time.localtime(os.path.getmtime(path)))
    sys.stdout.write(PAGE.replace("__TITLE__", html.escape(title))
                     .replace("__META__", html.escape(f"{os.path.basename(path)} · updated {updated} · {os.uname().nodename}"))
                     .replace("__MD__", json.dumps(md).replace("</", "<\\/")))


PAGE = r"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>__TITLE__</title>
<style>
:root{--bg:#fbfaf8;--paper:#fff;--ink:#1d1b26;--quiet:#6b6878;--line:#e7e4ee;--accent:#5b3fd1;--tint:#f3f0ff}
@media (prefers-color-scheme:dark){:root{--bg:#15141a;--paper:#1f1d26;--ink:#ece9f5;--quiet:#a19db0;--line:#33303d;--accent:#a493ff;--tint:#2a2540}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.6 -apple-system,BlinkMacSystemFont,Inter,sans-serif}
.wrap{display:grid;grid-template-columns:220px minmax(0,1fr);gap:32px;max-width:1180px;margin:0 auto;padding:24px 16px 80px}
nav{position:sticky;top:16px;align-self:start;font-size:13px}nav a{display:block;color:var(--quiet);text-decoration:none;padding:3px 0}nav a:hover{color:var(--accent)}
nav .meta{color:var(--quiet);font-size:12px;margin-bottom:12px;word-break:break-all}
article{background:var(--paper);border:1px solid var(--line);border-radius:12px;padding:28px 36px}
h1{font-size:26px;line-height:1.25;margin:0 0 12px}h2{font-size:18px;margin:32px 0 8px;padding-top:12px;border-top:1px solid var(--line)}
blockquote{margin:12px 0;padding:12px 16px;background:var(--tint);border-left:4px solid var(--accent);border-radius:6px}blockquote p{margin:0}
table{border-collapse:collapse;width:100%;margin:10px 0;font-size:14px;display:block;overflow-x:auto}th,td{border:1px solid var(--line);padding:6px 10px;text-align:left;vertical-align:top}th{background:var(--tint)}
code{font:13px ui-monospace,Menlo,monospace;background:var(--tint);padding:1px 4px;border-radius:4px}pre{background:var(--tint);padding:12px;border-radius:8px;overflow-x:auto}pre code{background:none;padding:0}
a{color:var(--accent)}.mermaid{background:#fff;border:1px solid var(--line);border-radius:10px;padding:12px;margin:12px 0;overflow-x:auto;text-align:center}
.mermaid svg{max-width:100%;height:auto}.legend{font-size:12px;color:var(--quiet)}.legend b.hit{background:#ffe1d6;border:2px solid #d4502a;padding:0 6px;border-radius:3px;color:#1d1b26}.legend b.near{background:#fff4cc;border:2px solid #b08900;padding:0 6px;border-radius:3px;color:#1d1b26}
@media (max-width:820px){.wrap{grid-template-columns:1fr}nav{position:static}article{padding:20px 16px}}
@media print{nav{display:none}.wrap{display:block}article{border:none}}
</style></head><body><div class="wrap"><nav><div class="meta">__META__</div><div id="toc"></div>
<p class="legend">In the layers map:<br><b class="hit">changed</b> <b class="near">read / depends on</b></p></nav>
<article id="doc">Loading…</article></div>
<script src="https://cdn.jsdelivr.net/npm/marked@12.0.2/marked.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/mermaid@10.9.1/dist/mermaid.min.js"></script>
<script>
const md = __MD__;
const doc = document.getElementById('doc');
if (!window.marked) { doc.innerHTML = '<pre></pre>'; doc.firstChild.textContent = md; }
else {
  const r = new marked.Renderer();
  const code = r.code.bind(r);
  r.code = (c, lang) => {
    const text = typeof c === 'object' ? c.text : c; const l = typeof c === 'object' ? c.lang : lang;
    if (l === 'mermaid') { const d = document.createElement('div'); d.className = 'mermaid'; d.textContent = text; return d.outerHTML; }
    return code(c, lang);
  };
  doc.innerHTML = marked.parse(md, { renderer: r, gfm: true });
  doc.querySelectorAll('a[href^="http"]').forEach(a => a.target = '_blank');
  const toc = document.getElementById('toc');
  doc.querySelectorAll('h2').forEach((h, i) => { h.id = 's' + i; const a = document.createElement('a'); a.href = '#s' + i; a.textContent = h.textContent; toc.appendChild(a); });
  if (window.mermaid) { mermaid.initialize({ startOnLoad: false, theme: 'default', securityLevel: 'strict', flowchart: { htmlLabels: true } }); mermaid.run({ querySelector: '.mermaid' }); }
}
</script></body></html>
"""

if __name__ == "__main__":
    main()
