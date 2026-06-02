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

Generate a dynamic workflow spec from current Helix artifacts:

`python3 ~/.claude/scripts/helix_workflow.py plan --root . --force`

Run a workflow:

`python3 ~/.claude/scripts/helix_workflow.py run --root .`

Show latest run status:

`python3 ~/.claude/scripts/helix_workflow.py status --root .`

## Required behavior

1. Read `.helix/state/TASK_CARD.md`, `.helix/state/ROUTING_DECISION.md`, and `.helix/specs/WORKFLOW_BRIEF.md`.
2. Run `python3 ~/.claude/scripts/helix_workflow.py plan --root . --force` to generate `.helix/workflows/helix-workflow.json` from the current project artifacts.
3. Shard work into phases and tasks.
4. Give every task an effort rating: `complexity_score`, `effort_size`, `suggested_model_tier`, and `review_depth`.
5. Give every task an execution plan: `workflow_pattern`, `required_skills`, `use_subagent`, `use_worktree`, `isolation`, and `stop_condition`.
6. Map each task to a role such as `frontend-dev`, `backend-dev`, `test-agent`, `review-agent`, or a project-specific role.
7. Model project plans as `milestones[]` with `tasks[]`, `tests[]`, optional `repair_tasks[]`, and acceptance criteria.
8. Set `executor.dry_run=true` until the user approves a real run.
9. Let the generated `complexity` block determine `max_concurrency`, `max_iterations`, and research depth.
10. Let each task's `effort` block determine the cheapest sufficient model tier: cheap for low-risk repetitive tasks, standard for normal implementation, strong for high-risk/adversarial/release-gate work.
11. Let each task's `execution_plan` decide whether a subagent or worktree is justified.
12. Put testing and adversarial review in separate phases.
13. Never put secrets or full private logs into task prompts.
14. Run the workflow only after explaining expected cost/risk.
15. Continue iterations until `target_state` is reached, `max_iterations` is exhausted, or a blocker is documented.

## Pattern policy

- `direct-bounded`: small local task; no subagent unless verification risk is non-trivial.
- `classify-and-act`: ambiguous task; classify first, then route to the minimum sufficient worker.
- `fan-out-and-synthesize`: many independent files/items; fan out workers, synthesize only structured results.
- `adversarial-verification`: high-risk claims, security, release gates, or reviews; separate verifier context.
- `generate-and-filter`: options, names, designs, approaches; generate variants and filter by rubric.
- `tournament`: qualitative ranking; compare outputs pairwise instead of absolute scoring.
- `hypothesis-refute-loop`: flaky bugs or incidents; generate hypotheses and refute until one survives or all are blocked.

## Dynamic execution rule

When the user says something like "arbeite den Projektplan mit Meilensteinen ab", do not ask the user to run several commands. Execute this sequence yourself:

1. `python3 ~/.claude/scripts/helix_bootstrap.py --root .`
2. `python3 ~/.claude/scripts/helix_workflow.py plan --root . --force`
3. inspect `.helix/workflows/helix-workflow.json`
4. keep dry run unless the user approved a real run or `.helix/workflows/APPROVED` exists
5. `python3 ~/.claude/scripts/helix_workflow.py run --root .`
6. summarize only `.helix/runs/<run_id>/summary.json`

## When to use

- codebase-wide audits
- large migrations
- independent research with cross-checking
- repeated fix/verify loops
- many low-overlap work units
- milestone plans that should run autonomously until accepted

Do not use this for routine local edits.
