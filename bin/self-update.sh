#!/usr/bin/env bash
# SessionStart: at most every 6 hours, pull claude-hooks in the background and
# reinstall when it changed. Never blocks or fails the session.
dir="$(cd "$(dirname "$0")/.." && pwd)"
state="${CLAUDE_CONFIG_DIR:-$HOME/.claude}/claude-hooks-state"
mkdir -p "$state" 2>/dev/null || exit 0
stamp="$state/last-update"
[ -d "$dir/.git" ] || exit 0
if [ -f "$stamp" ] && [ -z "$(find "$stamp" -mmin +360 2>/dev/null)" ]; then exit 0; fi
touch "$stamp"
(
  before=$(git -C "$dir" rev-parse HEAD 2>/dev/null)
  git -C "$dir" pull -q --ff-only 2>/dev/null || exit 0
  [ "$(git -C "$dir" rev-parse HEAD)" = "$before" ] || bash "$dir/install.sh"
) >"$state/last-update.log" 2>&1 </dev/null &
exit 0
