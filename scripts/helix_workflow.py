#!/usr/bin/env python3
"""Run Helix-native workflows from a repo-local JSON specification.

The runner is intentionally small: orchestration lives in a versionable JSON file,
intermediate results live under .helix/runs, and only summaries need to return to
Claude's conversation context.
"""

from __future__ import annotations

import argparse
import concurrent.futures as cf
import datetime as dt
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


DEFAULT_SPEC = {
    "name": "helix-workflow",
    "objective": "",
    "target_state": "",
    "max_concurrency": 4,
    "max_iterations": 3,
    "complexity": {
        "level": "auto",
        "score": None,
        "research_depth": "auto",
        "risk": "auto",
    },
    "model_policy": {
        "default": "sonnet",
        "cheap": "haiku",
        "standard": "sonnet",
        "strong": "opus",
        "model_arg": "--model",
        "role_defaults": {
            "frontend-dev": "sonnet",
            "backend-dev": "sonnet",
            "test-agent": "sonnet",
            "review-agent": "opus",
            "release-gate": "opus",
            "researcher": "sonnet",
            "worker": "sonnet",
        },
        "complexity_bands": [
            {"max_score": 5, "model": "haiku"},
            {"max_score": 12, "model": "sonnet"},
            {"max_score": 99, "model": "opus"},
        ],
    },
    "executor": {
        "command": "claude",
        "args": ["-p"],
        "dry_run": True,
    },
    "agents": {
        "frontend-dev": {
            "skills": ["ui", "accessibility", "browser-verification"],
            "mission": "Implement bounded frontend/UI work and verify visible behavior.",
        },
        "backend-dev": {
            "skills": ["api", "data-modeling", "integration"],
            "mission": "Implement bounded backend/API/data work and verify contracts.",
        },
        "test-agent": {
            "skills": ["unit-tests", "integration-tests", "regression"],
            "mission": "Prove the milestone works against acceptance criteria.",
        },
        "review-agent": {
            "skills": ["code-review", "risk-analysis", "adversarial-testing"],
            "mission": "Challenge implementation quality and surface blockers.",
        },
        "release-gate": {
            "skills": ["integration-review", "risk-control", "acceptance"],
            "mission": "Decide if the milestone is safe to integrate or must return to repair.",
        },
        "researcher": {
            "skills": ["source-triage", "fact-checking", "synthesis"],
            "mission": "Resolve only the research uncertainty needed for execution.",
        },
        "worker": {
            "skills": ["bounded-implementation", "verification", "handoff"],
            "mission": "Complete a bounded work unit with minimal context and clear evidence.",
        },
    },
    "milestones": [
        {
            "id": "m1",
            "goal": "Reach the first verifiable project milestone.",
            "acceptance": ["All scoped checks pass.", "No known critical blocker remains."],
            "tasks": [
                {
                    "id": "m1-frontend",
                    "role": "frontend-dev",
                    "prompt": "Implement the frontend part of milestone m1 if applicable.",
                },
                {
                    "id": "m1-backend",
                    "role": "backend-dev",
                    "prompt": "Implement the backend part of milestone m1 if applicable.",
                },
            ],
            "tests": [
                {
                    "id": "m1-test",
                    "role": "test-agent",
                    "prompt": "Test milestone m1 against its acceptance criteria.",
                }
            ],
        }
    ],
    "phases": [
        {
            "id": "orient",
            "mode": "parallel",
            "tasks": [
                {
                    "id": "orient-1",
                    "role": "researcher",
                    "prompt": "Summarize the relevant repo context for this workflow.",
                }
            ],
        },
        {
            "id": "review",
            "mode": "parallel",
            "tasks": [
                {
                    "id": "review-1",
                    "role": "evaluator",
                    "prompt": "Review prior findings adversarially and list only verified issues.",
                }
            ],
        },
    ],
}


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def read_optional(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def clamp(value: int, low: int = 0, high: int = 3) -> int:
    return max(low, min(high, value))


def count_keywords(text: str, keywords: list[str]) -> int:
    lower = text.lower()
    return sum(1 for keyword in keywords if keyword in lower)


def score_complexity(text: str) -> dict[str, Any]:
    """Deterministic routing score. It is intentionally simple and inspectable."""
    lower = text.lower()
    lines = [line for line in text.splitlines() if line.strip()]
    unit_count = len(re.findall(r"\bU-\d{3}\b", text))
    milestone_count = len(re.findall(r"\bM\d+\b|^###\s+m\d+", text, flags=re.IGNORECASE | re.MULTILINE))

    ambiguity = clamp(
        count_keywords(
            lower,
            ["tbd", "unknown", "unclear", "maybe", "material ambiguity", "frage", "oder", "unklar"],
        )
        + (1 if "?" in text else 0)
    )
    scope = clamp((len(lines) // 80) + (unit_count // 4) + (milestone_count // 3))
    risk = clamp(
        count_keywords(
            lower,
            [
                "auth",
                "security",
                "payment",
                "production",
                "migration",
                "database",
                "privacy",
                "compliance",
                "secret",
                "destructive",
                "deploy",
            ],
        )
    )
    novelty = clamp(
        count_keywords(
            lower,
            ["new", "unknown", "integration", "ai", "agent", "realtime", "distributed", "mcp", "api"],
        )
    )
    research_need = clamp(
        count_keywords(lower, ["research", "docs", "current", "latest", "market", "benchmark", "compare"])
    )
    verification_difficulty = clamp(
        count_keywords(lower, ["e2e", "playwright", "browser", "load", "stress", "concurrent", "sync", "ui"])
    )
    parallelizability = clamp((unit_count // 2) + (milestone_count // 2) + count_keywords(lower, ["parallel", "worktree", "swarm"]))
    total = ambiguity + scope + risk + novelty + research_need + verification_difficulty
    level = "low"
    if total >= 13 or risk >= 3:
        level = "critical"
    elif total >= 9:
        level = "high"
    elif total >= 5:
        level = "medium"

    return {
        "ambiguity": ambiguity,
        "scope": scope,
        "risk": risk,
        "novelty": novelty,
        "research_need": research_need,
        "verification_difficulty": verification_difficulty,
        "parallelizability": parallelizability,
        "total": total,
        "level": level,
        "unit_count": unit_count,
        "milestone_count": milestone_count,
    }


def score_task_effort(text: str, role: str = "worker") -> dict[str, Any]:
    """Score one work unit so the orchestrator can right-size model and review depth."""
    base = score_complexity(text)
    role_weight = {
        "review-agent": 2,
        "release-gate": 3,
        "backend-dev": 1,
        "frontend-dev": 1,
        "test-agent": 1,
        "researcher": 1,
        "worker": 0,
    }.get(role, 0)
    file_count = len(re.findall(r"[\w./-]+\.(ts|tsx|js|jsx|py|go|rs|swift|md|json|yaml|yml)", text))
    dependency_count = len(re.findall(r"\bU-\d{3}\b", text))
    score = base["ambiguity"] + base["risk"] + base["novelty"] + base["verification_difficulty"]
    score += clamp(file_count // 4, 0, 2) + clamp(dependency_count, 0, 2) + role_weight

    effort = "xs"
    if score >= 12:
        effort = "xl"
    elif score >= 9:
        effort = "l"
    elif score >= 6:
        effort = "m"
    elif score >= 3:
        effort = "s"

    return {
        "score": score,
        "effort": effort,
        "risk": base["risk"],
        "ambiguity": base["ambiguity"],
        "verification_difficulty": base["verification_difficulty"],
        "suggested_review": "release-gate"
        if role == "release-gate" or base["risk"] >= 3
        else ("adversarial" if score >= 6 else "standard"),
        "suggested_model_tier": "strong" if score >= 9 or role in {"release-gate", "review-agent"} else ("standard" if score >= 3 else "cheap"),
    }


def collect_project_context(root: Path) -> dict[str, str]:
    files = {
        "task_card": ".helix/state/TASK_CARD.md",
        "routing": ".helix/state/ROUTING_DECISION.md",
        "workflow_brief": ".helix/specs/WORKFLOW_BRIEF.md",
        "work_units": ".helix/specs/WORK_UNITS.md",
        "requirements": ".helix/specs/REQUIREMENTS_CATALOG.md",
        "prd": ".helix/specs/PRD.md",
        "spec": ".helix/specs/SPEC.md",
        "architecture": ".helix/specs/ARCHITECTURE.md",
        "roadmap": ".helix/specs/ROADMAP.md",
        "quality_gates": ".helix/specs/QUALITY_GATES.md",
        "test_strategy": ".helix/specs/TEST_STRATEGY.md",
    }
    return {name: read_optional(root / rel) for name, rel in files.items()}


def split_sections(markdown: str, heading_pattern: str) -> list[tuple[str, str]]:
    matches = list(re.finditer(heading_pattern, markdown, flags=re.IGNORECASE | re.MULTILINE))
    sections: list[tuple[str, str]] = []
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(markdown)
        sections.append((match.group(1).strip(), markdown[start:end].strip()))
    return sections


def field_value(section: str, field: str) -> str:
    pattern = rf"^\s*-\s*{re.escape(field)}\s*:\s*(.*)$"
    match = re.search(pattern, section, flags=re.IGNORECASE | re.MULTILINE)
    return match.group(1).strip() if match else ""


def infer_role(text: str) -> str:
    lower = text.lower()
    if count_keywords(lower, ["frontend", "ui", "css", "component", "browser", "react", "svelte"]):
        return "frontend-dev"
    if count_keywords(lower, ["api", "backend", "server", "database", "auth", "service", "migration"]):
        return "backend-dev"
    if count_keywords(lower, ["test", "verify", "playwright", "e2e", "regression"]):
        return "test-agent"
    if count_keywords(lower, ["review", "risk", "security", "release", "gate"]):
        return "review-agent"
    if count_keywords(lower, ["research", "docs", "compare", "benchmark"]):
        return "researcher"
    return "worker"


def extract_work_units(markdown: str) -> list[dict[str, Any]]:
    units: list[dict[str, Any]] = []
    for unit_id, section in split_sections(markdown, r"^##\s+(U-\d{3})\s*$"):
        prompt = field_value(section, "intent") or field_value(section, "purpose") or section.splitlines()[0:1]
        if isinstance(prompt, list):
            prompt = " ".join(prompt).strip()
        verification = field_value(section, "verification")
        suggested_role = field_value(section, "suggested_worker_role")
        role = suggested_role if suggested_role else infer_role(section)
        effort = score_task_effort(section, role)
        units.append(
            {
                "id": unit_id.lower(),
                "role": role,
                "prompt": prompt or f"Complete work unit {unit_id}.",
                "verification": verification,
                "effort": effort,
                "section": section,
            }
        )
    return units


def extract_milestones(markdown: str) -> list[dict[str, str]]:
    milestones: list[dict[str, str]] = []
    for milestone_id, section in split_sections(markdown, r"^###\s+(M\d+)\s*$"):
        goal = field_value(section, "goal") or section.splitlines()[0:1]
        if isinstance(goal, list):
            goal = " ".join(goal).strip()
        acceptance = field_value(section, "exit criteria")
        milestones.append({"id": milestone_id.lower(), "goal": goal or f"Complete {milestone_id}.", "acceptance": acceptance})
    return milestones


def model_for_score(policy: dict[str, Any], score: int) -> str:
    for band in policy.get("complexity_bands", []):
        if score <= int(band.get("max_score", 99)):
            return str(band.get("model", policy.get("default", "sonnet")))
    return str(policy.get("default", "sonnet"))


def select_model(spec: dict[str, Any], phase: dict[str, Any], task: dict[str, Any]) -> str:
    if task.get("model"):
        return str(task["model"])
    policy = spec.get("model_policy", {})
    role = task.get("role", "worker")
    effort = task.get("effort") or {}
    tier = effort.get("suggested_model_tier")
    if tier and tier in policy:
        return str(policy[tier])
    role_default = policy.get("role_defaults", {}).get(role)
    score = int((spec.get("complexity") or {}).get("score") or 0)
    selected = role_default or model_for_score(policy, score)

    if (spec.get("complexity") or {}).get("level") in {"high", "critical"}:
        if role in {"review-agent", "release-gate"}:
            selected = str(policy.get("strong", "opus"))
    return str(selected or policy.get("default", "sonnet"))


def build_task_command(spec: dict[str, Any], executor: dict[str, Any], model: str, prompt: str) -> list[str]:
    cmd = [executor.get("command", "claude"), *executor.get("args", ["-p"])]
    model_arg = executor.get("model_arg")
    if model_arg is None:
        model_arg = (spec.get("model_policy") or {}).get("model_arg")
    if model_arg is None:
        model_arg = os.environ.get("HELIX_MODEL_ARG", "--model")
    if model and model_arg:
        cmd.extend([str(model_arg), model])
    cmd.append(prompt)
    return cmd


def init_spec(path: Path, force: bool) -> int:
    if path.exists() and not force:
        print(f"skip {path}")
        return 0
    write_json(path, DEFAULT_SPEC)
    print(f"write {path}")
    return 0


def build_dynamic_milestones(context: dict[str, str], complexity: dict[str, Any]) -> list[dict[str, Any]]:
    units = extract_work_units(context.get("work_units", ""))
    roadmap_milestones = extract_milestones(context.get("roadmap", ""))
    source_text = "\n\n".join(context.values()).strip()
    objective = first_nonempty_line(
        context.get("workflow_brief", ""),
        context.get("task_card", ""),
        context.get("prd", ""),
        fallback="Reach the requested target state.",
    )

    if not units:
        inferred_roles = ["worker"]
        if count_keywords(source_text.lower(), ["frontend", "ui", "browser", "component"]):
            inferred_roles.append("frontend-dev")
        if count_keywords(source_text.lower(), ["backend", "api", "database", "auth"]):
            inferred_roles.append("backend-dev")
        if inferred_roles == ["worker"]:
            inferred_roles = [infer_role(source_text)]
        units = [
            {
                "id": f"auto-{index + 1}",
                "role": role,
                "prompt": f"Execute the {role} slice needed for: {objective}",
                "verification": "Run the smallest meaningful verification for this slice.",
                "section": source_text,
                "effort": score_task_effort(source_text, role),
            }
            for index, role in enumerate(dict.fromkeys(inferred_roles))
        ]

    if not roadmap_milestones:
        roadmap_milestones = [
            {
                "id": "m1",
                "goal": objective,
                "acceptance": "Target state is reached and verified.",
            }
        ]

    milestones: list[dict[str, Any]] = []
    for index, milestone in enumerate(roadmap_milestones):
        assigned_units = units if len(roadmap_milestones) == 1 else units[index :: len(roadmap_milestones)]
        if not assigned_units:
            assigned_units = units
        tasks = [
            {
                "id": f"{milestone['id']}-{unit['id']}",
                "role": unit["role"],
                "effort": unit.get("effort", {}),
                "prompt": "\n".join(
                    [
                        f"Milestone goal: {milestone['goal']}",
                        f"Work unit: {unit['id']}",
                        f"Effort: {(unit.get('effort') or {}).get('effort', 'unknown')} / score {(unit.get('effort') or {}).get('score', 'unknown')}",
                        f"Task: {unit['prompt']}",
                        f"Verification intent: {unit.get('verification') or 'Verify against acceptance criteria.'}",
                    ]
                ),
            }
            for unit in assigned_units
        ]
        tests = [
            {
                "id": f"{milestone['id']}-test",
                "role": "test-agent",
                "effort": score_task_effort(
                    f"Verify milestone {milestone['id']} against: {milestone.get('acceptance') or milestone['goal']}",
                    "test-agent",
                ),
                "prompt": f"Verify milestone {milestone['id']} against: {milestone.get('acceptance') or milestone['goal']}",
            }
        ]
        if complexity["risk"] >= 2 or complexity["level"] in {"high", "critical"}:
            tests.append(
                {
                    "id": f"{milestone['id']}-release-gate",
                    "role": "release-gate",
                    "effort": score_task_effort(
                        f"Release gate for {milestone['id']}: {milestone.get('acceptance') or milestone['goal']}",
                        "release-gate",
                    ),
                    "prompt": f"Perform adversarial release-gate review for milestone {milestone['id']}. Block if unresolved high-risk issues remain.",
                }
            )
        milestones.append(
            {
                "id": milestone["id"],
                "goal": milestone["goal"],
                "acceptance": [
                    milestone.get("acceptance") or "All scoped checks pass.",
                    "No critical blocker remains undocumented.",
                ],
                "tasks": tasks,
                "tests": tests,
                "repair_tasks": tasks,
            }
        )
    return milestones


def first_nonempty_line(*texts: str, fallback: str) -> str:
    for text in texts:
        for line in text.splitlines():
            stripped = line.strip(" -#:\t")
            if stripped and not stripped.lower().startswith(("route", "status", "score")):
                return stripped[:240]
    return fallback


def generate_plan_spec(root: Path, spec_path: Path, force: bool) -> int:
    if spec_path.exists() and not force:
        print(f"skip {spec_path}")
        return 0

    context = collect_project_context(root)
    source_text = "\n\n".join(context.values())
    complexity = score_complexity(source_text)
    objective = first_nonempty_line(
        context.get("workflow_brief", ""),
        context.get("task_card", ""),
        context.get("prd", ""),
        fallback="Reach the requested target state.",
    )
    target_state = first_nonempty_line(
        context.get("spec", ""),
        context.get("quality_gates", ""),
        context.get("test_strategy", ""),
        fallback="All acceptance criteria are verified and blockers are documented.",
    )

    spec = json.loads(json.dumps(DEFAULT_SPEC))
    spec["objective"] = objective
    spec["target_state"] = target_state
    spec["complexity"] = {
        "level": complexity["level"],
        "score": complexity["total"],
        "research_depth": "deep" if complexity["research_need"] >= 2 else ("light" if complexity["research_need"] else "none"),
        "risk": "high" if complexity["risk"] >= 2 else ("medium" if complexity["risk"] else "low"),
        "dimensions": complexity,
    }
    spec["max_concurrency"] = 1 + min(7, max(complexity["parallelizability"], complexity["unit_count"] // 2))
    spec["max_iterations"] = 1 if complexity["level"] == "low" else (2 if complexity["level"] == "medium" else 3)
    spec["milestones"] = build_dynamic_milestones(context, complexity)
    spec["phases"] = []

    write_json(spec_path, spec)
    print(f"write {spec_path}")
    print(json.dumps(spec["complexity"], indent=2, ensure_ascii=False))
    return 0


def render_prompt(
    spec: dict[str, Any],
    phase: dict[str, Any],
    task: dict[str, Any],
    prior_results: list[dict[str, Any]] | None = None,
) -> str:
    role = task.get("role", "worker")
    agent = spec.get("agents", {}).get(role, {})
    skills = ", ".join(agent.get("skills", [])) or "none specified"
    prior_paths = "\n".join(f"- {r['result_path']}" for r in prior_results or [])
    return "\n".join(
        [
            "You are a Helix workflow worker.",
            f"Workflow: {spec.get('name', '')}",
            f"Objective: {spec.get('objective', '')}",
            f"Target state: {spec.get('target_state', '')}",
            f"Phase: {phase.get('id', '')}",
            f"Role: {role}",
            f"Role mission: {agent.get('mission', '')}",
            f"Relevant skills: {skills}",
            f"Task effort: {(task.get('effort') or {}).get('effort', 'unknown')} / score {(task.get('effort') or {}).get('score', 'unknown')}",
            f"Review depth: {(task.get('effort') or {}).get('suggested_review', 'standard')}",
            f"Milestone: {phase.get('milestone_id', '')}",
            "",
            "Task:",
            task.get("prompt", ""),
            "",
            "Acceptance criteria:",
            "\n".join(f"- {item}" for item in phase.get("acceptance", [])) or "- Not specified",
            "",
            "Prior result files:",
            prior_paths or "- none",
            "",
            "Rules:",
            "- Work only on this bounded task.",
            "- Record changed files, commands run, verification, and residual risk.",
            "- If blocked, explain the blocker and what the orchestrator must decide.",
            "- End with exactly one status line: HELIX_STATUS: pass|fail|blocked",
        ]
    )


def parse_status(output: str, returncode: int) -> str:
    if returncode != 0:
        return "fail"
    for line in reversed(output.splitlines()):
        normalized = line.strip().lower()
        if normalized.startswith("helix_status:"):
            value = normalized.split(":", 1)[1].strip()
            if value in {"pass", "fail", "blocked"}:
                return value
    if "blocked" in output.lower():
        return "blocked"
    return "pass"


def run_task(
    root: Path,
    run_dir: Path,
    spec: dict[str, Any],
    phase: dict[str, Any],
    task: dict[str, Any],
    prior_results: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    task_id = task["id"]
    task_dir = run_dir / phase["id"] / task_id
    task_dir.mkdir(parents=True, exist_ok=True)
    prompt = render_prompt(spec, phase, task, prior_results)
    (task_dir / "prompt.md").write_text(prompt, encoding="utf-8")

    executor = spec.get("executor", {})
    dry_run = bool(executor.get("dry_run", True))
    started = dt.datetime.now(dt.timezone.utc).isoformat()
    selected_model = select_model(spec, phase, task)

    if dry_run:
        output = "\n".join(
            [
                "DRY RUN: set executor.dry_run=false to execute this task.",
                f"Selected model: {selected_model}",
                "HELIX_STATUS: pass",
                "",
            ]
        )
        returncode = 0
    else:
        cmd = build_task_command(spec, executor, selected_model, prompt)
        proc = subprocess.run(
            cmd,
            cwd=root,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        output = proc.stdout
        returncode = proc.returncode

    (task_dir / "result.md").write_text(output, encoding="utf-8")
    result = {
        "task_id": task_id,
        "phase": phase["id"],
        "milestone_id": phase.get("milestone_id"),
        "role": task.get("role", "worker"),
        "model": selected_model,
        "effort": task.get("effort", {}),
        "status": parse_status(output, returncode),
        "returncode": returncode,
        "started_at": started,
        "finished_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "result_path": str((task_dir / "result.md").relative_to(root)),
    }
    write_json(task_dir / "result.json", result)
    return result


def run_phase(
    root: Path,
    run_dir: Path,
    spec: dict[str, Any],
    phase: dict[str, Any],
    prior_results: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    tasks = phase.get("tasks", [])
    mode = phase.get("mode", "parallel")
    max_concurrency = max(1, int(spec.get("max_concurrency", 4)))
    if mode == "serial" or len(tasks) <= 1:
        return [run_task(root, run_dir, spec, phase, task, prior_results) for task in tasks]

    results: list[dict[str, Any]] = []
    with cf.ThreadPoolExecutor(max_workers=min(max_concurrency, len(tasks))) as pool:
        futures = [
            pool.submit(run_task, root, run_dir, spec, phase, task, prior_results) for task in tasks
        ]
        for future in cf.as_completed(futures):
            results.append(future.result())
    return results


def phases_from_milestone(milestone: dict[str, Any], iteration: int) -> list[dict[str, Any]]:
    milestone_id = milestone["id"]
    suffix = f"i{iteration}"
    return [
        {
            "id": f"{milestone_id}-{suffix}-execute",
            "milestone_id": milestone_id,
            "mode": "parallel",
            "acceptance": milestone.get("acceptance", []),
            "tasks": milestone.get("tasks", []),
        },
        {
            "id": f"{milestone_id}-{suffix}-test",
            "milestone_id": milestone_id,
            "mode": "parallel",
            "acceptance": milestone.get("acceptance", []),
            "tasks": milestone.get("tests", []),
        },
    ]


def run_legacy_phases(
    root: Path,
    run_dir: Path,
    spec: dict[str, Any],
) -> list[dict[str, Any]]:
    all_results: list[dict[str, Any]] = []
    for phase in spec.get("phases", []):
        phase_results = run_phase(root, run_dir, spec, phase, all_results)
        all_results.extend(phase_results)
    return all_results


def run_milestones(
    root: Path,
    run_dir: Path,
    spec: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    all_results: list[dict[str, Any]] = []
    blockers: list[dict[str, Any]] = []
    max_iterations = max(1, int(spec.get("max_iterations", 3)))

    for milestone in spec.get("milestones", []):
        milestone_results: list[dict[str, Any]] = []
        passed = False
        for iteration in range(1, max_iterations + 1):
            iteration_results: list[dict[str, Any]] = []
            for phase in phases_from_milestone(milestone, iteration):
                phase_results = run_phase(root, run_dir, spec, phase, all_results + milestone_results)
                iteration_results.extend(phase_results)
                milestone_results.extend(phase_results)
                all_results.extend(phase_results)

                if any(result["status"] == "blocked" for result in phase_results):
                    blockers.extend(result for result in phase_results if result["status"] == "blocked")
                    write_json(run_dir / "blockers.json", blockers)
                    return all_results, blockers

            test_results = [r for r in iteration_results if r["phase"].endswith("-test")]
            if test_results and all(r["status"] == "pass" for r in test_results):
                passed = True
                break

            if iteration < max_iterations:
                repair_phase = {
                    "id": f"{milestone['id']}-i{iteration + 1}-repair",
                    "milestone_id": milestone["id"],
                    "mode": "parallel",
                    "acceptance": milestone.get("acceptance", []),
                    "tasks": milestone.get("repair_tasks", milestone.get("tasks", [])),
                }
                repair_results = run_phase(root, run_dir, spec, repair_phase, milestone_results)
                milestone_results.extend(repair_results)
                all_results.extend(repair_results)
                if any(result["status"] == "blocked" for result in repair_results):
                    blockers.extend(result for result in repair_results if result["status"] == "blocked")
                    write_json(run_dir / "blockers.json", blockers)
                    return all_results, blockers

        if not passed:
            blockers.append(
                {
                    "milestone_id": milestone["id"],
                    "status": "blocked",
                    "reason": f"Milestone did not pass after {max_iterations} iterations.",
                    "result_paths": [r["result_path"] for r in milestone_results],
                }
            )
            write_json(run_dir / "blockers.json", blockers)
            return all_results, blockers

    return all_results, blockers


def run_workflow(root: Path, spec_path: Path) -> int:
    spec = read_json(spec_path)
    if (spec.get("complexity") or {}).get("level") == "auto":
        spec_text = json.dumps(spec, ensure_ascii=False)
        scored = score_complexity(spec_text)
        spec["complexity"] = {
            "level": scored["level"],
            "score": scored["total"],
            "research_depth": "deep" if scored["research_need"] >= 2 else ("light" if scored["research_need"] else "none"),
            "risk": "high" if scored["risk"] >= 2 else ("medium" if scored["risk"] else "low"),
            "dimensions": scored,
        }
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%d-%H%M%S")
    run_dir = root / ".helix" / "runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    write_json(run_dir / "workflow.json", spec)
    write_json(run_dir / "complexity.json", spec.get("complexity", {}))

    if spec.get("milestones"):
        all_results, blockers = run_milestones(root, run_dir, spec)
    else:
        all_results = run_legacy_phases(root, run_dir, spec)
        blockers = []

    summary = {
        "run_id": run_id,
        "spec": str(spec_path),
        "result_count": len(all_results),
        "target_state": spec.get("target_state", ""),
        "complexity": spec.get("complexity", {}),
        "status": "blocked"
        if blockers
        else ("failed" if any(r["status"] == "fail" for r in all_results) else "passed"),
        "blockers": blockers,
        "failed": [r for r in all_results if r["status"] == "fail"],
        "results": sorted(all_results, key=lambda r: (r["phase"], r["task_id"])),
    }
    write_json(run_dir / "summary.json", summary)
    print(str(run_dir))
    return 0 if summary["status"] == "passed" else 1


def show_status(root: Path) -> int:
    runs = sorted((root / ".helix" / "runs").glob("*/summary.json"))
    if not runs:
        print("No Helix workflow runs found.")
        return 0
    latest = runs[-1]
    data = read_json(latest)
    print(json.dumps(data, indent=2, ensure_ascii=False))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["init", "plan", "run", "status"])
    parser.add_argument("--root", default=".", help="project root")
    parser.add_argument("--spec", default=".helix/workflows/helix-workflow.json")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    spec_path = (root / args.spec).resolve()

    if args.command == "init":
        return init_spec(spec_path, args.force)
    if args.command == "plan":
        return generate_plan_spec(root, spec_path, args.force)
    if args.command == "run":
        if not spec_path.exists():
            print(f"Missing workflow spec: {spec_path}", file=sys.stderr)
            return 2
        return run_workflow(root, spec_path)
    return show_status(root)


if __name__ == "__main__":
    raise SystemExit(main())
