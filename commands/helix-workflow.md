---
description: Escalate suitable work into a Helix-native workflow
model: opus
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, Agent
---

# `/helix-workflow`

Use when a task needs many agents, repeatable orchestration, adversarial validation, or long-running parallel work.
This command must prefer Helix-native workflows over Claude Code Dynamic Workflows.

## Workflow candidates

- codebase-wide security, auth, performance, dead-code, or migration audits
- large migrations touching many independent files
- research questions that need independent source cross-checking
- high-stakes plans that need several independent drafts and refutation
- repeated CI/test-fix loops across independent failures
- project plans with milestones that should be worked until accepted

## Required behavior

1. Read `.helix/state/TASK_CARD.md`, `.helix/state/ROUTING_DECISION.md`, `WORK_UNITS.md`, and `QUALITY_GATES.md` when present.
2. Write `.helix/specs/WORKFLOW_BRIEF.md`.
3. Create or update `.helix/workflows/helix-workflow.json`.
4. Use `python3 ~/.claude/scripts/helix_workflow.py init --root .` if the workflow spec is missing.
5. Keep `executor.dry_run=true` until the user approves a real run.
6. Require approval before launching expensive workflow runs.
7. Make the workflow phases explicit:
   - orient
   - shard
   - execute milestone tasks in parallel
   - test with `test-agent`
   - repair and retry when tests fail
   - adversarial review or release gate
   - integrate and summarize
8. Run with `python3 ~/.claude/scripts/helix_workflow.py run --root .` only after review.
9. Summarize `.helix/runs/<run_id>/summary.json`, not every intermediate result.
10. Stop only when target state is reached, max iterations are exhausted, or blockers are documented in `.helix/runs/<run_id>/blockers.json`.

Do not use workflows for routine one-file work.
