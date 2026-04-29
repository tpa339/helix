# Architecture

Helix uses Claude Code's native extension points instead of a heavy external runtime.

- Commands define the user-facing workflow.
- Skills define reusable operating procedures.
- Agents define bounded roles for planning, execution, review, and integration.
- Templates create project-local durable memory under `.helix/`.
- Hooks add deterministic safety checks around risky tool use.
- Scripts provide small utilities for bootstrapping and advisor-style guidance.

The core pattern is Advisor plus Executors:

- `helix-master` or `helix-advisor` handles hard reasoning and stop/scope decisions.
- Worker agents receive narrow tasks with bounded file scopes.
- Evaluators review independently and should not be the same agent that implemented a unit.

Project knowledge belongs in the target project's `.helix/` directory, not in global prompts.
