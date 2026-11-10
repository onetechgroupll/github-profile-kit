# Explanation: how the kit works, and why it is built this way

A GitHub profile README is a Markdown file in a special repository. It can show images, but it cannot run code, load scripts, fetch data or change over time. Everything that looks alive on a profile built with this kit is a trick played within those limits. This page explains the tricks and what they cost.

For the facts (files, commands, keys), see the [CLI reference](reference-cli.md), [config reference](reference-config.md) and [workflow reference](reference-workflows.md).

## The problem

Most "pimped" profiles stitch together widgets from different public services: a stats card from one server, a streak counter from another, a snake animation from a third. That causes three recurring failures:

1. **Nothing matches.** Each widget brings its own fonts, colours and spacing. The profile looks like a collage.
2. **Public instances break.** Shared stats servers hit GitHub's rate limits and show error images, sometimes for days.
3. **Private work is invisible.** A public server cannot see the contributions you made in private repositories.

## The approach

```
              profile.toml
                   │  validate against profilekit/schema.json
                   ▼
            profilekit build ───────────────┐
           │                │               │
     static graphics   live graphics    README.md
       assets/*.svg      dist/*.svg     (CUSTOM block kept)
           │                │               │
     commit to main   force-push to    commit to main
                      branch "output"
           └────────────────┴───────────────┘
                            │
             GitHub renders README.md, which embeds
             ./assets/*.svg and raw.githubusercontent.com/.../output/*.svg
```

### One renderer, one design language

Every graphic comes from the same Python package and the same theme tokens (`profilekit/core.py`). The default theme `ink` uses neutral greys, one violet accent and an orange highlight, with Inter for text and JetBrains Mono for data and code. Because one program draws everything, the header, the cards, the stats and the skyline share spacing, radii and colours.

### Animation without JavaScript

GitHub shows README images through `<img>`. An SVG inside `<img>` may animate, but it cannot run scripts or load external files. So:

- **Animations are CSS keyframes and SMIL** (`<animate>`, `<animateMotion>`, `<animateTransform>`) inside each SVG. SMIL covers what CSS cannot do in this context, such as animating a clip path's width for the typing effect in the terminal.
- **Fonts are embedded** as base64 WOFF2 in every SVG that uses them. That is why a graphic weighs 65 to 130 KB, depending on whether it needs one or both fonts.
- **Light and dark mode** are two files per graphic, switched by `<picture><source media="(prefers-color-scheme: dark)">`. A single SVG cannot follow the viewer's GitHub theme.
- **Reduced motion is respected.** Under `prefers-reduced-motion: reduce`, animations stop and every element shows its final state.

### Static and live parts, split by branch

Graphics that only change when you change the config (header, cards, terminal) live in `assets/` on `main`. Graphics that change with the world (contribution stats, skyline with weather, star counts) are rebuilt every 30 minutes and force-pushed to a separate `output` branch.

This keeps the history of `main` readable. Thirty-minute weather updates on `main` would produce 48 commits a day. The README points at the `output` branch with absolute raw URLs, so live images update without touching `main`.

### Live data without a server

The workflow runs inside your own repository with the `GITHUB_TOKEN` that Actions provides:

- **Contributions** come from the GraphQL `contributionCalendar` of your account. It includes private contributions if you allow that in your profile settings, which a public stats server can never see.
- **Weather, sunrise and sunset** come from [Open-Meteo](https://open-meteo.com), which needs no API key. The skyline is `dusk` within 30 minutes of sunrise or sunset, `day` between them and `night` otherwise, computed in the city's own time zone.
- **Stars and languages** of recommended repositories come from the REST API.

Any network failure falls back (sample calendar, day and clear sky, last known values) and is reported in the build `notes`. A failed weather request never blanks your profile.

### A city from its name

A hand-drawn skyline takes hours per city, so the default is procedural. `layer_generic` in `profilekit/skyline.py` seeds a random number generator with the lower-cased city name. The same name always produces the same buildings, so the skyline does not reshuffle every 30 minutes, while two cities look different. Landmarks you choose get fixed slots, buildings fill the gaps around them.

### One schema for people and agents

`profilekit/schema.json` is the single source of truth for the config. The validator in `profilekit/config.py` reads that file instead of duplicating its rules, `python3 -m profilekit schema` prints it for agents, and `docs/gen_reference.py` turns it into the [config reference](reference-config.md). The `maxLength` values are layout limits measured against the graphics, so a valid config is also one whose text fits.

Every command has `--json` output and stable exit codes, and the procedure an agent should follow is a standard [Agent Skill](../skills/github-profile/SKILL.md). An agent never has to parse prose or guess a key name.

### Safe handling of visitor input

The light-up game turns a stranger's issue title into a commit. The workflow never interpolates the title or the author into a shell command. Both travel only through environment variables into `profilekit lightup`, which accepts nothing but `light: <colour>` with one of seven fixed colours and a syntactically valid GitHub login. Everything else is closed as "not planned".

## Trade-offs

| Choice | What it costs |
|---|---|
| Python standard library only | No SVG or font libraries. Text width is estimated from fixed advance widths, so layout limits are enforced by `maxLength` instead of measurement. |
| Embedded fonts | 65 to 130 KB per graphic, roughly 2.6 MB for a full profile in both modes. The kit cannot subset fonts without a dependency. |
| Two files per graphic | Twice the files and builds, in exchange for a correct light and dark mode. |
| `output` branch force-pushed | No history of live graphics. Old stats and skylines are gone. |
| 30-minute schedule | Weather and time of day can be up to 30 minutes behind, plus up to 5 minutes of image cache. GitHub may also delay scheduled runs under load. |
| Procedural cities | The skyline is plausible, not your real city. Real cities need a hand-drawn layer ([how to add one](howto-add-a-hand-drawn-city.md)). |
| Profile repository only | The workflows do nothing in a repository that is not named like its owner. That protects the kit repository, but you cannot test the full flow in a fork with another name. |

## Alternatives that were not taken

- **A hosted service that renders images on request** would update instantly, but it is exactly the shared, rate-limited server this kit avoids, and it could not see private contributions.
- **One huge SVG for the whole profile** would allow cross-section animation, but it would load slowly through GitHub's image proxy, and the README would lose its headings, links and per-section alt texts.
- **Committing live graphics to `main`** is simpler, but floods the history with weather commits.
