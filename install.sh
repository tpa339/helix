#!/usr/bin/env bash
set -euo pipefail

repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
target="${CLAUDE_HOME:-$HOME/.claude}"
backup="$target/backups/helix-install-$(date +%Y%m%d-%H%M%S)"

copy_tree() {
  local dir="$1"
  mkdir -p "$target/$dir"
  if [ -d "$target/$dir" ] && find "$target/$dir" -maxdepth 1 -type f | grep -q .; then
    mkdir -p "$backup/$dir"
    cp -R "$target/$dir/." "$backup/$dir/"
  fi
  cp -R "$repo_dir/$dir/." "$target/$dir/"
}

mkdir -p "$target"

for dir in agents commands skills hooks scripts templates; do
  copy_tree "$dir"
done

cp "$repo_dir/settings.helix.example.json" "$target/settings.helix.example.json"

chmod +x "$target/hooks/"*.sh 2>/dev/null || true
chmod +x "$target/scripts/"*.py 2>/dev/null || true

echo "Helix installed to $target"
if [ -d "$backup" ]; then
  echo "Backups written to $backup"
fi
echo "Next: open Claude Code in a project and run /helix-start"
echo "Optional: merge hooks/env from $target/settings.helix.example.json into your Claude Code settings."
