---
description: Dynamically classify a task, create the needed Helix structure, and autonomously route execution
model: opus
allowed-tools: Read, Write, Edit, MultiEdit, Glob, Grep, Bash, Agent, TodoWrite
---

# `/helix-auto`

Use this as the default autonomous entrypoint for any non-trivial task.

## Contract

Do not follow a fixed workflow. First classify the task, then choose the minimum sufficient process.

## Phase 0: Ensure structure

Run:

`python3 ~/.claude/scripts/helix_bootstrap.py --root .`

Do not overwrite existing files unless the user explicitly asks for `--force`.

## Phase 1: Intake and route

Run the `/helix-intake` logic:

- score ambiguity, scope, risk, novelty, research_need, verification_difficulty, and parallelizability from 0-3
- write `.helix/state/TASK_CARD.md`
- write `.helix/state/ROUTING_DECISION.md`
- select exactly one next route

## Route table

- `direct`: clear, local, low-risk task. Execute with a short plan and focused verification.
- `interview`: material product or architecture ambiguity blocks a correct solution. Ask one grouped numbered-choice interview.
- `steckbrief`: product idea is understandable but lacks users, scope, success criteria, or constraints. Create a compact task/profile brief before planning.
- `catalog`: larger initiative with multiple modules, personas, integrations, or acceptance criteria. Create an requirements catalog.
- `research`: unknown external facts, APIs, market/architecture choices, or current docs matter. Create and execute a research plan.
- `blueprint`: enough clarity exists for PRD/SPEC/ARCHITECTURE/TEST_STRATEGY.
- `swarm`: 3+ independent work units with low file overlap.
- `workflow`: large parallel audit/migration/research or high-stakes adversarial validation. Use Helix-native workflows.

## Autonomy rules

- Make low-risk assumptions yourself and record them.
- Ask the user only when a decision changes product behavior, architecture, cost, privacy, legal/compliance, or destructive operations.
- If asking, use numbered options plus `Eigene Antwort`.
- Prefer the cheapest route that can produce a verifiable result.
- Escalate to `workflow` only when parallelism or independent cross-checking materially improves outcome quality.
- Prefer `/helix-native-workflow` over Claude Code Dynamic Workflows.
- End every run with: route chosen, artifacts changed, verification performed, residual risk, next action.
