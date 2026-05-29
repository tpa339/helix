---
description: Decide and execute the minimum necessary research depth before planning
model: opus
allowed-tools: Read, Write, Edit, Glob, Grep, WebSearch, WebFetch, Agent
---

# `/helix-research`

Use when local context is not enough.

## Research levels

- `R0`: no research; local execution is enough
- `R1`: local repo scan only
- `R2`: focused docs/source lookup, 2-5 primary sources
- `R3`: deep research across several angles with source comparison
- `R4`: adversarial research with independent claims and refutation

## Required behavior

1. Read `.helix/state/TASK_CARD.md` and `.helix/state/ROUTING_DECISION.md`.
2. Choose the minimum level that can support a correct plan.
3. Write `.helix/specs/RESEARCH_PLAN.md`.
4. Execute the plan only as far as needed.
5. Write findings into `.helix/overview/DECISIONS.md` or `.helix/specs/SPEC.md`.
6. Discard irrelevant findings.

Prefer primary sources for technical claims.

