---
name: helix-execute
description: "Execute work units with parallel workers and independent evaluation"
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, Agent, TodoWrite
model: sonnet
user-invocable: true
---

# Helix Execute

Execution rules:

- dispatch read-heavy research in parallel
- dispatch independent implementation units in parallel
- keep each worker context minimal
- route uncertainty to advisor instead of bloating every worker
- require evaluator review before integration
- if there are 3 or more independent units, create `AGENT_TOPOLOGY.md` and `DISPATCH_BOARD.md`
- assign each writing worker one branch and one worktree
- prefer `Opus` as master, `Sonnet/Haiku` as executors, and `Codex` for bounded execution or review where available
