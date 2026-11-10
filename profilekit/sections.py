"""Section graphics. Each function takes theme tokens `t` (+ config parts) and returns an SVG string."""
import datetime as dt

from .core import BASE_CSS, MONO_ADV, esc, font_css, svg, window

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


# ---------------------------------------------------------------- header
def header(t, profile, hub=None):
    W, H = 1200, 340
    words = profile.get("words") or [""]
    n = len(words)
    cycle = 3.2 * n
    word_css = []
    for i in range(n):
        a, b = i / n * 100, (i + 1) / n * 100
        word_css.append(
            f"@keyframes w{i}{{0%,{max(a-0.01,0):.2f}%{{opacity:0;transform:translateY(10px)}}"
            f"{a+1.5:.2f}%,{b-2:.2f}%{{opacity:1;transform:translateY(0)}}"
            f"{b-0.5:.2f}%,100%{{opacity:0;transform:translateY(-10px)}}}}"
            f".w{i}{{opacity:0;animation:w{i} {cycle}s infinite}}")
    if n == 1:  # a single word just stays
        word_css = [".w0{opacity:1}"]
    ticks = (hub or {}).get("ticker", [])
    for i in range(len(ticks)):  # the ticker cycles on its own clock
        a, b = i / len(ticks) * 100, (i + 1) / len(ticks) * 100
        word_css.append(f"@keyframes k{i}{{0%,{max(a-0.01,0):.2f}%{{opacity:0}}{a+1:.2f}%,{b-1:.2f}%{{opacity:1}}{b:.2f}%,100%{{opacity:0}}}}"
                        f".k{i}{{opacity:0;animation:k{i} {2.4 * len(ticks)}s infinite}}")
    style = font_css(mono_bold=True) + BASE_CSS + "".join(word_css) + """
@keyframes dash{to{stroke-dashoffset:-24}}
.flow{stroke-dasharray:3 9;animation:dash 1.2s linear infinite}
@keyframes ring{0%{r:34;opacity:.55}100%{r:70;opacity:0}}
.ring{animation:ring 2.4s ease-out infinite}
.ring2{animation-delay:1.2s}
@keyframes rise{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}
.in{opacity:0;animation:rise .7s ease-out forwards}
.d1{animation-delay:.1s}.d2{animation-delay:.3s}.d3{animation-delay:.5s}
"""
    g = [f'<defs><pattern id="dots" width="22" height="22" patternUnits="userSpaceOnUse">'
         f'<circle cx="2" cy="2" r="1.1" fill="{t["border"]}"/></pattern>'
         f'<linearGradient id="fade" x1="0" x2="1"><stop offset="0" stop-color="{t["page"]}" stop-opacity="1"/>'
         f'<stop offset=".55" stop-color="{t["page"]}" stop-opacity=".2"/>'
         f'<stop offset="1" stop-color="{t["page"]}" stop-opacity="0"/></linearGradient></defs>',
         f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="12" fill="{t["page"]}" stroke="{t["border"]}"/>',
         f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="12" fill="url(#dots)" opacity="{t["grid_op"]}"/>',
         f'<rect x="1" y="1" width="760" height="{H-2}" rx="12" fill="url(#fade)"/>']
    text_w = 620
    if hub:
        g += _hub(t, hub)
    else:
        text_w = 1080

    x0 = 64
    kicker = profile.get("kicker", "")
    if kicker:
        g.append(f'<text class="mono in d1" x="{x0}" y="118" font-size="13" letter-spacing="2.2" fill="{t["link"]}">'
                 f'{esc(kicker.upper())}</text>')
    name = profile["name"]
    fs = min(66, text_w / (len(name) * 0.56))
    g.append(f'<text class="sans in d2" x="{x0-3}" y="186" font-size="{fs:.0f}" font-weight="640" letter-spacing="-{fs/30:.1f}" '
             f'fill="{t["text"]}">{esc(name)}</text>')
    prefix = profile.get("build_prefix", "I build")
    if profile.get("words"):
        wx = x0 + len(prefix) * 13.2 + 26
        g.append(f'<g class="in d3"><text class="sans" x="{x0}" y="238" font-size="26" fill="{t["secondary"]}">{esc(prefix)}</text>')
        for i, w in enumerate(words):
            g.append(f'<text class="mono w{i}" style="transform-box:fill-box" x="{wx:.0f}" y="238" font-size="25" '
                     f'font-weight="700" fill="{t["link"]}">{esc(w)}</text>')
        g.append('</g>')
    title = f"{name}. {kicker}. {prefix} " + ", ".join(w.rstrip('.') for w in profile.get("words", []))
    return svg(W, H, title, style, "".join(g))


