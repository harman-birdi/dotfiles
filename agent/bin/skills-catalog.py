#!/usr/bin/env python3
"""List every Claude Code skill, plugin and subagent this box can use, with what each one does.

Runs on an Ona box (or your Mac). No dependencies.
  python3 skills-catalog.py            → HTML page on stdout (what `ws skills <box>` opens)
  python3 skills-catalog.py --text     → plain list
  python3 skills-catalog.py --json     → machine-readable

Sources, in the order shown:
  mine        ~/.claude/skills/*            (your dotfiles: agent/claude/skills)
  plugin      enabled plugins               (e.g. fde, from the obsidian marketplace)
  repo        <repo>/.claude/skills/*       (loaded in every session in that checkout)
  available   marketplace plugins not enabled, and the opt-in skills registry (<repo>/skills)
  subagent    ~/.claude/agents/*.md and enabled plugins' agents
"""
import glob
import html
import json
import os
import re
import sys

HOME = os.path.expanduser("~")
CLAUDE = os.path.join(HOME, ".claude")


def frontmatter(path):
    """Return (name, description) from a SKILL.md / agent .md YAML header. Tolerant, no yaml lib."""
    try:
        text = open(path, encoding="utf-8", errors="replace").read()
    except OSError:
        return None, ""
    m = re.match(r"^---\s*\n(.*?)\n---", text, re.S)
    if not m:
        first = next((l.strip("# ").strip() for l in text.splitlines() if l.strip()), "")
        return None, first
    fields, key, buf = {}, None, []
    for line in m.group(1).splitlines():
        km = re.match(r"^([A-Za-z_-]+):\s*(.*)$", line)
        if km and not line.startswith(" "):
            if key:
                fields[key] = " ".join(buf).strip()
            key, val = km.group(1), km.group(2).strip()
            buf = [] if val in (">", "|", ">-", "|-") else [val.strip("\"'")]
        elif key:
            buf.append(line.strip())
    if key:
        fields[key] = " ".join(buf).strip()
    return fields.get("name"), fields.get("description", "")


def load_json(path):
    try:
        with open(path) as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def find_repo():
    for d in sorted(glob.glob("/workspaces/*/")):
        if os.path.isfile(os.path.join(d, ".claude-plugin", "marketplace.json")):
            return d.rstrip("/")
    cwd = os.getcwd()
    return cwd if os.path.isfile(os.path.join(cwd, ".claude-plugin", "marketplace.json")) else None


def skills_in(folder):
    out = []
    for p in sorted(glob.glob(os.path.join(folder, "*", "SKILL.md"))):
        name, desc = frontmatter(p)
        out.append({"name": name or os.path.basename(os.path.dirname(p)), "description": desc, "path": p})
    return out


def main():
    items = []
    add = lambda **kw: items.append(kw)
    repo = find_repo()

    # Enabled plugins: user settings, plus the repo's project and local settings.
    enabled = {}
    for s in [os.path.join(CLAUDE, "settings.json")] + (
        [os.path.join(repo, ".claude", f) for f in ("settings.json", "settings.local.json")] if repo else []
    ):
        for k, v in (load_json(s).get("enabledPlugins") or {}).items():
            enabled[k] = enabled.get(k, False) or bool(v)

    # 1. Mine
    for s in skills_in(os.path.join(CLAUDE, "skills")):
        real = os.path.realpath(os.path.dirname(s["path"]))
        origin = "dotfiles" if ".agent-setup" in real or "dotfiles" in real else "local"
        add(group="mine", name=s["name"], call="/" + s["name"], description=s["description"], source=origin, kind="skill")

    # 2. Installed plugins (enabled ones in full; disabled ones listed once)
    installed = load_json(os.path.join(CLAUDE, "plugins", "installed_plugins.json")).get("plugins", {})
    seen_plugins = set()
    for pid, entries in sorted(installed.items()):
        entry = entries[-1] if isinstance(entries, list) and entries else (entries or {})
        root = entry.get("installPath", "")
        pname = pid.split("@")[0]
        seen_plugins.add(pname)
        manifest = load_json(os.path.join(root, ".claude-plugin", "plugin.json"))
        on = enabled.get(pid, False)
        if not on:
            add(group="available", name=pname, call=f"enable: add '{pname}' to agent/plugins.txt", description=manifest.get("description", ""), source=pid + " (installed, off)", kind="plugin")
            continue
        for s in skills_in(os.path.join(root, "skills")):
            add(group="plugin", name=f"{pname}:{s['name']}", call=f"/{pname}:{s['name']}", description=s["description"], source=pid, kind="skill")
        for c in sorted(glob.glob(os.path.join(root, "commands", "*.md"))):
            _, desc = frontmatter(c)
            cname = os.path.splitext(os.path.basename(c))[0]
            add(group="plugin", name=f"{pname}:{cname}", call=f"/{pname}:{cname}", description=desc, source=pid, kind="command")
        for a in sorted(glob.glob(os.path.join(root, "agents", "*.md"))):
            name, desc = frontmatter(a)
            add(group="subagent", name=name or os.path.basename(a)[:-3], call="Agent tool", description=desc, source=pid, kind="subagent")

    if repo:
        # 3. Repo project skills
        for s in skills_in(os.path.join(repo, ".claude", "skills")):
            add(group="repo", name=s["name"], call="/" + s["name"], description=s["description"], source=os.path.basename(repo) + "/.claude/skills", kind="skill")
        # 4a. Marketplace plugins not installed
        mkt = load_json(os.path.join(repo, ".claude-plugin", "marketplace.json"))
        for p in mkt.get("plugins", []):
            if p.get("name") in seen_plugins:
                continue
            src = p.get("source")
            sk = []
            if isinstance(src, str):
                sk = [s["name"] for s in skills_in(os.path.join(repo, src, "skills"))]
            desc = p.get("description", "")
            if sk:
                desc = (desc + " Skills: " + ", ".join(sk) + ".").strip()
            add(group="available", name=p.get("name", "?"), call=f"enable: add '{p.get('name')}' to agent/plugins.txt", description=desc, source=mkt.get("name", "marketplace"), kind="plugin")
        # 4b. Opt-in skills registry
        for s in skills_in(os.path.join(repo, "skills")):
            add(group="available", name=s["name"], call=f"just marketplace skills add ./skills --skill {s['name']} --global --copy", description=s["description"], source="skills registry", kind="skill")

    # 5. My subagents
    for a in sorted(glob.glob(os.path.join(CLAUDE, "agents", "*.md"))):
        name, desc = frontmatter(a)
        add(group="subagent", name=name or os.path.basename(a)[:-3], call="Agent tool", description=desc, source="dotfiles" if ".agent-setup" in os.path.realpath(a) else "local", kind="subagent")

    fmt = sys.argv[1] if len(sys.argv) > 1 else "--html"
    if fmt == "--json":
        json.dump({"repo": repo, "items": items}, sys.stdout, indent=2)
    elif fmt == "--text":
        for g in GROUPS:
            rows = [i for i in items if i["group"] == g[0]]
            if rows:
                print(f"\n== {g[1]} ({len(rows)})")
                for i in rows:
                    print(f"  {i['name']:<34} {i['description'][:110]}")
    else:
        sys.stdout.write(render_html(items, repo))


