import json, subprocess, sys, time, html
from collections import Counter
from datetime import datetime, timedelta, timezone

USER = "littlebit0"
ROOT = sys.argv[1] if len(sys.argv) > 1 else "."
FONT = "SF Mono, Menlo, Consolas, DejaVu Sans Mono, monospace"


def gh(*args):
    for attempt in range(4):
        r = subprocess.run(["gh", "api", *args], capture_output=True, text=True)
        if r.returncode == 0:
            return json.loads(r.stdout)
        time.sleep(8 * (attempt + 1))
    raise RuntimeError(r.stderr.strip() or "gh api failed")


def search_count(kind, q):
    time.sleep(0.4)
    return gh(f"search/{kind}?q={q}&per_page=1")["total_count"]


today = datetime.now(timezone.utc).date()
year_ago = today - timedelta(days=365)
start30 = today - timedelta(days=29)

commits = search_count("commits", f"author:{USER}")
issues = search_count("issues", f"author:{USER}+type:issue")
prs = search_count("issues", f"author:{USER}+type:pr")

repos = [r for r in gh(f"search/repositories?q=user:{USER}&per_page=100")["items"]
         if not r["private"] and not r["fork"]]
stars = sum(r["stargazers_count"] for r in repos)
langs = Counter(r["language"] for r in repos if r["language"]).most_common(6)

contribs = None
daily = None
try:
    q = ('query($u:String!){user(login:$u){contributionsCollection{contributionCalendar'
         '{totalContributions weeks{contributionDays{date contributionCount}}}}}}')
    cal = gh("graphql", "-f", f"query={q}", "-f", f"u={USER}")["data"]["user"][
        "contributionsCollection"]["contributionCalendar"]
    days = [d for w in cal["weeks"] for d in w["contributionDays"]]
    days = [d for d in days if d["date"] <= today.isoformat()][-30:]
    contribs = cal["totalContributions"]
    daily = [(d["date"], d["contributionCount"]) for d in days]
except Exception:
    pass
if contribs is None or not daily or len(daily) < 30:
    daily = []
    for i in range(30):
        d = start30 + timedelta(days=i)
        daily.append((d.isoformat(), search_count("commits", f"author:{USER}+author-date:{d.isoformat()}")))
    since = year_ago.isoformat()
    contribs = (search_count("commits", f"author:{USER}+author-date:>={since}")
                + search_count("issues", f"author:{USER}+type:issue+created:>={since}")
                + search_count("issues", f"author:{USER}+type:pr+created:>={since}"))

import os, shutil

esc = html.escape
W = 860
LANG_COLORS = {"Python": "#3572A5", "JavaScript": "#f1e05a", "TypeScript": "#3178c6", "Dart": "#00B4AB",
               "Swift": "#F05138", "Jupyter Notebook": "#DA5B0B", "Java": "#b07219", "Shell": "#89e051",
               "HTML": "#e34c26", "CSS": "#8957e5", "C": "#9aa4af", "Kotlin": "#A97BFF", "C++": "#f34b7d"}
GRADS = {"g1": ("#1f6feb", "#79c0ff"), "g2": ("#238636", "#7ee787"), "g3": ("#8957e5", "#d2a8ff"),
         "g4": ("#bf8700", "#f2cc60"), "g5": ("#da3633", "#ffa198")}


def grad(gid, a, b, ao=1, bo=1):
    return (f'<linearGradient id="{gid}" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{a}" stop-opacity="{ao}"/>'
            f'<stop offset="1" stop-color="{b}" stop-opacity="{bo}"/></linearGradient>')


rows = []


def add_row(h, items):
    rows.append({"h": h, "items": items})


def full(h, body, defs="", link=None, alt=""):
    add_row(h, [{"x": 0, "w": W, "body": body, "defs": defs, "link": link, "alt": alt}])


def gap(h=24):
    full(h, "")


def prompt_row(cmd):
    full(34, f'<text x="32" y="22" fill="#7ee787">❯</text><text x="56" y="22" fill="#f0f6fc">{esc(cmd)}</text>', alt=cmd)


# title bar
full(46, f'<rect x="0" y="0" width="{W}" height="46" fill="#161b22"/><line x1="0" y1="46" x2="{W}" y2="46" stroke="#30363d" stroke-width="1.5"/>'
         '<circle cx="28" cy="24" r="7" fill="#ff5f56"/><circle cx="52" cy="24" r="7" fill="#ffbd2e"/><circle cx="76" cy="24" r="7" fill="#27c93f"/>'
         f'<text x="{W//2}" y="30" text-anchor="middle" fill="#8b949e" font-size="13">littlebit0 — zsh</text>', alt="terminal window")