def _hub(t, hub):
    cx, cy = 905, 170
    ins = hub.get("inputs", [])
    outs = hub.get("outputs", [])
    in_ys = {1: [170], 2: [130, 210], 3: [100, 170, 240], 4: [82, 140, 200, 258]}.get(len(ins), [])
    out_ys = {1: [170], 2: [130, 210], 3: [105, 170, 235]}.get(len(outs), [])
    srcs = [(lab, 735 if i in (0, 3) else 715, y) for i, (lab, y) in enumerate(zip(ins, in_ys))]
    dsts = [(lab, 1100 if y == 170 else 1085, y) for lab, y in zip(outs, out_ys)]
    g = []
    for i, (_, x, y) in enumerate(srcs):
        path = f"M{x+28},{y} C{x+90},{y} {cx-80},{cy} {cx-34},{cy}"
        g.append(f'<path d="{path}" fill="none" stroke="{t["border"]}" stroke-width="1.5"/>')
        g.append(f'<path class="flow" d="{path}" fill="none" stroke="{t["primary"]}" stroke-width="1.5" opacity=".55"/>')
        g.append(f'<circle r="3.5" fill="{t["primary"]}"><animateMotion dur="2.4s" begin="{i*0.6}s" '
                 f'repeatCount="indefinite" path="{path}" keyPoints="0;1" keyTimes="0;1" calcMode="spline" '
                 f'keySplines=".5 0 .5 1"/></circle>')
    for i, (_, x, y) in enumerate(dsts):
        path = f"M{cx+34},{cy} C{cx+80},{cy} {x-90},{y} {x-40},{y}"
        g.append(f'<path d="{path}" fill="none" stroke="{t["border"]}" stroke-width="1.5"/>')
        g.append(f'<circle r="3.5" fill="{t["success"]}"><animateMotion dur="2.4s" begin="{1.2+i*0.8}s" '
                 f'repeatCount="indefinite" path="{path}" calcMode="spline" keyPoints="0;1" keyTimes="0;1" '
                 f'keySplines=".5 0 .5 1"/></circle>')
    for label, x, y in srcs:
        g.append(f'<rect x="{x-28}" y="{y-13}" width="56" height="26" rx="6" fill="{t["card"]}" stroke="{t["border"]}"/>'
                 f'<text x="{x}" y="{y+4}" text-anchor="middle" class="mono" font-size="10.5" fill="{t["secondary"]}">{esc(label)}</text>')
    for label, x, y in dsts:
        g.append(f'<rect x="{x-40}" y="{y-13}" width="80" height="26" rx="6" fill="{t["card"]}" stroke="{t["border"]}"/>'
                 f'<circle cx="{x-27}" cy="{y}" r="2.5" fill="{t["success"]}"/>'
                 f'<text x="{x+5}" y="{y+4}" text-anchor="middle" class="mono" font-size="10.5" fill="{t["secondary"]}">{esc(label)}</text>')
    g.append(f'<circle class="ring" cx="{cx}" cy="{cy}" r="34" fill="none" stroke="{t["primary"]}" stroke-width="1.5"/>'
             f'<circle class="ring ring2" cx="{cx}" cy="{cy}" r="34" fill="none" stroke="{t["primary"]}" stroke-width="1.5"/>'
             f'<circle cx="{cx}" cy="{cy}" r="34" fill="{t["primary"]}"/>')
    center = hub.get("center", "")
    g.append(f'<text x="{cx}" y="{cy+6}" text-anchor="middle" class="mono" font-weight="700" font-size="{16 if len(center) <= 3 else 13}" '
             f'fill="{t["on_primary"]}">{esc(center)}</text>')
    if hub.get("label"):
        g.append(f'<text x="{cx}" y="{cy+58}" text-anchor="middle" class="mono" font-size="10" letter-spacing="1.5" '
                 f'fill="{t["muted"]}">{esc(hub["label"].upper())}</text>')
    ticks = hub.get("ticker", [])
    for i, b in enumerate(ticks):
        g.append(f'<text class="mono k{i}" x="{cx}" y="{cy+80}" text-anchor="middle" '
                 f'font-size="11" fill="{t["link"]}">{esc(b)}</text>')
    return g


# ---------------------------------------------------------------- focus cards + stage animations
def focus(t, cards):
    W = 1200
    n = len(cards)
    gap = 24
    cw = (W - (n - 1) * gap) / n
    ch = 328
    style = font_css() + BASE_CSS + """
@keyframes blink{0%,49%{opacity:1}50%,100%{opacity:.25}}
.live{animation:blink 1.6s steps(1) infinite}
@keyframes scroll{from{transform:translateY(0)}to{transform:translateY(-120px)}}
.ledger{animation:scroll 6s linear infinite}
@keyframes draw{0%{stroke-dashoffset:420}60%,100%{stroke-dashoffset:0}}
.spark{stroke-dasharray:420;animation:draw 5s ease-out infinite}
"""
    g = ['<defs><clipPath id="led"><rect x="0" y="0" width="236" height="112"/></clipPath></defs>']
    for i, c in enumerate(cards):
        x = i * (cw + gap)
        sw = cw - 44
        g.append(f'<g transform="translate({x:.1f},1)">')
        g.append(f'<rect x=".5" y=".5" width="{cw-1:.1f}" height="{ch-3}" rx="12" fill="{t["card"]}" stroke="{t["border"]}"/>')
        g.append(f'<text class="mono" x="22" y="36" font-size="11" letter-spacing="1.6" fill="{t["muted"]}">{i+1:02d} /</text>')
        g.append(f'<circle class="live" cx="{cw-30:.1f}" cy="32" r="2.5" fill="{t["success"]}"/>')
        g.append(f'<rect x="22" y="54" width="{sw:.1f}" height="120" rx="8" fill="{t["section"]}"/>')
        g.append(f'<g transform="translate({22 + (sw - 238) / 2:.1f},54)">{STAGES[c["visual"]](t, 238)}</g>')
        g.append(f'<text class="sans" x="22" y="218" font-size="21" font-weight="620" letter-spacing="-.4" fill="{t["text"]}">{esc(c["title"])}</text>')
        for k, key in enumerate(("line1", "line2")):
            if c.get(key):
                g.append(f'<text class="sans" x="22" y="{250 + k * 20}" font-size="14" fill="{t["secondary"]}">{esc(c[key])}</text>')
        tx = 22
        for tag in c.get("tags", []):
            w = len(tag) * 10 * MONO_ADV + 16
            g.append(f'<rect x="{tx:.1f}" y="288" width="{w:.0f}" height="20" rx="4" fill="{t["primary_light"]}"/>'
                     f'<text class="mono" x="{tx+8:.1f}" y="302" font-size="10" fill="{t["link"]}">{esc(tag)}</text>')
            tx += w + 6
        g.append('</g>')
    title = "Focus: " + "; ".join(f'{c["title"]}: {c.get("line1", "")} {c.get("line2", "")}'.strip() for c in cards)
    return svg(W, 330, title, style, "".join(g))


def stage_auction(t, w):
    out = []
    bw, gap, base = 26, 14, 100
    vals = [[40, 70, 55, 30, 40], [62, 35, 80, 58, 62], [30, 58, 42, 75, 30], [75, 50, 64, 46, 75], [50, 82, 38, 60, 50]]
    spl = ".4 0 .2 1;.4 0 .2 1;.4 0 .2 1;.4 0 .2 1"
    for k in range(5):
        x = 22 + k * (bw + gap)
        hs = vals[k]
        fills = ";".join(t["primary"] if h >= 75 else t["idle"] for h in hs)
        out.append(f'<rect x="{x}" y="{base-hs[0]}" width="{bw}" height="{hs[0]}" rx="3" fill="{t["idle"]}">'
                   f'<animate attributeName="height" values="{";".join(map(str, hs))}" dur="6s" repeatCount="indefinite" calcMode="spline" keySplines="{spl}"/>'
                   f'<animate attributeName="y" values="{";".join(str(base - h) for h in hs)}" dur="6s" repeatCount="indefinite" calcMode="spline" keySplines="{spl}"/>'
                   f'<animate attributeName="fill" values="{fills}" keyTimes="0;.25;.5;.75;1" dur="6s" repeatCount="indefinite" calcMode="discrete"/></rect>')
    out.append(f'<line x1="14" x2="{w-14}" y1="{base+.5}" y2="{base+.5}" stroke="{t["border"]}"/>')
    out.append(f'<text class="mono" x="14" y="18" font-size="10" fill="{t["muted"]}">bids/s 48k</text>')
    out.append(f'<text class="mono" x="{w-14}" y="18" text-anchor="end" font-size="10" fill="{t["link"]}">p95 9ms</text>')
    return "".join(out)


