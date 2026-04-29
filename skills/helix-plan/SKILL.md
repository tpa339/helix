---
name: helix-plan
description: "Create intent-driven plans with small parallel work units"
allowed-tools: Read, Write, Edit, Glob, Grep, Agent
model: sonnet
user-invocable: true
---

# Helix Plan

Plan by:

- using `INTERVIEW.md` first when goals or constraints are still unclear
- producing `PRD.md`, `SPEC.md`, and `ARCHITECTURE.md` for non-trivial work
- clarifying intent and end state
- defining left and right limits
- identifying independent work streams
- assigning verification and risk classes
- defining plan validation criteria before implementation
- preparing sharding inputs for `WORK_UNITS.md`

Prefer multiple small units over one large implementation block.
