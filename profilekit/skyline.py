"""The living skyline: sky, weather, seasons, river and a city layer (procedural or a hand-drawn preset)."""
import datetime as dt
import math
import random

from .core import BASE_CSS, LIGHT_ON, NIGHT, SIGNAL_RED, esc, font_css, svg

W, H, G = 1200, 400, 300  # canvas and promenade / waterline

WEATHER_LABEL = {"clear": "clear", "partly": "partly cloudy", "cloudy": "cloudy", "fog": "fog",
                 "rain": "rain", "snow": "snow", "storm": "thunderstorm"}
SEASON_LABEL = {"hoppeditz": "11.11. Helau!", "karneval": "Helau!", "advent": "Advent",
                "christmas": "Merry Christmas", "newyear": "Happy New Year!"}
CONFETTI = ["#dc2626", "#2563eb", "#e0a106", "#16a34a", "#b6358f", "#529abd"]

CSS = """
@keyframes waves{from{transform:translateX(0)}to{transform:translateX(-48px)}}
.wave{animation:waves 4s linear infinite}.wave2{animation-duration:6s}
@keyframes glow{0%,100%{opacity:.35}50%{opacity:.8}}
.glow{animation:glow 3s ease-in-out infinite}
@keyframes flick{0%,92%,100%{opacity:1}94%{opacity:.35}96%{opacity:1}97%{opacity:.5}}
.sign{animation:flick 7s steps(1) infinite}
@keyframes win{0%,100%{opacity:0}40%,70%{opacity:1}}
.win{opacity:0;animation:win 9s ease-in-out infinite}
@keyframes beacon{0%,60%,100%{opacity:.15}70%,85%{opacity:1}}
.beacon{animation:beacon 2s steps(1) infinite}
@keyframes drift{from{transform:translateX(-260px)}to{transform:translateX(1460px)}}
.cloud{animation:drift linear infinite}
@keyframes twinkle{0%,100%{opacity:.25}50%{opacity:1}}
.star{animation:twinkle 3s ease-in-out infinite}
@keyframes fogmove{0%,100%{transform:translateX(-40px)}50%{transform:translateX(40px)}}
.fog{animation:fogmove 18s ease-in-out infinite}
@keyframes flash{0%,88%,92%,96%,100%{opacity:0}89%,94%{opacity:.55}}
.flash{opacity:0;animation:flash 9s steps(1) infinite}
@keyframes bulb{0%,100%{opacity:.25}50%{opacity:1}}.bulb{animation:bulb 1.6s ease-in-out infinite}
@keyframes burst{0%{transform:scale(.15);opacity:0}10%{opacity:1}70%{opacity:.9}100%{transform:scale(1);opacity:0}}
.burst{transform-box:fill-box;transform-origin:center;animation:burst 2.6s ease-out infinite}
"""


class Ctx:
    """Drawing context shared by the city layers: g = normal layer, L = lights above the night overlay."""

    def __init__(self, t, mode, phase):
        self.t, self.mode = t, mode
        self.st = t["line"]
        self.on = LIGHT_ON[mode]
        self.night, self.dusk = phase == "night", phase == "dusk"
        self.g, self.L = [], []

    def bldg(self, pts, fill=None, stroke=None):
        d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts) + " Z"
        return (f'<path d="{d}" fill="{fill or self.t["card"]}" stroke="{stroke or self.st}" '
                f'stroke-width="1.5" stroke-linejoin="round"/>')

    def windows(self, x0, y0, cols, rows, dx, dy, w=4, h=3, seed=0):
        out = []
        for r in range(int(rows)):
            for c in range(int(cols)):
                x, y = x0 + c * dx, y0 + r * dy
                out.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w}" height="{h}" fill="{self.t["border"]}"/>')
                k = (r * 7 + c * 13 + seed) % 23
                if k in ((0, 5, 9, 14, 18) if self.night else (0, 9, 14) if self.dusk else (0, 5)):
                    cls = "" if self.night and k in (9, 14) else "win"
                    self.L.append(f'<rect class="{cls}" style="animation-delay:{(k + r + c) % 9}s" x="{x:.1f}" y="{y:.1f}" '
                                  f'width="{w}" height="{h}" fill="{self.on}"/>')
        return "".join(out)


