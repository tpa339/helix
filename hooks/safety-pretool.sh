#!/bin/zsh
set -euo pipefail

command=$(jq -r '.tool_input.command // empty' 2>/dev/null || true)

if echo "$command" | grep -qE '\brm\s+-(rf|fr)\b'; then
  echo "BLOCKED: Use a reversible delete strategy instead of rm -rf." >&2
  exit 2
fi

if echo "$command" | grep -qE 'git\s+push\s+(origin\s+)?(main|master)\b'; then
  echo "BLOCKED: Never push directly to main/master." >&2
  exit 2
fi

if echo "$command" | grep -qE 'git\s+(reset\s+--hard|clean\s+-[a-zA-Z]*f|push\s+.*--force|branch\s+-D|merge\b|rebase\b)'; then
  echo "BLOCKED: Potentially irreversible git operation. Ask for explicit approval first." >&2
  exit 2
fi

if echo "$command" | grep -qE '\b(chmod\s+-R|chown\s+-R|sudo\s+rm|find\s+.*\s-delete)\b'; then
  echo "BLOCKED: Potentially destructive filesystem operation. Ask for explicit approval first." >&2
  exit 2
fi
