---
description: Disable Helix advisor mode in local Claude settings
allowed-tools: Read, Write, Edit
model: sonnet
---

# `/advisor-off`

Disable advisor mode by updating `~/.claude/settings.local.json`.

Rules:

- preserve existing settings
- ensure `env.HELIX_ADVISOR_MODE` is `"off"`
- ensure the file stays valid JSON
- do not remove unrelated keys