# ======================================================================== shared landmarks
def sign_tower(c, sx0, text, beacon=None):
    """Rhomboid glass tower with a glowing rooftop sign. Returns the sign's (x, y)."""
    t = c.t
    sx1, sxt0, sxt1, stop = sx0 + 48, sx0 + 20, sx0 + 68, 150
    c.g.append(c.bldg([(sx0, G), (sx1, G), (sxt1, stop), (sxt0, stop)], fill=t["primary_light"], stroke=t["primary"]))
    for k in range(1, 8):
        y = stop + k * (G - stop) / 8
        f = (y - stop) / (G - stop)
        xa, xb = sxt0 + (sx0 - sxt0) * f, sxt1 + (sx1 - sxt1) * f
        c.g.append(f'<line x1="{xa:.1f}" y1="{y:.1f}" x2="{xb:.1f}" y2="{y:.1f}" stroke="{t["primary"]}" stroke-width=".8" opacity=".45"/>')
    c.g.append(f'<line x1="{sxt0}" y1="{stop}" x2="{sx1}" y2="{G}" stroke="{t["primary"]}" stroke-width=".8" opacity=".45"/>'
               f'<line x1="{sxt1}" y1="{stop}" x2="{sx0}" y2="{G}" stroke="{t["primary"]}" stroke-width=".8" opacity=".45"/>')
    bw = 40 if len(text) <= 2 else 52
    bx, by = sxt0 + 24 - bw / 2, stop - 30
    c.g.append(f'<line x1="{bx+8}" y1="{stop}" x2="{bx+8}" y2="{by+22}" stroke="{c.st}" stroke-width="1.5"/>'
               f'<line x1="{bx+bw-8}" y1="{stop}" x2="{bx+bw-8}" y2="{by+22}" stroke="{c.st}" stroke-width="1.5"/>')
    fill = beacon or t["primary"]
    c.L.append(f'<rect class="glow" x="{bx-4}" y="{by-4}" width="{bw+8}" height="30" rx="6" fill="{fill}" opacity=".35"/>'
               f'<rect x="{bx}" y="{by}" width="{bw}" height="22" rx="4" fill="{fill}"/>'
               f'<text class="mono sign" x="{bx+bw/2}" y="{by+16.5}" text-anchor="middle" font-size="16" '
               f'font-weight="700" letter-spacing="1" fill="{t["on_primary"] if not beacon else "#ffffff"}">{esc(text)}</text>')
    return bx + bw / 2, by


def tv_tower(c, rx, pod, lit_by, label):
    """Telecom tower with a pod (the light-up target) and aircraft warning lights."""
    t = c.t
    c.g.append(c.bldg([(rx - 13, G), (rx + 13, G), (rx + 6, 92), (rx - 6, 92)]))
    pod_fill = pod or t["primary"]
    if c.night or c.dusk or pod:
        c.L.append(f'<rect class="glow" x="{rx-30}" y="73" width="60" height="24" rx="10" fill="{pod_fill}" opacity=".35"/>')
    c.g.append(f'<rect x="{rx-24}" y="78" width="48" height="14" rx="6" fill="{pod_fill}"/>'
               f'<rect x="{rx-20}" y="81.5" width="40" height="4" rx="2" fill="{t["primary_light"]}" opacity=".9"/>'
               f'<rect x="{rx-18}" y="68" width="36" height="10" rx="4" fill="{t["card"]}" stroke="{c.st}" stroke-width="1.5"/>'
               f'<rect x="{rx-11}" y="61" width="22" height="7" rx="3" fill="{t["card"]}" stroke="{c.st}" stroke-width="1.5"/>'
               f'<line x1="{rx}" y1="61" x2="{rx}" y2="18" stroke="{c.st}" stroke-width="2"/>'
               f'<line x1="{rx}" y1="38" x2="{rx}" y2="18" stroke="{t["muted"]}" stroke-width="1"/>')
    if lit_by and label:
        c.g.append(f'<path d="M{rx+26},85 H{rx+40}" stroke="{t["muted"]}" stroke-width=".8"/>'
                   f'<text class="mono" x="{rx+44}" y="88.5" font-size="9.5" fill="{t["muted"]}">lit by @{esc(lit_by)}</text>')
    c.L.append(f'<circle class="beacon" cx="{rx}" cy="16" r="2.6" fill="{SIGNAL_RED[c.mode]}"/>')
    for k, y in enumerate((130, 190, 250)):
        c.L.append(f'<circle class="beacon" style="animation-delay:{k * .4:.1f}s" cx="{rx}" cy="{y}" r="1.6" fill="{SIGNAL_RED[c.mode]}"/>')


def bridge(c, x0=806, px=960, deck=262):
    t = c.t
    c.g.append(f'<rect x="{x0}" y="{deck}" width="{W - x0}" height="5" fill="{t["section"]}" stroke="{c.st}" stroke-width="1.2"/>')
    for k in range(8):
        y0 = 92 + k * 12
        for side in (-1, 1):
            c.g.append(f'<line x1="{px}" y1="{y0}" x2="{px + side * (34 + k * 22)}" y2="{deck}" stroke="{c.st}" stroke-width="1"/>')
    c.g.append(c.bldg([(px - 5, G), (px + 5, G), (px + 3, 70), (px - 3, 70)]))
    for pier in (850, 1070, 1160):
        c.g.append(f'<rect x="{pier-3}" y="{deck+5}" width="6" height="{G-deck-5}" fill="{t["section"]}" stroke="{c.st}" stroke-width="1.2"/>')
    for i, (beg, rev) in enumerate([(0, False), (-3.5, True), (-7, False)]):
        path = f"M{x0+4},{deck-2} H{W}" if not rev else f"M{W},{deck-2} H{x0+4}"
        col = c.on if i != 1 else SIGNAL_RED[c.mode]
        c.L.append(f'<rect x="-4" y="-2" width="8" height="3.4" rx="1.5" fill="{col}"><animateMotion dur="9s" begin="{beg}s" '
                   f'repeatCount="indefinite" path="{path}"/></rect>')
    return px


def spire(c, lx):
    t = c.t
    c.g.append(c.bldg([(lx - 18, G), (lx - 18, 246), (lx + 30, 246), (lx + 30, G)], fill=t["section"]))
    c.g.append(c.bldg([(lx - 9, G), (lx - 9, 192), (lx + 9, 192), (lx + 9, G)]))
    c.g.append(c.bldg([(lx - 11, 192), (lx + 3, 126), (lx + 11, 192)], fill=t["primary_subtle"]))
    c.g.append(f'<path d="M{lx-7},180 L{lx+4},150 M{lx-3},188 L{lx+7},162" stroke="{c.st}" stroke-width=".9"/>'
               f'<circle cx="{lx}" cy="206" r="4" fill="none" stroke="{c.st}" stroke-width="1.2"/>')