GROUPS = [
    ("mine", "My skills", "From your dotfiles. Edit them in agent/claude/skills."),
    ("plugin", "Plugin skills (on)", "From enabled plugins. Call them with the plugin prefix."),
    ("repo", "Repo skills", "Load in every session started inside this checkout."),
    ("subagent", "Subagents", "Helpers a session can hand work to (e.g. the plan reviewer)."),
    ("available", "Available, not turned on", "Add a plugin to agent/plugins.txt, then ws open <box>. Registry skills install with the command shown."),
]


def render_html(items, repo):
    e = html.escape
    host = os.uname().nodename
    sections = []
    for key, title, hint in GROUPS:
        rows = [i for i in items if i["group"] == key]
        if not rows:
            continue
        cards = "".join(
            f'<article data-q="{e((i["name"] + " " + i["description"] + " " + i["source"]).lower())}">'
            f'<header><b>{e(i["name"])}</b><span class="k {e(i["kind"])}">{e(i["kind"])}</span></header>'
            f'<p>{e(i["description"]) or "<i>No description.</i>"}</p>'
            f'<footer><code>{e(i["call"])}</code><span>{e(i["source"])}</span></footer></article>'
            for i in rows
        )
        sections.append(f'<section><h2>{e(title)} <small>{len(rows)}</small></h2><p class="hint">{e(hint)}</p><div class="grid">{cards}</div></section>')
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Skills on {e(host)}</title><style>
:root{{--bg:#fbfaf8;--card:#fff;--ink:#1d1b26;--quiet:#6b6878;--line:#e7e4ee;--accent:#5b3fd1}}
@media (prefers-color-scheme:dark){{:root{{--bg:#15141a;--card:#1f1d26;--ink:#ece9f5;--quiet:#a19db0;--line:#33303d;--accent:#a493ff}}}}
body{{margin:0;background:var(--bg);color:var(--ink);font:14px/1.5 -apple-system,BlinkMacSystemFont,"Inter",sans-serif}}
main{{max-width:1100px;margin:0 auto;padding:24px 16px 64px}} h1{{font-size:22px;margin:0 0 4px}} .sub{{color:var(--quiet);margin:0 0 16px}}
input{{width:100%;box-sizing:border-box;padding:10px 12px;border:1px solid var(--line);border-radius:8px;background:var(--card);color:var(--ink);font-size:15px}}
h2{{font-size:16px;margin:28px 0 2px}} h2 small{{color:var(--quiet);font-weight:400}} .hint{{color:var(--quiet);margin:0 0 10px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:10px}}
article{{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px 14px;display:flex;flex-direction:column;gap:6px}}
article header{{display:flex;justify-content:space-between;gap:8px;align-items:baseline}} article p{{margin:0;color:var(--ink)}}
article footer{{display:flex;justify-content:space-between;gap:8px;color:var(--quiet);font-size:12px;margin-top:auto}}
code{{font:12px ui-monospace,Menlo,monospace;color:var(--accent);word-break:break-all}}
.k{{font-size:11px;border:1px solid var(--line);border-radius:99px;padding:0 8px;color:var(--quiet)}}
</style></head><body><main>
<h1>Skills on {e(host)}</h1><p class="sub">{len(items)} items · repo: {e(repo or "none found")} · type to filter</p>
<input id="q" placeholder="Filter: jira, intake, review, mock…" autofocus>
{"".join(sections)}
</main><script>
document.getElementById('q').addEventListener('input',ev=>{{const q=ev.target.value.toLowerCase().trim();
document.querySelectorAll('article').forEach(a=>a.style.display=!q||a.dataset.q.includes(q)?'':'none');
document.querySelectorAll('section').forEach(s=>s.style.display=[...s.querySelectorAll('article')].some(a=>a.style.display!=='none')?'':'none');}});
</script></body></html>"""


if __name__ == "__main__":
    main()