def stage_retail(t, w):
    out = []
    y = 62
    xs = [36, w / 2, w - 36]
    path = f"M{xs[0]},{y} L{xs[2]},{y}"
    out.append(f'<path d="{path}" stroke="{t["border"]}" stroke-width="2" stroke-dasharray="2 6"/>')
    sx = xs[0]
    out.append(f'<g><rect x="{sx-20}" y="{y-24}" width="40" height="48" rx="4" fill="{t["card"]}" stroke="{t["border"]}"/>'
               f'<line x1="{sx-20}" x2="{sx+20}" y1="{y-4}" y2="{y-4}" stroke="{t["border"]}"/>'
               f'<rect x="{sx-14}" y="{y-18}" width="8" height="12" rx="1" fill="{t["accent"]}"/>'
               f'<rect x="{sx-3}" y="{y-16}" width="8" height="10" rx="1" fill="{t["idle"]}"/>'
               f'<rect x="{sx+8}" y="{y-20}" width="6" height="14" rx="1" fill="{t["idle"]}"/>'
               f'<rect x="{sx-14}" y="{y+2}" width="10" height="14" rx="1" fill="{t["idle"]}"/>'
               f'<rect x="{sx+1}" y="{y+4}" width="12" height="12" rx="1" fill="{t["accent"]}" opacity=".6"/></g>')
    mx = xs[1]
    out.append(f'<rect x="{mx-24}" y="{y-20}" width="48" height="32" rx="4" fill="{t["card"]}" stroke="{t["border"]}"/>'
               f'<rect x="{mx-19}" y="{y-15}" width="38" height="22" rx="2" fill="{t["primary"]}" opacity=".15">'
               f'<animate attributeName="opacity" values=".15;.15;.9;.15;.15" keyTimes="0;.42;.5;.62;1" dur="3s" repeatCount="indefinite"/></rect>'
               f'<line x1="{mx}" x2="{mx}" y1="{y+12}" y2="{y+22}" stroke="{t["border"]}" stroke-width="2"/>'
               f'<line x1="{mx-10}" x2="{mx+10}" y1="{y+22}" y2="{y+22}" stroke="{t["border"]}" stroke-width="2"/>')
    rx = xs[2]
    out.append(f'<path d="M{rx-15},{y-24} h30 v46 l-5,-4 l-5,4 l-5,-4 l-5,4 l-5,-4 l-5,4 z" fill="{t["card"]}" stroke="{t["border"]}"/>'
               f'<line x1="{rx-9}" x2="{rx+9}" y1="{y-14}" y2="{y-14}" stroke="{t["idle"]}" stroke-width="2"/>'
               f'<line x1="{rx-9}" x2="{rx+5}" y1="{y-7}" y2="{y-7}" stroke="{t["idle"]}" stroke-width="2"/>'
               f'<line x1="{rx-9}" x2="{rx+9}" y1="{y+2}" y2="{y+2}" stroke="{t["success"]}" stroke-width="2.5">'
               f'<animate attributeName="opacity" values="0;0;1;1;0" keyTimes="0;.82;.88;.97;1" dur="3s" repeatCount="indefinite"/></line>')
    out.append(f'<circle r="4" fill="{t["primary"]}"><animateMotion dur="3s" repeatCount="indefinite" path="{path}" '
               f'keyPoints="0;.5;.5;1;1" keyTimes="0;.42;.6;.85;1" calcMode="linear"/></circle>')
    out.append(f'<text class="mono" x="14" y="112" font-size="10" fill="{t["muted"]}">exposure</text>')
    out.append(f'<text class="mono" x="{w-14}" y="112" text-anchor="end" font-size="10" fill="{t["link"]}">+uplift</text>')
    return "".join(out)


def stage_sync(t, w):
    out = []
    px, py, slides, dur = 30, 14, 4, 8
    out.append(f'<rect x="{px}" y="{py}" width="50" height="92" rx="8" fill="{t["card"]}" stroke="{t["primary"]}" stroke-width="1.5"/>')
    for s in range(slides):
        v, kt = window(s / slides, (s + 1) / slides)
        out.append(f'<g opacity="0"><animate attributeName="opacity" values="{v}" keyTimes="{kt}" '
                   f'dur="{dur}s" repeatCount="indefinite" calcMode="discrete"/>'
                   f'<rect x="{px+7}" y="{py+12}" width="36" height="{14+s*8}" rx="2" fill="{t["primary"]}" opacity=".85"/>'
                   f'<text class="mono" x="{px+25}" y="{py+82}" text-anchor="middle" font-size="9" fill="{t["muted"]}">{s+1}/{slides}</text></g>')
    for k in range(2):
        out.append(f'<circle cx="{px+50}" cy="{py+46}" r="6" fill="none" stroke="{t["primary"]}" stroke-width="1.2" opacity="0">'
                   f'<animate attributeName="r" values="6;48" dur="2s" begin="{k}s" repeatCount="indefinite"/>'
                   f'<animate attributeName="opacity" values=".6;0" dur="2s" begin="{k}s" repeatCount="indefinite"/></circle>')
    for j in range(3):
        ax, ay = 118 + j * 34, 28 + (j % 2) * 10
        out.append(f'<rect x="{ax}" y="{ay}" width="26" height="48" rx="5" fill="{t["card"]}" stroke="{t["border"]}"/>')
        lag = 0.15 + j * 0.07
        for s in range(slides):
            v, kt = window(s / slides, (s + 1) / slides)
            out.append(f'<rect x="{ax+4}" y="{ay+6}" width="18" height="{7+s*4}" rx="1.5" fill="{t["primary"]}" opacity="0">'
                       f'<animate attributeName="opacity" values="{v}" keyTimes="{kt}" begin="{lag:.2f}s" '
                       f'dur="{dur}s" repeatCount="indefinite" calcMode="discrete"/></rect>')
        out.append(f'<circle cx="{ax+13}" cy="{ay+42}" r="2" fill="{t["success"]}"/>')
    out.append(f'<text class="mono" x="{w-14}" y="108" text-anchor="end" font-size="10" fill="{t["link"]}">&lt;80ms</text>')
    return "".join(out)


