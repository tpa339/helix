# Helix Framework for Claude Code

Helix is a lightweight orchestration framework for Claude Code. It turns vague product requests into a compact, auditable workflow:

1. `/helix-start` bootstraps project-local `.helix/` files.
2. `/interview` resolves material ambiguity with numbered choices.
3. `/blueprint` creates compact PRD, SPEC, architecture, constraints, and test strategy.
4. `/validate-plan` checks readiness before implementation.
5. `/helix`, `/swarm`, `/review`, and `/ship` route execution, evaluation, and release.

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
/helix-start
```

Helix will initialize `.helix/`, interview you if the goal is unclear, write compact planning artifacts, validate the plan, and recommend lean, standard, or swarm execution.

For direct initialization without the interview:

```text
/init-project
```

## Main Commands

- `/helix-start`: full autonomous project start.
- `/interview`: numbered Material Ambiguity interview.
- `/blueprint`: PRD, SPEC, architecture, constraints, and test strategy.
- `/validate-plan`: readiness and quality-gate check.
- `/helix`: route an existing task through the right mode.
- `/swarm`: deterministic multi-agent dispatch for low-overlap work.
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

## What Is Intentionally Excluded

- Personal `CLAUDE.md`.
- `settings.local.json`.
- `.mcp.json` and auth caches.
- `projects/`, `history.jsonl`, `file-history/`, `session-env/`, `todos/`, `telemetry/`, `paste-cache/`, backups, and caches.

See `docs/SECURITY.md` before publishing or accepting external contributions.
