---
description: Force a strategic advisor pass on the current task without handing implementation over to the advisor
model: opus
allowed-tools: Read, Write, Edit, Glob, Grep, Agent
---

# `/advisor`

Run a strategic advisor checkpoint.

## Required behavior

1. read the current relevant artifacts
2. invoke the advisor role
3. return one structured decision:
   - `plan`
   - `course_correction`
   - `stop`
   - `escalate`
   - `no_advice_needed`
4. log the result in `ADVISOR_LOG.md`
5. do not let the advisor implement code directly
