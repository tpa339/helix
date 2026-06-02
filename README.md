# Helix Framework for Claude Code

Helix is a lightweight orchestration framework for Claude Code. It turns vague product requests into a compact, auditable workflow:

1. `/helix-auto` classifies the task and chooses the minimum sufficient route.
2. `/helix-start` bootstraps project-local `.helix/` files when needed.
3. `/interview` resolves material ambiguity with numbered choices.
4. `/helix-catalog` creates a compact requirements catalog for larger initiatives.
5. `/helix-research` chooses the minimum necessary research depth.
6. `/blueprint` creates compact PRD, SPEC, architecture, constraints, and test strategy.
7. `/validate-plan` checks readiness before implementation.
8. `/helix`, `/swarm`, `/helix-native-workflow`, `/review`, and `/ship` route execution, evaluation, and release.

The framework is designed for token efficiency: global instructions stay small, durable project state lives in files, and workers receive narrow task contexts.

## Install

From a cloned repo:

```bash
bash install.sh
```

One-line install after publishing:

```bash
git clone https://github.com/YOUR_ORG/helix-framework.git && cd helix-framework && bash install.sh
```

The installer copies only Helix framework files into `~/.claude`. It does not copy runtime logs, session history, project transcripts, local settings, MCP auth files, or a personal `CLAUDE.md`.

## Quick Start

In any project:

```text
/helix-auto <your task>
```

Helix will initialize `.helix/`, classify complexity, decide whether to ask, research, create a catalog, blueprint, execute directly, spawn workers, or create a Helix-native workflow.

For direct initialization without the interview:

```text
/init-project
```

## Main Commands

- `/helix-start`: full autonomous project start.
- `/helix-auto`: dynamic intake, classification, and routing.
- `/helix-intake`: task card and routing decision.
- `/interview`: numbered Material Ambiguity interview.
- `/helix-catalog`: requirements catalog for larger initiatives.
- `/helix-research`: research depth R0-R4.
- `/blueprint`: PRD, SPEC, architecture, constraints, and test strategy.
- `/validate-plan`: readiness and quality-gate check.
- `/helix`: route an existing task through the right mode.
- `/swarm`: deterministic multi-agent dispatch for low-overlap work.
- `/helix-workflow`: prepare Helix-native workflows for large parallel/adversarial work.
- `/helix-native-workflow`: create and run `.helix/workflows/*.json` with the Helix runner.
- `/review`: independent review.
- `/ship`: final verification and changelog discipline.
- `/advisor`: consult the higher-intelligence advisor pattern when useful.

## What Is Included

- `agents/`: Helix roles for advisor, coordinator, planner, workers, evaluator, and integrator.
- `commands/`: Claude Code slash commands.
- `skills/`: reusable Helix workflows.
- `hooks/`: safety and task guard hooks.
- `scripts/`: bootstrap and advisor helper scripts.
- `templates/`: project-local `.helix/` artifacts.

## Helix-Native Workflows

Helix does not need Claude Code Dynamic Workflows. For large parallel work, it creates a versionable workflow spec under `.helix/workflows/` and stores all prompts/results under `.helix/runs/`.
For project plans, Helix converts milestones into role-based tasks, runs implementers and test agents, retries failed milestones, and stops only when the target state is reached or blockers are documented.

```bash
python3 ~/.claude/scripts/helix_workflow.py init --root .
python3 ~/.claude/scripts/helix_workflow.py run --root .
python3 ~/.claude/scripts/helix_workflow.py status --root .
```

## What Is Intentionally Excluded

- Personal `CLAUDE.md`.
- `settings.local.json`.
- `.mcp.json` and auth caches.
- `projects/`, `history.jsonl`, `file-history/`, `session-env/`, `todos/`, `telemetry/`, `paste-cache/`, backups, and caches.

See `docs/SECURITY.md` before publishing or accepting external contributions.
