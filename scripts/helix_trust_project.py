#!/usr/bin/env python3
"""Enable project-local Helix autonomy permissions for safe routine commands."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


SAFE_ALLOW_RULES = [
    "Read(//private/tmp/**)",
    "Read(/private/tmp/**)",
    "Read(/tmp/**)",
    "Bash(pwd)",
    "Bash(pwd *)",
    "Bash(echo *)",
    "Bash(sleep *)",
    "Bash(cat /private/tmp/**)",
    "Bash(cat /tmp/**)",
    "Bash(tail /private/tmp/**)",
    "Bash(tail /tmp/**)",
    "Bash(tail -*)",
    "Bash(test *)",
    "Bash(pgrep *)",
    "Bash(ps *)",
    "Bash(jobs *)",
    "Bash(grep * /private/tmp/**)",
    "Bash(grep * /tmp/**)",
    "Bash(jq *)",
    "Bash(git status *)",
    "Bash(git diff *)",
    "Bash(git log *)",
    "Bash(git show *)",
    "Bash(git branch *)",
    "Bash(python3 -m pytest tests/*)",
    "Bash(python -m pytest tests/*)",
    "Bash(pytest tests/*)",
    "Bash(bash ~/.claude/scripts/helix_process_guard.sh status)",
    "Bash(bash ~/.claude/scripts/helix_process_guard.sh kill-old-pytest *)",
    "Skill(helix-auto)",
    "Skill(helix-on)",
    "Skill(helix-off)",
    "Skill(helix-processes)",
]


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def enable(root: Path) -> int:
    settings_path = root / ".claude" / "settings.local.json"
    data = read_json(settings_path)
    permissions = data.setdefault("permissions", {})
    allow = permissions.setdefault("allow", [])
    before = set(allow)
    for rule in SAFE_ALLOW_RULES:
        if rule not in before:
            allow.append(rule)
    write_json(settings_path, data)
    print(f"write {settings_path}")
    print(f"added {len(set(allow) - before)} allow rule(s)")
    return 0


def status(root: Path) -> int:
    settings_path = root / ".claude" / "settings.local.json"
    data = read_json(settings_path)
    allow = data.get("permissions", {}).get("allow", [])
    active = [rule for rule in SAFE_ALLOW_RULES if rule in allow]
    print(json.dumps({"settings": str(settings_path), "active_rules": len(active), "expected_rules": len(SAFE_ALLOW_RULES)}, indent=2))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["enable", "status"])
    parser.add_argument("--root", default=".")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    if args.command == "enable":
        return enable(root)
    return status(root)


if __name__ == "__main__":
    raise SystemExit(main())