gap(24)
prompt_row("whoami")
full(58, '<text x="56" y="44" fill="#58a6ff" font-size="44" font-weight="700">LittleBit0</text>', alt="LittleBit0")
gap()
prompt_row("cat motto.txt")
full(40, '<text x="56" y="26" fill="#f0f6fc" font-size="22">Tiny steps, meaningful things.</text>', alt="Tiny steps, meaningful things.")
full(30, '<text x="56" y="20" fill="#7ee787">"!TinyTinyTiny!"</text>', alt="TinyTinyTiny")
gap()
prompt_row("echo $FOCUS")
full(40, '<text x="56" y="26" font-size="19"><tspan fill="#79c0ff">Frontend</tspan><tspan fill="#8b949e"> · </tspan><tspan fill="#7ee787">Backend</tspan>'
         '<tspan fill="#8b949e"> · </tspan><tspan fill="#d2a8ff">Data</tspan><tspan fill="#8b949e"> · </tspan><tspan fill="#ffa657">Mobile</tspan></text>',
     alt="Frontend · Backend · Data · Mobile")
gap()
prompt_row("cat links.txt")
for name, color, val, href in [("velog", "#20C997", "velog.io/@littlebit0", "https://velog.io/@littlebit0/"),
                               ("disquiet", "#f0f6fc", "disquiet.io/@little_bit", "https://disquiet.io/@little_bit"),
                               ("email", "#EA4335", "littlebits12n@gmail.com", "mailto:littlebits12n@gmail.com"),
                               ("portfolio", "#79c0ff", "notion.site/Littlebit", "https://speckled-meeting-8f9.notion.site/Littlebit-2fbe3d635bfc80cf812df966ab82974f?source=copy_link")]:
    full(30, f'<text x="56" y="20" fill="{color}" font-weight="700">{name}</text><text x="190" y="20" fill="#c9d1d9">{val}</text>',
         link=href, alt=f"{name} {val}")
gap()

# stack
prompt_row("ls ~/stack")
stack = [("languages", "#79c0ff", False, ["JavaScript", "Python", "C", "HTML", "CSS", "Java", "Swift", "Kotlin", "Flutter"]),
         ("frameworks", "#7ee787", False, ["React", "Node.js"]),
         ("data", "#d2a8ff", False, ["Pandas", "NumPy", "Matplotlib"]),
         ("tools", "#ffa657", False, ["Git", "GitHub", "Notion", "VS Code", "Xcode", "Figma"]),
         ("learning", "#f2cc60", True, ["TypeScript", "Spring"])]
LABEL_W = 190
for label, c, dash, names in stack:
    lines, cur, cx = [], [], LABEL_W
    for n in names:
        iw = int(len(n) * 10.2 + 28) + 12
        if cx + iw > W - 24 and cur:
            lines.append(cur); cur, cx = [], LABEL_W
        cur.append((n, iw)); cx += iw
    lines.append(cur)
    for li, line in enumerate(lines):
        its = [{"x": 0, "w": LABEL_W, "alt": label if li == 0 else "", "defs": "",
                "body": f'<text x="32" y="26" fill="#8b949e">{label}</text>' if li == 0 else "", "link": None}]
        x = LABEL_W
        for n, iw in line:
            pw = iw - 12
            d = ' stroke-dasharray="5 4"' if dash else ""
            its.append({"x": x, "w": iw, "alt": n, "defs": "", "link": None,
                        "body": f'<rect x="{x+0.75}" y="6.75" width="{pw-1.5}" height="28.5" rx="14.25" fill="{c}" fill-opacity="0.12" stroke="{c}" stroke-width="1.5"{d}/>'
                                f'<text x="{x+pw/2:.1f}" y="26" text-anchor="middle" fill="#f0f6fc" font-size="15">{esc(n)}</text>'})
            x += iw
        its.append({"x": x, "w": W - x, "alt": "", "defs": "", "body": "", "link": None})
        add_row(42, its)
gap()

# bars
BX, BW = 210, 400


def bar_row(label, value, vmax, gid, defs, text):
    w = max(14, round(BW * value / max(vmax, 1)))
    full(34, f'<text x="32" y="24" fill="#8b949e">{esc(label)}</text>'
             f'<rect x="{BX}" y="10" width="{BW}" height="14" rx="7" fill="#21262d"/>'
             f'<rect x="{BX}" y="10" width="{w}" height="14" rx="7" fill="url(#{gid})"/>'
             f'<text x="{BX+BW+20}" y="24" fill="#f0f6fc" font-weight="700">{esc(text)}</text>',
         defs=defs, alt=f"{label} {text}")


prompt_row(f"gh stats --user {USER}")
vmax = max(commits, issues, prs, stars, contribs)
for label, v, gid, txt in [("commits", commits, "g1", f"{commits:,}"), ("issues", issues, "g2", f"{issues:,}"),
                           ("pull requests", prs, "g3", f"{prs:,}"), ("stars", stars, "g4", f"{stars:,}"),
                           ("contributions", contribs, "g5", f"{contribs:,}  (1y)")]:
    bar_row(label, v, vmax, gid, grad(gid, *GRADS[gid]), txt)
gap()