def stage_ledger(t, w):
    out = []
    rows = [("INV-2041", "+1,240.00"), ("PAYOUT", "-380.50"), ("INV-2042", "+2,915.00"), ("FEE", "-12.90"),
            ("INV-2043", "+760.00"), ("REFUND", "-95.00")]
    out.append('<g clip-path="url(#led)"><g class="ledger">')
    for rep in range(2):
        for k, (ref, amt) in enumerate(rows):
            yy = 22 + (rep * len(rows) + k) * 20
            col = t["success"] if amt.startswith("+") else t["secondary"]
            out.append(f'<circle cx="16" cy="{yy-4}" r="2.5" fill="{t["success"]}"/>'
                       f'<text class="mono" x="26" y="{yy}" font-size="10" fill="{t["muted"]}">{ref}</text>'
                       f'<text class="mono" x="{w/2+20}" y="{yy}" text-anchor="end" font-size="10" fill="{col}">{amt}</text>')
    out.append('</g></g>')
    sx = w / 2 + 34
    pts = [(0, 80), (14, 72), (28, 76), (42, 58), (56, 62), (70, 44), (84, 40)]
    d = "M" + " L".join(f"{sx+x},{y}" for x, y in pts)
    out.append(f'<line x1="{sx-6}" x2="{sx-6}" y1="10" y2="104" stroke="{t["border"]}"/>')
    out.append(f'<path class="spark" d="{d}" fill="none" stroke="{t["primary"]}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>')
    out.append(f'<text class="mono" x="{w-10}" y="104" text-anchor="end" font-size="10" fill="{t["link"]}">Δ 0.00</text>')
    return "".join(out)


STAGES = {"auction": stage_auction, "retail": stage_retail, "sync": stage_sync, "ledger": stage_ledger}


# ---------------------------------------------------------------- terminal
BOLD = ' font-weight="700"'


