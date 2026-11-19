#!/usr/bin/env bash
# Install the shared hooks into the user-level Claude Code settings.
# Run from a clone at ~/.claude/claude-hooks:
#   git clone https://github.com/luuvminh/claude-hooks ~/.claude/claude-hooks
#   bash ~/.claude/claude-hooks/install.sh
set -euo pipefail
dir="$(cd "$(dirname "$0")" && pwd)"
claude="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
python3 "$dir/bin/link-skills.py" "$claude/skills"
python3 "$dir/bin/merge-settings.py" "$claude/settings.json" "$dir"
