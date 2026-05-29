#!/usr/bin/env python3
"""Create a project-local Helix structure without overwriting user work."""

from __future__ import annotations

import argparse
import datetime as dt
import os
import shutil
from pathlib import Path


TEMPLATE_MAP = {
    "INTERVIEW.template.md": ".helix/interview/INTERVIEW.md",
    "PROJECT_STATE.template.md": ".helix/state/PROJECT_STATE.md",
    "TASK_CARD.template.md": ".helix/state/TASK_CARD.md",
    "ROUTING_DECISION.template.md": ".helix/state/ROUTING_DECISION.md",
    "ROADMAP.template.md": ".helix/state/ROADMAP.md",
    "PROGRESS.template.md": ".helix/state/PROGRESS.md",
    "LEARNINGS.template.md": ".helix/state/LEARNINGS.md",
    "PRD.template.md": ".helix/specs/PRD.md",
    "SPEC.template.md": ".helix/specs/SPEC.md",
    "ARCHITECTURE.template.md": ".helix/specs/ARCHITECTURE.md",
    "NEGATIVE_CONSTRAINTS.template.md": ".helix/specs/NEGATIVE_CONSTRAINTS.md",
    "TEST_STRATEGY.template.md": ".helix/specs/TEST_STRATEGY.md",
    "REQUIREMENTS_CATALOG.template.md": ".helix/specs/REQUIREMENTS_CATALOG.md",
    "RESEARCH_PLAN.template.md": ".helix/specs/RESEARCH_PLAN.md",
    "ISSUE_TRACKING.template.md": ".helix/specs/ISSUE_TRACKING.md",
    "LOAD_PLAN.template.md": ".helix/specs/LOAD_PLAN.md",
    "WORK_UNITS.template.md": ".helix/specs/WORK_UNITS.md",
    "QUALITY_GATES.template.md": ".helix/specs/QUALITY_GATES.md",
    "RUBRIC.template.md": ".helix/specs/RUBRIC.md",
    "REVIEW.template.md": ".helix/specs/REVIEW.md",
    "ADVISOR_POLICY.template.md": ".helix/specs/ADVISOR_POLICY.md",
    "ADVISOR_LOG.template.md": ".helix/specs/ADVISOR_LOG.md",
    "AGENT_TOPOLOGY.template.md": ".helix/specs/AGENT_TOPOLOGY.md",
    "DISPATCH_BOARD.template.md": ".helix/specs/DISPATCH_BOARD.md",
    "WORKFLOW_BRIEF.template.md": ".helix/specs/WORKFLOW_BRIEF.md",
    "OVERVIEW_INDEX.template.md": ".helix/overview/INDEX.md",
    "DECISIONS.template.md": ".helix/overview/DECISIONS.md",
    "CURRENT_STATE.template.md": ".helix/overview/CURRENT_STATE.md",
    "OPEN_QUESTIONS.template.md": ".helix/overview/OPEN_QUESTIONS.md",
    "CHANGELOG.template.md": ".helix/changelog/CHANGELOG.md",
    "CLAUDE.project.template.md": "CLAUDE.md",
}


def copy_template(src: Path, dst: Path, force: bool) -> str:
    if dst.exists() and not force:
        return f"skip {dst}"
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dst)
    return f"write {dst}"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".", help="project root")
    parser.add_argument("--force", action="store_true", help="overwrite existing files")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    explicit_template_dir = os.getenv("HELIX_TEMPLATE_DIR")
    repo_templates = Path(__file__).resolve().parent.parent / "templates"
    home_templates = Path.home() / ".claude" / "templates"
    if explicit_template_dir:
        templates = Path(explicit_template_dir).expanduser().resolve()
    elif repo_templates.exists():
        templates = repo_templates
    else:
        templates = home_templates

    for rel in [
        ".helix/interview",
        ".helix/specs",
        ".helix/state",
        ".helix/rules",
        ".helix/kb/graphify-out",
        ".helix/kb/wiki",
        ".helix/overview",
        ".helix/changelog/daily",
    ]:
        (root / rel).mkdir(parents=True, exist_ok=True)

    results = []
    for template, target in TEMPLATE_MAP.items():
        src = templates / template
        if src.exists():
            results.append(copy_template(src, root / target, args.force))

    today = dt.date.today().isoformat()
    day_log = root / ".helix" / "changelog" / "daily" / f"{today}.md"
    if not day_log.exists() or args.force:
        day_log.write_text(f"# {today}\n\n", encoding="utf-8")
        results.append(f"write {day_log}")

    print("\n".join(results))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
