---
name: helix-swarm
description: "Run deterministic master-led swarm execution with explicit tasks, worktrees, and hook-enforced quality gates"
allowed-tools: Read, Write, Edit, MultiEdit, Glob, Grep, Bash, Agent, TodoWrite
model: opus
user-invocable: true
---

# Helix Swarm

Use this skill when the task benefits from a master-led multi-agent run.

Operating rules:

- an `Opus` master leads the run
- worker count is explicit, not accidental
- every writing worker is bounded to one work unit
- shared tasks must map to unit ids like `[U-001]`
- require plan approval for risky writing teammates
- keep `AGENT_TOPOLOGY.md` and `DISPATCH_BOARD.md` current
- use hooks as hard gates for task creation, completion, and teammate idling
- integrate only validated units