def dome(c, x):
    t = c.t
    c.g.append(c.bldg([(x - 34, G), (x - 34, 238), (x + 34, 238), (x + 34, G)], fill=t["section"]))
    for k in range(-2, 3):
        c.g.append(f'<line x1="{x + k * 13}" y1="246" x2="{x + k * 13}" y2="{G-4}" stroke="{c.st}" stroke-width="1.2"/>')
    c.g.append(c.bldg([(x - 22, 238), (x - 22, 218), (x + 22, 218), (x + 22, 238)]))
    c.g.append(f'<path d="M{x-24},218 A24,26 0 0 1 {x+24},218 Z" fill="{t["primary_subtle"]}" stroke="{c.st}" stroke-width="1.5"/>'
               f'<rect x="{x-4}" y="186" width="8" height="8" rx="1" fill="{t["card"]}" stroke="{c.st}" stroke-width="1.2"/>'
               f'<line x1="{x}" y1="186" x2="{x}" y2="176" stroke="{c.st}" stroke-width="1.4"/>')


def ferris_wheel(c, x, r=54):
    t = c.t
    cy = G - r - 14
    c.g.append(f'<path d="M{x-26},{G} L{x},{cy} L{x+26},{G}" fill="none" stroke="{c.st}" stroke-width="2"/>')
    spokes = "".join(f'<line x1="0" y1="0" x2="{r * math.cos(a / 12 * 6.2832):.1f}" y2="{r * math.sin(a / 12 * 6.2832):.1f}" '
                     f'stroke="{c.st}" stroke-width="1"/>' for a in range(12))
    cabins = "".join(f'<circle cx="{r * math.cos(a / 12 * 6.2832):.1f}" cy="{r * math.sin(a / 12 * 6.2832):.1f}" r="4.2" '
                     f'fill="{t["primary"] if a % 3 == 0 else t["card"]}" stroke="{c.st}" stroke-width="1"/>' for a in range(12))
    rot = '<animateTransform attributeName="transform" type="rotate" from="0" to="360" dur="80s" repeatCount="indefinite"/>'
    c.g.append(f'<g transform="translate({x},{cy})"><g>'
               f'<circle r="{r}" fill="none" stroke="{c.st}" stroke-width="1.8"/>{spokes}{cabins}{rot}</g>'
               f'<circle r="5" fill="{t["card"]}" stroke="{c.st}" stroke-width="1.5"/></g>')
    if c.night or c.dusk:
        lights = "".join(f'<circle cx="{r * math.cos(a / 24 * 6.2832):.1f}" cy="{r * math.sin(a / 24 * 6.2832):.1f}" r="1.4" '
                         f'fill="{c.on}"/>' for a in range(24))
        c.L.append(f'<g transform="translate({x},{cy})"><g>{lights}{rot}</g></g>')


def flag(c, fx, fy, text, color=None):
    red = color or ("#dc2626" if c.mode == "light" else "#ef4444")
    c.g.append(f'<line x1="{fx}" y1="{fy}" x2="{fx}" y2="{fy-34}" stroke="{c.st}" stroke-width="1.3"/>'
               f'<circle cx="{fx}" cy="{fy-35}" r="1.4" fill="{c.st}"/>'
               f'<g transform="translate({fx+.7},{fy-33})"><g>'
               f'<path d="M0,0 H26 Q24,7 26,16 H0 Z" fill="{red}"/>'
               f'<rect x="0" y="6.4" width="25" height="3.2" fill="#ffffff"/>'
               f'<text class="mono" x="12.5" y="12.9" text-anchor="middle" font-size="8.5" font-weight="700" '
               f'fill="#ffffff" stroke="{red}" stroke-width="2.2" paint-order="stroke">{esc(text)}</text>'
               f'<animateTransform attributeName="transform" type="skewY" dur="2.6s" repeatCount="indefinite" '
               f'values="0;4;-2;0"/></g></g>')


# ======================================================================== city layers
LANDMARK_SLOTS = {"tower": (466, 514), "dome": (566, 634), "wheel": (622, 738), "spire": (752, 800), "bridge": (806, 1200)}


