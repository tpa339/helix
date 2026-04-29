# Security and Publish Checklist

Do not publish a raw `~/.claude` directory.

Helix releases should include only:

- `agents/helix-*.md`
- `commands/*.md`
- `skills/helix-*`
- `hooks/`
- `scripts/helix_*.py`
- `templates/*.template.md`
- `README.md`, `install.sh`, `settings.helix.example.json`, and docs

Never publish:

- personal `CLAUDE.md`
- `settings.local.json`
- `.mcp.json`
- API keys, OAuth caches, or MCP auth files
- `projects/`, `history.jsonl`, `file-history/`, `session-env/`, `todos/`, `telemetry/`, `paste-cache/`
- backups or generated caches

Before pushing:

```bash
rg -n "(sk-|AKIA|BEGIN (RSA|OPENSSH|PRIVATE)|ANTHROPIC_API_KEY|OPENAI_API_KEY|password|secret|bearer|oauth|/Users/)" .
git status --short
```
