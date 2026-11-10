# Reference: workflows

Two GitHub Actions workflows keep a profile alive. Both live in `.github/workflows/` and both only do work in a **profile repository**, the one named exactly like its owner (`octocat/octocat`). In the kit repository itself they skip.

## `profile.yml`

Builds the profile and publishes the live graphics.

| Trigger | When |
|---|---|
| `schedule` | Every 30 minutes (`*/30 * * * *`): new contribution numbers, time of day, weather and star counts. |
| `push` to `main` | After every change, for example an edit of `profile.toml` in the browser. |
| `workflow_dispatch` | By hand from the Actions tab, and from `lightup.yml`. |

Permissions: `contents: write`. Concurrency group `profile`, runs are queued, never cancelled.

| Step | Does |
|---|---|
| Draft `profile.toml` on first run | Only when `profile.toml` does not exist: `python3 -m profilekit init --from-github --handle <owner>`. |
| Build | `python3 -m profilekit build` with `GITHUB_TOKEN`. |
| Commit README and static graphics | Commits `README.md`, `assets/` and `profile.toml` to `main` if anything changed. Pushes made with `GITHUB_TOKEN` do not trigger new workflow runs, so this cannot loop. |
| Publish live graphics | Force-pushes `dist/` to the `output` branch with `crazy-max/ghaction-github-pages@v4`. |

The README references live graphics as `https://raw.githubusercontent.com/<owner>/<repo>/output/<file>.svg`. GitHub caches these images for up to five minutes.

## `lightup.yml`

Lets visitors colour your skyline.

| Trigger | `issues: opened` with a title starting with `light:` |
|---|---|
| Permissions | `contents: write` (commit the colour), `issues: write` (comment and close), `actions: write` (start `profile.yml`) |
| Concurrency | group `lightup`, queued |

| Step | Does |
|---|---|
| Validate | Passes the issue title and author **only through environment variables** to `python3 -m profilekit lightup`, which accepts `light: <colour>` with one of seven colours and a valid GitHub login. |
| Commit | Writes `state/lightup.json`, commits `lit <colour> via #<issue>`, pushes and runs `gh workflow run profile.yml`. The explicit dispatch is needed because a push made with `GITHUB_TOKEN` starts no workflow. |
| Reply | Thanks the visitor and closes the issue, or closes an invalid request as "not planned" with the list of colours. |

The colour lights the TV tower's pod when the city has a `tower` landmark, otherwise the rooftop sign. The visitor's handle appears next to it as `lit by @handle`.

## Files the workflows touch

| Path | Branch | Written by |
|---|---|---|
| `README.md`, `assets/` | `main` | `profile.yml` |
| `profile.toml` | `main` | `profile.yml` on the first run only |
| `state/lightup.json` | `main` | `lightup.yml` |
| all of `dist/` | `output` (force-pushed, history not kept) | `profile.yml` |

## Related

- [How to turn on live data and the light-up game](howto-turn-on-live-data-and-light-up.md)
- [Explanation: how the kit works](explanation-how-it-works.md)
- [Reference: CLI](reference-cli.md)
