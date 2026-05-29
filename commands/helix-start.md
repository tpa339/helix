---
description: Start a project autonomously through Helix: bootstrap, interview, blueprint, validation, and next dispatch decision
model: opus
allowed-tools: Read, Write, Edit, MultiEdit, Glob, Grep, Bash, Agent, TodoWrite
---

# `/helix-start`

Run the full guided Helix start without requiring the user to manually call each command.

## Flow

1. Bootstrap project structure:
   - run `python3 ~/.claude/scripts/helix_bootstrap.py --root .`
   - do not overwrite existing project files unless the user explicitly asks
2. Intake:
   - run `/helix-intake`
   - write `.helix/state/TASK_CARD.md`
   - write `.helix/state/ROUTING_DECISION.md`
   - choose direct, interview, steckbrief, catalog, research, blueprint, swarm, or workflow
3. Orient:
   - read project `CLAUDE.md`
   - read `.helix/interview/INTERVIEW.md`
   - read `.helix/state/PROJECT_STATE.md`
   - inspect only the minimum files needed to understand the repo shape
4. Interview when routed:
   - use the `/interview` Material Ambiguity protocol
   - ask at most 7 high-leverage questions at once with numbered choices
   - let the user answer compactly, for example `1.2, 2.1, 3: custom`
   - if enough information already exists, skip questions and state the assumption
   - write answers to `.helix/interview/INTERVIEW.md`
   - update `.helix/state/PROJECT_STATE.md`
   - update `.helix/overview/OPEN_QUESTIONS.md`
5. Catalog or research when routed:
   - use `/helix-catalog` for multi-part requirements
   - use `/helix-research` for unknown external facts or current docs
6. Blueprint:
   - create or update `.helix/specs/PRD.md`
   - create or update `.helix/specs/SPEC.md`
   - create or update `.helix/specs/ARCHITECTURE.md`
   - create or update `.helix/specs/NEGATIVE_CONSTRAINTS.md`
   - create or update `.helix/specs/TEST_STRATEGY.md`
7. Validate:
   - check consistency, acceptance criteria, boundaries, risks, test strategy, and sharding potential
   - write result to `.helix/specs/QUALITY_GATES.md`
8. Decide next mode:
   - `lean`: direct implementation
   - `standard`: 2-4 bounded workers
   - `swarm`: 5-8 workers with low overlap and worktrees
   - `workflow`: Claude Code dynamic workflow for large parallel/repeatable/adversarial work
   - stop for human approval if risk is high or requirements conflict

## Rules

- The user should only need to answer the interview or approve a high-risk gate.
- Do not ask the user to run `/interview`, `/blueprint`, or `/validate-plan` manually.
- Do not proceed from idea to blueprint while material product or architecture ambiguity is unresolved.
- Do not generate documents for their own sake; write compact artifacts that guide execution.
- Use `helix-advisor` only for high-risk ambiguity or plan conflicts.
- Use hooks as safety gates and logging, not as the primary orchestration engine.
- End with one clear next action: proceed, ask, or stop.
