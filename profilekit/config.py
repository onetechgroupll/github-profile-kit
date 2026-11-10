"""Load and validate profile.toml against profilekit/schema.json (stdlib only)."""
import json
import re
import tomllib
from pathlib import Path

SCHEMA_PATH = Path(__file__).resolve().parent / "schema.json"
DEFAULT_SECTIONS = ["header", "contact", "focus", "org", "terminal", "recommend", "contributions", "city", "lightup"]


def schema():
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


_TYPES = {"object": dict, "array": list, "string": str, "boolean": bool}


def _check(value, sch, path, errors):
    """Validate the subset of JSON Schema the kit uses. Appends {path, message} dicts."""
    where = path or "/"
    typ = sch.get("type")
    if typ:
        if typ == "number":
            ok = isinstance(value, (int, float)) and not isinstance(value, bool)
        else:  # bool is a subclass of int in Python; only "boolean" may hold one
            ok = isinstance(value, _TYPES[typ]) and (typ == "boolean" or not isinstance(value, bool))
        if not ok:
            errors.append(dict(path=where, message=f"must be of type {typ}"))
            return
    if "enum" in sch and value not in sch["enum"]:
        errors.append(dict(path=where, message=f"must be one of {sch['enum']}"))
        return
    if isinstance(value, str):
        if "maxLength" in sch and len(value) > sch["maxLength"]:
            errors.append(dict(path=where, message=f"is {len(value)} characters, max {sch['maxLength']} (it would not fit the graphic)"))
        if "pattern" in sch and not re.search(sch["pattern"], value):
            errors.append(dict(path=where, message=f"does not match {sch['pattern']}"))
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if "minimum" in sch and value < sch["minimum"]:
            errors.append(dict(path=where, message=f"must be >= {sch['minimum']}"))
        if "maximum" in sch and value > sch["maximum"]:
            errors.append(dict(path=where, message=f"must be <= {sch['maximum']}"))
    if isinstance(value, list):
        if "maxItems" in sch and len(value) > sch["maxItems"]:
            errors.append(dict(path=where, message=f"has {len(value)} items, max {sch['maxItems']}"))
        if "minItems" in sch and len(value) < sch["minItems"]:
            errors.append(dict(path=where, message=f"needs at least {sch['minItems']} item(s)"))
        if sch.get("uniqueItems") and len(set(map(json.dumps, value))) != len(value):
            errors.append(dict(path=where, message="items must be unique"))
        for i, item in enumerate(value):
            if "items" in sch:
                _check(item, sch["items"], f"{path}/{i}", errors)
    if isinstance(value, dict):
        props = sch.get("properties", {})
        for req in sch.get("required", []):
            if req not in value:
                errors.append(dict(path=f"{path}/{req}", message="is required"))
        for k, v in value.items():
            if k in props:
                _check(v, props[k], f"{path}/{k}", errors)
            elif sch.get("additionalProperties") is False:
                hint = f" (known keys: {', '.join(props)})" if props else ""
                errors.append(dict(path=f"{path}/{k}", message=f"is not a known key{hint}"))


def validate(data):
    errors = []
    _check(data, schema(), "", errors)
    return errors


def load(path):
    """Return (config, errors). config has defaults applied when there are no errors."""
    p = Path(path)
    if not p.exists():
        return None, [dict(path="", message=f"{p} not found; run `python3 -m profilekit init`")]
    try:
        data = tomllib.loads(p.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError as e:
        return None, [dict(path="", message=f"TOML syntax error: {e}")]
    errors = validate(data)
    if errors:
        return data, errors
    return with_defaults(data), []


def with_defaults(d):
    d = json.loads(json.dumps(d))  # deep copy
    pr = d["profile"]
    pr.setdefault("build_prefix", "I build")
    pr.setdefault("theme", "ink")
    pr.setdefault("repo", f"{pr['handle']}/{pr['handle']}")
    pr.setdefault("words", [])
    d.setdefault("sections", DEFAULT_SECTIONS)
    if "contributions" in d:
        d["contributions"].setdefault("stats", True)
        d["contributions"].setdefault("settle", True)
    if "city" in d:
        c = d["city"]
        c.setdefault("timezone", "UTC")
        c.setdefault("preset", "generic")
        c.setdefault("river", True)
        c.setdefault("creatures", ["boats"])
        c.setdefault("seasons", ["newyear", "advent", "christmas"])
        c.setdefault("landmarks", ["tower", "bridge"])
        c.setdefault("heading", f"Based in {c['name']}")
    if "lightup" in d:
        d["lightup"].setdefault("enabled", True)
        d["lightup"].setdefault("title", "Light up the tower")
    if "org" in d:
        d["org"].setdefault("kicker", "BUILDING")
    for f in d.get("focus", []):
        f.setdefault("visual", ["auction", "retail", "sync", "ledger"][d["focus"].index(f) % 4])
    return d
