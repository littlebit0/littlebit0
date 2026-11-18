import json, subprocess, sys, time, html
from collections import Counter
from datetime import datetime, timedelta, timezone

USER = "littlebit0"
OUT = sys.argv[1] if len(sys.argv) > 1 else "assets/profile.svg"
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

esc = html.escape
W = 900
LANG_COLORS = {"Python": "#3572A5", "JavaScript": "#f1e05a", "TypeScript": "#3178c6", "Dart": "#00B4AB",
               "Swift": "#F05138", "Jupyter Notebook": "#DA5B0B", "Java": "#b07219", "Shell": "#89e051",
               "HTML": "#e34c26", "CSS": "#8957e5", "C": "#9aa4af", "Kotlin": "#A97BFF", "C++": "#f34b7d"}

parts = []
y = 84


def prompt(cmd):
    global y
    parts.append(f'<text x="32" y="{y}" fill="#7ee787">❯</text><text x="56" y="{y}" fill="#f0f6fc">{esc(cmd)}</text>')


def bar_row(label, value, vmax, c1, c2, gid, label_w=170, bar_w=440, text=None):
    global y
    w = max(14, round(bar_w * value / max(vmax, 1)))
    parts.append(f'<text x="32" y="{y+14}" fill="#8b949e">{esc(label)}</text>'
                 f'<rect x="{label_w+40}" y="{y}" width="{bar_w}" height="14" rx="7" fill="#21262d"/>'
                 f'<rect x="{label_w+40}" y="{y}" width="{w}" height="14" rx="7" fill="url(#{gid})"/>'
                 f'<text x="{label_w+40+bar_w+20}" y="{y+14}" fill="#f0f6fc" font-weight="700">{esc(text if text is not None else f"{value:,}")}</text>')
    y += 38


defs = ['<linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0d1117"/><stop offset="1" stop-color="#010409"/></linearGradient>',
        '<linearGradient id="area" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1f6feb" stop-opacity="0.55"/><stop offset="1" stop-color="#1f6feb" stop-opacity="0.02"/></linearGradient>']
grads = {"g1": ("#1f6feb", "#79c0ff"), "g2": ("#238636", "#7ee787"), "g3": ("#8957e5", "#d2a8ff"),
         "g4": ("#bf8700", "#f2cc60"), "g5": ("#da3633", "#ffa198")}
for k, (a, b) in grads.items():
    defs.append(f'<linearGradient id="{k}" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{a}"/><stop offset="1" stop-color="{b}"/></linearGradient>')

# whoami
prompt("whoami"); y += 56
parts.append(f'<text x="56" y="{y}" fill="#58a6ff" font-size="44" font-weight="700">LittleBit0</text>'); y += 48

# motto
prompt("cat motto.txt"); y += 38
parts.append(f'<text x="56" y="{y}" fill="#f0f6fc" font-size="22">Tiny steps, meaningful things.</text>'); y += 30
parts.append(f'<text x="56" y="{y}" fill="#7ee787">"!TinyTinyTiny!"</text>'); y += 48

# focus
prompt("echo $FOCUS"); y += 38
parts.append(f'<text x="56" y="{y}" font-size="19"><tspan fill="#79c0ff">Frontend</tspan><tspan fill="#8b949e"> · </tspan><tspan fill="#7ee787">Backend</tspan><tspan fill="#8b949e"> · </tspan><tspan fill="#d2a8ff">Data</tspan><tspan fill="#8b949e"> · </tspan><tspan fill="#ffa657">Mobile</tspan></text>'); y += 48

# links
prompt("cat links.txt"); y += 34
for name, color, val in [("velog", "#20C997", "velog.io/@littlebit0"),
                         ("disquiet", "#f0f6fc", "disquiet.io/@little_bit"),
                         ("email", "#EA4335", "littlebits12n@gmail.com"),
                         ("portfolio", "#79c0ff", "notion.site/Littlebit")]:
    parts.append(f'<text x="56" y="{y}" fill="{color}" font-weight="700">{name}</text><text x="190" y="{y}" fill="#c9d1d9">{val}</text>')
    y += 30
y += 20

# stack
prompt("ls ~/stack"); y += 24
rows = [("languages", "#79c0ff", False, ["JavaScript", "Python", "C", "HTML", "CSS"]),
        ("frameworks", "#7ee787", False, ["React", "Node.js"]),
        ("data", "#d2a8ff", False, ["Pandas", "NumPy", "Matplotlib"]),
        ("tools", "#ffa657", False, ["Git", "GitHub", "Notion", "VS Code", "Figma"]),
        ("learning", "#f2cc60", True, ["TypeScript", "Java", "Spring", "Flutter"])]
