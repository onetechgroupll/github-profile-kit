# How to turn on live data and the light-up game

Get real contribution numbers (including private work), live star counts for the repositories you recommend, and let visitors colour your skyline.

## Prerequisites

- Your profile repository is named exactly like your login and is public: `<login>/<login>`.
- `.github/workflows/profile.yml` and `.github/workflows/lightup.yml` are in it (they come with the template).
- Actions are enabled for the repository (*Actions* tab; GitHub asks once for repositories created from a template).

## Steps

1. Turn on the contribution graphics:

   ```toml
   [contributions]
   stats = true     # four tiles and a bar per month
   settle = true    # the calendar that settles into weekly bars
   ```

   An empty `[contributions]` table enables both.

2. Let your private contributions count. On GitHub, open *Settings → Profile → Contributions & activity* and turn on **Include private contributions on my profile**. Without this, the calendar only contains public activity. Repository names stay hidden either way; only counts are shown.

3. Recommend repositories. Each gets a card with live language and stars:

   ```toml
   [[recommend]]
   repo = "astral-sh/uv"
   tag = "PYTHON"
   line1 = "An extremely fast Python package"
   line2 = "and project manager."
   ```

   Without `line1`, the card uses the start of the repository description.

4. Switch on the light-up game. It needs a skyline with a `tower` landmark or a `sign` (see [how to design your skyline](howto-design-your-skyline.md)):

   ```toml
   [lightup]
   enabled = true
   title = "Light up the tower"
   ```

   The README gets seven colour links. Each opens a pre-filled issue `light: <colour>`. Visitors only have to submit it.

5. Commit and push. The push starts the `profile` workflow; after that it runs every 30 minutes.

## Verification

```bash
gh run list -R <login>/<login> -w profile -L 1        # completed, success
gh api repos/<login>/<login>/branches/output --jq .name   # "output" exists
```

Test the game yourself: open one of the colour links on your profile and submit the issue. Within about a minute the bot comments, closes the issue and starts a rebuild; a few minutes later your skyline shows the colour and `lit by @<you>`.

## Troubleshooting

| Symptom | Cause and fix |
|---|---|
| Stats show sample-looking numbers locally | Local builds without `GITHUB_TOKEN` use a sample calendar. Run `GITHUB_TOKEN=$(gh auth token) python3 -m profilekit build` for real data, or rely on the workflow. |
| Images are broken right after the first push | The `output` branch does not exist until the first `profile` run finishes. Wait for it, then reload. |
| Images update late | GitHub caches README images for up to five minutes, and scheduled runs can be delayed under load. |
| The light-up issue stays open | The title must start with `light:` and name one of `blue`, `red`, `green`, `purple`, `orange`, `pink`, `gold`. Anything else is closed as "not planned". If nothing happens at all, check that Actions are enabled and that the repository is named like your login. |
| Stars show 0 or are missing | The repository name in `repo` is wrong or the repository is private. The build keeps going and logs `repo info unavailable` in its notes. |

## Related

- [Reference: workflows](reference-workflows.md)
- [Reference: `[contributions]`, `[[recommend]]`, `[lightup]`](reference-config.md#contributions)
- [Explanation: live data without a server](explanation-how-it-works.md#live-data-without-a-server)
