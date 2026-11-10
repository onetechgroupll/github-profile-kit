"""Shared building blocks: themes, fonts, SVG wrapper, escaping."""
import base64
from functools import lru_cache
from pathlib import Path

FONTS = Path(__file__).resolve().parent / "fonts"
MONO_ADV = 0.6  # JetBrains Mono advance width / em (600/1000)

# Theme tokens. "ink" is the kit's own default: neutral greys, a violet accent, orange highlights.
# "slate" is a cool alternative with a teal accent. water / water_line colour the river and stay
# independent of `accent`. Every key must exist in every theme and mode.
THEMES = {
    "ink": {
        "light": dict(page="#f7f7f8", card="#ffffff", section="#f0f0f3", border="#e2e2e7",
                      border_light="#ececf0", text="#111114", secondary="#55555f", muted="#6b6b75",
                      primary="#6e56cf", link="#5b45b8", primary_light="#f4f1fd", primary_subtle="#e7e1fb",
                      success="#1f9d5c", accent="#f76b15", idle="#d4d4da", grid_op="0.55",
                      line="#b4b4bf", series="#5b45b8", water="#eaf1fa", water_line="#4f7fcf", on_primary="#ffffff"),
        "dark": dict(page="#111113", card="#18181b", section="#1f1f23", border="#2e2e34",
                     border_light="#232328", text="#ededef", secondary="#a9a9b4", muted="#8f8f9a",
                     primary="#7a66e6", link="#b1a4f7", primary_light="#231e3b", primary_subtle="#2c2550",
                     success="#3dd68c", accent="#ff8b3e", idle="#3a3a41", grid_op="0.7",
                     line="#4c4c55", series="#8e7cf0", water="#141c2b", water_line="#5b8ad6", on_primary="#ffffff"),
    },
    "slate": {
        "light": dict(page="#f8fafc", card="#ffffff", section="#f1f5f9", border="#e2e8f0",
                      border_light="#eef2f6", text="#0f172a", secondary="#475569", muted="#5b6779",
                      primary="#0f766e", link="#0f766e", primary_light="#ecfdf9", primary_subtle="#d5f5ee",
                      success="#16a34a", accent="#7c3aed", idle="#cbd5e1", grid_op="0.55",
                      line="#a8b3c2", series="#115e59", water="#e3f2f1", water_line="#0f766e", on_primary="#ffffff"),
        "dark": dict(page="#0b1120", card="#111827", section="#1a2232", border="#273244",
                     border_light="#1d2636", text="#e5e7eb", secondary="#a3adbd", muted="#8b95a7",
                     primary="#2dd4bf", link="#5eead4", primary_light="#10302f", primary_subtle="#143c3a",
                     success="#22c55e", accent="#a78bfa", idle="#334155", grid_op="0.7",
                     line="#475569", series="#14b8a6", water="#0e2a30", water_line="#2dd4bf", on_primary="#042f2e"),
    },
}

LIGHT_ON = {"light": "#e0a106", "dark": "#fbbf24"}   # warm window light
SIGNAL_RED = {"light": "#dc2626", "dark": "#f87171"}
NIGHT = {"light": "#16203a", "dark": "#05070d"}


def _mix(a, b, f):
    """Blend hex colour a toward b by fraction f."""
    pa = [int(a[i:i + 2], 16) for i in (1, 3, 5)]
    pb = [int(b[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * f):02x}" for x, y in zip(pa, pb))


def theme(name, mode, accent=None):
    """Theme tokens for one mode; `accent` (hex) re-tints primary/link/surfaces."""
    t = dict(THEMES[name][mode])
    if accent:
        if mode == "light":
            t.update(primary=accent, link=accent, series=_mix(accent, "#000000", .25),
                     primary_light=_mix(accent, "#ffffff", .94), primary_subtle=_mix(accent, "#ffffff", .88))
        else:
            t.update(primary=_mix(accent, "#ffffff", .25), link=_mix(accent, "#ffffff", .45),
                     series=_mix(accent, "#ffffff", .2),
                     primary_light=_mix(accent, t["card"], .8), primary_subtle=_mix(accent, t["card"], .74))
        t["on_primary"] = "#ffffff" if _contrast("#ffffff", t["primary"]) >= 4.5 else "#111114"
    return t


def _lum(h):
    c = [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    c = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def _contrast(a, b):
    hi, lo = sorted((_lum(a), _lum(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


@lru_cache(maxsize=None)
def _b64(name):
    return base64.b64encode((FONTS / name).read_bytes()).decode()


def font_css(sans=True, mono=True, mono_bold=False):
    """Embedded fonts: an SVG shown via <img> cannot load external fonts."""
    css = []
    if sans:
        css.append("@font-face{font-family:'Inter';font-weight:100 900;"
                   f"src:url(data:font/woff2;base64,{_b64('inter-latin-wght-normal.woff2')}) format('woff2');}}")
    if mono:
        css.append("@font-face{font-family:'JetBrains Mono';font-weight:400;"
                   f"src:url(data:font/woff2;base64,{_b64('jetbrains-mono-latin-400-normal.woff2')}) format('woff2');}}")
    if mono_bold:
        css.append("@font-face{font-family:'JetBrains Mono';font-weight:700;"
                   f"src:url(data:font/woff2;base64,{_b64('jetbrains-mono-latin-700-normal.woff2')}) format('woff2');}}")
    return "\n".join(css)


BASE_CSS = """
.sans{font-family:'Inter',-apple-system,'Segoe UI',Helvetica,Arial,sans-serif}
.mono{font-family:'JetBrains Mono',ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}
@media (prefers-reduced-motion: reduce){*{animation:none!important}
.in,.w0,.k0,.pfx{opacity:1!important;transform:none!important}.cur{visibility:visible!important}
.spark{stroke-dashoffset:0!important}}
"""


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace('"', "&quot;"))


def svg(w, h, title, style, body):
    """title must be plain text; it is escaped here."""
    title = esc(title)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'role="img" aria-label="{title}"><title>{title}</title>'
            f'<style>{style}</style>{body}</svg>\n')


def window(a, b):
    """values/keyTimes that show an element only during [a, b) of a discrete cycle."""
    if a <= 0:
        return "1;0", f"0;{b:.3f}"
    return "0;1;0", f"0;{a:.3f};{b:.3f}"
