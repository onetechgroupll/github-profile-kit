# How to let an agent build your profile

Hand the whole job to a coding agent (Claude Code, Codex, Cursor) or give an autonomous agent (OpenClaw, Hermes Agent) the skill to build a profile for its own GitHub account.

## Prerequisites

- The agent can run shell commands and has the GitHub CLI `gh` logged in to the account the profile is for (`gh auth status`).
- Python 3.11 or newer on that machine (`python3 --version`).
- You know whether the agent may publish on its own. A profile is public; by default the skill makes the agent ask first.

## Steps for a coding agent

1. Paste this prompt into the agent:

   ```text
   Create my GitHub profile with https://github.com/onetechgroupll/github-profile-kit.
   Follow skills/github-profile/SKILL.md from that repository. Ask me before you publish anything.
   ```

2. Answer the agent's one round of questions. Public data covers your name, company, location and languages. The agent asks for what it cannot know: the rotating words, up to four focus areas, links, your city and optional terminal lines.

3. Review the preview. The agent runs `python3 -m profilekit preview` and either opens `preview.html` in a browser or shows you the generated README. Ask for changes in plain language; the agent edits `profile.toml` and validates again.

4. Approve publishing. The agent pushes to `<login>/<login>`, and the `profile` workflow fetches live data.

If the agent works inside a repository created from the template, it finds the same instructions in `AGENTS.md` (read by Codex, Cursor and others) and `CLAUDE.md` (read by Claude Code), and the skill under `.claude/skills/` and `.agents/skills/`.

## Steps for an autonomous agent

1. Copy the skill folder into the agent's skills directory:

   ```bash
   git clone --depth 1 https://github.com/onetechgroupll/github-profile-kit /tmp/github-profile-kit
   cp -r /tmp/github-profile-kit/skills/github-profile ~/.hermes/skills/          # Hermes Agent
   # OpenClaw: copy it into the skills/ folder of the agent's workspace
   ```

   The folder is a standard [agentskills.io](https://agentskills.io) skill: a `SKILL.md` with `name` and `description` frontmatter.

2. Tell the agent to build its own profile, for example: "Build a GitHub profile for your account with the github-profile skill. Describe what you do, where you run and which tools you use."

3. Point it at [`examples/agent.toml`](../examples/agent.toml) as a model: `build_prefix = "I run"`, words for its jobs, the `slate` theme, a hub fed by issues, pull requests, cron and chat, and its operator in `whoami`.

4. Decide the publishing rule in the agent's own instructions. The skill tells it to follow its operator's rules when it publishes its own profile.

## Verification

```bash
gh repo view <login>/<login> --json visibility,url
gh run list -R <login>/<login> -w profile -L 1
```

The latest `profile` run should be `completed` and `success`. Then open `https://github.com/<login>`; images can lag up to five minutes behind because of GitHub's image cache.

## Troubleshooting

| Symptom | Cause and fix |
|---|---|
| The agent wants to overwrite an existing README | The skill forbids that without consent. Tell it to move the old text into the `<!-- CUSTOM:START -->` block. |
| `validate` keeps failing on a text | The text is longer than its graphic allows. The error names the key and the limit, for example `/focus/1/line1: is 35 characters, max 32`. Shorten it. |
| The workflow run was skipped | The repository is not named exactly like the account. Rename it to `<login>`. |
| Contributions show only public activity | Turn on *Settings → Profile → Include private contributions on my profile*. An agent cannot do this for you. |
| The agent invents facts | Tell it which lines are wrong. The skill requires real facts only, so ask it to remove anything it could not verify. |

## Related

- [The skill itself](../skills/github-profile/SKILL.md)
- [Reference: CLI](reference-cli.md) · [Reference: profile.toml](reference-config.md)
- [Tutorial: your first profile](tutorial-your-first-profile.md)
