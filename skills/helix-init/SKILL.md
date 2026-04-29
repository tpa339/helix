---
name: helix-init
description: "Initialize project-local Helix structure and baseline files"
allowed-tools: Read, Write, Edit, Glob, Bash
model: sonnet
user-invocable: true
---

# Helix Init

Default implementation:

`python3 ~/.claude/scripts/helix_bootstrap.py --root .`

Do not overwrite existing files unless the user explicitly requests `--force`.

Create project-local structure:

```text
.helix/
  state/
  specs/
  rules/
  kb/
  changelog/
    daily/
  interview/
  overview/
```

Create baseline files from templates:

- `INTERVIEW.md`
- `PROJECT_STATE.md`
- `ROADMAP.md`
- `PRD.md`
- `SPEC.md`
- `ARCHITECTURE.md`
- `NEGATIVE_CONSTRAINTS.md`
- `TEST_STRATEGY.md`
- `ISSUE_TRACKING.md`
- `LOAD_PLAN.md`
- `ADVISOR_POLICY.md`
- `ADVISOR_LOG.md`
- `PROGRESS.md`
- `LEARNINGS.md`
- `WORK_UNITS.md`
- `QUALITY_GATES.md`
- `RUBRIC.md`
- `REVIEW.md`
- `CHANGELOG.md`
- `daily/YYYY-MM-DD.md`
- `overview/INDEX.md`
- `overview/DECISIONS.md`
- `overview/CURRENT_STATE.md`
- `overview/OPEN_QUESTIONS.md`
