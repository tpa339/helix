---
description: Disable Helix swarm mode by updating local Claude settings
allowed-tools: Read, Write, Edit
model: sonnet
---

# `/helix-off`

Disable default Helix swarm behavior by updating `~/.claude/settings.local.json`.

Rules:

- preserve existing settings
- ensure `env.HELIX_SWARM_DEFAULT` is `"0"`
- keep `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` untouched unless the user explicitly asks to disable agent teams entirely
- ensure the file stays valid JSON
- do not remove unrelated keys
