---
description: Enable Helix advisor mode in local Claude settings
allowed-tools: Read, Write, Edit
model: sonnet
---

# `/advisor-on`

Enable advisor mode by updating `~/.claude/settings.local.json`.

Rules:

- preserve existing settings
- ensure `env.HELIX_ADVISOR_MODE` is `"framework"`
- ensure the file stays valid JSON
- do not remove unrelated keys
