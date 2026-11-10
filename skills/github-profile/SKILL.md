---
name: github-profile
description: Create or update an animated, living GitHub profile README with github-profile-kit (one profile.toml, a GitHub Action, live stats, a skyline with real weather). Use when someone asks to make, pimp, redesign or refresh a GitHub profile, or when an agent with its own GitHub account wants a profile of its own.
---

# GitHub profile with github-profile-kit

You turn one `profile.toml` into a complete profile README: header, contact row, focus cards, terminal, recommended repos, contribution stats and a living skyline. A GitHub Action rebuilds it every 30 minutes. No dependencies beyond Python 3.11 and `gh`.

## Ground rules

- **Publishing is outward-facing.** A profile README is public. Before you push or create a public repository, show the human what will be published (the `preview` output or the README text) and get a clear yes, unless they already told you to publish. An autonomous agent publishing its *own* profile follows its operator's rules.
- **Never overwrite an existing profile README without consent.** If `<login>/<login>` already has a README, move its text into the `<!-- CUSTOM:START -->` block of the generated README, or ask.
- **Only real facts.** Every line in `profile.toml` must be true for the person (or agent). Draft from public data, then confirm what you could not verify. Do not invent employers, numbers or projects.
- **Validate before you build.** `validate --json` returns machine-readable errors with a JSON path; fix exactly those keys.

## Procedure

1. **Identify the account.** `gh api user --jq .login` gives the login of the authenticated account. The profile repository must be named exactly like the login: `<login>/<login>`.
2. **Get the kit into that repository.**
   - Repository does not exist: `gh repo create <login>/<login> --public --template onetechgroupll/github-profile-kit --clone` (confirm first, see ground rules).
   - Repository exists: clone it, then copy `profilekit/`, `.github/workflows/`, `skills/`, `AGENTS.md` from the kit into it.
3. **Draft the config.** In the repository root: `python3 -m profilekit init --from-github --handle <login>`. This reads name, company, location, bio and top languages.
4. **Refine with the human** (or from the agent's own purpose). Ask for what public data cannot tell you, in one round:
   - 3 to 5 rotating words after "I build" (e.g. `"data pipelines."`)
   - up to four focus areas with two short lines each, and a visual per card: `auction`, `retail`, `sync`, `ledger`
   - links (https only; LinkedIn, website, Mastodon, Bluesky, X, RSS, mail)
   - city for the skyline with lat/lon/timezone, an optional 1-3 letter rooftop sign, landmarks from `tower bridge spire wheel dome`
   - optional terminal: whoami line, `--flags` with role descriptions, process names, principles
   - optional repos to recommend
   Every key, limit and allowed value: `python3 -m profilekit schema`.
5. **Validate:** `python3 -m profilekit --json validate`. Exit code 0 means valid. Otherwise fix each `errors[].path`; messages say why (most often a text that would not fit the graphic).
6. **Preview:** `python3 -m profilekit preview` writes `assets/`, `dist/`, `README.md` and `preview.html` with sample data for live graphics. If you can drive a browser, open `preview.html` and look at it in light and dark before publishing. Check that nothing overlaps or is cut off.
7. **Publish** (after consent): commit `profile.toml`, `README.md`, `assets/`, the workflows and push to `main`. The `profile` workflow then fetches live data and publishes `dist/` to the `output` branch, which the README references.
8. **Verify:** `gh run watch` on the profile workflow, then open `https://github.com/<login>`. Raw images are cached up to 5 minutes.
9. **Tell the human two manual steps** you cannot do for them:
   - Private contributions only count if they enable *Settings → Profile → Include private contributions on my profile*.
   - The avatar is not set by the kit. `assets/avatar-light.svg` is a square skyline crop they can convert and upload.

## Updating later

Edit `profile.toml`, run `validate`, push. Never edit `README.md` outside the CUSTOM block; it is regenerated. `python3 -m profilekit doctor` checks Python, config, remote name and workflows.

## Machine interface

All commands accept `--json` before the subcommand and return exit code 0 (ok), 1 (invalid / failed check) or 2 (usage):

| Command | Does |
|---|---|
| `init [--handle L] [--from-github] [--force]` | writes `profile.toml` |
| `validate` | checks against `profilekit/schema.json` |
| `build [--offline] [--phase] [--weather] [--season]` | renders everything; `GITHUB_TOKEN` enables live data |
| `preview` | offline build + `preview.html` |
| `schema` | prints the JSON Schema |
| `doctor` | environment and repository checks |
