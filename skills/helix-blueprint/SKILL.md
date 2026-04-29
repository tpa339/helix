---
name: helix-blueprint
description: "Run the industrial Helix blueprint: spec-first planning, validation gates, sharding, bounded implementation, and review-gated delivery"
allowed-tools: Read, Write, Edit, MultiEdit, Glob, Grep, Bash, Agent, TodoWrite
model: opus
user-invocable: true
---

# Helix Blueprint

This skill is the industrial operating model.

Sequence:

1. run interview and discovery if the target is still fuzzy
2. produce `PRD.md`, `SPEC.md`, `ARCHITECTURE.md`, `PROJECT_STATE.md`
3. validate the plan before implementation
4. shard the work into independent stories and units
5. create `AGENT_TOPOLOGY.md`, `DISPATCH_BOARD.md`, and `QUALITY_GATES.md`
6. run bounded workers in parallel
7. require independent evaluation
8. integrate only validated work
9. finish with memory and changelog consolidation

Rules:

- do not skip the plan gate
- do not start broad implementation from chat alone
- do not increase worker count without file-scope discipline
- do not treat research as a substitute for specification