for label, c, dash, items in rows:
    parts.append(f'<text x="32" y="{y+20}" fill="#8b949e">{label}</text>')
    x = 190
    for it in items:
        pw = len(it) * 10.2 + 28
        d = ' stroke-dasharray="5 4"' if dash else ""
        parts.append(f'<rect x="{x:.1f}" y="{y}" width="{pw:.1f}" height="30" rx="15" fill="{c}" fill-opacity="0.12" stroke="{c}" stroke-width="1.5"{d}/>'
                     f'<text x="{x+pw/2:.1f}" y="{y+20}" text-anchor="middle" fill="#f0f6fc" font-size="15">{esc(it)}</text>')
        x += pw + 12
    y += 46
y += 28

# stats
prompt(f"gh stats --user {USER}"); y += 34
vmax = max(commits, issues, prs, stars, contribs)
bar_row("commits", commits, vmax, "", "", "g1")
bar_row("issues", issues, vmax, "", "", "g2")
bar_row("pull requests", prs, vmax, "", "", "g3")
bar_row("stars", stars, vmax, "", "", "g4")
bar_row("contributions", contribs, vmax, "", "", "g5", text=f"{contribs:,}  (1y)")
y += 24

# languages
prompt("gh repo list --by-language"); y += 34
total = sum(n for _, n in langs) or 1
lmax = langs[0][1] if langs else 1
for i, (name, n) in enumerate(langs):
    gid = f"lg{i}"
    c = LANG_COLORS.get(name, "#8b949e")
    defs.append(f'<linearGradient id="{gid}" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{c}" stop-opacity="0.6"/><stop offset="1" stop-color="{c}"/></linearGradient>')
    bar_row(name, n, lmax, "", "", gid, text=f"{n} repo{'s' if n != 1 else ''}  {round(100 * n / total)}%")
y += 24

# contribution flow
prompt("git log --graph --since=30.days"); y += 26
cx0, cx1, ch = 56, 844, 130
vals = [v for _, v in daily]
top = max(max(vals), 1)
for g in range(4):
    gy = y + ch * g / 3
    parts.append(f'<line x1="{cx0}" y1="{gy:.1f}" x2="{cx1}" y2="{gy:.1f}" stroke="#21262d" stroke-width="1"/>')
pts = [(cx0 + (cx1 - cx0) * i / (len(vals) - 1), y + ch - ch * v / top) for i, v in enumerate(vals)]
line = " ".join(f"{px:.1f},{py:.1f}" for px, py in pts)
parts.append(f'<polygon points="{cx0},{y+ch} {line} {cx1},{y+ch}" fill="url(#area)"/>')
parts.append(f'<polyline points="{line}" fill="none" stroke="#58a6ff" stroke-width="2.5" stroke-linejoin="round" stroke-linecap="round"/>')
for (px, py), v in zip(pts, vals):
    if v:
        parts.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="3.2" fill="#0d1117" stroke="#79c0ff" stroke-width="2"/>')
pi = vals.index(max(vals))
parts.append(f'<text x="{min(max(pts[pi][0], 90), 810):.1f}" y="{pts[pi][1]-10:.1f}" text-anchor="middle" fill="#f0f6fc" font-size="13" font-weight="700">{max(vals)}</text>')
y += ch + 24
parts.append(f'<text x="{cx0}" y="{y}" fill="#8b949e" font-size="13">{daily[0][0][5:]}</text>'
             f'<text x="{cx1}" y="{y}" text-anchor="end" fill="#8b949e" font-size="13">{daily[-1][0][5:]}</text>'
             f'<text x="450" y="{y}" text-anchor="middle" fill="#8b949e" font-size="13">{sum(vals):,} in 30 days</text>')
y += 54

# footer
prompt('echo "build small · learn always · ship often"'); y += 44
parts.append(f'<text x="32" y="{y}" fill="#7ee787">❯</text><rect class="cur" x="56" y="{y-15}" width="10" height="18" fill="#58a6ff"/>')
H = y + 28

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<defs>{"".join(defs)}</defs>
<style>@keyframes blink{{0%,49%{{opacity:1}}50%,100%{{opacity:0}}}}.cur{{animation:blink 1.1s step-end infinite}}</style>
<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="14" fill="url(#bg)" stroke="#30363d" stroke-width="2"/>
<path d="M1 15 Q1 1 15 1 H{W-15} Q{W-1} 1 {W-1} 15 V46 H1 Z" fill="#161b22"/>
<line x1="1" y1="46" x2="{W-1}" y2="46" stroke="#30363d" stroke-width="1.5"/>
<circle cx="28" cy="24" r="7" fill="#ff5f56"/><circle cx="52" cy="24" r="7" fill="#ffbd2e"/><circle cx="76" cy="24" r="7" fill="#27c93f"/>
<g font-family="{FONT}" font-size="17">
<text x="{W//2}" y="30" text-anchor="middle" fill="#8b949e" font-size="13">littlebit0 — zsh</text>
{chr(10).join(parts)}
</g></svg>
'''
with open(OUT, "w", encoding="utf-8") as f:
    f.write(svg)
print(commits, issues, prs, stars, contribs, langs, sum(vals))
