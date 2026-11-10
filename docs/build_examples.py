"""Render the example images used in the kit README (offline, deterministic)."""
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from profilekit import build, config, sections, skyline  # noqa: E402
from profilekit.core import theme  # noqa: E402

OUT = ROOT / "docs" / "img"
OUT.mkdir(parents=True, exist_ok=True)
berlin = config.with_defaults(tomllib.loads((ROOT / "profilekit" / "example.toml").read_text()))
hamburg = dict(berlin["city"], name="Hamburg", lat=53.55, lon=9.99, sign="HH", landmarks=["tower", "spire", "bridge"],
               creatures=["boats", "crocodile"], flag={"text": "MOIN", "color": "#2563eb"})
days = build.sample_days("example")
for m in ("light", "dark"):
    t = theme("ink", m)
    (OUT / f"header-{m}.svg").write_text(sections.header(t, berlin["profile"], berlin["hub"]))
    (OUT / f"focus-{m}.svg").write_text(sections.focus(t, berlin["focus"]))
    (OUT / f"terminal-{m}.svg").write_text(sections.terminal(t, berlin["terminal"], "octocat"))
    (OUT / f"skyline-berlin-{m}.svg").write_text(skyline.scene(t, m, berlin["city"], phase="day", weather="partly", temp=14))
    (OUT / f"skyline-hamburg-{m}.svg").write_text(skyline.scene(t, m, hamburg, phase="night", weather="clear", temp=7, season="advent"))
    (OUT / f"settle-{m}.svg").write_text(sections.settle(t, m, days))
    ts = theme("slate", m)
    (OUT / f"skyline-slate-{m}.svg").write_text(skyline.scene(ts, m, dict(berlin["city"], name="Lisbon", lat=38.72, lon=-9.14,
                                                              sign="", landmarks=["bridge", "spire", "wheel"]), phase="dusk", weather="clear", temp=19))
print("\n".join(sorted(p.name for p in OUT.iterdir())))
