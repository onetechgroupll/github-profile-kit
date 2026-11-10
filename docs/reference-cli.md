# Reference: the `profilekit` CLI

`profilekit` renders every graphic and the README from `profile.toml`. It needs Python 3.11 or newer and nothing else. Run it from the root of your profile repository:

```bash
python3 -m profilekit [global options] <command> [command options]
```

To learn by doing, start with the [tutorial](tutorial-your-first-profile.md). For the config keys, see the [config reference](reference-config.md).

## Global options

Global options go **before** the command.

| Option | Default | Effect |
|---|---|---|
| `--json` | off | Print one JSON object instead of text. Every command supports it. |
| `--root PATH` | `.` | Profile repository root. `assets/`, `dist/`, `README.md`, `state/` and `preview.html` are written here. |
| `--config FILE` | `profile.toml` | Config file, relative to `--root`. |

```bash
python3 -m profilekit --json validate                       # right
python3 -m profilekit validate --json                       # wrong: argparse rejects it
python3 -m profilekit --config examples/agent.toml validate
```

## Exit codes

| Code | Meaning |
|---|---|
| `0` | Success, or a valid config. |
| `1` | Invalid config, failed check, or a refused write (for example `init` on an existing file). |
| `2` | Usage error from the argument parser, such as an unknown option or an invalid choice. |

## Commands

### `init`

Writes `profile.toml`.

| Option | Effect |
|---|---|
| `--handle LOGIN` | Your GitHub login. Without `--from-github`, it replaces `octocat` in the example config. In an interactive terminal without `--json`, `init` asks for it. |
| `--from-github` | Drafts the config from public GitHub data: name, company (as kicker), blog (as a Website link), location (as `based_in`), bio (as `whoami`) and your top three languages as rotating words. Needs `--handle`. Uses `GITHUB_TOKEN` when set. |
| `--force` | Overwrite an existing `profile.toml`. Without it, `init` refuses and exits with `1`. |

Without `--from-github`, `init` copies [`profilekit/example.toml`](../profilekit/example.toml), which switches every section on.

```json
{
  "ok": true,
  "written": "profile.toml",
  "errors": [],
  "next": ["edit profile.toml", "python3 -m profilekit validate", "python3 -m profilekit preview"]
}
```

`errors` holds validation errors of the written file. A drafted file is normally valid.

### `validate`

Checks the config against [`profilekit/schema.json`](../profilekit/schema.json). Exit code `0` when valid, `1` otherwise.

```json
{
  "ok": false,
  "errors": [
    {"path": "/profile/name", "message": "is 53 characters, max 28 (it would not fit the graphic)"},
    {"path": "/profile/theme", "message": "must be one of ['ink', 'slate']"},
    {"path": "/profile/color", "message": "is not a known key (known keys: handle, name, kicker, build_prefix, words, theme, accent, repo, credit)"},
    {"path": "/city/lon", "message": "is required"}
  ]
}
```

`path` is a JSON pointer into the config: `/focus/2/title` is the `title` of the third `[[focus]]` table. A TOML syntax error returns one error with an empty path and the parser message.

### `build`

Renders everything and rewrites `README.md`.

| Option | Effect |
|---|---|
| `--offline` | No network. Contributions use a plausible sample calendar, the skyline uses day and clear weather, recommendations keep only what the config says. |
| `--phase day\|dusk\|night` | Force the time of day of the skyline. |
| `--weather clear\|partly\|cloudy\|fog\|rain\|snow\|storm` | Force the weather. |
| `--season newyear\|advent\|christmas\|karneval\|hoppeditz` | Force a seasonal decoration, even if it is not in `[city].seasons`. |

Online, `build` uses `GITHUB_TOKEN` for the contribution calendar (GraphQL) and for repository stars. Without a token it falls back to sample contributions and unauthenticated repository requests. Network failures never fail the build; they show up in `notes`.

| Writes | Contents |
|---|---|
| `assets/` | Static graphics, committed to `main`: `header`, `focus`, `terminal`, `org`, `btn-<n>`, `status`, `light-<colour>`, `avatar`, each as `-light.svg` and `-dark.svg`. |
| `dist/` | Live graphics, published to the `output` branch: `stats`, `settle`, `skyline`, `rec-<owner>--<repo>`, each light and dark. |
| `README.md` | The profile. The text between `<!-- CUSTOM:START -->` and `<!-- CUSTOM:END -->` is kept. |

```json
{
  "ok": true,
  "written": ["assets/header-light.svg", "...", "README.md"],
  "notes": ["contributions: sample data (offline or no GITHUB_TOKEN)"],
  "weather": {"phase": "day", "weather": "clear", "temp": null, "season": null},
  "lightup": {"color": null, "user": null}
}
```

An invalid config makes `build` print the validation errors and exit with `1` without writing anything.

### `preview`

Runs an offline `build` (accepts `--phase`, `--weather`, `--season`) and writes `preview.html`, a page with every graphic and a light/dark toggle. Open it in a browser. `preview.html` and `dist/` are in `.gitignore`.

### `schema`

Prints the JSON Schema of `profile.toml`. Agents use it to learn every key, allowed value and limit.

### `doctor`

Checks the environment and the repository. Exit code `0` only when every check passes.

| Check | Fails when |
|---|---|
| `python >= 3.11` | Python is older (no `tomllib`). |
| `profile.toml valid` | The config has validation errors. |
| `git remote matches [profile].repo` | `origin` is missing or points elsewhere. |
| `profile repo is named like the handle` | `[profile].repo` is not `<handle>/<handle>`. GitHub only shows the README of that repository on your profile. |
| `profile workflow present` | `.github/workflows/profile.yml` is missing. |

### `lightup`

Used by the [light-up workflow](reference-workflows.md#lightupyml). Reads `ISSUE_TITLE` and `ISSUE_USER` from the environment, accepts titles of the form `light: <colour>` with one of `blue`, `red`, `green`, `purple`, `orange`, `pink`, `gold`, and writes `state/lightup.json`. Prints `result=ok` and `color=<colour>`, or `result=invalid`, in `$GITHUB_OUTPUT` format. Always exits `0`.

## Environment variables

| Variable | Used by | Effect |
|---|---|---|
| `GITHUB_TOKEN` | `build`, `init --from-github` | Contribution calendar (required for real data), higher API limits for stars and user data. |
| `ISSUE_TITLE`, `ISSUE_USER` | `lightup` | The issue that requests a colour. |

## Related

- [How to let an agent build your profile](howto-let-an-agent-build-your-profile.md)
- [Reference: workflows](reference-workflows.md)
- [Explanation: how the kit works](explanation-how-it-works.md)
