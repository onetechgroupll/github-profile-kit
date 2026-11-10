# How to add a hand-drawn city

Contribute a real city as a skyline preset, so people can set `preset = "<city>"` instead of the procedural skyline. A city is one Python function.

## Prerequisites

- A fork of the kit and Python 3.11.
- A reference photo or sketch of the skyline, and a list of the five to eight landmarks people recognise.
- A browser to look at the result.

## How a city layer works

The scene in `profilekit/skyline.py` draws the sky, river, trees, creatures, seasons, weather and labels. Your layer draws only the buildings between them.

| Fact | Value |
|---|---|
| Canvas | 1200 × 400 user units |
| Ground / waterline `G` | y = 300. Buildings stand on it, the river starts below it. |
| Sky | y = 0 to 300. The sun and moon sit near x = 1070, y = 74; keep the top right free of tall buildings. |
| Labels | City name and coordinates sit top left (x 32, y 44 to 80); keep that corner below y ≈ 90 free. |
| Avatar crop | `AVATAR_CROP = (262, 14, 380, 380)`: put your most recognisable landmark between x 262 and 642. |

Your function gets a drawing context `c`:

| Member | Use |
|---|---|
| `c.g` | List of SVG strings for the normal layer. Append buildings here. |
| `c.L` | Lights layer, drawn above the night overlay: lit windows, signs, beacons. |
| `c.t` | Theme tokens: `card`, `section`, `primary`, `primary_light`, `primary_subtle`, `border`, `muted`, `line` and more (see `profilekit/core.py`). Never hard-code colours for buildings, or dark mode breaks. |
| `c.st` | The line colour for outlines. |
| `c.night`, `c.dusk` | Booleans for the time of day. |
| `c.bldg(points, fill)` | A closed outline polygon in the house style. |
| `c.windows(x0, y0, cols, rows, dx, dy, w, h, seed)` | A window grid that lights up at dusk and night. |

Shared landmark helpers you can reuse: `sign_tower(c, x, text, beacon)`, `tv_tower(c, x, pod, lit_by, label)`, `bridge(c)`, `spire(c, x)`, `dome(c, x)`, `ferris_wheel(c, x)`.

## Steps

1. Write the layer in `profilekit/skyline.py`, next to `layer_generic`:

   ```python
   def layer_hamburg(c, city, beacon, lit_by, label):
       """Hand-drawn Hamburg: Elbphilharmonie, Michel, Heinrich-Hertz-Turm, Köhlbrandbrücke."""
       t = c.t
       c.g.append(c.bldg([(80, G), (80, 180), (200, 150), (200, G)], fill=t["primary_light"]))
       c.g.append(c.windows(90, 190, 10, 9, 10, 11, seed=3))
       sign = sign_tower(c, 372, city["sign"], None) if city.get("sign") else None
       tv_tower(c, 490, beacon, lit_by, label)          # light-up target
       spire(c, 770)
       px = bridge(c)
       return dict(sign=sign, tower_x=490, bridge_x=px, flag=(717, 242), tree_x=700, trees_skip=(800, 1200))
   ```

   The returned anchors tell the scene where things are:

   | Key | Used for |
   |---|---|
   | `sign` | `(x, y)` of the rooftop sign; the carnival "Helau!" bubble points at it. `None` if there is no sign. |
   | `tower_x` | x of the tower; draws its reflection in the river. |
   | `bridge_x` | x of the bridge pylon; draws its reflection. |
   | `flag` | `(x, y)` of a rooftop where `[city].flag` is planted, or `None`. |
   | `tree_x` | x of the Christmas tree in Advent. |
   | `trees_skip` | `(x0, x1)` range where every second promenade tree is left out, for example under a bridge. |

   Pass `beacon` (the light-up colour) to whatever should glow when a visitor lights the city, and print `lit by @<lit_by>` next to it when `label` is true. `tv_tower` does both for you.

2. Register it:

   ```python
   LAYERS = {"generic": layer_generic, "hamburg": layer_hamburg}
   ```

3. Allow it in the schema. In `profilekit/schema.json`, add the name to `properties.city.properties.preset.enum` and describe it in that key's `description`.

4. Regenerate the config reference:

   ```bash
   python3 docs/gen_reference.py
   ```

5. Render it under every condition and look at it in light and dark:

   ```bash
   cat > /tmp/city.toml <<'EOF'
   [profile]
   handle = "octocat"
   name = "Test"
   [city]
   name = "Hamburg"
   lat = 53.55
   lon = 9.99
   timezone = "Europe/Berlin"
   preset = "hamburg"
   sign = "HH"
   creatures = ["boats", "duck"]
   seasons = ["advent", "karneval", "newyear"]
   EOF
   mkdir -p /tmp/city && cp /tmp/city.toml /tmp/city/profile.toml
   for p in day dusk night; do python3 -m profilekit --root /tmp/city preview --phase $p --weather snow --season advent; done
   ```

   Open `/tmp/city/preview.html` after each run and check that labels, sun or moon, the "Helau!" bubble and the Christmas tree do not collide with your buildings.

6. Check that every file is well-formed XML:

   ```bash
   for f in /tmp/city/assets/*.svg /tmp/city/dist/*.svg; do xmllint --noout "$f"; done
   ```

7. Open a pull request with a light and a dark screenshot.

## Verification

- `python3 -m profilekit --root /tmp/city validate` prints `profile.toml is valid`.
- `python3 docs/gen_reference.py --check` prints `docs/reference-config.md is up to date`.
- Both modes look right at day, dusk and night.

## Troubleshooting

| Symptom | Cause and fix |
|---|---|
| `must be one of ['generic']` | The preset is missing from the schema enum (step 3). |
| `KeyError` in `scene` | The layer is missing from `LAYERS` (step 2). |
| Buildings stay bright at night | You appended lights to `c.g`. Lit windows and signs belong in `c.L`, or use `c.windows`, which handles that. |
| Dark mode shows white boxes | A hard-coded colour. Use `c.t[...]` tokens. |
| The XML check fails on `&` | Escape text with `esc()` from `profilekit/core.py`. |

## Related

- [How to design your skyline](howto-design-your-skyline.md)
- [Explanation: a city from its name](explanation-how-it-works.md#a-city-from-its-name)
