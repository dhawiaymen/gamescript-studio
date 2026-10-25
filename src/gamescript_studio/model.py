"""Versioned, data-only game definitions. No project field is evaluated as code."""

import copy
import json
import math
import re
from pathlib import Path

EVENTS = ("start", "tap", "collect", "miss")
ACTIONS = ("add_score", "add_time", "lose_life", "win", "lose")
MODES = ("tap", "catch", "dodge")
FIELDS = ("always", "score", "time", "lives")
OPS = (">=", "<=", "==", ">", "<")


class ProjectError(ValueError):
    """A user-correctable invalid project."""


def number(value, low, high, name, integer=False):
    if (
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not math.isfinite(value)
        or not low <= value <= high
        or (integer and int(value) != value)
    ):
        raise ProjectError(
            f"{name} must be {'an integer' if integer else 'a number'} in [{low}, {high}]"
        )
    return value


def default_project(mode="catch"):
    if mode not in MODES:
        raise ProjectError("Unknown mode")
    event = "tap" if mode == "tap" else "collect" if mode == "catch" else "miss"
    rules = [
        {
            "event": event,
            "field": "always",
            "op": ">=",
            "value": 0,
            "action": "add_score",
            "amount": 1,
        }
    ]
    if mode != "tap":
        rules.append(
            {
                "event": "miss" if mode == "catch" else "collect",
                "field": "always",
                "op": ">=",
                "value": 0,
                "action": "lose_life",
                "amount": 1,
            }
        )
    return {
        "version": 1,
        "title": f"My {mode.title()} Game",
        "mode": mode,
        "width": 480,
        "height": 640,
        "duration": 30,
        "target_score": 10,
        "lives": 3,
        "speed": 220,
        "spawn_interval": 0.8,
        "seed": 42,
        "background": "#15223b",
        "accent": "#58e0ae",
        "rules": rules,
    }


def validate(data):
    if not isinstance(data, dict):
        raise ProjectError("Project must be a JSON object")
    expected = set(default_project())
    if set(data) != expected:
        raise ProjectError(
            f"Project fields mismatch. Missing: {expected - set(data)}; unknown: {set(data) - expected}"
        )
    if type(data["version"]) is not int or data["version"] != 1:
        raise ProjectError("Only schema version 1 is supported")
    if not isinstance(data["title"], str) or not 1 <= len(data["title"].strip()) <= 120:
        raise ProjectError("Title must contain 1–120 characters")
    if data["mode"] not in MODES:
        raise ProjectError("Mode must be tap, catch, or dodge")
    for name, low, high, integer in [
        ("width", 240, 1920, True),
        ("height", 240, 1920, True),
        ("duration", 1, 3600, False),
        ("target_score", 1, 100000, True),
        ("lives", 1, 100, True),
        ("speed", 10, 1500, False),
        ("spawn_interval", 0.1, 30, False),
        ("seed", 0, 4294967295, True),
    ]:
        number(data[name], low, high, name, integer)
    for name in ("background", "accent"):
        if not isinstance(data[name], str) or not re.fullmatch(r"#[0-9a-fA-F]{6}", data[name]):
            raise ProjectError(f"{name} must be a #RRGGBB color")
    if not isinstance(data["rules"], list) or len(data["rules"]) > 100:
        raise ProjectError("rules must be a list of at most 100 rules")
    keys = {"event", "field", "op", "value", "action", "amount"}
    for i, rule in enumerate(data["rules"]):
        if not isinstance(rule, dict) or set(rule) != keys:
            raise ProjectError(f"Rule {i + 1} has incorrect fields")
        for field, allowed in [
            ("event", EVENTS),
            ("field", FIELDS),
            ("op", OPS),
            ("action", ACTIONS),
        ]:
            if rule[field] not in allowed:
                raise ProjectError(f"Rule {i + 1}: invalid {field}")
        number(rule["value"], -100000, 100000, f"rule {i + 1} value")
        number(rule["amount"], -10000, 10000, f"rule {i + 1} amount")
        if rule["action"] == "lose_life":
            number(rule["amount"], 1, 100, f"rule {i + 1} lives", True)
    return copy.deepcopy(data)


def load_project(path):
    path = Path(path)
    if path.stat().st_size > 1_000_000:
        raise ProjectError("Project exceeds the 1 MB limit")
    try:
        return validate(json.loads(path.read_text(encoding="utf-8")))
    except (json.JSONDecodeError, UnicodeError) as exc:
        raise ProjectError(f"Invalid UTF-8 JSON: {exc}") from exc


def save_project(data, path):
    from .compiler import atomic_text

    atomic_text(Path(path), json.dumps(validate(data), indent=2, ensure_ascii=False) + "\n")
