---
description: Escalate suitable work into a Claude Code dynamic workflow
model: opus
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, Agent
---

# `/helix-workflow`

Use when a task needs many agents, repeatable orchestration, adversarial validation, or long-running parallel work.

## Workflow candidates

- codebase-wide security, auth, performance, dead-code, or migration audits
- large migrations touching many independent files
- research questions that need independent source cross-checking
- high-stakes plans that need several independent drafts and refutation
- repeated CI/test-fix loops across independent failures

## Required behavior

1. Read `.helix/state/TASK_CARD.md`, `.helix/state/ROUTING_DECISION.md`, `WORK_UNITS.md`, and `QUALITY_GATES.md` when present.
2. Write `.helix/specs/WORKFLOW_BRIEF.md`.
3. Ask Claude Code to create a dynamic workflow from that brief.
4. Require approval before launching expensive workflow runs.
5. Make the workflow phases explicit:
   - orient
   - shard
   - execute in parallel
   - adversarial review
   - integrate
   - verify
   - summarize
6. Save successful reusable workflows as project commands under `.claude/workflows/` when appropriate.

Do not use workflows for routine one-file work.

