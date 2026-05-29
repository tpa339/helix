---
description: Run Helix as the default autonomous orchestrator for the current task
model: opus
allowed-tools: Read, Write, Edit, MultiEdit, Glob, Grep, Bash, Agent, TodoWrite
---

# `/helix`

Use Helix as the task operating system.

## Routing

- For any non-trivial or unclear request, run `/helix-auto` first.
- If `.helix/` is missing or the project goal is unclear, run the `/helix-start` flow automatically.
- If planning artifacts exist but validation is missing or stale, run the validation part before implementation.
- If the task is narrow and local, use `lean` mode and execute directly.
- If there are 3 or more low-overlap units, create `WORK_UNITS.md`, `AGENT_TOPOLOGY.md`, and `DISPATCH_BOARD.md`, then dispatch workers.

## Required behavior

1. clarify intent, purpose, end state, boundaries, risk class, and proof
2. create only the artifacts needed for the task size
3. keep worker prompts minimal
4. use advisor only for hard ambiguity, repeated failure, or high-risk design choices
5. require independent evaluation before integration
6. use Claude Code dynamic workflows only for large parallel work or adversarial verification
7. end with proof, residual risk, and the next recommended action
