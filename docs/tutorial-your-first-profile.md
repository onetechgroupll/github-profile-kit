# Tutorial: your first living profile

In about ten minutes you will turn your GitHub profile into an animated page: a header with rotating words, focus cards, contribution stats, and a skyline of your city that follows the real time of day and weather. You will see the first result on your own machine after three steps, before anything goes public.

## What you'll need

- A GitHub account and the [GitHub CLI](https://cli.github.com) logged in: `gh auth status` shows your login.
- Python 3.11 or newer: `python3 --version`.
- Git.
- No profile repository yet. If `github.com/<you>/<you>` already exists, see [Already have a profile repository?](#already-have-a-profile-repository) at the end.

In the commands below, replace `<you>` with your GitHub login.

## Step 1: Create your profile repository from the template

GitHub shows the README of the repository named exactly like your login on your profile page. Create it from the kit, privately for now, so nothing is visible while you work:

```bash
gh repo create <you>/<you> --private --template onetechgroupll/github-profile-kit --clone
cd <you>
```

You now have the kit locally: the `profilekit/` renderer, two workflows and the docs.

## Step 2: Draft your config from your GitHub account

```bash
python3 -m profilekit init --from-github --handle <you>
```

```text
wrote profile.toml
next: edit it, then `python3 -m profilekit preview`
```

Open `profile.toml`. It already holds your name, company, location, bio and your top languages as rotating words.

## Step 3: See it

```bash
python3 -m profilekit preview
```

Open `preview.html` in your browser. You see your header, the contact row and the contribution graphics, filled with sample data until the workflow fetches the real calendar. Click **light / dark** in the top right to check both modes.

That is your profile. The rest of this tutorial makes it yours.

## Step 4: Say what you build

Replace the drafted words with what you actually do, and add two focus cards. Edit `profile.toml`:

```toml
[profile]
handle = "<you>"
name = "Your Name"
kicker = "Founder · Your Company"
words = ["developer tools.", "data pipelines.", "mobile apps."]

[[focus]]
title = "Developer Tools"
line1 = "CLIs and SDKs that feel"
line2 = "obvious on day one."
tags = ["CLI", "SDK"]
visual = "auction"

[[focus]]
title = "Data Pipelines"
line1 = "From raw events"
line2 = "to answers people trust."
tags = ["ETL"]
visual = "retail"
```

Check it:

```bash
python3 -m profilekit validate
```

If a text is too long for its graphic, the error tells you exactly which one, for example `/focus/0/line1: is 35 characters, max 32 (it would not fit the graphic)`. Shorten it and validate again. Run `preview` and reload the page: the header now rotates through your words, and two cards with small animations appear under **What I build**.

## Step 5: Add your city

Add a skyline. Use your city's coordinates and time zone, so day and night match reality:

```toml
[city]
name = "Hamburg"
lat = 53.55
lon = 9.99
timezone = "Europe/Berlin"
sign = "HH"
landmarks = ["tower", "spire", "bridge"]
creatures = ["boats", "duck"]

[lightup]
title = "Light up the tower"
```

See it at night, in the snow:

```bash
python3 -m profilekit preview --phase night --weather snow
```

Reload `preview.html`: windows glow, stars are out, snow falls, and your sign shines on the glass tower. Your city's name decides how the buildings look, and it always produces the same skyline.

## Step 6: Publish

Commit everything and push. The push starts the `profile` workflow, which fetches your real contribution calendar, the weather in your city and builds the live graphics:

```bash
git add -A
git commit -m "My profile"
git push
gh run watch
```

When the run is green, make the repository public. GitHub only shows a profile README from a public repository:

```bash
gh repo edit <you>/<you> --visibility public --accept-visibility-change-consequences
```

## Step 7: Look at your profile

Open `https://github.com/<you>`. The header types and rotates, the cards animate, the stats show your real numbers, and the skyline shows the current time of day and weather in your city. It refreshes every 30 minutes on its own.

Two things only you can do:

- **Count private work:** *Settings → Profile → Include private contributions on my profile*.
- **Set a matching avatar:** `assets/avatar-light.svg` is a square crop of your skyline. Convert it to PNG and upload it in *Settings → Profile*.

## What you built

A profile that keeps itself current. You edit one file, `profile.toml`; a GitHub Action does the rest, every 30 minutes and after every push, in your own repository with no outside service. Visitors can open an issue like `light: purple` and your tower glows in their colour.

Where to go next:

- Every key with its limits: [Reference: profile.toml](reference-config.md)
- Landmarks, flags, river life and seasons: [How to design your skyline](howto-design-your-skyline.md)
- Live stars, private contributions and the light-up game: [How to turn on live data and the light-up game](howto-turn-on-live-data-and-light-up.md)
- Let an agent maintain it: [How to let an agent build your profile](howto-let-an-agent-build-your-profile.md)
- Why it works this way: [Explanation](explanation-how-it-works.md)

## Already have a profile repository?

Clone it, copy the kit into it and keep your old text:

```bash
gh repo clone <you>/<you> && cd <you>
git clone --depth 1 https://github.com/onetechgroupll/github-profile-kit /tmp/kit
cp -r /tmp/kit/profilekit /tmp/kit/.github .
cp README.md /tmp/old-readme.md
python3 -m profilekit init --from-github --handle <you>
python3 -m profilekit build --offline
```

Then paste the parts of `/tmp/old-readme.md` you want to keep between `<!-- CUSTOM:START -->` and `<!-- CUSTOM:END -->` in the new `README.md`. That block survives every rebuild. Continue with step 4.
