---
description: Run the full Helix industrial blueprint with spec-first planning, plan validation, sharding, gated execution, and review-controlled delivery
model: opus
allowed-tools: Read, Write, Edit, MultiEdit, Glob, Grep, Bash, Agent, TodoWrite
---

# `/blueprint`

Use the industrial blueprint for any serious project or large feature.

## Phase order

1. interview and discovery if needed:
   - `INTERVIEW.md`
   - `PROJECT_STATE.md`
   - `overview/OPEN_QUESTIONS.md`
2. analyst/pm swarm:
   - `PRD.md`
   - `SPEC.md`
   - `ARCHITECTURE.md`
   - `PROJECT_STATE.md`
   - `NEGATIVE_CONSTRAINTS.md`
3. validate the plan
4. scrum-master sharding:
   - `PLAN.md`
   - `WORK_UNITS.md`
   - `AGENT_TOPOLOGY.md`
   - `DISPATCH_BOARD.md`
   - `QUALITY_GATES.md`
   - `PROGRESS.md`
   - `LEARNINGS.md`
   - `TEST_STRATEGY.md`
   - `ISSUE_TRACKING.md`
   - `LOAD_PLAN.md` when relevant
   - `ADVISOR_POLICY.md`
   - `ADVISOR_LOG.md`
5. execute with bounded workers
6. independently evaluate
7. integrate
8. consolidate project memory and changelog
9. require human review for high-risk transitions

## Required behavior

- use `Opus` as master and thinking head
- use cheaper workers for implementation and review where possible
- if the target is still fuzzy, do not skip the interview phase
- do not skip gates
- do not let research replace explicit requirements
- add explicit negative constraints before broad implementation
- derive tests from the spec, not just from the current code
- keep every phase auditable through files
