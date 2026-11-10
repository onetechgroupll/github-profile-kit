# AGENTS.md

Instructions for coding agents (Claude Code, Codex, Cursor, OpenClaw, Hermes Agent and others) working in a repository that uses **github-profile-kit**.

## What this repository is

A GitHub profile README generated from `profile.toml`. Python 3.11+ standard library only; nothing to install.

- `profile.toml`: the only file a person edits. Schema: `profilekit/schema.json` (`python3 -m profilekit schema`).
- `README.md`: **generated**. Only the block between `<!-- CUSTOM:START -->` and `<!-- CUSTOM:END -->` survives a rebuild.
- `assets/`: static graphics, committed. `dist/`: live graphics, published to the `output` branch by CI, not committed.
- `profilekit/`: the renderer. `skills/github-profile/SKILL.md`: the end-to-end procedure for creating a profile.
- `docs/`: human documentation ([index](docs/README.md)). `docs/reference-config.md` is generated from the schema by `python3 docs/gen_reference.py`; regenerate it after every schema change.

## Commands

```bash
python3 -m profilekit --json validate     # exit 0 = valid; errors[].path + message otherwise
python3 -m profilekit preview             # offline build + preview.html
python3 -m profilekit --json build        # full build; GITHUB_TOKEN enables live data
python3 -m profilekit doctor              # environment + repo checks
```

## Rules

1. Change content in `profile.toml`, never in `README.md` or `assets/` by hand.
2. Run `validate` after every edit and `preview` before every push. Look at the preview in light and dark mode if you can open a browser.
3. A profile README is public. Get the person's consent before pushing, creating a public repository or overwriting an existing README.
4. Only write facts about the person you were told or could verify from public data.
5. When you change the renderer (`profilekit/`): keep it dependency-free, keep every text inside its graphic (the schema's `maxLength` values are the layout limits), render both themes (`ink`, `slate`) and both modes, and check that every SVG is well-formed XML.
6. The light-up workflow handles untrusted issue titles. Input only ever travels through environment variables into `profilekit lightup`, which validates it against a fixed colour list. Do not interpolate issue data into shell commands.
