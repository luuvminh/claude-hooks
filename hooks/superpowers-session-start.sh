#!/usr/bin/env bash
# SessionStart: inject the using-superpowers skill. From github.com/obra/superpowers (MIT).
skill_md="$(dirname "$0")/../skills/using-superpowers/SKILL.md"
[ -r "$skill_md" ] || exit 0
exec python3 - "$skill_md" <<'PY'
import json, sys
body = open(sys.argv[1], encoding="utf-8").read().rstrip("\n")
ctx = ("<EXTREMELY_IMPORTANT>\nYou have superpowers.\n\n**Below is the full content of your "
       "'using-superpowers' skill - your introduction to using skills. For all other skills, "
       "use the 'Skill' tool:**\n\n" + body + "\n</EXTREMELY_IMPORTANT>")
print(json.dumps({"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": ctx}}))
PY
