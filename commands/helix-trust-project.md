---
description: Enable project-local Helix autonomy permissions for safe routine commands
allowed-tools: Bash, Read
model: sonnet
---

# `/helix-trust-project`

Use this when Claude Code keeps asking for confirmation on harmless routine commands such as polling test output, reading `/tmp` files, `pgrep`, `sleep`, `git status`, or focused test runs.

## Action

Run:

```bash
python3 ~/.claude/scripts/helix_trust_project.py enable --root .
```

Then report:

```bash
python3 ~/.claude/scripts/helix_trust_project.py status --root .
```

## Scope

This only edits the current project's `.claude/settings.local.json`.

It does not disable:

- global deny rules
- destructive command blocks
- `.env` protections
- `resource-guard.sh`
- `helix-workflow-guard.sh`

## Intended allow-list

- status and polling: `sleep`, `cat /tmp`, `tail /tmp`, `pgrep`, `ps`, `echo`
- safe git reads: `git status`, `git diff`, `git log`, `git show`, `git branch`
- focused tests under `tests/*`
- Helix process status and old-test cleanup

Do not add broad `Bash(*)` or global bypass permissions.
