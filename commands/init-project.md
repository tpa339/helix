---
description: Create project-local Helix structure without overwriting existing files
model: sonnet
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---

# `/init-project`

Initialize the project-local Helix file structure.

Run:

`python3 ~/.claude/scripts/helix_bootstrap.py --root .`

Then report:

- files created
- files skipped because they already existed
- next recommended command, usually `/helix-start`

Do not overwrite existing project files unless the user explicitly asks for `--force`.
