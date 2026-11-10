"""Live data: contribution calendar, weather + daylight, repo stars, light-up state. Network failures never fail a build."""
import datetime as dt
import json
import re
import urllib.parse
import urllib.request
from pathlib import Path
from zoneinfo import ZoneInfo

UA = "github-profile-kit"

# name -> (light-mode fill, dark-mode fill)
COLORS = {
    "blue": ("#2563eb", "#60a5fa"),
    "red": ("#dc2626", "#ef4444"),
    "green": ("#16a34a", "#22c55e"),
    "purple": ("#7c3aed", "#8b5cf6"),
    "orange": ("#ea580c", "#f97316"),
    "pink": ("#db2777", "#ec4899"),
    "gold": ("#ca8a04", "#eab308"),
}
LOGIN_RE = re.compile(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})")


def http_json(url, data=None, headers=None):
    req = urllib.request.Request(url, data=data, headers={"User-Agent": UA, **(headers or {})})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode())


def fetch_calendar(user, token):
    q = ('query($u:String!){user(login:$u){contributionsCollection{contributionCalendar{'
         'weeks{contributionDays{date contributionCount}}}}}}')
    res = http_json("https://api.github.com/graphql",
                    data=json.dumps({"query": q, "variables": {"u": user}}).encode(),
                    headers={"Authorization": f"bearer {token}", "Content-Type": "application/json"})
    weeks = res["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
    return [(d["date"], d["contributionCount"]) for w in weeks for d in w["contributionDays"]]


def wmo_to_weather(code):
    if code in (0, 1):
        return "clear"
    if code == 2:
        return "partly"
    if code == 3:
        return "cloudy"
    if code in (45, 48):
        return "fog"
    if code in (71, 73, 75, 77, 85, 86):
        return "snow"
    if code in (95, 96, 99):
        return "storm"
    return "rain"


def fetch_weather(city):
    """phase (day/dusk/night from real sunrise/sunset at the city), weather and temperature via Open-Meteo."""
    tz = city.get("timezone", "UTC")
    u = (f"https://api.open-meteo.com/v1/forecast?latitude={city['lat']}&longitude={city['lon']}"
         f"&current=weather_code,temperature_2m&daily=sunrise,sunset&timezone={urllib.parse.quote(tz, safe='')}&forecast_days=1")
    w = http_json(u)
    now = dt.datetime.now(ZoneInfo(tz)).replace(tzinfo=None)
    rise = dt.datetime.fromisoformat(w["daily"]["sunrise"][0])
    sset = dt.datetime.fromisoformat(w["daily"]["sunset"][0])
    half = dt.timedelta(minutes=30)  # ~civil twilight
    if rise - half <= now <= rise + half or sset - half <= now <= sset + half:
        phase = "dusk"
    elif rise < now < sset:
        phase = "day"
    else:
        phase = "night"
    return dict(phase=phase, weather=wmo_to_weather(w["current"]["weather_code"]), temp=w["current"]["temperature_2m"])


def enrich_repos(recs, token=None):
    """Adds stars, language and description to each recommendation (in place). Returns notes for failures."""
    headers = {"Authorization": f"bearer {token}"} if token else {}
    notes = []
    for p in recs:
        try:
            r = http_json(f"https://api.github.com/repos/{p['repo']}", headers=headers)
            p.update(stars=r["stargazers_count"], lang=r.get("language"), description=r.get("description") or "")
        except Exception as e:  # keep what we have
            notes.append(f"repo info unavailable for {p['repo']}: {e}")
    return notes


def load_lightup(root):
    p = Path(root) / "state" / "lightup.json"
    try:
        s = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {"color": None, "user": None}
    if s.get("color") not in COLORS:
        s["color"] = None
    if s.get("user") and not LOGIN_RE.fullmatch(str(s["user"])):
        s["user"] = None
    return s


def apply_lightup(root, title, user):
    """Handle a light-up issue. title/user come from env vars of the issue event, never from a shell."""
    m = re.fullmatch(r"\s*light:\s*([a-z]+)\s*", (title or "").lower())
    color = m.group(1) if m else ""
    if color not in COLORS or not LOGIN_RE.fullmatch(user or ""):
        return None
    p = Path(root) / "state" / "lightup.json"
    p.parent.mkdir(exist_ok=True)
    p.write_text(json.dumps({"color": color, "user": user,
                             "at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")}, indent=2) + "\n",
                 encoding="utf-8")
    return color
