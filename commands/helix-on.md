---
description: Enable Helix live mode for the current project
allowed-tools: Read, Write, Edit, Bash
model: sonnet
---

# `/helix-on`

Enable Helix live mode for the current project.

This command is intentionally explicit: it creates the project approval file that allows real Helix workflow runs. Without this file, `helix-workflow-guard.sh` blocks workflows with `executor.dry_run=false`.

## Required actions

Run:

```bash
python3 ~/.claude/scripts/helix_bootstrap.py --root .
mkdir -p .helix/workflows .helix/state .helix/changelog/daily
touch .helix/workflows/APPROVED
```

Then write or update `.helix/state/PROJECT_STATE.md` with:

- `helix_live_mode: enabled`
- `workflow_approval: .helix/workflows/APPROVED`
- `enabled_at: <current ISO timestamp>`
- `safety_gate: real workflow runs still require executor.dry_run=false in the workflow spec`

Append a compact entry to `.helix/changelog/CHANGELOG.md` and today's daily changelog:

- Helix live mode enabled for this project.
- Approval file created at `.helix/workflows/APPROVED`.

## Report

End by reporting:

- approval file path
- whether `.helix/workflows/helix-workflow.json` exists
- current value of `executor.dry_run` if the workflow spec exists
- exact next command to start:

```text
/helix-auto Arbeite den Projektplan autonom ab.
```

## Guardrails

- Do not edit `executor.dry_run` automatically unless the user explicitly asks for live execution now.
- Do not disable hooks.
- Do not change global settings.
