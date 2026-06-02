# Helix Native Workflows

Helix Native Workflows are the open alternative to Claude Code Dynamic Workflows.

## Difference

Claude Code Dynamic Workflows move orchestration into a generated JavaScript script managed by Claude Code. Helix Native Workflows move orchestration into a project-local JSON spec plus a small runner script.

```text
.helix/workflows/*.json   # plan and phases
.helix/runs/<run_id>/     # prompts, results, summaries
scripts/helix_workflow.py # runner
```

## Why this exists

- versionable workflow plans
- inspectable prompts before execution
- rerunnable runs
- no dependency on proprietary workflow runtime
- explicit dry-run before real execution
- results stay out of Claude's context until summarized

## Execution model

1. `/helix-auto` decides that workflow orchestration is warranted.
2. `/helix-native-workflow` creates `.helix/workflows/helix-workflow.json`.
3. The user reviews the spec.
4. Set `executor.dry_run=false` for real execution.
5. `helix_workflow.py run` executes phases and stores outputs under `.helix/runs/`.

## Milestone mode

Project plans should be converted into `milestones[]`:

```json
{
  "id": "m1",
  "goal": "Implement login MVP",
  "acceptance": ["User can log in", "Invalid credentials show an error"],
  "tasks": [
    {"id": "m1-frontend", "role": "frontend-dev", "prompt": "..."},
    {"id": "m1-backend", "role": "backend-dev", "prompt": "..."}
  ],
  "tests": [
    {"id": "m1-test", "role": "test-agent", "prompt": "..."}
  ]
}
```

The runner executes implementation tasks, then test tasks. If tests fail, it runs repair tasks and repeats until the milestone passes, `max_iterations` is exhausted, or an agent returns `HELIX_STATUS: blocked`.

## Current limitation

The first runner uses the local `claude -p` CLI as an executor when `dry_run=false`. It is intentionally simple. Future versions can add:

- worktree-per-task isolation
- model selection per phase
- automatic result synthesis
- built-in evaluator quorum
- self-hosted sandbox dispatch
