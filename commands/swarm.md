---
description: Run the task in Master-Swarm mode with an Opus head and many bounded parallel workers
model: opus
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, Agent, TodoWrite
---

# `/swarm`

Use this command when the task is large enough to benefit from explicit multi-agent orchestration.

## Workflow

1. clarify intent, purpose, end state, and boundaries
2. create or update:
   - `PROJECT_STATE.md`
   - `PLAN.md`
   - `WORK_UNITS.md`
   - `AGENT_TOPOLOGY.md`
   - `DISPATCH_BOARD.md`
3. classify the run:
   - `lean`
   - `standard`
   - `swarm`
4. spawn the minimum number of workers that preserves throughput
5. assign one writing unit per worktree
6. route hard reasoning to advisor or master
7. require evaluator review before integration
8. integrate only validated units
9. if advisor mode is active, keep `ADVISOR_LOG.md` current

## Dispatch rules

- prefer 3-5 workers for most multi-stream tasks
- prefer 6-8 workers only when file overlap is low
- keep each worker on one bounded unit
- use Codex for bounded execution and validation where useful
- use Claude for planning, synthesis, and integration
- do not let worker count grow without updating the dispatch board
