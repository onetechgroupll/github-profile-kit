"""Render all graphics and the README from a validated config."""
import datetime as dt
import os
import random
import urllib.parse
from pathlib import Path
from zoneinfo import ZoneInfo

from . import live, sections, skyline
from .core import theme

MODES = ("light", "dark")
CUSTOM_START, CUSTOM_END = "<!-- CUSTOM:START -->", "<!-- CUSTOM:END -->"
KIT_URL = "https://github.com/onetechgroupll/github-profile-kit"


def sample_days(seed="kit"):
    """Plausible contribution calendar for offline previews."""
    rng = random.Random(seed)
    today = dt.date.today()
    start = today - dt.timedelta(days=364 + (today.weekday() + 1) % 7)
    days = []
    for i in range((today - start).days + 1):
        d = start + dt.timedelta(days=i)
        busy = d.weekday() < 5
        days.append((d.isoformat(), rng.choice([0, 0, 2, 5, 9, 14, 22]) if busy else rng.choice([0, 0, 0, 3, 6])))
    return days


def render(cfg, root, offline=False, phase=None, weather=None, season=None):
    """Write assets/ (static), dist/ (live) and README.md. Returns a summary dict."""
    root = Path(root)
    assets, dist = root / "assets", root / "dist"
    assets.mkdir(exist_ok=True)
    dist.mkdir(exist_ok=True)
    written, notes = [], []
    pr = cfg["profile"]
    sec = cfg["sections"]

    def write(folder, name, content):
        p = folder / name
        p.write_text(content, encoding="utf-8")
        written.append(str(p.relative_to(root)))

    T = {m: theme(pr["theme"], m, pr.get("accent")) for m in MODES}
    token = os.environ.get("GITHUB_TOKEN")

    # ---- static graphics
    for m, t in T.items():
        if "header" in sec:
            write(assets, f"header-{m}.svg", sections.header(t, pr, cfg.get("hub")))
        if "focus" in sec and cfg.get("focus"):
            write(assets, f"focus-{m}.svg", sections.focus(t, cfg["focus"]))
        if "terminal" in sec and cfg.get("terminal"):
            write(assets, f"terminal-{m}.svg", sections.terminal(t, cfg["terminal"], pr["handle"]))
        if "org" in sec and cfg.get("org"):
            write(assets, f"org-{m}.svg", sections.org_card(t, cfg["org"]))
        if "contact" in sec:
            for i, ln in enumerate(cfg.get("links", [])):
                write(assets, f"btn-{i}-{m}.svg", sections.button(t, ln["label"], ln.get("icon", "web")))
            if cfg.get("status"):
                write(assets, f"status-{m}.svg", sections.status_pills(t, cfg["status"]))
        if cfg.get("lightup", {}).get("enabled") and cfg.get("city"):
            for name, (lf, df) in live.COLORS.items():
                write(assets, f"light-{name}-{m}.svg", sections.color_chip(t, name, lf if m == "light" else df))
        if cfg.get("city"):
            write(assets, f"avatar-{m}.svg", skyline.scene(t, m, cfg["city"], crop=skyline.AVATAR_CROP, label=False))

    # ---- live graphics
    days = None
    if "contributions" in sec and cfg.get("contributions"):
        if offline or not token:
            days = sample_days(pr["handle"])
            notes.append("contributions: sample data (offline or no GITHUB_TOKEN)")
        else:
            try:
                days = live.fetch_calendar(pr["handle"], token)
            except Exception as e:
                days = sample_days(pr["handle"])
                notes.append(f"contributions: sample data ({e})")
    recs = [dict(r) for r in cfg.get("recommend", [])]
    if recs and "recommend" in sec and not offline:
        notes += live.enrich_repos(recs, token)
    wx = dict(phase="day", weather="clear", temp=None, season=None)
    city = cfg.get("city")
    if city and "city" in sec:
        if not offline:
            try:
                wx.update(live.fetch_weather(city))
            except Exception as e:
                notes.append(f"weather: fallback to day/clear ({e})")
        now = dt.datetime.now(ZoneInfo(city.get("timezone", "UTC")))
        wx["season"] = skyline.season_for(now, city.get("seasons", []))
    wx.update({k: v for k, v in dict(phase=phase, weather=weather, season=season).items() if v})
    lu = live.load_lightup(root) if cfg.get("lightup", {}).get("enabled") else {"color": None, "user": None}

    for m, t in T.items():
        if days is not None:
            if cfg["contributions"].get("stats", True):
                write(dist, f"stats-{m}.svg", sections.stats(t, sections.calendar_stats(days)))
            if cfg["contributions"].get("settle", True):
                write(dist, f"settle-{m}.svg", sections.settle(t, m, days))
        for p in recs:
            write(dist, f"rec-{p['repo'].replace('/', '--')}-{m}.svg", sections.rec_card(t, p))
        if city and "city" in sec:
            pod = live.COLORS[lu["color"]][0 if m == "light" else 1] if lu.get("color") else None
            write(dist, f"skyline-{m}.svg", skyline.scene(t, m, city, phase=wx["phase"], weather=wx["weather"],
                                                          temp=wx["temp"], season=wx["season"], beacon=pod,
                                                          lit_by=lu.get("user")))
    readme = root / "README.md"
    readme.write_text(render_readme(cfg, readme.read_text(encoding="utf-8") if readme.exists() else ""), encoding="utf-8")
    written.append("README.md")
    return dict(written=written, notes=notes, weather=wx, lightup=lu)


