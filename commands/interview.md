---
description: Run a structured project interview before planning, document the answers, and derive the initial project state
model: opus
allowed-tools: Read, Write, Edit, Glob, Grep, Agent
---

# `/interview`

Use this command when the project goal, scope, or constraints are still not precise enough.
The goal is an interactive Material Ambiguity interview: the user should be able to answer mostly with numbers, plus optional free text.

## Required behavior

1. Identify only decisions that materially change product behavior, architecture, risk, cost, or scope.
2. Ask one grouped batch of at most 7 questions. Prefer numbered choices over open-ended questions.
3. Use this format:

```text
Material Ambiguity — before I plan/build, I need N decisions:

1. <decision question>
   1. <option>
   2. <option>
   3. <option>
   4. Eigene Antwort

Antwortformat: `1.2, 2.1, 3: eigene Antwort`.
```

4. Include a recommended default only when it is genuinely low-risk: `Empfehlung: 1.2, weil ...`.
5. Accept compact answers such as `1b, 2a, 3 alle, 4 lean` and normalize them.
6. After the answer, write a short decision summary:
   - confirmed decisions
   - assumptions
   - open questions
   - next action
7. If high-risk ambiguity remains, ask one more compact batch. Otherwise continue to `/blueprint` or `/plan`.
8. Write or update:
   - `INTERVIEW.md`
   - `PROJECT_STATE.md`
   - `overview/OPEN_QUESTIONS.md`
9. Prepare the output so that `/blueprint` or `/plan` can start without re-asking the same questions.

## Question priorities

- product objective and success criteria
- target users and primary workflow
- MVP scope and explicit non-goals
- tool shape or delivery form
- technical constraints and existing stack
- verification method
- risk class and approval gates
