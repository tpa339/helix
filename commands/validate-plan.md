---
description: Validate PRD, SPEC, ARCHITECTURE, and plan artifacts before implementation starts
model: opus
allowed-tools: Read, Write, Edit, Glob, Grep, Agent
---

# `/validate-plan`

Validate the active planning artifacts before the implementation swarm starts.

Check:

- consistency between `PRD.md`, `SPEC.md`, and `ARCHITECTURE.md`
- missing acceptance criteria
- missing non-functional requirements
- contradictory boundaries
- missing quality gates
- missing negative constraints
- missing `TEST_STRATEGY.md` for important work
- whether work can be cleanly sharded

Output:

- pass
- pass with warnings
- fail

If validation fails, implementation should not start.