# ---------------------------------------------------------------- README
def _pic(src_light, src_dark, alt, width="100%", height=None):
    size = f'height="{height}"' if height else f'width="{width}"'
    alt = alt.replace('"', "&quot;")
    return (f'<picture><source media="(prefers-color-scheme: dark)" srcset="{src_dark}">'
            f'<img alt="{alt}" src="{src_light}" {size}></picture>')


def render_readme(cfg, previous=""):
    pr = cfg["profile"]
    repo = pr["repo"]
    raw = f"https://raw.githubusercontent.com/{repo}/output"
    A = "./assets"
    out = ["<!-- Generated by github-profile-kit. Edit profile.toml and rebuild; only the CUSTOM block below is kept. -->", ""]
    words = ", ".join(w.rstrip(".") for w in pr.get("words", []))
    for s in cfg["sections"]:
        if s == "header":
            out += [_pic(f"{A}/header-light.svg", f"{A}/header-dark.svg",
                         f"{pr['name']}. {pr.get('kicker', '')}. {pr['build_prefix']} {words}."), ""]
        elif s == "contact" and (cfg.get("links") or cfg.get("status")):
            row = ['<p align="center">']
            for i, ln in enumerate(cfg.get("links", [])):
                row.append(f'  <a href="{ln["url"]}">{_pic(f"{A}/btn-{i}-light.svg", f"{A}/btn-{i}-dark.svg", ln["label"], height=40)}</a>')
            if cfg.get("status"):
                st = cfg["status"]
                alt = ". ".join(x for x in (f"Based in {st['based_in']}" if st.get("based_in") else "",
                                            f"Open to {st['open_to']}" if st.get("open_to") else "") if x)
                row.append(f'  {_pic(f"{A}/status-light.svg", f"{A}/status-dark.svg", alt, height=32)}')
            out += row + ["</p>", ""]
        elif s == "focus" and cfg.get("focus"):
            alt = "; ".join(f'{c["title"]}: {c.get("line1", "")} {c.get("line2", "")}'.strip() for c in cfg["focus"])
            out += ["### What I build", "", _pic(f"{A}/focus-light.svg", f"{A}/focus-dark.svg", alt), ""]
        elif s == "org" and cfg.get("org"):
            o = cfg["org"]
            out += [f'<a href="{o["url"]}">{_pic(f"{A}/org-light.svg", f"{A}/org-dark.svg", f"{o["kicker"].capitalize()} {o["name"]}. {o.get("tagline", "")}")}</a>', ""]
        elif s == "terminal" and cfg.get("terminal"):
            tm = cfg["terminal"]
            alt = "Terminal: " + "; ".join([tm.get("whoami", "")] + [f["text"] for f in tm.get("flags", [])] + tm.get("principles", []))
            out += ["### How I work", "", _pic(f"{A}/terminal-light.svg", f"{A}/terminal-dark.svg", alt), ""]
        elif s == "recommend" and cfg.get("recommend"):
            cards = []
            for p in cfg["recommend"]:
                slug = p["repo"].replace("/", "--")
                alt = f'{p["repo"]}: {p.get("line1", "")} {p.get("line2", "")}'.strip()
                cards.append(f'<a href="https://github.com/{p["repo"]}">{_pic(f"{raw}/rec-{slug}-light.svg", f"{raw}/rec-{slug}-dark.svg", alt, width="49%")}</a>')
            out += ["### Projects I recommend", "", "<p>", *cards, "</p>", ""]
        elif s == "contributions" and cfg.get("contributions"):
            out += ["### Contributions", ""]
            if cfg["contributions"].get("stats", True):
                out += [_pic(f"{raw}/stats-light.svg", f"{raw}/stats-dark.svg", "Contribution stats for the last 12 months, updated every 15 minutes."), ""]
            if cfg["contributions"].get("settle", True):
                out += [_pic(f"{raw}/settle-light.svg", f"{raw}/settle-dark.svg",
                             "Contribution calendar of the last 12 months; it settles into weekly bars of active days and rebuilds."), ""]
        elif s == "city" and cfg.get("city"):
            c = cfg["city"]
            out += [f"### {c['heading']}", "",
                    _pic(f"{raw}/skyline-light.svg", f"{raw}/skyline-dark.svg",
                         f"Living skyline of {c['name']}: time of day and weather are live."), ""]
        elif s == "lightup" and cfg.get("lightup", {}).get("enabled") and cfg.get("city"):
            body = urllib.parse.quote(f"Just submit this issue: the skyline on @{pr['handle']}'s profile lights up in your colour "
                                      "within a few minutes, with your handle next to it. A bot closes the issue right away.")
            chips = [f'<a href="https://github.com/{repo}/issues/new?title=light%3A%20{n}&body={body}">'
                     f'{_pic(f"{A}/light-{n}-light.svg", f"{A}/light-{n}-dark.svg", f"Light it up in {n}", height=30)}</a>'
                     for n in live.COLORS]
            out += [f'<p align="center"><sub><b>{cfg["lightup"]["title"]}</b> · pick a colour, open the issue, '
                    "and the skyline lights up with your handle.</sub></p>", "", '<p align="center">', *chips, "</p>", ""]
    custom = ""
    if CUSTOM_START in previous and CUSTOM_END in previous:
        custom = previous[previous.index(CUSTOM_START) + len(CUSTOM_START):previous.index(CUSTOM_END)]
    out += [CUSTOM_START, custom.strip("\n") if custom.strip() else "", CUSTOM_END, ""]
    if pr.get("credit", True):
        out += [f'<p align="right"><sub>Built with <a href="{KIT_URL}">github-profile-kit</a></sub></p>', ""]
    return "\n".join(out)
