---
description: Create and run Helix-native workflows without Claude Code Dynamic Workflows
model: opus
allowed-tools: Read, Write, Edit, MultiEdit, Glob, Grep, Bash, Agent, TodoWrite
---

# `/helix-native-workflow`

Use this instead of Claude Code Dynamic Workflows.

## Mental model

Helix owns the orchestration:

- workflow plan lives in `.helix/workflows/*.json`
- intermediate results live in `.helix/runs/<run_id>/`
- Claude's conversation receives only route decisions, summaries, and final findings
- every workflow can be reviewed, edited, committed, and rerun

## Commands

Initialize a workflow spec:

`python3 ~/.claude/scripts/helix_workflow.py init --root .`

Run a workflow:

`python3 ~/.claude/scripts/helix_workflow.py run --root .`

Show latest run status:

`python3 ~/.claude/scripts/helix_workflow.py status --root .`

## Required behavior

1. Read `.helix/state/TASK_CARD.md`, `.helix/state/ROUTING_DECISION.md`, and `.helix/specs/WORKFLOW_BRIEF.md`.
2. Generate or update `.helix/workflows/helix-workflow.json`.
3. Shard work into phases and tasks.
4. Set `executor.dry_run=true` until the user approves a real run.
5. Use bounded `max_concurrency`; default to 4 unless there is a reason to increase.
6. Put adversarial review in a separate phase.
7. Never put secrets or full private logs into task prompts.
8. Run the workflow only after explaining expected cost/risk.

## When to use

- codebase-wide audits
- large migrations
- independent research with cross-checking
- repeated fix/verify loops
- many low-overlap work units

Do not use this for routine local edits.
