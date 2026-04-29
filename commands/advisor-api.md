---
description: Use the optional local Anthropic Advisor API bridge when configured
model: sonnet
allowed-tools: Read, Bash, Write, Edit, Glob, Grep
---

# `/advisor-api`

Use the local advisor sidecar if it exists.

Rules:

- only use when `HELIX_ADVISOR_MODE=api`
- read the current project artifacts
- pass compact structured context to the sidecar
- write the returned guidance into `ADVISOR_LOG.md`
- if the sidecar is unavailable, fall back to framework advisor mode
