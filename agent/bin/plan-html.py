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
.mermaid svg{max-width:100%;height:auto}
:root{--hit:#d4502a;--hit-bg:#ffe1d6;--near:#b08900;--near-bg:#fff4cc;--ok:#2f7d4f}
@media (prefers-color-scheme:dark){:root{--hit:#ff8a62;--hit-bg:#4a2418;--near:#e8c14a;--near-bg:#3d3212;--ok:#6cc995}}
.layersmap{border:1px solid var(--line);border-radius:10px;padding:14px;margin:12px 0}
.lm-top{display:flex;flex-wrap:wrap;gap:8px;justify-content:space-between;align-items:flex-start;margin-bottom:12px}
.lm-bar{display:flex;flex-wrap:wrap;gap:6px}
.lm-seg{display:inline-flex;border:1.5px solid var(--line);border-radius:8px;overflow:hidden;flex:none}
.lm-seg button{font:500 13px inherit;font-family:inherit;color:var(--ink);background:var(--paper);border:0;padding:5px 12px;cursor:pointer}
.lm-seg button[aria-pressed="true"]{background:var(--ink);color:var(--paper)}
.layersmap [hidden]{display:none!important}
.lm-flowwrap{overflow-x:auto}
.lm-flow{position:relative;display:grid;gap:10px 30px;align-items:center;padding:6px 2px}
.lm-cell{display:grid;gap:12px;align-content:center;position:relative;z-index:1}
.lm-fp{background:var(--paper);border-color:var(--line);font-size:12.5px}
.lm-flow svg{position:absolute;inset:0;width:100%;height:100%;pointer-events:none;z-index:0;overflow:visible}
.lm-flow path{fill:none;stroke:var(--line);stroke-width:1.25}.lm-flow path.on{stroke:var(--hit);stroke-width:2.25}.lm-flow path.soft{stroke:var(--near);stroke-width:2}
.lm-flow path.lm-ah{stroke:none;fill:var(--line)}.lm-flow path.lm-ah.on{fill:var(--hit)}.lm-flow path.lm-ah.soft{fill:var(--near)}
.lm-rest{margin-top:10px;display:grid;gap:6px}.lm-rest span{font:12px ui-monospace,Menlo,monospace;color:var(--quiet)}
.lm-tk{font:500 13px inherit;font-family:inherit;color:var(--ink);background:var(--paper);border:1.5px solid var(--line);border-radius:8px;padding:4px 10px;cursor:pointer;display:inline-flex;gap:6px;align-items:center}
.lm-tk[aria-pressed="true"]{border-color:var(--accent);box-shadow:0 0 0 2px var(--tint)}
.lm-tk i{width:8px;height:8px;border-radius:50%;border:1.5px solid var(--quiet)}.lm-tk i.done{background:var(--ok);border-color:var(--ok)}.lm-tk i.prog{background:var(--near);border-color:var(--near)}
.lm-rows{display:grid;gap:8px}.lm-row{display:grid;grid-template-columns:150px minmax(0,1fr);gap:10px}
.lm-name{font:12px ui-monospace,Menlo,monospace;color:var(--quiet);padding-top:8px}
.lm-parts{display:flex;flex-wrap:wrap;gap:8px;border:1px dashed var(--line);border-radius:8px;padding:8px}
.lm-part{font:13px inherit;font-family:inherit;text-align:left;color:var(--ink);background:var(--tint);border:1.5px solid transparent;border-radius:7px;padding:5px 10px;cursor:pointer;line-height:1.3}
.lm-part small{display:block;font:11.5px ui-monospace,Menlo,monospace;color:var(--quiet);overflow-wrap:anywhere}
.lm-part.hit{background:var(--hit-bg);border-color:var(--hit)}.lm-part.near{background:var(--near-bg);border-color:var(--near)}.lm-part.new{border-style:dashed;border-color:var(--quiet)}
.lm-part.hit small,.lm-part.near small{color:inherit;opacity:.75}
.lm-detail{margin-top:12px;border-top:1px solid var(--line);padding-top:10px;font-size:14px}.lm-detail p{margin:4px 0}.lm-detail ul{margin:4px 0;padding-left:18px}
.lm-st{font-size:12px;border:1px solid var(--line);border-radius:99px;padding:0 8px;color:var(--quiet)}
.lm-tk:focus-visible,.lm-part:focus-visible,.lm-seg button:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
@media (max-width:820px){.lm-row{grid-template-columns:1fr}.lm-name{padding-top:0}}.legend{font-size:12px;color:var(--quiet)}.legend b.hit{background:#ffe1d6;border:2px solid #d4502a;padding:0 6px;border-radius:3px;color:#1d1b26}.legend b.near{background:#fff4cc;border:2px solid #b08900;padding:0 6px;border-radius:3px;color:#1d1b26}
@media (max-width:820px){.wrap{grid-template-columns:1fr}nav{position:static}article{padding:20px 16px}}
@media print{nav{display:none}.wrap{display:block}article{border:none}}
</style></head><body><div class="wrap"><nav><div class="meta">__META__</div><div id="toc"></div>
<p class="legend">In the map (Layers or Flow), click a ticket or a part:<br><b class="hit">changes</b> <b class="near">reads / depends on</b></p></nav>
<article id="doc">Loading…</article></div>
<script src="https://cdn.jsdelivr.net/npm/marked@12.0.2/marked.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/mermaid@10.9.1/dist/mermaid.min.js"></script>
<script>
const md = __MD__;
// Interactive layers map: click a ticket to light up the parts it changes (hit) and reads (near);
// click a part to list the tickets that touch it. Data = the plan's ```layersmap JSON block.
function buildLayersMap(host) {
  let d; try { d = JSON.parse(host.textContent); } catch (e) { host.className = ''; host.innerHTML = '<pre></pre>'; host.firstChild.textContent = 'layersmap: invalid JSON (' + e.message + ')'; return; }
  const esc = s => String(s == null ? '' : s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const ST = { done: 'Done', prog: 'In progress', back: 'Backlog' };
  const tickets = d.tickets || [], parts = {}, order = [];
  const edges = (d.edges || []).filter(e => Array.isArray(e) && e.length > 1);
  host.innerHTML = '<div class="lm-top"><div class="lm-bar"></div><div class="lm-seg"><button type="button" aria-pressed="true">Layers</button><button type="button" aria-pressed="false">Flow</button></div></div>' +
    '<div class="lm-rows"></div><div class="lm-flowwrap" hidden><div class="lm-flow"></div><div class="lm-rest" hidden><span>Not in the flow</span><div class="lm-parts"></div></div></div><div class="lm-detail"></div>';
  const bar = host.querySelector('.lm-bar'), seg = host.querySelector('.lm-seg'), rows = host.querySelector('.lm-rows'), fwrap = host.querySelector('.lm-flowwrap'),
    flow = host.querySelector('.lm-flow'), rest = host.querySelector('.lm-rest'), detail = host.querySelector('.lm-detail');
  const mk = (p, cls) => { const b = document.createElement('button'); b.type = 'button'; b.className = cls + (p.new ? ' new' : '');
    b.innerHTML = esc(p.label) + (p.path && cls === 'lm-part' ? '<small>' + esc(p.path) + '</small>' : ''); if (p.path) b.title = p.path;
    b.addEventListener('click', () => showPart(p)); parts[p.id].els.push(b); return b; };
  // layers view
  (d.layers || []).forEach(L => {
    const row = document.createElement('div'); row.className = 'lm-row';
    row.innerHTML = '<div class="lm-name">' + esc(L.name) + '</div><div class="lm-parts"></div>';
    (L.parts || []).forEach(p => { parts[p.id] = { p, els: [] }; order.push(p.id); row.lastChild.appendChild(mk(p, 'lm-part')); });
    rows.appendChild(row);
  });
  // flow view: columns = how many arrows deep a part sits (left to right)
  const depth = {}; edges.forEach(([a, b]) => { if (parts[a] && parts[b]) { depth[a] = depth[a] || 0; depth[b] = depth[b] || 0; } });
  for (let i = 0; i < order.length; i++) edges.forEach(([a, b]) => { if (a in depth && b in depth && depth[b] < depth[a] + 1 && depth[a] < 9) depth[b] = depth[a] + 1; });
  const cols = Math.max(0, ...Object.values(depth)) + 1, fel = {};
  flow.style.gridTemplateColumns = 'repeat(' + cols + ',minmax(0,1fr))'; flow.style.minWidth = Math.max(560, cols * 150) + 'px';
  for (let c = 0; c < cols; c++) { const cell = document.createElement('div'); cell.className = 'lm-cell';
    order.filter(id => depth[id] === c).forEach(id => { fel[id] = mk(parts[id].p, 'lm-part lm-fp'); cell.appendChild(fel[id]); }); flow.appendChild(cell); }
  const loose = order.filter(id => !(id in depth)); rest.hidden = !loose.length; loose.forEach(id => rest.lastChild.appendChild(mk(parts[id].p, 'lm-part')));
  const NS = 'http://www.w3.org/2000/svg', svg = document.createElementNS(NS, 'svg'); svg.setAttribute('aria-hidden', 'true'); flow.appendChild(svg);
  let lit = {}; // part id -> 'hit' | 'near'
  function draw() {
    if (fwrap.hidden) return; const R = flow.getBoundingClientRect();
    let h = ['base', 'on', 'soft'].map(k => '<marker id="lmm-' + k + '" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" class="lm-ah ' + k + '"/></marker>').join('');
    edges.filter(([a, b]) => fel[a] && fel[b]).map(([a, b]) => [a, b, lit[a] && lit[b] ? (lit[a] === 'hit' || lit[b] === 'hit' ? 'on' : 'soft') : 'base'])
      .sort((x, y) => (x[2] === 'base' ? 0 : 1) - (y[2] === 'base' ? 0 : 1)).forEach(([a, b, k]) => {
        const A = fel[a].getBoundingClientRect(), B = fel[b].getBoundingClientRect();
        const x1 = A.right - R.left, y1 = A.top - R.top + A.height / 2, x2 = B.left - R.left, y2 = B.top - R.top + B.height / 2, mx = (x1 + x2) / 2;
        h += '<path d="M' + x1 + ' ' + y1 + 'C' + mx + ' ' + y1 + ',' + mx + ' ' + y2 + ',' + x2 + ' ' + y2 + '" class="' + k + '" marker-end="url(#lmm-' + k + ')"/>';
      });
    svg.innerHTML = h;
  }
  const paint = m => { lit = m; order.forEach(id => parts[id].els.forEach(el => { el.classList.toggle('hit', m[id] === 'hit'); el.classList.toggle('near', m[id] === 'near'); })); draw(); };
  const names = ids => (ids || []).filter(id => parts[id]).map(id => esc(parts[id].p.label)).join(', ') || 'none';
  const press = k => tickets.forEach(t => t._b.setAttribute('aria-pressed', String(t.key === k)));
  function showTicket(t) {
    press(t.key); const m = {}; (t.near || []).forEach(id => m[id] = 'near'); (t.hit || []).forEach(id => m[id] = 'hit'); paint(m);
    detail.innerHTML = '<b>' + esc(t.key) + ' · ' + esc(t.title) + '</b> <span class="lm-st ' + esc(t.status) + '">' + (ST[t.status] || '') + '</span>' + (t.nocode ? ' <span class="lm-st">no code change</span>' : '') +
      '<p><b>Changes:</b> ' + names(t.hit) + ' · <b>Reads or depends on:</b> ' + names(t.near) + '</p>' +
      ((t.notes || []).length ? '<ul>' + t.notes.map(n => '<li>' + esc(n) + '</li>').join('') + '</ul>' : '');
  }
  function showPart(p) {
    press(null); const down = [], seen = new Set([p.id]);
    (function walk(x) { edges.forEach(([a, b]) => { if (a === x && parts[b] && !seen.has(b)) { seen.add(b); down.push(b); walk(b); } }); })(p.id);
    const m = { [p.id]: 'hit' }; down.forEach(id => m[id] = 'near'); paint(m);
    const ts = tickets.filter(t => (t.hit || []).includes(p.id) || (t.near || []).includes(p.id));
    detail.innerHTML = '<b>' + esc(p.label) + '</b>' + (p.path ? ' <code>' + esc(p.path) + '</code>' : '') + (p.new ? ' <span class="lm-st">not on the Vanta map yet</span>' : '') +
      '<p><b>Touched by:</b> ' + (ts.map(t => esc(t.key) + ' (' + ((t.hit || []).includes(p.id) ? 'changes' : 'reads') + ')').join(', ') || 'no ticket in this plan') + '</p>' +
      '<p><b>Downstream:</b> ' + (down.length ? names(down) : 'nothing') + '</p>';
  }
  tickets.forEach(t => {
    const b = document.createElement('button'); b.type = 'button'; b.className = 'lm-tk'; b.title = t.title + ' (' + (ST[t.status] || '') + ')';
    b.innerHTML = '<i class="' + esc(t.status) + '"></i>' + esc(t.key); b.addEventListener('click', () => showTicket(t)); t._b = b; bar.appendChild(b);
  });
  seg.addEventListener('click', ev => { const b = ev.target.closest('button'); if (!b) return; const f = b === seg.children[1];
    seg.children[0].setAttribute('aria-pressed', String(!f)); seg.children[1].setAttribute('aria-pressed', String(f)); rows.hidden = f; fwrap.hidden = !f; draw(); });
  window.addEventListener('resize', draw);
  const f = tickets.find(t => t.key === d.focus) || tickets[0]; if (f) showTicket(f);
}
const doc = document.getElementById('doc');
if (!window.marked) { doc.innerHTML = '<pre></pre>'; doc.firstChild.textContent = md; }
else {
  const r = new marked.Renderer();
  const code = r.code.bind(r);
  r.code = (c, lang) => {
    const text = typeof c === 'object' ? c.text : c; const l = typeof c === 'object' ? c.lang : lang;
    if (l === 'layersmap') { const d = document.createElement('div'); d.className = 'layersmap'; d.textContent = text; return d.outerHTML; }
    if (l === 'mermaid') { const d = document.createElement('div'); d.className = 'mermaid'; d.textContent = text; return d.outerHTML; }
    return code(c, lang);
  };
  doc.innerHTML = marked.parse(md, { renderer: r, gfm: true });
  doc.querySelectorAll('a[href^="http"]').forEach(a => a.target = '_blank');
  const toc = document.getElementById('toc');
  doc.querySelectorAll('h2').forEach((h, i) => { h.id = 's' + i; const a = document.createElement('a'); a.href = '#s' + i; a.textContent = h.textContent; toc.appendChild(a); });
  doc.querySelectorAll('.layersmap').forEach(buildLayersMap);
  if (window.mermaid) { mermaid.initialize({ startOnLoad: false, theme: 'default', securityLevel: 'strict', flowchart: { htmlLabels: true } }); mermaid.run({ querySelector: '.mermaid' }); }
}
</script></body></html>
"""

if __name__ == "__main__":
    main()