def terminal(t, term, handle):
    W, fs = 1200, 15
    adv = fs * MONO_ADV
    lh, X = 24, 32
    TX = X + 2 * adv
    txt, sec, mut, link, ok = t["text"], t["secondary"], t["muted"], t["link"], t["success"]
    cmd = term.get("command", handle.lower()[:16])
    rows = []
    if term.get("whoami"):
        out = [(term["whoami"], sec)]
        if term.get("whoami_note"):
            out.append((" · " + term["whoami_note"], mut))
        rows += [("cmd", "whoami"), ("out", out), ("gap",)]
    flags = term.get("flags", [])
    if flags:
        pad = max(len(f["flag"]) for f in flags)
        rows += [("cmd", f"{cmd} --help"),
                 ("out", [(f"usage: {cmd} ", sec), (" ".join(f"[{f['flag']}]" for f in flags), mut)])]
        rows += [("out", [("  " + f["flag"].ljust(pad), link, True), ("  " + f["text"], sec)]) for f in flags]
        rows.append(("gap",))
    procs = term.get("processes", [])
    if procs:
        rows += [("cmd", "top -o impact"), ("out", [("  PID  PROCESS          STATE   LOAD", mut)])]
        for i, name in enumerate(procs):
            seed = sum(map(ord, name))
            loads = [round(.45 + ((seed * (k + 3)) % 45) / 100, 2) for k in range(4)]
            rows.append(("top", (str(101 + i), name, loads + [loads[0]])))
        rows.append(("gap",))
    pr = term.get("principles", [])
    if pr:
        rows.append(("cmd", "cat ./principles"))
        for k, p in enumerate(pr):
            rows.append(("out", [(f"{k+1:02d}  ", mut), (p, link, True) if k == 0 else (p, sec)]))
        rows.append(("gap",))
    y, layout = 76, []
    for r in rows:
        if r[0] == "gap":
            y += 10
            continue
        layout.append((r, y))
        y += lh
    H = y + lh + 18
    css = [font_css(sans=False, mono_bold=True), BASE_CSS,
           "@keyframes ping{0%,100%{opacity:1}50%{opacity:.3}}.run{animation:ping 1.4s ease-in-out infinite}"]
    g = [f'<clipPath id="win"><rect x="0" y="0" width="{W}" height="{H}" rx="12"/></clipPath>',
         f'<g clip-path="url(#win)"><rect width="{W}" height="{H}" fill="{t["card"]}"/>'
         f'<rect width="{W}" height="40" fill="{t["section"]}"/></g>',
         f'<path d="M0,40.5 H{W}" stroke="{t["border"]}"/>',
         f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="12" fill="none" stroke="{t["border"]}"/>']
    for k in range(3):
        g.append(f'<circle cx="{24+k*18}" cy="20.5" r="5.5" fill="{t["idle"]}"/>')
    host = term.get("host", f"{handle.lower()}@github")
    g.append(f'<text class="mono" x="{W/2}" y="25" text-anchor="middle" font-size="12" fill="{mut}">{esc(host)} — ~/ — zsh</text>')
    defs, body = ['<defs>'], []
    t0 = 0.4
    for i, (r, y) in enumerate(layout):
        kind = r[0]
        if kind == "cmd":
            text = r[1]
            width = len(text) * adv + 16
            dur = 0.05 * len(text)
            vals = ";".join(f"{min(k * adv, width):.1f}" for k in range(len(text) + 1)) + f";{width:.1f}"
            anim = (f'<animate attributeName="width" values="{vals}" begin="{t0:.2f}s" dur="{dur:.2f}s" '
                    f'calcMode="discrete" fill="freeze"/>')
            css.append(f"@keyframes p{i}{{to{{opacity:1}}}}.p{i}{{opacity:0;animation:p{i} .01s {t0:.2f}s forwards}}")
            body.append(f'<text class="mono pfx p{i}" x="{X}" y="{y}" font-size="{fs}" fill="{ok}">$</text>')
            body.append(f'<text class="mono" clip-path="url(#cl{i})" x="{TX}" y="{y}" font-size="{fs}" font-weight="700" '
                        f'fill="{txt}" xml:space="preserve">{esc(text)}</text>')
            t0 += dur + 0.3
        else:
            width = W - TX - 24
            dur = 0.22
            anim = (f'<animate attributeName="width" values="0;{width:.1f}" begin="{t0:.2f}s" dur="{dur:.2f}s" '
                    f'calcMode="spline" keySplines=".2 .7 .3 1" keyTimes="0;1" fill="freeze"/>')
            if kind == "out":
                spans = "".join(f'<tspan fill="{c[1]}"{BOLD if len(c) > 2 else ""}>{esc(c[0])}</tspan>' for c in r[1])
                body.append(f'<text class="mono" clip-path="url(#cl{i})" x="{TX}" y="{y}" font-size="{fs}" '
                            f'xml:space="preserve">{spans}</text>')
            else:
                pid, name, loads = r[1]
                bx, bw = TX + 32 * adv, 260
                vals = ";".join(f"{v * bw:.1f}" for v in loads)
                body.append(f'<g clip-path="url(#cl{i})">'
                            f'<text class="mono" x="{TX}" y="{y}" font-size="{fs}" xml:space="preserve">'
                            f'<tspan fill="{mut}">  {pid}  </tspan><tspan fill="{txt}">{esc(name.ljust(17))}</tspan></text>'
                            f'<circle class="run" style="animation-delay:{int(pid) % 5 * .2:.1f}s" cx="{TX + 24.5 * adv:.1f}" cy="{y-5}" r="3.2" fill="{ok}"/>'
                            f'<text class="mono" x="{TX + 25.6 * adv:.1f}" y="{y}" font-size="{fs}" fill="{sec}">R</text>'
                            f'<rect x="{bx:.1f}" y="{y-11}" width="{bw}" height="10" rx="3" fill="{t["section"]}"/>'
                            f'<rect x="{bx:.1f}" y="{y-11}" width="{loads[0]*bw:.1f}" height="10" rx="3" fill="{t["primary"]}">'
                            f'<animate attributeName="width" values="{vals}" dur="{4 + int(pid) % 3}s" repeatCount="indefinite" '
                            f'calcMode="spline" keySplines=".4 0 .2 1;.4 0 .2 1;.4 0 .2 1;.4 0 .2 1"/></rect></g>')
            t0 += dur + 0.06
        defs.append(f'<clipPath id="cl{i}"><rect x="{TX - 2 if kind == "cmd" else TX - 4}" y="{y-fs-2}" width="0" height="{lh}">{anim}</rect></clipPath>')
    defs.append('</defs>')
    y = (layout[-1][1] if layout else 52) + lh + 10
    css.append(f"@keyframes bl{{0%,49%{{opacity:1}}50%,100%{{opacity:0}}}}@keyframes on{{to{{visibility:visible}}}}"
               f".cur{{visibility:hidden;animation:on .01s {t0:.2f}s forwards, bl 1s steps(1) {t0:.2f}s infinite}}")
    body.append(f'<text class="mono" x="{X}" y="{y}" font-size="{fs}" fill="{ok}">$</text>')
    body.append(f'<rect class="cur" x="{TX}" y="{y-fs+2}" width="{adv:.1f}" height="{fs+2}" fill="{link}"/>')
    parts = []
    if term.get("whoami"):
        parts.append(f"whoami: {term['whoami']} {term.get('whoami_note', '')}".strip())
    if flags:
        parts.append("roles: " + "; ".join(f"{f['flag'][2:]} ({f['text']})" for f in flags))
    if procs:
        parts.append("running: " + ", ".join(procs))
    if pr:
        parts.append("principles: " + "; ".join(pr))
    return svg(W, H, "Terminal. " + ". ".join(parts), "".join(css), "".join(g + defs + body))


# ---------------------------------------------------------------- contributions
def calendar_stats(days):
    """days: [(iso_date, count)] ascending -> derived numbers."""
    total = sum(c for _, c in days)
    longest = cur = 0
    for _, c in days:
        cur = cur + 1 if c > 0 else 0
        longest = max(longest, cur)
    i = len(days) - 1
    if days and days[-1][1] == 0:  # today not started yet
        i -= 1
    current = 0
    while i >= 0 and days[i][1] > 0:
        current += 1
        i -= 1
    wd = [0] * 7
    for d, c in days:
        wd[dt.date.fromisoformat(d).weekday()] += c
    names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    months = {}
    for d, c in days:
        months[d[:7]] = months.get(d[:7], 0) + c
    keys = sorted(months)[-12:]
    return dict(total=total, longest=longest, current=current, weekday=names[wd.index(max(wd))] if total else "–",
                months=[(k, months[k]) for k in keys])


def stats(t, st):
    W, H = 1200, 300
    css = font_css() + BASE_CSS + """
@keyframes grow{from{transform:scaleY(0)}to{transform:scaleY(1)}}
@media (prefers-reduced-motion: no-preference){.bar{transform-box:fill-box;transform-origin:50% 100%;
animation:grow .9s cubic-bezier(.2,.7,.3,1) both}}
"""
    g = []
    tiles = [(f"{st['total']:,}", "contributions", "last 12 months"),
             (f"{st['longest']}", "days", "longest streak"),
             (f"{st['current']}", "days", "current streak"),
             (st["weekday"], "", "busiest weekday")]
    tw, th, gap = 280, 136, 20
    for i, (num, unit, lab) in enumerate(tiles):
        x, y = (i % 2) * (tw + gap) + .5, (i // 2) * (th + 26) + .5
        g.append(f'<rect x="{x}" y="{y}" width="{tw}" height="{th}" rx="12" fill="{t["card"]}" stroke="{t["border"]}"/>'
                 f'<text class="mono" x="{x+22}" y="{y+34}" font-size="11" letter-spacing="1.6" fill="{t["muted"]}">{lab.upper()}</text>')
        fs = 42 if len(num) < 8 else 34
        g.append(f'<text class="sans" x="{x+20}" y="{y+96}" font-size="{fs}" font-weight="640" letter-spacing="-1.2" '
                 f'fill="{t["text"]}">{num}<tspan class="mono" dx="8" font-size="13" font-weight="400" letter-spacing="0" '
                 f'fill="{t["secondary"]}">{unit}</tspan></text>')
    cx, cw = 600.5, 599
    g.append(f'<rect x="{cx}" y=".5" width="{cw-1}" height="{H-1}" rx="12" fill="{t["card"]}" stroke="{t["border"]}"/>'
             f'<text class="sans" x="{cx+24}" y="38" font-size="16" font-weight="600" fill="{t["text"]}">Contributions per month</text>'
             f'<text class="mono" x="{cx+24}" y="58" font-size="10.5" fill="{t["muted"]}">last 12 months</text>')
    months = st["months"] or [(dt.date.today().isoformat()[:7], 0)]
    base, top = 250, 96
    mx = max(c for _, c in months) or 1
    n = len(months)
    slot = (cw - 48) / n
    bw = slot - 14
    for gi in range(3):
        y = base - (base - top) * gi / 2
        g.append(f'<line x1="{cx+24}" x2="{cx+cw-24}" y1="{y:.1f}" y2="{y:.1f}" stroke="{t["border_light"]}"/>')
    imax = max(range(n), key=lambda i: months[i][1])
    for i, (k, c) in enumerate(months):
        h = max(2, (base - top) * c / mx)
        x = cx + 24 + i * slot + 7
        r = min(4, bw / 2, h / 2)
        d = (f"M{x:.1f},{base} V{base-h+r:.1f} Q{x:.1f},{base-h:.1f} {x+r:.1f},{base-h:.1f} "
             f"H{x+bw-r:.1f} Q{x+bw:.1f},{base-h:.1f} {x+bw:.1f},{base-h+r:.1f} V{base} Z")
        g.append(f'<path class="bar" style="animation-delay:{i*0.05:.2f}s" d="{d}" fill="{t["series"]}"/>'
                 f'<text class="mono" x="{x+bw/2:.1f}" y="{base+20}" text-anchor="middle" font-size="10" '
                 f'fill="{t["muted"]}">{MONTHS[int(k[5:7])-1]}</text>')
        if i in (imax, n - 1):
            g.append(f'<text class="mono" x="{x+bw/2:.1f}" y="{base-h-8:.1f}" text-anchor="middle" font-size="10.5" '
                     f'fill="{t["secondary"]}">{c:,}</text>')
    g.append(f'<line x1="{cx+24}" x2="{cx+cw-24}" y1="{base+.5}" y2="{base+.5}" stroke="{t["border"]}"/>')
    alt = (f"{st['total']:,} contributions in the last 12 months; longest streak {st['longest']} days; current streak "
           f"{st['current']} days; busiest weekday {st['weekday']}. Per month: "
           + ", ".join(f"{MONTHS[int(k[5:7])-1]} {c}" for k, c in months))
    return svg(W, H, alt, css, "".join(g))


def levels(t, mode):
    """Five-step sequential ramp from the empty cell to the accent."""
    from .core import _mix
    empty = t["border_light"] if mode == "light" else t["section"]
    top = t["primary"] if mode == "light" else t["link"]
    return [empty] + [_mix(empty, top, f) for f in (.28, .5, .75, 1.0)]


def settle(t, mode, days):
    """The contribution calendar collapses into weekly bars (active days per week) and rebuilds."""
    weeks = [days[i:i + 7] for i in range(0, len(days), 7)]
    first = next((i for i, w in enumerate(weeks) if any(c for _, c in w)), 0)
    weeks = weeks[first:] or weeks[-1:]
    n = len(weeks)
    W = 1200
    step = min(26.0, (W - 96) / max(n, 1))
    cs = step - 4
    x0 = (W - n * step + 4) / 2
    y0 = 74
    base = y0 + 7 * step
    H = int(base + 46)
    nz = sorted(c for _, c in days if c > 0)
    q = [nz[int(len(nz) * f)] if nz else 1 for f in (.25, .5, .75)]
    lv_col = levels(t, mode)

    def level(c):
        return 0 if c == 0 else 1 + sum(c > v for v in q)

    T, t_set, d_set, t_back = 12.0, 3.0, 0.9, 9.0
    css = font_css(mono_bold=True) + BASE_CSS
    g = [f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="12" fill="{t["card"]}" stroke="{t["border"]}"/>',
         f'<text class="mono" x="24" y="34" font-size="11" letter-spacing="1.6" fill="{t["muted"]}">CONTRIBUTIONS · LAST 12 MONTHS</text>']
    for lab, show in [("calendar", "1;1;0;0;1;1"), ("active days per week", "0;0;1;1;0;0")]:
        g.append(f'<text class="mono" x="{W-24}" y="34" text-anchor="end" font-size="11" letter-spacing="1" fill="{t["link"]}" opacity="{show[0]}">'
                 f'{lab}<animate attributeName="opacity" dur="{T}s" repeatCount="indefinite" values="{show}" '
                 f'keyTimes="0;{t_set/T:.4f};{(t_set+.5)/T:.4f};{t_back/T:.4f};{(t_back+.5)/T:.4f};1"/></text>')
    g.append(f'<line x1="{x0-6:.1f}" x2="{x0 + n*step + 2:.1f}" y1="{base + 2.5:.1f}" y2="{base + 2.5:.1f}" stroke="{t["border"]}"/>')
    last_month = None
    for c, wk in enumerate(weeks):
        x = x0 + c * step
        m = dt.date.fromisoformat(wk[0][0]).month
        if m != last_month:
            g.append(f'<text class="mono" x="{x:.1f}" y="{base + 22:.1f}" font-size="10" fill="{t["muted"]}">{MONTHS[m-1]}</text>')
            last_month = m
        active = [r for r, (_, cnt) in enumerate(wk) if cnt > 0]
        lag = c * 0.025
        ts, te, tb, tbe = t_set + lag, t_set + lag + d_set, t_back + lag, t_back + lag + d_set
        kt = f"0;{ts/T:.4f};{te/T:.4f};{tb/T:.4f};{tbe/T:.4f};1"
        for r, (_, cnt) in enumerate(wk):
            y = y0 + r * step
            lv = level(cnt)
            if lv == 0:
                g.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{cs:.1f}" height="{cs:.1f}" rx="3" fill="{lv_col[0]}">'
                         f'<animate attributeName="opacity" dur="{T}s" repeatCount="indefinite" values="1;1;0;0;1;1" keyTimes="{kt}"/></rect>')
                continue
            dy = (7 - len(active) + active.index(r) - r) * step
            g.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{cs:.1f}" height="{cs:.1f}" rx="3" fill="{lv_col[lv]}">'
                     f'<animateTransform attributeName="transform" type="translate" dur="{T}s" repeatCount="indefinite" '
                     f'values="0 0;0 0;0 {dy:.1f};0 {dy:.1f};0 0;0 0" keyTimes="{kt}" calcMode="spline" '
                     f'keySplines="0 0 1 1;.5 0 .2 1;0 0 1 1;.5 0 .2 1;0 0 1 1"/></rect>')
    return svg(W, H, "Contribution calendar of the last 12 months; it settles into weekly bars of active days and rebuilds.",
               css, "".join(g))


