---
description: Derive tests from PRD and SPEC before implementation, so validation checks the intended product rather than the current implementation
model: opus
allowed-tools: Read, Write, Edit, Glob, Grep, Agent
---

# `/prepare-tests`

Create or update `TEST_STRATEGY.md` and spec-derived test cases before broad implementation.

Rules:

- infer intended behavior from `PRD.md` and `SPEC.md`
- identify edge cases and missing requirements
- do not optimize tests for the current implementation
- document what must be tested, not just what already exists
