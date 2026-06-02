---
description: Disable Helix live mode for the current project
allowed-tools: Read, Write, Edit, Bash
model: sonnet
---

# `/helix-off`

Disable Helix live mode for the current project.

## Required actions

Run:

```bash
rm -f .helix/workflows/APPROVED
```

Then write or update `.helix/state/PROJECT_STATE.md` with:

- `helix_live_mode: disabled`
- `workflow_approval: absent`
- `disabled_at: <current ISO timestamp>`

Append a compact entry to `.helix/changelog/CHANGELOG.md` and today's daily changelog:

- Helix live mode disabled for this project.
- Approval file removed from `.helix/workflows/APPROVED`.

## Guardrails

- Do not delete `.helix/workflows/helix-workflow.json`.
- Do not delete run history.
- Do not change global settings.
- Do not disable Helix commands or hooks.