# ---------------------------------------------------------------- recommendations
LANG_COLOR = {"TypeScript": "#3178c6", "JavaScript": "#f1e05a", "Python": "#3572a5", "Rust": "#dea584",
              "Go": "#00add8", "Swift": "#f05138", "Kotlin": "#a97bff", "Java": "#b07219", "C": "#555555",
              "C++": "#f34b7d", "C#": "#178600", "Ruby": "#701516", "PHP": "#4f5d95", "Shell": "#89e051",
              "Zig": "#ec915c", "Elixir": "#6e4a7e", "Dart": "#00b4ab", "Lua": "#000080", "Svelte": "#ff3e00", "Vue": "#41b883"}


def fmt_stars(n):
    return f"{n/1000:.1f}k" if n >= 1000 else str(n)


def rec_card(t, p):
    W, H = 600, 176
    owner, name = p["repo"].split("/")
    css = font_css() + BASE_CSS + """
@keyframes nudge{0%,100%{transform:translateX(0)}50%{transform:translateX(4px)}}
.arrow{animation:nudge 1.8s ease-in-out infinite}
"""
    g = [f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="12" fill="{t["card"]}" stroke="{t["border"]}"/>',
         f'<rect x="24" y="24" width="44" height="44" rx="8" fill="{t["primary_light"]}"/>',
         f'<text class="mono" x="46" y="53" text-anchor="middle" font-size="20" font-weight="700" fill="{t["link"]}">{esc(name[0].upper())}</text>',
         f'<text class="sans" x="84" y="44" font-size="22" font-weight="620" letter-spacing="-.4" fill="{t["text"]}">{esc(name[:30])}</text>',
         f'<text class="mono" x="84" y="64" font-size="12" fill="{t["muted"]}">{esc(owner)}</text>']
    if p.get("tag"):
        tw = len(p["tag"]) * 10.5 * MONO_ADV + 18
        g.append(f'<rect x="{W-24-tw:.0f}" y="26" width="{tw:.0f}" height="22" rx="4" fill="{t["primary_light"]}"/>'
                 f'<text class="mono" x="{W-24-tw+9:.0f}" y="41" font-size="10.5" letter-spacing=".4" fill="{t["link"]}">{esc(p["tag"].upper())}</text>')
    l1 = p.get("line1") or p.get("description", "")[:48]
    g.append(f'<text class="sans" x="24" y="102" font-size="16" fill="{t["secondary"]}">{esc(l1)}</text>')
    if p.get("line2"):
        g.append(f'<text class="sans" x="24" y="124" font-size="16" fill="{t["secondary"]}">{esc(p["line2"])}</text>')
    g.append(f'<path d="M24,140 H{W-24}" stroke="{t["border_light"]}"/>')
    sx = 24
    if p.get("lang"):
        g.append(f'<circle cx="30" cy="158" r="5" fill="{LANG_COLOR.get(p["lang"], t["muted"])}"/>'
                 f'<text class="mono" x="42" y="162" font-size="12" fill="{t["muted"]}">{esc(p["lang"])}</text>')
        sx = 42 + len(p["lang"]) * 12 * MONO_ADV + 22
    if p.get("stars") is not None:
        g.append(f'<path transform="translate({sx:.0f},151) scale(.75)" d="M8,0 L10.4,5 L16,5.7 L11.9,9.5 L13,15 L8,12.3 L3,15 L4.1,9.5 L0,5.7 L5.6,5 Z" fill="{t["muted"]}"/>'
                 f'<text class="mono" x="{sx+18:.0f}" y="162" font-size="12" fill="{t["muted"]}">{fmt_stars(p["stars"])}</text>')
    g.append(f'<text class="mono" x="{W-52}" y="162" text-anchor="end" font-size="12" fill="{t["link"]}">view on GitHub</text>'
             f'<g class="arrow"><path d="M{W-44},158 h14 m-5,-5 l5,5 l-5,5" fill="none" stroke="{t["link"]}" stroke-width="1.6" '
             f'stroke-linecap="round" stroke-linejoin="round"/></g>')
    alt = f'Recommended: {p["repo"]}. {l1} {p.get("line2", "")}'.strip()
    return svg(W, H, alt, css, "".join(g))


