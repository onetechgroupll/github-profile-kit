"""Command line: one tool for humans and agents. Every command supports --json and uses exit codes.

  python3 -m profilekit init [--handle LOGIN] [--from-github] [--force]
  python3 -m profilekit validate
  python3 -m profilekit build [--offline] [--phase day|dusk|night] [--weather ...] [--season ...]
  python3 -m profilekit preview            # offline build + preview.html with every graphic
  python3 -m profilekit schema             # JSON Schema of profile.toml
  python3 -m profilekit doctor             # environment and repository checks
  python3 -m profilekit lightup            # used by the light-up workflow (reads ISSUE_TITLE / ISSUE_USER)

Exit codes: 0 ok, 1 invalid config or failed check, 2 usage error.
"""
import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

from . import build, config, live

EXAMPLE = Path(__file__).resolve().parent / "example.toml"


def emit(args, payload, text):
    print(json.dumps(payload, indent=2, ensure_ascii=False) if args.json else text)


def toml_str(s):
    return json.dumps(s, ensure_ascii=False)


def clip(s, n):
    """Shorten to n characters at a word boundary."""
    s = " ".join((s or "").split())
    if len(s) <= n:
        return s
    cut = s[:n + 1].rsplit(" ", 1)[0].rstrip(" ,;·-")
    return cut or s[:n]


def draft_from_github(handle, token=None):
    """A first profile.toml drafted from public GitHub data. The agent or human refines it afterwards."""
    headers = {"Authorization": f"bearer {token}"} if token else {}
    u = live.http_json(f"https://api.github.com/users/{handle}", headers=headers)
    repos = live.http_json(f"https://api.github.com/users/{handle}/repos?per_page=100&sort=pushed", headers=headers)
    langs = {}
    for r in repos:
        if r.get("language") and not r.get("fork"):
            langs[r["language"]] = langs.get(r["language"], 0) + 1
    top = [k for k, _ in sorted(langs.items(), key=lambda kv: -kv[1])][:4]
    name = clip(u.get("name") or handle, 28)
    lines = ["# Drafted from public GitHub data by `profilekit init --from-github`. Refine every line, then run",
             "# `python3 -m profilekit validate` and `python3 -m profilekit build`. Schema: profilekit/schema.json", "",
             "[profile]", f"handle = {toml_str(handle)}", f"name = {toml_str(name)}"]
    kicker = clip((u.get("company") or "").strip().lstrip("@"), 60)
    if kicker:
        lines.append(f"kicker = {toml_str(kicker)}")
    words = [f"{lang}." for lang in top[:3]] or ["software."]
    lines += [f"words = {json.dumps(words)}", 'theme = "ink"', ""]
    if u.get("blog"):
        url = u["blog"] if u["blog"].startswith("http") else "https://" + u["blog"]
        if url.startswith("https://"):
            lines += ["[[links]]", 'label = "Website"', f"url = {toml_str(url)}", 'icon = "web"', ""]
    lines += ["[[links]]", 'label = "GitHub"', f'url = "https://github.com/{handle}"', 'icon = "github"', ""]
    if u.get("location"):
        lines += ["[status]", f"based_in = {toml_str(clip(u['location'], 28))}", ""]
    if u.get("bio"):
        lines += ["[terminal]", f"whoami = {toml_str(clip(u['bio'], 48))}", ""]
    lines += ["[contributions]", "stats = true", "settle = true", "",
              "# Add [city] with name, lat, lon and timezone to get the living skyline.", ""]
    return "\n".join(lines)


def cmd_init(args, root):
    target = root / "profile.toml"
    if target.exists() and not args.force:
        emit(args, dict(ok=False, error="profile.toml exists; pass --force to overwrite"), "profile.toml exists; pass --force to overwrite")
        return 1
    handle = args.handle
    if not handle and sys.stdin.isatty() and not args.json:
        handle = input("GitHub login: ").strip()
    if args.from_github:
        if not handle:
            emit(args, dict(ok=False, error="--from-github needs --handle"), "--from-github needs --handle")
            return 2
        try:
            text = draft_from_github(handle, os.environ.get("GITHUB_TOKEN"))
        except Exception as e:
            emit(args, dict(ok=False, error=f"GitHub lookup failed: {e}"), f"GitHub lookup failed: {e}")
            return 1
    else:
        text = EXAMPLE.read_text(encoding="utf-8")
        if handle:
            text = text.replace('handle = "octocat"', f'handle = {toml_str(handle)}', 1)
    target.write_text(text, encoding="utf-8")
    _, errors = config.load(target)
    emit(args, dict(ok=not errors, written="profile.toml", errors=errors,
                    next=["edit profile.toml", "python3 -m profilekit validate", "python3 -m profilekit preview"]),
         f"wrote profile.toml{' (has validation errors, run validate)' if errors else ''}\n"
         "next: edit it, then `python3 -m profilekit preview`")
    return 0


def cmd_validate(args, root):
    _, errors = config.load(root / args.config)
    text = f"{args.config} is valid" if not errors else "\n".join(f"{e['path'] or '/'}: {e['message']}" for e in errors)
    emit(args, dict(ok=not errors, errors=errors), text)
    return 0 if not errors else 1


