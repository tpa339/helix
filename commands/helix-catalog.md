---
description: Create a compact requirements catalog for larger or multi-part initiatives
model: opus
allowed-tools: Read, Write, Edit, Glob, Grep, Agent
---

# `/helix-catalog`

Use when the task is larger than a single feature or has multiple users, modules, integrations, risks, or acceptance criteria.

## Required behavior

1. Read `.helix/state/TASK_CARD.md`, `.helix/interview/INTERVIEW.md`, and existing specs if present.
2. Create or update `.helix/specs/REQUIREMENTS_CATALOG.md`.
3. Keep it compact and decision-oriented.
4. Separate confirmed requirements from assumptions and open decisions.
5. Add acceptance criteria that can be verified.
6. Route to `/blueprint` when enough is known, otherwise ask a numbered-choice interview.

