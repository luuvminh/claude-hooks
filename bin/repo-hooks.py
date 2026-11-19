#!/usr/bin/env python3
"""Run the project hooks of repos below the session folder.

  repo-hooks.py <Event>
Cloud threads open in /home/user while repos live in /home/user/<repo>, so
Claude Code never loads <repo>/.claude/settings.json. This runs that file's
hooks for <Event>, with CLAUDE_PROJECT_DIR set to the repo, and merges results:
additionalContext is joined, the first decision/permission JSON wins, and any
exit 2 blocks with all stderr messages joined.
"""
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import repos  # noqa: E402

event = sys.argv[1]
raw = sys.stdin.read()
payload = repos.load_json(raw)
subject = payload.get("tool_name") or payload.get("source") or payload.get("agent_type") or ""

contexts, blocks, merged = [], [], {}
for repo in repos.hooked_children():
    groups = repos.load_json(repos.settings_text(repo)).get("hooks", {}).get(event, [])
    for g in groups:
        m = g.get("matcher") or ""
        if m not in ("", "*"):
            try:
                if not re.fullmatch(m, subject):
                    continue
            except re.error:
                continue
        for h in g.get("hooks", []):
            if h.get("type") != "command":
                continue
            env = dict(os.environ, CLAUDE_PROJECT_DIR=repo)
            try:
                r = subprocess.run(["bash", "-c", h["command"]], input=raw, cwd=repo, env=env,
                                   capture_output=True, text=True, timeout=h.get("timeout", 60))
            except subprocess.TimeoutExpired:
                continue
            if r.returncode == 2:
                blocks.append("[%s] %s" % (os.path.basename(repo), r.stderr.strip()))
                continue
            out = r.stdout.strip()
            if not out:
                continue
            j = repos.load_json(out) if out.startswith("{") else {}
            if not j:
                contexts.append(out)
                continue
            hso = j.pop("hookSpecificOutput", {}) or {}
            if hso.get("additionalContext"):
                contexts.append(hso.pop("additionalContext"))
            for k, v in hso.items():
                merged.setdefault("hookSpecificOutput", {}).setdefault(k, v)
            for k, v in j.items():
                merged.setdefault(k, v)

CONTEXT_EVENTS = {"SessionStart", "UserPromptSubmit", "SubagentStart", "PostToolUse", "PreToolUse"}
if contexts and event in CONTEXT_EVENTS:
    hso = merged.setdefault("hookSpecificOutput", {})
    hso["hookEventName"] = event
    hso["additionalContext"] = "\n\n".join(contexts)
if merged:
    print(json.dumps(merged))
if blocks:
    sys.stderr.write("\n\n".join(blocks) + "\n")
    sys.exit(2)
