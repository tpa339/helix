---
description: Inspect or stop long-running pytest processes spawned by agent runs
allowed-tools: Bash
model: sonnet
---

# `/helix-processes`

Use when tests or agent-spawned commands appear to keep running.

## Status

Run:

```bash
bash ~/.claude/scripts/helix_process_guard.sh status
```

## Stop pytest processes

Ask before stopping unless the user explicitly requested cleanup.

```bash
bash ~/.claude/scripts/helix_process_guard.sh kill-pytest
```

## Stop old pytest processes

Default threshold:

```bash
bash ~/.claude/scripts/helix_process_guard.sh kill-old-pytest 20
```

Report which PIDs were stopped.