# ---------------------------------------------------------------- contact row
def _icon(t, icon):
    c = t["link"]
    s = f'fill="none" stroke="{c}" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"'
    return {
        "linkedin": (f'<rect x="14" y="11" width="18" height="18" rx="4" fill="{t["primary"]}"/>'
                     '<text x="23" y="25" text-anchor="middle" font-family="Helvetica,Arial,sans-serif" '
                     f'font-size="12" font-weight="700" fill="{t["on_primary"]}">in</text>'),
        "web": (f'<circle cx="23" cy="20" r="8.5" {s}/><ellipse cx="23" cy="20" rx="3.6" ry="8.5" {s}/>'
                f'<line x1="14.5" y1="20" x2="31.5" y2="20" {s}/>'),
        "github": (f'<path d="M20,29 v-3 c-4,1 -5,-2 -5,-2 M26,29 v-3.5 c0,-1 -.3,-1.6 -.8,-2 c2.6,-.3 5.3,-1.3 5.3,-5.8 '
                   f'c0,-1.3 -.5,-2.4 -1.2,-3.2 c.1,-.3 .5,-1.5 -.1,-3.2 c0,0 -1,-.3 -3.3,1.2 c-1.9,-.5 -4,-.5 -5.9,0 '
                   f'c-2.3,-1.5 -3.3,-1.2 -3.3,-1.2 c-.6,1.7 -.2,2.9 -.1,3.2 c-.8,.8 -1.2,1.9 -1.2,3.2 c0,4.5 2.7,5.5 5.3,5.8 '
                   f'c-.5,.4 -.8,1.1 -.8,2 v3.5" {s}/>'),
        "x": f'<path d="M15,12 L31,28 M31,12 L15,28" {s} stroke-width="2"/>',
        "mastodon": (f'<rect x="14.5" y="11.5" width="17" height="15" rx="5" {s}/>'
                     f'<path d="M19,24 V17.5 M23,22 V17.5 M27,24 V17.5" {s}/>'),
        "bluesky": f'<path d="M23,20 C20,14 16,12 15,13 C14,15 16,21 20,21 C17,22 17,26 20,27 C22,27 23,23 23,21 C23,23 24,27 26,27 C29,26 29,22 26,21 C30,21 32,15 31,13 C30,12 26,14 23,20 Z" {s}/>',
        "mail": f'<rect x="14" y="13" width="18" height="14" rx="2.5" {s}/><path d="M14.5,14 L23,21 L31.5,14" {s}/>',
        "rss": (f'<circle cx="16.5" cy="26.5" r="1.8" fill="{c}"/><path d="M15,19 a8,8 0 0 1 8,8 M15,13 a14,14 0 0 1 14,14" {s}/>'),
    }[icon]


