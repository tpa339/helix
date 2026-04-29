---
description: Enable Helix swarm mode in local Claude settings
allowed-tools: Read, Write, Edit
model: sonnet
---

# `/helix-on`

Enable Helix swarm mode by updating `~/.claude/settings.local.json`.

Rules:

- preserve existing settings
- ensure `env.HELIX_SWARM_DEFAULT` is `"1"`
- ensure the file stays valid JSON
- do not remove unrelated keys
- after editing, briefly report the effective Helix mode