def cmd_build(args, root, offline=None):
    cfg, errors = config.load(root / args.config)
    if errors:
        emit(args, dict(ok=False, errors=errors), "\n".join(f"{e['path'] or '/'}: {e['message']}" for e in errors))
        return 1
    res = build.render(cfg, root, offline=args.offline if offline is None else offline,
                       phase=getattr(args, "phase", None), weather=getattr(args, "weather", None),
                       season=getattr(args, "season", None))
    emit(args, dict(ok=True, **res), "\n".join(res["written"] + [f"note: {n}" for n in res["notes"]]))
    return 0


def cmd_preview(args, root):
    rc = cmd_build(args, root, offline=True)
    if rc:
        return rc
    imgs = sorted(p for p in list((root / "assets").glob("*.svg")) + list((root / "dist").glob("*.svg")))
    cells = "".join(f'<figure><img src="{p.relative_to(root)}"><figcaption>{p.relative_to(root)}</figcaption></figure>' for p in imgs)
    (root / "preview.html").write_text(
        "<!doctype html><meta charset=utf-8><title>profile preview</title><style>"
        "body{font:13px system-ui;margin:24px;background:#f6f8fa}body.dark{background:#0d1117;color:#c9d1d9}"
        "figure{margin:0 0 20px}img{max-width:100%}button{position:fixed;top:12px;right:12px}"
        "</style><button onclick=\"document.body.classList.toggle('dark');for(const i of document.images)"
        "{i.src=i.src.replace(document.body.classList.contains('dark')?'-light.svg':'-dark.svg',"
        "document.body.classList.contains('dark')?'-dark.svg':'-light.svg')}\">light / dark</button>"
        + cells.replace("-dark.svg", "-light.svg"), encoding="utf-8")
    if not args.json:
        print("open preview.html in a browser (offline sample data for live graphics)")
    return 0


def cmd_doctor(args, root):
    checks = []

    def check(name, ok, hint=""):
        checks.append(dict(check=name, ok=bool(ok), hint="" if ok else hint))

    check("python >= 3.11", sys.version_info >= (3, 11), "install Python 3.11 or newer (tomllib)")
    cfg, errors = config.load(root / args.config)
    check("profile.toml valid", not errors, "run `python3 -m profilekit validate`")
    try:
        remote = subprocess.run(["git", "remote", "get-url", "origin"], cwd=root, capture_output=True, text=True).stdout.strip()
    except OSError:
        remote = ""
    if cfg and not errors:
        repo = cfg["profile"]["repo"]
        check("git remote matches [profile].repo", repo.lower() in remote.lower().removesuffix(".git"),
              f"origin is '{remote or 'missing'}'; the profile README only shows from github.com/{repo}")
        h = cfg["profile"]["handle"]
        check("profile repo is named like the handle", repo.lower() == f"{h}/{h}".lower(),
              "GitHub only shows README.md from the repository named exactly like your login")
    check("profile workflow present", (root / ".github/workflows/profile.yml").exists(), "copy .github/workflows from the kit")
    ok = all(c["ok"] for c in checks)
    emit(args, dict(ok=ok, checks=checks),
         "\n".join(f"{'ok ' if c['ok'] else 'FAIL'}  {c['check']}{'  -> ' + c['hint'] if c['hint'] else ''}" for c in checks))
    return 0 if ok else 1


def cmd_lightup(args, root):
    color = live.apply_lightup(root, os.environ.get("ISSUE_TITLE", ""), os.environ.get("ISSUE_USER", ""))
    print(f"result={'ok' if color else 'invalid'}")
    if color:
        print(f"color={color}")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(prog="profilekit", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument("--root", default=".", help="profile repository root")
    ap.add_argument("--config", default="profile.toml")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("init")
    p.add_argument("--handle")
    p.add_argument("--from-github", action="store_true")
    p.add_argument("--force", action="store_true")
    sub.add_parser("validate")
    p = sub.add_parser("build")
    p.add_argument("--offline", action="store_true", help="no network: sample contributions, day/clear skyline")
    p.add_argument("--phase", choices=["day", "dusk", "night"])
    p.add_argument("--weather", choices=["clear", "partly", "cloudy", "fog", "rain", "snow", "storm"])
    p.add_argument("--season", choices=["newyear", "advent", "christmas", "karneval", "hoppeditz"])
    p = sub.add_parser("preview")
    p.add_argument("--phase", choices=["day", "dusk", "night"])
    p.add_argument("--weather", choices=["clear", "partly", "cloudy", "fog", "rain", "snow", "storm"])
    p.add_argument("--season", choices=["newyear", "advent", "christmas", "karneval", "hoppeditz"])
    sub.add_parser("schema")
    sub.add_parser("doctor")
    sub.add_parser("lightup")
    args = ap.parse_args(argv)
    root = Path(args.root).resolve()
    if args.cmd == "schema":
        print(json.dumps(config.schema(), indent=2, ensure_ascii=False))
        return 0
    return {"init": cmd_init, "validate": cmd_validate, "build": cmd_build, "preview": cmd_preview,
            "doctor": cmd_doctor, "lightup": cmd_lightup}[args.cmd](args, root)
