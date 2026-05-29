# Dynamic Autonomy Model

Helix uses commands and scripts for active orchestration. Hooks are deterministic event gates.

## Why hooks are not the orchestrator

Claude Code hooks fire on events such as tool use, file changes, and stop conditions. They are useful for safety, logging, validation, and preventing bad actions. They should not be the main place where product logic or code generation lives, because hooks run outside the user's task intent and can become invisible automation.

## Active control plane

Use this chain for autonomous work:

```text
/helix-auto
  -> bootstrap .helix/
  -> /helix-intake
  -> direct | interview | steckbrief | catalog | research | blueprint | swarm | helix-native workflow
  -> verify
  -> changelog / state update
```

## Dynamic routing

The agent scores each task:

- ambiguity
- scope
- risk
- novelty
- research_need
- verification_difficulty
- parallelizability

The route decides how much structure to create. Small tasks do not get large plans. Large or risky tasks get catalogs, validation gates, workers, or dynamic workflows.

## Hooks in Helix

Hooks should do these things:

- block destructive shell commands
- enforce task state consistency
- warn when context or task state is missing
- record completion events
- run lightweight validation after file changes

Hooks should not silently launch expensive multi-agent work.

## Helix-native workflows

Use Helix-native workflows when orchestration should move out of Claude's context and into a versionable project artifact:

- many independent agents
- repeatable audit or migration
- adversarial verification
- long-running work
- intermediate results should stay out of Claude's context window

The orchestration file is `.helix/workflows/helix-workflow.json`. The runner stores prompts, results, and summaries in `.helix/runs/`.
