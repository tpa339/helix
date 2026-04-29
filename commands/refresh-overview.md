---
description: Compress changelog and working artifacts into the project overview files without losing traceability
model: sonnet
allowed-tools: Read, Write, Edit, Glob, Grep
---

# `/refresh-overview`

Refresh the compact project overview.

## Required behavior

Update or create:

- `overview/INDEX.md`
- `overview/DECISIONS.md`
- `overview/CURRENT_STATE.md`
- `overview/OPEN_QUESTIONS.md`

Rules:

- compress, do not duplicate raw logs
- reference changelog ids where possible
- keep only durable information
- treat `overview/INDEX.md` as the main human entry point
