---
name: helix-start
description: "Autonomous project start: bootstrap, interview, blueprint, validation, and dispatch recommendation"
allowed-tools: Read, Write, Edit, MultiEdit, Glob, Grep, Bash, Agent, TodoWrite
model: opus
user-invocable: true
---

# Helix Start

Use this skill when a project or large feature needs to move from idea to implementation-ready state.

## Contract

- bootstrap `.helix/` if missing
- interview the user only where information is missing
- use the numbered Material Ambiguity interview format from `helix-interview`
- produce compact planning artifacts
- validate before implementation
- choose lean, standard, or swarm mode
- do not require the user to manually call follow-up commands

## Required artifacts

- `.helix/interview/INTERVIEW.md`
- `.helix/state/PROJECT_STATE.md`
- `.helix/specs/PRD.md`
- `.helix/specs/SPEC.md`
- `.helix/specs/ARCHITECTURE.md`
- `.helix/specs/NEGATIVE_CONSTRAINTS.md`
- `.helix/specs/TEST_STRATEGY.md`
- `.helix/specs/QUALITY_GATES.md`

## Autonomy rules

- ask one grouped interview, not a chain of tiny questions
- let the user answer with numbers or short custom text
- infer low-risk defaults and record them as assumptions
- stop only for high-risk ambiguity, destructive actions, or conflicting requirements
- route hard strategic uncertainty to `helix-advisor`
