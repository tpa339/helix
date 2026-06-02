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


def init_spec(path: Path, force: bool) -> int:
    if path.exists() and not force:
        print(f"skip {path}")
        return 0
    write_json(path, DEFAULT_SPEC)
    print(f"write {path}")
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

    if dry_run:
        output = "DRY RUN: set executor.dry_run=false to execute this task.\nHELIX_STATUS: pass\n"
        returncode = 0
    else:
        cmd = [executor.get("command", "claude"), *executor.get("args", ["-p"]), prompt]
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
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%d-%H%M%S")
    run_dir = root / ".helix" / "runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    write_json(run_dir / "workflow.json", spec)

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
    parser.add_argument("command", choices=["init", "run", "status"])
    parser.add_argument("--root", default=".", help="project root")
    parser.add_argument("--spec", default=".helix/workflows/helix-workflow.json")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    spec_path = (root / args.spec).resolve()

    if args.command == "init":
        return init_spec(spec_path, args.force)
    if args.command == "run":
        if not spec_path.exists():
            print(f"Missing workflow spec: {spec_path}", file=sys.stderr)
            return 2
        return run_workflow(root, spec_path)
    return show_status(root)


if __name__ == "__main__":
    raise SystemExit(main())
