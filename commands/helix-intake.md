---
description: Classify task complexity and decide the minimum sufficient Helix route
model: opus
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---

# `/helix-intake`

Classify the user's task before planning or coding.

## Scoring

Score each dimension from 0-3:

- `ambiguity`: unclear goal, missing decisions, multiple plausible interpretations
- `scope`: number of files/systems/modules/users affected
- `risk`: security, data loss, money, production, legal/compliance, destructive changes
- `novelty`: unfamiliar domain, architecture, library, API, or business model
- `research_need`: need for current docs, external sources, benchmarks, or comparisons
- `verification_difficulty`: difficulty of proving the task is complete
- `parallelizability`: benefit from independent workers or adversarial review

## Required outputs

Write `.helix/state/TASK_CARD.md` using `TASK_CARD.template.md`.
Write `.helix/state/ROUTING_DECISION.md` using `ROUTING_DECISION.template.md`.

## Routing heuristic

- total 0-4: `direct`
- total 5-8: `interview` or `steckbrief`
- total 9-13: `blueprint` or `research`
- total 14-18: `catalog` plus `validate-plan`
- total 19+: `workflow` or `swarm`

Override the total when a single hard blocker dominates:

- ambiguity >= 2 and product behavior changes: `interview`
- research_need >= 2: `research`
- risk >= 2: `blueprint` plus independent review
- parallelizability >= 2 and scope >= 2: `swarm` or `workflow`
- scope >= 3 and repeatable orchestration matters: `workflow`

## Output to user

Return only:

- chosen route
- why this route is sufficient
- what will be created next
- any question that blocks progress

