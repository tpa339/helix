# Helix Expansion Plan

Purpose: turn Helix from a lightweight routing framework into a small, durable orchestration engine while keeping token use controlled.

## Principles

- Ship in small stages. Each stage must improve real project execution without requiring the later stages.
- Keep orchestration outside the chat context wherever possible.
- Use the cheapest sufficient model per task, not the strongest model per workflow.
- Escalate only on evidence: high risk, repeated failure, broad ambiguity, many dependencies, or adversarial review.
- Every stage must remain inspectable through project-local files under `.helix/`.

## Stage 1: Pattern Engine

Goal: make workflow patterns executable, not just labels.

Current state:

- Helix already assigns `execution_plan.pattern`.
- Runner still executes most task patterns with the same generic phase loop.

Deliverables:

- Add pattern handlers for:
  - `direct-bounded`
  - `classify-and-act`
  - `fan-out-and-synthesize`
  - `adversarial-verification`
  - `generate-and-filter`
  - `tournament`
  - `hypothesis-refute-loop`
  - `loop-until-done`
- Add pattern fields:
  - `synthesis_required`
  - `verifier_count`
  - `loop_condition`
  - `max_loops`
  - `quorum`
  - `budget_tokens`
- Store pattern outputs under `.helix/runs/<run_id>/patterns/<task_id>/`.

Work units:

- U-001: Add pattern schema to `HELIX_WORKFLOW.template.json`.
- U-002: Add pattern handler registry in `helix_workflow.py`.
- U-003: Implement `direct-bounded`, `fan-out-and-synthesize`, and `adversarial-verification` first.
- U-004: Implement `hypothesis-refute-loop` and `loop-until-done`.
- U-005: Add dry-run tests showing different phase plans per pattern.

Acceptance:

- `helix_workflow.py plan` writes pattern-specific execution fields.
- `helix_workflow.py run` changes behavior by pattern.
- Summary shows pattern, attempts, verifier results, synthesis result, and stop reason.

## Stage 2: Skill Registry

Goal: let Helix choose concrete skills from a registry instead of keyword-only labels.

Current state:

- `skill_policy.rules` maps keywords to skill names.
- It does not know cost, risk, tools, path scopes, or when a skill should be avoided.

Deliverables:

- Add `skills/registry.json`.
- Add fields per skill:
  - `name`
  - `description`
  - `triggers`
  - `path_scopes`
  - `allowed_tools`
  - `risk_class`
  - `model_floor`
  - `token_cost`
  - `requires_subagent`
  - `requires_worktree`
  - `verification`
- Add `helix_workflow.py skills --root .` to inspect effective registry.
- Make `infer_required_skills()` use registry metadata.

Work units:

- U-006: Create registry schema and default registry.
- U-007: Wire registry into planning.
- U-008: Add path-aware skill matching.
- U-009: Add report of selected skills and skipped candidate skills.

Acceptance:

- Every task result includes selected skills and why they were selected.
- Helix can explain why it did not use an expensive skill.
- Skill selection is deterministic and editable.

## Stage 3: Subagent And Worktree Scheduler

Goal: convert `use_subagent` and `use_worktree` into controlled execution behavior.

Current state:

- Helix writes `use_subagent` and `use_worktree`.
- The runner still shells out to `claude -p` without creating worktrees.

Deliverables:

- Add scheduler layer:
  - `main-context`
  - `separate-context`
  - `worktree`
  - `read-only-subagent`
- Add worktree creation:
  - branch naming: `helix/<run_id>/<task_id>`
  - path: `.helix/worktrees/<task_id>` or sibling workspace
  - copy/symlink strategy for dependencies
- Add cleanup/report mode.
- Add collision detection for file scopes.

Work units:

- U-010: Add scheduler abstraction.
- U-011: Implement read-only subagent mode.
- U-012: Implement worktree mode with branch naming and safe cleanup.
- U-013: Add file-overlap guard.
- U-014: Add scheduler summary.

Acceptance:

- Writing workers can be isolated in worktrees.
- Review/research workers can run without worktrees.
- Summary shows isolation mode, branch, touched files, and merge recommendation.

## Stage 4: Verifier Quorum And Release Gates

Goal: make quality control structural instead of relying on a single reviewer.

Current state:

- Helix has `test-agent` and `release-gate`.
- Review depth is currently advisory.

Deliverables:

- Add quorum policy:
  - `single`
  - `two_of_three`
  - `security_veto`
  - `human_required`
- Add verifier types:
  - functional verifier
  - security verifier
  - regression verifier
  - product/spec verifier
  - integration verifier
- Add release decision:
  - `pass`
  - `rework`
  - `blocked`
  - `human_required`

Work units:

- U-015: Add quorum schema.
- U-016: Add verifier task generation.
- U-017: Add verifier result merger.
- U-018: Add release decision output.

Acceptance:

- High-risk tasks cannot pass on implementer output alone.
- `security_veto` blocks release even if other verifiers pass.
- Summary explains the exact gate that passed or blocked.

## Stage 5: Budget Controller

Goal: prevent token waste and make model usage explicit.

Current state:

- Helix has basic effort scoring and model tiers.
- It does not enforce a real per-run or per-task budget.

Deliverables:

- Add budget fields:
  - `budget_tokens`
  - `budget_minutes`
  - `max_agents`
  - `max_tool_calls`
  - `max_retries`
  - `max_context_chars`
- Add budget classes:
  - `micro`
  - `standard`
  - `deep`
  - `critical`
- Add budget enforcement:
  - stop before spawning more agents
  - synthesize partials when budget is near limit
  - escalate to user if the target state is impossible under budget

Work units:

- U-019: Add budget policy schema.
- U-020: Add budget estimation during `plan`.
- U-021: Add budget accounting during `run`.
- U-022: Add budget stop reasons.

Acceptance:

- Every generated workflow contains an estimated cost class.
- Every run summary reports budget spent, budget remaining, and stop reason.
- Helix can choose fewer agents or cheaper models when budget is tight.

## Stage 6: Checkpoint, Resume, And Durable State

Goal: let long workflows pause, resume, and recover without redoing completed work.

Current state:

- Results are written under `.helix/runs/<run_id>/`.
- The runner does not resume from incomplete runs.

Deliverables:

- Add run state:
  - `queued`
  - `running`
  - `passed`
  - `failed`
  - `blocked`
  - `paused`
- Add checkpoint file:
  - `.helix/runs/<run_id>/state.json`
- Add commands:
  - `helix_workflow.py resume --root . --run-id <id>`
  - `helix_workflow.py list --root .`
  - `helix_workflow.py pause --root . --run-id <id>`
- Add skip-completed behavior.

Work units:

- U-023: Add state file and run registry.
- U-024: Add list/resume commands.
- U-025: Add skip-completed logic.
- U-026: Add interrupted-run recovery test.

Acceptance:

- Interrupted workflows resume from last incomplete phase.
- Completed tasks are not rerun unless `--force` is passed.
- Summary includes resumed-from checkpoint.

## Recommended Implementation Order

1. Stage 5 partial: model and budget policy foundation.
2. Stage 1 partial: pattern schema plus three core handlers.
3. Stage 2: skill registry.
4. Stage 3: scheduler and worktree isolation.
5. Stage 4: quorum gates.
6. Stage 6: checkpoint/resume.

Reason: model/budget routing affects every later stage. Pattern execution comes next because it makes the orchestrator materially better. Registry and scheduler then make decisions concrete. Quorum and resume harden production use.

