# Helix Model And Effort Routing

Purpose: choose the cheapest sufficient model per task while preserving quality on hard reasoning, high-risk verification, and release decisions.

## Core Concept

Do not select a model for the whole workflow. Select a model for each task.

Helix should route by:

- task effort
- role
- risk
- ambiguity
- verification difficulty
- context size
- failure history
- required skills
- workflow pattern

The strong model should be an advisor, release gate, or difficult-reasoning tool. It should not be the default executor for routine work.

## Model Tiers

### Cheap Tier

Use for:

- tiny edits
- deterministic file operations
- simple docs/copy changes
- low-risk classification
- small grep/read/summarize tasks

Default model class:

- Haiku-style

Rules:

- No broad architecture decisions.
- No production/security release decisions.
- No final validation for high-risk work.

### Standard Tier

Use for:

- normal implementation
- frontend/backend unit work
- tests
- debugging with clear reproduction
- medium-scope refactors
- synthesis of low-risk worker outputs

Default model class:

- Sonnet-style

Rules:

- Can write code.
- Can run verification.
- Should escalate after repeated failure or broad ambiguity.

### Strong Tier

Use for:

- architecture choices
- security/auth/payment/privacy tasks
- repeated failures
- release gates
- adversarial verification
- large migrations with unclear constraints
- task classification when wrong routing would be expensive

Default model class:

- Opus-style

Rules:

- Prefer short advisory output.
- Avoid full implementation unless the task genuinely requires strong reasoning throughout.
- Use as reviewer/advisor before committing to complex direction.

## Effort Score

Each task gets a score from these dimensions:

- ambiguity: 0-3
- risk: 0-3
- novelty: 0-3
- verification difficulty: 0-3
- file/dependency spread: 0-3
- role weight: 0-3
- failure history: 0-3

Suggested effort bands:

| Score | Effort | Default Tier | Typical Handling |
| --- | --- | --- | --- |
| 0-2 | xs | cheap | Direct bounded task |
| 3-5 | s | standard | Single worker, focused verification |
| 6-8 | m | standard | Worker plus verifier if risk exists |
| 9-11 | l | strong advisor or strong verifier | Advisor/reviewer required |
| 12+ | xl | strong | Split, classify, or require plan validation |

## Role Floors

Some roles must not fall below a tier:

| Role | Minimum Tier | Reason |
| --- | --- | --- |
| worker | cheap | Routine tasks can be cheap |
| frontend-dev | standard | UI changes require coherence and verification |
| backend-dev | standard | API/data changes require reliability |
| test-agent | standard | Weak tests create false confidence |
| researcher | standard | Source triage and synthesis need accuracy |
| review-agent | strong | Adversarial reasoning is the value |
| release-gate | strong | Final risk decision must be high quality |
| advisor | strong | Advisor exists for difficult judgment |

## Escalation Rules

Escalate one tier when:

- same task fails twice
- tests fail after a repair loop
- implementation contradicts spec
- task touches auth, payment, privacy, secrets, migrations, or production deploy
- more than five files are likely touched
- task requires interpreting external/current documentation
- reviewer flags unresolved risk

Escalate directly to strong when:

- release gate
- security veto
- architectural fork
- repeated non-converging loop
- human decision needed but options must be prepared

## De-escalation Rules

De-escalate when:

- task is read-only
- task only classifies or summarizes known local files
- task has explicit file scope and deterministic output
- verification is mechanical
- prior strong advisor already produced a clear plan

Example:

1. Strong advisor creates a 7-step migration plan.
2. Standard workers execute each step.
3. Standard test-agent verifies.
4. Strong release-gate reviews only final risk.

## Context Policy

Context size should affect model selection, but large context should not automatically mean strong model.

Rules:

- First reduce context through file pointers and summaries.
- Use cheap/standard workers on narrow slices.
- Use strong model only for synthesis, contradictions, or high-risk judgment.
- If a task needs more than 50k context tokens, split it unless the task is pure synthesis.

## Advisor Pattern

Use strong model as advisor when:

- task is complex but execution is mostly mechanical
- the standard worker is likely good enough after receiving a plan
- wrong approach would cause large rework

Advisor prompt should be short:

```text
Return under 120 words. Give decision, key constraints, and next 3 steps. No implementation.
```

Advisor max uses:

- low/medium task: 0-1
- high task: 1-2
- critical task: 2-3

## Proposed Policy Object

```json
{
  "model_policy": {
    "cheap": "haiku",
    "standard": "sonnet",
    "strong": "opus",
    "role_floor": {
      "worker": "cheap",
      "frontend-dev": "standard",
      "backend-dev": "standard",
      "test-agent": "standard",
      "researcher": "standard",
      "review-agent": "strong",
      "release-gate": "strong",
      "advisor": "strong"
    },
    "effort_bands": [
      {"max_score": 2, "tier": "cheap"},
      {"max_score": 8, "tier": "standard"},
      {"max_score": 99, "tier": "strong"}
    ],
    "escalation": {
      "failures_to_escalate": 2,
      "security_keywords_force_strong": true,
      "release_gate_force_strong": true,
      "advisor_max_uses": 2
    },
    "context": {
      "split_above_tokens": 50000,
      "strong_synthesis_above_shards": 6
    }
  }
}
```

## Implementation Plan

1. Add `role_floor` and `effort_bands` to workflow specs.
2. Replace current role-default model selection with tier resolution:
   - base tier from effort score
   - apply role floor
   - apply risk escalation
   - apply failure-history escalation
3. Store selected tier and reason in each task result.
4. Add budget estimate during planning.
5. Add budget summary after each run.

## Acceptance

- Every task result includes:
  - selected model
  - selected tier
  - reason
  - effort score
  - escalation flags
- Strong model is used only for tasks that justify it.
- Release-gate and review-agent never fall below strong.
- Routine work can run on cheap tier.

