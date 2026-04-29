---
name: helix-ship
description: "Finalize reviewed work, prepare changelog, and gate release-like actions"
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, Agent
model: sonnet
user-invocable: true
---

# Helix Ship

Before shipping:

1. ensure all required units are reviewed
2. verify integration status
3. update project changelog
4. summarize what was shipped and what remains
5. require explicit human confirmation before release-like actions