def button(t, label, icon):
    fs, H = 14, 40
    w = int(52 + len(label) * fs * 0.56)
    css = font_css(mono=False) + BASE_CSS
    body = (f'<rect x=".5" y=".5" width="{w-1}" height="{H-1}" rx="8" fill="{t["card"]}" stroke="{t["border"]}"/>'
            + _icon(t, icon) + f'<text class="sans" x="42" y="25" font-size="{fs}" font-weight="560" fill="{t["text"]}">{esc(label)}</text>')
    return svg(w, H, label, css, body)


def status_pills(t, status):
    parts = [(lab, status[k]) for k, lab in (("based_in", "BASED IN"), ("open_to", "OPEN TO")) if status.get(k)]
    fs = 12
    adv = fs * MONO_ADV
    x, body = 0, []
    for k, (lab, val) in enumerate(parts):
        w = int(28 + (len(lab) + len(val) + 2) * adv)
        body.append(f'<rect x="{x+.5}" y=".5" width="{w-1}" height="31" rx="16" fill="{t["card"]}" stroke="{t["border"]}"/>'
                    f'<circle cx="{x+15}" cy="16" r="2.5" fill="{t["success"] if lab == "OPEN TO" else t["link"]}"/>'
                    f'<text class="mono" x="{x+25}" y="20" font-size="{fs}" fill="{t["muted"]}">{lab}'
                    f'<tspan dx="{adv:.1f}" fill="{t["text"]}">{esc(val)}</tspan></text>')
        x += w + 8
    alt = ". ".join(f"{lab.capitalize()} {val}" for lab, val in parts)
    return svg(int(x - 8), 32, alt, font_css(sans=False) + BASE_CSS, "".join(body))


# ---------------------------------------------------------------- org card
def org_card(t, org):
    W, H = 1200, 132
    css = font_css(mono_bold=True) + BASE_CSS + """
@keyframes fan0{0%,15%{transform:rotate(0)}40%,80%{transform:rotate(-16deg)}100%{transform:rotate(0)}}
@keyframes fan2{0%,15%{transform:rotate(0)}40%,80%{transform:rotate(16deg)}100%{transform:rotate(0)}}
.k0{transform-box:view-box;transform-origin:96px 150px;animation:fan0 7s cubic-bezier(.3,.7,.2,1) infinite}
.k2{transform-box:view-box;transform-origin:96px 150px;animation:fan2 7s cubic-bezier(.3,.7,.2,1) infinite}
@media (prefers-reduced-motion: reduce){.k0{transform:rotate(-16deg)}.k2{transform:rotate(16deg)}}
@keyframes nudge{0%,100%{transform:translateX(0)}50%{transform:translateX(5px)}}
.arrow{animation:nudge 1.8s ease-in-out infinite}
"""
    g = [f'<clipPath id="oc"><rect width="{W}" height="{H}" rx="12"/></clipPath>',
         f'<g clip-path="url(#oc)"><rect width="{W}" height="{H}" fill="{t["card"]}"/>']
    for k in (0, 2, 1):
        front = k == 1
        g.append(f'<g class="k{k}"><rect x="72" y="26" width="48" height="66" rx="6" fill="{t["primary"] if front else t["section"]}" '
                 f'stroke="{t["primary"] if front else t["border"]}"/>'
                 + ("".join(f'<rect x="{80 + c * 11}" y="{36 + r * 9}" width="8" height="6" rx="1" fill="{t["on_primary"]}" opacity=".9"/>'
                            for r in range(3) for c in range(3)) if front else "") + '</g>')
    g.append('</g>')
    url = org["url"].removeprefix("https://").rstrip("/")
    g.append(f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="12" fill="none" stroke="{t["border"]}"/>'
             f'<text class="mono" x="168" y="46" font-size="11" letter-spacing="1.8" fill="{t["muted"]}">{esc(org["kicker"].upper())}</text>'
             f'<text class="sans" x="166" y="82" font-size="30" font-weight="640" letter-spacing="-.8" fill="{t["text"]}">{esc(org["name"])}</text>')
    if org.get("tagline"):
        g.append(f'<text class="sans" x="168" y="108" font-size="15" fill="{t["secondary"]}">{esc(org["tagline"])}</text>')
    g.append(f'<text class="mono" x="{W-80}" y="72" text-anchor="end" font-size="13" fill="{t["link"]}">{esc(url[:44])}</text>'
             f'<g class="arrow"><path d="M{W-62},66 h22 m-8,-8 l8,8 l-8,8" fill="none" stroke="{t["link"]}" stroke-width="2" '
             f'stroke-linecap="round" stroke-linejoin="round"/></g>')
    return svg(W, H, f"{org['kicker'].capitalize()} {org['name']}. {org.get('tagline', '')}", css, "".join(g))


# ---------------------------------------------------------------- light-up colour chips (system font: tiny files)
def color_chip(t, name, fill):
    w = int(28 + len(name) * 7.6 + 14)
    body = (f'<rect x=".5" y=".5" width="{w-1}" height="29" rx="15" fill="{t["card"]}" stroke="{t["border"]}"/>'
            f'<circle cx="16" cy="15" r="6" fill="{fill}"/>'
            f'<text x="28" y="19.5" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace" font-size="12.5" '
            f'fill="{t["secondary"]}">{name}</text>')
    return svg(w, 30, f"Light it up in {name}", "", body)