def layer_generic(c, city, beacon, lit_by, label):
    """Procedural city: seeded by the city name, so the skyline is stable between builds."""
    t = c.t
    rng = random.Random(city["name"].lower())
    marks = city.get("landmarks", [])
    reserved = [LANDMARK_SLOTS[m] for m in marks]
    has_sign = bool(city.get("sign"))
    if has_sign:
        reserved.append((372, 440))
    reserved.sort()
    limit = 806 if "bridge" in marks else W
    x = rng.randint(6, 18)
    k = 0
    gables = []
    while x < limit - 20:
        clash = next((r for r in reserved if x < r[1] and x + 30 > r[0]), None)
        if clash:
            x = clash[1] + rng.randint(4, 10)
            continue
        nxt = min([r[0] for r in reserved if r[0] > x] + [limit])
        kind = rng.choice(["block", "block", "stepped", "round", "gable", "gable", "slant", "wavy"])
        w = rng.randint(26, 30) if kind == "gable" else rng.randint(36, 84)
        w = min(w, nxt - x - 2)
        if w < 22:
            x = nxt + 1
            continue
        top = rng.randint(232, 256) if kind == "gable" else rng.randint(118, 240)
        fill = [t["card"], t["section"], t["card"], t["primary_subtle"], t["section"]][k % 5]
        seed = k * 5 + 1
        if kind == "block":
            c.g.append(c.bldg([(x, G), (x, top), (x + w, top), (x + w, G)], fill=fill))
            if rng.random() < .35:
                c.g.append(f'<line x1="{x + w / 2:.0f}" y1="{top}" x2="{x + w / 2:.0f}" y2="{top - rng.randint(12, 26)}" stroke="{c.st}" stroke-width="1.5"/>')
            c.g.append(c.windows(x + 7, top + 10, max(1, (w - 10) // 9), (G - top - 16) // 10, 9, 10, seed=seed))
        elif kind == "stepped":
            s = rng.randint(8, max(9, w // 4))
            c.g.append(c.bldg([(x, G), (x, top + 28), (x + s, top + 28), (x + s, top), (x + w - s, top),
                               (x + w - s, top + 28), (x + w, top + 28), (x + w, G)], fill=fill))
            c.g.append(c.windows(x + s + 5, top + 10, max(1, (w - 2 * s - 6) // 9), (G - top - 16) // 10, 9, 10, seed=seed))
        elif kind == "round":
            r = w / 2
            c.g.append(f'<path d="M{x},{G} V{top + r:.1f} A{r:.1f},{r:.1f} 0 0 1 {x + w},{top + r:.1f} V{G} Z" '
                       f'fill="{fill}" stroke="{c.st}" stroke-width="1.5"/>')
            c.g.append(c.windows(x + 8, top + r + 6, max(1, (w - 12) // 9), (G - top - r - 12) // 10, 9, 10, seed=seed))
        elif kind == "gable":
            c.g.append(c.bldg([(x, G), (x, top + 12), (x + w / 2, top), (x + w, top + 12), (x + w, G)], fill=fill))
            c.g.append(c.windows(x + 5, top + 18, 2, max(1, (G - top - 24) // 11), 11, 11, w=5, h=5, seed=seed))
            gables.append((x + w / 2, top))
        elif kind == "slant":
            dy = rng.randint(14, 30) * rng.choice([-1, 1])
            c.g.append(c.bldg([(x, G), (x, top + max(0, dy)), (x + w, top + max(0, -dy)), (x + w, G)], fill=fill))
            c.g.append(c.windows(x + 7, top + abs(dy) + 8, max(1, (w - 10) // 9), (G - top - abs(dy) - 14) // 10, 9, 10, seed=seed))
        else:  # wavy
            mid = x + w / 2
            d = (f"M{x},{G} C{x-6},{top+60} {x+8},{top+20} {x+4},{top} "
                 f"Q{mid},{top-10} {x+w-2},{top+4} C{x+w+6},{top+40} {x+w-8},{top+90} {x+w},{G} Z")
            c.g.append(f'<path d="{d}" fill="{fill}" stroke="{c.st}" stroke-width="1.5"/>')
            c.g.append(c.windows(x + 10, top + 16, max(1, int((w - 16) / 9)), int((G - top - 24) / 12), 9, 12, w=3, h=5, seed=seed))
        x += w + rng.randint(2, 9)
        k += 1
    anchors = dict(haze=True, tree_x=None, flag=None, sign=None, tower_x=None, bridge_x=None, trees_skip=None)
    for m in ("dome", "wheel", "spire"):
        if m in marks:
            a, b = LANDMARK_SLOTS[m]
            {"dome": dome, "wheel": ferris_wheel, "spire": spire}[m](c, (a + b) // 2 if m != "spire" else 770)
    if has_sign:
        anchors["sign"] = sign_tower(c, 372, city["sign"], None if "tower" in marks else beacon)
    if "tower" in marks:
        tv_tower(c, 490, beacon, lit_by, label)
        anchors["tower_x"] = 490
    elif has_sign and lit_by and label:
        sx, sy = anchors["sign"]
        c.g.append(f'<text class="mono" x="{sx + 34}" y="{sy + 14}" font-size="9.5" fill="{t["muted"]}">lit by @{esc(lit_by)}</text>')
    if "bridge" in marks:
        anchors["bridge_x"] = bridge(c)
        anchors["trees_skip"] = (800, 1200)
    if gables:
        anchors["flag"] = gables[len(gables) // 2]
        anchors["tree_x"] = int(gables[0][0])
    return anchors


LAYERS = {"generic": layer_generic}


# ======================================================================== sky, weather, seasons
def sky_layers(t, mode, phase, weather):
    out = []
    night, dusk = phase == "night", phase == "dusk"
    if night:
        out.append(f'<rect width="{W}" height="{G}" fill="{NIGHT[mode]}" opacity="{0.92 if mode == "light" else 0.75}"/>')
    if dusk:
        out.append('<defs><linearGradient id="dusk" x1="0" y1="0" x2="0" y2="1">'
                   '<stop offset="0" stop-color="#f97316" stop-opacity="0"/>'
                   f'<stop offset="1" stop-color="#f97316" stop-opacity="{0.3 if mode == "light" else 0.22}"/></linearGradient></defs>'
                   f'<rect width="{W}" height="{G}" fill="url(#dusk)"/>')
    if weather in ("cloudy", "rain", "snow", "storm", "fog") and not night:
        out.append(f'<rect width="{W}" height="{G}" fill="{t["section"]}" opacity=".7"/>')
    open_sky = weather in ("clear", "partly")
    if night and open_sky:
        for i in range(42):
            x, y = (i * 263) % 1180 + 10, (i * 97) % 190 + 12
            out.append(f'<circle class="star" style="animation-delay:{i % 7 * .45:.2f}s" cx="{x}" cy="{y}" '
                       f'r="{1.1 if i % 3 else 1.6}" fill="#f4f1ea"/>')
        out.append(f'<circle cx="1090" cy="64" r="20" fill="#f4f1ea"/><circle cx="1101" cy="57" r="18" fill="{NIGHT[mode]}"/>')
    elif open_sky:
        sx, sy, r = (1080, 236, 34) if dusk else (1070, 74, 24)
        col = "#f97316" if dusk else ("#f5b301" if mode == "light" else "#fbbf24")
        out.append(f'<circle cx="{sx}" cy="{sy}" r="{r + 14}" fill="{col}" opacity=".18"/><circle cx="{sx}" cy="{sy}" r="{r}" fill="{col}"/>')
    n = {"clear": 0, "partly": 3, "cloudy": 6, "fog": 3, "rain": 6, "snow": 6, "storm": 7}[weather]
    cfill = ("#3a4258" if mode == "light" else "#2a2a2e") if night else ("#ffffff" if mode == "light" else "#2c2b28")
    if weather in ("rain", "storm") and not night:
        cfill = "#d9d6d0" if mode == "light" else "#3a3835"
    for i in range(n):
        y = 36 + (i * 41) % 130
        s = 0.8 + (i % 3) * 0.25
        dur = 140 + (i * 37) % 90
        out.append(f'<g class="cloud" style="animation-duration:{dur}s;animation-delay:-{(i * 53) % dur}s">'
                   f'<g transform="translate(0,{y}) scale({s})">'
                   f'<path d="M0,30 a18,18 0 0 1 16,-22 a26,26 0 0 1 46,-4 a20,20 0 0 1 34,12 a14,14 0 0 1 4,14 Z" '
                   f'fill="{cfill}" stroke="{t["line"]}" stroke-width="1.2" opacity=".95"/></g></g>')
    return out


def weather_fx(t, weather):
    out = []
    if weather in ("rain", "storm"):
        out.append('<defs><pattern id="rain" width="34" height="46" patternUnits="userSpaceOnUse">'
                   f'<line x1="6" y1="0" x2="2" y2="12" stroke="{t["water_line"]}" stroke-width="1.2" opacity=".45"/>'
                   f'<line x1="24" y1="22" x2="20" y2="34" stroke="{t["water_line"]}" stroke-width="1.2" opacity=".35"/>'
                   '<animateTransform attributeName="patternTransform" type="translate" from="0 0" to="-12 46" '
                   'dur=".55s" repeatCount="indefinite"/></pattern></defs>'
                   f'<rect width="{W}" height="{H}" fill="url(#rain)"/>')
    if weather == "snow":
        out.append('<defs><pattern id="snow" width="40" height="60" patternUnits="userSpaceOnUse">'
                   '<circle cx="8" cy="10" r="1.8" fill="#ffffff"/><circle cx="28" cy="38" r="1.4" fill="#ffffff"/>'
                   '<animateTransform attributeName="patternTransform" type="translate" from="0 0" to="10 60" '
                   'dur="5s" repeatCount="indefinite"/></pattern></defs>'
                   f'<rect width="{W}" height="{H}" fill="url(#snow)"/>'
                   f'<rect width="{W}" height="{H}" fill="url(#snow)" opacity=".6" transform="translate(17,23)"/>')
    if weather == "fog":
        for i, (y, h, o) in enumerate([(170, 60, .55), (225, 50, .65), (275, 40, .7)]):
            out.append(f'<rect class="fog" style="animation-delay:-{i * 5}s" x="-60" y="{y}" width="{W + 120}" '
                       f'height="{h}" rx="{h / 2}" fill="{t["page"]}" opacity="{o}"/>')
    if weather == "storm":
        out.append(f'<rect class="flash" width="{W}" height="{H}" fill="#ffffff"/>'
                   '<path class="flash" d="M820,40 L796,112 L816,112 L792,190 L846,96 L824,96 L846,40 Z" fill="#fde68a"/>')
    return out


def easter(y):
    """Anonymous Gregorian algorithm."""
    a, b, c = y % 19, y // 100, y % 100
    d, e = b // 4, b % 4
    f = (b + 8) // 25
    g_ = (b - f + 1) // 3
    h = (19 * a + b - d - g_ + 15) % 30
    i, k = c // 4, c % 4
    l_ = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l_) // 451
    month = (h + l_ - 7 * m + 114) // 31
    return dt.date(y, month, (h + l_ - 7 * m + 114) % 31 + 1)


def season_for(now, allowed):
    """now: local datetime of the city -> season key (only from `allowed`) or None."""
    d = now.date()
    if (d.month == 12 and d.day == 31 and now.hour >= 18) or (d.month == 1 and d.day == 1 and now.hour < 2):
        key = "newyear"
    elif d.month == 11 and d.day == 11:
        key = "hoppeditz"
    elif easter(d.year) - dt.timedelta(days=52) <= d <= easter(d.year) - dt.timedelta(days=47):
        key = "karneval"
    elif d.month == 12 and 24 <= d.day <= 26:
        key = "christmas"
    else:
        nov27 = dt.date(d.year, 11, 27)
        first_advent = nov27 + dt.timedelta(days=(6 - nov27.weekday()) % 7)
        key = "advent" if first_advent <= d <= dt.date(d.year, 12, 23) else None
    return key if key in allowed else None


def _rope(y0=262, sag=10, span=150):
    return " ".join(f"M{x0},{y0} Q{x0 + span / 2},{y0 + 2 * sag} {x0 + span},{y0}" for x0 in range(0, W, span))


def _on_rope(x, y0=262, sag=10, span=150):
    u = (x % span) / span
    return y0 + 2 * sag * 2 * u * (1 - u)


def season_fx(t, mode, season, anchors):
    if not season:
        return []
    line = t["line"]
    out = []
    if season in ("hoppeditz", "karneval"):
        out.append(f'<path d="{_rope()}" fill="none" stroke="{line}" stroke-width="1.2"/>')
        for k, x in enumerate(range(8, W, 22)):
            y = _on_rope(x)
            out.append(f'<path d="M{x-6},{y:.1f} L{x+6},{y:.1f} L{x},{y+11:.1f} Z" fill="{"#dc2626" if k % 2 == 0 else "#ffffff"}" '
                       f'stroke="{line}" stroke-width=".6"/>')
        tiles = "".join(f'<rect x="{(k * 23) % 70 + 4}" y="{(k * 37) % 90 + 3}" width="4" height="7" rx="1" fill="{CONFETTI[k % 6]}" '
                        f'transform="rotate({(k * 47) % 180} {(k * 23) % 70 + 6} {(k * 37) % 90 + 6})"/>' for k in range(8))
        out.append('<defs><pattern id="confetti" width="80" height="100" patternUnits="userSpaceOnUse">' + tiles
                   + '<animateTransform attributeName="patternTransform" type="translate" from="0 0" to="16 100" '
                     'dur="6s" repeatCount="indefinite"/></pattern></defs>'
                   f'<rect width="{W}" height="{G}" fill="url(#confetti)" opacity=".7"/>')
        if anchors.get("sign"):
            sx, sy = anchors["sign"]
            bx, by, bw, bh = sx - 104, sy - 8, 66, 24
            out.append(f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="6" fill="{t["card"]}" stroke="#dc2626" stroke-width="1.5"/>'
                       f'<path d="M{bx+bw-14},{by+bh-.5} L{bx+bw+10},{by+bh+12} L{bx+bw-4},{by+bh-.5} Z" fill="{t["card"]}" stroke="#dc2626" stroke-width="1.5" stroke-linejoin="round"/>'
                       f'<rect x="{bx+bw-14.5}" y="{by+bh-3}" width="11" height="2.4" fill="{t["card"]}"/>'
                       f'<text class="mono" x="{bx+bw/2}" y="{by+16.5}" text-anchor="middle" font-size="12" font-weight="700" fill="#dc2626">Helau!</text>')
    if season in ("advent", "christmas"):
        warm = LIGHT_ON[mode]
        out.append(f'<path d="{_rope()}" fill="none" stroke="{line}" stroke-width="1"/>')
        for k, x in enumerate(range(10, W, 18)):
            out.append(f'<circle class="bulb" style="animation-delay:{(k % 5) * .32:.2f}s" cx="{x}" cy="{_on_rope(x) + 3:.1f}" '
                       f'r="2.6" fill="{warm if k % 3 else "#dc2626"}"/>')
        tx, base = anchors.get("tree_x") or 700, G - 3
        for k, (w, h) in enumerate([(46, 26), (36, 24), (24, 22)]):
            y = base - 18 - k * 18
            out.append(f'<path d="M{tx - w / 2},{y} L{tx},{y - h} L{tx + w / 2},{y} Z" fill="#1f7a3e" stroke="{line}" stroke-width=".8"/>')
        out.append(f'<rect x="{tx-3}" y="{base-18}" width="6" height="18" fill="#7b400e"/>')
        for k, (dx, dy) in enumerate([(-12, -24), (8, -30), (-4, -44), (6, -58), (-8, -62), (2, -74)]):
            out.append(f'<circle class="bulb" style="animation-delay:{k * .27:.2f}s" cx="{tx + dx}" cy="{base + dy}" r="2" fill="{warm}"/>')
        out.append(f'<path d="M{tx},{base-90} l2.4,5 5.4,.6 -4,3.6 1.2,5.3 -5,-2.8 -5,2.8 1.2,-5.3 -4,-3.6 5.4,-.6 z" fill="{warm}"/>')
    if season == "newyear":
        dark = ["#f87171", "#93c5fd", "#fbbf24", "#4ade80", "#d56db6", "#a4c9dc"]
        for k, (cx, cy, r) in enumerate([(230, 92, 42), (640, 70, 52), (820, 118, 38), (1010, 64, 48), (300, 112, 30), (1120, 150, 30)]):
            col = CONFETTI[k % 6] if mode == "light" else dark[k % 6]
            rays = "".join(f'<line x1="{cx}" y1="{cy}" x2="{cx + r * math.cos(a / 14 * 6.2832):.1f}" '
                           f'y2="{cy + r * math.sin(a / 14 * 6.2832):.1f}" stroke="{col}" stroke-width="2" '
                           f'stroke-linecap="round" stroke-dasharray="3 5"/>' for a in range(14))
            out.append(f'<g class="burst" style="animation-delay:{k * .55:.2f}s">{rays}</g>')
    return out


# ======================================================================== river life
def creatures(t, mode, kinds, sign_text):
    st = t["line"]
    out = []
    if "boats" in kinds:
        def sailboat(col):
            return (f'<path d="M-14,0 H14 L9,7 H-9 Z" fill="{t["card"]}" stroke="{st}" stroke-width="1.2"/>'
                    f'<line x1="0" y1="0" x2="0" y2="-28" stroke="{st}" stroke-width="1.2"/>'
                    f'<path d="M1.5,-27 L16,-3 H1.5 Z" fill="{col}"/><path d="M-1.5,-22 L-11,-3 H-1.5 Z" fill="{t["card"]}" stroke="{st}" stroke-width="1"/>')
        out.append(f'<g>{sailboat(t["primary"])}<animateMotion dur="70s" begin="-20s" repeatCount="indefinite" path="M-40,{G+30} H1240"/></g>'
                   f'<g>{sailboat(t["accent"])}<animateMotion dur="95s" begin="-70s" repeatCount="indefinite" path="M-40,{G+56} H1240"/></g>')
        ship = (f'<path d="M-46,0 H50 L42,10 H-40 Z" fill="{t["card"]}" stroke="{st}" stroke-width="1.3"/>'
                f'<rect x="-34" y="-9" width="62" height="9" rx="2" fill="{t["card"]}" stroke="{st}" stroke-width="1.2"/>'
                f'<rect x="-22" y="-16" width="30" height="7" rx="2" fill="{t["section"]}" stroke="{st}" stroke-width="1.2"/>'
                + "".join(f'<rect x="{-30 + k * 9}" y="-6" width="5" height="3" fill="{t["primary"]}" opacity=".7"/>' for k in range(7))
                + (f'<text class="mono" x="-38" y="7.5" font-size="6.5" font-weight="700" fill="{t["link"]}">{esc(sign_text)}</text>' if sign_text else ""))
        out.append(f'<g>{ship}<animateMotion dur="120s" begin="-35s" repeatCount="indefinite" path="M1260,{G+80} H-60"/></g>')
    if "crocodile" in kinds:
        cg, cd = t["success"], "#15803d" if mode == "light" else "#166534"
        croc = (f'<path d="M-30,1 Q-40,-1 -50,2" stroke="{cg}" stroke-width="3" fill="none" stroke-linecap="round">'
                f'<animate attributeName="d" dur="1.6s" repeatCount="indefinite" values="M-30,1 Q-40,-1 -50,2;M-30,1 Q-40,3 -50,0;M-30,1 Q-40,-1 -50,2"/></path>'
                f'<path d="M-32,1 Q-24,-6 -6,-6 Q6,-6 12,-3 L28,-3 Q32,-2.5 32,0.5 L32,1 Z" fill="{cg}" stroke="{cd}" stroke-width="1"/>'
                + "".join(f'<path d="M{x},-5.6 l2,-2.6 l2,2.6 Z" fill="{cd}"/>' for x in (-22, -16, -10, -4, 2))
                + f'<circle cx="15" cy="-5.5" r="3.2" fill="{cg}" stroke="{cd}" stroke-width="1"/>'
                f'<circle cx="15.4" cy="-6" r="1.8" fill="{t["card"]}"/><circle cx="16" cy="-6" r=".9" fill="#1f2937"/>'
                f'<circle cx="29" cy="-3.2" r="1" fill="{cd}"/>'
                f'<path d="M-36,4 H36" stroke="{t["water_line"]}" stroke-width="1.2" stroke-dasharray="6 5" opacity=".45"/>')
        out.append(f'<g><g><g transform="scale(.8)">{croc}</g><animateTransform attributeName="transform" type="translate" dur="2.2s" '
                   f'repeatCount="indefinite" values="0,0;0,1.5;0,0"/></g>'
                   f'<animateMotion dur="85s" begin="-50s" repeatCount="indefinite" path="M-60,{G+44} H1260"/></g>')
    if "duck" in kinds:
        duck = (f'<path d="M-9,0 Q-10,-7 -2,-6 Q0,-12 5,-11 Q9,-10 8,-6 L12,-5 L8,-4 Q9,0 0,1 Z" fill="#fbbf24" stroke="{st}" stroke-width="1"/>'
                f'<circle cx="5" cy="-9" r=".9" fill="#1f2937"/>')
        out.append(f'<g><g>{duck}<animateTransform attributeName="transform" type="translate" dur="1.8s" '
                   f'repeatCount="indefinite" values="0,0;0,1.2;0,0"/></g>'
                   f'<animateMotion dur="140s" begin="-90s" repeatCount="indefinite" path="M1240,{G+22} H-40"/></g>')
    return out


# ======================================================================== scene
def scene(t, mode, city, phase="day", weather="clear", temp=None, season=None, beacon=None, lit_by=None,
          crop=None, label=True):
    """Full skyline SVG. crop=(x, y, w, h) renders a square avatar crop."""
    c = Ctx(t, mode, phase)
    g = c.g
    css = font_css(sans=False, mono_bold=True) + BASE_CSS + CSS
    vb = crop or (0, 0, W, H)
    g.append(f'<defs><clipPath id="frame"><rect x="{vb[0]}" y="{vb[1]}" width="{vb[2]}" height="{vb[3]}" rx="{0 if crop else 12}"/></clipPath></defs>'
             '<g clip-path="url(#frame)">'
             f'<rect width="{W}" height="{H}" fill="{t["page"]}"/>')
    g += sky_layers(t, mode, phase, weather)
    for y, dur, beg in [(70, 38, 0), (95, 46, 12), (58, 52, 25)]:
        g.append(f'<path d="M-6,-3 Q-3,-6 0,0 Q3,-6 6,-3" fill="none" stroke="{t["muted"]}" stroke-width="1.4" '
                 f'stroke-linecap="round"><animateMotion dur="{dur}s" begin="{-beg}s" repeatCount="indefinite" '
                 f'path="M-20,{y} C300,{y-20} 800,{y+20} 1220,{y-10}"/></path>')
    for i, (x, y) in enumerate([(0, 240), (40, 225), (95, 250), (330, 230), (380, 245), (600, 236), (660, 250),
                                (720, 228), (780, 244), (990, 232), (1040, 248), (1100, 226), (1150, 242)]):
        g.append(f'<rect x="{x}" y="{y}" width="{48 + (i % 3) * 10}" height="{G - y}" fill="{t["border_light"]}"/>')

    anchors = LAYERS[city.get("preset", "generic")](c, city, beacon, lit_by, label)
    if city.get("flag") and anchors.get("flag"):
        fx, fy = anchors["flag"]
        flag(c, fx, fy, city["flag"]["text"], city["flag"].get("color"))

    g.append(f'<rect x="0" y="{G-3}" width="{W}" height="5" fill="{t["border"]}"/>')
    skip = anchors.get("trees_skip")
    for i, x in enumerate(range(14, W, 23)):
        if skip and skip[0] < x < skip[1] and i % 2:
            continue
        r = 5 + (i % 3)
        g.append(f'<circle cx="{x}" cy="{G-3-r}" r="{r}" fill="{t["success"]}" opacity=".45"/>')

    if city.get("river", True):
        g.append(f'<rect x="0" y="{G+2}" width="{W}" height="{H-G}" fill="{t["water"]}"/>')
        for x, h, sw in [(anchors.get("tower_x"), 62, 3), (anchors.get("bridge_x"), 52, 2)]:
            if x:
                g.append(f'<line x1="{x}" y1="{G+8}" x2="{x}" y2="{G+8+h}" stroke="{t["water_line"]}" stroke-width="{sw}" '
                         f'stroke-dasharray="6 6" opacity=".16"/>')
        for i, y in enumerate([G + 18, G + 38, G + 62, G + 84]):
            g.append(f'<path class="{"wave" if i % 2 == 0 else "wave wave2"}" d="M0,{y} H{W+48}" stroke="{t["water_line"]}" stroke-width="1.2" '
                     f'stroke-dasharray="{10+i*4} {26+i*6}" stroke-dashoffset="{i*13}" opacity=".28"/>')
        if not crop:
            g += creatures(t, mode, city.get("creatures", ["boats"]), city.get("sign", ""))
    else:
        g.append(f'<rect x="0" y="{G+2}" width="{W}" height="{H-G}" fill="{t["section"]}"/>')

    if c.night or c.dusk:
        g.append(f'<rect width="{W}" height="{H}" fill="{NIGHT[mode]}" opacity="{(0.5 if mode == "light" else 0.38) if c.night else 0.12}"/>')
    g += c.L
    g += season_fx(t, mode, season, anchors)
    g += weather_fx(t, weather)

    if label:
        night_light = c.night and mode == "light"
        g.append(f'<text class="mono" x="32" y="44" font-size="13" font-weight="700" letter-spacing="2.4" '
                 f'fill="{"#a9bcf0" if night_light else t["link"]}">{esc(city["name"].upper())}</text>')
        lat, lon = city["lat"], city["lon"]
        sub = f"{abs(lat):.2f}° {'N' if lat >= 0 else 'S'} · {abs(lon):.2f}° {'E' if lon >= 0 else 'W'}"
        if temp is not None:
            sub += f" · {temp:.0f} °C · {WEATHER_LABEL[weather]}"
        lab = "#c9cfe0" if night_light else t["muted"]
        g.append(f'<text class="mono" x="32" y="62" font-size="10.5" letter-spacing="1" fill="{lab}">{sub}</text>')
        if season:
            red = season in ("hoppeditz", "karneval")
            col = ("#f87171" if (c.night or mode == "dark") else "#dc2626") if red else lab
            g.append(f'<text class="mono" x="32" y="80" font-size="10.5" font-weight="700" letter-spacing="1" fill="{col}">{SEASON_LABEL[season]}</text>')
    g.append('</g>')
    if crop is None:
        g.append(f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="12" fill="none" stroke="{t["border"]}"/>')
    title = f"Skyline of {city['name']}"
    if temp is not None:
        title += f", now {phase}, {temp:.0f} °C, {WEATHER_LABEL[weather]}"
    out = svg(W, H, title, css, "".join(g))
    if crop:
        out = out.replace(f'width="{W}" height="{H}" viewBox="0 0 {W} {H}"',
                          f'width="{crop[2]}" height="{crop[3]}" viewBox="{crop[0]} {crop[1]} {crop[2]} {crop[3]}"', 1)
    return out


AVATAR_CROP = (262, 14, 380, 380)
