# How to design your skyline

Configure the living skyline at the bottom of your profile: city, landmarks, rooftop sign, river life, flag and seasons. The result follows the real time of day and weather in that city.

## Prerequisites

- A `profile.toml` (run `python3 -m profilekit init` if you have none).
- `"city"` in `sections`, or no `sections` key at all (the default includes it).

## Steps

1. Add a `[city]` table with the name, coordinates and time zone. All three matter: the name seeds the buildings, the coordinates drive weather and sunrise, the time zone decides day and night.

   ```toml
   [city]
   name = "Hamburg"
   lat = 53.55
   lon = 9.99
   timezone = "Europe/Berlin"
   heading = "Based in Hamburg"
   ```

   `heading` is the Markdown heading above the image; it defaults to `Based in <name>`.

2. Pick landmarks. They get fixed slots; procedural buildings fill everything else.

   ```toml
   landmarks = ["tower", "spire", "bridge"]
   ```

   | Landmark | Looks like | Position |
   |---|---|---|
   | `tower` | TV tower with a pod and blinking warning lights; the light-up target | centre left |
   | `dome` | Domed building with columns | centre |
   | `wheel` | Ferris wheel that turns slowly, lit at night | centre right |
   | `spire` | Church with a pointed spire | right of centre |
   | `bridge` | Cable-stayed bridge with moving car lights | right third |

   Without `landmarks`, you get `["tower", "bridge"]`. With `landmarks = []`, the whole width is procedural buildings.

3. Add a rooftop sign with up to three letters. It sits on a glass tower left of the TV tower and glows at night.

   ```toml
   sign = "HH"
   ```

   The same letters appear on the passenger ship. Leave `sign` out for no sign.

4. Choose what lives on the river.

   ```toml
   river = true
   creatures = ["boats", "crocodile", "duck"]
   ```

   `boats` are two sailboats and a passenger ship, `crocodile` swims downstream, `duck` paddles upstream. `river = false` draws plain ground and no creatures.

5. Optionally fly a flag on a gabled house.

   ```toml
   flag = { text = "MOIN", color = "#2563eb" }
   ```

   Up to four characters. The flag needs at least one gabled house in your procedural city; if the name produces none, the flag is not drawn. Changing the city name or landmarks changes the houses.

6. Choose the seasons that switch on by themselves.

   ```toml
   seasons = ["newyear", "advent", "christmas"]
   ```

   | Season | When (in the city's time zone) | Decoration |
   |---|---|---|
   | `newyear` | Dec 31 from 18:00 to Jan 1 02:00 | fireworks |
   | `advent` | First Sunday of Advent to Dec 23 | fairy lights and a Christmas tree |
   | `christmas` | Dec 24 to 26 | fairy lights and a Christmas tree |
   | `karneval` | Thursday before Shrove Tuesday to Shrove Tuesday | bunting, confetti, a "Helau!" bubble at the sign |
   | `hoppeditz` | Nov 11 | bunting, confetti, a "Helau!" bubble at the sign |

   The default is `["newyear", "advent", "christmas"]`.

7. Pick a theme for the whole profile, or re-tint it with your own accent colour.

   ```toml
   [profile]
   theme = "slate"        # or "ink" (default)
   accent = "#7c3aed"     # optional
   ```

## Verification

Render every condition without waiting for it:

```bash
python3 -m profilekit preview --phase night --weather snow --season advent
python3 -m profilekit preview --phase dusk --weather storm
```

Open `preview.html` and toggle light and dark. Weather values: `clear`, `partly`, `cloudy`, `fog`, `rain`, `snow`, `storm`.

## Troubleshooting

| Symptom | Cause and fix |
|---|---|
| The skyline shows day although it is dark in your city | `timezone` is missing and defaults to `UTC`. Set your IANA zone, for example `America/New_York`. |
| You do not like the buildings | They come from the city name. Try the local spelling (`"München"` instead of `"Munich"`) or change the landmarks, which changes the free gaps. |
| No flag | Your city produced no gabled house. Change the name spelling or landmarks, or drop the flag. |
| Light-up colour does not show | It colours the `tower` pod, or the `sign` if there is no tower. With neither, there is nothing to light; add one of them or switch `[lightup]` off. |
| The avatar crop shows only buildings | `assets/avatar-*.svg` is a fixed square around the sign and tower slots. Add `sign` and `tower` for a recognisable avatar. |

## Related

- [Reference: `[city]` keys](reference-config.md#city)
- [How to add a hand-drawn city](howto-add-a-hand-drawn-city.md)
- [Explanation: a city from its name](explanation-how-it-works.md#a-city-from-its-name)
