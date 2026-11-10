# Documentation

Pick the page that matches what you want right now.

| I want to… | Read |
|---|---|
| **learn** the kit by building my first profile | [Tutorial: your first living profile](tutorial-your-first-profile.md) |
| **get a task done** | [How to let an agent build your profile](howto-let-an-agent-build-your-profile.md) |
| | [How to design your skyline](howto-design-your-skyline.md) |
| | [How to turn on live data and the light-up game](howto-turn-on-live-data-and-light-up.md) |
| | [How to add a hand-drawn city](howto-add-a-hand-drawn-city.md) |
| **look something up** | [Reference: profile.toml](reference-config.md) (generated from the schema) |
| | [Reference: the `profilekit` CLI](reference-cli.md) |
| | [Reference: workflows](reference-workflows.md) |
| **understand** why it works this way | [Explanation: how the kit works](explanation-how-it-works.md) |

For agents: the end-to-end procedure is [`skills/github-profile/SKILL.md`](../skills/github-profile/SKILL.md), repository rules are in [`AGENTS.md`](../AGENTS.md).

## Keeping the docs current

`reference-config.md` is generated. After changing `profilekit/schema.json`, run:

```bash
python3 docs/gen_reference.py           # rewrite the reference
python3 docs/gen_reference.py --check   # exit 1 if it is stale
```

The images in `docs/img/` come from `python3 docs/build_examples.py`.
