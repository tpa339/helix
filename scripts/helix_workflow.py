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
    "max_concurrency": 4,
    "executor": {
        "command": "claude",
        "args": ["-p"],
        "dry_run": True,
    },
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


def render_prompt(spec: dict[str, Any], phase: dict[str, Any], task: dict[str, Any]) -> str:
    return "\n".join(
        [
            "You are a Helix workflow worker.",
            f"Workflow: {spec.get('name', '')}",
            f"Objective: {spec.get('objective', '')}",
            f"Phase: {phase.get('id', '')}",
            f"Role: {task.get('role', 'worker')}",
            "",
            "Task:",
            task.get("prompt", ""),
            "",
            "Return concise, structured Markdown with findings, evidence, and residual risk.",
        ]
    )


def run_task(
    root: Path,
    run_dir: Path,
    spec: dict[str, Any],
    phase: dict[str, Any],
    task: dict[str, Any],
) -> dict[str, Any]:
    task_id = task["id"]
    task_dir = run_dir / phase["id"] / task_id
    task_dir.mkdir(parents=True, exist_ok=True)
    prompt = render_prompt(spec, phase, task)
    (task_dir / "prompt.md").write_text(prompt, encoding="utf-8")

    executor = spec.get("executor", {})
    dry_run = bool(executor.get("dry_run", True))
    started = dt.datetime.now(dt.timezone.utc).isoformat()

    if dry_run:
        output = "DRY RUN: set executor.dry_run=false to execute this task.\n"
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
        "role": task.get("role", "worker"),
        "returncode": returncode,
        "started_at": started,
        "finished_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "result_path": str((task_dir / "result.md").relative_to(root)),
    }
    write_json(task_dir / "result.json", result)
    return result


def run_workflow(root: Path, spec_path: Path) -> int:
    spec = read_json(spec_path)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%d-%H%M%S")
    run_dir = root / ".helix" / "runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    write_json(run_dir / "workflow.json", spec)

    all_results: list[dict[str, Any]] = []
    max_concurrency = max(1, int(spec.get("max_concurrency", 4)))

    for phase in spec.get("phases", []):
        tasks = phase.get("tasks", [])
        mode = phase.get("mode", "parallel")
        if mode == "serial" or len(tasks) <= 1:
            for task in tasks:
                all_results.append(run_task(root, run_dir, spec, phase, task))
        else:
            with cf.ThreadPoolExecutor(max_workers=min(max_concurrency, len(tasks))) as pool:
                futures = [pool.submit(run_task, root, run_dir, spec, phase, task) for task in tasks]
                for future in cf.as_completed(futures):
                    all_results.append(future.result())

    summary = {
        "run_id": run_id,
        "spec": str(spec_path),
        "result_count": len(all_results),
        "failed": [r for r in all_results if r["returncode"] != 0],
        "results": sorted(all_results, key=lambda r: (r["phase"], r["task_id"])),
    }
    write_json(run_dir / "summary.json", summary)
    print(str(run_dir))
    return 1 if summary["failed"] else 0


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
