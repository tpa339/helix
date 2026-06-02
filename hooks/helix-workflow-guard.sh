#!/bin/bash
set -euo pipefail

INPUT="$(cat)"

if ! command -v jq >/dev/null 2>&1; then
  exit 0
fi

COMMAND="$(printf '%s' "$INPUT" | jq -r '.tool_input.command // ""')"
CWD="$(printf '%s' "$INPUT" | jq -r '.cwd // "."')"

if [[ "$COMMAND" != *"helix_workflow.py"* || "$COMMAND" != *" run"* ]]; then
  exit 0
fi

SPEC="$CWD/.helix/workflows/helix-workflow.json"
APPROVAL="$CWD/.helix/workflows/APPROVED"

if [[ ! -f "$SPEC" ]]; then
  exit 0
fi

DRY_RUN="$(jq -r 'if (.executor | has("dry_run")) then .executor.dry_run else true end' "$SPEC" 2>/dev/null || echo true)"

if [[ "$DRY_RUN" == "false" && ! -f "$APPROVAL" ]]; then
  echo "BLOCKED: real Helix workflow run requires .helix/workflows/APPROVED or executor.dry_run=true." >&2
  exit 2
fi

exit 0
