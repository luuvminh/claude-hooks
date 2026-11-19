#!/usr/bin/env python3
"""Add the shared hooks to a user-level settings.json, keeping everything else.

  merge-settings.py <settings.json> <claude-hooks dir>
Idempotent: old entries pointing into <claude-hooks dir> are replaced, others kept.
The previous file is backed up next to it before any change.
"""
import json
import os
import shutil
import sys
import time

path, home = sys.argv[1], os.path.abspath(sys.argv[2])
q = lambda p: '"%s"' % p  # noqa: E731
py = "python3 " + q(os.path.join(home, "bin", "common.py"))
rh = "python3 " + q(os.path.join(home, "bin", "repo-hooks.py"))
H = lambda *p: q(os.path.join(home, *p))  # noqa: E731


def cmd(c, timeout, msg=None):
    h = {"type": "command", "command": c, "timeout": timeout}
    if msg:
        h["statusMessage"] = msg
    return h


OURS = {
    "SessionStart": [
        {"hooks": [cmd("bash " + H("bin", "self-update.sh"), 5)]},
        {"matcher": "startup|clear|compact", "hooks": [cmd(
            py + " superpowers-session-start bash " + H("hooks", "superpowers-session-start.sh"), 10, "Loading superpowers")]},
        {"matcher": "startup|resume|clear|compact", "hooks": [cmd(
            py + " ponytail-activate node " + H("hooks", "ponytail-activate.js"), 15, "Loading ponytail mode")]},
        {"hooks": [cmd(py + " impeccable sh " + H("skills", "impeccable", "scripts", "impeccable") + " hook", 5)]},
        {"hooks": [cmd(rh + " SessionStart", 60)]},
    ],
    "UserPromptSubmit": [
        {"hooks": [cmd(py + " ponytail-mode-tracker node " + H("hooks", "ponytail-mode-tracker.js"), 15)]},
        {"hooks": [cmd(rh + " UserPromptSubmit", 60)]},
    ],
    "SubagentStart": [
        {"hooks": [cmd(py + " ponytail-subagent node " + H("hooks", "ponytail-subagent.js"), 15)]},
        {"hooks": [cmd(rh + " SubagentStart", 60)]},
    ],
    "PreToolUse": [
        {"hooks": [cmd(rh + " PreToolUse", 60)]},
    ],
    "PostToolUse": [
        {"matcher": "Edit|Write|MultiEdit", "hooks": [cmd(
            py + " impeccable sh " + H("skills", "impeccable", "scripts", "impeccable") + " hook", 10, "Checking UI changes")]},
        {"hooks": [cmd(rh + " PostToolUse", 90)]},
    ],
    "Stop": [
        {"hooks": [cmd(py + " impeccable sh " + H("skills", "impeccable", "scripts", "impeccable") + " hook", 30, "Design deep pass")]},
        {"hooks": [cmd(py + " ponytail-gate python3 " + H("hooks", "ponytail-gate.py"), 30, "Checking ponytail review")]},
        {"hooks": [cmd(rh + " Stop", 300)]},
    ],
}


def ours(group):
    return any(home in h.get("command", "") for h in group.get("hooks", []))


try:
    text = open(path, encoding="utf-8").read()
    data = json.loads(text) if text.strip() else {}
except FileNotFoundError:
    text, data = None, {}
hooks = data.setdefault("hooks", {})
for event in list(hooks):
    hooks[event] = [g for g in hooks[event] if not ours(g)]
    if not hooks[event]:
        del hooks[event]
for event, groups in OURS.items():
    hooks.setdefault(event, []).extend(groups)
new = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
if new == text:
    print("settings unchanged: " + path)
    sys.exit(0)
if text is not None:
    bak = path + ".bak-" + time.strftime("%Y%m%d-%H%M%S")
    shutil.copy2(path, bak)
    print("backup: " + bak)
os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
tmp = path + ".tmp"
open(tmp, "w", encoding="utf-8").write(new)
if text is not None:
    shutil.copymode(path, tmp)  # keep 600 on Mac
os.replace(tmp, path)
print("settings updated: " + path)