prompt_row("gh repo list --by-language")
total = sum(n for _, n in langs) or 1
lmax = langs[0][1] if langs else 1
for i, (name, n) in enumerate(langs):
    c = LANG_COLORS.get(name, "#8b949e")
    bar_row(name, n, lmax, "lg", grad("lg", c, c, 0.6, 1), f"{n} repo{'s' if n != 1 else ''}  {round(100 * n / total)}%")
gap()

# flow
prompt_row("git log --graph --since=30.days")
cx0, cx1, ch, top0 = 56, W - 56, 130, 16
vals = [v for _, v in daily]
vtop = max(max(vals), 1)
b = ""
for g in range(4):
    gy = top0 + ch * g / 3
    b += f'<line x1="{cx0}" y1="{gy:.1f}" x2="{cx1}" y2="{gy:.1f}" stroke="#21262d" stroke-width="1"/>'
pts = [(cx0 + (cx1 - cx0) * i / (len(vals) - 1), top0 + ch - ch * v / vtop) for i, v in enumerate(vals)]
line = " ".join(f"{px:.1f},{py:.1f}" for px, py in pts)
b += f'<polygon points="{cx0},{top0+ch} {line} {cx1},{top0+ch}" fill="url(#area)"/>'
b += f'<polyline points="{line}" fill="none" stroke="#58a6ff" stroke-width="2.5" stroke-linejoin="round" stroke-linecap="round"/>'
for (px, py), v in zip(pts, vals):
    if v:
        b += f'<circle cx="{px:.1f}" cy="{py:.1f}" r="3.2" fill="#0d1117" stroke="#79c0ff" stroke-width="2"/>'
pi = vals.index(max(vals))
b += f'<text x="{min(max(pts[pi][0], 90), W-90):.1f}" y="{max(pts[pi][1]-10, 12):.1f}" text-anchor="middle" fill="#f0f6fc" font-size="13" font-weight="700">{max(vals)}</text>'
ay = top0 + ch + 28
b += (f'<text x="{cx0}" y="{ay}" fill="#8b949e" font-size="13">{daily[0][0][5:]}</text>'
      f'<text x="{cx1}" y="{ay}" text-anchor="end" fill="#8b949e" font-size="13">{daily[-1][0][5:]}</text>'
      f'<text x="{W//2}" y="{ay}" text-anchor="middle" fill="#8b949e" font-size="13">{sum(vals):,} in 30 days</text>')
full(ay + 12, b, defs='<linearGradient id="area" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1f6feb" stop-opacity="0.55"/>'
                      '<stop offset="1" stop-color="#1f6feb" stop-opacity="0.02"/></linearGradient>', alt="contribution flow, last 30 days")
gap()

prompt_row('echo "build small · learn always · ship often"')
full(40, '<text x="32" y="26" fill="#7ee787">❯</text><rect class="cur" x="56" y="11" width="10" height="18" fill="#58a6ff"/>', alt="")
gap(26)

H = sum(r["h"] for r in rows)
outdir = os.path.join(ROOT, "assets", "p")
shutil.rmtree(outdir, ignore_errors=True)
os.makedirs(outdir)
STYLE = '<style>@keyframes blink{0%,49%{opacity:1}50%,100%{opacity:0}}.cur{animation:blink 1.1s step-end infinite}</style>'
yoff = 0
lines = []
n = 0
for r in rows:
    h = r["h"]
    parts = []
    for it in r["items"]:
        x, w = it["x"], it["w"]
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="{x} 0 {w} {h}">'
               f'<defs><linearGradient id="bg" gradientUnits="userSpaceOnUse" x1="0" y1="{-yoff}" x2="0" y2="{H-yoff}">'
               f'<stop offset="0" stop-color="#0d1117"/><stop offset="1" stop-color="#010409"/></linearGradient>'
               f'<clipPath id="win"><rect x="0" y="{-yoff}" width="{W}" height="{H}" rx="14"/></clipPath>{it["defs"]}</defs>{STYLE}'
               f'<g clip-path="url(#win)"><rect x="{x}" y="0" width="{w}" height="{h}" fill="url(#bg)"/>'
               f'<g font-family="{FONT}" font-size="17">{it["body"]}</g></g>'
               f'<rect x="1" y="{-yoff+1}" width="{W-2}" height="{H-2}" rx="14" fill="none" stroke="#30363d" stroke-width="2"/></svg>')
        name = f"{n:03d}.svg"
        n += 1
        with open(os.path.join(outdir, name), "w", encoding="utf-8") as f:
            f.write(svg)
        tag = f'<img align="top" src="assets/p/{name}" width="{w}" height="{h}" alt="{esc(it["alt"], quote=True)}">'
        if it["link"]:
            tag = f'<a href="{esc(it["link"], quote=True)}">{tag}</a>'
        parts.append(tag)
    lines.append("".join(parts))
    yoff += h

with open(os.path.join(ROOT, "README.md"), "w", encoding="utf-8") as f:
    f.write('<div align="center">\n\n' + "\n".join(lines) + "\n\n</div>\n")
print(commits, issues, prs, stars, contribs, "pieces:", n, "H:", H)
