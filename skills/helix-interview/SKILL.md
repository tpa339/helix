---
name: helix-interview
description: "Run a structured interview to clarify goals, constraints, scope, and open questions before planning"
allowed-tools: Read, Write, Edit, Glob, Grep, Agent
model: opus
user-invocable: true
---

# Helix Interview

Use this skill before planning when the target is not yet sharp enough.
Run it as an interactive Material Ambiguity interview, not as an open-ended brainstorm.

Output:

- `INTERVIEW.md`
- first `PROJECT_STATE.md`
- first `overview/OPEN_QUESTIONS.md`
- early scope notes for `PRD.md`

Rules:

- ask only the highest-leverage questions
- ask one grouped batch, not a long chain
- use numbered choices so the user can answer with `1.2, 2.1, 3: custom`
- include `Eigene Antwort` as the final option for each question
- add a recommended default only when the decision is low-risk
- prioritize purpose, scope, constraints, risks, and success definition
- document answers cleanly
- derive explicit assumptions where answers are still missing
- separate confirmed decisions from open questions

Question format:

```text
Material Ambiguity — before I plan/build, I need N decisions:

1. <decision question>
   1. <option>
   2. <option>
   3. <option>
   4. Eigene Antwort

Antwortformat: `1.2, 2.1, 3: eigene Antwort`.
```

After the user answers:

- normalize the choices into confirmed decisions
- record assumptions and unresolved questions
- update `INTERVIEW.md`, `PROJECT_STATE.md`, and `overview/OPEN_QUESTIONS.md`
- continue to blueprint when no high-risk ambiguity remains
